"""Synthetic lifecycle/transport tests. No private assets, HTTP, S3 or KRS calls."""
import copy
import io
import json
import os
import subprocess
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import ohi_private_pilot_worker as w


def when(hour=14, minute=0, day=28):
    return datetime(2026, 10, day, hour, minute, tzinfo=w.JST)


def binding():
    return dict(RAILWAY_PROJECT_ID=w.PROJECT, RAILWAY_ENVIRONMENT_ID=w.ENVIRONMENT,
                RAILWAY_SERVICE_ID=w.SERVICE, OHI_S3_ENDPOINT='https://test.invalid',
                OHI_S3_BUCKET='synthetic', OHI_S3_ACCESS_KEY_ID='synthetic-not-a-key',
                OHI_S3_SECRET_ACCESS_KEY='synthetic-not-a-secret',
                OHI_FIXED_CODE_ROOT='/opt/km-inputs/code',
                OHI_FIXED_ASSET_ROOT='/opt/km-inputs/assets',
                OHI_FIXED_CONTRACT_PATH='/opt/km-inputs/forward-contract.json',
                OHI_BOOTSTRAP_KEY=w.BOOTSTRAP_KEY, OHI_BOOTSTRAP_SHA256=w.BOOTSTRAP_SHA)


class LifecycleTests(unittest.TestCase):
    def test_default_and_bootstrap_cli_never_arm_prediction(self):
        with patch.object(w, 'main', return_value=0) as main:
            self.assertEqual(w.cli([]), 0)
            main.assert_called_once_with(execute=False)
            main.reset_mock()
            self.assertEqual(w.cli(['--bootstrap-only']), 0)
            main.assert_called_once_with(execute=False)

    def test_bootstrap_exits_before_source_import_or_calculation(self):
        clock = Mock(wraps=datetime)
        clock.now.return_value = when(18)
        store = Mock()
        store.put_new_and_read.return_value = {'actual_object_GET': True}
        output = io.StringIO()
        with patch.dict(os.environ, binding(), clear=True), patch.object(w, 'datetime', clock), \
             patch.object(w, 'PrivateStore', return_value=store), \
             patch.object(w, 'prepare_bootstrap', return_value=((Path('/unused'),)*4, {'synthetic': True})), \
             redirect_stdout(output):
            self.assertEqual(w.main(), 0)
        event = json.loads(output.getvalue())
        self.assertEqual(event['schema'], 'KM_OHI_PRIVATE_BOOTSTRAP_READY_V1')
        self.assertFalse(event['prediction_calculated'])
        self.assertFalse(event['relay_completed'])
        self.assertEqual(event['new_KRS_calls'], 0)

    def test_single_window_boundaries(self):
        for instant in (when(14, 0), when(14, 24)):
            w.require_execution_window(instant)
        for instant in (when(13, 59), when(14, 25), when(18), when(day=29)):
            with self.subTest(instant=instant), self.assertRaises(ValueError):
                w.require_execution_window(instant)
        with self.assertRaisesRegex(ValueError, 'TIMEZONE_REQUIRED'):
            w.require_execution_window(datetime(2026, 10, 28, 14))

    def test_late_execute_stops_before_store_or_source(self):
        clock = Mock(wraps=datetime)
        clock.now.return_value = when(18)
        with patch.dict(os.environ, binding(), clear=True), patch.object(w, 'datetime', clock), \
             patch.object(w, 'PrivateStore') as store:
            with self.assertRaisesRegex(ValueError, 'CUTOFF_PASSED'):
                w.main(execute=True)
            store.assert_not_called()

    def test_exact_actor_and_date_still_required(self):
        good = binding()
        w.require_actor(good, when())
        for key, value in [('RAILWAY_ENVIRONMENT_ID', 'production'), ('GITHUB_ACTIONS', 'true')]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                w.require_actor({**good, key: value}, when())
        with self.assertRaisesRegex(ValueError, 'EXACT_DATE'):
            w.require_actor(good, when(day=29))

    def test_cutoff_supervisor_terminates_only_owned_process_group(self):
        clock = Mock(wraps=datetime)
        clock.now.return_value = when(14, 24)
        process = Mock(pid=123456)
        process.wait.side_effect = [subprocess.TimeoutExpired('synthetic', 60), 0]
        with patch.object(w, 'datetime', clock), patch('subprocess.Popen', return_value=process) as popen, \
             patch('os.killpg') as kill:
            with self.assertRaisesRegex(ValueError, 'CUTOFF_PASSED'):
                w.cli(['--execute'])
        self.assertTrue(popen.call_args.kwargs['start_new_session'])
        self.assertEqual(kill.call_args.args[0], process.pid)
        self.assertEqual(process.wait.call_args_list[0].kwargs['timeout'], 60)

    def test_official_race_identity(self):
        race = dict(race_date=w.TARGET_DAY, race_no=1, provider_race_id=w.RACE_ID)
        w.require_race(race)
        with self.assertRaisesRegex(ValueError, 'OFFICIAL_RACE_ID_CONFLICT'):
            w.require_race({**race, 'provider_race_id': '2026102720110201'})

    def test_real_cgroup_files_required_with_approved_ceiling(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'cpu.max').write_text('100000 100000')
            (root/'memory.max').write_text(str(512*1024*1024))
            self.assertEqual(w.require_resource_limits(root)['vCPU_limit'], 1)
            for cpu, memory in [('max 100000', 'max'), ('200000 100000', '536870912'),
                                ('100000 100000', '1073741824')]:
                (root/'cpu.max').write_text(cpu)
                (root/'memory.max').write_text(memory)
                with self.subTest(cpu=cpu, memory=memory), self.assertRaises(ValueError):
                    w.require_resource_limits(root)
        with self.assertRaisesRegex(ValueError, 'UNVERIFIED'):
            w.require_resource_limits(Path('/nonexistent-synthetic-cgroup'))

    def test_v1_cgroup_support(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'cpu').mkdir(); (root/'memory').mkdir()
            (root/'cpu/cpu.cfs_quota_us').write_text('50000')
            (root/'cpu/cpu.cfs_period_us').write_text('100000')
            (root/'memory/memory.limit_in_bytes').write_text('268435456')
            self.assertEqual(w.require_resource_limits(root)['vCPU_limit'], .5)

    def test_r2_binding_refuses_original_71_file_transport(self):
        store = Mock()
        with self.assertRaisesRegex(ValueError, 'R2_BINDING_CONFLICT'):
            w.prepare_bootstrap(store, {**binding(), 'OHI_BOOTSTRAP_SHA256': 'a'*64})
        store.get.assert_not_called()

    def test_missing_or_changed_r2_object_refused(self):
        for data in (None, b'wrong', b'x'*w.BOOTSTRAP_BYTES):
            with self.subTest(data_bytes=None if data is None else len(data)), \
                 self.assertRaisesRegex(ValueError, 'BOOTSTRAP_SHA_CONFLICT'):
                w.prepare_bootstrap(Mock(get=Mock(return_value=data)), binding())

    def test_archive_traversal_remains_refused(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as z:
            z.writestr('../synthetic-escape', b'x')
        with tempfile.TemporaryDirectory() as folder, self.assertRaisesRegex(ValueError, 'PATH_CONFLICT'):
            w.safe_extract(buf.getvalue(), folder)

    def test_failure_receipt_names_stage_and_redacts_free_text(self):
        w.stage('BOOTSTRAP_GET_AND_SHA')
        receipt = w.hold_event(RuntimeError('synthetic-secret https://test.invalid'))
        self.assertEqual(receipt['stage'], 'BOOTSTRAP_GET_AND_SHA')
        self.assertNotIn('synthetic-secret', json.dumps(receipt))
        error = ValueError('PRIVATE_EXAMPLE:synthetic-secret')
        self.assertEqual(w.hold_event(error)['error_code'], 'PRIVATE_EXAMPLE')

    def test_pipeline_failure_location_comes_from_traceback(self):
        def simulate():
            raise RuntimeError('synthetic-engine-failure')
        try:
            simulate()
        except RuntimeError as exc:
            self.assertEqual(w.hold_event(exc)['stage'], 'KRS')

    def test_presentation_only_weight_correction_preserves_frozen_input(self):
        frozen = {'all_runners': [dict(runner_id='1', name='Synthetic', current_body_weight=450,
                                      current_body_weight_change=0), dict(runner_id='2', name='Unknown')]}
        original = copy.deepcopy(frozen)
        body = w.delivery_body(frozen, '馬体重・当日馬場は未観測で、後から更新。\n票と全29指数の合成テスト本文。')
        self.assertIn('|1 Synthetic|450|0|', body)
        self.assertIn('|2 Unknown|UNKNOWN|UNKNOWN|', body)
        self.assertNotIn('馬体重・当日馬場は未観測で、', body)
        self.assertIn('票と全29指数の合成テスト本文。', body)
        self.assertEqual(frozen, original)


class RelayTests(unittest.TestCase):
    def setUp(self):
        self.body = '合成テスト本文。全馬・券面を省略しない。\n'*4
        self.record = w.seal(dict(date=w.TARGET_DAY, race_no=1, race_id=w.RACE_ID,
                                  body_bytes=len(self.body.encode()), body_sha256=w.digest(self.body.encode())))
        self.events = list(w.body_events(self.body, self.record, limit=7))

    def test_full_unicode_roundtrip_with_out_of_order_chunks(self):
        mixed = [self.events[0], *reversed(self.events[1:-1]), self.events[-1]]
        self.assertEqual(w.assemble_body(mixed), (self.body, self.record))

    def test_missing_or_duplicate_chunk_refused(self):
        for events in (self.events[:2]+self.events[3:], self.events+[self.events[1]]):
            with self.assertRaisesRegex(ValueError, 'INCOMPLETE_OR_DUPLICATE'):
                w.assemble_body(events)

    def test_missing_end_refused(self):
        with self.assertRaisesRegex(ValueError, 'BOUNDARIES'):
            w.assemble_body(self.events[:-1])

    def test_wrong_race_begin_chunk_and_end_refused(self):
        for position in (0, 1, -1):
            events = copy.deepcopy(self.events)
            events[position]['race_id'] = '2026102820110302'
            with self.subTest(position=position), self.assertRaisesRegex(ValueError, 'IDENTITY_CONFLICT'):
                w.assemble_body(events)

    def test_wrong_race_sealed_record_refused(self):
        events = copy.deepcopy(self.events)
        record = {k: v for k, v in self.record.items() if k != 'sha256'}
        events[0]['record'] = w.seal({**record, 'race_id': '2026102720110201'})
        with self.assertRaisesRegex(ValueError, 'RECORD_RACE_CONFLICT'):
            w.assemble_body(events)

    def test_resealed_record_cannot_refer_to_another_body(self):
        events = copy.deepcopy(self.events)
        record = {k: v for k, v in self.record.items() if k != 'sha256'}
        events[0]['record'] = w.seal({**record, 'body_sha256': '0'*64})
        with self.assertRaisesRegex(ValueError, 'RECORD_BODY_CONFLICT'):
            w.assemble_body(events)

    def test_record_sha_tamper_refused(self):
        events = copy.deepcopy(self.events)
        events[0]['record']['sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'RECORD_SHA_MISMATCH'):
            w.assemble_body(events)

    def test_body_byte_length_tamper_refused(self):
        events = copy.deepcopy(self.events)
        events[0]['bytes'] += 1
        with self.assertRaisesRegex(ValueError, 'BODY_SHA_MISMATCH'):
            w.assemble_body(events)

    def test_boolean_chunk_index_refused(self):
        events = copy.deepcopy(self.events)
        events[1]['part'] = False
        with self.assertRaisesRegex(ValueError, 'INCOMPLETE_OR_DUPLICATE'):
            w.assemble_body(events)


class StoreTests(unittest.TestCase):
    def store(self, rows, returned=b'new'):
        store = w.PrivateStore.__new__(w.PrivateStore)
        store.bucket = 'synthetic'
        store.client = Mock()
        store.client.list_objects_v2.return_value = rows
        store.get = Mock(return_value=returned)
        return store

    def test_private_create_requires_actual_get_and_never_overwrites(self):
        store = self.store({'Contents': []})
        receipt = store.put_new_and_read('synthetic-key', b'new')
        self.assertTrue(receipt['actual_object_GET'])
        self.assertEqual(store.client.put_object.call_args.kwargs['IfNoneMatch'], '*')
        store.get.assert_called_once_with('synthetic-key')

    def test_get_mismatch_refused(self):
        with self.assertRaisesRegex(ValueError, 'ACTUAL_BYTE_READBACK_MISMATCH'):
            self.store({'Contents': []}, b'changed').put_new_and_read('synthetic', b'new')

    def test_one_gb_or_unproven_capacity_refuses_put(self):
        for rows in ({'Contents': [{'Size': w.MAX_BUCKET_BYTES}]}, {'IsTruncated': True}):
            store = self.store(rows)
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                store.put_new_and_read('synthetic', b'new')
            store.client.put_object.assert_not_called()


if __name__ == '__main__':
    unittest.main()

"""Synthetic lifecycle/transport tests. No private assets, HTTP, S3 or KRS calls."""
import copy
import io
import json
import os
import subprocess
import sys
import tempfile
import threading
import types
import unittest
import zipfile
from concurrent.futures import ThreadPoolExecutor
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
                OHI_BOOTSTRAP_KEY=w.BOOTSTRAP_KEY, OHI_BOOTSTRAP_SHA256=w.BOOTSTRAP_SHA,
                OHI_PROTECTED_WORK_ARCHIVE_KEY='protected/synthetic.zip',
                OHI_PROTECTED_WORK_ARCHIVE_SHA256='d'*64,
                OHI_PROTECTED_WORK_ARCHIVE_BYTES='1',
                OHI_PROTECTED_WORK_ORIGINAL_SHA256='e'*64)


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


class SyntheticPreconditionFailed(Exception):
    response = {'Error': {'Code': 'PreconditionFailed'},
                'ResponseMetadata': {'HTTPStatusCode': 412}}


class SingleRunTests(unittest.TestCase):
    def test_missing_protected_references_stop_before_store_or_claim(self):
        clock = Mock(wraps=datetime); clock.now.return_value = when()
        missing = {k: v for k, v in binding().items() if not k.startswith('OHI_PROTECTED_WORK_')}
        for env in (missing, {**missing, 'OHI_PROTECTED_WORK_ORIGINAL_SHA256': 'e'*64}):
            with self.subTest(present=sorted(env)), patch.dict(os.environ, env, clear=True), \
                 patch.object(w, 'datetime', clock), \
                 patch.object(w, 'require_resource_limits', return_value={'synthetic': True}), \
                 patch.object(w, 'PrivateStore') as store, \
                 patch.object(w, 'claim_single_run') as claim:
                with self.assertRaisesRegex(ValueError, 'BINDINGS_INCOMPLETE') as caught:
                    w.main(execute=True)
                store.assert_not_called(); claim.assert_not_called()
                self.assertEqual(w.hold_event(caught.exception)['stage'], 'PROTECTED_WORK_BINDINGS')

    def test_concurrent_claim_has_one_winner_without_overwrite(self):
        class ConditionalMemoryStore:
            def __init__(self):
                self.lock = threading.Lock()
                self.objects = {}

            def put_new_and_read(self, key, data):
                with self.lock:
                    if key in self.objects:
                        raise SyntheticPreconditionFailed()
                    self.objects[key] = data
                    actual = self.objects[key]
                    return {'key': key, 'bytes': len(actual),
                            'sha256': w.digest(actual), 'actual_object_GET': True}

        store = ConditionalMemoryStore()
        def attempt(_):
            try:
                return w.claim_single_run(store, 'synthetic/', when(), {})
            except ValueError as exc:
                return str(exc)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(attempt, range(2)))
        self.assertEqual(sum(isinstance(x, dict) for x in results), 1)
        self.assertEqual(results.count('PRIVATE_PILOT_EXECUTION_ALREADY_CLAIMED'), 1)
        self.assertEqual(len(store.objects), 1)
        saved = next(iter(store.objects.values()))
        self.assertFalse(json.loads(saved)['prediction_calculated'])
        with self.assertRaisesRegex(ValueError, 'ALREADY_CLAIMED'):
            w.claim_single_run(store, 'synthetic/', when(), {})
        self.assertEqual(next(iter(store.objects.values())), saved)

    def test_duplicate_stops_main_before_bootstrap_or_prediction(self):
        store = Mock()
        store.put_new_and_read.side_effect = SyntheticPreconditionFailed()
        clock = Mock(wraps=datetime)
        clock.now.return_value = when()
        with patch.dict(os.environ, binding(), clear=True), patch.object(w, 'datetime', clock), \
             patch.object(w, 'require_resource_limits', return_value={'synthetic': True}), \
             patch.object(w, 'PrivateStore', return_value=store), \
             patch.object(w, 'prepare_bootstrap') as bootstrap:
            with self.assertRaisesRegex(ValueError, 'ALREADY_CLAIMED') as caught:
                w.main(execute=True)
        bootstrap.assert_not_called()
        store.latest_record.assert_not_called()
        store.get.assert_not_called()
        self.assertEqual(store.put_new_and_read.call_count, 1)
        self.assertEqual(w.hold_event(caught.exception)['stage'], 'SINGLE_RUN_CLAIM')

    def test_other_store_errors_are_not_relabelled_as_duplicate(self):
        error = RuntimeError('synthetic network failure')
        with self.assertRaises(RuntimeError) as caught:
            w.claim_single_run(Mock(put_new_and_read=Mock(side_effect=error)), 'synthetic/', when(), {})
        self.assertIs(caught.exception, error)


class ProtectedOriginalTests(unittest.TestCase):
    def setUp(self):
        self.race = dict(race_date=w.TARGET_DAY, race_no=1, provider_race_id=w.RACE_ID,
                         prediction_cutoff=when(14, 25).isoformat())
        self.observation = w.seal({'race': self.race, 'synthetic': True})
        self.frozen = w.seal(dict(race=self.race, source_sha256=self.observation['sha256'],
                                 classification='OHI_SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS',
                                 freeze_at=when(8, 18).isoformat(), synthetic=True))
        self.files = {'original/synthetic-only.txt': b'not an official SOURCE or prediction',
                      'source/observation.json': json.dumps(self.observation).encode()}
        self.manifest = dict(race_id=w.RACE_ID, prediction_sha256=self.frozen['sha256'],
                             files=[dict(path=key, bytes=len(data), SHA256=w.digest(data))
                                    for key, data in self.files.items()])

    def archive(self, files=None, manifest=None):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as z:
            for key, data in (files if files is not None else self.files).items():
                z.writestr(key, data)
            z.writestr('SHA_Manifest.json', json.dumps(manifest if manifest is not None else self.manifest))
        return buf.getvalue()

    def env(self, data):
        return dict(OHI_PROTECTED_WORK_ARCHIVE_KEY='protected/synthetic.zip',
                    OHI_PROTECTED_WORK_ARCHIVE_SHA256=w.digest(data),
                    OHI_PROTECTED_WORK_ARCHIVE_BYTES=str(len(data)),
                    OHI_PROTECTED_WORK_ORIGINAL_SHA256=self.frozen['sha256'])

    def read(self, data, env=None, readback=None):
        with tempfile.TemporaryDirectory() as folder:
            result = w.protected_work_original(Mock(get=Mock(return_value=data)),
                       self.env(data) if env is None else env, folder,
                       readback or Mock(return_value=(self.frozen, 'synthetic complete body')))
            if result:
                original, source, record = result
                self.assertEqual(original, Path(folder)/'protected-work/original')
                self.assertEqual(source, Path(folder)/'protected-work/source')
                for key, value in self.files.items():
                    self.assertEqual((Path(folder)/'protected-work'/key).read_bytes(), value)
                return record

    def test_protected_readback_keeps_original_freeze_and_counts_no_new_krs(self):
        data = self.archive()
        reader = Mock(return_value=(self.frozen, 'synthetic complete body'))
        record = self.read(data, readback=reader)
        reader.assert_called_once()
        self.assertEqual(record['prediction_sha256'], self.frozen['sha256'])
        self.assertEqual(record['freeze_at'], self.frozen['freeze_at'])
        self.assertEqual(record['new_KRS_calls'], 0)
        self.assertEqual(record['new_prestart_credit'], 0)
        self.assertFalse(record['current_source_verified'])
        self.assertEqual(record['origin_actor'], 'CHATGPT_WORK')
        self.assertEqual(record['manifest_payload_members_verified'], len(self.files))
        self.assertEqual(w.validate_record(record), record)

    def test_protected_pointer_cannot_silently_fall_back_when_incomplete(self):
        data = self.archive()
        with self.assertRaisesRegex(ValueError, 'BINDINGS_INCOMPLETE'):
            self.read(data, env={'OHI_PROTECTED_WORK_ORIGINAL_SHA256': self.frozen['sha256']})
        with self.assertRaisesRegex(ValueError, 'BINDINGS_INCOMPLETE'):
            w.protected_work_original(Mock(), {}, Path('/unused'), Mock())

    def test_missing_changed_or_wrong_length_archive_is_rejected(self):
        data = self.archive()
        for actual, env in [(None, self.env(data)), (data+b'x', self.env(data)),
                            (data, {**self.env(data), 'OHI_PROTECTED_WORK_ARCHIVE_BYTES': str(len(data)+1)})]:
            with tempfile.TemporaryDirectory() as folder, self.assertRaisesRegex(ValueError, 'ARCHIVE_SHA_CONFLICT'):
                w.protected_work_original(Mock(get=Mock(return_value=actual)), env, folder, Mock())

    def test_member_tamper_is_rejected_even_when_outer_sha_is_rebound(self):
        changed = {**self.files, 'original/synthetic-only.txt': b'changed'}
        with self.assertRaisesRegex(ValueError, 'MEMBER_SHA_CONFLICT'):
            self.read(self.archive(files=changed))

    def test_extra_zip_member_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'INVENTORY_CONFLICT'):
            self.read(self.archive(files={**self.files, 'unlisted.txt': b'extra'}))

    def test_duplicate_manifest_paths_are_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        manifest['files'].append(copy.deepcopy(manifest['files'][0]))
        with self.assertRaisesRegex(ValueError, 'MANIFEST_PATH_CONFLICT'):
            self.read(self.archive(manifest=manifest))

    def test_manifest_cannot_point_to_another_race(self):
        manifest = {**self.manifest, 'race_id': '2026102820110302'}
        with self.assertRaisesRegex(ValueError, 'MANIFEST_IDENTITY_CONFLICT'):
            self.read(self.archive(manifest=manifest))

    def test_readback_failure_is_not_bypassed_by_valid_archive(self):
        with self.assertRaisesRegex(ValueError, 'OHI_ORIGINAL_HASH_MISMATCH'):
            self.read(self.archive(), readback=Mock(side_effect=ValueError('OHI_ORIGINAL_HASH_MISMATCH')))

    def test_source_identity_cannot_be_resealed_to_a_different_snapshot(self):
        observation = w.seal({**{k: v for k, v in self.observation.items() if k != 'sha256'},
                              'synthetic': 'other'})
        changed = {**self.files, 'source/observation.json': json.dumps(observation).encode()}
        manifest = {**self.manifest, 'files': [dict(path=key, bytes=len(data), SHA256=w.digest(data))
                                              for key, data in changed.items()]}
        with self.assertRaisesRegex(ValueError, 'SOURCE_CONFLICT'):
            self.read(self.archive(files=changed, manifest=manifest))


class ReuseFlowTests(unittest.TestCase):
    def test_material_same_protected_or_worker_original_never_calls_run(self):
        # Synthetic control-flow integration; every SOURCE/Engine API is stubbed.
        for has_worker_record in (False, True):
            with self.subTest(worker_record=has_worker_record), tempfile.TemporaryDirectory() as folder:
                root = Path(folder); code = root/'code'; code.mkdir()
                pilot = root/'pilot'; pilot.mkdir()
                protected = pilot/'protected-work/original'; protected.mkdir(parents=True)
                protected_source = pilot/'protected-work/source'; protected_source.mkdir()
                race = dict(race_date=w.TARGET_DAY, race_no=1, provider_race_id=w.RACE_ID,
                            prediction_cutoff=when(14, 25).isoformat())
                observation = w.seal({'race': race, 'receipts': [{'fetched_at': when().isoformat()}],
                                      'synthetic': True})
                frozen = w.seal(dict(race=race, source_sha256='0'*64,
                         classification='OHI_SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS',
                         freeze_at=when(8, 18).isoformat(), all_runners=[dict(runner_id='1', name='Synthetic')],
                         krs={name: {'receipt': {'actual_engine_executed': True, 'runs': 5000, 'seed': 1}}
                              for name in ('BASELINE', 'OHI_FIXED_CANDIDATE')}))
                inherited = w.seal(dict(date=w.TARGET_DAY, race_no=1, race_id=w.RACE_ID,
                                       prediction_sha256=frozen['sha256'], origin_actor='CHATGPT_WORK'))
                payload = io.BytesIO()
                with zipfile.ZipFile(payload, 'w') as z:
                    z.writestr('prediction/synthetic.txt', b'prior frozen bytes')
                    z.writestr('source/synthetic.txt', b'prior source bytes')
                archive = payload.getvalue()
                previous = w.seal(dict(date=w.TARGET_DAY, race_no=1, race_id=w.RACE_ID,
                         prediction_sha256=frozen['sha256'], prior_original_origin='CHATGPT_WORK',
                         archive=dict(key='previous/synthetic.zip', bytes=len(archive), sha256=w.digest(archive))))
                store = Mock()
                store.latest_record.return_value = json.dumps(previous).encode() if has_worker_record else None
                store.get.return_value = archive
                store.put_new_and_read.side_effect = lambda key, data: dict(key=key, bytes=len(data),
                                                       sha256=w.digest(data), actual_object_GET=True)
                module = types.ModuleType('runtime.ohi_single_race_research')
                module.capture = Mock(return_value=observation)
                module.run = Mock(side_effect=AssertionError('REUSE must never recompute'))
                module.readback = Mock(return_value=(frozen, 'Synthetic complete frozen body.'))
                module.revision_decision = Mock(return_value={'decision': 'REUSE_FROZEN_ORIGINAL'})
                module.write = Mock(); module.render = Mock(); module.check_source_time = Mock()
                package = types.ModuleType('runtime'); package.__path__ = []
                clock = Mock(wraps=datetime); clock.now.return_value = when()
                old_cwd = Path.cwd(); old_path = list(sys.path); output = io.StringIO()
                try:
                    with patch.dict(os.environ, {**binding(), 'OHI_PROTECTED_WORK_ORIGINAL_SHA256': frozen['sha256']}, clear=True), patch.object(w, 'datetime', clock), \
                         patch.object(w, 'require_resource_limits', return_value={'synthetic': True}), \
                         patch.object(w, 'PrivateStore', return_value=store), \
                         patch.object(w, 'prepare_bootstrap', return_value=((code, code/'model', code/'engine', code/'params'), {})), \
                         patch.object(w.tempfile, 'mkdtemp', return_value=str(pilot)), \
                         patch.object(w, 'protected_work_original', return_value=(protected, protected_source, inherited)) as reader, \
                         patch.object(w, 'zip_original', return_value=b'synthetic archive') as zipper, \
                         patch.dict(sys.modules, {'runtime': package, 'runtime.ohi_single_race_research': module}), \
                         redirect_stdout(output):
                        self.assertEqual(w.main(execute=True), 0)
                    module.run.assert_not_called()
                    reader.assert_called_once()
                    self.assertEqual(module.readback.call_count, 2 if has_worker_record else 1)
                    expected_original = pilot/'prior/prediction' if has_worker_record else protected
                    expected_source = pilot/'prior/source' if has_worker_record else protected_source
                    self.assertEqual(zipper.call_args.args[:2], (expected_original, expected_source))
                    begin = json.loads(output.getvalue().splitlines()[0])
                    self.assertEqual(begin['record']['new_KRS_calls'], 0)
                    self.assertEqual(begin['record']['mode'], 'REUSE_WITH_SEPARATE_FRESH_SOURCE_CHECK')
                    self.assertEqual(begin['record']['freeze_at'], frozen['freeze_at'])
                    self.assertEqual(begin['record']['prediction_sha256'], frozen['sha256'])
                    self.assertEqual(begin['record']['prior_original_origin'], 'CHATGPT_WORK')
                    self.assertIn('single_run_claim', begin['record'])
                finally:
                    os.chdir(old_cwd); sys.path[:] = old_path


if __name__ == '__main__':
    unittest.main()

"""Offline regressions for the existing FNB REFERENCE lifecycle."""
from copy import deepcopy
from datetime import timedelta
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from runtime import local_fnb_day_supervisor as day
from runtime import local_fnb_finite_actor as actor
from runtime.local_fnb_bounded_rakuten_producer import BoundedCardProducer
from runtime.local_fnb_r20_chat_completion import ProducerHold


DATE = '2026-12-07'
BINDING = 'a' * 64


def activation(**changes):
    return {
        'enabled': True, 'reference_only': True, 'race_date': DATE,
        'venue_id': 'FNB', 'classification': day.CLASSIFICATION,
        'race_numbers': list(range(1, 13)), 'max_dispatches': 12,
        'binding_sha256': BINDING, 'actor_id': 'FIXTURE_ACTOR',
        'supervisor_code_sha256': sha256(Path(day.__file__).read_bytes()).hexdigest(),
        'approval_ref': 'FIXTURE', 'worker_duration_approval_ref': 'FIXTURE',
        'approved_worker_seconds': 2, 'effective_from': DATE + 'T14:30:00+09:00',
        'effective_until': DATE + 'T22:00:00+09:00', **changes,
    }


class ReferenceContinuation(unittest.TestCase):
    def test_future_lease_requires_dated_approval_and_keeps_old_checkpoint(self):
        approved = activation()
        binding = {'_binding_sha256': BINDING}
        start = DATE + 'T14:35:00+09:00'
        stop = DATE + 'T14:35:02+09:00'
        manifest = {
            'profile': actor.PROFILE, 'venue_id': 'FNB', 'classification': day.CLASSIFICATION,
            'race_dates': [DATE], 'approval_ref': approved['approval_ref'],
            'actor_id': approved['actor_id'], 'approved_day_worker_seconds': {DATE: 2},
            'actor_code_sha256': sha256(Path(actor.__file__).read_bytes()).hexdigest(),
            'leases': [{'race_date': DATE, 'start_at': start, 'stop_at': stop}],
        }
        with self.assertRaisesRegex(ValueError, 'NEW_DAY_APPROVAL_OR_ACTOR'):
            actor.validate(manifest, binding=binding, activations={DATE: activation(approval_ref='other')})
        with self.assertRaisesRegex(ValueError, 'EXACT_DATED_SCOPE'):
            actor.validate(manifest, binding=binding, activations={DATE: activation(reference_only=False)})
        current = day.stamp(start)
        calls = []

        def supervise(**kwargs):
            nonlocal current
            calls.append(kwargs['day'])
            current += timedelta(seconds=kwargs['worker_seconds'])
            return {'counts': {}}

        with TemporaryDirectory() as private:
            historical = Path(private) / actor.STATE_NAME
            historical.write_bytes(b'old immutable checkpoint')
            for _ in range(2):
                state = actor.run(manifest, private, binding=binding, activations={DATE: approved},
                                  clock=lambda: current, supervise=supervise)
            self.assertEqual(state['leases']['0']['status'], 'COMPLETED')
            self.assertEqual(calls, [DATE])
            self.assertEqual(historical.read_bytes(), b'old immutable checkpoint')
            self.assertTrue((Path(private) / f'FNB_{DATE}_FINITE_ACTOR_CHECKPOINT.json').is_file())

    def test_sender_claim_precedes_send_and_readback_keeps_receipt_levels_separate(self):
        race = {'race_id': 'KM-LOCAL-FNB-20261207-R01-REFERENCE', 'race_no': 1,
                'prediction_cutoff': DATE + 'T14:40:00+09:00'}
        target = {'delivery_recipient_id': 'fixture-recipient', 'delivery_route_id': 'fixture-route'}
        approved = activation(delivery_enabled=True, delivery_approval_ref='FIXTURE', **target)
        current = day.stamp(DATE + 'T14:36:00+09:00')
        completion = {'private_readback_verified': True, 'active_universe_sha256': 'b' * 64,
                      'prepared_at': DATE + 'T14:35:50+09:00', 'revision': 'REFERENCE-fixture',
                      'body_sha256': 'c' * 64, 'observation_within_existing_600s': True}
        cell = {'reference_execution_status': 'REFERENCE_CALLBACK_AND_BODY_READBACK_VERIFIED',
                'reference': completion, 'reference_claim': {'delivery_target': target,
                    'race_sha256': day.sha(race), 'approval_ref': approved['approval_ref']}}
        sends, checkpoints = [], []
        with TemporaryDirectory() as private:
            root = Path(private)
            receipt_path = root / 'sender.json'

            def send(*, idempotency_key, now, **kwargs):
                self.assertEqual(checkpoints[-1]['reference_delivery_claim']['idempotency_key'], idempotency_key)
                sends.append(idempotency_key)
                receipt_path.write_bytes(day.encoded({**target, 'idempotency_key': idempotency_key,
                    'sent_at': now.isoformat(), 'race_id': race['race_id'],
                    'revision': completion['revision'], 'body_sha256': completion['body_sha256'],
                    'run_id': 'fixture-run', 'chat_ref': 'fixture-chat', 'sender_accepted_verified': True}))

            def inspect(**kwargs):
                if not receipt_path.is_file():
                    return {}
                return {'sender_accepted_verified': True, 'original': {'path': receipt_path.name,
                    'sha256': sha256(receipt_path.read_bytes()).hexdigest()}}

            binding = {'_binding_sha256': BINDING, 'inspect_reference_delivery': inspect,
                       'authorize_reference_delivery': lambda **_: True, 'deliver_reference': send}

            def tick(active=approved, *, execute=True):
                day._reference_delivery({'race_date': DATE}, race, binding, active, root, cell,
                    lambda: current, lambda: checkpoints.append(deepcopy(cell)), execute=execute)

            tick(activation(**{**approved, 'delivery_recipient_id': 'wrong'}))
            tick(execute=False)
            self.assertEqual(sends, [])
            tick()
            tick()
            self.assertEqual(len(sends), 1)
            self.assertFalse(cell['reference_delivery']['prestart_arrival'])
            self.assertFalse(cell['reference_delivery']['recipient_ack_verified'])
            receipt = json.loads(receipt_path.read_bytes())
            receipt.update(received_at=current.isoformat(), recipient_ack_verified=True)
            receipt_path.write_bytes(day.encoded(receipt))
            tick(execute=False)
            self.assertTrue(cell['reference_delivery']['prestart_arrival'])
            self.assertTrue(cell['reference_delivery']['recipient_ack_verified'])
            self.assertEqual(cell['reference_delivery']['run_id'], 'fixture-run')
            receipt_path.unlink()
            tick()
            self.assertEqual(len(sends), 1)

    def test_future_direct_transport_is_closed_without_dated_scope(self):
        with TemporaryDirectory() as private, patch(
            'runtime.local_fnb_bounded_rakuten_producer.urllib.request.build_opener',
            side_effect=AssertionError('unexpected HTTP'),
        ):
            producer = BoundedCardProducer(root=private, observed_cards={}, robots_path='unused',
                                           actor_id='FIXTURE_ACTOR')
            with self.assertRaises(ProducerHold):
                producer.fetch(url='https://keiba.rakuten.co.jp/unused',
                    intent={'venue_id': 'FNB', 'race_date': DATE, 'race_no': 1},
                    now=day.stamp(DATE + 'T14:35:00+09:00'))


if __name__ == '__main__':
    unittest.main()

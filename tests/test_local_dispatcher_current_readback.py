"""Current-store monitoring only; synthetic checkpoints, no provider or POST."""
from copy import deepcopy
from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from runtime import local_race_day_dispatcher as d
from runtime import local_race_key_gate as gate

NOW = datetime.fromisoformat('2026-11-03T11:30:00+09:00')
EID = 'KM-LOCAL-FNB-20261103-R01-LIVE-R1'


def inputs():
    fields = dict(venue_id='FNB', race_date='2026-11-03', race_no=1,
                  scheduled_post_at='2026-11-03T12:10:00+09:00',
                  prediction_cutoff='2026-11-03T12:05:00+09:00')
    plan = {'race_date': '2026-11-03', 'venue_id': 'FNB',
            'races': [{'execution_id': EID, 'race_key': 'FNB-20261103-R01-LIVE-R1', 'fields': fields}]}
    plan['plan_sha256'] = d.sha(plan)
    approval = dict(race_numbers=[1], minimum_remaining_seconds=300)
    state = {'races': {EID: {'claimed_at': (NOW-timedelta(minutes=1)).isoformat(),
                           'acknowledgement': {'acknowledged': True},
                           'final_readback': {'signed_final_pass': True,
                                              'prestart_final_pass': True,
                                              'render_available': True}}}}
    return plan, approval, state


def observation(final):
    return {'stages': {'FINAL': {'status': 'PERSISTED_REQUIRES_FRESH_VERIFICATION' if final
                                                   else 'NOT_OBSERVED'}}}


def run(tmp_path, monkeypatch, *, final=True, reader=None, claimed=True):
    plan, approval, state = inputs()
    if not claimed:
        state['races'][EID].pop('claimed_at')
    monkeypatch.setattr(d, 'checkpoint_status', lambda root, eid: observation(final))
    monkeypatch.setattr(d, 'existing_race_refs', lambda root, race: [tmp_path/'existing'])
    monkeypatch.setattr(d, 'owned_registration', lambda *a: False)
    if reader is not None:
        monkeypatch.setattr(gate, 'readback_final', reader)
    send = Mock(side_effect=AssertionError('MUST NOT REDISPATCH'))
    result = d.tick(tmp_path, plan, approval, state, now=NOW, execute=True,
                    authorize=lambda *a: 'UNCHANGED_AUTHORITY', publish=lambda: None,
                    reconcile=lambda *a: {'status': 'completed', 'conclusion': 'success'}, send=send)
    send.assert_not_called()
    return result['races'][EID]


@pytest.mark.parametrize('claimed', [True, False])
def test_final_readback_uses_the_explicit_store_and_canonical_reader(tmp_path, monkeypatch, claimed):
    calls = []
    expected = {'signed_final_pass': True, 'prestart_final_pass': True,
                'render_available': True, 'prestart_delivery_pass': False}
    def reader(eid, job_status, *, repo_root):
        calls.append((eid, job_status, repo_root))
        return deepcopy(expected)
    monkeypatch.setattr(gate, 'terminal_state', Mock(side_effect=AssertionError('NO VERIFICATION POST')))
    cell = run(tmp_path, monkeypatch, reader=reader, claimed=claimed)
    assert calls == [(EID, 'completed' if claimed else 'existing', tmp_path)]
    assert cell['final_readback'] == expected
    assert cell['final_readback']['prestart_delivery_pass'] is False


def test_disappeared_final_cannot_retire_the_claim_on_previous_success(tmp_path, monkeypatch):
    cell = run(tmp_path, monkeypatch, final=False,
               reader=Mock(side_effect=AssertionError('NO FINAL TO READ')))
    assert 'final_readback' not in cell
    assert d.worker_pending_races({'races': {EID: cell}}) == [cell]


def test_failed_current_readback_cannot_reuse_previous_success(tmp_path, monkeypatch):
    cell = run(tmp_path, monkeypatch,
               reader=Mock(side_effect=ValueError('CURRENT_RECEIPT_MISMATCH')))
    assert 'final_readback' not in cell
    assert cell['monitor_error'] == 'CURRENT_RECEIPT_MISMATCH'
    assert d.worker_pending_races({'races': {EID: cell}}) == [cell]

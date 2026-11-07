"""Mechanical regressions only: no SOURCE acquisition, live Owner or tickets."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import textwrap

import pytest

from runtime import local_race_day_dispatcher as d


NOW = datetime(2026, 11, 3, 2, 0, tzinfo=timezone.utc)


@pytest.mark.parametrize('status', [
    'DISPATCH_ACKNOWLEDGED_MONITOR_CHECKPOINTS',
    'HOLD_AMBIGUOUS_DISPATCH_NO_AUTOMATIC_RETRY',
])
def test_single_claim_remains_observed_until_verified_final(status):
    clock = [NOW]
    calls = []
    cell = {'claimed_at': NOW.isoformat(), 'status': status}
    state = {'races': {'R1': cell}}
    def step():
        calls.append(clock[0])
        if len(calls) == 3:
            cell['final_readback'] = {
                'signed_final_pass': True, 'prestart_final_pass': True,
                'render_available': True, 'prestart_delivery_pass': False,
                'user_received_at': None,
            }
        return state
    result = d.run_worker(
        {'worker_seconds': 180, 'worker_duration_approval_ref': 'TEST_ONLY'},
        step, clock=lambda: clock[0],
        sleep=lambda s: clock.__setitem__(0, clock[0] + timedelta(seconds=s)))
    assert calls == [NOW, NOW + timedelta(seconds=60), NOW + timedelta(seconds=120)]
    assert result is state
    assert cell['claimed_at'] == NOW.isoformat()
    assert cell['final_readback']['prestart_delivery_pass'] is False


def test_ambiguous_claim_stops_at_existing_lease_without_new_send_or_success():
    clock = [NOW]
    state = {'races': {'R1': {'claimed_at': NOW.isoformat(),
              'status': 'HOLD_AMBIGUOUS_DISPATCH_NO_AUTOMATIC_RETRY'}}}
    original = deepcopy(state)
    calls = []
    def step():
        calls.append(clock[0])
        return state
    result = d.run_worker(
        {'worker_seconds': 75, 'worker_duration_approval_ref': 'TEST_ONLY'},
        step, clock=lambda: clock[0],
        sleep=lambda s: clock.__setitem__(0, clock[0] + timedelta(seconds=s)))
    assert calls == [NOW, NOW + timedelta(seconds=60), NOW + timedelta(seconds=75)]
    assert result == original


@pytest.mark.parametrize('cell', [
    {'claimed_at': NOW.isoformat(), 'status': 'FINAL_DEADLINE_EXPIRED'},
    {'claimed_at': NOW.isoformat(), 'status': 'ACTIONS_FAILURE_CHECKPOINT_RECOVERY_HOLD'},
    {'status': 'HOLD_PRE_DISPATCH', 'manual_recovery_required': True},
    {'status': 'EXISTING_RACE_READ_BACK_OR_APPROVED_CHECKPOINT_RESUME_ONLY'},
])
def test_terminal_or_owner_repair_hold_does_not_expand_worker(cell):
    assert d.worker_pending_races({'races': {'R1': cell}}) == []


def test_one_unverified_boolean_cannot_end_monitoring():
    for key in ('signed_final_pass', 'prestart_final_pass', 'render_available'):
        final = {k: True for k in ('signed_final_pass', 'prestart_final_pass', 'render_available')}
        final[key] = False
        cell = {'claimed_at': NOW.isoformat(),
                'status': 'DISPATCH_ACKNOWLEDGED_MONITOR_CHECKPOINTS', 'final_readback': final}
        assert d.worker_pending_races({'races': {'R1': cell}}) == [cell]


def test_source_first_execution_id_is_a_real_github_output_line(tmp_path):
    workflow = (Path(__file__).resolve().parents[1] /
                '.github/workflows/km-local-source-first-entry.yml').read_text()
    code = textwrap.dedent(re.search(
        r"python - <<'PY'\n(.*?)\n          PY", workflow, re.S)[1])
    eid = 'KM-LOCAL-FNB-20261103-R01-LIVE-R1'
    output = tmp_path / 'github-output'
    env = dict(os.environ, GITHUB_EVENT_NAME='workflow_dispatch',
               RACE_REQUEST_JSON=json.dumps({'family_id': 'LOCAL',
                   'execution_phase': 'SOURCE', 'execution_id': eid}),
               GITHUB_OUTPUT=str(output))
    subprocess.run([sys.executable, '-c', code], cwd=tmp_path, env=env,
                   check=True, capture_output=True, text=True)
    assert output.read_bytes() == ('execution_id=' + eid + '\n').encode()
    assert json.loads((tmp_path / 'race-request.json').read_text())['execution_id'] == eid

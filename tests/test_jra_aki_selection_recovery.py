"""Crossing cutoff during numerical recovery never backdates a LIVE decision."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'runtime'))
import jra_aki_selection_recovery as recovery
from jra_production_no_bet_terminal import verify_no_bet_terminal


def test_cutoff_crossed_while_preparation_runs_is_historical(monkeypatch):
    eid = 'KM-JRA-KYO-20261012-R05-LIVE-R1'
    intent = json.loads((ROOT/'runtime/jra_formal_intents'/f'{eid}.json').read_text())
    env = json.loads((ROOT/'runtime/executions'/eid/'SOURCE/runs/38196179597/source_receipt_envelope.json').read_text())
    report = json.loads((ROOT/'runtime/exact_gaps'/f'{eid}.json').read_text())
    report['static_owner_executable_diagnostic'] = None
    report['static_owner_executable_error'] = 'STATIC_FREEZE_AFTER_CUTOFF'
    authority = json.loads((ROOT/'profiles/KM_FAMILY_CURRENT_AUTHORITY_20261011_R50.json').read_text())
    clocks = iter([datetime(2026,10,12,3,19,tzinfo=timezone.utc),
                   datetime(2026,10,12,3,21,tzinfo=timezone.utc)])
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return next(clocks, datetime(2026,10,12,3,21,tzinfo=timezone.utc))
    monkeypatch.setattr(recovery, 'datetime', Clock)
    monkeypatch.setattr(recovery, 'load_current_authority', lambda: authority)
    monkeypatch.setattr(recovery, 'prepare_production_numerical', lambda *a, **k: deepcopy(report))
    t = recovery.recover(intent, env, source_receipt_verified=True)
    assert t['lineage'] == 'HISTORICAL_DIAGNOSTIC'
    assert t['created_at'].startswith('2026-10-12T03:21:')
    assert t['failure_report']['recovery_static_basis'].startswith('HISTORICAL_DIAGNOSTIC_ONLY')
    assert verify_no_bet_terminal(t)['total_investment'] == 0
    with pytest.raises(ValueError, match='FORWARD_LIVE'):
        verify_no_bet_terminal(t, require_live=True)

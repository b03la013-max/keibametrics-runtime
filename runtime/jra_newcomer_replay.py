"""Build a post-start PAPER acceptance request over the original signed SOURCE."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from jra_execution_maturity_bridge import (prepare_production_numerical,
    load_current_authority, build_formal_request, verify_formal_request_binding)
from jra_production_auto_handoff import compile_production_auto_handoff


def build(intent, envelope):
    original = intent['execution_id']
    q = dict(intent)
    q.update(execution_id=original+'-NEWCOMER-REPLAY-R51-R2',
             prediction_id=original+'-NEWCOMER-REPLAY-R51-R2',
             temporal_mode='POST-START-REPLAY', acceptance_only=True,
             mec_profile='KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R3',
             current_authority_manifest=load_current_authority()['manifest_id'],
             replay_computed_at=datetime.now(timezone.utc).isoformat(),
             original_pre_race_execution_id=original)
    report = prepare_production_numerical(q, envelope, source_execution_id=original)
    if report.get('production_full_numerical_ready') is not True:
        raise ValueError('NEWCOMER_REPLAY_FULL20_NOT_CLOSED')
    # Historical freeze BASIS, explicitly never a backdated LIVE computation.
    basis = envelope['artifact']['source_freeze_at']
    out = compile_production_auto_handoff(q, envelope, report,
        current_authority=load_current_authority(), frozen_at=basis)
    out = build_formal_request(out, envelope, source_execution_id=original)
    verify_formal_request_binding(out, envelope)
    assert out['aki_information_gate']['action'] == 'PAPER'
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--intent', required=True)
    p.add_argument('--source-envelope', required=True)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    from verify_source_envelope import verify
    assert verify(a.source_envelope)['valid'] is True
    out = build(json.loads(Path(a.intent).read_text()), json.loads(Path(a.source_envelope).read_text()))
    path = Path(a.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=2)+'\n')
    print(json.dumps({'execution_id':out['execution_id'],'indices':len(out['runners'])*20,
                     'columns':out['aki_column_selection']['columns'],'action':'PAPER',
                     'temporal_mode':out['temporal_mode']}, ensure_ascii=False))

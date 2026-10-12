"""All six actual AKI stops: new rules close newcomers; trust failures stay closed."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from jra_aki_dispatch import apply_authorized_v21
from jra_aki_capital_preflight import verify_aki_ticket_binding,AKICapitalError
from jra_aki_no_bet_terminal import record_selection_failure,verify_failure,terminal_eligible
from minimum_efficient_coverage import build_mec_plan
from capital_policy import resolve_capital_policy


@pytest.mark.parametrize('venue,race,tickets,stop',[
    ('KYO',4,35,None),('TKY',5,15,None),('TKY',6,15,None),('KYO',6,24,None),
    ('TKY',3,None,'AKI_SINGLE_HEAD_FORBIDDEN'),('TKY',4,None,'AKI_EVIDENCE_SELECTED_COLUMN_EMPTY')])
def test_every_actual_aki_stop_has_reproducible_current_rule_outcome(venue,race,tickets,stop):
    eid=f'KM-JRA-{venue}-20261012-R{race:02d}-LIVE-R1'
    report=json.loads((ROOT/'runtime/exact_gaps'/f'{eid}.json').read_text())
    source_path=next((ROOT/'runtime/executions'/eid/'SOURCE/runs').glob('*/source_receipt_envelope.json'))
    source=json.loads(source_path.read_text())['artifact']
    q=deepcopy(report['prepared_numerical_request'])
    q.update(source_snapshot_sha256=source['source_snapshot_sha256'],
             static_prediction=report['static_owner_executable_diagnostic']['static_prediction'])
    authority=json.loads((ROOT/'profiles/KM_FAMILY_CURRENT_AUTHORITY_20261012_R51.json').read_text())
    original=deepcopy((q,source))
    if stop:
        with pytest.raises(AKICapitalError,match=stop):
            apply_authorized_v21(q,source,authority,root=ROOT)
        report['current_authority_manifest']=authority['manifest_id']
        report['auto_handoff_error']=stop
        record_selection_failure(report,q,source,authority,root=ROOT)
        assert verify_failure(report,root=ROOT)['code']==stop
        assert terminal_eligible(report,root=ROOT)
    else:
        out=apply_authorized_v21(q,source,authority,root=ROOT)
        mec=build_mec_plan(out)
        verify_aki_ticket_binding(out,mec,source=source,current_authority=authority,root=ROOT)
        assert mec['ticket_count']==tickets
        assert resolve_capital_policy(out,mec)['decision']=='PAPER'
        assert all(out['aki_column_selection']['columns'].values())
    assert (q,source)==original

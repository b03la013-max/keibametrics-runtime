"""Newcomer execution closes under PAPER without weakening established rules."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from jra_aki_dispatch import apply_authorized_v21
from jra_aki_capital_preflight import verify_aki_ticket_binding, AKICapitalError
from minimum_efficient_coverage import build_mec_plan
from capital_policy import resolve_capital_policy


def real():
    eid='KM-JRA-KYO-20261012-R06-LIVE-R1'
    report=json.loads((ROOT/'runtime/exact_gaps'/f'{eid}.json').read_text())
    path=next((ROOT/'runtime/executions'/eid/'SOURCE/runs').glob('*/source_receipt_envelope.json'))
    source=json.loads(path.read_text())['artifact']
    q=deepcopy(report['prepared_numerical_request'])
    q.update(source_snapshot_sha256=source['source_snapshot_sha256'],
             static_prediction=report['static_owner_executable_diagnostic']['static_prediction'])
    a=json.loads((ROOT/'profiles/KM_FAMILY_CURRENT_AUTHORITY_20261012_R51.json').read_text())
    return q,source,a


def test_real_newcomer_closes_240_indices_and_24_paper_tickets():
    q,s,a=real(); before=deepcopy((q,s))
    out=apply_authorized_v21(q,s,a,root=ROOT)
    mec=build_mec_plan(out)
    verify_aki_ticket_binding(out,mec,source=s,current_authority=a,root=ROOT)
    assert out['aki_column_selection']['columns']=={'W':['7','8','5'],'P2':['7','8','5'],
                                                   'P3':['7','8','5','12','2','11']}
    assert mec['ticket_count']==24
    out['capital_policy']={'mode':'RECOMMENDATION_ONLY'}
    capital=resolve_capital_policy(out,mec)
    assert capital['decision']=='PAPER' and capital['no_bet'] and capital['paper_only']
    assert (q,s)==before and len(out['runners'])*20==240


@pytest.mark.parametrize('fault',['activation','registry','late_source','missing_provenance'])
def test_cannot_bypass_authority_or_source_gates(fault):
    q,s,a=real()
    if fault=='activation':a['family_scoped_authority']['JRA']['newcomer_aki_paper_activation']['purchase_authority']=True
    if fault=='registry':a['family_scoped_authority']['JRA']['newcomer_aki_paper_activation']['policy_sha256']='0'*64
    if fault=='late_source':s['source_freeze_at']='2026-10-12T15:00:00+09:00'
    if fault=='missing_provenance':q['runners'][0]['canonical_components']['BVI']['evidence_refs']=[]
    with pytest.raises((ValueError,AKICapitalError)):apply_authorized_v21(q,s,a,root=ROOT)


def test_transport_neutrals_do_not_become_observed_channels():
    q,s,a=real()
    for r in q['runners']:
        for k in ('CFI','BVI','JTI','CSI','BWI'):
            r['canonical_components'][k]['components']=[]
    with pytest.raises(AKICapitalError,match='COLUMN_EMPTY'):
        apply_authorized_v21(q,s,a,root=ROOT)


def test_established_policy_is_unchanged():
    from test_jra_aki_v21_enacted import fixture
    from jra_aki_v21 import apply_authorized_v21 as old
    q,s,_=fixture()
    a=real()[2]
    assert apply_authorized_v21(q,s,a,root=ROOT)==old(q,s,a,root=ROOT)

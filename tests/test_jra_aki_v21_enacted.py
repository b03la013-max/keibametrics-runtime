"""Acceptance of enacted mappings, not evidence of predictive accuracy."""
from copy import deepcopy
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from jra_aki_v21 import apply_authorized_v21
from jra_aki_capital_preflight import AKICapitalError, verify_aki_ticket_binding
from minimum_efficient_coverage import build_mec_plan
from capital_policy import resolve_capital_policy


def fixture(kind='solid',external=True):
    authority=json.loads((ROOT/'profiles/KM_FAMILY_CURRENT_AUTHORITY_20261011_R50.json').read_text())
    registry=json.loads((ROOT/authority['family_scoped_authority']['JRA']['aki_v21_activation']['components']['path']).read_text())
    indices=registry['feature_compiler_policy']['required_indices']
    runners=[]
    for i in range(8):
        value=95-i*7 if kind=='solid' else 80-i*.01
        runners.append({'runner_id':str(i+1),'canonical_components':{k:{'value':value,'rule_id':'TEST-NOT-PRODUCTION','mapping_version':'TEST','source_fact':'Synthetic test, not pre-race/OOS','evidence_refs':['TEST']} for k in indices}})
    source={'family_id':'JRA','race_id':'TEST-ENACTED','source_snapshot_sha256':'a'*64,'source_freeze_at':'2026-10-11T10:00:00+09:00','prediction_cutoff':'2026-10-11T10:05:00+09:00','conflicts':[]}
    if external:
        source['aki_external_observations']=[{'observed_at':at,'production_fact_authority':True,'source_authority':'JRA_OFFICIAL','evidence_refs':['TEST-SIGNED-SOURCE'],'source_fact':'Test odds/going observation','win_odds':{str(i+1):2+i for i in range(8)},'going':'良'} for at in ['2026-10-11T09:58:00+09:00','2026-10-11T10:00:00+09:00']]
    request={'family_id':'JRA','race_id':source['race_id'],'source_snapshot_sha256':source['source_snapshot_sha256'],'prediction_cutoff':source['prediction_cutoff'],'runners':runners,'static_prediction':{'ranking':[str(i+1) for i in range(8)],'roles':{}},'capital_policy':{'mode':'HARD_RACE_BUDGET','max_race_capital':10000,'insufficient_action':'PAPER'}}
    return request,source,authority


def execute(request,source,authority):
    selected=apply_authorized_v21(request,source,authority,root=ROOT)
    mec=build_mec_plan(selected)
    verify_aki_ticket_binding(selected,mec,source=source,current_authority=authority,root=ROOT)
    return selected,mec,resolve_capital_policy(selected,mec)


def test_solid_small_chaotic_wide_and_budget_paper():
    solid,sm,sc=execute(*fixture('solid'))
    wide,wm,wc=execute(*fixture('chaotic'))
    assert sm['ticket_count'] < wm['ticket_count']
    assert len(solid['purchased_heads'])==1
    assert len(wide['purchased_heads'])>1
    assert sc['no_bet'] is False
    assert wc['paper_only'] is True
    assert wm['material_coverage_ratio']==1
    assert solid['static_prediction']['aki_jra_v21']['axes']['solid_finish_correction']==10
    assert wide['static_prediction']['aki_jra_v21']['axes']['solid_finish_correction']==0


def test_external_absence_is_not_stability_or_bet_permission():
    q,s,a=fixture(external=False)
    q['capital_policy']={'mode':'RECOMMENDATION_ONLY'}
    before=deepcopy((q,s,a))
    o,m,c=execute(q,s,a)
    assert (q,s,a)==before
    assert o['aki_information_gate']['status']=='LIMITED'
    assert o['static_prediction']['aki_jra_v21']['axes']['external_change']==100
    assert c['decision']=='PAPER' and c['no_bet']
    assert o['aki_compiler_receipt']['signed_source_enriched'] is False


@pytest.mark.parametrize('fault',['late','shadow','short','missing_odds','negative','reverse'])
def test_external_series_fail_closed(fault):
    q,s,a=fixture()
    last=s['aki_external_observations'][-1]
    if fault=='late':last['observed_at']='2026-10-11T10:01:00+09:00'
    if fault=='shadow':last['source_authority']='JMA_SHADOW'
    if fault=='short':last['observed_at']='2026-10-11T09:58:10+09:00'
    if fault=='missing_odds':last['win_odds'].pop('1')
    if fault=='negative':last['win_odds']['1']=-1
    if fault=='reverse':s['aki_external_observations'].reverse()
    with pytest.raises(AKICapitalError):execute(q,s,a)


def test_full20_missing_and_nonfinite_block():
    q,s,a=fixture()
    q['runners'][0]['canonical_components'].pop('DCR')
    with pytest.raises(AKICapitalError,match='FULL20_INCOMPLETE'):execute(q,s,a)
    q,s,a=fixture();q['runners'][0]['canonical_components']['DCR']['value']=float('nan')
    with pytest.raises(AKICapitalError,match='INDEX_INVALID'):execute(q,s,a)


def test_gate_and_ticket_tampering_rejected_by_independent_recompute():
    q,s,a=fixture(external=False);o,m,c=execute(q,s,a)
    o['aki_information_gate']['action']='ALLOW'
    with pytest.raises(AKICapitalError,match='RECOMPUTATION_MISMATCH'):verify_aki_ticket_binding(o,m,source=s,current_authority=a,root=ROOT)


def test_budget_never_widens_selection_and_ranking_is_preserved():
    q,s,a=fixture();o,m,c=execute(q,s,a)
    q['capital_policy']['max_race_capital']=100000
    oo,mm,cc=execute(q,s,a)
    assert o['aki_column_selection']==oo['aki_column_selection']
    assert m['tickets']==mm['tickets']
    assert oo['static_prediction']['ranking']==q['static_prediction']['ranking']


def test_actual_tokyo11_unsigned_replay_not_rewritten_final():
    request=ROOT/'runtime/requests/KM-JRA-TKY-20261011-R11-LIVE-R1-FORMAL.json'
    if not request.exists():pytest.skip('Historical replay fixture unavailable')
    q=json.loads(request.read_text());s={**q['source_snapshot'],'source_snapshot_sha256':q['source_snapshot_sha256']}
    _,_,a=fixture();o,m,c=execute(q,s,a)
    assert m['ticket_count']==10
    assert m['minimum_required_capital']==1000
    assert c['paper_only'] is True
    assert o['static_prediction']['ranking']==q['static_prediction']['ranking']
    assert o['static_prediction']['aki_jra_v21']['axis_failure_risk']==22.5


def test_review_alternatives_preserve_set_protection_instead_of_all_ordered_triples():
    q,s,a=fixture()
    for row,w in zip(q['runners'],[80,77,70,67,60,53,46,39]):
        row['canonical_components']['ZAI_WIN']['value']=w
    q['runners'][0]['canonical_components']['DCR']['value']=59
    o,m,c=execute(q,s,a)
    assert o['aki_column_selection']['triggers']['W']=='REVIEW'
    assert any(row['status']=='PROTECTED' and row['column']=='W' for row in o['role_registry'])
    assert any(row['status']=='PROTECT' for row in o['pair_dispositions'])
    assert any(t['bet_type']=='TRIO' for t in m['tickets'])
    assert m['material_coverage_ratio']==1

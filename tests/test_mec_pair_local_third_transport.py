"""Material transport regressions; no new selection or SOURCE authority."""
from copy import deepcopy
import importlib.util
from pathlib import Path

import pytest

from runtime.minimum_efficient_coverage import build_mec_plan, validate_mec_plan, MECError
from runtime.local_fnb_r17_method_constructor import construct


def request():
    return {'race_id':'SYNTHETIC-PAIR-LOCAL-CONSUMER','family_id':'LOCAL',
        'runners':[{'runner_id':str(n)} for n in range(1,6)],
        'role_registry':[{'runner_id':'1','column':'W','status':'CORE'},
            {'runner_id':'2','column':'P2','status':'CORE'},
            {'runner_id':'3','column':'P3','status':'CORE'},
            {'runner_id':'4','column':'P3','status':'INACTIVE'},
            {'runner_id':'5','column':'P2','status':'PROTECTED'}],
        'pair_dispositions':[{'head':'1','second':'2','status':'PURCHASE','reason':'FROZEN_MATERIAL_PAIR'},
            {'head':'1','second':'5','status':'PROTECT','reason':'FROZEN_MATERIAL_OTHER_PAIR'}],
        'third_dispositions':[{'head':'1','second':'2','third':'4','status':'PROTECT',
            'reason':'FROZEN_PAIR_SPECIFIC_THIRD','evidence_refs':['SYNTHETIC-EVIDENCE-1'],
            'source_snapshot_sha256':'a'*64}]}


def selected(plan, kind):
    return {tuple(t['selection']) for t in plan['tickets'] if t['bet_type']==kind}


def test_already_material_local_third_is_preserved_only_in_its_pair_scope():
    req=request();original=deepcopy(req)
    plan=build_mec_plan(req)
    assert (1,2,4) in selected(plan,'TRIO')
    assert (1,4,5) not in selected(plan,'TRIO')
    assert {(1,2,3),(1,3,5)} <= selected(plan,'TRIO')
    assert not selected(plan,'TRIFECTA')
    assert req==original
    trace=plan['pair_local_third_transport']
    assert trace['global_static_roles_changed'] is False
    assert trace['material_selection_inferred'] is False
    row=trace['consumed_original_material_thirds'][0]
    assert row['evidence_refs']==['SYNTHETIC-EVIDENCE-1']
    assert row['source_snapshot_sha256']=='a'*64
    assert row['semantic_source']=='PAIR_LOCAL'
    assert validate_mec_plan(plan)['mec_verified']


def test_material_exact_third_keeps_orientation_without_automatic_set_purchase():
    req=request();req['third_dispositions'][0]['status']='PURCHASE'
    plan=build_mec_plan(req)
    assert (1,2,4) in selected(plan,'TRIFECTA')
    assert (1,2,4) not in selected(plan,'TRIO')
    assert plan['material_coverage_ratio']==1.0


@pytest.mark.parametrize('status',['SEMANTIC_ONLY','UNKNOWN','UNADOPTED_RESEARCH_SEMANTIC_ONLY','EXCLUDE'])
def test_possibility_or_unknown_outside_global_p3_cannot_become_material(status):
    req=request();req['third_dispositions'][0]['status']=status
    plan=build_mec_plan(req)
    assert not any(4 in t['selection'] for t in plan['tickets'])
    assert 'pair_local_third_transport' not in plan


def test_material_local_third_does_not_invent_a_material_parent_pair():
    req=request();req['pair_dispositions']=[]
    with pytest.raises(MECError,match='ACTIVE_W_WITHOUT_MATERIAL_PAIR_CLOSURE'):
        build_mec_plan(req)
    plan=build_mec_plan(req,strict_head_closure=False)
    assert plan['tickets']==[]
    assert plan['orphan_thirds']==req['third_dispositions']


def test_conflicting_material_third_is_not_resolved_by_last_row_wins():
    req=request();other=deepcopy(req['third_dispositions'][0]);other['status']='EXCLUDE'
    req['third_dispositions'].append(other)
    with pytest.raises(MECError,match='THIRD_DISPOSITION_CONFLICTING_STATUS'):
        build_mec_plan(req)


def method_fixture(tmp_path):
    path=Path(__file__).with_name('test_fnb_20261102_r17_method_constructor.py')
    spec=importlib.util.spec_from_file_location('_r17_material_transport_fixture',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module,module.objects(tmp_path)


def test_six_method_constructor_consumes_local_materiality_without_role_promotion(tmp_path):
    fixture,(root,sem,krs,numeric_sha)=method_fixture(tmp_path)
    original=deepcopy(sem)
    for req in sem.values():
        req['role_registry']=[row for row in req['role_registry'] if row['column']!='P3']
    before=deepcopy(sem)
    result=construct(race_id=fixture.RID,owner_semantics=sem,private_root=root,
        dual_krs_manifest=krs,source_snapshot_sha256=fixture.SRC,
        numerical_materialization_sha256=numeric_sha)
    assert sem==before
    assert original!=sem
    for owner in ('BASELINE','CANDIDATE'):
        assert len(result['plan_evidence'][owner]['pair_local_third_transport']['consumed_original_material_thirds'])==2
        for method in ('EXACTA','TRIO','TRIFECTA'):
            assert result['owners'][owner][method]['point_count']==1
            assert result['owners'][owner][method]['no_bet'] is False
    assert result['canonical_ticket_roundtrip']['complete']


def test_unadopted_semantics_cannot_turn_empty_consumption_into_computed_no_bet(tmp_path):
    fixture,(root,sem,krs,numeric_sha)=method_fixture(tmp_path)
    for row in sem['BASELINE']['role_registry']:
        row['status']='INACTIVE'
    sem['BASELINE']['pair_dispositions'][0]['status']='UNADOPTED_RESEARCH_SEMANTIC_ONLY'
    with pytest.raises(ValueError,match='UNRESOLVED_SEMANTIC_SELECTION'):
        construct(race_id=fixture.RID,owner_semantics=sem,private_root=root,
            dual_krs_manifest=krs,source_snapshot_sha256=fixture.SRC,
            numerical_materialization_sha256=numeric_sha)


def test_unknown_role_selection_is_hold_before_method_capital(tmp_path):
    fixture,(root,sem,krs,numeric_sha)=method_fixture(tmp_path)
    sem['BASELINE']['role_registry'][0]['status']='UNKNOWN'
    with pytest.raises(ValueError,match='UNRESOLVED_ROLE_SELECTION'):
        construct(race_id=fixture.RID,owner_semantics=sem,private_root=root,
            dual_krs_manifest=krs,source_snapshot_sha256=fixture.SRC,
            numerical_materialization_sha256=numeric_sha)


def test_orphan_material_third_cannot_become_six_method_computed_no_bet(tmp_path):
    fixture,(root,sem,krs,numeric_sha)=method_fixture(tmp_path)
    for row in sem['BASELINE']['role_registry']:
        row['status']='INACTIVE'
    sem['BASELINE']['pair_dispositions']=[]
    before=deepcopy(sem)
    with pytest.raises(ValueError,match='ORPHAN_MATERIAL_THIRD_WITHOUT_PAIR'):
        construct(race_id=fixture.RID,owner_semantics=sem,private_root=root,
            dual_krs_manifest=krs,source_snapshot_sha256=fixture.SRC,
            numerical_materialization_sha256=numeric_sha)
    assert sem==before

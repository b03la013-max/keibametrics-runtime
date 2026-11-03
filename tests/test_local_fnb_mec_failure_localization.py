"""Failure localization keeps missing selection separate from NO-BET/capital."""
from copy import deepcopy
import pytest

from runtime import local_fnb_semantic_closure as semantic
from runtime.local_fnb_mec_failure_localization import audit_prediction, paper_comparison
from tests.test_local_fnb_semantic_closure import fixture, seal, NOW


def inputs(all_unknown=False):
    prediction = fixture()
    context = {'race_id':prediction['race_id'], 'source_snapshot_sha256':prediction['source_snapshot_sha256'],
        'runners':[{'runner_id':r, 'status':'UNKNOWN' if all_unknown or r=='4' else 'RESEARCH_INFERRED',
                    'input_observations':0 if all_unknown or r=='4' else 2} for r in prediction['active_runners']]}
    context['sha256'] = semantic._sha(context)
    if all_unknown:
        for col in ('W','P2','P3'):
            prediction['column_rankings'][col]['front'] = []
            for row in prediction['column_rankings'][col]['rows']:
                row.update(unknown=True,rank=None)
        prediction['roles'] = {r:['W_UNKNOWN_POSSIBLE','P2_UNKNOWN_POSSIBLE','P3_UNKNOWN_PROTECTED']
                                for r in prediction['active_runners']}
        prediction.update(pair_dispositions=[],third_dispositions=[],head_local_P2=[],pair_conditioned_Third=[])
    prediction['input_context_sha256'] = context['sha256']
    seal(prediction)
    return prediction, semantic.execute_strict_mec(prediction,evaluated_at=NOW), context


def test_all_unknown_first_failure_is_not_capital_or_rendering_or_empty_no_bet():
    p, strict, c = inputs(True)
    result = audit_prediction(p,strict,c,evaluated_at=NOW)
    assert result['first_algorithmic_failure']=='FIXED_CONTEXT_UNKNOWN_NO_MATERIAL_W_HEAD'
    assert result['earliest_pipeline_failure']=='SOURCE_ACTIVE_QUALIFICATION'
    assert result['context_unknown_runners']==4
    assert result['historical_FNB_observations_consumed']==0
    categories = {r['category']:r for r in result['categories']}
    assert categories['PAIR_SELECTION']['state']=='NO_PAIR_PROPOSALS_REACHED'
    assert categories['GLOBAL_P3_CONSUMER']['state']=='NOT_TRIGGERED_BY_THIS_FROZEN_PREDICTION'
    assert categories['CAPITAL']['state'].startswith('NOT_REACHED')
    assert categories['CANONICAL_TICKET_RENDERER']['state'].startswith('NOT_REACHED')
    assert result['fresh_strict']['canonical_mec_plan']['tickets']==[]
    assert result['fresh_strict']['tickets'] is None and result['computed_no_bet'] is False


def test_known_unadopted_head_and_pairlocal_mismatch_are_independent_causes():
    p, strict, c = inputs()
    result = audit_prediction(p,strict,c,evaluated_at=NOW)
    categories = {r['category']:r for r in result['categories']}
    assert result['first_algorithmic_failure']=='KNOWN_W_HEAD_WITHOUT_MATERIAL_PAIR_CLOSURE'
    assert categories['PAIR_SELECTION']['state']=='UNADOPTED_PROPOSALS'
    assert len(categories['GLOBAL_P3_CONSUMER']['off_global_proposals'])==1
    assert categories['STRUCTURAL_EXCLUSION']['state']=='ALL_DUPLICATE_POSITION_EXCLUSIONS_RECORDED'
    assert not result['original_strict_hold_lifted']


def test_audit_rejects_cross_revision_context_or_mec():
    p, strict, c = inputs()
    changed=deepcopy(c);changed['runners'][0]['input_observations']=50
    with pytest.raises(ValueError,match='CONTEXT_ORIGINAL'):
        audit_prediction(p,strict,changed,evaluated_at=NOW)
    strict['model_prediction_sha256']='f'*64
    with pytest.raises(ValueError,match='STRICT_PREDICTION_BINDING'):
        audit_prediction(p,strict,c,evaluated_at=NOW)


def test_two_paper_policies_preserve_original_owner_and_reflatten_all_stakes():
    p, _, _=inputs(True)
    before=deepcopy(p)
    out=paper_comparison(p,evaluated_at=NOW,authorization_ref='SYNTHETIC_EXPLICIT_PAPER_PERMISSION')
    known=out['studies'][semantic.RESEARCH_POLICY]
    unknown=out['studies'][semantic.UNKNOWN_RESEARCH_POLICY]
    assert known['methods']['EXACTA']['point_count']==0
    assert unknown['methods']['EXACTA']['point_count']==12
    assert unknown['methods']['TRIO']['point_count']==4
    assert unknown['methods']['TRIFECTA']['point_count']==0
    assert unknown['methods']['TRIFECTA']['whole_race_no_bet'] is None
    assert all(r['independent_reflatten_verified'] for r in unknown['method_identity_witness'].values())
    assert out['owner_count']==1 and out['independent_BC'] is False
    assert out['new_krs_executions']==0 and p==before


def test_optional_paper_comparison_requires_current_request_permission():
    p,_,_=inputs()
    with pytest.raises(ValueError,match='AUTHORIZATION_REF'):
        paper_comparison(p,evaluated_at=NOW,authorization_ref='')

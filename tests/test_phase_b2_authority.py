"""Mechanical tests never increment repository forward cohorts."""
import copy
import pytest
from test_phase_b1_forward import capture,result,signed_result,settle,f

@pytest.mark.parametrize('defect',['flag','reference','execution','receipt','digest','signature','outcome'])
def test_result_authority_holds_research_not_production(defect):
    req,fin,pre=capture();art,rreq=result(req);before=copy.deepcopy(fin)
    rreq['official_result_verification_ref']='https://official.test/result'
    env=signed_result(art);verify={'verified':True}
    if defect=='flag':rreq['official_result_verified']=False
    if defect=='reference':rreq.pop('official_result_verification_ref')
    if defect=='execution':rreq.pop('execution_id')
    if defect=='receipt':env['receipt']['race_id']='WRONG'
    if defect=='digest':env['receipt']['artifact_sha256']='WRONG'
    if defect=='signature':verify['verified']=False
    if defect=='outcome':art['official_result']['top3']=[2,1,3]
    m=f.settle_forward_capture(pre,fin,art,result_request=rreq,result_envelope=env,result_verification=verify)
    assert m['status']=='HOLD_RESULT_AUTHORITY' and not m['krs_eligible'] and not m['eligible']
    assert fin==before and m['production_effect']=='NONE'

def test_frozen_candidate_outcome_preserves_disadvantage():
    req,fin,pre=capture();pre['static_prediction'].update(W=['1'],P2=['2'],P3=['3']);pre['candidate']={'candidate_static_prediction':{'ranking':['4','3','2','1'],'W':['4'],'P2':['3'],'P3':['2']}}
    pre['sha256']=f._sha({k:v for k,v in pre.items() if k!='sha256'})
    art,rreq=result(req);x=settle(pre,fin,art,rreq)['candidate_evaluation']
    assert x['paired_winner_rank_difference']==3 and x['role_capture_delta']<0
    assert x['false_W_promotion']==1 and x['false_W_demotion']==1


def test_futility_is_contextual_not_30_race_rule():
    rows=[{'status':'EVALUATED_FROZEN_V01','race_id':venue+'-2099010'+str(i)+'-R01','scheduled_post_at':'2099-01-0'+str(i)+'T01:00:00+00:00','paired_winner_rank_difference':2,'paired_top3_rank_difference':1,'role_capture_delta':-1,'missingness':{'index_saturation':{'1':{'BVI':{'fully_neutral_sub_index':True}}}}} for i,venue in [(1,'FNB'),(2,'URW')]]
    assert f.candidate_futility_review(rows[:1])['decision']=='HOLD_INSUFFICIENT_CONTEXT'
    assert f.candidate_futility_review(rows)['decision'].startswith('EARLY_FUTILITY')
    rows[1]['paired_winner_rank_difference']=-1
    assert f.candidate_futility_review(rows)['decision']=='CONTINUE'

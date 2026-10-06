"""Correctness regression and forward-boundary acceptance for the OHI review."""
import base64
import copy
import datetime as dt
import gzip
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from formal_execution_orchestrator import parse_official_result_snapshot, FormalOrchestrationError, formal_start_preflight
from mec_r4_shadow import settle_ticket_list, official_result_for_settlement
from family_conversion_diagnostics import build_diagnostics, bind_to_trace, settle_diagnostics, forward_status, _sha
from local_mec_r5_oos_tracker import canonical_capture
from post_result_learning import _coverage
from test_family_conversion_diagnostics import request


def snapshot(ranks=(1,1,3), excluded=False, omit=False):
    rows=''.join(f'<tr><td>{rank}</td><td>{horse}</td><td>H{horse}</td></tr>' for rank,horse in zip(ranks,(1,2,5)))
    if excluded:rows+='<tr><td>除外</td><td>10</td><td>Excluded</td></tr>'
    pays='<tr><td>馬連単</td><td>1-2</td><td>260円</td><td>1人気</td></tr>'
    if not omit:pays+='<tr><td>馬連単</td><td>2-1</td><td>240円</td><td>2人気</td></tr>'
    pays+='<tr><td>三連複</td><td>1-2-5</td><td>100円</td><td>1人気</td></tr>'
    pays+='<tr><td>三連単</td><td>1-2-5</td><td>730円</td><td>1人気</td></tr>'
    pays+='<tr><td>三連単</td><td>2-1-5</td><td>650円</td><td>2人気</td></tr>'
    raw=('<h2>2026年10月6日 大井 第2競走 競走成績</h2><table><tr><th>着順</th><th>馬番</th><th>馬名</th></tr>'+rows+'</table><table>'+pays+'</table>').encode()
    return {'http_status':200,'official':True,'raw_gzip_b64':base64.b64encode(gzip.compress(raw)).decode(),
            'raw_sha256':hashlib.sha256(raw).hexdigest(),'content_type':'text/html; charset=utf-8','final_url':'official'}


def test_dead_heat_normal_terminal_and_all_official_winners():
    order,payouts,details=parse_official_result_snapshot(snapshot(excluded=True),{'race_date':'2026-10-06','venue_id':'OHI','race_no':2},[1,2,5,10],detailed=True)
    assert details['dead_heat'] and order==[1,2,5]
    assert details['refund_runner_ids']==[10]
    assert len(details['winning_selections']['EXACTA'])==2
    result=official_result_for_settlement({'finish_order':order,'payouts':payouts,**details})
    tickets=[{'bet_type':bt,'selection':sel,'stake':100} for bt,sel in [('EXACTA',[1,2]),('EXACTA',[2,1]),('TRIFECTA',[1,2,5]),('TRIFECTA',[2,1,5])]]
    settled=settle_ticket_list(tickets,result)
    assert settled['status']=='SETTLED' and settled['return']==1880
    assert len(settled['winning_tickets'])==4


@pytest.mark.parametrize('ranks,omit', [((1,1,2),False),((1,1,3),True)])
def test_bad_rank_or_incomplete_multi_payout_holds(ranks,omit):
    with pytest.raises(FormalOrchestrationError):
        parse_official_result_snapshot(snapshot(ranks=ranks,omit=omit),{'race_date':'2026-10-06','venue_id':'OHI','race_no':2},[1,2,5])


def frozen_final(race):
    folder=ROOT/'runtime/executions'/f'KM-LOCAL-OHI-20261006-R{race:02d}-LIVE-R1'/'FORMAL/runs'
    return json.loads(next(folder.glob('*/final_receipt_envelope.json')).read_text())


def test_r9_refund_regression_keeps_frozen_tickets():
    final=frozen_final(9);before=copy.deepcopy(final)
    request={'finish_order':[2,3,13],'payouts':{'EXACTA':930,'TRIO':26700,'TRIFECTA':46220},
             'refund_runner_ids':[10],'refund_authority':'OHI 2026-10-06 Daily Review / regression-only supplied official exclusion'}
    settled=settle_ticket_list(final['artifact']['final_ticket']['tickets'],official_result_for_settlement(request))
    assert settled['investment']==19700
    assert settled['winning_return']==27630
    assert settled['refund']==2900 and settled['at_risk_capital']==16800
    assert settled['refund_adjusted_pfs']==pytest.approx(164.4642857)
    assert settled['pfs']==pytest.approx(154.9746193)
    assert settled['profit_loss']==10830 and final==before


def test_refund_not_a_hit_and_all_refund_denominator_unknown():
    tickets=[{'bet_type':'TRIO','selection':[1,2,10],'stake':100}]
    result=official_result_for_settlement({'finish_order':[1,2,3],'refund_runner_ids':[10],'refund_authority':'official'})
    settled=settle_ticket_list(tickets,result)
    assert settled['return']==100 and settled['hit_types']==[]
    assert settled['at_risk_capital']==0 and settled['refund_adjusted_pfs'] is None
    result['official_result']['refund_authority']=None
    with pytest.raises(AssertionError,match='REFUND_OFFICIAL_AUTHORITY'):settle_ticket_list(tickets,result)


def test_three_coverage_layers_do_not_confuse_wrong_permutation_with_trio():
    final={'final_prediction_package':{'roles':{'1':['P3'],'4':['W'],'7':['P2']}},'final_ticket':{'tickets':[{'bet_type':'TRIFECTA','selection':[4,1,7],'stake':100}]}}
    c=_coverage(final,[4,7,1])
    assert c['semantic_set_coverage'] and c['exact_oriented_set_coverage']
    assert not c['unordered_monetizable_set_coverage'] and not c['ordered_exact_ticket_coverage']


@pytest.mark.parametrize('race',[1,3,4,7,8,9,11,12])
def test_missing_ohi_captured_from_canonical_attestation_same_frozen_sha(race):
    rid=f'KM-LOCAL-OHI-20261006-R{race:02d}-LIVE-R1'
    legacy=ROOT/"runtime/local_mec_r5_shadow_lineage"/f"{rid}.json"
    before=legacy.read_bytes() if legacy.exists() else None
    shadow,line,settlement,authority=canonical_capture(rid)
    assert line['capture_source']=='CANONICAL_FORMAL_PRE_RESULT_ATTESTATION'
    assert line['shadow_sha256']==shadow['sha256']
    assert settlement['oos_eligible'] and authority['verified']
    legacy=ROOT/'runtime/local_mec_r5_shadow_lineage'/f'{rid}.json'
    assert (legacy.read_bytes() if legacy.exists() else None)==before  # No legacy rewrite.


def diagnostic_inputs():
    req=request();req.update(race_id='KM-LOCAL-OHI-20990101-R01',scheduled_post_at='2099-01-01T12:00:00+09:00',oos_eligible=True)
    req['static_prediction']['ranking']=[7,2,6,8,9]
    req['third_dispositions']=[{'head':7,'second':2,'third':8,'status':'PURCHASE','reason':'PAIR_LOCAL_CURRENT_STAGE_DIRECT_EVIDENCE'}]
    utility={'actionable_ordered_pair_proposals':[{'head':7,'second':9,'actionable':True}],
             'summary':[{'horse_no':h,'ranks':{'SSR-P3':i+1}} for i,h in enumerate([7,2,6,8])]}
    ticket={'tickets':[{'bet_type':'TRIFECTA','selection':[7,2,8],'stake':100,'mec_tier':'CORE'},
                       {'bet_type':'TRIO','selection':[7,2,6],'stake':100,'mec_tier':'TAIL'},
                       {'bet_type':'EXACTA','selection':[7,2],'stake':100,'mec_tier':'CORE'}]}
    return req,utility,ticket


def test_pair_review_is_independently_corroborated_and_pair_local_exact_only():
    req,u,t=diagnostic_inputs();original=copy.deepcopy((req,u,t))
    d=build_diagnostics(req,t,req['static_prediction'],u,'2099-01-01T11:00:00+09:00','basis')
    residual=next(x for x in d['pair_residual_candidates'] if x['second']==9)
    assert residual['terminal']=='PAIR-REVIEW' and not residual['purchase_authority']
    terms={tuple(x['exact']):x['terminal'] for x in d['pair_local_third_terminals']}
    assert terms[(7,2,8)]=='THIRD_EXACT_MATERIAL'
    assert terms[(7,2,6)]=='THIRD_SET_PROTECTION'
    arm=d['daily_improvement_shadow']['arms']['PAIR_LOCAL_SELECTIVE_EXACT']['tickets']
    assert [x['selection'] for x in arm if x['bet_type']=='TRIFECTA']==[[7,2,8]]
    assert (req,u,t)==original
    req['third_dispositions'][0]['reason']='STRUCTURAL_HARD_EXCLUSION'
    d=build_diagnostics(req,t,req['static_prediction'],u,'2099-01-01T11:00:00+09:00','basis')
    assert [7,2,8] not in [x['exact'] for x in d['pair_local_third_terminals']]


def test_market_unknown_stale_quotes_and_protection_measurement():
    req,u,t=diagnostic_inputs()
    def build():return build_diagnostics(req,t,req['static_prediction'],u,'2099-01-01T11:00:00+09:00','basis')['daily_improvement_shadow']
    d=build();assert d['market_payout_sufficiency']['status']=='UNKNOWN'
    assert d['protection_burden']['protection_burden_ratio']==pytest.approx(1/3)
    req['market_payout_snapshot']={'source':'official-market','available_at':'2099-01-01T10:59:00+09:00','quotes':[
        {'bet_type':'TRIFECTA','selection':[7,2,8],'payout_per_100_low':150,'payout_per_100_high':250},
        {'bet_type':'TRIO','selection':[7,2,6],'payout_per_100_low':300,'payout_per_100_high':400}]}
    d=build();assert d['market_payout_sufficiency']['capital_to_payout_mismatches']
    assert d['protection_burden']['selection_specific_market_ceiling_range']==[300,400]
    req['market_payout_snapshot']['available_at']='2099-01-01T11:01:00+09:00'
    assert build()['market_payout_sufficiency']['status']=='UNKNOWN'


def test_consensus_forward_signed_freeze_and_historical_exclusion(tmp_path):
    req,u,t=diagnostic_inputs()
    def create(gen):
        d=build_diagnostics(req,t,req['static_prediction'],u,gen,'basis')
        fin={'artifact':{'race_id':req['race_id'],'ticket_transport_trace':bind_to_trace({},d)},'receipt':{'phase':'FINAL','status':'PASS'},'receipt_sha256':'final'}
        result={'race_id':req['race_id'],'finish_order':[7,2,8],'payouts':{'EXACTA':400,'TRIO':300,'TRIFECTA':1000},'result_available_at':req['scheduled_post_at']}
        auth={'status':'PASS','verified_signed_result':True,'verification_ref':'official','result_receipt_sha256':'result','result_artifact_sha256':'result-art'}
        return d,settle_diagnostics(d,fin,result,auth,final_signature_verified=True)
    d,out=create('2099-01-01T11:00:00+09:00')
    assert d['daily_improvement_shadow']['arms']['CONSENSUS_CORE_3']['core']==[7,2,6]
    assert d['daily_improvement_shadow']['arms']['CONSENSUS_CORE_4']['core']==[7,2,6,8]
    assert out['daily_improvement_measurement']['oos_eligible']
    (tmp_path/'row.json').write_text(json.dumps(out))
    assert forward_status(str(tmp_path))['daily_improvement_cohort']['eligible_races']==1
    req.update(race_id='KM-LOCAL-OHI-20261006-R01',scheduled_post_at='2026-10-06T12:00:00+09:00')
    d,out=create('2026-10-06T11:00:00+09:00')
    assert not out['daily_improvement_measurement']['oos_eligible']


def test_active_universe_and_deadline_margin_preflight(monkeypatch):
    import formal_execution_orchestrator as o
    env={'receipt_sha256':'source','artifact':{'active_runner_universe':{'runners':[{'runner_id':1},{'runner_id':2}]}}}
    monkeypatch.setattr(o,'_load_checkpoint_json',lambda _,name:env if name=='source_receipt_envelope.json' else {'verified':True})
    now=dt.datetime.fromisoformat('2099-01-01T11:50:00+09:00')
    req={'scheduled_post_at':'2099-01-01T12:00:00+09:00','runners':[{'runner_id':1},{'runner_id':2}]}
    assert formal_start_preflight(req,{},now=now)['status']=='PASS'
    req['runners'].append({'runner_id':3})
    with pytest.raises(FormalOrchestrationError,match='ACTIVE_RUNNER'):formal_start_preflight(req,{},now=now)
    req['runners'].pop();now=dt.datetime.fromisoformat('2099-01-01T11:56:00+09:00')
    with pytest.raises(FormalOrchestrationError,match='DEADLINE_MARGIN'):formal_start_preflight(req,{},now=now)


def test_canonical_tamper_fails_without_legacy_fallback(tmp_path,monkeypatch):
    import shutil
    from execution_store import persist_phase
    rid='KM-LOCAL-OHI-20261006-R01-LIVE-R1'
    source=ROOT/'runtime/executions'/rid
    monkeypatch.chdir(tmp_path)
    shutil.copytree(source,tmp_path/'runtime/executions'/rid)
    formal=next((tmp_path/'runtime/executions'/rid/'FORMAL/runs').iterdir())
    stage=tmp_path/'changed';shutil.copytree(formal,stage)
    shadow_path=stage/'local_mec_r5_shadow_pre_result.json'
    sh=json.loads(shadow_path.read_text());sh['arms']['SET_ONLY']['tickets'].append({'bet_type':'TRIO','selection':[1,2,3],'stake':100})
    sh['sha256']=_sha({k:v for k,v in sh.items() if k!='sha256'});shadow_path.write_text(json.dumps(sh))
    persist_phase(rid,'FORMAL','tampered',stage,root=tmp_path/'runtime/executions')
    with pytest.raises(AssertionError,match='SHA_NOT_BOUND'):canonical_capture(rid)


def test_signed_result_api_replays_refund_and_preserves_financial_fields(monkeypatch):
    import importlib.util
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    key=Ed25519PrivateKey.generate().private_bytes(serialization.Encoding.Raw,serialization.PrivateFormat.Raw,serialization.NoEncryption())
    for name,value in {'KM_LOCAL_ENGINE_SHA256':'test-engine','KM_LOCAL_PARAMETER_MAP_SHA256':'test-map',
                       'KM_LOCAL_RECEIPT_SIGNER_KEY_ID':'ACCEPTANCE_ONLY','KM_LOCAL_RECEIPT_PRIVATE_KEY_B64':base64.b64encode(key).decode()}.items():
        monkeypatch.setenv(name,value)
    spec=importlib.util.spec_from_file_location('km_daily_acceptance_app',ROOT/'runtime/local_physical/app.py')
    app=importlib.util.module_from_spec(spec);spec.loader.exec_module(app)
    tickets=[{'bet_type':'EXACTA','selection':[1,2],'stake':100},{'bet_type':'TRIO','selection':[1,2,10],'stake':100}]
    final=app.signed_receipt('FINAL','ACCEPT-R42', 'PASS',{'final_ticket':{'tickets':tickets,'total_investment':200},
        'final_prediction_package':{'roles':{'1':['W'],'2':['P2'],'3':['P3']}},'final_freeze_timestamp':'2099-01-01T01:00:00+00:00'})
    result=app.result({'family_id':'LOCAL','race_id':'ACCEPT-R42','final_receipt':final,
        'official_result':{'finish_order':[1,2,3],'payouts':{'EXACTA':400},'refund_runner_ids':[10],'refund_authority':'official'},
        'result_available_at':'2099-01-01T02:00:00+00:00',
        'settlement':{'status':'COMPLETE','investment':200,'settled_investment':200,'return':500},
        'pfs_authority':'FROZEN-RECOMMENDATION'})
    assert result['receipt']['status']=='PASS'
    assert app.verify_envelope(result)
    s=result['artifact']['settlement']
    assert s['refund']==100 and s['at_risk_capital']==100
    assert s['pfs']==250 and s['refund_adjusted_pfs']==400
    assert result['artifact']['automatic_post_result_review']['capital']['refund_adjusted_pfs']==400


def test_payout_sufficiency_sums_simultaneous_winners_without_ev():
    req,u,t=diagnostic_inputs()
    t['tickets'][1]['selection']=[7,2,8]
    req['market_payout_snapshot']={'source':'market','available_at':'2099-01-01T10:59:00+09:00','quotes':[
        {'bet_type':bt,'selection':sel,'payout_per_100_low':100,'payout_per_100_high':200}
        for bt,sel in [('TRIFECTA',[7,2,8]),('TRIO',[7,2,8]),('EXACTA',[7,2])]]}
    d=build_diagnostics(req,t,req['static_prediction'],u,'2099-01-01T11:00:00+09:00','basis')
    market=d['daily_improvement_shadow']['market_payout_sufficiency']
    assert market['portfolio_outcome_payout_ranges'][0]['return_high']==600
    assert market['portfolio_capital_to_payout_mismatches']==[]
    assert market['ev'] is None
    req['market_payout_snapshot']['quotes'].pop()
    d=build_diagnostics(req,t,req['static_prediction'],u,'2099-01-01T11:00:00+09:00','basis')
    assert d['daily_improvement_shadow']['market_payout_sufficiency']['portfolio_outcome_payout_ranges'][0]['status']=='UNKNOWN'

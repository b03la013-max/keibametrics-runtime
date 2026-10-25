"""Real official-page fact fixtures; original HTTP/signature claims stay separate."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/jra_source_runtime'),str(ROOT/'tests')]
from jra_candidate_postresult_closedloop import (
    PendingOfficialResult, verify_official_result, official_top3_orders,
    official_payout_entries, settle_frozen_candidate,
)
from jra_production_postresult import (
    settle_final, build_result_request, process, verify_archived_final_signature,
    ProductionPostResultError, _sha,
)
from jra_same_day_results import finish_groups_and_top3_orders, parse_result_detail
from post_result_learning import build_post_result_review, build_learning_state
from test_jra_production_postresult import final as synthetic_final
from test_jra_candidate_postresult_closedloop import frozen as synthetic_candidate

FACTS=json.loads((ROOT/'tests/fixtures/jra_20261025_ngt_dead_heat.json').read_text())

def official(fixture):
    return verify_official_result(fixture['parsed'],fixture['official_payout_text_derived'],
                                  [r['runner_id'] for r in fixture['parsed']['runners']])

def carrier(tickets):
    return {'final_ticket':{'tickets':tickets,'total_investment':sum(t['stake'] for t in tickets)}}

@pytest.mark.parametrize('fixture',FACTS['records'],ids=lambda x:x['race_id'])
def test_real_official_fact_fixtures_preserve_both_third_places_and_payouts(fixture):
    assert fixture['raw_http_bytes_available'] is False
    assert fixture['raw_http_bytes_sha256'] is None
    result=official(fixture)
    assert official_top3_orders(result)==fixture['expected_top3_orders']
    assert result['finish_groups'][2]['horse_numbers']==sorted(o[2] for o in fixture['expected_top3_orders'])
    for kind,prices in fixture['expected_payout_entries'].items():
        assert official_payout_entries(result,kind)==prices
    assert isinstance(result['payouts']['EXACTA'],dict)
    assert len(result['payouts']['TRIO'])==len(result['payouts']['TRIFECTA'])==2

@pytest.mark.parametrize('fixture',FACTS['records'],ids=lambda x:x['race_id'])
def test_every_distinct_winning_canonical_ticket_pays_once(fixture):
    result=official(fixture);tickets=[]
    for kind,entries in fixture['expected_payout_entries'].items():
        for entry in entries:tickets.append({'bet_type':kind,'selection':entry['selection'],'stake':100})
    frozen=carrier(tickets);before=deepcopy((frozen,result))
    s=settle_final(frozen,result)
    assert len(s['winning_tickets'])==5
    assert s['total_payout']==sum(p['per_100_yen'] for ps in fixture['expected_payout_entries'].values() for p in ps)
    assert s['total_investment']==500
    assert settle_final(frozen,result)==s
    assert (frozen,result)==before
    with pytest.raises(ProductionPostResultError,match='DUPLICATE_FROZEN_TICKET'):
        settle_final(carrier(tickets+[deepcopy(tickets[0])]),result)
    duplicate=deepcopy(result);duplicate['payouts']['TRIO'].append(deepcopy(duplicate['payouts']['TRIO'][0]))
    with pytest.raises(ProductionPostResultError,match='DUPLICATE_COMBINATION'):
        settle_final(frozen,duplicate)

@pytest.mark.parametrize('fixture',FACTS['records'],ids=lambda x:x['race_id'])
def test_actual_frozen_ngt_tickets_are_not_rewritten_or_inferred_hits(fixture):
    path=ROOT/'runtime/final_artifacts'/(fixture['race_id']+'.json')
    raw=path.read_bytes();f=json.loads(raw)
    checked=verify_official_result(fixture['parsed'],fixture['official_payout_text_derived'],
                                    list(map(str,f['static_prediction']['ranking'])))
    out=settle_final(f,checked)
    assert out['total_payout']==0 and out['pfs']==0
    assert out['total_investment']==f['final_ticket']['total_investment']
    assert out['actual_pfs_status']=='NOT_VERIFIED'
    assert path.read_bytes()==raw

def test_partial_extra_wrong_or_duplicate_dead_heat_payout_is_not_silently_zero():
    fixture=FACTS['records'][0];text=fixture['official_payout_text_derived'];universe=[r['runner_id'] for r in fixture['parsed']['runners']]
    for changed in [text.replace('9-11-14 22070 円',''),
                    text.replace('勝馬の紹介','14-11-9 1000 円 勝馬の紹介'),
                    text.replace('3連単','14-11-9 1920 円 3連単')]:
        with pytest.raises(PendingOfficialResult):verify_official_result(fixture['parsed'],changed,universe)
    with pytest.raises(ValueError,match='UNIVERSE'):
        verify_official_result(fixture['parsed'],text,[n for n in universe if n!='14'])
    result=official(fixture);result['refund_runner_ids']=[14]
    with pytest.raises(ProductionPostResultError,match='REFUND_TOP3_CONFLICT'):
        settle_final(carrier([]),result)

def test_first_and_second_place_ties_use_competition_ranks_and_all_orders():
    first={'official':True,'runners':[{'runner_id':str(n),'horse_no':n,'finish':r} for n,r in [(1,1),(2,1),(3,3)]]}
    text='払戻金 単勝 1 100 円 馬単 1-2 100 円 2-1 200 円 3連複 1-2-3 300 円 3連単 1-2-3 400 円 2-1-3 500 円 勝馬の紹介'
    result=verify_official_result(first,text,['1','2','3'])
    assert result['top3_orders']==[[1,2,3],[2,1,3]]
    second=deepcopy(first);second['runners'][1]['finish']=2;second['runners'][2]['finish']=2
    text='払戻金 単勝 1 100 円 馬単 1-2 100 円 1-3 200 円 3連複 1-2-3 300 円 3連単 1-2-3 400 円 1-3-2 500 円 勝馬の紹介'
    assert verify_official_result(second,text,['1','2','3'])['top3_orders']==[[1,2,3],[1,3,2]]
    malformed=deepcopy(second);malformed['runners'][1]['finish']=malformed['runners'][2]['finish']=3
    with pytest.raises(ValueError,match='RANK_GROUP_INCOMPLETE'):
        finish_groups_and_top3_orders(malformed['runners'])

def test_tied_parsed_html_preserves_rank_groups_without_changing_parser_schema():
    rows=''.join(f'<tr><td>{rank}</td><td>1</td><td>{n}</td><td>馬{n}</td><td></td></tr>'
                 for n,rank in [(9,1),(11,2),(10,3),(14,3)])
    raw=('<table><tr><th>着順</th><th>枠</th><th>馬番</th><th>馬名</th><th>コーナー通過順位</th></tr>'+rows+'</table>').encode()
    parsed=parse_result_detail(raw,'text/html;charset=UTF-8')
    assert [r['finish'] for r in parsed['runners']]==[1,2,3,3]
    assert finish_groups_and_top3_orders(parsed['runners'])['top3_orders']==[[9,11,10],[9,11,14]]
    assert 'finish_groups' not in parsed  # historic SOURCE hashes stay intact

def test_review_retains_joint_orders_and_does_not_count_investment_twice():
    # Synthetic arithmetic control, not a changed historic signed FINAL.
    f=synthetic_final();f['final_ticket']={'tickets':[{'bet_type':'TRIFECTA','selection':[9,11,14],'stake':100}],
                                        'total_investment':100,'no_bet':False}
    f['final_prediction_package']['roles']={'9':['W'],'11':['P2'],'14':['P3']}
    f['sha256']=_sha({k:v for k,v in f.items() if k!='sha256'})
    req=build_result_request(f,official(FACTS['records'][0]),{'parsed':FACTS['records'][0]['parsed']})
    review=build_post_result_review(req,f)
    assert review['prediction']['role_capture']['third_p3'] is True
    assert [x['role_capture']['third_p3'] for x in review['prediction']['dead_heat_order_evaluations']]==[False,True]
    assert review['conversion']['investment']==100
    assert review['capital']['return']==22070
    assert review['failure_localization']['first_material_failure']=='NONE'
    assert build_post_result_review(req,f)==review
    now=datetime.now(timezone.utc).isoformat()
    assert build_learning_state(review,effective_time=now)==build_learning_state(review,effective_time=now)
    changed=deepcopy(req);changed['official_result']['top3_orders'].pop()
    with pytest.raises(ValueError,match='GROUP_BINDING_MISMATCH'):build_post_result_review(changed,f)

def test_candidate_settlement_reuses_identical_multi_payout_arithmetic():
    pre,f=synthetic_candidate();parsed={'official':True,'runners':[
        {'runner_id':str(n),'horse_no':n,'finish':r} for n,r in [(4,1),(8,2),(3,3),(5,3)]]}
    text='払戻金 単勝 4 270 円 馬単 4-8 1240 円 3連複 3-4-8 720 円 4-5-8 800 円 3連単 4-8-3 4850 円 4-8-5 9500 円 勝馬の紹介'
    result=verify_official_result(parsed,text,['3','4','5','8'])
    before=deepcopy((pre,f));out=settle_frozen_candidate(pre,f,result,source_sha256='UNIT_TEST_NOT_RAW_SIGNATURE',source_url='UNIT_TEST')
    assert out['settlement']['recommended_return_yen']==8050
    assert out['settlement']['recommended_stake_yen']==400
    assert out['settlement']['actual_top3_orders']==[[4,8,3],[4,8,5]]
    assert out['settlement']['prediction_measurement']['third_static_rank'] is None
    assert (pre,f)==before

def test_zero_exposure_dead_heat_records_groups_and_keeps_pfs_undefined():
    from test_jra_no_bet_postresult_learning import build_input,run,_hash
    terminal,result=build_input()
    result['runners'][2]['finish']=2
    result['sha256']=_hash({k:v for k,v in result.items() if k not in ('sha256','race_no','source_snapshot_sha256')})
    out=run(terminal,result)
    assert out['official_top3_orders']==[[2,1,3],[2,3,1]]
    assert out['investment']==out['payout']==0 and out['pfs'] is None
    assert out['eligible_for_production_prediction_kpi'] is False

def test_existing_non_dead_heat_review_hashes_and_learning_bindings_remain_exact():
    paths=sorted((ROOT/'runtime/reviews_auto').glob('*2026102[45]*AUTO.json'))
    assert len(paths)>=50
    for path in paths:
        before=path.read_bytes();saved=json.loads(before);rid=saved['race_id']
        result=json.loads((ROOT/'runtime/results'/f'{rid}.json').read_text())
        f=json.loads((ROOT/'runtime/final_artifacts'/f'{rid}.json').read_text())
        review=build_post_result_review(result,f,review_semantics=saved.get('review_semantics','LEGACY'))
        assert review['sha256']==saved['sha256'],rid
        assert path.read_bytes()==before
        state=ROOT/'runtime/learning_states'/f'{rid}.json'
        if state.exists():
            raw=state.read_bytes();learning=json.loads(raw)
            assert learning['source_review_sha256']==saved['sha256'],rid
            assert learning['sha256']==_sha({k:v for k,v in learning.items() if k!='sha256'})
            assert state.read_bytes()==raw

def _copy_trust(root,final):
    authority=final['final_prediction_package']['execution_stage_manifest']['SIGNED_SOURCE_RECEIPT_VERIFIED']['current_authority_manifest']
    profile='profiles/'+authority.replace('-','_')+'.json'
    contracts=json.loads((ROOT/profile).read_text())['common_family_components']['family_runtime_contracts_profile']
    for relative in [profile,contracts,'evidence/jra_bvi_phase3_20261017/runtime_health.json']:
        target=root/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/relative,target)

@pytest.mark.parametrize('mutation',['signature_missing','signature_invalid','payload','cross_race'])
def test_production_process_rejects_unsigned_tampered_or_other_race_before_any_fetch(tmp_path,monkeypatch,mutation):
    rid='KM-JRA-KYO-20261025-R07';f=json.loads((ROOT/'runtime/final_artifacts'/f'{rid}.json').read_text());_copy_trust(tmp_path,f)
    if mutation=='signature_missing':f['final_receipt'].pop('signature')
    elif mutation=='signature_invalid':f['final_receipt']['signature']='AA=='
    elif mutation=='payload':f['final_ticket']['tickets'][0]['stake']+=100;f['final_ticket']['total_investment']+=100
    else:f['race_id']='KM-JRA-KYO-20261024-R07'
    f['sha256']=_sha({k:v for k,v in f.items() if k!='sha256'})
    path=tmp_path/'runtime/final_artifacts'/f'{rid}.json';path.parent.mkdir(parents=True);path.write_text(json.dumps(f))
    def forbidden(*a,**kw):raise AssertionError('NETWORK_OR_DISPATCH_FORBIDDEN')
    monkeypatch.setattr('jra_candidate_postresult_closedloop.fetch_jra_result',forbidden)
    monkeypatch.setattr('jra_production_postresult.subprocess.check_output',forbidden)
    with pytest.raises(ProductionPostResultError,match='SIGNATURE_NOT_VERIFIED|RACE_ID_MISMATCH'):
        process(tmp_path,rid)
    assert not (tmp_path/'runtime/results'/f'{rid}.json').exists()

def test_existing_63_real_signed_finals_pass_existing_offline_signature_verifier(monkeypatch):
    def forbidden(*a,**kw):raise AssertionError('LIVE_HEALTH_OR_NETWORK_FORBIDDEN')
    monkeypatch.setattr('urllib.request.urlopen',forbidden)
    paths=sorted((ROOT/'runtime/final_artifacts').glob('KM-JRA-*-2026102[45]-R*.json'))
    assert len(paths)==63
    for path in paths:
        raw=path.read_bytes();f=json.loads(raw)
        verify_archived_final_signature(f,root=ROOT,race_id=path.stem)
        assert path.read_bytes()==raw

@pytest.mark.parametrize('fixture',FACTS['records'],ids=lambda x:x['race_id'])
def test_actual_rendered_dom_keeps_finish_numbers_separate_from_other_race_numbers(fixture):
    """Rendered DOM is post-result evidence, never the original HTTP payload."""
    race_no=fixture['race_id'][-2:]
    path=ROOT/'tests/fixtures'/f'jra_20261025_ngt{race_no}_rendered_dom.json'
    raw=path.read_bytes();dom=json.loads(raw)
    assert dom['provenance']=='BROWSER_RENDERED_DOM_NOT_RAW_HTTP_RESPONSE'
    assert dom['url']==fixture['official_url']
    assert datetime.fromisoformat(dom['captured_at'].replace('Z','+00:00')).tzinfo is not None
    rendered='\n'.join(dom['tables']).encode('utf-8')
    parsed=parse_result_detail(rendered,'text/html;charset=UTF-8')
    assert [(r['finish'],r['horse_no']) for r in parsed['runners']]==[
        (r['finish'],r['horse_no']) for r in fixture['parsed']['runners']]
    assert finish_groups_and_top3_orders(parsed['runners'])['top3_orders']==fixture['expected_top3_orders']
    by_number={r['horse_no']:r for r in parsed['runners']}
    if race_no=='11':
        assert by_number[9]['horse_name']=='モズナナスター'
        assert by_number[1]['finish']==7
        assert all(r['passing_positions']==[] for r in parsed['runners'])
    else:
        assert by_number[6]['horse_name']=='ビーグラッド'
        assert by_number[6]['finish']==1 and by_number[6]['passing_positions']==[7,6]
        assert by_number[2]['finish']==3 and by_number[2]['passing_positions']==[3,4]
        assert by_number[10]['finish']==3 and by_number[10]['passing_positions']==[3,3]
    # The browser snapshot did not include the payout list; use the separately
    # attributed official-page facts, never invent DOM payout bytes or a SHA.
    from source_acquisition import _html_text
    assert '払戻金' not in _html_text(rendered.decode('utf-8'))
    with pytest.raises(PendingOfficialResult,match='PAYOUT_SECTION_NOT_PUBLISHED'):
        verify_official_result(parsed,_html_text(rendered.decode('utf-8')),
                               [r['runner_id'] for r in parsed['runners']])
    checked=verify_official_result(parsed,fixture['official_payout_text_derived'],
                                   [r['runner_id'] for r in parsed['runners']])
    assert checked['payouts']==official(fixture)['payouts']
    assert path.read_bytes()==raw

@pytest.mark.parametrize('fixture',FACTS['records'],ids=lambda x:x['race_id'])
def test_actual_rendered_payout_dom_matches_every_distinct_supported_payout(fixture):
    import re
    from source_acquisition import _html_text
    from jra_candidate_postresult_closedloop import parse_official_payouts
    path=ROOT/'tests/fixtures/jra_20261025_ngt1112_payout_rendered_dom.json'
    raw=path.read_bytes();dom=json.loads(raw)
    assert dom['provenance']=='BROWSER_RENDERED_DOM_NOT_RAW_HTTP_RESPONSE'
    assert dom['url']=='https://www.jra.go.jp/JRADB/accessH.html'
    race_no=fixture['race_id'][-2:]
    race=next(r for r in dom['races'] if r['id']==f'harai_{race_no}R')
    text=_html_text(race['html'])
    # The captured race container excludes the page's 払戻金 heading. This
    # explicit parser adapter is derived text, not original response bytes.
    assert '払戻金' not in text
    derived='払戻金 '+text[text.index('単勝 '):]
    payouts=parse_official_payouts(derived)
    checked=verify_official_result(fixture['parsed'],derived,
                                    [r['runner_id'] for r in fixture['parsed']['runners']])
    for kind,expected in fixture['expected_payout_entries'].items():
        assert official_payout_entries(checked,kind)==expected
    assert payouts==official(fixture)['payouts']
    # Additional payouts are evidence only; Production bet kinds stay fixed.
    place=text.split('複勝 ',1)[1].split('枠連 ',1)[0]
    wide=text.split('ワイド ',1)[1].split('3連複 ',1)[0]
    places=[(int(n),int(yen.replace(',',''))) for n,yen in
            re.findall(r'(\d{1,2})\s+([\d,]+)\s+円',place)]
    wides=[(tuple(map(int,n.split('-'))),int(yen.replace(',',''))) for n,yen in
            re.findall(r'(\d{1,2}-\d{1,2})\s+([\d,]+)\s+円',wide)]
    if race_no=='11':
        assert places==[(9,290),(11,140),(10,530),(14,110)]
        assert wides==[((9,11),870),((9,10),3260),((9,14),580),((10,11),1470),((11,14),230)]
    else:
        assert places==[(6,620),(7,520),(2,180),(10,130)]
        assert wides==[((6,7),7860),((2,6),3680),((6,10),1530),((2,7),2350),((7,10),1110)]
    assert path.read_bytes()==raw

@pytest.mark.parametrize('case',['dead_heat','normal','shadow_error'])
def test_workflow_skips_unsupported_dead_heat_shadow_kpi_without_blocking_production(tmp_path,monkeypatch,case):
    """Run the actual post-signature workflow block; never call the Runtime."""
    import os
    from test_jra_result_persistence import _production_closed_loop_code
    from post_result_learning import build_post_result_review,build_learning_state
    from krs_oos_promotion_gate import build_oos_measurement,evaluate_r30
    from race_day_fast_reflection import build_fast_reflection
    import jra_role_learning_shadow
    if case=='dead_heat':
        fixture=FACTS['records'][0];rid=fixture['race_id']
        final_raw=(ROOT/'runtime/final_artifacts'/f'{rid}.json').read_bytes()
        final=json.loads(final_raw)
        result=build_result_request(final,official(fixture),{'parsed':fixture['parsed']})
    else:
        rid='KM-JRA-TKY-20261018-R11'
        final_raw=(ROOT/'runtime/final_artifacts'/f'{rid}.json').read_bytes()
        final=json.loads(final_raw)
        result=json.loads((ROOT/'runtime/results'/f'{rid}.json').read_text())
    final_path=tmp_path/'runtime/final_artifacts'/f'{rid}.json'
    final_path.parent.mkdir(parents=True);final_path.write_bytes(final_raw)
    calls=[]
    def persist(*args,**kwargs):
        assert case!='dead_heat','REPRESENTATIVE_ONLY_SHADOW_MUST_NOT_RUN'
        calls.append((args,kwargs))
        if case=='shadow_error':raise ValueError('offline injected research error')
        return {'status':'SETTLED','test_only':True}
    monkeypatch.setattr(jra_role_learning_shadow,'persist_shadow_result',persist)
    monkeypatch.chdir(tmp_path)
    stamp=datetime.now(timezone.utc).isoformat()
    krs_calls=[]
    def measure(*args):
        assert case!='dead_heat','REPRESENTATIVE_ONLY_KRS_MEASUREMENT_MUST_NOT_RUN'
        krs_calls.append(args)
        return build_oos_measurement(*args)
    env=dict(json=json,os=os,p=deepcopy(result),
             settle_mec_r4_shadow=lambda *a:pytest.fail('no shadow fixture exists'),
             build_post_result_review=build_post_result_review,
             build_learning_state=lambda r,**kw:build_learning_state(r,effective_time=stamp),
             build_oos_measurement=measure,build_fast_reflection=build_fast_reflection)
    exec(_production_closed_loop_code(),env)
    assert env['review']==build_post_result_review(result,final,review_semantics='DECISION_AWARE_V2')
    assert env['learning']==build_learning_state(env['review'],effective_time=stamp)
    checkpoint=tmp_path/'runtime_out/result_checkpoint'
    assert json.loads((checkpoint/'post_result_review.json').read_text())==env['review']
    assert json.loads((checkpoint/'learning_state.json').read_text())==env['learning']
    assert env['p']==result and final_path.read_bytes()==final_raw
    if case=='dead_heat':
        assert calls==krs_calls==[] and env['oos'] is None
        assert env['oos_diagnostic']=={'status':'NOT_SETTLED',
            'reason':'UNKNOWN_DEAD_HEAT_RANK_EVALUATION','production_effect':'NONE'}
        assert env['role_shadow_result']=={'status':'NOT_SETTLED',
            'reason':'UNKNOWN_DEAD_HEAT_RANK_EVALUATION','production_effect':'NONE'}
    elif case=='normal':
        assert len(calls)==1 and env['role_shadow_result']['status']=='SETTLED'
    else:
        assert len(calls)==1 and env['role_shadow_result']['status']=='NOT_SETTLED'
        assert 'offline injected research error' in env['role_shadow_result']['reason']
    if case!='dead_heat':
        assert len(krs_calls)==1 and env['oos_diagnostic'] is None
        assert env['oos']==build_oos_measurement(env['review'],final,result)
    # Run the actual persistence/aggregation block too. Even if a historic
    # representative-only measurement exists, preserve it without counting it
    # in this unsupported result's current aggregate.
    import textwrap
    workflow=(ROOT/'.github/workflows/km-formal-result-runner.yml').read_text()
    start=workflow.index('          if not candidate_only:\n              os.makedirs("runtime/reviews_auto"')
    end=workflow.index('              # Forward MEC-R4 OOS',start)
    measurement=tmp_path/'runtime/krs_oos_measurements'/f'{rid}.json'
    measurement.parent.mkdir(parents=True)
    old=b'{"eligible":true,"opaque_historic_measurement":"do not overwrite"}\n'
    if case=='dead_heat':measurement.write_bytes(old)
    # A subsequent ordinary race must not count a previous tied measurement.
    # Keep the old result and measurement exactly as found.
    historic_rid=FACTS['records'][1]['race_id']
    historic_measurement=measurement.parent/f'{historic_rid}.json'
    historic_measurement.write_bytes(old)
    historic_result=tmp_path/'runtime/results'/f'{historic_rid}.json'
    historic_result.parent.mkdir(parents=True)
    historic_raw=json.dumps({'official_result':official(FACTS['records'][1])}).encode()
    historic_result.write_bytes(historic_raw)
    seen=[]
    def aggregate(rows):
        seen.extend(rows)
        return evaluate_r30(rows)
    env['evaluate_r30']=aggregate
    exec(compile(textwrap.dedent(workflow[start:end]),'<actual-result-workflow-persistence>','exec'),env)
    assert json.loads((tmp_path/'runtime/reviews_auto'/f'{rid}-AUTO.json').read_text())==env['review']
    assert json.loads((tmp_path/'runtime/learning_states'/f'{rid}.json').read_text())==env['learning']
    if case=='dead_heat':
        assert measurement.read_bytes()==old and seen==[]
        assert env['r30']['eligible_races']==0
    else:
        assert seen==[env['oos']]
        assert json.loads(measurement.read_text())==env['oos']
    assert historic_measurement.read_bytes()==old
    assert historic_result.read_bytes()==historic_raw
    assert {'race_id':historic_rid,'reason':'UNKNOWN_DEAD_HEAT_RANK_EVALUATION'} in env['krs_oos_aggregate_exclusions']

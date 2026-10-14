"""Real NAR HTML parser fixtures + explicitly synthetic temporal/signing contexts.
Live cryptographic acceptance is stored separately, never inferred from these.
"""
import copy,datetime,gzip,json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'runtime'))
from runtime.local_race_key_shadow_owner import bind_market_evidence,market_source_manifest,_sha,ShadowOwnerError
from runtime.local_physical.source_acquisition import snapshot_from_bytes

TICKETS=[{'bet_type':'EXACTA','selection':['4','10'],'stake':100},
         {'bet_type':'TRIO','selection':['10','4','1'],'stake':100},
         {'bet_type':'TRIFECTA','selection':['4','10','1'],'stake':100}]


def context(final=False):
    q={'family_id':'LOCAL','race_id':'SYNTHETIC-MARKET-CONTEXT','venue_id':'KAW','race_date':'2026-10-14','race_no':4,
       'prediction_cutoff':'2026-10-14T06:14:00+00:00','scheduled_post_at':'2026-10-14T07:15:00+00:00',
       'runners':[{'runner_id':i} for i in range(1,13)],'market_max_age_seconds':120}
    m=market_source_manifest(q);sources=[]
    for spec in m['sources']:
        page=spec['url'].split('/')[-1].split('?')[0]
        p=ROOT/'evidence/aki_market_20261015/parser_fixtures'/(page+'.html')
        if not p.exists():continue
        raw=p.read_bytes()
        if not final:
            raw=raw.replace('（最終）'.encode(), '15:00現在'.encode()).replace('(最終)'.encode(),'15:00現在'.encode())
        snap,_=snapshot_from_bytes(spec,raw,final_url=spec['url'],status_code=200,headers={'content-type':'text/html;charset=utf-8'},
             fetched_at='2026-10-14T06:00:30+00:00',prediction_cutoff=q['prediction_cutoff'])
        sources.append(snap)
    a={'race_id':q['race_id'],'source_race_context':{'venue_id':'KAW','race_date':'2026/10/14','race_no':4},
       'official_runner_universe':{'runners':q['runners']},'source_freeze_at':'2026-10-14T06:01:00+00:00',
       'source_snapshot_sha256':'SYNTHETIC-SOURCE-BASIS','sources':sources,
       'normalized_evidence':{'start_time':{'authority':'NAR_OFFICIAL','value':'16:15'}}}
    return q,seal(a)


def seal(a):
    r={'race_id':a['race_id'],'phase':'SOURCE','status':'SOURCE_FROZEN','artifact_sha256':_sha(a)}
    return {'artifact':a,'receipt':r,'receipt_sha256':_sha(r)}


def bind(q,e,**kw):
    return bind_market_evidence(q,e,signatures_verified=True,tickets=TICKETS,
         frozen_at='2026-10-14T06:02:00+00:00',selection_sha256='SYNTHETIC-SELECTION',**kw)


def test_literal_official_combination_prices_and_order():
    q,e=context();b=bind(q,e)
    assert [x['quoted_odds'] for x in b['ticket_price_coverage']]==[12.2,10.6,39.1]
    assert b['market_payout_sufficiency']=='SUFFICIENT_OBSERVED_PRICES'
    assert b['economic_action']=='PAPER_ONLY / EV_UNCALIBRATED'
    assert b['panels']['EXACTA']['prices']['10-4']==22.1
    assert 'expected_value' not in b and 'kelly' not in b


def test_real_final_odds_cannot_become_prestart_by_late_cutoff():
    q,e=context(final=True);b=bind(q,e)
    assert b['market_payout_sufficiency']=='UNKNOWN'
    assert all(not x['usable'] for x in b['ticket_price_coverage'])
    assert 'FINAL_ODDS_NOT_PRESTART_EVIDENCE' in b['panels']['TRIFECTA']['reasons']


@pytest.mark.parametrize('field,value', [('race_no',5),('venue_id','OHI'),('race_date','2026-10-15')])
def test_cross_race_rejected(field,value):
    q,e=context();q[field]=value
    with pytest.raises(ShadowOwnerError,match='IDENTITY'):bind(q,e)


def test_runner_universe_mismatch_rejected():
    q,e=context();q['runners']=copy.deepcopy(q['runners']);q['runners'].pop()
    with pytest.raises(ShadowOwnerError,match='UNIVERSE'):bind(q,e)


def test_signature_required():
    q,e=context()
    with pytest.raises(ShadowOwnerError,match='SIGNATURE'):
        bind_market_evidence(q,e,signatures_verified=False,frozen_at=q['prediction_cutoff'],selection_sha256=None)


def test_raw_tamper_rejected_even_with_rehashed_outer_source():
    q,e=context();e['artifact']['sources'][0]['raw_sha256']='0'*64;e=seal(e['artifact'])
    with pytest.raises(ShadowOwnerError,match='RAW_HASH'):bind(q,e)


@pytest.mark.parametrize('cutoff,freeze', [('2026-10-14T06:02:00+00:00','2026-10-14T06:02:00+00:00'),
                                         ('2026-10-14T06:14:00+00:00','2026-10-14T06:00:59+00:00')])
def test_cutoff_and_fetch_completion_are_fail_closed(cutoff,freeze):
    q,e=context();q['prediction_cutoff']=cutoff
    b=bind_market_evidence(q,e,signatures_verified=True,tickets=TICKETS,frozen_at=freeze,selection_sha256='X')
    assert b['market_payout_sufficiency']=='UNKNOWN'


def test_stale_and_unknown_update_not_usable():
    q,e=context();q['market_max_age_seconds']=1
    assert bind(q,e)['market_payout_sufficiency']=='UNKNOWN'
    q.pop('market_max_age_seconds');assert bind(q,e)['market_payout_sufficiency']=='UNKNOWN'


def test_missing_trifecta_not_inferred_from_other_prices():
    q,e=context();e['artifact']['sources']=[s for s in e['artifact']['sources'] if 'Odds3LenTan' not in s['final_url']];e=seal(e['artifact'])
    b=bind(q,e);assert b['ticket_price_coverage'][-1]['quoted_odds'] is None
    assert b['market_payout_sufficiency']=='UNKNOWN'


def test_ticket_and_selection_binding_no_results():
    q,e=context();b=bind(q,e)
    assert b['ticket_sha256']==_sha(TICKETS) and b['selection_sha256']=='SYNTHETIC-SELECTION'
    assert b['sha256']==_sha({k:v for k,v in b.items() if k!='sha256'})
    assert b['actual_purchase_pfs'] is None


def test_zero_prices_not_interpreted_as_payouts():
    q,e=context();b=bind(q,e)
    assert all(v>0 for p in b['panels'].values() for v in p['prices'].values())


def test_previous_hash_or_chronology_cannot_be_forged():
    q,e=context();b=bind(q,e)
    with pytest.raises(ShadowOwnerError,match='PREVIOUS'):bind(q,e,previous=b)
    b['frozen_at']='2026-10-14T05:59:00+00:00'
    with pytest.raises(ShadowOwnerError,match='PREVIOUS'):bind(q,e,previous=b)


def test_manifest_does_not_change_production_default():
    from runtime.local_physical.nar_source_manifest import build_local_nar_manifest
    q,e=context();old=build_local_nar_manifest(q);new=market_source_manifest(q)
    assert all('Odds3' not in x['url'] for x in old['sources'])
    assert len(new['sources'])==5 and new['production_consumption_authorized'] is False


def test_actual_signed_unreleased_snapshot_remains_unknown():
    base=ROOT/'evidence/aki_market_20261015/live_prices'
    e=json.loads(gzip.decompress((base/'source_receipt.json.gz').read_bytes()))
    q=json.loads((ROOT/'evidence/aki_market_20261015/request.json').read_text())
    b=bind_market_evidence(q,e,signatures_verified=True,tickets=[],
        frozen_at='2026-10-14T23:00:00+00:00',selection_sha256=None)
    assert b['panels']['WIN_PLACE']['status']=='NOT_ON_SALE'
    assert b['market_payout_sufficiency']=='UNKNOWN'
    assert not b['ticket_price_coverage'] and not b['production_authority']


def test_price_change_requires_verified_chronological_fetches():
    q,e=context();first=bind(q,e)
    for s in e['artifact']['sources']:
        s['fetched_at']='2026-10-14T06:03:00+00:00'
        s['snapshot_sha256']=_sha({k:v for k,v in s.items() if k!='snapshot_sha256'})
    e['artifact']['source_freeze_at']='2026-10-14T06:03:30+00:00';e=seal(e['artifact'])
    second=bind_market_evidence(q,e,signatures_verified=True,tickets=TICKETS,
        frozen_at='2026-10-14T06:04:00+00:00',selection_sha256='X',previous=first,previous_signatures_verified=True)
    assert second['price_changes']['EXACTA']['4-10']==0
    assert second['previous_binding_sha256']==first['sha256']
    assert 'NO_STABILITY_CLAIM' in second['price_change_authority']


def test_no_bet_empty_ticket_binding_cannot_be_sufficient():
    q,e=context()
    b=bind_market_evidence(q,e,signatures_verified=True,tickets=[],
        frozen_at='2026-10-14T06:02:00+00:00',selection_sha256='X')
    assert b['market_payout_sufficiency']=='UNKNOWN'
    assert b['ticket_sha256']==_sha([])


def test_real_frozen_pipeline_market_observation_preserves_selection_capital_and_no_bet():
    from runtime.local_nar_evidence_candidate import compile_candidate_evidence
    from runtime.local_fullnumerical_candidate import materialize_candidate
    from runtime.local_krs_bridge_candidate import build_candidate_prediction
    from runtime.local_race_key_shadow_owner import compile_candidate_portfolio,compact_portfolio
    eid='KM-LOCAL-KAW-20261014-R04-LIVE-R1'
    source_path=next((ROOT/'runtime/executions'/eid/'FORMAL').rglob('source_receipt_envelope.json'))
    envelope=json.loads(source_path.read_text());source=envelope['artifact']
    req=json.loads((ROOT/'runtime/formal_intents'/(eid+'.json')).read_text())
    q=build_candidate_prediction(materialize_candidate(compile_candidate_evidence(source,req)))
    plain=compile_candidate_portfolio(q,source,budget=0)
    bound=compile_candidate_portfolio(q,source,budget=0,market=envelope,market_signatures_verified=True,
        frozen_at=source['source_freeze_at'])
    assert bound['selection_sha256']==plain['selection_sha256']
    assert bound['variants']==plain['variants'] and bound['capital_variants']==plain['capital_variants']
    assert all(not x['tickets'] for x in bound['capital_variants'].values())
    assert all(x['market_payout_sufficiency']=='UNKNOWN' for x in bound['market_evidence'].values())
    assert compact_portfolio(bound)['market_evidence']==bound['market_evidence']


def test_recovered22_does_not_rewrite_frozen17_or_create_forward_credit():
    root=ROOT/'research/aki_market_20261015/comparison22'
    r=json.loads(gzip.decompress((root/'full_report.json.gz').read_bytes()))
    assert len(r['rows'])==22
    old=[x for x in r['rows'] if x['date']<'2026-10-14']
    assert len(old)==17
    expected={'A_PRODUCTION':(361000,193310),'B_ORIGINAL_AKI':(17800,10700),
              'PR262_REFERENCE':(85800,98260),'C_SELECTION':(89800,69550)}
    for arm,money in expected.items():
        assert (sum(x['arms'][arm]['investment'] for x in old),sum(x['arms'][arm]['return'] for x in old))==money
    assert r['candidate_forward_oos']==0
    for row in r['rows']:
        assert row['selection']['sha256']==_sha({k:v for k,v in row['selection'].items() if k!='sha256'})
        assert all(x.get('removed_capital') is None for x in row['selection']['conditional_audit']['excluded_pairs'])
    a=json.loads(gzip.decompress((root/'residual_audit.json.gz').read_bytes()))
    assert all(not s['paper_tickets'] for row in a['capital_paper_budget_scenarios'] for s in row['scenarios'] if s['capital']['decision']=='NO_BET')
    assert sum(s['capital']['decision']=='NO_BET' for row in a['capital_paper_budget_scenarios'] for s in row['scenarios'])==132


def test_cached_probe_terminal_never_bypasses_source_verification(tmp_path,monkeypatch):
    from tools import local_kaw_candidate_comparison as tool
    root=ROOT/'evidence/aki_market_20261015'
    q=json.loads((root/'request.json').read_text());request=tmp_path/'request.json';request.write_text(json.dumps(q))
    out=tmp_path/'saved';out.mkdir()
    e=json.loads(gzip.decompress((root/'live_prices/source_receipt.json.gz').read_bytes()))
    b=json.loads((root/'live_prices/market_binding.json').read_text()) if (root/'live_prices/market_binding.json').exists() else json.loads((root/'live_prices_final_binding.json').read_text())
    for name,obj in [('source_receipt',e),('market_binding',b),('terminal',{'source_ref':e['receipt_sha256'],'binding_sha256':b['sha256']})]:
        (out/(name+'.json')).write_text(json.dumps(obj))
    called=[]
    monkeypatch.setattr(tool,'verify',lambda job:called.append(job) or {'offline_signature':False})
    with pytest.raises(ValueError,match='CACHED_SIGNATURE'):tool.market_probe(request,out)
    assert len(called)==1


def test_supplied_post_cannot_extend_official_race_clock():
    q,e=context();q['scheduled_post_at']='2026-10-14T08:15:00+00:00'
    with pytest.raises(ShadowOwnerError,match='OFFICIAL_POST_TIME'):bind(q,e)

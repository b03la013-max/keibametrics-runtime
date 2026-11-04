"""Mechanical fixtures only; real HTTP acceptance is separately retained."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib
import json
from datetime import timedelta
import pytest
from runtime import local_fnb_multisource as multi
from runtime.local_fnb_rakuten_reference import parse_card

NOW=datetime(2026,11,4,0,0,tzinfo=timezone.utc)

def fixture_card():
    rows=[]
    for rid in (1,2):
        frame='<th class="position">1</th>' if rid==1 else ''
        rows.append(f'''<tr>{frame}<td class="number">{rid}</td><td class="myForecast">-</td>
          <td class="name">父{rid}<br><span class="mainHorse"><a href="https://keiba.rakuten.co.jp/horse_detail/detail/HORSEID/{100+rid}">機械試験馬{rid}</a></span><br>母{rid}<div class="append">(母父{rid})<span class="rate">0.0（-人気）</span>2024/1/1生</div></td>
          <td class="profile">牡2<br>鹿毛<br>55.0<br><a>試験騎手</a><br>試験厩舎</td>
          <td class="weight">-</td><td class="weightDistance">-</td>
          <td class="race"><div class="firstInfo"><span class="place">1</span><span class="stateInfo">良</span><span class="numberInfo">8頭</span></div>
          船橋 26.10.01<br><span class="raceName">２歳新馬</span><br>２歳<br>1200左ダ 2人<br>試験騎手 54.0<br>1:17.0 (0.5)<br>40.0 470k 1番<br>1-1-1<br>相手</td>
          <td class="race"><div class="firstInfo"><span class="place">取止</span><span class="stateInfo">良</span><span class="numberInfo"></span></div>浦和 26.09.01<br><span class="raceName">２歳</span><br>1400左ダ -人<br>試験騎手 54.0<br>470k 1番</td>
          <td>-</td><td>-</td><td>-</td></tr>''')
    raw=('''<h1>船橋競馬場 1R 出馬表</h1><div class="raceNote">2026年11月6日 船橋競馬 ダ1,200m 発走時刻14:45<h2>２歳六</h2></div><table><tbody class="raceCard">'''+''.join(rows)+'</tbody></table>').encode()
    capture={'source_url':'https://keiba.rakuten.co.jp/race_card/list/RACEID/202611061914080501',
        'http_status':200,'raw_sha256':hashlib.sha256(raw).hexdigest(),'captured_at':NOW.isoformat()}
    return raw,capture,{'race_date':'2026-11-06','race_no':1,'venue_id':'FNB'}

def test_original_namespaced_ids_cancelled_history_and_winner_difference():
    raw,capture,race=fixture_card();r=parse_card(raw,capture=capture,race=race,now=NOW)
    assert r['listed_count']==2
    assert [x['frame_no'] for x in r['runners']]==[1,1]
    assert r['active_universe_verified'] is False
    h=r['runners'][0]
    assert h['provider_horse_id']=='101' and h['official_horse_id'] is None
    assert h['odds'] is None and h['popularity'] is None
    assert len(h['starts'])==len(h['non_completed_history'])==1
    assert h['starts'][0]['margin']==0 and h['starts'][0]['printed_time_difference']==.5
    assert h['starts'][0]['content_positions']==[1,1,1]

@pytest.mark.parametrize('changed',[b'\n',b'<h1>wrong</h1>'])
def test_modified_bytes_never_reuse_an_original_capture_hash(changed):
    raw,capture,race=fixture_card()
    with pytest.raises(ValueError,match='HASH_INVALID'):
        parse_card(raw+changed,capture=capture,race=race,now=NOW)


def test_unprinted_history_direction_is_unknown_without_dropping_other_facts():
    raw,capture,race=fixture_card();raw=raw.replace('1200左ダ'.encode(),'1200ダ'.encode())
    capture['raw_sha256']=hashlib.sha256(raw).hexdigest()
    parsed=parse_card(raw,capture=capture,race=race,now=NOW)
    start=parsed['runners'][0]['starts'][0]
    assert start['direction'] is None and start['distance']==1200 and start['surface']=='DIRT'
    assert start['content_positions']==[1,1,1] and start['field_size']==8

def test_wrong_race_header_is_not_resolved_from_url():
    raw,capture,race=fixture_card();raw=raw.replace('船橋競馬場 1R'.encode(),'船橋競馬場 2R'.encode())
    capture['raw_sha256']=hashlib.sha256(raw).hexdigest()
    with pytest.raises(ValueError,match='RACE_NUMBER_CONFLICT'):
        parse_card(raw,capture=capture,race=race,now=NOW)

def test_nar_retired_before_callback_and_independent_route_still_attempted(tmp_path):
    r=multi.acquire_available([
        {'provider':'NAR_OFFICIAL','url':'https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/DebaTable'},
        {'provider':'RAKUTEN_KEIBA','url':'https://keiba.rakuten.co.jp/race_card/list/RACEID/202611061914080501'}],{},
        intent={'venue_id':'FNB','race_date':'2026-11-06','race_no':1},actor_id='MECHANICAL',
        now=NOW,private_root=tmp_path/'private',clock=lambda:NOW)
    assert [x['status'] for x in r['provider_receipts']]==['RETIRED_ARCHIVE_ONLY','HOLD']
    assert r['provider_receipts'][1]['reason']=='MULTISOURCE_PROVIDER_BINDING_NOT_CONNECTED'
    assert not multi.execution_targets([{'provider':'NAR_OFFICIAL'}])
    # Archive validation retains the true historic source label and host.
    assert multi.validate_url('NAR_OFFICIAL','https://www.keiba.go.jp/history').netloc=='www.keiba.go.jp'


def reference_publication(tmp_path):
    """Synthetic presentation only; no claim of actual calculations or LIVE."""
    from runtime.local_reference_delivery import sha
    raw,capture,intent=fixture_card()
    rows=[f'|{i}|機械試験馬{i}|UNKNOWN|UNKNOWN|UNKNOWN|' for i in (1,2)]
    body='TEST_SYNTHETIC_ONLY\n'+'\n'.join(rows)+'''\nW参考候補：UNKNOWN
P2参考候補：UNKNOWN
P3参考候補：UNKNOWN
## 最終参考結論
UNKNOWN
## 元の全29指数・全Role・S1/S2/R16全券面とStake
TEST_SYNTHETIC_ONLY_NO_REAL_NUMERICS_OR_TICKETS
'''
    manifest={**intent,'classification':'REFERENCE','runner_count':2,
        'runners':[{'runner_id':str(i),'name':f'機械試験馬{i}'} for i in (1,2)],
        'required_parts':rows,'body_sha256':hashlib.sha256(body.encode()).hexdigest(),
        'observation_raw_sha256':hashlib.sha256(raw).hexdigest(),'observation_capture':capture,
        'source_fetched_at':NOW.isoformat(),'forecast_frozen_at':(NOW+timedelta(seconds=1)).isoformat(),
        'prepared_at':(NOW+timedelta(seconds=2)).isoformat(),'prediction_cutoff':'2026-11-06T14:40:00+09:00',
        **{k:False for k in ('formal_final_proven','signed_final_claim','recipient_delivery_ack',
                            'natural_delivery_verified','actual_purchase')}}
    manifest['sha256']=sha(manifest)
    folder=tmp_path/'reference';folder.mkdir()
    (folder/'manifest.json').write_text(json.dumps(manifest))
    (folder/'answer.md').write_text(body);(folder/'observation.html').write_bytes(raw)
    return folder,manifest,intent


def test_normal_reference_readback_does_not_call_source_or_engine(tmp_path,monkeypatch):
    from runtime import local_fnb_r20_chat_completion as r20
    from runtime import local_fnb_research_runtime as compute
    folder,m,i=reference_publication(tmp_path)
    monkeypatch.delenv('CI',raising=False);monkeypatch.delenv('GITHUB_ACTIONS',raising=False)
    def forbidden(*a,**k):pytest.fail('existing REFERENCE must not fetch, calculate or sign')
    monkeypatch.setattr(compute,'execute_krs',forbidden)
    r=r20.complete('2026-11-06 船橋1R',tmp_path,now=NOW+timedelta(seconds=3),
        producers={'entry_mode':'FNB_ALTERNATIVE_PROVIDER_SINGLE_OWNER_V1',
                   'source':forbidden,'reference':lambda **kw:folder})
    assert r['status']=='VERIFIED_REFERENCE_BODY_READY_TO_RENDER'
    assert r['body']==(folder/'answer.md').read_text()
    assert not r['formal_final_proven'] and not r['recipient_delivery_ack']


def test_explicit_formal_failure_still_returns_independent_reference(tmp_path,monkeypatch):
    from runtime import local_fnb_r20_chat_completion as r20
    folder,m,i=reference_publication(tmp_path);raw,capture,_=fixture_card()
    request={**i,'family_id':'LOCAL','race_id':'KM-LOCAL-FNB-20261106-R01-LIVE-SYNTHETIC',
        'scheduled_post_at':'2026-11-06T14:45:00+09:00','prediction_cutoff':m['prediction_cutoff']}
    monkeypatch.delenv('CI',raising=False);monkeypatch.delenv('GITHUB_ACTIONS',raising=False)
    r=r20.complete('2026-11-06 船橋1R 正式予測',tmp_path,now=NOW+timedelta(seconds=3),
        producers={'entry_mode':'FNB_ALTERNATIVE_PROVIDER_SINGLE_OWNER_V1',
            'source':lambda **kw:{'raw':raw,'capture':capture,'request':request},
            'reference':lambda **kw:folder})
    assert r['status']=='VERIFIED_REFERENCE_BODY_READY_TO_RENDER'
    assert r['formal']['reason']=='ALTERNATIVE_SOURCE_SIGNED_RECEIPT_MISSING'
    assert r['formal']['status']=='EXECUTION_HOLD_NOT_NO_BET'
    assert not r['formal_final_proven']


@pytest.mark.parametrize('damage',['body','raw','race','formal','missing-horse-rehashed','truncated-rehashed','future-observation'])
def test_reference_does_not_relabel_corruption_or_future_evidence(tmp_path,damage):
    from runtime.local_fnb_rakuten_reference import read_saved_reference
    from runtime.local_reference_delivery import sha
    folder,m,i=reference_publication(tmp_path)
    if damage=='body':(folder/'answer.md').write_text('truncated')
    elif damage=='raw':(folder/'observation.html').write_bytes(b'wrong')
    elif damage=='race':m['race_no']=2
    elif damage=='formal':m['formal_final_proven']=True
    elif damage=='future-observation':m['prepared_at']=NOW.isoformat()
    else:
        body=(folder/'answer.md').read_text()
        if damage=='missing-horse-rehashed':
            body=body.replace(m['required_parts'][0],'MISSING')
            m['required_parts'][0]='MISSING'
        else:body=body.split('## 最終参考結論')[0]
        m['body_sha256']=hashlib.sha256(body.encode()).hexdigest()
        (folder/'answer.md').write_text(body)
    m['sha256']=sha({k:v for k,v in m.items() if k!='sha256'})
    (folder/'manifest.json').write_text(json.dumps(m))
    with pytest.raises(ValueError,match='REFERENCE_FROZEN'):
        read_saved_reference(folder,i,now=NOW+timedelta(seconds=3))


def test_saved_reference_after_cutoff_keeps_original_time_and_no_prestart_delivery_claim(tmp_path):
    from runtime.local_fnb_rakuten_reference import read_saved_reference
    folder,m,i=reference_publication(tmp_path)
    r=read_saved_reference(folder,i,now=datetime(2026,11,7,tzinfo=timezone.utc))
    assert r['manifest']['prepared_at']==m['prepared_at']
    assert r['prestart_at_readback'] is False and not r['recipient_delivery_ack']


def test_reference_revision_can_change_without_reusing_the_old_race_id():
    from runtime.local_fnb_rakuten_reference import materialize_reference
    raw,capture,race=fixture_card()
    race['race_id']='KM-LOCAL-FNB-20261106-R01-RAKUTEN-REFERENCE-CHANGED-FACTS'
    out=materialize_reference(raw,capture=capture,race=race,generated_at=NOW)
    assert out['request']['race_id']==race['race_id']
    race['race_id']='KM-LOCAL-FNB-20261106-R02-RAKUTEN-REFERENCE-WRONG-RACE'
    with pytest.raises(ValueError,match='REVISION_IDENTITY'):
        materialize_reference(raw,capture=capture,race=race,generated_at=NOW)


def test_current_header_conditions_feed_existing_going_rules_without_historical_substitution():
    from runtime.local_fnb_rakuten_reference import materialize_reference
    raw,capture,race=fixture_card()
    absent=parse_card(raw,capture=capture,race=race,now=NOW)
    assert absent['current_conditions']=={'weather':None,'going':None}
    # The history contains 良, but the current header prints 重.
    raw=raw.replace('発走時刻'.encode(),'天候： 雨 ダ： 重 発走時刻'.encode())
    capture['raw_sha256']=hashlib.sha256(raw).hexdigest()
    out=materialize_reference(raw,capture=capture,race=race,generated_at=NOW)
    assert out['parsed']['current_conditions']=={'weather':'雨','going':'重'}
    assert out['source']['normalized_evidence']['track_condition']['value']=='重'
    assert out['source']['normalized_evidence']['weather']['value']=='雨'
    state=out['numerical']['candidate_current_state']
    assert state['official_going']=='重' and state['official_weather']=='雨'
    assert out['source']['formal_source_admitted'] is False


@pytest.mark.parametrize('changed',['unchanged','weather','going','previously-unconsumed-going'])
def test_publication_compares_consumed_conditions_and_reuses_unchanged_krs(tmp_path,monkeypatch,changed):
    from runtime import local_fnb_saved_paper_tickets as saved
    from runtime import local_fnb_saved_exact_paper as exact_saved
    from runtime.local_fnb_rakuten_reference import publish_saved_reference
    raw,capture,intent=fixture_card()
    raw=raw.replace('発走時刻'.encode(),'天候： 曇 ダ： 稍重 発走時刻'.encode())
    capture['raw_sha256']=hashlib.sha256(raw).hexdigest()
    parsed=parse_card(raw,capture=capture,race=intent,now=NOW)
    parsed['capture']=capture
    krs_raw=b'{}'
    rows=[{'runner_id':str(i),'rank':None} for i in (1,2)]
    pred={'race_id':'SYNTHETIC_ONLY','sha256':'synthetic-static',
        'source_snapshot_sha256':'synthetic-source','model_code_sha256':'synthetic-model',
        'source_freeze_at':NOW.isoformat(),'freeze_at':(NOW+timedelta(seconds=1)).isoformat(),
        'column_rankings':{c:{'rows':rows,'front':[],'unknown_protected':['1','2']} for c in ('W','P2','P3')},
        'roles':{'1':['UNKNOWN'],'2':['UNKNOWN']},'head_local_P2':[],'pair_conditioned_Third':[]}
    request={**intent,'scheduled_post_at':'2026-11-06T14:45:00+09:00',
        'prediction_cutoff':'2026-11-06T14:40:00+09:00','race':{'name':'SYNTHETIC_ONLY'}}
    inputs={'request':request,'prediction':pred,'documents':{'parsed_provider_card.json':parsed},
        'raw':{'krs/execution_output.json':krs_raw,'original_provider_card.html':raw},
        'numerical':{'candidate_current_state':{'official_going':'稍重','official_weather':'曇'},
            'candidate_full_numerical_summary':{'required_count':58,'calculated_count':0,
                'ruled_neutral_count':58,'unresolved_count':0,'candidate_neutral_missing_component_count':0}},
        'krs_output':{'summary':[{'horse_no':i,'SSR-W':0.5,'SSR-P2':0.5,'SSR-P3':0} for i in (1,2)]},
        'context':{'runners':[{'runner_id':str(i),'paths':[],'input_observations':0} for i in (1,2)]}}
    if changed=='previously-unconsumed-going':
        inputs['numerical']['candidate_current_state']['official_going']=''
    monkeypatch.setattr(saved,'verify_saved_run',lambda *a,**kw:inputs)
    monkeypatch.setattr(exact_saved,'read_previous',lambda *a:({'race_id':pred['race_id']},{},None))
    folder=tmp_path/'exact';folder.mkdir()
    exact={'race_id':pred['race_id'],'static_prediction_sha256':pred['sha256'],
        'source_snapshot_sha256':pred['source_snapshot_sha256'],
        'KRS_output_sha256':hashlib.sha256(krs_raw).hexdigest(),'selected_at':(NOW+timedelta(seconds=2)).isoformat(),
        'portfolio':{'methods':{}}}
    (folder/'exact_recovery_receipt.json').write_text(json.dumps({'files':{}}))
    (folder/'exact_paper_portfolio.json').write_text(json.dumps(exact))
    (folder/'COMPLETE_PREDICTION_AND_ALL_TICKETS.md').write_text('SYNTHETIC_ONLY_NO_REAL_NUMERICS_OR_TICKETS')
    current=tmp_path/'current';current.mkdir()
    if changed=='weather':raw=raw.replace('曇'.encode(),'雨'.encode())
    if changed=='going':raw=raw.replace('稍重'.encode(),'重'.encode())
    capture={**capture,'raw_sha256':hashlib.sha256(raw).hexdigest()}
    (current/'original.html').write_bytes(raw);(current/'capture.json').write_text(json.dumps(capture))
    args=dict(intent=intent,source_folder=tmp_path/'source',paper_folder=tmp_path/'paper',
        exact_folder=folder,destination=tmp_path/'publications',current_card_folder=current,
        now=NOW+timedelta(seconds=3))
    if changed!='unchanged':
        with pytest.raises(ValueError,match='MATERIAL_INPUT_CHANGE_NEW_CALCULATION_REVISION_REQUIRED'):
            publish_saved_reference(**args)
    else:
        result=publish_saved_reference(**args)
        assert result['manifest']['new_KRS']==0
        assert result['manifest']['KRS_output_sha256']==hashlib.sha256(krs_raw).hexdigest()
        assert result['manifest']['source_fetched_at']==NOW.isoformat()
        assert result['source_within_existing_600s'] is True
        again=publish_saved_reference(**{**args,'now':NOW+timedelta(seconds=700)})
        assert again['body']==result['body']
        assert again['manifest']['prepared_at']==result['manifest']['prepared_at']
        assert again['source_within_existing_600s'] is False
        assert again['source_age_seconds_at_readback']==700
        old_body=result['body']
        old_path=Path(result['publication_folder'])
        original_bytes={p.name:p.read_bytes() for p in old_path.iterdir() if p.is_file()}
        # Identical Raw, new frozen calculation: old bytes stay available, but
        # a new publication must bind to the new Static/KRS, not return old text.
        pred['sha256']='synthetic-corrected-static'
        exact['static_prediction_sha256']=pred['sha256']
        (args['exact_folder']/'exact_paper_portfolio.json').write_text(json.dumps(exact))
        (args['exact_folder']/'COMPLETE_PREDICTION_AND_ALL_TICKETS.md').write_text('SYNTHETIC_ONLY_CORRECTED_REVISION')
        corrected=publish_saved_reference(**{**args,'now':NOW+timedelta(seconds=701)})
        assert corrected['manifest']['static_sha256']==pred['sha256']
        assert corrected['manifest']['revision']!=result['manifest']['revision']
        assert corrected['body']!=old_body and 'CORRECTED_REVISION' in corrected['body']
        assert original_bytes=={p.name:p.read_bytes() for p in old_path.iterdir() if p.is_file()}
        repeated=publish_saved_reference(**{**args,'now':NOW+timedelta(seconds=702)})
        assert repeated['body']==corrected['body']
        assert repeated['manifest']['prepared_at']==corrected['manifest']['prepared_at']

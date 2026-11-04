"""Mechanical fixtures only; real HTTP acceptance is separately retained."""
from datetime import datetime,timezone
import hashlib
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

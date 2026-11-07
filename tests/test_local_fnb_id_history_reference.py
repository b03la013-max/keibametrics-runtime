"""Synthetic original-byte/native-event correctness, never LIVE qualification."""
import base64
from copy import deepcopy
from datetime import date, datetime
import gzip
import hashlib
import pytest

from runtime import local_fnb_id_history_reference as history
from tests.test_local_historical_identity_observations import snapshot

ASOF=datetime.fromisoformat("2026-11-04T02:00:00+00:00")
TARGET=date(2026,11,4)


def result_fixture():
    original=snapshot()
    text=gzip.decompress(base64.b64decode(original["raw_gzip_b64"])).decode()
    text=text.replace('<td>1</td><td>1</td><td>1</td>','<td>2</td><td>1</td><td>1</td>')
    text=text.replace('<th>通過</th>','<th>コーナー通過順</th>')
    text=text.replace('<td>37.0</td><td></td>','<td>37.0</td><td>(1,2)-3</td>')
    s=snapshot(text);raw=gzip.decompress(base64.b64decode(s['raw_gzip_b64']))
    origin={"zip_raw_sha256":"a"*64,"member":"202610_horselist.csv","member_sha256":"b"*64,"csv_row":2}
    race={"頭数":"8","距離":"1200","芝ダート区分":"ダート","回り":"左","馬場":"良","レース名":"Ｃ３四","_csv_origin":origin}
    horse={"馬名":"Synthetic","着順":"2","負担重量":"56","騎手名":"SyntheticJ","人気":"1",
        "馬体重":"480","上がり3F":"37.0","着差":"2.1/2","_csv_origin":origin}
    tables={"racelist":{('船橋','20261001',1):race},"horselist":{('船橋','20261001',1,1):horse}}
    return s,raw,tables


def test_same_row_native_link_survives_rowspan_and_nested_record_table():
    text='<table><tr><td rowspan="5">4</td><td><a href="../DataRoom/HorseMarkInfo?k_lineageLoginCode=123">Synthetic</a></td><td><table><tr><td>全</td><td>1-0-0-0</td></tr></table></td></tr></table>'
    row=history._card_ids(text,'https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/DebaTable')['4']
    assert row[0]=='NAR:123' and row[1]=='Synthetic'
    with pytest.raises(ValueError,match='ROW_IDENTITY'):
        history._card_ids(text.replace('<td rowspan="5">4</td>','<td>UNKNOWN</td>'), 'https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/DebaTable')


def test_native_result_and_exact_event_csv_supply_explicit_denominator_only():
    s,raw,tables=result_fixture()
    found=history._result_pairs(s,raw,tables,{'NAR:123'},TARGET,ASOF)
    assert len(found)==1
    candidate,independent=found[0][1]
    assert candidate['field_size']==8  # The single printed result row is not a denominator.
    assert candidate['finish_score']==pytest.approx(100*6/7)
    assert float(independent['finish_score'])==pytest.approx(100*6/7)
    assert candidate['margin'] is None and independent['margin'] is None
    assert candidate['result_length_margin_raw_not_seconds']=='2.1/2'
    assert candidate['content_positions']==[] and independent['positions']==[]
    assert candidate['historical_csv_horse_origin']['zip_raw_sha256']=='a'*64
    assert found[0][2].endswith('k_lineageLoginCode=123')


def test_shared_name_cannot_replace_missing_native_identity_or_event_row():
    s,raw,tables=result_fixture()
    assert history._result_pairs(s,raw,tables,{'NAR:999'},TARGET,ASOF)==[]
    tables['horselist']={('船橋','20261001',2,1):next(iter(tables['horselist'].values()))}
    assert history._result_pairs(s,raw,tables,{'NAR:123'},TARGET,ASOF)==[]


@pytest.mark.parametrize('change', ['name','load','finish'])
def test_csv_conflicts_do_not_silently_replace_signed_result_facts(change):
    s,raw,tables=result_fixture();horse=next(iter(tables['horselist'].values()))
    horse[{'name':'馬名','load':'負担重量','finish':'着順'}[change]]={'name':'Different','load':'55','finish':'3'}[change]
    with pytest.raises(ValueError,match='CONFLICT'):
        history._result_pairs(s,raw,tables,{'NAR:123'},TARGET,ASOF)


def test_printed_apprentice_weight_is_not_subtracted_twice():
    s,raw,tables=result_fixture();next(iter(tables['horselist'].values()))['負担重量']='▲56.0'
    found=history._result_pairs(s,raw,tables,{'NAR:123'},TARGET,ASOF)
    assert found[0][1][0]['ride_carried_weight']==56.0


@pytest.mark.parametrize('field,value', [('距離','1000'),('芝ダート区分','芝'),('馬場','重'),('レース名','Ｃ２四')])
def test_signed_result_heading_cannot_be_replaced_by_conflicting_csv_context(field,value):
    s,raw,tables=result_fixture();next(iter(tables['racelist'].values()))[field]=value
    with pytest.raises(ValueError,match='RESULT_HEADING_CSV_CONFLICT'):
        history._result_pairs(s,raw,tables,{'NAR:123'},TARGET,ASOF)


def test_missing_optional_signed_heading_is_unknown_without_inventing_it():
    s,raw,tables=result_fixture()
    text=raw.decode().replace('<section class="raceTitle"><h3>Ｃ３四</h3><li>ダート 1200ｍ 天候：晴 馬場：良</li></section>','')
    s=snapshot(text);raw=gzip.decompress(base64.b64decode(s['raw_gzip_b64']))
    found=history._result_pairs(s,raw,tables,{'NAR:123'},TARGET,ASOF)
    assert len(found)==1
    assert set(found[0][1][0]['signed_result_heading_csv_comparison'].values())=={'OPTIONAL_SIGNED_HEADING_UNKNOWN'}


def test_duplicate_event_unknown_fill_preserves_all_original_provenance():
    old=({'finish':2,'surface':'DIRT','content_positions':[3,2], 'history_source_provenance':[{'raw_sha256':'a'}]},
         {'positions':[3,2],'history_source_provenance':[{'raw_sha256':'a'}]})
    new=({'finish':2,'surface':'UNKNOWN','content_positions':[], 'history_source_provenance':[{'raw_sha256':'b'}]},
         {'positions':[],'history_source_provenance':[{'raw_sha256':'b'}]})
    merged=history._merge(deepcopy(old),new)
    assert merged[0]['content_positions']==[3,2]
    assert len(merged[0]['history_source_provenance'])==len(merged[1]['history_source_provenance'])==2
    with pytest.raises(ValueError,match='CONFLICTING_DATED_FACT'):
        history._merge(deepcopy(old),({'finish':1},{}))

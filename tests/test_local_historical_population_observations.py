"""Synthetic correctness cases; no provider access or empirical score credit."""
import base64
from copy import deepcopy
import gzip
import hashlib
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("population_observations", Path(__file__).resolve().parents[1]/"runtime/local_historical_population_observations.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def snapshot(*, day="2026/10/02", link_day="2026/10/02", number="4", link_number="4", distance="1200", venue="船橋", code="19"):
    cells = [day, venue, number, "研究fixture", "C2", distance, "晴", "良", "ナ",
             "10", "1", "1", "3", "2", "1:14.1", "0.1", "38.0", "470", "騎手名", "55", "厩舎名", "100000", "他馬"]
    url = f"/KeibaWeb/TodayRaceInfo/RaceMarkTable?k_raceDate={link_day}&amp;k_raceNo={link_number}&amp;k_babaCode={code}"
    raw = ("<table><tr>" + "".join(f'<td><a href="{url}">{v}</a></td>' if i==3 else f'<td>{v}</td>' for i,v in enumerate(cells)) + "</tr></table>").encode()
    return {"official":True,"authority":"NAR_OFFICIAL","source_class":"OFFICIAL_HORSE_HISTORY_PROFILE",
        "http_status":200,"fetched_at":"2026-10-03T00:30:00+09:00",
        "requested_url":"https://www.keiba.go.jp/KeibaWeb/DataRoom/HorseMarkInfo?k_lineageLoginCode=3001",
        "final_url":"https://www.keiba.go.jp/KeibaWeb/DataRoom/HorseMarkInfo?k_lineageLoginCode=3001",
        "content_type":"text/html; charset=UTF-8","raw_gzip_b64":base64.b64encode(gzip.compress(raw)).decode(),
        "raw_sha256":hashlib.sha256(raw).hexdigest(),"byte_count":len(raw),"source_id":"synthetic"}


def extract(s, **kwargs):
    return m.extract_horse_history(s, as_of="2026-10-03T10:00:00+09:00", **kwargs)


def test_explicit_official_row_identity_and_unknowns():
    out=extract(snapshot());r=out['records'][0]
    assert r['race_id']=="NAR:20261002:19:R04"
    assert r['horse_id']=="NAR:3001"
    assert r['finish']==2 and r['body_weight_kg']==470
    assert r['parent_id'] is None and r['jockey_id'] is None and r['stable_id'] is None
    assert r['event_at'] is None and r['surface'] is None
    assert not out['comparison_population_complete'] and not out['score_generated']


@pytest.mark.parametrize('mutation,error',[
    ({'raw_sha256':'0'*64},'RAW_HASH'),
    ({'byte_count':1},'RAW_HASH'),
    ({'authority':'SECONDARY'},'OFFICIAL_HISTORY'),
    ({'http_status':403},'OFFICIAL_HISTORY'),
    ({'fetched_at':'2026-10-03T10:00:00+09:00'},'SOURCE_AT_OR_AFTER'),
    ({'fetched_at':'2026-10-03T00:30:00'},'AWARE_TIME'),
    ({'final_url':'https://www.keiba.go.jp/KeibaWeb/DataRoom/HorseMarkInfo?k_lineageLoginCode=9999'},'HORSE_IDENTITY'),
    ({'final_url':'https://example.com/KeibaWeb/DataRoom/HorseMarkInfo?k_lineageLoginCode=3001'},'URL_SCOPE'),
])
def test_unqualified_or_changed_original_is_rejected(mutation,error):
    s=snapshot();s.update(mutation)
    with pytest.raises(ValueError,match=error):extract(s)


@pytest.mark.parametrize('kwargs',[{'link_day':'2026/10/01'},{'link_number':'5'}])
def test_same_row_identity_conflict_rejects(kwargs):
    with pytest.raises(ValueError,match='LINK_CONFLICT'):extract(snapshot(**kwargs))


def test_target_day_results_never_become_predictive_history():
    out=extract(snapshot(),target_race_date='2026-10-02')
    assert out['records']==[] and out['excluded_rows']==1


def test_jst_date_boundary_is_not_compared_to_utc_date():
    s=snapshot(day='2026/10/03',link_day='2026/10/03')
    # UTC is October2; the official printed result date is JST October3.
    out=extract(s)
    assert len(out['records'])==1 and out['records'][0]['event_at'] is None


def test_date_after_snapshot_is_excluded():
    s=snapshot(day='2026/10/04',link_day='2026/10/04')
    assert extract(s)['records']==[]


def test_only_printed_surface_prefix_establishes_surface():
    row=extract(snapshot(distance='芝1600'))['records'][0]
    assert row['distance_m']==1600 and row['surface']=='TURF'
    assert extract(snapshot(distance='1600'))['records'][0]['surface'] is None


def test_existing_official_venue_map_conflict_is_rejected():
    with pytest.raises(ValueError,match='VENUE_CONFLICT'):extract(snapshot(venue='浦和',code='19'))


def test_unknown_venue_code_is_not_verified_from_a_name():
    row=extract(snapshot(venue='未知場',code='99'))['records'][0]
    assert row['printed_venue_identity_status']=='UNKNOWN_CODE_NOT_IN_EXISTING_LOCAL_MAP'


def test_impossible_printed_calendar_date_is_rejected():
    with pytest.raises(ValueError,match='EVENT_DATE_INVALID'):extract(snapshot(day='2026/02/31',link_day='2026/02/31'))


def test_race_number_zero_is_rejected():
    with pytest.raises(ValueError,match='NUMBER_OUT_OF_RANGE'):extract(snapshot(number='0',link_number='0'))

import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"/"local_physical"))

from nar_source_manifest import LOCAL_BABA_CODES, PROFILE, build_local_nar_manifest
from source_acquisition import _html_tables


def test_nar_local_manifest_kochi():
    m=build_local_nar_manifest({
        "family_id":"LOCAL",
        "race_id":"KCH-20260913-R03",
        "venue_id":"KCH",
        "race_date":"2026-09-13",
        "race_no":3,
        "prediction_cutoff":"2026-09-13T15:30:00+09:00",
        "include_same_day_results":True,
        "include_odds":True,
    })
    assert m["manifest_profile"]==PROFILE
    assert m["nar_baba_code"]=="31"
    assert m["venue_name"]=="高知"
    assert m["sources"][0]["required"] is True
    assert "DebaTable" in m["sources"][0]["url"]
    assert "k_babaCode=31" in m["sources"][0]["url"]
    assert "k_raceNo=3" in m["sources"][0]["url"]
    ids=[x["source_id"] for x in m["sources"]]
    assert any("ODDS-TANFUKU" in x for x in ids)
    assert any("R01-RESULT" in x for x in ids)
    assert any("R02-RESULT" in x for x in ids)


def test_all_local_venue_codes_are_explicit():
    expected={"MOR","MIZ","URW","FNB","OHI","KAW","KNZ","KSM","NGY","SON","HIM","KCH","SAG","MON"}
    assert set(LOCAL_BABA_CODES)==expected
    assert len(set(LOCAL_BABA_CODES.values()))==len(expected)


def test_html_table_extraction_preserves_headers_and_rows():
    html="""
    <html><body>
      <table>
        <tr><th>馬番</th><th>馬名</th><th>馬体重</th></tr>
        <tr><td>1</td><td>テストホース</td><td>486(+8)</td></tr>
      </table>
    </body></html>
    """
    tables=_html_tables(html)
    assert tables==[[["馬番","馬名","馬体重"],["1","テストホース","486(+8)"]]]


def test_invalid_or_ban_venue_is_rejected():
    try:
        build_local_nar_manifest({
            "family_id":"LOCAL","venue_id":"OBI","race_date":"2026-09-23","race_no":1,
            "prediction_cutoff":"2026-09-23T12:00:00+09:00"
        })
        raise AssertionError("BAN venue must not use LOCAL adapter")
    except ValueError as e:
        assert "LOCAL_NAR_VENUE_ID_UNSUPPORTED" in str(e)


def test_same_day_result_fields_are_race_scoped():
    m=build_local_nar_manifest({
        "family_id":"LOCAL",
        "race_id":"KCH-20260913-R03",
        "venue_id":"KCH",
        "race_date":"2026-09-13",
        "race_no":3,
        "prediction_cutoff":"2026-09-13T15:30:00+09:00",
        "include_same_day_results":True,
        "include_odds":False,
    })
    r1=next(x for x in m["sources"] if "R01-RESULT" in x["source_id"])
    r2=next(x for x in m["sources"] if "R02-RESULT" in x["source_id"])
    f1={x["field"] for x in r1["extract"]}
    f2={x["field"] for x in r2["extract"]}
    assert "same_day_r01_result_tables" in f1
    assert "same_day_r02_result_tables" in f2
    assert f1.isdisjoint(f2)


def test_formal_active_runner_universe_requires_official_odds_source():
    m=build_local_nar_manifest({
        "family_id":"LOCAL",
        "race_id":"URW-20260923-R08",
        "venue_id":"URW",
        "race_date":"2026-09-23",
        "race_no":8,
        "prediction_cutoff":"2026-09-23T17:03:00+09:00",
        "include_same_day_results":True,
        "include_odds":True,
        "require_active_runner_universe":True,
    })
    odds=next(x for x in m["sources"] if "ODDS-TANFUKU" in x["source_id"])
    assert odds["required"] is True
    assert odds["source_class"]=="OFFICIAL_TIMESTAMPED_ODDS"
    assert m["source_policy"]["odds"]=="REQUIRED_FOR_ACTIVE_RUNNER_UNIVERSE"
    assert m["source_policy"]["runner_universe_model"]=="DECLARED_RACE_CARD_PLUS_ACTIVE_OFFICIAL_BETTING_UNIVERSE"

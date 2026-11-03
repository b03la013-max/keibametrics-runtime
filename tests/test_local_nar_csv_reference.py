"""Synthetic documented-schema correctness only; no official data acquisition."""
from datetime import datetime, timezone
import csv
import hashlib
import io
import zipfile

import pytest
from runtime.local_nar_csv_reference import inspect_zip, SCHEMAS

NOW = datetime.fromisoformat("2026-11-03T03:20:00+00:00")
RACE = {"venue_id": "FNB", "race_date": "2026-11-03", "race_no": 2}


def original(*, outcomes=False, wrong_count=False, header=True, encoding="utf-8", duplicate=False):
    race = dict.fromkeys(SCHEMAS["racelist"], "")
    race.update(競馬場="船橋", 競走年月日="20261103", レース番号="2", 発走時刻="1245", 頭数="2" if wrong_count else "1", 距離="1200", 芝ダート区分="ダート", 回り="左")
    horse = dict.fromkeys(SCHEMAS["horselist"], "")
    horse.update(競馬場="船橋", 競走年月日="20261103", レース番号="2", 馬番="1", 馬名="合成テスト馬", 父馬名="合成父", 騎手名="合成騎手")
    if outcomes:
        horse.update(着順="1", タイム="1140")
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        for name, row in [("racelist", race), ("horselist", horse)]:
            s = io.StringIO(newline="")
            w = csv.writer(s)
            if header:w.writerow(SCHEMAS[name])
            w.writerow([row[k] for k in SCHEMAS[name]])
            if duplicate and name == "horselist":w.writerow([row[k] for k in SCHEMAS[name]])
            z.writestr("20261103_"+name+".csv", s.getvalue().encode(encoding))
    return b.getvalue()


def capture(raw):
    return {"provider": "NAR_OFFICIAL_CSV", "http_status": 200,
        "source_url": "https://www.keiba.go.jp/KeibaWeb/DataDownload/RaceDataDownload?type=daily",
        "retrieval_method": "OFFICIAL_BROWSER_DOWNLOAD", "captured_at": "2026-11-03T03:19:00+00:00",
        "raw_sha256": hashlib.sha256(raw).hexdigest(), "usage_qualification": {"status": "SYNTHETIC_NOT_QUALIFIED"}}


@pytest.mark.parametrize("encoding,header_mode", [("utf-8", "present"), ("utf-8-sig", "present"), ("cp932", "absent")])
def test_documented_columns_parse_without_granting_source_or_identity(encoding, header_mode):
    b = original(encoding=encoding, header=header_mode=="present")
    p = inspect_zip(b, capture=capture(b), race=RACE, encoding=encoding, header_mode=header_mode, now=NOW)
    assert p["parsed_horse_rows"] == 1
    assert p["headcount_matches_horse_rows"] is True
    assert p["schema_basis"]["counts"] == {"racelist":66,"horselist":36,"odds":10,"payback":54}
    assert p["formal_source_ready"] is False
    assert p["formal_numerical_consumption_authorized"] is False
    assert p["active_universe_verified"] is False
    assert p["race_identity"]["official_race_id"] is None
    assert p["runners"][0]["horse_id"] is None
    assert p["runners"][0]["sire_id"] is None
    assert p["runners"][0]["field_provenance"]["馬体重"]["csv_column"] == 23


def test_target_outcomes_are_separate_never_prestart_features():
    b=original(outcomes=True)
    p=inspect_zip(b,capture=capture(b),race=RACE,encoding="utf-8",header_mode="present",now=NOW)
    assert p["target_outcome_fields_present"] is True
    assert p["candidate_prestart_claim"] is False
    assert "着順" not in p["runners"][0]["prestart_reference_fields"]
    assert p["runners"][0]["outcome_fields_separated"]["着順"] == "1"


@pytest.mark.parametrize("field,wrong", [("distance_m", 1500), ("surface", "TURF"), ("turn", "RIGHT"),
    ("scheduled_post_at", "2026-11-03T12:40:00+09:00")])
def test_caller_identity_cannot_override_csv_facts(field, wrong):
    b=original()
    with pytest.raises(ValueError,match="EXPECTED_RACE_CONFLICT:"+field):
        inspect_zip(b,capture=capture(b),race={**RACE,field:wrong},encoding="utf-8",header_mode="present",now=NOW)


def test_naive_clock_cannot_be_completed_with_host_timezone():
    b=original()
    with pytest.raises(ValueError,match="AWARE_CLOCK_REQUIRED"):
        inspect_zip(b,capture=capture(b),race=RACE,encoding="utf-8",header_mode="present",now=datetime(2026,11,3,3,20))


def test_headcount_does_not_infer_cancelled_active_status():
    b=original(wrong_count=True)
    p=inspect_zip(b,capture=capture(b),race=RACE,encoding="utf-8",header_mode="present",now=NOW)
    assert p["headcount_matches_horse_rows"] is False
    assert p["active_universe_verified"] is False
    assert p["change_semantics_verified"] is False


@pytest.mark.parametrize("mutation,reason",[
    (lambda c:c.update(raw_sha256="0"*64),"PROVENANCE"),
    (lambda c:c.update(captured_at="2026-11-04T00:00:00+00:00"),"FUTURE"),
    (lambda c:c.update(source_url="https://example.com/race.zip"),"URL_SCOPE"),
    (lambda c:c.update(source_url="https://www.keiba.go.jp/KeibaWeb/DataDownload/RaceDataDownload?type=daily&fake=1"),"URL_SCOPE"),
    (lambda c:c.update(source_url="https://www.keiba.go.jp/KeibaWeb/DataDownload/RaceDataDownload?type=monthly&k_year=2026&k_month=10"),"MONTH_RACE"),
])
def test_ineligible_capture_is_rejected(mutation,reason):
    b=original();c=capture(b);mutation(c)
    with pytest.raises(ValueError,match=reason):inspect_zip(b,capture=c,race=RACE,encoding="utf-8",header_mode="present",now=NOW)


def test_duplicate_horse_rows_cannot_be_reconciled_by_name():
    b=original(duplicate=True)
    with pytest.raises(ValueError,match="DUPLICATE_RUNNER"):
        inspect_zip(b,capture=capture(b),race=RACE,encoding="utf-8",header_mode="present",now=NOW)


def test_schema_drift_and_guessing_format_are_rejected():
    b=original(header=False)
    with pytest.raises(ValueError,match="HEADER_MISMATCH"):
        inspect_zip(b,capture=capture(b),race=RACE,encoding="utf-8",header_mode="present",now=NOW)
    with pytest.raises(ValueError,match="EXPLICIT_ENCODING"):
        inspect_zip(b,capture=capture(b),race=RACE,encoding="auto",header_mode="auto",now=NOW)


def test_archive_path_is_never_extracted_or_trusted():
    s=io.BytesIO()
    with zipfile.ZipFile(s,"w") as z:z.writestr("../20261103_horselist.csv","anything")
    b=s.getvalue()
    with pytest.raises(ValueError,match="ARCHIVE_MEMBER"):
        inspect_zip(b,capture=capture(b),race=RACE,encoding="utf-8",header_mode="present",now=NOW)

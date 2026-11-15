"""Synthetic field tests; no acquisition, rights, Active or model grant."""
from datetime import datetime, timezone
from copy import deepcopy
import csv
import hashlib
import io
import zipfile

import pytest

from runtime.local_nar_csv_reference import SCHEMAS, inspect_zip
from runtime.local_fnb_csv_preliminary_numeric import materialize_preliminary
from runtime.local_fnb_r8_arithmetic_29 import verify_29

NOW = datetime(2026, 11, 3, 14, 30, tzinfo=timezone.utc)


def sample(*, outcomes=False, bad_payback_header=False):
    tables = {}
    race = dict.fromkeys(SCHEMAS["racelist"], "")
    race.update(競馬場="船橋", 競走年月日="20261104", レース番号="1", 発走時刻="1440",
        距離="1200", 芝ダート区分="ダート", 回り="左", 頭数="2", レース名="Ｃ２五六", 条件="サラブレッド系 一般")
    tables["racelist"] = [race]
    tables["horselist"] = []
    for no, load in ((1, "▲53"), (2, "56")):
        horse = dict.fromkeys(SCHEMAS["horselist"], "")
        horse.update(競馬場="船橋", 競走年月日="20261104", レース番号="1", 枠番=str(no), 馬番=str(no),
            馬名="合成馬"+str(no), 性="牡", 齢="3", 父馬名="合成父", 母馬名="合成母", 母父馬名="合成母父",
            騎手名="合成騎手", 負担重量=load, 調教師="合成調教師", 全成績="99-99-99-99")
        if outcomes:
            horse["着順"] = "1"
        tables["horselist"].append(horse)
    tables["payback"] = []
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for kind, rows in tables.items():
            stream = io.StringIO(newline="")
            writer = csv.writer(stream)
            header = list(SCHEMAS[kind])
            if kind == "payback":
                header[27], header[31] = "馬複人気1", "馬単人気1"
                if bad_payback_header:
                    header[26] = "勝手な列名"
            writer.writerow(header)
            for row in rows:
                writer.writerow([row[field] for field in SCHEMAS[kind]])
            archive.writestr("202611_"+kind+".csv", stream.getvalue().encode("utf-8-sig"))
    raw = output.getvalue()
    capture = {"provider": "NAR_OFFICIAL_CSV", "http_status": 200,
        "source_url": "https://www.keiba.go.jp/KeibaWeb/DataDownload/RaceDataDownload?type=monthly&k_year=2026&k_month=11",
        "retrieval_method": "AUTHORIZED_HTTP_GET", "captured_at": "2026-11-03T14:23:36+00:00",
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "usage_qualification": {"status": "SYNTHETIC_NOT_QUALIFIED"}}
    return raw, capture, {"venue_id": "FNB", "race_date": "2026-11-04", "race_no": 1}


def test_real_shape_ascii_payback_headers_and_allowance_mark_keep_exact_arithmetic():
    raw, capture, race = sample()
    result = materialize_preliminary(raw, capture=capture, race=race, now=NOW)
    receipt = result["receipt"]
    assert receipt["component_records"] == receipt["component_matches"] == 126
    assert receipt["base_index_records"] == receipt["base_index_matches"] == 18
    assert receipt["arithmetic29"]["status"] == "29_OF_29_RECORDED_FEATURE_ARITHMETIC_PASS"
    assert receipt["arithmetic29"]["checked_cells"] == 58
    assert result["raw_field"]["1"]["current_load"] == 53
    assert [r["evidence_features"]["carried_weight"]["score"] for r in result["numerical"]["runners"]] == [85, 40]
    assert all(r["evidence_features"]["current_class"]["score"] == 58 for r in result["numerical"]["runners"])
    assert receipt["active_universe_verified"] is False
    assert receipt["formal_source_admitted"] is False
    assert receipt["registered_oos_increment"] == receipt["live_accepted_races"] == 0


def test_aggregate_record_cannot_create_individual_history_or_pedigree_population():
    raw, capture, race = sample()
    result = materialize_preliminary(raw, capture=capture, race=race, now=NOW)
    for runner in result["numerical"]["runners"]:
        assert runner["raw_candidate_evidence"]["starts"] == []
        assert runner["evidence_features"]["recent_finish"]["missing"] is True
        assert runner["evidence_features"]["sire_fit"]["missing"] is True
        assert runner["evidence_features"]["official_recent_coverage"]["score"] == 0
        assert runner["raw_candidate_evidence"]["horse_id"] is None


def test_header_alias_does_not_accept_other_column_changes():
    raw, capture, race = sample(bad_payback_header=True)
    with pytest.raises(ValueError, match="HEADER_MISMATCH"):
        inspect_zip(raw, capture=capture, race=race, encoding="utf-8-sig", header_mode="present", now=NOW)


@pytest.mark.parametrize("outcomes,now", [(True, NOW), (False, datetime(2026,11,4,15,tzinfo=timezone.utc))])
def test_outcomes_or_expired_race_cannot_be_preliminary_future(outcomes, now):
    raw, capture, race = sample(outcomes=outcomes)
    with pytest.raises(ValueError, match="FUTURE_OUTCOME_FREE_RACE_REQUIRED"):
        materialize_preliminary(raw, capture=capture, race=race, now=now)


def test_mapping_policy_unknown_cannot_be_smuggled_as_legacy_candidate():
    raw, capture, race = sample()
    result = materialize_preliminary(raw, capture=capture, race=race, now=NOW)
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    registry = json.loads((root/"mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json").read_text())
    mapping = json.loads((root/"mapping/local_full_numerical_mapping_v0.1_candidate_20260923.json").read_text())
    changed = deepcopy(mapping)
    changed["missing_semantics"]["neutral_score"] = 51
    assert "NUMERIC_MAPPING_POLICY_UNRECOGNIZED" in verify_29(result["numerical"], registry, changed)["issues"]

"""Census reuses prior arithmetic and never promotes hypotheses or old gaps."""
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import zipfile

import pytest

from runtime.local_fnb_base63_readiness_census import census, rule_decision_packet, reconcile_current_csv
from runtime.local_fnb_csv_preliminary_numeric import materialize_preliminary
from test_local_fnb_csv_preliminary_numeric import sample, NOW

ROOT = Path(__file__).resolve().parents[1]


def prior(tmp_path):
    raw, capture, race = sample()
    artifact = materialize_preliminary(raw, capture=capture, race=race, now=NOW)
    path = tmp_path/"prior.json"
    path.write_text(json.dumps(artifact, ensure_ascii=False))
    return path, raw, capture


def test_all15_contracts_distinguish_formal_neutral_and_new_midrank_mapping():
    packet = rule_decision_packet(ROOT)
    assert packet["rule_count"] == 15
    assert {name: sum(r["index"] == name for r in packet["rules"]) for name in ["BVIg-L","JTI-L","CSI-L","BWI-L"]} == {
        "BVIg-L":7,"JTI-L":1,"CSI-L":3,"BWI-L":4}
    for rule in packet["rules"]:
        assert rule["formal_available_missing_terminal"]["score"] == 52
        assert rule["research_missing"].startswith("UNKNOWN score=null")
        assert "reference_raw" in rule["research_0_to_100_formula"]
        assert rule["production_adoption_ready"] is False
        assert rule["prediction_freeze_eligibility"]["formal_KRS_consumption"] is False
    assert packet["formal_registry"]["sha256"] != packet["candidate_profile"]["sha256"]


def test_current_census_is_complete_partition_without_reusing_old212_as_current():
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        path, _, _ = prior(Path(directory))
        result = census([path], repo_root=ROOT)
    assert result["scope"]["listed_runners"] == 2
    assert result["scope"]["active_runner_count"] is None
    assert result["current_listed_component_records"] == 126
    assert sum(result["primary_gap_partition"].values()) == 126
    assert result["primary_gap_partition"]["UNADOPTED_NONMISSING_NUMERIC_MAPPING"] == 30
    assert result["existing_witness_readback_comparisons"] == {"MATCH":126}
    assert result["historical_gap_ledger"]["old_missing"] == 212
    assert result["historical_gap_ledger"]["added_to_current_counts"] is False
    assert result["formal_qualified_consumable_records"] == result["new_live_races"] == 0
    assert result["new_score_computation"] is False


def test_duplicate_race_and_drifted_old_feature_cannot_reuse_PASS(tmp_path):
    path, _, _ = prior(tmp_path)
    with pytest.raises(ValueError, match="DUPLICATE_RACE"):
        census([path,path], repo_root=ROOT)
    artifact = json.loads(path.read_text())
    artifact["numerical"]["runners"][0]["evidence_features"]["recent_finish"]["score"] = 53
    path.write_text(json.dumps(artifact))
    with pytest.raises(ValueError, match="WITNESS_RECORD_DRIFT"):
        census([path], repo_root=ROOT)


def test_current_raw_changes_force_refresh_without_rewriting_old_scores(tmp_path):
    path, raw, capture = prior(tmp_path)
    original = path.read_bytes()
    result = reconcile_current_csv(raw, capture=capture, numerical_artifact_paths=[path], now=NOW)
    assert result["races_with_changed_numerical_inputs"] == 0
    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(raw)) as old, zipfile.ZipFile(output,"w") as new:
        for name in old.namelist():
            content = old.read(name)
            if name.endswith("horselist.csv"):
                content = content.replace("▲53".encode(), "▲52".encode())
            new.writestr(name, content)
    changed = output.getvalue()
    new_capture = deepcopy(capture)
    new_capture["raw_sha256"] = hashlib.sha256(changed).hexdigest()
    result = reconcile_current_csv(changed, capture=new_capture, numerical_artifact_paths=[path], now=NOW)
    assert result["races_with_changed_numerical_inputs"] == 1
    assert result["race_comparisons"][0]["differences"][0]["field"] == "負担重量"
    assert result["new_score_computations"] == result["formal_coverage_increment"] == 0
    assert path.read_bytes() == original

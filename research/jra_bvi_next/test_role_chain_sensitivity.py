"""Adversarial boundary tests: archived role replay never becomes a FINAL."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import role_chain_sensitivity as r


def fixture(role="W"):
    return {
        "static_prediction": {"ranking": ["1", "2", "3"],
                              "roles": {"1": [role], "2": ["P2"], "3": ["P3"]}},
        "pair_dispositions": [{"head": "1", "second": "2", "status": "PURCHASE"}],
        "third_dispositions": [{"head": "1", "second": "2", "third": "3", "status": "PURCHASE"}],
    }


def test_stage_identity_is_order_stable_and_does_not_mutate_inputs():
    a = fixture()
    copy_a = copy.deepcopy(a)
    assert r.stage_delta(r.state(a), r.state(copy_a)) == {
        "static_ranking_changed": False,
        "role_membership_symmetric_difference": {"W": 0, "P2": 0, "P3": 0},
        "pair_decision_symmetric_difference": 0, "third_decision_symmetric_difference": 0}
    assert a == copy_a


def test_role_pair_third_changes_remain_separately_visible():
    a, b = fixture(), fixture()
    b["static_prediction"]["roles"]["2"].append("W")
    b["pair_dispositions"].append({"head": "2", "second": "1", "status": "PURCHASE"})
    b["third_dispositions"] = []
    diff = r.stage_delta(r.state(a), r.state(b))
    assert diff["role_membership_symmetric_difference"] == {"W": 1, "P2": 0, "P3": 0}
    assert diff["pair_decision_symmetric_difference"] == 1
    assert diff["third_decision_symmetric_difference"] == 1


def test_authority_guard_rejects_foreign_manifest_without_rewriting_model(tmp_path):
    with pytest.raises(ValueError, match="RESEARCH_AUTHORITY_R51_REQUIRED"):
        r.guard_authority({"manifest_id": "R52"}, tmp_path)


def test_research_gate_does_not_admit_wrong_or_unbound_source():
    base = {"family_id": "JRA", "current_authority_manifest": r.AUTHORITY,
            "temporal_mode": "FORMAL-PRE-RACE", "source_snapshot": {"race_id": "X"},
            "source_snapshot_sha256": "incorrect", "index_provenance_ledger": {"runners": {}}}
    with pytest.raises(ValueError, match="ARCHIVED_SOURCE_HASH_MISMATCH"):
        r._validate_source(base)
    bad = copy.deepcopy(base)
    bad["family_id"] = "LOCAL"
    with pytest.raises(ValueError, match="ARCHIVED_RACE_SCOPE_OR_AUTHORITY_MISMATCH"):
        r._validate_source(bad)


def test_real_d_fixed_sha_and_authority_read_only():
    root = HERE.parents[1]
    authority = __import__("json").loads(
        (root / "profiles/KM_FAMILY_CURRENT_AUTHORITY_20261012_R51.json").read_text())
    assert r.guard_authority(authority, root) == r.D_SHA256


def test_krs_bridge_only_counts_inputs_not_simulations(monkeypatch):
    import types
    import sys

    def synthetic_bridge(record):
        return {"krs_input_data": {
            "race": {"race_id": "R"},
            "environment": {"weather": "UNKNOWN"},
            "simulation": {"run_count": 5000, "master_seed": 1},
            "horses": [{"horse_no": 1, "hsv": {"speed": 70},
                        "static": {"tpi": record["measure"], "zai_win": 50},
                        "static_roles": ["W"]}],
        }}
    monkeypatch.setitem(sys.modules, "jra_krs_input_builder_production",
                        types.SimpleNamespace(build_krs_input=synthetic_bridge))
    one = {**fixture(), "measure": 50, "runners": [{"runner_id": 1}]}
    two = {**fixture(), "measure": 51, "runners": [{"runner_id": 1}]}
    out = r.krs_bridge_delta(one, two)
    assert out["changed_input_runners"] == 1
    assert out["changed_static_numeric_cells"] == 1
    assert out["changed_hsv_cells"] == 0
    assert out["krs_executed"] is False and out["krs_output_changed"] is None

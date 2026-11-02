"""R8: real offline FNB source semantic adversarial acceptance."""
import json
import runpy
from pathlib import Path

from runtime.local_fnb_r8_day_semantics import audit_day
from runtime.local_fnb_r8_card_raw_check import check_card
from runtime.local_race_day_dispatcher import sha
from runtime.local_physical.nar_runner_universe import enrich_source_artifact

R7 = runpy.run_path(str(Path(__file__).with_name(
    "test_fnb_20261102_r7_plan_provenance.py")))
fixture = R7["_fixture_plan"]


def full_plan():
    plan = fixture()
    cards = {s["source_id"]: s for s in plan["official_snapshots"]}
    for row in plan["races"]:
        n = row["fields"]["race_no"]
        card = cards[f"NAR-FNB-20261102-R{n:02d}-RACE-CARD"]
        evidence = {"normalized_evidence":{"race_card_tables":{
            "value":card["extracted_evidence"]["race_card_tables"],
            "source_id":card["source_id"],
            "snapshot_sha256":card["snapshot_sha256"]}}}
        rebuilt = enrich_source_artifact(evidence)
        row["runner_status_registry"] = rebuilt["runner_status_registry"]
        row["observed_active_runner_universe"] = None
        row["active_universe_status"] = "UNKNOWN_PENDING_FRESH_SIGNED_SOURCE"
        row["odds_observation_error"] = "SYNTHETIC_ODDS_UNAVAILABLE"
    plan["plan_sha256"] = sha({k:v for k,v in plan.items() if k!="plan_sha256"})
    return plan


def test_fnb_r8_12_race_semantic_replay_complete():
    result = audit_day(full_plan(), "2026-11-02")
    assert result["status"] == "FNB_DAY_SEMANTICS_CONSISTENT", result["issues"]
    assert result["verified_races"] == 12
    assert result["formal_authority"] is False
    assert result["signed_source_proven"] is False


def test_fnb_r8_unobserved_bodyweight_cannot_be_forged_in_self_hashed_plan():
    plan = full_plan()
    row = plan["races"][0]
    row["declared_runner_universe"]["runners"][0]["body_weight"] = 500
    row["declared_runner_universe"]["runner_universe_sha256"] = sha({
        k:v for k,v in row["declared_runner_universe"].items()
        if k!="runner_universe_sha256"})
    plan["plan_sha256"] = sha({k:v for k,v in plan.items() if k!="plan_sha256"})
    # R7 verified only horse number+name; R8 also checks weight and frame.
    result = audit_day(plan, "2026-11-02")
    assert result["status"] != "FNB_DAY_SEMANTICS_CONSISTENT"


def test_fnb_r8_declared_horse_status_cannot_be_changed_without_raw():
    plan = full_plan()
    plan["races"][0]["runner_status_registry"][0]["status"] = "CANCELLED"
    plan["plan_sha256"] = sha({k:v for k,v in plan.items() if k!="plan_sha256"})
    result = audit_day(plan, "2026-11-02")
    assert "CANCELLED_OR_ACTIVE_STATUS_MISMATCH" in str(result["issues"])


def test_fnb_r8_missing_odds_requires_explicit_unknown_not_active():
    plan = full_plan()
    del plan["races"][2]["odds_observation_error"]
    plan["plan_sha256"] = sha({k:v for k,v in plan.items() if k!="plan_sha256"})
    result = audit_day(plan, "2026-11-02")
    assert "ODDS_UNKNOWN_REASON_MISSING" in str(result["issues"])

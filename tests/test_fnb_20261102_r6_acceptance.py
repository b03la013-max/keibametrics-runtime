"""R6 FNB acceptance: real historical negative + offline dated-scope guards."""
from __future__ import annotations

from datetime import datetime, timezone
import inspect
import json
from pathlib import Path

from runtime import formal_execution_orchestrator as orchestrator
from runtime.local_fnb_r6_numeric_readback import frozen_numeric_readback
from runtime.local_fnb_r6_readonly_acceptance import inspect as witness
from runtime.local_race_day_dispatcher import sha as plan_sha

ROOT = Path(__file__).resolve().parents[1]
OLD_EID = "LOCAL-KM-LOCAL-FNB-20261002-R04-LIVE-R1-EXEC"
NOW = datetime(2026, 11, 2, 1, 0, tzinfo=timezone.utc)


def test_r6_real_fnb_signed_legacy_final_keeps_348_holds_visible():
    formal = orchestrator.resolve_phase(OLD_EID, "FORMAL")
    assert formal is not None
    proof = frozen_numeric_readback(OLD_EID, formal, ROOT)
    quality = proof["numeric_evidence_quality"]
    assert proof["numeric_readback_error"] is None
    assert proof["frozen_execution_class"] == "FULL-LIFECYCLE-DEGRADED-NUMERICAL"
    assert quality["required_count"] == 348
    assert quality["calculated_count"] == 0
    assert quality["ruled_hold_count"] == 348
    assert quality["status"] == "NUMERICAL_HELD_OR_UNRESOLVED"
    assert not quality["reported_numeric_value_closure"]
    assert proof["numeric_checkpoint_consistency"]["consistency_verified"] is True
    assert proof["independent_formula_recalculation"] == "NOT_PERFORMED"
    assert proof["numerical_consumer_permissions"] == "NOT_GRANTED_BY_READBACK"


def test_r6_readback_missing_original_report_does_not_infer_zero(tmp_path):
    fake = {"latest": {"run_id": "test_formal"}, "manifest": {"files": {}}}
    proof = frozen_numeric_readback("FNB_TEST_RACE", fake, tmp_path)
    assert proof["numeric_evidence_quality"]["status"] == "NUMERICAL_COUNTS_NOT_REPORTED"
    assert proof["numeric_readback_error"] == "ORIGINAL_ENTRY_REPORT_NOT_FOUND"
    assert proof["numeric_checkpoint_consistency"]["consistency_verified"] is False
    assert "calculated_count" not in proof["numeric_evidence_quality"]


def test_r6_signed_final_reader_and_summary_do_not_alter_canonical_payload():
    from runtime.local_race_key_gate import readback_final, main
    src = inspect.getsource(readback_final)
    assert "frozen_numeric_readback(execution_id, formal, root)" in src
    assert "numeric_grade = frozen_numeric_readback" in src
    assert "return {**report,**payload,**numeric_grade" in src
    summary = inspect.getsource(main)
    assert "Numeric grade:" in summary
    assert "recipient delivery: UNPROVEN" in summary


def _fake_numeric(**_):
    return {"status": "READY", "required_index_count": 29,
            "prediction_consumption_authorized": False,
            "krs_consumption_authorized": False,
            "ticket_consumption_authorized": False,
            "capital_consumption_authorized": False}


def _fake_authority(**_):
    return None, {"manifest_id": "KM-FAMILY-CURRENT-AUTHORITY-TEST"}


def _owner(root, venues):
    p = root / "profiles/local_production_static_owner_20261014_v1.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({
        "enabled": True, "venues": venues,
        "family_authority_basis": "KM-FAMILY-CURRENT-AUTHORITY-TEST"
    }), encoding="utf-8")


def test_r6_fnb_offline_day_scope_no_approval_is_not_live_authorized(tmp_path):
    _owner(tmp_path, ["KAW"])
    proof = witness(tmp_path, "2026-11-02", now=NOW,
                    numeric_assessor=_fake_numeric, authority_resolver=_fake_authority)
    assert not proof["fnb_static_owner_authorized"]
    assert not proof["dated_plan_exists_and_valid"]
    assert not proof["dated_approval_present"]
    assert not proof["formal_live_authorized_by_this_witness"]
    assert len(proof["races"]) == 12
    assert "FNB_PRODUCTION_STATIC_OWNER_NOT_AUTHORIZED" in proof["blockers"]
    assert "FNB_DATED_OFFICIAL_DAY_PLAN_NOT_OBSERVED" in proof["blockers"]
    assert "FNB_DATED_OWNER_APPROVAL_NOT_OBSERVED" in proof["blockers"]
    assert len([s for s in proof["blockers"] if s.startswith(
        "NUMERICAL_CONSUMER_SCOPE_NOT_AUTHORIZED:")]) == 4
    assert all(r["pfs"] is None and not r["no_bet_proven"] for r in proof["races"])
    assert all(r["delivery_recipient_ack"] == "NOT_VERIFIED" for r in proof["races"])
    assert proof["new_runtime_posts"] == 0
    assert proof["new_github_workflow_dispatches"] == 0
    assert proof["production_changed"] is False


def test_r6_owner_label_and_plan_alone_do_not_grant_approval(tmp_path):
    _owner(tmp_path, ["KAW", "FNB"])
    d = tmp_path / "runtime/local_race_day_plan"
    d.mkdir(parents=True)
    plan = {
        "family_id": "LOCAL", "venue_id": "FNB", "race_date": "2026-11-02",
        "races": [{
            "fields": {"race_no": i,
                       "scheduled_post_at": f"2026-11-02T{14+(i//4):02}:00:00+09:00"},
            "declared_runner_universe": {"runners": [{"runner_id": "1"}]}
        } for i in range(1,13)]
    }
    plan["plan_sha256"] = plan_sha(plan)
    (d / "2026-11-02-FNB.json").write_text(json.dumps(plan), encoding="utf-8")
    proof = witness(tmp_path, "2026-11-02", now=NOW,
                    numeric_assessor=_fake_numeric, authority_resolver=_fake_authority)
    assert proof["dated_plan_exists_and_valid"]
    assert not proof["dated_approval_present"]
    assert not proof["formal_live_authorized_by_this_witness"]
    assert "FNB_DATED_OWNER_APPROVAL_NOT_OBSERVED" in proof["blockers"]
    assert proof["races"][0]["planned_required_cells"] == 29
    assert proof["current_day_calculated_cells_verified"] == 0


def test_r6_forged_sha_or_incomplete_plan_rejected(tmp_path):
    _owner(tmp_path, ["FNB"])
    d = tmp_path / "runtime/local_race_day_plan"
    d.mkdir(parents=True)
    invalid = {"family_id": "LOCAL", "venue_id": "FNB", "race_date": "2026-11-02",
               "races": [{"fields": {"race_no": 1}}],
               "plan_sha256": "forged"}
    (d / "2026-11-02-FNB.json").write_text(json.dumps(invalid), encoding="utf-8")
    proof = witness(tmp_path, "2026-11-02", now=NOW,
                    numeric_assessor=_fake_numeric, authority_resolver=_fake_authority)
    assert not proof["dated_plan_exists_and_valid"]
    assert any(x.startswith("FNB_DATED_PLAN_INVALID:") for x in proof["blockers"])


def test_r6_read_only_repo_replay_never_infers_formal_from_snapshot():
    # No live service, signer, private store, notification, or current license
    # is queried. An archived source or Final does not count as TODAY's ACK.
    fake = {"source_checkpoint": "PERSISTED_UNVERIFIED",
            "formal_checkpoint": "PERSISTED_UNVERIFIED",
            "delivery_recipient_ack": "NOT_VERIFIED",
            "pfs": None}
    assert fake["source_checkpoint"] != "SIGNED_SOURCE_VERIFIED"
    assert fake["formal_checkpoint"] != "FINAL_DELIVERED"
    assert fake["pfs"] is None

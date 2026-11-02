"""R7 day-plan: independent persisted official-shaped RAW validation.

Synthetic inputs are test fixtures, NOT real NAR issuer proof, signed SOURCE,
license acceptance, registered OOS or valid production approval.
"""
from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

from runtime.local_fnb_r7_plan_provenance import verify_fnb_plan
from runtime.local_fnb_r6_readonly_acceptance import inspect as inspect_day
from runtime.local_race_day_dispatcher import sha
from runtime.local_physical.nar_source_manifest import _race_card_source, _url
from runtime.local_physical.source_acquisition import snapshot_from_bytes
from runtime.local_physical.nar_runner_universe import enrich_source_artifact

DAY = "2026-11-02"
JST = timezone(timedelta(hours=9))
POSTS = ["14:45", "15:15", "15:45", "16:20", "16:50", "17:20",
         "17:55", "18:30", "19:05", "19:40", "20:15", "20:50"]


def _snapshot(spec, html, at):
    snap, errors = snapshot_from_bytes(
        spec, html.encode("utf-8"), final_url=spec["url"], status_code=200,
        headers={"content-type": "text/html; charset=UTF-8"},
        fetched_at=at.isoformat(), prediction_cutoff="")
    assert not errors, errors
    return snap


def _fixture_plan():
    from urllib.parse import quote
    dayurl = DAY.replace("-", "/")
    links = "".join(
        '<a href="' + _url("DebaTable", "19", dayurl, n) + '">R' + str(n) + '</a>'
        for n in range(1, 13))
    menu_spec = {"source_id":"NAR-FNB-DAY-MENU",
                 "source_class":"OFFICIAL_DAY_MENU", "authority":"NAR_OFFICIAL",
                 "official":True, "required":True,
                 "url":_url("RaceList", "19", dayurl, 1)}
    menu = _snapshot(menu_spec, "<html><body>" + links + "</body></html>",
                     datetime(2026,11,2,12,0,tzinfo=JST))
    snapshots = [menu]
    rows = []
    for n, hhmm in enumerate(POSTS,1):
        post = datetime.fromisoformat(DAY+"T"+hhmm+":00+09:00")
        cutoff = post - timedelta(minutes=5)
        spec = _race_card_source("FNB", "19", dayurl, n)
        page = (
            "<html><body><p>2026年11月2日 船橋 第" + str(n) +
            "競走 " + hhmm + "発走</p><table>"
            "<tr><th>枠番</th><th>馬番</th><th>競走馬</th></tr>"
            "<tr><td>1</td><td>1</td><td>テスト一号</td></tr>"
            "<tr><td>2</td><td>2</td><td>テスト二号</td></tr>"
            "</table></body></html>"
        )
        snap = _snapshot(spec, page, cutoff-timedelta(minutes=10))
        snapshots.append(snap)
        evidence = {"normalized_evidence": {"race_card_tables": {
            "value": snap["extracted_evidence"]["race_card_tables"],
            "source_id": snap["source_id"],
            "snapshot_sha256": snap["snapshot_sha256"],
        }}}
        enriched = enrich_source_artifact(evidence)
        rows.append({
            "race_key": f"FNB-{DAY.replace('-','')}-R{n:02d}-LIVE-R1",
            "fields": {"venue_id":"FNB", "race_date":DAY, "race_no":n,
                       "scheduled_post_at":post.isoformat(),
                       "prediction_cutoff":cutoff.isoformat()},
            "source_basis_sha256":snap["snapshot_sha256"],
            "declared_runner_universe":enriched["declared_runner_universe"],
            "intent_status":"DRAFT_NOT_FORMAL_STATIC_NOT_DISPATCHED",
            "execution_id":f"LOCAL-KM-LOCAL-FNB-{DAY.replace('-','')}-R{n:02d}-LIVE-R1-EXEC",
        })
    plan={"family_id":"LOCAL","venue_id":"FNB","race_date":DAY,
          "prediction_freeze":False,
          "status":"DISCOVERY_ONLY_NOT_REGISTERED_NOT_SIGNED_SOURCE",
          "official_snapshots":snapshots,"races":rows}
    plan["plan_sha256"]=sha(plan)
    return plan


def _rehash(plan):
    plan["plan_sha256"] = sha({k:v for k,v in plan.items() if k!="plan_sha256"})
    return plan


def test_r7_reparses_all_12_official_shaped_cards_with_24_test_runners():
    plan=_fixture_plan()
    proof=verify_fnb_plan(plan,DAY)
    assert proof["raw_integrity_verified"] is True, proof["issues"]
    assert proof["official_raw_reparsed_race_count"]==12
    assert proof["total_declared_runners"]==24
    assert proof["planned_required_cells"]==696
    assert all(r["observation_relation_to_cutoff"]=="BEFORE_CUTOFF"
               for r in proof["races"])
    assert proof["signed_source"]=="NOT_VERIFIED"
    assert proof["source_license"]=="NOT_VERIFIED"
    assert proof["formal_authority_granted"] is False


def test_r7_rejects_self_hashed_invented_post_time():
    plan=_fixture_plan()
    plan["races"][0]["fields"]["scheduled_post_at"]="2026-11-02T14:55:00+09:00"
    proof=verify_fnb_plan(_rehash(plan),DAY)
    assert not proof["raw_integrity_verified"]
    assert any("OFFICIAL_CARD_PRINTED_CLOCK_MISMATCH" in x for x in proof["issues"])


def test_r7_rejects_self_hashed_forged_runner_identity():
    plan=_fixture_plan()
    row=plan["races"][3]
    row["declared_runner_universe"]["runners"][0]["name"]="偽の競走馬"
    row["declared_runner_universe"]["runner_universe_sha256"]=sha({
        k:v for k,v in row["declared_runner_universe"].items()
        if k!="runner_universe_sha256"})
    proof=verify_fnb_plan(_rehash(plan),DAY)
    assert not proof["raw_integrity_verified"]
    assert any("DECLARED_RUNNERS_DISAGREE_WITH_OFFICIAL_RAW" in x
               for x in proof["issues"])


def test_r7_rejects_raw_or_card_snapshot_tamper_even_when_plan_rehashed():
    plan=_fixture_plan()
    card=plan["official_snapshots"][2]
    card["raw_sha256"]="0"*64
    result=verify_fnb_plan(_rehash(plan),DAY)
    assert not result["raw_integrity_verified"]
    assert any("OFFICIAL_CARD_SNAPSHOT_HASH_MISMATCH" in x for x in result["issues"])
    plan=_fixture_plan()
    row=plan["races"][1]
    row["source_basis_sha256"]="f"*64
    result=verify_fnb_plan(_rehash(plan),DAY)
    assert not result["raw_integrity_verified"]
    assert any("SOURCE_BASIS_SNAPSHOT_MISMATCH" in x for x in result["issues"])


def test_r7_rejects_missing_menu_and_conflicting_card_identity():
    plan=_fixture_plan()
    plan["official_snapshots"].pop(0)
    p=verify_fnb_plan(_rehash(plan),DAY)
    assert "PLAN_DAY_MENU_COUNT_NOT_ONE" in p["issues"]
    plan=_fixture_plan()
    plan["official_snapshots"].append(copy.deepcopy(plan["official_snapshots"][1]))
    p=verify_fnb_plan(_rehash(plan),DAY)
    assert any("PLAN_DUPLICATE_OFFICIAL_CARD" in x for x in p["issues"])


def test_r7_rejects_fake_twelfth_race_even_with_self_consistent_shallow_sha():
    plan=_fixture_plan()
    plan["races"][11]["fields"]["race_no"]=11
    proof=verify_fnb_plan(_rehash(plan),DAY)
    assert not proof["raw_integrity_verified"]
    assert "PLAN_12_RACE_SET_MISSING_OR_DUPLICATE" in proof["issues"]


def test_r7_observed_raw_day_plan_still_cannot_authorize_formal(tmp_path):
    plan=_fixture_plan()
    p=tmp_path/"runtime/local_race_day_plan"/f"{DAY}-FNB.json"
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps(plan,ensure_ascii=False),encoding="utf-8")
    owner=tmp_path/"profiles/local_production_static_owner_20261014_v1.json"
    owner.parent.mkdir(parents=True)
    owner.write_text(json.dumps({"enabled":True,"venues":["KAW"],
        "family_authority_basis":"TEST_R7"}),encoding="utf-8")
    def authority(**_):
        return None,{"manifest_id":"TEST_R7"}
    def numeric(**_):
        return {"status":"READY",
                "prediction_consumption_authorized":False,
                "krs_consumption_authorized":False,
                "ticket_consumption_authorized":False,
                "capital_consumption_authorized":False}
    result=inspect_day(tmp_path,DAY,now=datetime(2026,11,2,10,tzinfo=JST),
                       numeric_assessor=numeric,authority_resolver=authority)
    assert result["dated_plan_exists_and_valid"] is True
    assert result["dated_plan_official_raw_reparsed"] is True
    assert result["formal_live_authorized_by_this_witness"] is False
    assert not result["dated_approval_present"]
    assert not result["fnb_static_owner_authorized"]
    assert result["races"][0]["planned_required_cells"]==58
    assert all(r["pfs"] is None for r in result["races"])



def test_r7_frozen_numeric_rejects_wrong_race_report_even_if_counts_appear_valid(tmp_path):
    from runtime import formal_execution_orchestrator as o
    from runtime.local_fnb_r6_numeric_readback import frozen_numeric_readback
    root=Path(__file__).resolve().parents[1]
    eid="LOCAL-KM-LOCAL-FNB-20261002-R04-LIVE-R1-EXEC"
    original=o.resolve_phase(eid,"FORMAL")
    assert original is not None
    run_id=original["latest"]["run_id"]
    report=json.loads((root/"runtime/execution_reports"/eid/(run_id+".json")).read_text())
    report["race_id"]="KM-LOCAL-FNB-20261002-R01-LIVE-R1"
    target=tmp_path/"runtime/execution_reports"/eid
    target.mkdir(parents=True)
    (target/(run_id+".json")).write_text(json.dumps(report))
    proof=frozen_numeric_readback(eid,original,tmp_path)
    assert proof["numeric_evidence_quality"]["status"]=="NUMERICAL_COUNTS_NOT_REPORTED"
    assert proof["numeric_checkpoint_consistency"]["consistency_verified"] is False
    assert "NUMERIC_LEDGER_READBACK_FAILED" in proof["numeric_readback_error"]


def test_r7_frozen_numeric_rejects_counters_forged_against_original_manifest(tmp_path):
    from runtime import formal_execution_orchestrator as o
    from runtime.local_fnb_r6_numeric_readback import frozen_numeric_readback
    root=Path(__file__).resolve().parents[1]
    eid="LOCAL-KM-LOCAL-FNB-20261002-R04-LIVE-R1-EXEC"
    original=o.resolve_phase(eid,"FORMAL")
    assert original is not None
    run_id=original["latest"]["run_id"]
    report=json.loads((root/"runtime/execution_reports"/eid/(run_id+".json")).read_text())
    report["completion"]["numeric_coverage"]["calculated_count"]=348
    report["completion"]["numeric_coverage"]["ruled_hold_count"]=0
    target=tmp_path/"runtime/execution_reports"/eid
    target.mkdir(parents=True)
    (target/(run_id+".json")).write_text(json.dumps(report))
    proof=frozen_numeric_readback(eid,original,tmp_path)
    assert proof["numeric_evidence_quality"]["status"]=="NUMERICAL_UNVERIFIED_FROZEN_COUNTER_MISMATCH"
    assert proof["numeric_evidence_quality"]["all_cells_calculated"] is False
    assert proof["numeric_checkpoint_consistency"]["consistency_verified"] is False
    assert proof["numeric_readback_error"]=="NUMERIC_REPORT_MATERIALIZED_MANIFEST_MISMATCH"



def test_r7_existing_dispatcher_rejects_self_hashed_fnb_plan_before_authority(monkeypatch,tmp_path):
    import pytest
    from runtime import local_race_day_dispatcher as dispatcher

    valid=_fixture_plan()
    valid["races"][0]["fields"]["scheduled_post_at"]="2026-11-02T14:55:00+09:00"
    forged=_rehash(valid)
    # Even with a self-consistent SHA and twelve numbered rows, the existing
    # actual authorization pathway must reject the stale/forged official clock.
    def forbidden(**_):
        raise AssertionError("MUST_FAIL_BEFORE_CURRENT_AUTHORITY_OR_DISPATCH")
    from runtime import family_authority_guard
    monkeypatch.setattr(family_authority_guard,"resolve_current_authority",forbidden)
    with pytest.raises(ValueError, match="FNB_DAY_PLAN_OFFICIAL_RAW_INTEGRITY_REQUIRED"):
        dispatcher.authorization({},forged,tmp_path,datetime(2026,11,2,9,tzinfo=JST))

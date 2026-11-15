"""Verify a saved FNB race's raw-backed full horse and active status.

This is a read-only integrity comparison, not source permission or signing.
"""
from runtime.local_fnb_r8_card_raw_check import check_card
from runtime.local_fnb_r8_odds_raw_check import check_odds
from runtime.local_physical.nar_runner_universe import enrich_source_artifact


def audit_race(row, snapshots, race_date):
    n = row["fields"]["race_no"]
    prefix = f"NAR-FNB-{race_date.replace('-', '')}-R{n:02d}"
    card = snapshots[prefix+"-RACE-CARD"]
    parsed = check_card(card, race_date, n)
    if row["declared_runner_universe"]["runners"] != parsed["card_runners"]:
        raise ValueError("DECLARED_HORSE_BODYWEIGHT_OR_DRAW_MISMATCH")
    ev = {"race_card_tables": {
        "value": parsed["extracted"]["race_card_tables"],
        "source_id": card["source_id"],
        "snapshot_sha256": card["snapshot_sha256"]}}
    odds = snapshots.get(prefix+"-ODDS-TANFUKU")
    if odds is not None:
        if row.get("odds_observation_error") is not None:
            raise ValueError("ODDS_ERROR_WITH_VALID_SNAPSHOT")
        parsed_odds = check_odds(odds, race_date, n)
        ev["odds_tables"] = {
            "value": parsed_odds.get("odds_tables"),
            "source_id": odds["source_id"],
            "snapshot_sha256": odds["snapshot_sha256"]}
    elif not row.get("odds_observation_error"):
        raise ValueError("ODDS_UNKNOWN_REASON_MISSING")
    rebuilt = enrich_source_artifact({"normalized_evidence": ev})
    if rebuilt["runner_status_registry"] != row.get("runner_status_registry"):
        raise ValueError("CANCELLED_OR_ACTIVE_STATUS_MISMATCH")
    active_known = not any(s["status"]=="ACTIVE_DECLARED"
                           for s in rebuilt["runner_status_registry"])
    active = rebuilt["active_runner_universe"] if active_known else None
    if row.get("observed_active_runner_universe") != active:
        raise ValueError("ACTIVE_UNIVERSE_LINEAGE_MISMATCH")
    status = ("OFFICIAL_OBSERVATION_REQUIRES_DISPATCH_RECHECK" if active_known
              else "UNKNOWN_PENDING_FRESH_SIGNED_SOURCE")
    if row.get("active_universe_status") != status:
        raise ValueError("ACTIVE_UNIVERSE_AUTHORITY_MISMATCH")
    return {"race_no":n, "runner_count":len(parsed["card_runners"]),
            "cancelled":sum(x["status"]=="CANCELLED"
                            for x in rebuilt["runner_status_registry"]),
            "active_verified":False, "odds_reparsed":odds is not None,
            "raw_sha256":card["raw_sha256"]}

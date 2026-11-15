"""Offline 12-race semantic replay of an already frozen FNB discovery plan."""
from runtime.local_fnb_r7_plan_provenance import verify_fnb_plan
from runtime.local_fnb_r8_single_race_semantics import audit_race


def audit_day(plan, race_date):
    base = verify_fnb_plan(plan, race_date)
    issues = list(base.get("issues") or [])
    rows = []
    if not base.get("raw_integrity_verified"):
        return {"status":"FNB_DAY_R7_RAW_HOLD", "issues":issues, "races":rows,
                "formal_authority":False, "signed_source_proven":False}
    snapshots = {}
    for src in plan.get("official_snapshots", []):
        name = src.get("source_id") if isinstance(src, dict) else None
        if not name or name in snapshots:
            issues.append("SNAPSHOT_SOURCE_ID_INVALID_OR_DUPLICATE")
        else:
            snapshots[name] = src
    for r in plan["races"]:
        try:
            rows.append(audit_race(r, snapshots, race_date))
        except (KeyError, TypeError, ValueError, OSError, EOFError) as exc:
            num = r.get("fields", {}).get("race_no", "?")
            issues.append(f"R{num}:{type(exc).__name__}:{exc}")
    if len(rows) != 12:
        issues.append("SEMANTIC_REPLAY_NOT_ALL_12_RACES")
    return {"status":"FNB_DAY_SEMANTICS_CONSISTENT" if not issues else
            "FNB_DAY_SEMANTICS_HOLD", "issues":issues[:60],
            "verified_races":len(rows), "races":rows,
            "formal_authority":False, "signed_source_proven":False,
            "personal_delivery_proven":False}

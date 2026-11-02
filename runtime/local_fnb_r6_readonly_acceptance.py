"""FNB day acceptance witness, intentionally offline and non-activating.

This reader never fetches a provider URL, dispatches Actions, invokes a
simulation, emits a signed receipt, or changes Production. It distinguishes
repository-snapshot presence from verified live execution, actual recipient
delivery, and authorized numerical consumption. A missing file is not
proof that no external run exists.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import json
from pathlib import Path

from runtime.local_numerical_authority_gate import assess as assess_numeric
from runtime.local_race_day_dispatcher import sha as plan_sha

PROFILE = "KM-FNB-R6-READONLY-ACCEPTANCE-WITNESS-v1"
CONSUMERS = ("prediction_consumption_authorized", "krs_consumption_authorized",
             "ticket_consumption_authorized", "capital_consumption_authorized")


def _json(path: Path):
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("REQUIRED_JSON_OBJECT:" + str(path))
    return value



def cutoff_disposition(fields: dict | None, *, now: datetime) -> str:
    """Never convert post-cutoff diagnostic work into prestart success."""
    if not isinstance(fields, dict):
        return "OFFICIAL_CUTOFF_NOT_PROVEN"
    try:
        post = datetime.fromisoformat(str(fields["scheduled_post_at"]).replace("Z", "+00:00"))
        cutoff = datetime.fromisoformat(str(fields["prediction_cutoff"]).replace("Z", "+00:00"))
    except (TypeError, ValueError, KeyError):
        return "OFFICIAL_CUTOFF_NOT_PROVEN"
    if post.tzinfo is None or cutoff.tzinfo is None or cutoff >= post:
        return "OFFICIAL_CUTOFF_INVALID"
    if now.tzinfo is None:
        return "OBSERVATION_CLOCK_INVALID"
    if now >= cutoff:
        return "CUTOFF_EXPIRED_DIAGNOSTIC_ONLY_NO_RETROACTIVE_PRESTART"
    return "PRE_CUTOFF_WINDOW_OBSERVED_AUTHORIZATION_STILL_REQUIRED"

def inspect(root: Path, race_date: str, *, now: datetime | None = None,
            numeric_assessor=None, authority_resolver=None) -> dict:
    """Check existing signed-execution prerequisites without granting them.

    The plan is valid only when it exists, identifies FNB/date and has the
    correct checksum. The dated approval is never inferred from a plan or a
    request. An owner profile listing only KAW cannot authorize FNB.
    """
    root = Path(root)
    if date.fromisoformat(race_date).isoformat() != race_date:
        raise ValueError("FNB_DATE_ISO_REQUIRED")
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("AWARE_OBSERVATION_TIME_REQUIRED")
    blockers: list[str] = []
    def block(code):
        if code not in blockers:
            blockers.append(code)

    owner_path = root / "profiles/local_production_static_owner_20261014_v1.json"
    try:
        owner = _json(owner_path)
        owner_venues = owner.get("venues", [])
        owner_scope = (owner.get("enabled") is True
                       and isinstance(owner_venues, list)
                       and "FNB" in owner_venues)
        if not owner_scope:
            block("FNB_PRODUCTION_STATIC_OWNER_NOT_AUTHORIZED")
    except (OSError, ValueError, TypeError) as exc:
        owner_venues, owner_scope = [], False
        block("PRODUCTION_OWNER_PROFILE_UNAVAILABLE_OR_INVALID:" + type(exc).__name__)

    try:
        from runtime.family_authority_guard import resolve_current_authority
        resolver = authority_resolver or resolve_current_authority
        _, authority = resolver(root=root, now=now)
        authority_id = authority["manifest_id"]
        if owner_scope and owner.get("family_authority_basis") != authority_id:
            owner_scope = False
            block("FNB_STATIC_OWNER_AUTHORITY_BASIS_MISMATCH")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        authority_id = None
        block("CURRENT_AUTHORITY_UNRESOLVED:" + type(exc).__name__)

    try:
        registry = root / "mapping"
        checker = numeric_assessor or assess_numeric
        numerical = checker(
            evidence_registry_path=registry / "local_evidence_feature_rule_registry_v1.1_production_numerical_20261008.json",
            mapping_registry_path=registry / "local_full_numerical_mapping_v1.0_production_20261008.json")
        materialization_ready = numerical.get("status") == "READY"
        if not materialization_ready:
            block("FULL29_NUMERICAL_MATERIALIZER_NOT_READY")
        consumption = {k: numerical.get(k) is True for k in CONSUMERS}
        for k, enabled in consumption.items():
            if not enabled:
                block("NUMERICAL_CONSUMER_SCOPE_NOT_AUTHORIZED:" + k)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        materialization_ready = False
        consumption = {k: False for k in CONSUMERS}
        block("NUMERICAL_AUTHORITY_UNRESOLVED:" + type(exc).__name__)

    plan_path = root / "runtime/local_race_day_plan" / f"{race_date}-FNB.json"
    approval_path = root / "profiles/local_autonomous_approvals" / f"{race_date}-FNB.json"
    plan, approval = None, None
    if not plan_path.is_file():
        block("FNB_DATED_OFFICIAL_DAY_PLAN_NOT_OBSERVED")
    else:
        try:
            plan = _json(plan_path)
            if (plan.get("family_id") != "LOCAL" or plan.get("venue_id") != "FNB"
                    or plan.get("race_date") != race_date
                    or plan.get("plan_sha256") != plan_sha({k: v for k, v in plan.items()
                                                            if k != "plan_sha256"})):
                raise ValueError("DAY_PLAN_IDENTITY_OR_SHA_MISMATCH")
            rows = plan.get("races")
            numbers = [r["fields"]["race_no"] for r in rows]
            if (not isinstance(rows, list) or sorted(numbers) != list(range(1, 13))
                    or any(type(n) is not int for n in numbers)):
                raise ValueError("FNB_COMPLETE_OFFICIAL_12R_PLAN_REQUIRED")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            plan = None
            block("FNB_DATED_PLAN_INVALID:" + str(exc))

    if not approval_path.is_file():
        block("FNB_DATED_OWNER_APPROVAL_NOT_OBSERVED")
    else:
        try:
            approval = _json(approval_path)
            if plan is None:
                block("FNB_APPROVAL_HAS_NO_VALID_PLAN")
            else:
                # The existing dispatcher enforces dated scope, phase promotion,
                # bounded dispatch/cost, authority and owner identity.
                from runtime.local_race_day_dispatcher import authorization
                if authority_id is None:
                    block("FNB_APPROVAL_AUTHORITY_UNRESOLVED")
                else:
                    authorization(approval, plan, root, now)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            block("FNB_DATED_APPROVAL_INVALID:" + str(exc))

    # The source license is not proven merely by viewing a public page.
    # A signed receipt is also not evidence of recipient ACK.
    block("CURRENT_FNB_OFFICIAL_SOURCE_LICENSE_AND_SIGNED_INTAKE_UNVERIFIED")
    block("CURRENT_FNB_DELIVERY_RECIPIENT_ACK_UNVERIFIED")

    by_no = {}
    if plan is not None:
        by_no = {int(r["fields"]["race_no"]): r for r in plan["races"]}
    races = []
    for n in range(1, 13):
        planned = by_no.get(n)
        existing = sorted((root / "runtime/executions").glob(
            f"*FNB*{race_date.replace('-', '')}*R{n:02d}*"))
        # No signatures are verified in this read-only witness.
        phases = {p: False for p in ("SOURCE", "FORMAL", "RESULT")}
        for folder in existing:
            if folder.is_dir():
                for phase in phases:
                    phases[phase] |= (folder / phase / "LATEST.json").is_file()
        races.append({
            "race_no": n,
            "scheduled_post_at": (planned or {}).get("fields", {}).get("scheduled_post_at"),
            "cutoff_disposition": cutoff_disposition((planned or {}).get("fields"), now=now),
            "runner_count": (planned or {}).get("declared_runner_universe", {}).get("runner_count"),
            "planned_required_cells": None if planned is None else
                29 * len((planned.get("declared_runner_universe") or {}).get("runners") or []),
            "source_checkpoint": "PERSISTED_UNVERIFIED" if phases["SOURCE"] else "NOT_OBSERVED_IN_REPO",
            "formal_checkpoint": "PERSISTED_UNVERIFIED" if phases["FORMAL"] else "NOT_OBSERVED_IN_REPO",
            "result_checkpoint": "PERSISTED_UNVERIFIED" if phases["RESULT"] else "NOT_OBSERVED_IN_REPO",
            "actual_29_index_calculation": "NOT_VERIFIED",
            "signed_final_prestart": "NOT_VERIFIED",
            "krs_5000": "NOT_VERIFIED",
            "delivery_recipient_ack": "NOT_VERIFIED",
            "ticket_status": "NOT_COMPUTED_OR_NOT_VERIFIED",
            "no_bet_proven": False,
            "pfs": None,
            "pfs_disposition": "NULL_UNTIL_VERIFIED_SELECTION_AND_SETTLEMENT",
        })

    return {
        "profile": PROFILE,
        "classification": "READ_ONLY_REPOSITORY_SNAPSHOT / NON_PRODUCTION / NOT_REGISTERED_OOS",
        "race_date": race_date, "venue_id": "FNB",
        "observed_at": now.isoformat(), "authority_manifest_observed": authority_id,
        "owner_venues": owner_venues, "fnb_static_owner_authorized": owner_scope,
        "production_numeric_materialization_ready": materialization_ready,
        "numeric_consumption": consumption,
        "dated_plan_exists_and_valid": plan is not None,
        "plan_validation_scope": "FILE_IDENTITY_SHA_AND_RACE_SET_ONLY_NOT_FRESH_OFFICIAL",
        "dated_approval_present": approval is not None,
        "formal_live_authorized_by_this_witness": False,
        "blockers": blockers,
        "races": races, "target_race_count": 12,
        "current_day_calculated_cells_verified": 0,
        "current_day_signed_final_verified": 0,
        "current_day_delivery_ack_verified": 0,
        "evidence_scope": "COUNTS_ARE_VERIFIED_IN_THIS_READ_ONLY_REPOSITORY_CHECK_ONLY",
        "runtime_and_private_store_not_queried": True,
        "new_github_workflow_dispatches": 0, "new_runtime_posts": 0,
        "production_changed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--date", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = inspect(Path(args.root), args.date)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                      encoding="utf-8")
    print(json.dumps({"status": "READ_ONLY_NOT_LIVE", "blockers": result["blockers"],
                      "output": str(target)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""FNB private, noncommercial research use: explicit purpose, not Production grant.

The user has declared wholly private/noncommercial KeibaMetrics use. For a
separately authorized SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS
execution, absent v2 full-day OOS plan or Production Consumer activation must
NOT be misclassified as a failure of the independent private numerical lane.

A user purpose declaration is not an Ed25519 SOURCE receipt or a technical
assurance that a provider permits a particular automated transport. No raw
source, model, user file, or private prediction may be published in the
PUBLIC GitHub repository or its public Actions artifacts by this lane.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

SCOPE="SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS"
PURPOSE="WHOLLY_PRIVATE_NONCOMMERCIAL_RESEARCH"

def _stamp(v):
    t=datetime.fromisoformat(str(v).replace("Z","+00:00"))
    if t.tzinfo is None:
        raise ValueError("PRIVATE_SOURCE_TIMESTAMP_TIMEZONE_REQUIRED")
    return t

def admit(*, source:dict, request:dict, purpose:str, classification:str,
          destination:Path, public_repo_root:Path):
    if purpose!=PURPOSE or classification!=SCOPE:
        raise ValueError("PRIVATE_SOURCE_USE_SCOPE_NOT_EXPLICIT")
    destination=Path(destination).resolve()
    public_repo_root=Path(public_repo_root).resolve()
    if destination==public_repo_root or public_repo_root in destination.parents:
        raise ValueError("PRIVATE_RAW_OR_FULL_PREDICTION_PUBLIC_GIT_REPO_FORBIDDEN")
    if (not isinstance(source,dict) or not isinstance(request,dict)
            or request.get("venue_id")!="FNB"):
        raise ValueError("FNB_PRIVATE_SOURCE_AND_INTENT_REQUIRED")
    race=request.get("race") or {}
    day=str(request.get("race_date") or race.get("race_date") or "")
    n=request.get("race_no") or race.get("race_no")
    context=source.get("source_race_context") or {}
    if (context.get("venue_id")!="FNB" or
            str(context.get("race_date") or "").replace("/","-")!=day or
            context.get("race_no")!=n or
            source.get("race_id")!=request.get("race_id")):
        raise ValueError("PRIVATE_SOURCE_RACE_IDENTITY_MISMATCH")
    fetched=_stamp(source["source_freeze_at"])
    cutoff=_stamp(request["prediction_cutoff"])
    post=_stamp(request["scheduled_post_at"])
    if not fetched<cutoff<post:
        raise ValueError("PRIVATE_OFFICIAL_SOURCE_NOT_PRESTART_FRESH")
    sources=source.get("sources") or []
    matching=[s for s in sources if isinstance(s,dict) and
              s.get("official") is True and
              s.get("source_class")=="OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT"]
    if len(matching)!=1:
        raise ValueError("PRIVATE_ONE_ORIGINAL_NAR_RACE_CARD_REQUIRED")
    card=matching[0]
    if (not card.get("source_id") or not card.get("snapshot_sha256")
            or not card.get("raw_sha256")
            or len(str(card["snapshot_sha256"]))!=64):
        raise ValueError("PRIVATE_ORIGINAL_RAW_PROVENANCE_UNPROVEN")
    declared=source.get("declared_runner_universe") or {}
    if not isinstance(declared.get("runners"),list) or not declared["runners"]:
        raise ValueError("PRIVATE_OFFICIAL_DECLARED_RUNNERS_NOT_OBSERVED")
    return {
        "status":"PRIVATE_NUMERICAL_LANE_SOURCE_METADATA_ADMITTED",
        "classification":SCOPE,"use_purpose":PURPOSE,
        "runner_count_declared":len(declared["runners"]),
        "source_snapshot_sha256":card["snapshot_sha256"],
        "source_raw_sha256":card["raw_sha256"],
        "source_freeze_at":source["source_freeze_at"],
        "cutoff_at":request["prediction_cutoff"],
        "private_destination_class":"OUTSIDE_PUBLIC_REPOSITORY",
        "full_v2_dated_oos_plan_required_for_this_lane":False,
        "formal_owner_or_numeric_consumers_authorized":False,
        "registered_oos_increment":0,
        "issuer_signature_verified_here":False,
        "raw_bytes_reparsed_here":False,
        "source_provider_access_policy_verified_here":False,
        "source_metadata_is_not_full_29_calculation":True,
        "private_use_does_not_authorize_public_distribution":True
    }

"""R10 FNB signed Race ID ↔ execution store key binding.

Actual historical LOCAL receipt.race_id is KM-LOCAL-FNB-YYYYMMDD-RXX-LIVE-Rn;
the execution-store directory is LOCAL-<race_id>-EXEC. They are not equal.
This helper keeps the two IDs distinct while requiring an exact one-to-one
canonical relation. No signer, source, venue, policy, scope or new permission.
"""
from __future__ import annotations

from datetime import date
import re

PATTERN=re.compile(
    r"^LOCAL-(KM-LOCAL-FNB-(\d{8})-R(\d{2})-LIVE-R([1-9]\d*))-EXEC$")


def expected_race_id(execution_id, source_artifact=None):
    match=PATTERN.fullmatch(str(execution_id or ""))
    if match is None:
        raise ValueError("FNB_CANONICAL_EXECUTION_ID_REQUIRED")
    signed_id, day, number, revision=match.groups()
    if int(number)<1 or int(number)>12:
        raise ValueError("FNB_RACE_NO_RANGE_INVALID")
    date.fromisoformat(day[:4]+"-"+day[4:6]+"-"+day[6:8])
    if source_artifact is not None:
        if not isinstance(source_artifact,dict):
            raise ValueError("FNB_SIGNED_SOURCE_ARTIFACT_REQUIRED")
        ctx=source_artifact.get("source_race_context")
        if not isinstance(ctx,dict):
            raise ValueError("FNB_SIGNED_SOURCE_CONTEXT_MISSING")
        observed=str(ctx.get("race_date") or "").replace("/","").replace("-","")
        if (source_artifact.get("race_id")!=signed_id
                or ctx.get("venue_id")!="FNB"
                or observed!=day or str(ctx.get("race_no"))!=str(int(number))):
            raise ValueError("FNB_SIGNED_SOURCE_RACE_IDENTITY_MISMATCH")
    return signed_id


def local_receipt_race_id(execution_id, source_artifact=None):
    """Preserve legacy behavior for every non-FNB venue."""
    eid=str(execution_id or "")
    if eid.startswith("LOCAL-KM-LOCAL-FNB-"):
        return expected_race_id(eid,source_artifact)
    return eid

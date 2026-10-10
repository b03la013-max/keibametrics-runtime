"""Current official detailed card takes precedence over planned calendar races.

Old signed artifacts remain immutable. Their retained raw card can be parsed
into a receipt-bound context view without changing their artifact/hash.
"""
from __future__ import annotations

import base64
from copy import deepcopy
import gzip
import hashlib
import io

try:
    from .jra_race_card_detail import parse_detail_race_context
    from .source_acquisition import sha_obj
except ImportError:
    from jra_race_card_detail import parse_detail_race_context
    from source_acquisition import sha_obj


FIELDS = ("race_date", "venue_id", "race_no", "surface", "distance_m", "race_class", "scheduled_post_at")


def resolve_observed_context(artifact):
    detail = artifact.get("jra_official_race_card_detail") or {}
    snapshots = [x for x in artifact.get("sources") or []
                 if x.get("source_id") == "JRA-OFFICIAL-RACE-CARD-DETAIL"
                 and x.get("snapshot_sha256") == detail.get("source_snapshot_sha256")]
    context = detail.get("race_context")
    if snapshots:
        if len(snapshots) != 1:
            raise ValueError("JRA_DETAIL_CONTEXT_SNAPSHOT_AMBIGUOUS")
        snap = snapshots[0]
        if snap.get("official") is not True or snap.get("authority") != "JRA_OFFICIAL":
            raise ValueError("JRA_DETAIL_CONTEXT_NOT_OFFICIAL")
        if snap.get("cutoff_relation") != "PRE_CUTOFF":
            raise ValueError("JRA_DETAIL_CONTEXT_AFTER_CUTOFF")
        if snap.get("raw_gzip_b64"):
            with gzip.GzipFile(fileobj=io.BytesIO(base64.b64decode(snap["raw_gzip_b64"],validate=True))) as stream:
                raw = stream.read(6000001)
            if len(raw) > 6000000 or hashlib.sha256(raw).hexdigest() != snap.get("raw_sha256"):
                raise ValueError("JRA_DETAIL_CONTEXT_RAW_HASH_INVALID")
            observed = parse_detail_race_context(raw,snap.get("content_type", ""))
            if context is not None and context != observed:
                raise ValueError("JRA_DETAIL_CONTEXT_PARSED_RAW_MISMATCH")
            context = observed
        if context is None:
            raise ValueError("JRA_DETAIL_CONTEXT_NOT_OBSERVED")
        context = {**context,"context_source_snapshot_sha256":snap["snapshot_sha256"],
                   "context_source_raw_sha256":snap["raw_sha256"],
                   "context_source":"JRA_OFFICIAL_DETAILED_CARD"}
    elif context is not None:
        # An unbound parsed assertion cannot override signed calendar evidence.
        raise ValueError("JRA_DETAIL_CONTEXT_SOURCE_BINDING_REQUIRED")
    else:
        return deepcopy(artifact.get("jra_race_context") or {})
    identity = artifact.get("source_race_context") or {}
    for field in ("race_date", "venue_id", "race_no"):
        if str(context.get(field)) != str(identity.get(field)):
            raise ValueError("JRA_DETAIL_CONTEXT_IDENTITY_MISMATCH:" + field)
    context["sha256"] = sha_obj(context)
    return context


def bind_observed_context(artifact):
    """Called during new SOURCE acquisition, before external signing."""
    context = resolve_observed_context(artifact)
    if context.get("context_source") != "JRA_OFFICIAL_DETAILED_CARD":
        raise ValueError("JRA_OBSERVED_DETAIL_CONTEXT_REQUIRED")
    planned = artifact.get("jra_race_context") or {}
    artifact["jra_calendar_race_context"] = deepcopy(planned)
    artifact["jra_race_context_reconciliation"] = {
        "status":"OBSERVED_DETAIL_PRECEDENCE",
        "differences":{k:{"planned":planned.get(k),"observed":context.get(k)}
                       for k in FIELDS if planned.get(k) != context.get(k)},
        "planned_context_sha256":planned.get("sha256"),
        "observed_context_sha256":context["sha256"],
    }
    artifact["jra_race_context"] = context
    artifact["jra_race_context_sha256"] = sha_obj(context)
    return artifact

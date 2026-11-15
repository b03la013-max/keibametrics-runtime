"""Research-only FNB SOURCE -> descriptive Venue antecedents.

This compiler prepares the observations which the absent FNB interpretation
producer needs.  It is not a Context/model adoption: historical position
sequences are not today's reachable range, race demand, intention, or cost.
No thresholds, scores, role changes, signer or registry are introduced.
"""
from __future__ import annotations

import base64
import copy
from datetime import datetime
import gzip
import hashlib
import unicodedata
import re

from runtime.local_fnb_venue_context_binding import CANON, MODULE_FIELDS, canonical_sha256
from runtime.local_nar_evidence_candidate import parse_race_card
from runtime.local_physical.source_acquisition import _decode, _html_tables, verify_source_artifact
from runtime.local_production_static_owner import _card_heading, _dt, _start_date, JST
from runtime.local_fnb_r11_venue_temporal import verify as verify_temporal

PROFILE = "KM-FNB-OBSERVATION-ANTECEDENTS-RESEARCH-v0.1-20261103"


def build_observation_packet(request, envelope, *, generated_at):
    """Compile immutable official historical observations, never model outputs.

    The caller must verify the envelope's cryptographic signature separately.
    Here artifact hashes and raw->table equality are independently required.
    Historical replays use actual generated_at; no prestart status is inferred.
    """
    source = envelope.get("artifact") or {}
    valid, errors = verify_source_artifact(source)
    if not valid:
        raise ValueError("FNB_OBSERVATION_SOURCE_INVALID:" + ",".join(errors))
    if request.get("venue_id") != "FNB" or source.get("race_id") != request.get("race_id"):
        raise ValueError("FNB_OBSERVATION_RACE_IDENTITY_MISMATCH")
    receipt = envelope.get("receipt") or {}
    if (not envelope.get("signature") or receipt.get("family") != "LOCAL" or
            receipt.get("phase") != "SOURCE" or receipt.get("status") != "SOURCE_FROZEN" or
            receipt.get("race_id") != request.get("race_id") or receipt.get("errors") or
            canonical_sha256(receipt) != envelope.get("receipt_sha256") or
            receipt.get("artifact_sha256") != canonical_sha256(source)):
        raise ValueError("FNB_OBSERVATION_ENVELOPE_HASH_MISMATCH")
    temporal = verify_temporal(source_artifact=source, request=request)
    header = _card_heading(source, expected_race=request)
    cards = [s for s in source["sources"]
             if s.get("source_class") == "OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT"
             and s.get("official") is True]
    card = cards[0]  # _card_heading has already required exactly one.
    if card.get("stale") is True or card.get("current") is False:
        raise ValueError("FNB_OBSERVATION_OFFICIAL_CARD_NOT_CURRENT_AT_FREEZE")
    raw = gzip.decompress(base64.b64decode(card["raw_gzip_b64"], validate=True))
    raw_tables = _html_tables(_decode(raw, card.get("content_type", "text/html")))
    carrier = (source.get("normalized_evidence") or {}).get("race_card_tables") or {}
    if (carrier.get("source_id") != card.get("source_id") or
            carrier.get("snapshot_sha256") != card.get("snapshot_sha256") or
            carrier.get("fetched_at") != card.get("fetched_at") or
            carrier.get("value") != raw_tables):
        raise ValueError("FNB_OBSERVATION_RAW_NORMALIZED_TABLE_MISMATCH")
    rows = parse_race_card(source)
    active = (source.get("active_runner_universe") or source.get("official_runner_universe") or {}).get("runners") or []
    ids = [str(row.get("runner_id")) for row in active]
    if (len(ids) < 2 or len(ids) != len(set(ids)) or not set(ids).issubset(rows) or
            any(rows[str(row["runner_id"])]["name"] != row["name"] for row in active)):
        raise ValueError("FNB_OBSERVATION_ACTIVE_UNIVERSE_MISMATCH")
    status_rows = source.get("runner_status_registry") or []
    status_ids = [str(row.get("runner_id")) for row in status_rows]
    if (len(status_ids) != len(set(status_ids)) or set(status_ids) != set(rows) or
            {str(row.get("runner_id")) for row in status_rows if row.get("status") == "ACTIVE"} != set(ids)):
        raise ValueError("FNB_OBSERVATION_ACTIVE_STATUS_UNIVERSE_MISMATCH")
    post = _dt(request["scheduled_post_at"])
    generated = _dt(generated_at)
    freeze = _dt(source["source_freeze_at"])
    if generated < freeze:
        raise ValueError("FNB_OBSERVATION_GENERATION_BEFORE_SOURCE_FREEZE")
    day = post.astimezone(JST).replace(hour=0, minute=0, second=0, microsecond=0)
    fetched_day = _dt(card["fetched_at"]).astimezone(JST).date()
    runners, total, trajectories = [], 0, 0
    for rid in ids:
        antecedents = []
        for start in rows[rid].get("starts") or []:
            observed = _start_date(start.get("date"))
            if observed is None:
                continue
            if observed >= day or observed.date() > fetched_day:
                raise ValueError("FNB_OBSERVATION_HISTORICAL_EVENT_AFTER_AVAILABLE_TIME")
            venue = re.sub(r"\s+", "", unicodedata.normalize("NFKC", str(start.get("venue") or "")))
            # Export actual FNB dirt evidence only, never transfer another venue's
            # behavior as FNB reachability/cost or silently invent a course ID.
            if venue not in {"船橋", "船橋ナ", "FNB"} or start.get("surface") != "DIRT":
                continue
            count, finish = start.get("field_size"), start.get("finish")
            positions = start.get("content_positions") or []
            if (type(count) is not int or count < 2 or type(finish) is not int or
                    not 1 <= finish <= count or not isinstance(positions, list) or
                    any(type(p) is not int or not 1 <= p <= count for p in positions)):
                raise ValueError("FNB_OBSERVATION_HISTORICAL_POSITION_INVALID")
            antecedents.append({"event_date": observed.date().isoformat(),
                "venue_label": start["venue"], "distance_m": start.get("distance"),
                "going": start.get("going"), "field_size": count, "finish": finish,
                "printed_position_sequence": copy.deepcopy(positions),
                "same_distance": start.get("distance") == header["distance"],
                "source_id": card["source_id"], "source_raw_sha256": card["raw_sha256"],
                "source_fetched_at": card["fetched_at"],
                "permanent_race_id": None,
                "identity_limit": "printed date/venue/distance/horse; permanent historical Race ID absent"})
            total += 1
            trajectories += bool(positions)
        runners.append({"runner_id": rid, "name": rows[rid]["name"],
                        "historical_fnb_observations": antecedents,
                        "historical_evidence_status": "OBSERVED" if antecedents else "UNKNOWN"})
    output = {"profile": PROFILE, "venue_canon": CANON,
        "classification": "PRIVATE_RESEARCH_UNADOPTED_NOT_REGISTERED_OOS",
        "race_id": request["race_id"], "generated_at": generated_at,
        "source_freeze_at": source["source_freeze_at"],
        "source_receipt_sha256": envelope["receipt_sha256"],
        "source_snapshot_sha256": source["source_snapshot_sha256"],
        "raw_card_sha256": hashlib.sha256(raw).hexdigest(),
        "raw_to_normalized_tables_equal": True,
        "source_signature_verification": "CALLER_CRYPTOGRAPHIC_VERIFICATION_REQUIRED_NOT_GRANTED_HERE",
        "prestart_generation": generated < _dt(request["prediction_cutoff"]),
        "header": header, "runners": runners,
        "counts": {"active_runners": len(runners), "historical_fnb_starts": total,
                   "printed_position_sequences": trajectories},
        "same_day_temporal_receipt": temporal,
        "predictive_modules": {module: {"status": "UNKNOWN", "value": None,
            "reason": "FNB qualitative interpretation producer not adopted/implemented; antecedents are not its output"}
            for module in MODULE_FIELDS if module != "CURRENT_TRACK_STATE_CLASSIFY"},
        "formal_context_ready": False, "owner_scope_granted": False,
        "role_or_rank_changed": False, "numerical_policy_changed": False,
        "forward_oos_credit": 0}
    output["sha256"] = canonical_sha256(output)
    return output

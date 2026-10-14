"""Result-blind LOCAL static-owner *hypothesis* from Production-numerical data.

NON-PRODUCTION paper baseline only. Existing numerically closed 29-index
records are uncalibrated and explicitly forbid Production Prediction/Ticket
consumption. This shadow output never enters the FORMAL external request.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
from typing import Any


PROFILE = "KM-LOCAL-RACE-KEY-STATIC-SHADOW-v0.1-20261014"
VALID = {"CALCULATED", "RULED-NEUTRAL"}
INDEXES = ("ZAI-WIN", "ZAI-PLACE", "T3I-L")
COLUMNS = ("W", "P2", "P3")


class ShadowOwnerError(ValueError):
    pass


def _sha(payload: Any) -> str:
    return hashlib.sha256(json.dumps(
        payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")).hexdigest()


def _aware(value: str, name: str) -> datetime:
    try:
        stamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ShadowOwnerError(name + "_INVALID") from exc
    if stamp.tzinfo is None:
        raise ShadowOwnerError(name + "_TIMEZONE_REQUIRED")
    return stamp.astimezone(timezone.utc)


def _ranking(rows: list[dict], name: str) -> list[str]:
    # RULED-NEUTRAL is unknown/incomparable, NOT an estimate of weak ability.
    # Keep all runners and label neutral values; no negative missingness scores.
    # Unknowns are not compared numerically with CALCULATED estimates.
    def identifier_key(rid: str):
        return (0, int(rid)) if rid.isdigit() else (1, rid)

    calculated, unknown = [], []
    for row in rows:
        spec = row["canonical_components"][name]
        rid = str(row["runner_id"])
        (unknown if spec["terminal_status"] == "RULED-NEUTRAL" else calculated).append(
            (float(spec["value"]), rid)
        )
    return ([rid for _, rid in sorted(calculated, key=lambda v: (-v[0], identifier_key(v[1])))]
            + [rid for _, rid in sorted(unknown, key=lambda v: identifier_key(v[1]))])


def compile_shadow(
    request: dict,
    source_envelope: dict,
    materialized: dict,
    *,
    now: datetime | None = None,
) -> dict:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ShadowOwnerError("CURRENT_TIME_TZ_REQUIRED")
    if request.get("family_id") != "LOCAL":
        raise ShadowOwnerError("LOCAL_FAMILY_ONLY")
    eid = str(request.get("execution_id") or "")
    if not eid or eid != request.get("race_id"):
        raise ShadowOwnerError("RACE_IDENTITY_INVALID")
    if source_envelope.get("receipt_sha256") in ("", None):
        raise ShadowOwnerError("SOURCE_SIGNED_RECEIPT_REQUIRED")
    source = source_envelope.get("artifact") or {}
    source_time = _aware(source.get("source_freeze_at"), "SOURCE_FREEZE_AT")
    cutoff = _aware(request.get("prediction_cutoff"), "PREDICTION_CUTOFF")
    if source_time >= cutoff or now.astimezone(timezone.utc) >= cutoff:
        raise ShadowOwnerError("SHADOW_FREEZE_AFTER_PRESTART_CUTOFF")
    if source.get("formal_ready") is not True:
        raise ShadowOwnerError("SOURCE_NOT_READY")
    if materialized.get("strict_full_numerical_ready") is not True:
        raise ShadowOwnerError("FULL_29_INDEX_TERMINAL_REQUIRED")
    summary = materialized.get("production_numerical_authority") or {}
    if summary.get("prediction_consumption_authorized") is not False:
        raise ShadowOwnerError("NUMERICAL_PROMOTION_SCOPE_UNEXPECTED")
    rows = materialized.get("runners") or []
    universe = source.get("official_runner_universe") or {}
    official = universe.get("runners") or []
    official_ids = {str(row.get("runner_id")) for row in official}
    ids = [str(row.get("runner_id")) for row in rows]
    if len(rows) < 2 or len(ids) != len(set(ids)) or set(ids) != official_ids:
        raise ShadowOwnerError("FULL_RUNNER_UNIVERSE_MISMATCH")
    if len(materialized.get("required_indices") or []) != 29:
        raise ShadowOwnerError("REQUIRED_INDEX_MANIFEST_INCOMPLETE")
    neutrals = {}
    for row in rows:
        rid = str(row["runner_id"])
        cc = row.get("canonical_components") or {}
        if len(cc) != 29:
            raise ShadowOwnerError("RUNNER_FULL29_REQUIRED:" + rid)
        n = []
        for key in INDEXES:
            spec = cc.get(key) or {}
            term = str(spec.get("terminal_status") or "")
            val = spec.get("value")
            if term not in VALID or isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(val):
                raise ShadowOwnerError("INDEX_NOT_TERMINAL:" + rid + ":" + key)
            if term == "RULED-NEUTRAL":
                n.append(key)
        neutrals[rid] = n
    ranked = {k: _ranking(rows, k) for k in INDEXES}
    winner_scores = sorted((float(row["canonical_components"]["ZAI-WIN"]["value"])
                            for row in rows), reverse=True)
    spread = round(winner_scores[0] - winner_scores[1], 5)
    # Explicit UNVALIDATED SHADOW bands. Never infer a calibrated probability.
    # Widths are only a provisional paper baseline for unknown-future OOS.
    if spread >= 15:
        widths = (1, 2, 5)
        band = "SHADOW_NARROW"
    elif spread >= 7:
        widths = (2, 3, 6)
        band = "SHADOW_MEDIUM"
    else:
        widths = (3, 5, 8)
        band = "SHADOW_WIDE"
    heads = ranked["ZAI-WIN"][:min(widths[0], len(rows))]
    seconds = list(heads) if len(heads) > 1 else []
    for rid in ranked["ZAI-PLACE"]:
        if rid not in seconds and (len(heads) > 1 or rid not in heads):
            seconds.append(rid)
        if len(seconds) >= widths[1]:
            break
    thirds = []
    for rid in ranked["T3I-L"]:
        if rid not in thirds:
            thirds.append(rid)
        if len(thirds) >= widths[2]:
            break
    p3_unknown = [rid for rid in ids if "T3I-L" in neutrals[rid]]
    # One unknown third is protected in this paper baseline rather than being
    # silently equated to a low score. Never promote to Production.
    protected_unknown = None
    if p3_unknown and not any(rid in thirds for rid in p3_unknown) and thirds:
        protected_unknown = p3_unknown[0]
        thirds[-1] = protected_unknown
    roles = {rid: [col for col, pool in
                   (("W", heads), ("P2", seconds), ("P3", thirds))
                   if rid in pool] for rid in ids}
    pairs = [(h, p) for h in heads for p in seconds if h != p]
    # Order-exact paper candidates are not actual bets or Producer SIGNED FINAL.
    exacta = [{"bet_type": "EXACTA", "selection": [h, p], "stake": 100}
              for h, p in pairs]
    trifecta = [{"bet_type": "TRIFECTA", "selection": [h, p, t], "stake": 100}
                for h, p in pairs for t in thirds if t not in {h, p}]
    output = {
        "profile": PROFILE,
        "status": "STATIC_SHADOW_FROZEN / NON-PRODUCTION / UNCALIBRATED",
        "race_id": eid,
        "source_receipt_sha256": source_envelope["receipt_sha256"],
        "source_snapshot_sha256": source.get("source_snapshot_sha256"),
        "numeric_provenance_sha256": materialized.get("index_provenance_hash"),
        "frozen_at": now.isoformat(),
        "prediction_cutoff": request["prediction_cutoff"],
        "ranking": ranked["ZAI-WIN"],
        "rankings_by_column": ranked,
        "role_columns": roles,
        "winner_head_local_pairs": [{"head": h, "second": p} for h, p in pairs],
        "neutral_index_registry": neutrals,
        "p3_unknown_protection": protected_unknown,
        "paper_ticket_count": len(exacta) + len(trifecta),
        "paper_capital_yen": 100 * (len(exacta) + len(trifecta)),
        "paper_tickets": exacta + trifecta,
        "shadow_width": {"band": band, "winner_spread": spread,
                         "heads": len(heads), "seconds": len(seconds),
                         "thirds": len(thirds)},
        "evidence_statement": "29 Production-numerical fields are complete but uncalibrated; candidate ranking uses three ordinal values only, not an authorized predictive probability.",
        "pair_conditioning_statement": "Provisional role-row combinations, not empirically proven pair-specific interactions.",
        "prediction_consumption_authorized": False,
        "production_authority": False,
        "signed_final_claim": False,
        "actual_purchase": False,
        "promotable_without_forward_oos": False,
    }
    output["sha256"] = _sha(output)
    return output

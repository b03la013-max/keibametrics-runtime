from __future__ import annotations

"""LOCAL Required-Evidence round-trip validator.

This module does not score horses and does not invent missing evidence.
It proves that every declared required evidence cell has a terminal acquisition
state before Production numerical materialization.

Allowed terminal states:
FOUND, MISSING, CONFLICT, STALE, NOT-AVAILABLE.

FOUND requires an actual source-backed evidence value. Other terminal states
carry no synthetic value and are left for the Production materializer to
resolve as RULED-HOLD / RULED-NEUTRAL / NOT-APPLICABLE under its own authority.
"""

from typing import Any, Dict, Iterable, List, Tuple\nimport json\nfrom pathlib import Path

PROFILE_ID = "KM-LOCAL-EVIDENCE-ACQUISITION-ROUNDTRIP-v1.0-20260928-R1"
TERMINAL = {"FOUND", "MISSING", "CONFLICT", "STALE", "NOT-AVAILABLE"}


class EvidenceRoundTripError(ValueError):
    pass


def _runner_id(row: Dict[str, Any]) -> str:
    return str(row.get("runner_id") or row.get("horse_no") or row.get("number") or "").strip()


def _flatten_evidence(obj: Any, prefix: str = "") -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    if isinstance(obj, dict):
        # Source acquisition normalized fields often wrap the value.
        if "value" in obj and any(k in obj for k in ("source_id", "authority", "snapshot_sha256", "fetched_at")):
            if prefix:
                out[prefix] = obj
            return out
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            out.update(_flatten_evidence(v, key))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            key = f"{prefix}.{i}" if prefix else str(i)
            out.update(_flatten_evidence(v, key))
    elif prefix:
        out[prefix] = obj
    return out


def _source_fields(source_artifact: Dict[str, Any]) -> Dict[str, Any]:
    candidates = [
        source_artifact.get("normalized_evidence"),
        source_artifact.get("evidence"),
        source_artifact.get("merged_evidence"),
        source_artifact.get("structured_evidence"),
    ]
    merged: Dict[str, Any] = {}
    for c in candidates:
        if isinstance(c, (dict, list)):
            merged.update(_flatten_evidence(c))
    return merged


def _lookup(fields: Dict[str, Any], key: str, aliases: Iterable[str]) -> Tuple[bool, Any, str | None]:
    names = [str(key)] + [str(x) for x in aliases or []]
    for name in names:
        if name in fields:
            return True, fields[name], name
        # Permit an unambiguous suffix match so runner-scoped normalized
        # evidence can be declared without coupling to parser nesting.
        matches = [(k, v) for k, v in fields.items() if k.endswith("." + name)]
        if len(matches) == 1:
            return True, matches[0][1], matches[0][0]
    return False, None, None


def _status_from_source(source_artifact: Dict[str, Any], source_id: str | None) -> str | None:
    if not source_id:
        return None
    for snap in source_artifact.get("snapshots") or []:
        if str(snap.get("source_id") or "") != str(source_id):
            continue
        code = int(snap.get("http_status") or 0)
        if snap.get("stale") is True:
            return "STALE"
        if code < 200 or code >= 300:
            return "NOT-AVAILABLE"
        return None
    return None


def build_evidence_acquisition_ledger(
    request: Dict[str, Any],
    source_artifact: Dict[str, Any],
) -> Dict[str, Any]:
    manifest = request.get("required_evidence_manifest")
    if manifest is None:
        # Backward compatible derivation from per-runner declarations.
        manifest = []
        for r in request.get("runners") or []:
            rid = _runner_id(r)
            for item in r.get("required_evidence") or []:
                row = dict(item) if isinstance(item, dict) else {"evidence_key": str(item)}
                row.setdefault("runner_id", rid)
                manifest.append(row)
    if not isinstance(manifest, list) or not manifest:
        raise EvidenceRoundTripError("REQUIRED_EVIDENCE_MANIFEST_MISSING")

    runner_ids = {_runner_id(r) for r in request.get("runners") or []}
    runner_ids.discard("")
    fields = _source_fields(source_artifact)
    declared_terminal = request.get("evidence_acquisition_dispositions") or []
    disp: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for row in declared_terminal:
        if not isinstance(row, dict):
            continue
        k = (str(row.get("runner_id") or "*"), str(row.get("evidence_key") or ""))
        if k[1]:
            disp[k] = row

    rows: List[Dict[str, Any]] = []
    seen = set()
    counts = {s: 0 for s in sorted(TERMINAL)}
    for item in manifest:
        if not isinstance(item, dict):
            raise EvidenceRoundTripError("REQUIRED_EVIDENCE_ROW_INVALID")
        rid = str(item.get("runner_id") or "*")
        key = str(item.get("evidence_key") or item.get("field") or "").strip()
        if not key:
            raise EvidenceRoundTripError("REQUIRED_EVIDENCE_KEY_MISSING")
        if rid != "*" and rid not in runner_ids:
            raise EvidenceRoundTripError(f"REQUIRED_EVIDENCE_RUNNER_UNKNOWN:{rid}:{key}")
        cell = (rid, key)
        if cell in seen:
            raise EvidenceRoundTripError(f"REQUIRED_EVIDENCE_DUPLICATE:{rid}:{key}")
        seen.add(cell)

        aliases = item.get("aliases") or []
        found, value, matched = _lookup(fields, key, aliases)
        explicit = disp.get(cell) or disp.get(("*", key))
        source_id = str(item.get("source_id") or "") or None

        if found:
            status = "FOUND"
            reason = "SOURCE_BACKED_VALUE"
        elif explicit:
            status = str(explicit.get("status") or "").upper()
            reason = str(explicit.get("reason") or "")
            if status not in TERMINAL - {"FOUND"}:
                raise EvidenceRoundTripError(f"EVIDENCE_DISPOSITION_INVALID:{rid}:{key}:{status}")
            if not reason:
                raise EvidenceRoundTripError(f"EVIDENCE_DISPOSITION_REASON_MISSING:{rid}:{key}")
        else:
            source_status = _status_from_source(source_artifact, source_id)
            status = source_status or "MISSING"
            reason = "SOURCE_UNAVAILABLE" if source_status else "NOT_PRESENT_IN_SIGNED_SOURCE"

        counts[status] += 1
        rows.append({
            "runner_id": rid,
            "evidence_key": key,
            "status": status,
            "required": bool(item.get("required", True)),
            "source_id": source_id,
            "matched_field": matched,
            "reason": reason,
            "value_present": found,
        })

    unresolved = [r for r in rows if r["status"] not in TERMINAL]
    if unresolved:
        raise EvidenceRoundTripError("EVIDENCE_ACQUISITION_UNRESOLVED")

    required_rows = [r for r in rows if r["required"]]
    return {
        "profile": PROFILE_ID,
        "race_id": request.get("race_id"),
        "runner_count": len(runner_ids),
        "required_evidence_count": len(required_rows),
        "terminalized_count": len(required_rows),
        "found_count": sum(1 for r in required_rows if r["status"] == "FOUND"),
        "missing_count": sum(1 for r in required_rows if r["status"] == "MISSING"),
        "conflict_count": sum(1 for r in required_rows if r["status"] == "CONFLICT"),
        "stale_count": sum(1 for r in required_rows if r["status"] == "STALE"),
        "not_available_count": sum(1 for r in required_rows if r["status"] == "NOT-AVAILABLE"),
        "unresolved_count": 0,
        "full_terminalization": True,
        "all_found": all(r["status"] == "FOUND" for r in required_rows),
        "rows": rows,
    }


def enforce_before_numerical(request: Dict[str, Any], source_artifact: Dict[str, Any]) -> Dict[str, Any]:
    ledger = build_evidence_acquisition_ledger(request, source_artifact)
    if ledger["full_terminalization"] is not True or ledger["unresolved_count"] != 0:
        raise EvidenceRoundTripError("EVIDENCE_ACQUISITION_TERMINALIZATION_INCOMPLETE")
    return ledger

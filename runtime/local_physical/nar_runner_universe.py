from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from typing import Any, Dict, List, Tuple


PROFILE = "KM-LOCAL-NAR-RUNNER-UNIVERSE-v1.0-20260923"


def _sha(x: Any) -> str:
    return hashlib.sha256(
        json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def canonical_name(value: Any) -> str:
    s = unicodedata.normalize("NFKC", str(value or ""))
    return re.sub(r"\s+", "", s).strip()


def _bodyweight_from_following_rows(rows: List[List[str]], row_index: int) -> Tuple[int | None, int | None]:
    # NAR DebaTable normally puts current body weight in the sire/trainer row
    # two rows below the primary horse row. Search a short bounded window so
    # rowspan presentation differences do not break extraction.
    for j in range(row_index + 1, min(len(rows), row_index + 4)):
        for cell in rows[j]:
            s = unicodedata.normalize("NFKC", str(cell or "")).strip()
            m = re.fullmatch(r"(\d{3,4})\s*\(([+-]?\d+)\)", s)
            if m:
                return int(m.group(1)), int(m.group(2))
    return None, None


def extract_runner_universe_from_tables(tables: Any) -> List[Dict[str, Any]]:
    if not isinstance(tables, list):
        raise ValueError("NAR_RACE_CARD_TABLES_REQUIRED")

    found: Dict[int, Dict[str, Any]] = {}
    for table in tables:
        if not isinstance(table, list):
            continue
        rows = [
            [str(x or "").strip() for x in row]
            for row in table
            if isinstance(row, list)
        ]
        for i, row in enumerate(rows):
            if len(row) < 2:
                continue
            c0 = row[0].strip()
            if not re.fullmatch(r"\d{1,2}", c0):
                continue

            runner_id: int | None = None
            name: str | None = None
            frame: int | None = None

            # Standard row: [枠番, 馬番, 馬名, ...]
            if (
                len(row) >= 3
                and re.fullmatch(r"\d{1,2}", row[1].strip())
                and canonical_name(row[2])
                and canonical_name(row[2]) not in {"競走馬", "馬名"}
            ):
                frame = int(c0)
                runner_id = int(row[1].strip())
                name = row[2].strip()
            # Rowspan row: the frame column is omitted in flattened HTML, so
            # row begins [馬番, 馬名, ...].
            elif (
                canonical_name(row[1])
                and not re.fullmatch(r"\d{1,2}", row[1].strip())
                and canonical_name(row[1]) not in {"競走馬", "馬名", "前走回"}
            ):
                runner_id = int(c0)
                name = row[1].strip()

            if runner_id is None or not (1 <= runner_id <= 18) or not name:
                continue

            cname = canonical_name(name)
            if not cname or cname in {"枠番", "馬番", "競走馬", "馬名"}:
                continue

            # Declared universe preserves every officially listed horse, including later scratches.
            bw, bw_change = _bodyweight_from_following_rows(rows, i)
            rec = {
                "runner_id": str(runner_id),
                "horse_no": runner_id,
                "name": name,
                "canonical_name": cname,
                "frame_no": frame,
                "body_weight": bw,
                "body_weight_change": bw_change,
            }
            prior = found.get(runner_id)
            if prior:
                if prior["canonical_name"] != cname:
                    raise ValueError(
                        f"NAR_RUNNER_IDENTITY_CONFLICT:{runner_id}:{prior['name']}:{name}"
                    )
                # Prefer record carrying more physical state information.
                if prior.get("body_weight") is None and bw is not None:
                    found[runner_id] = rec
            else:
                found[runner_id] = rec

    if not found:
        raise ValueError("NAR_RUNNER_UNIVERSE_EMPTY")

    ids = sorted(found)
    # Horse numbers in a race need not be perfectly contiguous after scratches,
    # so do not synthesize missing numbers. Preserve the exact official set.
    return [found[i] for i in ids]


def _explicit_excluded_ids_from_tables(tables: Any) -> set[int]:
    excluded: set[int] = set()
    if not isinstance(tables, list):
        return excluded
    for table in tables:
        if not isinstance(table, list):
            continue
        for row in table:
            if not isinstance(row, list):
                continue
            cells=[unicodedata.normalize("NFKC", str(x or "")).strip() for x in row]
            joined=" ".join(cells)
            if not any(m in joined for m in ("出走取消","競走除外","取消馬","除外馬")):
                continue
            nums=[]
            for cell in cells[:4]:
                if re.fullmatch(r"\d{1,2}", cell):
                    nums.append(int(cell))
            if len(nums)>=2:
                excluded.add(nums[1])
            elif len(nums)==1:
                excluded.add(nums[0])
    return excluded


def _official_odds_active_ids(tables: Any, declared: List[Dict[str, Any]]) -> set[int]:
    if not isinstance(tables, list) or not declared:
        return set()
    text = canonical_name(" ".join(
        str(cell or "")
        for table in tables if isinstance(table, list)
        for row in table if isinstance(row, list)
        for cell in row
    ))
    active=set()
    for r in declared:
        name=canonical_name(r.get("name"))
        if name and name in text:
            active.add(int(r.get("horse_no") or r.get("runner_id")))
    # Fail-safe: only trust odds-as-active-set when it looks like the same race,
    # allowing at most two inactive/scratched declarations.
    if len(active) >= max(2, len(declared)-2):
        return active
    return set()


def enrich_source_artifact(artifact: Dict[str, Any]) -> Dict[str, Any]:
    ev = artifact.get("normalized_evidence") or {}
    rc = ev.get("race_card_tables")
    if not isinstance(rc, dict) or "value" not in rc:
        raise ValueError("NAR_RACE_CARD_EVIDENCE_MISSING")

    declared = extract_runner_universe_from_tables(rc["value"])
    race_card_excluded = _explicit_excluded_ids_from_tables(rc["value"])

    odds = ev.get("odds_tables")
    odds_value=(odds or {}).get("value") if isinstance(odds, dict) else None
    odds_excluded = _explicit_excluded_ids_from_tables(odds_value)
    odds_active = _official_odds_active_ids(odds_value, declared)

    statuses=[]
    active=[]
    for r in declared:
        rid=int(r.get("horse_no") or r.get("runner_id"))
        evidence=[str(rc.get("source_id") or "NAR_RACE_CARD")]
        if rid in race_card_excluded:
            status="CANCELLED"
            reason="EXPLICIT_RACE_CARD_CANCELLATION"
        elif rid in odds_excluded:
            status="CANCELLED"
            reason="EXPLICIT_OFFICIAL_ODDS_CANCELLATION"
            evidence.append(str((odds or {}).get("source_id") or "NAR_ODDS"))
        elif odds_active:
            evidence.append(str((odds or {}).get("source_id") or "NAR_ODDS"))
            if rid in odds_active:
                status="ACTIVE"
                reason="PRESENT_IN_OFFICIAL_ACTIVE_BETTING_UNIVERSE"
            else:
                status="INACTIVE"
                reason="ABSENT_FROM_OFFICIAL_ACTIVE_BETTING_UNIVERSE"
        else:
            status="ACTIVE_DECLARED"
            reason="NO_RELIABLE_OFFICIAL_ODDS_ACTIVE_SET"
        statuses.append({
            "runner_id":str(rid),
            "name":r.get("name"),
            "status":status,
            "reason":reason,
            "evidence_sources":evidence,
        })
        if status in {"ACTIVE","ACTIVE_DECLARED"}:
            active.append(r)

    declared_universe={
        "profile":PROFILE,
        "universe_type":"DECLARED",
        "source_id":rc.get("source_id"),
        "source_snapshot_sha256":rc.get("snapshot_sha256"),
        "runner_count":len(declared),
        "runners":declared,
    }
    declared_universe["runner_universe_sha256"]=_sha(declared_universe)

    active_universe={
        "profile":PROFILE,
        "universe_type":"ACTIVE",
        "source_id":rc.get("source_id"),
        "source_snapshot_sha256":rc.get("snapshot_sha256"),
        "runner_count":len(active),
        "runners":active,
        "status_registry_sha256":_sha(statuses),
    }
    active_universe["runner_universe_sha256"]=_sha(active_universe)

    artifact["declared_runner_universe"]=declared_universe
    artifact["active_runner_universe"]=active_universe
    artifact["runner_status_registry"]=statuses
    artifact["runner_status_registry_sha256"]=_sha(statuses)

    # Backward-compatible formal authority: official_runner_universe means ACTIVE.
    artifact["official_runner_universe"]=active_universe
    artifact["official_runner_universe_sha256"]=active_universe["runner_universe_sha256"]
    artifact["official_declared_runner_universe_sha256"]=declared_universe["runner_universe_sha256"]
    return artifact


def validate_request_runners(
    artifact: Dict[str, Any],
    runners: Any,
) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    official = artifact.get("official_runner_universe") or {}
    off_rows = official.get("runners")
    if not isinstance(off_rows, list) or not off_rows:
        return False, ["OFFICIAL_RUNNER_UNIVERSE_MISSING"]
    if not isinstance(runners, list) or not runners:
        return False, ["REQUEST_RUNNER_UNIVERSE_MISSING"]

    off = {
        str(x.get("runner_id") or x.get("horse_no")): canonical_name(x.get("name"))
        for x in off_rows
        if str(x.get("runner_id") or x.get("horse_no") or "")
    }
    req: Dict[str, str] = {}
    for x in runners:
        if not isinstance(x, dict):
            errors.append("REQUEST_RUNNER_INVALID")
            continue
        rid = str(x.get("runner_id") or x.get("horse_no") or "")
        if not rid:
            errors.append("REQUEST_RUNNER_ID_MISSING")
            continue
        if rid in req:
            errors.append("REQUEST_RUNNER_DUPLICATE:" + rid)
        req[rid] = canonical_name(x.get("name"))

    missing = sorted(set(off) - set(req), key=lambda z: int(z) if z.isdigit() else z)
    extra = sorted(set(req) - set(off), key=lambda z: int(z) if z.isdigit() else z)
    if missing:
        errors.append("REQUEST_RUNNERS_MISSING_OFFICIAL:" + ",".join(missing))
    if extra:
        errors.append("REQUEST_RUNNERS_NOT_OFFICIAL:" + ",".join(extra))
    for rid in sorted(set(off) & set(req), key=lambda z: int(z) if z.isdigit() else z):
        if not req[rid]:
            errors.append("REQUEST_RUNNER_NAME_MISSING:" + rid)
        elif off[rid] != req[rid]:
            errors.append(f"REQUEST_RUNNER_NAME_MISMATCH:{rid}:{req[rid]}!={off[rid]}")
    return not errors, errors


def validate_krs_horses(
    artifact: Dict[str, Any],
    krs_input_data: Any,
) -> Tuple[bool, List[str]]:
    if not isinstance(krs_input_data, dict):
        return False, ["KRS_INPUT_DATA_MISSING_FOR_RUNNER_UNIVERSE"]
    horses = krs_input_data.get("horses")
    return validate_request_runners(artifact, horses)

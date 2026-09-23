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

            # NAR race cards keep cancelled/excluded horses visible in the card.
            # Build the local presentation block for this horse and remove a
            # runner only when an explicit official cancellation/exclusion marker
            # exists in that block. This is Runner-Universe correctness, not a
            # prediction-policy change.
            block_rows=[row]
            for j in range(i + 1, len(rows)):
                nxt=rows[j]
                if nxt and re.fullmatch(r"\d{1,2}", (nxt[0] or "").strip()):
                    # Stop at the next apparent primary runner row.
                    if (
                        (len(nxt)>=3 and re.fullmatch(r"\d{1,2}", (nxt[1] or "").strip()) and canonical_name(nxt[2]))
                        or (len(nxt)>=2 and canonical_name(nxt[1]) and not re.fullmatch(r"\d{1,2}", (nxt[1] or "").strip()))
                    ):
                        break
                block_rows.append(nxt)
                if len(block_rows)>=5:
                    break
            block_text=canonical_name(" ".join(cell for rr in block_rows for cell in rr))
            if any(marker in block_text for marker in ("出走取消","競走除外","取消馬","除外馬")):
                continue

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


def enrich_source_artifact(artifact: Dict[str, Any]) -> Dict[str, Any]:
    ev = artifact.get("normalized_evidence") or {}
    rc = ev.get("race_card_tables")
    if not isinstance(rc, dict) or "value" not in rc:
        raise ValueError("NAR_RACE_CARD_EVIDENCE_MISSING")
    runners = extract_runner_universe_from_tables(rc["value"])
    # Current NAR odds table carries the explicit change-information column.
    # Use it to remove officially cancelled/excluded horses from the active
    # runner universe while preserving their presence in the raw race card.
    odds = ev.get("odds_tables")
    excluded_ids = _explicit_excluded_ids_from_tables((odds or {}).get("value") if isinstance(odds, dict) else None)
    if excluded_ids:
        runners = [r for r in runners if int(r.get("horse_no") or r.get("runner_id")) not in excluded_ids]
    universe = {
        "profile": PROFILE,
        "source_id": rc.get("source_id"),
        "source_snapshot_sha256": rc.get("snapshot_sha256"),
        "runner_count": len(runners),
        "runners": runners,
    }
    universe["runner_universe_sha256"] = _sha(universe)
    artifact["official_runner_universe"] = universe
    artifact["official_runner_universe_sha256"] = universe["runner_universe_sha256"]
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

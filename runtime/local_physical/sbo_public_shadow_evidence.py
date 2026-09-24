from __future__ import annotations

import datetime
import hashlib
import html
import re
import unicodedata
import urllib.error
import urllib.request
import urllib.robotparser
from typing import Any, Dict, List, Tuple
from zoneinfo import ZoneInfo

from nar_source_manifest import LOCAL_BABA_CODES
from source_acquisition import _decode, _html_tables, _html_text, _parse_dt, sha_obj, utcnow, validate_public_url

PROFILE = "KM-LOCAL-SBO-PUBLIC-SHADOW-EVIDENCE-v1.0-20260924"
SOURCE_CLASS = "THIRD_PARTY_PUBLIC_SHADOW"
SOURCE_AUTHORITY = "SBO_PUBLIC_NON_OFFICIAL"
PRODUCTION_AUTHORITY = False
PREDICTION_AUTHORITY = False
BASE = "https://nar.k-ba.net"
USER_AGENT = "KeibaMetrics-SBO-Shadow/1.0 (+public pre-race evidence; one request per race; contact via repository)"
DEFAULT_TIMEOUT = 20
DEFAULT_MAX_BYTES = 900000

_INDEX_HEADERS = {
    "近走指数": "recent_index",
    "距離指数": "distance_index",
    "馬場指数": "going_index",
    "平均指数": "average_index",
}
_EXPECTED_HEADERS = {"馬番", "馬名", "平均指数"}


def _norm_text(v: Any) -> str:
    s = unicodedata.normalize("NFKC", str(v or ""))
    return re.sub(r"\s+", "", s).strip()


def _clean_name(v: Any) -> str:
    s = unicodedata.normalize("NFKC", html.unescape(str(v or "")))
    s = re.sub(r"\s+", " ", s).strip()
    # SBO sometimes appends recency notes such as "3ヶ月前" to a horse name.
    s = re.sub(r"\s*\d+\s*ヶ?月前\s*$", "", s).strip()
    return s


def _date_compact(v: Any) -> str:
    s = str(v or "").strip().replace("/", "-")
    d = datetime.date.fromisoformat(s)
    return d.strftime("%Y%m%d")


def build_sbo_url(venue_id: str, race_date: str, race_no: int) -> str:
    venue = str(venue_id or "").upper().strip()
    if venue not in LOCAL_BABA_CODES:
        raise ValueError("SBO_VENUE_ID_UNSUPPORTED:" + venue)
    n = int(race_no)
    if n < 1 or n > 12:
        raise ValueError("SBO_RACE_NO_OUT_OF_RANGE")
    return f"{BASE}/{_date_compact(race_date)}/{int(LOCAL_BABA_CODES[venue])}/{n}/table.html"


def _robots_allowed(url: str, timeout: int = 10) -> Tuple[bool, str]:
    robots_url = BASE + "/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        req = urllib.request.Request(robots_url, headers={"User-Agent": USER_AGENT}, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(200000)
            text = _decode(raw, str(resp.headers.get("content-type") or ""))
            rp.parse(text.splitlines())
        return bool(rp.can_fetch(USER_AGENT, url)), "ROBOTS_LOADED"
    except urllib.error.HTTPError as e:
        if int(e.code) in (404, 410):
            return True, f"ROBOTS_ABSENT_HTTP_{int(e.code)}"
        if int(e.code) in (401, 403):
            return False, f"ROBOTS_DENIED_HTTP_{int(e.code)}"
        return False, f"ROBOTS_HTTP_{int(e.code)}"
    except Exception as e:
        # Fail closed for a third-party source when robots policy cannot be established.
        return False, "ROBOTS_CHECK_FAILED:" + str(e)


def _fetch(url: str, timeout: int = DEFAULT_TIMEOUT, max_bytes: int = DEFAULT_MAX_BYTES) -> Tuple[bytes, Dict[str, str], str]:
    validate_public_url(url)
    allowed, robots_status = _robots_allowed(url)
    if not allowed:
        raise ValueError("SBO_ROBOTS_DISALLOWED:" + robots_status)
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.1",
            "Accept-Language": "ja,en;q=0.4",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=min(int(timeout), 60)) as resp:
        final_url = str(resp.geturl())
        validate_public_url(final_url)
        raw = resp.read(int(max_bytes) + 1)
        if len(raw) > int(max_bytes):
            raise ValueError("SBO_MAX_BYTES_EXCEEDED")
        headers = {str(k).lower(): str(v) for k, v in resp.headers.items()}
        return raw, headers, robots_status


def _parse_index_cell(v: Any) -> Dict[str, Any]:
    s = unicodedata.normalize("NFKC", str(v or "")).strip()
    m = re.search(r"(\*|-?\d+(?:\.\d+)?)\s*\(\s*(\d+)\s*\)", s)
    if m:
        raw_value = m.group(1)
        count = int(m.group(2))
        value = None if raw_value == "*" else float(raw_value)
        if value is not None and value.is_integer():
            value = int(value)
        return {"value": value, "sample_count": count, "raw": s}
    m2 = re.search(r"(?<!\d)(-?\d+(?:\.\d+)?)(?!\d)", s)
    if m2:
        value = float(m2.group(1))
        if value.is_integer():
            value = int(value)
        return {"value": value, "sample_count": None, "raw": s}
    return {"value": None, "sample_count": None, "raw": s}


def _parse_weight(v: Any) -> Dict[str, Any]:
    s = unicodedata.normalize("NFKC", str(v or "")).strip()
    m = re.search(r"(\d{2,4})\s*\(?\s*([+-]?\d+)?\s*\)?", s)
    if not m:
        return {"body_weight": None, "body_weight_change": None, "raw": s}
    return {
        "body_weight": int(m.group(1)),
        "body_weight_change": int(m.group(2)) if m.group(2) else None,
        "raw": s,
    }


def _find_runner_table(decoded: str) -> Tuple[List[str], List[List[str]]]:
    for table in _html_tables(decoded):
        if not table:
            continue
        header_idx = None
        for i, row in enumerate(table[:5]):
            hs = [_norm_text(x) for x in row]
            if _EXPECTED_HEADERS.issubset(set(hs)):
                header_idx = i
                break
        if header_idx is None:
            continue
        headers = [_norm_text(x) for x in table[header_idx]]
        rows = table[header_idx + 1 :]
        return headers, rows
    raise ValueError("SBO_INDEX_TABLE_NOT_FOUND")


def parse_sbo_html(raw: bytes, content_type: str = "text/html; charset=utf-8") -> Dict[str, Any]:
    decoded = _decode(raw, content_type)
    text = _html_text(decoded)
    headers, rows = _find_runner_table(decoded)
    col = {h: i for i, h in enumerate(headers)}
    runners: List[Dict[str, Any]] = []
    for row in rows:
        if not row:
            continue
        horse_no_raw = str(row[col.get("馬番", 0)] if col.get("馬番", 0) < len(row) else "").strip()
        if not re.fullmatch(r"\d{1,2}", horse_no_raw):
            continue
        horse_no = int(horse_no_raw)
        name_idx = col.get("馬名")
        if name_idx is None or name_idx >= len(row):
            continue
        rec: Dict[str, Any] = {
            "horse_no": horse_no,
            "horse_name": _clean_name(row[name_idx]),
        }
        for source_header, key in _INDEX_HEADERS.items():
            idx = col.get(source_header)
            if idx is not None and idx < len(row):
                rec[key] = _parse_index_cell(row[idx])
            else:
                rec[key] = {"value": None, "sample_count": None, "raw": ""}
        trainer_idx = col.get("調教師")
        rider_idx = col.get("騎手")
        burden_idx = col.get("負担重量")
        body_idx = col.get("馬体重")
        if trainer_idx is not None and trainer_idx < len(row):
            rec["trainer"] = str(row[trainer_idx]).strip()
        if rider_idx is not None and rider_idx < len(row):
            rec["rider"] = str(row[rider_idx]).strip()
        if burden_idx is not None and burden_idx < len(row):
            try:
                rec["assigned_weight"] = float(str(row[burden_idx]).strip())
            except Exception:
                rec["assigned_weight"] = None
        if body_idx is not None and body_idx < len(row):
            rec.update(_parse_weight(row[body_idx]))
        runners.append(rec)

    if not runners:
        raise ValueError("SBO_RUNNER_ROWS_NOT_FOUND")

    avg_sorted = sorted(
        [x for x in runners if (x.get("average_index") or {}).get("value") is not None],
        key=lambda x: (-(x["average_index"]["value"]), x["horse_no"]),
    )
    rank = {}
    last_value = None
    last_rank = 0
    for pos, x in enumerate(avg_sorted, 1):
        v = x["average_index"]["value"]
        if v != last_value:
            last_rank = pos
            last_value = v
        rank[x["horse_no"]] = last_rank
    for x in runners:
        x["average_index_rank"] = rank.get(x["horse_no"])

    def _group(label: str, next_labels: List[str]) -> List[Dict[str, Any]]:
        stop = "|".join(re.escape(z) for z in next_labels)
        pat = rf"{re.escape(label)}\s*[:：]\s*(.*?)(?=(?:{stop})\s*[:：]|基本\s*[:：]|\[単\]|\[縦\]|\[箱\]|$)"
        m = re.search(pat, text, re.S)
        if not m:
            return []
        out = []
        for no, score in re.findall(r"(\d{1,2})\s*\(\s*(\*|-?\d+(?:\.\d+)?)\s*\)", m.group(1)):
            out.append({
                "horse_no": int(no),
                "score": None if score == "*" else float(score),
            })
        for x in out:
            if isinstance(x["score"], float) and x["score"].is_integer():
                x["score"] = int(x["score"])
        return out

    recommendation = {
        "axis": _group("軸", ["本線", "おさえ"]),
        "main": _group("本線", ["おさえ"]),
        "cover": _group("おさえ", []),
    }

    race_meta = {}
    m = re.search(r"第\s*(\d+)\s*競走\s+(\d+)m\s+(\d{1,2}:\d{2})発走\s+馬場\s*[:：]\s*([^\s]+)", text)
    if m:
        race_meta = {
            "race_no": int(m.group(1)),
            "distance_m": int(m.group(2)),
            "start_time": m.group(3),
            "going": m.group(4),
        }

    return {
        "runners": sorted(runners, key=lambda x: x["horse_no"]),
        "average_index_ranking": [
            {"horse_no": x["horse_no"], "horse_name": x["horse_name"], "rank": x["average_index_rank"], "average_index": x["average_index"]["value"]}
            for x in sorted(runners, key=lambda z: (z["average_index_rank"] or 999, z["horse_no"]))
        ],
        "recommendation_groups": recommendation,
        "race_meta": race_meta,
    }


def _scheduled_post_utc(artifact: Dict[str, Any]) -> datetime.datetime | None:
    ctx = artifact.get("source_race_context") or {}
    race_date = str(ctx.get("race_date") or "").replace("/", "-")
    start = None
    try:
        start = (((artifact.get("normalized_evidence") or {}).get("start_time") or {}).get("value"))
    except Exception:
        start = None
    if not start:
        return None
    try:
        local = datetime.datetime.fromisoformat(f"{race_date}T{str(start).strip()}:00").replace(tzinfo=ZoneInfo("Asia/Tokyo"))
        return local.astimezone(datetime.timezone.utc)
    except Exception:
        return None


def _official_runner_map(artifact: Dict[str, Any]) -> Dict[int, str]:
    uni = artifact.get("official_runner_universe") or {}
    out = {}
    for r in uni.get("runners") or []:
        try:
            if str(r.get("status") or "ACTIVE").upper() not in {"ACTIVE", ""}:
                continue
            out[int(r.get("runner_id") or r.get("horse_no"))] = str(r.get("name") or r.get("horse_name") or "")
        except Exception:
            continue
    return out


def _runner_match(parsed: Dict[str, Any], artifact: Dict[str, Any]) -> Dict[str, Any]:
    official = _official_runner_map(artifact)
    if not official:
        return {"status": "NOT_AVAILABLE", "matched": 0, "official_count": 0, "sbo_count": len(parsed.get("runners") or []), "errors": []}
    sbo = {int(x["horse_no"]): x["horse_name"] for x in parsed.get("runners") or []}
    errors = []
    for no, name in official.items():
        if no not in sbo:
            errors.append(f"SBO_MISSING_OFFICIAL_RUNNER:{no}")
            continue
        if _norm_text(name) != _norm_text(sbo[no]):
            errors.append(f"SBO_RUNNER_NAME_MISMATCH:{no}:{name}:{sbo[no]}")
    for no in sorted(set(sbo) - set(official)):
        errors.append(f"SBO_EXTRA_RUNNER:{no}")
    return {
        "status": "MATCHED" if not errors else "MISMATCH",
        "matched": len(set(official) & set(sbo)),
        "official_count": len(official),
        "sbo_count": len(sbo),
        "errors": errors,
    }


def build_sbo_shadow_evidence(
    artifact: Dict[str, Any],
    prediction_cutoff: str,
    *,
    require_sbo: bool = False,
) -> Tuple[Dict[str, Any], List[str]]:
    ctx = artifact.get("source_race_context") or {}
    venue_id = str(ctx.get("venue_id") or "").upper().strip()
    race_date = str(ctx.get("race_date") or "").strip()
    race_no = int(ctx.get("race_no") or 0)
    errors: List[str] = []
    warnings: List[str] = []

    base = {
        "profile": PROFILE,
        "source_class": SOURCE_CLASS,
        "authority": SOURCE_AUTHORITY,
        "official": False,
        "production_authority": PRODUCTION_AUTHORITY,
        "prediction_authority": PREDICTION_AUTHORITY,
        "status": "UNAVAILABLE",
        "storage_policy": "NORMALIZED_EXTRACTED_DATA_PLUS_RAW_SHA_ONLY / NO_RAW_HTML_PERSISTENCE",
        "copyright_boundary": "THIRD_PARTY_PUBLIC_CONTENT / NO_REPUBLICATION_AUTHORITY / ALL_RIGHTS_RESERVED_NOTICE_OBSERVED",
        "robots_policy": "CHECK_BEFORE_FETCH / FAIL_CLOSED_IF_DISALLOWED_OR_UNKNOWN",
        "warnings": warnings,
    }

    try:
        url = build_sbo_url(venue_id, race_date, race_no)
        base["requested_url"] = url
        raw, headers, robots_status = _fetch(url)
        fetched_at = utcnow()
        base["robots_status"] = robots_status
        base["fetched_at"] = fetched_at
        base["http_content_type"] = str(headers.get("content-type") or "")
        base["raw_sha256"] = hashlib.sha256(raw).hexdigest()
        base["raw_byte_count"] = len(raw)
        parsed = parse_sbo_html(raw, base["http_content_type"])
        base.update(parsed)
        base["runner_universe_match"] = _runner_match(parsed, artifact)

        fetched_dt = _parse_dt(fetched_at)
        cutoff_dt = _parse_dt(prediction_cutoff)
        base["cutoff_relation"] = "PRE_CUTOFF" if fetched_dt and cutoff_dt and fetched_dt <= cutoff_dt else "POST_CUTOFF"
        post_dt = _scheduled_post_utc(artifact)
        if post_dt and fetched_dt:
            base["scheduled_post_at"] = post_dt.isoformat()
            base["start_relation"] = "PRE_START" if fetched_dt < post_dt else "POST_START"
        else:
            base["scheduled_post_at"] = None
            base["start_relation"] = "UNKNOWN"

        if base["cutoff_relation"] != "PRE_CUTOFF":
            warnings.append("SBO_POST_CUTOFF_NOT_ELIGIBLE")
        if base["start_relation"] == "POST_START":
            warnings.append("SBO_POST_START_NOT_ELIGIBLE")
        if base["runner_universe_match"]["status"] == "MISMATCH":
            warnings.extend(base["runner_universe_match"]["errors"])

        base["oos_eligible"] = bool(
            base["cutoff_relation"] == "PRE_CUTOFF"
            and base["start_relation"] == "PRE_START"
            and base["runner_universe_match"]["status"] in {"MATCHED", "NOT_AVAILABLE"}
        )
        base["status"] = "CAPTURED_PRE_RACE_SHADOW" if base["oos_eligible"] else "CAPTURED_NOT_OOS_ELIGIBLE"
    except Exception as e:
        base["status"] = "UNAVAILABLE"
        base["error"] = str(e)
        warnings.append("SBO_CAPTURE_FAILED:" + str(e))
        if require_sbo:
            errors.append("SBO_PUBLIC_SHADOW_REQUIRED_FAILED:" + str(e))

    base["warnings"] = list(dict.fromkeys(warnings))
    base["artifact_sha256"] = sha_obj({k: v for k, v in base.items() if k != "artifact_sha256"})
    artifact["sbo_public_shadow_evidence"] = base
    artifact["sbo_public_shadow_evidence_sha256"] = base["artifact_sha256"]
    return artifact, errors

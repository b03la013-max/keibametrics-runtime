from __future__ import annotations

import base64
import datetime
import email.utils
import gzip
import hashlib
import html
import ipaddress
import json
import os
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import Any, Dict, List, Tuple

SOURCE_PROFILE = "KM-JRA-EXTERNAL-SOURCE-ACQUISITION-v1.0-20260925"
SOURCE_SCHEMA = "KM-SOURCE-SNAPSHOT-v1"
DEFAULT_MAX_BYTES = int(os.environ.get("KM_SOURCE_MAX_BYTES", "2000000"))
DEFAULT_TIMEOUT_SECONDS = int(os.environ.get("KM_SOURCE_TIMEOUT_SECONDS", "20"))
DEFAULT_ALLOWED_HOSTS = [
    # JRA official sources (race calendar, JRADB auxiliary HTML, official race-card PDF).
    "jra.go.jp",
    "*.jra.go.jp",
    # JMA official weather context.
    "jma.go.jp",
    "*.jma.go.jp",
    # JRA-only third-party public shadow source: 統計ショッカーリミテッド (TSL).
    "jra.k-ba.net",
]


def utcnow() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _parse_dt(v: Any) -> datetime.datetime | None:
    if not v:
        return None
    if isinstance(v, datetime.datetime):
        dt = v
    else:
        s = str(v).strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            dt = datetime.datetime.fromisoformat(s)
        except Exception:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc)


def _jdump(x: Any) -> bytes:
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha_obj(x: Any) -> str:
    return hashlib.sha256(_jdump(x)).hexdigest()


def _allowed_hosts() -> List[str]:
    extra = [x.strip().lower() for x in os.environ.get("KM_SOURCE_ALLOWED_HOSTS", "").split(",") if x.strip()]
    return list(dict.fromkeys(DEFAULT_ALLOWED_HOSTS + extra))


def _host_allowed(host: str) -> bool:
    h = (host or "").lower().rstrip(".")
    for rule in _allowed_hosts():
        r = rule.lower().rstrip(".")
        if r.startswith("*."):
            suffix = r[1:]
            if h.endswith(suffix) and h != suffix[1:]:
                return True
        elif h == r:
            return True
    return False


def _ip_public(ip_text: str) -> bool:
    ip = ipaddress.ip_address(ip_text)
    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def validate_public_url(url: str) -> urllib.parse.SplitResult:
    p = urllib.parse.urlsplit(str(url or ""))
    if p.scheme.lower() != "https":
        raise ValueError("SOURCE_HTTPS_REQUIRED")
    if not p.hostname:
        raise ValueError("SOURCE_HOST_REQUIRED")
    if p.username or p.password:
        raise ValueError("SOURCE_USERINFO_FORBIDDEN")
    if not _host_allowed(p.hostname):
        raise ValueError("SOURCE_HOST_NOT_ALLOWED:" + p.hostname)
    try:
        infos = socket.getaddrinfo(p.hostname, p.port or 443, type=socket.SOCK_STREAM)
    except socket.gaierror as e:
        raise ValueError("SOURCE_DNS_RESOLUTION_FAILED:" + str(e))
    ips = {x[4][0] for x in infos}
    if not ips:
        raise ValueError("SOURCE_DNS_EMPTY")
    for ip in ips:
        if not _ip_public(ip):
            raise ValueError("SOURCE_PRIVATE_ADDRESS_FORBIDDEN:" + ip)
    return p


class _SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_public_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: List[str] = []

    def handle_data(self, data: str):
        if data and data.strip():
            self.parts.append(data.strip())

    def text(self) -> str:
        return " ".join(self.parts)


class _TableExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables: List[List[List[str]]] = []
        self._table: List[List[str]] | None = None
        self._row: List[str] | None = None
        self._cell: List[str] | None = None
        self._nested_table_depth = 0

    def handle_starttag(self, tag: str, attrs):
        t = tag.lower()
        if t == "table":
            if self._table is None:
                self._table = []
                self._nested_table_depth = 0
            else:
                self._nested_table_depth += 1
        elif self._table is not None and self._nested_table_depth == 0 and t == "tr":
            self._row = []
        elif self._row is not None and t in {"td", "th"}:
            self._cell = []
        elif self._cell is not None and t in {"br", "p", "div"}:
            self._cell.append(" ")

    def handle_data(self, data: str):
        if self._cell is not None and data:
            self._cell.append(data)

    def handle_endtag(self, tag: str):
        t = tag.lower()
        if t in {"td", "th"} and self._cell is not None:
            value = re.sub(r"\s+", " ", "".join(self._cell)).strip()
            if self._row is not None:
                self._row.append(value)
            self._cell = None
        elif t == "tr" and self._row is not None and self._nested_table_depth == 0:
            if any(x for x in self._row):
                self._table.append(self._row)
            self._row = None
        elif t == "table" and self._table is not None:
            if self._nested_table_depth > 0:
                self._nested_table_depth -= 1
            else:
                if self._table:
                    self.tables.append(self._table)
                self._table = None


def _html_tables(decoded: str) -> List[List[List[str]]]:
    parser = _TableExtractor()
    parser.feed(decoded)
    return parser.tables


def _decode(raw: bytes, content_type: str) -> str:
    charset = "utf-8"
    m = re.search(r"charset\s*=\s*['\"]?([^;\s'\"]+)", content_type or "", re.I)
    if m:
        charset = m.group(1)
    for enc in (charset, "utf-8", "cp932", "shift_jis", "euc_jp"):
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return raw.decode("utf-8", errors="replace")


def _html_text(decoded: str) -> str:
    parser = _TextExtractor()
    try:
        parser.feed(decoded)
        return html.unescape(parser.text())
    except Exception:
        return decoded


def _json_path(obj: Any, path: str) -> Any:
    cur = obj
    for token in [x for x in str(path).split(".") if x != ""]:
        if isinstance(cur, list):
            cur = cur[int(token)]
        elif isinstance(cur, dict):
            if token not in cur:
                raise KeyError(token)
            cur = cur[token]
        else:
            raise KeyError(token)
    return cur


def _cast(value: Any, cast: str | None) -> Any:
    if cast in (None, "", "raw"):
        return value
    c = str(cast).lower()
    if c == "str":
        return str(value).strip()
    if c == "int":
        return int(str(value).replace(",", "").strip())
    if c == "float":
        return float(str(value).replace(",", "").strip())
    if c == "bool":
        s = str(value).strip().lower()
        if s in {"1", "true", "yes", "y", "on"}:
            return True
        if s in {"0", "false", "no", "n", "off"}:
            return False
        raise ValueError("BOOL_CAST_FAILED")
    raise ValueError("UNKNOWN_CAST:" + c)


def _extract(raw: bytes, content_type: str, rules: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[str]]:
    evidence: Dict[str, Any] = {}
    errors: List[str] = []
    decoded: str | None = None
    html_text: str | None = None
    json_obj: Any = None
    for rule in rules or []:
        field = str(rule.get("field") or "").strip()
        typ = str(rule.get("type") or "").strip().lower()
        required = bool(rule.get("required", False))
        if not field:
            errors.append("EXTRACT_FIELD_REQUIRED")
            continue
        try:
            if typ == "regex":
                if decoded is None:
                    decoded = _decode(raw, content_type)
                scope = str(rule.get("scope") or "decoded").lower()
                if scope == "html_text":
                    if html_text is None:
                        html_text = _html_text(decoded)
                    src = html_text
                else:
                    src = decoded
                pat = str(rule.get("pattern") or "")
                if not pat:
                    raise ValueError("REGEX_PATTERN_REQUIRED")
                m = re.search(pat, src, re.I | re.S)
                if not m:
                    raise ValueError("REGEX_NO_MATCH")
                group = rule.get("group", 1)
                value = m.group(group)
            elif typ == "json_path":
                if json_obj is None:
                    json_obj = json.loads(_decode(raw, content_type))
                value = _json_path(json_obj, str(rule.get("path") or ""))
            elif typ == "html_text":
                if decoded is None:
                    decoded = _decode(raw, content_type)
                value = _html_text(decoded)
                if rule.get("required") and not value:
                    raise ValueError("HTML_TEXT_EMPTY")
            elif typ == "html_tables":
                if decoded is None:
                    decoded = _decode(raw, content_type)
                value = _html_tables(decoded)
                if rule.get("required") and not value:
                    raise ValueError("HTML_TABLES_EMPTY")
            elif typ == "meta":
                name = str(rule.get("name") or "")
                if name == "raw_sha256":
                    value = hashlib.sha256(raw).hexdigest()
                elif name == "byte_count":
                    value = len(raw)
                else:
                    raise ValueError("UNKNOWN_META_FIELD:" + name)
            else:
                raise ValueError("UNKNOWN_EXTRACT_TYPE:" + typ)
            evidence[field] = _cast(value, rule.get("cast"))
        except Exception as e:
            if required:
                errors.append("EXTRACT_REQUIRED_FAILED:" + field + ":" + str(e))
    return evidence, errors


def _last_modified_age_seconds(headers: Dict[str, str], now: datetime.datetime) -> float | None:
    v = headers.get("last-modified")
    if not v:
        return None
    try:
        dt = email.utils.parsedate_to_datetime(v)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return max(0.0, (now - dt.astimezone(datetime.timezone.utc)).total_seconds())
    except Exception:
        return None


def snapshot_from_bytes(
    spec: Dict[str, Any],
    raw: bytes,
    *,
    final_url: str,
    status_code: int,
    headers: Dict[str, str] | None = None,
    fetched_at: str | None = None,
    prediction_cutoff: str | None = None,
) -> Tuple[Dict[str, Any], List[str]]:
    headers = {str(k).lower(): str(v) for k, v in (headers or {}).items()}
    fetched_at = fetched_at or utcnow()
    content_type = headers.get("content-type", "")
    evidence, extraction_errors = _extract(raw, content_type, spec.get("extract") or [])
    raw_sha = hashlib.sha256(raw).hexdigest()
    packed = gzip.compress(raw, compresslevel=9)
    now_dt = _parse_dt(fetched_at) or datetime.datetime.now(datetime.timezone.utc)
    cutoff_dt = _parse_dt(prediction_cutoff)
    relation = "UNKNOWN"
    if cutoff_dt:
        relation = "PRE_CUTOFF" if now_dt <= cutoff_dt else "POST_CUTOFF"
    age = _last_modified_age_seconds(headers, now_dt)
    max_age = spec.get("max_age_seconds")
    stale = bool(max_age is not None and age is not None and age > float(max_age))
    snapshot = {
        "schema": SOURCE_SCHEMA,
        "source_id": str(spec.get("source_id") or ""),
        "source_class": str(spec.get("source_class") or "UNCLASSIFIED"),
        "authority": str(spec.get("authority") or "UNSPECIFIED"),
        "authority_priority": int(spec.get("priority") or (100 if spec.get("official") else 50)),
        "official": bool(spec.get("official", False)),
        "required": bool(spec.get("required", False)),
        "requested_url": str(spec.get("url") or final_url),
        "final_url": final_url,
        "http_status": int(status_code),
        "content_type": content_type,
        "etag": headers.get("etag"),
        "last_modified": headers.get("last-modified"),
        "last_modified_age_seconds": age,
        "fetched_at": fetched_at,
        "cutoff_relation": relation,
        "current": not stale,
        "stale": stale,
        "raw_sha256": raw_sha,
        "byte_count": len(raw),
        "raw_encoding": "gzip+base64",
        "raw_gzip_b64": base64.b64encode(packed).decode("ascii"),
        "extracted_evidence": evidence,
        "extraction_errors": extraction_errors,
    }
    snapshot["snapshot_sha256"] = sha_obj({k: v for k, v in snapshot.items() if k != "snapshot_sha256"})
    errors = list(extraction_errors)
    if (status_code < 200 or status_code >= 300) and spec.get("required"):
        errors.append("SOURCE_HTTP_STATUS:" + str(status_code))
    if stale and spec.get("required"):
        errors.append("SOURCE_STALE:" + snapshot["source_id"])
    if relation == "POST_CUTOFF" and spec.get("required"):
        errors.append("SOURCE_POST_CUTOFF:" + snapshot["source_id"])
    return snapshot, errors


def fetch_source(spec: Dict[str, Any], prediction_cutoff: str) -> Tuple[Dict[str, Any], List[str]]:
    url = str(spec.get("url") or "")
    validate_public_url(url)
    max_bytes = min(int(spec.get("max_bytes") or DEFAULT_MAX_BYTES), DEFAULT_MAX_BYTES)
    timeout = min(int(spec.get("timeout_seconds") or DEFAULT_TIMEOUT_SECONDS), 60)
    req_headers = {
        "User-Agent": "KeibaMetrics-SourceAcquisition/1.0 (+formal evidence capture)",
        "Accept": str(spec.get("accept") or "text/html,application/json,application/xml,text/plain;q=0.9,*/*;q=0.1"),
        "Accept-Language": str(spec.get("accept_language") or "ja,en;q=0.5"),
    }
    opener = urllib.request.build_opener(_SafeRedirect())
    request = urllib.request.Request(url, headers=req_headers, method="GET")
    fetched_at = utcnow()
    try:
        with opener.open(request, timeout=timeout) as resp:
            final_url = resp.geturl()
            validate_public_url(final_url)
            raw = resp.read(max_bytes + 1)
            if len(raw) > max_bytes:
                raise ValueError("SOURCE_MAX_BYTES_EXCEEDED")
            headers = {k.lower(): v for k, v in resp.headers.items()}
            if str(headers.get("content-encoding") or "").lower() == "gzip":
                raw = gzip.decompress(raw)
                if len(raw) > max_bytes:
                    raise ValueError("SOURCE_DECOMPRESSED_MAX_BYTES_EXCEEDED")
            ctype = str(headers.get("content-type") or "").lower()
            allowed_content = ("text/", "application/json", "application/xml", "application/xhtml+xml")
            if ctype and not any(x in ctype for x in allowed_content):
                raise ValueError("SOURCE_CONTENT_TYPE_NOT_ALLOWED:" + ctype)
            return snapshot_from_bytes(
                spec,
                raw,
                final_url=final_url,
                status_code=int(getattr(resp, "status", 200)),
                headers=headers,
                fetched_at=fetched_at,
                prediction_cutoff=prediction_cutoff,
            )
    except urllib.error.HTTPError as e:
        raw = e.read(max_bytes + 1)
        headers = {k.lower(): v for k, v in e.headers.items()}
        return snapshot_from_bytes(
            spec,
            raw[:max_bytes],
            final_url=e.geturl() or url,
            status_code=int(e.code),
            headers=headers,
            fetched_at=fetched_at,
            prediction_cutoff=prediction_cutoff,
        )


def _merge_evidence(snapshots: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[str]]:
    candidates: Dict[str, List[Dict[str, Any]]] = {}
    for s in snapshots:
        if s.get("http_status", 0) < 200 or s.get("http_status", 0) >= 300:
            continue
        for field, value in (s.get("extracted_evidence") or {}).items():
            candidates.setdefault(field, []).append({
                "value": value,
                "source_id": s.get("source_id"),
                "authority": s.get("authority"),
                "priority": int(s.get("authority_priority") or 0),
                "snapshot_sha256": s.get("snapshot_sha256"),
                "fetched_at": s.get("fetched_at"),
                "cutoff_relation": s.get("cutoff_relation"),
            })
    normalized: Dict[str, Any] = {}
    conflicts: List[Dict[str, Any]] = []
    errors: List[str] = []
    for field, rows in candidates.items():
        rows = sorted(rows, key=lambda x: (-x["priority"], str(x["source_id"])))
        top_priority = rows[0]["priority"]
        top = [x for x in rows if x["priority"] == top_priority]
        distinct_top = {json.dumps(x["value"], ensure_ascii=False, sort_keys=True) for x in top}
        if len(distinct_top) > 1:
            conflicts.append({"field": field, "status": "UNRESOLVED_EQUAL_PRIORITY", "candidates": rows})
            errors.append("SOURCE_CONFLICT_UNRESOLVED:" + field)
            continue
        winner = rows[0]
        normalized[field] = {
            "value": winner["value"],
            "source_id": winner["source_id"],
            "authority": winner["authority"],
            "authority_priority": winner["priority"],
            "snapshot_sha256": winner["snapshot_sha256"],
            "fetched_at": winner["fetched_at"],
            "cutoff_relation": winner["cutoff_relation"],
        }
        lower_conflicts = [x for x in rows[1:] if x["value"] != winner["value"]]
        if lower_conflicts:
            conflicts.append({
                "field": field,
                "status": "RESOLVED_BY_AUTHORITY_PRIORITY",
                "winner": winner,
                "lower_priority_conflicts": lower_conflicts,
            })
    return normalized, conflicts, errors


def acquire_sources(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    race_id = str(payload.get("race_id") or "")
    cutoff = str(payload.get("prediction_cutoff") or "")
    specs = payload.get("sources")
    errors: List[str] = []
    if not race_id:
        errors.append("RACE_ID_REQUIRED")
    if not cutoff or _parse_dt(cutoff) is None:
        errors.append("PREDICTION_CUTOFF_REQUIRED")
    if not isinstance(specs, list) or not specs:
        errors.append("REQUIRED_SOURCE_MANIFEST_REQUIRED")
        specs = []
    if len(specs) > 50:
        errors.append("SOURCE_MANIFEST_TOO_LARGE")
        specs = specs[:50]

    snapshots: List[Dict[str, Any]] = []
    seen_ids = set()
    for idx, spec in enumerate(specs):
        if not isinstance(spec, dict):
            errors.append("SOURCE_SPEC_INVALID:" + str(idx))
            continue
        source_id = str(spec.get("source_id") or "").strip()
        if not source_id:
            errors.append("SOURCE_ID_REQUIRED:" + str(idx))
            continue
        if source_id in seen_ids:
            errors.append("SOURCE_ID_DUPLICATE:" + source_id)
            continue
        seen_ids.add(source_id)
        try:
            snap, serr = fetch_source(spec, cutoff)
            snapshots.append(snap)
            errors.extend(serr)
        except Exception as e:
            snapshots.append({
                "schema": SOURCE_SCHEMA,
                "source_id": source_id,
                "source_class": str(spec.get("source_class") or "UNCLASSIFIED"),
                "authority": str(spec.get("authority") or "UNSPECIFIED"),
                "official": bool(spec.get("official", False)),
                "required": bool(spec.get("required", False)),
                "requested_url": str(spec.get("url") or ""),
                "status": "FETCH_FAILED",
                "error": str(e),
                "fetched_at": utcnow(),
            })
            if spec.get("required"):
                errors.append("REQUIRED_SOURCE_FETCH_FAILED:" + source_id + ":" + str(e))

    by_id = {s.get("source_id"): s for s in snapshots}
    missing_required = [
        str(spec.get("source_id"))
        for spec in specs
        if isinstance(spec, dict)
        and spec.get("required")
        and (
            str(spec.get("source_id")) not in by_id
            or by_id[str(spec.get("source_id"))].get("status") == "FETCH_FAILED"
            or int(by_id[str(spec.get("source_id"))].get("http_status") or 0) < 200
            or int(by_id[str(spec.get("source_id"))].get("http_status") or 0) >= 300
        )
    ]
    if missing_required:
        errors.append("MISSING_REQUIRED_SOURCES:" + ",".join(missing_required))

    normalized, conflicts, conflict_errors = _merge_evidence(snapshots)
    errors.extend(conflict_errors)
    stale_sources = [s.get("source_id") for s in snapshots if s.get("stale")]
    post_cutoff_sources = [s.get("source_id") for s in snapshots if s.get("cutoff_relation") == "POST_CUTOFF"]
    required_extract_failures = [
        s.get("source_id")
        for s in snapshots
        if s.get("required") and any(str(x).startswith("EXTRACT_REQUIRED_FAILED:") for x in (s.get("extraction_errors") or []))
    ]
    if required_extract_failures:
        errors.append("REQUIRED_EXTRACTION_INCOMPLETE:" + ",".join(str(x) for x in required_extract_failures))

    manifest_canonical = [
        {
            "source_id": str(s.get("source_id") or ""),
            "url": str(s.get("url") or ""),
            "source_class": str(s.get("source_class") or "UNCLASSIFIED"),
            "authority": str(s.get("authority") or "UNSPECIFIED"),
            "priority": int(s.get("priority") or (100 if s.get("official") else 50)),
            "official": bool(s.get("official", False)),
            "required": bool(s.get("required", False)),
            "extract": s.get("extract") or [],
        }
        for s in specs
        if isinstance(s, dict)
    ]
    raw_bundle = [
        {
            "source_id": s.get("source_id"),
            "raw_sha256": s.get("raw_sha256"),
            "snapshot_sha256": s.get("snapshot_sha256"),
            "fetched_at": s.get("fetched_at"),
            "final_url": s.get("final_url"),
        }
        for s in snapshots
    ]
    artifact = {
        "schema": SOURCE_SCHEMA,
        "profile": SOURCE_PROFILE,
        "race_id": race_id,
        "prediction_cutoff": cutoff,
        "source_freeze_at": utcnow(),
        "required_source_manifest": manifest_canonical,
        "required_source_manifest_sha256": sha_obj(manifest_canonical),
        "sources": snapshots,
        "raw_source_bundle_sha256": sha_obj(raw_bundle),
        "normalized_evidence": normalized,
        "normalized_evidence_sha256": sha_obj(normalized),
        "conflicts": conflicts,
        "missing_required_sources": missing_required,
        "stale_sources": stale_sources,
        "post_cutoff_sources": post_cutoff_sources,
        "formal_ready": not errors,
        "errors": list(dict.fromkeys(errors)),
    }
    artifact["source_snapshot_sha256"] = sha_obj({k: v for k, v in artifact.items() if k != "source_snapshot_sha256"})
    return artifact, artifact["errors"]


def verify_source_artifact(artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    if not isinstance(artifact, dict):
        return False, ["SOURCE_ARTIFACT_INVALID"]
    if artifact.get("profile") != SOURCE_PROFILE:
        errors.append("SOURCE_PROFILE_MISMATCH")
    snapshots = artifact.get("sources")
    if not isinstance(snapshots, list):
        errors.append("SOURCE_SNAPSHOTS_MISSING")
        snapshots = []
    for s in snapshots:
        if not isinstance(s, dict) or "raw_gzip_b64" not in s:
            if isinstance(s, dict) and s.get("status") == "FETCH_FAILED":
                continue
            errors.append("SOURCE_RAW_SNAPSHOT_MISSING")
            continue
        try:
            raw = gzip.decompress(base64.b64decode(s["raw_gzip_b64"]))
            if hashlib.sha256(raw).hexdigest() != s.get("raw_sha256"):
                errors.append("SOURCE_RAW_HASH_MISMATCH:" + str(s.get("source_id")))
            expected = sha_obj({k: v for k, v in s.items() if k != "snapshot_sha256"})
            if expected != s.get("snapshot_sha256"):
                errors.append("SOURCE_SNAPSHOT_HASH_MISMATCH:" + str(s.get("source_id")))
        except Exception:
            errors.append("SOURCE_RAW_DECODE_FAILED:" + str(s.get("source_id")))
    if sha_obj(artifact.get("normalized_evidence") or {}) != artifact.get("normalized_evidence_sha256"):
        errors.append("SOURCE_NORMALIZED_EVIDENCE_HASH_MISMATCH")
    optional_hashes = [
        ("discovered_auxiliary_source_manifest", "discovered_auxiliary_source_manifest_sha256", "SOURCE_AUXILIARY_MANIFEST_HASH_MISMATCH"),
        ("nar_entity_registry", "nar_entity_registry_sha256", "SOURCE_ENTITY_REGISTRY_HASH_MISMATCH"),
        ("auxiliary_evidence", "auxiliary_evidence_sha256", "SOURCE_AUXILIARY_EVIDENCE_HASH_MISMATCH"),
        ("jma_weather_evidence", "jma_weather_evidence_sha256", "SOURCE_JMA_WEATHER_HASH_MISMATCH"),
        ("point_in_time_population_ledger", "point_in_time_population_ledger_sha256", "SOURCE_POPULATION_LEDGER_HASH_MISMATCH"),
        ("sbo_public_shadow_evidence", "sbo_public_shadow_evidence_sha256", "SOURCE_SBO_PUBLIC_SHADOW_HASH_MISMATCH"),
        ("tsl_public_shadow_evidence", "tsl_public_shadow_evidence_sha256", "SOURCE_TSL_PUBLIC_SHADOW_HASH_MISMATCH"),
        ("jra_official_runner_universe", "jra_official_runner_universe_sha256", "SOURCE_JRA_RUNNER_UNIVERSE_HASH_MISMATCH"),
        ("jra_auxiliary_evidence", "jra_auxiliary_evidence_sha256", "SOURCE_JRA_AUXILIARY_EVIDENCE_HASH_MISMATCH"),
    ]
    for field, hash_field, err in optional_hashes:
        if field in artifact and sha_obj(artifact.get(field)) != artifact.get(hash_field):
            errors.append(err)
    expected_artifact = sha_obj({k: v for k, v in artifact.items() if k != "source_snapshot_sha256"})
    if expected_artifact != artifact.get("source_snapshot_sha256"):
        errors.append("SOURCE_ARTIFACT_HASH_MISMATCH")
    if artifact.get("formal_ready") is not True:
        errors.append("SOURCE_NOT_FORMAL_READY")
    return not errors, errors

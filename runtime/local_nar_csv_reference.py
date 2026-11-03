"""Offline NAR CSV ZIP inspection, not SOURCE admission or a download bypass.

Field order is documented by the official September 16, 2026 manual. Actual
encoding and header presence are intentionally caller-supplied: the manual
does not specify them. This parser grants no licence, signature, permanent ID,
active universe or numerical Consumer authority, and makes no network call.
"""
from __future__ import annotations

import csv
from datetime import date, datetime, timezone
import hashlib
import io
import json
import re
import stat
import unicodedata
from urllib.parse import parse_qs, urlsplit
import zipfile

PROFILE = "KM-NAR-DOCUMENTED-CSV-REFERENCE-v0.1-20261103"
MANUAL = "https://www.keiba.go.jp/pdf/manual/data_pdf_manual.pdf"
SCHEMAS = {
    "racelist": tuple(["競馬場", "競走年月日", "レース番号", "発走時刻", "競走種類名称", "レース名"]
        + [f"副賞名{i}" for i in range(1, 16)]
        + ["芝ダート区分", "回り", "距離", "天候", "馬場", "頭数", "条件"]
        + [f"{i}着賞金(円)" for i in range(1, 6)] + ["上がり4F", "上がり3F"]
        + [f"ハロンタイム{i}" for i in range(1, 16)]
        + [f"コーナー名称{i}" for i in range(1, 9)]
        + [f"コーナー通過順{i}" for i in range(1, 9)]),
    "horselist": tuple("競馬場 競走年月日 レース番号 枠番 帽色 馬番 馬名 性 齢 毛色 生年月日 父馬名 母馬名 母父馬名 騎手名 騎手所属 負担重量 騎手成績 調教師 調教師所属 馬主氏名 生産牧場名 馬体重 馬体重増減 全成績 ダート左成績 ダート右成績 当競馬場成績 うち当距離成績 最高タイム 最高タイム良馬場 着順 タイム 着差 上がり3F 人気".split()),
    "odds": tuple("競馬場 競走年月日 レース番号 賭式 番号1 番号2 番号3 オッズ オッズ（最大） 人気".split()),
    "payback": tuple(["競馬場", "競走年月日", "レース番号", "レース名", "単勝組番", "単勝払戻金（円）", "単勝人気"]
        + [f"{part}{i}{suffix}" for i in range(1, 4) for part, suffix in
           [("複勝組番", ""), ("複勝払戻金", "（円）"), ("複勝人気", "")]]
        + [f"{kind}{part}" for kind in ("枠複", "枠単", "馬複", "馬単") for part in
           ("組番1", "組番2", "払戻金（円）", "人気" if kind.startswith("枠") else "人気１")]
        + [f"ワイド{part}{i}{suffix}" for i in range(1, 4) for part, suffix in
           [("組番", "馬番1"), ("組番", "馬番2"), ("払戻金", "（円）"), ("人気", "")]]
        + [f"{kind}{part}" for kind in ("３連複", "３連単") for part in
           ("組番馬番1", "組番馬番2", "組番馬番3", "払戻金（円）", "人気")]),
}
_HORSE_OUTCOMES = ("着順", "タイム", "着差", "上がり3F", "人気")
_RACE_OUTCOMES = tuple(["上がり4F", "上がり3F"] + [f"ハロンタイム{i}" for i in range(1, 16)]
    + [f"コーナー通過順{i}" for i in range(1, 9)])


def _hash(raw):
    return hashlib.sha256(raw).hexdigest()


def _dt(value):
    out = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if out.tzinfo is None:
        raise ValueError("NAR_CSV_AWARE_CLOCK_REQUIRED")
    return out.astimezone(timezone.utc)


def _norm(value):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", str(value)))


def _observed_download_url(value):
    """Accept the observed daily/monthly UI endpoints, never generate a URL."""
    p = urlsplit(value)
    q = parse_qs(p.query, strict_parsing=True)
    if (p.scheme != "https" or p.netloc != "www.keiba.go.jp" or p.fragment
            or p.path not in {"/KeibaWeb/DataDownload/RaceDataDownload", "/KeibaWeb/DataDownload/OddsDataDownload"}
            or any(len(v) != 1 for v in q.values())):
        raise ValueError("NAR_CSV_OBSERVED_URL_SCOPE_REQUIRED")
    if q == {"type": ["daily"]}:
        return "daily"
    if (set(q) == {"type", "k_year", "k_month"} and q["type"] == ["monthly"]
            and re.fullmatch(r"\d{4}", q["k_year"][0])
            and q["k_month"][0].isdigit() and 1 <= int(q["k_month"][0]) <= 12):
        return "monthly"
    raise ValueError("NAR_CSV_OBSERVED_URL_SCOPE_REQUIRED")


def inspect_zip(raw, *, capture, race, encoding, header_mode, now=None):
    """Return explicit Tier3 facts/provenance from supplied original ZIP bytes.

    ``capture`` must describe actual HTTP bytes supplied by the caller. Its
    claims are not verified here and cannot become a SOURCE receipt. The strict
    raw hash and observed URL gates prevent a search excerpt from masquerading
    as ZIP bytes. No defaults infer header/encoding or cancellation semantics.
    """
    if not isinstance(raw, bytes) or not 0 < len(raw) <= 30_000_000:
        raise ValueError("NAR_CSV_RAW_BYTES_REQUIRED_OR_COMPRESSED_LIMIT")
    if encoding not in {"utf-8", "utf-8-sig", "cp932"} or header_mode not in {"present", "absent"}:
        raise ValueError("NAR_CSV_EXPLICIT_ENCODING_AND_HEADER_MODE_REQUIRED")
    if (capture.get("provider") != "NAR_OFFICIAL_CSV" or capture.get("http_status") != 200
            or capture.get("raw_sha256") != _hash(raw)
            or capture.get("retrieval_method") not in {"AUTHORIZED_HTTP_GET", "OFFICIAL_BROWSER_DOWNLOAD"}
            or not isinstance(capture.get("usage_qualification"), dict)):
        raise ValueError("NAR_CSV_CAPTURE_PROVENANCE_UNVERIFIED")
    period = _observed_download_url(capture["source_url"])
    captured = _dt(capture["captured_at"])
    if captured > _dt(now or datetime.now(timezone.utc)):
        raise ValueError("NAR_CSV_CAPTURE_IN_FUTURE")
    day = date.fromisoformat(race["race_date"])
    if period == "monthly":
        query = parse_qs(urlsplit(capture["source_url"]).query)
        if int(query["k_year"][0]) != day.year or int(query["k_month"][0]) != day.month:
            raise ValueError("NAR_CSV_URL_MONTH_RACE_MISMATCH")
    if race.get("venue_id") != "FNB" or type(race.get("race_no")) is not int or not 1 <= race["race_no"] <= 12:
        raise ValueError("NAR_CSV_FNB_RACE_IDENTITY_REQUIRED")
    key = ("船橋", day.strftime("%Y%m%d"), str(race["race_no"]))
    tables, file_meta = {}, {}
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries = archive.infolist()
        if not 1 <= len(entries) <= 4 or sum(i.file_size for i in entries) > 200_000_000:
            raise ValueError("NAR_CSV_ARCHIVE_LIMIT")
        for item in entries:
            name = item.filename
            m = re.fullmatch(r"(\d{6}|\d{8})(?:_0[1-3])?_(racelist|horselist|odds|payback)\.csv", name)
            mode = item.external_attr >> 16
            if (not m or name in file_meta or item.flag_bits & 1 or stat.S_ISLNK(mode)
                    or item.is_dir() or item.file_size > 150_000_000):
                raise ValueError("NAR_CSV_UNEXPECTED_ARCHIVE_MEMBER")
            stamp, kind = m.groups()
            expected_stamp = day.strftime("%Y%m%d" if period == "daily" else "%Y%m")
            if stamp != expected_stamp or kind in tables:
                raise ValueError("NAR_CSV_PERIOD_OR_DUPLICATE_TABLE_MISMATCH")
            content = archive.read(item)
            rows = list(csv.reader(io.StringIO(content.decode(encoding, errors="strict"), newline=""), strict=True))
            schema = SCHEMAS[kind]
            if header_mode == "present":
                if not rows or tuple(rows.pop(0)) != schema:
                    raise ValueError("NAR_CSV_DOCUMENTED_HEADER_MISMATCH")
            out = []
            for number, row in enumerate(rows, 2 if header_mode == "present" else 1):
                if len(row) != len(schema):
                    raise ValueError("NAR_CSV_DOCUMENTED_COLUMN_COUNT_MISMATCH")
                record = dict(zip(schema, row))
                if (not re.fullmatch(r"\d{8}", record["競走年月日"])
                        or not 1 <= int(record["レース番号"]) <= 12):
                    raise ValueError("NAR_CSV_ROW_RACE_IDENTITY_INVALID")
                actual_day = date.fromisoformat("-".join((record["競走年月日"][:4], record["競走年月日"][4:6], record["競走年月日"][6:])))
                if actual_day.strftime("%Y%m%d" if period == "daily" else "%Y%m") != expected_stamp:
                    raise ValueError("NAR_CSV_ROW_OUTSIDE_FILE_PERIOD")
                if (record["競馬場"], record["競走年月日"], record["レース番号"]) == key:
                    out.append((number, record))
            tables[kind] = out
            file_meta[name] = {"raw_sha256": _hash(content), "uncompressed_bytes": len(content), "kind": kind}
    if len(tables.get("racelist", [])) != 1 or not tables.get("horselist"):
        raise ValueError("NAR_CSV_RACE_CARD_JOIN_UNAVAILABLE")
    race_row_number, race_row = tables["racelist"][0]
    post = race_row["発走時刻"]
    if not re.fullmatch(r"\d{4}", post) or int(post[:2]) > 23 or int(post[2:]) > 59:
        raise ValueError("NAR_CSV_POST_TIME_INVALID")
    distance = race_row["距離"]
    if not distance.isdigit() or int(distance) <= 0:
        raise ValueError("NAR_CSV_DISTANCE_INVALID")
    parsed_identity = {"venue_id": "FNB", "race_date": day.isoformat(), "race_no": race["race_no"],
        "official_race_id": None, "source_composite_key": list(key),
        "scheduled_post_at": f"{day.isoformat()}T{post[:2]}:{post[2:]}:00+09:00",
        "distance_m": int(distance), "surface": {"ダート": "DIRT", "芝": "TURF"}.get(race_row["芝ダート区分"]),
        "turn": {"左": "LEFT", "右": "RIGHT", "直": "STRAIGHT"}.get(race_row["回り"]),
        "surface_label": race_row["芝ダート区分"], "turn_label": race_row["回り"]}
    for field in ("distance_m", "surface", "turn", "scheduled_post_at"):
        if field in race:
            expected, observed = race[field], parsed_identity[field]
            if field == "scheduled_post_at":
                expected, observed = _dt(expected), _dt(observed)
            if expected != observed:
                raise ValueError("NAR_CSV_EXPECTED_RACE_CONFLICT:" + field)
    numbers, names, runners = set(), set(), []
    outcome_present = any(race_row.get(k) for k in _RACE_OUTCOMES)
    for row_number, row in tables["horselist"]:
        if not row["馬番"].isdigit() or int(row["馬番"]) < 1 or not row["馬名"].strip():
            raise ValueError("NAR_CSV_HORSE_IDENTITY_INVALID")
        number = int(row["馬番"])
        name = _norm(row["馬名"])
        if number in numbers or name in names:
            raise ValueError("NAR_CSV_DUPLICATE_RUNNER_NOT_RECONCILED")
        numbers.add(number); names.add(name)
        outcome_present |= any(row.get(k) for k in _HORSE_OUTCOMES)
        # Names are labels, never permanent horse/parent/jockey/stable IDs.
        runners.append({"runner_number": number, "horse_name": row["馬名"],
            "horse_id": None, "sire_id": None, "damsire_id": None, "jockey_id": None, "stable_id": None,
            "prestart_reference_fields": {k: v for k, v in row.items() if k not in _HORSE_OUTCOMES},
            "outcome_fields_separated": {k: row[k] for k in _HORSE_OUTCOMES},
            "field_provenance": {k: {"table": "horselist", "csv_row": row_number,
                "csv_column": SCHEMAS["horselist"].index(k) + 1, "zip_raw_sha256": capture["raw_sha256"]}
                for k in row}})
    declared_count = race_row["頭数"]
    # Public CSV does not define whether cancellations are removed from 頭数.
    # The count comparison is an audit, never a fabricated active universe.
    reported_count = int(declared_count) if declared_count.isdigit() else None
    packet = {"profile": PROFILE, "provider_id": "NAR_OFFICIAL_CSV", "provider_authority": "NAR_OFFICIAL",
        "schema_basis": {"url": MANUAL, "manual_revision": "2026-09-16", "counts": {k: len(v) for k, v in SCHEMAS.items()}},
        "capture": dict(capture), "encoding_caller_supplied_not_auto_detected": encoding,
        "header_mode_caller_supplied_not_verified_by_manual": header_mode,
        "zip_files": file_meta, "race_identity": parsed_identity,
        "race_reference_fields": {k: v for k, v in race_row.items() if k not in _RACE_OUTCOMES},
        "race_field_provenance": {k: {"table": "racelist", "csv_row": race_row_number,
            "csv_column": SCHEMAS["racelist"].index(k) + 1, "zip_raw_sha256": capture["raw_sha256"]} for k in race_row},
        "runners": runners, "reported_headcount": reported_count, "parsed_horse_rows": len(runners),
        "headcount_matches_horse_rows": reported_count == len(runners), "target_outcome_fields_present": bool(outcome_present),
        "active_universe_verified": False, "change_semantics_verified": False,
        "source_update_time": None, "prediction_cutoff": None, "permanent_id_provision": "NOT_PROVIDED_BY_NAR_CSV_MANUAL_FAQ",
        "admission_classification": "PRIVATE_REFERENCE_NOT_FORMAL_SOURCE_NOT_SIGNED_NOT_REGISTERED_OOS",
        "formal_source_ready": False, "formal_numerical_consumption_authorized": False,
        "candidate_prestart_claim": False, "new_formal_scores": 0,
        "missingness": ["permanent entity IDs", "official latest changes/cancellations", "official Cutoff", "SOURCE signature",
                        "complete dated individual past starts", "Provider access/consumer admission"]}
    packet["sha256"] = _hash(json.dumps(packet, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())
    return packet

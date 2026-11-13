"""Read-only integrity of the optional FNB odds snapshot.

Odds evidence can only identify a provisional observed active set. Missing
odds remains UNKNOWN. No probability, market calibration, licensed use or
production winner/consumer authority is granted.
"""
from __future__ import annotations

import base64
import gzip
import hashlib
import io

from runtime.local_physical.nar_source_manifest import _odds_source
from runtime.local_physical.source_acquisition import _extract, sha_obj

MAX_RAW = 600000


def check_odds(odds: dict, race_date: str, race_no: int) -> dict:
    spec = _odds_source("FNB", "19", race_date.replace("-", "/"), race_no)
    if (odds.get("source_id") != spec["source_id"]
            or odds.get("source_class") != spec["source_class"]
            or odds.get("requested_url") != spec["url"]
            or odds.get("final_url") != spec["url"]
            or odds.get("authority") != "NAR_OFFICIAL"
            or odds.get("official") is not True
            or odds.get("http_status") != 200):
        raise ValueError("FNB_ODDS_IDENTITY_INVALID")
    if odds.get("snapshot_sha256") != sha_obj(
            {k: v for k, v in odds.items() if k != "snapshot_sha256"}):
        raise ValueError("FNB_ODDS_SNAPSHOT_HASH_MISMATCH")
    encoded = odds.get("raw_gzip_b64")
    if not isinstance(encoded, str) or len(encoded) > MAX_RAW * 2:
        raise ValueError("FNB_ODDS_RAW_MISSING_OR_OVERSIZE")
    with gzip.GzipFile(fileobj=io.BytesIO(base64.b64decode(
            encoded, validate=True))) as stream:
        raw = stream.read(MAX_RAW + 1)
    if (len(raw) > MAX_RAW or len(raw) != odds.get("byte_count")
            or hashlib.sha256(raw).hexdigest() != odds.get("raw_sha256")):
        raise ValueError("FNB_ODDS_RAW_SHA_OR_SIZE_MISMATCH")
    parsed, errors = _extract(raw, odds.get("content_type", ""), spec["extract"])
    if errors or parsed != odds.get("extracted_evidence"):
        raise ValueError("FNB_ODDS_EXTRACTED_FACTS_DIFFER_FROM_RAW")
    return parsed

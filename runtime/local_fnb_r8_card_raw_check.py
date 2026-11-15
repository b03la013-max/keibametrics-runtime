"""Revalidate one FNB race card against its archived source bytes.

An offline integrity check only: no fresh acquisition, issuer signature,
provider license, betting authority or delivery permission is inferred.
"""
from __future__ import annotations
import base64
import gzip
import io

from runtime.local_fnb_r7_plan_provenance import _parse_raw, MAX_CARD_BYTES
from runtime.local_physical.nar_source_manifest import _race_card_source
from runtime.local_physical.source_acquisition import _extract


def check_card(card: dict, race_date: str, race_no: int) -> dict:
    _header, parsed, fetched = _parse_raw(card)
    spec = _race_card_source("FNB", "19", race_date.replace("-", "/"), race_no)
    if (card.get("source_id") != spec["source_id"]
            or card.get("requested_url") != spec["url"]
            or card.get("final_url") != spec["url"]):
        raise ValueError("FNB_CARD_ID_OR_URL_MISMATCH")
    with gzip.GzipFile(fileobj=io.BytesIO(
            base64.b64decode(card["raw_gzip_b64"], validate=True))) as stream:
        raw = stream.read(MAX_CARD_BYTES + 1)
    if len(raw) > MAX_CARD_BYTES:
        raise ValueError("FNB_CARD_TOO_LARGE")
    extracted, errors = _extract(raw, card.get("content_type", ""), spec["extract"])
    if errors or extracted != card.get("extracted_evidence"):
        raise ValueError("FNB_CARD_EXTRACTED_FACTS_DIFFER_FROM_RAW")
    if not isinstance(parsed, list) or not parsed:
        raise ValueError("FNB_CARD_RUNNERS_EMPTY")
    return {"card_runners": parsed, "fetched": fetched,
            "raw_sha256": card["raw_sha256"], "extracted": extracted}

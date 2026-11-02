"""FNB R13: resolve jockey from the *same* stored official race card.

The NAR active_runner_universe currently holds number/name/status but
ordinarily not rider. Its companion parsed official card records a separate
current_jockey field. Do not treat missing active-row 'jockey' as a missing
official current jockey, and never accept an unrelated secondary-news rider
as a signed fact.

This helper does NOT claim independent re-extraction from raw HTML, live
network admission, a verified issuer signature, or any scope grant.
"""
from __future__ import annotations

import re
from typing import Any

def _norm(value: Any) -> str:
    if not isinstance(value,str):
        return ""
    return re.sub(r"\s+","",value).strip()

def resolve_current_jockey(source: dict, horse_no: int, *, parser=None) -> dict:
    if type(horse_no) is not int or not 1 <= horse_no <= 20:
        raise ValueError("FNB_OFFICIAL_RIDER_HORSE_NUMBER_INVALID")
    universe=source.get("official_runner_universe") or source.get("active_runner_universe") or {}
    if not isinstance(universe,dict) or not isinstance(universe.get("runners"),list):
        raise ValueError("FNB_OFFICIAL_ACTIVE_RUNNER_LIST_REQUIRED")
    horse_rows=[r for r in universe["runners"] if isinstance(r,dict)
                and str(r.get("horse_no") or r.get("runner_id"))==str(horse_no)]
    if len(horse_rows)!=1:
        raise ValueError("FNB_OFFICIAL_RIDER_RUNNER_NOT_ACTIVE_OR_DUPLICATE")
    row=horse_rows[0]
    if parser is None:
        # Existing NAR card parser, shared with numerical evidence compiler.
        # It reads the frozen recorded race-card tables, not external news.
        from runtime.local_nar_evidence_candidate import parse_race_card
        parser=parse_race_card
    parsed=parser(source)
    if not isinstance(parsed,dict):
        raise ValueError("FNB_RECORDED_OFFICIAL_RIDER_CARD_INVALID")
    key=str(horse_no)
    facts=parsed.get(key)
    if not isinstance(facts,dict):
        raise ValueError("FNB_RECORDED_OFFICIAL_RIDER_ID_NOT_FOUND")
    if (str(facts.get("runner_id"))!=key or
            _norm(facts.get("name"))!=_norm(row.get("name"))):
        raise ValueError("FNB_RECORDED_OFFICIAL_RIDER_HORSE_ID_MISMATCH")
    rider=facts.get("current_jockey")
    if not _norm(rider):
        raise ValueError("FNB_RECORDED_OFFICIAL_RIDER_UNKNOWN")
    embedded=row.get("jockey")
    if embedded is not None and _norm(embedded)!=_norm(rider):
        raise ValueError("FNB_ACTIVE_ROW_VS_OFFICIAL_CARD_RIDER_CONFLICT")
    identity=source.get("normalized_evidence") or {}
    rc=identity.get("race_card_tables") or {}
    if not isinstance(rc,dict) or not rc.get("source_id") or not rc.get("snapshot_sha256"):
        raise ValueError("FNB_RECORDED_RIDER_SOURCE_ID_OR_SHA_MISSING")
    if (facts.get("race_card_source_id")!=rc["source_id"] or
            facts.get("race_card_snapshot_sha256")!=rc["snapshot_sha256"]):
        raise ValueError("FNB_RECORDED_RIDER_FROZEN_CARD_PROVENANCE_MISMATCH")
    return {"horse_no":horse_no, "current_jockey":str(rider),
            "race_card_source_id":rc["source_id"],
            "race_card_snapshot_sha256":rc["snapshot_sha256"],
            "result_source":"RECORDED_NAR_OFFICIAL_RACE_CARD",
            "independent_raw_bytes_reparsed_here":False,
            "issuer_signature_verified_here":False}

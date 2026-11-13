"""FNB private Work-browser offline ingestion of original NAR desktop HTML bytes.

This path does not make an automated HTTP request, alter robots controls or
claim a provider-issued receipt. It requires real response bytes already
saved by the user's private browser. It reconstructs one official NAR
RaceCard snapshot using EXISTING extractors, verifies raw content identity,
and saves the unsigned source under a path outside the PUBLIC GitHub repo.

Only a verified external signer can elevate this capture to Signed SOURCE.
For research, the captured SOURCE can feed the existing independent
non-Production 29-index pipeline without requiring registered v2 OOS Plan.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import base64,hashlib,json

from runtime.local_fnb_r13_private_single_numeric import (
    _atomic_private_write,_encoded)
from runtime.local_fnb_r13_private_source_admission import SCOPE,PURPOSE

PROFILE="KM-FNB-R16-OFFICIAL-DESKTOP-BROWSER-RAW-OFFLINE-IMPORT-v1"

def time(value):
    stamp=datetime.fromisoformat(str(value).replace("Z","+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("FNB_BROWSER_CAPTURE_TIMEZONE_REQUIRED")
    return stamp

def ingest(*,html_path:Path,request:dict,observed_url:str,
           capture_time:str,private_output:Path,public_repo:Path,
           now=None,diagnostic_only=False):
    from runtime.local_physical.nar_source_manifest import _race_card_source
    from runtime.local_physical.source_acquisition import (
        snapshot_from_bytes,sha_obj)
    from runtime.local_fnb_r8_card_raw_check import check_card
    from runtime.local_physical.nar_runner_universe import enrich_source_artifact
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("FNB_BROWSER_IMPORT_NOW_TIMEZONE_REQUIRED")
    root=Path(public_repo).resolve()
    dest=Path(private_output).resolve()
    html=Path(html_path).resolve()
    if (dest==root or root in dest.parents or
            html==root or root in html.parents):
        raise ValueError("FNB_OFFICIAL_PRIVATE_BROWSER_BYTES_PUBLIC_REPO_FORBIDDEN")
    if not isinstance(request,dict) or request.get("venue_id")!="FNB":
        raise ValueError("FNB_OFFICIAL_BROWSER_EXPLICIT_VENUE_REQUIRED")
    day=request.get("race_date")
    race_no=request.get("race_no")
    if not isinstance(day,str) or type(race_no) is not int or not 1<=race_no<=12:
        raise ValueError("FNB_BROWSER_DATE_OR_RACE_NUMBER_INVALID")
    race_id=request.get("race_id")
    if (not isinstance(race_id,str) or
            race_id!=f"KM-LOCAL-FNB-{day.replace('-','')}-R{race_no:02d}-LIVE-R1"):
        raise ValueError("FNB_BROWSER_RACE_KEY_NOT_EXACT")
    expected=_race_card_source("FNB","19",day.replace("-","/"),race_no)
    if observed_url!=expected["url"]:
        raise ValueError("FNB_BROWSER_CANONICAL_OFFICIAL_URL_REQUIRED")
    stamp=time(capture_time)
    cutoff=time(request["prediction_cutoff"])
    post=time(request["scheduled_post_at"])
    if not stamp<cutoff<post:
        raise ValueError("FNB_BROWSER_SOURCE_NOT_CAPTURED_BEFORE_CUTOFF")
    if not diagnostic_only and now>=cutoff:
        raise ValueError("FNB_BROWSER_PREDICTION_CUTOFF_ALREADY_EXPIRED")
    raw=html.read_bytes()
    if not raw or len(raw)>expected["max_bytes"]:
        raise ValueError("FNB_BROWSER_OFFICIAL_HTML_BYTES_INVALID")
    fetched=stamp.astimezone(timezone.utc).isoformat()
    card,errors=snapshot_from_bytes(expected,raw,
        final_url=observed_url,status_code=200,
        headers={"content-type":"text/html; charset=UTF-8"},
        fetched_at=fetched,prediction_cutoff=request["prediction_cutoff"])
    if errors:
        raise ValueError("FNB_BROWSER_SOURCE_EXTRACTOR_REQUIRED_FIELDS_MISSING:"+
                         ",".join(str(x).split(":")[0] for x in errors[:4]))
    card["snapshot_sha256"]=sha_obj({k:v for k,v in card.items()
                                     if k!="snapshot_sha256"})
    parsed=check_card(card,day,race_no)
    if hashlib.sha256(raw).hexdigest()!=parsed["raw_sha256"]:
        raise ValueError("FNB_BROWSER_ORIGINAL_RAW_HASH_MISMATCH")
    normalized={"race_card_tables":{
        "value":parsed["extracted"]["race_card_tables"],
        "source_id":card["source_id"],
        "snapshot_sha256":card["snapshot_sha256"],
        "fetched_at":fetched}}
    active=enrich_source_artifact({"normalized_evidence":normalized})
    known={str(h["runner_id"]) for h in active["declared_runner_universe"]["runners"]}
    intended={str(h["runner_id"]) for h in request.get("runners",[])
              if isinstance(h,dict) and h.get("runner_id") is not None}
    if not known or not intended or known!=intended:
        raise ValueError("FNB_BROWSER_INTENT_VS_OFFICIAL_DECLARED_RUNNERS_CONFLICT")
    imported={"race_id":race_id,
        "source_race_context":{"venue_id":"FNB","race_date":day.replace("-","/"),
                              "race_no":race_no},
        "source_freeze_at":fetched,
        "prediction_cutoff":request["prediction_cutoff"],
        "scheduled_post_at":request["scheduled_post_at"],
        "sources":[card],
        "normalized_evidence":normalized,
        "declared_runner_universe":active["declared_runner_universe"],
        "active_runner_universe":active["active_runner_universe"],
        "official_runner_universe":active["official_runner_universe"],
        "runner_status_registry":active["runner_status_registry"],
        "source_snapshot_sha256":card["snapshot_sha256"],
        "research_mode":SCOPE,
        "capture_method":"PRIVATE_BROWSER_RESPONSE_BYTES_OFFLINE_IMPORT",
        "source_became_signed":False}
    folder=dest/race_id
    blob=_encoded(imported)
    source_sha=_atomic_private_write(folder/"unsigned_official_card_artifact.json",blob)
    receipt={"profile":PROFILE,
        "classification":("POSTCUTOFF_DIAGNOSTIC_ONLY_NOT_REGISTERED_OOS"
            if diagnostic_only else SCOPE),
        "purpose":PURPOSE,
        "race_id":race_id,"source_id":card["source_id"],
        "captured_at_reported_by_private_browser":fetched,
        "original_html_sha256":hashlib.sha256(raw).hexdigest(),
        "reconstructed_card_snapshot_sha256":card["snapshot_sha256"],
        "stored_artifact_sha256":source_sha,
        "declared_runner_count":len(known),
        "active_runner_count_verified":False,
        "card_raw_reparsed_and_identity_checked":True,
        "source_original_html_may_be_in_private_browser_workspace":True,
        "external_browser_timestamp_independently_signed":False,
        "official_issuer_signed_source_verified":False,
        "full_29_indices_calculated_here":False,
        "two_owner_krs_executed_here":False,
        "public_git_repository_raw_or_horse_data_exposed":False,
        "registered_oos_increment":0}
    receipt_sha=_atomic_private_write(folder/"source_browser_import_receipt.json",
                                     _encoded(receipt))
    if (hashlib.sha256((folder/"unsigned_official_card_artifact.json").read_bytes()).hexdigest()
            !=source_sha or
        hashlib.sha256((folder/"source_browser_import_receipt.json").read_bytes()).hexdigest()
            !=receipt_sha):
        raise ValueError("FNB_BROWSER_IMPORTED_PRIVATE_BYTES_READBACK_FAILED")
    return {"status":"FNB_BROWSER_SOURCE_IMPORTED_TO_PRIVATE_RESEARCH_UNSIGNED",
            "race_id":race_id,
            "declared_runner_count":receipt["declared_runner_count"],
            "raw_sha256":receipt["original_html_sha256"],
            "source_artifact_sha256":source_sha,
            "receipt_sha256":receipt_sha,
            "public_repo_touched":False,
            "signed_source_verified":False,
            "first_future_stage":"PRIVATE_FULL_29_NUMERIC_MATERIALIZER",
            "registered_oos_increment":0}

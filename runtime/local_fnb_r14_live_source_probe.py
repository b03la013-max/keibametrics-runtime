"""R14 actual same-day official FNB card GET in ephemeral, non-publishing mode.

A permitted private/noncommercial inspection is not a signed SOURCE or
approved numeric consumer. Only public clock/count/hashed provenance and
sanitized errors are disclosed from the public Actions runner. Card bytes,
individual horse names, rider history and 29-index grids NEVER go to the
public repository, logs or Actions artifacts. No Owner activation, KRS,
prediction, ticket, cost or external delivery is attempted.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from runtime.local_fnb_r11_prestart_emergency import DAY,program

PROFILE="KM-FNB-R14-OFFICIAL-LIVE-SOURCE-DIAGNOSTIC-v1"

def _card_spec(race_no):
    from runtime.local_physical.nar_source_manifest import _race_card_source
    return _race_card_source("FNB","19",DAY.replace("-","/"),race_no)

def classify_snapshot(card, *, race_no, now=None):
    from runtime.local_fnb_r8_card_raw_check import check_card
    from runtime.local_physical.nar_runner_universe import enrich_source_artifact
    now=now or datetime.now(timezone.utc)
    frozen=check_card(card,DAY,race_no)
    original=frozen["extracted"]["race_card_tables"]
    source={"normalized_evidence":{"race_card_tables":{
        "value":original,"source_id":card["source_id"],
        "snapshot_sha256":card["snapshot_sha256"]}}}
    grouped=enrich_source_artifact(source)
    declared=grouped["declared_runner_universe"]["runners"]
    registry=grouped["runner_status_registry"]
    listed=next(x for x in program() if x["race_no"]==race_no)
    post=datetime.fromisoformat(listed["scheduled_post_at"])
    seen=len(declared)
    if seen!=listed["declared_runner_count"]:
        raise ValueError("R14_OFFICIAL_LIVE_LISTED_COUNT_DRIFT_REQUIRES_RECHECK")
    if now.tzinfo is None:
        raise ValueError("R14_OBSERVATION_TIMEZONE_REQUIRED")
    recorded_card_fetch=card.get("fetched_at") or card.get("observed_at")
    result={
        "profile":PROFILE,
        "classification":"PRIVATE_NONCOMMERCIAL_EPHEMERAL_SOURCE_DIAGNOSTIC",
        "date":DAY,"venue":"FNB","race_no":race_no,
        "scheduled_post":listed["scheduled_post_at"],
        "observed_at":now.isoformat(),
        "before_scheduled_post":now<post,
        "prediction_cutoff_verified_from_authorized_plan":False,
        "source_class":"NAR_OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT",
        "source_id":card.get("source_id"),
        "source_url_public":card.get("requested_url"),
        "actual_http_status":card.get("http_status"),
        "card_fetched_at":recorded_card_fetch,
        "card_raw_sha256":card.get("raw_sha256"),
        "card_snapshot_sha256":card.get("snapshot_sha256"),
        "raw_byte_integrity_checked":True,
        "extracted_table_facts_reparsed_from_original_raw":True,
        "declared_runner_count":seen,
        "declared_body_weight_observed_count":sum(
            type(h.get("body_weight")) is int for h in declared),
        "runner_status_distribution":{k:sum(s.get("status")==k for s in registry)
            for k in ("ACTIVE","CANCELLED","EXCLUDED","ACTIVE_DECLARED")},
        "active_universe_proven_from_card_alone":not any(
            s.get("status")=="ACTIVE_DECLARED" for s in registry),
        "official_day_changes_complete":False,
        "signed_source_receipt_verified":False,
        "current_day_full_29_index_computed":False,
        "baseline_candidate_krs_5000_seed1":False,
        "six_method_tickets":False,
        "recipient_ack":False,
        "registered_forward_oos":False,
        "pfs":None,
        "raw_or_horse_content_exported_to_public_repository":False,
        "result":"CARD_RAW_IN_MEMORY_VERIFIED_PUBLIC_SAFE_RECEIPT",
    }
    return result

def probe_one(race_no, *, fetch=None,now=None):
    now=now or datetime.now(timezone.utc)
    if type(race_no) is not int or not 1<=race_no<=12:
        raise ValueError("R14_RACE_NUMBER_1_TO_12_REQUIRED")
    from runtime.local_physical.source_acquisition import fetch_source
    from runtime.local_race_day_dispatcher import read_official
    call=fetch or fetch_source
    spec=_card_spec(race_no)
    reads=[]
    try:
        card,errors=read_official(spec,fetch=call,reads=reads)
        if errors:
            return {"status":"OFFICIAL_LIVE_SOURCE_FETCH_HOLD",
                    "race_no":race_no,"errors":[str(e)[:120] for e in errors[:8]],
                    "get_attempts":len(reads),"raw_published":False,
                    "signed_source":False}
        observed=classify_snapshot(card,race_no=race_no,now=now)
        return {"status":"OFFICIAL_CARD_RAW_SEMANTICS_PASS",**observed,
                "get_attempts":len(reads)}
    except Exception as exc:
        return {"status":"OFFICIAL_LIVE_SOURCE_FETCH_HOLD",
                "race_no":race_no,
                "failure_type":type(exc).__name__,
                "failure_code":str(exc).split(":")[0][:120],
                "get_attempts":len(reads),"raw_published":False,
                "signed_source":False}

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("--race-no",type=int,required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args(argv)
    proof=probe_one(args.race_no)
    path=Path(args.output)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(proof,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
                    encoding="utf-8")
    print(json.dumps({
        "status":proof["status"],
        "race_no":args.race_no,
        "declared_runner_count":proof.get("declared_runner_count"),
        "source_status":proof.get("actual_http_status"),
        "failure_code":proof.get("failure_code"),
        "signed_source":False,
        "private_raw_content_published":False},ensure_ascii=False))
    return 0

if __name__=="__main__":
    raise SystemExit(main())

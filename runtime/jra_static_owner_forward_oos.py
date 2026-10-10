"""Independent Static Owner forward evidence; never issues Production approval.

Only actual Production-formula Full20 enters this shadow. Existing
source-derived Candidate cohorts cannot be counted for this policy.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from jra_static_owner_executable import compile_static_owner, PROFILE as OWNER_PROFILE

ROOT = Path(__file__).resolve().parents[1]
PROFILE = "JRA-STATIC-OWNER-INDEPENDENT-FORWARD-OOS"


def sha(obj):
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def time(value):
    result=datetime.fromisoformat(str(value).replace("Z","+00:00"))
    if result.tzinfo is None: raise ValueError("OOS_TIMEZONE_REQUIRED")
    return result


def fingerprint(root=ROOT):
    paths=("runtime/jra_static_owner_executable.py","runtime/jra_official_fact_evaluator_production.py",
           "runtime/jra_source_to_evidence_features.py","runtime/jra_source_runtime/jra_observed_context.py",
           "runtime/jra_source_runtime/jra_race_card_detail.py",
           "runtime/jra_evidence_to_base_production.py","runtime/jra_index_provenance_builder.py",
           "runtime/jra_evidence_feature_normalizer_production.py",
           "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json")
    return sha({p:hashlib.sha256((Path(root)/p).read_bytes()).hexdigest() for p in paths})


def freeze(intent, envelope, report, *, source_verified, created_at=None, root=ROOT):
    now=time(created_at or datetime.now(timezone.utc).isoformat())
    cutoff=time(intent["prediction_cutoff"]); post=time(intent["scheduled_post_at"])
    if not now <= cutoff < post: raise ValueError("STATIC_OWNER_FORWARD_CUTOFF_EXPIRED")
    if intent.get("acceptance_only") is True or intent.get("temporal_mode","FORMAL-PRE-RACE") != "FORMAL-PRE-RACE":
        raise ValueError("STATIC_OWNER_REPLAY_OR_ACCEPTANCE_FORBIDDEN")
    if source_verified is not True: raise ValueError("STATIC_OWNER_SIGNED_SOURCE_REQUIRED")
    if report.get("production_full_numerical_ready") is not True or report.get("source_only_full_numerical_ready") is not True:
        raise ValueError("STATIC_OWNER_SOURCE_ONLY_PRODUCTION_FULL20_REQUIRED")
    meeting_key=(intent.get("jra_source") or {}).get("jra_meeting_key")
    if not isinstance(meeting_key,str) or len(meeting_key)!=10 or not meeting_key.isdigit():
        raise ValueError("STATIC_OWNER_OFFICIAL_MEETING_KEY_REQUIRED")
    source=envelope["artifact"]
    if (source.get("race_id") != intent["race_id"] or source.get("prediction_cutoff") != intent["prediction_cutoff"]
            or source.get("source_snapshot_sha256") != sha({k:v for k,v in source.items() if k!="source_snapshot_sha256"})):
        raise ValueError("STATIC_OWNER_SOURCE_BINDING_INVALID")
    if report.get("race_id") != intent["race_id"] or report.get("family_id") != "JRA":
        raise ValueError("STATIC_OWNER_REPORT_IDENTITY_MISMATCH")
    prepared=report["prepared_numerical_request"]
    if prepared.get("race_id") != intent["race_id"] or prepared.get("family_id") != "JRA":
        raise ValueError("STATIC_OWNER_NUMERIC_IDENTITY_MISMATCH")
    official=source.get("jra_official_runner_universe") or {}
    ids=[str(x.get("runner_id") or x.get("horse_no")) for x in official.get("runners") or []]
    if set(ids) != {str(x["runner_id"]) for x in prepared["runners"]}:
        raise ValueError("STATIC_OWNER_OFFICIAL_RUNNER_UNIVERSE_MISMATCH")
    if report.get("verified_full_index_count") != len(ids)*20 or report.get("required_index_count") != len(ids)*20:
        raise ValueError("STATIC_OWNER_FULL20_COUNT_MISMATCH")
    owner=compile_static_owner(prepared,source_snapshot_sha256=source["source_snapshot_sha256"],
                               source_receipt_sha256=envelope["receipt_sha256"],
                               frozen_at=now.isoformat(),prediction_cutoff=intent["prediction_cutoff"])
    # Use published popularity only, never odds-derived synthetic probabilities.
    market={str(x.get("runner_id") or x.get("horse_no")):x.get("popularity_rank")
            for x in (source.get("jra_official_race_card_detail") or {}).get("runners") or []}
    if set(market) != set(ids) or {v for v in market.values() if type(v) is int} != set(range(1,len(ids)+1)):
        raise ValueError("STATIC_OWNER_MARKET_BASELINE_INCOMPLETE")
    market_order=sorted(ids,key=lambda rid:market[rid])
    result={"profile":PROFILE,"owner_profile":OWNER_PROFILE,"race_id":intent["race_id"],
            "policy_fingerprint":fingerprint(root),"frozen_at":now.isoformat(),
            "prediction_cutoff":intent["prediction_cutoff"],"scheduled_post_at":intent["scheduled_post_at"],
            "race_date":intent["race_date"],"race_no":intent["race_no"],
            "meeting_key":(intent.get("jra_source") or {}).get("jra_meeting_key"),
            "source_snapshot_sha256":source["source_snapshot_sha256"],"source_receipt_sha256":envelope["receipt_sha256"],
            "owner":owner,"ranking":owner["static_prediction"]["ranking"],"market_ranking":market_order,
            "numeric_provenance_hash":prepared["index_provenance_hash"],
            "full_index_count":owner["full_index_count"],"candidate_only":True,
            "production_authority":False,"purchase_authority":False,"signed_final_issued":False}
    result["sha256"]=sha(result)
    return result


def evaluate(pre, top3, *, result_sha256, observed_at, git_commit_at):
    if pre.get("profile") != PROFILE or pre.get("owner_profile") != OWNER_PROFILE:
        raise ValueError("STATIC_OWNER_WRONG_POLICY_COHORT")
    if pre.get("sha256") != sha({k:v for k,v in pre.items() if k!="sha256"}):
        raise ValueError("STATIC_OWNER_FROZEN_HASH_INVALID")
    if not time(pre["frozen_at"]) <= time(git_commit_at) <= time(pre["prediction_cutoff"]) < time(pre["scheduled_post_at"]) < time(observed_at):
        raise ValueError("STATIC_OWNER_NOT_PROSPECTIVE")
    actual=[str(x) for x in top3]
    if len(actual)!=3 or len(set(actual))!=3 or not set(actual).issubset(pre["ranking"]):
        raise ValueError("STATIC_OWNER_RESULT_UNIVERSE_INVALID")
    if pre.get("production_authority") is not False or pre.get("candidate_only") is not True:
        raise ValueError("STATIC_OWNER_AUTHORITY_LEAK")
    if len(result_sha256)!=64: raise ValueError("STATIC_OWNER_RESULT_HASH_REQUIRED")
    static=[pre["ranking"].index(x)+1 for x in actual]
    market=[pre["market_ranking"].index(x)+1 for x in actual]
    out={"profile":PROFILE,"race_id":pre["race_id"],"policy_fingerprint":pre["policy_fingerprint"],
         "frozen_sha256":pre["sha256"],"official_result_sha256":result_sha256,
         "observed_at":observed_at,"git_commit_at":git_commit_at,"top3":actual,
         "winner_rank_gain":market[0]-static[0],
         "top3_mean_rank_gain":sum(m-s for m,s in zip(market,static))/3,
         "oos_eligible":True,"production_effect":"NONE"}
    out["sha256"]=sha(out); return out


def scorecard(records, *, policy_fingerprint):
    accepted={}; rejected=[]
    for row in records:
        if (row.get("profile")!=PROFILE or row.get("policy_fingerprint")!=policy_fingerprint
                or row.get("oos_eligible") is not True
                or row.get("sha256")!=sha({k:v for k,v in row.items() if k!="sha256"})):
            rejected.append(row.get("race_id")); continue
        rid=row["race_id"]
        if rid in accepted and accepted[rid] != row: raise ValueError("STATIC_OWNER_DUPLICATE_RESULT_CONFLICT")
        accepted[rid]=row
    count=len(accepted)
    return {"profile":PROFILE,"policy_fingerprint":policy_fingerprint,"eligible_settled_races":count,
            "required_forward_races":30,"remaining_forward_races":max(0,30-count),
            "mean_winner_rank_gain":sum(x["winner_rank_gain"] for x in accepted.values())/count if count else None,
            "mean_top3_rank_gain":sum(x["top3_mean_rank_gain"] for x in accepted.values())/count if count else None,
            "rejected_records":rejected,"market_baseline_superiority_proven":False,
            "independent_review_required":True,"production_activation_authorized":False,
            "automatic_promotion":False,"status":"WAITING_FORWARD_OOS" if count<30 else "INDEPENDENT_REVIEW_REQUIRED"}


def save_immutable(path, obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if json.loads(path.read_text()) != obj: raise ValueError("STATIC_OWNER_IMMUTABLE_RECORD_CONFLICT")
        return
    with path.open("x",encoding="utf-8") as stream:
        json.dump(obj,stream,ensure_ascii=False,sort_keys=True,indent=2)


def main():
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest="command",required=True)
    p=sub.add_parser("freeze")
    for name in ("intent","source-envelope","report","output"):p.add_argument("--"+name,required=True)
    sub.add_parser("settle")
    args=parser.parse_args()
    if args.command=="freeze":
        report=json.loads(Path(args.report).read_text())
        if report.get("source_only_full_numerical_ready") is not True:
            print("STATIC_OWNER_FORWARD_NOT_READY_NUMERICAL_EVIDENCE_MISSING");return
        sys.path.insert(0,str(ROOT/"runtime/jra_source_runtime"))
        from verify_source_envelope import verify
        # Independent GitHub OIDC verification is performed by the caller.
        verified=verify(args.source_envelope)
        out=freeze(json.loads(Path(args.intent).read_text()),json.loads(Path(args.source_envelope).read_text()),
                   report,source_verified=verified["valid"])
        save_immutable(args.output,out)
    else:
        from jra_candidate_postresult_closedloop import fetch_jra_result,verify_official_result,PendingOfficialResult
        base=ROOT/"runtime/jra_static_owner_forward_oos"
        for path in sorted(base.glob("*/pre_result.json")):
            result_path=path.with_name("result_evaluation.json")
            if result_path.exists():continue
            pre=json.loads(path.read_text())
            if datetime.now(timezone.utc)<=time(pre["scheduled_post_at"]):continue
            witness=subprocess.check_output(["git","log","-1","--format=%cI","--",str(path.relative_to(ROOT))],cwd=ROOT,text=True).strip()
            if not witness:raise ValueError("STATIC_OWNER_COMMIT_WITNESS_REQUIRED")
            try:
                evidence=fetch_jra_result(pre["race_date"],pre["meeting_key"],pre["race_no"])
                actual=verify_official_result(evidence["parsed"],evidence["text"],pre["ranking"])
                record=evaluate(pre,actual["top3"],result_sha256=evidence["sha256"],observed_at=evidence["captured_at"],git_commit_at=witness)
                save_immutable(result_path,record)
            except PendingOfficialResult as exc:
                print(pre["race_id"],str(exc))
        records=[json.loads(p.read_text()) for p in base.glob("*/result_evaluation.json")]
        out=scorecard(records,policy_fingerprint=fingerprint())
        target=base/"current.json";target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
        print(json.dumps(out))


if __name__=="__main__":main()

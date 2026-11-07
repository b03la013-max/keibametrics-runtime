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
import re
import subprocess
import sys
import time as _clock

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
    paths=("runtime/jra_bvi_failure_attribution.py","runtime/jra_static_owner_executable.py","runtime/jra_bvi_shadow_comparison.py",
           "runtime/jra_owner_authorized_feature_rules.py","runtime/jra_pedigree_corpus.py",
           "mapping/jra_evidence_feature_rule_registry_v1.3_20261010.json",
           "runtime/jra_official_fact_evaluator_production.py",
           "runtime/jra_source_to_evidence_features.py","runtime/jra_source_runtime/jra_observed_context.py",
           "runtime/jra_source_runtime/jra_current_environment.py",
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
    if all(isinstance(r.get("evidence_features"),dict) and r.get("career_starts") is not None
           for r in prepared["runners"]):
        from jra_bvi_shadow_comparison import compare
        mapping=json.loads((Path(root)/"mapping/jra_base_index_evidence_mapping_v1.0_20260921.json").read_text())
        comparison_request = dict(intent)
        comparison_request.update(prepared)
        result["pedigree_comparison"] = compare(comparison_request, mapping,
            source_sha=source["source_snapshot_sha256"], receipt_sha=envelope["receipt_sha256"],
            algorithm_freeze_at=now.isoformat(), cutoff=intent["prediction_cutoff"])
        result["pedigree_comparison"]["status"] = "FROZEN_UNKNOWN_FUTURE_SHADOW / B_EQUALS_A_UNTIL_DISTINCT_INPUT"
    else:
        result["pedigree_comparison"] = {"status":"BLOCKED_FEATURE_LEDGER_UNAVAILABLE",
            "production_effect":"NONE", "oos_eligible":False}
    result["sha256"]=sha(result)
    return result


def _verify_frozen_before_result(pre, *, observed_at, git_commit_at):
    if pre.get("profile") != PROFILE or pre.get("owner_profile") != OWNER_PROFILE:
        raise ValueError("STATIC_OWNER_WRONG_POLICY_COHORT")
    if pre.get("sha256") != sha({k:v for k,v in pre.items() if k!="sha256"}):
        raise ValueError("STATIC_OWNER_FROZEN_HASH_INVALID")
    if not time(pre["frozen_at"]) <= time(git_commit_at) <= time(pre["prediction_cutoff"]) < time(pre["scheduled_post_at"]) < time(observed_at):
        raise ValueError("STATIC_OWNER_NOT_PROSPECTIVE")
    if pre.get("production_authority") is not False or pre.get("candidate_only") is not True:
        raise ValueError("STATIC_OWNER_AUTHORITY_LEAK")


def evaluate(pre, top3, *, result_sha256, observed_at, git_commit_at):
    _verify_frozen_before_result(pre, observed_at=observed_at, git_commit_at=git_commit_at)
    actual=[str(x) for x in top3]
    if len(actual)!=3 or len(set(actual))!=3 or not set(actual).issubset(pre["ranking"]):
        raise ValueError("STATIC_OWNER_RESULT_UNIVERSE_INVALID")
    if len(result_sha256)!=64: raise ValueError("STATIC_OWNER_RESULT_HASH_REQUIRED")
    static=[pre["ranking"].index(x)+1 for x in actual]
    market=[pre["market_ranking"].index(x)+1 for x in actual]
    out={"profile":PROFILE,"race_id":pre["race_id"],"policy_fingerprint":pre["policy_fingerprint"],
         "frozen_sha256":pre["sha256"],"official_result_sha256":result_sha256,
         "observed_at":observed_at,"git_commit_at":git_commit_at,"top3":actual,
         "winner_rank_gain":market[0]-static[0],
         "top3_mean_rank_gain":sum(m-s for m,s in zip(market,static))/3,
         "oos_eligible":True,"production_effect":"NONE"}
    comparison = pre.get("pedigree_comparison") or {}
    arms = comparison.get("arms") or {}
    if arms:
        measured = {}
        for name, arm in arms.items():
            owner = arm["owner"]
            ranking = owner["static_prediction"]["ranking"]
            columns = owner["active_columns"]
            candidates = set().union(*(set(x) for x in columns.values()))
            measured[name] = {
                "winner_rank": ranking.index(actual[0]) + 1,
                "winner_discovery_recall": int(actual[0] in columns["W"]),
                "p2_capture": actual[1] in columns["P2"],
                "p3_capture": actual[2] in columns["P3"],
                "top3_mean_rank": sum(ranking.index(x)+1 for x in actual)/3,
                "ordered_pair_capture": any((x["head"],x["second"]) == tuple(actual[:2])
                    for x in owner["pair_dispositions"]),
                "exact_semantic_capture": any((x["head"],x["second"],x["third"]) == tuple(actual)
                    for x in owner["third_dispositions"]),
                "candidate_width": len(candidates),
                "false_positive_candidates": len(candidates-set(actual)),
                "low_popularity_top3_discovered": [x for x in actual if x in candidates
                    and pre["market_ranking"].index(x)+1 >= 6],
                "krs_input_changed_vs_current": arm["krs_input"] != arms["A_CURRENT"]["krs_input"],
                "krs_result_utility": None, "ticket_count": None, "capital_required": None,
                "investment_weighted_pfs": None, "robust_pfs": None,
                "downstream_blocker": "SHADOW_KRS_MEC_SETTLEMENT_NOT_EXECUTED",
            }
        out["pedigree_arm_metrics"] = measured
        out["pedigree_enhanced_input_distinct"] = comparison["enhanced_input_distinct"]
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


def settle_pending(root=ROOT, *, now=None, fetch=None, budget_seconds=None, monotonic=None):
    from jra_candidate_postresult_closedloop import (fetch_jra_result,verify_official_result,
        PendingOfficialResult,validate_result_target)
    from jra_postresult_health import build_execution_health,failure_row
    root=Path(root);base=root/"runtime/jra_static_owner_forward_oos"
    now=now or datetime.now(timezone.utc)
    if budget_seconds is not None and budget_seconds<0:
        raise ValueError('STATIC_OWNER_EXECUTION_BUDGET_INVALID')
    clock=monotonic or _clock.monotonic
    started=clock()
    rows=[];records=[]
    # Include orphan results in diagnostics, never silently qualify them.
    def routing_priority(path):
        # The canonical ID date orders existing work only. It never fills a
        # missing post/cutoff or qualifies the underlying Frozen evidence.
        match=re.fullmatch(r'KM-JRA-[A-Z]{3}-(\d{8})-R\d{2}',path.parent.name)
        try:
            day=datetime.strptime(match[1],'%Y%m%d') if match else None
        except ValueError:
            day=None
        return (-int(day.strftime('%Y%m%d')) if day else 0,str(path))
    paths=sorted(set(base.glob("*/pre_result.json")) |
                 {p.with_name('pre_result.json') for p in base.glob('*/result_evaluation.json')},
                 key=routing_priority)
    for path in paths:
        rid=path.parent.name;stage='READ_FROZEN_PRE_RESULT'
        refs={'pre_result_ref':path.relative_to(root).as_posix(),
              'frozen_pre_result_sha256':None,'source_ref':None,'final_ref':None}
        try:
            pre=json.loads(path.read_text())
            refs.update(frozen_pre_result_sha256=pre.get('sha256'),
                frozen_file_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                source_ref=pre.get('source_snapshot_sha256'),
                final_ref=pre.get('final_receipt_sha256'))
            stage='VERIFY_FROZEN_IDENTITY'
            if pre.get('race_id')!=rid:raise ValueError('STATIC_OWNER_FROZEN_RACE_ID_MISMATCH')
            if now<=time(pre['scheduled_post_at']):
                rows.append(dict(refs,race_id=rid,status='RESULT_NOT_YET_DUE',persisted=False))
                continue
            stage='VERIFY_GIT_COMMIT_WITNESS'
            witness=subprocess.check_output(['git','log','-1','--format=%cI','--',
                str(path.relative_to(root))],cwd=root,text=True).strip()
            if not witness:raise ValueError('STATIC_OWNER_COMMIT_WITNESS_REQUIRED')
            stage='VERIFY_FROZEN_BEFORE_HTTP'
            _verify_frozen_before_result(pre,observed_at=now.isoformat(),git_commit_at=witness)
            stage='VERIFY_RESULT_TARGET'
            validate_result_target(rid,pre['race_date'],pre['meeting_key'],pre['race_no'])
            result_path=path.with_name('result_evaluation.json')
            if result_path.exists():
                stage='VERIFY_EXISTING_IMMUTABLE_RESULT'
                record=json.loads(result_path.read_text())
                if (record.get('race_id')!=rid or record.get('profile')!=PROFILE
                        or record.get('policy_fingerprint')!=pre['policy_fingerprint']
                        or record.get('oos_eligible') is not True
                        or record.get('frozen_sha256')!=pre['sha256']
                        or record.get('sha256')!=sha({k:v for k,v in record.items() if k!='sha256'})):
                    raise ValueError('STATIC_OWNER_IMMUTABLE_RESULT_BINDING_INVALID')
                records.append(record)
                rows.append(dict(refs,race_id=rid,status='ALREADY_SETTLED',persisted=True,
                    result_sha256=record['sha256']))
                continue
            stage='FETCH_OFFICIAL_RESULT'
            if budget_seconds is not None and clock()-started>=budget_seconds:
                rows.append(dict(refs,race_id=rid,status='NOT_RUN_BUDGET',persisted=False,
                    first_not_executed_stage=stage,resume_condition='NEXT_EXISTING_SCHEDULE',
                    recommendation_pfs=None))
                continue
            evidence=(fetch or fetch_jra_result)(pre['race_date'],pre['meeting_key'],pre['race_no'])
            stage='VERIFY_OFFICIAL_RESULT'
            actual=verify_official_result(evidence['parsed'],evidence['text'],pre['ranking'])
            stage='EVALUATE_STATIC_OWNER_RESULT'
            if actual.get('dead_heat') is True or len(actual.get('top3_orders') or [])>1:
                # This existing metric contract accepts one ordered top3 only.
                # Do not select an arbitrary tied order and issue OOS credit.
                # Production's separate full-payout settlement remains usable.
                rows.append(dict(refs,race_id=rid,status='NOT_ELIGIBLE',persisted=False,
                    first_failed_stage=stage,error_code='STATIC_OWNER_DEAD_HEAT_METRICS_UNSUPPORTED',
                    official_result_state='VERIFIED_DEAD_HEAT_METRICS_UNSUPPORTED',
                    official_result_sha256=evidence['sha256'],oos_eligible=False,
                    recommendation_pfs=None))
                continue
            record=evaluate(pre,actual['top3'],result_sha256=evidence['sha256'],
                observed_at=evidence['captured_at'],git_commit_at=witness)
            stage='SAVE_IMMUTABLE_RESULT'
            save_immutable(result_path,record)
            records.append(record)
            rows.append(dict(refs,race_id=rid,status='SETTLED',persisted=True,
                result_sha256=record['sha256'],official_result_state='VERIFIED'))
        except PendingOfficialResult as exc:
            rows.append(dict(refs,race_id=rid,status='PENDING_OFFICIAL_RESULT',persisted=False,
                first_failed_stage=stage,exception_class=type(exc).__name__,error_code=str(exc),
                recommendation_pfs=None))
        except Exception as exc:
            if str(exc) in ('STATIC_OWNER_WRONG_POLICY_COHORT','STATIC_OWNER_NOT_PROSPECTIVE'):
                rows.append(dict(refs,race_id=rid,status='NOT_ELIGIBLE',persisted=False,
                    first_failed_stage=stage,error_code=str(exc),exception_class=type(exc).__name__,
                    recommendation_pfs=None))
            else:
                rows.append(failure_row(rid,exc,stage,**refs))
    # Existing scorecard rules retain their policy/cohort and no-promotion gates.
    card=scorecard(records,policy_fingerprint=fingerprint(root))
    target=base/'current.json';target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(card,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    health=build_execution_health('STATIC_OWNER',rows,observed_at=now.isoformat())
    health['execution_budget_seconds']=budget_seconds
    health['execution_budget_exhausted']=any(row['status']=='NOT_RUN_BUDGET' for row in rows)
    health['scorecard']=card
    return health


def main(argv=None):
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest="command",required=True)
    p=sub.add_parser("freeze")
    for name in ("intent","source-envelope","report","output"):p.add_argument("--"+name,required=True)
    settle_parser=sub.add_parser("settle")
    settle_parser.add_argument('--repo-root',default=str(ROOT))
    settle_parser.add_argument('--health-out')
    settle_parser.add_argument('--budget-seconds',type=float,default=180)
    args=parser.parse_args(argv)
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
        from jra_postresult_health import write_execution_health,health_exit_code
        root=Path(args.repo_root).resolve()
        out=settle_pending(root,budget_seconds=args.budget_seconds)
        target=args.health_out or root/'runtime/jra_static_owner_forward_oos/settlement_health.json'
        out=write_execution_health(target,out)
        print(json.dumps(out,ensure_ascii=False))
        return health_exit_code(out)


if __name__=="__main__":raise SystemExit(main())

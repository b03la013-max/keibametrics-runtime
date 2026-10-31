"""JRA verified zero-bet result settlement and post-result learning.

A blocked Production Full20 can legitimately terminate NO_BET, not a
fabricated Final. This module closes the zero-exposure result branch
without counting it as a prediction or capital/PFS sample.
"""
from __future__ import annotations
from datetime import datetime
from hashlib import sha256
from copy import deepcopy
from pathlib import Path
import json
import re
import subprocess
from jra_production_no_bet_terminal import verify_no_bet_terminal

PROFILE = "KM-JRA-NO-BET-POSTRESULT-LEARNING-v1-20261010"

class JRANoBetLearningError(ValueError):
    pass

def _hash(obj):
    return sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()

def _time(value):
    try:
        d=datetime.fromisoformat(str(value).replace("Z","+00:00"))
        return d if d.tzinfo is not None else None
    except (TypeError,ValueError):
        return None

def select_no_bet_paths(directory, race_id=""):
    """An optional manual selector narrows the existing worker, never expands it."""
    if race_id is None:race_id=""
    if not isinstance(race_id,str):
        raise JRANoBetLearningError("NO_BET_SELECTOR_INVALID")
    if race_id:
        match=re.fullmatch(r"KM-JRA-([A-Z]{3})-(\d{8})-R(0[1-9]|1[0-2])",race_id)
        from jra_source_runtime.jra_race_day_resolver import VENUES
        if not match or match[1] not in {v[0] for v in VENUES.values()}:
            raise JRANoBetLearningError("NO_BET_SELECTOR_INVALID")
        try:datetime.strptime(match[2],"%Y%m%d")
        except ValueError as exc:raise JRANoBetLearningError("NO_BET_SELECTOR_INVALID") from exc
    paths=sorted(p for p in Path(directory).glob("*.json")
                 if not race_id or p.name.startswith(race_id+"-"))
    if race_id and len(paths)>1:
        raise JRANoBetLearningError("NO_BET_SELECTOR_AMBIGUOUS_EXECUTION")
    return paths


def verify_no_bet_oidc(path,*,kind,not_before,not_after,source_digest=None):
    """Call the existing verifier under the established workflow/main trust.

    A past Terminal's code comes from its cryptographically verified
    certificate, never from SOURCE's different Run or a caller's verified flag.
    """
    repository="b03la013-max/keibametrics-runtime"
    workflows={"capture":"km-jra-no-bet-postresult-learning.yml",
               "terminal":"km-jra-formal-single-entry.yml"}
    if kind not in workflows or (kind=="capture" and source_digest is None):
        raise JRANoBetLearningError("NO_BET_OIDC_ORIGIN_REQUIRED")
    if source_digest is not None and not re.fullmatch(r"[0-9a-f]{40}",str(source_digest)):
        raise JRANoBetLearningError("NO_BET_OIDC_CODE_REQUIRED")
    path=Path(path);before=sha256(path.read_bytes()).hexdigest()
    command=["gh","attestation","verify",str(path),"--repo",repository,
             "--signer-workflow",repository+"/.github/workflows/"+workflows[kind],
             "--source-ref","refs/heads/main","--deny-self-hosted-runners","--format","json"]
    if source_digest is not None:command.extend(["--source-digest",source_digest])
    verified=subprocess.run(command,check=True,capture_output=True,text=True,timeout=60)
    values=json.loads(verified.stdout)
    start,finish=_time(not_before),_time(not_after)
    if not isinstance(values,list) or not start or not finish or start>finish:
        raise JRANoBetLearningError("NO_BET_OIDC_ORIGIN_OR_WITNESS_UNKNOWN")
    for value in values:
        if not isinstance(value,dict):continue
        result=value.get("verificationResult") or {}
        certificate=(result.get("signature") or {}).get("certificate") or {}
        code=certificate.get("sourceRepositoryDigest")
        statement=result.get("statement") or {}
        times=[_time(t.get("timestamp") or t.get("time"))
               for t in result.get("verifiedTimestamps") or [] if isinstance(t,dict)]
        witnessed=[t for t in times if t is not None and start<=t<=finish]
        if (certificate.get("issuer")=="https://token.actions.githubusercontent.com"
                and certificate.get("subjectAlternativeName")=="https://github.com/"+repository+"/.github/workflows/"+workflows[kind]+"@refs/heads/main"
                and certificate.get("sourceRepositoryRef")=="refs/heads/main"
                and certificate.get("runnerEnvironment")=="github-hosted"
                and re.fullmatch(r"[0-9a-f]{40}",str(code))
                and (source_digest is None or code==source_digest)
                and witnessed
                and any((s.get("digest") or {}).get("sha256")==before
                        for s in statement.get("subject") or [] if isinstance(s,dict))):
            if sha256(path.read_bytes()).hexdigest()!=before:
                raise JRANoBetLearningError("NO_BET_OIDC_ARTIFACT_CHANGED")
            return {"artifact_file_sha256":before,"workflow":workflows[kind],
                    "repository":repository,"source_ref":"refs/heads/main","source_digest":code,
                    "run_invocation_uri":certificate.get("runInvocationURI"),
                    "verified_timestamp":min(witnessed).isoformat(),"statement_sha256":_hash(statement)}
    raise JRANoBetLearningError("NO_BET_OIDC_ORIGIN_OR_WITNESS_UNKNOWN")

def build_no_bet_learning(terminal,official_result,*,race_no,acquired_at,
                          result_source_snapshot_sha256,official_capture_verified=False,
                          scheduled_post_at=None):
    """Zero investment and payout are recorded; PFS is undefined, not 100%.
    
    The external caller must independently verify the official JRA raw source
    and its GitHub OIDC artifact attestation before setting the verified flag.
    """
    if official_capture_verified is not True:
        raise JRANoBetLearningError("OFFICIAL_POSTRESULT_CAPTURE_NOT_VERIFIED")
    try:
        decision=verify_no_bet_terminal(terminal,require_live=True)
    except ValueError as exc:
        raise JRANoBetLearningError("NO_BET_TERMINAL_INVALID:"+str(exc)) from exc
    if not (isinstance(official_result,dict)
            and official_result.get("official") is True
            and official_result.get("result_derived") is True
            and type(race_no) is int and 1<=race_no<=12
            and str(terminal.get("race_id") or "").endswith(f"-R{race_no:02d}")
            and official_result.get("race_no") == race_no):
        raise JRANoBetLearningError("OFFICIAL_RESULT_IDENTITY_INVALID")
    if not (isinstance(result_source_snapshot_sha256,str)
            and len(result_source_snapshot_sha256)==64
            and all(c in "0123456789abcdef" for c in result_source_snapshot_sha256)
            and official_result.get("source_snapshot_sha256")==result_source_snapshot_sha256):
        raise JRANoBetLearningError("OFFICIAL_RESULT_SNAPSHOT_UNBOUND")
    announced=official_result.get("sha256")
    raw_parsed={k:v for k,v in official_result.items()
                if k not in ("sha256","race_no","source_snapshot_sha256")}
    if not announced or announced!=_hash(raw_parsed):
        raise JRANoBetLearningError("OFFICIAL_RESULT_CONTENT_HASH_INVALID")
    taken=_time(acquired_at)
    decided=_time(terminal.get("created_at"))
    post=_time(terminal.get("scheduled_post_at") or scheduled_post_at)
    if (not taken or not decided or taken<=decided
            or (post is not None and taken<=post)):
        raise JRANoBetLearningError("POSTRESULT_CHRONOLOGY_INVALID")
    results=official_result.get("runners")
    if not isinstance(results,list) or len(results)<3:
        raise JRANoBetLearningError("OFFICIAL_RESULT_UNIVERSE_INVALID")
    seen=set()
    finish_rows=[]
    for row in results:
        if not isinstance(row,dict):
            raise JRANoBetLearningError("OFFICIAL_RESULT_ROW_BAD")
        rid=str(row.get("runner_id") or "")
        pos=row.get("finish")
        if not rid or rid in seen or rid not in terminal["index_universe"]:
            raise JRANoBetLearningError("OFFICIAL_RESULT_RUNNER_MISMATCH")
        if type(pos) is not int or pos<1:
            raise JRANoBetLearningError("OFFICIAL_RESULT_FINISH_INVALID")
        # Older official result rows carry only the already universe-bound
        # runner ID. Build a local view; the hash-checked source stays intact.
        try:
            horse_no=int(rid)
        except ValueError as exc:
            raise JRANoBetLearningError("OFFICIAL_RESULT_HORSE_NUMBER_INVALID") from exc
        if str(horse_no)!=rid or not 1<=horse_no<=18:
            raise JRANoBetLearningError("OFFICIAL_RESULT_HORSE_NUMBER_INVALID")
        if "horse_no" in row and (type(row["horse_no"]) is not int or row["horse_no"]!=horse_no):
            raise JRANoBetLearningError("OFFICIAL_RESULT_HORSE_NUMBER_MISMATCH")
        finish_rows.append({**row,"horse_no":horse_no})
        seen.add(rid)
    non_finishers=official_result.get("non_finishers",[])
    if not isinstance(non_finishers,list):
        raise JRANoBetLearningError("OFFICIAL_RESULT_NON_FINISHERS_INVALID")
    for row in non_finishers:
        if not isinstance(row,dict):
            raise JRANoBetLearningError("OFFICIAL_RESULT_ROW_BAD")
        rid=str(row.get("runner_id") or "")
        if not rid or rid in seen or rid not in terminal["index_universe"]:
            raise JRANoBetLearningError("OFFICIAL_RESULT_RUNNER_MISMATCH")
        if row.get("finish_status") not in ("CANCELLED","EXCLUDED","DID_NOT_FINISH","DISQUALIFIED"):
            raise JRANoBetLearningError("OFFICIAL_RESULT_NON_FINISHER_STATUS_INVALID")
        try:
            horse_no=int(rid)
        except ValueError as exc:
            raise JRANoBetLearningError("OFFICIAL_RESULT_HORSE_NUMBER_INVALID") from exc
        if str(horse_no)!=rid or not 1<=horse_no<=18:
            raise JRANoBetLearningError("OFFICIAL_RESULT_HORSE_NUMBER_INVALID")
        if "horse_no" in row and (type(row["horse_no"]) is not int or row["horse_no"]!=horse_no):
            raise JRANoBetLearningError("OFFICIAL_RESULT_HORSE_NUMBER_MISMATCH")
        seen.add(rid)
    if seen!=set(terminal["index_universe"]):
        raise JRANoBetLearningError("OFFICIAL_RESULT_UNIVERSE_INCOMPLETE")
    from jra_source_runtime.jra_same_day_results import finish_groups_and_top3_orders
    try:
        grouped=finish_groups_and_top3_orders(finish_rows)
    except ValueError as exc:
        raise JRANoBetLearningError("OFFICIAL_TOP3_INCOMPLETE:"+str(exc)) from exc
    top3=list(map(str,grouped["top3_orders"][0]))
    obj={
        "profile":PROFILE,
        "race_id":terminal["race_id"],
        "family_id":"JRA",
        "decision_lineage_sha256":terminal["sha256"],
        "signed_pre_race_source_receipt_sha256":terminal["signed_source_receipt_sha256"],
        "post_race_official_snapshot_sha256":result_source_snapshot_sha256,
        "post_race_official_detail_sha256":announced,
        "post_race_official_acquired_at":taken.isoformat(),
        "official_top3":top3,
        "official_finish_count":len(results),
        "official_non_finisher_count":len(non_finishers),
        "official_runner_universe_count":len(seen),
        "decision":"NO_BET",
        "reason":terminal["decision_reason"],
        "status":"ZERO_EXPOSURE_RESULT_RECORDED",
        "final_prediction_existed":False,
        "pre_krs_executed":False,
        "krs_executed":False,
        "signed_final_verified":False,
        "ticket_count":0,
        "investment":0,
        "payout":0,
        "profit_loss":0,
        "pfs":None,
        "eligible_for_production_prediction_kpi":False,
        "eligible_for_market_superiority_promotion":False,
        "learning_class":("AKI_POSITIVE_EVIDENCE_AND_OPPORTUNITY_COST_ONLY"
                          if str(terminal.get("decision_reason") or "").startswith("AKI_")
                          else "EVIDENCE_AVAILABILITY_AND_OPPORTUNITY_COST_ONLY"),
        "first_blocked_stage":terminal.get("first_blocked_stage"),
        "terminal_index_count":decision["terminal_index_count"],
        "base_calculated_count":decision["calculated_base_count"],
        "base_held_count":decision["held_base_count"],
        "derived_held_count":decision["held_derived_count"],
        "production_effect":"NONE",
    }
    if grouped["dead_heat"]:
        obj.update(official_top3_orders=grouped["top3_orders"],
                   official_finish_groups=grouped["finish_groups"],
                   official_top3_is_legacy_representative=True)
    obj["sha256"]=_hash(obj)
    return obj


def build_no_bet_review_state(terminal,learning,*,effective_time,official_capture_verified=False):
    """Project the verified zero-exposure branch without inventing a FINAL.

    The producer retains its existing SOURCE/terminal and capture OIDC checks.
    The shared State builder admits only candidate Shadow context; it grants
    neither numeric Production learning nor prediction/PFS sample eligibility.
    """
    if official_capture_verified is not True:
        raise JRANoBetLearningError("OFFICIAL_POSTRESULT_CAPTURE_NOT_VERIFIED")
    decision=verify_no_bet_terminal(terminal,require_live=True)
    if (not isinstance(learning,dict)
            or learning.get("profile")!=PROFILE or learning.get("family_id")!="JRA"
            or learning.get("sha256")!=_hash({k:v for k,v in learning.items() if k!="sha256"})
            or learning.get("race_id")!=terminal.get("race_id")
            or learning.get("decision_lineage_sha256")!=terminal.get("sha256")
            or learning.get("signed_pre_race_source_receipt_sha256")!=terminal.get("signed_source_receipt_sha256")
            or learning.get("status")!="ZERO_EXPOSURE_RESULT_RECORDED"
            or learning.get("decision")!="NO_BET" or learning.get("reason")!=terminal.get("decision_reason")
            or learning.get("production_effect")!="NONE"
            or any(type(learning.get(k)) is not int or learning[k]!=0
                   for k in ("ticket_count","investment","payout","profit_loss"))
            or learning.get("pfs") is not None
            or any(learning.get(k) is not False for k in
                   ("final_prediction_existed","signed_final_verified","pre_krs_executed","krs_executed",
                    "eligible_for_production_prediction_kpi","eligible_for_market_superiority_promotion"))):
        raise JRANoBetLearningError("NO_BET_PROJECTION_BINDING_INVALID")
    top3=learning.get("official_top3")
    if (not isinstance(top3,list) or len(top3)!=3 or len(set(map(str,top3)))!=3
            or not set(map(str,top3))<=set(terminal["index_universe"])):
        raise JRANoBetLearningError("NO_BET_PROJECTION_TOP3_INVALID")
    acquired=_time(learning.get("post_race_official_acquired_at"));effective=_time(effective_time)
    if not acquired or not effective or effective<acquired:
        raise JRANoBetLearningError("NO_BET_PROJECTION_EFFECTIVE_TIME_INVALID")
    from post_result_learning import LEARNING_PROFILE,build_learning_state
    from family_pfs_improvement import build_pfs_improvement_assessment
    review={
        "profile":LEARNING_PROFILE,"race_id":terminal["race_id"],
        "formal_grade":decision["status"],"decision":"NO_BET",
        "source_no_bet_result_sha256":learning["sha256"],
        "source_no_bet_terminal_sha256":terminal["sha256"],
        "official_top3":[int(x) for x in top3],
        "source_evidence":{
            "signed_pre_race_source_receipt_sha256":learning["signed_pre_race_source_receipt_sha256"],
            "official_snapshot_sha256":learning["post_race_official_snapshot_sha256"],
            "official_detail_sha256":learning["post_race_official_detail_sha256"],
            "acquired_at":learning["post_race_official_acquired_at"],
        },
        "prediction":{"status":"NOT_APPLICABLE_ZERO_EXPOSURE","role_capture":{}},
        "conversion":{"status":"NOT_APPLICABLE_ZERO_EXPOSURE","ticket_count":0,"investment":0},
        "capital":{"status":"NOT_APPLICABLE_ZERO_EXPOSURE","authority":"ZERO_EXPOSURE_NO_BET",
                   "settlement_status":"ZERO_EXPOSURE_RESULT_RECORDED","investment":0,
                   "settled_investment":0,"return":0,"profit_loss":0,"pfs":None,
                   "pfs_status":"NOT_APPLICABLE_ZERO_EXPOSURE","hit":False,"hit_but_loss":False},
        "failure_localization":{"first_material_failure":"NONE","no_bet_reason":learning["reason"],
                                "prediction_quality_assessment":"NOT_PERFORMED_WITHOUT_SIGNED_FINAL"},
        "final_prediction_existed":False,"signed_final_verified":False,
        "eligible_for_production_prediction_kpi":False,"eligible_for_market_superiority_promotion":False,
        "production_change_authorized":False,"prequential_only":True,
    }
    if "official_oidc_proofs" in learning:
        review["source_evidence"]["official_oidc_proofs"]=deepcopy(learning["official_oidc_proofs"])
    if learning.get("official_top3_orders") is not None:
        for key in ("official_top3_orders","official_finish_groups","official_top3_is_legacy_representative"):
            review[key]=deepcopy(learning[key])
    review["pfs_improvement"]=build_pfs_improvement_assessment(review)
    review["sha256"]=_hash(review)
    state=build_learning_state(review,effective_time=effective.isoformat())
    state.update(source_no_bet_result_sha256=learning["sha256"],
                 source_no_bet_terminal_sha256=terminal["sha256"],
                 eligible_for_production_prediction_kpi=False,
                 numeric_production_learning_consumption="NOT_ESTABLISHED")
    state["reference_metrics"].update(no_bet_reason=learning["reason"],zero_exposure=True,
                                      learning_class=learning["learning_class"])
    state["sha256"]=_hash({k:v for k,v in state.items() if k!="sha256"})
    return {"review":review,"state":state}


def persist_no_bet_review_state(root,terminal,learning,*,execution_id,effective_time,
                               official_capture_verified=False):
    """Append original zero-bet data and its Review/State using the existing writer."""
    race_id=terminal.get("race_id") or ""
    if (not isinstance(execution_id,str) or not execution_id.startswith(race_id+"-")
            or not re.fullmatch(r"[A-Za-z0-9_.-]+",execution_id)
            or terminal.get("source_execution_id") not in (None,execution_id)):
        raise JRANoBetLearningError("NO_BET_PROJECTION_EXECUTION_MISMATCH")
    root=Path(root)
    require_no_bet_final_absent(root,[race_id])
    state_path=root/"runtime/learning_states"/(race_id+".json")
    # A repeated readback keeps the first actual publication time. Never
    # backdate a missing State from capture time or trust an arbitrary old one:
    # rebuilding below must reproduce every existing field and its digest.
    if state_path.is_symlink():
        raise JRANoBetLearningError("NO_BET_PROJECTION_IMMUTABLE_CONFLICT")
    if state_path.exists():
        old=json.loads(state_path.read_text())
        original_time=_time(old.get("effective_time")) if isinstance(old,dict) else None
        requested_time=_time(effective_time)
        if not original_time or not requested_time or requested_time<original_time:
            raise JRANoBetLearningError("NO_BET_PROJECTION_EFFECTIVE_TIME_INVALID")
        effective_time=original_time.isoformat()
    projection=build_no_bet_review_state(terminal,learning,effective_time=effective_time,
                                        official_capture_verified=official_capture_verified)
    files={root/"runtime/jra_no_bet_learning"/(execution_id+".json"):learning,
           root/"runtime/reviews_auto"/(race_id+"-AUTO.json"):projection["review"],
           root/"runtime/learning_states"/(race_id+".json"):projection["state"]}
    from execution_store import require_public_storage
    for path,value in files.items():
        require_public_storage(value)
        if path.is_symlink() or (path.exists() and json.loads(path.read_text())!=value):
            raise JRANoBetLearningError("NO_BET_PROJECTION_IMMUTABLE_CONFLICT")
    from jra_shadow_checkpoint import write_once
    try:
        for path,value in files.items():write_once(path,value)
    except (OSError,ValueError) as exc:
        # A partial local addition must never reach the workflow's broad git
        # add through its per-Race validation-error isolation.
        raise RuntimeError("NO_BET_PROJECTION_CANONICAL_WRITE_FAILED") from exc
    return projection


def require_no_bet_final_absent(root,race_ids):
    """Reapply the same branch guard after rebase, immediately before push."""
    for race_id in race_ids:
        if (not isinstance(race_id,str)
                or not re.fullmatch(r"KM-JRA-[A-Z]{3}-\d{8}-R(0[1-9]|1[0-2])",race_id)):
            raise JRANoBetLearningError("NO_BET_PROJECTION_RACE_INVALID")
        path=Path(root)/"runtime/final_artifacts"/(race_id+".json")
        if path.exists() or path.is_symlink():
            raise JRANoBetLearningError("NO_BET_PROJECTION_SIGNED_FINAL_BRANCH_EXISTS")

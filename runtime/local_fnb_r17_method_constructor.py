"""FNB R17: construct six *alternative* tickets from verified frozen Owner semantics.

P0 root cause fix: R14 previously ONLY audited caller-supplied method tickets.
This module uses the EXISTING Common MEC builder, existing Capital Policy and
existing Canonical Ticket Tree renderer to generate the 2×3 method portfolios
from the already frozen distinct B/C Role/Pair/Third requests.

It does NOT infer owner roles from third-party rankings or KRS SSR. All owner
snapshots must already be frozen, each bound to numeric SHA, active IDs,
and already executed private KRS (5000 seed1) with real-byte output SHA.
Unformed owner semantic sources are HOLD, not computed NO-BET.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib,json
from pathlib import Path

from runtime.minimum_efficient_coverage import build_mec_plan,validate_mec_plan
from runtime.capital_policy import resolve_capital_policy
from runtime.jra_ticket_tree_renderer import render_ticket_tree
from runtime.local_fnb_r9_method_audit import audit_methods
from runtime.local_fnb_r14_private_dual_krs import OWNERS

METHODS=("EXACTA","TRIO","TRIFECTA")
PROFILE="KM-FNB-R17-FROZEN-COMMON-MEC-SIX-METHOD-TICKET-CONSTRUCTION-v1"

def sha(data):
    return hashlib.sha256(json.dumps(data,ensure_ascii=False,
                       sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

def _validate_owner(owner,req,expected_race,active,source_sha,numeric_sha,krs_receipt,private_root):
    if not isinstance(req,dict) or req.get("owner")!=owner:
        raise ValueError("FNB_R17_FROZEN_OWNER_SEMANTIC_MISSING:"+owner)
    if (req.get("race_id")!=expected_race or
            req.get("family_id")!="LOCAL" or
            req.get("venue_id")!="FNB" or
            req.get("classification")!="PRIVATE_NONPRODUCTION_FIXED_OWNER"):
        raise ValueError("FNB_R17_OWNER_RACE_OR_SCOPE_MISMATCH:"+owner)
    if (req.get("numerical_materialization_sha256")!=numeric_sha
            or req.get("source_snapshot_sha256")!=source_sha):
        raise ValueError("FNB_R17_OWNER_SOURCE_NUMERIC_FREEZE_NOT_BOUND:"+owner)
    model_sha=req.get("original_prediction_sha256")
    if not isinstance(model_sha,str) or len(model_sha)!=64:
        raise ValueError("FNB_R17_OWNER_FROZEN_MODEL_SHA_MISSING:"+owner)
    if not isinstance(req.get("role_registry"),list):
        raise ValueError("FNB_R17_ROLE_REGISTRY_NOT_FROZEN:"+owner)
    role_ids={str(row.get("runner_id")) for row in req["role_registry"]
              if isinstance(row,dict)}
    if role_ids!={str(v) for v in active}:
        raise ValueError("FNB_R17_FROZEN_ROLE_FULL_ACTIVE_SET_MISMATCH:"+owner)
    for key in ("pair_dispositions","third_dispositions"):
        if not isinstance(req.get(key),list):
            raise ValueError("FNB_R17_SEMANTIC_"+key+"_MISSING:"+owner)
        # Only frozen material/structural terminals can enter the existing
        # Common consumer. Candidate possibilities cannot become a six-method
        # computed NO-BET merely because the consumer selected no tickets.
        if any(not isinstance(row,dict) or row.get("status") not in
                {"PURCHASE","PROTECT","EXCLUDE","SEMANTIC_ONLY"} for row in req[key]):
            raise ValueError("FNB_R17_UNRESOLVED_SEMANTIC_SELECTION:"+owner+":"+key)
    if any(any(marker in str(row.get("status") or "").upper()
               for marker in ("UNKNOWN","UNRESOLVED","UNADOPTED","PENDING"))
            for row in req["role_registry"]):
        raise ValueError("FNB_R17_UNRESOLVED_ROLE_SELECTION:"+owner)
    if (not isinstance(krs_receipt,dict) or
            krs_receipt.get("owner")!=owner or
            krs_receipt.get("source_original_prediction_sha256")!=model_sha or
            krs_receipt.get("actual_krs_runs")!=5000 or
            krs_receipt.get("actual_master_seed")!=1):
        raise ValueError("FNB_R17_OWNER_ACTUAL_KRS_5K_SEED1_MISSING:"+owner)
    output_name=owner+"_krs_output.json"
    recorded=Path(private_root)/expected_race/output_name
    if not recorded.is_file() or hashlib.sha256(recorded.read_bytes()).hexdigest()!=(
            krs_receipt.get("actual_output_sha256")):
        raise ValueError("FNB_R17_OWNER_KRS_REAL_OUTPUT_BYTES_NOT_VERIFIED:"+owner)
    return model_sha

def construct(*,race_id,owner_semantics,private_root,dual_krs_manifest,
              source_snapshot_sha256,numerical_materialization_sha256):
    if not isinstance(race_id,str) or not race_id.startswith("KM-LOCAL-FNB-"):
        raise ValueError("FNB_R17_RACE_ID_INVALID")
    if not isinstance(owner_semantics,dict) or set(owner_semantics)!=set(OWNERS):
        raise ValueError("FNB_R17_BOTH_OWNER_FROZEN_SEMANTICS_REQUIRED")
    if (not isinstance(dual_krs_manifest,dict)
            or dual_krs_manifest.get("race_id")!=race_id
            or set(dual_krs_manifest.get("owners") or {})!=set(OWNERS)):
        raise ValueError("FNB_R17_BOTH_REAL_KRS_OWNER_RECEIPTS_REQUIRED")
    active=dual_krs_manifest.get("active_runners")
    if not isinstance(active,list) or len(set(active))!=len(active) or len(active)<2:
        raise ValueError("FNB_R17_CURRENT_ACTIVE_RUNNER_LIST_INVALID")
    if (not isinstance(numerical_materialization_sha256,str)
            or len(numerical_materialization_sha256)!=64):
        raise ValueError("FNB_R17_NUMERIC_FREEZE_SHA_REQUIRED")
    numeric_file=Path(private_root)/race_id/"numerical_materialization.json"
    if (not numeric_file.is_file() or
            hashlib.sha256(numeric_file.read_bytes()).hexdigest()!=numerical_materialization_sha256):
        raise ValueError("FNB_R17_NUMERIC_ORIGINAL_PRIVATE_READBACK_FAIL")
    frozen_models=set()
    all_methods={}
    plan_receipts={}
    for owner in OWNERS:
        req=deepcopy(owner_semantics[owner])
        model=_validate_owner(owner,req,race_id,active,source_snapshot_sha256,
            numerical_materialization_sha256,
            dual_krs_manifest["owners"][owner],private_root)
        if model in frozen_models:
            raise ValueError("FNB_R17_BASELINE_CANDIDATE_SAME_MODEL_FORBIDDEN")
        frozen_models.add(model)
        mec=build_mec_plan(req,strict_head_closure=True,min_stake=100)
        if mec.get("orphan_thirds"):
            raise ValueError("FNB_R17_ORPHAN_MATERIAL_THIRD_WITHOUT_PAIR:"+owner)
        validation=validate_mec_plan(mec)
        if not validation["mec_verified"]:
            raise ValueError("FNB_R17_FAMILY_MEC_NOT_VERIFIED")
        method_out={}
        for method in METHODS:
            original=[{k:deepcopy(v) for k,v in t.items()}
                for t in mec["tickets"] if t["bet_type"]==method]
            required=sum(t["stake"] for t in original)
            # Per-method alternatives are separately budgeted; never pool
            # the six variants into one fictional actual purchase.
            class_view={**mec,"minimum_required_capital":required,
                "sha256":sha({"race_id":race_id,"owner":owner,
                              "method":method,"tickets":original}),
                "material_coverage_ratio":None}
            policy=resolve_capital_policy(req,class_view)
            budget=policy.get("capital_limit")
            if type(budget) is not int:
                raise ValueError("FNB_R17_HARD_BUDGET_REQUIRED_FOR_SIX_INDEPENDENT_METHODS")
            if budget<0:
                raise ValueError("FNB_R17_CAPITAL_LIMIT_NEGATIVE")
            no_candidates=not original
            rejected=policy.get("no_bet") is True
            computed_no_bet=bool(no_candidates or rejected)
            if computed_no_bet:
                tickets=[]
                reason=("FROZEN_COMMON_MEC_HAS_NO_"+method+"_SELECTION"
                        if no_candidates else
                        policy.get("reason") or "CAPITAL_OR_INFORMATION_GATE_NO_BET")
            else:
                tickets=original
                reason=None
            # Existing tree renderer is used; no custom ticket text derived
            # independently of the canonical leaf set.
            rendered=render_ticket_tree({"final_ticket":{
                "tickets":tickets,"no_bet":computed_no_bet},
                "capital_policy_decision":{"decision":"RECOMMENDATION_ONLY"}})
            total=sum(t["stake"] for t in tickets)
            method_out[method]={"tickets":tickets,
               "point_count":len(tickets),"total_investment":total,
               "capital_limit":budget,"unused_capital":budget-total,
               "no_bet":computed_no_bet,
               "reason":reason,
               "canonical_tree":rendered["text"],
               "required_method_mec_capital":required,
               "capital_policy_decision":policy["decision"],
               "pre_capital_mec_sha256":mec["sha256"],
               "method_is_an_alternative_not_combined_purchase":True}
        all_methods[owner]=method_out
        plan_receipts[owner]={"model_sha256":model,
           "mec_sha256":mec["sha256"],
           "mec_selected_before_capital":mec["ticket_count"],
           "mec_total_required_capital":mec["minimum_required_capital"],
           "method_alternative_trees_sha256":sha(method_out),
           "source_snapshot_sha256":source_snapshot_sha256,
           "numeric_sha256":numerical_materialization_sha256}
        if mec.get("pair_local_third_transport"):
            plan_receipts[owner]["pair_local_third_transport"]=deepcopy(mec["pair_local_third_transport"])
    result=audit_methods(all_methods)
    if not result["complete"]:
        raise ValueError("FNB_R17_GENERATED_SIX_CANONICAL_METHODS_FAILED:"+
                         ",".join(result["failures"][:5]))
    return {"profile":PROFILE,"status":"SIX_METHODS_FROM_VERIFIED_FROZEN_COMMON_MEC",
        "race_id":race_id,"owners":all_methods,
        "plan_evidence":plan_receipts,
        "six_alternative_ticket_methods_verified":True,
        "all_six_pooled_purchase_forbidden":True,
        "canonical_ticket_roundtrip":result,
        "candidate_predictions_generated_by_this_module":False,
        "new_scope_policy_or_seeds_added":False,
        "formal_signed_final_or_user_delivery_ack":False,
        "actual_purchase_verified":False,
        "registered_forward_oos_increment":0}

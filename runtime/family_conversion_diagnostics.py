from __future__ import annotations

import copy
import datetime as dt
import hashlib
import json
from typing import Any, Dict

PROFILE="KM-FAMILY-CONVERSION-DIAGNOSTICS-SHADOW-20261005-R1"
ACTIVATION_AT="2026-10-06T00:00:00+09:00"
HARD_MARKERS=("STRUCTURAL","NOT_APPLICABLE","SCRATCH","WITHDRAWN","UNIVERSE_MISMATCH","FORMAL_OUT_OF_SCOPE","STRUCTURAL_HARD","HARD_EXCLUSION","HARD-EXCLUSION","IMPOSSIBLE","INELIGIBLE")
FORWARD_ARMS=("PRODUCTION_BASELINE_R3","SET_ONLY","SET_PAIR","SELECTIVE_EXACT")
FORWARD_PROTOCOL="KM-LOCAL-PFS-FORWARD-20261006-R1"


def _sha(obj:Any)->str:
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def _roles(req:Dict[str,Any], final_package:Dict[str,Any])->Dict[str,list]:
    return (final_package or {}).get("roles") or (req.get("static_prediction") or {}).get("roles") or {}


def _role_rows(req:Dict[str,Any])->Dict[int,Dict[str,Dict[str,Any]]]:
    out={}
    for row in req.get("role_registry") or []:
        try:
            runner=int(row["runner_id"])
        except Exception:
            continue
        col=str(row.get("column") or "").upper()
        if col:
            out.setdefault(runner,{})[col]=dict(row)
    return out


def _hard(reason:Any)->bool:
    text=str(reason or "").upper()
    return any(x in text for x in HARD_MARKERS)


def _material_pairs(req:Dict[str,Any])->Dict[tuple[int,int],Dict[str,Any]]:
    out={}
    for row in req.get("pair_dispositions") or []:
        status=str(row.get("status") or "").upper()
        if status not in {"PURCHASE","PROTECT","MATERIAL"}:
            continue
        try:
            out[(int(row["head"]),int(row["second"]))]=dict(row)
        except Exception:
            continue
    return out


def _hard_pairs(req:Dict[str,Any])->set[tuple[int,int]]:
    out=set()
    for row in req.get("pair_dispositions") or []:
        if str(row.get("status") or "").upper()!="EXCLUDE" or not _hard(row.get("reason")):
            continue
        try:
            out.add((int(row["head"]),int(row["second"])))
        except Exception:
            continue
    return out


def _explicit_thirds(req:Dict[str,Any])->Dict[tuple[int,int,int],Dict[str,Any]]:
    out={}
    for row in req.get("third_dispositions") or []:
        try:
            out[(int(row["head"]),int(row["second"]),int(row["third"]))]=dict(row)
        except Exception:
            continue
    return out


def _krs_p3_ranks(utility:Dict[str,Any])->Dict[int,int]:
    out={}
    for row in (utility or {}).get("summary") or []:
        try:
            runner=int(row.get("horse_no") if row.get("horse_no") is not None else row.get("runner_id"))
        except Exception:
            continue
        ranks=row.get("ranks") or {}
        raw=ranks.get("SSR-P3")
        try:
            out[runner]=int(raw)
        except Exception:
            continue
    return out


def _purchased_exact(final_ticket:Dict[str,Any])->set[tuple[int,int,int]]:
    out=set()
    for row in (final_ticket or {}).get("tickets") or []:
        if str(row.get("bet_type") or "").upper()!="TRIFECTA":
            continue
        sel=row.get("selection") or []
        if len(sel)!=3:
            continue
        try:
            out.add(tuple(int(x) for x in sel))
        except Exception:
            continue
    return out


def build_diagnostics(req:Dict[str,Any], final_ticket:Dict[str,Any],
                      final_package:Dict[str,Any], krs_utility:Dict[str,Any],
                      generated_at:str, basis_sha256:str, *, _include_forward:bool=True)->Dict[str,Any]:
    roles=_roles(req,final_package)
    registry=_role_rows(req)
    material_pairs=_material_pairs(req)
    hard_pairs=_hard_pairs(req)
    explicit_thirds=_explicit_thirds(req)
    p3_ranks=_krs_p3_ranks(krs_utility)
    purchased_exact=_purchased_exact(final_ticket)

    active_w=sorted(int(r) for r,vals in roles.items()
                    if any(str(v).upper().startswith("W") for v in (vals or [])))
    active_p3=sorted(int(r) for r,vals in roles.items()
                     if any(str(v).upper().startswith("P3") for v in (vals or [])))

    winner_migration=[]
    for runner,vals in roles.items():
        rid=int(runner)
        role_set={str(v).upper() for v in (vals or [])}
        if any(v.startswith("W") for v in role_set):
            continue
        wrow=(registry.get(rid) or {}).get("W") or {}
        if _hard(wrow.get("reason")):
            continue
        lower={}
        for col in ("P2","P3"):
            row=(registry.get(rid) or {}).get(col) or {}
            status=str(row.get("status") or "").upper()
            if status in {"CORE","PROTECTED"}:
                lower[col]=status
        if lower:
            winner_migration.append({
                "runner_id":rid,
                "lower_role_status":lower,
                "diagnostic":"LOWER_ROLE_RETAINED_W_ABSENT",
                "structural_hard_w_negative_observed":False,
                "automatic_w_promotion":False,
                "purchase_authority":False,
            })

    active_p2={int(r) for r,vals in roles.items() if any(str(v).upper().startswith("P2") for v in vals)}
    protected_p2=[]
    for rid,cols in registry.items():
        status=str((cols.get("P2") or {}).get("status") or "").upper()
        if rid in active_p2 and status in {"CORE","PROTECTED"}:
            protected_p2.append((rid,status))

    pair_residual=[]
    for head in active_w:
        for second,p2_status in protected_p2:
            if head==second or (head,second) in material_pairs or (head,second) in hard_pairs:
                continue
            pair_residual.append({
                "head":head,
                "second":second,
                "p2_status":p2_status,
                "terminal":"PAIR-RESIDUAL",
                "diagnostic":"ACTIVE_W_X_CORE_OR_PROTECTED_P2_NO_MATERIAL_PAIR",
                "automatic_purchase":False,
                "purchase_authority":False,
            })

    selective_exact=[]
    for (head,second),pair in sorted(material_pairs.items()):
        for third in active_p3:
            if third in {head,second}:
                continue
            exact=(head,second,third)
            explicit=explicit_thirds.get(exact) or {}
            if (head,second) in hard_pairs or (
                str(explicit.get("status") or "").upper()=="EXCLUDE"
                and _hard(explicit.get("reason"))
            ):
                continue
            if exact in purchased_exact:
                continue
            reasons=[]
            p3row=(registry.get(third) or {}).get("P3") or {}
            p3_status=str(p3row.get("status") or "").upper()
            if p3_status in {"CORE","PROTECTED"}:
                reasons.append("STATIC_P3_"+p3_status)
            if any(x in str(p3row.get("reason") or "").upper()
                   for x in ("DIRECT","PROTECT","CURRENT_STATE","STAGE")):
                reasons.append("STATIC_P3_INDEPENDENT_REASON")
            explicit=explicit_thirds.get(exact) or {}
            explicit_status=str(explicit.get("status") or "").upper()
            if explicit_status in {"PURCHASE","PROTECT","MATERIAL"}:
                reasons.append("PAIR_LOCAL_THIRD_"+explicit_status)
            rank=p3_ranks.get(third)
            if rank is not None and rank<=3:
                reasons.append("KRS_P3_TOP3_REAUDIT")
            if _hard(p3row.get("reason")) or not reasons:
                continue
            selective_exact.append({
                "exact":[head,second,third],
                "pair_status":str(pair.get("status") or "").upper(),
                "p3_role_status":p3_status or None,
                "krs_p3_rank":rank,
                "independent_protection_reasons":sorted(set(reasons)),
                "diagnostic":"MATERIAL_PAIR_X_INDEPENDENTLY_PROTECTED_P3",
                "automatic_purchase":False,
                "purchase_authority":False,
            })

    out={
        "profile":PROFILE,
        "status":"SHADOW-DIAGNOSTIC / NON-PRODUCTION / NO-AUTO-PROMOTION",
        "activation_at":ACTIVATION_AT,
        "race_id":req.get("race_id"),
        "generated_at":generated_at,
        "scheduled_post_at":req.get("scheduled_post_at"),
        "temporal_mode":req.get("temporal_mode"),
        "source_basis_sha256":basis_sha256,
        "winner_role_migration_candidates":winner_migration,
        "pair_residual_candidates":pair_residual,
        "selective_exact_candidates":selective_exact,
        "production_effect":"NONE",
        "automatic_purchase":False,
        "existing_common_exact_oos_arms_changed":False,
        "existing_local_mec_r5_arms_changed":False,
    }
    if _include_forward:
        from formal_oos_policy import request_oos_policy
        from local_mec_r5_shadow import build_arm
        policy=request_oos_policy(req)
        out["forward_protocol"]=FORWARD_PROTOCOL
        out["request_oos_allowed"]=bool(policy["oos_allowed"])
        out["acceptance_only"]=bool(policy["acceptance_only"])
        out["frozen_roles"]=copy.deepcopy(roles)
        out["material_pairs"]=[list(p) for p in sorted(material_pairs)]
        out["explicit_material_exacts"]=[list(p) for p,r in sorted(explicit_thirds.items())
            if str(r.get("status") or "").upper() in {"PURCHASE","PROTECT","MATERIAL"}]
        envelope={"final_ticket":final_ticket,"final_prediction_package":final_package}
        arms={a:build_arm(req,envelope,a) for a in ("SET_ONLY","SET_PAIR")}
        selected=copy.deepcopy(arms["SET_PAIR"]["tickets"])
        # Missing-exact diagnostics and already purchased independently protected
        # exacts share one rule; diagnostics themselves remain missing-only.
        all_exact=build_selective_tickets(req,final_package,krs_utility)
        selected.extend(all_exact)
        arms["SELECTIVE_EXACT"]={"tickets":selected,"ticket_count":len(selected)}
        arms["PRODUCTION_BASELINE_R3"]={"tickets":copy.deepcopy(final_ticket.get("tickets") or [])}
        out["forward_arms"]=arms
    out["sha256"]=_sha({k:v for k,v in out.items() if k!="sha256"})
    return out


def bind_to_trace(trace:Dict[str,Any], diagnostic:Dict[str,Any])->Dict[str,Any]:
    out=copy.deepcopy(trace or {})
    out["family_conversion_diagnostics_binding"]={
        "profile":PROFILE,
        "sha256":diagnostic.get("sha256"),
        "basis_sha256":diagnostic.get("source_basis_sha256"),
        "generated_at":diagnostic.get("generated_at"),
        "scheduled_post_at":diagnostic.get("scheduled_post_at"),
        "production_effect":"NONE",
    }
    return out


def verify_signed_final_binding(final_envelope:Dict[str,Any], diagnostic:Dict[str,Any])->Dict[str,Any]:
    expected=_sha({k:v for k,v in diagnostic.items() if k!="sha256"})
    if diagnostic.get("sha256")!=expected:
        raise AssertionError("FAMILY_CONVERSION_DIAGNOSTIC_CONTENT_HASH_MISMATCH")
    rec=final_envelope.get("receipt") or {}
    art=final_envelope.get("artifact") or {}
    if rec.get("phase")!="FINAL" or rec.get("status")!="PASS":
        raise AssertionError("FAMILY_CONVERSION_DIAGNOSTIC_FINAL_NOT_PASS")
    binding=(art.get("ticket_transport_trace") or {}).get("family_conversion_diagnostics_binding") or {}
    if binding.get("sha256")!=diagnostic.get("sha256"):
        raise AssertionError("FAMILY_CONVERSION_DIAGNOSTIC_SHA_NOT_BOUND")
    if binding.get("basis_sha256")!=diagnostic.get("source_basis_sha256"):
        raise AssertionError("FAMILY_CONVERSION_DIAGNOSTIC_BASIS_SHA_NOT_BOUND")
    if str(binding.get("production_effect"))!="NONE":
        raise AssertionError("FAMILY_CONVERSION_DIAGNOSTIC_PRODUCTION_EFFECT_FORBIDDEN")
    for key in ("generated_at","scheduled_post_at"):
        if binding.get(key)!=diagnostic.get(key):
            raise AssertionError("FAMILY_CONVERSION_DIAGNOSTIC_TEMPORAL_BINDING_MISMATCH")
    return {
        "valid":True,
        "profile":PROFILE,
        "diagnostic_sha256":diagnostic.get("sha256"),
        "basis_sha256":diagnostic.get("source_basis_sha256"),
        "final_receipt_sha256":final_envelope.get("receipt_sha256"),
        "production_effect":"NONE",
    }


def build_selective_tickets(req, final_package, krs_utility):
    # Reuse the diagnostic selector with an empty purchase baseline; all
    # independently protected exacts are considered under the same rule.
    diagnostic=build_diagnostics(req,{"tickets":[]},final_package,krs_utility,
        generated_at="",basis_sha256="",_include_forward=False)
    return [{"bet_type":"TRIFECTA","selection":x["exact"],"stake":100}
            for x in diagnostic["selective_exact_candidates"]]


def settle_diagnostics(diagnostic, final_envelope, result_request, result_authority,
                       *, final_signature_verified=False):
    from mec_r4_shadow import settle_ticket_list
    binding=verify_signed_final_binding(final_envelope,diagnostic)
    if not final_signature_verified:
        raise AssertionError("FAMILY_CONVERSION_FINAL_SIGNATURE_UNVERIFIED")
    rid=diagnostic.get("race_id")
    art=final_envelope.get("artifact") or {}
    if rid!=result_request.get("race_id") or rid!=art.get("race_id"):
        raise AssertionError("FAMILY_CONVERSION_RACE_ID_MISMATCH")
    top3=[int(x) for x in result_request.get("finish_order",[])[:3]]
    if len(top3)!=3 or len(set(top3))!=3:
        raise AssertionError("FAMILY_CONVERSION_RESULT_TOP3_INVALID")
    if diagnostic.get("forward_protocol")!=FORWARD_PROTOCOL or diagnostic.get("production_effect")!="NONE":
        raise AssertionError("FAMILY_CONVERSION_PROTOCOL_MISMATCH")
    gen=dt.datetime.fromisoformat(diagnostic["generated_at"])
    post=dt.datetime.fromisoformat(diagnostic["scheduled_post_at"])
    available=dt.datetime.fromisoformat(result_request["result_available_at"])
    activation=dt.datetime.fromisoformat(ACTIVATION_AT)
    official=(result_authority.get("status")=="PASS"
        and result_authority.get("verified_signed_result") is True
        and all(result_authority.get(k) for k in
                ("verification_ref","result_receipt_sha256","result_artifact_sha256")))
    result={"official_result":{"top3":top3,"payouts_per_100_yen":result_request.get("payouts") or {}}}
    arms={a:settle_ticket_list(diagnostic["forward_arms"][a]["tickets"],result) for a in FORWARD_ARMS}
    roles=diagnostic.get("frozen_roles") or {}
    winner,second,third=top3
    w=any(str(r).upper().startswith("W") for r in roles.get(str(winner),[]))
    pair=[winner,second] in diagnostic.get("material_pairs",[])
    exact=(top3 in diagnostic.get("explicit_material_exacts",[])
        or any(t.get("bet_type")=="TRIFECTA" and t.get("selection")==top3
               for t in diagnostic["forward_arms"]["PRODUCTION_BASELINE_R3"]["tickets"]))
    universe=all(str(h) in roles for h in top3)
    first=("UNIVERSE" if not universe else "WINNER_HEAD" if not w else
           "PAIR_MATERIALITY" if not pair else "EXACT_CONTINUITY" if not exact else
           "MEC_CROSS_BET" if "TRIFECTA" not in arms["PRODUCTION_BASELINE_R3"].get("hit_types",[]) else
           "CAPITAL_HIT_BUT_LOSS" if 0<arms["PRODUCTION_BASELINE_R3"]["return"]<arms["PRODUCTION_BASELINE_R3"]["investment"] else "NONE")
    eligible=bool(official and gen>=activation and gen<post<=available
        and diagnostic.get("temporal_mode")=="FORMAL-PRE-RACE"
        and diagnostic.get("request_oos_allowed") and not diagnostic.get("acceptance_only")
        and not result_request.get("acceptance_only")
        and all(x.get("status")=="SETTLED" for x in arms.values()))
    outcomes={
        "winner_role_migration_hit":any(x["runner_id"]==winner for x in diagnostic["winner_role_migration_candidates"]),
        "pair_residual_hit":any([x["head"],x["second"]]==top3[:2] for x in diagnostic["pair_residual_candidates"]),
        "selective_exact_hit":any(x["exact"]==top3 for x in diagnostic["selective_exact_candidates"]),
    }
    out={"protocol":FORWARD_PROTOCOL,"race_id":rid,"generated_at":diagnostic["generated_at"],
        "diagnostic_sha256":diagnostic["sha256"],"binding":binding,"result_authority":result_authority,
        "oos_eligible":eligible,"arms":arms,"first_failure":first,"diagnostic_outcomes":outcomes,
        "coverage":{a:{"set": "TRIO" in x.get("hit_types",[]),
                       "pair":"EXACTA" in x.get("hit_types",[]),
                       "exact":"TRIFECTA" in x.get("hit_types",[])} for a,x in arms.items()},
        "candidate_counts":{k:len(diagnostic[k]) for k in
            ("winner_role_migration_candidates","pair_residual_candidates","selective_exact_candidates")},
        "authority":"FROZEN-RECOMMENDATION / SHADOW / NOT-ACTUAL-PURCHASE",
        "production_effect":"NONE","automatic_promotion":False}
    out["sha256"]=_sha(out)
    return out


def forward_status(root="runtime/family_conversion_measurements"):
    from pathlib import Path
    from collections import Counter
    from local_mec_r5_oos_tracker import _aggregate, _normalized_comparison
    rows=[]; held=[]
    for path in sorted(Path(root).glob("*.json")):
        try:
            row=json.loads(path.read_text())
            if row.get("sha256")!=_sha({k:v for k,v in row.items() if k!="sha256"}):
                raise ValueError("MEASUREMENT_HASH_MISMATCH")
            if row.get("protocol")!=FORWARD_PROTOCOL or not row.get("oos_eligible"):
                held.append({"race_id":row.get("race_id"),"reason":"NOT_FORWARD_OOS"}); continue
            rows.append(row)
        except Exception as e:
            held.append({"file":str(path),"reason":str(e)})
    if len({r["race_id"] for r in rows})!=len(rows):
        raise AssertionError("FAMILY_CONVERSION_DUPLICATE_RACE")
    rows.sort(key=lambda x:(x["generated_at"],x["race_id"]))
    # Fixed first-30 cohort; never replace losses with later wins.
    rows=rows[:30]
    agg={a:_aggregate([r["arms"][a] for r in rows]) for a in FORWARD_ARMS}
    coverage={a:{k:sum(r["coverage"][a][k] for r in rows) for k in ("set","pair","exact")} for a in FORWARD_ARMS}
    normalized=_normalized_comparison(agg)
    normalized["equal_budget_aggregates"]={a:_aggregate([
        {**r["arms"][a], **{key: r["arms"][a][key]*min(r["arms"][b]["investment"] for b in FORWARD_ARMS)/r["arms"][a]["investment"]
          for key in ("investment","return","profit_loss")}}
        for r in rows if all(r["arms"][b]["investment"]>0 for b in FORWARD_ARMS)]) for a in FORWARD_ARMS}
    normalized["equal_ticket_aggregates"]={a:_aggregate([
        {**r["arms"][a], **{key: r["arms"][a][key]*min(r["arms"][b]["ticket_count"] for b in FORWARD_ARMS)/r["arms"][a]["ticket_count"]
          for key in ("investment","return","profit_loss")},
         "ticket_count":min(r["arms"][b]["ticket_count"] for b in FORWARD_ARMS)}
        for r in rows if all(r["arms"][b]["ticket_count"]>0 for b in FORWARD_ARMS)]) for a in FORWARD_ARMS}
    b=agg["PRODUCTION_BASELINE_R3"]; gates={}
    for a in FORWARD_ARMS[1:]:
        x=agg[a]; returns=[r["arms"][a]["return"] for r in rows]
        share=max(returns,default=0)/sum(returns) if sum(returns)>0 else None
        checks={"fixed_30_complete":len(rows)==30,"no_integrity_holds":not any(x.get("reason")!="NOT_FORWARD_OOS" for x in held),
            "multiple_race_days":len({r["generated_at"][:10] for r in rows})>=3,
            "pfs_above_production":x["investment_weighted_pfs"] is not None and b["investment_weighted_pfs"] is not None and x["investment_weighted_pfs"]>b["investment_weighted_pfs"],
            "pfs_above_break_even":x["investment_weighted_pfs"] is not None and x["investment_weighted_pfs"]>100,
            "drawdown_not_worse":x["max_drawdown"]<=b["max_drawdown"],
            "equal_budget_drawdown_not_worse":normalized["equal_budget_aggregates"][a]["max_drawdown"]<=normalized["equal_budget_aggregates"]["PRODUCTION_BASELINE_R3"]["max_drawdown"],
            "equal_ticket_profit_not_worse":normalized["equal_ticket_aggregates"][a]["profit_loss"]>=normalized["equal_ticket_aggregates"]["PRODUCTION_BASELINE_R3"]["profit_loss"],
            "hit_but_loss_not_worse":x["hit_but_loss_count"]<=b["hit_but_loss_count"],
            "set_coverage_preserved":coverage[a]["set"]>=coverage["PRODUCTION_BASELINE_R3"]["set"],
            "no_single_race_dependence":share is not None and share<=0.5,
            "positive_without_best_race":sum(r["arms"][a]["profit_loss"] for r in rows)-max((r["arms"][a]["profit_loss"] for r in rows),default=0)>0}
        gates[a]={"checks":checks,"decision":"REVIEW_ELIGIBLE" if all(checks.values()) else "CONTINUE" if len(rows)<30 else "REJECT_OR_SIMPLIFY_REVIEW",
            "max_return_share":share,"automatic_promotion":False,"explicit_promotion_declaration_required":True}
    out={"protocol":FORWARD_PROTOCOL,"eligible_races":len(rows),"target":30,
        "entries":rows,"held":held,"aggregates":agg,"coverage":coverage,
        "first_failure_counts":dict(Counter(r["first_failure"] for r in rows)),
        "diagnostic_hits":{k:sum(r["diagnostic_outcomes"][k] for r in rows) for k in
                           ("winner_role_migration_hit","pair_residual_hit","selective_exact_hit")},
        "candidate_counts":{k:sum(r["candidate_counts"][k] for r in rows) for k in
                            ("winner_role_migration_candidates","pair_residual_candidates","selective_exact_candidates")},
        "normalized_comparison":normalized,"promotion_gate":gates,
        "production_effect":"NONE","automatic_promotion":False}
    out["sha256"]=_sha(out)
    return out

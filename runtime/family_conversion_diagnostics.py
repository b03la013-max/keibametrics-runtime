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

    # A residual is an audit trigger, never a purchase instruction. The
    # independent KRS actionable list corroborates the static role universe.
    krs_pairs={(int(x["head"]),int(x["second"])) for x in
               (krs_utility or {}).get("actionable_ordered_pair_proposals") or []
               if x.get("actionable") is True}
    for residual in pair_residual:
        support=["STATIC_ACTIVE_W_X_CORE_OR_PROTECTED_P2"]
        if (residual["head"],residual["second"]) in krs_pairs:
            support.append("KRS_ACTIONABLE_SUPPORT")
        residual["independent_support"]=support
        if len(support)>=2:residual["terminal"]="PAIR-REVIEW"
    pair_local=[]
    for (head,second),pair in sorted(material_pairs.items()):
        if (head,second) in hard_pairs:continue
        for third in active_p3:
            if third in {head,second}:continue
            row=explicit_thirds.get((head,second,third)) or {}
            p3row=(registry.get(third) or {}).get("P3") or {}
            if _hard(row.get("reason")) or _hard(p3row.get("reason")):continue
            status=str(row.get("status") or "").upper()
            sufficient=bool(status in {"PURCHASE","MATERIAL"} and row.get("reason")
                            and not any(x in str(row["reason"]).upper() for x in ("UNKNOWN","GLOBAL_P3","SET_ONLY")))
            pair_local.append({"exact":[head,second,third],
                "terminal":"THIRD_EXACT_MATERIAL" if sufficient else "THIRD_SET_PROTECTION",
                "pair_local_reason":row.get("reason"),"reason_sufficient":sufficient,
                "automatic_purchase":False,"production_effect":"NONE"})
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
        "pair_local_third_terminals":pair_local,
        "measurement_principles":["UNKNOWN != WEAK","UNKNOWN != MUST PURCHASE"],
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
        out["daily_improvement_shadow"]=build_daily_improvement_shadow(req,final_ticket,final_package,krs_utility,pair_local,generated_at)
    out["sha256"]=_sha({k:v for k,v in out.items() if k!="sha256"})
    return out


DAILY_PROTOCOL="KM-LOCAL-DAILY-IMPROVEMENT-20261007-R1"
DAILY_ACTIVATION="2026-10-07T00:00:00+09:00"
DAILY_ARMS=("PRODUCTION_BASELINE_R3","PAIR_LOCAL_SELECTIVE_EXACT","CONSENSUS_CORE_3","CONSENSUS_CORE_4")


def build_daily_improvement_shadow(req, final_ticket, final_package, utility, terminals, generated_at):
    """Absorbed diagnostic extension. No probability, EV or live capital policy."""
    from local_mec_r5_shadow import build_arm
    from formal_oos_policy import request_oos_policy
    ranking=[int(x) for x in (final_package.get("ranking") or (req.get("static_prediction") or {}).get("ranking") or [])]
    consensus=set()
    for row in (utility or {}).get("summary") or []:
        ranks=row.get("ranks") or {}
        if any(isinstance(ranks.get(k),int) and 1<=ranks[k]<=4 for k in ("SSR-W","SSR-P2","SSR-P3")):
            consensus.add(int(row.get("horse_no") or row.get("runner_id")))
    registry=_role_rows(req)
    hard={rid for rid,cols in registry.items() if any(_hard(x.get("reason")) for x in cols.values())}
    core=[x for x in ranking[:4] if x in consensus and x not in hard]
    base=copy.deepcopy(final_ticket.get("tickets") or [])
    envelope={"final_ticket":final_ticket,"final_prediction_package":final_package}
    selected=build_arm(req,envelope,"SET_PAIR")["tickets"]
    selected.extend({"bet_type":"TRIFECTA","selection":x["exact"],"stake":100}
                    for x in terminals if x["terminal"]=="THIRD_EXACT_MATERIAL")
    arms={"PRODUCTION_BASELINE_R3":{"tickets":base},"PAIR_LOCAL_SELECTIVE_EXACT":{"tickets":selected}}
    for n in (3,4):
        members=core[:n]
        tickets=[copy.deepcopy(t) for t in selected if set(map(int,t["selection"])).issubset(set(members))] if len(members)==n else []
        arms["CONSENSUS_CORE_"+str(n)]={"tickets":tickets,"core":members,
            "disposition":"PAPER" if len(members)!=n or not tickets else "SHADOW_ONLY",
            "semantic_universe_unchanged":True}
    # Quotes must be frozen market evidence with their own source/time. Missing
    # prices remain UNKNOWN; realised result payouts never enter this function.
    quote=req.get("market_payout_snapshot") or {}
    quote_valid=False
    if quote.get("source") and quote.get("available_at") and generated_at:
        try:
            age=(dt.datetime.fromisoformat(generated_at)-dt.datetime.fromisoformat(quote["available_at"])).total_seconds()
            quote_valid=0<=age<=300
            if quote.get("sha256") and quote["sha256"]!=_sha({k:v for k,v in quote.items() if k!="sha256"}):quote_valid=False
        except ValueError:pass
    quote_rows=quote.get("quotes") or [] if quote_valid else []
    def key(t):
        bt=str(t.get("bet_type") or "").upper();sel=list(map(int,t.get("selection") or []))
        return bt,tuple(sorted(sel) if bt=="TRIO" else sel)
    qmap={}
    for q in quote_rows:
        low=q.get("payout_per_100_low");high=q.get("payout_per_100_high")
        if isinstance(low,(int,float)) and isinstance(high,(int,float)) and 0<low<=high:
            qmap[key(q)]=(low,high)
    capital=sum(int(t.get("stake") or 0) for t in base)
    protection=[t for t in base if t.get("mec_tier") in {"PROTECTION","TAIL"}]
    unknown_tier=[t for t in base if t.get("mec_tier") not in {"CORE","PROTECTION","TAIL"}]
    protection_capital=sum(int(t.get("stake") or 0) for t in protection)
    def ranges(tickets):
        return [{"bet_type":t["bet_type"],"selection":t["selection"],
                 "return_low":qmap[key(t)][0]*int(t["stake"])/100,
                 "return_high":qmap[key(t)][1]*int(t["stake"])/100}
                for t in tickets if key(t) in qmap]
    core_quotes=ranges([t for t in base if t.get("mec_tier")=="CORE"])
    protected_quotes=ranges(protection)
    # For each frozen core exact scenario, sum every simultaneously winning
    # frozen bet. Missing a relevant quote makes that scenario UNKNOWN.
    portfolio_ranges=[]
    for candidate in [t for t in base if t.get("mec_tier")=="CORE" and str(t.get("bet_type") or "").upper()=="TRIFECTA"]:
        order=list(map(int,candidate["selection"]))
        matching=[t for t in base if key(t)==key({"bet_type":t["bet_type"],"selection":order[:2] if str(t["bet_type"]).upper()=="EXACTA" else order})]
        complete=all(key(t) in qmap for t in matching)
        portfolio_ranges.append({"exact":order,"status":"OBSERVED" if complete else "UNKNOWN",
            "return_low":sum(qmap[key(t)][0]*int(t["stake"])/100 for t in matching) if complete else None,
            "return_high":sum(qmap[key(t)][1]*int(t["stake"])/100 for t in matching) if complete else None,
            "missing_quote_count":sum(key(t) not in qmap for t in matching)})
    portfolio_mismatches=[r for r in portfolio_ranges if r["status"]=="OBSERVED" and r["return_high"]<capital]
    # Selection-specific sufficiency is not portfolio EV or a winning probability.
    economic={"status":"OBSERVED" if core_quotes else "UNKNOWN","capital":capital,
        "core_selection_payout_ranges":core_quotes,
        "portfolio_outcome_payout_ranges":portfolio_ranges,
        "portfolio_capital_to_payout_mismatches":portfolio_mismatches,
        "quoted_core_ticket_count":len(core_quotes),
        "capital_to_payout_mismatches":[q for q in core_quotes if q["return_high"]<capital],
        "shadow_disposition":"REVIEW_CORE_ONLY_PAPER_NO_BET" if portfolio_mismatches else "UNKNOWN_OR_NO_MISMATCH",
        "quote_snapshot_sha256":_sha(quote) if quote_valid else None,
        "quote_source":quote.get("source") if quote_valid else None,
        "quote_available_at":quote.get("available_at") if quote_valid else None,
        "probability":None,"ev":None,"automatic_purchase":False}
    burden={"status":"UNKNOWN" if unknown_tier else "MEASURED",
        "protection_capital":protection_capital,"total_capital":capital,
        "protection_burden_ratio":protection_capital/capital if capital and not unknown_tier else None,
        "unknown_tier_capital":sum(int(t.get("stake") or 0) for t in unknown_tier),
        "protection_payout_ranges":protected_quotes,
        "protection_capital_ceiling_status":"MEASURED_SHADOW" if protected_quotes and not unknown_tier else "UNKNOWN",
        "selection_specific_market_ceiling_range":[min(q["return_low"] for q in protected_quotes),max(q["return_high"] for q in protected_quotes)] if protected_quotes else None,
        "protection_capital_exceeds_market_ceiling":protection_capital>max(q["return_high"] for q in protected_quotes) if protected_quotes and not unknown_tier else None,
        "fixed_cutoff":None,"production_effect":"NONE"}
    policy=request_oos_policy(req)
    return {"protocol":DAILY_PROTOCOL,"activation_at":DAILY_ACTIVATION,
        "cohort":"NEW_FORWARD_ONLY / FIRST_30 / MINIMUM_3_DAYS / NO_AUTO_PROMOTION",
        "historical_boundary":"2026-10-06 OHI is regression only; never new-cohort credit",
        "request_oos_allowed":bool(policy["oos_allowed"]),"arms":arms,
        "market_payout_sufficiency":economic,"protection_burden":burden,
        "production_effect":"NONE","automatic_promotion":False}


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
    from mec_r4_shadow import official_result_for_settlement
    result=official_result_for_settlement(result_request)
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
    from post_result_learning import _coverage
    winning_orders=[x["selection"] for x in (result_request.get("winning_selections") or {}).get("TRIFECTA",[])] or [top3]
    set_layers={}
    for a in FORWARD_ARMS:
        coverage_final={"final_prediction_package":{"roles":roles},"final_ticket":{"tickets":diagnostic["forward_arms"][a]["tickets"]}}
        evaluations=[_coverage(coverage_final,order) for order in winning_orders]
        set_layers[a]={k:any(e[k] for e in evaluations) for k in
            ("semantic_set_coverage","exact_oriented_set_coverage","unordered_monetizable_set_coverage")}
    outcomes={
        "winner_role_migration_hit":any(x["runner_id"]==winner for x in diagnostic["winner_role_migration_candidates"]),
        "pair_residual_hit":any([x["head"],x["second"]]==top3[:2] for x in diagnostic["pair_residual_candidates"]),
        "selective_exact_hit":any(x["exact"]==top3 for x in diagnostic["selective_exact_candidates"]),
    }
    out={"protocol":FORWARD_PROTOCOL,"race_id":rid,"generated_at":diagnostic["generated_at"],
        "diagnostic_sha256":diagnostic["sha256"],"binding":binding,"result_authority":result_authority,
        "oos_eligible":eligible,"arms":arms,"first_failure":first,"diagnostic_outcomes":outcomes,
        "set_coverage_layers":set_layers,
        "coverage":{a:{"set": "TRIO" in x.get("hit_types",[]),
                       "pair":"EXACTA" in x.get("hit_types",[]),
                       "exact":"TRIFECTA" in x.get("hit_types",[])} for a,x in arms.items()},
        "candidate_counts":{k:len(diagnostic[k]) for k in
            ("winner_role_migration_candidates","pair_residual_candidates","selective_exact_candidates")},
        "authority":"FROZEN-RECOMMENDATION / SHADOW / NOT-ACTUAL-PURCHASE",
        "production_effect":"NONE","automatic_promotion":False}
    daily=diagnostic.get("daily_improvement_shadow")
    if daily and daily.get("protocol")==DAILY_PROTOCOL:
        daily_arms={a:settle_ticket_list(daily["arms"][a]["tickets"],result) for a in DAILY_ARMS}
        daily_layers={}
        for a in DAILY_ARMS:
            coverage_final={"final_prediction_package":{"roles":roles},"final_ticket":{"tickets":daily["arms"][a]["tickets"]}}
            evaluations=[_coverage(coverage_final,order) for order in winning_orders]
            daily_layers[a]={k:any(e[k] for e in evaluations) for k in
                ("semantic_set_coverage","exact_oriented_set_coverage","unordered_monetizable_set_coverage")}
        out["daily_improvement_measurement"]={"protocol":DAILY_PROTOCOL,"set_coverage_layers":daily_layers,
            "oos_eligible":bool(eligible and gen>=dt.datetime.fromisoformat(DAILY_ACTIVATION)
                                 and all(daily["arms"][a].get("disposition")!="PAPER" and daily_arms[a]["investment"]>0 for a in DAILY_ARMS)),
            "arms":daily_arms,"market_payout_sufficiency":daily["market_payout_sufficiency"],
            "protection_burden":daily["protection_burden"],"production_effect":"NONE"}
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
    daily_rows=[r for r in rows if (r.get("daily_improvement_measurement") or {}).get("oos_eligible") is True][:30]
    rows=rows[:30]
    agg={a:_aggregate([r["arms"][a] for r in rows]) for a in FORWARD_ARMS}
    coverage={a:{k:sum(r["coverage"][a][k] for r in rows) for k in ("set","pair","exact")} for a in FORWARD_ARMS}
    normalized=_normalized_comparison(agg)
    normalized["equal_budget_aggregates"]={a:_aggregate([
        {**r["arms"][a], **{key: r["arms"][a][key]*min(r["arms"][b]["investment"] for b in FORWARD_ARMS)/r["arms"][a]["investment"]
          for key in ("investment","return","profit_loss","refund","winning_return") if key in r["arms"][a]}}
        for r in rows if all(r["arms"][b]["investment"]>0 for b in FORWARD_ARMS)]) for a in FORWARD_ARMS}
    normalized["equal_ticket_aggregates"]={a:_aggregate([
        {**r["arms"][a], **{key: r["arms"][a][key]*min(r["arms"][b]["ticket_count"] for b in FORWARD_ARMS)/r["arms"][a]["ticket_count"]
          for key in ("investment","return","profit_loss","refund","winning_return") if key in r["arms"][a]},
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
    daily_agg={a:_aggregate([r["daily_improvement_measurement"]["arms"][a] for r in daily_rows]) for a in DAILY_ARMS}
    daily_normalized=_normalized_comparison(daily_agg)
    for label,denominator in (("equal_budget","investment"),("equal_ticket","ticket_count")):
        daily_normalized[label+"_aggregates"]={a:_aggregate([
            {**r["daily_improvement_measurement"]["arms"][a],
             "ticket_count":min(r["daily_improvement_measurement"]["arms"][b]["ticket_count"] for b in DAILY_ARMS) if denominator=="ticket_count" else r["daily_improvement_measurement"]["arms"][a]["ticket_count"],
             **{k:r["daily_improvement_measurement"]["arms"][a][k]*min(r["daily_improvement_measurement"]["arms"][b][denominator] for b in DAILY_ARMS)/r["daily_improvement_measurement"]["arms"][a][denominator]
                for k in ("investment","return","profit_loss","refund","winning_return")}}
            for r in daily_rows]) for a in DAILY_ARMS}
    baseline=daily_agg["PRODUCTION_BASELINE_R3"]
    daily_gates={}
    for a in DAILY_ARMS[1:]:
        arm=daily_agg[a]
        returns=[r["daily_improvement_measurement"]["arms"][a]["return"] for r in daily_rows]
        checks={"fixed_30_complete":len(daily_rows)==30,
            "minimum_3_days":len({dt.datetime.fromisoformat(r["generated_at"]).astimezone(dt.timezone(dt.timedelta(hours=9))).date() for r in daily_rows})>=3,
            "positive_pfs_above_baseline":arm["investment_weighted_pfs"] is not None and baseline["investment_weighted_pfs"] is not None and arm["investment_weighted_pfs"]>max(100,baseline["investment_weighted_pfs"]),
            "drawdown_not_worse":arm["max_drawdown"]<=baseline["max_drawdown"],
            "equal_budget_drawdown_not_worse":daily_normalized["equal_budget_aggregates"][a]["max_drawdown"]<=daily_normalized["equal_budget_aggregates"]["PRODUCTION_BASELINE_R3"]["max_drawdown"],
            "equal_ticket_profit_not_worse":daily_normalized["equal_ticket_aggregates"][a]["profit_loss"]>=daily_normalized["equal_ticket_aggregates"]["PRODUCTION_BASELINE_R3"]["profit_loss"],
            "semantic_set_preserved":all(r["daily_improvement_measurement"]["set_coverage_layers"][a]["semantic_set_coverage"]==r["daily_improvement_measurement"]["set_coverage_layers"]["PRODUCTION_BASELINE_R3"]["semantic_set_coverage"] for r in daily_rows),
            "no_integrity_holds":not any(h.get("reason")!="NOT_FORWARD_OOS" for h in held),
            "hit_but_loss_not_worse":arm["hit_but_loss_count"]<=baseline["hit_but_loss_count"],
            "return_concentration":bool(sum(returns)>0 and max(returns,default=0)/sum(returns)<=0.5),
            "positive_without_best":sum(r["daily_improvement_measurement"]["arms"][a]["profit_loss"] for r in daily_rows)-max((r["daily_improvement_measurement"]["arms"][a]["profit_loss"] for r in daily_rows),default=0)>0}
        daily_gates[a]={"checks":checks,"decision":"REVIEW_ELIGIBLE" if all(checks.values()) else "CONTINUE" if len(daily_rows)<30 else "REJECT_OR_SIMPLIFY_REVIEW",
            "explicit_promotion_required":True,"automatic_promotion":False}
    out["daily_improvement_cohort"]={"protocol":DAILY_PROTOCOL,"activation_at":DAILY_ACTIVATION,
        "eligible_races":len(daily_rows),"target":30,"aggregates":daily_agg,
        "set_coverage_layers":{a:{k:sum(r["daily_improvement_measurement"]["set_coverage_layers"][a][k] for r in daily_rows) for k in ("semantic_set_coverage","exact_oriented_set_coverage","unordered_monetizable_set_coverage")} for a in DAILY_ARMS},
        "entries":[{"race_id":r["race_id"],"diagnostic_sha256":r["diagnostic_sha256"]} for r in daily_rows],
        "normalized_comparison":daily_normalized,"promotion_gate":daily_gates,
        "production_effect":"NONE","automatic_promotion":False}
    out["sha256"]=_sha(out)
    return out

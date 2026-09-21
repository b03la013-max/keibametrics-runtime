from __future__ import annotations
import copy, json, hashlib
from collections import defaultdict

MEC_PROFILE="KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R1"
BUDGET_MARKERS=("BUDGET","FIXED_CAPITAL","CAPITAL_LIMIT","LOWER_MATERIALITY_UNDER_FIXED_CAPITAL")
PROCEDURAL_MARKERS=("CORRECTNESS_REPAIR","TERMINALIZATION_CORRECTNESS","EXPECTED_PAIR_TERMINALIZATION")
ROLE_ACTIVE={"CORE","PROTECTED","CONDITIONAL","RESIDUAL"}

class MECError(ValueError):
    pass

def _s(v): return str(v)

def _budget_only(reason:str)->bool:
    u=str(reason or "").upper()
    return any(x in u for x in BUDGET_MARKERS)

def _procedural_only(reason:str)->bool:
    u=str(reason or "").upper()
    return any(x in u for x in PROCEDURAL_MARKERS)

def _active_roles(req):
    out=defaultdict(set)
    for x in req.get("role_registry") or []:
        if str(x.get("status")) in ROLE_ACTIVE:
            out[_s(x.get("runner_id"))].add(str(x.get("column")))
    return out

def _semantic_pairs(req):
    rows=[]
    for x in req.get("pair_dispositions") or []:
        st=str(x.get("status") or "")
        reason=str(x.get("reason") or "")
        if st=="PURCHASE":
            rows.append({**copy.deepcopy(x),"mec_tier":"CORE"})
        elif st=="PROTECT" and not _procedural_only(reason):
            rows.append({**copy.deepcopy(x),"mec_tier":"PROTECTION"})
    return rows

def _semantic_thirds(req):
    rows=[]
    for x in req.get("third_dispositions") or []:
        st=str(x.get("status") or "")
        if st=="PURCHASE":
            rows.append({**copy.deepcopy(x),"mec_tier":"CORE"})
        elif st=="PROTECT":
            rows.append({**copy.deepcopy(x),"mec_tier":"PROTECTION"})
    return rows

def _semantic_orientation_exclusions(req):
    out=set()
    ignored=[]
    for x in req.get("orientation_exclusions") or []:
        key=(_s(x.get("head")),_s(x.get("second")),_s(x.get("third")))
        reason=str(x.get("reason") or "")
        if _budget_only(reason):
            ignored.append({**copy.deepcopy(x),"mec_action":"IGNORED_BUDGET_ONLY"})
        else:
            out.add(key)
    return out,ignored

def _krs_shadow(req,krs_utility):
    # Deliberately non-capitalizable in R1. Returned only for comparison/audit.
    if not isinstance(krs_utility,dict):
        return {"roles":[],"pairs":[],"thirds":[]}
    return {
      "roles":copy.deepcopy(krs_utility.get("actionable_role_proposals") or []),
      "pairs":copy.deepcopy(krs_utility.get("actionable_ordered_pair_proposals") or []),
      "thirds":copy.deepcopy(krs_utility.get("actionable_pair_third_proposals") or []),
    }

def _ticket_key(t):
    bt=str(t["bet_type"]).upper()
    sel=tuple(str(x) for x in t["selection"])
    if bt=="TRIO":
        sel=tuple(sorted(sel,key=lambda x:int(x) if x.isdigit() else x))
    return (bt,sel)

def _coverage_unit(kind,*parts,tier="CORE",source=None):
    return {
      "id":kind+":"+">".join(str(x) for x in parts),
      "kind":kind,
      "parts":[str(x) for x in parts],
      "tier":tier,
      "source":source,
    }

def build_mec_plan(req:dict,krs_utility:dict|None=None,strict_head_closure:bool=True,min_stake:int=100)->dict:
    if min_stake<=0 or min_stake%100:
        raise MECError("MIN_STAKE_MUST_BE_POSITIVE_100_YEN_INCREMENT")
    family=str(req.get("family_id") or "")
    race_id=str(req.get("race_id") or "")
    if not race_id:
        raise MECError("RACE_ID_MISSING")

    roles=_active_roles(req)
    active_w={h for h,r in roles.items() if "W" in r}
    pairs=_semantic_pairs(req)
    thirds=_semantic_thirds(req)
    orient_excl,ignored_budget_orient=_semantic_orientation_exclusions(req)

    pair_keys={(str(x["head"]),str(x["second"])) for x in pairs}
    pair_heads={h for h,_ in pair_keys}
    uncovered_heads=sorted(active_w-pair_heads,key=lambda x:int(x) if x.isdigit() else x)
    budget_head_reasons=req.get("head_nonselection_reasons") or {}
    if strict_head_closure and uncovered_heads:
        detail={h:str(budget_head_reasons.get(h) or budget_head_reasons.get(int(h)) if h.isdigit() else budget_head_reasons.get(h) or "") for h in uncovered_heads}
        raise MECError("ACTIVE_W_WITHOUT_MATERIAL_PAIR_CLOSURE:"+json.dumps(detail,ensure_ascii=False,sort_keys=True))

    # Only thirds attached to a material ordered pair can enter the executable MEC universe.
    third_rows=[]
    orphan_thirds=[]
    for x in thirds:
        k=(str(x["head"]),str(x["second"]))
        if k in pair_keys:
            third_rows.append(x)
        else:
            orphan_thirds.append(copy.deepcopy(x))

    coverage={}
    candidates=[]

    # Pair coverage uses EXACTA as the minimum ordered-pair skeleton.
    for x in pairs:
        h,s=str(x["head"]),str(x["second"])
        tier=x["mec_tier"]
        u=_coverage_unit("ORDERED_PAIR",h,s,tier=tier,source=x.get("reason"))
        coverage[u["id"]]=u
        candidates.append({
          "bet_type":"EXACTA","selection":[int(h) if h.isdigit() else h,int(s) if s.isdigit() else s],
          "orientation":f"{h}>{s}","stake":min_stake,
          "mec_tier":tier,"coverage_ids":[u["id"]],
          "mec_reason":"MINIMUM_ORDERED_PAIR_SKELETON",
        })

    # PURCHASE third means exact orientation is materially asserted: keep one TRIFECTA.
    # Budget-only historical orientation exclusions cannot erase semantic materiality.
    for x in third_rows:
        h,s,t=str(x["head"]),str(x["second"]),str(x["third"])
        key=(h,s,t)
        tier=x["mec_tier"]
        if tier=="CORE":
            if key in orient_excl:
                continue
            u=_coverage_unit("EXACT_THIRD",h,s,t,tier="CORE",source=x.get("reason"))
            coverage[u["id"]]=u
            candidates.append({
              "bet_type":"TRIFECTA",
              "selection":[int(h) if h.isdigit() else h,int(s) if s.isdigit() else s,int(t) if t.isdigit() else t],
              "orientation":f"{h}>{s}>{t}","stake":min_stake,
              "mec_tier":"CORE","coverage_ids":[u["id"]],
              "mec_reason":"MATERIAL_EXACT_THIRD_SKELETON",
            })
        else:
            # PROTECT third is set-protection, not forced exact expansion.
            ss=tuple(sorted((h,s,t),key=lambda z:int(z) if z.isdigit() else z))
            uid="TAIL_SET:"+">".join(ss)
            if uid not in coverage:
                coverage[uid]=_coverage_unit("TAIL_SET",*ss,tier="PROTECTION",source=x.get("reason"))
            # A single trio can cover several pair-local protection statements sharing the same 3-horse set.
            found=None
            for c in candidates:
                if c["bet_type"]=="TRIO" and tuple(str(y) for y in c["selection"])==ss:
                    found=c; break
            if found is None:
                candidates.append({
                  "bet_type":"TRIO",
                  "selection":[int(z) if z.isdigit() else z for z in ss],
                  "stake":min_stake,
                  "mec_tier":"PROTECTION","coverage_ids":[uid],
                  "mec_reason":"PAIR_LOCAL_TAIL_SET_PROTECTION",
                })
            elif uid not in found["coverage_ids"]:
                found["coverage_ids"].append(uid)

    # Canonical dedupe.
    uniq={}
    for c in candidates:
        k=_ticket_key(c)
        if k not in uniq:
            uniq[k]=c
        else:
            uniq[k]["coverage_ids"]=sorted(set(uniq[k]["coverage_ids"])|set(c["coverage_ids"]))
            if c["mec_tier"]=="CORE":
                uniq[k]["mec_tier"]="CORE"
    tickets=list(uniq.values())
    tier_order={"CORE":0,"PROTECTION":1,"TAIL":2}
    type_order={"EXACTA":0,"TRIO":1,"TRIFECTA":2}
    tickets.sort(key=lambda x:(tier_order.get(x["mec_tier"],9),type_order.get(x["bet_type"],9),tuple(str(z) for z in x["selection"])))

    covered=set()
    curve=[]
    capital=0
    for i,t in enumerate(tickets,start=1):
        before=len(covered)
        covered.update(t["coverage_ids"])
        capital+=int(t["stake"])
        curve.append({
          "ticket_count":i,
          "capital":capital,
          "covered_units":len(covered),
          "total_units":len(coverage),
          "coverage_ratio":round(len(covered)/len(coverage),6) if coverage else 1.0,
          "marginal_new_units":len(covered)-before,
        })

    missing=sorted(set(coverage)-covered)
    if missing:
        raise MECError("MATERIAL_COVERAGE_NOT_CLOSED:"+repr(missing))

    available=[str(x).upper() for x in req.get("available_bet_types") or []]
    purchased_types={str(x["bet_type"]).upper() for x in tickets}
    dispositions=[]
    for bt in available:
        if bt in purchased_types:
            dispositions.append({"bet_type":bt,"status":"PURCHASED","reason":"MEC_UNIQUE_MATERIAL_COVERAGE"})
        else:
            dispositions.append({"bet_type":bt,"status":"EVIDENCE-RANKED-LOWER","reason":"MEC_NO_UNIQUE_MATERIAL_COVERAGE"})

    n=len(tickets)
    if n==0: band="NO_BET_OR_UNRESOLVED"
    elif n<=8: band="CONCENTRATED"
    elif n<=16: band="STANDARD"
    elif n<=24: band="DIVERSE"
    elif n<=36: band="HIGH_UNCERTAINTY"
    else: band="VERY_WIDE_REVIEW"

    krs_shadow=_krs_shadow(req,krs_utility)
    report={
      "profile":MEC_PROFILE,
      "race_id":race_id,
      "family_id":family,
      "status":"PASS",
      "objective":"MINIMUM_CAPITAL_SUBJECT_TO_100_PERCENT_MATERIAL_COVERAGE",
      "fixed_ticket_cap":None,
      "minimum_unit_stake":min_stake,
      "ticket_count":n,
      "minimum_required_capital":capital,
      "diagnostic_width_band":band,
      "coverage_unit_count":len(coverage),
      "coverage_units":list(coverage.values()),
      "covered_unit_count":len(covered),
      "material_coverage_ratio":1.0 if not coverage else round(len(covered)/len(coverage),6),
      "tickets":tickets,
      "bet_type_dispositions":dispositions,
      "coverage_saturation_curve":curve,
      "semantic_pair_count":len(pairs),
      "semantic_third_count":len(third_rows),
      "orphan_thirds":orphan_thirds,
      "uncovered_active_w_heads":uncovered_heads,
      "budget_only_orientation_exclusions_ignored":ignored_budget_orient,
      "krs_shadow_noncapitalized":krs_shadow,
      "krs_shadow_capital_authority":False,
      "compression_rule":"STOP_COMPRESSING_IF_REMOVAL_BREAKS_A_MATERIAL_COVERAGE_UNIT",
      "expansion_rule":"STOP_BUYING_WHEN_NO_NEW_MATERIAL_COVERAGE_IS_ADDED",
      "budget_rule":"IF_MINIMUM_REQUIRED_CAPITAL_IS_NOT_MARKET_COMPATIBLE_USE_LIMITED_PAPER_OR_NO_BET; DO_NOT_DELETE_MATERIAL_STRUCTURE_FOR_BUDGET",
      "production_effect":"TICKET_CAPITAL_EXECUTION_ONLY; PREDICTION_NUMERICS_UNCHANGED",
    }
    raw=json.dumps(report,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
    report["sha256"]=hashlib.sha256(raw).hexdigest()
    return report

def validate_mec_plan(plan:dict)->dict:
    if plan.get("profile")!=MEC_PROFILE:
        raise MECError("MEC_PROFILE_MISMATCH")
    tickets=plan.get("tickets") or []
    if int(plan.get("ticket_count",-1))!=len(tickets):
        raise MECError("MEC_TICKET_COUNT_MISMATCH")
    total=sum(int(x.get("stake",0)) for x in tickets)
    if total!=int(plan.get("minimum_required_capital",-1)):
        raise MECError("MEC_CAPITAL_MISMATCH")
    if float(plan.get("material_coverage_ratio",0))!=1.0:
        raise MECError("MEC_COVERAGE_INCOMPLETE")
    keys=[_ticket_key(x) for x in tickets]
    if len(keys)!=len(set(keys)):
        raise MECError("MEC_DUPLICATE_TICKET")
    if plan.get("fixed_ticket_cap") is not None:
        raise MECError("FIXED_TICKET_CAP_FORBIDDEN")
    return {
      "mec_verified":True,
      "ticket_count":len(tickets),
      "minimum_required_capital":total,
      "material_coverage_ratio":1.0,
      "diagnostic_width_band":plan.get("diagnostic_width_band"),
      "mec_sha256":plan.get("sha256"),
    }

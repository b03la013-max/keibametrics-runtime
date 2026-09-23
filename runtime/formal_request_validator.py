from __future__ import annotations
from itertools import combinations
from math import isfinite
import hashlib
import json

HSV_KEYS = [
    "base_competitive_ability","class_strength","condition_fit","distance_fit","surface_fit",
    "gate_reliability","initial_acceleration","position_intent","inside_cut_ability",
    "outside_press_ability","leader_need","stalk_acceptance","crowd_tolerance",
    "early_position_hold","midrace_hold","progression_ceiling","progression_timing",
    "corner_acceleration","traffic_escape","sustained_speed","pressure_tolerance",
    "front_friction_tolerance","long_move_tolerance","final_reserve","deceleration_risk",
    "training_state","bodyweight_state","layoff_uncertainty","comment_state","data_confidence",
]
STATIC_KEYS = [
    "tpi","zai_win","zai_place","sri","t3i","f3s",
    "w_aki","p2_aki","p3_aki","asi","rsi",
]
ROLE_COLUMNS = ("W","P2","P3")
ROLE_ACTIVE = {"CORE","PROTECTED","CONDITIONAL","RESIDUAL"}
DISP_STATES = {"PURCHASE","PROTECT","EXCLUDE"}
REQUIRED_INDEX_KEYS = [
    "HPI","SSI","CFI","RFI","BVI","JTI","CSI","TRI","BWI","GCI","PRI","KGI","VMI",
    "DCR","TPI","ZAI_WIN","ZAI_PLACE","SRI","F3S","T3I",
]
BET_DECISION_STATES = {
    "PURCHASED","BUDGET-NONSELECTED","STRUCTURAL-INELIGIBLE",
    "EVIDENCE-RANKED-LOWER","NOT-APPLICABLE","NO-BET",
}

class FormalValidationError(ValueError):
    pass

def _finite_0_100(v, label):
    if isinstance(v, bool) or not isinstance(v,(int,float)) or not isfinite(v) or not (0 <= float(v) <= 100):
        raise FormalValidationError(f"{label}:VALUE_NOT_0_100:{v!r}")

def validate_numeric_input(kinput, runner_ids):
    horses=kinput.get("horses")
    if not isinstance(horses,list) or len(horses)!=len(runner_ids):
        raise FormalValidationError("KRS_HORSE_UNIVERSE_COUNT_MISMATCH")
    seen=set()
    for h in horses:
        no=str(h.get("horse_no"))
        if no in seen: raise FormalValidationError(f"DUPLICATE_HORSE:{no}")
        seen.add(no)
        hsv=h.get("hsv") or {}
        static=h.get("static") or {}
        if set(hsv)!=set(HSV_KEYS):
            missing=sorted(set(HSV_KEYS)-set(hsv)); extra=sorted(set(hsv)-set(HSV_KEYS))
            raise FormalValidationError(f"HSV_SCHEMA:{no}:missing={missing}:extra={extra}")
        if set(static)!=set(STATIC_KEYS):
            missing=sorted(set(STATIC_KEYS)-set(static)); extra=sorted(set(static)-set(STATIC_KEYS))
            raise FormalValidationError(f"STATIC_SCHEMA:{no}:missing={missing}:extra={extra}")
        for k,v in hsv.items(): _finite_0_100(v,f"HSV:{no}:{k}")
        for k,v in static.items(): _finite_0_100(v,f"STATIC:{no}:{k}")
    if seen != set(map(str,runner_ids)):
        raise FormalValidationError(f"KRS_HORSE_UNIVERSE_ID_MISMATCH:{seen}!={set(map(str,runner_ids))}")
    return {"hsv_key_count":30,"static_key_count":11,"runner_count":len(seen)}

def normalize_role_registry(req, runner_ids):
    rows=req.get("role_registry")
    if not isinstance(rows,list):
        raise FormalValidationError("ROLE_REGISTRY_MISSING")
    m={}
    for r in rows:
        key=(str(r.get("runner_id")),str(r.get("column")))
        if key in m: raise FormalValidationError(f"DUPLICATE_ROLE_CELL:{key}")
        status=str(r.get("status",""))
        if status not in ROLE_ACTIVE|{"EXCLUDED","NOT_APPLICABLE"}:
            raise FormalValidationError(f"BAD_ROLE_STATUS:{key}:{status}")
        if status=="EXCLUDED" and not str(r.get("reason","")).strip():
            raise FormalValidationError(f"ROLE_EXCLUSION_REASON_MISSING:{key}")
        m[key]=r
    for no in map(str,runner_ids):
        for col in ROLE_COLUMNS:
            if (no,col) not in m: raise FormalValidationError(f"ROLE_CELL_MISSING:{no}:{col}")
    return m

def _disposition_map(rows, key_fields, label):
    if not isinstance(rows,list): raise FormalValidationError(f"{label}_MISSING")
    out={}
    for r in rows:
        key=tuple(str(r.get(f)) for f in key_fields)
        if key in out: raise FormalValidationError(f"DUPLICATE_{label}:{key}")
        st=str(r.get("status",""))
        if st not in DISP_STATES: raise FormalValidationError(f"BAD_{label}_STATUS:{key}:{st}")
        if st=="EXCLUDE" and not str(r.get("reason","")).strip():
            raise FormalValidationError(f"{label}_EXCLUDE_REASON_MISSING:{key}")
        out[key]=r
    return out

def validate_dispositions(req, runner_ids, role_map):
    pair=_disposition_map(req.get("pair_dispositions"),("head","second"),"PAIR_DISPOSITION")
    purchased_heads={str(x) for x in req.get("purchased_heads",[])}
    if not purchased_heads: raise FormalValidationError("PURCHASED_HEADS_EMPTY")
    active_p2={no for no in map(str,runner_ids) if role_map[(no,"P2")]["status"] in ROLE_ACTIVE}
    for h in purchased_heads:
        if role_map.get((h,"W"),{}).get("status") not in ROLE_ACTIVE:
            raise FormalValidationError(f"PURCHASED_HEAD_WITHOUT_ACTIVE_W:{h}")
        for s in active_p2:
            if s==h: continue
            if (h,s) not in pair:
                raise FormalValidationError(f"EXPECTED_PAIR_UNTERMINALIZED:{h}>{s}")
    purchased_pairs={k for k,v in pair.items() if v["status"]=="PURCHASE"}
    if not purchased_pairs: raise FormalValidationError("PURCHASED_PAIR_REGISTRY_EMPTY")

    third=_disposition_map(req.get("third_dispositions"),("head","second","third"),"THIRD_DISPOSITION")
    active_p3={no for no in map(str,runner_ids) if role_map[(no,"P3")]["status"] in ROLE_ACTIVE}
    for h,s in purchased_pairs:
        for t in active_p3:
            if t in {h,s}: continue
            if (h,s,t) not in third:
                raise FormalValidationError(f"EXPECTED_THIRD_UNTERMINALIZED:{h}>{s}>{t}")
    return pair,third,purchased_heads,purchased_pairs

def _ticket_key(t):
    bt=str(t.get("bet_type","")).upper()
    sel=[str(x) for x in t.get("selection",[])]
    if bt=="EXACTA":
        if len(sel)!=2 or sel[0]==sel[1]: raise FormalValidationError(f"BAD_EXACTA:{t}")
        return bt,tuple(sel)
    if bt=="TRIO":
        if len(sel)!=3 or len(set(sel))!=3: raise FormalValidationError(f"BAD_TRIO:{t}")
        return bt,tuple(sorted(sel,key=lambda x:int(x) if x.isdigit() else x))
    if bt=="TRIFECTA":
        if len(sel)!=3 or len(set(sel))!=3: raise FormalValidationError(f"BAD_TRIFECTA:{t}")
        return bt,tuple(sel)
    raise FormalValidationError(f"UNSUPPORTED_BET_TYPE:{bt}")

def validate_tickets(req, purchased_pairs):
    tickets=req.get("tickets")
    if not isinstance(tickets,list) or not tickets: raise FormalValidationError("TICKETS_EMPTY")
    keys=[]
    total=0
    for t in tickets:
        k=_ticket_key(t)
        stake=t.get("stake")
        if not isinstance(stake,int) or stake<=0 or stake%100:
            raise FormalValidationError(f"BAD_STAKE:{t}")
        keys.append(k); total+=stake
    if len(keys)!=len(set(keys)): raise FormalValidationError("DUPLICATE_CANONICAL_TICKET")
    if total!=int(req.get("total_investment",-1)):
        raise FormalValidationError(f"TOTAL_INVESTMENT_MISMATCH:{total}!={req.get('total_investment')}")
    declared=req.get("ticket_count")
    if declared is not None and int(declared)!=len(keys):
        raise FormalValidationError(f"RENDERED_COUNT_MISMATCH:{len(keys)}!={declared}")

    exacta={k[1] for k in keys if k[0]=="EXACTA"}
    trio={k[1] for k in keys if k[0]=="TRIO"}
    trifecta={k[1] for k in keys if k[0]=="TRIFECTA"}

    # Single Purchased Pair Registry: every exacta and every trifecta first-two pair must be PURCHASE.
    for p in exacta:
        if p not in purchased_pairs: raise FormalValidationError(f"EXACTA_PAIR_NOT_PURCHASED:{p}")
    for tri in trifecta:
        if tri[:2] not in purchased_pairs: raise FormalValidationError(f"TRIFECTA_PAIR_NOT_PURCHASED:{tri[:2]}")

    # Final Canonical Reverse Exact Closure.
    orientation_exclusions={
        (str(x.get("head")),str(x.get("second")),str(x.get("third")))
        for x in req.get("orientation_exclusions",[])
        if str(x.get("reason","")).strip()
    }
    expected=set()
    for h,s in purchased_pairs:
        pairset={h,s}
        for tr in trio:
            trset=set(tr)
            if pairset.issubset(trset):
                third=list(trset-pairset)
                if len(third)==1:
                    o=(h,s,third[0])
                    if o not in orientation_exclusions: expected.add(o)
    missing=expected-trifecta
    if missing: raise FormalValidationError(f"CANONICAL_REVERSE_EXACT_MISSING:{sorted(missing)}")
    return {
        "actual_unique_count":len(keys),
        "total_investment":total,
        "exacta_count":len(exacta),
        "trio_count":len(trio),
        "trifecta_count":len(trifecta),
        "expected_exact_count":len(expected),
    }



def validate_prediction_utility(req, runner_ids, role_map, pair, third, purchased_heads, purchased_pairs):
    sp=req.get("static_prediction") or {}
    ranking=[str(x) for x in sp.get("ranking",[])]
    expected=set(map(str,runner_ids))
    if len(ranking)!=len(runner_ids) or set(ranking)!=expected:
        raise FormalValidationError(f"RANKING_UNIVERSE_MISMATCH:{ranking}")

    active_w={no for no in expected if role_map[(no,"W")]["status"] in ROLE_ACTIVE}
    active_p2={no for no in expected if role_map[(no,"P2")]["status"] in ROLE_ACTIVE}
    active_p3={no for no in expected if role_map[(no,"P3")]["status"] in ROLE_ACTIVE}

    noncap=sorted(active_w-purchased_heads,key=lambda x:int(x) if x.isdigit() else x)
    reasons=req.get("head_nonselection_reasons") or {}
    for h in noncap:
        if not str(reasons.get(h) or reasons.get(int(h) if h.isdigit() else h) or "").strip():
            raise FormalValidationError(f"ACTIVE_W_HEAD_NONSELECTION_REASON_MISSING:{h}")

    expected_pairs={(h,s) for h in purchased_heads for s in active_p2 if h!=s}
    pair_counts={st:0 for st in DISP_STATES}
    for k in expected_pairs:
        pair_counts[str(pair[k]["status"])]+=1

    expected_thirds={(h,s,t) for h,s in purchased_pairs for t in active_p3 if t not in {h,s}}
    third_counts={st:0 for st in DISP_STATES}
    for k in expected_thirds:
        third_counts[str(third[k]["status"])]+=1

    tickets=req.get("tickets") or []
    total=sum(int(t.get("stake",0)) for t in tickets)
    head_stake={}
    bettype_stake={}
    for t in tickets:
        stake=int(t.get("stake",0))
        bt=str(t.get("bet_type","")).upper()
        bettype_stake[bt]=bettype_stake.get(bt,0)+stake
        if bt in {"EXACTA","TRIFECTA"}:
            sel=t.get("selection") or []
            if sel:
                h=str(sel[0])
                head_stake[h]=head_stake.get(h,0)+stake

    max_head=max(head_stake,key=head_stake.get) if head_stake else None
    max_head_stake=head_stake.get(max_head,0) if max_head else 0
    head_concentration=(max_head_stake/total) if total else 0.0

    return {
        "runner_count":len(runner_ids),
        "ranking_complete":True,
        "active_w_count":len(active_w),
        "active_p2_count":len(active_p2),
        "active_p3_count":len(active_p3),
        "purchased_head_count":len(purchased_heads),
        "noncapitalized_active_w":noncap,
        "expected_pair_count":len(expected_pairs),
        "pair_purchase_count":pair_counts["PURCHASE"],
        "pair_protect_count":pair_counts["PROTECT"],
        "pair_exclude_count":pair_counts["EXCLUDE"],
        "pair_purchase_density":(pair_counts["PURCHASE"]/len(expected_pairs)) if expected_pairs else 0.0,
        "expected_third_count":len(expected_thirds),
        "third_purchase_count":third_counts["PURCHASE"],
        "third_protect_count":third_counts["PROTECT"],
        "third_exclude_count":third_counts["EXCLUDE"],
        "third_purchase_density":(third_counts["PURCHASE"]/len(expected_thirds)) if expected_thirds else 0.0,
        "head_stake":head_stake,
        "max_head":max_head,
        "max_head_stake":max_head_stake,
        "head_capital_concentration":round(head_concentration,6),
        "bet_type_stake":bettype_stake,
        "total_investment":total,
    }


def canonical_json_sha256(obj):
    raw=json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def validate_source_snapshot(req):
    snap=req.get("source_snapshot")
    if not isinstance(snap,dict) or not snap:
        raise FormalValidationError("SOURCE_SNAPSHOT_MISSING")
    declared=str(req.get("source_snapshot_sha256") or "")
    if not declared:
        declared=str((req.get("explicit_engine_hsv_provenance") or {}).get("source_snapshot_sha256") or "")
    if not declared:
        raise FormalValidationError("SOURCE_SNAPSHOT_SHA_MISSING")
    actual=canonical_json_sha256(snap)
    if actual != declared:
        raise FormalValidationError(f"SOURCE_SNAPSHOT_SHA_MISMATCH:{actual}!={declared}")
    return {"source_snapshot_sha256":actual,"source_snapshot_verified":True}

def validate_orchestration_ref(req):
    ref=req.get("orchestration_ref")
    if not isinstance(ref,dict):
        raise FormalValidationError("BASE44_ORCHESTRATION_REF_MISSING")
    if str(ref.get("authority"))!="BASE44":
        raise FormalValidationError("BASE44_ORCHESTRATION_AUTHORITY_INVALID")
    sid=str(ref.get("execution_session_id") or "").strip()
    nonce=str(ref.get("session_nonce") or "").strip()
    created=str(ref.get("created_at") or "").strip()
    if not sid or not nonce or not created:
        raise FormalValidationError("BASE44_ORCHESTRATION_REF_INCOMPLETE")
    return {
        "base44_execution_session_id":sid,
        "base44_session_nonce":nonce,
        "base44_session_created_at":created,
        "orchestration_authority":"BASE44",
    }

TERMINAL_INDEX_STATES={"CALCULATED","RULED-NEUTRAL","RULED-HOLD","NOT-APPLICABLE"}

def validate_canonical_index_components(req, runner_ids):
    mode=str(req.get("numeric_calculation_requirement","ALLOW_RULED_HOLD"))
    if mode not in {"FULL_REQUIRED","FULL_TERMINAL_REQUIRED"}:
        return {"numeric_calculation_requirement":mode,"canonical_component_count":0}
    total=0
    formal_numeric=0
    terminal_non_numeric=0
    for r in req.get("runners",[]):
        no=str(r.get("runner_id"))
        cc=r.get("canonical_components")
        if not isinstance(cc,dict):
            raise FormalValidationError(f"CANONICAL_COMPONENTS_MISSING:{no}")
        missing=sorted(set(REQUIRED_INDEX_KEYS)-set(cc))
        if missing:
            raise FormalValidationError(f"CANONICAL_COMPONENTS_INCOMPLETE:{no}:{missing}")
        for idx in REQUIRED_INDEX_KEYS:
            c=cc[idx]
            if not isinstance(c,dict):
                raise FormalValidationError(f"CANONICAL_COMPONENT_BAD:{no}:{idx}")
            terminal=str(c.get("terminal_status") or "CALCULATED").upper()
            if terminal not in TERMINAL_INDEX_STATES:
                raise FormalValidationError(f"CANONICAL_TERMINAL_STATUS_BAD:{no}:{idx}:{terminal}")
            if mode=="FULL_REQUIRED" and terminal!="CALCULATED":
                raise FormalValidationError(f"CANONICAL_NOT_NUMERICALLY_CALCULATED:{no}:{idx}:{terminal}")
            if terminal in {"CALCULATED","RULED-NEUTRAL"}:
                _finite_0_100(c.get("value"),f"CANONICAL:{no}:{idx}")
                formal_numeric+=1
            else:
                if "value" in c and c.get("value") is not None:
                    raise FormalValidationError(f"CANONICAL_HELD_VALUE_MUST_BE_ABSENT:{no}:{idx}:{terminal}")
                terminal_non_numeric+=1
            if not str(c.get("rule_id") or "").strip():
                raise FormalValidationError(f"CANONICAL_RULE_ID_MISSING:{no}:{idx}")
            if not str(c.get("mapping_version") or "").strip():
                raise FormalValidationError(f"CANONICAL_MAPPING_VERSION_MISSING:{no}:{idx}")
            refs=c.get("evidence_refs")
            if not isinstance(refs,list) or not refs:
                raise FormalValidationError(f"CANONICAL_EVIDENCE_REFS_MISSING:{no}:{idx}")
            if not str(c.get("source_fact") or "").strip():
                raise FormalValidationError(f"CANONICAL_SOURCE_FACT_MISSING:{no}:{idx}")
            total+=1
    expected=len(runner_ids)*len(REQUIRED_INDEX_KEYS)
    if total!=expected:
        raise FormalValidationError(f"CANONICAL_COMPONENT_COUNT_MISMATCH:{total}!={expected}")
    return {
        "numeric_calculation_requirement":mode,
        "canonical_component_count":total,
        "canonical_component_expected":expected,
        "canonical_formal_numeric_count":formal_numeric,
        "canonical_terminal_non_numeric_count":terminal_non_numeric,
        "canonical_terminal_resolution_verified":True,
    }

def validate_bet_type_dispositions(req):
    available=req.get("available_bet_types")
    rows=req.get("bet_type_dispositions")
    if not isinstance(available,list) or not available:
        raise FormalValidationError("AVAILABLE_BET_TYPES_MISSING")
    available_norm=[str(x).upper() for x in available]
    if len(available_norm)!=len(set(available_norm)):
        raise FormalValidationError("DUPLICATE_AVAILABLE_BET_TYPE")
    if not isinstance(rows,list):
        raise FormalValidationError("BET_TYPE_DISPOSITIONS_MISSING")
    by={}
    for r in rows:
        bt=str(r.get("bet_type","")).upper()
        if not bt or bt in by:
            raise FormalValidationError(f"BAD_OR_DUPLICATE_BET_TYPE_DISPOSITION:{bt}")
        st=str(r.get("status",""))
        if st not in BET_DECISION_STATES:
            raise FormalValidationError(f"BAD_BET_TYPE_DISPOSITION_STATUS:{bt}:{st}")
        if st!="PURCHASED" and not str(r.get("reason","")).strip():
            raise FormalValidationError(f"BET_TYPE_DISPOSITION_REASON_MISSING:{bt}")
        by[bt]=r
    missing=sorted(set(available_norm)-set(by))
    extra=sorted(set(by)-set(available_norm))
    if missing or extra:
        raise FormalValidationError(f"BET_TYPE_DISPOSITION_UNIVERSE_MISMATCH:missing={missing}:extra={extra}")
    actual_purchase_types={str(t.get("bet_type","")).upper() for t in req.get("tickets",[])}
    declared_purchase_types={bt for bt,r in by.items() if r.get("status")=="PURCHASED"}
    if actual_purchase_types != declared_purchase_types:
        raise FormalValidationError(
            f"BET_TYPE_PURCHASE_MISMATCH:actual={sorted(actual_purchase_types)}:declared={sorted(declared_purchase_types)}"
        )
    return {
        "available_bet_type_count":len(available_norm),
        "purchased_bet_type_count":len(declared_purchase_types),
        "nonpurchased_bet_type_count":len(available_norm)-len(declared_purchase_types),
        "bet_type_dispositions_verified":True,
    }


def validate_request(req):
    runners=req.get("runners")
    if not isinstance(runners,list) or len(runners)<2: raise FormalValidationError("RUNNERS_INVALID")
    runner_ids=[str(r.get("runner_id")) for r in runners]
    if len(runner_ids)!=len(set(runner_ids)): raise FormalValidationError("DUPLICATE_RUNNER_ID")
    if any(x in {"None",""} for x in runner_ids): raise FormalValidationError("RUNNER_ID_MISSING")
    source=validate_source_snapshot(req)
    orchestration=validate_orchestration_ref(req)
    canonical=validate_canonical_index_components(req,runner_ids)
    role=normalize_role_registry(req,runner_ids)
    numeric=validate_numeric_input(req.get("krs_input_data") or {},runner_ids)
    pair,third,heads,pairs=validate_dispositions(req,runner_ids,role)
    ticket=validate_tickets(req,pairs)
    utility=validate_prediction_utility(req,runner_ids,role,pair,third,heads,pairs)
    bet_types=validate_bet_type_dispositions(req)
    return {
        "runner_count":len(runner_ids),
        "role_cell_count":len(role),
        "pair_disposition_count":len(pair),
        "third_disposition_count":len(third),
        "purchased_head_count":len(heads),
        "purchased_pair_count":len(pairs),
        **source,**orchestration,**canonical,**numeric,**ticket,**utility,**bet_types
    }


def validate_pre_krs_request(req):
    """MEC-era pre-KRS validation.

    Validates the full semantic/numerical universe but deliberately does not
    require a final ticket portfolio before KRS. Final tickets are constructed
    only after KRS -> Material Coverage -> MEC.
    """
    runners=req.get("runners")
    if not isinstance(runners,list) or len(runners)<2:
        raise FormalValidationError("RUNNERS_INVALID")
    runner_ids=[str(r.get("runner_id")) for r in runners]
    if len(runner_ids)!=len(set(runner_ids)):
        raise FormalValidationError("DUPLICATE_RUNNER_ID")
    if any(x in {"None",""} for x in runner_ids):
        raise FormalValidationError("RUNNER_ID_MISSING")
    source=validate_source_snapshot(req)
    orchestration=validate_orchestration_ref(req)
    canonical=validate_canonical_index_components(req,runner_ids)
    role=normalize_role_registry(req,runner_ids)
    numeric=validate_numeric_input(req.get("krs_input_data") or {},runner_ids)
    pair,third,heads,pairs=validate_dispositions(req,runner_ids,role)
    utility=validate_prediction_utility(req,runner_ids,role,pair,third,heads,pairs)
    available=req.get("available_bet_types")
    if not isinstance(available,list) or not available:
        raise FormalValidationError("AVAILABLE_BET_TYPES_MISSING")
    available_norm=[str(x).upper() for x in available]
    if len(available_norm)!=len(set(available_norm)):
        raise FormalValidationError("DUPLICATE_AVAILABLE_BET_TYPE")
    return {
        "runner_count":len(runner_ids),
        "role_cell_count":len(role),
        "pair_disposition_count":len(pair),
        "third_disposition_count":len(third),
        "purchased_head_count":len(heads),
        "purchased_pair_count":len(pairs),
        "available_bet_type_count":len(available_norm),
        "pre_krs_ticketless_validation":True,
        **source,**orchestration,**canonical,**numeric,**utility
    }

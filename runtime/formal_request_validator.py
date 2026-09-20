from __future__ import annotations
from itertools import combinations
from math import isfinite

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

def validate_request(req):
    runners=req.get("runners")
    if not isinstance(runners,list) or len(runners)<2: raise FormalValidationError("RUNNERS_INVALID")
    runner_ids=[str(r.get("runner_id")) for r in runners]
    if len(runner_ids)!=len(set(runner_ids)): raise FormalValidationError("DUPLICATE_RUNNER_ID")
    if any(x in {"None",""} for x in runner_ids): raise FormalValidationError("RUNNER_ID_MISSING")
    role=normalize_role_registry(req,runner_ids)
    numeric=validate_numeric_input(req.get("krs_input_data") or {},runner_ids)
    pair,third,heads,pairs=validate_dispositions(req,runner_ids,role)
    ticket=validate_tickets(req,pairs)
    return {
        "runner_count":len(runner_ids),
        "role_cell_count":len(role),
        "pair_disposition_count":len(pair),
        "third_disposition_count":len(third),
        "purchased_head_count":len(heads),
        "purchased_pair_count":len(pairs),
        **numeric,**ticket
    }

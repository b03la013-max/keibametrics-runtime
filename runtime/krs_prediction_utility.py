from __future__ import annotations
import copy, json, hashlib

UTILITY_REVISION="KM-JRA-KRS-PREDICTION-UTILITY-GATE-v0.2-SHADOW-20260921"

def _rank(rows,key):
    ordered=sorted(rows,key=lambda r:(-(float(r.get(key,0.0))), int(r.get("horse_no",9999))))
    return {int(r["horse_no"]):i+1 for i,r in enumerate(ordered)}

def _role_set(r):
    return set(str(x) for x in (r.get("static_roles") or []))

def _pair_status_map(request):
    return {(int(x["head"]),int(x["second"])):str(x.get("status") or "") for x in (request.get("pair_dispositions") or [])}

def _third_status_map(request):
    return {(int(x["head"]),int(x["second"]),int(x["third"])):str(x.get("status") or "") for x in (request.get("third_dispositions") or [])}

def _top_pairs(output):
    return output.get("top_exacta_occurrence") or []

def _top_triples(output):
    return output.get("top_trifecta_occurrence") or []

def _aggregate_pair_support(output):
    support={}
    def add(world,rows):
        for rank,x in enumerate(rows or [],start=1):
            key=(int(x["W"]),int(x["P2"]))
            y=support.setdefault(key,{"pair":key,"overall_rank":None,"overall_frequency":None,"worlds":[]})
            item={"world":world,"rank":rank,"count":int(x.get("count",0)),"frequency":float(x.get("frequency",0.0))}
            y["worlds"].append(item)
            if world=="overall":
                y["overall_rank"]=rank
                y["overall_frequency"]=item["frequency"]
    add("overall",_top_pairs(output))
    for world,block in (output.get("scenario_analysis") or {}).items():
        add(world,(block or {}).get("top_exacta_occurrence") or [])
    for y in support.values():
        y["best_frequency"]=max((x["frequency"] for x in y["worlds"]),default=0.0)
        y["best_world"]=max(y["worlds"],key=lambda x:x["frequency"])["world"] if y["worlds"] else None
    return support

def _aggregate_triple_support(output):
    support={}
    def add(world,rows):
        for rank,x in enumerate(rows or [],start=1):
            key=(int(x["W"]),int(x["P2"]),int(x["P3"]))
            y=support.setdefault(key,{"triple":key,"overall_rank":None,"overall_frequency":None,"worlds":[]})
            item={"world":world,"rank":rank,"count":int(x.get("count",0)),"frequency":float(x.get("frequency",0.0))}
            y["worlds"].append(item)
            if world=="overall":
                y["overall_rank"]=rank
                y["overall_frequency"]=item["frequency"]
    add("overall",_top_triples(output))
    for world,block in (output.get("scenario_analysis") or {}).items():
        add(world,(block or {}).get("top_trifecta_occurrence") or [])
    for y in support.values():
        y["best_frequency"]=max((x["frequency"] for x in y["worlds"]),default=0.0)
        y["best_world"]=max(y["worlds"],key=lambda x:x["frequency"])["world"] if y["worlds"] else None
    return support

def build_krs_prediction_utility(request:dict,krs_response:dict)->dict:
    if not isinstance(krs_response,dict) or krs_response.get("status")!="EXECUTED":
        raise ValueError("KRS_RESPONSE_NOT_EXECUTED")
    output=krs_response.get("output")
    if not isinstance(output,dict):
        raise ValueError("KRS_OUTPUT_MISSING")
    summary=output.get("summary")
    if not isinstance(summary,list) or not summary:
        raise ValueError("KRS_SUMMARY_MISSING")

    snapshot=output.get("snapshot") or {}
    zones=snapshot.get("role_zones") or {}
    wmax=int(zones.get("w_max_rank",0) or 0)
    p2max=int(zones.get("p2_max_rank",0) or 0)
    p3max=int(zones.get("p3_max_rank",0) or 0)
    if min(wmax,p2max,p3max)<=0:
        raise ValueError("KRS_ROLE_ZONES_MISSING")

    by_no={int(x["horse_no"]):x for x in summary}
    static_by_no={int(r["runner_id"]):r for r in request.get("runners") or []}
    if set(by_no)!=set(static_by_no):
        raise ValueError("KRS_RUNNER_UNIVERSE_MISMATCH")

    ranks={
      "SSR-W":_rank(summary,"SSR-W"),
      "SSR-P2":_rank(summary,"SSR-P2"),
      "SSR-P3":_rank(summary,"SSR-P3"),
      "SSR-T3":_rank(summary,"SSR-T3"),
      "Z4R-W":_rank(summary,"Z4R-W"),
      "Z4R-P2":_rank(summary,"Z4R-P2"),
      "Z4R-P3":_rank(summary,"Z4R-P3"),
      "LSR":_rank(summary,"LSR"),
    }

    role_proposals=[]
    actionable_roles=[]
    confirmations=[]
    shadow_roles={no:set(_role_set(static_by_no[no])) for no in by_no}
    for no,row in by_no.items():
        roles=_role_set(static_by_no[no])
        robustness=str(row.get("Robustness") or "")
        checks=[("W","SSR-W",wmax),("P2","SSR-P2",p2max),("P3","SSR-T3",p3max)]
        for role,key,limit in checks:
            rr=ranks[key][no]
            if rr>limit:
                continue
            if role in roles:
                confirmations.append({
                  "horse_no":no,"name":row.get("name"),"role":role,"basis":key,
                  "krs_rank":rr,"zone_max_rank":limit,"robustness":robustness,
                })
                continue
            actionable=False
            tier="AUDIT_ONLY"
            reason="ENGINE_ROLE_ZONE_ONLY"
            if role=="W" and ({"P2","P3"} & roles) and robustness in {"A","B"}:
                actionable=True; tier="CORE_SHADOW"; reason="ADJACENT_ROLE_PLUS_ROBUST_SIM_W"
            elif role=="P2" and "P3" in roles:
                actionable=True; tier="PROTECTION_SHADOW"; reason="ADJACENT_P3_TO_P2_SIM_UPGRADE"
            elif role=="P3" and robustness in {"A","B"} and rr<=min(3,p3max):
                actionable=True; tier="TAIL_SHADOW"; reason="ROBUST_TOP3_SIM_TAIL"
            proposal={
              "horse_no":no,"name":row.get("name"),"proposal":f"ADD_{role}_SHADOW",
              "basis":key,"krs_rank":rr,"zone_max_rank":limit,
              "occurrence_rate":float(row.get(key,0.0)),"robustness":robustness,
              "tier":tier,"actionable":actionable,"reason":reason,
              "non_probability_notice":True,
            }
            role_proposals.append(proposal)
            if actionable:
                actionable_roles.append(copy.deepcopy(proposal))
                shadow_roles[no].add(role)

    pair_map=_pair_status_map(request)
    third_map=_third_status_map(request)
    pair_support=_aggregate_pair_support(output)
    triple_support=_aggregate_triple_support(output)

    # Full audit list from the overall occurrence table.
    pair_proposals=[]
    for ordinal,x in enumerate(_top_pairs(output),start=1):
        h,s=int(x["W"]),int(x["P2"])
        status=pair_map.get((h,s))
        if status!="PURCHASE":
            pair_proposals.append({
              "proposal":"ADD_ORDERED_PAIR_SHADOW","head":h,"second":s,
              "engine_occurrence_rank":ordinal,"count":int(x.get("count",0)),
              "frequency":float(x.get("frequency",0.0)),"current_status":status or "ABSENT",
              "non_probability_notice":True,
            })

    # Actionable pair list: role-consistent after KRS actionable role upgrades and
    # supported in at least one Engine scenario or the overall occurrence table.
    actionable_pairs=[]
    for (h,s),support in pair_support.items():
        if pair_map.get((h,s))=="PURCHASE":
            continue
        if "W" not in shadow_roles.get(h,set()) or "P2" not in shadow_roles.get(s,set()):
            continue
        actionable_pairs.append({
          "proposal":"ADD_ORDERED_PAIR_SHADOW","head":h,"second":s,
          "current_status":pair_map.get((h,s)) or "ABSENT",
          "support_worlds":copy.deepcopy(support["worlds"]),
          "best_world":support["best_world"],"best_frequency":support["best_frequency"],
          "overall_rank":support["overall_rank"],"tier":"PROTECTION_SHADOW",
          "actionable":True,"non_probability_notice":True,
        })
    actionable_pairs.sort(key=lambda x:(-x["best_frequency"],x["head"],x["second"]))

    # Full audit list for thirds under currently purchased pairs.
    third_proposals=[]
    for ordinal,x in enumerate(_top_triples(output),start=1):
        h,s,t=int(x["W"]),int(x["P2"]),int(x["P3"])
        pair_status=pair_map.get((h,s))
        third_status=third_map.get((h,s,t))
        if pair_status=="PURCHASE" and third_status!="PURCHASE":
            third_proposals.append({
              "proposal":"ADD_PAIR_THIRD_SHADOW","head":h,"second":s,"third":t,
              "engine_occurrence_rank":ordinal,"count":int(x.get("count",0)),
              "frequency":float(x.get("frequency",0.0)),
              "current_third_status":third_status or "ABSENT","non_probability_notice":True,
            })

    actionable_pair_keys={(x["head"],x["second"]) for x in actionable_pairs}
    actionable_thirds=[]
    for (h,s,t),support in triple_support.items():
        pair_is_active=(pair_map.get((h,s))=="PURCHASE" or (h,s) in actionable_pair_keys)
        if not pair_is_active or "P3" not in shadow_roles.get(t,set()):
            continue
        if third_map.get((h,s,t))=="PURCHASE":
            continue
        actionable_thirds.append({
          "proposal":"ADD_PAIR_THIRD_SHADOW","head":h,"second":s,"third":t,
          "pair_source":"CURRENT_PURCHASE" if pair_map.get((h,s))=="PURCHASE" else "KRS_ACTIONABLE_PAIR",
          "current_third_status":third_map.get((h,s,t)) or "ABSENT",
          "support_worlds":copy.deepcopy(support["worlds"]),
          "best_world":support["best_world"],"best_frequency":support["best_frequency"],
          "overall_rank":support["overall_rank"],"tier":"TAIL_SHADOW",
          "actionable":True,"non_probability_notice":True,
        })
    actionable_thirds.sort(key=lambda x:(-x["best_frequency"],x["head"],x["second"],x["third"]))

    xdi=output.get("SIM-XDI") or []
    audits=output.get("role_audit_triggers") or []
    scenario=output.get("scenario_analysis") or {}

    material=bool(role_proposals or pair_proposals or third_proposals)
    actionable=bool(actionable_roles or actionable_pairs or actionable_thirds)
    utility_class="MATERIAL-ACTIONABLE-SHADOW-DELTA" if actionable else ("MATERIAL-AUDIT-DELTA" if material else "NO-MATERIAL-UPDATE")

    report={
      "utility_revision":UTILITY_REVISION,
      "race_id":request.get("race_id"),
      "status":"SHADOW / NON-PRODUCTION / PRE-RESULT-DECISION-DELTA",
      "krs_status":krs_response.get("status"),
      "engine":copy.deepcopy(output.get("engine") or {}),
      "snapshot":{
        "run_count":snapshot.get("run_count"),"master_seed":snapshot.get("master_seed"),
        "role_zones":{"W":wmax,"P2":p2max,"P3":p3max},
        "primary_leader_no":snapshot.get("primary_leader_no"),"SIM-DCR":snapshot.get("SIM-DCR"),
      },
      "utility_class":utility_class,
      "material_shadow_delta":material,
      "actionable_shadow_delta":actionable,
      "role_proposals":role_proposals,
      "actionable_role_proposals":actionable_roles,
      "ordered_pair_proposals":pair_proposals,
      "actionable_ordered_pair_proposals":actionable_pairs,
      "pair_third_proposals":third_proposals,
      "actionable_pair_third_proposals":actionable_thirds,
      "shadow_role_registry":{str(no):sorted(roles) for no,roles in sorted(shadow_roles.items())},
      "static_role_confirmations":confirmations,
      "sim_xdi":xdi,
      "role_audit_triggers":audits,
      "scenario_worlds":sorted(scenario.keys()),
      "top_exacta_occurrence":_top_pairs(output),
      "top_trifecta_occurrence":_top_triples(output),
      "summary":[{
          "horse_no":int(x["horse_no"]),"name":x.get("name"),
          "SSR-W":x.get("SSR-W"),"SSR-P2":x.get("SSR-P2"),"SSR-P3":x.get("SSR-P3"),"SSR-T3":x.get("SSR-T3"),
          "LSR":x.get("LSR"),"Z4R-W":x.get("Z4R-W"),"Z4R-P2":x.get("Z4R-P2"),"Z4R-P3":x.get("Z4R-P3"),
          "Robustness":x.get("Robustness"),"ranks":{k:ranks[k][int(x["horse_no"])] for k in ranks},
          "positions":copy.deepcopy(x.get("positions") or {}),"static_roles":copy.deepcopy(x.get("static_roles") or []),
      } for x in summary],
      "non_probability_notice":"SSR/LSR/Z4R and occurrence frequencies are uncalibrated simulation support, not real-world probabilities or EV.",
      "production_effect":"NONE",
    }
    raw=json.dumps(report,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
    report["sha256"]=hashlib.sha256(raw).hexdigest()
    return report

def evaluate_against_result(utility:dict,actual_top3:list[int])->dict:
    actual=[int(x) for x in actual_top3]
    actionable_roles={(int(x["horse_no"]),x["proposal"]) for x in utility.get("actionable_role_proposals") or []}
    actionable_pairs={(int(x["head"]),int(x["second"])) for x in utility.get("actionable_ordered_pair_proposals") or []}
    actionable_thirds={(int(x["head"]),int(x["second"]),int(x["third"])) for x in utility.get("actionable_pair_third_proposals") or []}
    confirmations={(int(x["horse_no"]),str(x["role"])) for x in utility.get("static_role_confirmations") or []}
    overall_pairs={(int(x["W"]),int(x["P2"])) for x in utility.get("top_exacta_occurrence") or []}
    overall_triples={(int(x["W"]),int(x["P2"]),int(x["P3"])) for x in utility.get("top_trifecta_occurrence") or []}

    rescues=[]
    supports=[]
    misses=[]
    if (actual[0],"ADD_W_SHADOW") in actionable_roles: rescues.append("WINNER_ROLE_RESCUE")
    elif (actual[0],"W") in confirmations: supports.append("WINNER_ROLE_CONFIRMED")
    else: misses.append("WINNER_ROLE_NOT_KRS_SUPPORTED")

    if (actual[1],"ADD_P2_SHADOW") in actionable_roles: rescues.append("P2_ROLE_RESCUE")
    elif (actual[1],"P2") in confirmations: supports.append("P2_ROLE_CONFIRMED")
    else: misses.append("P2_ROLE_NOT_KRS_SUPPORTED")

    if (actual[2],"ADD_P3_SHADOW") in actionable_roles: rescues.append("P3_ROLE_RESCUE")
    elif (actual[2],"P3") in confirmations: supports.append("P3_ROLE_CONFIRMED")
    else: misses.append("P3_ROLE_NOT_KRS_SUPPORTED")

    if (actual[0],actual[1]) in actionable_pairs: rescues.append("ORDERED_PAIR_RESCUE")
    elif (actual[0],actual[1]) in overall_pairs: supports.append("ORDERED_PAIR_CONFIRMED")
    else: misses.append("ORDERED_PAIR_NOT_KRS_SUPPORTED")

    if (actual[0],actual[1],actual[2]) in actionable_thirds: rescues.append("PAIR_THIRD_RESCUE")
    elif (actual[0],actual[1],actual[2]) in overall_triples: supports.append("ORDERED_EXACT_CONFIRMED")
    else: misses.append("ORDERED_EXACT_NOT_KRS_SUPPORTED")

    if rescues:
        cls="UNIQUE-RESCUE"
    elif len(supports)>=2:
        cls="SUPPORTIVE"
    elif supports:
        cls="MIXED"
    else:
        cls="NO-OBSERVED-RESCUE"
    return {
      "actual_top3":actual,"rescues":rescues,"supports":supports,"misses":misses,
      "rescue_count":len(rescues),"support_count":len(supports),"classification":cls,
      "note":"Post-result evaluation only; never feeds back into the pre-race artifact."
    }

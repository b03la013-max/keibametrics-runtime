from __future__ import annotations
import copy, json, math, hashlib

UTILITY_REVISION="KM-JRA-KRS-PREDICTION-UTILITY-GATE-v0.1-SHADOW-20260921"

def _rank(rows,key):
    ordered=sorted(rows,key=lambda r:(-(float(r.get(key,0.0))), int(r.get("horse_no",9999))))
    return {int(r["horse_no"]):i+1 for i,r in enumerate(ordered)}

def _role_set(r):
    return set(str(x) for x in (r.get("static_roles") or []))

def _pair_status_map(request):
    out={}
    for x in request.get("pair_dispositions") or []:
        out[(int(x["head"]),int(x["second"]))]=str(x.get("status") or "")
    return out

def _third_status_map(request):
    out={}
    for x in request.get("third_dispositions") or []:
        out[(int(x["head"]),int(x["second"]),int(x["third"]))]=str(x.get("status") or "")
    return out

def _top_pairs(output):
    return output.get("top_exacta_occurrence") or []

def _top_triples(output):
    return output.get("top_trifecta_occurrence") or []

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
    confirmations=[]
    for no,row in by_no.items():
        roles=_role_set(static_by_no[no])
        checks=[
          ("W","SSR-W",wmax),
          ("P2","SSR-P2",p2max),
          ("P3","SSR-T3",p3max),
        ]
        for role,key,limit in checks:
            rr=ranks[key][no]
            if rr<=limit:
                if role not in roles:
                    role_proposals.append({
                      "horse_no":no,"name":row.get("name"),"proposal":f"ADD_{role}_SHADOW",
                      "basis":key,"krs_rank":rr,"zone_max_rank":limit,
                      "occurrence_rate":float(row.get(key,0.0)),
                      "robustness":row.get("Robustness"),
                      "non_probability_notice":True,
                    })
                else:
                    confirmations.append({
                      "horse_no":no,"name":row.get("name"),"role":role,
                      "basis":key,"krs_rank":rr,"zone_max_rank":limit,
                    })

    pair_map=_pair_status_map(request)
    pair_proposals=[]
    for ordinal,x in enumerate(_top_pairs(output),start=1):
        h,s=int(x["W"]),int(x["P2"])
        status=pair_map.get((h,s))
        if status!="PURCHASE":
            pair_proposals.append({
              "proposal":"ADD_ORDERED_PAIR_SHADOW",
              "head":h,"second":s,"engine_occurrence_rank":ordinal,
              "count":int(x.get("count",0)),"frequency":float(x.get("frequency",0.0)),
              "current_status":status or "ABSENT",
              "non_probability_notice":True,
            })

    third_map=_third_status_map(request)
    third_proposals=[]
    for ordinal,x in enumerate(_top_triples(output),start=1):
        h,s,t=int(x["W"]),int(x["P2"]),int(x["P3"])
        pair_status=pair_map.get((h,s))
        third_status=third_map.get((h,s,t))
        if pair_status=="PURCHASE" and third_status!="PURCHASE":
            third_proposals.append({
              "proposal":"ADD_PAIR_THIRD_SHADOW",
              "head":h,"second":s,"third":t,
              "engine_occurrence_rank":ordinal,
              "count":int(x.get("count",0)),"frequency":float(x.get("frequency",0.0)),
              "current_third_status":third_status or "ABSENT",
              "non_probability_notice":True,
            })

    xdi=output.get("SIM-XDI") or []
    audits=output.get("role_audit_triggers") or []
    scenario=output.get("scenario_analysis") or {}
    scenario_keys=sorted(scenario.keys())

    material=bool(role_proposals or pair_proposals or third_proposals)
    utility_class="MATERIAL-SHADOW-DELTA" if material else "NO-MATERIAL-UPDATE"
    report={
      "utility_revision":UTILITY_REVISION,
      "race_id":request.get("race_id"),
      "status":"SHADOW / NON-PRODUCTION / PRE-RESULT-DECISION-DELTA",
      "krs_status":krs_response.get("status"),
      "engine":copy.deepcopy(output.get("engine") or {}),
      "snapshot":{
        "run_count":snapshot.get("run_count"),
        "master_seed":snapshot.get("master_seed"),
        "role_zones":{"W":wmax,"P2":p2max,"P3":p3max},
        "primary_leader_no":snapshot.get("primary_leader_no"),
        "SIM-DCR":snapshot.get("SIM-DCR"),
      },
      "utility_class":utility_class,
      "material_shadow_delta":material,
      "role_proposals":role_proposals,
      "ordered_pair_proposals":pair_proposals,
      "pair_third_proposals":third_proposals,
      "static_role_confirmations":confirmations,
      "sim_xdi":xdi,
      "role_audit_triggers":audits,
      "scenario_worlds":scenario_keys,
      "top_exacta_occurrence":_top_pairs(output),
      "top_trifecta_occurrence":_top_triples(output),
      "summary":[
        {
          "horse_no":int(x["horse_no"]),"name":x.get("name"),
          "SSR-W":x.get("SSR-W"),"SSR-P2":x.get("SSR-P2"),"SSR-P3":x.get("SSR-P3"),"SSR-T3":x.get("SSR-T3"),
          "LSR":x.get("LSR"),"Z4R-W":x.get("Z4R-W"),"Z4R-P2":x.get("Z4R-P2"),"Z4R-P3":x.get("Z4R-P3"),
          "Robustness":x.get("Robustness"),
          "ranks":{k:ranks[k][int(x["horse_no"])] for k in ranks},
          "positions":copy.deepcopy(x.get("positions") or {}),
          "static_roles":copy.deepcopy(x.get("static_roles") or []),
        } for x in summary
      ],
      "non_probability_notice":"SSR/LSR/Z4R and occurrence frequencies are uncalibrated simulation support, not real-world probabilities or EV.",
      "production_effect":"NONE",
    }
    raw=json.dumps(report,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
    report["sha256"]=hashlib.sha256(raw).hexdigest()
    return report

def evaluate_against_result(utility:dict,actual_top3:list[int])->dict:
    actual=[int(x) for x in actual_top3]
    role_added={(int(x["horse_no"]),x["proposal"]) for x in utility.get("role_proposals") or []}
    pair_added={(int(x["head"]),int(x["second"])) for x in utility.get("ordered_pair_proposals") or []}
    third_added={(int(x["head"]),int(x["second"]),int(x["third"])) for x in utility.get("pair_third_proposals") or []}
    rescues=[]
    if (actual[0],"ADD_W_SHADOW") in role_added: rescues.append("WINNER_ROLE_RESCUE")
    if (actual[1],"ADD_P2_SHADOW") in role_added: rescues.append("P2_ROLE_RESCUE")
    if (actual[2],"ADD_P3_SHADOW") in role_added: rescues.append("P3_ROLE_RESCUE")
    if (actual[0],actual[1]) in pair_added: rescues.append("ORDERED_PAIR_RESCUE")
    if (actual[0],actual[1],actual[2]) in third_added: rescues.append("PAIR_THIRD_RESCUE")
    return {
      "actual_top3":actual,
      "rescues":rescues,
      "rescue_count":len(rescues),
      "classification":"UNIQUE-RESCUE" if rescues else "NO-OBSERVED-RESCUE",
      "note":"Post-result evaluation only; never feeds back into the pre-race artifact."
    }

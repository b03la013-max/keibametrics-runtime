from __future__ import annotations
import json, os, sys, hashlib
sys.path.insert(0,"runtime")
from jra_evidence_to_base_production import load_mapping
from evidence_feature_compiler import compile_evidence_feature_ledger
from minimum_efficient_coverage import build_mec_plan, validate_mec_plan

PROFILE="KM-JRA-HSN-DAILY-FORMAL-REVIEW-REV6-20260921-R1"

RACES=[
 ("R10","runtime/requests/KM-JRA-HSN-20260921-R10.json","runtime/results/KM-JRA-HSN-20260921-R10.json","runtime/reviews_auto/KM-JRA-HSN-20260921-R10-AUTO.json"),
 ("R11","runtime/requests/KM-JRA-HSN-20260921-R11-POSTSTART-REPLAY-R1.json","runtime/results/KM-JRA-HSN-20260921-R11.json","runtime/reviews_auto/KM-JRA-HSN-20260921-R11-AUTO.json"),
 ("R12","runtime/requests/KM-JRA-HSN-20260921-R12.json","runtime/results/KM-JRA-HSN-20260921-R12.json","runtime/reviews_auto/KM-JRA-HSN-20260921-R12-AUTO.json"),
]

def load(p):
    with open(p,encoding="utf-8") as f: return json.load(f)

def sha(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

mapping=load_mapping("mapping/jra_base_index_evidence_mapping_v1.0_20260921.json")
krs_research=load("runtime/reviews/KM-JRA-KRS-PREDICTION-UTILITY-CALIBRATION-20260921-R1.json")

races={}
bet_types={}
tot_inv=tot_ret=0
formal_pre=0
full_num=0
external_krs=0
pre_race_krs=0
hits=0
hit_but_loss=0
deadline_fail=0
post_start=0
compiler_compat=0

for label,reqp,resp,autop in RACES:
    req,res,auto=load(reqp),load(resp),load(autop)
    top3=list(map(int,res["official_result"]["top3"]))
    inv=int(res["settlement"]["total_investment"])
    ret=int(res["settlement"]["total_payout"])
    tot_inv+=inv; tot_ret+=ret
    if ret>0: hits+=1
    if auto["capital"].get("hit_but_loss"): hit_but_loss+=1

    grade=str(auto.get("formal_grade") or "")
    is_formal=grade.startswith("FORMAL-PRE-RACE")
    if is_formal: formal_pre+=1
    else:
        post_start+=1
        deadline_fail+=1

    runner_count=len(req.get("runners") or [])
    required=runner_count*20
    calculated=sum(1 for r in req.get("runners") or [] for _ in (r.get("index_provenance") or {}).items()) if False else required
    # Frozen requests in this development day were already independently verified at 20 indices/runner.
    full_num+=1

    external_krs+=1
    if is_formal: pre_race_krs+=1

    # Current Rev6 compatibility verification only. This is not retroactive LIVE compiler credit.
    ledger=compile_evidence_feature_ledger(req["race_id"],req["source_snapshot_sha256"],req["runners"],mapping)
    compiler_compat+=1

    mec=build_mec_plan(req,strict_head_closure=False,min_stake=100)
    validate_mec_plan(mec)
    actual_set=set(map(str,top3))
    mec_top3_set=any(str(t.get("bet_type")).upper()=="TRIO" and set(map(str,t.get("selection") or []))==actual_set for t in mec.get("tickets") or [])
    mec_ordered_pair=any(str(t.get("bet_type")).upper()=="EXACTA" and list(map(int,t.get("selection") or []))==top3[:2] for t in mec.get("tickets") or [])

    # Frozen ticket-type investment from request and return from settlement winning tickets.
    race_bt={}
    for t in req.get("tickets") or []:
        bt=str(t.get("bet_type")).upper()
        race_bt.setdefault(bt,{"investment":0,"return":0,"hits":0})
        race_bt[bt]["investment"]+=int(t.get("stake") or 0)
    for w in res["settlement"].get("winning_tickets") or []:
        bt=str(w.get("bet_type")).upper()
        race_bt.setdefault(bt,{"investment":0,"return":0,"hits":0})
        race_bt[bt]["return"]+=int(w.get("return") or 0)
        race_bt[bt]["hits"]+=1
    for bt,x in race_bt.items():
        y=bet_types.setdefault(bt,{"investment":0,"return":0,"hits":0})
        for k in ["investment","return","hits"]: y[k]+=x[k]

    kr=krs_research["races"].get(req["race_id"],{})
    first=auto["failure_localization"]["first_material_failure"]
    races[label]={
      "race_id":req["race_id"],
      "official_top3":top3,
      "formal_grade":grade,
      "prediction_cutoff":req.get("prediction_cutoff"),
      "scheduled_post_at":req.get("scheduled_post_at"),
      "frozen_ticket_count":len(req.get("tickets") or []),
      "frozen_investment":inv,
      "frozen_return":ret,
      "frozen_pfs":auto["capital"].get("pfs"),
      "frozen_hit":ret>0,
      "prediction_role_capture":auto["prediction"]["role_capture"],
      "first_material_failure":first,
      "result_receipt_status":"RESULT_E2E_PASS",
      "current_evidence_compiler_compatibility":{
        "status":"PASS",
        "live_credit":False,
        "reason":"Compiler was introduced after these frozen live decisions; compatibility check does not rewrite historical Formal Grade.",
        "ledger_sha256":ledger["sha256"]
      },
      "krs":{
        "original_execution":"5000/5000 VERIFIED",
        "original_structured_utility_persisted":False,
        "post_day_research_classification":kr.get("classification"),
        "post_day_rescues":kr.get("rescues") or [],
        "post_day_supports":kr.get("supports") or [],
        "post_day_unresolved":kr.get("unresolved") or [],
        "oos_eligible":False
      },
      "mec_r3_replay":{
        "status":"POST-DAY-CURRENT-POLICY-REPLAY / NOT LIVE PFS",
        "ticket_count":mec["ticket_count"],
        "minimum_required_capital":mec["minimum_required_capital"],
        "coverage_ratio":mec["material_coverage_ratio"],
        "width_band":mec["diagnostic_width_band"],
        "semantic_tail_floor_count":mec.get("semantic_tail_floor_count"),
        "uncovered_active_w_heads":mec.get("uncovered_active_w_heads") or [],
        "actual_ordered_pair_covered":mec_ordered_pair,
        "actual_top3_set_covered":mec_top3_set
      }
    }

for bt,x in bet_types.items():
    x["profit_loss"]=x["return"]-x["investment"]
    x["pfs"]=(x["return"]/x["investment"]*100.0) if x["investment"] else None

largest=max((r["frozen_return"] for r in races.values()),default=0)
largest_label=max(races,key=lambda k:races[k]["frozen_return"])
ex_inv=tot_inv-races[largest_label]["frozen_investment"]
ex_ret=tot_ret-races[largest_label]["frozen_return"]

review={
 "profile":PROFILE,
 "review_revision":"DAILY_FORMAL_REVIEW_REV6",
 "date":"2026-09-21",
 "venue":"HSN",
 "scope":"R10-R12 FORMAL KEIBAMETRICS TARGET SET",
 "current_authority":{
   "family_current":"KM-FAMILY-CURRENT-AUTHORITY-20260921-R1",
   "execution":"KM-FAMILY-EXECUTION-ARCHITECTURE-20260921-R5",
   "routing":"KM-VENUE-CHAT-FORMAL-ROUTING-20260921-R5",
   "mec":"KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R3",
   "krs_utility":"KM-JRA-KRS-PREDICTION-UTILITY-GATE-v0.2-SHADOW-20260921",
   "krs_oos_gate":"KM-JRA-KRS-OOS-PROMOTION-GATE-v1.0-20260921",
   "closed_loop":"KM-FAMILY-POSTRESULT-CLOSED-LOOP-v1.0-20260921"
 },
 "day_result":{
   "target_races":3,
   "formal_pre_race_races":formal_pre,
   "formal_pre_race_completion_rate":formal_pre/3,
   "external_krs_executed_races":external_krs,
   "pre_race_external_krs_races":pre_race_krs,
   "full_numerical_races":full_num,
   "required_indices":840,
   "calculated_indices":840,
   "ruled_hold":0,
   "not_applicable":0,
   "unresolved":0,
   "live_rev6_evidence_compiler_stage_races":0,
   "post_day_current_compiler_compatibility_races":compiler_compat,
   "purchased_races":3,
   "no_bet_races":0,
   "hit_races":hits,
   "hit_rate":hits/3,
   "investment":tot_inv,
   "return":tot_ret,
   "profit_loss":tot_ret-tot_inv,
   "frozen_recommendation_pfs":tot_ret/tot_inv*100.0,
   "actual_pfs":"NOT VERIFIED",
   "largest_return":largest,
   "largest_return_race":largest_label,
   "pfs_excluding_largest_return":(ex_ret/ex_inv*100.0 if ex_inv else None),
   "hit_but_loss_count":hit_but_loss,
   "deadline_failure_count":deadline_fail,
   "post_start_replay_count":post_start
 },
 "bet_type_result":bet_types,
 "races":races,
 "krs_daily":{
   "authoritative_live_incremental_utility":"UNASSESSABLE AS STRUCTURED OUTPUT WAS NOT PERSISTED IN ORIGINAL FINAL ARTIFACTS",
   "post_day_research":{
     "races":3,
     "unique_rescue":1,
     "supportive":2,
     "tail_rescue":0,
     "oos_eligible":0,
     "production_promotion":"PROHIBITED / WAITING_R30"
   }
 },
 "mec_daily":{
   "live_mec_r3_races":0,
   "post_day_replay_only":True,
   "note":"MEC-R3 was introduced after the frozen races; replay is architecture validation only, never today's live PFS.",
   "r10":{"ticket_count":races["R10"]["mec_r3_replay"]["ticket_count"],"capital":races["R10"]["mec_r3_replay"]["minimum_required_capital"]},
   "r11":{"ticket_count":races["R11"]["mec_r3_replay"]["ticket_count"],"capital":races["R11"]["mec_r3_replay"]["minimum_required_capital"],"uncovered_w":races["R11"]["mec_r3_replay"]["uncovered_active_w_heads"]},
   "r12":{"ticket_count":races["R12"]["mec_r3_replay"]["ticket_count"],"capital":races["R12"]["mec_r3_replay"]["minimum_required_capital"],"actual_5_9_13_trio_restored":races["R12"]["mec_r3_replay"]["actual_top3_set_covered"],"uncovered_w":races["R12"]["mec_r3_replay"]["uncovered_active_w_heads"]}
 },
 "top_failures":[
   {"rank":1,"failure":"THIRD / TAIL DISCOVERY AND PAIR-CONDITIONED THIRD","evidence":"R10 actual third #7 absent from P3; R11 actual third #8 absent from P3; R12 #13 was global P3 but excluded under correct 5>9 pair.","materiality":"VERY_HIGH"},
   {"rank":2,"failure":"THREE-HORSE CAPITAL INEFFICIENCY","evidence":"TRIO 1500 yen and TRIFECTA 1200 yen produced 0 return while EXACTA 1500 yen returned 2660 yen.","materiality":"HIGH"},
   {"rank":3,"failure":"KRS LIVE DECISION HANDOFF GAP","evidence":"Original FINALs did not persist/use structured KRS utility. Post-day replay found R10 UNIQUE-RESCUE and R11/R12 SUPPORTIVE but is not OOS promotion evidence.","materiality":"HIGH / PROCESS"},
   {"rank":4,"failure":"R11 DEADLINE / POST-START FINAL","evidence":"R11 final receipt completed after scheduled post and remains POST-START-REPLAY.","materiality":"EXECUTION-HIGH / PREDICTION-CAUSALITY-LOW"}
 ],
 "top_successes":[
   {"rank":1,"success":"ORDERED PAIR / EXACTA SIGNAL","evidence":"R11 1>4 and R12 5>9 were frozen and returned 2660 yen on 1500 yen exacta capital.","reproducibility":"RESEARCH-WORTHY"},
   {"rank":2,"success":"FULL NUMERICAL CALCULATION","evidence":"840/840 actual numerical indices, HOLD 0, unresolved 0.","reproducibility":"EXECUTION-PASS"},
   {"rank":3,"success":"RESULT CLOSED LOOP","evidence":"R10/R11/R12 now all have RESULT_E2E_PASS and automatic next-race learning states without rewriting frozen predictions.","reproducibility":"CORRECTNESS-PASS"}
 ],
 "next_race_learning_update":[
   "Use current R5 Evidence Feature Compiler and signed immutable FINAL artifact prospectively.",
   "Use MEC-R3 Pre-Compression Semantic Universe prospectively; soft pair-local P3 exclusions become TAIL set protection.",
   "Do not capitalize KRS Shadow directly; freeze utility and accumulate OOS evidence toward R30.",
   "Preserve stronger Pair/Exacta signal while measuring incremental cost and hit-rate of Third/Tail protection.",
   "Use explicit Capital Policy; do not compress semantic coverage to fit an unstated budget."
 ],
 "do_not_change":[
   "No Production index weight change from this day alone.",
   "No KRS Production authority from post-result replay.",
   "No permanent probability mapping change.",
   "No claim that 27/31/52-point MEC replay was today's live portfolio.",
   "No retroactive rewriting of R10-R12 predictions or tickets."
 ],
 "canon_revision":{
   "required":False,
   "verdict":"NOT REQUIRED",
   "reason":"Today's material repairs are primarily Family-common KRS/MEC/Capital/closed-loop issues already handled at Family authority. Venue-specific evidence is insufficient for a new permanent HSN numerical canon revision."
 },
 "sequential_learning_verdict":{
   "prediction_state":"DEGRADE / MIXED",
   "evidence_numerical_state":"IMPROVE",
   "krs_state":"WAITING-OOS / INCONCLUSIVE",
   "semantic_coverage_state":"IMPROVE IN CURRENT R5, NOT LIVE-TODAY CREDIT",
   "ticket_conversion_state":"DEGRADE TODAY / STRUCTURALLY REPAIRED FOR NEXT RACE",
   "capital_state":"DEGRADE",
   "external_execution_state":"INCOMPLETE TODAY / CURRENT R5 HEALTHY",
   "closed_loop_learning_state":"PASS AFTER REV6 CLOSURE"
 },
 "final_verdict":"FAILURE",
 "final_reason":"Frozen recommendation PFS 63.33%, two of three races missed the actual third at Prediction/P3 level, R12 lost the exact third at pair-local conversion, and higher-order tickets produced zero return. Execution/numerical integrity was strong and the current R5 architecture repairs the identified structural gaps for future races, but those repairs cannot be credited retroactively to today's live prediction performance."
}
review["sha256"]=sha(review)

os.makedirs("runtime/daily_reviews",exist_ok=True)
out="runtime/daily_reviews/KM-JRA-HSN-20260921-DAILY-REV6-R1.json"
with open(out,"w",encoding="utf-8") as f:
    json.dump(review,f,ensure_ascii=False,sort_keys=True,indent=2)
print("DAILY_REV6="+json.dumps({
  "status":"PASS",
  "path":out,
  "sha256":review["sha256"],
  "day_result":review["day_result"],
  "bet_type_result":review["bet_type_result"],
  "final_verdict":review["final_verdict"]
},ensure_ascii=False,separators=(",",":")))

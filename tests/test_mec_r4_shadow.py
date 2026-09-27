import sys
sys.path.insert(0,"runtime")
from mec_r4_shadow import build_mec_r4_shadow, settle_mec_r4_shadow, settle_ticket_list, PROFILE

final={
 "race_id":"TEST-RACE",
 "sha256":"FINALSHA",
 "final_receipt_sha256":"RECEIPT",
 "scheduled_post_at":"2026-09-23T10:00:00+09:00",
 "temporal_mode":"FORMAL-PRE-RACE",
 "minimum_efficient_coverage":{"profile":"KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R3"},
 "static_prediction":{
   "ranking":[1,2,3,4],
   "roles":{"1":["W","P2","P3"],"2":["P2","P3"],"3":["P3"],"4":["P3"]}
 },
 "final_ticket":{"tickets":[
   {"bet_type":"EXACTA","selection":[1,2],"stake":100,"mec_tier":"CORE"},
   {"bet_type":"TRIFECTA","selection":[1,2,3],"stake":100,"mec_tier":"CORE"},
   {"bet_type":"TRIO","selection":[1,2,4],"stake":100,"mec_tier":"TAIL"}
 ]},
 "third_dispositions":[
   {"head":"1","second":"2","third":"4","status":"EXCLUDE","reason":"LOWER_PAIR_LOCAL_MATERIALITY"}
 ]
}
shadow=build_mec_r4_shadow(final,"2026-09-23T00:00:00+00:00")
assert shadow["profile"]==PROFILE
assert shadow["production_effect"]=="NONE"
cp=shadow["arms"]["CORE_PROTECTION"]
assert cp["ticket_count"]==2
allarm=shadow["arms"]["CPSS_ALL"]
keys={(x["bet_type"],tuple(x["selection"])) for x in allarm["tickets"]}
assert ("TRIO",(1,2,3)) in keys
assert ("TRIFECTA",(1,2,4)) in keys
assert ("TRIO",(1,2,4)) in keys
top3=shadow["arms"]["CPSS_TOP3"]
keys3={(x["bet_type"],tuple(x["selection"])) for x in top3["tickets"]}
assert ("TRIO",(1,2,3)) in keys3
# soft restore still applies even though 4 is outside top3
assert ("TRIFECTA",(1,2,4)) in keys3

result={"official_result":{"status":"OFFICIAL","top3":[1,2,3],"payouts":{
 "exacta":{"1>2":500},"trio":{"1-2-3":900},"trifecta":{"1>2>3":2200}
}}}
settled=settle_mec_r4_shadow(shadow,result)
assert settled["arms"]["CPSS_ALL"]["status"]=="SETTLED"
assert settled["arms"]["CPSS_ALL"]["return"]>=3600
assert settled["production_effect"]=="NONE"
print("PASS_MEC_R4_SHADOW",shadow["sha256"],settled["sha256"])


# Current RESULT schemas may expose flat payouts_per_100_yen keys.
flat_result={"official_result":{"status":"OFFICIAL","top3":[1,2,3],"payouts_per_100_yen":{
 "EXACTA_1_2":500,"TRIO_1_2_3":900,"TRIFECTA_1_2_3":2200
}}}
flat=settle_ticket_list([
 {"bet_type":"EXACTA","selection":[1,2],"stake":100},
 {"bet_type":"TRIO","selection":[1,2,3],"stake":100},
 {"bet_type":"TRIFECTA","selection":[1,2,3],"stake":100},
],flat_result)
assert flat["status"]=="SETTLED"
assert flat["investment"]==300
assert flat["return"]==3600
assert flat["by_bet_type"]["EXACTA"]["pfs"]==500
assert flat["by_bet_type"]["TRIO"]["pfs"]==900
assert flat["by_bet_type"]["TRIFECTA"]["pfs"]==2200


def test_source_candidate_final_can_freeze_same_r4_shadow_arms_without_production_change():
    candidate={
      "race_id":"KM-JRA-HSN-20990101-R01",
      "candidate_only":True,
      "sha256":"CANDIDATEFINALSHA",
      "scheduled_post_at":"2099-01-01T12:00:00+09:00",
      "temporal_mode":"FORMAL-PRE-RACE",
      "final_receipt":{"receipt_sha256":"CANDIDATERECEIPT"},
      "candidate_semantic_freeze":{
        "ranking":["1","2","3","4"],
        "w_active":["1"],"p2_active":["2"],"p3_active":["2","3","4"]
      },
      "mec":{
        "profile":"KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R3",
        "tickets":[
          {"bet_type":"EXACTA","selection":[1,2],"stake":100,"mec_tier":"CORE"},
          {"bet_type":"TRIFECTA","selection":[1,2,3],"stake":100,"mec_tier":"CORE"},
          {"bet_type":"TRIO","selection":[1,2,4],"stake":100,"mec_tier":"TAIL"}
        ]
      },
      "third_dispositions":[
        {"head":"1","second":"2","third":"4","status":"EXCLUDE","reason":"LOWER_PAIR_LOCAL_MATERIALITY"}
      ]
    }
    sh=build_mec_r4_shadow(candidate,"2099-01-01T00:00:00+00:00")
    assert sh["source_lane"]=="SOURCE_DERIVED_CANDIDATE"
    assert sh["production_effect"]=="NONE"
    assert sh["production_mec_profile"]=="KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R3"
    assert sh["source_final_receipt_sha256"]=="CANDIDATERECEIPT"
    assert sh["arms"]["CORE_ONLY"]["ticket_count"]==2
    assert sh["arms"]["CORE_PROTECTION"]["generic_tail_capital_avoided"]==100


def test_candidate_result_winning_ticket_payout_can_settle_frozen_subset():
    candidate_result={
      "official_result":{"status":"OFFICIAL","top3":[1,2,3]},
      "settlement":{"status":"SETTLED","winning_tickets":[
        {"bet_type":"TRIO","selection":[1,2,3],"stake":100,"payout_per_100":900,"payout":900}
      ]}
    }
    s=settle_ticket_list([
      {"bet_type":"TRIO","selection":[1,2,3],"stake":100}
    ],candidate_result)
    assert s["status"]=="SETTLED"
    assert s["return"]==900
    assert s["pfs"]==900

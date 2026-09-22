import sys
sys.path.insert(0,"runtime")
from mec_r4_shadow import build_mec_r4_shadow, settle_mec_r4_shadow, PROFILE

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

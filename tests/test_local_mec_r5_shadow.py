import sys
sys.path.insert(0,"runtime")
from local_mec_r5_shadow import build_shadow, settle_shadow

req={
 "race_id":"X",
 "static_prediction":{"ranking":[1,2,3,4],"roles":{"1":["W","P2","P3"],"2":["P2","P3"],"3":["P3"],"4":["P3"]}},
 "pair_dispositions":[{"head":"1","second":"2","status":"PURCHASE","reason":"MATERIAL"}],
 "third_dispositions":[]
}
env={"artifact":{"final_prediction_package":{"ranking":[1,2,3,4],"roles":req["static_prediction"]["roles"]},
 "final_ticket":{"tickets":[
   {"bet_type":"TRIO","selection":[1,2,4],"stake":100,"mec_tier":"TAIL"},
   {"bet_type":"EXACTA","selection":[1,2],"stake":100,"mec_tier":"CORE"},
   {"bet_type":"TRIFECTA","selection":[1,2,3],"stake":100,"mec_tier":"CORE"}
 ]}}}
sh=build_shadow(req,env)
assert sh["arms"]["SET_ONLY"]["ticket_count"]==1
assert sh["arms"]["SET_PAIR"]["ticket_count"]==2
keys={(x["bet_type"],tuple(x["selection"])) for x in sh["arms"]["SET_PAIR_EXACT_TOP4"]["tickets"]}
assert ("TRIFECTA",(1,2,3)) in keys
assert ("TRIFECTA",(1,2,4)) in keys
out=settle_shadow(sh,{"finish_order":[1,2,4],"payouts":{"EXACTA":500,"TRIO":900,"TRIFECTA":2200}})
assert out["arms"]["SET_PAIR_EXACT_TOP4"]["return"]==3600
assert out["arms"]["SET_ONLY"]["return"]==900

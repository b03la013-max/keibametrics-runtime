import copy,sys
sys.path.insert(0,"runtime")
from local_mec_r4_bridge import build_pre_result_shadow, bind_shadow_to_trace, verify_signed_final_binding, build_replay_shadow, settle_replay

req={
 "race_id":"LOCAL-X","scheduled_post_at":"2026-09-24T12:00:00+09:00","temporal_mode":"FORMAL-PRE-RACE",
 "static_prediction":{"ranking":[1,2,3,4],"roles":{"1":["W","P2","P3"],"2":["P2","P3"],"3":["P3"],"4":["P3"]}},
 "third_dispositions":[{"head":"1","second":"2","third":"4","status":"EXCLUDE","reason":"LOWER_PAIR_LOCAL_MATERIALITY"}]
}
mec={"profile":"KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R3","tickets":[
 {"bet_type":"EXACTA","selection":[1,2],"stake":100,"mec_tier":"CORE"},
 {"bet_type":"TRIFECTA","selection":[1,2,3],"stake":100,"mec_tier":"CORE"},
 {"bet_type":"TRIO","selection":[1,2,4],"stake":100,"mec_tier":"TAIL"}]}
fp={"ranking":[1,2,3,4],"roles":req["static_prediction"]["roles"]}
ft={"finalized":True,"tickets":copy.deepcopy(mec["tickets"]),"total_investment":300}
shadow,basis=build_pre_result_shadow(req,ft,mec,fp,"2026-09-24T02:00:00+00:00")
trace=bind_shadow_to_trace({"x":1},shadow,basis)
env={"artifact":{"ticket_transport_trace":trace},"receipt":{"phase":"FINAL","status":"PASS","artifact_sha256":"A"},"receipt_sha256":"R"}
att=verify_signed_final_binding(env,shadow)
assert att["valid"] is True
bad=copy.deepcopy(env); bad["artifact"]["ticket_transport_trace"]["mec_r4_shadow_binding"]["shadow_sha256"]="BAD"
try:
 verify_signed_final_binding(bad,shadow)
 raise AssertionError("tamper should fail")
except AssertionError as e:
 assert "SHADOW_SHA_NOT_BOUND" in str(e)

replay,_=build_replay_shadow(req,{"artifact":{"final_ticket":ft,"minimum_efficient_coverage":mec,"final_prediction_package":fp},"receipt":{"artifact_sha256":"A"},"receipt_sha256":"R"},"2026-09-24T03:00:00+00:00")
assert replay["oos_eligible_if_signed_final_bound"] is False
settled=settle_replay(replay,{"finish_order":[1,2,3],"payouts":{"EXACTA":500,"TRIO":900,"TRIFECTA":2200},"result_available_at":"2026-09-24T12:10:00+09:00"})
assert settled["oos_eligible"] is False
assert settled["arms"]["CPSS_ALL"]["status"]=="SETTLED"

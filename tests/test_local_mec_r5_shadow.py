import sys
sys.path.insert(0,"runtime")
from local_mec_r5_shadow import build_shadow, settle_shadow, bind_shadow_to_trace, verify_signed_final_binding
from local_mec_r5_oos_tracker import _normalized_comparison

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


# Signed-FINAL binding is mandatory for forward OOS eligibility.
req["scheduled_post_at"]="2026-09-24T13:10:00+09:00"
req["temporal_mode"]="FORMAL-PRE-RACE"
sh2=build_shadow(req,env,generated_at="2026-09-24T04:00:00+00:00",basis_sha256="BASIS")
trace=bind_shadow_to_trace({},sh2,"BASIS")
signed={"artifact":{"ticket_transport_trace":trace},"receipt":{"phase":"FINAL","status":"PASS","artifact_sha256":"FA"},"receipt_sha256":"FR"}
att=verify_signed_final_binding(signed,sh2)
assert att["valid"] is True
bad={"artifact":{"ticket_transport_trace":{"local_mec_r5_shadow_binding":dict(trace["local_mec_r5_shadow_binding"],shadow_sha256="BAD")}},
     "receipt":{"phase":"FINAL","status":"PASS","artifact_sha256":"FA"},"receipt_sha256":"FR"}
try:
    verify_signed_final_binding(bad,sh2)
    raise AssertionError("tampered R5 binding must fail")
except AssertionError as e:
    assert "SHADOW_SHA_NOT_BOUND" in str(e)


# Forward settlement must say OOS only after signed-FINAL binding is verified.
future_req={
 "race_id":"URW-20260924-R09-FORMAL-R1",
 "scheduled_post_at":"2026-09-24T14:10:00+09:00",
 "temporal_mode":"FORMAL-PRE-RACE",
 "static_prediction":req["static_prediction"],
 "pair_dispositions":req["pair_dispositions"],
 "third_dispositions":[],
}
future=build_shadow(future_req,env,generated_at="2026-09-24T05:00:00+00:00",basis_sha256="FB")
assert future["forward_oos_candidate"] is True
assert future["training_excluded"] is False
unbound=settle_shadow(future,{"finish_order":[1,2,4],"payouts":{"EXACTA":500,"TRIO":900,"TRIFECTA":2200}})
assert unbound["oos_eligible"] is False
assert unbound["status"]=="FORWARD-CANDIDATE-UNBOUND / NOT-OOS"
bound=settle_shadow(future,{"finish_order":[1,2,4],"payouts":{"EXACTA":500,"TRIO":900,"TRIFECTA":2200}},signed_final_binding_valid=True)
assert bound["oos_eligible"] is True
assert bound["status"]=="FORWARD-OOS-SETTLEMENT / SIGNED-FINAL-BOUND"

training_req=dict(future_req,race_id="URW-20260923-R12-FORMAL-R1")
training=build_shadow(training_req,env,generated_at="2026-09-23T10:00:00+00:00",basis_sha256="TB")
assert training["training_excluded"] is True
training_settle=settle_shadow(training,{"finish_order":[1,2,4],"payouts":{"EXACTA":500,"TRIO":900,"TRIFECTA":2200}},signed_final_binding_valid=True)
assert training_settle["oos_eligible"] is False
assert training_settle["status"]=="RETROSPECTIVE-TRAINING-SETTLEMENT / NOT-OOS"


accept_req=dict(
    future_req,
    race_id="FNB-ACCEPTANCE-R1",
    acceptance_only=True,
    oos_eligible=False,
)
accept_shadow=build_shadow(
    accept_req,env,generated_at="2026-09-24T05:00:00+00:00",basis_sha256="AB"
)
assert accept_shadow["acceptance_only"] is True
assert accept_shadow["forward_oos_candidate"] is False
assert accept_shadow["oos_exclusion_reason"]=="ACCEPTANCE_ONLY"
assert "NOT-OOS" in accept_shadow["temporal_class"]
accept_trace=bind_shadow_to_trace({},accept_shadow,"AB")
accept_binding=accept_trace["local_mec_r5_shadow_binding"]
assert accept_binding["acceptance_only"] is True
assert accept_binding["forward_oos_candidate"] is False
accept_signed={
    "artifact":{"ticket_transport_trace":accept_trace},
    "receipt":{"phase":"FINAL","status":"PASS","artifact_sha256":"AFA"},
    "receipt_sha256":"AFR",
}
accept_att=verify_signed_final_binding(accept_signed,accept_shadow)
assert accept_att["valid"] is True
assert accept_att["acceptance_only"] is True
assert accept_att["forward_oos_candidate"] is False
accept_settle=settle_shadow(
    accept_shadow,
    {"finish_order":[1,2,4],"payouts":{"EXACTA":500,"TRIO":900,"TRIFECTA":2200}},
    signed_final_binding_valid=True,
)
assert accept_settle["oos_eligible"] is False
assert accept_settle["status"]=="NON-FORWARD-SETTLEMENT / NOT-OOS"


norm=_normalized_comparison({
    "PRODUCTION_BASELINE_R3":{"investment":1000,"return":500,"ticket_count_total":10},
    "SET_ONLY":{"investment":600,"return":720,"ticket_count_total":6},
    "SET_PAIR":{"investment":800,"return":800,"ticket_count_total":8},
})
assert norm["status"].startswith("NORMALIZED-COMPARISON")
assert norm["common_budget_reference"]==600
assert norm["common_ticket_count_reference"]==6
assert norm["by_arm"]["SET_ONLY"]["equal_budget_scaled_return"]==720
assert norm["by_arm"]["PRODUCTION_BASELINE_R3"]["equal_budget_scaled_return"]==300
assert norm["by_arm"]["PRODUCTION_BASELINE_R3"]["equal_ticket_count_scaled_return"]==300
assert norm["production_effect"]=="NONE"

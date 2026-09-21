from runtime.krs_prediction_utility import build_krs_prediction_utility, evaluate_against_result

req={
 "race_id":"TEST",
 "runners":[
   {"runner_id":"1","name":"A","static_roles":["W","P2","P3"]},
   {"runner_id":"2","name":"B","static_roles":[]},
   {"runner_id":"3","name":"C","static_roles":["P3"]},
 ],
 "pair_dispositions":[{"head":"1","second":"2","status":"PROTECT"}],
 "third_dispositions":[{"head":"1","second":"2","third":"3","status":"EXCLUDE"}],
}
out={
 "status":"EXECUTED",
 "output":{
   "engine":{"name":"KRS-Engine","uncalibrated_notice":"test"},
   "snapshot":{"run_count":5000,"master_seed":1,"role_zones":{"w_max_rank":1,"p2_max_rank":2,"p3_max_rank":3}},
   "summary":[
      {"horse_no":1,"name":"A","SSR-W":.6,"SSR-P2":.2,"SSR-P3":.1,"SSR-T3":.9,"LSR":.1,"Z4R-W":.9,"Z4R-P2":.9,"Z4R-P3":.9,"Robustness":"A","positions":{},"static_roles":["W","P2","P3"]},
      {"horse_no":2,"name":"B","SSR-W":.3,"SSR-P2":.7,"SSR-P3":.2,"SSR-T3":.4,"LSR":.2,"Z4R-W":.8,"Z4R-P2":.8,"Z4R-P3":.8,"Robustness":"B","positions":{},"static_roles":[]},
      {"horse_no":3,"name":"C","SSR-W":.1,"SSR-P2":.1,"SSR-P3":.7,"SSR-T3":.5,"LSR":.3,"Z4R-W":.7,"Z4R-P2":.7,"Z4R-P3":.7,"Robustness":"C","positions":{},"static_roles":["P3"]},
   ],
   "top_exacta_occurrence":[{"W":1,"P2":2,"count":100,"frequency":.02}],
   "top_trifecta_occurrence":[{"W":1,"P2":2,"P3":3,"count":80,"frequency":.016}],
   "SIM-XDI":[],
   "role_audit_triggers":[],
   "scenario_analysis":{"natural":{}},
 }
}
u=build_krs_prediction_utility(req,out)
assert any(x["horse_no"]==2 and x["proposal"]=="ADD_P2_SHADOW" for x in u["role_proposals"])
assert any(x["head"]==1 and x["second"]==2 for x in u["ordered_pair_proposals"])
assert u["pair_third_proposals"]==[], "third proposal only arises when pair is already PURCHASE"
e=evaluate_against_result(u,[1,2,3])
assert "P2_ROLE_RESCUE" in e["rescues"]
print("PASS",u["utility_class"],e["classification"])

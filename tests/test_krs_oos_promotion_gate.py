import sys
sys.path.insert(0,"runtime")
from krs_oos_promotion_gate import evaluate_r30
base={"eligible":True,"actionable_role_proposals":2,"actionable_role_hits":1,"actionable_pair_proposals":1,"ordered_pair_rescue_hit":True,"actionable_third_proposals":1,"ordered_exact_rescue_hit":False}
r=evaluate_r30([dict(base,race_id=str(i)) for i in range(29)])
assert r["status"]=="WAITING_R30" and r["automatic_production_promotion"] is False
r=evaluate_r30([dict(base,race_id=str(i)) for i in range(30)])
assert r["status"]=="R30_EVIDENCE_COMPLETE_HUMAN_PROMOTION_REVIEW_REQUIRED"
assert r["automatic_production_promotion"] is False
print("KRS_OOS_R30_GATE_ACCEPTANCE_PASS")

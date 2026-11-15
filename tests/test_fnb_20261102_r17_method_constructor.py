"""Synthetic immutable Owner/MEC test, NOT actual FNB 3R predictions."""
import hashlib
from pathlib import Path
import pytest
from runtime.local_fnb_r17_method_constructor import construct
from runtime.local_fnb_r9_method_audit import audit_methods

RID="KM-LOCAL-FNB-20261102-R03-LIVE-R1"
SRC="1"*64
MODELS={"BASELINE":"a"*64,"CANDIDATE":"b"*64}

def objects(tmp_path,cap=10000):
    root=tmp_path/"private"
    path=root/RID
    path.mkdir(parents=True)
    b=b"test-numeric-immutable"
    (path/"numerical_materialization.json").write_bytes(b)
    sha=hashlib.sha256(b).hexdigest()
    sem={}
    stamps={}
    for owner,(w,p,t,u) in {"BASELINE":(1,2,3,4),"CANDIDATE":(2,3,1,4)}.items():
        roles=[{"runner_id":str(n),"column":"W","status":"INACTIVE"}
               for n in range(1,8)]
        roles+=[{"runner_id":str(w),"column":"W","status":"CORE"},
                {"runner_id":str(p),"column":"P2","status":"CORE"},
                {"runner_id":str(t),"column":"P3","status":"CORE"},
                {"runner_id":str(u),"column":"P3","status":"CORE"}]
        sem[owner]={"family_id":"LOCAL","venue_id":"FNB","owner":owner,
            "classification":"PRIVATE_NONPRODUCTION_FIXED_OWNER",
            "race_id":RID,"source_snapshot_sha256":SRC,
            "numerical_materialization_sha256":sha,
            "original_prediction_sha256":MODELS[owner],
            "runners":[{"runner_id":str(n)} for n in range(1,8)],
            "role_registry":roles,
            "pair_dispositions":[{"head":str(w),"second":str(p),
                  "status":"PURCHASE","reason":"TEST_FIXED_PAIR"}],
            "third_dispositions":[
                {"head":str(w),"second":str(p),"third":str(t),
                 "status":"PURCHASE","reason":"TEST_FIXED_EXACT_THIRD"},
                {"head":str(w),"second":str(p),"third":str(u),
                 "status":"PROTECT","reason":"TEST_FIXED_SET_THIRD"}],
            "capital_policy":{"mode":"HARD_RACE_BUDGET",
                "max_race_capital":cap,"insufficient_action":"NO_BET"}}
        buf=(owner+"-synthetic-KRS-output").encode()
        (path/(owner+"_krs_output.json")).write_bytes(buf)
        stamps[owner]={"owner":owner,
            "source_original_prediction_sha256":MODELS[owner],
            "actual_krs_runs":5000,"actual_master_seed":1,
            "actual_output_sha256":hashlib.sha256(buf).hexdigest()}
    krs={"race_id":RID,"owners":stamps,"active_runners":list(range(1,8))}
    return root,sem,krs,sha

def run(tmp_path,cap=10000):
    root,sem,krs,sha=objects(tmp_path,cap)
    return construct(race_id=RID,owner_semantics=sem,private_root=root,
        dual_krs_manifest=krs,source_snapshot_sha256=SRC,
        numerical_materialization_sha256=sha)

def test_six_alternative_real_common_mec_capital_trees(tmp_path):
    report=run(tmp_path)
    assert report["six_alternative_ticket_methods_verified"]
    assert audit_methods(report["owners"])["complete"]
    for o in ("BASELINE","CANDIDATE"):
        for m in ("EXACTA","TRIO","TRIFECTA"):
            t=report["owners"][o][m]
            assert t["point_count"]==1
            assert t["total_investment"]==100
            assert t["unused_capital"]==9900
            assert t["no_bet"] is False
            assert t["canonical_tree"]
    assert report["actual_purchase_verified"] is False
    assert report["formal_signed_final_or_user_delivery_ack"] is False

def test_budget_zero_computed_no_bet_not_missing_calculation(tmp_path):
    report=run(tmp_path,cap=0)
    for o in ("BASELINE","CANDIDATE"):
        for m in ("EXACTA","TRIO","TRIFECTA"):
            t=report["owners"][o][m]
            assert t["no_bet"] is True
            assert t["point_count"]==0
            assert t["total_investment"]==0
            assert t["required_method_mec_capital"]==100

def test_missing_real_owner_seed_does_not_generate_ticket(tmp_path):
    root,sem,krs,sha=objects(tmp_path)
    krs["owners"]["BASELINE"]["actual_master_seed"]=2026100204
    with pytest.raises(ValueError,match="ACTUAL_KRS_5K_SEED1_MISSING"):
        construct(race_id=RID,owner_semantics=sem,private_root=root,
           dual_krs_manifest=krs,source_snapshot_sha256=SRC,
           numerical_materialization_sha256=sha)

def test_missing_frozen_pair_is_hard_hold_not_no_bet(tmp_path):
    root,sem,krs,sha=objects(tmp_path)
    sem["BASELINE"]["pair_dispositions"]=[]
    with pytest.raises(ValueError,match="ACTIVE_W_WITHOUT_MATERIAL_PAIR_CLOSURE"):
        construct(race_id=RID,owner_semantics=sem,private_root=root,
           dual_krs_manifest=krs,source_snapshot_sha256=SRC,
           numerical_materialization_sha256=sha)

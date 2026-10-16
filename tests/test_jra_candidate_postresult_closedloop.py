import copy
import json
import sys
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))
from jra_candidate_postresult_closedloop import (
    PendingOfficialResult, canonical_sha, parse_official_payouts,
    verify_official_result, settle_frozen_candidate,
)


def price_text():
    return (
        "レース結果 払戻金 単勝 4 270 円 1 番人気 馬単 4-8 1,240 円 3 番人気 "
        "3連複 3-4-8 720 円 1 番人気 "
        "3連単 4-8-3 4,850 円 4 番人気 勝馬の紹介"
    )


def frozen():
    pre={
        "race_id":"KM-JRA-KYO-20261010-R03",
        "source_snapshot_sha256":"SRC", "oos_eligible":True,
        "candidate_final_verified":True,"candidate_final_receipt_sha256":"RR",
        "candidate_final_receipt_timestamp":"2026-10-10T01:45:00Z",
        "scheduled_post_at":"2026-10-10T10:50:00+09:00",
        "ranking":["4","8","3","5"],
        "roles":{"4":["W","P2","P3"],"8":["W","P2","P3"],"3":["P3"],"5":[]},
        "pair_dispositions":[{"head":"4","second":"8","status":"PURCHASE"}],
        "third_dispositions":[{"head":"4","second":"8","third":"3","status":"PURCHASE"}],
    }
    pre["sha256"]=canonical_sha(pre)
    fin={
        "race_id":pre["race_id"],"source_snapshot_sha256":"SRC","candidate_only":True,
        "production_effect":"NONE","final_receipt":{"receipt_sha256":"RR"},
        "capital":{"required_capital":400},
        "mec":{"ticket_count":3,"tickets":[
            {"bet_type":"EXACTA","selection":[4,8],"stake":200},
            {"bet_type":"TRIFECTA","selection":[4,8,3],"stake":100},
            {"bet_type":"TRIO","selection":[3,4,8],"stake":100},
        ]},
    }
    fin["sha256"]=canonical_sha(fin)
    return pre,fin


def official():
    return {"top3":[4,8,3],"payouts":parse_official_payouts(price_text())}


def test_strict_jra_payout_parsing():
    out=parse_official_payouts(price_text())
    assert out["EXACTA"]["selection"]==[4,8]
    assert out["TRIO"]["selection"]==[3,4,8]
    assert out["TRIFECTA"]["per_100_yen"]==4850
    with pytest.raises(PendingOfficialResult):
        parse_official_payouts("レース結果 払戻金 馬単 4-8 1,240 円")
    with pytest.raises(PendingOfficialResult):
        parse_official_payouts(price_text().replace("馬単 4-8 1,240 円","馬単 4-8 1,240 円 馬単 4-8 1,240 円"))


def test_official_top3_and_price_table_must_reconcile():
    parsed={"official":True,"runners":[
        {"runner_id":"4","horse_no":4,"finish":1},
        {"runner_id":"8","horse_no":8,"finish":2},
        {"runner_id":"3","horse_no":3,"finish":3},
    ]}
    result=verify_official_result(parsed,price_text(),["3","4","8"])
    assert result["top3"]==[4,8,3]
    with pytest.raises(PendingOfficialResult,match="MISMATCH"):
        verify_official_result(parsed,price_text().replace("4-8 1,240", "8-4 1,240"),["3","4","8"])
    with pytest.raises(ValueError,match="UNIVERSE"):
        verify_official_result(parsed,price_text(),["1","3","4"])


def test_settlement_reconciles_exact_stakes_and_never_claims_actual_pfs():
    pre,fin=frozen()
    out=settle_frozen_candidate(pre,fin,official(),source_sha256="OFFICIAL_RAW_HASH",source_url="https://www.jra.go.jp/JRADB/accessD.html")
    s=out["settlement"]
    assert s["recommended_stake_yen"]==400
    assert s["recommended_return_yen"]==2*1240+4850+720
    assert s["frozen_recommendation_pfs_percent"]==2012.5
    assert s["actual_purchase_status"]=="UNVERIFIED"
    assert s["actual_pfs_status"]=="NOT_VERIFIED"
    assert s["first_material_failure"]=="NONE"
    assert out["result_evaluation"]["result_evaluation"]["winner_capture"] is True
    assert out["learning"]["new_model_weights_applied"] is False
    assert out["learning"]["promotion_authority"] is False


def test_tampered_frozen_ticket_or_result_is_rejected():
    pre,fin=frozen()
    pre["ranking"]=["8","4","3","5"]
    with pytest.raises(ValueError,match="HASH_INVALID"):
        settle_frozen_candidate(pre,fin,official(),source_sha256="X",source_url="JRA")
    pre,fin=frozen()
    fin["mec"]["tickets"][0]["stake"]=300
    with pytest.raises(ValueError,match="HASH_INVALID"):
        settle_frozen_candidate(pre,fin,official(),source_sha256="X",source_url="JRA")
    pre,fin=frozen()
    fin["mec"]["tickets"].append(copy.deepcopy(fin["mec"]["tickets"][0]))
    fin["sha256"]=canonical_sha({k:v for k,v in fin.items() if k!="sha256"})
    with pytest.raises(ValueError,match="DUPLICATE_FROZEN_TICKET"):
        settle_frozen_candidate(pre,fin,official(),source_sha256="X",source_url="JRA")


def test_missing_true_role_is_first_failure_without_imputation():
    pre,fin=frozen()
    pre["roles"]["4"]=[]
    pre["sha256"]=canonical_sha({k:v for k,v in pre.items() if k!="sha256"})
    out=settle_frozen_candidate(pre,fin,official(),source_sha256="OFFICIAL_RAW_HASH",source_url="JRA")
    assert out["settlement"]["first_material_failure"]=="W_HEAD_ZERO"
    assert out["settlement"]["dominant_pfs_loss_owner"]=="NONE"

def test_real_repo_jra_official_payout_html_text_fixture():
    historical=ROOT/"runtime"/"diagnostics"/"jra_official_result_nav_probe.json"
    doc=json.loads(historical.read_text(encoding="utf-8"))
    prices=parse_official_payouts(doc["text_head"])
    assert prices["EXACTA"]=={"selection":[11,9],"per_100_yen":42810}
    assert prices["TRIO"]=={"selection":[9,11,12],"per_100_yen":118680}
    assert prices["TRIFECTA"]=={"selection":[11,9,12],"per_100_yen":699560}


def test_real_kyoto_pre_start_frozen_receipt_and_hashes_are_intact():
    from jra_candidate_postresult_closedloop import _verified_pre_frozen
    race="KM-JRA-KYO-20261010-R03"
    folder=ROOT/"runtime"/"source_candidate_oos"/race
    pre=json.loads((folder/"pre_result.json").read_text(encoding="utf-8"))
    final=json.loads((folder/"candidate_final.json").read_text(encoding="utf-8"))
    _verified_pre_frozen(pre,final,race)

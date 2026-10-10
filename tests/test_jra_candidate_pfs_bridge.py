from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))
from jra_candidate_pfs_bridge import bridge_race, bridge_all


RID="KM-JRA-KYO-20261010-R03"


def test_real_kyoto_candidate_is_transformed_without_changed_stake():
    doc=bridge_race(ROOT,RID)
    assert doc["production_effect"]=="NONE"
    assert doc["automatic_promotion"] is False
    s=doc["settlement"]
    assert s["pfs_authority"]=="CANDIDATE-FROZEN-RECOMMENDATION-PFS"
    assert s["actual_ticket_status"]=="UNVERIFIED"
    assert s["total_investment"]==1400
    assert s["total_payout"]==0
    assert s["pfs"]==0
    assert len(s["winning_tickets"])==0
    assert sum(x["investment"] for x in s["bet_type_summary"])==1400


def copy_kyoto(tmp_path:Path):
    src=ROOT/"runtime"/"source_candidate_oos"/RID
    dst=tmp_path/"runtime"/"source_candidate_oos"/RID
    dst.mkdir(parents=True)
    for file in ("pre_result.json","candidate_final.json","result_evaluation.json","settlement.json"):
        shutil.copy(src/file,dst/file)
    return dst


def test_bridge_pfs_grand_review_same_existing_definition_no_double_count(tmp_path,monkeypatch):
    copy_kyoto(tmp_path)
    doc=bridge_all(tmp_path)
    assert doc["written"]==[RID]
    dest=tmp_path/"runtime"/"source_candidate_results"/(RID+".json")
    assert dest.exists()
    before=dest.read_bytes()
    assert bridge_all(tmp_path)["unchanged"]==[RID]
    assert before==dest.read_bytes()
    monkeypatch.chdir(tmp_path)
    import pfs_grand_review as p
    r=p.build_report()
    c=r["candidate_forward_oos"]
    assert c["eligible_race_count"]==1
    assert c["settled_race_count"]==1
    assert c["aggregate"]["investment"]==1400
    assert c["aggregate"]["return"]==0
    assert c["aggregate"]["investment_weighted_pfs"]==0
    assert c["tier_pfs"]["tiers"]
    assert r["actual_pfs"]["verified_race_count"]==0
    assert r["cohorts"]["FORMAL_PRE_RACE"]["race_count"]==0


def test_bridge_rejects_tamper_and_conflicting_prior_result(tmp_path):
    dest_dir=copy_kyoto(tmp_path)
    p=dest_dir/"settlement.json"
    bad=json.loads(p.read_text(encoding="utf-8"))
    bad["recommended_return_yen"]=999999
    p.write_text(json.dumps(bad),encoding="utf-8")
    with pytest.raises(ValueError,match="IMMUTABLE_INPUT_HASH_MISMATCH"):
        bridge_race(tmp_path,RID)

    shutil.copy(ROOT/"runtime"/"source_candidate_oos"/RID/"settlement.json",p)
    bridge_all(tmp_path)
    legacy=tmp_path/"runtime"/"source_candidate_results"/(RID+".json")
    obj=json.loads(legacy.read_text(encoding="utf-8"))
    obj["settlement"]["total_investment"]=900
    legacy.write_text(json.dumps(obj),encoding="utf-8")
    with pytest.raises(ValueError,match="CANDIDATE_LEGACY_PFS_CONFLICT"):
        bridge_all(tmp_path)

"""R18: complete *presentation* must contain all horse cells and six trees.

These tests use synthetic mocked frozen semantics and real Common MEC/Capital
ticket compiler, not today's FNB race forecast or an actual KRS receipt.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib,json,sys
from pathlib import Path
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_fnb_20261102_r17_method_constructor import objects,RID,SRC
from runtime.local_fnb_r17_method_constructor import construct
from runtime.local_fnb_r18_full_private_delivery import verified_full_delivery

ROOT=Path(__file__).resolve().parents[1]
MAP=ROOT/"mapping/local_full_numerical_mapping_v1.0_production_20261008.json"

def prepared(tmp_path):
    root,sem,krs,num_sha=objects(tmp_path)
    path=root/RID
    idx=json.loads(MAP.read_text())["required_indices"]
    rows=[]
    for number in range(1,8):
        cells={k:{"value":52.0,"terminal_status":"RULED-NEUTRAL",
                  "rule_id":"SYNTHETIC_NEUTRAL_CORRECTNESS_TEST",
                  "evidence_refs":["SYNTHETIC_INPUT_ONLY"]}
               for k in idx}
        rows.append({"runner_id":str(number),"name":"TEST_"+str(number),
                     "canonical_components":cells,
                     "numerical_missing_components":[]})
    content=json.dumps({"runners":rows},ensure_ascii=False,sort_keys=True).encode()
    (path/"numerical_materialization.json").write_bytes(content)
    sha=hashlib.sha256(content).hexdigest()
    for owner in ("BASELINE","CANDIDATE"):
        req=sem[owner]
        req["numerical_materialization_sha256"]=sha
        req["rankings_by_column"]={
            "W":[str(i) for i in range(1,8)],
            "P2":[str(i) for i in range(1,8)],
            "P3":[str(i) for i in range(1,8)]}
        summary=[{"horse_no":n,"SSR-W":0.1,"SSR-P2":0.2,"SSR-P3":0.3,
                  "LSR":0.4,"Z4R-W":0.5} for n in range(1,8)]
        data={"snapshot":{"run_count":5000,"master_seed":1,
               "prediction_id":RID+"-"+owner},
              "engine":{"engine_version":"1.1.0",
                        "parameter_map_version":"0.1-provisional"},
              "summary":summary}
        raw=json.dumps(data,ensure_ascii=False).encode()
        (path/(owner+"_krs_output.json")).write_bytes(raw)
        krs["owners"][owner]["actual_output_sha256"]=hashlib.sha256(raw).hexdigest()
    return root,sem,krs,sha

def prepare_ticket(tmp_path):
    root,sem,krs,sha=prepared(tmp_path)
    port=construct(race_id=RID,owner_semantics=sem,
        private_root=root,dual_krs_manifest=krs,
        source_snapshot_sha256=SRC,
        numerical_materialization_sha256=sha)
    return root,sem,krs,port

def test_r18_actual_six_mec_trees_all7x29_and_two_owner_krs_in_full_document(tmp_path):
    root,sem,krs,port=prepare_ticket(tmp_path)
    result=verified_full_delivery(race_id=RID,private_root=root,
        semantics=sem,portfolios=port["owners"],diagnostic_only=True)
    assert result["status"]=="FULL_PRESENTATION_READY_RECIPIENT_ACK_UNVERIFIED"
    assert result["all_horses"]==7
    assert result["all_29_index_cells"]==203
    assert result["six_alternative_methods"] is True
    assert result["recipient_delivery_ack"] is False
    file=root/RID/result["body_filename"]
    body=file.read_text()
    assert body.count("#### EXACTA")==2
    assert body.count("#### TRIO")==2
    assert body.count("#### TRIFECTA")==2
    assert body.count("| HPI-L |")==7
    assert "POSTCUTOFF_DIAGNOSTIC_NOT_PRESTART" in body
    assert "未較正" in body
    assert result["full_body_sha256"]==hashlib.sha256(file.read_bytes()).hexdigest()

def test_r18_missing_w_p2_p3_full_rankings_never_presentation_pass(tmp_path):
    root,sem,krs,port=prepare_ticket(tmp_path)
    sem["BASELINE"]["rankings_by_column"].pop("P2")
    with pytest.raises(ValueError,match="FULL_RANKING_MISSING"):
        verified_full_delivery(race_id=RID,private_root=root,
            semantics=sem,portfolios=port["owners"])

def test_r18_krs_seed_other_than_one_never_passes(tmp_path):
    root,sem,krs,port=prepare_ticket(tmp_path)
    file=root/RID/"CANDIDATE_krs_output.json"
    data=json.loads(file.read_text())
    data["snapshot"]["master_seed"]=2
    file.write_text(json.dumps(data))
    with pytest.raises(ValueError,match="REAL_KRS_5000_SEED1_NOT_VERIFIED"):
        verified_full_delivery(race_id=RID,private_root=root,
            semantics=sem,portfolios=port["owners"])

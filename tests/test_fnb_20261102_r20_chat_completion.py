"""R20 one-trigger FNB private Work bridge: synthetic payloads, no official data."""
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path

import pytest
from runtime import local_fnb_r20_chat_completion as r20

NOW=datetime(2026,11,2,7,30,tzinfo=timezone.utc)
RACE="KM-LOCAL-FNB-20261102-R05-PRIVATE-R1"
QUERY="2026-11-02 船橋5R"

def _put(root,name,payload):
    p=root/name
    p.parent.mkdir(parents=True,exist_ok=True)
    b=payload if isinstance(payload,bytes) else json.dumps(payload).encode()
    p.write_bytes(b)
    return {"path":name,"sha256":hashlib.sha256(b).hexdigest()}

def _bundle(root, cutoff="2026-11-02T07:45:00+00:00", owner_pair=("a"*64,"b"*64)):
    b={"venue_id":"FNB","race_date":"2026-11-02","race_no":5,
       "classification":r20.CLASSIFICATION,
       "request":_put(root,"input/request.json",{"race_id":RACE,"venue_id":"FNB",
                "family_id":"LOCAL","race_date":"2026-11-02","race_no":5,
                "prediction_cutoff":cutoff}),
       "source":_put(root,"input/source.json",{"source_snapshot_sha256":"0"*64}),
       "owners":{},"engine":{"path":str(root/"engine.py")},
       "params":{"path":str(root/"map.json")}}
    for name,sha in zip(("BASELINE","CANDIDATE"),owner_pair):
        b["owners"][name]={
          "krs":_put(root,"input/"+name+"_krs.json",{"owner":name,
                       "original_prediction_sha256":sha}),
          "semantics":_put(root,"input/"+name+"_semantics.json",{"owner":name,
                       "original_prediction_sha256":sha})}
    path=root/"inbox"/"FNB_2026-11-02_R05_private_bundle.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(b))
    return path

def test_no_source_no_bet_is_not_calculated(tmp_path):
    r=r20.complete(QUERY,tmp_path,now=NOW)
    assert r["status"]=="EXECUTION_HOLD_NOT_NO_BET"
    assert r["first_failed_stage"]=="WORK_INPUT"
    assert r["recipient_delivery_ack"] is False

def test_expired_cutoff_is_diagnostic_only(tmp_path):
    _bundle(tmp_path,cutoff="2026-11-02T07:00:00+00:00")
    r=r20.complete(QUERY,tmp_path,now=NOW)
    assert r["reason"]=="PRESTART_CUTOFF_EXPIRED_DIAGNOSTIC_REQUIRED"
    assert r["registered_oos_increment"]==0

def test_identical_owner_model_is_rejected(tmp_path):
    _bundle(tmp_path,owner_pair=("a"*64,"a"*64))
    r=r20.complete(QUERY,tmp_path,now=NOW)
    assert r["reason"]=="FNB_R20_IDENTICAL_BASELINE_CANDIDATE_MODEL_FORBIDDEN"

def test_bad_source_raw_bytes_are_blocked(tmp_path):
    _bundle(tmp_path)
    p=tmp_path/"input/source.json"
    p.write_text('{"tampered":true}')
    r=r20.complete(QUERY,tmp_path,now=NOW)
    assert r["reason"]=="FNB_R20_SOURCE_BYTES_MISSING_OR_SHA_MISMATCH"

def test_private_path_escape_is_blocked(tmp_path):
    path=_bundle(tmp_path)
    b=json.loads(path.read_text())
    b["request"]["path"]="/tmp/external-private-request.json"
    path.write_text(json.dumps(b))
    r=r20.complete(QUERY,tmp_path,now=NOW)
    assert r["reason"]=="FNB_R20_REQUEST_NOT_IN_PRIVATE_ROOT"

def test_preexisting_complete_body_reused_without_dispatch(tmp_path, monkeypatch):
    marker={"status":"VERIFIED_FROZEN_PRIVATE_BODY_READY_TO_RENDER",
        "body":"synthetic-ticket-tree","body_sha256":"c"*64,
        "recipient_delivery_ack":False}
    monkeypatch.setattr(r20,"readback",lambda *_: marker)
    r=r20.complete(QUERY,tmp_path,now=NOW)
    assert r["new_prediction_executed"] is False
    assert r["body"]=="synthetic-ticket-tree"

def test_dated_complete_execution_is_one_call(tmp_path,monkeypatch):
    _bundle(tmp_path)
    monkeypatch.setattr(r20,"_asset_path",lambda s,expected_sha,label: tmp_path/label)
    called=[]
    def fake_run(**kw):
        called.append(kw)
        return {"status":"FULL_PRIVATE_PRESENTATION_READY_DELIVERY_ACK_UNVERIFIED"}
    import runtime.local_fnb_r14_private_work_entry as r14
    monkeypatch.setattr(r14,"run",fake_run)
    def fake_readback(*_):
        if called:
            return {"status":"VERIFIED_FROZEN_PRIVATE_BODY_READY_TO_RENDER",
                "body":"[synthetic only]","body_sha256":"d"*64,
                "recipient_delivery_ack":False,"registered_oos_increment":0}
        return {"status":"FULL_DELIVERY_NOT_COMPLETED","first_failed_stage":"PRIVATE_STORE",
                "reason":"NOT_YET_PRESENT"}
    monkeypatch.setattr(r20,"readback",fake_readback)
    result=r20.complete(QUERY,tmp_path,now=NOW)
    assert result["new_prediction_executed"] is True
    assert called[0]["request"]["race_no"]==5
    assert set(called[0]["owners"])=={"BASELINE","CANDIDATE"}
    assert set(called[0]["frozen_semantics"])=={"BASELINE","CANDIDATE"}
    assert result["recipient_delivery_ack"] is False

def test_public_ci_does_not_emit_horses(tmp_path,monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS","true")
    result=r20.complete(QUERY,tmp_path,now=NOW,emit_private_body=True)
    assert result["reason"]=="PRIVATE_HORSE_OR_TICKET_BODY_PUBLIC_CI_FORBIDDEN"

def test_race_id_path_traversal_is_rejected_before_private_write(tmp_path):
    manifest_path=_bundle(tmp_path)
    manifest=json.loads(manifest_path.read_text())
    malicious={"race_id":RACE+"-../../escape","venue_id":"FNB",
               "family_id":"LOCAL","race_date":"2026-11-02","race_no":5,
               "prediction_cutoff":"2026-11-02T07:45:00+00:00"}
    manifest["request"]=_put(tmp_path,"input/request-malicious.json",malicious)
    manifest_path.write_text(json.dumps(manifest))
    result=r20.complete(QUERY,tmp_path,now=NOW)
    assert result["reason"]=="FNB_R20_REQUEST_RACE_IDENTITY_MISMATCH"
    assert not (tmp_path/"escape").exists()

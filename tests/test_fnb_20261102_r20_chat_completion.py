"""R20 one-trigger FNB private Work bridge: synthetic payloads, no official data."""
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
from runtime import local_fnb_r20_chat_completion as r20

NOW=datetime(2026,11,2,7,30,tzinfo=timezone.utc)
RACE="KM-LOCAL-FNB-20261102-R05-PRIVATE-R1"
QUERY="2026-11-02 船橋5R"

def _minimal_work_cli(tmp_path, extra):
    """Run actual private-entry code without any unrelated Formal modules."""
    package=tmp_path/"minimal-transport"
    runtime=package/"runtime"
    runtime.mkdir(parents=True)
    original=Path(__file__).resolve().parents[1]/"runtime"
    for name in ("local_race_entry.py", "local_fnb_r20_chat_completion.py",
                 "local_fnb_r19_chat_readback.py", "local_fnb_r14_private_dual_krs.py",
                 "local_fnb_r13_private_single_numeric.py",
                 "local_fnb_r13_private_source_admission.py"):
        shutil.copyfile(original/name,runtime/name)
    env=os.environ.copy()
    env["PYTHONPATH"]=str(package)
    env.pop("KM_FNB_PRIVATE_WORK_ROOT",None)
    # This subprocess models a private Work CLI, with no real data or binding.
    env.pop("CI",None)
    env.pop("GITHUB_ACTIONS",None)
    return subprocess.run([sys.executable,"-m","runtime.local_race_entry",*extra],
                          cwd=package,env=env,capture_output=True,text=True,timeout=15)

@pytest.mark.parametrize("query,reason",[
    ("2026-11-02 船橋12レースのケイバメトリクス調査願います",
     "SOURCE_PRODUCER_NOT_CONNECTED"),
    ("2026-11-02 船橋12R 浦和11R", "FNB_CHAT_EXACTLY_ONE_RACE_REQUIRED"),
])
def test_normal_fnb_cli_reaches_private_gate_without_formal_stack(tmp_path,query,reason):
    public=tmp_path/"unused-public-output"
    result=_minimal_work_cli(tmp_path,["--query",query,"--private-root",str(tmp_path/"private"),
        "--output",str(public),"--run-id","R21-PRIVATE-ACTOR-ACCEPTANCE"])
    assert result.returncode==2,result.stderr
    body=json.loads(result.stdout)
    assert body["status"]=="EXECUTION_HOLD_NOT_NO_BET"
    assert body["reason"]==reason
    assert body["recipient_delivery_ack"] is False
    assert body["registered_oos_increment"]==0
    assert not public.exists()
    assert "ImportError" not in result.stderr

def test_cli_help_does_not_require_unrelated_formal_dependencies(tmp_path):
    result=_minimal_work_cli(tmp_path,["--help"])
    assert result.returncode==0,result.stderr
    assert "--private-root" in result.stdout
    assert "--persist-checkpoints" in result.stdout

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

def test_no_source_no_bet_is_not_calculated(tmp_path,monkeypatch):
    monkeypatch.delenv("CI",raising=False)
    monkeypatch.delenv("GITHUB_ACTIONS",raising=False)
    r=r20.complete(QUERY,tmp_path,now=NOW)
    assert r["status"]=="EXECUTION_HOLD_NOT_NO_BET"
    assert r["first_failed_stage"]=="SOURCE_PRODUCER"
    assert r["recipient_delivery_ack"] is False

@pytest.mark.parametrize("message,expected",[
    ("SOURCE_DNS_RESOLUTION_FAILED:private-provider", "SOURCE_DNS_RESOLUTION_FAILED"),
    ("SOURCE_DNS_EMPTY", "SOURCE_DNS_EMPTY"),
    ("SOURCE_POLICY_ROBOTS_DISALLOWED:https://private-provider", "SOURCE_ACCESS_POLICY_BLOCKED"),
    ("SOURCE_HTTP_STATUS:503 private-response", "SOURCE_HTTP_STATUS_FAILED"),
    ("private-URL-with-ROBOTS-and-POLICY-text", "SOURCE_CONNECTION_FAILED"),
])
def test_source_failure_layer_is_preserved_without_private_exception(tmp_path,monkeypatch,message,expected):
    # A synthetic private Work callback, never an actual provider in public CI.
    monkeypatch.delenv("CI",raising=False)
    monkeypatch.delenv("GITHUB_ACTIONS",raising=False)
    calls=[]
    def source(**kw):
        calls.append(kw)
        raise ValueError(message)
    result=r20.complete(QUERY,tmp_path,now=NOW,producers={"source":source})
    assert len(calls)==1
    assert result["status"]=="EXECUTION_HOLD_NOT_NO_BET"
    assert result["first_failed_stage"]=="SOURCE"
    assert result["reason"]==expected
    assert "private-" not in json.dumps(result)
    assert not (tmp_path/"inbox").exists()
    assert result["registered_oos_increment"]==0

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

def producer_fixture(root,monkeypatch):
    """Synthetic Producer protocol only; SOURCE/numeric/Engine boundaries stubbed.

    These test-only models, evidence and predictions are never LIVE assets.
    Existing R14/R17/R18/R19 tests independently cover downstream construction.
    """
    from copy import deepcopy
    import runtime.local_fnb_r13_private_single_numeric as r13
    monkeypatch.delenv("CI",raising=False)
    monkeypatch.delenv("GITHUB_ACTIONS",raising=False)
    monkeypatch.setattr(r20,"_verify_captured_source",lambda *args:None)
    monkeypatch.setattr(r20,"_asset_path",lambda *args:root/"SYNTHETIC_ASSET")
    request={"race_id":RACE,"family_id":"LOCAL","venue_id":"FNB",
        "race_date":"2026-11-02","race_no":5,
        "prediction_cutoff":"2026-11-02T07:45:00Z",
        "scheduled_post_at":"2026-11-02T07:50:00Z"}
    source={"race_id":RACE,"source_freeze_at":"2026-11-02T07:25:00Z",
        "source_race_context":{"venue_id":"FNB","race_date":"2026-11-02","race_no":5},
        "source_snapshot_sha256":"1"*64,
        "sources":[{"official":True,"source_class":"OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT",
            "source_id":"SYNTHETIC_ONLY","snapshot_sha256":"2"*64,"raw_sha256":"3"*64}],
        "declared_runner_universe":{"runners":[{"runner_id":1},{"runner_id":2}]}}
    calls=[]
    def numeric(**kwargs):
        calls.append("NUMERICAL_BOUNDARY")
        ref=r20._put_original(kwargs["private_root"],RACE+"/numerical_materialization.json",
            {"synthetic":True,"runners":[{"runner_id":1},{"runner_id":2}]})
        return {"private_materialization_sha256":ref["sha256"]}
    monkeypatch.setattr(r13,"execute",numeric)
    def capture(**kwargs):
        calls.append("SOURCE_BOUNDARY")
        return {"request":deepcopy(request),"source":deepcopy(source)}
    producers={"source":capture,"owners":{},"engine":{},"params":{}}
    for owner in ("BASELINE","CANDIDATE"):
        model={"model_id":"SYNTHETIC_TEST_ONLY_"+owner,"model_version":"test",
            "scope":{"family_id":"LOCAL","venues":["FNB"],"classification":r20.CLASSIFICATION}}
        ref=_put(root,"test-models/"+owner+".json",model)
        proof={"model_sha256":ref["sha256"],"model_id":model["model_id"],
            "owner":owner,"venue_id":"FNB","classification":r20.CLASSIFICATION,
            "decision":"ADOPTED_PRIVATE_RESEARCH","effective_at":"2026-11-01T00:00:00Z"}
        def produce(*,owner=owner,ref=deepcopy(ref),**kw):
            calls.append(owner)
            krs={"owner":owner,"race_id":RACE,"classification":"PRIVATE_NONPRODUCTION_FIXED_OWNER",
                "numerical_materialization_sha256":kw["numerical_sha256"],
                "race":{"prediction_id":RACE+"-"+owner,"date":"2026-11-02",
                    "racecourse":"FNB","race_no":5,"distance_m":1200,"surface":"DIRT","direction":"LEFT"},
                "horses":[{"horse_no":n,"hsv":{},"static":{}} for n in (1,2)]}
            sem={"owner":owner,"race_id":RACE,"family_id":"LOCAL","venue_id":"FNB",
                "classification":"PRIVATE_NONPRODUCTION_FIXED_OWNER",
                "numerical_materialization_sha256":kw["numerical_sha256"],
                "source_snapshot_sha256":kw["source"]["source_snapshot_sha256"],
                "role_registry":[{"runner_id":str(n),"column":"W","status":"INACTIVE"} for n in (1,2)],
                "pair_dispositions":[],"third_dispositions":[]}
            prediction={"model_id":kw["model"]["model_id"],"model_version":"test",
                "model_sha256":ref["sha256"],"owner":owner,"race_id":RACE,
                "classification":r20.CLASSIFICATION,"freeze_at":kw["now"].isoformat(),
                "source_snapshot_sha256":kw["source"]["source_snapshot_sha256"],
                "numerical_materialization_sha256":kw["numerical_sha256"],
                "active_runners":[1,2],"krs_input":deepcopy(krs),"semantics":deepcopy(sem)}
            original=_put(root,"test-predictions/"+owner+".json",prediction)
            krs["original_prediction_sha256"]=sem["original_prediction_sha256"]=original["sha256"]
            return {"model_id":kw["model"]["model_id"],"model_sha256":ref["sha256"],
                "prediction":original,"krs":krs,"semantics":sem}
        producers["owners"][owner]={"model":ref,"qualification":_put(root,"test-models/"+owner+"-scope.json",proof),"produce":produce}
    return producers,calls

def test_qualified_producers_assemble_actual_byte_bundle_and_reach_r14(tmp_path,monkeypatch):
    producers,calls=producer_fixture(tmp_path,monkeypatch)
    import runtime.local_fnb_r14_private_work_entry as r14
    delivered=[]
    def run(**kw):
        delivered.append(kw)
    monkeypatch.setattr(r14,"run",run)
    monkeypatch.setattr(r20,"readback",lambda *_: ({"status":"VERIFIED_FROZEN_PRIVATE_BODY_READY_TO_RENDER",
        "body":"SYNTHETIC_BOUNDARY_ONLY","recipient_delivery_ack":False} if delivered else
        {"status":"FULL_DELIVERY_NOT_COMPLETED","first_failed_stage":"COMPLETE_ORIGINAL"}))
    result=r20.complete(QUERY,tmp_path,now=NOW,producers=producers)
    assert result["new_prediction_executed"] is True
    assert calls==["SOURCE_BOUNDARY","NUMERICAL_BOUNDARY","BASELINE","CANDIDATE"]
    path=tmp_path/"inbox/FNB_2026-11-02_R05_private_bundle.json"
    bundle=json.loads(path.read_bytes())
    for owner in ("BASELINE","CANDIDATE"):
        p=r20._load_json(tmp_path,bundle["owners"][owner]["prediction"],"TEST")
        assert p["model_id"]=="SYNTHETIC_TEST_ONLY_"+owner
        assert delivered[0]["owners"][owner]["original_prediction_sha256"]==bundle["owners"][owner]["prediction"]["sha256"]
    before={p:p.read_bytes() for p in tmp_path.rglob("*.json")}
    assert r20.complete(QUERY,tmp_path,now=NOW,producers=producers)["new_prediction_executed"] is False
    assert before=={p:p.read_bytes() for p in tmp_path.rglob("*.json")}
    assert result["recipient_delivery_ack"] is False

@pytest.mark.parametrize("failure",["missing_owner","same_model","bad_scope","bad_prediction","bad_input","wrong_race","future_adoption"])
def test_producer_gaps_never_publish_empty_bundle_or_start_krs(tmp_path,monkeypatch,failure):
    producers,calls=producer_fixture(tmp_path,monkeypatch)
    if failure=="missing_owner":producers["owners"].pop("CANDIDATE")
    if failure=="same_model":producers["owners"]["CANDIDATE"]=producers["owners"]["BASELINE"]
    if failure in ("bad_scope","future_adoption"):
        entry=producers["owners"]["CANDIDATE"]
        proof=json.loads((tmp_path/entry["qualification"]["path"]).read_bytes())
        proof["venue_id"]="URW" if failure=="bad_scope" else "FNB"
        if failure=="future_adoption":proof["effective_at"]="2026-11-02T07:40:00Z"
        entry["qualification"]=_put(tmp_path,entry["qualification"]["path"],proof)
    if failure in ("bad_prediction","bad_input"):
        entry=producers["owners"]["CANDIDATE"];original=entry["produce"]
        def changed(**kw):
            out=original(**kw)
            if failure=="bad_prediction":(tmp_path/out["prediction"]["path"]).write_bytes(b"{}")
            else:out["krs"]["race"]["race_no"]=6
            return out
        entry["produce"]=changed
    if failure=="wrong_race":
        original=producers["source"]
        def wrong(**kw):
            out=original(**kw);out["request"]["race_id"]=RACE.replace("R05","R04")
            return out
        producers["source"]=wrong
    result=r20.complete(QUERY,tmp_path,now=NOW,producers=producers)
    assert result["status"]=="EXECUTION_HOLD_NOT_NO_BET"
    assert not (tmp_path/"inbox").exists()
    assert not (tmp_path/RACE).exists()
    if failure in ("missing_owner","same_model","bad_scope","wrong_race","future_adoption"):
        assert "NUMERICAL_BOUNDARY" not in calls

def test_cutoff_crossed_during_source_callback_stops_before_numeric(tmp_path,monkeypatch):
    producers,calls=producer_fixture(tmp_path,monkeypatch)
    observed=[NOW]
    original=producers["source"]
    def slow(**kw):
        out=original(**kw);observed[0]=NOW+timedelta(minutes=16)
        return out
    producers["source"]=slow
    result=r20.complete(QUERY,tmp_path,clock=lambda:observed[0],producers=producers)
    assert result["first_failed_stage"]=="TIME"
    assert "NUMERICAL_BOUNDARY" not in calls

def test_callback_exception_is_sanitized_and_no_bundle_is_written(tmp_path,monkeypatch):
    producers,_=producer_fixture(tmp_path,monkeypatch)
    def broken(**kw):raise RuntimeError("PRIVATE_RAW_MUST_NOT_APPEAR")
    producers["source"]=broken
    result=r20.complete(QUERY,tmp_path,now=NOW,producers=producers)
    assert result["reason"]=="SOURCE_OR_OWNER_PRODUCER_INPUT_UNVERIFIED"
    assert "PRIVATE_RAW_MUST_NOT_APPEAR" not in json.dumps(result)
    assert not (tmp_path/"inbox").exists()

def test_public_ci_never_imports_binding_or_calls_producers(tmp_path,monkeypatch):
    producers,calls=producer_fixture(tmp_path,monkeypatch)
    monkeypatch.setenv("GITHUB_ACTIONS","true")
    result=r20.complete(QUERY,tmp_path,now=NOW,producers=producers)
    assert result["reason"]=="PRIVATE_PRODUCER_EXECUTION_PUBLIC_CI_FORBIDDEN"
    assert calls==[]

@pytest.mark.parametrize("name",["producer_inputs", "inbox"])
def test_ancestor_symlink_never_writes_outside_store(tmp_path,name):
    root=tmp_path/"private";root.mkdir()
    outside=tmp_path/"public";outside.mkdir()
    (root/name).symlink_to(outside,target_is_directory=True)
    with pytest.raises(r20.ProducerHold,match="PRIVATE_PATH_OUTSIDE_STORE"):
        r20._put_original(root,name+"/nested/raw.json",{"private":"DO_NOT_WRITE"})
    assert list(outside.iterdir())==[]

def test_private_original_conflict_never_replaces_saved_bytes(tmp_path):
    ref=r20._put_original(tmp_path,"input/freeze.json",{"v":1})
    before=(tmp_path/ref["path"]).read_bytes()
    with pytest.raises(r20.ProducerHold,match="PRIVATE_ORIGINAL_REVISION_CONFLICT"):
        r20._put_original(tmp_path,"input/freeze.json",{"v":2})
    assert (tmp_path/ref["path"]).read_bytes()==before

def test_binding_executes_only_sha_pinned_source_bytes_not_old_pyc(tmp_path,monkeypatch):
    path=tmp_path/"FNB_PRODUCERS.py"
    data=b'def get_producers():\n    return {"marker":"PINNED_SOURCE_ONLY"}\n'
    path.write_bytes(data)
    monkeypatch.setenv("KM_FNB_PRODUCER_BINDING_SHA256",hashlib.sha256(data).hexdigest())
    assert r20._binding(tmp_path)=={"marker":"PINNED_SOURCE_ONLY"}
    path.write_bytes(data+b'raise RuntimeError("MODIFIED")\n')
    with pytest.raises(r20.ProducerHold,match="PRIVATE_PRODUCER_BINDING_SHA_UNVERIFIED"):
        r20._binding(tmp_path)

def test_same_race_concurrent_call_cannot_start_another_producer(tmp_path,monkeypatch):
    producers,calls=producer_fixture(tmp_path,monkeypatch)
    intent=r20.parse_intent(QUERY,NOW)
    with r20._race_lock(tmp_path,intent):
        result=r20.complete(QUERY,tmp_path,now=NOW,producers=producers)
    assert result["reason"]=="PRIVATE_RACE_EXECUTION_ALREADY_RUNNING"
    assert calls==[]

def test_callback_latest_files_cannot_mutate_frozen_bundle_originals(tmp_path,monkeypatch):
    producers,_=producer_fixture(tmp_path,monkeypatch)
    ref=r20._build_from_producers(r20.parse_intent(QUERY,NOW),tmp_path,lambda:NOW,False,producers)
    bundle=r20._load_json(tmp_path,ref,"BUNDLE")
    before={p:p.read_bytes() for p in (tmp_path/"producer_inputs").rglob("*.json")}
    for p in (tmp_path/"test-predictions").glob("*.json"):p.write_bytes(b"{}")
    for p in (tmp_path/"test-models").glob("*.json"):p.write_bytes(b"{}")
    assert before=={p:p.read_bytes() for p in (tmp_path/"producer_inputs").rglob("*.json")}
    owners={o:r20._load_json(tmp_path,bundle["owners"][o]["krs"],"KRS") for o in ("BASELINE","CANDIDATE")}
    sem={o:r20._load_json(tmp_path,bundle["owners"][o]["semantics"],"SEM") for o in owners}
    r20._producer_evidence(bundle,tmp_path,r20._load_json(tmp_path,bundle["request"],"REQUEST"),
        r20._load_json(tmp_path,bundle["source"],"SOURCE"),owners,sem,NOW)

@pytest.mark.parametrize("missing",["model","qualification","prediction","numeric"])
def test_resume_requires_real_producer_evidence_before_downstream(tmp_path,monkeypatch,missing):
    producers,_=producer_fixture(tmp_path,monkeypatch)
    ref=r20._build_from_producers(r20.parse_intent(QUERY,NOW),tmp_path,lambda:NOW,False,producers)
    bundle=r20._load_json(tmp_path,ref,"BUNDLE")
    if missing in ("model","qualification"):bad=bundle["producer_model_evidence"]["BASELINE"][missing]
    elif missing=="prediction":bad=bundle["owners"]["BASELINE"][missing]
    else:bad=bundle["producer_numeric_freeze"]
    (tmp_path/bad["path"]).unlink()
    import runtime.local_fnb_r14_private_work_entry as r14
    called=[]
    monkeypatch.setattr(r14,"run",lambda **kw:called.append(True))
    result=r20.complete(QUERY,tmp_path,now=NOW)
    assert result["status"]=="EXECUTION_HOLD_NOT_NO_BET"
    assert called==[]

def test_slow_downstream_cannot_leave_reusable_prestart_checkpoint(tmp_path,monkeypatch):
    producers,_=producer_fixture(tmp_path,monkeypatch)
    observed=[NOW]
    import runtime.local_fnb_r14_private_work_entry as r14
    def slow(**kw):
        folder=kw["root"]/RACE;folder.mkdir()
        (folder/"private_pipeline_checkpoint.json").write_text('{"pretend":"completed"}')
        observed[0]=NOW+timedelta(minutes=16)
    monkeypatch.setattr(r14,"run",slow)
    first=r20.complete(QUERY,tmp_path,clock=lambda:observed[0],producers=producers)
    second=r20.complete(QUERY,tmp_path,clock=lambda:observed[0],producers=producers)
    assert first["first_failed_stage"]==second["first_failed_stage"]=="TIME"
    assert not (tmp_path/RACE).exists()
    assert "body" not in first and "body" not in second

def test_owner_callback_cannot_emit_custom_private_hold_text(tmp_path,monkeypatch):
    producers,_=producer_fixture(tmp_path,monkeypatch)
    def broken(**kw):raise r20.ProducerHold("SECRET_STAGE","RAW_PRIVATE_TEXT")
    producers["owners"]["BASELINE"]["produce"]=broken
    result=r20.complete(QUERY,tmp_path,now=NOW,producers=producers)
    assert result["reason"]=="OWNER_PRODUCER_EXECUTION_UNVERIFIED"
    assert "RAW_PRIVATE_TEXT" not in json.dumps(result)

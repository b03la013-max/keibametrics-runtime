"""Single-call FNB chat → private verified 29-index/KRS/six-method ticket completion.

This is an executable bridge, not an independent data provider or a model.
It reuses a completed original or a pre-existing private Work bundle. When
neither exists, an explicitly pinned, separately qualified private binding
can acquire SOURCE and execute existing fixed Owner producers. Their actual
prediction bytes are verified before an immutable inbox bundle is published.
The existing R14→R17→R18→R19 path then executes without per-race manual JSON.

No placeholder tickets, no synthetic owner policy, no NAR access bypass, no
Production scope permission, no signing, no OOS registration or real purchase.
A private Work actor must acquire and persist lawful original source/model
packets before the cutoff. No full packet: explicit HOLD, not NO-BET.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
import re
from pathlib import Path
import tempfile

from runtime.local_fnb_r19_chat_readback import parse_intent, readback
from runtime.local_fnb_r14_private_dual_krs import ENGINE_SHA, MAP_SHA

PROFILE="KM-FNB-R20-CHAT-PRIVATE-ONE-TRIGGER-SIX-METHODS-v1"
CLASSIFICATION="SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS"

class ProducerHold(ValueError):
    def __init__(self,stage,code):
        self.stage,self.code=stage,code
        super().__init__(code)

@contextmanager
def _race_lock(root,intent):
    # One private filesystem/Actor only; this is not a distributed Origin lock.
    root.mkdir(parents=True,exist_ok=True,mode=0o700)
    name=f".FNB_{intent['race_date']}_R{intent['race_no']:02d}.lock"
    fd=os.open(root/name,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
    try:
        try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ProducerHold("WORK_ACTOR","PRIVATE_RACE_EXECUTION_ALREADY_RUNNING") from exc
        yield
    finally:
        os.close(fd)

def _binding(root):
    """Load only an explicitly pinned, already admitted private Actor binding.

    This connector neither creates a model nor grants a provider licence.
    An operator connects the real qualified producers once; no per-race
    bundle assembly or executable command from a prediction request is used.
    """
    path=root/"FNB_PRODUCERS.py"
    pin=os.environ.get("KM_FNB_PRODUCER_BINDING_SHA256","")
    if not path.is_file():
        raise ProducerHold("SOURCE_PRODUCER","SOURCE_PRODUCER_NOT_CONNECTED")
    if (path.is_symlink() or not re.fullmatch(r"[0-9a-f]{64}",pin)
            or hashlib.sha256(path.read_bytes()).hexdigest()!=pin):
        raise ProducerHold("WORK_ACTOR","PRIVATE_PRODUCER_BINDING_SHA_UNVERIFIED")
    # Execute exactly the bytes that were hashed, without a second path/pyc read.
    data=path.read_bytes()
    if hashlib.sha256(data).hexdigest()!=pin:
        raise ProducerHold("WORK_ACTOR","PRIVATE_PRODUCER_BINDING_SHA_UNVERIFIED")
    namespace={"__name__":"_km_fnb_producers_"+pin,"__file__":str(path)}
    try:
        exec(compile(data,str(path),"exec"),namespace)
        return namespace["get_producers"]()
    except Exception as exc:
        raise ProducerHold("WORK_ACTOR","PRIVATE_PRODUCER_BINDING_EXECUTION_UNVERIFIED") from exc

def _private_target(root,name):
    """Reject ancestor links before any legacy writer receives this path.

    The pinned private Actor is trusted code, not a sandbox for hostile plugins.
    The per-race lock coordinates only this filesystem, never other hosts.
    """
    relative=Path(name)
    if relative.is_absolute() or any(p in ("..",".") for p in relative.parts):
        raise ProducerHold("PRIVATE_STORE","PRIVATE_PATH_OUTSIDE_STORE")
    path=root
    for part in relative.parts:
        path=path/part
        if path.is_symlink() or (path.resolve()!=root and root not in path.resolve().parents):
            raise ProducerHold("PRIVATE_STORE","PRIVATE_PATH_OUTSIDE_STORE")
    return path

def _time(value):
    stamp=datetime.fromisoformat(str(value).replace("Z","+00:00"))
    if stamp.tzinfo is None:
        raise ProducerHold("TIME","PRODUCER_AWARE_TIME_REQUIRED")
    return stamp

def _prestart(request,clock,diagnostic_only):
    observed=clock()
    if observed.tzinfo is None:
        raise ProducerHold("TIME","PRODUCER_AWARE_TIME_REQUIRED")
    if observed>=_time(request["prediction_cutoff"]) and not diagnostic_only:
        raise ProducerHold("TIME","PRESTART_CUTOFF_EXPIRED_DIAGNOSTIC_REQUIRED")
    return observed

def _request_identity(request,intent):
    prefix=f"KM-LOCAL-FNB-{intent['race_date'].replace('-','')}-R{intent['race_no']:02d}"
    if (not isinstance(request,dict) or request.get("family_id")!="LOCAL"
            or request.get("venue_id")!="FNB" or request.get("race_date")!=intent["race_date"]
            or request.get("race_no")!=intent["race_no"]
            or not isinstance(request.get("race_id"),str)
            or not re.fullmatch(re.escape(prefix)+r"(?:-[A-Za-z0-9_]+)*",request["race_id"])):
        raise ProducerHold("SOURCE","FNB_R20_REQUEST_RACE_IDENTITY_MISMATCH")

def _verify_captured_source(source,request,observed):
    # Existing offline extractor replays the real card bytes. This does not
    # grant a provider licence, change robots policy, or issue a signed SOURCE.
    from runtime.local_fnb_r8_card_raw_check import check_card
    if _time(source["source_freeze_at"])>observed:
        raise ProducerHold("SOURCE","SOURCE_OBSERVATION_IN_FUTURE")
    cards=[s for s in source["sources"] if s.get("official") is True and
           s.get("source_class")=="OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT"]
    if len(cards)!=1:
        raise ProducerHold("SOURCE","SOURCE_ADMISSION_UNVERIFIED")
    parsed=check_card(cards[0],request["race_date"],request["race_no"])
    if _time(parsed["fetched"])>_time(source["source_freeze_at"]):
        raise ProducerHold("SOURCE","SOURCE_OBSERVATION_IN_FUTURE")
    evidence=(source.get("normalized_evidence") or {}).get("race_card_tables") or {}
    if (evidence.get("value")!=parsed["extracted"].get("race_card_tables")
            or evidence.get("snapshot_sha256")!=cards[0]["snapshot_sha256"]):
        raise ProducerHold("SOURCE","SOURCE_RAW_NORMALIZED_EVIDENCE_MISMATCH")

def _put_original(root,name,value):
    from runtime.local_fnb_r13_private_single_numeric import _encoded
    path=_private_target(root,name)
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    data=value if isinstance(value,bytes) else _encoded(value)
    if path.exists():
        if path.is_symlink() or path.read_bytes()!=data:
            raise ProducerHold("PRIVATE_BUNDLE","PRIVATE_ORIGINAL_REVISION_CONFLICT")
    else:
        # Publish without replacing any original, even from an uncoordinated
        # writer. The temporary file is never a completed inbox bundle.
        with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as f:
            temporary=Path(f.name);f.write(data);f.flush();os.fsync(f.fileno())
        try:
            os.chmod(temporary,0o600)
            try:os.link(temporary,path)
            except FileExistsError as exc:
                raise ProducerHold("PRIVATE_BUNDLE","PRIVATE_ORIGINAL_REVISION_CONFLICT") from exc
        finally:temporary.unlink(missing_ok=True)
    if path.read_bytes()!=data:
        raise ProducerHold("PRIVATE_BUNDLE","PRIVATE_BUNDLE_SHA_MISMATCH")
    return {"path":str(path.relative_to(root)),"sha256":hashlib.sha256(data).hexdigest()}

def _model(root,entry,owner,request,observed):
    if not isinstance(entry,dict) or not callable(entry.get("produce")):
        raise ProducerHold("OWNER","OWNER_MODEL_NOT_FOUND")
    model=_load_json(root,entry.get("model"),owner+"_MODEL")
    proof=_load_json(root,entry.get("qualification"),owner+"_QUALIFICATION")
    scope=model.get("scope") or {}
    if (not model.get("model_id") or not model.get("model_version")
            or scope.get("family_id")!="LOCAL" or "FNB" not in scope.get("venues",[])
            or scope.get("classification")!=CLASSIFICATION
            or proof.get("model_sha256")!=entry["model"]["sha256"]
            or proof.get("model_id")!=model["model_id"]
            or proof.get("owner")!=owner or proof.get("venue_id")!="FNB"
            or proof.get("classification")!=CLASSIFICATION
            or proof.get("decision")!="ADOPTED_PRIVATE_RESEARCH"):
        raise ProducerHold("OWNER","OWNER_MODEL_SCOPE_MISMATCH")
    effective=datetime.fromisoformat(proof["effective_at"].replace("Z","+00:00"))
    cutoff=datetime.fromisoformat(request["prediction_cutoff"].replace("Z","+00:00"))
    if effective.tzinfo is None or effective>=cutoff or effective>observed:
        raise ProducerHold("OWNER","OWNER_MODEL_SCOPE_MISMATCH")
    # The existing admission record is immutable evidence supplied by the
    # qualified Work Actor, not a Production/consumer authorization here.
    return model

def _build_from_producers(intent,root,clock,diagnostic_only,producers):
    """Actual orchestration; no empty bundle is ever published on a HOLD."""
    from runtime.local_fnb_r13_private_source_admission import admit,PURPOSE,SCOPE
    from runtime.local_fnb_r13_private_single_numeric import execute as numerical
    if not isinstance(producers,dict) or not callable(producers.get("source")):
        raise ProducerHold("SOURCE_PRODUCER","SOURCE_PRODUCER_NOT_CONNECTED")
    try:captured=producers["source"](intent=dict(intent),private_root=root,now=clock())
    except ValueError as exc:
        # Preserve the first actual layer without disclosing a private URL,
        # credential or Raw embedded in an arbitrary producer exception.
        # Match known error prefixes, not substrings supplied by a callback.
        code=str(exc).partition(":")[0]
        if code in {"SOURCE_DNS_RESOLUTION_FAILED", "SOURCE_DNS_EMPTY"}:
            failure=code
        elif code.startswith("SOURCE_POLICY_"):
            failure="SOURCE_ACCESS_POLICY_BLOCKED"
        elif code == "SOURCE_HTTP_STATUS":
            failure="SOURCE_HTTP_STATUS_FAILED"
        else:
            failure="SOURCE_CONNECTION_FAILED"
        raise ProducerHold("SOURCE",failure) from exc
    request,source=captured["request"],captured["source"]
    _request_identity(request,intent)
    observed=_prestart(request,clock,diagnostic_only)
    public=Path(__file__).resolve().parents[1]
    admit(source=source,request=request,purpose=PURPOSE,classification=SCOPE,
          destination=root,public_repo_root=public)
    _verify_captured_source(source,request,observed)
    models=deepcopy(producers.get("owners") or {})
    admitted={owner:_model(root,models.get(owner),owner,request,observed)
              for owner in ("BASELINE","CANDIDATE")}
    if (models["BASELINE"]["model"]["sha256"]==models["CANDIDATE"]["model"]["sha256"]
            or admitted["BASELINE"]["model_id"]==admitted["CANDIDATE"]["model_id"]):
        raise ProducerHold("OWNER","OWNER_MODEL_SCOPE_MISMATCH")
    engine=_asset_path(producers.get("engine"),ENGINE_SHA,"ENGINE")
    params=_asset_path(producers.get("params"),MAP_SHA,"MAP")
    target=_private_target(root,request["race_id"])
    if target.exists():
        raise ProducerHold("PRIVATE_STORE","PRIVATE_ORIGINAL_REVISION_CONFLICT")
    # Do not overwrite a prior freeze while preparing an Owner. R14 will
    # independently reproduce and compare the frozen numeric SHA downstream.
    with tempfile.TemporaryDirectory(dir=root) as staging:
        num=numerical(source_artifact=source,request=request,private_root=Path(staging),
                      repo_root=public,now=_prestart(request,clock,diagnostic_only),
                      diagnostic_only=diagnostic_only)
        frozen_bytes=(Path(staging)/request["race_id"]/"numerical_materialization.json").read_bytes()
        if hashlib.sha256(frozen_bytes).hexdigest()!=num["private_materialization_sha256"]:
            raise ProducerHold("NUMERICAL","PRIVATE_BUNDLE_SHA_MISMATCH")
    frozen=json.loads(frozen_bytes)
    active={int(r["runner_id"]) for r in frozen["runners"]}
    packets={}
    for owner in ("BASELINE","CANDIDATE"):
        # Each existing fixed model executes independently against the same
        # immutable SOURCE and numerical freeze. No rank or Role is invented.
        observed=_prestart(request,clock,diagnostic_only)
        try:
            p=models[owner]["produce"](request=json.loads(json.dumps(request)),
                source=json.loads(json.dumps(source)),numerical=json.loads(frozen_bytes),
                numerical_sha256=num["private_materialization_sha256"],model=deepcopy(admitted[owner]),
                private_root=root,now=observed)
        except Exception as exc:
            raise ProducerHold("OWNER","OWNER_PRODUCER_EXECUTION_UNVERIFIED") from exc
        observed=_prestart(request,clock,diagnostic_only)
        krs,semantics=p["krs"],p["semantics"]
        from runtime.local_fnb_r14_private_dual_krs import _check_input
        if (set(_check_input(krs,owner,request["race_id"]))!=active
                or krs["race"]["date"].replace("/","-")!=request["race_date"]
                or krs["race"]["race_no"]!=request["race_no"]):
            raise ProducerHold("OWNER","OWNER_PREDICTION_NOT_FROZEN")
        prediction=_load_json(root,p.get("prediction"),owner+"_PREDICTION_ORIGINAL")
        prediction_sha=p["prediction"]["sha256"]
        if (prediction.get("model_id")!=admitted[owner]["model_id"]
                or prediction.get("model_version")!=admitted[owner]["model_version"]
                or prediction.get("model_sha256")!=models[owner]["model"]["sha256"]
                or prediction.get("owner")!=owner or prediction.get("race_id")!=request["race_id"]
                or prediction.get("source_snapshot_sha256")!=source["source_snapshot_sha256"]
                or prediction.get("numerical_materialization_sha256")!=num["private_materialization_sha256"]
                or prediction.get("classification")!=CLASSIFICATION
                or sorted(prediction.get("active_runners") or [])!=sorted(active)
                or not _time(source["source_freeze_at"])<=_time(prediction["freeze_at"])<=observed
                or _time(prediction["freeze_at"])>=_time(request["prediction_cutoff"])
                or prediction.get("krs_input")!={k:v for k,v in krs.items() if k!="original_prediction_sha256"}
                or prediction.get("semantics")!={k:v for k,v in semantics.items() if k!="original_prediction_sha256"}):
            raise ProducerHold("OWNER","OWNER_PREDICTION_NOT_FROZEN")
        if (p.get("model_id")!=admitted[owner]["model_id"]
                or p.get("model_sha256")!=models[owner]["model"]["sha256"]
                or krs.get("owner")!=owner or semantics.get("owner")!=owner
                or krs.get("numerical_materialization_sha256")!=num["private_materialization_sha256"]
                or semantics.get("numerical_materialization_sha256")!=num["private_materialization_sha256"]
                or semantics.get("source_snapshot_sha256")!=source.get("source_snapshot_sha256")
                or semantics.get("race_id")!=request["race_id"]
                or semantics.get("family_id")!="LOCAL" or semantics.get("venue_id")!="FNB"
                or semantics.get("classification")!="PRIVATE_NONPRODUCTION_FIXED_OWNER"
                or not isinstance(semantics.get("role_registry"),list)
                or {int(row["runner_id"]) for row in semantics["role_registry"]}!=active
                or any(not isinstance(semantics.get(key),list) for key in ("pair_dispositions","third_dispositions"))
                or {int(h["horse_no"]) for h in krs.get("horses",[])}!=active
                or krs.get("original_prediction_sha256")!=prediction_sha
                or semantics.get("original_prediction_sha256")!=prediction_sha
                or not re.fullmatch(r"[0-9a-f]{64}",str(krs.get("original_prediction_sha256") or ""))):
            raise ProducerHold("OWNER","OWNER_PREDICTION_NOT_FROZEN")
        packets[owner]=deepcopy(p)
    conditions=[packets[o]["krs"]["race"] for o in ("BASELINE","CANDIDATE")]
    if any(conditions[0].get(k)!=conditions[1].get(k) for k in
           ("date","race_no","racecourse","distance_m","surface","direction")):
        raise ProducerHold("OWNER","OWNER_PREDICTION_NOT_FROZEN")
    if packets["BASELINE"]["krs"]["original_prediction_sha256"]==packets["CANDIDATE"]["krs"]["original_prediction_sha256"]:
        raise ProducerHold("OWNER","OWNER_PREDICTION_NOT_FROZEN")
    folder="producer_inputs/"+request["race_id"]
    _prestart(request,clock,diagnostic_only)
    bundle={"venue_id":"FNB","race_date":intent["race_date"],"race_no":intent["race_no"],
            "classification":CLASSIFICATION,"request":_put_original(root,folder+"/request.json",request),
            "source":_put_original(root,folder+"/source.json",source),"owners":{},
            "engine":{"path":str(engine)},"params":{"path":str(params)},
            "producer_bundle_version":1,"producer_model_evidence":{},
            "independent_model_adoption_attested_here":False,
            "producer_numeric_freeze":_put_original(root,folder+"/numerical.json",frozen)}
    for owner in ("BASELINE","CANDIDATE"):
        bundle["owners"][owner]={key:_put_original(root,folder+"/"+owner+"_"+key+".json",packets[owner][key])
                                 for key in ("krs","semantics")}
        original=packets[owner]["prediction"]
        bundle["owners"][owner]["prediction"]=_put_original(root,folder+"/"+owner+"_prediction.json",
            _read_file(root,original,owner+"_ORIGINAL").read_bytes())
        bundle["producer_model_evidence"][owner]={key:_put_original(root,
            folder+"/"+owner+"_"+key+".json",_read_file(root,models[owner][key],owner+"_"+key).read_bytes())
            for key in ("model","qualification")}
    # This is the last write: only a fully qualified set becomes an inbox item.
    name=f"inbox/FNB_{intent['race_date']}_R{intent['race_no']:02d}_private_bundle.json"
    _prestart(request,clock,diagnostic_only)
    return _put_original(root,name,bundle)

def _producer_evidence(bundle,root,request,source,owner_inputs,semantics,observed):
    """Recheck immutable Producer originals on resumption, before any KRS.

    Admission records are supplied external trust inputs, not issued here.
    Byte consistency never establishes new Model/Production permissions.
    """
    if bundle.get("producer_bundle_version")!=1:
        raise ProducerHold("PRIVATE_BUNDLE","PRIVATE_PRODUCER_BUNDLE_VERSION_INVALID")
    numeric=_load_json(root,bundle["producer_numeric_freeze"],"PRODUCER_NUMERIC")
    numeric_sha=bundle["producer_numeric_freeze"]["sha256"]
    active={int(r["runner_id"]) for r in numeric["runners"]}
    ids=[]
    for owner in ("BASELINE","CANDIDATE"):
        refs=bundle["producer_model_evidence"][owner]
        model=_model(root,{**refs,"produce":lambda:None},owner,request,observed)
        ids.append(model["model_id"])
        ref=bundle["owners"][owner]["prediction"]
        prediction=_load_json(root,ref,owner+"_PREDICTION_ORIGINAL")
        krs,sem=owner_inputs[owner],semantics[owner]
        if (prediction.get("model_id")!=model["model_id"]
                or prediction.get("model_version")!=model["model_version"]
                or prediction.get("model_sha256")!=refs["model"]["sha256"]
                or prediction.get("owner")!=owner or prediction.get("race_id")!=request["race_id"]
                or prediction.get("source_snapshot_sha256")!=source["source_snapshot_sha256"]
                or prediction.get("numerical_materialization_sha256")!=numeric_sha
                or prediction.get("classification")!=CLASSIFICATION
                or set(prediction.get("active_runners") or [])!=active
                or not _time(source["source_freeze_at"])<=_time(prediction["freeze_at"])<=observed
                or _time(prediction["freeze_at"])>=_time(request["prediction_cutoff"])
                or krs.get("original_prediction_sha256")!=ref["sha256"]
                or sem.get("original_prediction_sha256")!=ref["sha256"]
                or prediction.get("krs_input")!={k:v for k,v in krs.items() if k!="original_prediction_sha256"}
                or prediction.get("semantics")!={k:v for k,v in sem.items() if k!="original_prediction_sha256"}):
            raise ProducerHold("OWNER","OWNER_PREDICTION_NOT_FROZEN")
    if len(set(ids))!=2:
        raise ProducerHold("OWNER","OWNER_MODEL_SCOPE_MISMATCH")

def _hold(intent, stage, code):
    return {"profile":PROFILE,"status":"EXECUTION_HOLD_NOT_NO_BET",
            "intent":intent,"first_failed_stage":stage,"reason":code,
            "six_method_ticket_delivery_proven":False,
            "recipient_delivery_ack":False,"actual_purchase":False,
            "registered_oos_increment":0}

def _read_file(root, spec, label):
    if not isinstance(spec,dict) or set(spec)!={"path","sha256"}:
        raise ValueError("FNB_R20_"+label+"_PATH_AND_SHA_REQUIRED")
    name=spec["path"]
    expected=spec["sha256"]
    if not isinstance(name,str) or not name or not isinstance(expected,str) or len(expected)!=64:
        raise ValueError("FNB_R20_"+label+"_REF_INVALID")
    p=(root/name).resolve() if not Path(name).is_absolute() else Path(name).resolve()
    if p!=root and root not in p.parents:
        raise ValueError("FNB_R20_"+label+"_NOT_IN_PRIVATE_ROOT")
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
        raise ValueError("FNB_R20_"+label+"_BYTES_MISSING_OR_SHA_MISMATCH")
    return p

def _load_json(root, spec, label):
    p=_read_file(root,spec,label)
    data=p.read_bytes()
    if hashlib.sha256(data).hexdigest()!=spec["sha256"]:
        raise ValueError("FNB_R20_"+label+"_BYTES_MISSING_OR_SHA_MISMATCH")
    try:return json.loads(data)
    except (ValueError,UnicodeError) as exc:
        raise ValueError("FNB_R20_"+label+"_INVALID_JSON") from exc

def _asset_path(spec, expected_sha, label):
    if not isinstance(spec,dict) or not isinstance(spec.get("path"),str):
        raise ValueError("FNB_R20_"+label+"_PATH_MISSING")
    p=Path(spec["path"]).resolve()
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected_sha:
        raise ValueError("FNB_R20_"+label+"_CURRENT_FROZEN_SHA_MISMATCH")
    return p

def _public_ci():
    return any(os.environ.get(k,"").lower() not in ("","false","0")
               for k in ("CI","GITHUB_ACTIONS"))

def complete(query, private_root, *, now=None, diagnostic_only=False, emit_private_body=False,
             producers=None,clock=None):
    # A supplied fixed now is for deterministic offline tests. The CLI supplies
    # neither: callbacks and downstream dispatch always receive fresh UTC time.
    clock=clock or ((lambda:now) if now is not None else lambda:datetime.now(timezone.utc))
    now=clock()
    intent=parse_intent(query,now)
    root=Path(private_root).resolve()
    public=Path(__file__).resolve().parents[1]
    if root==public or public in root.parents:
        return _hold(intent,"PRIVATE_STORE","PUBLIC_REPOSITORY_FORBIDDEN_FOR_HORSE_DATA")
    if emit_private_body and _public_ci():
        return _hold(intent,"PRIVATE_DELIVERY","PRIVATE_HORSE_OR_TICKET_BODY_PUBLIC_CI_FORBIDDEN")
    try:
        with _race_lock(root,intent):
            return _complete(query,root,now=now,diagnostic_only=diagnostic_only,
                emit_private_body=emit_private_body,producers=producers,clock=clock)
    except ProducerHold as exc:
        safe=lambda value:isinstance(value,str) and re.fullmatch(r"[A-Z][A-Z0-9_]{0,119}",value)
        if not safe(exc.stage) or not safe(exc.code):
            return _hold(intent,"PRODUCER","SOURCE_OR_OWNER_PRODUCER_INPUT_UNVERIFIED")
        result=_hold(intent,exc.stage,exc.code)
        if exc.code=="SOURCE_PRODUCER_NOT_CONNECTED":
            result["independent_owner_status"]="OWNER_MODEL_NOT_FOUND"
        return result
    except Exception:
        # Pinned bindings are private trusted Actor code, but their exception
        # text may contain Raw. Never print a traceback or callback message.
        return _hold(intent,"WORK_ACTOR","PRIVATE_ACTOR_EXECUTION_UNVERIFIED")

def _complete(query, private_root, *, now, diagnostic_only,emit_private_body,producers,clock):
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("FNB_R20_AWARE_NOW_REQUIRED")
    intent=parse_intent(query,now)
    root=Path(private_root).resolve()
    public_repo=Path(__file__).resolve().parents[1]
    if root==public_repo or public_repo in root.parents:
        return _hold(intent,"PRIVATE_STORE","PUBLIC_REPOSITORY_FORBIDDEN_FOR_HORSE_DATA")
    if emit_private_body and _public_ci():
        return _hold(intent,"PRIVATE_DELIVERY","PRIVATE_HORSE_OR_TICKET_BODY_PUBLIC_CI_FORBIDDEN")
    existing=readback(query,root,now)
    # Never re-run or silently replace a complete immutable original.
    formal_index=root/'formal_single_owner_intents'/f"{intent['race_date']}-R{intent['race_no']:02d}"/'completion.json'
    if existing["status"]=="VERIFIED_FROZEN_PRIVATE_BODY_READY_TO_RENDER" and not formal_index.exists():
        return {"profile":PROFILE,**existing,"source":"EXISTING_COMPLETE_ORIGINAL_READBACK",
                "new_prediction_executed":False}
    if existing.get("first_failed_stage") in ("REVISION","BODY_BYTES","CONTENT") and not formal_index.exists():
        return _hold(intent,existing["first_failed_stage"],existing["reason"])
    name=f"FNB_{intent['race_date']}_R{intent['race_no']:02d}_private_bundle.json"
    manifest_path=_private_target(root,"inbox/"+name)
    if not manifest_path.is_file() or formal_index.exists():
        if _public_ci():
            return _hold(intent,"WORK_ACTOR","PRIVATE_PRODUCER_EXECUTION_PUBLIC_CI_FORBIDDEN")
        try:
            connected=producers if producers is not None else _binding(root)
            if isinstance(connected,dict) and connected.get('entry_mode')=='FNB_ALTERNATIVE_PROVIDER_SINGLE_OWNER_V1':
                from runtime.local_fnb_alternative_connection import run as run_single, _index_path
                # Look up a real signed completion first. Otherwise an already
                # connected independent REFERENCE can be read without another
                # HTTP/Owner attempt at an unchanged known Formal failure.
                reference=connected.get('reference')
                def independent_reference(formal):
                    if not callable(reference):return None
                    try:
                        folder=reference(intent=deepcopy(intent),private_root=root,now=clock())
                        if folder is None:return None
                        from runtime.local_fnb_rakuten_reference import read_saved_reference
                        result=read_saved_reference(folder,intent,now=clock())
                        result['formal']=deepcopy(formal)
                        return result
                    except (ValueError,OSError,KeyError,TypeError):
                        # A broken reference cannot block a separately valid
                        # Formal execution or disguise its first failed stage.
                        return None
                if (callable(reference) and not (root/_index_path(intent)).exists()
                        and '正式' not in query and 'FORMAL' not in query.upper()):
                    result=independent_reference(connected.get('formal_first_failure') or
                        {'status':'NOT_EXECUTED_NO_SIGNED_FINAL_FOUND'})
                    if result is not None:return result
                try:
                    if diagnostic_only:raise ProducerHold('MODE','ALTERNATIVE_FORMAL_ROUTE_DIAGNOSTIC_EXECUTION_NOT_AUTHORIZED')
                    return run_single(intent,root,connected,clock=clock)
                except ProducerHold as exc:
                    formal=_hold(intent,exc.stage,exc.code)
                    result=independent_reference(formal)
                    if result is not None:return result
                    raise
                except (ValueError,OSError,KeyError,TypeError):
                    formal=_hold(intent,'READBACK','SIGNED_ORIGINAL_RECONCILIATION_REQUIRED')
                    result=independent_reference(formal)
                    if result is not None:return result
                    raise
            _build_from_producers(intent,root,clock,diagnostic_only,connected)
        except ProducerHold:
            raise
        except Exception as exc:
            raise ProducerHold("PRODUCER","SOURCE_OR_OWNER_PRODUCER_INPUT_UNVERIFIED") from exc
    try:
        bundle=json.loads(manifest_path.read_bytes())
        if (bundle.get("venue_id")!="FNB" or bundle.get("race_date")!=intent["race_date"]
                or bundle.get("race_no")!=intent["race_no"]
                or bundle.get("classification")!=CLASSIFICATION):
            raise ValueError("FNB_R20_PRIVATE_BUNDLE_SCOPE_OR_RACE_MISMATCH")
        request=_load_json(root,bundle.get("request"),"REQUEST")
        race_id=request.get("race_id")
        prefix=f"KM-LOCAL-FNB-{intent['race_date'].replace('-','')}-R{intent['race_no']:02d}"
        if (not isinstance(race_id,str) or not re.fullmatch(re.escape(prefix)+r"(?:-[A-Za-z0-9_]+)*",race_id)
                or request.get("venue_id")!="FNB"
                or request.get("race_date")!=intent["race_date"]
                or request.get("race_no")!=intent["race_no"]):
            raise ValueError("FNB_R20_REQUEST_RACE_IDENTITY_MISMATCH")
        cutoff=datetime.fromisoformat(request["prediction_cutoff"].replace("Z","+00:00"))
        if cutoff.tzinfo is None:
            raise ValueError("FNB_R20_UNVERIFIED_CUTOFF_TIMEZONE")
        if now>=cutoff and not diagnostic_only:
            return _hold(intent,"TIME","PRESTART_CUTOFF_EXPIRED_DIAGNOSTIC_REQUIRED")
        if request.get("family_id")!="LOCAL":
            raise ValueError("FNB_R20_LOCAL_ONLY")
        sources=[k for k in ("source","private_browser_html") if k in bundle]
        if len(sources)!=1:
            raise ValueError("FNB_R20_ONE_OFFICIAL_SOURCE_INPUT_REQUIRED")
        owners=bundle.get("owners")
        if not isinstance(owners,dict) or set(owners)!={"BASELINE","CANDIDATE"}:
            raise ValueError("FNB_R20_BOTH_FIXED_OWNER_PACKETS_NOT_FROZEN")
        owner_inputs={x:_load_json(root,owners[x].get("krs"),x+"_FROZEN_KRS")
                      for x in ("BASELINE","CANDIDATE")}
        semantics={x:_load_json(root,owners[x].get("semantics"),x+"_FROZEN_SEMANTIC")
                   for x in ("BASELINE","CANDIDATE")}
        if owner_inputs["BASELINE"].get("original_prediction_sha256")==owner_inputs["CANDIDATE"].get("original_prediction_sha256"):
            raise ValueError("FNB_R20_IDENTICAL_BASELINE_CANDIDATE_MODEL_FORBIDDEN")
        if any(semantics[x].get("original_prediction_sha256")!=owner_inputs[x].get("original_prediction_sha256")
               for x in ("BASELINE","CANDIDATE")):
            raise ValueError("FNB_R20_OWNER_SEMANTIC_KRS_MODEL_FREEZE_MISMATCH")
        if sources[0]=="source":
            source=_load_json(root,bundle["source"],"SOURCE")
            if isinstance(source,dict) and "artifact" in source and "receipt" in source:
                source=source["artifact"]
        else:
            from runtime.local_fnb_r16_private_browser_capture import ingest
            captured=_read_file(root,bundle["private_browser_html"],"ORIGINAL_HTML")
            url=bundle.get("browser_original_url")
            captured_at=bundle.get("browser_captured_at")
            if not isinstance(url,str) or not isinstance(captured_at,str):
                raise ValueError("FNB_R20_ORIGINAL_BROWSER_URL_AND_TIME_REQUIRED")
            ingest(html_path=captured,request=request,observed_url=url,
                   capture_time=captured_at,private_output=root,
                   public_repo=public_repo,diagnostic_only=diagnostic_only)
            source=json.loads((root/race_id/"unsigned_official_card_artifact.json").read_bytes())
        # Verify source identity/immutable bytes before even resolving executable assets.
        engine=_asset_path(bundle.get("engine"),ENGINE_SHA,"ENGINE")
        params=_asset_path(bundle.get("params"),MAP_SHA,"MAP")
        _private_target(root,race_id)
        now=_prestart(request,clock,diagnostic_only)
        if "producer_model_evidence" in bundle or "producer_bundle_version" in bundle:
            _producer_evidence(bundle,root,request,source,owner_inputs,semantics,now)
        from runtime.local_fnb_r14_private_work_entry import run
        # A slow Engine must not publish a prestart checkpoint after cutoff.
        # Complete R14 and verify R19 in private staging, then publish immutable
        # bytes with the completion checkpoint last. Existing originals stay.
        with tempfile.TemporaryDirectory(dir=root) as work:
            staging=Path(work)
            run(source=source,request=request,root=staging,public_repo=public_repo,
                owners=owner_inputs,frozen_semantics=semantics,
                engine=engine,params=params,now=now,diagnostic_only=diagnostic_only)
            observed=_prestart(request,clock,diagnostic_only)
            staged=readback(query,staging,observed)
            if staged["status"]!="VERIFIED_FROZEN_PRIVATE_BODY_READY_TO_RENDER":
                return _hold(intent,"DELIVERY_BODY",staged.get("reason","VERIFIED_FULL_BODY_MISSING"))
            folder=staging/race_id
            if folder.exists():
                paths=sorted(folder.iterdir(),key=lambda p:p.name=="private_pipeline_checkpoint.json")
                for path in paths:
                    if path.is_symlink() or not path.is_file():
                        raise ProducerHold("PRIVATE_STORE","PRIVATE_STAGED_ORIGINAL_INVALID")
                    _prestart(request,clock,diagnostic_only)
                    _put_original(root,race_id+"/"+path.name,path.read_bytes())
        complete_original=readback(query,root,now)
        if complete_original["status"]!="VERIFIED_FROZEN_PRIVATE_BODY_READY_TO_RENDER":
            return _hold(intent,"DELIVERY_BODY",complete_original.get("reason","VERIFIED_FULL_BODY_MISSING"))
        return {"profile":PROFILE,**complete_original,"source":"NEW_PRIVATE_COMPLETE_EXECUTION",
                "new_prediction_executed":True}
    except (ValueError, OSError, KeyError, TypeError) as exc:
        # Never turn computation failure into a computed 0-ticket NO-BET.
        if isinstance(exc,ProducerHold):
            raise
        code=str(exc).split(":")[0]
        if not re.fullmatch(r"FNB_[A-Z0-9_]{1,120}",code):
            code="SOURCE_TO_SIX_METHOD_EXECUTION_UNVERIFIED"
        return _hold(intent,"SOURCE_TO_SIX_METHOD",code)

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--query",required=True)
    p.add_argument("--private-root",required=True)
    p.add_argument("--diagnostic-only",action="store_true")
    p.add_argument("--emit-private-full-body",action="store_true")
    args=p.parse_args(argv)
    result=complete(args.query,Path(args.private_root),
                    diagnostic_only=args.diagnostic_only,
                    emit_private_body=args.emit_private_full_body)
    ready=result["status"] in ("VERIFIED_FROZEN_PRIVATE_BODY_READY_TO_RENDER",
                               "VERIFIED_FORMAL_SINGLE_OWNER_BODY_READY_TO_RENDER",
                               "VERIFIED_REFERENCE_BODY_READY_TO_RENDER")
    if args.emit_private_full_body and ready:
        print(result["body"],end="")
    else:
        print(json.dumps({k:v for k,v in result.items() if k!="body"},
                         ensure_ascii=False,sort_keys=True))
    return 0 if ready else 2

if __name__=="__main__":
    raise SystemExit(main())

"""Read back a complete FNB private race original for venue-chat rendering.

Research-only, read-only adapter to the existing R14/R17/R18 private output.
It does not acquire official data, create predictions, authorize consumers,
issue FINAL signatures or certify user delivery. Never print horse content in
public CI; a private Work actor must explicitly request complete rendering.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, unicodedata
from datetime import datetime, timezone, timedelta
from pathlib import Path

JST=timezone(timedelta(hours=9))
COMPLETE="FULL_PRIVATE_PRESENTATION_READY_DELIVERY_ACK_UNVERIFIED"

def parse_intent(query, now=None):
    s=unicodedata.normalize("NFKC", query)
    matches=re.findall(r"(?:船橋|FNB)\s*(?:第)?\s*(\d{1,2})\s*(?:R|レース|競走)", s, re.I)
    any_races=re.findall(r"(\d{1,2})\s*(?:R|レース|競走)", s, re.I)
    if len(matches)!=1 or len(any_races)!=1 or not 1<=int(matches[0])<=12:
        raise ValueError("FNB_CHAT_EXACTLY_ONE_RACE_REQUIRED")
    if any(x in s for x in ("浦和","大井","川崎","園田","京都","JRA","ばんえい")):
        raise ValueError("FNB_CHAT_MIXED_VENUE")
    dates=re.findall(r"\d{4}-\d{2}-\d{2}", s)
    dates += [f"{y}-{int(m):02d}-{int(d):02d}" for y,m,d in re.findall(
        r"(\d{4})年(\d{1,2})月(\d{1,2})日",s)]
    if len(set(dates))>1:
        raise ValueError("FNB_CHAT_DATE_CONFLICT")
    if not dates and any(x in s for x in ("昨日","明日","あす","あした")):
        raise ValueError("FNB_CHAT_DATE_REQUIRED")
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("FNB_CHAT_AWARE_TIME_REQUIRED")
    day=dates[0] if dates else now.astimezone(JST).date().isoformat()
    datetime.strptime(day,"%Y-%m-%d")
    return {"venue_id":"FNB","race_date":day,"race_no":int(matches[0])}

def _hold(intent,code,stage):
    return {"status":"FULL_DELIVERY_NOT_COMPLETED","intent":intent,
        "reason":code,"first_failed_stage":stage,"computed_no_bet":False,
        "formal_final":False,"recipient_delivery_ack":False,
        "registered_oos_increment":0}

def _recheck_saved_presentation(folder,receipt,grade):
    """Rebuild the presentation from saved bytes without rerunning any Engine.

    This proves content consistency, not SOURCE licensing, signed execution,
    pre-cutoff timing, independent Owner approval or actual recipient delivery.
    Old originals without these saved inputs remain immutable and UNVERIFIED.
    """
    names={"numerical_materialization.json","private_dual_krs_receipt.json",
           "frozen_owner_semantics.json","six_alternative_method_portfolios.json"}
    names.update(owner+suffix for owner in ("BASELINE","CANDIDATE")
                 for suffix in ("_krs_input.json","_krs_output.json"))
    hashes=receipt.get("presentation_artifact_sha256")
    if not isinstance(hashes,dict) or set(hashes)!=names:
        raise ValueError("FNB_SAVED_PRESENTATION_INPUT_PROOF_MISSING")
    documents={}
    for name in sorted(names):
        p=folder/name
        if p.is_symlink() or not p.is_file() or p.resolve().parent!=folder.resolve():
            raise ValueError("FNB_SAVED_PRESENTATION_INPUT_BYTES_MISSING:"+name)
        data=p.read_bytes()
        if hashlib.sha256(data).hexdigest()!=hashes[name]:
            raise ValueError("FNB_SAVED_PRESENTATION_INPUT_SHA_MISMATCH:"+name)
        documents[name]=json.loads(data)
    semantics=documents["frozen_owner_semantics.json"]
    portfolios=documents["six_alternative_method_portfolios.json"]
    dual=documents["private_dual_krs_receipt.json"]
    if not isinstance(semantics,dict) or set(semantics)!={"BASELINE","CANDIDATE"}:
        raise ValueError("FNB_SAVED_FROZEN_OWNER_SEMANTICS_MISSING")
    source_shas={row.get("source_snapshot_sha256") for row in semantics.values()
                 if isinstance(row,dict)}
    if len(source_shas)!=1 or not isinstance(next(iter(source_shas)),str):
        raise ValueError("FNB_SAVED_OWNER_SOURCE_BINDING_MISMATCH")
    for owner in ("BASELINE","CANDIDATE"):
        proof=(dual.get("owners") or {}).get(owner) or {}
        if proof.get("candidate_or_baseline_input_sha256")!=hashes[owner+"_krs_input.json"]:
            raise ValueError("FNB_SAVED_KRS_INPUT_SHA_MISMATCH:"+owner)
        if proof.get("actual_output_sha256")!=hashes[owner+"_krs_output.json"]:
            raise ValueError("FNB_SAVED_KRS_OUTPUT_SHA_MISMATCH:"+owner)
    from runtime.local_fnb_r17_method_constructor import construct
    from runtime.local_fnb_r18_full_private_delivery import verified_full_delivery
    rebuilt=construct(race_id=folder.name,owner_semantics=semantics,
        private_root=folder.parent,dual_krs_manifest=dual,
        source_snapshot_sha256=next(iter(source_shas)),
        numerical_materialization_sha256=hashes["numerical_materialization.json"])
    if rebuilt["owners"]!=portfolios:
        raise ValueError("FNB_SAVED_TICKETS_NOT_FROZEN_COMMON_MEC_OUTPUT")
    classification=receipt.get("classification")
    if classification not in {"POSTCUTOFF_DIAGNOSTIC_ONLY",
            "SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS"}:
        raise ValueError("FNB_SAVED_PRIVATE_CLASSIFICATION_INVALID")
    expected=verified_full_delivery(race_id=folder.name,private_root=folder.parent,
        semantics=semantics,portfolios=portfolios,
        diagnostic_only=classification=="POSTCUTOFF_DIAGNOSTIC_ONLY",persist=False)
    for key in ("all_horses","all_29_index_cells","full_body_sha256"):
        if expected[key]!=grade.get(key):
            raise ValueError("FNB_SAVED_BODY_DIFFERS_FROM_FULL_INPUTS:"+key)

def readback(query, private_root, now=None):
    intent=parse_intent(query,now)
    root=Path(private_root).resolve()
    prefix=f"KM-LOCAL-FNB-{intent['race_date'].replace('-','')}-R{intent['race_no']:02d}"
    if not root.is_dir():
        return _hold(intent,"FNB_PRIVATE_STORE_UNAVAILABLE","PRIVATE_STORE")
    found=sorted(p for p in root.iterdir() if p.is_dir() and
        (p.name==prefix or p.name.startswith(prefix+"-")))
    if not found:
        return _hold(intent,"FNB_COMPLETE_ORIGINAL_NOT_FOUND","COMPLETE_ORIGINAL")
    if len(found)!=1:
        return _hold(intent,"FNB_MULTIPLE_REVISIONS_RECONCILIATION_REQUIRED","REVISION")
    folder=found[0]
    if folder.is_symlink() or folder.resolve().parent!=root:
        return _hold(intent,"FNB_PRIVATE_RACE_PATH_OUTSIDE_STORE","PRIVATE_STORE")
    path=folder/"private_pipeline_checkpoint.json"
    if path.is_symlink() or not path.is_file():
        return _hold(intent,"FNB_PRIVATE_CHECKPOINT_MISSING","PIPELINE")
    try:
        receipt=json.loads(path.read_bytes())
    except (UnicodeError,ValueError):
        return _hold(intent,"FNB_PRIVATE_CHECKPOINT_CORRUPT","PIPELINE")
    if not isinstance(receipt,dict):
        return _hold(intent,"FNB_PRIVATE_CHECKPOINT_CORRUPT","PIPELINE")
    if receipt.get("race_id")!=folder.name or receipt.get("status")!=COMPLETE:
        return _hold(intent,receipt.get("first_uncompleted_stage") or
            "FNB_UNFINISHED_PIPELINE","PIPELINE")
    grade=receipt.get("complete_private_full_horse_delivery_presentation") or {}
    if not isinstance(grade,dict):
        return _hold(intent,"FNB_FULL29_BC_KRS_SIX_METHOD_PROOF_MISSING","CONTENT")
    if (grade.get("status")!="FULL_PRESENTATION_READY_RECIPIENT_ACK_UNVERIFIED"
        or grade.get("private_body_roundtrip_verified") is not True
        or set(grade.get("two_owners") or [])!={"BASELINE","CANDIDATE"}
        or grade.get("six_alternative_methods") is not True
        or receipt.get("owner_six_methods_proven") is not True
        or receipt.get("two_owners_5000_seed1_executed") is not True
        or receipt.get("all29_source_feature_receipt_verified") is not True):
        return _hold(intent,"FNB_FULL29_BC_KRS_SIX_METHOD_PROOF_MISSING","CONTENT")
    count=grade.get("all_horses")
    if type(count) is not int or count<2 or grade.get("all_29_index_cells")!=count*29:
        return _hold(intent,"FNB_ALL_HORSE_29_CELL_COUNT_INVALID","CONTENT")
    name=grade.get("body_filename")
    sha=grade.get("full_body_sha256")
    if name!="FULL_ALL_HORSES_BC_SIX_METHODS.md" or not isinstance(sha,str) or not re.fullmatch(r"[0-9a-f]{64}",sha):
        return _hold(intent,"FNB_FULL_BODY_IDENTITY_INVALID","BODY_BYTES")
    file=folder/name
    if file.is_symlink() or not file.is_file():
        return _hold(intent,"FNB_FULL_BODY_NOT_SAVED","BODY_BYTES")
    data=file.read_bytes()
    if hashlib.sha256(data).hexdigest()!=sha:
        return _hold(intent,"FNB_FULL_BODY_SHA_MISMATCH","BODY_BYTES")
    try:
        body=data.decode("utf-8")
    except UnicodeError:
        return _hold(intent,"FNB_FULL_BODY_ENCODING_INVALID","BODY_BYTES")
    if any(s not in body for s in ("## BASELINE","## CANDIDATE",
                                   "## 全馬29指数","未使用")):
        return _hold(intent,"FNB_FULL_BODY_SECTIONS_INCOMPLETE","BODY_BYTES")
    try:
        _recheck_saved_presentation(folder,receipt,grade)
    except (OSError,ValueError,TypeError,KeyError,AttributeError) as exc:
        return _hold(intent,str(exc),"SAVED_CONTENT_PROOF")
    return {"status":"VERIFIED_FROZEN_PRIVATE_BODY_READY_TO_RENDER",
        "intent":intent,"race_id":folder.name,"classification":receipt.get("classification"),
        "body":body,"body_sha256":sha,"horse_count":count,"index_cell_count":count*29,
        "checkpoint_declares_six_methods":True,
        "presentation_content_recomputed_from_saved_inputs":True,
        "execution_signature_verified_by_readback":False,
        "formal_signed_final_proven":False,"recipient_delivery_ack":False,
        "actual_purchase":False,"registered_oos_increment":0}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--query",required=True)
    p.add_argument("--private-root",required=True)
    p.add_argument("--emit-private-full-body",action="store_true")
    a=p.parse_args(argv)
    result=readback(a.query,Path(a.private_root))
    if a.emit_private_full_body:
        if os.environ.get("CI")=="true" or os.environ.get("GITHUB_ACTIONS")=="true":
            raise ValueError("FNB_PRIVATE_BODY_PUBLIC_CI_FORBIDDEN")
        if result["status"]=="VERIFIED_FROZEN_PRIVATE_BODY_READY_TO_RENDER":
            print(result["body"],end="")
        else:
            print(json.dumps(result,ensure_ascii=False))
    else:
        print(json.dumps({k:v for k,v in result.items() if k!="body"},
                         ensure_ascii=False,sort_keys=True))
    return 0 if result["status"]=="VERIFIED_FROZEN_PRIVATE_BODY_READY_TO_RENDER" else 2

if __name__=="__main__":
    raise SystemExit(main())


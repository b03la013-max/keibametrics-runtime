from __future__ import annotations
import base64,datetime,hashlib,json,os,pathlib
from typing import Any,Dict
from fastapi import FastAPI,HTTPException
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from source_acquisition import acquire_sources,verify_source_artifact,sha_obj,utcnow
from jra_source_manifest import build_jra_manifest,race_card_url_from_meeting_key,result_url_from_meeting_key
from jra_runner_universe import enrich_source_artifact,validate_request_runners
from tsl_public_shadow_evidence import build_tsl_shadow_evidence,discover_tsl_race_url
from jma_weather_evidence import build_jma_weather_evidence
from jra_auxiliary_evidence import enrich_with_auxiliary_evidence
from jra_population_seed import enrich_with_population_seed
from jra_official_pdf import fetch_and_enrich_official_pdf
from jra_race_context import enrich_with_race_context
from jra_horse_history import enrich_with_horse_histories
from jra_race_card_detail import fetch_and_enrich_race_card_detail,runner_universes_from_detail

APP_VERSION="KM-JRA-SOURCE-RUNTIME-v1.4-20260926"
RECEIPT_SCHEMA="KM-JRA-SOURCE-SIGNED-RECEIPT-v1"
FAMILY="JRA"
SIGNER=os.environ.get("KM_JRA_SOURCE_SIGNER_KEY_ID","KM-JRA-SOURCE-ED25519-20260925")
PRIVATE_B64=os.environ.get("KM_JRA_SOURCE_PRIVATE_KEY_B64","")
GIT_REV=os.environ.get("KM_JRA_SOURCE_GITHUB_REV","UNKNOWN")
app=FastAPI(title="KeibaMetrics JRA Source Runtime",version=APP_VERSION)

def _jdump(x:Any)->bytes:
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")

def _private_key():
    if not PRIVATE_B64: raise RuntimeError("KM_JRA_SOURCE_PRIVATE_KEY_B64_REQUIRED")
    raw=base64.b64decode(PRIVATE_B64)
    if len(raw)!=32: raise RuntimeError("KM_JRA_SOURCE_PRIVATE_KEY_B64_INVALID")
    return Ed25519PrivateKey.from_private_bytes(raw)

def _public_b64():
    b=_private_key().public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
    return base64.b64encode(b).decode()

def _sha_file(name:str):
    p=pathlib.Path(__file__).parent/name
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None

def signed_receipt(race_id:str,status:str,artifact:Dict[str,Any],errors=None):
    receipt={
      "schema":RECEIPT_SCHEMA,"runtime_revision":APP_VERSION,"family":FAMILY,
      "phase":"SOURCE","race_id":race_id,"status":status,"errors":errors or [],
      "artifact_sha256":sha_obj(artifact),"timestamp":utcnow(),"github_revision":GIT_REV,
      "runtime_hashes":{
        "app_sha256":_sha_file("app.py"),"source_acquisition_sha256":_sha_file("source_acquisition.py"),
        "jra_source_manifest_sha256":_sha_file("jra_source_manifest.py"),
        "jra_runner_universe_sha256":_sha_file("jra_runner_universe.py"),
        "tsl_public_shadow_evidence_sha256":_sha_file("tsl_public_shadow_evidence.py"),
        "jma_weather_evidence_sha256":_sha_file("jma_weather_evidence.py"),
        "jra_auxiliary_evidence_sha256":_sha_file("jra_auxiliary_evidence.py"),
        "jra_population_seed_sha256":_sha_file("jra_population_seed.py"),
        "jra_official_pdf_sha256":_sha_file("jra_official_pdf.py"),
        "jra_race_context_sha256":_sha_file("jra_race_context.py"),
        "jra_horse_history_sha256":_sha_file("jra_horse_history.py"),
        "jra_race_card_detail_sha256":_sha_file("jra_race_card_detail.py"),
      }
    }
    rb=_jdump(receipt)
    return {"receipt":receipt,"receipt_sha256":hashlib.sha256(rb).hexdigest(),
            "signature":base64.b64encode(_private_key().sign(rb)).decode(),
            "signer_key_id":SIGNER,"signature_alg":"Ed25519","artifact":artifact}

def verify_envelope(env:Dict[str,Any])->bool:
    try:
        rec=env["receipt"]; rb=_jdump(rec)
        _private_key().public_key().verify(base64.b64decode(env["signature"]),rb)
        if hashlib.sha256(rb).hexdigest()!=env.get("receipt_sha256"): return False
        if sha_obj(env.get("artifact") or {})!=rec.get("artifact_sha256"): return False
        return True
    except Exception:return False

def _validate_family(p:Dict[str,Any]):
    if str(p.get("family_id") or "JRA").upper()!="JRA": raise HTTPException(422,"JRA_FAMILY_REQUIRED")

def _canonical_manifest_input(p:Dict[str,Any])->Dict[str,Any]:
    return {
      "venue_id":p.get("venue_id"),"race_date":p.get("race_date"),"race_no":p.get("race_no"),
      "official_race_card_url":p.get("official_race_card_url"),"jra_meeting_key":p.get("jra_meeting_key"),
      "same_day_result_urls":p.get("same_day_result_urls") or {},
    }

def _append_jra_card_specs(p:Dict[str,Any],meeting_key:str)->Dict[str,Any]:
    q=dict(p); existing=list(q.get("sources") or [])
    if any(str(x.get("source_id"))=="JRA-RACE-CARD" for x in existing if isinstance(x,dict)): return q
    mi=_canonical_manifest_input(q); mi["jra_meeting_key"]=meeting_key
    m=build_jra_manifest(mi)
    ids={str(x.get("source_id")) for x in existing if isinstance(x,dict)}
    q["sources"]=existing+[x for x in m["sources"] if str(x.get("source_id")) not in ids]
    return q

def _bind_source_identity(artifact:Dict[str,Any], race_id:str, ctx:Dict[str,Any])->Dict[str,Any]:
    artifact["family_id"]="JRA"
    artifact["race_id"]=str(race_id)
    artifact["source_race_context"]=dict(ctx)
    return artifact

def _rehash(artifact:Dict[str,Any]):
    raw_bundle=[{"source_id":s.get("source_id"),"raw_sha256":s.get("raw_sha256"),
                 "snapshot_sha256":s.get("snapshot_sha256"),"fetched_at":s.get("fetched_at"),
                 "final_url":s.get("final_url")} for s in artifact.get("sources") or []]
    artifact["raw_source_bundle_sha256"]=sha_obj(raw_bundle)
    artifact["source_snapshot_sha256"]=sha_obj({k:v for k,v in artifact.items() if k!="source_snapshot_sha256"})
    return artifact

@app.get("/health")
def health():
    try: pub=_public_b64(); status="READY"
    except Exception as e: pub=None; status="SIGNER_NOT_READY:"+str(e)
    return {"status":status,"family":"JRA","runtime_revision":APP_VERSION,"github_revision":GIT_REV,
            "receipt_signer_key_id":SIGNER,"receipt_public_key_b64":pub,
            "capabilities":["SOURCE_MANIFEST_JRA","SOURCE_ACQUIRE","SOURCE_VERIFY","SOURCE_RUNNER_UNIVERSE",
                            "SOURCE_JMA_WEATHER","SOURCE_JRA_AUXILIARY","SOURCE_JRA_POINT_IN_TIME_POPULATION_SEED","SOURCE_JRA_OFFICIAL_PDF_RUNNER_UNIVERSE","SOURCE_JRA_OFFICIAL_RACE_CONTEXT","SOURCE_JRA_OFFICIAL_RACE_CARD_DETAIL","SOURCE_TSL_PUBLIC_SHADOW"]}

@app.post("/source/manifest/jra")
def source_manifest(p:Dict[str,Any]):
    _validate_family(p)
    try:return build_jra_manifest(_canonical_manifest_input(p))
    except Exception as e: raise HTTPException(422,type(e).__name__+":"+str(e))

@app.post("/source/acquire")
def source_acquire(p:Dict[str,Any]):
    _validate_family(p); rid=str(p.get("race_id") or "")
    if not rid: raise HTTPException(422,"RACE_ID_REQUIRED")
    cutoff=str(p.get("prediction_cutoff") or "")
    q=dict(p)
    if not isinstance(q.get("sources"),list) or not q.get("sources"):
        m=build_jra_manifest(_canonical_manifest_input(q)); q["sources"]=m["sources"]
    ctx={"family_id":"JRA","venue_id":q.get("venue_id"),"race_date":q.get("race_date"),"race_no":int(q.get("race_no") or 0)}
    # Discover TSL meeting key from the public day index without granting TSL authority.
    meeting_key=str(q.get("jra_meeting_key") or "")
    tsl_discovery_error=None
    if not meeting_key:
        try:
            _,meeting_key,_=discover_tsl_race_url(ctx["venue_id"],ctx["race_date"],ctx["race_no"])
            q=_append_jra_card_specs(q,meeting_key)
        except Exception as e:
            tsl_discovery_error=type(e).__name__+":"+str(e)
    artifact,errors=acquire_sources(q); artifact=_bind_source_identity(artifact,rid,ctx)
    artifact["jra_meeting_key_discovered"]=meeting_key or None
    if tsl_discovery_error: artifact.setdefault("warnings",[]).append("TSL_MEETING_DISCOVERY:"+tsl_discovery_error)
    try:
        artifact=enrich_with_race_context(artifact)
    except Exception as e:
        artifact.setdefault("warnings",[]).append("JRA_RACE_CONTEXT_UNAVAILABLE:"+type(e).__name__+":"+str(e))

    # Official JRA PDF is the mandatory independent Runner Universe source.
    # JRADB HTML is retained only as auxiliary evidence because the public page
    # may render without server-side tables.
    pdf_runner_error=None
    try:
        if not meeting_key:
            raise ValueError("JRA_MEETING_KEY_REQUIRED_FOR_OFFICIAL_PDF")
        artifact=fetch_and_enrich_official_pdf(
            artifact,cutoff,
            race_date=ctx["race_date"],venue_id=ctx["venue_id"],
            race_no=ctx["race_no"],meeting_key=meeting_key
        )
    except Exception as e:
        pdf_runner_error=type(e).__name__+":"+str(e)
        artifact.setdefault("warnings",[]).append("JRA_OFFICIAL_PDF_RUNNER_UNIVERSE_UNAVAILABLE:"+pdf_runner_error)

    # Official JRA detailed race card contains current market snapshot, pedigree,
    # trainer/rider identity and up to four recent runs. It is Production-authorized
    # source material, but downstream feature categories still require registered evaluators.
    try:
        if not meeting_key:
            raise ValueError("JRA_MEETING_KEY_REQUIRED_FOR_RACE_CARD_DETAIL")
        artifact=fetch_and_enrich_race_card_detail(
            artifact,cutoff,race_date=ctx["race_date"],meeting_key=meeting_key,race_no=ctx["race_no"]
        )
    except Exception as e:
        artifact.setdefault("warnings",[]).append("JRA_RACE_CARD_DETAIL_UNAVAILABLE:"+type(e).__name__+":"+str(e))
        if q.get("require_jra_race_card_detail"):
            errors.append("JRA_RACE_CARD_DETAIL_REQUIRED_FAILED:"+type(e).__name__+":"+str(e))

    # Runner Universe policy: official PDF is preferred once published. Before the
    # PDF is available, the server-rendered official JRADB detailed card is a
    # same-authority JRA fallback. When both exist, their runner ID/name sets must agree.
    detail_u=artifact.get("jra_official_race_card_detail")
    if not artifact.get("jra_official_runner_universe") and detail_u:
        try:
            declared_u,active_u=runner_universes_from_detail(detail_u)
            artifact["jra_declared_runner_universe"]=declared_u
            artifact["jra_official_runner_universe"]=active_u
            artifact["jra_official_runner_universe_sha256"]=sha_obj(active_u)
            artifact["official_runner_universe"]=active_u
            artifact["official_runner_universe_sha256"]=active_u["runner_universe_sha256"]
            artifact["official_runner_source"]="JRA_OFFICIAL_JRADB_DETAIL_FALLBACK"
        except Exception as e:
            errors.append("JRA_DETAIL_RUNNER_UNIVERSE_FAILED:"+type(e).__name__+":"+str(e))
    elif artifact.get("jra_official_runner_universe") and detail_u:
        try:
            _,detail_active=runner_universes_from_detail(detail_u)
            p={int(x["horse_no"]):re.sub(r"\s+","",str(x.get("name") or "")) for x in (artifact["jra_official_runner_universe"].get("runners") or [])}
            h={int(x["horse_no"]):re.sub(r"\s+","",str(x.get("name") or "")) for x in (detail_active.get("runners") or [])}
            mismatch=(p!=h)
            artifact["official_runner_universe_reconciliation"]={"status":"PASS" if not mismatch else "MISMATCH","pdf_count":len(p),"detail_count":len(h)}
            if mismatch:
                errors.append("JRA_OFFICIAL_RUNNER_UNIVERSE_PDF_DETAIL_MISMATCH")
            else:
                artifact["official_runner_source"]="JRA_OFFICIAL_PDF_RECONCILED_WITH_JRADB_DETAIL"
        except Exception as e:
            errors.append("JRA_OFFICIAL_RUNNER_RECONCILIATION_FAILED:"+type(e).__name__+":"+str(e))
    if not artifact.get("jra_official_runner_universe"):
        errors.append("JRA_OFFICIAL_RUNNER_UNIVERSE_UNAVAILABLE:"+(pdf_runner_error or "PDF_NOT_AVAILABLE")+";DETAIL_FALLBACK_NOT_AVAILABLE")

    try:
        artifact,herrs=enrich_with_horse_histories(artifact,cutoff,require_history=bool(q.get("require_jra_horse_history",False)))
        errors.extend(herrs if q.get("require_jra_horse_history") else [])
        if herrs and not q.get("require_jra_horse_history"):
            artifact.setdefault("warnings",[]).extend(herrs)
    except Exception as e:
        if q.get("require_jra_horse_history"): errors.append("JRA_HORSE_HISTORY_REQUIRED_FAILED:"+type(e).__name__+":"+str(e))
        else: artifact.setdefault("warnings",[]).append("JRA_HORSE_HISTORY_UNAVAILABLE:"+type(e).__name__+":"+str(e))

    if isinstance(q.get("runners"),list) and artifact.get("jra_official_runner_universe"):
        ok,rerrs=validate_request_runners(artifact,q["runners"])
        artifact["request_runner_universe_match"]={"verified":ok,"errors":rerrs}
        errors.extend(rerrs)

    try:
        artifact,terr=build_tsl_shadow_evidence(artifact,cutoff,require_tsl=bool(q.get("require_tsl_shadow",False)))
        errors.extend(terr)
    except Exception as e:
        artifact["tsl_public_shadow_evidence"]={"profile":"KM-JRA-TSL-PUBLIC-SHADOW-EVIDENCE-v1.1-20260926","status":"UNAVAILABLE","production_authority":False,"prediction_authority":False,"error":str(e)}
        artifact["tsl_public_shadow_evidence_sha256"]=sha_obj(artifact["tsl_public_shadow_evidence"])
        if q.get("require_tsl_shadow"): errors.append("TSL_REQUIRED_FAILED:"+str(e))

    try:
        artifact,werrs=build_jma_weather_evidence(artifact,cutoff,require_weather=bool(q.get("require_jma_weather",False)))
        errors.extend(werrs)
    except Exception as e:
        if q.get("require_jma_weather"): errors.append("JMA_REQUIRED_FAILED:"+str(e))

    try: artifact=enrich_with_auxiliary_evidence(artifact)
    except Exception as e: artifact.setdefault("warnings",[]).append("JRA_AUXILIARY_UNAVAILABLE:"+type(e).__name__+":"+str(e))

    try: artifact=enrich_with_population_seed(artifact)
    except Exception as e: artifact.setdefault("warnings",[]).append("JRA_POPULATION_SEED_UNAVAILABLE:"+type(e).__name__+":"+str(e))

    artifact["errors"]=list(dict.fromkeys(errors))
    artifact["formal_ready"]=bool(not artifact["errors"] and artifact.get("jra_official_runner_universe"))
    _rehash(artifact)
    ok,verrs=verify_source_artifact(artifact)
    if not ok:
        artifact["errors"]=list(dict.fromkeys(artifact["errors"]+verrs)); artifact["formal_ready"]=False; _rehash(artifact)
    return signed_receipt(rid,"PASS" if artifact.get("formal_ready") else "FAIL",artifact,artifact.get("errors"))

@app.post("/source/verify")
def source_verify(env:Dict[str,Any]):
    valid=verify_envelope(env); artifact=env.get("artifact") or {}
    aok,aerrs=verify_source_artifact(artifact) if isinstance(artifact,dict) else (False,["SOURCE_ARTIFACT_INVALID"])
    valid=bool(valid and aok)
    return {"valid":valid,"verified":valid,"signer_key_id":SIGNER,"family":"JRA","artifact_errors":aerrs}

@app.post("/verify")
def verify(env:Dict[str,Any]):
    return source_verify(env)

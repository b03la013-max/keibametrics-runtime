"""Local JRA signed-SOURCE + formal Race Intent -> Blood-B private queue.

Never guess racing dates, issue fake signature receipts or backfill expired
intents as pre-race. This is diagnostic-only and provider-rights-gated. It only
prepares a queue: NO paid network access and NO Production BVI authority.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import fcntl
from typing import Any

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"runtime"))
from jra_bloodb_mac_collector import (
    HOME, BloodBError, official_universe, private_dir, utc_time
)
from jra_bloodb_mac_automation import load_official, VENUES

QUEUE=HOME/"bloodb_queue.json"
LOCK=HOME/"bloodb_queue_sync.lock"
REGEX=re.compile(r"^KM-JRA-([A-Z]{3})-(\d{8})-R(\d{2})(?:-LIVE-R\d+)?$")
VENUE_ID={"SPP":"札幌","HKD":"函館","FKS":"福島","NGT":"新潟",
          "TKY":"東京","NKY":"中山","CHK":"中京","KYO":"京都",
          "HSN":"阪神","KKR":"小倉"}
SIGNER="SOURCE_ED25519_ONLY_NOT_INDEPENDENT_OIDC_ATTESTED_HERE"

def _sha_file(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _intent(path:Path, *, now:datetime, horizon_h:int)->dict|None:
    try:
        row=json.loads(path.read_text(encoding="utf-8"))
        if row.get("family_id")!="JRA" or row.get("temporal_mode")!="FORMAL-PRE-RACE":
            return None
        race_id=row["race_id"]
        m=REGEX.fullmatch(race_id)
        if not m or len(race_id)!=len(f"KM-JRA-{m[1]}-{m[2]}-R{m[3]}"):
            return None
        venue_id,d8,n=m.groups()
        if row.get("venue_id")!=venue_id or venue_id not in VENUE_ID:
            return None
        when=datetime.strptime(d8,"%Y%m%d").date().isoformat()
        if row.get("race_date")!=when or int(row["race_no"])!=int(n):
            return None
        cutoff=utc_time(row["prediction_cutoff"])
        if cutoff<=now or cutoff-now>timedelta(hours=horizon_h):
            return None
        if (cutoff+timedelta(hours=9)).date().isoformat()!=when:
            return None
        post=utc_time(row["scheduled_post_at"])
        if not cutoff<post or post-cutoff>timedelta(minutes=30):
            return None
        if row.get("acceptance_only") is True:
            return None
        return {
            "race_id":race_id,"execution_id":row["execution_id"],
            "race_date":when,"race_no":int(n),
            "venue":VENUE_ID[venue_id],"prediction_cutoff":row["prediction_cutoff"],
            "scheduled_post_at":row["scheduled_post_at"],
            "race_intent_sha256":_sha_file(path),
        }
    except (KeyError,TypeError,ValueError,OverflowError,OSError):
        return None

def _source_candidates(root:Path,execution_id:str)->list[Path]:
    # Only formal acquisition artifacts belonging to the SAME execution ID.
    return sorted((root/"runtime/executions"/execution_id/"SOURCE/runs").glob(
        "*/source_receipt_envelope.json"))

def _race_binding(root:Path, intent:dict)->tuple[Path,dict]:
    valid=[]
    for source in _source_candidates(root,intent["execution_id"]):
        try:
            spec=dict(intent,signed_source_envelope_path=str(source))
            official,provenance=load_official(spec)
            if not (2<=len(official)<=18):
                continue
            env=json.loads(source.read_text(encoding="utf-8"))
            art=env["artifact"]
            if art.get("formal_ready") is False or art.get("errors"):
                continue
            source_cutoff=utc_time(art["prediction_cutoff"])
            if source_cutoff!=utc_time(intent["prediction_cutoff"]):
                continue
            frozen=utc_time(art["source_freeze_at"])
            if frozen>=source_cutoff:
                continue
            if frozen>utc_time(intent["scheduled_post_at"]):
                continue
            valid.append((frozen,source,provenance))
        except (KeyError,ValueError,TypeError,OSError):
            continue
    if not valid:
        raise BloodBError("JRA_SIGNED_SOURCE_FOR_RACE_NOT_VERIFIABLE")
    # If several signed runs are present, choose latest pre-cutoff SOURCE
    # only if no two top-frozen sources conflict at the same instant.
    valid.sort(key=lambda z:z[0],reverse=True)
    if len(valid)>1 and valid[0][0]==valid[1][0] and _sha_file(valid[0][1])!=_sha_file(valid[1][1]):
        raise BloodBError("JRA_SOURCE_AMBIGUOUS_EQUAL_FREEZE_TIME")
    return valid[0][1], valid[0][2]

def collect_specs(root:Path, *, now:datetime, horizon_h:int=36,
                  max_intents:int=200)->tuple[list[dict],dict]:
    if not 1<=horizon_h<=72:
        raise BloodBError("QUEUE_LOOKAHEAD_INVALID")
    files=sorted((root/"runtime/jra_formal_intents").glob("*.json"))
    specs=[]
    stats={"candidate_intents":0,"signed_source_ready":0,
           "skipped_source_missing":0,"skipped_deduplicated":0}
    candidates=[]
    for path in files:
        item=_intent(path,now=now,horizon_h=horizon_h)
        if item:
            candidates.append(item)
    stats["candidate_intents"]=len(candidates)
    if len(candidates)>max_intents:
        raise BloodBError("TOO_MANY_FUTURE_INTENTS")
    seen={}
    for candidate in candidates:
        rid=candidate["race_id"]
        if rid in seen:
            # Do not silently select whichever future request sorts last.
            if candidate["prediction_cutoff"]!=seen[rid]["prediction_cutoff"]:
                raise BloodBError("CONFLICTING_JRA_RACE_INTENTS:"+rid)
            stats["skipped_deduplicated"]+=1
            continue
        seen[rid]=candidate
    for item in seen.values():
        try:
            source,origin=_race_binding(root,item)
        except BloodBError:
            stats["skipped_source_missing"]+=1
            continue
        specs.append({
            "race_id":item["race_id"],"race_date":item["race_date"],
            "race_no":item["race_no"],"venue":item["venue"],
            "prediction_cutoff":item["prediction_cutoff"],
            "signed_source_envelope_path":str(source.resolve()),
            "race_intent_sha256":item["race_intent_sha256"],
            "jra_signed_source_artifact_sha256":origin["source_artifact_sha256"],
            "queue_authority":"DIAGNOSTIC_SOURCE_ED25519_NOT_OIDC_VERIFIED",
            "production_authority":False,"bvi_population_authority":False,
        })
        stats["signed_source_ready"]+=1
    return sorted(specs,key=lambda x:(x["prediction_cutoff"],x["race_id"])),stats

def _identity_for_merge(s:dict)->tuple:
    return (s.get("race_id"),s.get("race_date"),s.get("race_no"),
            s.get("venue"),s.get("prediction_cutoff"),
            s.get("jra_signed_source_artifact_sha256"))

def synchronize(root:Path,queue_path:Path=QUEUE,*,now=None,horizon_h:int=36,
                dry_run:bool=False)->dict:
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise BloodBError("QUEUE_NOW_TIMEZONE_REQUIRED")
    specs,stats=collect_specs(root,now=now,horizon_h=horizon_h)
    queue_path=queue_path.expanduser().resolve()
    private_dir(queue_path.parent)
    lock_path=queue_path.parent/"bloodb_queue_sync.lock"
    fd=os.open(lock_path,os.O_CREAT|os.O_RDWR,0o600)
    with os.fdopen(fd,"w") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        existing=json.loads(queue_path.read_text()) if queue_path.is_file() else []
        if not isinstance(existing,list) or len(existing)>200:
            raise BloodBError("EXISTING_QUEUE_INVALID")
        merged={}
        for old in existing:
            if not isinstance(old,dict) or not re.fullmatch(r"[A-Za-z0-9_.-]{4,120}",str(old.get("race_id",""))):
                raise BloodBError("EXISTING_QUEUE_INVALID_ITEM")
            if utc_time(old["prediction_cutoff"])<=now:
                continue
            k=old["race_id"]
            if k in merged and _identity_for_merge(merged[k])!=_identity_for_merge(old):
                raise BloodBError("EXISTING_QUEUE_CONFLICT:"+k)
            merged[k]=old
        added=[]
        for item in specs:
            rid=item["race_id"]
            if rid in merged:
                if _identity_for_merge(merged[rid])!=_identity_for_merge(item):
                    raise BloodBError("SIGNED_QUEUE_RACE_ID_CONFLICT:"+rid)
            else:
                merged[rid]=item
                added.append(rid)
        result=sorted(merged.values(),key=lambda z:(z["prediction_cutoff"],z["race_id"]))
        if len(result)>80:
            raise BloodBError("QUEUE_MAX_80_RACES")
        report={
            "status":"DRY_RUN" if dry_run else "LOCAL_DIAGNOSTIC_QUEUE_UPDATED",
            "candidate_intents":stats["candidate_intents"],
            "signed_source_ready":stats["signed_source_ready"],
            "missing_signed_source":stats["skipped_source_missing"],
            "queue_items":len(result),"new_items":len(added),
            "new_race_ids":added,
            "production_authority":False,
            "paid_page_fetches":0,
            "source_verification_level":SIGNER,
        }
        if not dry_run:
            temp_fd,temp_name=tempfile.mkstemp(dir=queue_path.parent,
                                              prefix=".bloodb-queue-",suffix=".tmp")
            try:
                with os.fdopen(temp_fd,"wb") as out:
                    os.fchmod(out.fileno(),0o600)
                    out.write((json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode())
                    out.flush()
                    os.fsync(out.fileno())
                os.replace(temp_name,queue_path)
            finally:
                if os.path.exists(temp_name):
                    os.unlink(temp_name)
        fcntl.flock(lock,fcntl.LOCK_UN)
    return report

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument("--queue",type=Path,default=QUEUE)
    p.add_argument("--horizon-hours",type=int,default=36)
    p.add_argument("--dry-run",action="store_true")
    a=p.parse_args(argv)
    print(json.dumps(synchronize(a.repo.expanduser().resolve(),a.queue,
                    horizon_h=a.horizon_hours,dry_run=a.dry_run),
                     ensure_ascii=False,sort_keys=True))
if __name__=="__main__":
    main()

from __future__ import annotations

import datetime
import hashlib
import re
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Tuple

from source_acquisition import _decode, _html_tables, sha_obj, snapshot_from_bytes, utcnow, validate_public_url
from jra_source_manifest import JRA_VENUE_CODES, canonical_venue

PROFILE="KM-JRA-REGISTERED-COMMON-NETKEIBA-v1.1-20260926"
AUTHORITY="REGISTERED_JRA_COMMON"
UA="KeibaMetrics-JRA-Registered-Common/1.0"
BASE="https://race.netkeiba.com"

def _norm(v:Any)->str:
    return re.sub(r"\s+","",str(v or "")).replace("前走","").strip()

def _fetch(url:str,prediction_cutoff:str,source_id:str,source_class:str):
    validate_public_url(url)
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/html,*/*;q=0.1","Accept-Language":"ja,en;q=0.4"})
    fetched=utcnow()
    with urllib.request.urlopen(req,timeout=30) as r:
        raw=r.read(8000001)
        if len(raw)>8000000: raise ValueError("REGISTERED_COMMON_MAX_BYTES_EXCEEDED")
        headers={str(k).lower():str(v) for k,v in r.headers.items()}
        final=str(r.geturl()); validate_public_url(final)
        status=int(getattr(r,"status",200))
    spec={"source_id":source_id,"source_class":source_class,"authority":AUTHORITY,
          "priority":90,"official":False,"required":False,"url":url,"max_bytes":8000000,
          "timeout_seconds":30,"extract":[]}
    snap,errs=snapshot_from_bytes(spec,raw,final_url=final,status_code=status,headers=headers,
                                  fetched_at=fetched,prediction_cutoff=prediction_cutoff)
    if snap.get("cutoff_relation")=="POST_CUTOFF":
        raise ValueError("REGISTERED_COMMON_POST_CUTOFF:"+source_id)
    if errs: raise ValueError("REGISTERED_COMMON_SNAPSHOT_ERROR:"+"|".join(errs))
    return raw,headers,snap

def _discover_race_id(venue_id:str,race_date:str,race_no:int,prediction_cutoff:str,meeting_key:str=""):
    d=datetime.date.fromisoformat(str(race_date).replace("/","-")).strftime("%Y%m%d")
    # Preferred identity path: JRA meeting key is already authority-bound and maps
    # deterministically to netkeiba's YYYY+venue+meeting+day+race identifier.
    key=re.sub(r"\D","",str(meeting_key or ""))
    code=JRA_VENUE_CODES.get(canonical_venue(venue_id))
    if re.fullmatch(r"\d{10}",key):
        kcode,year,meeting,day=key[:2],key[2:6],key[6:8],key[8:10]
        if code and kcode==code and year==d[:4]:
            rid=f"{year}{kcode}{meeting}{day}{int(race_no):02d}"
            # No discovery snapshot is synthesized. The actual workout/speed pages
            # are still fetched, hashed, cutoff-checked and runner-reconciled.
            return rid,None
    url=f"{BASE}/top/race_list.html?kaisai_date={d}"
    raw,headers,snap=_fetch(url,prediction_cutoff,"NETKEIBA-RACE-LIST","REGISTERED_COMMON_NETKEIBA_RACE_LIST")
    decoded=_decode(raw,headers.get("content-type",""))
    code=JRA_VENUE_CODES.get(canonical_venue(venue_id))
    candidates=sorted(set(re.findall(r"race_id=(\d{12})",decoded)))
    exact=[x for x in candidates if x[:4]==d[:4] and x[4:6]==code and int(x[-2:])==int(race_no)]
    if len(exact)!=1:
        raise ValueError(f"NETKEIBA_RACE_ID_NOT_UNIQUE:{venue_id}:{race_date}:{race_no}:{exact}")
    return exact[0],snap

def _find_table(decoded:str,required:List[str]):
    for table in _html_tables(decoded):
        if not table: continue
        h=[re.sub(r"\s+","",str(x or "")) for x in table[0]]
        if all(any(req in x for x in h) for req in required):
            return h,table[1:]
    raise ValueError("REGISTERED_COMMON_TABLE_NOT_FOUND:"+",".join(required))

def _last_lap(v:Any):
    s=str(v or "")
    vals=re.findall(r"(\d{2}\.\d)\s*\(\s*(\d{2}\.\d)\s*\)",s)
    if vals:return float(vals[-1][1])
    nums=re.findall(r"\d{2}\.\d",s)
    return float(nums[-1]) if nums else None

def parse_workout(raw:bytes,content_type:str="")->Dict[str,Any]:
    decoded=_decode(raw,content_type)
    h,rows=_find_table(decoded,["馬番","馬名","コース","調教タイム","評価"])
    def idx(part):
        return next((i for i,x in enumerate(h) if part in x),None)
    ni,mi,ci,ti,gi,li,ei=[idx(x) for x in ["馬番","馬名","コース","調教タイム","脚色","評価","評価"]]
    # Some pages put text assessment and A-D in the final two columns; locate both
    # by fixed trailing layout when duplicate/compound headers collapse.
    out=[]
    for row in rows:
        if ni is None or ni>=len(row):continue
        m=re.search(r"\d+",str(row[ni] or ""))
        if not m:continue
        no=int(m.group(0))
        if not 1<=no<=18:continue
        name=_norm(row[mi] if mi is not None and mi<len(row) else "")
        course=str(row[ci] if ci is not None and ci<len(row) else "").strip()
        t=str(row[ti] if ti is not None and ti<len(row) else "").strip()
        # The canonical netkeiba workout table ends with [脚色, short-comment, A-D].
        gait=str(row[-3] if len(row)>=3 else "").strip()
        comment=str(row[-2] if len(row)>=2 else "").strip()
        rating=str(row[-1] if len(row)>=1 else "").strip().upper()
        if rating not in {"A","B","C","D"}:
            rating=""
        out.append({"runner_id":str(no),"horse_no":no,"horse_name":name,"course":course,
                    "workout_time_raw":t,"final1f":_last_lap(t),"gait":gait,
                    "assessment":comment,"rating":rating})
    if not out: raise ValueError("NETKEIBA_WORKOUT_RUNNERS_EMPTY")
    return {"runner_count":len(out),"runners":sorted(out,key=lambda x:x["horse_no"])}

def parse_speed(raw:bytes,content_type:str="")->Dict[str,Any]:
    decoded=_decode(raw,content_type)
    h,rows=_find_table(decoded,["馬番","馬名","過去1年","5走平均"])
    def idx(part):
        return next((i for i,x in enumerate(h) if part in x),None)
    ni,mi,hi,ai=idx("馬番"),idx("馬名"),idx("過去1年"),idx("5走平均")
    out=[]
    for row in rows:
        if ni is None or ni>=len(row):continue
        m=re.search(r"\d+",str(row[ni] or ""))
        if not m:continue
        no=int(m.group(0))
        if not 1<=no<=18:continue
        name=_norm(row[mi] if mi is not None and mi<len(row) else "")
        highest=str(row[hi] if hi is not None and hi<len(row) else "").strip()
        avg=str(row[ai] if ai is not None and ai<len(row) else "").strip()
        out.append({"runner_id":str(no),"horse_no":no,"horse_name":name,
                    "past_year_best_raw":highest,"five_run_average_raw":avg})
    if not out: raise ValueError("NETKEIBA_SPEED_RUNNERS_EMPTY")
    return {"runner_count":len(out),"runners":sorted(out,key=lambda x:x["horse_no"])}

def _reconcile(parsed:Dict[str,Any],artifact:Dict[str,Any]):
    u=artifact.get("jra_official_runner_universe") or {}
    official={int(x.get("horse_no") or x.get("runner_id")):_norm(x.get("name")) for x in u.get("runners") or []}
    got={int(x["horse_no"]):_norm(x["horse_name"]) for x in parsed.get("runners") or []}
    errs=[]
    for no,name in official.items():
        if no not in got: errs.append(f"MISSING_OFFICIAL_RUNNER:{no}")
        elif name!=got[no]: errs.append(f"RUNNER_NAME_MISMATCH:{no}:{name}:{got[no]}")
    for no in sorted(set(got)-set(official)): errs.append(f"EXTRA_RUNNER:{no}")
    return {"verified":not errs,"official_count":len(official),"source_count":len(got),"errors":errs}

def enrich_with_registered_common(artifact:Dict[str,Any],prediction_cutoff:str,*,require_workout:bool=False):
    ctx=artifact.get("source_race_context") or {}
    warnings=[];errors=[];snaps=[]
    base={"profile":PROFILE,"authority":AUTHORITY,"official":False,"production_fact_authority":True,
          "prediction_rule_authority":"FACTS ONLY / EXISTING REGISTERED RULE EVALUATORS ONLY",
          "result_derived":False,"status":"UNAVAILABLE"}
    try:
        race_id,rsnap=_discover_race_id(
            ctx.get("venue_id"),ctx.get("race_date"),int(ctx.get("race_no") or 0),prediction_cutoff,
            str(artifact.get("jra_meeting_key_discovered") or "")
        )
        if rsnap is not None: snaps.append(rsnap)
        base["netkeiba_race_id"]=race_id
        raw,h,snap=_fetch(f"{BASE}/race/oikiri.html?race_id={race_id}&type=2",prediction_cutoff,
                          "NETKEIBA-WORKOUT","REGISTERED_COMMON_NETKEIBA_WORKOUT")
        workout=parse_workout(raw,h.get("content-type","")); workout["source_snapshot_sha256"]=snap["snapshot_sha256"]
        workout["runner_universe_match"]=_reconcile(workout,artifact);snaps.append(snap)
        if not workout["runner_universe_match"]["verified"]:
            raise ValueError("NETKEIBA_WORKOUT_RUNNER_MISMATCH:"+str(workout["runner_universe_match"]["errors"]))
        base["workout"]=workout
        raw,h,snap=_fetch(f"{BASE}/race/speed.html?mode=past&race_id={race_id}&type=shutuba",prediction_cutoff,
                          "NETKEIBA-SPEED-PAST","REGISTERED_COMMON_NETKEIBA_SPEED")
        speed=parse_speed(raw,h.get("content-type","")); speed["source_snapshot_sha256"]=snap["snapshot_sha256"]
        speed["runner_universe_match"]=_reconcile(speed,artifact);snaps.append(snap)
        base["speed"]=speed
        base["status"]="PASS"
    except Exception as e:
        msg="REGISTERED_COMMON_FAILED:"+type(e).__name__+":"+str(e)
        if require_workout:errors.append(msg)
        else:warnings.append(msg)
    base["warnings"]=warnings;base["errors"]=errors
    base["sha256"]=sha_obj({k:v for k,v in base.items() if k!="sha256"})
    artifact["sources"]=list(artifact.get("sources") or [])+snaps
    artifact["jra_registered_common"]=base
    artifact["jra_registered_common_sha256"]=sha_obj(base)
    return artifact,errors

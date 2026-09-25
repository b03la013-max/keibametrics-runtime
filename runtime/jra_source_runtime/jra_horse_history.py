from __future__ import annotations

import datetime
import re
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Tuple

from source_acquisition import _SafeRedirect, _decode, _html_tables, sha_obj, snapshot_from_bytes, utcnow, validate_public_url

PROFILE="KM-JRA-OFFICIAL-HORSE-HISTORY-v1.0-20260926"
BASE="https://www.jra.go.jp/JRADB/accessU.html"

def _norm(v:Any)->str:
    return re.sub(r"\s+"," ",str(v or "")).strip()

def _int(v):
    m=re.search(r"-?\d+",str(v or "").replace(",",""))
    return int(m.group(0)) if m else None

def _float(v):
    m=re.search(r"-?\d+(?:\.\d+)?",str(v or "").replace(",",""))
    return float(m.group(0)) if m else None

def _date(v):
    s=_norm(v)
    m=re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日",s)
    if not m:return None
    return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"

def _course(v):
    s=_norm(v)
    m=re.search(r"(芝ダ|芝|ダ|障)\s*(\d{3,4})",s)
    if not m:return None,None
    surface={"ダ":"ダ","芝":"芝","芝ダ":"芝ダ","障":"障"}.get(m.group(1),m.group(1))
    return surface,int(m.group(2))

def parse_horse_history(raw:bytes,content_type:str="")->Dict[str,Any]:
    decoded=_decode(raw,content_type)
    tables=_html_tables(decoded)
    chosen=None
    for table in tables:
        if not table:continue
        h=[_norm(x) for x in table[0]]
        required={"年月日","場","レース名","距離","頭数","人気","着順","騎手名","負担重量","馬体重","タイム"}
        if required.issubset(set(h)):
            chosen=table;break
    if chosen is None:
        raise ValueError("JRA_HORSE_HISTORY_TABLE_NOT_FOUND")
    h=[_norm(x) for x in chosen[0]]
    idx={name:h.index(name) for name in h}
    runs=[]
    for row in chosen[1:]:
        if not isinstance(row,list):continue
        def cell(name):
            i=idx.get(name)
            return row[i] if i is not None and i<len(row) else None
        d=_date(cell("年月日"))
        if not d:continue
        surface,distance=_course(cell("距離"))
        runs.append({
          "date":d,
          "venue":_norm(cell("場")),
          "race_name":_norm(cell("レース名")),
          "surface":surface,
          "distance_m":distance,
          "going":_norm(cell("馬場")),
          "field_size":_int(cell("頭数")),
          "popularity_rank":_int(cell("人気")),
          "finish":_int(cell("着順")),
          "jockey":_norm(cell("騎手名")),
          "assigned_weight":_float(cell("負担重量")),
          "body_weight":_int(cell("馬体重")),
          "time":_norm(cell("タイム")),
          "rating":_int(cell("Rt")) if "Rt" in idx else None,
          "winner_or_second":_norm(cell("1着馬（2着馬）")) if "1着馬（2着馬）" in idx else None,
        })
    if not runs:
        raise ValueError("JRA_HORSE_HISTORY_RUNS_EMPTY")
    out={"profile":PROFILE,"official":True,"production_fact_authority":True,"run_count":len(runs),"runs":runs}
    out["sha256"]=sha_obj({k:v for k,v in out.items() if k!="sha256"})
    return out

def _fetch_one(token:str,prediction_cutoff:str)->Tuple[Dict[str,Any],Dict[str,Any]]:
    q=urllib.parse.urlencode({"CNAME":token})
    url=BASE+"?"+q
    validate_public_url(url)
    spec={"source_id":"JRA-OFFICIAL-HORSE-HISTORY","source_class":"OFFICIAL_JRA_HORSE_HISTORY","authority":"JRA_OFFICIAL",
          "priority":118,"official":True,"required":False,"url":url,"max_bytes":3000000,"timeout_seconds":30,"extract":[]}
    opener=urllib.request.build_opener(_SafeRedirect())
    req=urllib.request.Request(url,headers={"User-Agent":"KeibaMetrics-JRA-Horse-History/1.0","Accept":"text/html,*/*;q=0.1","Accept-Language":"ja,en;q=0.4"})
    fetched=utcnow()
    with opener.open(req,timeout=30) as resp:
        final=str(resp.geturl());validate_public_url(final)
        raw=resp.read(3000001)
        if len(raw)>3000000:raise ValueError("JRA_HORSE_HISTORY_MAX_BYTES_EXCEEDED")
        headers={str(k).lower():str(v) for k,v in resp.headers.items()}
        snap,errs=snapshot_from_bytes(spec,raw,final_url=final,status_code=int(getattr(resp,"status",200)),headers=headers,fetched_at=fetched,prediction_cutoff=prediction_cutoff)
        if errs:raise ValueError("JRA_HORSE_HISTORY_SNAPSHOT_ERROR:"+"|".join(errs))
    parsed=parse_horse_history(raw,headers.get("content-type",""))
    parsed["source_snapshot_sha256"]=snap["snapshot_sha256"]
    parsed["raw_sha256"]=snap["raw_sha256"]
    parsed["profile_token_sha256"]=sha_obj({"token":token})
    parsed["sha256"]=sha_obj({k:v for k,v in parsed.items() if k!="sha256"})
    return snap,parsed

def enrich_with_horse_histories(artifact:Dict[str,Any],prediction_cutoff:str,*,require_history:bool=False,max_workers:int=6)->Tuple[Dict[str,Any],List[str]]:
    detail=artifact.get("jra_official_race_card_detail") or {}
    rows=list(detail.get("runners") or [])
    targets=[(str(x.get("runner_id") or x.get("horse_no")),str(x.get("horse_name") or ""),str(x.get("horse_profile_token") or "")) for x in rows if x.get("horse_profile_token")]
    errors=[]
    out={}
    snapshots=[]
    if not targets:
        msg="JRA_HORSE_HISTORY_PROFILE_TOKENS_MISSING"
        if require_history:errors.append(msg)
        artifact["jra_official_horse_history"]={"profile":PROFILE,"status":"UNAVAILABLE","production_fact_authority":True,"runner_count":0,"runners":{},"errors":[msg]}
        artifact["jra_official_horse_history_sha256"]=sha_obj(artifact["jra_official_horse_history"])
        return artifact,errors
    with ThreadPoolExecutor(max_workers=max(1,min(int(max_workers),8))) as ex:
        fut={ex.submit(_fetch_one,token,prediction_cutoff):(rid,name) for rid,name,token in targets}
        for f in as_completed(fut):
            rid,name=fut[f]
            try:
                snap,parsed=f.result()
                snapshots.append(snap)
                parsed["runner_id"]=rid;parsed["horse_name"]=name
                out[rid]=parsed
            except Exception as exc:
                errors.append(f"JRA_HORSE_HISTORY_FAILED:{rid}:{type(exc).__name__}:{exc}")
    artifact["sources"]=list(artifact.get("sources") or [])+snapshots
    payload={"profile":PROFILE,"status":"PASS" if out else "UNAVAILABLE","official":True,"production_fact_authority":True,
             "runner_count":len(out),"requested_runner_count":len(targets),"runners":out,"errors":errors}
    payload["sha256"]=sha_obj({k:v for k,v in payload.items() if k!="sha256"})
    artifact["jra_official_horse_history"]=payload
    artifact["jra_official_horse_history_sha256"]=sha_obj(payload)
    if require_history and len(out)!=len(targets):
        errors.append(f"JRA_HORSE_HISTORY_INCOMPLETE:{len(out)}/{len(targets)}")
    return artifact,list(dict.fromkeys(errors))

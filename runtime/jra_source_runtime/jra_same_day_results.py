from __future__ import annotations

import http.cookiejar
import re
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Tuple

from source_acquisition import _decode, _html_tables, _html_text, sha_obj, snapshot_from_bytes, utcnow
from jra_race_card_detail import _calendar_url, _fetch, _post, _date8

PROFILE="KM-JRA-OFFICIAL-SAME-DAY-RESULT-DETAIL-v1.0-20260926"
BASE="https://www.jra.go.jp"

def _norm(v:Any)->str:
    return re.sub(r"\s+"," ",str(v or "")).strip()

def _int(v:Any):
    m=re.search(r"-?\d+",str(v or "").replace(",",""))
    return int(m.group(0)) if m else None

def _flt(v:Any):
    m=re.search(r"-?\d+(?:\.\d+)?",str(v or "").replace(",",""))
    return float(m.group(0)) if m else None

def _positions(v:Any)->List[int]:
    return [int(x) for x in re.findall(r"\d{1,2}",str(v or ""))]

def parse_result_detail(raw:bytes,content_type:str="")->Dict[str,Any]:
    decoded=_decode(raw,content_type)
    text=_html_text(decoded)
    chosen=None
    for table in _html_tables(decoded):
        if not table: continue
        h=[re.sub(r"\s+","",str(x or "")) for x in table[0]]
        if "着順" in h and "馬番" in h and "馬名" in h and any("コーナー通過順位" in x for x in h):
            chosen=table
            break
    if chosen is None:
        raise ValueError("JRA_RESULT_DETAIL_TABLE_NOT_FOUND")
    h=[re.sub(r"\s+","",str(x or "")) for x in chosen[0]]
    def idx(part):
        return next((i for i,x in enumerate(h) if part in x),None)
    fi,ni,mi,pi,li=idx("着順"),idx("馬番"),idx("馬名"),idx("コーナー通過順位"),idx("推定上り")
    runners=[]
    for row in chosen[1:]:
        if ni is None or ni>=len(row): continue
        no=_int(row[ni])
        finish=_int(row[fi]) if fi is not None and fi<len(row) else None
        if no is None or finish is None: continue
        name=_norm(row[mi] if mi is not None and mi<len(row) else "")
        passing=_positions(row[pi] if pi is not None and pi<len(row) else "")
        final3f=_flt(row[li]) if li is not None and li<len(row) else None
        runners.append({
            "horse_no":no,"runner_id":str(no),"horse_name":name,"finish":finish,
            "passing_positions":passing,"final3f":final3f
        })
    if not runners:
        raise ValueError("JRA_RESULT_DETAIL_RUNNERS_EMPTY")
    lap_table=None
    corner_table=None
    for table in _html_tables(decoded):
        if table and table[0] and str(table[0][0]).strip()=="ハロンタイム":
            lap_table=table
        if table and table[0] and str(table[0][0]).strip() in {"1コーナー","2コーナー","3コーナー","4コーナー"}:
            corner_table=table
    mt=re.search(r"発走時刻[:：]?\s*(\d{1,2})時(\d{2})分",text)
    scheduled_post=(f"{int(mt.group(1)):02d}:{int(mt.group(2)):02d}" if mt else None)
    mg=re.search(r"天候\s*([^\s]+)\s+(芝|ダート|ダ)\s*(良|稍重|重|不良)",text)
    env={"weather":mg.group(1),"surface":mg.group(2),"going":mg.group(3)} if mg else {}
    md=re.search(r"コース[:：]?\s*([\d,]+)\s*メートル\s*[（(]([^）)]+)",text)
    if md:
        env["distance_m"]=int(md.group(1).replace(",",""))
        env["course_text"]=_norm(md.group(2))
    out={
        "profile":PROFILE,"official":True,"production_fact_authority":True,
        "result_derived":True,"runner_count":len(runners),"runners":runners,
        "scheduled_post_hhmm":scheduled_post,"race_environment":env,
        "lap_table":lap_table,"corner_table":corner_table,
    }
    out["sha256"]=sha_obj({k:v for k,v in out.items() if k!="sha256"})
    return out

def _open_day(race_date:str,meeting_key:str):
    d=_date8(race_date)
    key=re.sub(r"\D","",str(meeting_key or ""))
    if not re.fullmatch(r"\d{10}",key):
        raise ValueError("JRA_MEETING_KEY_INVALID")
    jar=http.cookiejar.CookieJar()
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    u0,r0,h0=_fetch(opener,_calendar_url(race_date))
    s0=_decode(r0,h0.get("content-type",""))
    tokens=re.findall(r"doAction\('/JRADB/accessS\.html'\s*,\s*'([^']+)'\)",s0)
    entry=next((x for x in tokens if str(x).startswith("pw01sli00")),tokens[0] if tokens else None)
    if not entry:
        raise ValueError("JRA_RESULT_ENTRY_TOKEN_NOT_FOUND")
    u1,r1,h1=_post(opener,entry,u0)
    s1=_decode(r1,h1.get("content-type",""))
    m=re.search(r"(pw01srl00"+re.escape(key)+re.escape(d)+r"/[0-9A-Fa-f]{2})",s1)
    if not m:
        raise ValueError("JRA_RESULT_DAY_TOKEN_NOT_FOUND")
    day=m.group(1)
    u2,r2,h2=_post(opener,day,u1)
    s2=_decode(r2,h2.get("content-type",""))
    return opener,u2,s2,key,d

def _fetch_race(opener,referer:str,day_html:str,key:str,d:str,race_no:int,prediction_cutoff:str):
    prefix="pw01sde01"+key+f"{int(race_no):02d}"+d
    m=re.search(r"("+re.escape(prefix)+r"/[0-9A-Fa-f]{2})",day_html)
    if not m:
        raise ValueError(f"JRA_RESULT_RACE_TOKEN_NOT_FOUND:{race_no}")
    fetched=utcnow()
    final,raw,headers=_post(opener,m.group(1),referer)
    spec={
        "source_id":f"JRA-OFFICIAL-SAME-DAY-R{int(race_no):02d}-DETAIL",
        "source_class":"OFFICIAL_JRA_SAME_DAY_RESULT","authority":"JRA_OFFICIAL",
        "priority":122,"official":True,"required":False,
        "url":BASE+"/JRADB/accessS.html","max_bytes":3000000,"timeout_seconds":30,"extract":[]
    }
    snap,errs=snapshot_from_bytes(
        spec,raw,final_url=final,status_code=200,headers=headers,fetched_at=fetched,
        prediction_cutoff=prediction_cutoff
    )
    if snap.get("cutoff_relation")=="POST_CUTOFF":
        raise ValueError(f"JRA_SAME_DAY_RESULT_POST_CUTOFF:{race_no}")
    if errs:
        raise ValueError("JRA_SAME_DAY_RESULT_SNAPSHOT_ERROR:"+"|".join(errs))
    parsed=parse_result_detail(raw,headers.get("content-type",""))
    parsed["race_no"]=int(race_no)
    parsed["source_snapshot_sha256"]=snap["snapshot_sha256"]
    return snap,parsed

def enrich_with_same_day_results(
    artifact:Dict[str,Any],prediction_cutoff:str,*,require_same_day_results:bool=False
)->Tuple[Dict[str,Any],List[str]]:
    ctx=artifact.get("source_race_context") or {}
    race_no=int(ctx.get("race_no") or 0)
    race_date=str(ctx.get("race_date") or "")
    meeting_key=str(artifact.get("jra_meeting_key_discovered") or "")
    errors=[]; warnings=[]; snapshots=[]; results={}
    if race_no<=1:
        payload={"profile":PROFILE,"status":"NOT_APPLICABLE_FIRST_RACE","official":True,
                 "production_fact_authority":True,"result_derived":True,"race_count":0,"races":{}}
        payload["sha256"]=sha_obj(payload)
        artifact["jra_official_same_day_results"]=payload
        artifact["jra_official_same_day_results_sha256"]=sha_obj(payload)
        return artifact,[]
    try:
        if not meeting_key:
            raise ValueError("JRA_MEETING_KEY_REQUIRED_FOR_SAME_DAY_RESULTS")
        opener,referer,day_html,key,d=_open_day(race_date,meeting_key)
        for rn in range(1,race_no):
            try:
                snap,parsed=_fetch_race(opener,referer,day_html,key,d,rn,prediction_cutoff)
                snapshots.append(snap); results[str(rn)]=parsed
            except Exception as exc:
                msg=f"JRA_SAME_DAY_RESULT_FAILED:{rn}:{type(exc).__name__}:{exc}"
                if require_same_day_results: errors.append(msg)
                else: warnings.append(msg)
    except Exception as exc:
        msg="JRA_SAME_DAY_RESULT_SESSION_FAILED:"+type(exc).__name__+":"+str(exc)
        if require_same_day_results: errors.append(msg)
        else: warnings.append(msg)
    payload={
        "profile":PROFILE,
        "status":"PASS" if results else ("FAIL" if errors else "UNAVAILABLE"),
        "official":True,"production_fact_authority":True,"result_derived":True,
        "target_race_no":race_no,"race_count":len(results),"races":results,
        "rule":"Only completed races with race_no < target_race_no are captured. Target-race result is structurally excluded.",
        "errors":errors,"warnings":warnings,
    }
    payload["sha256"]=sha_obj({k:v for k,v in payload.items() if k!="sha256"})
    artifact["sources"]=list(artifact.get("sources") or [])+snapshots
    artifact["jra_official_same_day_results"]=payload
    artifact["jra_official_same_day_results_sha256"]=sha_obj(payload)
    return artifact,errors

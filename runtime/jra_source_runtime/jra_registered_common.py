from __future__ import annotations

import datetime
from html.parser import HTMLParser
import hashlib
import re
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Tuple

from source_acquisition import _decode, _html_tables, sha_obj, snapshot_from_bytes, utcnow, validate_public_url
from jra_source_manifest import JRA_VENUE_CODES, canonical_venue

PROFILE="KM-JRA-REGISTERED-COMMON-NETKEIBA-v1.5-20260927"
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

def _find_tables(decoded:str,required:List[str]):
    out=[]
    for table in _html_tables(decoded):
        if not table: continue
        h=[re.sub(r"\s+","",str(x or "")) for x in table[0]]
        if all(any(req in x for x in h) for req in required):
            out.append((h,table[1:]))
    return out

def _find_table(decoded:str,required:List[str]):
    xs=_find_tables(decoded,required)
    if xs:
        return xs[0]
    raise ValueError("REGISTERED_COMMON_TABLE_NOT_FOUND:"+",".join(required))

def _last_lap(v:Any):
    s=str(v or "")
    vals=re.findall(r"(\d{2}\.\d)\s*\(\s*(\d{2}\.\d)\s*\)",s)
    if vals:return float(vals[-1][1])
    nums=re.findall(r"\d{2}\.\d",s)
    return float(nums[-1]) if nums else None

def parse_workout(raw:bytes,content_type:str="",official_universe:Dict[str,Any]|None=None)->Dict[str,Any]:
    decoded=_decode(raw,content_type)
    tables=_find_tables(decoded,["馬番","馬名","コース","調教タイム","評価"])
    schema="DETAILED"
    if not tables:
        tables=_find_tables(decoded,["馬番","馬名","評価"])
        schema="COMPACT_ASSESSMENT"
    if not tables:
        raise ValueError("REGISTERED_COMMON_TABLE_NOT_FOUND:馬番,馬名,評価")

    expected=None
    if official_universe:
        expected={int(x.get("horse_no") or x.get("runner_id")):_norm(x.get("name"))
                  for x in official_universe.get("runners") or []}

    parsed_candidates=[]
    for h,rows in tables:
        def idx(part):
            return next((i for i,x in enumerate(h) if part in x),None)
        ni,mi,ci,ti,gi,li,ei=[idx(x) for x in ["馬番","馬名","コース","調教タイム","脚色","評価","評価"]]
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
            gait=str(row[gi] if gi is not None and gi<len(row) else "").strip()
            comment=str(row[-2] if len(row)>=2 else "").strip()
            rating=str(row[-1] if len(row)>=1 else "").strip().upper()
            if rating not in {"A","B","C","D"}:
                rating=""
            out.append({"runner_id":str(no),"horse_no":no,"horse_name":name,"course":course,
                        "workout_time_raw":t,"final1f":_last_lap(t),"gait":gait,
                        "assessment":comment,"rating":rating})
        if not out:
            continue
        payload={"runner_count":len(out),"schema":schema,"runners":sorted(out,key=lambda x:x["horse_no"])}
        parsed_candidates.append(payload)
        if expected is not None:
            got={int(x["horse_no"]):_norm(x["horse_name"]) for x in payload["runners"]}
            if got==expected:
                return payload
    if parsed_candidates:
        return parsed_candidates[0]
    raise ValueError("NETKEIBA_WORKOUT_RUNNERS_EMPTY")

class _SpeedTables(HTMLParser):
    """Preserve multi-row speed-table headers without shifting data columns."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables=[]; self.table=None; self.row=None; self.cell=None
        self.depth=0; self.spans={}; self.width=1; self.height=1

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            if self.table is None: self.table=[]; self.spans={}; self.depth=1
            else: self.depth+=1
        elif self.depth==1 and tag=="tr":
            self.row={}; self.col=0
            for col,(value,left) in list(self.spans.items()):
                self.row[col]=value
                if left<=1: del self.spans[col]
                else: self.spans[col]=(value,left-1)
        elif self.depth==1 and self.row is not None and tag in ("td","th"):
            self.cell=[]; a=dict(attrs)
            try: self.width=int(a.get("colspan",1)); self.height=int(a.get("rowspan",1))
            except (ValueError,TypeError): raise ValueError("SPEED_HEADER_INVALID_SPAN")
            if not 1<=self.width<=32 or not 1<=self.height<=8:
                raise ValueError("SPEED_HEADER_INVALID_SPAN")
        elif self.cell is not None and tag in ("br","div","p"):
            self.cell.append(" ")

    def handle_data(self, data):
        if self.cell is not None and self.depth==1: self.cell.append(data)

    def handle_endtag(self, tag):
        if self.depth==1 and tag in ("td","th") and self.cell is not None:
            value=re.sub(r"\s+"," ","".join(self.cell)).strip()
            while self.col in self.row: self.col+=1
            for offset in range(self.width):
                col=self.col+offset
                if col in self.row: raise ValueError("SPEED_HEADER_OVERLAPPING_SPAN")
                self.row[col]=value
                if self.height>1: self.spans[col]=(value,self.height-1)
            self.col+=self.width; self.cell=None
        elif self.depth==1 and tag=="tr" and self.row is not None:
            if self.row:
                self.table.append([self.row.get(i,"") for i in range(max(self.row)+1)])
            self.row=None
        elif tag=="table" and self.table is not None:
            self.depth-=1
            if self.depth==0:
                self.tables.append(self.table); self.table=None


def parse_speed(raw:bytes,content_type:str="")->Dict[str,Any]:
    decoded=_decode(raw,content_type)
    reader=_SpeedTables(); reader.feed(decoded)
    candidates=[]
    for table in reader.tables:
        if not table: continue
        header=[re.sub(r"\s+","",str(x)) for x in table[0]]
        if all(any(key in x for x in header) for key in ("馬番","馬名","過去1年","5走平均")):
            candidates.append((header,table[1:]))
    if len(candidates)!=1: raise ValueError("REGISTERED_COMMON_SPEED_TABLE_NOT_UNIQUE")
    h,rows=candidates[0]
    def idx(part):
        return next((i for i,x in enumerate(h) if part in x),None)
    ni,mi,hi,ai=idx("馬番"),idx("馬名"),idx("過去1年"),idx("5走平均")
    out=[]
    for row in rows:
        if ni is None or ni>=len(row):continue
        cell=str(row[ni] or "").strip()
        if not re.fullmatch(r"\d{1,2}",cell):continue
        no=int(cell)
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


def _normalize_declared_cancelled_workout(parsed:Dict[str,Any], artifact:Dict[str,Any], raw:bytes, content_type:str=""):
    """Remove only exact officially cancelled identities from a complete feed.

    Normal feeds keep the existing path. A cancellation exception requires the
    same page date/venue/race, complete declared-name identity, an independently
    declared CANCELLED status, and an exact remaining Active universe.
    Unknown extras, partial feeds and identity mismatches remain rejected by
    the unchanged _reconcile gate. No rating, clock or feature is inferred.
    """
    if _reconcile(parsed, artifact)["verified"]:
        return parsed
    declared_obj=artifact.get("jra_declared_runner_universe") or {}
    declared_rows=declared_obj.get("runners") or []
    active_rows=(artifact.get("jra_official_runner_universe") or {}).get("runners") or []
    source_rows=parsed.get("runners") or []
    def strict_number(row):
        def convert(value):
            if type(value) is int and 1<=value<=18:
                return value
            if isinstance(value,str) and re.fullmatch(r"(?:[1-9]|1[0-8])",value):
                return int(value)
            raise ValueError("WORKOUT_RUNNER_NUMBER_INVALID")
        no=convert(row.get("horse_no") if "horse_no" in row else row.get("runner_id"))
        if "runner_id" in row and convert(row["runner_id"])!=no:
            raise ValueError("WORKOUT_RUNNER_NUMBER_ID_CONFLICT")
        return no
    try:
        declared={strict_number(r):r for r in declared_rows}
        active={strict_number(r):r for r in active_rows}
        got={strict_number(r):r for r in source_rows}
    except (TypeError,ValueError,KeyError):
        return parsed
    if (not active or len(declared)!=len(declared_rows) or len(got)!=len(source_rows)
            or len(active)!=len(active_rows) or set(got)!=set(declared)):
        return parsed
    cancelled={no for no,r in declared.items() if r.get("status")=="CANCELLED"}
    if (not cancelled or set(declared)-cancelled!=set(active)
            or declared_obj.get("universe_type")!="DECLARED"
            or not declared_obj.get("runner_universe_sha256")
            or not declared_obj.get("source_snapshot_sha256")
            or any(not declared[no].get("status_source_id") or not declared[no].get("status_source_snapshot_sha256") for no in cancelled)):
        return parsed
    for no,row in declared.items():
        if (not _norm(row.get("name")) or _norm(row.get("name"))!=_norm(got[no].get("horse_name"))
                or (no in active and (_norm(active[no].get("name"))!=_norm(row.get("name")) or row.get("status")!="ACTIVE" or active[no].get("status")!="ACTIVE"))):
            return parsed
    decoded=_decode(raw,content_type)
    title=re.search(r"<title[^>]*>(.*?)</title>",decoded,re.I|re.S)
    identity=re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日\s+([^\d<]+?)(\d{1,2})R",title.group(1) if title else "")
    if not identity:
        return parsed
    actual_day=f"{int(identity[1]):04d}-{int(identity[2]):02d}-{int(identity[3]):02d}"
    context=artifact.get("source_race_context") or {}
    expected_venue=(artifact.get("jra_race_context") or {}).get("venue_name")
    try:
        same=(actual_day==context.get("race_date") and _norm(identity[4])==_norm(expected_venue)
              and int(identity[5])==int(context.get("race_no")))
    except (TypeError,ValueError):
        return parsed
    if not same:
        return parsed
    import copy
    out=copy.deepcopy(parsed)
    out["runners"]=[r for r in out["runners"] if int(r["horse_no"]) in active]
    out["runner_count"]=len(out["runners"])
    out["cancelled_runner_exclusions"]={
        "basis":"EXACT_DECLARED_IDENTITIES_AND_EXPLICIT_CANCELLED_STATUS",
        "declared_universe_sha256":declared_obj.get("runner_universe_sha256"),
        "declared_source_snapshot_sha256":declared_obj.get("source_snapshot_sha256"),
        "original_source_runner_count":len(got),
        "excluded":[{"horse_no":no,"name":declared[no].get("name"),"status":"CANCELLED",
                     "status_source_id":declared[no].get("status_source_id"),
                     "status_source_snapshot_sha256":declared[no].get("status_source_snapshot_sha256")} for no in sorted(cancelled)],
        "page_identity":{"race_date":actual_day,"venue_name":_norm(identity[4]),"race_no":int(identity[5])},
    }
    if not _reconcile(out,artifact)["verified"]:
        return parsed
    return out

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
        workout=None
        workout_attempt_errors=[]
        workout_urls=[
            f"{BASE}/race/oikiri.html?race_id={race_id}&rf=race_submenu",
            f"{BASE}/race/oikiri.html?race_id={race_id}",
            f"{BASE}/race/oikiri.html?race_id={race_id}&type=1",
            f"{BASE}/race/oikiri.html?race_id={race_id}&type=2",
        ]
        for wi,wurl in enumerate(workout_urls):
            try:
                raw,h,snap=_fetch(
                    wurl,prediction_cutoff,
                    f"NETKEIBA-WORKOUT-{wi}","REGISTERED_COMMON_NETKEIBA_WORKOUT"
                )
                snaps.append(snap)
                candidate=parse_workout(raw,h.get("content-type",""),artifact.get("jra_official_runner_universe"))
                candidate["source_snapshot_sha256"]=snap["snapshot_sha256"]
                candidate=_normalize_declared_cancelled_workout(candidate,artifact,raw,h.get("content-type",""))
                candidate["runner_universe_match"]=_reconcile(candidate,artifact)
                if candidate["runner_universe_match"]["verified"]:
                    workout=candidate
                    break
                workout_attempt_errors.append(
                    "RUNNER_MISMATCH:"+str(candidate["runner_universe_match"]["errors"])
                )
            except Exception as exc:
                workout_attempt_errors.append(type(exc).__name__+":"+str(exc))
        if workout is None:
            msg="NETKEIBA_WORKOUT_NO_COMPLETE_UNIVERSE:"+"|".join(workout_attempt_errors)
            if require_workout: errors.append(msg)
            else: warnings.append(msg)
        base["workout"]=workout
        base["workout_selection"]={
            "strategy":"FIRST_COMPLETE_OFFICIAL-UNIVERSE-MATCH",
            "attempt_count":len([x for x in snaps if str(x.get("source_id") or "").startswith("NETKEIBA-WORKOUT-")]),
            "rejected_attempts":workout_attempt_errors,
        }
        try:
            raw,h,snap=_fetch(f"{BASE}/race/speed.html?mode=past&race_id={race_id}&type=shutuba",prediction_cutoff,
                              "NETKEIBA-SPEED-PAST","REGISTERED_COMMON_NETKEIBA_SPEED")
            speed=parse_speed(raw,h.get("content-type",""))
            speed["source_snapshot_sha256"]=snap["snapshot_sha256"]
            speed["runner_universe_match"]=_reconcile(speed,artifact)
            snaps.append(snap)
            base["speed"]=speed
        except Exception as exc:
            # Historical speed is independent from the required workout fact.
            # Debut/newcomer universes can legitimately have no past-speed table.
            msg="REGISTERED_COMMON_SPEED_UNAVAILABLE:"+type(exc).__name__+":"+str(exc)
            warnings.append(msg)
            base["speed"]={"status":"UNAVAILABLE","reason":msg,"result_derived":False}
        base["status"]="PASS" if workout is not None else "PARTIAL"
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

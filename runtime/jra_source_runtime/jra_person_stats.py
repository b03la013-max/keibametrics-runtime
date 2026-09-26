from __future__ import annotations

import http.cookiejar
import re
import urllib.parse
import urllib.request
import urllib.error
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Tuple

from source_acquisition import _decode, _html_tables, _html_text, sha_obj, snapshot_from_bytes, utcnow, validate_public_url

PROFILE="KM-JRA-OFFICIAL-PERSON-STATS-v1.0-20260926"
BASE="https://www.jra.go.jp"
UA="KeibaMetrics-JRA-Person-Stats/1.0"

def _norm(v:Any)->str:
    s=str(v or "").strip()
    s=re.sub(r"[▲△◇☆★]", "", s)
    s=re.sub(r"\s+","",s)
    return s

def _flt(v:Any):
    m=re.search(r"-?\d+(?:\.\d+)?",str(v or "").replace(",",""))
    return float(m.group(0)) if m else None

def _int(v:Any):
    m=re.search(r"-?\d+",str(v or "").replace(",",""))
    return int(m.group(0)) if m else None

def _fetch_horse_session(horse_token:str)->Tuple[Any,str]:
    jar=http.cookiejar.CookieJar()
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    url=BASE+"/JRADB/accessU.html?"+urllib.parse.urlencode({"CNAME":horse_token})
    validate_public_url(url)
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/html,*/*;q=0.1","Accept-Language":"ja,en;q=0.4"})
    with opener.open(req,timeout=30) as r:
        r.read(3000000)
        return opener,str(r.geturl())

def _post_profile(opener,kind:str,token:str,referer:str,prediction_cutoff:str,*,max_attempts:int=4):
    page="accessK" if kind=="jockey" else "accessC"
    url=BASE+"/JRADB/"+page+".html"
    validate_public_url(url)
    data=urllib.parse.urlencode({"cname":token}).encode()
    retryable={429,500,502,503,504}
    last=None
    for attempt in range(1,max(1,int(max_attempts))+1):
        try:
            req=urllib.request.Request(url,data=data,headers={
              "User-Agent":UA,"Accept":"text/html,*/*;q=0.1","Accept-Language":"ja,en;q=0.4","Referer":referer
            })
            fetched=utcnow()
            with opener.open(req,timeout=30) as r:
                raw=r.read(3000001)
                if len(raw)>3000000: raise ValueError("JRA_PERSON_PROFILE_MAX_BYTES_EXCEEDED")
                headers={str(k).lower():str(v) for k,v in r.headers.items()}
                final=str(r.geturl()); validate_public_url(final)
                status=int(getattr(r,"status",200))
            decoded=_decode(raw,headers.get("content-type",""))
            if "パラメータエラー" in _html_text(decoded)[:500]:
                raise ValueError("JRA_PERSON_PROFILE_PARAMETER_ERROR")
            spec={"source_id":"JRA-OFFICIAL-PERSON-STATS","source_class":"OFFICIAL_JRA_PERSON_STATS","authority":"JRA_OFFICIAL",
                  "priority":116,"official":True,"required":False,"url":url,"max_bytes":3000000,"timeout_seconds":30,"extract":[]}
            snap,errs=snapshot_from_bytes(spec,raw,final_url=final,status_code=status,headers=headers,fetched_at=fetched,prediction_cutoff=prediction_cutoff)
            if errs: raise ValueError("JRA_PERSON_PROFILE_SNAPSHOT_ERROR:"+"|".join(errs))
            return snap,parse_person_profile(raw,headers.get("content-type",""),kind,token)
        except urllib.error.HTTPError as exc:
            last=exc
            if int(getattr(exc,"code",0) or 0) not in retryable or attempt>=max_attempts:
                raise
        except (urllib.error.URLError, TimeoutError) as exc:
            last=exc
            if attempt>=max_attempts:
                raise
        # JRA intermittently returns 503 under short bursts. Retry deterministically,
        # with a small linear backoff; no prediction semantics are changed.
        time.sleep(0.6*attempt)
    raise last if last else RuntimeError("JRA_PERSON_PROFILE_RETRY_EXHAUSTED")

def _flat_row(table:List[List[str]],kind:str):
    if not table:return None
    h=[str(x).strip() for x in table[0]]
    count_name="騎乗回数" if kind=="jockey" else "出走回数"
    needed={"1着","2着","3着","勝率","連対率","3着内率",count_name}
    if not needed.issubset(set(h)):return None
    idx={x:h.index(x) for x in needed}
    for row in table[1:]:
        if row and str(row[0]).strip()=="平地":
            return {
              "wins":_int(row[idx["1着"]]),"seconds":_int(row[idx["2着"]]),"thirds":_int(row[idx["3着"]]),
              "starts":_int(row[idx[count_name]]),
              "win_rate":_flt(row[idx["勝率"]]),"quinella_rate":_flt(row[idx["連対率"]]),"top3_rate":_flt(row[idx["3着内率"]])
            }
    return None

def parse_person_profile(raw:bytes,content_type:str,kind:str,token:str)->Dict[str,Any]:
    decoded=_decode(raw,content_type); text=_html_text(decoded)
    label="騎手情報" if kind=="jockey" else "調教師情報"
    m=re.search(re.escape(label)+r"\s+(.+?)\s*[（(]",text)
    name=m.group(1).strip() if m else ""
    rows=[]
    for table in _html_tables(decoded):
        x=_flat_row(table,kind)
        if x:rows.append(x)
    out={
      "profile":PROFILE,"official":True,"production_fact_authority":True,"kind":kind,"name":name,
      "token_sha256":sha_obj({"token":token}),
      "current_year_flat":rows[0] if rows else None,
      "career_flat":rows[1] if len(rows)>1 else None,
      "stat_table_count":len(rows),
    }
    out["sha256"]=sha_obj({k:v for k,v in out.items() if k!="sha256"})
    return out

def _runner_identity(detail:Dict[str,Any],rid:str):
    for x in detail.get("runners") or []:
        if str(x.get("runner_id") or x.get("horse_no"))==rid:return x
    return {}

def enrich_with_person_stats(artifact:Dict[str,Any],prediction_cutoff:str,*,require_person_stats:bool=False,max_workers:int=2):
    history=((artifact.get("jra_official_horse_history") or {}).get("runners") or {})
    detail=artifact.get("jra_official_race_card_detail") or {}
    unique={}
    for rid,hh in history.items():
        d=_runner_identity(detail,str(rid))
        ht=str(d.get("horse_profile_token") or "")
        if not ht: continue
        for kind in ("jockey","trainer"):
            for tok in ((hh.get("person_profile_tokens") or {}).get(kind) or []):
                unique.setdefault((kind,str(tok)),ht)
    profiles={};snaps=[];errors=[]
    failed=[]
    def job(kind,tok,ht):
        op,ref=_fetch_horse_session(ht)
        return _post_profile(op,kind,tok,ref,prediction_cutoff)
    with ThreadPoolExecutor(max_workers=max(1,min(int(max_workers),3))) as ex:
        fut={ex.submit(job,k,t,h):(k,t,h) for (k,t),h in unique.items()}
        for f in as_completed(fut):
            k,t,h=fut[f]
            try:
                snap,p=f.result();snaps.append(snap);profiles[(k,t)]=p
            except Exception as exc:
                failed.append((k,t,h,exc))
    # One sequential second pass avoids a transient burst failure turning an
    # entire jockey class into 0/N. This changes acquisition reliability only.
    for k,t,h,first_exc in failed:
        try:
            snap,p=job(k,t,h);snaps.append(snap);profiles[(k,t)]=p
        except Exception as exc:
            errors.append(
              f"JRA_PERSON_STATS_PROFILE_FAILED:{k}:{type(exc).__name__}:{exc};"
              f"FIRST={type(first_exc).__name__}:{first_exc}"
            )
    by_runner={}
    for rid,hh in history.items():
        d=_runner_identity(detail,str(rid))
        current={"jockey":_norm(d.get("jockey")),"trainer":_norm(d.get("trainer"))}
        matched={}
        p=hh.get("person_profile_tokens") or {}
        for kind in ("jockey","trainer"):
            candidates=[]
            for tok in p.get(kind) or []:
                prof=profiles.get((kind,str(tok)))
                if not prof:continue
                candidates.append(prof)
                if current[kind] and _norm(prof.get("name"))==current[kind]:
                    matched[kind]=prof;break
            if kind not in matched and len(candidates)==1:
                matched[kind]=candidates[0]
        by_runner[str(rid)]={
          "current_jockey":d.get("jockey"),"current_trainer":d.get("trainer"),
          "jockey":matched.get("jockey"),"trainer":matched.get("trainer"),
          "jockey_matched":bool(matched.get("jockey")),"trainer_matched":bool(matched.get("trainer"))
        }
    artifact["sources"]=list(artifact.get("sources") or [])+snaps
    payload={
      "profile":PROFILE,"status":"PASS" if by_runner else "UNAVAILABLE","official":True,"production_fact_authority":True,
      "runner_count":len(by_runner),"matched_jockey_count":sum(1 for x in by_runner.values() if x["jockey_matched"]),
      "matched_trainer_count":sum(1 for x in by_runner.values() if x["trainer_matched"]),
      "runners":by_runner,"errors":errors
    }
    payload["sha256"]=sha_obj({k:v for k,v in payload.items() if k!="sha256"})
    artifact["jra_official_person_stats"]=payload
    artifact["jra_official_person_stats_sha256"]=sha_obj(payload)
    if require_person_stats:
        n=len(by_runner)
        if payload["matched_jockey_count"]<n or payload["matched_trainer_count"]<n:
            errors.append(f"JRA_PERSON_STATS_INCOMPLETE:{payload['matched_jockey_count']}/{n}:{payload['matched_trainer_count']}/{n}")
    return artifact,list(dict.fromkeys(errors))

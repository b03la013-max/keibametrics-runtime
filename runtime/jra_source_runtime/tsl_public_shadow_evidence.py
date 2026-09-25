from __future__ import annotations
import datetime,hashlib,html,re,unicodedata,urllib.error,urllib.parse,urllib.request,urllib.robotparser
from html.parser import HTMLParser
from typing import Any,Dict,List,Tuple
from zoneinfo import ZoneInfo
from source_acquisition import _decode,_html_tables,_html_text,_parse_dt,sha_obj,utcnow,validate_public_url
from jra_source_manifest import JRA_VENUE_CODES, canonical_venue, date_compact

PROFILE="KM-JRA-TSL-PUBLIC-SHADOW-EVIDENCE-v1.0-20260925"
SOURCE_CLASS="THIRD_PARTY_PUBLIC_SHADOW"
SOURCE_AUTHORITY="TSL_PUBLIC_NON_OFFICIAL"
BASE="https://jra.k-ba.net"
USER_AGENT="KeibaMetrics-TSL-Shadow/1.0 (+public pre-race evidence; one race capture; normalized extract only)"
DEFAULT_TIMEOUT=20
DEFAULT_MAX_BYTES=1000000

def _norm(v:Any)->str:
    return re.sub(r"\s+","",unicodedata.normalize("NFKC",html.unescape(str(v or "")))).strip()

class _AnchorParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.a=[]; self.href=None; self.buf=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()=="a":
            self.href=dict(attrs).get("href"); self.buf=[]
    def handle_data(self,data):
        if self.href is not None: self.buf.append(data)
    def handle_endtag(self,tag):
        if tag.lower()=="a" and self.href is not None:
            self.a.append({"href":self.href,"text":" ".join(self.buf).strip()}); self.href=None; self.buf=[]

def _anchors(raw:bytes,ctype:str="")->List[Dict[str,str]]:
    p=_AnchorParser(); p.feed(_decode(raw,ctype)); return p.a

def _robots_allowed(url:str,timeout:int=10)->Tuple[bool,str]:
    robots=BASE+"/robots.txt"; rp=urllib.robotparser.RobotFileParser(); rp.set_url(robots)
    try:
        req=urllib.request.Request(robots,headers={"User-Agent":USER_AGENT})
        with urllib.request.urlopen(req,timeout=timeout) as resp:
            txt=_decode(resp.read(200000),str(resp.headers.get("content-type") or ""))
        rp.parse(txt.splitlines()); return bool(rp.can_fetch(USER_AGENT,url)),"ROBOTS_LOADED"
    except urllib.error.HTTPError as e:
        if int(e.code) in (404,410): return True,f"ROBOTS_ABSENT_HTTP_{int(e.code)}"
        return False,f"ROBOTS_HTTP_{int(e.code)}"
    except Exception as e:
        return False,"ROBOTS_CHECK_FAILED:"+type(e).__name__+":"+str(e)

def _fetch(url:str)->Tuple[bytes,Dict[str,str],str,str]:
    validate_public_url(url)
    ok,rs=_robots_allowed(url)
    if not ok: raise ValueError("TSL_ROBOTS_DISALLOWED:"+rs)
    req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT,"Accept":"text/html,application/xhtml+xml;q=0.9,*/*;q=0.1","Accept-Language":"ja,en;q=0.3"})
    with urllib.request.urlopen(req,timeout=DEFAULT_TIMEOUT) as resp:
        final=str(resp.geturl()); validate_public_url(final)
        raw=resp.read(DEFAULT_MAX_BYTES+1)
        if len(raw)>DEFAULT_MAX_BYTES: raise ValueError("TSL_MAX_BYTES_EXCEEDED")
        headers={str(k).lower():str(v) for k,v in resp.headers.items()}
        return raw,headers,rs,final

def discover_tsl_race_url(venue_id:str,race_date:str,race_no:int)->Tuple[str,str,Dict[str,Any]]:
    venue=canonical_venue(venue_id); code=JRA_VENUE_CODES.get(venue)
    if not code: raise ValueError("TSL_JRA_VENUE_UNSUPPORTED:"+venue)
    d=date_compact(race_date); idx=f"{BASE}/{d}/"
    raw,headers,robots,final=_fetch(idx)
    candidates=[]
    for a in _anchors(raw,headers.get("content-type","")):
        href=urllib.parse.urljoin(final,str(a.get("href") or ""))
        p=urllib.parse.urlsplit(href)
        m=re.search(rf"/{d}/(\d{{10}})/0?{int(race_no)}/(?:last|table|index)\.html(?:$|\?)",p.path,re.I)
        if not m: continue
        key=m.group(1)
        if key.startswith(code): candidates.append((0 if "last.html" in p.path else 1,href,key,a.get("text")))
    if not candidates:
        # Some archive/index pages expose a meeting link rather than every race link.
        for a in _anchors(raw,headers.get("content-type","")):
            href=urllib.parse.urljoin(final,str(a.get("href") or ""))
            m=re.search(rf"/{d}/(\d{{10}})/",urllib.parse.urlsplit(href).path)
            if m and m.group(1).startswith(code):
                key=m.group(1)
                return f"{BASE}/{d}/{key}/{int(race_no)}/last.html",key,{"index_url":idx,"index_raw_sha256":hashlib.sha256(raw).hexdigest(),"robots_status":robots,"discovery":"MEETING_LINK"}
        raise ValueError("TSL_RACE_URL_NOT_DISCOVERED")
    candidates.sort()
    _,url,key,text=candidates[0]
    return url,key,{"index_url":idx,"index_raw_sha256":hashlib.sha256(raw).hexdigest(),"robots_status":robots,"anchor_text":text,"discovery":"RACE_LINK"}

def _number(v:Any):
    s=unicodedata.normalize("NFKC",str(v or "")).replace(",","")
    m=re.search(r"-?\d+(?:\.\d+)?",s)
    if not m:return None
    x=float(m.group(0)); return int(x) if x.is_integer() else x

def _find_table(decoded:str)->Tuple[List[str],List[List[str]]]:
    for table in _html_tables(decoded):
        if not table: continue
        for i,row in enumerate(table[:8]):
            hs=[_norm(x) for x in row]
            if "馬番" in hs and any("馬名" in h for h in hs):
                return hs,table[i+1:]
    raise ValueError("TSL_RUNNER_TABLE_NOT_FOUND")

def parse_tsl_html(raw:bytes,content_type:str="")->Dict[str,Any]:
    decoded=_decode(raw,content_type); text=_html_text(decoded)
    headers,rows=_find_table(decoded); col={h:i for i,h in enumerate(headers)}
    def idx_like(*names):
        for n in names:
            for h,i in col.items():
                if n in h:return i
        return None
    ni=idx_like("馬番"); namei=idx_like("馬名"); marki=idx_like("印")
    runners=[]
    for row in rows:
        if ni is None or ni>=len(row): continue
        hn=_number(row[ni])
        if not isinstance(hn,int) or not (1<=hn<=18): continue
        name=str(row[namei]).strip() if namei is not None and namei<len(row) else ""
        if not name: continue
        rec={"horse_no":hn,"horse_name":name,"mark":str(row[marki]).strip() if marki is not None and marki<len(row) else ""}
        mappings={
          "win_vote":["単勝"],"place_vote":["複勝"],"quinella_vote":["馬連"],
          "fracture":["断層"],"competition":["拮抗"],"anomaly":["異常"],
        }
        for key,names in mappings.items():
            ii=idx_like(*names); rawv=str(row[ii]).strip() if ii is not None and ii<len(row) else ""
            rec[key]={"value":_number(rawv),"raw":rawv}
        runners.append(rec)
    if not runners: raise ValueError("TSL_RUNNER_ROWS_NOT_FOUND")
    recommendations={}
    labels=[("axis","軸"),("main","本線"),("next","次点"),("cover","おさえ")]
    for key,label in labels:
        m=re.search(rf"{label}\s*[:：]\s*([^\n]+)",text)
        vals=[]
        if m:
            for no,score in re.findall(r"(\d{{1,2}})\s*\(\s*(-?\d+(?:\.\d+)?)\s*\)",m.group(1)):
                vals.append({"horse_no":int(no),"score":float(score)})
        recommendations[key]=vals
    meta={}
    m=re.search(r"(\d{1,2})R\s+(\d{1,2}:\d{2})\s+(\d+)m\s*([芝ダ障])",text)
    if m: meta={"race_no":int(m.group(1)),"start_time":m.group(2),"distance_m":int(m.group(3)),"surface":m.group(4)}
    return {"runners":sorted(runners,key=lambda x:x["horse_no"]),"recommendation_groups":recommendations,"race_meta":meta}

def _official_map(artifact:Dict[str,Any])->Dict[int,str]:
    u=artifact.get("jra_official_runner_universe") or artifact.get("official_runner_universe") or {}
    out={}
    for x in u.get("runners") or []:
        try: out[int(x.get("horse_no") or x.get("runner_id"))]=str(x.get("name") or "")
        except Exception: pass
    return out

def _runner_match(parsed:Dict[str,Any],artifact:Dict[str,Any])->Dict[str,Any]:
    official=_official_map(artifact); tsl={int(x["horse_no"]):str(x["horse_name"]) for x in parsed.get("runners") or []}
    if not official:return {"status":"NOT_AVAILABLE","official_count":0,"tsl_count":len(tsl),"matched":0,"errors":[]}
    errs=[]
    for no,name in official.items():
        if no not in tsl: errs.append(f"TSL_MISSING_OFFICIAL_RUNNER:{no}")
        elif _norm(name)!=_norm(tsl[no]): errs.append(f"TSL_RUNNER_NAME_MISMATCH:{no}:{name}:{tsl[no]}")
    for no in sorted(set(tsl)-set(official)): errs.append(f"TSL_EXTRA_RUNNER:{no}")
    return {"status":"MATCHED" if not errs else "MISMATCH","official_count":len(official),"tsl_count":len(tsl),"matched":len(set(official)&set(tsl)),"errors":errs}

def build_tsl_shadow_evidence(artifact:Dict[str,Any],prediction_cutoff:str,*,require_tsl:bool=False)->Tuple[Dict[str,Any],List[str]]:
    ctx=artifact.get("source_race_context") or {}; warnings=[]; errors=[]
    base={"profile":PROFILE,"source_class":SOURCE_CLASS,"authority":SOURCE_AUTHORITY,"official":False,
          "production_authority":False,"prediction_authority":False,"status":"UNAVAILABLE",
          "storage_policy":"NORMALIZED_EXTRACTED_DATA_PLUS_RAW_SHA_ONLY / NO_RAW_HTML_PERSISTENCE",
          "copyright_boundary":"THIRD_PARTY_PUBLIC_CONTENT / NO_REPUBLICATION_AUTHORITY",
          "robots_policy":"CHECK_BEFORE_FETCH / FAIL_CLOSED_IF_DISALLOWED_OR_UNKNOWN","warnings":warnings}
    try:
        url,key,discovery=discover_tsl_race_url(ctx.get("venue_id"),ctx.get("race_date"),int(ctx.get("race_no") or 0))
        raw,headers,robots,final=_fetch(url); fetched=utcnow()
        base.update({"requested_url":url,"final_url":final,"meeting_key":key,"discovery":discovery,
                     "robots_status":robots,"fetched_at":fetched,"raw_sha256":hashlib.sha256(raw).hexdigest(),"raw_byte_count":len(raw)})
        parsed=parse_tsl_html(raw,headers.get("content-type","")); base.update(parsed)
        base["runner_universe_match"]=_runner_match(parsed,artifact)
        fd=_parse_dt(fetched); cd=_parse_dt(prediction_cutoff)
        base["cutoff_relation"]="PRE_CUTOFF" if fd and cd and fd<=cd else "POST_CUTOFF"
        start=((parsed.get("race_meta") or {}).get("start_time"))
        post=None
        if start:
            d=str(ctx.get("race_date") or "").replace("/","-")
            try: post=datetime.datetime.fromisoformat(f"{d}T{start}:00").replace(tzinfo=ZoneInfo("Asia/Tokyo")).astimezone(datetime.timezone.utc)
            except Exception: post=None
        base["scheduled_post_at"]=post.isoformat() if post else None
        base["start_relation"]="PRE_START" if fd and post and fd<post else ("POST_START" if fd and post else "UNKNOWN")
        match=base["runner_universe_match"]["status"]
        base["oos_eligible"]=bool(base["cutoff_relation"]=="PRE_CUTOFF" and base["start_relation"]=="PRE_START" and match in {"MATCHED","NOT_AVAILABLE"})
        if match=="MISMATCH": warnings.extend(base["runner_universe_match"]["errors"])
        base["status"]="CAPTURED_PRE_RACE_SHADOW" if base["oos_eligible"] else "CAPTURED_NOT_OOS_ELIGIBLE"
    except Exception as e:
        base["error"]=type(e).__name__+":"+str(e); warnings.append("TSL_CAPTURE_FAILED:"+base["error"])
        if require_tsl: errors.append("TSL_PUBLIC_SHADOW_REQUIRED_FAILED:"+base["error"])
    base["warnings"]=list(dict.fromkeys(warnings))
    artifact["tsl_public_shadow_evidence"]=base
    artifact["tsl_public_shadow_evidence_sha256"]=sha_obj(base)
    if base.get("meeting_key"): artifact["jra_meeting_key_discovered"]=base["meeting_key"]
    return artifact,errors

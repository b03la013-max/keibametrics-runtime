from __future__ import annotations
import datetime, re, urllib.request
from typing import Any, Dict, List, Tuple
import fitz

from source_acquisition import (
    _SafeRedirect, sha_obj, snapshot_from_bytes, utcnow, validate_public_url
)

PROFILE="KM-JRA-OFFICIAL-PDF-RUNNER-UNIVERSE-v1.0-20260926"
SLUGS={
    "SPP":"sapporo","HKD":"hakodate","FKS":"fukushima","NGT":"niigata","TKY":"tokyo",
    "NKY":"nakayama","CHK":"chukyo","KYO":"kyoto","HSN":"hanshin","KKR":"kokura",
}
ALIASES={"SAP":"SPP","HAK":"HKD","NII":"NGT","TOK":"TKY","CHU":"CHK","KOK":"KKR"}

def _venue(v:Any)->str:
    x=str(v or "").upper().strip()
    return ALIASES.get(x,x)

def official_pdf_url(race_date:str, venue_id:str, meeting_key:str)->str:
    key=re.sub(r"\D","",str(meeting_key or ""))
    if not re.fullmatch(r"\d{10}",key):
        raise ValueError("JRA_MEETING_KEY_INVALID")
    venue=_venue(venue_id)
    if venue not in SLUGS:
        raise ValueError("JRA_VENUE_ID_UNSUPPORTED:"+venue)
    code,year,meeting,day=key[:2],key[2:6],key[6:8],key[8:10]
    expected={"SPP":"01","HKD":"02","FKS":"03","NGT":"04","TKY":"05","NKY":"06","CHK":"07","KYO":"08","HSN":"09","KKR":"10"}[venue]
    if code!=expected:
        raise ValueError("JRA_MEETING_KEY_VENUE_MISMATCH")
    d=datetime.date.fromisoformat(str(race_date).replace("/","-"))
    if str(d.year)!=year:
        raise ValueError("JRA_MEETING_KEY_YEAR_MISMATCH")
    return f"https://www.jra.go.jp/keiba/rpdf/pdf/{d.strftime('%Y%m%d')}-{meeting}{SLUGS[venue]}{day}.pdf"

def _clean_line(v:Any)->str:
    s=str(v or "").replace("\u3000"," ").strip()
    return re.sub(r"[\x00-\x1f\x7f]","",s).strip()

def _kana_name(v:Any)->bool:
    s=re.sub(r"\s+","",_clean_line(v))
    return bool(s and re.fullmatch(r"[ァ-ヶー・ヴヷヸヹヺ]+",s))

def _expected_count(lines:List[str], header_idx:int)->int|None:
    for i in range(header_idx-1,max(-1,header_idx-12),-1):
        m=re.search(r"[（(]\s*(\d{1,2})\s*頭\s*[）)]",lines[i])
        if m:
            return int(m.group(1))
    return None

def parse_runner_universe_from_pages(pages:List[str], race_no:int)->Dict[str,Any]:
    target=f"{int(race_no)}R"
    chosen=None
    for page_no,text in enumerate(pages,1):
        lines=[_clean_line(x) for x in str(text or "").splitlines()]
        for i,line in enumerate(lines):
            if re.sub(r"\s+","",line).upper()==target.upper():
                count=_expected_count(lines,i)
                if count:
                    chosen=(page_no,lines,i,count)
                    break
        if chosen:
            break
    if not chosen:
        raise ValueError("JRA_OFFICIAL_PDF_RACE_HEADER_NOT_FOUND")
    page_no,lines,header,count=chosen
    end=len(lines)
    for i in range(header+1,len(lines)-1):
        if lines[i]=="コース" and lines[i+1]=="レコード":
            end=i
            break
    block=lines[header+1:end]
    markers=[i for i,x in enumerate(block) if re.search(r"（\d{4}年）",x)]
    if len(markers)<count:
        raise ValueError(f"JRA_OFFICIAL_PDF_RUNNER_MARKERS_SHORT:{len(markers)}<{count}")
    runners=[]
    for no,mi in enumerate(markers[:count],1):
        stop=markers[no] if no<count and no<len(markers) else len(block)
        name_parts=[]
        for x in block[mi+1:stop]:
            s=re.sub(r"\s+","",_clean_line(x))
            if not s:
                continue
            if _kana_name(s):
                name_parts.append(s)
                continue
            if name_parts:
                break
        name="".join(name_parts)
        if not name:
            raise ValueError(f"JRA_OFFICIAL_PDF_HORSE_NAME_MISSING:{no}")
        runners.append({
            "runner_id":str(no),"horse_no":no,"frame_no":None,
            "name":name,"canonical_name":name,"status":"ACTIVE",
            "body_weight":None,"body_weight_change":None,
            "source":"JRA_OFFICIAL_RACE_PDF",
        })
    if len(runners)!=count:
        raise ValueError("JRA_OFFICIAL_PDF_RUNNER_COUNT_MISMATCH")
    base={
        "profile":PROFILE,
        "source_id":"JRA-OFFICIAL-RACE-PDF",
        "pdf_page_number":page_no,
        "race_no":int(race_no),
        "declared_runner_count":count,
        "runner_count":len(runners),
        "runners":runners,
        "universe_type":"ACTIVE",
    }
    base["runner_universe_sha256"]=sha_obj(base)
    return base

def fetch_and_enrich_official_pdf(
    artifact:Dict[str,Any], prediction_cutoff:str, *,
    race_date:str, venue_id:str, race_no:int, meeting_key:str
)->Dict[str,Any]:
    url=official_pdf_url(race_date,venue_id,meeting_key)
    validate_public_url(url)
    spec={
        "source_id":"JRA-OFFICIAL-RACE-PDF",
        "source_class":"OFFICIAL_JRA_RACE_CARD_PDF",
        "authority":"JRA_OFFICIAL",
        "priority":130,
        "official":True,
        "required":True,
        "url":url,
        "max_bytes":6500000,
        "timeout_seconds":30,
        "extract":[],
    }
    opener=urllib.request.build_opener(_SafeRedirect())
    req=urllib.request.Request(url,headers={
        "User-Agent":"KeibaMetrics-JRA-Source-Acquisition/1.1",
        "Accept":"application/pdf,*/*;q=0.1",
        "Accept-Language":"ja,en;q=0.5",
    })
    fetched_at=utcnow()
    with opener.open(req,timeout=30) as resp:
        final_url=resp.geturl(); validate_public_url(final_url)
        raw=resp.read(6500001)
        if len(raw)>6500000:
            raise ValueError("JRA_OFFICIAL_PDF_MAX_BYTES_EXCEEDED")
        if not raw.startswith(b"%PDF"):
            raise ValueError("JRA_OFFICIAL_PDF_MAGIC_INVALID")
        headers={k.lower():v for k,v in resp.headers.items()}
        snapshot,serr=snapshot_from_bytes(
            spec,raw,final_url=final_url,status_code=int(getattr(resp,"status",200)),
            headers=headers,fetched_at=fetched_at,prediction_cutoff=prediction_cutoff
        )
        if serr:
            raise ValueError("JRA_OFFICIAL_PDF_SNAPSHOT_ERROR:"+"|".join(serr))
    doc=fitz.open(stream=raw,filetype="pdf")
    pages=[p.get_text("text") for p in doc]
    universe=parse_runner_universe_from_pages(pages,int(race_no))
    universe["source_snapshot_sha256"]=snapshot["snapshot_sha256"]
    universe["raw_sha256"]=snapshot["raw_sha256"]
    universe["official_pdf_url"]=final_url
    universe["runner_universe_sha256"]=sha_obj({k:v for k,v in universe.items() if k!="runner_universe_sha256"})
    artifact["sources"]=list(artifact.get("sources") or [])+[snapshot]
    artifact["jra_official_pdf_runner_universe"]=universe
    artifact["jra_official_pdf_runner_universe_sha256"]=sha_obj(universe)
    artifact["jra_declared_runner_universe"]={**universe,"universe_type":"DECLARED"}
    artifact["jra_official_runner_universe"]=universe
    artifact["jra_official_runner_universe_sha256"]=sha_obj(universe)
    artifact["official_runner_universe"]=universe
    artifact["official_runner_universe_sha256"]=universe["runner_universe_sha256"]
    return artifact

from __future__ import annotations
import datetime, re, urllib.request
from typing import Any, Dict, List, Tuple
import fitz

from source_acquisition import (
    _SafeRedirect, sha_obj, snapshot_from_bytes, utcnow, validate_public_url
)

PROFILE="KM-JRA-OFFICIAL-PDF-RUNNER-UNIVERSE-v1.3-20260927"
SLUGS={
    "SPP":"sapporo","HKD":"hakodate","FKS":"fukushima","NGT":"niigata","TKY":"tokyo",
    "NKY":"nakayama","CHK":"chukyo","KYO":"kyoto","HSN":"hanshin","KKR":"kokura",
}
ALIASES={"SAP":"SPP","HAK":"HKD","NII":"NGT","TOK":"TKY","CHU":"CHK","KOK":"KKR"}
FRAME_COLOR={"白":1,"黒":2,"赤":3,"青":4,"黄":5,"緑":6,"橙":7,"桃":8}

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

def _race_header_priority(line:Any,race_no:int)->int|None:
    # Live JRA PDFs can emit the race label as either "10R" or "R4 <race name>"
    # depending on page/layout text extraction. Prefer the explicit R<n> form
    # because a bare <n>R token can also appear accidentally inside column text.
    s=re.sub(r"\s+","",_clean_line(line)).upper()
    n=str(int(race_no))
    if re.match(rf"^R{re.escape(n)}(?:$|[^0-9])",s):
        return 0
    if re.match(rf"^{re.escape(n)}R(?:$|[^0-9])",s):
        return 1
    return None

def _race_label_number(v:Any)->int|None:
    s=re.sub(r"\s+","",_clean_line(v)).upper()
    m=re.fullmatch(r"R(\d{1,2})",s)
    if m:return int(m.group(1))
    m=re.fullmatch(r"(\d{1,2})R",s)
    if m:return int(m.group(1))
    return None

def _column_clip_for_race(page:Any,race_no:int):
    words=list(page.get_text("words") or [])
    labels=[]
    for w in words:
        if len(w)<5:continue
        no=_race_label_number(w[4])
        if no is None:continue
        x0,y0,x1,y1=map(float,w[:4])
        labels.append({"race_no":no,"x0":x0,"y0":y0,"x1":x1,"y1":y1,
                       "xc":(x0+x1)/2.0,"yc":(y0+y1)/2.0})
    targets=[x for x in labels if int(x["race_no"])==int(race_no)]
    if not targets:
        return None
    # Race headers sharing the same page row define the JRA multi-column layout.
    # Pick the target that has the largest same-row peer set.
    ranked=[]
    for t in targets:
        peers=[x for x in labels if abs(x["yc"]-t["yc"])<=18.0]
        ranked.append((len(peers),t,peers))
    _,target,peers=max(ranked,key=lambda z:z[0])
    peers=sorted(peers,key=lambda x:x["xc"])
    centers=[x["xc"] for x in peers]
    pos=min(range(len(peers)),key=lambda i:abs(peers[i]["xc"]-target["xc"]))
    left=float(page.rect.x0) if pos==0 else (centers[pos-1]+centers[pos])/2.0
    right=float(page.rect.x1) if pos==len(peers)-1 else (centers[pos]+centers[pos+1])/2.0
    if right-left < 40:
        return None

    # JRA race-card PDF pages may use a multi-row grid (for example R5/R6 on
    # the upper row and later races below).  An X-only clip therefore leaks a
    # later race from the same column into the target race block.  Bound the
    # clip vertically at midpoints between race headers in the same column.
    same_col=sorted(
        [x for x in labels if left <= x["xc"] <= right],
        key=lambda x:x["yc"]
    )
    above=[x for x in same_col if x["yc"] < target["yc"]-18.0]
    below=[x for x in same_col if x["yc"] > target["yc"]+18.0]
    top=float(page.rect.y0) if not above else (above[-1]["yc"]+target["yc"])/2.0
    bottom=float(page.rect.y1) if not below else (target["yc"]+below[0]["yc"])/2.0
    if bottom-top < 60:
        return None
    return fitz.Rect(left,top,right,bottom)

def parse_runner_universe_from_doc(doc:Any,race_no:int)->Dict[str,Any]:
    errors=[]
    for page_index,page in enumerate(doc):
        clip=_column_clip_for_race(page,int(race_no))
        if clip is None:
            continue
        # sort=True restores natural top-to-bottom order inside a single race column.
        text=page.get_text("text",clip=clip,sort=True)
        try:
            out=parse_runner_universe_from_pages([text],int(race_no))
            out["pdf_page_number"]=page_index+1
            out["pdf_column_clip"]=[round(float(clip.x0),3),round(float(clip.y0),3),
                                    round(float(clip.x1),3),round(float(clip.y1),3)]
            return out
        except Exception as exc:
            errors.append(type(exc).__name__+":"+str(exc))
    if errors:
        raise ValueError("JRA_OFFICIAL_PDF_COLUMN_PARSE_FAILED:"+"|".join(errors))
    raise ValueError("JRA_OFFICIAL_PDF_RACE_COLUMN_NOT_FOUND")

def parse_runner_universe_from_pages(pages:List[str], race_no:int)->Dict[str,Any]:
    candidates=[]
    for page_no,text in enumerate(pages,1):
        lines=[_clean_line(x) for x in str(text or "").splitlines()]
        for i,line in enumerate(lines):
            pri=_race_header_priority(line,int(race_no))
            if pri is None:
                continue
            count=_expected_count(lines,i)
            if count:
                candidates.append((pri,page_no,lines,i,count))
    if not candidates:
        raise ValueError("JRA_OFFICIAL_PDF_RACE_HEADER_NOT_FOUND")
    candidates.sort(key=lambda x:(x[0],x[1],x[3]))
    _,page_no,lines,header,count=candidates[0]
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
        pre=block[max(0,mi-10):mi]
        sex=None; age=None; assigned_weight=None; frame_no=None
        for x in reversed(pre):
            s=re.sub(r"\s+","",_clean_line(x))
            if not s:
                continue
            if frame_no is None and s in FRAME_COLOR:
                frame_no=FRAME_COLOR[s]
            if sex is None:
                sm=re.fullmatch(r"(牡|牝|騸|せん)(\d{1,2})",s)
                if sm:
                    sex=sm.group(1); age=int(sm.group(2))
            if assigned_weight is None:
                wm=re.search(r"(?:白|黒|赤|青|黄|緑|橙|桃|鹿|栗|芦|栃|粕).*?(\d{2}(?:\.\d+)?)$",s)
                if wm:
                    assigned_weight=float(wm.group(1))
        segment=block[mi+1:stop]
        name_parts=[]; name_end=None
        for j,x in enumerate(segment):
            s=re.sub(r"\s+","",_clean_line(x))
            if not s:
                continue
            if _kana_name(s):
                name_parts.append(s); name_end=j
                continue
            if name_parts:
                break
        name="".join(name_parts)
        if not name:
            raise ValueError(f"JRA_OFFICIAL_PDF_HORSE_NAME_MISSING:{no}")
        jockey_parts=[]
        if name_end is not None:
            for x in segment[name_end+1:name_end+7]:
                s=re.sub(r"\s+","",_clean_line(x))
                if not s:
                    continue
                if re.fullmatch(r"\d+",s) or re.search(r"[A-Za-z]",s):
                    if jockey_parts:
                        break
                    continue
                clean=re.sub(r"[0-9０-９,，.．].*$","",s)
                if clean and re.fullmatch(r"[一-龯々ヶぁ-んァ-ヶー・]+",clean):
                    jockey_parts.append(clean)
                    if len(jockey_parts)>=2:
                        break
        runners.append({
            "runner_id":str(no),"horse_no":no,"frame_no":frame_no,
            "name":name,"canonical_name":name,"status":"ACTIVE",
            "sex":sex,"age":age,"assigned_weight":assigned_weight,
            "jockey":"".join(jockey_parts[:2]) if jockey_parts else None,
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
        "User-Agent":"KeibaMetrics-JRA-Source-Acquisition/1.2",
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
        if snapshot.get("cutoff_relation")=="POST_CUTOFF":
            raise ValueError("JRA_OFFICIAL_PDF_POST_CUTOFF")
        if serr:
            raise ValueError("JRA_OFFICIAL_PDF_SNAPSHOT_ERROR:"+"|".join(serr))
    doc=fitz.open(stream=raw,filetype="pdf")
    try:
        universe=parse_runner_universe_from_doc(doc,int(race_no))
    except Exception:
        # Compatibility fallback for historical single-column fixtures/PDFs.
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

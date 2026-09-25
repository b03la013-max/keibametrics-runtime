from __future__ import annotations
import datetime,re
from typing import Any,Dict
from zoneinfo import ZoneInfo
from source_acquisition import sha_obj
from jra_source_manifest import JRA_VENUE_NAMES,canonical_venue

PROFILE="KM-JRA-OFFICIAL-RACE-CONTEXT-v1.0-20260926"

def _text(artifact:Dict[str,Any])->str:
    x=((artifact.get("normalized_evidence") or {}).get("calendar_text") or {})
    return str(x.get("value") or "")

def _distance_surface(block:str):
    m=re.search(r"(?<!\d)(\d{3,4}|\d,\d{3})\s*（([^）]+)）",block)
    if not m:return None,None
    distance=int(m.group(1).replace(",",""))
    s=m.group(2)
    if "芝" in s: surface="芝"
    elif "ダ" in s: surface="ダ"
    elif "障" in s: surface="障"
    else: surface=None
    return distance,surface

def parse_race_context(calendar_text:str,venue_id:str,race_date:str,race_no:int)->Dict[str,Any]:
    venue=canonical_venue(venue_id)
    venue_name=JRA_VENUE_NAMES.get(venue)
    if not venue_name: raise ValueError("JRA_VENUE_UNSUPPORTED:"+venue)
    text=re.sub(r"\s+"," ",str(calendar_text or "")).strip()
    if not text: raise ValueError("JRA_CALENDAR_TEXT_EMPTY")
    mm=re.search(rf"(\d+)回{re.escape(venue_name)}(\d+)日",text)
    if not mm: raise ValueError("JRA_MEETING_CONTEXT_NOT_FOUND")
    start=mm.start()
    nxt=re.search(r"\d+回(?:札幌|函館|福島|新潟|東京|中山|中京|京都|阪神|小倉)\d+日",text[mm.end():])
    end=mm.end()+nxt.start() if nxt else len(text)
    meeting=text[start:end]
    rn=int(race_no)
    rpat=rf"(?:^|\s){rn}\s*レース\s+(.*?)(?=\s+{rn+1}\s*レース\s+|\s+表示モード|$)" if rn<12 else rf"(?:^|\s){rn}\s*レース\s+(.*?)(?=\s+表示モード|$)"
    rm=re.search(rpat,meeting)
    if not rm: raise ValueError("JRA_RACE_CONTEXT_NOT_FOUND")
    block=rm.group(1).strip()
    distance,surface=_distance_surface(block)
    tm=re.search(r"(\d{1,2})時(\d{2})分",block)
    start_time=f"{int(tm.group(1)):02d}:{tm.group(2)}" if tm else None
    weight_rule=next((x for x in ("ハンデ","定量","別定") if x in block),None)
    course_variant=None
    if "芝・外" in block: course_variant="外"
    elif "芝・内" in block: course_variant="内"
    race_class=None
    for x in ("新馬","未勝利","1勝クラス","2勝クラス","3勝クラス","オープン","リステッド","GⅠ","GⅡ","GⅢ"):
        if x in block:
            race_class=x
    d=datetime.date.fromisoformat(str(race_date).replace("/","-"))
    scheduled=None
    if start_time:
        scheduled=datetime.datetime.fromisoformat(f"{d.isoformat()}T{start_time}:00").replace(tzinfo=ZoneInfo("Asia/Tokyo")).isoformat()
    out={
      "profile":PROFILE,"official":True,"production_fact_authority":True,
      "venue_id":venue,"venue_name":venue_name,"meeting_no":int(mm.group(1)),"meeting_day":int(mm.group(2)),
      "race_date":d.isoformat(),"race_no":rn,"distance_m":distance,"surface":surface,
      "course_variant":course_variant,"weight_rule":weight_rule,"race_class":race_class,
      "start_time":start_time,"scheduled_post_at":scheduled,"raw_race_context":block
    }
    out["sha256"]=sha_obj({k:v for k,v in out.items() if k!="sha256"})
    return out

def enrich_with_race_context(artifact:Dict[str,Any])->Dict[str,Any]:
    ctx=artifact.get("source_race_context") or {}
    out=parse_race_context(_text(artifact),ctx.get("venue_id"),ctx.get("race_date"),int(ctx.get("race_no") or 0))
    artifact["jra_race_context"]=out
    artifact["jra_race_context_sha256"]=sha_obj(out)
    return artifact

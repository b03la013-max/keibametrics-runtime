from __future__ import annotations
import datetime, re
from typing import Any, Dict, List
from source_acquisition import sha_obj

PROFILE="KM-JRA-SOURCE-MANIFEST-v1.0-20260925"
JRA_VENUE_CODES={
    "SPP":"01","HKD":"02","FKS":"03","NGT":"04","TKY":"05",
    "NKY":"06","CHK":"07","KYO":"08","HSN":"09","KKR":"10",
}
JRA_VENUE_NAMES={
    "SPP":"札幌","HKD":"函館","FKS":"福島","NGT":"新潟","TKY":"東京",
    "NKY":"中山","CHK":"中京","KYO":"京都","HSN":"阪神","KKR":"小倉",
}
ALIASES={"SAP":"SPP","HAK":"HKD","NII":"NGT","TOK":"TKY","CHU":"CHK","KOK":"KKR"}

def canonical_venue(v: Any)->str:
    x=str(v or "").upper().strip()
    return ALIASES.get(x,x)

def date_compact(v: Any)->str:
    s=str(v or "").strip().replace("/","-")
    d=datetime.date.fromisoformat(s)
    return d.strftime("%Y%m%d")

def calendar_url(race_date: str)->str:
    d=datetime.date.fromisoformat(str(race_date).replace("/","-"))
    return f"https://www.jra.go.jp/keiba/calendar{d.year}/{d.year}/{d.month}/{d.strftime('%m%d')}.html"

def race_card_url_from_meeting_key(meeting_key: str, race_date: str, race_no: int)->str:
    key=re.sub(r"\D","",str(meeting_key or ""))
    if not re.fullmatch(r"\d{10}",key):
        raise ValueError("JRA_MEETING_KEY_INVALID")
    return f"https://www.jra.go.jp/JRADB/accessD.html?CNAME=pw01dde01{key}{int(race_no):02d}{date_compact(race_date)}"

def result_url_from_meeting_key(meeting_key: str, race_date: str, race_no: int)->str:
    key=re.sub(r"\D","",str(meeting_key or ""))
    if not re.fullmatch(r"\d{10}",key):
        raise ValueError("JRA_MEETING_KEY_INVALID")
    return f"https://www.jra.go.jp/JRADB/accessS.html?CNAME=pw01sde01{key}{int(race_no):02d}{date_compact(race_date)}"

def _spec(source_id, source_class, url, *, required=False, extract=None, priority=100):
    return {
        "source_id":source_id,"source_class":source_class,"authority":"JRA_OFFICIAL",
        "priority":priority,"official":True,"required":required,"url":url,
        "max_bytes":2000000,"timeout_seconds":25,"extract":extract or [],
    }

def build_jra_manifest(payload: Dict[str,Any])->Dict[str,Any]:
    venue=canonical_venue(payload.get("venue_id"))
    if venue not in JRA_VENUE_CODES:
        raise ValueError("JRA_VENUE_ID_UNSUPPORTED:"+venue)
    race_date=str(payload.get("race_date") or "").replace("/","-")
    race_no=int(payload.get("race_no") or 0)
    if race_no<1 or race_no>12:
        raise ValueError("JRA_RACE_NO_OUT_OF_RANGE")
    date_compact(race_date)
    sources: List[Dict[str,Any]]=[
        _spec("JRA-CALENDAR","OFFICIAL_JRA_CALENDAR",calendar_url(race_date),required=False,extract=[
            {"field":"calendar_text","type":"html_text","required":False}
        ])
    ]
    card=str(payload.get("official_race_card_url") or "").strip()
    meeting_key=str(payload.get("jra_meeting_key") or "").strip()
    if not card and meeting_key:
        card=race_card_url_from_meeting_key(meeting_key,race_date,race_no)
    if card:
        sources.append(_spec("JRA-RACE-CARD","OFFICIAL_JRA_RACE_CARD",card,required=True,extract=[
            {"field":"race_card_tables","type":"html_tables","required":True},
            {"field":"race_card_text","type":"html_text","required":True},
        ],priority=120))
    for r in range(1,race_no):
        u=(payload.get("same_day_result_urls") or {}).get(str(r)) if isinstance(payload.get("same_day_result_urls"),dict) else None
        if not u and meeting_key:
            u=result_url_from_meeting_key(meeting_key,race_date,r)
        if u:
            sources.append(_spec(f"JRA-SAME-DAY-R{r:02d}-RESULT","OFFICIAL_JRA_SAME_DAY_RESULT",str(u),required=False,extract=[
                {"field":f"same_day_r{r:02d}_result_tables","type":"html_tables","required":False}
            ],priority=110))
    out={
        "profile":PROFILE,"family_id":"JRA","venue_id":venue,"venue_name":JRA_VENUE_NAMES[venue],
        "jra_venue_code":JRA_VENUE_CODES[venue],"race_date":race_date,"race_no":race_no,
        "automatic_tsl_discovery":True,"sources":sources,
        "official_runner_universe_required_for_formal_full":True,
    }
    out["sha256"]=sha_obj({k:v for k,v in out.items() if k!="sha256"})
    return out

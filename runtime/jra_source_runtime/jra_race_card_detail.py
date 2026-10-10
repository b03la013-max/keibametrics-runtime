from __future__ import annotations
import datetime, hashlib, http.cookiejar, html, re, urllib.parse, urllib.request
from typing import Any, Dict, List, Tuple

try:
    from .source_acquisition import _decode, _html_text, _html_tables, sha_obj, snapshot_from_bytes, utcnow, validate_public_url
except ImportError:
    from source_acquisition import _decode, _html_text, _html_tables, sha_obj, snapshot_from_bytes, utcnow, validate_public_url

PROFILE="KM-JRA-OFFICIAL-RACE-CARD-DETAIL-v1.0-20260926"
BASE="https://www.jra.go.jp"
USER_AGENT="KeibaMetrics-JRA-Official-Detail/1.0"

def _norm(v:Any)->str:
    return re.sub(r"\s+"," ",str(v or "")).strip()

def _date8(v:str)->str:
    return datetime.date.fromisoformat(str(v).replace("/","-")).strftime("%Y%m%d")

def _fetch(opener,url:str,*,data:bytes|None=None,referer:str|None=None)->Tuple[str,bytes,Dict[str,str]]:
    validate_public_url(url)
    h={"User-Agent":USER_AGENT,"Accept":"text/html,application/xhtml+xml;q=0.9,*/*;q=0.1","Accept-Language":"ja,en;q=0.4"}
    if referer:h["Referer"]=referer
    req=urllib.request.Request(url,data=data,headers=h)
    with opener.open(req,timeout=30) as resp:
        final=str(resp.geturl()); validate_public_url(final)
        raw=resp.read(6000000)
        return final,raw,{str(k).lower():str(v) for k,v in resp.headers.items()}

def _post(opener,token:str,referer:str)->Tuple[str,bytes,Dict[str,str]]:
    data=urllib.parse.urlencode({"cname":token}).encode()
    return _fetch(opener,BASE+"/JRADB/accessD.html",data=data,referer=referer)

def _calendar_url(race_date:str)->str:
    d=datetime.date.fromisoformat(str(race_date).replace("/","-"))
    return f"{BASE}/keiba/calendar{d.year}/{d.year}/{d.month}/{d.strftime('%m%d')}.html"

def _discover_and_fetch(race_date:str,meeting_key:str,race_no:int)->Tuple[bytes,Dict[str,str],str,Dict[str,str]]:
    d=_date8(race_date)
    key=re.sub(r"\D","",str(meeting_key or ""))
    if not re.fullmatch(r"\d{10}",key): raise ValueError("JRA_MEETING_KEY_INVALID")
    jar=http.cookiejar.CookieJar()
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    u0,r0,h0=_fetch(opener,_calendar_url(race_date))
    s0=_decode(r0,h0.get("content-type",""))
    m=re.search(r"doAction\('/JRADB/accessD\.html'\s*,\s*'([^']+)'\)",s0)
    if not m: raise ValueError("JRA_DETAIL_ENTRY_TOKEN_NOT_FOUND")
    entry=m.group(1)
    u1,r1,h1=_post(opener,entry,u0)
    s1=_decode(r1,h1.get("content-type",""))
    m=re.search(r"(pw01drl00"+re.escape(key)+re.escape(d)+r"/[0-9A-Fa-f]{2})",s1)
    if not m: raise ValueError("JRA_DETAIL_DAY_TOKEN_NOT_FOUND")
    day=m.group(1)
    u2,r2,h2=_post(opener,day,u1)
    s2=_decode(r2,h2.get("content-type",""))
    prefix="pw01dde01"+key+f"{int(race_no):02d}"+d
    m=re.search(r"("+re.escape(prefix)+r"/[0-9A-Fa-f]{2})",s2)
    if not m: raise ValueError("JRA_DETAIL_RACE_TOKEN_NOT_FOUND")
    race=m.group(1)
    u3,r3,h3=_post(opener,race,u2)
    return r3,h3,u3,{"entry_token":entry,"day_token":day,"race_token":race}

def parse_detail_race_context(raw:bytes, content_type:str="")->Dict[str,Any]|None:
    """Printed current card conditions; calendar is only a scheduled program."""
    text=_html_text(_decode(raw,content_type))
    head=re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日[（(][^）)]*[）)]\s*(\d+)回(札幌|函館|福島|新潟|東京|中山|中京|京都|阪神|小倉)(\d+)日\s+(\d+)レース",text)
    tm=re.search(r"発走時刻[：:]\s*(\d{1,2})時(\d{2})分",text)
    course=re.search(r"コース[：:]\s*([\d,]+)\s*メートル\s*[（(]([^）)]+)[）)]",text)
    if not (head and tm and course): return None
    y,m,d,meeting,venue,day,rn=head.groups()
    date=datetime.date(int(y),int(m),int(d)).isoformat()
    distance=int(course.group(1).replace(",",""))
    description=course.group(2)
    surface="ダ" if "ダ" in description else "芝" if "芝" in description else "障" if "障" in description else None
    if surface is None: return None
    before=text[tm.end():course.start()]
    classes=[x for x in ("新馬","未勝利","1勝クラス","2勝クラス","3勝クラス","オープン","リステッド","GⅠ","GⅡ","GⅢ") if x in before]
    weather=re.search(r"天候\s+(\S+)",before)
    going=re.search(r"(?:芝|ダート|ダ)\s+(良|稍重|重|不良)",before)
    try:
        from .jra_source_manifest import JRA_VENUE_NAMES
    except ImportError:
        from jra_source_manifest import JRA_VENUE_NAMES
    start=f"{int(tm.group(1)):02d}:{tm.group(2)}"
    return {"profile":"KM-JRA-OBSERVED-DETAIL-RACE-CONTEXT-v1",
            "official":True,"production_fact_authority":True,
            "venue_id":next(k for k,v in JRA_VENUE_NAMES.items() if v==venue),"venue_name":venue,
            "race_date":date,"race_no":int(rn),"meeting_no":int(meeting),"meeting_day":int(day),
            "distance_m":distance,"surface":surface,"course_variant":"外" if "外" in description else "内" if "内" in description else None,
            "race_class":classes[-1] if classes else None,
            "weight_rule":next((x for x in ("ハンデ","定量","別定") if x in before),None),
            "weather":weather.group(1) if weather else None,"going":going.group(1) if going else None,
            "start_time":start,"scheduled_post_at":f"{date}T{start}:00+09:00",
            "raw_race_context":before.strip()+" コース： "+course.group(0)}

def _num(v:Any)->int|None:
    m=re.search(r"-?\d+",str(v or "").replace(",",""))
    return int(m.group(0)) if m else None

def _flt(v:Any)->float|None:
    m=re.search(r"-?\d+(?:\.\d+)?",str(v or "").replace(",",""))
    return float(m.group(0)) if m else None

def _parse_identity(cell:str)->Dict[str,Any]:
    s=_norm(cell)
    name=s.split(" ")[0] if s else ""
    odds=pop=None
    m=re.search(r"(.+?)\s+(\d+(?:\.\d+)?)\s*\(\s*(\d+)\s*番人気\s*\)",s)
    if m:
        name=m.group(1).strip(); odds=float(m.group(2)); pop=int(m.group(3))
    rec=None
    m2=re.search(r"\((\d+)\.(\d+)\.(\d+)\.(\d+)\)",s)
    if m2:
        rec={"wins":int(m2.group(1)),"seconds":int(m2.group(2)),"thirds":int(m2.group(3)),"others":int(m2.group(4))}
        rec["starts"]=sum(rec.values())
    prize=None
    m3=re.search(r"([\d,]+)\s*万円",s)
    if m3: prize=int(m3.group(1).replace(",",""))
    sire=dam=damsire=None
    m4=re.search(r"父[:：]\s*([^\s]+)\s+母[:：]\s*([^\s(]+)\s*\(母の父[:：]\s*([^)]+)\)",s)
    if m4: sire,dam,damsire=[x.strip() for x in m4.groups()]
    trainer=None; trainer_base=None
    before=s.split("父：",1)[0]
    ms=list(re.finditer(r"([一-龯々ぁ-んァ-ヶー・A-Za-z.]+(?:\s+[一-龯々ぁ-んァ-ヶー・A-Za-z.]+)?)\((美浦|栗東)\)",before))
    if ms:
        trainer=ms[-1].group(1).strip(); trainer_base=ms[-1].group(2)
    bw=bwd=None
    mb=list(re.finditer(r"(\d{3})\s*kg(?:\s*\(\s*([+-]?\d+)\s*\))?",s,re.I))
    if mb:
        bw=int(mb[-1].group(1))
        if mb[-1].group(2) is not None: bwd=int(mb[-1].group(2))
    return {"horse_name":name,"win_odds":odds,"popularity_rank":pop,"career_record":rec,"total_prize_10k_yen":prize,
            "trainer":trainer,"trainer_base":trainer_base,"sire":sire,"dam":dam,"damsire":damsire,
            "current_body_weight":bw,"current_body_weight_change":bwd,"raw":s}

def _parse_current_person(cell:str)->Dict[str,Any]:
    s=_norm(cell)
    sex=age=color=None; assigned=None; jockey=None
    m=re.search(r"(牡|牝|騸|せん)(\d+)\s*/\s*([^\s]+)",s)
    if m: sex=m.group(1); age=int(m.group(2)); color=m.group(3)
    m2=re.search(r"(\d{2}(?:\.\d+)?)\s*kg\s+(.+)$",s)
    if m2: assigned=float(m2.group(1)); jockey=m2.group(2).strip()
    return {"sex":sex,"age":age,"color":color,"assigned_weight":assigned,"jockey":jockey,"raw":s}

def decode_passing_positions(digits:str,field_size:Any)->List[int]|None:
    """Decode concatenated corner calls; None when ambiguous or invalid."""
    s=str(digits or "")
    try:
        n=int(field_size)
    except (TypeError,ValueError):
        return None
    if not s.isdigit() or n<1:
        return None
    best=[]
    def walk(i,acc):
        if len(acc)>4:
            return
        if i==len(s):
            if acc:
                best.append(list(acc))
            return
        for w in (1,2):
            part=s[i:i+w]
            if len(part)<w or part.startswith("0"):
                continue
            v=int(part)
            if 1<=v<=n:
                acc.append(v); walk(i+w,acc); acc.pop()
    walk(0,[])
    if not best:
        return None
    # JRA cards list at least two calls whenever more than one digit is shown.
    multi=[c for c in best if len(c)>=2]
    if multi:
        best=multi
    def cost(c):
        return sum(abs(a-b) for a,b in zip(c,c[1:]))
    low=min(cost(c) for c in best)
    winners=[c for c in best if cost(c)==low]
    if len({(c[0],c[-1]) for c in winners})!=1:
        return None
    return min(winners,key=len)

def _parse_recent(cell:str)->Dict[str,Any]|None:
    s=_norm(cell)
    if not s or "着" not in s:return None
    out={"raw":s}
    m=re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日",s)
    if m: out["date"]=f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m=re.search(r"\d{1,2}日\s+([^\s]+)",s)
    if m: out["venue"]=m.group(1)
    m=re.search(r"(\d+)\s*着",s); out["finish"]=int(m.group(1)) if m else None
    m=re.search(r"(\d+)\s*頭",s); out["field_size"]=int(m.group(1)) if m else None
    m=re.search(r"(\d+)\s*番人気",s); out["popularity_rank"]=int(m.group(1)) if m else None
    m=re.search(r"(\d{2}(?:\.\d+)?)\s*kg\s+(\d{3,4})\s*(芝|ダ|障)",s)
    if m:
        out["assigned_weight"]=float(m.group(1)); out["distance_m"]=int(m.group(2)); out["surface"]=m.group(3)
    mt=re.search(r"(?:芝|ダ|障)\s+(\d+:\d{2}\.\d|\d{2,3}\.\d)",s)
    if mt: out["time"]=mt.group(1)
    # Open/handicap races print the official rating between going and weight.
    mg=re.search(r"\s(良|稍重|重|不良)\s+(?:(\d{2,3})\s+)?(\d{3})\s*kg",s)
    if mg:
        out["going"]=mg.group(1); out["body_weight"]=int(mg.group(3))
        if mg.group(2): out["rating"]=int(mg.group(2))
    mf=re.search(r"3F\s*(\d{2}\.\d)",s)
    if mf: out["final3f"]=float(mf.group(1))
    mm=re.search(r"\(([+-]?\d+(?:\.\d+)?)\)\s*$",s)
    if mm: out["margin"]=float(mm.group(1))
    pos=None
    if mg and mf:
        between=s[mg.end():mf.start()]
        nums=re.sub(r"\D","",between)
        if nums: pos=nums
    out["passing_positions_raw"]=pos
    # Preserve unambiguous call positions as a structured list. Values >=10 are
    # kept when separators survived the HTML table normalization.
    calls=[]
    if mg and mf:
        between=s[mg.end():mf.start()]
        calls=[int(z) for z in re.findall(r"(?<!\d)(\d{1,2})(?!\d)",between)]
        if len(calls)==1 and pos and len(str(pos))>2:
            calls=[]
        if calls:
            out["passing_positions_parser"]="CORNER-LIST-SEPARATED-v2"
        if not calls and pos and str(pos).isdigit():
            # The official card concatenates corner calls without separators
            # ("1515" = 15-15, "119" = 11-9). Splitting per digit corrupted
            # every call >=10. Decode only when the segmentation is unique
            # under the field-size bound and the smallest-movement criterion.
            calls=decode_passing_positions(str(pos),out.get("field_size")) or []
            if calls:
                out["passing_positions_parser"]="CONCATENATED-DECODED-v2"
    out["passing_positions"]=calls
    # Recent rider is the text between popularity and assigned weight.
    jm=re.search(r"番人気\s+(.+?)\s+\d{2}(?:\.\d+)?\s*kg",s)
    out["jockey"]=jm.group(1).strip() if jm else None
    # class text between venue and finish, retained for future registered evaluator.
    if m:=re.search(r"\d{1,2}日\s+[^\s]+\s+(.*?)\s+\d+\s*着",s):
        out["race_class_text"]=m.group(1).strip()
    return out

def parse_race_card_detail(raw:bytes,content_type:str="")->Dict[str,Any]:
    decoded=_decode(raw,content_type)
    # Corner calls are separate <li> items; keep a separator so tag stripping
    # cannot concatenate "10","10","1","1" into the ambiguous "101011".
    decoded=re.sub(r'(<div class="corner_list">.*?</div>)',
                   lambda m:re.sub(r"</li>"," </li>",m.group(1)),decoded,flags=re.S)
    token_by_name={}
    for token,label in re.findall(r'<a[^>]+href=["\']/JRADB/accessU\.html\?CNAME=([^"\']+)["\'][^>]*>(.*?)</a>',decoded,re.I|re.S):
        name=re.sub(r"<[^>]+>","",html.unescape(label))
        name=re.sub(r"\s+","",name).strip()
        if name:token_by_name[name]=urllib.parse.unquote(token)

    # Capture current rider/trainer profile tokens directly from the current
    # official JRA race-card HTML. Horse-history tokens are historical and can
    # legitimately refer to a different rider/trainer; using them as the sole
    # lookup source caused current-person stats to resolve 0/N on live cards.
    def _person_token_map(page:str):
        out={}
        pat=r'<a([^>]*)>(.*?)</a>'
        for attrs,label in re.findall(pat,decoded,re.I|re.S):
            if page.lower() not in str(attrs).lower():
                continue
            token=None
            if "CNAME=" in attrs:
                tail=attrs.split("CNAME=",1)[1]
                token=re.split(r"[&\"'<>\s]+",tail,1)[0]
            if not token and re.search(r"doAction",attrs,re.I):
                m_action=re.search(
                    r"""doAction\(\s*['"]([^'"]+)['"]\s*,\s*['"]([^'"]+)['"]\s*\)""",
                    attrs,re.I
                )
                if m_action and page.lower()+".html" in m_action.group(1).lower():
                    token=m_action.group(2)
            if not token:
                continue
            token=urllib.parse.unquote(str(token))
            label_txt=re.sub(r"<[^>]+>","",html.unescape(label))
            key=re.sub(r"[▲△◇☆★\s]+","",label_txt).strip()
            if key and key not in out:
                out[key]=token
        return out
    jockey_token_by_name=_person_token_map("accessK")
    trainer_token_by_name=_person_token_map("accessC")
    table=None
    for t in _html_tables(decoded):
        if not t: continue
        h=[_norm(x) for x in t[0]]
        if "馬番" in h and any("馬名" in x for x in h) and any("前走" in x for x in h):
            table=t; break
    if table is None: raise ValueError("JRA_DETAIL_RUNNER_TABLE_NOT_FOUND")
    headers=[_norm(x) for x in table[0]]
    no_i=headers.index("馬番")
    identity_i=next(i for i,x in enumerate(headers) if "馬名" in x)
    person_i=next(i for i,x in enumerate(headers) if "性齢" in x and "騎手" in x)
    run_indices=[i for i,x in enumerate(headers) if x in {"前走","前々走","3走前","4走前"}]
    runners=[]
    for row in table[1:]:
        if no_i>=len(row):continue
        no=_num(row[no_i])
        if no is None or no<1 or no>18:continue
        ident=_parse_identity(row[identity_i] if identity_i<len(row) else "")
        person=_parse_current_person(row[person_i] if person_i<len(row) else "")
        frame_no=_num(row[0]) if len(row)>0 else None
        joined=" ".join(str(z or "") for z in row)
        status="CANCELLED" if ("出走取消" in joined or "競走除外" in joined) else "ACTIVE"
        recent=[]
        for i in run_indices:
            x=_parse_recent(row[i] if i<len(row) else "")
            if x:recent.append(x)
        cname=re.sub(r"\s+","",str(ident.get("horse_name") or "")).strip()
        jkey=re.sub(r"[▲△◇☆★\s]+","",str(person.get("jockey") or "")).strip()
        tkey=re.sub(r"[▲△◇☆★\s]+","",str(ident.get("trainer") or "")).strip()
        runners.append({"runner_id":str(no),"horse_no":no,"frame_no":frame_no,"status":status,
                        "horse_profile_token":token_by_name.get(cname),
                        "jockey_profile_token":jockey_token_by_name.get(jkey),
                        "trainer_profile_token":trainer_token_by_name.get(tkey),
                        **ident,**person,"recent_runs":recent})
    if not runners: raise ValueError("JRA_DETAIL_RUNNERS_EMPTY")
    weather=None; going=None; going_surface=None
    # Official markup: <span class="cap">天候</span><span class="txt">晴</span>
    # and <span class="cap">ダート</span><span class="txt">良</span>.
    mw=re.search(r'class="cap">\s*天候\s*</span>\s*<span class="txt">\s*([^<\s]+)',decoded) \
        or re.search(r"天候\s*[:：]?\s*([^\s<]+)",decoded)
    if mw: weather=mw.group(1)
    mgc=re.search(r'class="cap">\s*(芝|ダート|ダ)\s*</span>\s*<span class="txt">\s*(良|稍重|重|不良)',decoded) \
        or re.search(r"(芝|ダート|ダ)\s*[:：]?\s*(良|稍重|重|不良)",decoded)
    if mgc:
        going_surface=mgc.group(1); going=mgc.group(2)
    observed_context = parse_detail_race_context(raw, content_type)
    if observed_context:
        # Prefer the printed race context, but never erase an observed value
        # with an absent one.
        weather=observed_context["weather"] or weather
        if observed_context["going"]:
            going=observed_context["going"]
            going_surface=observed_context["surface"]
    out={"profile":PROFILE,"official":True,"production_fact_authority":True,"runner_count":len(runners),"runners":runners,
         "race_context":observed_context,
         "race_environment":{"weather":weather,"going":going,"going_surface":going_surface}}
    out["sha256"]=sha_obj({k:v for k,v in out.items() if k!="sha256"})
    return out

def fetch_and_enrich_race_card_detail(artifact:Dict[str,Any],prediction_cutoff:str,*,race_date:str,meeting_key:str,race_no:int)->Dict[str,Any]:
    raw,headers,final,tokens=_discover_and_fetch(race_date,meeting_key,race_no)
    spec={"source_id":"JRA-OFFICIAL-RACE-CARD-DETAIL","source_class":"OFFICIAL_JRA_RACE_CARD_DETAIL","authority":"JRA_OFFICIAL",
          "priority":125,"official":True,"required":False,"url":BASE+"/JRADB/accessD.html","extract":[]}
    snap,errs=snapshot_from_bytes(spec,raw,final_url=final,status_code=200,headers=headers,fetched_at=utcnow(),prediction_cutoff=prediction_cutoff)
    if snap.get("cutoff_relation")=="POST_CUTOFF":
        raise ValueError("JRA_DETAIL_POST_CUTOFF")
    if errs: raise ValueError("JRA_DETAIL_SNAPSHOT_ERROR:"+"|".join(errs))
    detail=parse_race_card_detail(raw,headers.get("content-type",""))
    detail["navigation_tokens_sha256"]=hashlib.sha256(str(tokens).encode()).hexdigest()
    detail["source_snapshot_sha256"]=snap["snapshot_sha256"]
    artifact["sources"]=list(artifact.get("sources") or [])+[snap]
    artifact["jra_official_race_card_detail"]=detail
    artifact["jra_official_race_card_detail_sha256"]=sha_obj(detail)
    try:
        from .jra_observed_context import bind_observed_context
    except ImportError:
        from jra_observed_context import bind_observed_context
    return bind_observed_context(artifact)


def runner_universes_from_detail(detail:Dict[str,Any])->Tuple[Dict[str,Any],Dict[str,Any]]:
    runners=[]
    for x in detail.get("runners") or []:
        name=str(x.get("horse_name") or "").strip()
        if not name: continue
        runners.append({
            "runner_id":str(x.get("runner_id") or x.get("horse_no")),
            "horse_no":int(x.get("horse_no")),
            "frame_no":x.get("frame_no"),
            "name":name,
            "canonical_name":re.sub(r"\s+","",name),
            "status":str(x.get("status") or "ACTIVE"),
            "sex":x.get("sex"),
            "age":x.get("age"),
            "assigned_weight":x.get("assigned_weight"),
            "jockey":x.get("jockey"),
            "body_weight":x.get("current_body_weight"),
            "body_weight_change":x.get("current_body_weight_change"),
            "source":"JRA_OFFICIAL_JRADB_DETAIL",
        })
    if not runners:
        raise ValueError("JRA_DETAIL_RUNNER_UNIVERSE_EMPTY")
    declared={
        "profile":"KM-JRA-OFFICIAL-DETAIL-RUNNER-UNIVERSE-v1.0-20260926",
        "source_id":"JRA-OFFICIAL-RACE-CARD-DETAIL",
        "source_snapshot_sha256":detail.get("source_snapshot_sha256"),
        "universe_type":"DECLARED",
        "runner_count":len(runners),
        "runners":runners,
    }
    declared["runner_universe_sha256"]=sha_obj(declared)
    active=[x for x in runners if x.get("status")=="ACTIVE"]
    active_u={**declared,"universe_type":"ACTIVE","runner_count":len(active),"runners":active}
    active_u["runner_universe_sha256"]=sha_obj(active_u)
    return declared,active_u

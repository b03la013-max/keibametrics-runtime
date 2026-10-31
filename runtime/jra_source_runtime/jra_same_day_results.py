from __future__ import annotations

import http.cookiejar
import itertools
import re
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Tuple

if __package__:
    from .source_acquisition import _decode, _html_tables, _html_text, sha_obj, snapshot_from_bytes, utcnow
    from .jra_race_card_detail import _calendar_url, _fetch, _post, _date8
else:
    try:
        from jra_source_runtime.source_acquisition import _decode, _html_tables, _html_text, sha_obj, snapshot_from_bytes, utcnow
        from jra_source_runtime.jra_race_card_detail import _calendar_url, _fetch, _post, _date8
    except ModuleNotFoundError as exc:
        if exc.name != "jra_source_runtime":
            raise
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

def finish_groups_and_top3_orders(runners:List[Dict[str,Any]])->Dict[str,Any]:
    """Preserve official competition ranks, including a tie crossing third.

    A third-place tie has ranks 1, 2, 3, 3, 5, not four distinct ranks.
    Enumerating the permissible orders does not choose a preferred tied horse.
    This helper deliberately does not change the historic parsed SOURCE body.
    """
    groups={};seen=set()
    for row in runners:
        rank=row.get("finish");number=row.get("horse_no")
        if (type(rank) is not int or rank<1 or type(number) is not int
                or not 1<=number<=18 or number in seen):
            raise ValueError("JRA_OFFICIAL_FINISH_GROUP_INVALID")
        if str(row.get("runner_id",number))!=str(number):
            raise ValueError("JRA_OFFICIAL_FINISH_RUNNER_ID_MISMATCH")
        seen.add(number);groups.setdefault(rank,[]).append(number)
    orders=[[]];next_rank=1
    for rank,numbers in sorted(groups.items()):
        if len(orders[0])>=3:break
        if rank!=next_rank:
            raise ValueError("JRA_OFFICIAL_TOP3_RANK_GROUP_INCOMPLETE")
        numbers=sorted(numbers)
        take=min(len(numbers),3-len(orders[0]))
        orders=[prefix+list(p) for prefix in orders
                for p in itertools.permutations(numbers,take)]
        next_rank+=len(numbers)
    if not orders or len(orders[0])!=3:
        raise ValueError("JRA_OFFICIAL_TOP3_RANK_GROUP_INCOMPLETE")
    return {"finish_groups":[{"finish":rank,"horse_numbers":sorted(numbers)}
                              for rank,numbers in sorted(groups.items())],
            "top3_orders":sorted(orders),"dead_heat":len(orders)>1}

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
    non_finishers=[]
    statuses={"取消":"CANCELLED", "除外":"EXCLUDED", "中止":"DID_NOT_FINISH", "失格":"DISQUALIFIED"}
    for row in chosen[1:]:
        if ni is None or ni>=len(row): continue
        no=_int(row[ni])
        finish_label=_norm(row[fi]) if fi is not None and fi<len(row) else ""
        finish=int(finish_label) if re.fullmatch(r"\d+",finish_label) else None
        if no is None: continue
        name=_norm(row[mi] if mi is not None and mi<len(row) else "")
        if finish is None:
            status=statuses.get(finish_label)
            if status:
                non_finishers.append({"horse_no":no,"runner_id":str(no),"horse_name":name,
                                      "finish_status":status,"raw_finish_label":finish_label})
            continue
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
        "non_finishers":non_finishers,
        "scheduled_post_hhmm":scheduled_post,"race_environment":env,
        "lap_table":lap_table,"corner_table":corner_table,
    }
    out["sha256"]=sha_obj({k:v for k,v in out.items() if k!="sha256"})
    return out

class OfficialResultNavigationError(ValueError):
    def __init__(self, code, stage, *, client=None):
        super().__init__(code)
        self.error_code = code
        self.first_failed_stage = stage
        self.official_navigation = list(getattr(client, 'result_navigation', []))
        self.diagnostic = {'navigation':[{k:v for k,v in row.items() if k!='fetched_at'}
                                         for row in self.official_navigation]}


def _navigation_observation(client, stage, *, token=None):
    import hashlib
    record = {**dict(client.last_response), 'stage': stage,
              'method': 'POST' if token is not None else 'GET'}
    if token is not None:
        record['cname_sha256'] = hashlib.sha256(token.encode()).hexdigest()
    client.result_navigation.append(record)


def _result_post(client, token, referer):
    """The existing official client/session, bound to accessS rather than cards."""
    if client.last_response.get('response_url') != referer:
        raise OfficialResultNavigationError('JRA_RESULT_SESSION_REFERER_MISMATCH',
                                            'RESULT_NAVIGATION', client=client)
    client.post('/JRADB/accessS.html', token)
    final = client.last_response.get('response_url')
    parsed = urllib.parse.urlsplit(final or '')
    if (parsed.scheme != 'https' or parsed.hostname != 'www.jra.go.jp'
            or parsed.path != '/JRADB/accessS.html' or client.last_raw is None):
        raise OfficialResultNavigationError('JRA_RESULT_RESPONSE_ENDPOINT_MISMATCH',
                                            'RESULT_NAVIGATION', client=client)
    return final, client.last_raw, client.last_headers


def _open_day(race_date:str,meeting_key:str):
    if __package__:
        from .jra_pedigree_harvest import _Client, _day_navigation
        from .jra_race_day_resolver import VENUES
    else:
        from jra_pedigree_harvest import _Client, _day_navigation
        from jra_race_day_resolver import VENUES
    import time
    d = _date8(race_date)
    key = str(meeting_key or '')
    if (not re.fullmatch(r'\d{10}', key) or key[:2] not in VENUES
            or key[2:6] != d[:4] or int(key[6:8]) < 1 or int(key[8:10]) < 1):
        raise OfficialResultNavigationError('JRA_MEETING_KEY_INVALID', 'RESULT_INPUT')
    client = _Client(delay=1.0, deadline_monotonic=time.monotonic()+180,
                     stop_on_access_denied=True, referer_chain=True)
    client.result_navigation = []
    # _day_navigation already follows only the observed official result entry,
    # archive form, published month/checksum, and requested-day tokens.
    # Record every successful request without inventing tokens or an archive URL.
    original_get, original_post = client.get, client.post
    def get(path):
        try: result = original_get(path)
        except Exception as exc:
            exc.first_failed_stage = 'RESULT_CALENDAR'
            raise
        _navigation_observation(client, 'RESULT_CALENDAR')
        return result
    def post(path, token):
        stage = ('RESULT_ARCHIVE' if token.startswith('pw01skl') else
                 'RESULT_DAY' if token.startswith('pw01srl') else
                 'RESULT_DETAIL' if token.startswith('pw01sde') else 'RESULT_ENTRY')
        if path != '/JRADB/accessS.html':
            raise OfficialResultNavigationError('JRA_RESULT_ENDPOINT_INVALID',stage,client=client)
        try: result = original_post(path,token)
        except Exception as exc:
            exc.first_failed_stage = stage
            raise
        _navigation_observation(client,stage,token=token)
        return result
    client.get, client.post = get, post
    try:
        page, entry, days, _ = _day_navigation(client,race_date,'results')
    except Exception as exc:
        aliases = {'JRA_HARVEST_ENTRY_TOKEN_NOT_FOUND':'JRA_RESULT_ENTRY_TOKEN_NOT_OBSERVED',
                   'JRA_HARVEST_ARCHIVE_ENTRY_NOT_OBSERVED':'JRA_RESULT_ARCHIVE_SELECTION_REQUIRED',
                   'JRA_HARVEST_ARCHIVE_FORM_NOT_OBSERVED':'JRA_RESULT_ARCHIVE_FORM_NOT_OBSERVED'}
        if str(exc) in aliases:
            raise OfficialResultNavigationError(aliases[str(exc)],'RESULT_NAVIGATION',client=client) from exc
        if not hasattr(exc,'first_failed_stage'):exc.first_failed_stage='RESULT_NAVIGATION'
        exc.official_navigation=list(client.result_navigation)
        exc.diagnostic={'navigation':[{k:v for k,v in row.items() if k!='fetched_at'}
                                      for row in client.result_navigation]}
        raise
    expected = r'pw01srl\d{2}'+re.escape(key+d)+r'/[0-9A-Fa-f]{2}'
    target = [token for token in days if re.fullmatch(expected,token)]
    if len(target) != 1:
        code = 'JRA_RESULT_MEETING_KEY_MISMATCH' if days else 'JRA_RESULT_DAY_TOKEN_NOT_OBSERVED'
        raise OfficialResultNavigationError(code,'RESULT_DAY_SELECTION',client=client)
    day_html = client.post(page,target[0])
    if not re.search(r'pw01sde\d{2}'+re.escape(key)+r'\d{2}'+d+r'/[0-9A-Fa-f]{2}',day_html):
        raise OfficialResultNavigationError('JRA_RESULT_DAY_HTML_UNRECOGNIZED','RESULT_DAY_BODY',client=client)
    return client, client.last_response['response_url'], day_html, key, d


def validate_result_identity(raw, content_type, key, day, race_no):
    if __package__:
        from .jra_race_day_resolver import VENUES
    else:
        from jra_race_day_resolver import VENUES
    from bs4 import BeautifulSoup
    decoded = _decode(raw,content_type)
    soup = BeautifulSoup(decoded,'html.parser')
    header_nodes = soup.select('.race_header')
    date_pattern = (r'(\d{4})年(\d{1,2})月(\d{1,2})日[（(][^）)]*[）)]\s*'
                    r'(\d+)回(札幌|函館|福島|新潟|東京|中山|中京|京都|阪神|小倉)(\d+)日')
    if header_nodes:
        # JRA prints the race number as an image alt in this same header;
        # global text flattening drops it and can mix footer/navigation races.
        if len(header_nodes)!=1:
            raise OfficialResultNavigationError('JRA_RESULT_PRINTED_IDENTITY_NOT_OBSERVED','RESULT_DETAIL_IDENTITY')
        header=header_nodes[0]
        dates=header.select('.date_line .cell.date')
        numbers=header.select('.race_number')
        date=re.fullmatch(date_pattern,dates[0].get_text(' ',strip=True)) if len(dates)==1 else None
        labels=([x.get('alt') for x in numbers[0].select('img[alt]')] if len(numbers)==1 else [])
        number=re.fullmatch(r'(\d+)レース',labels[0]) if len(labels)==1 else None
        if not date or not number:
            raise OfficialResultNavigationError('JRA_RESULT_PRINTED_IDENTITY_NOT_OBSERVED','RESULT_DETAIL_IDENTITY')
        y,m,d,meeting,venue,meeting_day=date.groups();rn=number[1]
    else:
        # Retain legacy textual headers, only before the result table. Do not
        # borrow a target identity from another race in the page footer.
        prefix=re.split(r'<table\b',decoded,maxsplit=1,flags=re.I)[0]
        heads=re.findall(date_pattern+r'\s+(\d+)レース',_html_text(prefix))
        if len(set(heads))!=1:
            raise OfficialResultNavigationError('JRA_RESULT_PRINTED_IDENTITY_NOT_OBSERVED','RESULT_DETAIL_IDENTITY')
        y,m,d,meeting,venue,meeting_day,rn=heads[0]
    actual = (f'{int(y):04d}{int(m):02d}{int(d):02d}',venue,int(meeting),int(meeting_day),int(rn))
    expected = (day,VENUES[key[:2]][1],int(key[6:8]),int(key[8:10]),int(race_no))
    if actual != expected:
        raise OfficialResultNavigationError('JRA_RESULT_PRINTED_IDENTITY_MISMATCH','RESULT_DETAIL_IDENTITY')
    return {'race_date':f'{day[:4]}-{day[4:6]}-{day[6:]}','meeting_key':key,
            'venue':venue,'meeting_no':int(meeting),'meeting_day':int(meeting_day),'race_no':int(rn)}


def _fetch_race(opener,referer:str,day_html:str,key:str,d:str,race_no:int,prediction_cutoff:str):
    prefix="pw01sde01"+key+f"{int(race_no):02d}"+d
    m=re.search(r"("+re.escape(prefix)+r"/[0-9A-Fa-f]{2})",day_html)
    if not m:
        raise ValueError(f"JRA_RESULT_RACE_TOKEN_NOT_FOUND:{race_no}")
    final,raw,headers=_result_post(opener,m.group(1),referer)
    fetched=opener.last_response.get("fetched_at") or utcnow()
    validate_result_identity(raw,headers.get("content-type",""),key,d,race_no)
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

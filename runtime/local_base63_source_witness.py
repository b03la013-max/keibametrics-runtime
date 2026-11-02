"""Offline independent SOURCE -> 63 component -> 9 base-index witness.

This audit reads the original gzip HTML and separately parses and calculates
the existing governed rules. It imports no production evidence compiler or
scoring helper. It grants no licence, signature, Owner or Consumer authority.
Arithmetic agreement, observation quality and predictive validity are separate.
"""
from __future__ import annotations

import base64
from collections import Counter
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal, localcontext, ROUND_HALF_EVEN
import gzip
import hashlib
from html.parser import HTMLParser
import io
import json
import re
import unicodedata
from urllib.parse import urlsplit, parse_qs

PROFILE="KM-LOCAL-BASE63-INDEPENDENT-SOURCE-WITNESS-v1"
BASE=("HPI-L","CFIg-L","RFIg-L","BVIg-L","JTI-L","CSI-L","BWI-L","DCR","NCI")
D=Decimal
NEUTRAL=D(52)
RECENCY=tuple(map(D,(".30",".25",".20",".15",".10")))
EPSILON=D(".000002")
MAX_RAW=8_000_000

def digest(data):
    return hashlib.sha256(data).hexdigest()

def canon_hash(value):
    return digest(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode())

def compact(value):
    return re.sub(r"\s+","",unicodedata.normalize("NFKC",str(value or "")))

def number(value):
    if value is None:return None
    v=D(str(value))
    if not v.is_finite():raise ValueError("NON_FINITE_SOURCE_NUMBER")
    return v

def q(value):
    return float(number(value).quantize(D(".000001"),rounding=ROUND_HALF_EVEN))

def clip(value):
    return max(D(0),min(D(100),number(value)))

def avg(values):
    xs=[number(x) for x in values if x is not None]
    return sum(xs,D(0))/len(xs) if xs else None

def spread(values):
    xs=[number(x) for x in values if x is not None]
    if len(xs)<2:return None
    mean=avg(xs)
    return (sum(((x-mean)**2 for x in xs),D(0))/len(xs)).sqrt()

def decay_mean(values):
    pairs=[(number(v),RECENCY[i]) for i,v in enumerate(values[:5]) if v is not None]
    return sum((v*w for v,w in pairs),D(0))/sum((w for _,w in pairs),D(0)) if pairs else None

def finish(rank,size):
    return clip(D(100)*(size-rank)/(size-1)) if rank is not None and size and size>1 else None

def coverage(n,den):
    return min(D(1),D(n)/D(den))

def jockey(value):
    return re.split(r"[（(]",compact(value))[0].translate(str.maketrans("","","☆▲△"))

def grade(value):
    t=compact(value).upper()
    rank_patterns=[(r"(?<![A-Z0-9])(?:JPN1|JPNI|G1|GI|S1|I)(?![A-Z0-9])",100),
        (r"(?<![A-Z0-9])(?:JPN2|JPNII|G2|GII|S2)(?![A-Z0-9])",96),
        (r"(?<![A-Z0-9])(?:JPN3|JPNIII|G3|GIII|S3)(?![A-Z0-9])",92)]
    rank_patterns += [(r"オープン|OPEN|A1",88),(r"A2",84),(r"A3",80),
        (r"3勝クラス|B1",78),(r"2勝クラス|B2",74),(r"1勝クラス|B3",70),
        (r"C1",64),(r"C2",58),(r"C3",52),(r"未勝利|新馬",54)]
    hits=[v for pat,v in rank_patterns if re.search(pat,t)]
    if hits:return D(max(hits)),"PARSED_CLASS_ORDINAL"
    tokens=re.findall(r"[ABC]\d",t)
    if tokens:
        values={"A1":88,"A2":84,"A3":80,"B1":78,"B2":74,"B3":70,"C1":64,"C2":58,"C3":52}
        return avg([values.get(x,52) for x in tokens]),"PARSED_COMPOSITE_CLASS_ORDINAL"
    return NEUTRAL,"CLASS_UNRESOLVED_CANONICAL_NEUTRAL"

def seconds(value):
    m=re.search(r"(\d+):(\d{2})\.(\d)",str(value))
    if m:return D(m[1])*60+D(m[2])+D(m[3])/10
    m=re.search(r"(?<!\d)(\d{2,3})\.(\d)(?!\d)",str(value))
    return D(m[1])+D(m[2])/10 if m else None

def interval_score(days):
    if days is None:return None
    if 14<=days<=42:return D(85)
    if 8<=days<=70:return D(72)
    if 71<=days<=120:return D(60)
    return D(58 if days<8 else 52)

def going_group(value):
    return {"良":"DRY","稍重":"INTERMEDIATE","重":"WET","不良":"WET"}.get(compact(value),"UNKNOWN")

def going_matches(a,b):
    a,b=going_group(a),going_group(b)
    return "UNKNOWN" not in (a,b) and (a==b or {a,b}<={"WET","INTERMEDIATE"})

def same_venue(a,b):
    return bool(compact(b) and compact(b) in compact(a).replace("ナ",""))

class OriginalTables(HTMLParser):
    """Own HTML table traversal; no production extractor code is called."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[];self.tables=[];self.text=[];self.headings=[];self.heading=None
    def handle_starttag(self,tag,attrs):
        if tag in ("h3","h4"):self.heading=[tag,[]]
        if tag=="table":self.stack.append({"rows":[],"row":None,"cell":None})
        elif self.stack and tag=="tr":self.stack[-1]["row"]=[]
        elif self.stack and tag in ("td","th"):self.stack[-1]["cell"]=[]
        elif tag=="br":self.handle_data(" ")
    def handle_data(self,data):
        self.text.append(data)
        if self.heading is not None:self.heading[1].append(data)
        for frame in self.stack:
            if frame["cell"] is not None:frame["cell"].append(data)
    def handle_endtag(self,tag):
        if self.heading is not None and self.heading[0]==tag:
            self.headings.append([tag," ".join(" ".join(self.heading[1]).split())]);self.heading=None
        if not self.stack:return
        current=self.stack[-1]
        if tag in ("td","th") and current["cell"] is not None:
            if current["row"] is not None:current["row"].append(" ".join(" ".join(current["cell"]).split()))
            current["cell"]=None
        elif tag=="tr" and current["row"] is not None:
            if current["row"]:current["rows"].append(current["row"])
            current["row"]=None
        elif tag=="table":self.tables.append(self.stack.pop()["rows"])

def original_card(source,request):
    if request.get("family_id")!="LOCAL" or request.get("venue_id")!="FNB":
        raise ValueError("FNB_LOCAL_ARCHIVAL_WITNESS_SCOPE_REQUIRED")
    cards=[c for c in source.get("sources",[]) if isinstance(c,dict) and c.get("official") is True
           and c.get("source_class")=="OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT"]
    if len(cards)!=1:raise ValueError("ONE_OFFICIAL_ORIGINAL_CARD_REQUIRED")
    card=cards[0]
    data=base64.b64decode(card["raw_gzip_b64"],validate=True)
    with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:raw=stream.read(MAX_RAW+1)
    if not raw or len(raw)>MAX_RAW:raise ValueError("ORIGINAL_CARD_BYTE_LIMIT")
    if digest(raw)!=card.get("raw_sha256"):raise ValueError("ORIGINAL_RAW_SHA_MISMATCH")
    if canon_hash({k:v for k,v in card.items() if k!="snapshot_sha256"})!=card.get("snapshot_sha256"):
        raise ValueError("ORIGINAL_CARD_SNAPSHOT_SHA_MISMATCH")
    for field in ("requested_url","final_url"):
        url=urlsplit(card[field]);query=parse_qs(url.query)
        if (url.hostname!="www.keiba.go.jp" or query.get("k_babaCode")!=["19"]
            or query.get("k_raceNo")!=[str(request["race_no"])]
            or query.get("k_raceDate")!=[request["race_date"].replace("-","/")]):
            raise ValueError("ORIGINAL_CARD_OFFICIAL_IDENTITY_MISMATCH")
    try:text=raw.decode("utf-8")
    except UnicodeDecodeError:text=raw.decode("cp932")
    parser=OriginalTables();parser.feed(text)
    return card,raw,parser

def official_context(parser,request):
    heads=[compact(v) for tag,v in parser.headings if tag=="h4"]
    identity=[re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日.*?船橋第(\d{1,2})競走(\d{1,2}):(\d{2})発走",h) for h in heads]
    identity=[m for m in identity if m]
    if len(identity)!=1:raise ValueError("OFFICIAL_RAW_RACE_IDENTITY_HEADER_AMBIGUOUS")
    h=identity[0];raw_day=date(int(h[1]),int(h[2]),int(h[3]))
    if raw_day.isoformat()!=request["race_date"].replace("/","-") or int(h[4])!=request["race_no"]:
        raise ValueError("OFFICIAL_RAW_RACE_DATE_OR_NUMBER_CONFLICT")
    raw_post=datetime.combine(raw_day,datetime.min.time()).replace(hour=int(h[5]),minute=int(h[6]),tzinfo=timezone(timedelta(hours=9)))
    if request.get("scheduled_post_at"):
        expected=datetime.fromisoformat(request["scheduled_post_at"].replace("Z","+00:00"))
        if expected.tzinfo is None or expected!=raw_post:raise ValueError("OFFICIAL_RAW_SCHEDULED_POST_CONFLICT")
    text=compact(" ".join(parser.text))
    matches=re.findall(r"(ダート|芝)(\d{3,4})m\(([左右])\).*?天候[:：](.*?)馬場[:：](不良|稍重|良|重)",text)
    if len(matches)!=1:raise ValueError("OFFICIAL_CONTEXT_HEADER_AMBIGUOUS")
    surface,distance,direction,weather,going=matches[0]
    titles=[v for tag,v in parser.headings if tag=="h3" and grade(v)[1]!="CLASS_UNRESOLVED_CANONICAL_NEUTRAL"]
    context={"venue":request["venue_id"],"distance":int(distance),
        "direction":"LEFT" if direction=="左" else "RIGHT","surface":"DIRT" if surface=="ダート" else "TURF",
        "weather":weather.strip("、,;；:"),"going":going,"race_titles":titles,
        "race_date":raw_day.isoformat(),"race_no":int(h[4]),"scheduled_post_at":raw_post.isoformat(),
        "proof":"ORIGINAL_HTML_RACE_HEADER_NOT_REQUEST_ALIAS_INFERENCE"}
    race=request.get("race") or {}
    requested_distance=race.get("distance_m") or race.get("distance")
    if requested_distance is not None and int(requested_distance)!=context["distance"]:
        raise ValueError("OFFICIAL_REQUEST_DISTANCE_CONFLICT")
    if race.get("direction") and race["direction"]!=context["direction"]:
        raise ValueError("OFFICIAL_REQUEST_DIRECTION_CONFLICT")
    if race.get("surface") and str(race["surface"]).upper()!=context["surface"]:
        raise ValueError("OFFICIAL_REQUEST_SURFACE_CONFLICT")
    if race.get("class") and (grade(race["class"])[1]=="CLASS_UNRESOLVED_CANONICAL_NEUTRAL" or
            not any(grade(x)[0]==grade(race["class"])[0] for x in titles)):
        raise ValueError("OFFICIAL_REQUEST_CLASS_CONFLICT")
    return context

def source_snapshot_audit(source):
    """Hash original snapshots and as-of metadata; never acquire new bytes."""
    verified=[]
    freeze=datetime.fromisoformat(source["source_freeze_at"].replace("Z","+00:00"))
    if freeze.tzinfo is None:raise ValueError("SOURCE_FREEZE_TIMEZONE_REQUIRED")
    for s in source["sources"]:
        if "raw_gzip_b64" not in s:raise ValueError("SOURCE_ORIGINAL_SNAPSHOT_MISSING")
        with gzip.GzipFile(fileobj=io.BytesIO(base64.b64decode(s["raw_gzip_b64"],validate=True))) as stream:
            raw=stream.read(MAX_RAW+1)
        if len(raw)>MAX_RAW:raise ValueError("SOURCE_ORIGINAL_SNAPSHOT_BYTE_LIMIT")
        if digest(raw)!=s.get("raw_sha256"):raise ValueError("SOURCE_ORIGINAL_RAW_SHA_MISMATCH")
        if canon_hash({k:v for k,v in s.items() if k!="snapshot_sha256"})!=s.get("snapshot_sha256"):
            raise ValueError("SOURCE_ORIGINAL_SNAPSHOT_SHA_MISMATCH")
        stamp=datetime.fromisoformat(s["fetched_at"].replace("Z","+00:00"))
        if stamp.tzinfo is None:raise ValueError("SOURCE_SNAPSHOT_TIMEZONE_REQUIRED")
        cutoff=datetime.fromisoformat(source["prediction_cutoff"].replace("Z","+00:00"))
        verified.append({"source_id":s["source_id"],"source_class":s.get("source_class"),
            "snapshot_sha256":s["snapshot_sha256"],"raw_sha256":digest(raw),"raw_bytes":len(raw),"fetched_at":s["fetched_at"],
            "observed_before_source_freeze":stamp<=freeze,"observed_before_prediction_cutoff":stamp<cutoff,
            "time_grade":"AT_OR_BEFORE_SOURCE_FREEZE" if stamp<=freeze else "AFTER_FREEZE_BEFORE_CUTOFF" if stamp<cutoff else "AFTER_CUTOFF"})
    known={(x["source_id"],x["snapshot_sha256"]) for x in verified}
    for key,value in (source.get("normalized_evidence") or {}).items():
        if isinstance(value,dict) and value.get("source_id"):
            if (value["source_id"],value.get("snapshot_sha256")) not in known:
                raise ValueError("NORMALIZED_EVIDENCE_SNAPSHOT_REF_MISMATCH")
    return verified

def management_source_inputs(source,request):
    """Derive DCR source-presence/count facts from original official pages.

    Normalized keys are checked against the independently parsed page set;
    adding a correctly self-hashed metadata key cannot create a prior result
    or an official odds table that is absent from the real Raw bytes.
    """
    prior={};odds=[];evidence=[]
    for snapshot in source.get("sources",[]):
        kind=snapshot.get("source_class")
        if kind not in {"OFFICIAL_SAME_DAY_RACE_RESULT_PASSING_ORDER","OFFICIAL_ACTIVE_BETTING_UNIVERSE"}:continue
        if snapshot.get("official") is not True:raise ValueError("DCR_SOURCE_NOT_OFFICIAL")
        with gzip.GzipFile(fileobj=io.BytesIO(base64.b64decode(snapshot["raw_gzip_b64"],validate=True))) as stream:
            raw=stream.read(MAX_RAW+1)
        if len(raw)>MAX_RAW or digest(raw)!=snapshot.get("raw_sha256"):raise ValueError("DCR_SOURCE_RAW_HASH_OR_LIMIT")
        parser=OriginalTables()
        try:parser.feed(raw.decode("utf-8"))
        except UnicodeDecodeError:parser.feed(raw.decode("cp932"))
        heads=[compact(v) for tag,v in parser.headings if tag=="h4"]
        found=[re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日.*?船橋第(\d{1,2})競走",t) for t in heads]
        found=[m for m in found if m]
        if len(found)!=1:raise ValueError("DCR_ORIGINAL_PAGE_RACE_IDENTITY_AMBIGUOUS")
        m=found[0];day=date(int(m[1]),int(m[2]),int(m[3])).isoformat();race_no=int(m[4])
        if day!=request["race_date"]:raise ValueError("DCR_SOURCE_WRONG_DAY")
        endpoint="RaceMarkTable" if kind=="OFFICIAL_SAME_DAY_RACE_RESULT_PASSING_ORDER" else "OddsTanFuku"
        for field in ("requested_url","final_url"):
            url=urlsplit(snapshot[field]);query=parse_qs(url.query)
            if (url.hostname!="www.keiba.go.jp" or not url.path.endswith("/"+endpoint)
                    or query.get("k_babaCode")!=["19"] or query.get("k_raceDate")!=[day.replace("-","/")]
                    or query.get("k_raceNo")!=[str(race_no)]):
                raise ValueError("DCR_ORIGINAL_PAGE_URL_IDENTITY_MISMATCH")
        item={"source_id":snapshot["source_id"],"snapshot_sha256":snapshot["snapshot_sha256"],
            "raw_sha256":digest(raw),"race_date":day,"race_no":race_no,"source_class":kind}
        if kind=="OFFICIAL_SAME_DAY_RACE_RESULT_PASSING_ORDER":
            if not 1<=race_no<request["race_no"]:raise ValueError("DCR_CURRENT_OR_FUTURE_RESULT_FORBIDDEN")
            tables=[t for t in parser.tables if t and {"着順","馬番","馬名"}<={compact(c) for c in t[0]}]
            if len(tables)!=1 or len(tables[0])<2:raise ValueError("DCR_OFFICIAL_RESULT_TABLE_MISSING")
            column=[compact(x) for x in tables[0][0]].index("着順")
            if not any(len(row)>column and re.fullmatch(r"\d+",compact(row[column])) for row in tables[0][1:]):
                raise ValueError("DCR_OFFICIAL_RESULT_FINISHES_MISSING")
            if race_no in prior:raise ValueError("DCR_DUPLICATE_PRIOR_RESULT_SOURCE")
            prior[race_no]=item
        else:
            if race_no!=request["race_no"]:raise ValueError("DCR_ODDS_WRONG_RACE")
            tables=[t for t in parser.tables if t and "馬番" in [compact(c) for c in t[0]]
                and any("単勝" in compact(c) for c in t[0]) and any("複勝" in compact(c) for c in t[0])]
            if len(tables)!=1 or len(tables[0])<2:raise ValueError("DCR_OFFICIAL_ODDS_TABLE_MISSING")
            col=[compact(x) for x in tables[0][0]].index("馬番")
            ids=[compact(row[col]) for row in tables[0][1:] if len(row)>col and re.fullmatch(r"\d+",compact(row[col]))]
            if not ids or len(ids)!=len(set(ids)):raise ValueError("DCR_ODDS_RUNNER_ROWS_INVALID")
            expected={str(x["runner_id"]) for x in request["runners"]}
            if not expected<=set(ids):raise ValueError("DCR_ODDS_CURRENT_ACTIVE_IDS_MISSING")
            item["observed_odds_runner_ids"]=ids;odds.append(item)
        evidence.append(item)
    if len(odds)>1:raise ValueError("DCR_MULTIPLE_OFFICIAL_ODDS_SNAPSHOTS")
    normalized=source.get("normalized_evidence") or {}
    keys={int(m[1]):(key,value) for key,value in normalized.items()
          if (m:=re.fullmatch(r"same_day_r(\d+)_result_tables",key))}
    # Count key spellings too: r1/r01 aliases must not count as two sources.
    key_count=sum(bool(re.fullmatch(r"same_day_r\d+_result_tables",key)) for key in normalized)
    if set(keys)!=set(prior) or key_count!=len(prior):raise ValueError("DCR_NORMALIZED_PRIOR_RESULT_SET_DIFFERS_FROM_RAW")
    for n,(_,value) in keys.items():
        if (not isinstance(value,dict) or value.get("source_id")!=prior[n]["source_id"]
                or value.get("snapshot_sha256")!=prior[n]["snapshot_sha256"]):
            raise ValueError("DCR_NORMALIZED_PRIOR_RESULT_REF_DIFFERS_FROM_RAW")
    od=normalized.get("odds_tables")
    if isinstance(od,dict)!=bool(odds):raise ValueError("DCR_NORMALIZED_ODDS_PRESENCE_DIFFERS_FROM_RAW")
    if odds and (od.get("source_id")!=odds[0]["source_id"] or od.get("snapshot_sha256")!=odds[0]["snapshot_sha256"]):
        raise ValueError("DCR_NORMALIZED_ODDS_REF_DIFFERS_FROM_RAW")
    return {"prior_race_numbers":sorted(prior),"prior_result_count":len(prior),
        "odds_source_present":bool(odds),"independently_raw_parsed_sources":evidence,
        "normalized_key_semantics_match_raw":True}

def history_descriptor(text):
    text=unicodedata.normalize("NFKC",str(text)).strip()
    m=re.match(r"(\d+)\s+(\d{2})\.(\d{2})\.(\d{2})\s+(\S+)\s+(\d+)頭\s+(\S+)\s+(.+?)\s+(\d+)番$",text)
    if not m:return None
    course=m[8];distance=re.search(r"(\d{3,4})$",course)
    return {"finish":int(m[1]),"date":date(2000+int(m[2]),int(m[3]),int(m[4])),"going":m[5],
        "field_size":int(m[6]),"venue":m[7],"course":course,"horse_no":int(m[9]),
        "distance":int(distance[1]) if distance else None,"surface":"TURF" if "芝" in course else "DIRT",
        "direction":"LEFT" if "左" in course else "RIGHT" if "右" in course else "UNKNOWN","raw_descriptor":text}

def parse_original_runners(parser,source,request):
    candidates=[t for t in parser.tables if any("競走馬" in row for row in t)]
    if not candidates:raise ValueError("ORIGINAL_MAIN_TABLE_NOT_FOUND")
    rows=max(candidates,key=len)
    starts=[]
    for i,row in enumerate(rows):
        if len(row)<2 or not re.fullmatch(r"\d{1,2}",row[0].strip()):continue
        off=3 if len(row)>2 and re.fullmatch(r"\d{1,2}",row[1].strip()) else 2
        name=row[off-1]
        if compact(name) not in ("","競走馬","馬名","前走回"):starts.append((i,off))
    runners={}
    for n,(at,off) in enumerate(starts):
        stop=starts[n+1][0] if n+1<len(starts) else len(rows)
        group=rows[at:stop]
        if len(group)<5:raise ValueError("ORIGINAL_RUNNER_ROWS_INCOMPLETE")
        primary,meta,blood,content,margins=group[:5]
        rid=str(int(primary[off-2]));recent=[]
        for i,desc in enumerate(primary[-5:]):
            h=history_descriptor(desc)
            if h is None:continue
            h["race_name"]=meta[-5:][i]
            h["class_score"],h["class_state"]=grade(h["race_name"])
            ride=unicodedata.normalize("NFKC",blood[-5:][i])
            m=re.match(r"(\d+)人\s+(\d{3,4})\s+(.+?)\s+(\d+(?:\.\d+)?)$",ride)
            h.update(popularity=int(m[1]) if m else None,body_weight=int(m[2]) if m else None,
                     jockey=jockey(m[3]) if m else "",carried_weight=D(m[4]) if m else None)
            ct=unicodedata.normalize("NFKC",content[-5:][i])
            pos=re.search(r"(?<!\d)(\d+(?:-\d+){1,5})(?!\d)",ct)
            h["positions"]=[int(x) for x in pos[1].split("-")] if pos else []
            h["time_seconds"]=seconds(ct)
            margin=re.match(r"(\d+(?:\.\d+)?)\s+(.+)$",unicodedata.normalize("NFKC",margins[-5:][i]))
            h["margin"]=D(margin[1]) if margin else None
            h["finish_score"]=finish(h["finish"],h["field_size"])
            h["raw_cells"]={"descriptor":desc,"race_name":h["race_name"],"ride":ride,"content":ct,"margin":margins[-5:][i]}
            recent.append(h)
        load=re.search(r"\d+(?:\.\d+)?",unicodedata.normalize("NFKC",meta[3]))
        weight=re.search(r"(\d{3,4})\s*\(([+-]?\d+)\)",unicodedata.normalize("NFKC",blood[2]))
        runners[rid]={"runner_id":rid,"horse_no":int(rid),"name":primary[off-1],
            "jockey":jockey(primary[off]),"load":D(load[0]) if load else None,
            "body_weight":int(weight[1]) if weight else None,"body_weight_change":int(weight[2]) if weight else None,
            "sire":blood[0],"dam":content[0],"damsire":margins[0],"trainer":blood[1],
            "history":recent,"original_table_rows":group[:5]}
    active=(source.get("active_runner_universe") or source.get("official_runner_universe") or {}).get("runners") or []
    if active:
        ids={str(x.get("runner_id") or x.get("horse_no")) for x in active}
        if ids-set(runners):raise ValueError("ORIGINAL_ACTIVE_IDS_NOT_FOUND")
        runners={k:v for k,v in runners.items() if k in ids}
    expected={str(x["runner_id"]):compact(x["name"]) for x in request["runners"]}
    if expected!={k:compact(v["name"]) for k,v in runners.items()}:raise ValueError("ORIGINAL_RUNNER_IDENTITY_CONFLICT")
    return runners

def _json(value):
    if isinstance(value,D):return str(value)
    if isinstance(value,(datetime,date)):return value.isoformat()
    if isinstance(value,list):return [_json(v) for v in value]
    if isinstance(value,dict):return {k:_json(v) for k,v in value.items()}
    return value

def independently_score(raw_field,source,request,registry,*,context=None,management=None):
    """Separate Decimal rule execution from independently parsed observations."""
    race=request.get("race") or {};context=context or {}
    management=management_source_inputs(source,request) if management is None else management
    # Use declared official context without silently changing missing aliases.
    venue=context.get("venue") or race.get("venue_id") or request.get("venue_id")
    venue_name={"FNB":"船橋","OHI":"大井","KAW":"川崎","URW":"浦和"}.get(venue,venue)
    distance=int(context.get("distance") or race.get("distance_m") or race.get("distance") or 0)
    direction=context.get("direction") or race.get("direction") or "UNKNOWN"
    surface=str(context.get("surface") or race.get("surface") or "DIRT").upper()
    going=context.get("going") or str(((source.get("normalized_evidence") or {}).get("track_condition") or {}).get("value") or race.get("going") or "")
    day=date.fromisoformat(request["race_date"].replace("/","-"))
    sets=registry["common_component_sets"];rules=registry["component_score_rules"]
    if tuple(sets)!=BASE or sum(map(len,sets.values()))!=63:raise ValueError("CURRENT_63_RULE_MANIFEST_REQUIRED")
    observations={};all_rows=[]
    proxy={"opponent_strength","course_geometry","draw_style_fit","third_corner_progression","kickback_traffic_tolerance",
        "venue_recent","distance_record","position_acquisition_skill","progression_timing_skill","favorite_reliability","longshot_record",
        "transfer_preparation","layoff_preparation","jockey_use_continuity","rotation_management","good_weight_range","carried_weight","interval","fatigue_rebound",
        "current_class","previous_class","recent_opponent_class","race_set_level","class_change_pressure","transfer_class","class_relative_time"}
    for rid,horse in raw_field.items():
        starts=horse["history"];size=len(raw_field);components={}
        for run in starts:
            if run["date"]>=day:raise ValueError("FUTURE_OR_SAME_DAY_HISTORY_FORBIDDEN")
        def put(index,name,value,cov,obs,reason=None):
            rule=rules[index][name];missing=value is None
            quality="UNKNOWN_MISSING" if missing else "MANAGEMENT" if index=="DCR" else "PROXY" if name in proxy else "DERIVED_OBSERVATION"
            issues=[]
            if name in {"passing_position_content","position_acquisition","position_maintenance","third_corner_progression","position_acquisition_skill","progression_timing_skill"}:
                issues.append("CORNER_NAMES_NOT_OBSERVED_IN_CARD_POSITION_STRING")
            if name in {"venue_recent","distance_record","position_acquisition_skill","progression_timing_skill","favorite_reliability","longshot_record"}:
                issues.append("SELECTED_SAME_HORSE_HISTORY_NOT_COMPLETE_PERSON_POPULATION")
            if name=="class_relative_time":issues.append("DISTANCE_ONLY_TIME_COMPARISON_NOT_ENVIRONMENT_ADJUSTED")
            if index=="BVIg-L":issues.append("PARENT_NAMES_ARE_NOT_PERMANENT_PARENT_ID_OR_POPULATION")
            rec={"runner_id":rid,"horse_name":horse["name"],"index":index,"component":name,
                "rule_id":rule["rule_id"],"transform":rule["transform"],"weight":sets[index][name],
                "witness_score":q(NEUTRAL if missing else clip(value)),"missing":missing,"coverage":q(cov),
                "partial_observation":not missing and number(cov)<1,"evidence_quality":quality,
                "source_observation":_json(obs),"missing_reason":reason if missing else None,
                "source_snapshot_sha256":source.get("source_snapshot_sha256"),"source_freeze_at":source.get("source_freeze_at"),
                "qualification_issues":issues,"empirical_ability_measurement_proven":False}
            components[name]=rec;all_rows.append(rec)
        finishes=[x["finish_score"] for x in starts];classes=[x["class_score"] for x in starts]
        margins=[D(100)*(-x["margin"]/2).exp() if x["margin"] is not None else None for x in starts]
        early=[];late=[];progress=[]
        for run in starts:
            p=run["positions"];fs=run["field_size"]
            a=finish(p[0],fs) if p and fs>1 else None;z=finish(p[-1],fs) if p and fs>1 else None
            early.append(a);late.append(z);progress.append(clip(D(50)+(z-a)/2) if a is not None and z is not None else None)
        put("HPI-L","recent_finish",decay_mean(finishes),coverage(len(starts),5),finishes,"NO_ELIGIBLE_RECENT_FINISH")
        put("HPI-L","finish_margin",decay_mean(margins),D(sum(x is not None for x in margins))/5,[x["margin"] for x in starts],"NO_NUMERIC_WINNER_MARGIN")
        put("HPI-L","passing_position_content",decay_mean(late),D(sum(x is not None for x in late))/5,late,"NO_ELIGIBLE_POINT_POSITION")
        put("HPI-L","class_level",decay_mean(classes),D(len(classes))/5,classes,"NO_RECENT_CLASS")
        opponent=[clip(D(".75")*x["class_score"]+D(".25")*clip(D(50)+(x["field_size"]-8)*4)) for x in starts]
        put("HPI-L","opponent_strength",decay_mean(opponent),D(len(opponent))/5,opponent,"NO_RECENT_CLASS_OR_FIELD")
        sd=spread(finishes)
        put("HPI-L","repeatability",clip(100-D("1.6")*sd) if sd is not None else None,coverage(len(starts),3),finishes,"FEWER_THAN_TWO_FINISHES")
        def matched(index,name,predicate):
            chosen=[x for x in starts if predicate(x)]
            put(index,name,avg([x["finish_score"] for x in chosen]),coverage(len(chosen),3),chosen,"NO_MATCHED_ELIGIBLE_HISTORY")
        matched("CFIg-L","same_venue",lambda x:same_venue(x["venue"],venue_name))
        matched("CFIg-L","same_distance",lambda x:x["distance"]==distance)
        matched("CFIg-L","similar_distance",lambda x:x["distance"] and abs(x["distance"]-distance)<=max(200,int(distance*D(".20"))))
        matched("CFIg-L","course_geometry",lambda x:x["direction"]==direction and x["surface"]==surface)
        matched("CFIg-L","turn_direction",lambda x:x["direction"]==direction)
        em=avg(early);inner=D(100)*(size-horse["horse_no"])/(size-1) if size>1 else None
        draw=clip(52+(em-50)/50*(inner-50)/2) if em is not None and inner is not None else None
        put("CFIg-L","draw_style_fit",draw,D(".5") if draw is not None else D(0),{"early":em,"inner":inner},"NO_POINT_EARLY_POSITION")
        matched("CFIg-L","going_fit",lambda x:going_matches(x["going"],going))
        valid=[v for v in early if v is not None];sd=spread(valid)
        put("RFIg-L","running_style_repro",clip(100-D("1.5")*sd) if sd is not None else None,coverage(len(valid),3),valid,"FEWER_THAN_TWO_EARLY_POSITIONS")
        put("RFIg-L","position_acquisition",decay_mean(early),D(len(valid))/5,early,"NO_POINT_EARLY_POSITION")
        put("RFIg-L","position_maintenance",decay_mean(progress),D(sum(x is not None for x in progress))/5,progress,"NO_ELIGIBLE_POINT_POSITION_PAIR")
        put("RFIg-L","third_corner_progression",decay_mean(progress),D(sum(x is not None for x in progress))/5,progress,"NO_ELIGIBLE_POINT_POSITION_PAIR")
        for name,predicate in (("leadership_stalk_acceptance",lambda x:x["positions"][0]<=3),
                               ("kickback_traffic_tolerance",lambda x:x["positions"][0]>3)):
            chosen=[x["finish_score"] for x in starts if x["positions"] and x["field_size"] and predicate(x)]
            put("RFIg-L",name,avg(chosen),coverage(len(chosen),3),chosen,"NO_MATCHED_RUNNING_POSITION_HISTORY")
        wet=[x["finish_score"] for x in starts if going_matches(x["going"],going)]
        put("RFIg-L","going_adaptation",avg(wet),coverage(len(wet),3),wet,"NO_MATCHED_GOING_HISTORY")
        jr=[x for x in starts if x["jockey"]==horse["jockey"]]
        put("RFIg-L","jockey_reproducibility",avg([x["finish_score"] for x in jr]),coverage(len(jr),3),jr,"NO_CURRENT_JOCKEY_HORSE_HISTORY")
        for name in sets["BVIg-L"]:put("BVIg-L",name,None,0,{"sire_name":horse["sire"],"damsire_name":horse["damsire"]},"PARENT_ID_CONDITIONAL_POPULATION_AND_COMPONENT_STATISTIC_NOT_IN_CARD")
        for name,predicate in (("venue_recent",lambda x:same_venue(x["venue"],venue_name)),("distance_record",lambda x:x["distance"]==distance)):
            chosen=[x for x in jr if predicate(x)]
            put("JTI-L",name,avg([x["finish_score"] for x in chosen]),coverage(len(chosen),3),chosen,"NO_MATCHED_CURRENT_JOCKEY_HORSE_HISTORY")
        put("JTI-L","stable_combo",None,0,{"jockey":horse["jockey"],"trainer":horse["trainer"]},"STABLE_WIDE_JOCKEY_COMBINATION_POPULATION_NOT_IN_SOURCE")
        ja=[];jp=[]
        for x in jr:
            if x["positions"] and x["field_size"]>1:
                a=finish(x["positions"][0],x["field_size"]);z=finish(x["positions"][-1],x["field_size"])
                ja.append(a);jp.append(clip(50+(z-a)/2))
        put("JTI-L","position_acquisition_skill",avg(ja),coverage(len(ja),3),ja,"NO_CURRENT_JOCKEY_POINT_POSITION_HISTORY")
        put("JTI-L","progression_timing_skill",avg(jp),coverage(len(jp),3),jp,"NO_CURRENT_JOCKEY_POINT_POSITION_PAIR")
        for name,predicate in (("favorite_reliability",lambda x:x["popularity"]<=3),
                               ("longshot_record",lambda x:x["popularity"]>=max(6,size//2))):
            chosen=[x["finish_score"] for x in jr if x["popularity"] and predicate(x)]
            put("JTI-L",name,avg(chosen),coverage(len(chosen),3),chosen,"NO_CURRENT_JOCKEY_MATCHED_POPULARITY_HISTORY")
        put("CSI-L","stable_venue_class_distance",None,0,{"trainer":horse["trainer"]},"STABLE_CONTEXT_POPULATION_NOT_IN_SOURCE")
        venues={re.sub("ナ$","",compact(x["venue"])) for x in starts if x["venue"]}
        put("CSI-L","transfer_preparation",D(70 if len(venues)<=2 else 60) if starts else None,coverage(len(starts),5),sorted(venues),"NO_RECENT_HISTORY")
        gaps=[]
        if starts:gaps.append((day-starts[0]["date"]).days)
        gaps.extend((a["date"]-b["date"]).days for a,b in zip(starts,starts[1:]));gaps=[x for x in gaps if x>=0]
        first=gaps[0] if gaps else None
        put("CSI-L","layoff_preparation",interval_score(first),int(first is not None),{"days":first},"NO_DATED_HISTORY")
        put("CSI-L","jockey_use_continuity",D(100)*len(jr)/max(1,min(5,len(starts))) if starts else None,coverage(len(starts),5),{"same_jockey":len(jr),"starts":len(starts)},"NO_RECENT_HISTORY")
        put("CSI-L","cci_specificity",None,0,None,"OFFICIAL_STABLE_COMMENT_NOT_IN_SOURCE")
        put("CSI-L","tri_vertical_comparison",None,0,None,"OFFICIAL_TRAINING_OR_TRIAL_NOT_IN_SOURCE")
        sd=spread(gaps)
        put("CSI-L","rotation_management",clip(100-sd) if sd is not None else None,coverage(len(gaps),3),gaps,"FEWER_THAN_TWO_INTERVALS")
        bw=[(x["body_weight"],x["finish_score"]) for x in starts if x["body_weight"]]
        good=[w for w,f in bw if f is not None and f>=60];cur=horse["body_weight"]
        value=None
        if cur is not None and good:
            lo,hi=min(good)-5,max(good)+5;value=D(85) if lo<=cur<=hi else clip(85-min(abs(cur-lo),abs(cur-hi))*2)
        put("BWI-L","good_weight_range",value,coverage(len(good),3),{"current":cur,"good_history":good},"CURRENT_OR_GOOD_HISTORY_WEIGHT_UNAVAILABLE")
        put("BWI-L","weight_change_reason_rate",None,0,{"change_kg":horse["body_weight_change"]},"CAUSAL_WEIGHT_CHANGE_REASON_NOT_IN_SOURCE")
        loads=[x["load"] for x in raw_field.values() if x["load"] is not None]
        value=None
        if horse["load"] is not None and loads:
            lo,hi=min(loads),max(loads);value=NEUTRAL if lo==hi else 40+45*(hi-horse["load"])/(hi-lo)
        put("BWI-L","carried_weight",value,int(value is not None),{"load":horse["load"],"field_loads":loads},"FIELD_LOAD_NOT_OBSERVED")
        put("BWI-L","age_growth",None,0,None,"HORSE_SPECIFIC_GROWTH_EVIDENCE_NOT_IN_SOURCE")
        put("BWI-L","interval",interval_score(first),int(first is not None),{"days":first},"NO_DATED_HISTORY")
        change=horse["body_weight_change"]
        value=clip(70+D(min(15,max(-15,change)))/3-max(0,14-first)) if first is not None and change is not None else None
        put("BWI-L","fatigue_rebound",value,D(".5") if value is not None else 0,{"days":first,"change":change},"INTERVAL_OR_WEIGHT_CHANGE_NOT_OBSERVED")
        put("BWI-L","transport_season",None,0,None,"TRANSPORT_AND_SEASON_CAUSAL_SOURCE_NOT_IN_BUNDLE")
        put("BWI-L","paddock",None,0,None,"OFFICIAL_PADDOCK_NOT_IN_SOURCE")
        put("DCR","official_recent_coverage",100*coverage(len(starts),5),1,{"history_rows":len(starts)})
        comparable=sum(same_venue(x["venue"],venue_name) and x["distance"]==distance for x in starts)
        put("DCR","same_venue_distance_comparability",100*coverage(comparable,3),1,{"matched_history":comparable})
        put("DCR","training_comment_trial",0,1,{"manifest_supported_current_implementation":0})
        put("DCR","bodyweight_range_coverage",100*coverage(int(cur is not None)+len(bw),6),1,{"observations":int(cur is not None)+len(bw)})
        put("DCR","same_day_gci_coverage",100*coverage(management["prior_result_count"],max(1,request["race_no"]-1)),1,{"raw_verified_prior_races":management["prior_race_numbers"]})
        put("DCR","late_odds_changes_coverage",100 if management["odds_source_present"] else 0,1,{"raw_verified_odds_source_present":management["odds_source_present"]})
        curclass,state=grade(str(race.get("class") or ""));prev=starts[0]["class_score"] if starts else None
        for name,value,obs,reason in (("current_class",curclass,{"class":race.get("class"),"parse_state":state},None),
             ("previous_class",prev,starts[0]["race_name"] if starts else None,"NO_RECENT_CLASS"),
             ("recent_opponent_class",decay_mean(classes),classes,"NO_RECENT_CLASS"),
             ("race_set_level",curclass,{"class":race.get("class"),"parse_state":state},None),
             ("class_change_pressure",clip(50+(prev-curclass)*D("1.5")) if prev is not None else None,{"previous":prev,"current":curclass},"NO_PREVIOUS_CLASS"),
             ("transfer_class",clip(50+((prev or NEUTRAL)-curclass)*(D("1.2") if starts and compact(starts[0]["venue"]).startswith("J") else D(".8"))) if starts else None,{"previous":prev,"current":curclass},"NO_PREVIOUS_CLASS")):
            cov=D(len(classes))/5 if name=="recent_opponent_class" else int(value is not None)
            put("NCI",name,value,cov,obs,reason)
        observations[rid]={"horse":horse,"components":components,"current_distance":distance}
    best={rid:min(x["time_seconds"] for x in row["horse"]["history"] if x["distance"]==distance and x["time_seconds"] is not None)
          for rid,row in observations.items() if any(x["distance"]==distance and x["time_seconds"] is not None for x in row["horse"]["history"])}
    for rid,row in observations.items():
        rule=rules["NCI"]["class_relative_time"];score=None
        if rid in best:
            lo,hi=min(best.values()),max(best.values());score=D(70) if lo==hi else 40+50*(hi-best[rid])/(hi-lo)
        rec={"runner_id":rid,"horse_name":row["horse"]["name"],"index":"NCI","component":"class_relative_time",
             "rule_id":rule["rule_id"],"transform":rule["transform"],"weight":sets["NCI"]["class_relative_time"],
             "witness_score":q(NEUTRAL if score is None else clip(score)),"missing":score is None,"coverage":int(score is not None),
             "partial_observation":False,"evidence_quality":"UNKNOWN_MISSING" if score is None else "PROXY",
             "source_observation":_json({"distance":distance,"best_time":best.get(rid),"field_best_times":best}),
             "missing_reason":"NO_COMPARABLE_DISTANCE_TIME" if score is None else None,
             "source_snapshot_sha256":source.get("source_snapshot_sha256"),"source_freeze_at":source.get("source_freeze_at"),
             "qualification_issues":["DISTANCE_ONLY_TIME_COMPARISON_NOT_ENVIRONMENT_ADJUSTED"],"empirical_ability_measurement_proven":False}
        row["components"]["class_relative_time"]=rec;all_rows.append(rec)
    result=[]
    for rid,row in observations.items():
        for index,weights in sets.items():
            numerator=sum((D(str(row["components"][c]["witness_score"]))*D(str(w)) for c,w in weights.items()),D(0))
            value=clip(numerator/sum((D(str(w)) for w in weights.values()),D(0)))
            result.append({"runner_id":rid,"index":index,"witness_value":q(value),"component_count":len(weights),
                "missing":sum(row["components"][c]["missing"] for c in weights),"all_components_missing":all(row["components"][c]["missing"] for c in weights)})
    return all_rows,result

def verify(source,request,registry,materialized=None,*,context=None):
    """Return real-source audit; no Producer or network call occurs here."""
    with localcontext() as ctx:
        ctx.prec=40
        snapshots=source_snapshot_audit(source)
        card,raw,parser=original_card(source,request)
        fetched=datetime.fromisoformat(card["fetched_at"].replace("Z","+00:00"))
        freeze=datetime.fromisoformat(source["source_freeze_at"].replace("Z","+00:00"))
        cutoff=datetime.fromisoformat(request["prediction_cutoff"].replace("Z","+00:00"))
        if (cutoff.tzinfo is None or fetched>freeze or not freeze<cutoff
                or datetime.fromisoformat(source["prediction_cutoff"].replace("Z","+00:00"))!=cutoff):
            raise ValueError("CARD_FREEZE_OR_CUTOFF_INELIGIBLE")
        header=official_context(parser,request)
        management=management_source_inputs(source,request)
        horses=parse_original_runners(parser,source,request)
        rows,indices=independently_score(horses,source,request,registry,context=context or header,management=management)
    actual={str(x["runner_id"]):x for x in (materialized or {}).get("runners",[])}
    mismatch=[]
    for row in rows:
        if row["component"]=="same_day_gci_coverage":
            inputs=[s for s in management["independently_raw_parsed_sources"] if s["source_class"]=="OFFICIAL_SAME_DAY_RACE_RESULT_PASSING_ORDER"]
        elif row["component"]=="late_odds_changes_coverage":
            inputs=[s for s in management["independently_raw_parsed_sources"] if s["source_class"]=="OFFICIAL_ACTIVE_BETTING_UNIVERSE"]
        else:inputs=[{"source_id":card["source_id"],"snapshot_sha256":card["snapshot_sha256"],"raw_sha256":card["raw_sha256"]}]
        row["independent_source_inputs"]=[{k:s[k] for k in ("source_id","snapshot_sha256","raw_sha256")} for s in inputs]
        row["raw_runner_json_pointer"]="/raw_parsed_runners/"+row["runner_id"]
        old=(actual.get(row["runner_id"],{}).get("evidence_features") or {}).get(row["component"])
        if not isinstance(old,dict):row["independent_comparison"]="NO_MATERIALIZED_RECORD";continue
        same=(abs(number(old["score"])-number(row["witness_score"]))<=EPSILON and old.get("missing")==row["missing"] and
              abs(number(old.get("coverage",0))-number(row["coverage"]))<=EPSILON and old.get("rule_id")==row["rule_id"])
        row["production_record"]={k:old.get(k) for k in ("score","missing","coverage","rule_id")}
        row["production_refs_cover_independent_inputs"]=all(s[k] in (old.get("evidence_refs") or []) for s in inputs for k in ("source_id","snapshot_sha256"))
        row["independent_comparison"]="MATCH" if same else "MISMATCH"
        if not same:mismatch.append({k:row[k] for k in ("runner_id","index","component","witness_score","production_record")})
    for row in indices:
        old=(actual.get(row["runner_id"],{}).get("canonical_components") or {}).get(row["index"])
        row["production_value"]=old.get("value") if isinstance(old,dict) else None
        row["independent_comparison"]="NO_MATERIALIZED_RECORD" if old is None else "MATCH" if abs(number(old["value"])-number(row["witness_value"]))<=EPSILON else "MISMATCH"
    return {"profile":PROFILE,"classification":"HISTORICAL_DIAGNOSTIC_PRIVATE_NOT_OOS",
        "race_id":request["race_id"],"original_raw_sha256":digest(raw),"original_card_snapshot_sha256":card["snapshot_sha256"],
        "source_freeze_at":source.get("source_freeze_at"),"cutoff":request["prediction_cutoff"],
        "source_snapshot_byte_audit":snapshots,"independent_official_race_context":header,
        "independent_management_source_inputs":management,
        "source_snapshots_after_freeze":sum(not x["observed_before_source_freeze"] for x in snapshots),
        "source_snapshots_at_or_after_cutoff":sum(not x["observed_before_prediction_cutoff"] for x in snapshots),
        "context_policy":"INDEPENDENT_OFFICIAL_HEADER" if context is None else "EXPLICIT_DIAGNOSTIC_CONTEXT_OVERRIDE_NOT_OFFICIAL_HEADER",
        "runner_count":len(horses),"rule_count":63,"component_records":len(rows),
        "component_match_counts":dict(Counter(x["independent_comparison"] for x in rows)),
        "index_match_counts":dict(Counter(x["independent_comparison"] for x in indices)),
        "missing_count":sum(x["missing"] for x in rows),"evidence_quality_counts":dict(Counter(x["evidence_quality"] for x in rows)),
        "partial_observation_count":sum(x["partial_observation"] for x in rows),
        "production_input_provenance_gaps":sum(r.get("production_refs_cover_independent_inputs") is False for r in rows),
        "all_63_rules_visited":len({(r["index"],r["component"]) for r in rows})==63,
        "distinct_observed_rules_exercised":len({(r["index"],r["component"]) for r in rows if not r["missing"]}),
        "missing_terminal_match_count":sum(r["missing"] and r["independent_comparison"]=="MATCH" for r in rows),
        "nonmissing_arithmetic_match_count":sum(not r["missing"] and r["independent_comparison"]=="MATCH" for r in rows),
        "all_63_rules_empirical_measurement_complete":False,
        "source_to_score_all_records_arithmetic_match":bool(actual) and not mismatch,
        "independent_parser_used":True,"production_compiler_called":False,"provider_license_or_source_signature_verified_here":False,
        "model_consumers_authorized":False,"predictive_validity_proven":False,"new_independent_raw_acquired":0,
        "mismatches":mismatch,"component_ledger":rows,"base_index_ledger":indices,
        "raw_parsed_runners":_json(horses)}

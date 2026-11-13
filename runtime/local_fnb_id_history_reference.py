"""Private archived history selected by a separately verified native horse ID.

No label/composite selects a horse here. IDs are checked against actual same-row
official links or an original HorseMarkInfo request/final URL. History remains
an incomplete archived observation set, not a current SOURCE or Active grant.
"""
from __future__ import annotations

import base64
import csv
from copy import deepcopy
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
import gzip
import hashlib
from html.parser import HTMLParser
import json
import io
from pathlib import Path
import re
from urllib.parse import parse_qs, urljoin, urlsplit
import zipfile

from runtime import local_base63_source_witness as witness
from runtime.local_fnb_csv_composite_history import normalize
from runtime.local_fnb_r12_historical_krs_witness import verify_envelope
from runtime.local_historical_population_observations import extract_horse_history, _HistoryRows
from runtime.local_historical_identity_observations import extract_result_row_identities
from runtime.local_historical_population_observations import VENUE_NAMES_BY_CODE
from runtime.local_nar_csv_reference import SCHEMAS
from runtime.local_fnb_csv_preliminary_numeric import _load_number
from runtime.local_nar_evidence_candidate import parse_race_card, _class_score, _finish_score, _time_seconds
from runtime.local_physical.source_acquisition import _decode, _html_tables

PROFILE = "KM-FNB-NATIVE-ID-ARCHIVED-HISTORY-REFERENCE-v1"
JST = timezone(timedelta(hours=9))


def _stamp(value):
    out = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if out.tzinfo is None: raise ValueError("ID_HISTORY_AWARE_ASOF_REQUIRED")
    return out


def _sha(raw): return hashlib.sha256(raw).hexdigest()


def _hash(value):
    return _sha(json.dumps(value, sort_keys=True, ensure_ascii=False,
        separators=(",", ":"), allow_nan=False).encode())


def _raw(snapshot, as_of):
    if (snapshot.get("official") is not True or snapshot.get("authority") != "NAR_OFFICIAL"
            or snapshot.get("http_status") != 200 or _stamp(snapshot["fetched_at"]) >= as_of):
        raise ValueError("ID_HISTORY_ORIGINAL_OFFICIAL_ASOF_REQUIRED")
    raw = gzip.decompress(base64.b64decode(snapshot["raw_gzip_b64"], validate=True))
    if (not raw or len(raw)>8_000_000 or _sha(raw)!=snapshot.get("raw_sha256")
            or len(raw)!=snapshot.get("byte_count")
            or _hash({k:v for k,v in snapshot.items() if k!="snapshot_sha256"})!=snapshot.get("snapshot_sha256")):
        raise ValueError("ID_HISTORY_ORIGINAL_RAW_OR_SNAPSHOT_SHA_INVALID")
    return raw


class _LinkedRows(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.rows=[];self.row=None;self.cell=None;self.anchor=None;self.horse_links=[]
    def handle_starttag(self,tag,attrs):
        if tag=="tr":self.row=[]
        elif tag in {"td","th"} and self.row is not None:self.cell={"text":[],"anchors":[]}
        elif tag=="a" and self.cell is not None:self.anchor=[dict(attrs).get("href",""),[]]
    def handle_data(self,text):
        if self.cell is not None:self.cell["text"].append(text)
        if self.anchor is not None:self.anchor[1].append(text)
    def handle_endtag(self,tag):
        if tag=="a" and self.anchor is not None:
            href,label=self.anchor[0],normalize("".join(self.anchor[1]))
            self.cell["anchors"].append((href,label))
            # Record the actual preceding same-row horse-number cell before
            # nested record tables start inside a later cell of this row.
            if "HorseMarkInfo" in href and self.row:
                self.horse_links.append((self.row[-1]["text"],href,label))
            self.anchor=None
        elif tag in {"td","th"} and self.cell is not None:
            self.cell["text"]=normalize("".join(self.cell["text"]));self.row.append(self.cell);self.cell=None
        elif tag=="tr" and self.row is not None:self.rows.append(self.row);self.row=None


def _card_ids(text, base_url):
    parser=_LinkedRows();parser.feed(text);out={}
    for preceding,href,label in parser.horse_links:
        url=urlsplit(urljoin(base_url,href))
        if url.path!="/KeibaWeb/DataRoom/HorseMarkInfo":continue
        ids=parse_qs(url.query).get("k_lineageLoginCode") or []
        if (url.scheme!="https" or url.hostname not in {"www.keiba.go.jp","keiba.go.jp"}
                or len(ids)!=1 or not ids[0].isdigit() or not preceding.isdigit()):
            raise ValueError("ID_HISTORY_DIRECT_CARD_ROW_IDENTITY_INVALID")
        rid=str(int(preceding));value=("NAR:"+ids[0],label,urljoin(base_url,href))
        if rid in out and out[rid]!=value:raise ValueError("ID_HISTORY_CARD_ROW_ID_CONFLICT")
        out[rid]=value
    return out


def _day(start):
    m=re.fullmatch(r"(\d{2})\.(\d{2})\.(\d{2})",str(start.get("date","")))
    if not m:raise ValueError("ID_HISTORY_DATED_START_REQUIRED")
    return date(2000+int(m[1]),int(m[2]),int(m[3]))


def _number(value):
    text=normalize(value).replace(",","")
    if not re.fullmatch(r"[+-]?\d+(?:\.\d+)?",text):return None
    number=Decimal(text)
    return float(number) if number.is_finite() else None


def _profile_pairs(snapshot, raw, target_day, as_of):
    # Existing extractor verifies URL-native-ID, original bytes and per-row
    # official Race links. A separate table traversal supplies Decimal witness
    # values; no aggregate record is turned into individual starts.
    extracted=extract_horse_history(snapshot,as_of=as_of.isoformat(),target_race_date=target_day.isoformat())
    text=_decode(raw,snapshot.get("content_type",""));parsed=_HistoryRows();parsed.feed(text)
    independent=witness.OriginalTables();independent.feed(text)
    independent_rows=[r for table in independent.tables for r in table if len(r)>=23 and re.fullmatch(r"\d{4}/\d{2}/\d{2}",r[0])]
    actual_by_ordinal={i:cells for i,(cells,links) in enumerate(parsed.rows)}
    pairs=[]
    for observation in extracted["records"]:
        cells=actual_by_ordinal[observation["field_provenance"]["row_ordinal"]]
        when=date.fromisoformat(observation["event_date"].replace("/","-"))
        expected=[r for r in independent_rows if r[0]==cells[0] and normalize(r[1])==normalize(cells[1])
                  and r[2]==cells[2] and r[11]==cells[11]]
        if len(expected)!=1:raise ValueError("ID_HISTORY_PROFILE_INDEPENDENT_EVENT_ROW_CONFLICT")
        other=expected[0]
        for column in (0,1,2,3,4,5,7,9,11,12,13,14,15,16,17,18,19):
            if normalize(other[column])!=normalize(cells[column]):raise ValueError("ID_HISTORY_PROFILE_INDEPENDENT_CELL_CONFLICT")
        class_score,class_state=_class_score(cells[3]);field=observation["field_size"];finish=observation["finish"]
        distance=observation["distance_m"]
        # The profile prints no course turn and often no surface. Do not infer
        # either from venue or silently call all LOCAL starts dirt.
        surface=observation.get("surface") or "UNKNOWN"
        candidate={"date":when.strftime("%y.%m.%d"),"finish":finish,"field_size":field,
            "venue":observation["venue_label"],"distance":distance,"surface":surface,"direction":"UNKNOWN",
            "going":observation["going"],"horse_no":observation["horse_no"],"race_name":cells[3],
            "ride_popularity":int(cells[12]) if cells[12].isdigit() else None,
            "ride_body_weight":observation["body_weight_kg"],"ride_jockey":normalize(cells[18].split("(")[0].split("（")[0]),
            "ride_carried_weight":_load_number(cells[19]),"content_time_seconds":_time_seconds(cells[14]),
            "content_final3f":_number(cells[16]),"content_positions":[],"margin":_number(cells[15]),
            "class_score":class_score,"class_parse_state":class_state,"finish_score":_finish_score(finish,field),
            "official_past_race_id":observation["race_id"],"historical_source_raw_sha256":snapshot["raw_sha256"],
            "profile_row_ordinal":observation["field_provenance"]["row_ordinal"]}
        score,state=witness.grade(other[3]);direct={"date":when,"finish":int(other[13]),"field_size":int(other[9]),
            "venue":other[1],"distance":distance,"surface":surface,"direction":"UNKNOWN","going":other[7],
            "horse_no":int(other[11]),"race_name":other[3],"class_score":score,"class_state":state,
            "popularity":int(other[12]) if other[12].isdigit() else None,"body_weight":int(other[17]) if other[17].isdigit() else None,
            "jockey":witness.jockey(other[18]),"carried_weight":witness.number(candidate["ride_carried_weight"]),
            "time_seconds":witness.seconds(other[14]),"positions":[],"margin":witness.number(candidate["margin"]),
            "finish_score":witness.finish(int(other[13]),int(other[9]))}
        pairs.append((candidate,direct))
    return extracted["horse_id"],pairs


def _merge(old,new):
    # Complementary actual observations may fill missing cells. Any conflicting
    # finite scoring input removes that event; no latest-capture overwrite.
    candidate,independent=old;other,other_independent=new
    fields=("finish","field_size","distance","surface","direction","going","horse_no",
        "ride_popularity","ride_body_weight","ride_jockey","ride_carried_weight",
        "content_time_seconds","content_final3f","content_positions","margin","class_score","finish_score")
    absent=lambda v:v in (None,"","UNKNOWN") or v==[]
    for key in fields:
        a,b=candidate.get(key),other.get(key)
        if absent(a) and not absent(b):candidate[key]=deepcopy(b)
        elif not absent(a) and not absent(b):
            equal=normalize(a)==normalize(b) if isinstance(a,str) and isinstance(b,str) else a==b
            if not equal:raise ValueError("ID_HISTORY_CONFLICTING_DATED_FACT:"+key)
    independent_fields={"distance":"distance","surface":"surface","direction":"direction","going":"going",
        "ride_popularity":"popularity","ride_body_weight":"body_weight","ride_jockey":"jockey",
        "ride_carried_weight":"carried_weight","content_time_seconds":"time_seconds","content_positions":"positions",
        "margin":"margin","class_score":"class_score","finish_score":"finish_score"}
    for source,target in independent_fields.items():
        if absent(independent.get(target)) and not absent(other_independent.get(target)):
            independent[target]=deepcopy(other_independent[target])
    for record,extra in ((candidate,other),(independent,other_independent)):
        provenance=record.setdefault("history_source_provenance",[])
        for ref in extra.get("history_source_provenance",[]):
            if ref not in provenance:provenance.append(deepcopy(ref))
    return candidate,independent


def _historical_csv(raw,receipt,as_of):
    if not isinstance(raw,bytes) or not isinstance(receipt,dict):raise ValueError("ID_HISTORY_CSV_ORIGINAL_AND_RECEIPT_REQUIRED")
    zip_digest=_sha(raw)
    if (receipt.get("http_status")!=200 or receipt.get("sha256")!=zip_digest
            or receipt.get("bytes")!=len(raw) or _stamp(receipt["ended_at"])>=as_of):
        raise ValueError("ID_HISTORY_CSV_CAPTURE_HASH_OR_ASOF_INVALID")
    url=urlsplit(receipt["url"]);query=parse_qs(url.query)
    if (url.scheme!="https" or url.hostname!="www.keiba.go.jp" or url.path!="/KeibaWeb/DataDownload/RaceDataDownload"
            or query.get("type")!=["monthly"] or query.get("k_year")!=["2026"] or query.get("k_month")!=["10"]):
        raise ValueError("ID_HISTORY_EXACT_OBTAINED_OCTOBER_CSV_REQUIRED")
    tables={};origins={}
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        if len(raw)>30_000_000 or archive.testzip() is not None:raise ValueError("ID_HISTORY_CSV_ZIP_HASH_OR_CRC")
        for kind in ("racelist","horselist"):
            name="202610_"+kind+".csv";content=archive.read(name)
            member_digest=_sha(content)
            reader=csv.DictReader(io.StringIO(content.decode("utf-8-sig"),newline=""))
            if tuple(reader.fieldnames or[])!=SCHEMAS[kind]:raise ValueError("ID_HISTORY_CSV_DOCUMENTED_HEADER")
            table={}
            for number,row in enumerate(reader,2):
                if not row["競走年月日"].startswith("202610"):raise ValueError("ID_HISTORY_CSV_PERIOD_CONFLICT")
                key=(normalize(row["競馬場"]),row["競走年月日"],int(row["レース番号"]))
                if kind=="horselist":key+=(int(row["馬番"]),)
                if key in table:raise ValueError("ID_HISTORY_CSV_EVENT_ROW_DUPLICATE")
                row["_csv_origin"]={"zip_raw_sha256":zip_digest,"member":name,"member_sha256":member_digest,"csv_row":number}
                table[key]=row
            tables[kind]=table
    return tables,{"source_id":"NAR-OFFERED-CSV-HISTORY-"+zip_digest,
        "snapshot_sha256":_hash(receipt),"raw_sha256":zip_digest,"fetched_at":receipt["ended_at"],
        "scope":"HISTORICAL_CSV_SUPPLEMENT_NOT_FORMAL_SOURCE"}


def _result_pairs(snapshot,raw,tables,ids,target,as_of):
    extracted=extract_result_row_identities(snapshot,as_of=as_of.isoformat(),target_race_date=target.isoformat())
    text=_decode(raw,snapshot.get("content_type",""));parser=witness.OriginalTables();parser.feed(text)
    candidates=[table for table in parser.tables if table and table[0][:4]==["着順","枠","馬番","馬名"]]
    if len(candidates)!=1:raise ValueError("ID_HISTORY_ONE_INDEPENDENT_RESULT_TABLE_REQUIRED")
    table=candidates[0];header=[normalize(x) for x in table[0]]
    result=[]
    for observation in extracted["records"]:
        native=observation.get("horse_id")
        if native not in ids or observation.get("finish") is None:continue
        day=date.fromisoformat(observation["event_date"]);venue=VENUE_NAMES_BY_CODE[observation["venue_code"]]
        key=(venue,day.strftime("%Y%m%d"),observation["race_no"])
        race=tables["racelist"].get(key);horse=tables["horselist"].get(key+(observation["horse_no"],))
        if race is None or horse is None:continue
        # Both inputs refer to this exact event. An independently printed
        # signed-result heading cannot be silently replaced by CSV context.
        # Missing optional heading fields remain unobserved in this audit;
        # the separately observed CSV retains its own provenance.
        csv_heading={"distance_m":int(race["距離"]),
            "surface":{"ダート":"DIRT","芝":"TURF"}.get(race["芝ダート区分"],"UNKNOWN"),
            "going":race["馬場"],"race_name":race["レース名"]}
        heading_comparison={}
        for field,from_csv in csv_heading.items():
            printed=observation.get(field)
            if printed in (None,""):
                heading_comparison[field]="OPTIONAL_SIGNED_HEADING_UNKNOWN"
                continue
            equal=(printed==from_csv) if field=="distance_m" else normalize(printed)==normalize(from_csv)
            if not equal:raise ValueError("ID_HISTORY_RESULT_HEADING_CSV_CONFLICT:"+field)
            heading_comparison[field]="MATCH"
        if normalize(horse["馬名"])!=normalize(observation["horse_label"]) or horse["着順"]!=str(observation["finish"]):
            raise ValueError("ID_HISTORY_RESULT_CSV_EXACT_EVENT_IDENTITY_CONFLICT")
        field=int(race["頭数"])
        if not 1<=observation["finish"]<=field or field<=1:raise ValueError("ID_HISTORY_CSV_EXPLICIT_FIELD_SIZE_INVALID")
        rows=[row for row in table[1:] if len(row)==len(header) and row[2].isdigit() and int(row[2])==observation["horse_no"]]
        if len(rows)!=1:raise ValueError("ID_HISTORY_INDEPENDENT_RESULT_HORSE_ROW_NOT_UNIQUE")
        row=rows[0]
        if normalize(row[3])!=normalize(horse["馬名"]) or row[0]!=horse["着順"]:raise ValueError("ID_HISTORY_INDEPENDENT_RESULT_ROW_CONFLICT")
        values=dict(zip(header,row));time_text=values.get("タイム","");time_value=_time_seconds(time_text)
        load=_load_number(values.get("負担重量"));jockey=witness.jockey(values.get("騎手(所属)",values.get("騎手（所属）","")))
        if not jockey:jockey=witness.jockey(row[7])
        if load!=_load_number(horse["負担重量"]) or jockey!=witness.jockey(horse["騎手名"]):raise ValueError("ID_HISTORY_RESULT_CSV_RIDE_CONFLICT")
        position_text=values.get("コーナー通過順","")
        positions=[int(x) for x in position_text.split("-")] if re.fullmatch(r"\d+(?:-\d+)+",position_text) else []
        if any(not 1<=x<=field for x in positions):raise ValueError("ID_HISTORY_RESULT_POINT_POSITION_INVALID")
        surface={"ダート":"DIRT","芝":"TURF"}.get(race["芝ダート区分"],"UNKNOWN")
        direction={"左":"LEFT","右":"RIGHT","直":"STRAIGHT"}.get(race["回り"],"UNKNOWN")
        grade,state=_class_score(race["レース名"]);decimal_grade,decimal_state=witness.grade(race["レース名"])
        # Result 着差 is a length/fraction to another finisher, not the seconds
        # margin used by the existing card transform. Preserve it raw and leave
        # that component UNKNOWN. Group corner strings never become point ranks.
        candidate={"date":day.strftime("%y.%m.%d"),"finish":observation["finish"],"field_size":field,
            "venue":venue,"distance":int(race["距離"]),"surface":surface,"direction":direction,
            "going":race["馬場"],"horse_no":observation["horse_no"],"race_name":race["レース名"],
            "ride_popularity":int(horse["人気"]) if horse["人気"].isdigit() else None,
            "ride_body_weight":int(horse["馬体重"]) if horse["馬体重"].isdigit() else None,
            "ride_jockey":jockey,"ride_carried_weight":load,"content_time_seconds":time_value,
            "content_final3f":_number(horse["上がり3F"]),"content_positions":positions,"margin":None,
            "class_score":grade,"class_parse_state":state,"finish_score":_finish_score(observation["finish"],field),
            "official_past_race_id":observation["race_id"],"result_length_margin_raw_not_seconds":horse["着差"],
            "historical_source_raw_sha256":snapshot["raw_sha256"],"historical_csv_race_origin":race["_csv_origin"],
            "historical_csv_horse_origin":horse["_csv_origin"],
            "signed_result_heading_csv_comparison":heading_comparison}
        direct={"date":day,"finish":int(row[0]),"field_size":field,"venue":venue,"distance":int(race["距離"]),
            "surface":surface,"direction":direction,"going":race["馬場"],"horse_no":int(row[2]),
            "race_name":race["レース名"],"class_score":decimal_grade,"class_state":decimal_state,
            "popularity":candidate["ride_popularity"],"body_weight":candidate["ride_body_weight"],
            "jockey":witness.jockey(row[7]),"carried_weight":witness.number(load),"time_seconds":witness.seconds(row[10]),
            "positions":deepcopy(positions),"margin":None,"finish_score":witness.finish(int(row[0]),field)}
        result.append((native,(candidate,direct),observation["field_provenance"]["identity_links"]["horse_id"]["url"]))
    return result


def build_id_history_index(repo_root, envelope_manifest, native_ids, as_of, target_race_date,
                           *, envelope_raw_by_sha=None, historical_csv_raw=None, historical_csv_receipt=None):
    root=Path(repo_root).resolve();clock=_stamp(as_of);target=date.fromisoformat(target_race_date)
    ids=set(native_ids)
    if not ids or any(not re.fullmatch(r"NAR:\d+",str(x)) for x in ids):raise ValueError("ID_HISTORY_EXPLICIT_NATIVE_IDS_REQUIRED")
    cfg=json.loads((root/"profiles/current_execution_gateway.json").read_bytes())["families"]["LOCAL"]
    trust_path=root/"evidence/family_audit_20261016/runtime_health.json";trust=json.loads(trust_path.read_bytes())
    if any(trust[k]!=cfg[k] for k in ("receipt_signer_key_id","engine_sha256","parameter_map_sha256")):
        raise ValueError("ID_HISTORY_CANONICAL_TRUST_MISMATCH")
    public=base64.b64decode(trust["receipt_public_key_b64"],validate=True)
    historical=None;csv_ref=None
    if historical_csv_raw is not None or historical_csv_receipt is not None:
        historical,csv_ref=_historical_csv(historical_csv_raw,historical_csv_receipt,clock)
    entries={native:{"status":"NATIVE_ID_ARCHIVED_HISTORY_REFERENCE_NOT_CURRENT_SOURCE", "horse_id":native,
        "starts":[],"independent_history":[],"context_observations":[],"provenance":[],"source_refs":[],
        "history_complete":False,"formal_source_admitted":False,"active_universe_verified":False,"_events":{}}
        for native in ids}
    holds=[];manifest=[];seen_snapshots=set();seen_result_raw=set();seen_profile_raw=set();verified=0
    def add(native,pairs,ref):
        item=entries[native];item["provenance"].append(ref)
        item["source_refs"].extend([ref["source_id"],ref["snapshot_sha256"],ref["raw_sha256"]])
        item["source_refs"].extend(ref.get("supplemental_source_refs",[]))
        for candidate,direct in pairs:
            candidate=deepcopy(candidate);direct=deepcopy(direct)
            candidate.setdefault("history_source_provenance",[]).append(deepcopy(ref))
            direct.setdefault("history_source_provenance",[]).append(deepcopy(ref))
            day=_day(candidate)
            if day>=target or day>=clock.astimezone(JST).date():
                holds.append({"horse_id":native,"event_date":day.isoformat(),"reason":"ID_HISTORY_SAME_OR_FUTURE_DATE_EXCLUDED"});continue
            key=(day,normalize(candidate["venue"]))
            if item["_events"].get(key)=="HOLD":continue
            if key in item["_events"]:
                try:item["_events"][key]=_merge(item["_events"][key],(candidate,direct))
                except ValueError as exc:item["_events"][key]="HOLD";holds.append({"horse_id":native,"event_date":day.isoformat(),"reason":str(exc)})
            else:item["_events"][key]=(deepcopy(candidate),deepcopy(direct))
    for original in envelope_manifest:
        path=Path(original["envelope_path"]);path=path if path.is_absolute() else root/path
        if envelope_raw_by_sha is None:
            raw_envelope=path.read_bytes()
        else:
            raw_envelope=envelope_raw_by_sha.get(original["envelope_file_sha256"])
            if not isinstance(raw_envelope,bytes):raise ValueError("ID_HISTORY_EMBEDDED_ORIGINAL_BYTES_REQUIRED")
        if _sha(raw_envelope)!=original["envelope_file_sha256"]:raise ValueError("ID_HISTORY_MANIFEST_FILE_SHA_MISMATCH")
        manifest.append({"path":str(path),"sha256":_sha(raw_envelope),"bytes":len(raw_envelope)})
        env=json.loads(raw_envelope);source=env.get("artifact") or {}
        if source.get("source_snapshot_sha256") in seen_snapshots:continue
        seen_snapshots.add(source.get("source_snapshot_sha256"))
        source=verify_envelope(env,race_id=source["race_id"],phase="SOURCE",status="SOURCE_FROZEN",public=public,cfg=cfg);verified+=1
        if _stamp(source["source_freeze_at"])>=clock:raise ValueError("ID_HISTORY_ARCHIVE_FREEZE_AT_OR_AFTER_ASOF")
        common={"envelope_path":str(path),"envelope_file_sha256":_sha(raw_envelope),"receipt_sha256":env["receipt_sha256"],"signature_verified":True}
        card_interest={"NAR:"+str(r.get("horse_lineage_login_code")) for r in source.get("nar_entity_registry",[])}&ids
        if card_interest:
            cards=[s for s in source["sources"] if s.get("source_class")=="OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT" and s.get("official") is True]
            if len(cards)!=1:raise ValueError("ID_HISTORY_ONE_ARCHIVED_CARD_REQUIRED")
            card=cards[0];raw=_raw(card,clock);text=_decode(raw,card.get("content_type",""));carrier=source["normalized_evidence"]["race_card_tables"]
            if carrier["value"]!=_html_tables(text) or carrier["source_id"]!=card["source_id"] or carrier["snapshot_sha256"]!=card["snapshot_sha256"]:
                raise ValueError("ID_HISTORY_CARD_RAW_NORMALIZED_MISMATCH")
            row_ids=_card_ids(text,card["final_url"]);candidate=parse_race_card(source)
            active=(source.get("active_runner_universe") or source.get("official_runner_universe") or{}).get("runners",[])
            active_ids={str(x.get("runner_id") or x.get("horse_no")) for x in active}
            parser=witness.OriginalTables();parser.feed(text)
            independent=witness.parse_original_runners(parser,source,{"runners":[{"runner_id":rid,"name":candidate[rid]["name"]} for rid in active_ids]})
            archive_day=date.fromisoformat(str(source["source_race_context"]["race_date"]).replace("/","-"))
            for rid in active_ids:
                if rid not in row_ids:raise ValueError("ID_HISTORY_CARD_NATIVE_LINK_MISSING")
                native,label,url=row_ids[rid]
                if native not in ids:continue
                if label!=normalize(candidate[rid]["name"]):raise ValueError("ID_HISTORY_SAME_ROW_LABEL_CONFLICT")
                pairs=list(zip(candidate[rid]["starts"],independent[rid]["history"]))
                if len(candidate[rid]["starts"])!=len(independent[rid]["history"]) or any(_day(a)!=b["date"] or _day(a)>=archive_day for a,b in pairs):
                    raise ValueError("ID_HISTORY_INDEPENDENT_CARD_HISTORY_CONFLICT")
                add(native,pairs,{**common,"source_id":card["source_id"],"snapshot_sha256":card["snapshot_sha256"],
                    "raw_sha256":card["raw_sha256"],"fetched_at":card["fetched_at"],"kind":"DIRECT_NATIVE_ID_CARD_LAST5",
                    "official_horse_link":url,"archived_runner_id":rid})
        for snapshot in source["sources"]:
            if historical is not None and snapshot.get("source_class")=="OFFICIAL_SAME_DAY_RACE_RESULT_PASSING_ORDER":
                if snapshot.get("raw_sha256") in seen_result_raw:continue
                try:
                    raw=_raw(snapshot,clock)
                    # This is a bounded search of already verified bytes, only
                    # to avoid parsing unrelated result tables. The actual
                    # Native-ID decision below still requires its same-row link.
                    if not any(native.removeprefix("NAR:").encode() in raw for native in ids):
                        seen_result_raw.add(snapshot["raw_sha256"]);continue
                    matched=_result_pairs(snapshot,raw,historical,ids,target,clock)
                    seen_result_raw.add(snapshot["raw_sha256"])
                    for native,pair,link in matched:
                        add(native,[pair],{**common,"source_id":snapshot["source_id"],"snapshot_sha256":snapshot["snapshot_sha256"],
                            "raw_sha256":snapshot["raw_sha256"],"fetched_at":snapshot["fetched_at"],
                            "kind":"DIRECT_NATIVE_ID_RESULT_AND_EXACT_EVENT_CSV", "official_horse_link":link,
                            "historical_csv_capture":csv_ref,"supplemental_source_refs":[csv_ref["source_id"],csv_ref["snapshot_sha256"],csv_ref["raw_sha256"]]})
                except (ValueError,KeyError,TypeError) as exc:holds.append({"source_id":snapshot.get("source_id"),"reason":str(exc)})
                continue
            if snapshot.get("source_class")!="OFFICIAL_HORSE_HISTORY_PROFILE":continue
            query=parse_qs(urlsplit(snapshot.get("requested_url","")).query);got=query.get("k_lineageLoginCode") or[]
            if len(got)!=1 or "NAR:"+got[0] not in ids or (got[0],snapshot.get("raw_sha256")) in seen_profile_raw:continue
            try:
                raw=_raw(snapshot,clock);native,pairs=_profile_pairs(snapshot,raw,target,clock)
                seen_profile_raw.add((got[0],snapshot["raw_sha256"]))
                add(native,pairs,{**common,"source_id":snapshot["source_id"],"snapshot_sha256":snapshot["snapshot_sha256"],
                    "raw_sha256":snapshot["raw_sha256"],"fetched_at":snapshot["fetched_at"],"kind":"DIRECT_NATIVE_ID_HORSE_PROFILE",
                    "official_horse_link":snapshot["requested_url"]})
            except (ValueError,KeyError,TypeError) as exc:holds.append({"source_id":snapshot.get("source_id"),"reason":str(exc)})
    for native,item in entries.items():
        events=sorted(((key,pair) for key,pair in item.pop("_events").items() if pair!="HOLD"),reverse=True)
        item["all_observed_dated_starts"]=len(events)
        selected=events[:5];item["starts"]=[v[0] for k,v in selected];item["independent_history"]=[v[1] for k,v in selected]
        for (day,venue),(start,direct) in selected:
            positions=start.get("content_positions") or[];field=start.get("field_size")
            if venue in {"船橋","船橋ナ","FNB"} and start.get("surface")=="DIRT" and positions:
                item["context_observations"].append({"event_date":day.isoformat(),"venue_label":start["venue"],
                    "distance_m":start.get("distance"),"going":start.get("going"),"field_size":field,"finish":start.get("finish"),
                    "printed_position_sequence":deepcopy(positions),"horse_id":native,
                    "identity_basis":"ACTUAL_ARCHIVED_NATIVE_ID_OFFICIAL_LINK_NOT_CURRENT_LABEL_JOIN",
                    "history_source_provenance":deepcopy(start.get("history_source_provenance",[]))})
        item["source_refs"]=sorted(set(item["source_refs"]));item["latest_observed_start_date"]=selected[0][0][0].isoformat() if selected else None
        item["used_envelope_paths"]=sorted({p["envelope_path"] for p in item["provenance"]})
    used_paths=sorted({p for item in entries.values() for p in item["used_envelope_paths"]})
    receipt={"profile":PROFILE,"as_of":clock.astimezone(timezone.utc).isoformat(),"target_race_date":target.isoformat(),
        "native_ids_requested":sorted(ids),"envelope_signatures_verified":verified,"input_manifest":manifest,
        "input_manifest_sha256":_hash(manifest),"holds":holds,"hold_count":len(holds),
        "selected_last5_observed_starts":sum(len(e["starts"]) for e in entries.values()),
        "native_ID_entries_with_history":sum(bool(e["starts"]) for e in entries.values()),
        "used_envelope_paths":used_paths,"embedded_envelope_bytes_used":envelope_raw_by_sha is not None,
        "historical_csv_supplement":csv_ref,"historical_csv_bytes_reparsed":historical is not None,
        "current_label_composite_join_used":False,"ID_inferred_or_decoded":False,
        "formal_source_or_consumer_grant":False,"history_completeness_claimed":False,"new_network_requests":0}
    receipt["sha256"]=_hash(receipt)
    return {"entries":entries,"receipt":receipt,"holds":holds,"used_envelope_paths":used_paths}

from __future__ import annotations
import base64,gzip,html,re,unicodedata
from html.parser import HTMLParser
from typing import Any,Dict,List,Tuple
from source_acquisition import _decode, sha_obj

PROFILE="KM-JRA-OFFICIAL-RUNNER-UNIVERSE-v1.0-20260925"

def norm(v:Any)->str:
    return re.sub(r"\s+","",unicodedata.normalize("NFKC",html.unescape(str(v or "")))).strip()

def _raw(snapshot:Dict[str,Any])->bytes:
    return gzip.decompress(base64.b64decode(str(snapshot.get("raw_gzip_b64") or "")))

def _clean_name(v:Any)->str:
    s=unicodedata.normalize("NFKC",html.unescape(str(v or ""))).strip()
    s=re.sub(r"\s+"," ",s)
    s=re.sub(r"\s*\d+(?:\.\d+)?\s*\(\d+番人気\).*$","",s)
    s=re.sub(r"\s*\(\d+\.\d+\.\d+\.\d+\).*$","",s)
    return s.strip()

def extract_from_tables(tables:Any)->List[Dict[str,Any]]:
    if not isinstance(tables,list): raise ValueError("JRA_RACE_CARD_TABLES_REQUIRED")
    found={}
    for table in tables:
        if not isinstance(table,list): continue
        for row in table:
            if not isinstance(row,list) or len(row)<3: continue
            cells=[unicodedata.normalize("NFKC",str(x or "")).strip() for x in row]
            nums=[]
            for i,c in enumerate(cells[:4]):
                m=re.fullmatch(r"(?:枠)?(\d{1,2})(?:\D.*)?",c)
                if m: nums.append((i,int(m.group(1))))
            if len(nums)<2: continue
            frame=nums[0][1]; horse_no=nums[1][1]
            if not (1<=frame<=8 and 1<=horse_no<=18): continue
            name_idx=nums[1][0]+1
            if name_idx>=len(cells): continue
            name=_clean_name(cells[name_idx])
            if not name or norm(name) in {"馬名","競走馬"}: continue
            joined=" ".join(cells)
            status="CANCELLED" if ("出走取消" in joined or "競走除外" in joined) else "ACTIVE"
            bw=None; bwc=None
            for m in re.finditer(r"(?<!\d)(\d{3,4})\s*kg?\s*\(([+-]?\d+)\)",joined,re.I):
                bw=int(m.group(1)); bwc=int(m.group(2))
            rec={"runner_id":str(horse_no),"horse_no":horse_no,"frame_no":frame,
                 "name":name,"canonical_name":norm(name),"status":status,
                 "body_weight":bw,"body_weight_change":bwc}
            if horse_no in found and found[horse_no]["canonical_name"]!=rec["canonical_name"]:
                continue
            found[horse_no]=rec
    if not found: raise ValueError("JRA_RUNNER_UNIVERSE_EMPTY")
    return [found[k] for k in sorted(found)]

def enrich_source_artifact(artifact:Dict[str,Any])->Dict[str,Any]:
    ev=artifact.get("normalized_evidence") or {}
    rc=ev.get("race_card_tables") or {}
    if not isinstance(rc,dict) or not isinstance(rc.get("value"),list):
        raise ValueError("JRA_RACE_CARD_EVIDENCE_MISSING")
    declared=extract_from_tables(rc["value"])
    active=[x for x in declared if x["status"]=="ACTIVE"]
    base={"profile":PROFILE,"source_id":rc.get("source_id"),"source_snapshot_sha256":rc.get("snapshot_sha256")}
    declared_u={**base,"universe_type":"DECLARED","runner_count":len(declared),"runners":declared}
    declared_u["runner_universe_sha256"]=sha_obj(declared_u)
    active_u={**base,"universe_type":"ACTIVE","runner_count":len(active),"runners":active}
    active_u["runner_universe_sha256"]=sha_obj(active_u)
    artifact["jra_declared_runner_universe"]=declared_u
    artifact["jra_official_runner_universe"]=active_u
    artifact["jra_official_runner_universe_sha256"]=sha_obj(active_u)
    artifact["official_runner_universe"]=active_u
    artifact["official_runner_universe_sha256"]=active_u["runner_universe_sha256"]
    return artifact

def validate_request_runners(artifact:Dict[str,Any], runners:Any)->Tuple[bool,List[str]]:
    off=artifact.get("jra_official_runner_universe") or {}
    expected={int(x["horse_no"]):norm(x["name"]) for x in off.get("runners") or []}
    if not expected: return False,["JRA_OFFICIAL_RUNNER_UNIVERSE_EMPTY"]
    actual={}
    if isinstance(runners,list):
        for r in runners:
            try: actual[int(r.get("horse_no") or r.get("runner_id"))]=norm(r.get("horse_name") or r.get("name"))
            except Exception: pass
    errs=[]
    if set(actual)!=set(expected): errs.append("JRA_RUNNER_ID_SET_MISMATCH")
    for k in sorted(set(actual)&set(expected)):
        if actual[k] and expected[k] and actual[k]!=expected[k]:
            errs.append(f"JRA_RUNNER_NAME_MISMATCH:{k}")
    return not errs,errs

from __future__ import annotations
import re,unicodedata
from typing import Any,Dict,List
from source_acquisition import sha_obj

PROFILE="KM-JRA-AUXILIARY-EVIDENCE-v1.0-20260925"

def _norm(v:Any)->str:
    return re.sub(r"\s+","",unicodedata.normalize("NFKC",str(v or ""))).strip()

def _as_int(v):
    m=re.search(r"-?\d+",str(v or "").replace(",","")); return int(m.group(0)) if m else None

def _positions(v):
    return [int(x) for x in re.findall(r"\d+",str(v or ""))]

def build_same_day_bias(artifact:Dict[str,Any])->Dict[str,Any]:
    races=[]
    for field,w in sorted((artifact.get("normalized_evidence") or {}).items()):
        if not re.fullmatch(r"same_day_r\d{2}_result_tables",field): continue
        tables=(w or {}).get("value") if isinstance(w,dict) else None
        if not isinstance(tables,list): continue
        result=[]
        for table in tables:
            if not isinstance(table,list) or not table: continue
            head=[_norm(x) for x in table[0]]
            if not ("着順" in head and "馬番" in head and "馬名" in head): continue
            idx={h:i for i,h in enumerate(head)}
            for row in table[1:]:
                if not isinstance(row,list): continue
                try: finish=_as_int(row[idx["着順"]]); no=_as_int(row[idx["馬番"]])
                except Exception: continue
                if finish is None or no is None: continue
                pi=next((i for i,h in enumerate(head) if "コーナー" in h and "通過" in h),None)
                fi=next((i for i,h in enumerate(head) if h.startswith("枠")),None)
                result.append({"finish":finish,"horse_no":no,"horse_name":row[idx["馬名"]],
                               "frame_no":_as_int(row[fi]) if fi is not None and fi<len(row) else None,
                               "passing_positions":_positions(row[pi]) if pi is not None and pi<len(row) else []})
            if result:break
        if result:
            top3=[x for x in result if x["finish"]<=3]; winner=next((x for x in result if x["finish"]==1),None)
            races.append({"field":field,"field_size":len(result),"winner_last_corner":((winner or {}).get("passing_positions") or [None])[-1],"top3":top3,
                          "source_id":(w or {}).get("source_id"),"snapshot_sha256":(w or {}).get("snapshot_sha256")})
    top=[x for r in races for x in r["top3"]]; frames=[x["frame_no"] for x in top if x.get("frame_no")]
    out={"profile":"KM-JRA-SAME-DAY-POSITION-BIAS-v1.0-20260925-SHADOW","production_authority":False,
         "races_observed":len(races),"top3_observations":len(top),
         "front_at_last_corner_top3_rate":round(sum(1 for x in top if x.get("passing_positions") and x["passing_positions"][-1]<=3)/len(top),6) if top else None,
         "leader_at_last_corner_win_rate":round(sum(1 for r in races if r.get("winner_last_corner")==1)/len(races),6) if races else None,
         "inner_frame_top3_rate":round(sum(1 for x in frames if x<=3)/len(frames),6) if frames else None,
         "outer_frame_top3_rate":round(sum(1 for x in frames if x>=6)/len(frames),6) if frames else None,"races":races}
    out["sha256"]=sha_obj({k:v for k,v in out.items() if k!="sha256"}); return out

def build_race_card_seed(artifact:Dict[str,Any])->Dict[str,Any]:
    text=((artifact.get("normalized_evidence") or {}).get("race_card_text") or {}).get("value") or ""
    runners=(artifact.get("jra_official_runner_universe") or {}).get("runners") or []
    seeds=[]
    for r in runners:
        name=str(r.get("name") or ""); i=str(text).find(name); chunk=str(text)[i:i+2500] if i>=0 else ""
        sire=dam=damsire=""
        m=re.search(r"父[:：]\s*([^\s]+)",chunk); sire=m.group(1) if m else ""
        m=re.search(r"母[:：]\s*([^\s(]+)",chunk); dam=m.group(1) if m else ""
        m=re.search(r"母の父[:：]\s*([^\s)]+)",chunk); damsire=m.group(1) if m else ""
        seeds.append({"runner_id":r.get("runner_id"),"horse_no":r.get("horse_no"),"horse_name":name,
                      "body_weight":r.get("body_weight"),"body_weight_change":r.get("body_weight_change"),
                      "sire":sire,"dam":dam,"damsire":damsire})
    out={"profile":"KM-JRA-RACE-CARD-POPULATION-SEED-v1.0-20260925","production_authority":False,
         "population_fit_ready":False,"runner_count":len(seeds),"seeds":seeds,
         "rule":"Identity/current race-card seed only; do not infer population BVI from the current field."}
    out["sha256"]=sha_obj({k:v for k,v in out.items() if k!="sha256"}); return out

def enrich_with_auxiliary_evidence(artifact:Dict[str,Any])->Dict[str,Any]:
    ev={"profile":PROFILE,"production_authority":False,"same_day_position_bias":build_same_day_bias(artifact),"race_card_population_seed":build_race_card_seed(artifact)}
    ev["sha256"]=sha_obj({k:v for k,v in ev.items() if k!="sha256"})
    artifact["jra_auxiliary_evidence"]=ev
    artifact["jra_auxiliary_evidence_sha256"]=sha_obj(ev)
    return artifact

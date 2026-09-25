from __future__ import annotations
from typing import Any, Dict
from source_acquisition import sha_obj, utcnow

PROFILE="KM-JRA-OFFICIAL-MARKET-OBSERVATION-v1.0-20260926"

def build_market_observation(artifact:Dict[str,Any])->Dict[str,Any]:
    d=artifact.get("jra_official_race_card_detail") or {}
    rows=[]
    for x in d.get("runners") or []:
        rid=str(x.get("runner_id") or x.get("horse_no") or "")
        if not rid:continue
        rows.append({
          "runner_id":rid,
          "horse_no":x.get("horse_no"),
          "horse_name":x.get("horse_name"),
          "win_odds":x.get("win_odds"),
          "popularity_rank":x.get("popularity_rank"),
        })
    observed=sum(1 for x in rows if x.get("win_odds") is not None or x.get("popularity_rank") is not None)
    out={
      "profile":PROFILE,
      "status":"PASS" if observed else "NOT_YET_PUBLISHED",
      "official":True,
      "production_fact_authority":True,
      "observation_only":True,
      "stability_authority":False,
      "captured_at":utcnow(),
      "runner_count":len(rows),
      "observed_runner_count":observed,
      "runners":rows,
      "source_detail_sha256":artifact.get("jra_official_race_card_detail_sha256"),
      "rule":"A single official observation can support current market facts only. market_stability requires >=2 temporally ordered Signed SOURCE observations; no stability is synthesized here."
    }
    out["sha256"]=sha_obj({k:v for k,v in out.items() if k!="sha256"})
    return out

def enrich_with_market_observation(artifact:Dict[str,Any])->Dict[str,Any]:
    out=build_market_observation(artifact)
    artifact["jra_official_market_observation"]=out
    artifact["jra_official_market_observation_sha256"]=sha_obj(out)
    return artifact

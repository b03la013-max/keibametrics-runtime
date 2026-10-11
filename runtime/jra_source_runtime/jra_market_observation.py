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


# ------------------------------------------------ AKI-JRA v2.1 external_state
# Two temporally ordered official observations of win odds and going, taken by
# the SOURCE runtime itself before source_freeze_at. Nothing is interpolated:
# if either observation is incomplete (an active runner without odds, no going,
# a scratch between the fetches, a late or failed re-fetch) no series is
# published and AKI v2.1 keeps external_state = UNOBSERVABLE (information gate).
EXTERNAL_PROFILE="KM-JRA-AKI-EXTERNAL-TWO-POINT-OBSERVATION-v1.0-20261011"
EXTERNAL_TARGET_INTERVAL_SECONDS=75   # registered policy minimum is 60 s
EXTERNAL_CUTOFF_MARGIN_SECONDS=60


def _ts(x:str):
    import datetime as _d
    t=_d.datetime.fromisoformat(str(x).replace("Z","+00:00"))
    if t.tzinfo is None: raise ValueError("NAIVE_TIMESTAMP")
    return t


def _active_ids(artifact:Dict[str,Any])->set:
    u=artifact.get("jra_official_runner_universe") or {}
    return {str(x.get("runner_id") or int(x["horse_no"])) for x in u.get("runners") or []
            if str(x.get("status") or "ACTIVE").upper()=="ACTIVE"}


def official_observation(detail:Dict[str,Any],snap:Dict[str,Any],active:set):
    """One AKI external observation, or (None, reason). Never fills gaps."""
    if not active: return None,"RUNNER_UNIVERSE_MISSING"
    if snap.get("official") is not True or snap.get("authority")!="JRA_OFFICIAL": return None,"NOT_OFFICIAL"
    if snap.get("cutoff_relation")!="PRE_CUTOFF": return None,"NOT_PRE_CUTOFF"
    going=(detail.get("race_environment") or {}).get("going")
    if not going: return None,"GOING_NOT_PUBLISHED"
    odds={}
    for x in detail.get("runners") or []:
        rid=str(x.get("runner_id") or x.get("horse_no") or "")
        if rid in active:
            v=x.get("win_odds")
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not v>0 or v!=v or v==float("inf"):
                return None,"WIN_ODDS_MISSING:"+rid
            odds[rid]=float(v)
    if set(odds)!=active: return None,"RUNNER_SET_MISMATCH"
    return {
        "observed_at":snap["fetched_at"],
        "production_fact_authority":True,
        "source_authority":"JRA_OFFICIAL",
        "evidence_refs":["SOURCE-SNAPSHOT:"+snap["snapshot_sha256"]],
        "source_fact":{"source_id":snap.get("source_id"),"raw_sha256":snap.get("raw_sha256"),
                       "final_url":snap.get("final_url"),"fields":"runners[].win_odds, race_environment.going",
                       "runner_count":len(odds)},
        "win_odds":odds,
        "going":going,
    },None


def attach_aki_external_observations(artifact:Dict[str,Any],prediction_cutoff:str,*,refetch,
                                     sleep=None,now=None)->Dict[str,Any]:
    """Re-observe the official card >= EXTERNAL_TARGET_INTERVAL_SECONDS after the
    primary detail fetch and publish artifact['aki_external_observations'] only
    when both observations are complete and ordered."""
    import time as _time_mod, datetime as _d
    sleep=sleep or _time_mod.sleep
    now=now or (lambda:_d.datetime.now(_d.timezone.utc))
    status={"profile":EXTERNAL_PROFILE,"status":"UNAVAILABLE","target_interval_seconds":EXTERNAL_TARGET_INTERVAL_SECONDS}
    def done(reason=None,series=None):
        if series:
            artifact["aki_external_observations"]=series
            artifact["aki_external_observations_sha256"]=sha_obj(series)
            status.update(status="PASS",observation_count=len(series),
                          interval_seconds=(_ts(series[-1]["observed_at"])-_ts(series[0]["observed_at"])).total_seconds())
        else:
            artifact.pop("aki_external_observations",None); artifact.pop("aki_external_observations_sha256",None)
            status["reason"]=reason
        artifact["aki_external_observation_status"]=status
        return artifact
    detail=artifact.get("jra_official_race_card_detail") or {}
    snap1=next((x for x in artifact.get("sources") or []
                if x.get("source_id")=="JRA-OFFICIAL-RACE-CARD-DETAIL"
                and x.get("snapshot_sha256")==detail.get("source_snapshot_sha256")),None)
    if not detail or not snap1: return done("PRIMARY_DETAIL_SNAPSHOT_MISSING")
    active=_active_ids(artifact)
    obs1,why=official_observation(detail,snap1,active)
    if obs1 is None: return done("FIRST:"+why)
    try:
        t1=_ts(obs1["observed_at"]); cutoff=_ts(prediction_cutoff)
    except Exception as e:
        return done("TIMESTAMP_INVALID:"+type(e).__name__)
    wait=EXTERNAL_TARGET_INTERVAL_SECONDS-(now()-t1).total_seconds()
    if now()+_d.timedelta(seconds=max(0,wait)+EXTERNAL_CUTOFF_MARGIN_SECONDS)>cutoff:
        return done("INSUFFICIENT_TIME_BEFORE_CUTOFF")
    if wait>0: sleep(wait)
    try:
        detail2,snap2=refetch()
    except Exception as e:
        return done("REOBSERVATION_FAILED:"+type(e).__name__+":"+str(e)[:160])
    obs2,why=official_observation(detail2,snap2,active)
    if obs2 is None: return done("SECOND:"+why)
    t2=_ts(obs2["observed_at"])
    if t2>cutoff: return done("SECOND_AFTER_CUTOFF")
    if (t2-t1).total_seconds()<EXTERNAL_TARGET_INTERVAL_SECONDS-5: return done("INTERVAL_TOO_SHORT")
    artifact["sources"]=list(artifact.get("sources") or [])+[snap2]
    status["reobservation_detail_sha256"]=sha_obj(detail2)
    return done(series=[obs1,obs2])

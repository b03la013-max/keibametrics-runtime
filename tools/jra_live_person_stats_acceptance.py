"""Mechanical current-card probe; never creates a prediction or historical SOURCE."""
from datetime import datetime, timedelta
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime/jra_source_runtime'))
from jra_race_day_resolver import JST, resolve_meetings, resolve_day
from jra_race_card_detail import _discover_and_fetch, parse_race_card_detail
from jra_person_stats import enrich_with_person_stats


def select_current_card(now, *, meetings=resolve_meetings, resolve=resolve_day):
    failures=[]
    for offset in range(8):
        day=(now+timedelta(days=offset)).date().isoformat()
        try:venues=meetings(day)
        except Exception as exc:
            failures.append({'date':day,'error':type(exc).__name__+':'+str(exc)[:200]});continue
        for venue in venues:
            try:
                key,races=resolve(day,venue)
                if not races:continue
                race=races[0]
                if type(race.get('field_size')) is not int or race['field_size']<=0:
                    raise ValueError('OFFICIAL_EXPECTED_RUNNER_COUNT_MISSING')
                return day,venue,key,race
            except Exception as exc:
                failures.append({'date':day,'venue':venue,'error':type(exc).__name__+':'+str(exc)[:200]})
    raise ValueError('JRA_CURRENT_CARD_UNAVAILABLE:'+json.dumps(failures,ensure_ascii=False))


def main():
    now=datetime.now(JST)
    day,venue,key,race=select_current_card(now)
    raw,headers,url,tokens=_discover_and_fetch(day,key,race['race_no'])
    detail=parse_race_card_detail(raw,headers.get('content-type',''))
    runners=detail['runners'];expected=race['field_size']
    if len(runners)!=expected:raise ValueError('OFFICIAL_DECLARED_RUNNER_COUNT_MISMATCH')
    for name in ['jockey_profile_token','trainer_profile_token','horse_profile_token']:
        missing=[r['runner_id'] for r in runners if not r.get(name)]
        if missing:raise ValueError('JRA_CURRENT_DIRECT_TOKEN_MISSING:'+name+':'+str(missing))
    # This deadline bounds present factual capture. It is NOT a pre-race cutoff
    # and must never be passed to a Production prediction or backdated SOURCE.
    deadline=(now+timedelta(minutes=10)).isoformat()
    artifact={'family_id':'JRA','race_id':f'JRA-LIVE-MECHANICAL-{day}-{key}-{race["race_no"]}',
              'jra_official_race_card_detail':detail,'jra_official_horse_history':{'runners':{}},'sources':[]}
    artifact,errors=enrich_with_person_stats(artifact,deadline,require_person_stats=True,max_workers=2)
    if errors:raise ValueError('JRA_PERSON_STATS_FAILED:'+str(errors))
    stats=artifact['jra_official_person_stats']
    for name in ['matched_jockey_count','matched_trainer_count','direct_jockey_token_count','direct_trainer_token_count']:
        if stats[name]!=expected:raise ValueError('JRA_PERSON_STATS_COVERAGE_INCOMPLETE:'+name)
    if not all((r.get('jockey') or {}).get('current_year_flat') and
               (r.get('trainer') or {}).get('current_year_flat') for r in stats['runners'].values()):
        raise ValueError('JRA_CURRENT_YEAR_PERSON_STATS_INCOMPLETE')
    record={'profile':'KM-JRA-CURRENT-PERSON-STATS-MECHANICAL-ACCEPTANCE-v1','status':'PASS',
            'classification':'CURRENT-OBSERVATION / MECHANICAL / NO-OOS / NOT-A-PREDICTION',
            'race_date':day,'venue':venue,'meeting_key':key,'race_no':race['race_no'],
            'observed_at':datetime.now(JST).isoformat(),'official_url':url,
            'raw_sha256':hashlib.sha256(raw).hexdigest(),'expected_declared_runners':expected,
            'matched_jockey_count':stats['matched_jockey_count'],
            'matched_trainer_count':stats['matched_trainer_count'],
            'historical_source_claim':False,'prediction_authority':False,'actual_purchase':False}
    run_id=os.environ.get('GITHUB_RUN_ID','local')
    if not run_id.isdigit() and run_id!='local':raise ValueError('PROBE_RUN_ID_INVALID')
    path=ROOT/'runtime/acceptance/jra_person_stats_live'/(run_id+'.json')
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():raise ValueError('PROBE_RECORD_ALREADY_EXISTS')
    path.write_text(json.dumps(record,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps(record,ensure_ascii=False))


if __name__=='__main__':main()

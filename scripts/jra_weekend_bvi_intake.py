"""Owner-authorized weekend re-acquisition through existing JRA BVI trust gates.

Only public dates/counts are queued. Blood-B rows and ratings are never converted
to JRA evidence. Admission requires actual original-workflow OIDC verification.
"""
from __future__ import annotations
import argparse
import hashlib
from datetime import date, datetime, timedelta, timezone
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
sys.path.insert(0, str(ROOT / 'runtime/jra_source_runtime'))
PROFILE = 'KM-JRA-WEEKEND-OFFICIAL-BVI-INTAKE-v1'


def resolve_scheduled_target(schedule, *, run_created_at, observed_at=None):
    """Resolve a delayed existing cron from the immutable original run clock.

    GitHub's original ``created_at`` remains the anchor on later attempts. The
    most recent past due slot is only an inferred scheduling reference, not a
    horse observation/capture time or proof that an official race exists.
    Discovery, acquisition clocks and cutoff checks remain unchanged.
    """
    schedules = {
        '20 21 * * 5,6,0': (21, {5, 6, 0}, 'cards'),
        '20 12 * * 6,0,1': (12, {6, 0, 1}, 'results'),
    }
    if not isinstance(schedule, str) or schedule not in schedules:
        raise ValueError('INTAKE_SCHEDULE_UNSUPPORTED')
    observed_at = observed_at if observed_at is not None else datetime.now(timezone.utc)
    for stamp in (run_created_at, observed_at):
        if not isinstance(stamp, datetime) or stamp.utcoffset() is None:
            raise ValueError('INTAKE_SCHEDULE_AWARE_CLOCK_REQUIRED')
    created = run_created_at.astimezone(timezone.utc)
    observed = observed_at.astimezone(timezone.utc)
    if created > observed:
        raise ValueError('INTAKE_SCHEDULE_RUN_CREATED_IN_FUTURE')
    hour, weekdays, mode = schedules[schedule]
    due = None
    for offset in range(8):
        day = created.date() - timedelta(days=offset)
        candidate = datetime(day.year, day.month, day.day, hour, 20, tzinfo=timezone.utc)
        # Python Monday=0, cron Sunday=0; evaluate the cron in UTC.
        if (candidate.weekday() + 1) % 7 in weekdays and candidate <= created:
            due = candidate
            break
    if due is None or created - due >= timedelta(days=1):
        raise ValueError('INTAKE_SCHEDULE_STALE_OR_AMBIGUOUS_REFERENCE')
    return {
        'schedule': schedule,
        'run_created_at': created.isoformat(),
        'inferred_due_at': due.isoformat(),
        'observed_at': observed.isoformat(),
        'date': due.astimezone(timezone(timedelta(hours=9))).date().isoformat(),
        'mode': mode,
        'reference_scope': 'SCHEDULING_ONLY_NOT_SOURCE_CAPTURE_OR_PREDICTION_EVIDENCE',
    }


def windows(plan, now=None):
    now = now or datetime.now(timezone.utc)
    jst = now.astimezone(timezone(timedelta(hours=9)))
    if plan.get('profile') != PROFILE or plan.get('input_policy') != 'JRA_OFFICIAL_REACQUISITION_ONLY':
        raise ValueError('INTAKE_PLAN_POLICY_INVALID')
    if plan.get('historical_prediction_rewrite') is not False:
        raise ValueError('HISTORICAL_REWRITE_FORBIDDEN')
    rows = plan.get('dates')
    if not isinstance(rows, list) or not 1 <= len(rows) <= 2:
        raise ValueError('INTAKE_DATE_COUNT_INVALID')
    result = []; seen = set()
    for row in rows:
        day = date.fromisoformat(row['date'])
        if day in seen or row['expected_races'] not in (12, 24, 36):
            raise ValueError('INTAKE_DATE_OR_RACE_COUNT_INVALID')
        seen.add(day)
        # Same-day result research is allowed only after the full afternoon card.
        # This gate does not assert JRA result availability: discovery must pass.
        if day > jst.date() or (day == jst.date() and jst.hour < 19):
            continue
        for start in range(0, row['expected_races'], 3):
            result.append({'date':day.isoformat(),'start':start})
    return result


def verify_admission(path, *, now=None):
    from jra_pedigree_corpus import _verified_harvest, build_corpus
    now = now or datetime.now(timezone.utc)
    obj = _verified_harvest(path, not_after=now)
    if obj is None:
        raise ValueError('JRA_ORIGINAL_WORKFLOW_OIDC_OR_CONTENT_INVALID')
    if obj.get('mode') not in ('results','cards') or obj.get('max_races') != 3:
        raise ValueError('INTAKE_RESULT_WINDOW_INVALID')
    if not obj['horse_token_count'] or obj['horse_count'] / obj['horse_token_count'] < .90:
        raise ValueError('INTAKE_OFFICIAL_COVERAGE_BELOW_FLOOR')
    # Prove the untouched production reader actually consumes these bytes.
    # A temporary archive limits verification cost; it grants no test verifier.
    with tempfile.TemporaryDirectory() as tmp:
        dest=Path(tmp)/'runtime/pedigree_corpus'/path.name
        dest.parent.mkdir(parents=True);shutil.copyfile(path,dest)
        target_day=(max(date.fromisoformat(obj['race_date']),now.astimezone(timezone(timedelta(hours=9))).date())
                    if obj['mode']=='cards' else
                    max(date.fromisoformat(obj['race_date'])+timedelta(days=1),now.date()+timedelta(days=1)))
        corpus=build_corpus(tmp,prediction_cutoff=now.isoformat(),race_date=target_day.isoformat())
    key='ATTESTED_HARVEST:'+obj['sha256']
    if key not in corpus['snapshots']:
        raise ValueError('OFFICIAL_BVI_CORPUS_DID_NOT_CONSUME_HARVEST')
    return {'profile':PROFILE,'status':'OFFICIAL_BVI_CORPUS_ADMITTED',
            'file':path.name,'harvest_sha256':obj['sha256'],
            'verified_at':now.isoformat(),'harvested_at':obj['harvested_at'],
            'horse_count':obj['horse_count'],'horse_token_count':obj['horse_token_count'],
            'all_observed_profiles_collected':obj['horse_count']==obj['horse_token_count'],
            'prior_run_count':corpus['run_count'],
            'coverage_class':obj['coverage_class'],
            'earliest_eligible_target_race_date':target_day.isoformat(),
            'consumer':'runtime/jra_pedigree_corpus.py::build_corpus',
            'automatic_future_bvi_feature_compilation':True,
            'bvi_formula_changed':False,'historical_prediction_rewritten':False,
            'future_race_bvi_values_verified':False}


def day_plan(race_date, mode, *, client=None):
    """All officially observed races, using the existing three-race windows."""
    from jra_pedigree_harvest import _Client, discover_day
    client=client or _Client(delay=1.3,stop_on_access_denied=True)
    races=discover_day(client,race_date,mode=mode)
    return [{'date':race_date,'mode':mode,'start':start,'expected_races':len(races),
             'race_ids':[r['race_id'] for r in races[start:start+3]],
             'official_races':races[start:start+3]}
            for start in range(0,len(races),3)]


def producer_valid(obj):
    body={k:v for k,v in obj.items() if k!='sha256'}
    return (obj.get('official') is True and obj.get('source')=='www.jra.go.jp'
            and obj.get('sha256')==hashlib.sha256(json.dumps(body,ensure_ascii=False,sort_keys=True).encode()).hexdigest())


def stored_windows(root,day,mode,start):
    stem=f"{day.replace('-','')}-{mode}-race{start}-r3"
    return sorted((Path(root)/'runtime/pedigree_corpus').glob(stem+'*.json'))


def collect_window(window,root=ROOT,*,run_id, verifier=None, collector=None):
    """Retain old bytes, retry missing profiles only, and isolate bad data."""
    from jra_pedigree_corpus import _verified_harvest
    from jra_pedigree_harvest import harvest_day
    root=Path(root);now=datetime.now(timezone.utc)
    check=verifier or (lambda p:_verified_harvest(p,not_after=now))
    receipt_dir=root/'runtime/pedigree_intake_receipts';receipt_dir.mkdir(parents=True,exist_ok=True)
    if not str(run_id).replace('-','').isalnum():raise ValueError('INTAKE_RUN_ID_INVALID')
    for prior in receipt_dir.glob(f'*{run_id}*-acquisition.json'):
        if json.loads(prior.read_text()).get('access_refused') is True:
            return {'status':'DEFERRED_ACCESS_REFUSED','new':False,'access_refused':True}
    day,mode,start=window['date'],window['mode'],int(window['start'])
    if mode not in ('cards','results') or start not in range(0,36,3):raise ValueError('INTAKE_WINDOW_INVALID')
    files=stored_windows(root,day,mode,start)
    for file in files:
        obj=check(file)
        if (obj and obj['horse_count']==obj['horse_token_count'] and obj['horse_count']>0
                and [r['race_id'] for r in obj.get('race_observations',[])]==window['race_ids']
                and all(r.get('universe_status')=='OBSERVED_OFFICIAL' for r in obj.get('race_observations',[]))):
            return {'status':'ALREADY_VERIFIED_COMPLETE','new':False,'file':str(file.relative_to(root)),
                    'harvest_sha256':obj['sha256'],'horse_count':obj['horse_count']}
    cache={}
    for path in sorted((root/'runtime/pedigree_corpus').glob(f"{day.replace('-','')}-{mode}-race*.json")):
        obj=check(path)
        if not obj or not producer_valid(obj):continue
        for h in obj['horses']:
            cache.setdefault(h['profile_token_sha256'],{**h,'reused_from_harvest_sha256':obj['sha256']})
    stem=f"{day.replace('-','')}-{mode}-race{start}-r3"
    file=root/'runtime/pedigree_corpus'/(stem+(f'-retry-{run_id}' if files else '')+'.json')
    if file.exists():raise ValueError('INTAKE_IMMUTABLE_OUTPUT_EXISTS')
    record={'date':day,'mode':mode,'start':start,'run_id':str(run_id),'new':False,
            'status':'ACQUISITION_FAILED','access_refused':False,'started_at':now.isoformat()}
    try:
        obj=(collector or harvest_day)(day,mode=mode,start_race=start,max_races=3,delay=1.3,existing_horses=cache)
        record['access_refused']=obj.get('access_refused',False)
        if not producer_valid(obj):raise ValueError('INTAKE_PRODUCER_DIGEST_INVALID')
        observed=obj.get('race_observations') or []
        if [r['race_id'] for r in observed]!=window['race_ids']:
            raise ValueError('INTAKE_OFFICIAL_RACE_UNIVERSE_CHANGED')
        if any(r.get('universe_status')!='OBSERVED_OFFICIAL' for r in observed):
            raise ValueError('INTAKE_OFFICIAL_RACE_UNIVERSE_UNRESOLVED')
        if (record['access_refused'] or not obj['horse_token_count']
                or obj['horse_count']/obj['horse_token_count']<.90):
            quarantine=receipt_dir/f'{stem}-{run_id}-quarantine.json'
            if quarantine.exists():raise ValueError('INTAKE_IMMUTABLE_QUARANTINE_EXISTS')
            quarantine.write_text(json.dumps(obj,ensure_ascii=False,indent=1)+'\n')
            record.update(status='QUARANTINED_ACQUISITION',quarantine=str(quarantine.relative_to(root)))
        else:
            file.parent.mkdir(parents=True,exist_ok=True)
            file.write_text(json.dumps(obj,ensure_ascii=False,indent=1)+'\n')
            record.update(status='ACQUIRED_NOT_YET_OIDC_VERIFIED',new=True,file=str(file.relative_to(root)),
                          harvest_sha256=obj['sha256'],horse_count=obj['horse_count'])
    except Exception as exc:
        import urllib.error
        record['access_refused']=record.get('access_refused',False) or (
            isinstance(exc,urllib.error.HTTPError) and exc.code in (403,429))
        record['error']=f'{type(exc).__name__}:{exc}'[:250]
    record['completed_at']=datetime.now(timezone.utc).isoformat()
    target=receipt_dir/f'{stem}-{run_id}-acquisition.json'
    if target.exists():raise ValueError('INTAKE_IMMUTABLE_ACQUISITION_RECEIPT_EXISTS')
    target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    return record


def pending_windows(plan, root=ROOT, now=None):
    """Partial admission is not collection completion; keep old bytes immutable."""
    pending=[]
    for window in windows(plan, now=now):
        stem=f"{window['date'].replace('-','')}-race{window['start']}"
        complete=False
        for receipt in (Path(root)/'runtime/pedigree_intake_receipts').glob(stem+'*.json'):
            record=json.loads(receipt.read_text())
            file=Path(root)/'runtime/pedigree_corpus'/record['file']
            if not file.is_file():
                continue
            raw=json.loads(file.read_text())
            if (record.get('status')=='OFFICIAL_BVI_CORPUS_ADMITTED'
                    and record.get('harvest_sha256')==raw.get('sha256')
                    and raw.get('horse_count',0)>0
                    and raw.get('horse_count')==raw.get('horse_token_count')):
                complete=True
                break
        if not complete:
            pending.append(window)
    return pending


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['matrix','admit','day-plan','collect-window'])
    p.add_argument('--plan',type=Path);p.add_argument('--file',type=Path);p.add_argument('--receipt',type=Path)
    p.add_argument('--date');p.add_argument('--mode',choices=['cards','results'],default='cards')
    p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--run-id');p.add_argument('--index',type=int)
    a=p.parse_args()
    if a.action=='day-plan':
        result=day_plan(a.date,a.mode)
        if a.plan:
            a.plan.parent.mkdir(parents=True,exist_ok=True)
            if a.plan.exists():raise ValueError('INTAKE_PLAN_IMMUTABLE')
            a.plan.write_text(json.dumps({'include':result},ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'include':result},ensure_ascii=False))
    elif a.action=='collect-window':
        from jra_pedigree_corpus import _attested
        if not _attested(a.plan,signer='km-jra-pedigree-corpus-harvest.yml',not_after=datetime.now(timezone.utc)):
            raise ValueError('INTAKE_DAY_PLAN_OIDC_UNVERIFIED')
        window=json.loads(a.plan.read_text())['include'][a.index]
        result=collect_window(window,a.root,run_id=a.run_id)
        if os.environ.get('GITHUB_OUTPUT'):
            with open(os.environ['GITHUB_OUTPUT'],'a') as out:
                out.write('new='+str(result['new']).lower()+'\n')
                out.write('file='+result.get('file','')+'\n')
        print(json.dumps(result,ensure_ascii=False))
    elif a.action=='matrix':
        if not a.plan:p.error('--plan required')
        print(json.dumps({'include':windows(json.loads(a.plan.read_text()))},separators=(',',':')))
    else:
        if not a.file or not a.receipt:p.error('--file and --receipt required')
        result=verify_admission(a.file)
        a.receipt.parent.mkdir(parents=True,exist_ok=True)
        a.receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()

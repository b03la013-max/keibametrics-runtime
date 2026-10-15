"""Owner-authorized weekend re-acquisition through existing JRA BVI trust gates.

Only public dates/counts are queued. Blood-B rows and ratings are never converted
to JRA evidence. Admission requires actual original-workflow OIDC verification.
"""
from __future__ import annotations
import argparse
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
sys.path.insert(0, str(ROOT / 'runtime/jra_source_runtime'))
PROFILE = 'KM-JRA-WEEKEND-OFFICIAL-BVI-INTAKE-v1'


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
    if obj.get('mode') != 'results' or obj.get('max_races') != 3:
        raise ValueError('INTAKE_RESULT_WINDOW_INVALID')
    if not obj['horse_token_count'] or obj['horse_count'] / obj['horse_token_count'] < .90:
        raise ValueError('INTAKE_OFFICIAL_COVERAGE_BELOW_FLOOR')
    # Prove the untouched production reader actually consumes these bytes.
    # A temporary archive limits verification cost; it grants no test verifier.
    with tempfile.TemporaryDirectory() as tmp:
        dest=Path(tmp)/'runtime/pedigree_corpus'/path.name
        dest.parent.mkdir(parents=True);shutil.copyfile(path,dest)
        target_day=max(date.fromisoformat(obj['race_date'])+timedelta(days=1),now.date()+timedelta(days=1))
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
    p=argparse.ArgumentParser();p.add_argument('action',choices=['matrix','admit'])
    p.add_argument('--plan',type=Path);p.add_argument('--file',type=Path);p.add_argument('--receipt',type=Path)
    a=p.parse_args()
    if a.action=='matrix':
        if not a.plan:p.error('--plan required')
        print(json.dumps({'include':windows(json.loads(a.plan.read_text()))},separators=(',',':')))
    else:
        if not a.file or not a.receipt:p.error('--file and --receipt required')
        result=verify_admission(a.file)
        a.receipt.parent.mkdir(parents=True,exist_ok=True)
        a.receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()

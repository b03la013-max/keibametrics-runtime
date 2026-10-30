"""Read-only official result corroboration in the existing KAW audit path.

No Runtime calls, SOURCE signing, Race registration, dispatch or FINAL creation.
These observations are explicitly post-event and cannot be pre-race evidence.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(ROOT/'runtime/local_physical')]
from local_physical.nar_source_manifest import _result_source, LOCAL_BABA_CODES
from local_physical.source_acquisition import fetch_source
from formal_execution_orchestrator import parse_official_result_snapshot


def acquire(day,race_no,out):
    context={'venue_id':'KAW','race_date':day,'race_no':race_no}
    spec=_result_source('KAW',LOCAL_BABA_CODES['KAW'],day.replace('-','/'),race_no)
    record={'context':context,'mode':'POST_RESULT_READ_ONLY','new_signatures':0,'url':spec['url']}
    try:
        # Deliberately preserve POST_CUTOFF; never relabel this as prestart.
        snap,errors=fetch_source(spec,day+'T00:00:00+09:00')
        record.update(raw_snapshot=snap,acquisition_errors=errors)
        order,payouts=parse_official_result_snapshot(snap,context,list(map(str,range(1,19))))
        record.update(status='VERIFIED',official_result={'finish_order':order,'payouts':payouts,'source':snap['final_url']})
    except Exception as exc:
        record.update(status='HOLD',original_error=type(exc).__name__+':'+str(exc))
    record['observed_at']=dt.datetime.now(dt.timezone.utc).isoformat()
    (out/f'{day}-R{race_no:02}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    return {k:v for k,v in record.items() if k!='raw_snapshot'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--date',default='2026-10-16');p.add_argument('--out',default='evidence/kaw_v26_20261016/official_readonly')
    args=p.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows=list(pool.map(lambda n:acquire(args.date,n,out),range(1,13)))
    (out/'summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(rows,ensure_ascii=False))

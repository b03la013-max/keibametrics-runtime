"""Resolve only the existing approved start-request push transport."""
import argparse
from datetime import date, datetime
import json
import os
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo


def resolve_start(*, event, requested_date='', mode='', changed=(), root=Path('.'), today=None):
    today=today or datetime.now(ZoneInfo('Asia/Tokyo')).date().isoformat()
    if event=='push':
        paths=[p for p in changed if p.startswith('runtime/jra_autopilot_start_requests/') and p.endswith('.json')]
        if len(paths)!=1:raise ValueError('JRA_START_EXACTLY_ONE_REQUEST_REQUIRED')
        obj=json.loads((root/paths[0]).read_text())
        requested_date=obj['race_date'];mode=obj.get('mode','loop')
        if obj.get('family_id','JRA')!='JRA':raise ValueError('JRA_START_FAMILY_MISMATCH')
    selected=requested_date or today
    if date.fromisoformat(selected).isoformat()!=selected:raise ValueError('JRA_START_DATE_INVALID')
    if selected!=today:raise ValueError('JRA_START_MUST_BE_RACE_DAY_USE_PREREGISTRATION_FOR_FUTURE_DATES')
    mode=mode or 'loop'
    if mode not in {'loop','tick'}:raise ValueError('JRA_START_MODE_INVALID')
    return {'race_date':selected,'mode':mode}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--event',required=True);p.add_argument('--date',default='');p.add_argument('--mode',default='');a=p.parse_args()
    changed=subprocess.check_output(['git','diff','--name-only','HEAD^','HEAD'],text=True).splitlines() if a.event=='push' else []
    resolved=resolve_start(event=a.event,requested_date=a.date,mode=a.mode,changed=changed)
    with open(os.environ['GITHUB_OUTPUT'],'a') as output:
        for key,value in resolved.items():output.write(f'{key}={value}\n')

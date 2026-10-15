"""Small read-only GitHub run summary; never a completion/signature verifier."""
import argparse
from datetime import datetime, timezone
import json
import subprocess


def summarize(run, jobs):
    rows=[]
    for job in jobs.get('jobs') or []:
        failed=[s for s in job.get('steps') or [] if s.get('conclusion')=='failure']
        active=[s for s in job.get('steps') or [] if s.get('status')=='in_progress']
        rows.append({'job':job['name'],'state':job['status'],'conclusion':job.get('conclusion'),
                     'current_step':active[0]['name'] if active else None,
                     'failed_step':failed[0]['name'] if failed else None})
    return {'run_id':run['id'],'state':run['status'],'conclusion':run.get('conclusion'),
            'url':run['html_url'],'updated_at':run.get('updated_at'),'jobs':rows,
            'checked_at':datetime.now(timezone.utc).isoformat(),
            'signature_verification_claim':False,
            'next_action':'READ_VERIFIED_ARTIFACTS' if run['status']=='completed' else 'EXTERNAL_RUN_CONTINUES'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run-id',type=int,required=True);a=p.parse_args()
    def get(path):
        r=subprocess.run(['gh','api',path],capture_output=True,text=True,timeout=15,check=True)
        return json.loads(r.stdout)
    path=f'repos/b03la013-max/keibametrics-runtime/actions/runs/{a.run_id}'
    print(json.dumps(summarize(get(path),get(path+'/jobs')),ensure_ascii=False))

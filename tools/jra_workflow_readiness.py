"""Read-only authenticated Actions-state evidence. Never enable or dispatch a workflow."""
import datetime
import json
import os
import urllib.request
import urllib.error
from pathlib import Path

WORKFLOWS=('km-jra-race-day-autopilot.yml','km-jra-race-intent-resolver.yml',
           'km-jra-formal-single-entry.yml','km-formal-request-runner.yml','km-formal-result-runner.yml')
NOT_BEFORE=datetime.datetime.fromisoformat('2026-10-18T12:47:36+00:00')


def classify(status, headers, body):
    headers={k.lower():v for k,v in headers.items()}
    if status==429 or (status==403 and (headers.get('x-ratelimit-remaining')=='0' or 'rate limit' in body.lower())):
        return 'RATE_LIMIT'
    if status in (401,403):return 'AUTHENTICATION_OR_PERMISSION'
    if status>=500:return 'TEMPORARY_PROVIDER_ERROR'
    if status==200:return 'OK'
    return 'OTHER_HTTP_ERROR'


def collect(token, *, now=None, opener=urllib.request.urlopen):
    now=now or datetime.datetime.now(datetime.timezone.utc)
    if now<NOT_BEFORE:return {'status':'NOT_DUE','not_before':NOT_BEFORE.isoformat(),'workflows':[]}
    if not token:return {'status':'AUTHENTICATED_TOKEN_UNAVAILABLE','workflows':[]}
    rows=[]
    for name in WORKFLOWS:
        url='https://api.github.com/repos/b03la013-max/keibametrics-runtime/actions/workflows/'+name
        request=urllib.request.Request(url,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'KeibaMetrics-readonly-readiness'})
        try:
            with opener(request,timeout=15) as response:
                status=response.status;headers=dict(response.headers);body=response.read().decode()
        except urllib.error.HTTPError as error:
            status=error.code;headers=dict(error.headers);body=error.read(4096).decode()
        except (urllib.error.URLError,TimeoutError) as error:
            rows.append({'workflow':name,'classification':'TEMPORARY_TRANSPORT_ERROR','error':str(error)[:200]});break
        headers={k.lower():v for k,v in headers.items()}
        result=classify(status,headers,body)
        row={'workflow':name,'http_status':status,'classification':result,
             'rate_remaining':headers.get('x-ratelimit-remaining'),'rate_reset':headers.get('x-ratelimit-reset'),
             'request_id':headers.get('x-github-request-id')}
        if status==200:
            obj=json.loads(body);row.update(workflow_id=obj.get('id'),state=obj.get('state'),path=obj.get('path'))
        else:row['error_body']=body[:1000]
        rows.append(row)
        if result!='OK':break  # never retry or flood after refusal
    return {'observed_at':now.isoformat(),'authenticated':True,'scope':'READ_ONLY_NO_DISPATCH_OR_ENABLE',
            'status':'VERIFIED' if len(rows)==len(WORKFLOWS) and all(r['classification']=='OK' for r in rows) else 'PARTIAL',
            'workflows':rows}


if __name__=='__main__':
    report=collect(os.environ.get('GH_TOKEN'))
    Path('workflow-readiness.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps(report))

"""Wait for the canonical Production artifact, never for optional Shadow jobs."""
import argparse
import json
import subprocess
import time


def select_artifact(run, artifacts):
    rid=run['id']
    if (run.get('repository',{}).get('full_name')!='b03la013-max/keibametrics-runtime'
            or run.get('head_repository',{}).get('full_name')!='b03la013-max/keibametrics-runtime'
            or run.get('head_branch')!='main' or run.get('path')!='.github/workflows/km-formal-request-runner.yml'
            or run.get('event') not in ('push','workflow_dispatch') or not run.get('head_sha')):
        raise ValueError('CANONICAL_RUN_AUTHORITY')
    matches=[a for a in artifacts if a.get('name')==f'krs-production-{rid}' and not a.get('expired')]
    if len(matches)>1: raise ValueError('PRODUCTION_ARTIFACT_NOT_UNIQUE')
    def bound(artifact):
        ref=artifact.get('workflow_run') or {}
        if ref.get('id')!=rid or ref.get('head_sha')!=run['head_sha']:raise ValueError('CANONICAL_ARTIFACT_RUN_BINDING')
        return artifact
    if matches:return bound(matches[0])
    # Compatibility only for completed old workflows, not a live Shadow archive.
    if run.get('status')=='completed':
        old=[a for a in artifacts if a.get('name')==f'krs-utility-{rid}' and not a.get('expired')]
        if len(old)==1:return bound(old[0])
        raise ValueError('CANONICAL_PRODUCTION_ARTIFACT_MISSING')
    return None


class ApiNoResponse(Exception):
    """The API gave no answer in time (transport timeout). Not a refusal."""


MAX_NO_RESPONSE=3


def wait(run_id, fetch, *, timeout=900, clock=time.monotonic, pause=time.sleep):
    # Case KYO-20261122-R07: one 20 s non-answer aborted the Single Entry after the
    # FINAL was already being built, so the pre-post Owner delivery never ran.
    # A non-answer is retried (bounded, inside the same deadline); a refusal
    # (permission / rate limit / HTTP error) is still never retried.
    end=clock()+timeout
    no_response=0
    while clock()<end:
        try:
            run=fetch(f'actions/runs/{run_id}')
            if str(run.get('id'))!=str(run_id):raise ValueError('CANONICAL_RUN_ID_MISMATCH')
            artifact=select_artifact(run,fetch(f'actions/runs/{run_id}/artifacts?per_page=100')['artifacts'])
        except ApiNoResponse:
            no_response+=1
            if no_response>MAX_NO_RESPONSE:raise
            pause(min(5,max(0,end-clock())))
            continue
        if artifact:return artifact
        pause(min(5,max(0,end-clock())))
    raise TimeoutError('CANONICAL_PRODUCTION_ARTIFACT_TIMEOUT')


def main():
    p=argparse.ArgumentParser();p.add_argument('--run-id',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    def fetch(path):
        # No repeated API request after permission/rate-limit/transport refusal.
        try:
            result=subprocess.run(['gh','api','repos/b03la013-max/keibametrics-runtime/'+path],
                                  capture_output=True,text=True,timeout=20)
        except subprocess.TimeoutExpired as exc:
            raise ApiNoResponse('CANONICAL_API_NO_RESPONSE:'+path) from exc
        if result.returncode:
            raise RuntimeError('CANONICAL_API_REFUSED:'+result.stderr[:400])
        return json.loads(result.stdout)
    artifact=wait(a.run_id,fetch)
    subprocess.run(['gh','run','download',a.run_id,'--name',artifact['name'],'--dir',a.output],check=True,timeout=60)


if __name__=='__main__':main()

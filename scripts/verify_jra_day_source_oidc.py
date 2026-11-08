"""Verify existing Oct17 SOURCE; public read-only API and official gh verifier.

Requires GitHub CLI with attestation support. Leaves signed artifacts unchanged.
"""
import pathlib,json,hashlib,urllib.request,urllib.error,subprocess,concurrent.futures,datetime,time
import argparse
parser=argparse.ArgumentParser(description='Read-only independent SOURCE Sigstore verification; no signing or production writes.')
parser.add_argument('--gh', default='gh', help='Path to official GitHub CLI')
args=parser.parse_args()
root=pathlib.Path(__file__).resolve().parents[1];out=root/'evidence/jra_day_review_20261017/source_oidc';out.mkdir(exist_ok=True)
def one(p):
 rid=p.parts[-5];digest=hashlib.sha256(p.read_bytes()).hexdigest();att=json.loads((p.parent/'source_attestation.json').read_text());rec={'race_id':rid,'source_path':str(p.relative_to(root)),'subject_sha256':digest,'expected_source_sha':att['sha'],'expected_run_id':att['run_id']}
 try:
  bundlepath=out/(rid+'.sigstore.json');url='https://api.github.com/repos/b03la013-max/keibametrics-runtime/attestations/sha256:'+digest
  if not bundlepath.exists():
   for attempt in range(3):
    try:
     obj=json.load(urllib.request.urlopen(url,timeout=25));break
    except urllib.error.HTTPError as exc:
     if exc.code in (400,401,403,404,422) or attempt==2:raise
     time.sleep(attempt+1)
    except Exception:
     if attempt==2:raise
     time.sleep(attempt+1)
   bundlepath.write_text('\n'.join(json.dumps(a['bundle']) for a in obj['attestations'])+'\n')
  cmd=[args.gh,'attestation','verify',str(p),'--repo','b03la013-max/keibametrics-runtime','--bundle',str(bundlepath),'--signer-workflow','b03la013-max/keibametrics-runtime/.github/workflows/km-jra-source-first-runner.yml','--source-digest',att['sha'],'--source-ref','refs/heads/main','--deny-self-hosted-runners','--format','json']
  run=subprocess.run(cmd,capture_output=True,text=True,timeout=120);rec['verifier_exit']=run.returncode
  (out/(rid+'.verification.json')).write_text(run.stdout if run.returncode==0 else json.dumps({'error':run.stderr}))
  if run.returncode:raise ValueError(run.stderr[-1200:])
  verified=json.loads(run.stdout);valid=[]
  for v in verified:
   vr=v['verificationResult'];statement=vr['statement'];inv=statement['predicate']['runDetails']['metadata']['invocationId'];valid.append('/runs/'+str(att['run_id'])+'/' in inv)
  if not any(valid):raise ValueError('RUN_ID_NOT_BOUND')
  rec.update(status='PASS',bundle_path=str(bundlepath.relative_to(root)),bundle_sha256=hashlib.sha256(bundlepath.read_bytes()).hexdigest(),verification_path=str((out/(rid+'.verification.json')).relative_to(root)),verification_sha256=hashlib.sha256((out/(rid+'.verification.json')).read_bytes()).hexdigest(),verified_attestations=len(verified),run_id_bound=True)
 except Exception as e:rec.update(status='BLOCKED',error=str(e))
 return rec
paths=sorted(root.glob('runtime/executions/KM-JRA-*-20261017-*-LIVE-R1/SOURCE/runs/*/source_receipt_envelope.json'))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 rows=[]
 for row in pool.map(one,paths):
  rows.append(row);print(row['race_id'],row['status'],flush=True)
report={'collected_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verifier':subprocess.check_output([args.gh,'--version'],text=True).splitlines()[0]+' / gh attestation verify','policy':'repo + exact source workflow + source SHA + refs/heads/main + GitHub-hosted + invocation run ID','rows':rows,'passed':sum(r['status']=='PASS' for r in rows),'total':len(rows),'production_effect':'NONE','warning':'Predicate run ID is a subject-bound workflow claim; certificate identity, source digest and signed transparency timestamps are independently verified by gh.'}
(out/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')

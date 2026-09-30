"""Offline recasting evidence. Run from repository root; no acquisition or purchase."""
import ast
import base64
import copy
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/recasting'
BASE = 'af4e9677e5f0a8b23ce429947a0e8e767fbee742'
sys.path.insert(0, str(ROOT / 'runtime'))
from execution_store import persist_phase, resolve_phase, ExecutionStoreError
from formal_execution_orchestrator import resume_plan
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def source_function(text, legacy=False, direct_formal=False):
    if legacy:
        if direct_formal:
            a=text.index('    source_req=req.get("source_acquisition_request")',text.index('if isinstance(provided_source,dict):'))
            b=text.index('\n# Signed SOURCE formal readiness',a)
            block=text[a:b]
            block+='\n    if source_artifact.get("formal_ready") is not True:\n        fail_closed("SOURCE_NOT_FORMAL_READY",source_artifact)\n'
        else:
            a=text.index('    race_meta=req.get("race")',text.index('if phase in {"SOURCE"'))
            b=text.index('    off=source_artifact.get',a)
            block=text[a:b]
        text='def acquire_verified_source(req, rid):\n'+block+'\n    return source, source_artifact\n'
    tree=ast.parse(text)
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='acquire_verified_source')
    def run(mode, failure):
        calls=[]; saved={}
        req={'venue_id':'FNB','race_date':'2026-09-29','race_no':6,'prediction_cutoff':'cutoff'}
        if mode=='manifest': req['required_source_manifest']=[{'id':'official'}]
        if mode=='request': req['source_acquisition_request']={'sources':[{'id':'official'}]}
        def call(path,payload,timeout):
            calls.append((path,copy.deepcopy(payload),timeout))
            if path.endswith('/local'):return 200,{'sources':[{'id':'official'}]}
            if path.endswith('/acquire'):
                return 200,{'receipt':{'status':'FAILED' if failure=='acquire' else 'SOURCE_FROZEN'},'artifact':{'formal_ready':failure!='readiness'}}
            return 200,{'valid':failure!='verify'}
        def fail(code,details):raise ValueError(code)
        env={'copy':copy,'call':call,'persist':lambda k,v:saved.update({k:v}),'fail_closed':fail}
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<source>','exec'),env)
        try:result=env['acquire_verified_source'](req,'race')
        except ValueError as e:result=str(e)
        return calls,saved,result,req
    return run

old=subprocess.check_output(['git','show',BASE+':runtime/non_jra_formal_runner.py'],cwd=ROOT,text=True)
new=(ROOT/'runtime/non_jra_formal_runner.py').read_text()
fresh=source_function(new)
checks=[]
for direct in (False,True):
    previous=source_function(old,legacy=True,direct_formal=direct)
    for mode in ('discovered','manifest','request'):
        for failure in (None,'acquire','verify','readiness'):
            checks.append({'old_path':'direct_formal' if direct else 'source','mode':mode,'failure':failure,'equivalent':previous(mode,failure)==fresh(mode,failure)})
assert all(x['equivalent'] for x in checks)
changed=subprocess.check_output(['git','diff',BASE,'--name-only','--','runtime','services','mapping','profiles'],cwd=ROOT,text=True).splitlines()
allowed={'runtime/execution_store.py','runtime/formal_execution_orchestrator.py','runtime/non_jra_formal_runner.py'}
assert set(changed)<=allowed,changed
# Reproduce old overwrite, confirm correction preserves original receipt.
import types
baseline=types.ModuleType('baseline_store'); baseline.__file__=str(ROOT/'runtime/execution_store.py')
exec(subprocess.check_output(['git','show',BASE+':runtime/execution_store.py'],cwd=ROOT,text=True),baseline.__dict__)
repro={}
for label,fn in [('before',baseline.persist_phase),('after',persist_phase)]:
    with tempfile.TemporaryDirectory() as d:
        d=pathlib.Path(d);src=d/'input';src.mkdir();p=src/'final_receipt_envelope.json';p.write_text('{"a":1}')
        fn('E','FORMAL','same',src,root=d/'store');p.write_text('{"a":2}')
        try:fn('E','FORMAL','same',src,root=d/'store');repro[label]='OVERWRITTEN'
        except ExecutionStoreError:repro[label]='REJECTED_ORIGINAL_PRESERVED'
assert repro=={'before':'OVERWRITTEN','after':'REJECTED_ORIGINAL_PRESERVED'}
report={'baseline':BASE,'source_equivalence_cases':checks,'protected_policy_files_changed':[],'changed_runtime_files':changed,'same_run_overwrite_reproduction':repro,'grade':'OFFLINE_STRUCTURAL_AND_MOCKED_DIFFERENTIAL; NOT LIVE OR OOS'}
(OUT/'equivalence.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'source_equivalence':str(len(checks))+'/'+str(len(checks)),'overwrite':repro,'protected_policy_files_changed':[]}))

# Offline receipt verification against the public key observed in the recorded health response.
health=json.loads((OUT/'runtime_health.json').read_text())
key=Ed25519PublicKey.from_public_bytes(base64.b64decode(health['health']['receipt_public_key_b64']))
canon=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
sha=lambda x:hashlib.sha256(canon(x)).hexdigest()
verified=[]
for phase in ('SOURCE','FORMAL'):
    resolved=resolve_phase('LOCAL-KM-LOCAL-FNB-20260929-R06-LIVE-R1-EXEC',phase)
    for p in sorted(resolved['run_dir'].glob('*receipt_envelope.json')):
        env=json.loads(p.read_text())
        key.verify(base64.b64decode(env['signature']),canon(env['receipt']))
        assert sha(env['receipt'])==env['receipt_sha256']
        assert sha(env['artifact'])==env['receipt']['artifact_sha256']
        verified.append(str(p.relative_to(ROOT)))
print(json.dumps({'locally_verified_receipt_files':len(verified),'distinct_receipts':4,'remote_verify':'SEE_EXTERNAL_VERIFICATION_JSON_THIS_SCRIPT_IS_OFFLINE','not_oos':True}))

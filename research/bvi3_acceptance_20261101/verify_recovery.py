"""Read-only original RESULT recovery plus explicitly separate fault injection."""
import json,sys,shutil,tempfile,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'runtime'))
import jra_static_owner_forward_oos as s
import jra_research_settlement_manifest as m
from family_authority_guard import resolve_current_authority
OUT=Path(__file__).resolve().parent
RACE='KM-JRA-TKY-20261031-R12'

def write(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def digest(path):
 import hashlib
 return hashlib.sha256(path.read_bytes()).hexdigest()

with tempfile.TemporaryDirectory(prefix='bvi3-recovery-') as td:
 root=Path(td)
 # Exactly the existing fingerprint's immutable dependencies.
 deps=next(c for c in s.fingerprint.__code__.co_consts if isinstance(c,tuple) and len(c)>10)
 paths=list(deps)+[f'runtime/jra_static_owner_forward_oos/{RACE}/pre_result.json',
 f'runtime/results/{RACE}.json',f'runtime/final_artifacts/{RACE}.json']
 paths += [str(p.relative_to(ROOT)) for p in (ROOT/'runtime/executions'/(RACE+'-LIVE-R1')/'RESULT/runs/41191875119').glob('*.json')]
 for name in paths:
  p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
 _,authority=resolve_current_authority(ROOT)
 contract=json.loads((ROOT/authority['common_family_components']['family_runtime_contracts_profile']).read_text())['families']['JRA']
 health=json.loads((ROOT/'tests/fixtures/jra_result_public_trust_20261101.json').read_text())
 def no_http(*a,**k):raise AssertionError('retained original RESULT must suffice')
 pre=root/f'runtime/jra_static_owner_forward_oos/{RACE}/pre_result.json';original=pre.read_bytes()
 first=s.settle(root,health_loader=lambda:(health,contract),fetch_result=no_http)
 second=s.settle(root,health_loader=lambda:(health,contract),fetch_result=no_http)
 diagnostic=json.loads(next(pre.parent.glob('result_match_diagnostic_*.json')).read_text())
 assert first['processing_manifest']['diagnostic_settled_count']==1
 assert second['processing_manifest']['already_complete_count']==1
 assert first['eligible_settled_races']==second['eligible_settled_races']==0
 assert pre.read_bytes()==original
 assert diagnostic['top3']==['7','10','8']
 proof={'status':'VERIFIED COMPLETE','scope':'SAVED_OFFICIAL_SIGNED_RESULT_RECOVERY_DIAGNOSTIC_NOT_NEW_OOS',
 'race_id':RACE,'original_input_hashes':{name:digest(ROOT/name) for name in paths},
 'original_prediction_unchanged':True,'first':first['processing_manifest'],'second':second['processing_manifest'],
 'diagnostic':diagnostic,'fixed_D_forward_increment':0,'new_HTTP_or_KRS':False,
 'signature_trust':'INHERITED_PUBLIC_TRUST_FIXTURE; NOT_NEW_LIVE_HEALTH'}
 write(OUT/'real_result_recovery.json',proof)
 # Injection has no effect on either canonical lane or any OOS count.
 directory=OUT/'failure_injection'
 def cmd(value,code=0):return [sys.executable,'-c','import json;print('+repr(json.dumps(value))+');raise SystemExit('+str(code)+')']
 m.run_stage('source_candidate',cmd({'profile':m.STAGE_PROFILES['source_candidate'],
 'processed':[{'race_id':'INJECTION_ONLY_NOT_A_RACE','status':'BLOCKED','reason':'INJECTED_DAY_TOKEN_FAILURE'}]},1),directory=directory,root=root)
 m.run_stage('static_owner',cmd(first),directory=directory,root=root)
 m.run_stage('bvi_env',cmd({'profile':m.STAGE_PROFILES['bvi_env'],'environment_candidate':
 {'profile':'KM-JRA-BVI-ENV-FOUR-ARM-FORWARD-SHADOW-v1','cohorts':{}}}),directory=directory,root=root)
 manifest=m.collect(directory);write(directory/'manifest.json',manifest)
 gate=subprocess.run([sys.executable,str(ROOT/'runtime/jra_research_settlement_manifest.py'),'gate',
 '--manifest',str(directory/'manifest.json')],capture_output=True,text=True)
 assert manifest['status']=='PARTIAL' and manifest['success_count']==1 and manifest['failure_count']==1 and gate.returncode==2
 write(OUT/'failure_injection_summary.json',{'classification':'INJECTION_ONLY_NOT_OOS','manifest_status':manifest['status'],
 'counts':{k:v for k,v in manifest.items() if k.endswith('_count')},'gate_exit':gate.returncode,'static_continued':True})
 print(json.dumps({'real_result_recovery':'PASS','failure_injection':'PARTIAL / gate exit 2','forward_increment':0}))

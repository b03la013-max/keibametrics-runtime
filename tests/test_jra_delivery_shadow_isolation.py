"""Durable isolation, real frozen input mutations, timeout and transport failures."""
import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tests')]
from test_jra_role_learning_repair import fixture
from jra_shadow_checkpoint import pack,execute,restore,write_once,validate,CODES,MODEL
from jra_role_learning_shadow import digest
from jra_formal_artifact_wait import wait,select_artifact


class IsolationTests(unittest.TestCase):
 def setup_root(self, folder):
  root=Path(folder)
  for name in (*CODES,MODEL,'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json'):
   p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/name).read_bytes())
  return root
 def test_checkpoint_real_input_binding_and_no_production_mutation(self):
  q,f,_=fixture();old=copy.deepcopy((q,f))
  with tempfile.TemporaryDirectory() as folder:
   root=self.setup_root(folder);c=pack(root,q,f,created_at=f['final_freeze_timestamp'])
   out=execute(root,c,verify_final=lambda x:self.assertEqual(x,f),clock=lambda:f['final_freeze_timestamp'])
   self.assertEqual(out['delivery_checkpoint_sha256'],c['sha256'])
   self.assertEqual(out['checkpoint_learning_input_sha256'],c['learning_input_sha256'])
   self.assertFalse(out['oos_eligible']);self.assertFalse((root/'runtime/final_artifacts').exists())
   self.assertEqual((q,f),old)
   again=execute(root,c,verify_final=lambda x:None,clock=lambda:f['final_freeze_timestamp'])
   self.assertEqual(again,out)
 def test_late_start_or_late_finish_cannot_create_shadow(self):
  q,f,_=fixture()
  for late_start in (True,False):
   with self.subTest(late_start=late_start),tempfile.TemporaryDirectory() as folder:
    root=self.setup_root(folder);c=pack(root,q,f,created_at=f['final_freeze_timestamp'])
    times=iter(['2026-10-18T23:59:00+09:00'] if late_start else [f['final_freeze_timestamp'],f['final_freeze_timestamp'],'2026-10-18T23:59:00+09:00'])
    with self.assertRaisesRegex(ValueError,'CUTOFF'):execute(root,c,verify_final=lambda x:None,clock=lambda:next(times))
    self.assertFalse((root/'runtime/role_rescue_shadow').exists())
 def test_shadow_exception_or_save_failure_cannot_mutate_final(self):
  q,f,_=fixture();old=copy.deepcopy(f)
  for target,error in [('jra_shadow_checkpoint.persist_shadow',RuntimeError('worker failed')),('jra_shadow_checkpoint.write_once',OSError('disk full'))]:
   with self.subTest(target=target),tempfile.TemporaryDirectory() as folder:
    root=self.setup_root(folder);c=pack(root,q,f,created_at=f['final_freeze_timestamp'])
    with patch(target,side_effect=error),self.assertRaises(type(error)):
     execute(root,c,verify_final=lambda x:None,clock=lambda:f['final_freeze_timestamp'])
    self.assertEqual(f,old);self.assertFalse((root/'runtime/final_artifacts').exists())
 def test_checkpoint_tampering_code_policy_model_or_learning_is_refused(self):
  q,f,_=fixture()
  with tempfile.TemporaryDirectory() as folder:
   root=self.setup_root(folder);c=pack(root,q,f,created_at=f['final_freeze_timestamp'])
   for key in ('request_sha256','source_sha256','runner_universe_sha256','policy_sha256','model_sha256','learning_input_sha256'):
    bad=copy.deepcopy(c);bad[key]='bad';bad['sha256']=digest({k:v for k,v in bad.items() if k!='sha256'})
    with self.subTest(key=key),self.assertRaises(ValueError):validate(root,bad)
   for kind in ('full20','evidence'):
    bad=copy.deepcopy(c)
    if kind=='full20':bad['request']['runners'][0]['canonical_components']['BVI']['value']+=1
    else:bad['request']['runners'][0]['evidence_features']['position_quality']['category']='VERY_WEAK'
    bad['request_sha256']=digest(bad['request']);bad['sha256']=digest({k:v for k,v in bad.items() if k!='sha256'})
    with self.subTest(kind=kind),self.assertRaises(ValueError):validate(root,bad)
   (root/CODES[0]).write_text('changed code')
   with self.assertRaisesRegex(ValueError,'CODE_POLICY'):validate(root,c)
 def test_immutable_duplicate_conflict_and_race_local_paths(self):
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'R01.json';write_once(p,{'x':1});write_once(p,{'x':1})
   with self.assertRaisesRegex(ValueError,'CONFLICT'):write_once(p,{'x':2})
   write_once(Path(folder)/'R02.json',{'x':2});self.assertEqual(json.loads(p.read_text()),{'x':1})
 def test_resume_archived_bytes_requires_original_pre_cutoff_witness(self):
  q,f,_=fixture()
  with tempfile.TemporaryDirectory() as folder:
   root=self.setup_root(folder);c=pack(root,q,f,created_at=f['final_freeze_timestamp'])
   out=execute(root,c,verify_final=lambda x:None,clock=lambda:f['final_freeze_timestamp'])
   with self.assertRaisesRegex(ValueError,'WITNESS'):restore(root,c,out,witness=lambda s:{'verified':False})
   self.assertEqual(restore(root,c,out,witness=lambda s:{'verified':True}),out)
 def test_signature_failure_never_executes_shadow(self):
  q,f,_=fixture()
  with tempfile.TemporaryDirectory() as folder:
   root=self.setup_root(folder);c=pack(root,q,f,created_at=f['final_freeze_timestamp'])
   with patch('jra_shadow_checkpoint.persist_shadow') as shadow:
    with self.assertRaisesRegex(ValueError,'SIGNATURE'):
     execute(root,c,verify_final=lambda x:(_ for _ in ()).throw(ValueError('SIGNATURE')),clock=lambda:f['final_freeze_timestamp'])
    shadow.assert_not_called()


def provider_run(status='in_progress'):
 return {'id':123,'status':status,'repository':{'full_name':'b03la013-max/keibametrics-runtime'},'head_repository':{'full_name':'b03la013-max/keibametrics-runtime'},'head_branch':'main','head_sha':'a'*40,'path':'.github/workflows/km-formal-request-runner.yml','event':'workflow_dispatch'}
def provider_artifact(name='krs-production-123'):
 return {'name':name,'expired':False,'id':1,'workflow_run':{'id':123,'head_sha':'a'*40}}

class WorkflowIsolationTests(unittest.TestCase):
 def test_production_and_shadow_dag_and_archive_order(self):
  j=yaml.safe_load((ROOT/'.github/workflows/km-formal-request-runner.yml').read_text())['jobs']
  p=j['formal-run'];s=j['shadow-run'];self.assertNotIn('needs',p);self.assertEqual(s['needs'],'formal-run');self.assertTrue(s['continue-on-error']);self.assertEqual(s['permissions']['actions'],'read')
  formal=next(x['run'] for x in p['steps'] if x.get('id')=='formal_execution')
  self.assertNotIn('from jra_shadow_checkpoint',formal);self.assertNotIn('persist_shadow(',formal);self.assertNotIn('build_mec_r4_shadow(',formal)
  self.assertIn('verify_aki_ticket_binding',formal);self.assertIn('fvcode,fv=call(KRS,"/verify",f',formal)
  names=[x.get('name','') for x in p['steps']]
  self.assertLess(names.index('Verify canonical FINAL availability after publication'),names.index('Upload KRS structured output and utility delta'))
  self.assertEqual(next(x['with']['name'] for x in p['steps'] if x.get('uses')=='actions/upload-artifact@v4'),'krs-production-${{ github.run_id }}')
  names=[x.get('name','') for x in s['steps']]
  self.assertLess(names.index('Archive Shadow independently before any Git push'),names.index('Persist immutable Race-local Shadow checkpoint'))
  self.assertLessEqual(s['timeout-minutes'],3)
  compute=next(x for x in s['steps'] if x.get('id')=='compute');self.assertEqual(compute['timeout-minutes'],1)
  # Delivery failure does not disable Shadow; Shadow failure does not change parent result.
  self.assertIn('always()',s['if']);self.assertNotIn("result == 'success'",s['if'])
 def test_single_entry_never_waits_for_whole_formal_workflow(self):
  steps=yaml.safe_load((ROOT/'.github/workflows/km-jra-formal-single-entry.yml').read_text())['jobs']['orchestrate']['steps']
  code=next(s['run'] for s in steps if s.get('id')=='formal_run')
  self.assertNotIn('gh run watch',code);self.assertIn('jra_formal_artifact_wait.py',code);self.assertIn('verify_formal_completion_summary',code)
 def test_optional_shadow_running_cannot_delay_production_artifact(self):
  calls=[]
  def fetch(path):
   calls.append(path)
   return {'artifacts':[provider_artifact()]} if '/artifacts?' in path else provider_run()
  self.assertEqual(wait(123,fetch,pause=lambda t:self.fail('waited for optional Shadow'))['id'],1)
  self.assertEqual(len(calls),2)
 def test_api_refusal_is_not_retried_or_assumed_complete(self):
  calls=[]
  def fetch(path):calls.append(path);raise RuntimeError('403 RATE_LIMIT')
  with self.assertRaisesRegex(RuntimeError,'RATE_LIMIT'):wait(123,fetch)
  self.assertEqual(len(calls),1)
  with self.assertRaises(ValueError):select_artifact(provider_run('completed'),[])
  self.assertIsNone(select_artifact(provider_run(),[provider_artifact('krs-utility-123')]))
 def test_old_completed_run_compatibility_and_expired_refusal(self):
  run=provider_run('completed')
  self.assertEqual(select_artifact(run,[provider_artifact('krs-utility-123')])['id'],1)
  with self.assertRaises(ValueError):select_artifact(run,[{'name':'krs-production-123','expired':True}])
 def test_provider_authority_and_artifact_head_tampering_refused(self):
  for kind in ('fork','branch','workflow','event','artifact_run','artifact_head'):
   run=provider_run();a=provider_artifact()
   if kind=='fork':run['head_repository']['full_name']='attacker/repo'
   if kind=='branch':run['head_branch']='untrusted'
   if kind=='workflow':run['path']='.github/workflows/other.yml'
   if kind=='event':run['event']='pull_request'
   if kind=='artifact_run':a['workflow_run']['id']=124
   if kind=='artifact_head':a['workflow_run']['head_sha']='b'*40
   with self.subTest(kind=kind),self.assertRaises(ValueError):select_artifact(run,[a])


class AuthenticatedReadinessTests(unittest.TestCase):
 def test_http_classification_and_not_due_token_guard(self):
  spec=importlib.util.spec_from_file_location('workflow_readiness',ROOT/'tools/jra_workflow_readiness.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  self.assertEqual(m.classify(403,{'X-RateLimit-Remaining':'0'},''),'RATE_LIMIT')
  self.assertEqual(m.classify(403,{},'Resource not accessible by integration'),'AUTHENTICATION_OR_PERMISSION')
  self.assertEqual(m.classify(503,{},''),'TEMPORARY_PROVIDER_ERROR')
  self.assertEqual(m.collect('',now=m.NOT_BEFORE)['status'],'AUTHENTICATED_TOKEN_UNAVAILABLE')
  self.assertEqual(m.collect('not printed',now=m.NOT_BEFORE-__import__('datetime').timedelta(seconds=1))['status'],'NOT_DUE')


class RealGitRaceConflictTests(unittest.TestCase):
 def test_distinct_races_merge_and_same_race_conflict_preserves_upstream(self):
  import subprocess
  sys.path.insert(0,str(ROOT))
  from tools.persist_local_checkpoints import persist
  with tempfile.TemporaryDirectory() as folder:
   base=Path(folder);remote=base/'remote.git'
   def git(cwd,*args):
    return subprocess.check_output(['git',*args],cwd=cwd,stderr=subprocess.DEVNULL,text=True).strip()
   git(base,'init','--bare','--initial-branch=main',str(remote))
   def clone(name):
    root=base/name;git(base,'clone',str(remote),str(root));git(root,'config','user.name','isolated-test');git(root,'config','user.email','test@example.invalid');return root
   first=clone('first');(first/'base').write_text('base');git(first,'add','.');git(first,'commit','-m','base');git(first,'push','origin','HEAD:main')
   second=clone('second')
   def commit(root,race,value):
    p=root/'runtime/role_rescue_shadow'/f'{race}.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'value':value}));git(root,'add','.');git(root,'commit','-m',race)
   commit(first,'R01',1);commit(second,'R02',2)
   persist(cwd=first,branch='main',refresh=lambda p:None,attempts=1)
   persist(cwd=second,branch='main',refresh=lambda p:None,attempts=1)
   self.assertEqual(git(base,'--git-dir='+str(remote),'show','main:runtime/role_rescue_shadow/R01.json'),'{"value": 1}')
   third=clone('third');fourth=clone('fourth');commit(third,'R01',3);commit(fourth,'R01',4)
   persist(cwd=third,branch='main',refresh=lambda p:None,attempts=1)
   with self.assertRaisesRegex(RuntimeError,'IMMUTABLE_OR_UNKNOWN_CONFLICT'):
    persist(cwd=fourth,branch='main',refresh=lambda p:None,attempts=1)
   self.assertEqual(git(base,'--git-dir='+str(remote),'show','main:runtime/role_rescue_shadow/R01.json'),'{"value": 3}')


class DurableResumeAndTelemetryTests(unittest.TestCase):
 setup_root=IsolationTests.setup_root
 def test_killed_worker_leaves_started_record_and_never_a_new_freeze(self):
  import subprocess
  q,f,_=fixture()
  with tempfile.TemporaryDirectory() as folder:
   root=self.setup_root(folder);c=pack(root,q,f,created_at=f['final_freeze_timestamp'])
   p=root/'input.json';p.write_text(json.dumps(c))
   program="""import sys,os,signal
sys.path.insert(0,sys.argv[1])
import family_authority_guard,jra_shadow_checkpoint
family_authority_guard.resolve_current_authority=lambda **kwargs:os.kill(os.getpid(),signal.SIGKILL)
sys.argv=['checkpoint','--root',sys.argv[2],'--checkpoint',sys.argv[3]]
jra_shadow_checkpoint.main()
"""
   result=subprocess.run([sys.executable,'-c',program,str(ROOT/'runtime'),str(root),str(p)],timeout=10)
   self.assertEqual(result.returncode,-9)
   self.assertTrue(list((root/'shadow-output').glob('worker-*.started.json')))
   self.assertTrue(list((root/'shadow-output'/f['race_id']).glob('execution-*-started.json')))
   self.assertFalse((root/'runtime/role_rescue_shadow').exists())
 def test_pre_checkpoint_failure_is_also_recorded(self):
  import jra_shadow_checkpoint as checkpoint
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'input.json';p.write_text('not JSON')
   with patch('sys.argv',['checkpoint','--root',folder,'--checkpoint',str(p)]),self.assertRaises(ValueError):checkpoint.main()
   paths=list((Path(folder)/'shadow-output').glob('worker-*.failed.json'))
   self.assertEqual(len(paths),1);self.assertEqual(json.loads(paths[0].read_text())['status'],'FAILED')
 def test_real_handoff_retry_preserves_original_time_and_learning_snapshot(self):
  from jra_shadow_checkpoint import prepare
  q,f,_=fixture()
  with tempfile.TemporaryDirectory() as folder:
   root=self.setup_root(folder)
   first=prepare(root,q,f,created_at=f['final_freeze_timestamp'])
   # A later corrupt state must not alter the original frozen retry input.
   p=root/'runtime/learning_states/new.json';p.parent.mkdir(parents=True);p.write_text('not JSON')
   second=prepare(root,q,f,created_at='2026-10-24T10:00:00+09:00')
   self.assertEqual(first,second)
   altered=copy.deepcopy(q);altered['source_snapshot_sha256']='0'*64
   with self.assertRaisesRegex(ValueError,'CONFLICT'):prepare(root,altered,f)
 def test_learning_effect_distinguishes_read_from_numerical_and_ticket_change(self):
  from jra_shadow_checkpoint import learning_effect
  from jra_role_learning_shadow import build_shadow
  q,f,_=fixture()
  out=build_shadow(q,f,observed_at=f['final_freeze_timestamp'])
  effect=learning_effect(out)
  self.assertEqual(effect['accepted_count'],0);self.assertFalse(effect['input_values_changed'])
  self.assertEqual(effect['added_ticket_count'],0)
  self.assertEqual(effect['numerical_rank_or_role_effect'],'NONE_FIXED_MODEL')
  out['learning_intake']['accepted']=[{'state_id':'test-only','state_sha256':'a'*64}]
  effect=learning_effect(out)
  self.assertTrue(effect['input_values_changed']);self.assertEqual(effect['added_ticket_count'],0)
  self.assertNotEqual(effect['accepted_input_sha256'],effect['without_learning_input_sha256'])
 def test_cli_failure_retains_diagnostic_without_a_new_forecast(self):
  import jra_shadow_checkpoint as checkpoint
  q,f,_=fixture()
  with tempfile.TemporaryDirectory() as folder:
   root=self.setup_root(folder);c=pack(root,q,f,created_at=f['final_freeze_timestamp'])
   p=root/'input.json';p.write_text(json.dumps(c))
   with patch('sys.argv',['checkpoint','--root',str(root),'--checkpoint',str(p)]),patch('family_authority_guard.resolve_current_authority',side_effect=RuntimeError('simulated interruption')):
    with self.assertRaises(RuntimeError):checkpoint.main()
   files=[p for p in (root/'shadow-output'/f['race_id']).glob('execution-*.json') if not p.name.endswith('-started.json')]
   self.assertEqual(len(files),1);trace=json.loads(files[0].read_text())
   self.assertEqual(trace['status'],'FAILED');self.assertFalse(trace['oos_eligible'])
   self.assertIn('WORKER_SELF_REPORTED',trace['clock_trust']);self.assertGreaterEqual(trace['elapsed_seconds'],0)
   self.assertFalse((root/'runtime/role_rescue_shadow').exists())

class FreshRunnerArchiveTests(unittest.TestCase):
 setup_root=IsolationTests.setup_root
 def archive_fixture(self,root):
  import io,zipfile,hashlib,os
  from jra_shadow_checkpoint import recover_previous
  q,f,_=fixture();env={'GITHUB_REPOSITORY':'b03la013-max/keibametrics-runtime','GITHUB_RUN_ID':'123','GITHUB_RUN_ATTEMPT':'1','GITHUB_SHA':'a'*40}
  with patch.dict(os.environ,env):c=pack(root,q,f,created_at=f['final_freeze_timestamp'])
  stream=io.BytesIO()
  with zipfile.ZipFile(stream,'w') as z:z.writestr(f['race_id']+'/shadow_input.json',json.dumps(c))
  raw=stream.getvalue();run=provider_run('completed');run.update(run_attempt=1,created_at=q['source_snapshot']['source_freeze_at'],conclusion='cancelled')
  a=provider_artifact('krs-shadow-checkpoint-123-1');a.update(size_in_bytes=len(raw),digest='sha256:'+hashlib.sha256(raw).hexdigest(),created_at=f['final_freeze_timestamp'],updated_at=f['final_freeze_timestamp'])
  items={'total_count':1,'artifacts':[a]};calls=[]
  def api(path):
   calls.append(path)
   if '/artifacts?' in path:return json.dumps(items).encode()
   if '/attempts/' in path:return json.dumps(run).encode()
   return raw
  env['GITHUB_RUN_ATTEMPT']='2'
  return q,f,c,run,a,items,raw,api,env,calls
 def test_killed_previous_runner_restores_original_learning_then_resumes_before_cutoff(self):
  import os
  from jra_shadow_checkpoint import recover_previous
  with tempfile.TemporaryDirectory() as folder:
   root=self.setup_root(folder);q,f,c,run,a,items,raw,api,env,calls=self.archive_fixture(root)
   p=root/'runtime/learning_states/new.json';p.parent.mkdir(parents=True);p.write_text('invalid later state')
   seen=[]
   with patch.dict(os.environ,env):got=recover_previous(root,q,f,api=api,verify_final=lambda final:seen.append(final))
   self.assertEqual(got,c);self.assertEqual(seen,[f]);self.assertEqual(got['learning_states'],[])
   out=execute(root,got,verify_final=lambda f:None,clock=lambda:f['final_freeze_timestamp'])
   self.assertEqual(out['delivery_checkpoint_sha256'],c['sha256']);self.assertFalse((root/'runtime/final_artifacts').exists())
 def test_missing_duplicate_partial_refused_without_new_checkpoint(self):
  import os
  from jra_shadow_checkpoint import recover_previous
  for failure in ('missing','duplicate','partial','truncated_list'):
   with self.subTest(failure=failure),tempfile.TemporaryDirectory() as folder:
    root=self.setup_root(folder);q,f,c,run,a,items,raw,api,env,calls=self.archive_fixture(root)
    if failure=='missing':items['artifacts']=[]
    if failure=='duplicate':items['artifacts']=[a,a]
    if failure=='partial':a['digest']='sha256:'+'0'*64
    if failure=='truncated_list':items['total_count']=101
    with patch.dict(os.environ,env),self.assertRaises(ValueError):recover_previous(root,q,f,api=api,verify_final=lambda f:None)
    self.assertFalse((root/'shadow-output'/f['race_id']/'shadow_input.json').exists())
 def test_wrong_execution_source_model_time_receipt_are_refused(self):
  import os
  from jra_shadow_checkpoint import recover_previous
  for failure in ('execution','source','model','late_archive','receipt'):
   with self.subTest(failure=failure),tempfile.TemporaryDirectory() as folder:
    root=self.setup_root(folder);q,f,c,run,a,items,raw,api,env,calls=self.archive_fixture(root)
    if failure=='execution':run['id']=999
    if failure=='source':q=copy.deepcopy(q);q['source_snapshot_sha256']='b'*64
    if failure=='model':p=root/MODEL;d=json.loads(p.read_text());d['sha256']='b'*64;p.write_text(json.dumps(d))
    if failure=='late_archive':a['updated_at']='2026-10-25T23:59:00+09:00'
    def signed(f):
     if failure=='receipt':raise ValueError('SIGNATURE')
    with patch.dict(os.environ,env),self.assertRaises(ValueError):recover_previous(root,q,f,api=api,verify_final=signed)
    self.assertFalse((root/'runtime/role_rescue_shadow').exists())
 def test_checkpoint_only_resume_after_cutoff_does_not_compute(self):
  import os
  from jra_shadow_checkpoint import recover_previous
  with tempfile.TemporaryDirectory() as folder:
   root=self.setup_root(folder);q,f,c,run,a,items,raw,api,env,calls=self.archive_fixture(root)
   with patch.dict(os.environ,env):got=recover_previous(root,q,f,api=api,verify_final=lambda f:None)
   with patch('jra_shadow_checkpoint.persist_shadow') as compute,self.assertRaisesRegex(ValueError,'AFTER_CUTOFF'):
    execute(root,got,verify_final=lambda f:None,clock=lambda:'2026-10-25T23:59:00+09:00')
   compute.assert_not_called()
 def test_provider_refusal_is_not_retried(self):
  import os
  from jra_shadow_checkpoint import recover_previous
  with tempfile.TemporaryDirectory() as folder:
   root=self.setup_root(folder);q,f,c,run,a,items,raw,api,env,calls=self.archive_fixture(root);calls=[]
   def refused(path):calls.append(path);raise RuntimeError('403')
   with patch.dict(os.environ,env),self.assertRaisesRegex(RuntimeError,'403'):recover_previous(root,q,f,api=refused,verify_final=lambda f:None)
   self.assertEqual(len(calls),1)
 def test_completed_shadow_restored_unchanged_after_cutoff(self):
  import os,io,zipfile,hashlib
  from jra_shadow_checkpoint import recover_previous
  with tempfile.TemporaryDirectory() as folder:
   root=self.setup_root(folder);q,f,c,run,a,items,raw,api,env,calls=self.archive_fixture(root)
   out=execute(root,c,verify_final=lambda f:None,clock=lambda:f['final_freeze_timestamp'])
   (root/'runtime/role_rescue_shadow'/(f['race_id']+'.json')).unlink()
   b=io.BytesIO()
   with zipfile.ZipFile(b,'w') as z:z.writestr(f['race_id']+'/role_learning_shadow.json',json.dumps(out))
   archive=b.getvalue();u=provider_artifact('krs-utility-123');u.update(id=2,size_in_bytes=len(archive),digest='sha256:'+hashlib.sha256(archive).hexdigest());items['artifacts'].append(u);items['total_count']=2
   original_api=api
   def api(path):return archive if path=='actions/artifacts/2/zip' else original_api(path)
   with patch.dict(os.environ,env),patch('jra_shadow_checkpoint.persist_shadow') as compute:
    got=recover_previous(root,q,f,api=api,verify_final=lambda f:None,witness=lambda s:{'verified':True})
   compute.assert_not_called();self.assertEqual(got,c);self.assertEqual(json.loads((root/'runtime/role_rescue_shadow'/(f['race_id']+'.json')).read_text()),out)
 def test_attempt_artifact_name_keeps_original_witness_identity(self):
  import io,zipfile,hashlib
  from test_jra_live_acceptance_continuation import proof_fixture
  from jra_role_learning_shadow import verify_actions_artifact,utility_artifact_name
  s,run,a,data,code,r=proof_fixture();s['actions_freeze_context']['run_attempt']='2';s['sha256']=digest({k:v for k,v in s.items() if k!='sha256'});run['run_attempt']=2
  b=io.BytesIO()
  with zipfile.ZipFile(b,'w') as z:z.writestr(s['race_id']+'/role_learning_shadow.json',json.dumps(s))
  data=b.getvalue();a['digest']='sha256:'+hashlib.sha256(data).hexdigest();a['name']=utility_artifact_name(123,2)
  self.assertTrue(verify_actions_artifact(s,run,a,data,code)['verified'])
  a['name']='krs-utility-123'
  with self.assertRaises(ValueError):verify_actions_artifact(s,run,a,data,code)

 def test_third_attempt_preserves_first_archive_before_cutoff(self):
  import os
  from jra_shadow_checkpoint import recover_previous
  with tempfile.TemporaryDirectory() as folder:
   root=self.setup_root(folder);q,f,c,run,a,items,raw,api,env,calls=self.archive_fixture(root)
   late=copy.deepcopy(a);late.update(id=3,name='krs-shadow-checkpoint-123-2',created_at='2026-10-25T23:59:00+09:00',updated_at='2026-10-25T23:59:00+09:00')
   items['artifacts'].append(late);items['total_count']=2;env['GITHUB_RUN_ATTEMPT']='3'
   with patch.dict(os.environ,env):got=recover_previous(root,q,f,api=api,verify_final=lambda f:None)
   self.assertEqual(got,c);self.assertIn('actions/runs/123/attempts/1',calls)
   self.assertNotIn('actions/artifacts/3/zip',calls)


class CrossRunReadbackTests(unittest.TestCase):
 setup_root=IsolationTests.setup_root
 archive_fixture=FreshRunnerArchiveTests.archive_fixture
 def test_cross_run_preserves_original_context_and_learning(self):
  import os
  from jra_shadow_checkpoint import recover_previous
  with tempfile.TemporaryDirectory() as folder:
   root=self.setup_root(folder);q,f,c,run,a,items,raw,api,env,calls=self.archive_fixture(root)
   env.update(GITHUB_RUN_ID='456',GITHUB_RUN_ATTEMPT='1',GITHUB_SHA='b'*40)
   with patch.dict(os.environ,env):got=recover_previous(root,q,f,api=api,verify_final=lambda f:None,origin_run_id='123')
   self.assertEqual(got,c);self.assertEqual(got['actions_checkpoint_context']['run_id'],'123')
   self.assertTrue(all('/456/' not in x for x in calls))
   with self.assertRaisesRegex(ValueError,'AFTER_CUTOFF'):
    execute(root,got,verify_final=lambda f:None,clock=lambda:'2099-01-01T00:00:00Z')
 def test_cross_run_rejects_wrong_origin_and_active_origin(self):
  import os
  from jra_shadow_checkpoint import recover_previous
  for mutation in ('origin','active','model','receipt'):
   with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as folder:
    root=self.setup_root(folder);q,f,c,run,a,items,raw,api,env,calls=self.archive_fixture(root)
    env.update(GITHUB_RUN_ID='456',GITHUB_RUN_ATTEMPT='1',GITHUB_SHA='b'*40)
    if mutation=='origin':run['id']=999
    if mutation=='active':run['status']='in_progress'
    if mutation=='model':(root/MODEL).write_text('{}')
    def signed(f):
     if mutation=='receipt':raise ValueError('BAD_RECEIPT')
    with patch.dict(os.environ,env),self.assertRaises((ValueError,KeyError)):
     recover_previous(root,q,f,api=api,verify_final=signed,origin_run_id='123')
    self.assertFalse((root/'shadow-output'/f['race_id']/'shadow_input.json').exists())
 def production_fixture(self,root):
  import io,zipfile,hashlib
  q,f,c,run,a,items,raw,api,env,calls=self.archive_fixture(root)
  qp='runtime/requests/'+f['race_id']+'.json';fp='runtime/final_artifacts/'+f['race_id']+'.json'
  (root/qp).parent.mkdir(parents=True);(root/qp).write_text(json.dumps(q))
  # Synthetic provider/signature callback fixture around real frozen numerical input.
  # Historic signed files remain untouched; live signature checks are not mocked in CLI.
  output={'summary':[]};wire=json.dumps(output)
  f=copy.deepcopy(f);f['krs_run_receipt']['receipt']['output_sha256']=hashlib.sha256(wire.encode()).hexdigest()
  f['sha256']=digest({k:v for k,v in f.items() if k!='sha256'})
  from test_jra_single_entry_outcome import fixture as completion_fixture
  _,summary=completion_fixture()
  summary.update(race_id=f['race_id'],source_snapshot_sha256=q['source_snapshot_sha256'])
  summary['manifest'].update(required_count=len(q['runners'])*20,calculated_count=len(q['runners'])*20)
  summary['pre_krs']['receipt_sha256']=f['pre_krs_receipt']['receipt_sha256']
  summary['krs'].update(receipt_sha256=f['krs_run_receipt']['receipt_sha256'],requested_run_count=q.get('run_count',5000),actual_run_count=q.get('run_count',5000))
  summary['final'].update(receipt_sha256=f['final_receipt_sha256'],immutable_artifact_sha256=f['sha256'],receipt_timestamp=f['final_receipt']['receipt']['timestamp'])
  prefix='krs-artifacts/'+f['race_id']+'/'
  files={qp:json.dumps(q).encode(),fp:json.dumps(f).encode(),'krs-artifacts/original.json':b'{"receipt":"original"}',
    prefix+'formal_execution_summary.json':json.dumps(summary).encode(),prefix+'krs_response.json':json.dumps({'run_receipt':f['krs_run_receipt'],'output':output,'output_canonical_json':wire}).encode(),prefix+'krs_prediction_utility.json':json.dumps(f['krs_prediction_utility']).encode()}
  def rebuild():
   out=io.BytesIO()
   with zipfile.ZipFile(out,'w') as z:
    for name,data in files.items():z.writestr(zipfile.ZipInfo(name,date_time=(2026,10,18,0,0,0)),data)
   raw=out.getvalue();a.update(name='krs-production-123',digest='sha256:'+hashlib.sha256(raw).hexdigest(),size_in_bytes=len(raw));return raw
  raw=rebuild()
  def api(path):
   calls.append(path)
   if '/artifacts?' in path:return json.dumps(items).encode()
   if path=='actions/runs/123':return json.dumps(run).encode()
   return rebuild()
  return q,f,qp,fp,files,a,items,api,env,calls
 def test_production_rerun_reads_exact_bytes_without_recompute(self):
  import os
  from jra_shadow_checkpoint import production_readback
  with tempfile.TemporaryDirectory() as folder:
   root=self.setup_root(folder);q,f,qp,fp,files,a,items,api,env,calls=self.production_fixture(root);seen=[]
   with patch.dict(os.environ,env):r=production_readback(root,qp,api=api,verify_final=lambda f:seen.append(f))
   self.assertTrue(r['reused']);self.assertEqual(len(seen),1)
   for name,data in files.items():self.assertEqual((root/name).read_bytes(),data)
   with patch.dict(os.environ,env):r2=production_readback(root,qp,api=api,verify_final=lambda f:None)
   self.assertEqual(r,r2)
 def test_production_cross_run_and_partial_conflict_refusal(self):
  import os
  from jra_shadow_checkpoint import production_readback
  for mutation in ('none','missing','summary','stage','duplicate','conflict','source','receipt','traversal','wire','output'):
   with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as folder:
    root=self.setup_root(folder);q,f,qp,fp,files,a,items,api,env,calls=self.production_fixture(root)
    env.update(GITHUB_RUN_ID='456',GITHUB_RUN_ATTEMPT='1',GITHUB_SHA='b'*40)
    if mutation=='missing':files.pop(fp)
    if mutation=='summary':files.pop('krs-artifacts/'+f['race_id']+'/formal_execution_summary.json')
    if mutation=='stage':files['krs-artifacts/'+f['race_id']+'/krs_response.json']=b'{}'
    if mutation in {'wire','output'}:
     name='krs-artifacts/'+f['race_id']+'/krs_response.json';k=json.loads(files[name]);k['output_canonical_json' if mutation=='wire' else 'output']='tamper' if mutation=='wire' else {'summary':[1]};files[name]=json.dumps(k).encode()
    if mutation=='duplicate':items['artifacts'].append(copy.deepcopy(a))
    if mutation=='conflict':(root/fp).parent.mkdir(parents=True);(root/fp).write_text('conflict')
    if mutation=='source':q['source_snapshot_sha256']='0'*64;(root/qp).write_text(json.dumps(q))
    if mutation=='traversal':files['krs-artifacts/../../escape']=b'x'
    def signed(f):
     if mutation=='receipt':raise ValueError('BAD_RECEIPT')
    # Archive metadata is settled before download; no mutations after its provider digest.
    api('download')
    with patch.dict(os.environ,env):
     if mutation=='none':self.assertTrue(production_readback(root,qp,api=api,verify_final=signed,origin_run_id='123')['reused'])
     else:
      with self.assertRaises(ValueError):production_readback(root,qp,api=api,verify_final=signed,origin_run_id='123')
      self.assertFalse((root/'krs-artifacts/original.json').exists())
 def test_live_first_attempt_has_no_readback_api_dependency(self):
  import os
  from jra_shadow_checkpoint import production_readback
  with tempfile.TemporaryDirectory() as folder:
   root=self.setup_root(folder);q,f,qp,fp,files,a,items,api,env,calls=self.production_fixture(root)
   env['GITHUB_RUN_ATTEMPT']='1'
   with patch.dict(os.environ,env):r=production_readback(root,qp,api=lambda _:self.fail('unexpected API'),verify_final=lambda _:self.fail('unexpected signature'))
   self.assertFalse(r['reused']);self.assertFalse((root/fp).exists())
 def test_workflow_uses_readback_before_compute_and_reuses_original_archive(self):
  w=yaml.safe_load((ROOT/'.github/workflows/km-formal-request-runner.yml').read_text())
  steps=w['jobs']['formal-run']['steps'];rd=next(i for i,x in enumerate(steps) if x.get('id')=='production_readback');co=next(i for i,x in enumerate(steps) if x.get('id')=='formal_execution')
  self.assertLess(rd,co);self.assertIn("reused == 'false'",steps[co]['if'])
  up=next(x for x in steps if x.get('uses')=='actions/upload-artifact@v4');self.assertIn("reused == 'false'",up['if'])
  download=next(x for x in w['jobs']['shadow-run']['steps'] if x.get('uses')=='actions/download-artifact@v4')
  self.assertIn('artifact_run_id',download['with']['run-id']);self.assertNotIn('shadow-run',w['jobs']['formal-run'].get('needs',[]))

 def test_cross_run_chain_restores_later_output_without_new_freeze(self):
  import os,io,zipfile,hashlib
  from jra_shadow_checkpoint import recover_previous
  with tempfile.TemporaryDirectory() as folder:
   root=self.setup_root(folder);q,f,c,run,a,items,raw,api,env,calls=self.archive_fixture(root)
   with patch.dict(os.environ,{**env,'GITHUB_ACTIONS':'true','GITHUB_RUN_ID':'456','GITHUB_RUN_ATTEMPT':'1'}):
    out=execute(root,c,verify_final=lambda f:None,clock=lambda:f['final_freeze_timestamp'])
   destination=root/'runtime/role_rescue_shadow'/(f['race_id']+'.json');destination.unlink()
   b=io.BytesIO()
   with zipfile.ZipFile(b,'w') as z:z.writestr(f['race_id']+'/role_learning_shadow.json',json.dumps(out))
   archive=b.getvalue();u=provider_artifact('krs-utility-456');u.update(id=2,size_in_bytes=len(archive),digest='sha256:'+hashlib.sha256(archive).hexdigest())
   u['workflow_run']={'id':456,'head_sha':'b'*40}
   later=copy.deepcopy(run);later.update(id=456,head_sha='b'*40)
   original_api=api
   def api(path):
    if path=='actions/runs/456':return json.dumps(later).encode()
    if path=='actions/runs/456/artifacts?per_page=100':return json.dumps({'artifacts':[u],'total_count':1}).encode()
    if path=='actions/artifacts/2/zip':return archive
    return original_api(path)
   env.update(GITHUB_RUN_ID='789',GITHUB_RUN_ATTEMPT='1',GITHUB_SHA='c'*40)
   with patch.dict(os.environ,env),patch('jra_shadow_checkpoint.persist_shadow') as compute:
    got=recover_previous(root,q,f,api=api,verify_final=lambda f:None,witness=lambda s:{'verified':True},origin_run_id='123',output_run_id='456')
   compute.assert_not_called();self.assertEqual(got,c);self.assertEqual(json.loads(destination.read_text()),out)
   self.assertEqual(out['actions_freeze_context']['run_id'],'456')
 def test_explicit_missing_output_never_falls_back_to_new_prediction(self):
  import os
  from jra_shadow_checkpoint import recover_previous
  with tempfile.TemporaryDirectory() as folder:
   root=self.setup_root(folder);q,f,c,run,a,items,raw,api,env,calls=self.archive_fixture(root)
   original_api=api
   def api(path):
    if path=='actions/runs/456':return json.dumps({**run,'id':456}).encode()
    return b'{"artifacts":[],"total_count":0}' if '/456/artifacts?' in path else original_api(path)
   env.update(GITHUB_RUN_ID='789',GITHUB_RUN_ATTEMPT='1')
   with patch.dict(os.environ,env),self.assertRaisesRegex(ValueError,'EXPLICIT_OUTPUT_MISSING'):
    recover_previous(root,q,f,api=api,verify_final=lambda f:None,origin_run_id='123',output_run_id='456')
   self.assertFalse((root/'shadow-output'/f['race_id']/'shadow_input.json').exists())

 def test_later_shadow_provider_must_be_canonical_and_completed(self):
  import os
  from jra_shadow_checkpoint import recover_previous
  for field,value in (('id',999),('status','in_progress'),('head_branch','research'),('path','other.yml'),('head_sha','bad')):
   with self.subTest(field=field),tempfile.TemporaryDirectory() as folder:
    root=self.setup_root(folder);q,f,c,run,a,items,raw,api,env,calls=self.archive_fixture(root)
    later={**run,'id':456,field:value};original_api=api
    def api(path):return json.dumps(later).encode() if path=='actions/runs/456' else original_api(path)
    env.update(GITHUB_RUN_ID='789',GITHUB_RUN_ATTEMPT='1')
    with patch.dict(os.environ,env),self.assertRaisesRegex(ValueError,'OUTPUT_PROVIDER_IDENTITY'):
     recover_previous(root,q,f,api=api,verify_final=lambda f:None,origin_run_id='123',output_run_id='456')
    self.assertFalse((root/'shadow-output'/f['race_id']/'shadow_input.json').exists())

 def test_normal_production_preflight_exits_before_shadow_dependencies(self):
  import os,subprocess
  w=yaml.safe_load((ROOT/'.github/workflows/km-formal-request-runner.yml').read_text())
  script=next(x['run'] for x in w['jobs']['formal-run']['steps'] if x.get('id')=='production_readback')
  with tempfile.TemporaryDirectory() as folder:
   output=Path(folder)/'outputs'
   env={**os.environ,'ORIGIN_RUN_ID':'','GITHUB_RUN_ATTEMPT':'1','GITHUB_RUN_ID':'456','RACE_ID':'KM-JRA-TKY-20261024-R01','GITHUB_OUTPUT':str(output)}
   result=__import__('subprocess').run(['bash','-c',script],cwd=folder,env=env,capture_output=True,text=True,timeout=5)
   self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(output.read_text(),'reused=false\nartifact_run_id=456\n')

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
  p=j['formal-run'];s=j['shadow-run'];self.assertNotIn('needs',p);self.assertEqual(s['needs'],'formal-run');self.assertTrue(s['continue-on-error'])
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

"""Provider receipt binding and existing NO_BET workflow isolation regressions."""
import copy,hashlib,io,json,os,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
import yaml
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'));sys.path.insert(0,str(ROOT/'tests'))
from test_jra_role_learning_repair import fixture
from jra_role_learning_shadow import build_shadow,digest,verify_actions_artifact,actions_pre_result_witness,settle_shadow


def proof_fixture():
 q,f,r=fixture();s=build_shadow(q,f,historical=True,observed_at=f['final_freeze_timestamp'])
 s['actions_freeze_context']={'repository':'b03la013-max/keibametrics-runtime','run_id':'123','run_attempt':'1','head_sha':'a'*40}
 code=b'exact tested module';s['code_sha256']=hashlib.sha256(code).hexdigest()
 s['sha256']=digest({k:v for k,v in s.items() if k!='sha256'})
 run={'id':123,'run_attempt':1,'repository':{'full_name':s['actions_freeze_context']['repository']},
      'head_repository':{'full_name':s['actions_freeze_context']['repository']},'head_branch':'main','head_sha':'a'*40,
      'path':'.github/workflows/km-formal-request-runner.yml','event':'workflow_dispatch','conclusion':'success',
      'created_at':q['source_snapshot']['source_freeze_at']}
 blob=io.BytesIO()
 with zipfile.ZipFile(blob,'w') as z:z.writestr(s['race_id']+'/role_learning_shadow.json',json.dumps(s))
 data=blob.getvalue();a={'id':321,'name':'krs-utility-123','expired':False,'workflow_run':{'id':123,'head_sha':'a'*40},
   'created_at':s['observed_at'],'updated_at':s['observed_at'],'digest':'sha256:'+hashlib.sha256(data).hexdigest()}
 return s,run,a,data,code,r

class WitnessTests(unittest.TestCase):
 def test_server_content_and_code_bind_but_historical_fixture_is_not_oos(self):
  s,run,a,data,code,r=proof_fixture()
  self.assertTrue(verify_actions_artifact(s,run,a,data,code)['verified'])
  self.assertFalse(s['temporally_eligible']);self.assertFalse(settle_shadow(s,r)['oos_eligible'])
 def test_late_upload_fork_attempt_changed_code_or_wrong_archive_fail(self):
  s,run,a,data,code,r=proof_fixture()
  cases=[]
  b=copy.deepcopy(a);b['updated_at']='2026-10-18T23:59:00Z';cases.append((run,b,data,code))
  b=copy.deepcopy(run);b['head_repository']['full_name']='attacker/fork';cases.append((b,a,data,code))
  b=copy.deepcopy(run);b['run_attempt']=2;cases.append((b,a,data,code))
  b=copy.deepcopy(run);b['path']='.github/workflows/other.yml';cases.append((b,a,data,code))
  b=copy.deepcopy(a);b['workflow_run']['head_sha']='b'*40;cases.append((run,b,data,code))
  cases.extend([(run,a,data+b'bad',code),(run,a,data,b'other code')])
  for values in cases:
   with self.subTest(values=str(values)[:100]),self.assertRaises(ValueError):verify_actions_artifact(s,*values)
 def test_matching_digest_with_changed_shadow_member_is_rejected(self):
  s,run,a,data,code,r=proof_fixture();wrong=copy.deepcopy(s);wrong['observed_at']='forged'
  blob=io.BytesIO()
  with zipfile.ZipFile(blob,'w') as z:z.writestr(s['race_id']+'/role_learning_shadow.json',json.dumps(wrong))
  data=blob.getvalue();a['digest']='sha256:'+hashlib.sha256(data).hexdigest()
  with self.assertRaisesRegex(ValueError,'CONTENT'):verify_actions_artifact(s,run,a,data,code)
 def test_missing_context_never_falls_back_to_git_time(self):
  s,run,a,data,code,r=proof_fixture();s.pop('actions_freeze_context')
  self.assertFalse(actions_pre_result_witness(s)['verified'])
 def test_false_positive_cost_is_stake_on_added_losing_tickets(self):
  q,f,r=fixture();s=build_shadow(q,f,historical=True,observed_at=f['final_freeze_timestamp']);out=settle_shadow(s,r)
  for name,a in out['arms'].items():
   self.assertEqual(a['false_positive_cost']+a['added_winning_stake'],a['added_capital'])
  self.assertEqual(out['arms']['PRODUCTION']['false_positive_cost'],0)

class NoBetWorkflowTests(unittest.TestCase):
 def steps(self):
  return yaml.safe_load((ROOT/'.github/workflows/km-jra-no-bet-postresult-learning.yml').read_text())['jobs']['official-result-ingest']['steps']
 def code(self,step_id):
  step=next(s for s in self.steps() if s.get('id')==step_id)
  return step['run'].split("python - <<'PY'\n",1)[1].rsplit('\nPY',1)[0]
 def test_unverified_or_invalid_one_does_not_block_verified_sibling(self):
  code=self.code('settle')
  import jra_no_bet_postresult_learning as module
  for failure in ('attestation','builder'):
   with self.subTest(failure=failure),tempfile.TemporaryDirectory() as td:
    root=Path(td);old=os.getcwd();os.chdir(td)
    try:
     for name in ('bad','good'):
      for base in ('runtime_out/capture','runtime/jra_no_bet_terminals'):
       p=root/base/(name+'.json');p.parent.mkdir(parents=True,exist_ok=True)
       p.write_text(json.dumps({'name':name,'official_result_detail':{},'race_no':5,'result_capture_timestamp':'now','source_snapshot':{'snapshot_sha256':'a'*64}}))
     def attest(cmd,**kwargs):
      if failure=='attestation' and 'bad.json' in cmd[3]:raise subprocess.CalledProcessError(1,cmd)
     def build(t,*args,**kwargs):
      if failure=='builder' and t['name']=='bad':raise ValueError('REAL_BAD_INPUT')
      return {'investment':0,'payout':0,'pfs':None}
     with patch.dict(os.environ,{'GITHUB_OUTPUT':str(root/'output'),'GITHUB_REPOSITORY':'b03la013-max/keibametrics-runtime'}),patch('subprocess.run',side_effect=attest),patch.object(module,'build_no_bet_learning',side_effect=build):
      exec(compile(code,'no_bet_workflow','exec'),{})
     self.assertTrue((root/'runtime_out/learning/good.json').exists());self.assertFalse((root/'runtime_out/learning/bad.json').exists())
     self.assertIn('learned=true',(root/'output').read_text())
    finally:os.chdir(old)
 def test_current_two_no_bet_terminals_are_in_bounded_capture_selection(self):
  # Execute the actual capture step against the current five pending terminals,
  # replacing official network IO only. No capture is claimed verified.
  seen=[];opened=[]
  from datetime import datetime,timezone
  class Clock(datetime):
   @classmethod
   def now(cls,tz=None):return cls(2026,10,18,9,0,tzinfo=timezone.utc)
  sys.path.insert(0,str(ROOT/'runtime/jra_source_runtime'))
  import jra_same_day_results as module
  def fetch(opener,referer,day,key,d,rn,cutoff):
   seen.append((key,rn));return {},{'official':False}
  def open_day(date,key):
   opened.append((date,key));return None,None,None,key,None
  old=os.getcwd();os.chdir(ROOT)
  try:
   with tempfile.TemporaryDirectory() as td,patch('datetime.datetime',Clock),patch.object(module,'_open_day',side_effect=open_day),patch.object(module,'_fetch_race',side_effect=fetch),patch.dict(os.environ,{'GITHUB_OUTPUT':str(Path(td)/'out')}):
    exec(compile(self.code('capture'),'capture_workflow','exec'),{})
   # Both today's terminals are encountered before the older three.
   self.assertEqual(len(seen),4)
   today=[]
   for v in ('TKY','KYO'):
    i=json.loads((ROOT/'runtime/jra_formal_intents'/f'KM-JRA-{v}-20261018-R05-LIVE-R1.json').read_text());today.append((i['jra_source']['jra_meeting_key'],5))
   self.assertEqual(set(seen[:2]),set(today))
   self.assertEqual([d for d,k in opened[:2]],['2026-10-18','2026-10-18'])
  finally:os.chdir(old)

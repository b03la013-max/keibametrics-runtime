import copy,json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
from kaw_v25_conversion_review import build_review,sha
from formal_execution_orchestrator import parse_official_result_snapshot,FormalOrchestrationError

def case(r):
 rid=f'KM-LOCAL-KAW-20261013-R{r:02}-LIVE-R1'
 req=json.loads((ROOT/'runtime/formal_intents'/f'{rid}.json').read_text())
 d=next((ROOT/'runtime/executions'/rid/'FORMAL').rglob('final_receipt_envelope.json')).parent
 return req,json.loads((d/'final_receipt_envelope.json').read_text())['artifact'],json.loads((d/'aki_adaptive_purchase_shadow_pre_result.json').read_text())

@pytest.mark.parametrize('race',[1,3,5,6,7,9,10,12])
def test_saved_review_preserves_prediction_and_tickets(race):
 req,a,s=case(race);original=copy.deepcopy((req,a,s));r=build_review(req,a,s,generated_at=s['generated_at'])
 assert (req,a,s)==original
 assert r['candidate_tickets']==s['candidate_tickets'] and r['purchase_authority'] is False
 assert r['actual_pfs'] is None and r['market_status']=='HOLD_PRICE_COVERAGE_MISSING'
 assert all(c['decision']['disposition']=='UNRESOLVED-REVIEW' for c in r['cells'])

@pytest.mark.parametrize('race,head,second',[(3,'3','5'),(9,'7','2'),(12,'10','8')])
def test_material_pair_loss_retains_worlds(race,head,second):
 req,a,s=case(race);r=build_review(req,a,s,generated_at=s['generated_at'])
 losses=[c for c in r['cells'] if c['type']=='HEAD_LOCAL_P2' and c['baseline_material']]
 assert losses and all('lost_third_worlds' in c for c in losses)
 if (head,second)==('10','8'):assert any(c['cell']==[head,second] for c in losses)

def test_protect_not_automatic_exact():
 req,a,s=case(5);r=build_review(req,a,s,generated_at=s['generated_at'])
 assert any(c['baseline_status']=='PROTECT' for c in r['cells'])
 assert r['candidate_tickets']==s['candidate_tickets']

def test_unknown_not_weak_or_must_buy():
 req,a,s=case(10);r=build_review(req,a,s,generated_at=s['generated_at'])
 assert any(x['runner_id']=='3' for x in r['unknown_role_review'])
 assert r['candidate_tickets']==s['candidate_tickets']

def test_market_postcutoff_rejected():
 req,a,s=case(12)
 with pytest.raises(ValueError,match='MARKET_TEMPORAL'):build_review(req,a,s,generated_at=s['generated_at'],market={'race_id':req['race_id'],'observed_at':req['scheduled_post_at'],'source_ref':'official'})

def test_final_deadline():
 req,a,s=case(12)
 with pytest.raises(ValueError,match='REVIEW_AFTER_POST'):build_review(req,a,s,generated_at=req['scheduled_post_at'])

def test_lower_tie_top3_audit_preserves_default_hold():
 p=ROOT/'evidence/kaw_v25_20261013/2026-10-12-R12-official.json';a=json.loads(p.read_text())['artifact'];raw=a['sources'][0]
 with pytest.raises(FormalOrchestrationError,match='DEAD_HEAT'):parse_official_result_snapshot(raw,a['source_race_context'],range(1,19))
 order,pay=parse_official_result_snapshot(raw,a['source_race_context'],range(1,19),top3_only=True)
 assert order==[2,4,7] and set(pay)=={'EXACTA','TRIO','TRIFECTA'}

def test_failure_report_saved_without_execution_directory(tmp_path):
 # Verify actual shell persistence, not string presence alone.
 import subprocess
 root=tmp_path; (root/'runtime_out').mkdir();(root/'runtime_out/orchestration_report.json').write_text('{"status":"DEADLINE_HOLD"}')
 workflow=(ROOT/'.github/workflows/km-formal-single-entry.yml').read_text()
 start=workflow.index('          mkdir -p "runtime/execution_reports/$EXECUTION_ID"')
 end=workflow.index('          git config user.name',start)
 script='\n'.join(line[10:] for line in workflow[start:end].splitlines()).replace('${{ github.run_id }}','1')
 subprocess.run(['bash','-eu','-c',script],cwd=root,env={'EXECUTION_ID':'FAILED','GITHUB_RUN_ID':'1','PATH':'/usr/bin:/bin'},check=True)
 assert list((root/'runtime/execution_reports/FAILED').glob('*.json'))

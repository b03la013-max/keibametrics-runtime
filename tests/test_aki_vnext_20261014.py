"""Real frozen inputs; outcome never supplied to selector."""
import copy,json,sys,hashlib
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
from local_aki_columns import build,decision,verify,LocalAKIError,sha
from local_fullnumerical_production import materialize_production
from pfs_grand_review import capital_arms

def real(race):
 rid=f'KM-LOCAL-KAW-20261013-R{race:02d}-LIVE-R1'
 q=json.loads((ROOT/'runtime/formal_intents'/f'{rid}.json').read_text())
 path=next((ROOT/'runtime/executions'/rid/'FORMAL').rglob('source_receipt_envelope.json'))
 src=json.loads(path.read_text())['artifact'];q['source_snapshot_sha256']=src['source_snapshot_sha256']
 q=materialize_production(src,q,q['required_indices']);q['aki_column_candidate']='HEAD_LOCAL_VNEXT_R1'
 return q,src

@pytest.mark.parametrize('race',[1,3,5,6,7,9,10,12])
def test_original_universe_context_and_orientation_preserved(race):
 q,src=real(race);before=copy.deepcopy(q);s=build(q,src);d=decision(q,s)
 assert q==before and verify(q,src,s)['status']=='PASS'
 for c,col in s['columns'].items():
  assert set(col['selected']) <= {str(r['runner_id']) for r in q['role_registry'] if r['column']==c}
 for row in s['pair_dispositions']:
  assert row in q['pair_dispositions'] and row['status'] in {'PURCHASE','PROTECT'}
 for row in s['third_dispositions']:
  assert row in q['third_dispositions'] # never PROTECT->Exact by score alone
 for ticket in d['paper_tickets']:
  if ticket['bet_type']=='TRIFECTA':
   assert any([str(row[k]) for k in ['head','second','third']]==[str(x) for x in ticket['selection']] and row['status']=='PURCHASE' for row in s['third_dispositions'])
 assert not d['purchase_tickets'] and d['capital']['paper_only']


def test_candidate_cannot_invent_prediction_universe_or_unknown_role():
 q,src=real(10);s=build(q,src)
 assert '3' not in s['columns']['P2']['selected'] # upstream UNKNOWN miss remains upstream
 q['role_registry']=[]
 with pytest.raises(LocalAKIError,match='FROZEN_PREDICTION_UNIVERSE_REQUIRED'):build(q,src)


def test_capital_budget_and_result_do_not_change_selection():
 q,src=real(12);s=build(q,src)
 for amount in [0,100,999999]:
  q['capital_policy']={'mode':'HARD_RACE_BUDGET','max_race_capital':amount}
  q['official_result']={'top3':[1,2,3]}
  assert build(q,src)==s


def test_each_conditional_pool_uses_own_column_risk():
 q,src=real(12);s=build(q,src)
 for head,x in s['conditional_audit']['heads'].items():
  assert x['leader'] not in {head}
  assert x['risk']==max(s['runner_axes'][x['leader']]['P2-AKI'],s['runner_axes'][x['leader']]['RSI'])
 for pair,x in s['conditional_audit']['pairs'].items():
  if 'leader' in x:
   assert x['leader'] not in pair.split('>')
   assert x['risk']==max(s['runner_axes'][x['leader']]['P3-AKI'],s['runner_axes'][x['leader']]['RSI'])
 assert all('lost_third_worlds' in x and x['exclusion_reason'] for x in s['conditional_audit']['excluded_pairs'])


def test_existing_pr262_arm_not_changed():
 for race,count in [(1,98),(3,3),(5,34),(6,10),(7,40),(9,14),(10,105),(12,45)]:
  q,src=real(race);q.pop('aki_column_candidate')
  assert len(decision(q,build(q,src))['paper_tickets'])==count


def test_saved_regression_keeps_original_oos_and_capital_ticket_keys():
 import gzip
 report=json.loads(gzip.decompress((ROOT/'research/aki_vnext_20261014/full_report.json.gz').read_bytes()))
 assert report['candidate_forward_oos']==0
 original=report['original17_and_replay']['B_ORIGINAL_AKI']['aggregate']
 assert (original['investment'],original['return'])==(17800,10700)
 for row in report['rows']:
  c=row['arms']['C_SELECTION'];d=row['arms']['D_CAPITAL_ONLY']
  if d['status']=='SETTLED':
   keys=lambda a:{(t['bet_type'],tuple(t['selection'])) for t in a['tickets']}
   assert keys(c)==keys(d)
   assert all(t['stake']>0 and t['stake']%100==0 for t in d['tickets'])
   assert d['investment']==row['arms']['A_PRODUCTION']['investment']


def test_real_external_receipt_source_and_krs_lineage():
 import base64
 from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
 root=ROOT/'evidence/aki_vnext_20261014/external/KM-LOCAL-KAW-20261013-R12-LIVE-R1/f613ba0c2da58926'
 from tools.local_aki_external_acceptance import restore_archived_receipts
 root.mkdir(parents=True,exist_ok=True)
 restore_archived_receipts(root,'KM-LOCAL-KAW-20261013-R12-LIVE-R1','f613ba0c2da58926')
 key=Ed25519PublicKey.from_public_bytes(base64.b64decode('jqWqOYlmhXXmpv/nR7lx3c2n/S5shDYava/WJVxn4kE='))
 envelopes=[json.loads((root/p).read_text()) for p in ['signed_source_input.json','pre_krs_receipt.json','krs_receipt.json','final_receipt.json','replay_result_receipt.json']]
 for e in envelopes:
  key.verify(base64.b64decode(e['signature']),json.dumps(e['receipt'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
  assert sha(e['artifact'])==e['receipt']['artifact_sha256']
 inp=json.loads((root/'krs_input.json').read_text());assert envelopes[2]['artifact']['actual_run_count']==20000
 assert sha(inp)==envelopes[1]['artifact']['input_sha256']==envelopes[2]['artifact']['input_sha256']
 q,src=real(12);s=json.loads((root/'selection.json').read_text());assert build(q,src)==s
 assert envelopes[3]['artifact']['final_prediction_package']['roles']==q['static_prediction']['roles']
 assert envelopes[4]['artifact']['frozen_refs']['final_receipt_sha256']==envelopes[3]['receipt_sha256']


def test_no_bet_is_not_a_paper_investment_and_typo_fails_closed():
 q,src=real(12)
 for runner in q['runners']:
  for feature in runner['evidence_features'].values():feature['missing']=True
 s=build(q,src);assert s['status']=='NO_BET'
 assert decision(q,s)['paper_tickets']==[]
 q['aki_column_candidate']='HEAD_LOCAL_VNEXT_TYPO'
 with pytest.raises(LocalAKIError,match='UNKNOWN_CANDIDATE_MODE'):build(q,src)


def test_capital_external_archive_restores_without_network_and_stake_only(tmp_path):
 from tools.local_aki_external_acceptance import restore_archived_receipts
 restore_archived_receipts(tmp_path,'KM-LOCAL-KAW-20261013-R12-LIVE-R1','f613ba0c2da58926')
 f=json.loads((tmp_path/'final_receipt.json').read_text())['artifact']['final_prediction_package']
 c=f['paper_tickets'];d=f['capital_paper_arm']['allocation']['tickets']
 keys=lambda tickets:{(t['bet_type'],tuple(t['selection'])) for t in tickets}
 assert keys(c)==keys(d)
 assert sum(t['stake'] for t in d)==15800
 assert all(t['stake']%100==0 and t['stake']>=100 for t in d)
 assert f['capital_paper_arm']['virtual_time_is_prestart_evidence'] is False
 assert f['temporal_mode']=='REPLAY' and f['purchase_authority'] is False
 assert json.loads((tmp_path/'capital_arm_settlement.json').read_text())['return']==80460

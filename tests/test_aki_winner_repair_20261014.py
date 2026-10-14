"""Real frozen field: normalization correctness is separate from performance."""
import gzip,json,copy,hashlib,sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_aki_vnext_20261014 import real
from local_aki_columns import build,decision
ROOT=Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('race,winner',[(1,'6'),(6,'1'),(7,'1')])
def test_field_scale_repairs_admission_induced_winner_loss(race,winner):
 q,src=real(race);before=copy.deepcopy(q);old=build(q,src)
 q['aki_column_candidate']='HEAD_LOCAL_VNEXT_R2';new=build(q,src)
 assert winner not in old['columns']['W']['selected']
 assert winner in new['columns']['W']['selected']
 assert old['column_diagnostics']['W']['risk']==new['column_diagnostics']['W']['risk']
 assert old['column_diagnostics']['W']['leader']==new['column_diagnostics']['W']['leader']
 d=new['column_diagnostics']['W'];scores=d['normalization_scores']
 assert d['score_span']==max(scores.values())-min(scores.values())
 assert d['gap_limit']==d['score_span']*d['risk']/100
 assert set(new['columns']['W']['selected']) <= {str(x['runner_id']) for x in q['role_registry'] if x['column']=='W'}
 q['aki_column_candidate']='HEAD_LOCAL_VNEXT_R1';assert q==before


def test_outcome_and_budget_cannot_add_winner_or_change_selection():
 q,src=real(9);q['aki_column_candidate']='HEAD_LOCAL_VNEXT_R2';s=build(q,src)
 assert '7' not in s['columns']['W']['selected'] # remaining policy failure, never outcome repair
 q['official_result']={'top3':[7,2,3]};q['capital_policy']={'max_race_capital':999999}
 assert build(q,src)==s


def test_winner_restore_does_not_claim_p2_or_success_restore():
 q,src=real(6);q['aki_column_candidate']='HEAD_LOCAL_VNEXT_R2';s=build(q,src)
 assert '1' in s['columns']['W']['selected']
 assert not any(str(p['head'])=='1' and str(p['second'])=='7' for p in s['pair_dispositions'])
 assert not any(t['bet_type']=='TRIFECTA' and t['selection']==[1,7,4] for t in decision(q,s)['paper_tickets'])


def test_old_observations_unchanged_and_failed_candidate_not_admitted():
 old=ROOT/'research/aki_vnext_20261014/full_report.json.gz'
 c=json.loads(gzip.decompress((ROOT/'research/aki_winner_repair_20261014/comparison.json.gz').read_bytes()))
 assert c['prior_observation_gzip_sha256']==hashlib.sha256(old.read_bytes()).hexdigest()
 assert c['forward_admission']=='REJECTED' and c['new_preregistered_arms']==c['genuine_forward_count']==0
 r=json.loads(gzip.decompress(old.read_bytes()))
 assert c['old_R1_aggregate']==r['original17_and_replay']
 assert c['new_R2_aggregate']['C_SELECTION']['aggregate']['investment']==89800
 assert c['new_R2_aggregate']['C_SELECTION']['aggregate']['return']==69550


def test_default_and_r1_selection_hashes_match_all_17_saved_observations():
 from local_fullnumerical_production import materialize_production
 old=json.loads(gzip.decompress((ROOT/'research/aki_vnext_20261014/full_report.json.gz').read_bytes()))
 for row in old['rows']:
  rid=row['race_id'];q=json.loads((ROOT/'runtime/formal_intents'/f'{rid}.json').read_text())
  src=json.loads(next((ROOT/'runtime/executions'/rid/'FORMAL').rglob('source_receipt_envelope.json')).read_text())['artifact']
  q['source_snapshot_sha256']=src['source_snapshot_sha256'];q=materialize_production(src,q,q['required_indices'])
  assert decision(q,build(q,src))['paper_tickets']==row['arms']['PR262_REFERENCE']['tickets']
  q['aki_column_candidate']='HEAD_LOCAL_VNEXT_R1';selected=build(q,src)
  assert selected['sha256']==row['selection']['sha256']
  assert decision(q,selected)['paper_tickets']==row['arms']['C_SELECTION']['tickets']

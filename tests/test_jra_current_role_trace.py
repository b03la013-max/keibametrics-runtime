"""Current JRA trace projection; preserve old frozen artifacts and formulas."""
import copy,json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
from jra_index_provenance_builder import materialize_index_provenance,IndexLedgerError
from jra_krs_input_builder_production import build_krs_input

def request():return json.loads((ROOT/'runtime/requests/KM-JRA-TKY-20261031-R08-LIVE-R1-FORMAL.json').read_text())
def trace(q):return materialize_index_provenance(q)['index_provenance_replay']['runners']

def test_registered_current_horse_roles_reach_trace_with_frozen_numerical_values():
 q=build_krs_input(request());before=copy.deepcopy(q);out=materialize_index_provenance(q)
 assert q==before
 assert {h:r['static_roles'] for h,r in out['index_provenance_replay']['runners'].items()}=={h:sorted(rs) for h,rs in q['static_prediction']['roles'].items()}
 for old,new in zip(q['runners'],out['runners']):
  assert {k:v['value'] for k,v in old['canonical_components'].items()}=={k:v['value'] for k,v in new['canonical_components'].items()}

def test_explicit_current_empty_map_and_runner_role_remain_empty_despite_stale_W():
 q=request();q['static_prediction']['roles']={};q['runners'][0]['static_roles']=['W']
 assert all(r['static_roles']==[] for r in trace(build_krs_input(q)).values())
 q=request();h=str(q['runners'][0]['runner_id']);q['static_prediction']['roles'][h]=[];q['runners'][0]['static_roles']=['W']
 assert trace(build_krs_input(q))[h]['static_roles']==[]

def test_old_column_to_runner_map_keeps_legacy_trace_semantics():
 q=request();cols={'W':['7'],'P2':['2','7','13'],'P3':['4','7','13']};q['static_prediction']['roles']=cols
 assert {h:r['static_roles'] for h,r in trace(q).items()}=={str(r['runner_id']):sorted(c for c,ids in cols.items() if str(r['runner_id']) in ids) for r in q['runners']}

@pytest.mark.parametrize('mode',['ABSENT','SHADOW','LOCAL','BAN'])
def test_default_non_authoritative_and_other_family_readers_are_not_reinterpreted(mode):
 q=request()
 if mode=='ABSENT':q.pop('static_prediction')
 elif mode=='SHADOW':q['static_prediction']['production_authority']=False
 else:q['family_id']=mode
 assert all(r['static_roles']==[] for r in trace(q).values())

@pytest.mark.parametrize('bad',[None,{'1':['W']},'UNKNOWN'])
def test_malformed_current_map_does_not_turn_into_a_legacy_trace(bad):
 q=build_krs_input(request());q['static_prediction']['roles']=bad
 with pytest.raises(IndexLedgerError):trace(q)

def test_new_trace_hash_is_not_retroactively_bound_to_original_signed_receipt():
 path=ROOT/'runtime/final_artifacts/KM-JRA-TKY-20261031-R08.json';raw=path.read_bytes();f=json.loads(raw);out=materialize_index_provenance(request())
 assert out['index_provenance_hash']==f['index_provenance_hash']
 assert materialize_index_provenance(build_krs_input(request()))['index_provenance_hash']!=f['index_provenance_hash']
 assert path.read_bytes()==raw

@pytest.mark.parametrize('field',['static_role_binding_version','static_role_map_sha256'])
def test_marked_trace_version_and_role_map_hash_are_not_ignored(field):
 q=build_krs_input(request());q['explicit_engine_hsv_provenance'][field]='INVALID'
 with pytest.raises(IndexLedgerError):trace(q)

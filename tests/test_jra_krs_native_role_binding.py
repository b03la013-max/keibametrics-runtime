"""Frozen client inputs, no Engine calls, new SOURCE or new numerical rules."""
import copy,json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
from jra_krs_input_builder_production import build_krs_input,build_runner_input,KRSInputBridgeError

def request():return json.loads((ROOT/'runtime/requests/KM-JRA-TKY-20261031-R08-LIVE-R1-FORMAL.json').read_text())
def roles(out):return {str(h['horse_no']):h['static_roles'] for h in out['krs_input_data']['horses']}

def test_registered_current_static_roles_reach_native_without_changing_frozen_numbers():
 q=request();before=copy.deepcopy(q);out=build_krs_input(q)
 assert roles(out)==q['static_prediction']['roles'] and q==before
 saved={str(h['horse_no']):h for h in q['krs_input_data']['horses']}
 for h in out['krs_input_data']['horses']:
  for field in ('hsv','static','uncertainty_scale'):assert h[field]==saved[str(h['horse_no'])][field]
 assert out['runners']==q['runners'] and out['static_prediction']==q['static_prediction'] and out['source_snapshot']==q['source_snapshot']

def test_current_empty_map_or_empty_runner_role_never_revives_stale_embedded_W():
 q=request();q['static_prediction']['roles']={};q['runners'][0]['static_roles']=['W']
 assert all(rs==[] for rs in roles(build_krs_input(q)).values())
 q=request();h=str(q['runners'][0]['runner_id']);q['static_prediction']['roles'][h]=[];q['runners'][0]['static_roles']=['W']
 assert roles(build_krs_input(q))[h]==[]

@pytest.mark.parametrize('mode',['ABSENT','LEGACY_COLUMN','SHADOW','LOCAL','BAN'])
def test_legacy_and_other_family_metadata_behavior_remains(mode):
 q=request();h=str(q['runners'][0]['runner_id']);q['runners'][0]['static_roles']=['P3']
 if mode=='ABSENT':q['static_prediction'].pop('roles')
 elif mode=='LEGACY_COLUMN':q['static_prediction']['roles']={'W':['7'],'P2':['2','13'],'P3':['4']}
 elif mode=='SHADOW':q['static_prediction']['production_authority']=False
 else:q['family_id']=mode
 assert roles(build_krs_input(q))[h]==['P3']

@pytest.mark.parametrize('bad',[None,{'1':['W']},'UNKNOWN'])
def test_malformed_formal_map_cannot_be_filled_from_stale_runner(bad):
 q=request();q['static_prediction']['roles']=bad;q['runners'][0]['static_roles']=['W']
 with pytest.raises(KRSInputBridgeError):build_krs_input(q)

@pytest.mark.parametrize('bad',[['W','W'],['UNKNOWN']])
def test_unknown_or_duplicate_role_is_not_authorized(bad):
 q=request();q['static_prediction']['roles']['1']=bad
 with pytest.raises(KRSInputBridgeError):build_krs_input(q)

def test_direct_legacy_runner_api_and_explicit_empty_override_are_distinct():
 r=request()['runners'][0];r['static_roles']=['W']
 assert build_runner_input(r)['static_roles']==['W']
 assert build_runner_input(r,static_roles=[])['static_roles']==[]

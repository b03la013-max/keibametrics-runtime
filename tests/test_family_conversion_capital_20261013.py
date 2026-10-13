import copy,json,sys,math
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
from family_conversion_diagnostics import measure_capital_conversion,build_diagnostics
from family_pfs_promotion_gate import evaluate_promotion_gate,_num
from pfs_grand_review import _venue,_family
from family_pfs_improvement import classify_dominant_pfs_loss_owner

def race(r):
 rid=f'KM-LOCAL-KAW-20261013-R{r:02}-LIVE-R1';req=json.loads((ROOT/'runtime/formal_intents'/f'{rid}.json').read_text());d=next((ROOT/'runtime/executions'/rid/'FORMAL').rglob('final_receipt_envelope.json')).parent;a=json.loads((d/'final_receipt_envelope.json').read_text())['artifact'];s=json.loads((d/'aki_adaptive_purchase_shadow_pre_result.json').read_text());return req,a,s
@pytest.mark.parametrize('r',[1,3,5,6,7,9,10,12])
def test_real_pair_capital_measurement_never_selects(r):
 req,a,s=race(r);before=copy.deepcopy((req,a,s));q=measure_capital_conversion(req,a['final_ticket'],a['final_prediction_package'],a['final_prediction_package']['krs_prediction_utility_shadow'],candidate_tickets=s['candidate_tickets'])
 assert (req,a,s)==before and q['investment']==s['candidate_capital_yen']
 assert sum(q['exposure']['bet_type'].values())==q['investment'] and q['expected_value'] is None
 assert all(x['purchase_required'] is False for x in q['material_pair_losses'])
 if r in [3,9,12]:assert q['material_pair_losses']
 if r==10:assert any(x['runner_id']=='3' for x in q['unknown_role_review'])
@pytest.mark.parametrize('family',['LOCAL','JRA','BAN'])
def test_common_money_measurement_has_no_family_coefficients(family):
 req={'family_id':family,'race_id':'R','pair_dispositions':[]};ticket={'tickets':[{'bet_type':'TRIO','selection':[1,2,3],'stake':100}]};m=measure_capital_conversion(req,ticket,{},{});assert m['exposure']['head']=={} and m['exposure']['pair']=={} and m['unclassified_tier_capital']==100 and m['family_numeric_authority_changed'] is False
@pytest.mark.parametrize('value',[float('inf'),float('-inf'),float('nan'),'inf',True])
def test_nonfinite_is_missing_not_promotion_evidence(value):
 assert _num(value) is None
 d=evaluate_promotion_gate({'eligible_races':30,'distinct_days':3,'candidate_pfs':value})
 assert d['verdict']=='HOLD_INCOMPLETE_OR_INTEGRITY' and d['production_change_authorized'] is False
@pytest.mark.parametrize('venue',['KCH','KNZ','MIZ','HIM'])
def test_existing_local_venues_are_not_unknown(venue):
 rid=f'KM-LOCAL-{venue}-20261013-R01';assert _venue(rid)==venue and _family(rid)=='LOCAL'
def test_opt_in_leaves_existing_diagnostic_unchanged():
 req,a,s=race(6);fpp=a['final_prediction_package'];u=fpp['krs_prediction_utility_shadow'];args=(req,a['final_ticket'],fpp,u,s['generated_at'],'basis');old=build_diagnostics(*args)
 req2=copy.deepcopy(req);req2['family_capital_conversion_measurement']=True;new=build_diagnostics(req2,*args[1:]);assert 'capital_conversion_measurement' not in old
 stripped={k:v for k,v in new.items() if k not in ['capital_conversion_measurement','sha256']};assert stripped=={k:v for k,v in old.items() if k!='sha256'}
def test_first_failure_and_dominant_owner_are_distinct():
 req,a,s=race(1);rid=req['race_id'];p=next((ROOT/'runtime/executions'/rid/'RESULT').rglob('result_receipt_envelope.json'));review=json.loads(p.read_text())['artifact']['automatic_post_result_review'];assert review['failure_localization']['first_material_failure']=='ORDERED_PAIR_CONVERSION';assert classify_dominant_pfs_loss_owner(review)['owner']=='CAPITAL'

def test_historical_snapshot_does_not_read_mutable_live_17(tmp_path):
 from family_pfs_regression_readout import build_regression_readout
 import shutil
 shutil.copytree(ROOT/'research/common',tmp_path/'research/common')
 manifest=tmp_path/'research/common/KM-FAMILY-OHI-20261009-DAY-R43-REGRESSION-R1.json'
 # Source RESULT records stay actual and immutable.
 (tmp_path/'runtime').mkdir()
 for row in json.loads(manifest.read_text())['verified_result_records']:
  dest=tmp_path/row['result_summary_path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['result_summary_path'],dest)
 (tmp_path/'runtime/aki_adaptive_oos_status.json').write_text('{"corrupt_live_view":true}')
 report=build_regression_readout(tmp_path,manifest)
 assert report['paired_aki_paper']['candidate']['investment']==9200
 assert report['paired_aki_paper']['oos_increment_from_this_regression']==0
 assert (tmp_path/'runtime/aki_adaptive_oos_status.json').read_text()=='{"corrupt_live_view":true}'

@pytest.mark.parametrize('value',[float('inf'),float('nan'),True])
def test_nonfinite_learning_loss_owner_is_unknown(value):
 review={'race_id':'R','capital':{'pfs':value},'failure_localization':{'first_material_failure':'NONE'}}
 assert classify_dominant_pfs_loss_owner(review)['owner']=='UNKNOWN'

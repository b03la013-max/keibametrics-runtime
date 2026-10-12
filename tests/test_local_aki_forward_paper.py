"""Real pre-start archives plus fail-closed chronology; no external requests."""
import datetime as dt
import json
from pathlib import Path
import pytest
from tools.local_aki_forward_archive import restore,MANIFEST
from tools.local_aki_forward_result_worker import validate_forward_freeze,validate_krs_chain,run_case
from tools.local_aki_external_acceptance import _run
ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def unpacked(tmp_path_factory):
    target=tmp_path_factory.mktemp('real_forward_archive')
    assert restore(target)['network_calls']==0
    return target,json.loads(MANIFEST.read_text())


@pytest.mark.parametrize('venue,count',[('MON',30),('MOR',45),('KAW',119),('KNZ',13),('NGY',10)])
def test_real_five_forward_signatures_independent_numerics_and_krs(unpacked,venue,count):
    target,manifest=unpacked
    case=next(c for c in manifest['cases'] if c['terminal']['venue_id']==venue)
    t=case['terminal'];directory=target/case['output_path']
    source=json.loads((target/t['source_path']).read_text());intent=json.loads((target/t['intent_path']).read_text())
    final=json.loads((directory/'final_receipt.json').read_text());selection=json.loads((directory/'selection.json').read_text())
    plan=json.loads((target/'profiles/local_aki_prospective_evaluation_20261013_R2.json').read_text())
    q=validate_forward_freeze(intent,source,final,selection,plan);validate_krs_chain(directory,intent,final)
    assert q['numeric_coverage']['unresolved_count']==0
    assert q['numeric_coverage']['required_count']==29*len(q['runners'])
    assert len(final['artifact']['final_prediction_package']['paper_tickets'])==count
    assert final['artifact']['capital_policy_decision']['decision']=='PAPER'
    assert final['artifact']['final_ticket']['tickets']==[]
    assert case['acceptance']['unknown_future_oos_count']==0
    assert final['artifact']['final_prediction_package']['temporal_mode']=='FORWARD_PAPER'


def test_signed_final_cannot_be_declared_preregistered_after_its_freeze(unpacked):
    target,m=unpacked;c=m['cases'][0];t=c['terminal'];d=target/c['output_path']
    source=json.loads((target/t['source_path']).read_text());intent=json.loads((target/t['intent_path']).read_text())
    final=json.loads((d/'final_receipt.json').read_text());selection=json.loads((d/'selection.json').read_text())
    plan=json.loads((target/'profiles/local_aki_prospective_evaluation_20261013_R2.json').read_text())
    plan['registered_at']='2026-10-14T00:00:00+09:00'
    with pytest.raises(ValueError,match='PREREGISTRATION_FINAL_BINDING_INVALID'):
        validate_forward_freeze(intent,source,final,selection,plan)


def test_archived_past_source_cannot_start_a_new_forward_job(tmp_path):
    race='KM-LOCAL-OHI-20261007-R04-LIVE-R1'
    request=json.loads((ROOT/('runtime/formal_intents/'+race+'.json')).read_text())
    request.update(aki_temporal_mode='FORWARD_PAPER',prospective_evaluation_plan='profiles/local_aki_prospective_evaluation_20261013_R2.json')
    p=tmp_path/'intent.json';p.write_text(json.dumps(request))
    source=ROOT/('runtime/executions/'+race+'/FORMAL/runs/37582570990-formal/source_receipt_envelope.json')
    with pytest.raises(RuntimeError,match='FORWARD_REGISTRATION_SOURCE_CUTOFF_POST_ORDER_INVALID'):
        _run(p,source,tmp_path/'out')


def test_not_yet_post_is_waiting_not_success_failure_or_oos(monkeypatch):
    import urllib.request
    def no_network(*args,**kwargs):raise AssertionError('result not yet due')
    monkeypatch.setattr(urllib.request,'urlopen',no_network)
    plan=json.loads((ROOT/'profiles/local_aki_prospective_evaluation_20261013_R2.json').read_text())
    pilot=json.loads((ROOT/'research/local_aki_forward_20261013/pilot_status.json').read_text())
    for t in pilot['results']:
        r=run_case(t,plan,now=dt.datetime.fromisoformat('2026-10-13T02:00:00+09:00'))
        assert r['status']=='WAITING_OFFICIAL_RESULT / NOT_YET_POST'
        assert r['unknown_future_oos_count']==0

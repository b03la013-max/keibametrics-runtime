"""Synthetic forward round-trip; no original data, HTTP, signing or purchase."""
import argparse
import ast
import copy
from datetime import datetime,timedelta,timezone
from pathlib import Path

import pytest

from scripts import urw_paper_selection_replay as cli
from runtime.local_race_key_shadow_owner import predict_conditioned_owner
from runtime.urw_paper_selection import sha
from runtime.urw_nankan_reference_source import save_json


def seal(x):
    x.pop('sha256',None);x['sha256']=sha(x);return x


def protocol(models):
    path=cli.ROOT/'scripts/urw_candidate_krs_replay.py'
    nodes=[n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='owner_forward_protocol']
    ns={'_sha':sha};exec(compile(ast.Module(body=nodes,type_ignores=[]),'synthetic_existing_protocol','exec'),ns)
    return ns['owner_forward_protocol'](models['BASELINE'],models['CANDIDATE'])


def bundle(no=1):
    t=datetime.now(timezone.utc);day='2099-10-21';race_id=f'KM-LOCAL-URW-20991021-R{no:02}-SYNTHETIC'
    post=f'{day}T{12+(no-1)//2:02}:{20+30*((no-1)%2):02}:00+09:00'
    cutoff=(datetime.fromisoformat(post)-timedelta(minutes=2)).isoformat()
    race={'provider':'NANKAN_OFFICIAL','venue_id':'URW','race_date':day,'race_no':no,
          'provider_race_id':f'20991021180703{no:02}','scheduled_post_at':post,'prediction_cutoff':cutoff,'distance':1400}
    source={'raw_sha256':'synthetic_raw','fetched_at':(t-timedelta(minutes=1)).isoformat()}
    pack=seal({'race_id':race_id,'venue_id':'URW','race_date':day,'scheduled_post_at':post,'prediction_cutoff':cutoff,
          'source_snapshot_sha256':source['raw_sha256'],'source_observed_at':source['fetched_at'],
          'venue_canon':'SYNTHETIC_ONLY','venue_canon_source_sha256':'synthetic_canon',
          'runners':{str(i):{'INDEX:SYNTHETIC':float(i),'STAGE:progression':None,'STAGE:final_reserve':None} for i in range(1,5)},
          'baseline':{role:list(map(str,range(1,5))) for role in ('W','P2','P3')},'production_authority':False})
    models={arm:seal({'venue_id':'URW','venue_canon':pack['venue_canon'],'venue_canon_source_sha256':pack['venue_canon_source_sha256'],
          'training_races':[],'training_max_post_at':'2026-10-20T12:00:00+09:00',
          'trained_at':'2026-10-20T11:00:00+09:00','stage_evidence':False,'interactions':False,
          'fits':[{'feature_names':['INDEX:SYNTHETIC'],'training_means':[0.0],'training_scales':[1.0],
                   'coefficients':[coef]} for _ in range(3)],'production_authority':False})
          for arm,coef in (('BASELINE',0.1),('CANDIDATE',0.2))}
    predictions={a:predict_conditioned_owner(m,pack) for a,m in models.items()}
    frozen=seal({'race_id':race_id,'race_date':day,'scheduled_post_at':post,'prediction_cutoff':cutoff,
                 'same_source_snapshot_sha256':source['raw_sha256'],'feature_pack':pack,'models':models,
                 'predictions':predictions,'frozen_at':datetime.now(timezone.utc).isoformat(),'protocol':protocol(models)})
    audits={}
    for arm,pred in predictions.items():
        template={'semantic_request':{'family_id':'LOCAL','race_id':race_id,'runners':[{'runner_id':str(i)} for i in range(1,5)],
                   'capital_policy':{'mode':'HARD_RACE_BUDGET','max_race_capital':0,'insufficient_action':'PAPER'}}}
        rebuilt=cli._research_mec(pred,template)
        snapshot={'prediction_id':race_id,'date':day,'race_no':no,'master_seed':1}
        ku=seal({'race_id':race_id,'snapshot':{'master_seed':1},'krs_status':'EXECUTED',
                  'top_exacta_occurrence':[],'top_trifecta_occurrence':[]})
        stamp=datetime.now(timezone.utc).isoformat()
        audits[arm]=seal({**rebuilt,'race_id':race_id,'reference_static':pred,
             'source_snapshot_sha256':source['raw_sha256'],'snapshot':snapshot,'master_seed':1,
             'started_at':stamp,'completed_at':stamp,'krs_utility':ku,'krs_input_sha256':'synthetic_input',
             'krs_output_file_sha256':'synthetic_output',
             'ticket_tree':{'reflattened_tickets':cli.canonical_tickets(rebuilt['mec']['tickets'])}})
    obs={'race':race,'source':source,'facts':[{'runner_id':str(i),'status':'ACTIVE_DECLARED','starts':[]} for i in range(1,5)]}
    return {'frozen':frozen,'audits':audits,'observation':obs}


def setup(tmp_path,monkeypatch,b):
    tmp_path.chmod(0o700);bp=tmp_path/'bundle.json';save_json(bp,b)
    mp=tmp_path/'model-comparison.json';save_json(mp,b['frozen'])
    reg=tmp_path/'registration.json';ledger=tmp_path/'ledger'
    # Only the registration clock is offset in this synthetic test; forecasting
    # itself uses the real compiler clock. There is no CLI clock override.
    monkeypatch.setattr(cli,'now',lambda:datetime.now(timezone.utc)-timedelta(seconds=30))
    cli.register(argparse.Namespace(model_bundle=mp,output=reg,ledger=ledger))
    monkeypatch.setattr(cli,'now',lambda:datetime.now(timezone.utc))
    races=[]
    for i in range(1,13):races.append({'fields':bundle(i)['observation']['race']})
    plan={'family_id':'LOCAL','venue_id':'URW','race_date':'2099-10-21','races':races}
    plan['plan_sha256']=sha(plan);pp=tmp_path/'day-plan.json';save_json(pp,plan)
    cli.register_day(argparse.Namespace(registration=reg,day_plan=pp))
    return argparse.Namespace(registration=reg,input_bundle=bp,ledger=ledger,output=tmp_path/'freeze')


def test_real_model_four_cell_forward_freeze_and_duplicate_protection(tmp_path,monkeypatch):
    b=bundle();a=setup(tmp_path,monkeypatch,b);cli.freeze(a)
    result=cli.read(a.output/'research-selection-freeze.json')
    assert result['formal_quality_credit']==0 and not result['signed_final_claim']
    assert set(result['views']['CANDIDATE']['cells'])==set(cli.CELLS)
    assert len(list(a.ledger.glob('event-*.json')))==2
    with pytest.raises(ValueError,match='DUPLICATE'):cli.freeze(a)
    status=tmp_path/'status.json';cli.cohort_status(argparse.Namespace(registration=a.registration,output=status))
    assert cli.read(status)['planned_fixed_denominator']==12
    assert len(cli.read(status)['races'])==12  # Eleven uninvoked races retained.


@pytest.mark.parametrize('bad',['model_body','model_declared_sha','conditional_output','cutoff','source_time','labels','future_audit'])
def test_forward_bad_inputs_hold_and_remain_in_event_denominator(tmp_path,monkeypatch,bad):
    b=bundle();a=setup(tmp_path,monkeypatch,b)
    if bad=='model_body':b['frozen']['models']['BASELINE']['fits'][0]['coefficients'][0]+=1
    if bad=='model_declared_sha':b['frozen']['predictions']['BASELINE']['model_sha256']='other';seal(b['frozen']['predictions']['BASELINE'])
    if bad=='conditional_output':
        p=b['frozen']['predictions']['BASELINE'];p['ranking'].reverse();seal(p)
        b['audits']['BASELINE']['reference_static']=p;seal(b['audits']['BASELINE'])
    if bad=='cutoff':b['frozen']['prediction_cutoff']='not-a-timestamp'
    if bad=='source_time':b['observation']['source']['fetched_at']='2026-01-01T00:00:00+09:00'
    if bad=='labels':b['observation']['official_result']={'top3':[1,2,3]}
    if bad=='future_audit':
        a0=b['audits']['BASELINE'];a0['started_at']=a0['completed_at']=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat();seal(a0)
    seal(b['frozen']);a.input_bundle=tmp_path/'bad.json';save_json(a.input_bundle,b)
    with pytest.raises((ValueError,KeyError)):cli.freeze(a)
    es=[cli.read(p) for p in sorted(a.ledger.glob('event-*.json'))]
    assert es[0]['status']=='ATTEMPT_RESERVED'
    assert es[-1]['status']=='HOLD_RETAINED_IN_DENOMINATOR'
    assert not (a.output/'research-selection-freeze.json').exists()


def test_crash_before_completion_preserves_reservation_and_other_ledger_rejected(tmp_path,monkeypatch):
    b=bundle();a=setup(tmp_path,monkeypatch,b);real_save=cli.save_json
    def fail_completion(path,value):
        if Path(path).name=='event-0002.json':raise OSError('SYNTHETIC_CRASH_AFTER_ARTIFACT')
        return real_save(path,value)
    monkeypatch.setattr(cli,'save_json',fail_completion)
    with pytest.raises(OSError):cli.freeze(a)
    assert (a.output/'research-selection-freeze.json').exists()
    reservation=cli.read(a.ledger/'event-0001.json')
    assert reservation['remaining']['CANDIDATE']['P0S1']==22000
    with pytest.raises(ValueError,match='DUPLICATE'):cli.freeze(a)
    a.ledger=tmp_path/'new-ledger'
    with pytest.raises(ValueError,match='CANONICAL_LEDGER'):cli.freeze(a)


def test_partial_result_summary_never_certifies_full_day_pfs():
    one={'status':'SETTLED','investment':100,'return':500,'refund':0,'profit_loss':400}
    value=cli._summary([one],12,planned_investment=1200)
    assert value['return'] is None and value['pfs'] is None and value['profit_loss'] is None
    assert value['investment']==1200 and value['observed_partial_return_not_full_day']==500


def test_uncompleted_later_race_reservation_still_blocks_old_race(tmp_path,monkeypatch):
    b=bundle(5);a=setup(tmp_path,monkeypatch,b);real_save=cli.save_json
    def fail_completion(path,value):
        if Path(path).name=='event-0002.json':raise OSError('SYNTHETIC_COMPLETION_FAILURE')
        return real_save(path,value)
    monkeypatch.setattr(cli,'save_json',fail_completion)
    with pytest.raises(OSError):cli.freeze(a)
    monkeypatch.setattr(cli,'save_json',real_save)
    older=bundle(4);a.input_bundle=tmp_path/'older.json';save_json(a.input_bundle,older);a.output=tmp_path/'older-freeze'
    with pytest.raises(ValueError,match='RACE_ORDER'):cli.freeze(a)


def test_explicit_cancellation_reaches_all_research_selectors_not_original_s0():
    b=bundle();b['observation']['facts'][3]['status']='CANCELLED'
    remaining={a:{k:24000 for k in ('P0S1','P1S1','P0S1_NO_KRS')} for a in cli.ARMS}
    views=cli.build_views(b['frozen'],b['audits'],b['observation'],remaining)
    for v in views.values():
        assert any(4 in t['selection'] for t in v['cells']['P0S0']['tickets'])
        for name in ('P0S1','P1S1'):
            assert not any(4 in t['selection'] for t in v['cells'][name]['tickets'])
        assert not any(4 in t['selection'] for t in v['P0S1_NO_KRS']['selected_tickets'])
        assert not any(4 in t['selection'] for t in v['TOP4_BOX_DIAGNOSTIC'])

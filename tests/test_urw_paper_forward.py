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
from runtime.urw_nankan_reference_source import save_json,immutable


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


def refresh_checkpoint(args):
    paths=list(args.registration.parent.glob('ledger-checkpoint-*.json'))
    path=args.registration.parent/f'ledger-checkpoint-{len(paths):03d}.json'
    cli.checkpoint(argparse.Namespace(registration=args.registration,output=path))
    args.ledger_checkpoint=path
    args.expected_checkpoint_sha256=cli.file_sha(path)
    return args


def setup(tmp_path,monkeypatch,b):
    tmp_path.chmod(0o700);bp=tmp_path/'bundle.json';save_json(bp,b)
    mp=tmp_path/'model-comparison.json';save_json(mp,b['frozen'])
    reg=tmp_path/'registration.json';ledger=tmp_path/'ledger'
    # Only the registration clock is offset in this synthetic test; forecasting
    # itself uses the real compiler clock. There is no CLI clock override.
    monkeypatch.setattr(cli,'now',lambda:datetime.now(timezone.utc)-timedelta(seconds=30))
    cli.register(argparse.Namespace(model_bundle=mp,output=reg,ledger=ledger))
    monkeypatch.setattr(cli,'now',lambda:datetime.now(timezone.utc))
    args=refresh_checkpoint(argparse.Namespace(registration=reg,input_bundle=bp,ledger=ledger,
                                              output=tmp_path/'freeze'))
    races=[]
    for i in range(1,13):races.append({'fields':bundle(i)['observation']['race']})
    plan={'family_id':'LOCAL','venue_id':'URW','race_date':'2099-10-21','races':races}
    plan['plan_sha256']=sha(plan);pp=tmp_path/'day-plan.json';save_json(pp,plan)
    cli.register_day(argparse.Namespace(registration=reg,day_plan=pp,
        ledger_checkpoint=args.ledger_checkpoint,expected_checkpoint_sha256=args.expected_checkpoint_sha256))
    return refresh_checkpoint(args)


def test_real_model_four_cell_forward_freeze_and_duplicate_protection(tmp_path,monkeypatch):
    b=bundle();a=setup(tmp_path,monkeypatch,b);cli.freeze(a)
    result=cli.read(a.output/'research-selection-freeze.json')
    assert result['formal_quality_credit']==0 and not result['signed_final_claim']
    assert set(result['views']['CANDIDATE']['cells'])==set(cli.CELLS)
    assert len(list(a.ledger.glob('event-*.json')))==2
    refresh_checkpoint(a)
    with pytest.raises(ValueError,match='DUPLICATE'):cli.freeze(a)
    status=tmp_path/'status.json';cli.cohort_status(argparse.Namespace(registration=a.registration,output=status,
        ledger_checkpoint=a.ledger_checkpoint,expected_checkpoint_sha256=a.expected_checkpoint_sha256))
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
    refresh_checkpoint(a)
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
    refresh_checkpoint(a)
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


@pytest.mark.parametrize('conflicting',[False,True])
def test_duplicate_runner_facts_cannot_choose_last_row_or_change_exclusion(conflicting):
    b=bundle();duplicate=copy.deepcopy(b['observation']['facts'][0])
    if conflicting:duplicate['status']='CANCELLED'
    b['observation']['facts'].append(duplicate)
    remaining={a:{k:24000 for k in ('P0S1','P1S1','P0S1_NO_KRS')} for a in cli.ARMS}
    with pytest.raises(ValueError,match='OBSERVATION_RUNNER_UNIVERSE_OR_DUPLICATE'):
        cli.build_views(b['frozen'],b['audits'],b['observation'],remaining)


def test_day_validator_is_pinned_and_wrong_policy_digest_is_refused(tmp_path,monkeypatch):
    b=bundle();a=setup(tmp_path,monkeypatch,b)
    assert 'runtime/local_reference_day.py' in cli.code_pins()
    reg=cli.read(a.registration);reg['policy_sha256']='0'*64;seal(reg)
    a.registration=tmp_path/'wrong-policy-digest.json';save_json(a.registration,reg)
    with pytest.raises(ValueError,match='PREREGISTERED_CODE_OR_POLICY_CHANGED'):
        cli.cohort_status(argparse.Namespace(registration=a.registration,output=tmp_path/'status.json'))


def test_day_validator_code_change_requires_new_registration(tmp_path,monkeypatch):
    a=setup(tmp_path,monkeypatch,bundle());pins=cli.code_pins()
    pins['runtime/local_reference_day.py']='0'*64
    monkeypatch.setattr(cli,'code_pins',lambda:pins)
    with pytest.raises(ValueError,match='PREREGISTERED_CODE_OR_POLICY_CHANGED'):
        cli.freeze(a)


def test_artifact_write_finishing_after_cutoff_is_a_hold(tmp_path,monkeypatch):
    b=bundle();a=setup(tmp_path,monkeypatch,b);real_save=cli.save_json
    clock=[datetime.now(timezone.utc)]
    monkeypatch.setattr(cli,'now',lambda:clock[0])
    def delayed_artifact(path,value):
        real_save(path,value)
        if Path(path).name=='research-selection-freeze.json':
            clock[0]=datetime.fromisoformat(b['frozen']['prediction_cutoff'])+timedelta(seconds=1)
    monkeypatch.setattr(cli,'save_json',delayed_artifact)
    with pytest.raises(ValueError,match='FORWARD_PERSISTED_AFTER_CUTOFF'):
        cli.freeze(a)
    completion=cli.read(a.ledger/'event-0002.json')
    assert completion['status']=='HOLD_RETAINED_IN_DENOMINATOR'
    assert completion['reason']=='FORWARD_PERSISTED_AFTER_CUTOFF'
    assert (a.output/'research-selection-freeze.json').exists()  # Immutable orphan, not an accepted Freeze.


@pytest.mark.parametrize('deletion',['all_events','last_event'])
def test_checkpoint_verifies_complete_restore_and_refuses_empty_or_suffix_rollback(tmp_path,monkeypatch,deletion):
    a=setup(tmp_path,monkeypatch,bundle());cli.freeze(a);refresh_checkpoint(a)
    cli.verify_restore(a)
    paths=sorted(a.ledger.glob('event-*.json'))
    originals={p:p.read_bytes() for p in paths}
    for path in paths if deletion=='all_events' else paths[-1:]:path.unlink()
    with pytest.raises(ValueError,match='CHECKPOINT_MISMATCH_RESTORE_COMPLETE_LEDGER'):
        cli.verify_restore(a)
    with pytest.raises(ValueError,match='CHECKPOINT_MISMATCH_RESTORE_COMPLETE_LEDGER'):
        cli.freeze(a)
    with pytest.raises(ValueError,match='CHECKPOINT_MISMATCH_RESTORE_COMPLETE_LEDGER'):
        cli.cohort_status(argparse.Namespace(registration=a.registration,output=tmp_path/'status.json',
            ledger_checkpoint=a.ledger_checkpoint,expected_checkpoint_sha256=a.expected_checkpoint_sha256))
    for path,raw in originals.items():
        if not path.exists():immutable(path,raw)
    cli.verify_restore(a)


def test_crash_reservation_is_part_of_full_checkpoint_restore(tmp_path,monkeypatch):
    a=setup(tmp_path,monkeypatch,bundle());real_save=cli.save_json
    def interrupted(path,value):
        if Path(path).name=='event-0002.json':raise OSError('SYNTHETIC_COMPLETION_CRASH')
        real_save(path,value)
    monkeypatch.setattr(cli,'save_json',interrupted)
    with pytest.raises(OSError):cli.freeze(a)
    monkeypatch.setattr(cli,'save_json',real_save);refresh_checkpoint(a)
    cli.verify_restore(a)
    checkpoint=cli.read(a.ledger_checkpoint)
    assert checkpoint['event_count']==1 and 'event-0001.json' in checkpoint['members']
    assert cli.read(a.ledger/'event-0001.json')['remaining']['CANDIDATE']['P0S1']==22000
    (a.ledger/'event-0001.json').unlink()
    with pytest.raises(ValueError,match='CHECKPOINT_MISMATCH_RESTORE_COMPLETE_LEDGER'):
        cli.verify_restore(a)


def test_old_or_altered_checkpoint_cannot_be_silently_used(tmp_path,monkeypatch):
    a=setup(tmp_path,monkeypatch,bundle());cli.freeze(a)
    with pytest.raises(ValueError,match='CHECKPOINT_MISMATCH_RESTORE_COMPLETE_LEDGER'):
        cli.freeze(a)  # The pre-attempt checkpoint is stale, even before duplicate checking.
    refresh_checkpoint(a)
    original_sha=a.expected_checkpoint_sha256
    replacement=tmp_path/'changed-checkpoint.json'
    raw=a.ledger_checkpoint.read_bytes()+b'\n';replacement.write_bytes(raw);replacement.chmod(0o600)
    a.ledger_checkpoint=replacement
    assert a.expected_checkpoint_sha256==original_sha
    with pytest.raises(ValueError,match='CHECKPOINT_FILE_SHA_MISMATCH'):
        cli.verify_restore(a)


@pytest.mark.parametrize('kind',['path_traversal','member_bytes','symlink'])
def test_checkpoint_rejects_bad_member_paths_integrity_and_symlinks(tmp_path,monkeypatch,kind):
    a=setup(tmp_path,monkeypatch,bundle())
    if kind=='symlink':
        (a.ledger/'event-9999.json').symlink_to(a.ledger/'initialization.json')
        match='CHECKPOINT_SYMLINK_OR_NONFILE'
    else:
        value=cli.read(a.ledger_checkpoint)
        if kind=='path_traversal':
            value['members']['../initialization.json']=value['members'].pop('initialization.json')
            match='CHECKPOINT_MEMBER_PATH'
        else:
            value['members']['initialization.json']['bytes']+=1
            match='CHECKPOINT_MEMBER_INTEGRITY'
        path=tmp_path/'bad-checkpoint.json';save_json(path,seal(value))
        a.ledger_checkpoint=path;a.expected_checkpoint_sha256=cli.file_sha(path)
    with pytest.raises(ValueError,match=match):cli.verify_restore(a)


def test_new_forward_invocation_requires_caller_trusted_checkpoint(tmp_path,monkeypatch):
    a=setup(tmp_path,monkeypatch,bundle());a.expected_checkpoint_sha256=None
    with pytest.raises(ValueError,match='CHECKPOINT_AND_TRUSTED_SHA_REQUIRED'):
        cli.freeze(a)
    assert not list(a.ledger.glob('event-*.json'))


@pytest.mark.parametrize('operation',['freeze','cohort_status','checkpoint'])
@pytest.mark.parametrize('nested',[False,True])
def test_forward_outputs_cannot_poison_canonical_ledger(tmp_path,monkeypatch,operation,nested):
    a=setup(tmp_path,monkeypatch,bundle())
    before={p.name:p.read_bytes() for p in a.ledger.iterdir()}
    a.output=a.ledger/'nested' if nested else a.ledger
    with pytest.raises(ValueError,match='OUTPUT_MUST_BE_OUTSIDE_LEDGER'):
        getattr(cli,operation)(a)
    assert {p.name:p.read_bytes() for p in a.ledger.iterdir()}==before
    cli.verify_restore(a)


def test_registration_output_cannot_create_an_unusable_ledger(tmp_path):
    mp=tmp_path/'models.json';save_json(mp,bundle()['frozen']);ledger=tmp_path/'ledger'
    with pytest.raises(ValueError,match='OUTPUT_MUST_BE_OUTSIDE_LEDGER'):
        cli.register(argparse.Namespace(model_bundle=mp,ledger=ledger,output=ledger/'registration.json'))
    assert not ledger.exists()

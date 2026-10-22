"""Synthetic transport tests, not unseen race-day or UI acceptance."""
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

import pytest

from runtime import urw_registered_paper_entry as p
from runtime import local_race_entry as entry


def fixture(tmp_path,monkeypatch,classification='POSTCUTOFF_DIAGNOSTIC_NOT_FORWARD'):
    # Keep the project's private-Git boundary intact even under a Git checkout.
    import tempfile
    root=Path(tempfile.mkdtemp(prefix='km-paper-transport-',dir='/var/tmp'))
    root.chmod(0o700);store=root/'store';folder=store/'races/2026-10-22/R02/fixture';folder.mkdir(parents=True,mode=0o700)
    reg={'sha256':'registration'};config={'store':str(store),'checkpoint_sha256':'initial-checkpoint'}
    monkeypatch.setattr(p,'configuration',lambda path:(config,reg,{}))
    pred={'ranking':['1','2','3']};tickets=[{'bet_type':'EXACTA','selection':[1,2],'stake':100}]
    methods={m:{'tickets':copy.deepcopy(tickets),'tree':p.tree(pred,tickets)} for m in p.METHODS}
    artifact=p.seal({'classification':classification,'prediction_cutoff':'2026-10-22T12:48:00+09:00',
        'race_id':'TEST-R02','race_no':2,'race_date':'2026-10-22',
        'arms':{arm:{'prediction':pred,'methods':copy.deepcopy(methods)} for arm in p.ARMS}})
    p.save_json(folder/'calculation.json',artifact);p.immutable(folder/'readback.txt',b'EXACT_BODY_STAKES_100\n')
    archive=folder/'archive.zip'
    manifest={f.name:{'bytes':f.stat().st_size,'sha256':p.digest(f)} for f in folder.iterdir() if f.is_file()}
    with ZipFile(archive,'w',compression=ZIP_DEFLATED) as z:
        for name in manifest:z.write(folder/name,name)
        z.writestr('BYTE_MANIFEST.json',json.dumps(manifest))
    completed=p.seal({'status':'PRIVATE_SAVE_REQUIRED','race_id':'TEST-R02','race_date':'2026-10-22','race_no':2,
        'folder':str(folder),'archive':str(archive),'archive_sha256':p.digest(archive),
        'artifact_sha256':artifact['sha256'],'answer_sha256':p.digest(folder/'readback.txt'),
        'classification':classification,'chat_render_verified':False,'user_received':False})
    p.save_json(folder/'complete.json',completed)
    receipt=root/'receipt.json';p.save_json(receipt,{'storage_id':'SYNTHETIC_TEST_ONLY','provider_created_at':'2026-10-22T04:30:00+00:00','readback_sha256':p.digest(archive)})
    return root,folder,archive,receipt,completed


def test_local_complete_is_not_a_published_pointer(tmp_path,monkeypatch):
    root,folder,archive,receipt,complete=fixture(tmp_path,monkeypatch)
    assert p.read_delivery('config',{'race_date':'2026-10-22','race_no':2}) is None
    assert not (root/'store/publications').exists()


def test_actual_readback_required_and_no_receipt_reuse(tmp_path,monkeypatch):
    root,folder,archive,receipt,complete=fixture(tmp_path,monkeypatch)
    wrong=root/'wrong.zip';wrong.write_bytes(archive.read_bytes()+b'changed')
    with pytest.raises(ValueError,match='READBACK_BYTE'):p.publish('config',folder/'complete.json',wrong,receipt)
    r=p.read(receipt);r['readback_sha256']='old-checkpoint';receipt.write_text(json.dumps(r))
    with pytest.raises(ValueError,match='STORAGE_RECEIPT'):p.publish('config',folder/'complete.json',archive,receipt)
    assert not (root/'store/publications').exists()


def test_readback_reuses_exact_body_portfolios_and_no_engine(tmp_path,monkeypatch):
    root,folder,archive,receipt,complete=fixture(tmp_path,monkeypatch)
    p.publish('config',folder/'complete.json',archive,receipt)
    monkeypatch.setattr(p,'simulate',lambda *a,**k:pytest.fail('Reader must never execute KRS'))
    result=p.read_delivery('config',{'race_date':'2026-10-22','race_no':2})
    assert result['body']=='EXACT_BODY_STAKES_100\n'
    assert result['prediction_reexecution'] is False
    assert result['forward_oos_credit']==0
    assert result['delivery']['chat_render_verified'] is False
    assert p.read_delivery('config',{'race_date':'2026-10-22','race_no':1}) is None
    assert result['checkpoint_scope']=='INITIAL_SNAPSHOT_NOT_CURRENT_LIVE_LEDGER'


def test_partial_engine_attempt_is_preserved_without_a_duplicate_run(tmp_path,monkeypatch):
    folder=tmp_path/'partial';folder.mkdir()
    (folder/'engine.log').write_text('interrupted attempt')
    monkeypatch.setattr(p.subprocess,'run',lambda *a,**k:pytest.fail('Interrupted execution must not run again'))
    with pytest.raises(ValueError,match='INTERRUPTED_ENGINE_ATTEMPT_PRESERVED'):
        p.simulate(folder,{}, {'synthetic':True},'R02',2,'2026-10-22')
    assert (folder/'engine.log').read_text()=='interrupted attempt'


@pytest.mark.parametrize('seed',[2,-1,True])
def test_transport_cannot_change_the_existing_same_seed_contract(tmp_path,monkeypatch,seed):
    config=tmp_path/'connection.json';config.write_text('{}');config.chmod(0o600)
    monkeypatch.setattr(p,'private_directory',lambda x:x)
    monkeypatch.setattr(p,'read',lambda path:p.seal({}) if str(path)=='registration' else
        {'registration':'registration','seed':seed,'runs':5000})
    with pytest.raises(ValueError,match='EXISTING_SIMULATION_CONTRACT'):
        p.configuration(config)


def test_later_diagnostic_does_not_replace_an_eligible_forward_pointer(tmp_path,monkeypatch):
    root,folder,archive,receipt,complete=fixture(tmp_path,monkeypatch)
    diagnostic=p.publish('config',folder/'complete.json',archive,receipt)
    forward_folder=folder.parent/'earlier-forward';forward_folder.mkdir(mode=0o700)
    a=p.read(folder/'calculation.json');a['classification']='REGISTERED_FORWARD_PAPER_PENDING_PRIVATE_SAVE'
    a=p.seal(a);p.save_json(forward_folder/'calculation.json',a)
    p.immutable(forward_folder/'readback.txt',b'ORIGINAL_ELIGIBLE_FORWARD_BODY\n')
    earlier=p.seal({**diagnostic,'folder':str(forward_folder),'artifact_sha256':a['sha256'],
        'answer_sha256':p.digest(forward_folder/'readback.txt'),'classification':a['classification'],
        'published_at':'2026-10-22T03:00:00+00:00'})
    p.save_json(root/'store/publications/2026-10-22/R02'/(a['sha256']+'.json'),earlier)
    result=p.read_delivery('config',{'race_date':'2026-10-22','race_no':2})
    assert result['artifact_sha256']==a['sha256']
    assert result['body']=='ORIGINAL_ELIGIBLE_FORWARD_BODY\n'


@pytest.mark.parametrize('damage',['body','race','tree'])
def test_mixed_race_missing_ticket_or_changed_body_never_passes(tmp_path,monkeypatch,damage):
    root,folder,archive,receipt,complete=fixture(tmp_path,monkeypatch)
    pub=p.publish('config',folder/'complete.json',archive,receipt)
    pubpath=root/'store/publications/2026-10-22/R02'/(complete['artifact_sha256']+'.json')
    if damage=='body':(folder/'readback.txt').write_text('missing ticket')
    elif damage=='race':
        pub['race_no']=1;pub=p.seal({k:v for k,v in pub.items() if k!='sha256'});pubpath.write_text(json.dumps(pub))
    else:
        a=p.read(folder/'calculation.json');a['arms']['BASELINE']['methods']['P0S1']['tickets']=[]
        a=p.seal({k:v for k,v in a.items() if k!='sha256'});(folder/'calculation.json').write_text(json.dumps(a))
        pub['artifact_sha256']=a['sha256'];pub=p.seal({k:v for k,v in pub.items() if k!='sha256'});pubpath.write_text(json.dumps(pub))
    with pytest.raises(ValueError):p.read_delivery('config',{'race_date':'2026-10-22','race_no':2})


def test_late_external_save_cannot_be_forward_delivery(tmp_path,monkeypatch):
    root,folder,archive,receipt,complete=fixture(tmp_path,monkeypatch,'REGISTERED_FORWARD_PAPER_PENDING_PRIVATE_SAVE')
    monkeypatch.setattr(p,'now',lambda:datetime(2026,10,22,4,30,tzinfo=timezone.utc))
    with pytest.raises(ValueError,match='AFTER_CUTOFF'):p.publish('config',folder/'complete.json',archive,receipt)
    assert not (root/'store/publications').exists()


def test_normal_entry_prefers_complete_research_over_reference(tmp_path,monkeypatch):
    import tempfile
    root=Path(tempfile.mkdtemp(prefix='km-entry-read-',dir='/var/tmp'));root.chmod(0o700)
    monkeypatch.setenv('KM_URW_PAPER_CONNECTION','synthetic-config')
    monkeypatch.setattr(entry,'_chat_final',lambda i:(None,[]))
    monkeypatch.setattr(entry,'chat_formal_status',lambda i:{'status':'BLOCKED','first_failed_stage':'OWNER','code':'FORMAL_HOLD'})
    monkeypatch.setattr(entry,'_chat_reference',lambda *a,**k:pytest.fail('Completed registered-model readback must precede reference'))
    monkeypatch.setattr(p,'read_delivery',lambda *a,**k:{'status':'VERIFIED_PRIVATE_RESEARCH_READBACK','body':'ALL_ACTUAL_TICKETS',
        'race_id':'TEST-R02','execution_id':'TEST-R02','prediction_reexecution':False,'answer_required_parts':[],
        'private_storage_required':True,'public_redistribution_authorized':False})
    report=entry.run_chat({'family_id':'LOCAL','venue_id':'URW','race_date':'2026-10-22','race_no':2},output=root,run_id='test')
    assert report['status']=='FORMAL_HOLD_RESEARCH_READBACK_VERIFIED'
    assert 'ALL_ACTUAL_TICKETS' in report['message'] and 'reference' not in report
    assert report['formal_final_proven'] is False
    assert report['delivery']['chat_render_verified'] is False


def test_research_hold_is_not_no_bet_or_silent_reference_success(tmp_path,monkeypatch):
    import tempfile
    root=Path(tempfile.mkdtemp(prefix='km-entry-hold-',dir='/var/tmp'));root.chmod(0o700)
    monkeypatch.setenv('KM_URW_PAPER_CONNECTION','synthetic-config')
    monkeypatch.setattr(entry,'_chat_final',lambda i:(None,[]))
    monkeypatch.setattr(entry,'chat_formal_status',lambda i:{'status':'BLOCKED','first_failed_stage':'OWNER','code':'FORMAL_HOLD'})
    monkeypatch.setattr(p,'read_delivery',lambda *a,**k:None)
    def stopped(*a,**k):raise ValueError('FULL_DAY_PLAN_NOT_REGISTERED')
    monkeypatch.setattr(p,'prepare',stopped)
    monkeypatch.setattr(entry,'_chat_reference',lambda *a,**k:({'execution_id':'REF-R02','answer_required_parts':[]},'REFERENCE_ONLY'))
    report=entry.run_chat({'family_id':'LOCAL','venue_id':'URW','race_date':'2026-10-22','race_no':2},output=root,run_id='test')
    assert report['research_execution']['no_bet'] is False
    assert report['completion'] is False
    assert '研究実行・保存・配送の成功ではありません' in report['message']


@pytest.mark.parametrize('single',[False,True])
def test_single_race_is_separate_from_registered_admission(tmp_path,monkeypatch,single):
    import tempfile
    root=Path(tempfile.mkdtemp(prefix='km-independent-entry-',dir='/var/tmp'));root.chmod(0o700)
    c={'store':str(root),'source_root':'unused','seed':1,'runs':5000}
    if single:c['execution_mode']=p.SINGLE_MODE
    reg={'sha256':'pins-not-admission'}
    monkeypatch.setattr(p,'configuration',lambda path:(c,reg,{arm:{'sha256':arm} for arm in p.ARMS}))
    obs={'race':{'prediction_cutoff':'2026-10-22T15:23:00+09:00'},'source':{'raw_sha256':'raw'}}
    monkeypatch.setattr(p,'now',lambda:datetime(2026,10,22,6,10,tzinfo=timezone.utc))
    monkeypatch.setattr(p,'source_observation',lambda *a:obs)
    monkeypatch.setattr(p,'current_single_observation',lambda *a:obs)
    monkeypatch.setattr(p,'calculation_pins',lambda *a:{'synthetic':True})
    monkeypatch.setattr(p.registered,'_registered_context',lambda *a:pytest.fail('Must not fabricate a registered context'))
    def compute(*a):raise ValueError('ACTUAL_NUMERICAL_ENTRY_REACHED')
    monkeypatch.setattr(p,'numerical',compute)
    expected='ACTUAL_NUMERICAL_ENTRY_REACHED' if single else 'CURRENT_LIVE_LEDGER_LATESTNESS_NOT_VERIFIED'
    with pytest.raises(ValueError,match=expected):p.prepare('config',{'race_date':'2026-10-22','race_no':7})
    assert not list(root.rglob('checkpoint-after.json'))


def test_historical_reparse_keeps_original_bytes_and_all_raw_time_identity_guards(tmp_path,monkeypatch):
    day='2026-10-22';folder=tmp_path/'sources/R09';folder.mkdir(parents=True)
    program=tmp_path/'program';program.mkdir()
    raw=b'SYNTHETIC_CARD_TRANSPORT_TEST';program_raw=b'SYNTHETIC_PROGRAM_TRANSPORT_TEST'
    race={'race_date':day,'race_no':9,'venue_id':'URW','provider_race_id':'2026102218010109',
        'distance':1400,'program_runner_count':3,'scheduled_post_at':'2026-10-22T16:35:00+09:00',
        'prediction_cutoff':'2026-10-22T16:33:00+09:00'}
    receipt={'fetched_at':'2026-10-22T16:00:00+09:00','raw_sha256':hashlib.sha256(raw).hexdigest(),
        'http_status':200,'url':'https://www.nankankeiba.com/synthetic-not-real-source',
        'source_policy':{'usage_scope':'USER_PERSONAL_NONCOMMERCIAL_PRIVATE_ONLY_NOT_PUBLIC_REDISTRIBUTION'}}
    old=[{'runner_id':'1','starts':[]}];new=[{'runner_id':'1','starts':[{'date':'2026-09-01'}]}]
    evidence=p.seal({'race':race,'runners':old,'sources':[receipt],'parser_sha256':'original-parser'})
    p.save_json(folder/'reference_evidence.json',evidence);p.save_json(folder/'card.receipt.json',receipt)
    (folder/'card.raw.html').write_bytes(raw);(program/'program.raw.html').write_bytes(program_raw)
    p.save_json(program/'program.receipt.json',{'url':p.ORIGIN+'/program/'+race['provider_race_id'][:-2]+'.do',
        'fetched_at':receipt['fetched_at'],'http_status':200,'raw_sha256':hashlib.sha256(program_raw).hexdigest()})
    original=(folder/'reference_evidence.json').read_bytes()
    monkeypatch.setattr(p,'parse_card',lambda *a:copy.deepcopy(new));monkeypatch.setattr(p,'parse_program',lambda *a,**k:[race])
    monkeypatch.setattr(p,'verify_history_asof',lambda *a:None)
    monkeypatch.setattr(p,'now',lambda:datetime(2026,10,22,8,tzinfo=timezone.utc))
    with pytest.raises(ValueError,match='PARSE_DIFFERS'):p.source_observation(tmp_path,day,9)
    result=p.source_observation(tmp_path,day,9,diagnostic_reparse=True)
    provenance=result['historical_reparse']
    assert provenance['original_facts_sha256']==p.sha(old) and provenance['current_facts_sha256']==p.sha(new)
    assert provenance['original_parser_sha256']=='original-parser' and provenance['original_files_modified'] is False
    assert result['facts']==new and (folder/'reference_evidence.json').read_bytes()==original
    monkeypatch.setattr(p,'now',lambda:datetime(2026,10,22,7,10,tzinfo=timezone.utc))
    with pytest.raises(ValueError,match='REQUIRES_POSTCUTOFF'):p.source_observation(tmp_path,day,9,diagnostic_reparse=True)
    monkeypatch.setattr(p,'now',lambda:datetime(2026,10,22,8,tzinfo=timezone.utc))
    (folder/'card.raw.html').write_bytes(raw+b'DAMAGED')
    with pytest.raises(ValueError,match='RAW_RECEIPT_OR_RACE_IDENTITY'):p.source_observation(tmp_path,day,9,diagnostic_reparse=True)


def test_single_publication_needs_readback_but_no_v2_checkpoint(tmp_path,monkeypatch):
    root,folder,archive,receipt,complete=fixture(tmp_path,monkeypatch,p.SINGLE_CLASS)
    config={'store':str(root/'store'),'execution_mode':p.SINGLE_MODE}
    monkeypatch.setattr(p,'configuration',lambda path:(config,{'sha256':'registration'},{}))
    monkeypatch.setattr(p,'now',lambda:datetime(2026,10,22,3,45,tzinfo=timezone.utc))
    r=p.read(receipt);r['provider_created_at']='2026-10-22T03:40:00+00:00';receipt.write_text(json.dumps(r))
    pub=p.publish('config',folder/'complete.json',archive,receipt)
    assert pub['checkpoint_file_sha256'] is None
    assert pub['checkpoint_scope']=='NOT_APPLICABLE_NO_V2_LEDGER_MUTATION'
    assert pub['forward_oos_credit']==0 and not pub['formal_final_proven']


def test_single_late_save_is_not_prestart(tmp_path,monkeypatch):
    root,folder,archive,receipt,complete=fixture(tmp_path,monkeypatch,p.SINGLE_CLASS)
    monkeypatch.setattr(p,'now',lambda:datetime(2026,10,22,6,0,tzinfo=timezone.utc))
    with pytest.raises(ValueError,match='AFTER_CUTOFF'):p.publish('config',folder/'complete.json',archive,receipt)
    assert not (root/'store/publications').exists()


@pytest.mark.parametrize('current_id,accepted',[('031253',True),('031248',False),('999999',False)])
def test_jockey_change_joins_provider_identity_and_requires_new_rider(current_id,accepted):
    card=('<table class="tb-shousai"><tr><td class="umaban">7</td>'
        '<td><a href="/uma_info/2019109091.do">horse</a></td><td class="cs-g1">'
        f'<a href="/kis_info/{current_id}.do">SHORT</a></td></tr></table>').encode()
    changes=('<div class="nk23_c-block01__list2__item"><a href="/uma_info/2019109091.do">horse</a>'
        '<a href="/kis_info/031248.do">OLD</a> → <a href="/kis_info/031253.do">FULL</a></div>').encode()
    fact={'runner_id':'7','provider_horse_id':'2019109091','current_jockey':'SHORT'}
    if accepted:
        result=p.current_jockey_identity(card,changes,fact)
        assert result['provider_jockey_link']=='/kis_info/031253.do'
        assert fact['current_jockey']=='SHORT'  # No model-input rewriting.
    else:
        with pytest.raises(ValueError,match='JOCKEY_CHANGE_CARD_RECONCILIATION_REQUIRED'):
            p.current_jockey_identity(card,changes,fact)


@pytest.mark.parametrize('day',['2026-10-22','2026-10-23'])
def test_current_source_store_is_bound_to_date_and_race(tmp_path,monkeypatch,day):
    import tempfile
    root=Path(tempfile.mkdtemp(prefix='km-current-source-date-',dir='/var/tmp'));root.chmod(0o700)
    seen=[]
    def capture(observed_day,number,folder,**kwargs):
        seen.append((observed_day,number,folder));raise ValueError('OBSERVATION_STARTED')
    monkeypatch.setattr(p,'capture_race',capture)
    with pytest.raises(ValueError,match='OBSERVATION_STARTED'):
        p.current_single_observation({'current_source_root':str(root)},day,8)
    assert seen==[(day,8,root/day/'R08')]


def render_artifact():
    """Small invented calculation, not a race-day fixture or Engine receipt."""
    ids=['1','2','3','4']
    prediction={'ranking':ids,'rankings_by_role':{role:ids for role in ('W','P2','P3')},
        'role_columns':{rid:['W','P2','P3'] for rid in ids},
        'missingness':{rid:['history_margin'] if rid=='4' else [] for rid in ids}}
    tickets=[{'bet_type':'EXACTA','selection':[1,2],'stake':100}]
    methods={method:{'tickets':copy.deepcopy(tickets),'tree':p.tree(prediction,tickets)} for method in p.METHODS}
    view={'prediction':prediction,'methods':methods,
        'engine_receipt':{'run_count':5000,'master_seed':1,'completed_at':'SYNTHETIC_NOT_ACTUAL_EXECUTION'},
        'krs_utility':{'snapshot':{},'utility_class':'SYNTHETIC',
            'summary':[{'horse_no':rid,'SSR-W':0.25,'SSR-P2':0.25,'SSR-P3':0.25} for rid in ids]}}
    return p.seal({'race_no':2,'race_date':'2026-10-22','race_id':'SYNTHETIC-R02-R1','provider_race_id':'SYNTHETIC',
        'classification':'POSTCUTOFF_DIAGNOSTIC_NOT_FORWARD','created_at':'2026-10-22T04:00:00+00:00',
        'prediction_cutoff':'2026-10-22T03:48:00+00:00',
        'source':{'fetched_at':'2026-10-22T03:00:00+00:00','raw_sha256':'synthetic-source'},
        'registration_sha256':'synthetic-pins','numerical':{'runners':[{'runner_id':rid,'name':'HORSE_'+rid} for rid in ids],
            'candidate_full_numerical_summary':{'required_count':116,'calculated_count':112,'ruled_neutral_count':0,'unresolved_count':4,
                'numeric_transport_complete':True,'full_numerical_complete':False,'mean_real_component_coverage':0.75,
                'candidate_neutral_missing_component_count':12}},
        'arms':{arm:copy.deepcopy(view) for arm in p.ARMS}})


def test_render_contains_all_horses_all_six_trees_stakes_and_unknown_reasons():
    artifact=render_artifact();before=copy.deepcopy(artifact);body=p.render(artifact)
    for rid in ('1','2','3','4'):assert f'|{rid} HORSE_{rid}|' in body
    for arm in p.ARMS:
        for method in p.METHODS:assert arm+' / '+method+'｜全選択票・各Stake' in body
    assert body.count('└─ EXACTA 1→2：100円')==6
    assert body.count('合計1点 / 試算100円 / 未使用1900円 / 計算済・研究票')==6
    assert 'B: history_margin（観測不足） / C: history_margin（観測不足）' in body
    assert '未較正' in body and '原本Artifact SHA '+artifact['sha256'] in body
    assert 'numeric_transport_complete=True / full_numerical_complete=False' in body
    assert '平均coverage=0.75 / 中立化された欠測成分数=12' in body
    assert artifact==before and p.render(artifact)==body


@pytest.mark.parametrize('missing',['method','tickets','reason','horse'])
def test_incomplete_calculation_never_renders_as_complete_no_bet(missing):
    artifact=render_artifact();view=artifact['arms']['BASELINE'];m=view['methods']['P0S1']
    if missing=='method':del view['methods']['P0S1']
    elif missing=='tickets':del m['tickets']
    elif missing=='reason':m.update(tickets=[],tree=p.tree(view['prediction'],[]))
    else:view['prediction']['ranking'].remove('4')
    with pytest.raises(ValueError,match='NOT_CALCULATED|WITHOUT_CALCULATED_NO_BET_REASON|ALL_HORSE'):
        p.render(artifact)


def test_calculated_zero_ticket_result_has_reason_and_independent_unused_budget():
    artifact=render_artifact();view=artifact['arms']['BASELINE'];m=view['methods']['P0S1']
    m.update(tickets=[],tree=p.tree(view['prediction'],[]),selection={'selected_tickets':[],
        'race_budget_yen':2000,'used_budget_yen':0,'unused_budget_yen':2000,'no_bet':True,
        'no_bet_reason':'SYNTHETIC_NO_QUALIFIED_TICKET','tier_spend_yen':{'CORE':0,'PROTECTION':0}})
    body=p.render(artifact)
    assert '合計0点 / 試算0円 / 未使用2000円 / NO-BET：SYNTHETIC_NO_QUALIFIED_TICKET' in body
    assert 'CANDIDATE/P0S1|1|100円|1900円|計算済・研究票' in body
    m['selection']['used_budget_yen']=100
    with pytest.raises(ValueError,match='ACCOUNTING_MISMATCH'):p.render(artifact)


def add_saved_original(root,folder,base_pub,*,source_time,created_at,published_at,source_sha,revision):
    target=folder.parent/('revision-'+str(revision));target.mkdir(mode=0o700)
    artifact=p.read(folder/'calculation.json')
    artifact.update(source={'fetched_at':source_time,'raw_sha256':source_sha},created_at=created_at,
        race_id='TEST-R02-R'+str(revision))
    artifact=p.seal(artifact);p.save_json(target/'calculation.json',artifact)
    p.immutable(target/'readback.txt',('ORIGINAL_'+str(revision)+'\n').encode())
    pub=p.seal({**base_pub,'folder':str(target),'race_id':artifact['race_id'],
        'artifact_sha256':artifact['sha256'],'source_sha256':source_sha,'revision':str(revision),
        'answer_sha256':p.digest(target/'readback.txt'),'published_at':published_at})
    path=root/'store/publications/2026-10-22/R02'/(artifact['sha256']+'.json');p.save_json(path,pub)
    return artifact,pub,path


def test_catalog_selects_by_original_source_not_upload_time_and_can_request_exact_revision(tmp_path,monkeypatch):
    root,folder,archive,receipt,complete=fixture(tmp_path,monkeypatch)
    base=p.publish('config',folder/'complete.json',archive,receipt)
    newer,newpub,_=add_saved_original(root,folder,base,source_time='2026-10-22T03:30:00+00:00',
        created_at='2026-10-22T03:40:00+00:00',published_at='2026-10-22T05:00:00+00:00',source_sha='new-source',revision=2)
    older,oldpub,_=add_saved_original(root,folder,base,source_time='2026-10-22T03:00:00+00:00',
        created_at='2026-10-22T03:10:00+00:00',published_at='2026-10-22T06:00:00+00:00',source_sha='old-source',revision=1)
    intent={'race_date':'2026-10-22','race_no':2}
    result=p.read_delivery('config',intent);assert result['body']=='ORIGINAL_2\n'
    assert p.read_delivery('config',{**intent,'classification':older['classification'],
        'artifact_sha256':older['sha256'],'source_sha256':'old-source','revision':'1'})['body']=='ORIGINAL_1\n'
    assert p.read_delivery('config',{**intent,'artifact_sha256':older['sha256'],'source_sha256':'new-source'}) is None
    assert p.read_delivery('config',{**intent,'classification':'UNRELATED_CLASS'}) is None
    assert (Path(oldpub['folder'])/'readback.txt').read_text()=='ORIGINAL_1\n'


@pytest.mark.parametrize('field,value',[('race_date','2026-10-23'),('race_no',3),('race_id','OTHER-R02'),('source_sha256','wrong')])
def test_catalog_binds_original_identity_and_source_before_display(tmp_path,monkeypatch,field,value):
    root,folder,archive,receipt,complete=fixture(tmp_path,monkeypatch)
    base=p.publish('config',folder/'complete.json',archive,receipt)
    artifact,pub,path=add_saved_original(root,folder,base,source_time='2026-10-22T03:00:00+00:00',
        created_at='2026-10-22T03:10:00+00:00',published_at='2026-10-22T05:00:00+00:00',source_sha='source',revision=1)
    pub[field]=value;path.write_text(json.dumps(p.seal(pub)))  # Deliberate corruption, not an allowed writer operation.
    with pytest.raises(ValueError,match='MIX|IDENTITY_MISMATCH'):
        p.read_delivery('config',{'race_date':'2026-10-22','race_no':2})


@pytest.mark.parametrize('found',[False,True])
def test_work_transport_selects_requested_completed_artifact_without_recompute(tmp_path,found):
    import shutil
    import subprocess
    node=shutil.which('node')
    if not node:pytest.skip('Node required for Work caller routing regression')
    source=Path('scripts/urw_work_transport.js').read_text()
    options={'repo':'synthetic','config':'private-config','query':'2026-10-22 浦和2R',
        'readback':{'artifact_sha256':'exact-original'}}
    # For an existing completed target, another published artifact must not win.
    if found:options['completed']={'artifact_sha256':'exact-original','classification':p.SINGLE_CLASS}
    script='const transport='+source+';\n'+'''
const commands=[];
const tools={exec_command:async x=>{commands.push(x.cmd);return {exit_code:0,output:JSON.stringify(FOUND?{artifact_sha256:'exact-original'}:null)}}};
(async()=>{try{const result=await transport(tools,OPTIONS);console.log(JSON.stringify({commands,result}));}
catch(e){console.log(JSON.stringify({commands,error:e.message}));}})();
'''.replace('FOUND',json.dumps(found)).replace('OPTIONS',json.dumps(options))
    result=json.loads(subprocess.run([node,'-e',script],check=True,text=True,capture_output=True).stdout)
    assert len(result['commands'])==1 and "--artifact-sha256 'exact-original'" in result['commands'][0]
    if found:assert result['result']['storage_writes']==0 and not result['result']['calculation_executed']
    else:assert result['error']=='WORK_REQUESTED_ORIGINAL_NOT_FOUND_NO_RECOMPUTATION'


def work_mock(responses,options):
    import shutil
    import subprocess
    node=shutil.which('node')
    if not node:pytest.skip('Node required for Work caller routing regression')
    source=Path('scripts/urw_work_transport.js').read_text()
    script='const transport='+source+';\n'+'''
const commands=[],responses=RESPONSES;
const tools={exec_command:async x=>{commands.push(x.cmd);if(!responses.length)throw new Error('UNEXPECTED_COMMAND');
return {exit_code:0,output:JSON.stringify(responses.shift())}}};
(async()=>{const result=await transport(tools,OPTIONS);console.log(JSON.stringify({commands,result}));})();
'''.replace('RESPONSES',json.dumps(responses)).replace('OPTIONS',json.dumps(options))
    return json.loads(subprocess.run([node,'-e',script],check=True,text=True,capture_output=True).stdout)


@pytest.mark.parametrize('status',['FORMAL_VERIFIED','FORMAL_HOLD_SINGLE_RACE_READBACK_VERIFIED'])
def test_work_generic_single_uses_ordinary_classification_before_paper_catalog(status):
    options={'repo':'synthetic','config':'private-config','query':'2026-10-22 浦和2R',
        'executionMode':p.SINGLE_MODE,'privateDirectory':'private','python':"/verified path/py'thon"}
    report={'status':status,'message':'EXACT_EXISTING_ORIGINAL','prediction_reexecution':False}
    result=work_mock([{},report],options)
    assert len(result['commands'])==2 and 'runtime.local_race_entry' in result['commands'][0]
    assert 'runtime.urw_registered_paper_entry' not in result['commands'][0]
    assert "'/verified path/py'\\''thon'" in result['commands'][0]
    assert result['result']['body']=='EXACT_EXISTING_ORIGINAL'
    assert result['result']['storage_writes']==0 and result['result']['calculation_executed'] is False


@pytest.mark.parametrize('explicit,generation',[(False,False),(False,None),(True,False)])
def test_work_keeps_verified_local_full_body_when_storage_tools_absent(explicit,generation):
    complete={'status':'PRIVATE_SAVE_REQUIRED','folder':'private-complete','artifact_sha256':'exact-original'}
    options={'repo':'synthetic','config':'private-config','query':'2026-10-22 浦和2R',
        'executionMode':p.SINGLE_MODE,'privateDirectory':'private','python':'/verified/python'}
    local={'body':'ALL_HORSES_AND_SIX_TREES_STAKES_FROM_NATIVE_READER','artifact_sha256':'exact-original'}
    if explicit:
        options['completed']=complete;responses=[None,local]
    else:
        report={'status':'SINGLE_RACE_CALCULATED_PRIVATE_SAVE_PENDING','research_execution':complete,
            'prediction_reexecution':generation,'research_execution_invocation':{'prepare_invoked':True}}
        responses=[{},report,local]
    result=work_mock(responses,options);value=result['result']
    assert value['status']=='CALCULATED_PRIVATE_SAVE_PENDING' and value['body']==local['body']
    assert '_prepared_paper_answer' in result['commands'][-1] and 'resolve_chat_intent' in result['commands'][-1]
    assert not any(' prepare --query' in command for command in result['commands'])
    assert value['calculation_executed'] is generation and value['storage_writes']==0
    assert value['external_storage_roundtrip_verified'] is False and value['independent_external_anchor_verified'] is False
    assert value['formal_quality_credit']==0 and value['chat_render_verified'] is False


@pytest.mark.parametrize('single',[False,True])
def test_repaired_single_caller_records_own_code_without_rebinding_v2_registration(tmp_path,monkeypatch,single):
    models={arm:p.seal({'synthetic_arm':arm}) for arm in p.ARMS}
    reg=p.seal({'canonical_ledger_path':str(tmp_path/'old-ledger'),'code_sha256':{'old':'immutable'},
        'policy':copy.deepcopy(p.POLICY),'policy_sha256':p.sha(p.POLICY),
        'models':{arm:models[arm]['sha256'] for arm in p.ARMS}})
    config={'seed':1,'runs':5000,'registration':'registration','engine':'engine','parameters':'parameters',
        'model_bundle':'model-bundle','store':str(tmp_path/'single-store'),
        'registered_store':str(tmp_path/'old-store'),'current_source_root':str(tmp_path/'current-source')}
    if single:config['execution_mode']=p.SINGLE_MODE
    path=tmp_path/'connection.json';path.write_text('{}');path.chmod(0o600)
    monkeypatch.setattr(p,'private_directory',lambda path:path)
    monkeypatch.setattr(p,'read',lambda path:reg if str(path)=='registration' else
        {'models':models} if str(path)=='model-bundle' else config)
    monkeypatch.setattr(p,'digest',lambda path:p.ENGINE if str(path)=='engine' else p.PARAMETERS)
    monkeypatch.setattr(p.registered,'code_pins',lambda:{'current':'repaired'})
    before=copy.deepcopy(reg)
    if single:assert p.configuration(path)[1]==before
    else:
        with pytest.raises(ValueError,match='REGISTERED_CODE_OR_POLICY_CHANGED'):p.configuration(path)
    assert reg==before


@pytest.mark.parametrize('past,requested_day,saved_exists',[
    (False,'2026-10-22',True),(True,'2026-10-22',True),(True,'2026-10-23',True),(True,'2026-10-22',False)])
def test_saved_source_route_is_explicit_postcutoff_only_and_live_keeps_current_observations(tmp_path,monkeypatch,past,requested_day,saved_exists):
    import tempfile
    root=Path(tempfile.mkdtemp(prefix='km-saved-diagnostic-',dir='/var/tmp'));root.chmod(0o700)
    c={'store':str(root/'outputs'),'source_root':str(root/'saved-source'),'execution_mode':p.SINGLE_MODE,
        'allow_postcutoff_diagnostic':True,'seed':1,'runs':5000}
    cutoff='2026-10-22T15:23:00+09:00';obs={'race':{'prediction_cutoff':cutoff},'source':{'raw_sha256':'source'}}
    historical_route=past and requested_day=='2026-10-22' and saved_exists
    if not historical_route:obs['race']['prediction_cutoff']='2026-10-23T15:23:00+09:00'
    routes=[]
    if saved_exists:
        saved=Path(c['source_root'])/'sources/R09';saved.mkdir(parents=True)
        p.save_json(saved/'reference_evidence.json',{'race':{'race_date':'2026-10-22','race_no':9,'prediction_cutoff':cutoff}})
    monkeypatch.setattr(p,'configuration',lambda path:(c,{'sha256':'immutable-pins'},{}))
    monkeypatch.setattr(p,'calculation_pins',lambda *a:{'synthetic':True})
    monkeypatch.setattr(p,'now',lambda:datetime(2026,10,22,7 if past else 6,tzinfo=timezone.utc))
    def historical(*args,**kwargs):routes.append(('saved',kwargs));return obs
    def current(*args):routes.append(('current',{}));return obs
    monkeypatch.setattr(p,'source_observation',historical);monkeypatch.setattr(p,'current_single_observation',current)
    def stop(*a):raise ValueError('SYNTHETIC_NUMERICAL_BOUNDARY_NO_ENGINE')
    monkeypatch.setattr(p,'numerical',stop)
    with pytest.raises(ValueError,match='SYNTHETIC_NUMERICAL_BOUNDARY'):
        p.prepare('config',{'race_date':requested_day,'race_no':9})
    assert routes==[('saved',{'diagnostic_reparse':True})] if historical_route else routes==[('current',{})]
    assert not list(root.rglob('checkpoint-after.json'))


def test_interrupted_prepare_preserves_manifest_and_original_reparse_timestamp(tmp_path,monkeypatch):
    import tempfile
    root=Path(tempfile.mkdtemp(prefix='km-resume-source-',dir='/var/tmp'));root.chmod(0o700)
    c={'store':str(root/'out'),'source_root':str(root/'source'),'execution_mode':p.SINGLE_MODE,
        'allow_postcutoff_diagnostic':True,'seed':1,'runs':5000}
    race={'race_date':'2026-10-22','race_no':9,'prediction_cutoff':'2026-10-22T16:33:00+09:00'}
    folder=Path(c['source_root'])/'sources/R09';folder.mkdir(parents=True)
    p.save_json(folder/'reference_evidence.json',{'race':race})
    clock=[datetime(2026,10,22,8,tzinfo=timezone.utc)]
    monkeypatch.setattr(p,'now',lambda:clock[0]);monkeypatch.setattr(p,'configuration',lambda path:(c,{'sha256':'pins'},{}))
    monkeypatch.setattr(p,'calculation_pins',lambda *a:{'synthetic':True})
    def observed(*a,**k):return {'race':race,'source':{'raw_sha256':'raw'},'facts':[],
        'historical_reparse':{'current_facts_sha256':'same-facts','reparsed_at':p.now().isoformat()}}
    monkeypatch.setattr(p,'source_observation',observed)
    def stop(*a):raise ValueError('SYNTHETIC_INTERRUPTION_BEFORE_NUMERICAL')
    monkeypatch.setattr(p,'numerical',stop)
    for attempt in range(2):
        with pytest.raises(ValueError,match='SYNTHETIC_INTERRUPTION'):p.prepare('config',{'race_date':'2026-10-22','race_no':9})
        paths=list((root/'out').rglob('calculation-manifest.json'))+list((root/'out').rglob('source-observation.json'))
        current={str(path):path.read_bytes() for path in paths}
        if not attempt:original=current
        else:assert current==original
        clock[0]=datetime(2026,10,22,8,1,tzinfo=timezone.utc)


def test_program_observations_reach_native_numerical_and_krs_without_inventing_unknown(tmp_path,monkeypatch):
    import re
    import test_urw_nankan_reference_source as pages
    raw=pages.detailed_card().decode();first=re.search(r'<tr>.*?</tr>',raw).group()
    third=first.replace('class="umaban">1','class="umaban">3').replace('/uma_info/1.do','/uma_info/3.do').replace('テスト1','テスト3')
    card=raw.replace('(2頭)','(3頭)').replace('</tbody>',third+'</tbody>').encode()
    monkeypatch.setattr(p,'now',lambda:datetime(2026,10,22,8,tzinfo=timezone.utc))
    for known in (False,True):
        program=pages.program().replace('2頭'.encode(),'3頭'.encode())+pages.condition_header(
            weather='曇' if known else '－',going='ダ良' if known else '－').encode()
        url=p.ORIGIN+'/program/'+pages.DAY_ID+'.do';race=p.parse_program(program,url,pages.DAY)[0]
        receipt=pages.current_receipt(program,url,fetched='2026-10-22T12:00:00+09:00')
        conditions=p.program_condition_observation(program,receipt,race)
        facts=p.parse_card(card,race,p.ORIGIN+'/uma_shosai/'+race['provider_race_id']+'.do')
        source=pages.current_receipt(card,p.ORIGIN+'/uma_shosai/'+race['provider_race_id']+'.do',fetched='2026-10-22T12:01:00+09:00')
        n=p.numerical({'race':race,'facts':facts,'source':source,'program_conditions':conditions},'SYNTHETIC-CONDITION-TRANSPORT')
        data=p.krs_input(n,{'role_columns':{fact['runner_id']:['W','P2','P3'] for fact in facts}},seed=1,runs=5000)
        assert conditions['observed_at']==receipt['fetched_at']!=source['fetched_at']
        assert conditions['source']['raw_sha256']==hashlib.sha256(program).hexdigest()
        assert n['candidate_current_state']['official_weather']==('曇' if known else '')
        assert n['candidate_current_state']['official_going']==('良' if known else '')
        assert data['race'].get('weather')==('曇' if known else None)
        assert data['race'].get('going')==('良' if known else None)
    damaged={**receipt,'fetched_at':race['prediction_cutoff']}
    with pytest.raises(ValueError,match='PROGRAM_CONDITION_RAW_RECEIPT_OR_TIME'):
        p.program_condition_observation(program,damaged,race)


def test_current_cached_raw_reparses_facts_and_preserves_old_derived_sidecars(tmp_path,monkeypatch):
    import gzip
    import tempfile
    import test_urw_nankan_reference_source as pages
    root=Path(tempfile.mkdtemp(prefix='km-current-reparse-',dir='/var/tmp'));root.chmod(0o700)
    folder=root/pages.DAY/'R01';folder.mkdir(parents=True)
    program=pages.program()+pages.condition_header(weather='曇').encode();card=pages.detailed_card()
    race=p.parse_program(program,p.ORIGIN+'/program/'+pages.DAY_ID+'.do',pages.DAY)[0]
    receipts=[{},pages.current_receipt(program,p.ORIGIN+'/program/'+pages.DAY_ID+'.do',fetched=pages.DAY+'T12:08:00+09:00'),{},
        pages.current_receipt(card,p.ORIGIN+'/uma_shosai/'+race['provider_race_id']+'.do')]
    facts=p.parse_card(card,race,receipts[3]['url']);old=copy.deepcopy(facts)
    for fact in old:fact['starts']=[]
    evidence=p.seal({'race':race,'runners':old,'sources':receipts,'parser_sha256':'old-parser'})
    for name,raw in (('program',program),('card',card)):(folder/(name+'.html.gz')).write_bytes(gzip.compress(raw))
    for name,raw,url in (('odds',pages.current_odds_page(),p.ORIGIN+'/odds/'+race['provider_race_id']+'01.do'),
            ('changes',pages.no_changes_page(),p.ORIGIN+'/henko_info/00000000000000.do')):
        (folder/(name+'.raw.html')).write_bytes(raw);p.save_json(folder/(name+'.receipt.json'),pages.current_receipt(raw,url))
        (folder/(name+'.parsed.json')).write_text('OLD_DERIVED_BYTES_PRESERVED')
    monkeypatch.setattr(p,'capture_race',lambda *a,**k:(None,evidence,None,None))
    monkeypatch.setattr(p,'now',lambda:datetime(2026,10,22,3,15,tzinfo=timezone.utc))
    monkeypatch.setattr(p,'Client',lambda:None)
    first=p.current_single_observation({'current_source_root':str(root)},pages.DAY,1)
    second=p.current_single_observation({'current_source_root':str(root)},pages.DAY,1)
    assert first==second and all(len(fact['starts'])==1 for fact in first['facts'])
    assert all(not fact['starts'] for fact in evidence['runners'])
    assert first['current_parser_reparse']['original_facts_sha256']!=first['current_parser_reparse']['current_facts_sha256']
    for name in ('odds','changes'):
        assert (folder/(name+'.parsed.json')).read_text()=='OLD_DERIVED_BYTES_PRESERVED'
        assert len(list(folder.glob(name+'.parsed-*.json')))==1

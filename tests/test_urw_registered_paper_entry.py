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

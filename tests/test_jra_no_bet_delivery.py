"""Offline NO-BET projection/trust/transport contracts; never Live evidence."""
import base64
import copy
from datetime import datetime,timedelta
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from cryptography.exceptions import InvalidSignature

ROOT=Path(__file__).resolve().parents[1]
PROJECT=Path(os.environ.get('KM_TEST_REPOSITORY_ROOT',ROOT))
sys.path[:0]=[str(ROOT/'runtime'),str(PROJECT/'runtime'),str(PROJECT/'runtime/jra_source_runtime')]
import jra_delivery as delivery
import jra_no_bet_presentation as projection
from jra_execution_maturity_bridge import source_checkpoint_manifest
from test_jra_self_delivery import FakeGmail,prepared as prepared_signed


def oidc_result(command,stamp):
    workflow=command[command.index('--signer-workflow')+1]
    sha='1'*40 if workflow.endswith('km-jra-source-first-runner.yml') else '2'*40
    certificate={'issuer':'https://token.actions.githubusercontent.com',
        'subjectAlternativeName':'https://github.com/'+workflow+'@refs/heads/main',
        'sourceRepositoryDigest':sha,'sourceRepositoryRef':'refs/heads/main','runnerEnvironment':'github-hosted'}
    subject={'name':Path(command[3]).name,'digest':{'sha256':projection.file_sha(command[3])}}
    return [{'verificationResult':{'signature':{'certificate':certificate},
        'statement':{'_type':'https://in-toto.io/Statement/v1','subject':[subject]},
        'verifiedTimestamps':[{'timestamp':stamp.isoformat()}]}}]


@pytest.fixture(autouse=True)
def no_real_network(monkeypatch):
    def blocked(*args,**kwargs):pytest.fail('NO-BET offline test attempted real network')
    monkeypatch.setattr(delivery.urllib.request,'urlopen',blocked)
    monkeypatch.setattr(delivery.urllib.request.OpenerDirector,'open',blocked)


@pytest.fixture
def case(tmp_path,monkeypatch):
    original=json.loads((ROOT/'runtime/jra_no_bet_terminals/KM-JRA-TKY-20261031-R05-LIVE-R1.json').read_text())
    terminal=copy.deepcopy(original)
    at=projection.instant(terminal['created_at'])+timedelta(minutes=1)
    frozen=projection.instant(terminal['source_freeze_at'])
    prepared=terminal['failure_report']['prepared_numerical_request']['runners']
    artifact={'race_id':terminal['race_id'],'prediction_cutoff':terminal['failure_report']['source_checkpoint_manifest']['prediction_cutoff'],
              'source_freeze_at':terminal['source_freeze_at'],'source_snapshot_sha256':terminal['source_snapshot_sha256'],
              'jra_official_runner_universe':{'universe_type':'ACTIVE','runners':[
                  {'runner_id':str(r['runner_id']),'horse_no':int(r['runner_id']),'name':r['name']} for r in prepared]}}
    receipt={'race_id':terminal['race_id'],'family':'JRA','phase':'SOURCE','status':'PASS','errors':[],
             'artifact_sha256':projection.digest(artifact),'timestamp':(frozen+timedelta(seconds=1)).isoformat(),
             'runtime_revision':terminal['failure_report']['source_checkpoint_manifest']['runtime_revision']}
    # A fresh ephemeral key signs only this synthetic offline SOURCE fixture.
    key=Ed25519PrivateKey.generate()
    envelope={'receipt':receipt,'artifact':artifact,'receipt_sha256':projection.digest(receipt),
              'receipt_public_key_b64':base64.b64encode(key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)).decode(),
              'signature':base64.b64encode(key.sign(delivery.canonical_bytes(receipt))).decode(),
              'signer_trust_class':projection.TRUST_POLICY['source_trust_class'],
              'github_repository':projection.TRUST_POLICY['repository'],'github_sha':'1'*40}
    checkpoint=source_checkpoint_manifest(envelope,terminal['source_execution_id'])
    terminal['signed_source_receipt_sha256']=envelope['receipt_sha256']
    terminal['failure_report']['source_checkpoint_manifest']=checkpoint
    terminal['failure_report']['sha256']=projection.digest({k:v for k,v in terminal['failure_report'].items() if k!='sha256'})
    terminal['report_sha256']=terminal['failure_report']['sha256']
    terminal['sha256']=projection.digest({k:v for k,v in terminal.items() if k!='sha256'})
    intent={'family_id':'JRA','race_id':terminal['race_id'],'execution_id':terminal['source_execution_id'],
            'prediction_cutoff':terminal['prediction_cutoff'],'scheduled_post_at':terminal['scheduled_post_at']}
    paths={}
    for name,value in [('terminal',terminal),('source',envelope),('intent',intent)]:
        path=tmp_path/(name+'.json');path.write_text(json.dumps(value,ensure_ascii=False));paths[name]=path
    commands=[]
    def gh(command,**kwargs):
        assert command[:3]==['gh','attestation','verify']
        assert '--source-ref' in command and '--source-digest' in command and '--deny-self-hosted-runners' in command
        commands.append(command)
        source=command[command.index('--signer-workflow')+1].endswith('km-jra-source-first-runner.yml')
        stamp=(frozen+timedelta(seconds=2) if source else projection.instant(terminal['created_at'])+timedelta(seconds=1))
        return SimpleNamespace(returncode=0,stdout=json.dumps(oidc_result(command,stamp)),stderr='')
    monkeypatch.setattr(projection.subprocess,'run',gh)
    args={'intent_path':paths['intent'],'source_envelope_path':paths['source'],'root':PROJECT,'producer_sha':'2'*40}
    directory=tmp_path/'presentation'
    auth={'enabled':True,'actor':'GMAIL_SELF','scope':projection.DELIVERY_SCOPE,
          'owner_approval_ref':'OFFLINE_ONLY_NO_REAL_APPROVAL',
          'actor_code_sha256':hashlib.sha256(Path(delivery.__file__).read_bytes()).hexdigest(),
          'no_bet_projection_code_sha256':hashlib.sha256(Path(projection.__file__).read_bytes()).hexdigest(),
          'no_bet_trust_policy_sha256':projection.digest(projection.TRUST_POLICY),
          'authority':terminal['failure_report']['current_authority_manifest'],
          'account_sub':'offline-owner-sub','account_email':'owner@example.invalid','readback_authorized':True}
    return {'original':original,'terminal':terminal,'paths':paths,'args':args,'directory':directory,
            'auth':auth,'transport':FakeGmail(at),'at':at,'commands':commands,'private_store':tmp_path/'private','fixture_key':key}


def compose(c):
    bundle=projection.build_no_bet_presentation(c['paths']['terminal'],**c['args'])
    return projection.save_no_bet_presentation(c['directory'],bundle)


def send(c,**changes):
    return delivery.send_no_bet_self_mail(c['paths']['terminal'],**c['args'],
        **{'presentation_dir':c['directory'],'private_store':c['private_store'],'authorization':c['auth'],
           'transport':c['transport'],'now':lambda:c['at'],**changes})


def test_no_bet_projection_is_complete_zero_exposure_and_originals_immutable(case):
    before={p:p.read_bytes() for p in case['paths'].values()}
    bundle=compose(case);detail=bundle['detail']
    assert detail['status']=='NO_BET' and detail['pfs'] is None and detail['pfs_status']=='N/A_ZERO_INVESTMENT'
    assert detail['ticket_count']==detail['total_investment']==0 and detail['tickets']==[]
    assert detail['signed_final_verified'] is False and 'final_sha256' not in bundle['manifest']
    assert detail['subtype']=='AKI_NO_BET' and detail['full20_eligible'] is True
    assert detail['normal_aki_no_bet'] is True and detail['formal_full_prediction_completed'] is False
    assert detail['source_freeze_at']==case['terminal']['source_freeze_at']
    assert 'SOURCE Freeze：'+detail['source_freeze_at'] in bundle['text']
    assert 'AKI_SINGLE_HEAD_FORBIDDEN' in bundle['text'] and 'PFS：N/A' in bundle['text']
    assert len(detail['runners'])==9
    for row in detail['runners']:
        assert len(row['indices'])==20
        assert row['indices']==case['terminal']['index_universe'][row['runner_id']]
        assert all(name in bundle['text'] for name in row['indices'])
    assert before=={p:p.read_bytes() for p in before}
    assert len(case['commands'])==2


@pytest.mark.parametrize('kind',['source_signature','source_race','source_universe','source_time','terminal_hash','intent_cutoff'])
def test_no_bet_projection_rejects_unbound_originals(case,kind):
    path=case['paths']['source' if kind.startswith('source') else 'terminal' if kind=='terminal_hash' else 'intent']
    value=json.loads(path.read_text())
    if kind=='source_signature':value['signature']=base64.b64encode(b'0'*64).decode()
    elif kind=='source_race':value['artifact']['race_id']='KM-JRA-KYO-20261031-R05'
    elif kind=='source_universe':value['artifact']['jra_official_runner_universe']['runners'].pop()
    elif kind=='source_time':value['receipt']['timestamp']='2099-01-01T00:00:00Z'
    elif kind=='terminal_hash':value['index_universe']['1']['HPI']['value']+=1
    else:value['prediction_cutoff']='2099-01-01T00:00:00Z'
    path.write_text(json.dumps(value))
    with pytest.raises((ValueError,InvalidSignature)):compose(case)


@pytest.mark.parametrize('kind',['active_ids','receipt_after_terminal','wrong_race'])
def test_even_cryptographically_signed_source_must_bind_active_identity_and_clocks(case,kind):
    envelope=json.loads(case['paths']['source'].read_text())
    if kind=='active_ids':envelope['artifact']['jra_official_runner_universe']['runners'].pop()
    elif kind=='receipt_after_terminal':envelope['receipt']['timestamp']=(projection.instant(case['terminal']['created_at'])+timedelta(seconds=1)).isoformat()
    else:
        envelope['artifact']['race_id']='KM-JRA-KYO-20261031-R05'
        envelope['receipt']['race_id']='KM-JRA-KYO-20261031-R05'
    envelope['receipt']['artifact_sha256']=projection.digest(envelope['artifact'])
    envelope['receipt_sha256']=projection.digest(envelope['receipt'])
    envelope['signature']=base64.b64encode(case['fixture_key'].sign(delivery.canonical_bytes(envelope['receipt']))).decode()
    case['paths']['source'].write_text(json.dumps(envelope))
    terminal=copy.deepcopy(case['terminal'])
    terminal['signed_source_receipt_sha256']=envelope['receipt_sha256']
    terminal['failure_report']['source_checkpoint_manifest']=source_checkpoint_manifest(envelope,terminal['source_execution_id'])
    terminal['failure_report']['sha256']=projection.digest({k:v for k,v in terminal['failure_report'].items() if k!='sha256'})
    terminal['report_sha256']=terminal['failure_report']['sha256']
    terminal['sha256']=projection.digest({k:v for k,v in terminal.items() if k!='sha256'})
    case['paths']['terminal'].write_text(json.dumps(terminal))
    expected='ACTIVE_RUNNER_UNIVERSE_MISMATCH' if kind=='active_ids' else 'SOURCE_OWNER_IDENTITY_OR_TIME_MISMATCH'
    with pytest.raises(ValueError,match=expected):compose(case)


@pytest.mark.parametrize('mode',['refused','empty_result','no_witness','late_witness'])
def test_no_bet_requires_actual_successful_oidc_verifier_and_early_witness(case,monkeypatch,mode):
    def gh(*args,**kwargs):
        values=[] if mode=='empty_result' else [{'verificationResult':{'verifiedTimestamps':
            [] if mode=='no_witness' else [{'timestamp':'2099-01-01T00:00:00Z'}]}}]
        return SimpleNamespace(returncode=1 if mode=='refused' else 0,stdout=json.dumps(values),stderr='not authorized')
    monkeypatch.setattr(projection.subprocess,'run',gh)
    with pytest.raises(ValueError):compose(case)


def test_no_bet_boolean_trust_is_never_a_verifier(case):
    with pytest.raises(ValueError,match='INDEPENDENT_TRUST_VERIFIER_REQUIRED'):
        projection.build_no_bet_presentation(case['paths']['terminal'],**case['args'],trust=True)


@pytest.mark.parametrize('kind',['issuer','workflow','code','ref','runner','subject'])
def test_success_exit_and_timestamp_cannot_substitute_for_pinned_identity_and_subject(case,monkeypatch,kind):
    original=projection.subprocess.run
    def gh(command,**kwargs):
        result=original(command,**kwargs);data=json.loads(result.stdout)
        certificate=data[0]['verificationResult']['signature']['certificate']
        keys={'issuer':'issuer','workflow':'subjectAlternativeName','code':'sourceRepositoryDigest',
              'ref':'sourceRepositoryRef','runner':'runnerEnvironment'}
        if kind=='subject':data[0]['verificationResult']['statement']['subject'][0]['digest']['sha256']='0'*64
        else:certificate[keys[kind]]='UNTRUSTED'
        return SimpleNamespace(returncode=0,stdout=json.dumps(data),stderr='')
    monkeypatch.setattr(projection.subprocess,'run',gh)
    with pytest.raises(ValueError,match='OIDC_BYTES_OR_PRE_CUTOFF_WITNESS_INVALID'):compose(case)


def test_projection_rejects_terminal_replacement_between_structural_and_oidc_verification(case,monkeypatch):
    from jra_source_runtime import verify_source_envelope
    original=verify_source_envelope.verify
    def replace_after_source_verify(path):
        result=original(path)
        value=json.loads(case['paths']['terminal'].read_text())
        value['created_at']=(projection.instant(value['created_at'])+timedelta(seconds=1)).isoformat()
        value['sha256']=projection.digest({k:v for k,v in value.items() if k!='sha256'})
        case['paths']['terminal'].write_text(json.dumps(value))
        return result
    monkeypatch.setattr(verify_source_envelope,'verify',replace_after_source_verify)
    with pytest.raises(ValueError,match='INPUT_BYTES_CHANGED_DURING_VERIFICATION'):compose(case)


def test_no_bet_saved_projection_rehash_cannot_change_canonical_values(case):
    compose(case)
    detail=case['directory']/'no_bet_presentation_detail.json'
    value=json.loads(detail.read_text());value['runners'][0]['indices']['HPI']['value']+=1;detail.write_text(json.dumps(value))
    with pytest.raises(ValueError,match='CANONICAL_PROJECTION_MISMATCH'):send(case)
    assert not case['transport'].sent


def test_no_bet_uses_existing_sender_and_inbox_but_no_fake_final_or_ack(case):
    compose(case);record=send(case)
    assert record['terminal_sha256']==case['terminal']['sha256'] and 'final_sha256' not in record
    assert record['NOTIFICATION_SENT'] is True and record['DESTINATION_ARRIVAL_CONFIRMED'] is None
    checked=delivery.verify_no_bet_mail_arrival(case['paths']['terminal'],**case['args'],
        presentation_dir=case['directory'],private_store=case['private_store'],authorization=case['auth'],
        transport=case['transport'],now=lambda:case['at'])
    assert checked['DESTINATION_ARRIVAL_CONFIRMED'] is True and checked['delivered_before_cutoff'] is True
    assert checked['USER_ACKNOWLEDGED'] is None and checked['user_received_at'] is None


@pytest.mark.parametrize('change',[{'scope':'JRA_SIGNED_FINAL_COMPLETE_BODY'},
    {'no_bet_trust_policy_sha256':'0'*64},{'no_bet_projection_code_sha256':'0'*64},{'enabled':False}])
def test_no_bet_separate_owner_scope_and_pins_required_before_trust_io(case,change):
    case['auth'].update(change)
    with pytest.raises(ValueError):send(case)
    assert not case['commands'] and not case['transport'].sent


def test_final_and_no_bet_share_same_race_account_claim_namespace(case):
    compose(case)
    key=hashlib.sha256((case['terminal']['race_id']+'\0'+case['auth']['account_sub']).encode()).hexdigest()
    case['private_store'].mkdir(mode=0o700)
    (case['private_store']/(key+'.claim.json')).write_text(json.dumps({
        'race_id':case['terminal']['race_id'],'final_sha256':'0'*64,'source_sha256':'1'*64,'body_sha256':'2'*64}))
    with pytest.raises(ValueError,match='IMMUTABLE_CLAIM_CONFLICT'):send(case)
    assert not case['transport'].sent


def config_file(tmp_path,authorization,private_store,*,kind='SIGNED_FINAL'):
    path=tmp_path/'owner-private-config.json'
    path.write_text(json.dumps({'authorization':authorization if kind=='SIGNED_FINAL' else {'enabled':False},
        'no_bet_authorization':authorization if kind=='NO_BET' else {'enabled':False},
        'gmail_oauth':{'client_id':'PRIVATE_FAKE_CLIENT','client_secret':'PRIVATE_FAKE_SECRET',
                       'refresh_token':'PRIVATE_FAKE_REFRESH'},'private_store':str(private_store)}))
    path.chmod(0o600)
    return path


def mock_canonical_api(monkeypatch,artifact_path,directory,*,kind='SIGNED_FINAL',missing=False):
    artifact=json.loads(Path(artifact_path).read_text());race=artifact['race_id']
    files={'runtime/final_artifacts/'+race+'.json':Path(artifact_path)} if kind=='SIGNED_FINAL' else {
        'runtime/jra_no_bet_terminals/'+artifact['source_execution_id']+'.json':Path(artifact_path)}
    names=['presentation.json','presentation_detail.json','presentation.md'] if kind=='SIGNED_FINAL' else []
    files.update({'runtime/jra_delivery/'+race+'/'+name:Path(directory)/name for name in names})
    original=projection.subprocess.run
    def gh(command,**kwargs):
        if command[:2]!=['gh','api']:return original(command,**kwargs)
        assert '--method' in command and command[command.index('--method')+1]=='GET'
        relative=command[4].split('/contents/',1)[1].split('?ref=',1)[0]
        assert 'complete_body' not in relative and 'no_bet_presentation' not in relative
        if missing:return SimpleNamespace(returncode=1,stdout='',stderr='not found')
        value=files[relative].read_bytes()
        return SimpleNamespace(returncode=0,stdout=hashlib.sha1(b'blob '+str(len(value)).encode()+b'\0'+value).hexdigest()+'\n',stderr='')
    monkeypatch.setattr(projection.subprocess,'run',gh)


@pytest.mark.parametrize('kind',['SIGNED_FINAL','NO_BET'])
def test_completion_event_disabled_means_no_config_artifact_trust_or_oauth_io(tmp_path,monkeypatch,kind):
    monkeypatch.delenv('KM_JRA_SELF_DELIVERY_ENABLED',raising=False)
    monkeypatch.setenv('KM_JRA_DELIVERY_CONFIG_PATH',str(tmp_path/'NONEXISTENT'))
    monkeypatch.setattr(delivery,'GmailSelfTransport',lambda **kwargs:pytest.fail('OAuth constructor reached'))
    monkeypatch.setattr(projection.subprocess,'run',lambda *args,**kwargs:pytest.fail('external verifier reached'))
    result=delivery.dispatch_owner_delivery_event(tmp_path/'NONEXISTENT',presentation_dir=tmp_path/'NONE',root=PROJECT,kind=kind)
    assert result['send_attempted'] is False and result['NOTIFICATION_SENT'] is None


def test_global_flag_does_not_activate_disabled_private_scope(tmp_path,monkeypatch):
    cfg=config_file(tmp_path,{'enabled':False},tmp_path/'private')
    monkeypatch.setenv('KM_JRA_SELF_DELIVERY_ENABLED','true')
    monkeypatch.setenv('KM_JRA_DELIVERY_CONFIG_PATH',str(cfg))
    monkeypatch.setattr(delivery,'GmailSelfTransport',lambda **kwargs:pytest.fail('OAuth constructor reached'))
    result=delivery.dispatch_owner_delivery_event(tmp_path/'NONE',presentation_dir=tmp_path/'NONE',root=PROJECT)
    assert result['reason']=='OWNER_C_SCOPE_NOT_ACTIVATED' and result['send_attempted'] is False


def test_signed_completion_event_creates_exact_body_privately_without_public_mutation(prepared_signed,tmp_path,monkeypatch):
    final,args,transport,at,bundle=prepared_signed
    artifact=tmp_path/'final.json';artifact.write_text(json.dumps(final))
    public_before={p:p.read_bytes() for p in Path(args['presentation_dir']).iterdir()}
    mock_canonical_api(monkeypatch,artifact,args['presentation_dir'])
    cfg=config_file(tmp_path,args['authorization'],args['private_store'])
    monkeypatch.setenv('KM_JRA_SELF_DELIVERY_ENABLED','true');monkeypatch.setenv('KM_JRA_DELIVERY_CONFIG_PATH',str(cfg))
    monkeypatch.setenv('GITHUB_RUN_ID','OFFLINE_EVENT_1')
    monkeypatch.setattr(delivery,'GmailSelfTransport',lambda **kwargs:transport)
    result=delivery.dispatch_owner_delivery_event(artifact,presentation_dir=args['presentation_dir'],root=ROOT,
                    canonical_ref='3'*40,now=lambda:at)
    assert {p:p.read_bytes() for p in Path(args['presentation_dir']).iterdir()}==public_before
    private=Path(args['private_store'])/'canonical'/final['race_id']/final['sha256']
    before=(private/'complete_body.json').read_bytes()
    delivery.save_complete_body(final,private,root=ROOT,created_at='2099-01-01T00:00:00Z')
    assert (private/'complete_body.json').read_bytes()==before
    assert all(not p.stat().st_mode&0o077 for p in (Path(args['private_store']),private))
    assert result['NOTIFICATION_SENT'] is True and result['DESTINATION_ARRIVAL_CONFIRMED'] is True
    assert result['delivered_before_cutoff'] is True and result['USER_ACKNOWLEDGED'] is None
    assert all(value not in json.dumps(result) for value in ('PRIVATE_FAKE_SECRET','owner@example.invalid','offline-1'))
    receipt=json.loads(next(Path(args['private_store']).glob('*.receipt.json')).read_text())
    assert receipt['execution_context']['GITHUB_RUN_ID']=='OFFLINE_EVENT_1'
    assert receipt['canonical_readback']['canonical_ref']=='3'*40
    assert receipt['final_sha256']==final['sha256'] and receipt['autonomous_completion_claim'] is False
    sent=len(transport.sent);read=len(transport.read_calls)
    again=delivery.dispatch_owner_delivery_event(artifact,presentation_dir=args['presentation_dir'],root=ROOT,
                    canonical_ref='3'*40,now=lambda:at+timedelta(days=1))
    assert again['delivered_before_cutoff'] is True
    assert len(transport.sent)==sent and len(transport.read_calls)==read


def test_completion_event_remote_mismatch_never_reaches_oauth(prepared_signed,tmp_path,monkeypatch):
    final,args,transport,at,bundle=prepared_signed
    artifact=tmp_path/'final.json';artifact.write_text(json.dumps(final))
    mock_canonical_api(monkeypatch,artifact,args['presentation_dir'],missing=True)
    cfg=config_file(tmp_path,args['authorization'],args['private_store'])
    monkeypatch.setenv('KM_JRA_SELF_DELIVERY_ENABLED','true');monkeypatch.setenv('KM_JRA_DELIVERY_CONFIG_PATH',str(cfg))
    monkeypatch.setattr(delivery,'GmailSelfTransport',lambda **kwargs:pytest.fail('OAuth constructor reached'))
    with pytest.raises(ValueError,match='CANONICAL_REMOTE_EXACT_BYTES_NOT_VERIFIED'):
        delivery.dispatch_owner_delivery_event(artifact,presentation_dir=args['presentation_dir'],root=ROOT,
                    canonical_ref='3'*40,now=lambda:at)


def test_complete_body_rejects_public_output_before_any_projection_or_directory_creation(tmp_path,monkeypatch):
    root=tmp_path/'checkout';directory=root/'runtime/jra_delivery/new-race'
    with pytest.raises(ValueError,match='PRIVATE_BODY_OUTSIDE_REPOSITORY_REQUIRED'):
        delivery.save_complete_body({},directory,root=root)
    assert not directory.exists()


def test_private_event_invalid_store_never_reaches_gmail_or_writes_public_body(prepared_signed,tmp_path,monkeypatch):
    final,args,transport,at,bundle=prepared_signed
    artifact=tmp_path/'final.json';artifact.write_text(json.dumps(final))
    public_before={p:p.read_bytes() for p in Path(args['presentation_dir']).iterdir()}
    args['private_store'].mkdir(mode=0o755)
    cfg=config_file(tmp_path,args['authorization'],args['private_store'])
    monkeypatch.setenv('KM_JRA_SELF_DELIVERY_ENABLED','true');monkeypatch.setenv('KM_JRA_DELIVERY_CONFIG_PATH',str(cfg))
    monkeypatch.setattr(delivery,'GmailSelfTransport',lambda **kwargs:pytest.fail('OAuth constructor reached'))
    with pytest.raises(ValueError,match='PRIVATE_BODY_DIRECTORY_0700_REQUIRED'):
        delivery.dispatch_owner_delivery_event(artifact,presentation_dir=args['presentation_dir'],root=ROOT,
                    canonical_ref='3'*40,now=lambda:at)
    assert not list(args['private_store'].iterdir())
    assert {p:p.read_bytes() for p in Path(args['presentation_dir']).iterdir()}==public_before


def test_unknown_event_send_retains_private_attempt_and_no_false_provider_acceptance(case,tmp_path,monkeypatch):
    compose(case);mock_canonical_api(monkeypatch,case['paths']['terminal'],case['directory'],kind='NO_BET')
    cfg=config_file(tmp_path,case['auth'],case['private_store'],kind='NO_BET')
    monkeypatch.setenv('KM_JRA_SELF_DELIVERY_ENABLED','true');monkeypatch.setenv('KM_JRA_DELIVERY_CONFIG_PATH',str(cfg))
    monkeypatch.setenv('GITHUB_RUN_ID','OFFLINE_NO_BET_EVENT')
    case['transport'].fail_send=True
    monkeypatch.setattr(delivery,'GmailSelfTransport',lambda **kwargs:case['transport'])
    with pytest.raises(delivery.DeliveryEventError) as caught:
        delivery.dispatch_owner_delivery_event(case['paths']['terminal'],**case['args'],
            presentation_dir=case['directory'],kind='NO_BET',canonical_ref='3'*40,now=lambda:case['at'])
    summary=caught.value.summary
    assert summary['send_attempted'] is True and summary['provider_accepted_parts_recorded']==0
    assert summary['NOTIFICATION_SENT'] is False and summary['DESTINATION_ARRIVAL_CONFIRMED'] is None
    assert summary['private_receipt_id'] and summary['private_receipt_sha256']
    assert summary['terminal_sha256']==case['terminal']['sha256'] and 'final_sha256' not in summary
    assert summary['original_execution_context']['GITHUB_RUN_ID']=='OFFLINE_NO_BET_EVENT'
    assert 'PRIVATE_FAKE_SECRET' not in json.dumps(summary)
    sent=len(case['transport'].sent)
    with pytest.raises(delivery.DeliveryEventError):
        delivery.dispatch_owner_delivery_event(case['paths']['terminal'],**case['args'],
            presentation_dir=case['directory'],kind='NO_BET',canonical_ref='3'*40,now=lambda:case['at'])
    assert len(case['transport'].sent)==sent


def test_completion_event_resumes_multipart_readback_after_last_send_timeout(prepared_signed,tmp_path,monkeypatch):
    final,args,sender,at,bundle=prepared_signed
    artifact=tmp_path/'final.json';artifact.write_text(json.dumps(final))
    mock_canonical_api(monkeypatch,artifact,args['presentation_dir'])
    cfg=config_file(tmp_path,args['authorization'],args['private_store'])
    monkeypatch.setenv('KM_JRA_SELF_DELIVERY_ENABLED','true')
    monkeypatch.setenv('KM_JRA_DELIVERY_CONFIG_PATH',str(cfg))
    plan=delivery._complete_delivery_plan(final,args['presentation_dir'],ROOT,250000)
    assert len(plan['chunks'])>1
    send=sender.send
    def timeout_on_last(raw):
        sender.fail_send=len(sender.sent)==len(plan['chunks'])-1
        return send(raw)
    sender.send=timeout_on_last
    monkeypatch.setattr(delivery,'GmailSelfTransport',lambda **kwargs:sender)
    def run():
        return delivery.dispatch_owner_delivery_event(artifact,presentation_dir=args['presentation_dir'],
            root=ROOT,canonical_ref='3'*40,now=lambda:at)
    with pytest.raises(delivery.DeliveryEventError,match='SEND_OUTCOME_UNKNOWN_NO_RETRY'):
        run()
    reader=FakeGmail(at)
    reader.sent=sender.sent.copy()
    reader.send=lambda raw:pytest.fail('unexpected second send')
    reader.find_inbox_message=lambda value:f'offline-{len(plan["chunks"])}'
    monkeypatch.setattr(delivery,'GmailSelfTransport',lambda **kwargs:reader)
    result=run()
    assert result['DESTINATION_ARRIVAL_CONFIRMED'] is True
    assert result['provider_accepted_parts_recorded']==len(plan['chunks'])
    assert len(reader.read_calls)==len(plan['chunks'])
    assert result['USER_ACKNOWLEDGED'] is None


def test_claim_without_receipt_never_becomes_send_attempt_or_provider_evidence(case,tmp_path,monkeypatch):
    compose(case);mock_canonical_api(monkeypatch,case['paths']['terminal'],case['directory'],kind='NO_BET')
    cfg=config_file(tmp_path,case['auth'],case['private_store'],kind='NO_BET')
    monkeypatch.setenv('KM_JRA_SELF_DELIVERY_ENABLED','true');monkeypatch.setenv('KM_JRA_DELIVERY_CONFIG_PATH',str(cfg))
    monkeypatch.setattr(delivery,'GmailSelfTransport',lambda **kwargs:case['transport'])
    plan=delivery._no_bet_delivery_plan(case['paths']['terminal'],**case['args'],presentation_dir=case['directory'],part_bytes=250000)
    key=hashlib.sha256((plan['race_id']+'\0'+case['auth']['account_sub']).encode()).hexdigest()
    case['private_store'].mkdir(mode=0o700)
    (case['private_store']/(key+'.claim.json')).write_text(json.dumps(delivery._delivery_binding(plan)))
    with pytest.raises(delivery.DeliveryEventError) as caught:
        delivery.dispatch_owner_delivery_event(case['paths']['terminal'],**case['args'],
            presentation_dir=case['directory'],kind='NO_BET',canonical_ref='3'*40,now=lambda:case['at'])
    assert caught.value.summary['send_attempted'] is None and caught.value.summary['NOTIFICATION_SENT'] is None
    assert not case['transport'].sent


def test_evidence_no_bet_is_deliverable_but_not_full20_or_normal_prediction_completion(case):
    from jra_production_no_bet_terminal import build_no_bet_terminal
    report=copy.deepcopy(case['terminal']['failure_report'])
    report['production_full_numerical_ready']=False
    partial=report['partial_production_base_calculation']
    first=next(iter(partial['runners']))
    partial['runners'][first]['indices']['HPI']={'status':'BLOCKED','value':None,'reason':'OFFLINE_MISSING_EVIDENCE'}
    partial['calculated_base_cells']=116;partial['blocked_base_cells']=1
    intent=json.loads(case['paths']['intent'].read_text());intent['current_authority_manifest']=case['auth']['authority']
    intent['prediction_cutoff']=report['source_checkpoint_manifest']['prediction_cutoff']
    case['paths']['intent'].write_text(json.dumps(intent))
    terminal=build_no_bet_terminal(intent,report,source_receipt_verified=True,created_at=case['terminal']['created_at'])
    case['paths']['terminal'].write_text(json.dumps(terminal))
    bundle=compose(case)
    assert bundle['detail']['subtype']=='EVIDENCE_NO_BET'
    assert bundle['detail']['full20_eligible'] is False and bundle['detail']['normal_aki_no_bet'] is False
    assert bundle['detail']['formal_full_prediction_completed'] is False and bundle['detail']['pfs'] is None

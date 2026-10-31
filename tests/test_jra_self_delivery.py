"""Offline sender contract tests. No Gmail, OAuth or Live acceptance occurs."""
import base64
import copy
from datetime import datetime, timedelta, timezone
from email import policy
from email.parser import BytesParser
import hashlib
import json
from pathlib import Path
import sys

import pytest
from cryptography.exceptions import InvalidSignature

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'runtime'))
import jra_presentation as presentation
import jra_delivery as delivery


class FakeGmail:
    def __init__(self, at):
        self.at=at
        self.identity_calls=0
        self.sent=[]
        self.read_calls=[]
        self.identity_value={'sub':'offline-owner-sub','email':'owner@example.invalid','email_verified':True}
        self.label_ids=['INBOX','SENT']
        self.change=None
        self.fail_send=False
        self.duplicate_id=False

    def identity(self):
        self.identity_calls+=1
        return self.identity_value

    def send(self, raw):
        self.sent.append(raw)
        if self.fail_send: raise TimeoutError('PRIVATE_CREDENTIAL_MUST_NOT_APPEAR')
        return {'id':'offline-1' if self.duplicate_id else f'offline-{len(self.sent)}',
                'provider_date':self.at.strftime('%a, %d %b %Y %H:%M:%S GMT')}

    def received(self, identifier):
        self.read_calls.append(identifier)
        number=int(identifier.split('-')[-1])-1
        raw=self.sent[number]
        if self.change: raw=self.change(raw)
        return {'id':identifier,'labelIds':self.label_ids,
                'internalDate':str(int(self.at.timestamp()*1000)),
                '_provider_readback_date':self.at.strftime('%a, %d %b %Y %H:%M:%S GMT'),
                'raw':base64.urlsafe_b64encode(raw).decode()}


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def blocked(*args, **kwargs): pytest.fail('Offline test attempted a real network call')
    monkeypatch.setattr(delivery.urllib.request,'urlopen',blocked)
    monkeypatch.setattr(delivery.urllib.request.OpenerDirector,'open',blocked)


@pytest.fixture
def prepared(tmp_path):
    final=json.loads((ROOT/'runtime/final_artifacts/KM-JRA-KYO-20261017-R07.json').read_text())
    health,contract=presentation.archived_trust(final,ROOT)
    bundle=presentation.build_presentation(final,health=health,contract=contract,
                                         generated_at='2026-10-17T03:30:00Z')
    directory=tmp_path/'presentation'
    presentation.save_presentation(directory,bundle)
    at=datetime.fromisoformat(final['final_receipt']['receipt']['timestamp'].replace('Z','+00:00'))+timedelta(minutes=1)
    auth={'enabled':True,'actor':'GMAIL_SELF','scope':'JRA_SIGNED_FINAL_COMPLETE_BODY',
          'owner_approval_ref':'OFFLINE_TEST_ONLY_NO_ACTUAL_APPROVAL',
          'actor_code_sha256':hashlib.sha256(Path(delivery.__file__).read_bytes()).hexdigest(),
          'authority':bundle['manifest']['authority'],'account_email':'owner@example.invalid',
          'account_sub':'offline-owner-sub','readback_authorized':True}
    transport=FakeGmail(at)
    args={'presentation_dir':directory,'root':ROOT,'private_store':tmp_path/'private',
          'authorization':auth,'transport':transport,'part_bytes':250000}
    return final,args,transport,at,bundle


def send(prepared, **changes):
    final,args,transport,at,bundle=prepared
    return delivery.send_complete_self_mail(final,now=lambda:at,**{**args,**changes})


def receipt_path(args):
    return next(Path(args['private_store']).glob('*.receipt.json'))


def rewrite_receipt(args, edit):
    path=receipt_path(args);record=json.loads(path.read_text());edit(record)
    record['sha256']=delivery._sha({k:v for k,v in record.items() if k!='sha256'})
    path.write_text(json.dumps(record))


def test_d1_final_signature_or_saved_projection_tamper_prevents_send(prepared):
    final,args,transport,at,bundle=prepared
    final['final_ticket']['tickets'][0]['stake']+=100
    final['sha256']=delivery._sha({k:v for k,v in final.items() if k!='sha256'})
    with pytest.raises((ValueError,InvalidSignature)):
        send(prepared)
    assert not transport.sent and transport.identity_calls==0


def test_d1_rehashed_canonical_projection_forgery_is_rejected(prepared):
    final,args,transport,at,bundle=prepared
    detail=args['presentation_dir']/'presentation_detail.json'
    data=json.loads(detail.read_text());data['ranking'][0]['indices']['HPI']=999
    detail.write_text(json.dumps(data))
    manifest=args['presentation_dir']/'presentation.json';m=json.loads(manifest.read_text())
    m['detail_sha256']=presentation.digest(data)
    m['sha256']=presentation.digest({k:v for k,v in m.items() if k!='sha256'})
    manifest.write_text(json.dumps(m))
    with pytest.raises(ValueError,match='CANONICAL_PROJECTION'):
        send(prepared)
    assert not transport.sent and transport.identity_calls==0


def test_d2_d3_exact_full_body_indices_roles_and_entire_ticket_ledger(prepared):
    final,args,transport,at,bundle=prepared
    original=copy.deepcopy(final)
    before={p.name:p.read_bytes() for p in args['presentation_dir'].iterdir()}
    record=send(prepared)
    chunks=[]
    for raw in transport.sent:
        message=BytesParser(policy=policy.default).parsebytes(raw)
        assert message.get_all('To')==['owner@example.invalid']
        assert not message.get_all('Cc') and not message.get_all('Bcc')
        chunks.append(next(message.iter_attachments()).get_payload(decode=True))
    body=b''.join(chunks).decode()
    assert body==presentation.complete_body(bundle,final)
    for row in bundle['detail']['ranking']:
        assert row['name'] in body
        assert all(index in body and str(value) in body for index,value in row['indices'].items())
    assert bundle['detail']['canonical_tree'] in body
    assert record['body_sha256']==hashlib.sha256(body.encode()).hexdigest()
    assert final==original
    assert before=={p.name:p.read_bytes() for p in args['presentation_dir'].iterdir()}
    assert record['NOTIFICATION_SENT'] is True
    assert record['DESTINATION_ARRIVAL_CONFIRMED'] is None
    assert record['user_delivery_verified'] is False and record['USER_ACKNOWLEDGED'] is None


def test_d4_paper_mec_is_never_promoted_to_purchase_recommendation(prepared):
    final,args,transport,at,bundle=prepared
    f=json.loads((ROOT/'runtime/final_artifacts/KM-JRA-KYO-20261017-R05.json').read_text())
    h,c=presentation.archived_trust(f,ROOT)
    b=presentation.build_presentation(f,health=h,contract=c,generated_at=f['final_freeze_timestamp'])
    directory=args['presentation_dir'].parent/'paper';presentation.save_presentation(directory,b)
    when=datetime.fromisoformat(f['final_receipt']['receipt']['timestamp'].replace('Z','+00:00'))+timedelta(seconds=1)
    delivery.send_complete_self_mail(f,**{**args,'presentation_dir':directory},now=lambda:when)
    body=b''.join(next(BytesParser(policy=policy.default).parsebytes(raw).iter_attachments()).get_payload(decode=True)
                  for raw in transport.sent).decode()
    assert '正式券面 0点・0円' in body
    assert 'MEC参考 8点・800円（正式券面と別）' in body
    assert f['final_ticket']['tickets']==[]


@pytest.mark.parametrize('change',[
    {'enabled':False},{'owner_approval_ref':''},{'actor_code_sha256':'0'*64},
    {'account_email':'another@example.invalid'},{'account_sub':'different-sub'},
    {'account_email':'owner@example.invalid\r\nBcc: other@example.invalid'},
    {'authority':'UNAPPROVED'},{'scope':'ANY_MESSAGE'}])
def test_d5_owner_code_scope_identity_and_single_self_destination(prepared,change):
    final,args,transport,at,bundle=prepared
    args['authorization'].update(change)
    with pytest.raises(ValueError): send(prepared)
    assert transport.sent==[]


def test_d5_default_disabled_never_even_requests_identity(prepared):
    final,args,transport,at,bundle=prepared
    with pytest.raises(ValueError,match='OWNER_ACTIVATION_REQUIRED'):
        send(prepared,authorization=None)
    assert transport.identity_calls==0 and not transport.sent


def test_d5_unverified_google_email_fails(prepared):
    final,args,transport,at,bundle=prepared
    transport.identity_value['email_verified']=False
    with pytest.raises(ValueError,match='AUTHENTICATED_SELF_MISMATCH'): send(prepared)
    assert not transport.sent


def test_d5_readback_needs_separate_owner_permission(prepared):
    final,args,transport,at,bundle=prepared
    send(prepared);args['authorization']['readback_authorized']=False
    with pytest.raises(ValueError,match='OWNER_INBOX_READBACK_REQUIRED'):
        delivery.verify_self_mail_arrival(final,**args,now=lambda:transport.at)
    assert not transport.read_calls


def test_d6_unknown_send_outcome_is_durable_private_and_never_retried(prepared):
    final,args,transport,at,bundle=prepared
    transport.fail_send=True
    with pytest.raises(ValueError,match='SEND_OUTCOME_UNKNOWN_NO_RETRY'): send(prepared)
    text=receipt_path(args).read_text();record=json.loads(text)
    assert record['NOTIFICATION_SENT'] is False
    assert record['failure_class']=='UNKNOWN_SEND_OUTCOME:TimeoutError'
    assert 'PRIVATE_CREDENTIAL_MUST_NOT_APPEAR' not in text
    assert 'owner@example.invalid' not in text and 'offline-owner-sub' not in text
    with pytest.raises(ValueError,match='PRIOR_ATTEMPT_REVIEW_REQUIRED'): send(prepared)
    assert len(transport.sent)==1


def test_d6_duplicate_provider_ids_cannot_mark_complete(prepared):
    final,args,transport,at,bundle=prepared
    transport.duplicate_id=True
    with pytest.raises(ValueError,match='SEND_OUTCOME_UNKNOWN_NO_RETRY'):
        send(prepared,part_bytes=10000)
    record=json.loads(receipt_path(args).read_text())
    assert record['NOTIFICATION_SENT'] is False and len(transport.sent)==2


def test_d7_all_utf8_parts_reassemble_and_inbox_readback_never_claims_ack(prepared):
    final,args,transport,at,bundle=prepared
    args['part_bytes']=10000
    sent=send(prepared)
    assert sent['part_count']>1 and all(len(c.encode())<=10000 for c in delivery._complete_delivery_plan(
        final,args['presentation_dir'],ROOT,10000)['chunks'])
    checked=delivery.verify_self_mail_arrival(final,**args,now=lambda:transport.at)
    assert checked['DESTINATION_ARRIVAL_CONFIRMED'] is True
    assert checked['verified_body_sha256']==sent['body_sha256']
    assert checked['delivered_before_cutoff'] is True
    assert checked['USER_ACKNOWLEDGED'] is None


@pytest.mark.parametrize('kind',['missing_part','tampered_body','bcc','wrong_source','wrong_sub','wrong_destination','invalid_time'])
def test_d7_incomplete_or_unbound_receipts_and_messages_reject(prepared,kind):
    final,args,transport,at,bundle=prepared
    send(prepared)
    if kind=='missing_part': rewrite_receipt(args,lambda r:r['parts'].pop())
    elif kind=='wrong_sub': rewrite_receipt(args,lambda r:r.update(account_sub_sha256='0'*64))
    elif kind=='wrong_destination': rewrite_receipt(args,lambda r:r.update(destination_sha256='0'*64))
    else:
        def change(raw):
            message=BytesParser(policy=policy.default).parsebytes(raw)
            if kind=='tampered_body':
                part=next(message.iter_attachments());part.set_payload(base64.b64encode(b'omitted').decode())
            elif kind=='bcc': message['Bcc']='other@example.invalid'
            elif kind=='wrong_source': message.replace_header('X-KeibaMetrics-Source-SHA256','0'*64)
            return message.as_bytes()
        transport.change=change
        if kind=='invalid_time': transport.at=at-timedelta(days=1)
    with pytest.raises(ValueError): delivery.verify_self_mail_arrival(final,**args,now=lambda:transport.at)
    assert json.loads(receipt_path(args).read_text())['user_delivery_verified'] is False


def test_d7_provider_acceptance_without_inbox_is_not_arrival(prepared):
    final,args,transport,at,bundle=prepared
    send(prepared);transport.label_ids=['SENT']
    with pytest.raises(ValueError,match='DESTINATION_NOT_OBSERVED'):
        delivery.verify_self_mail_arrival(final,**args,now=lambda:transport.at)


@pytest.mark.parametrize('preserve_folding_whitespace',[False,True])
def test_d7_folded_single_sha_headers_preserve_exact_source_binding(prepared,monkeypatch,preserve_folding_whitespace):
    final,args,transport,at,bundle=prepared
    send(prepared)
    # Wire headers fold onto an indented continuation line under SMTP policy.
    assert b'X-KeibaMetrics-Source-SHA256:\r\n ' in transport.sent[0]
    if preserve_folding_whitespace:
        # Email parser versions can preserve initial FWS in unstructured values.
        # Preserve the actual unfolded value rather than normalizing it in the fixture.
        original=policy.default.header_factory
        def factory(name,value):
            return value if name.lower().startswith('x-keibametrics-') and name.lower().endswith('-sha256') else original(name,value)
        source_parse=type(policy.default).header_source_parse
        def preserve_source_fws(self,lines):
            name,value=lines[0].split(':',1)
            if name.lower().startswith('x-keibametrics-') and name.lower().endswith('-sha256'):
                return name, ''.join([value]+lines[1:]).rstrip('\r\n')
            return source_parse(self,lines)
        monkeypatch.setattr(type(policy.default),'header_source_parse',preserve_source_fws)
        monkeypatch.setattr(policy,'default',policy.default.clone(header_factory=factory))
        parsed=BytesParser(policy=policy.default).parsebytes(transport.sent[0])
        assert str(parsed['X-KeibaMetrics-Source-SHA256']).startswith(' ')
    record=delivery.verify_self_mail_arrival(final,**args,now=lambda:at)
    assert record['DESTINATION_ARRIVAL_CONFIRMED'] is True


@pytest.mark.parametrize('kind',['altered_hash','duplicate_header','internal_space','non_hex','too_long'])
def test_d7_sha_header_folding_never_weakens_hash_or_uniqueness(prepared,kind):
    final,args,transport,at,bundle=prepared
    send(prepared)
    def change(raw):
        message=BytesParser(policy=policy.default).parsebytes(raw)
        key='X-KeibaMetrics-Source-SHA256';original=str(message[key]).strip()
        if kind=='duplicate_header':message[key]=original
        else:
            value={'altered_hash':('0' if original[0]!='0' else '1')+original[1:],
                   'internal_space':original[:32]+' '+original[32:],
                   'non_hex':'g'+original[1:],'too_long':original+'0'}[kind]
            message.replace_header(key,value)
        return message.as_bytes()
    transport.change=change
    with pytest.raises(ValueError,match='RECEIVED_SOURCE_BINDING_INVALID'):
        delivery.verify_self_mail_arrival(final,**args,now=lambda:at)


def test_d8_race_claim_suppresses_unconditional_resend_and_body_revision(prepared):
    final,args,transport,at,bundle=prepared
    first=send(prepared);calls=len(transport.sent)
    assert send(prepared)==first and len(transport.sent)==calls
    claim=next(Path(args['private_store']).glob('*.claim.json'))
    value=json.loads(claim.read_text());value['body_sha256']='0'*64;claim.write_text(json.dumps(value))
    with pytest.raises(ValueError,match='IMMUTABLE_CLAIM_CONFLICT'): send(prepared)
    assert len(transport.sent)==calls


def test_d8_readback_cannot_silently_change_chunk_boundaries(prepared):
    final,args,transport,at,bundle=prepared
    send(prepared)
    with pytest.raises(ValueError,match='RECEIPT_OR_PART_SET_INVALID'):
        delivery.verify_self_mail_arrival(final,**{**args,'part_bytes':9999},now=lambda:transport.at)


def test_d8_concurrent_same_race_has_one_atomic_send_claim(prepared):
    from concurrent.futures import ThreadPoolExecutor
    import threading
    final,args,transport,at,bundle=prepared
    barrier=threading.Barrier(2)
    def identity():
        transport.identity_calls+=1
        barrier.wait(timeout=10)
        return transport.identity_value
    transport.identity=identity
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(send,prepared) for _ in range(2)]
        accepted=[];rejected=[]
        for future in futures:
            try: accepted.append(future.result())
            except ValueError as exc: rejected.append(str(exc))
    assert len(accepted)==len(rejected)==1
    assert rejected==['JRA_DELIVERY_PRIOR_ATTEMPT_REVIEW_REQUIRED']
    assert len(transport.sent)==accepted[0]['part_count']


def test_d9_candidate_never_claims_unattended_live_acceptance(prepared):
    r=send(prepared)
    assert r['execution_origin']=='UNWIRED_OWNER_SELF_DELIVERY_CANDIDATE'
    assert r['autonomous_completion_claim'] is False and r['delivery_state']=='DELIVERY_UNKNOWN'


def test_d10_expired_cutoff_is_checked_before_identity_or_send(prepared):
    final,args,transport,at,bundle=prepared
    cutoff=datetime.fromisoformat(final['prediction_cutoff'])
    with pytest.raises(ValueError,match='CUTOFF_EXPIRED'):
        delivery.send_complete_self_mail(final,**args,now=lambda:cutoff)
    assert transport.identity_calls==0 and transport.sent==[]


def test_d10_late_return_or_inbox_arrival_never_becomes_predeadline_delivery(prepared):
    final,args,transport,at,bundle=prepared
    cutoff=datetime.fromisoformat(final['prediction_cutoff'])
    clock=[at]
    original=transport.send
    def late(raw):
        value=original(raw);clock[0]=cutoff+timedelta(seconds=2);return value
    transport.send=late
    send_record=delivery.send_complete_self_mail(final,**{**args,'part_bytes':1024*1024},now=lambda:clock[0])
    assert send_record['send_observed_before_cutoff'] is False
    transport.at=clock[0]
    received=delivery.verify_self_mail_arrival(final,**{**args,'part_bytes':1024*1024},now=lambda:transport.at)
    assert received['user_delivery_verified'] is True and received['delivered_before_cutoff'] is False


def test_d10_partial_cutoff_expiry_is_preserved_and_not_resent(prepared):
    final,args,transport,at,bundle=prepared
    cutoff=datetime.fromisoformat(final['prediction_cutoff']);clock=[at]
    original=transport.send
    def late(raw):
        value=original(raw);clock[0]=cutoff+timedelta(seconds=2);return value
    transport.send=late
    with pytest.raises(ValueError,match='CUTOFF_EXPIRED'):
        delivery.send_complete_self_mail(final,**{**args,'part_bytes':10000},now=lambda:clock[0])
    record=json.loads(receipt_path(args).read_text())
    assert record['NOTIFICATION_SENT'] is False
    assert len(transport.sent)==len(record['parts'])==1 and record['parts'][0]['accepted'] is True
    with pytest.raises(ValueError,match='PRIOR_ATTEMPT_REVIEW_REQUIRED'):
        send(prepared,part_bytes=10000)
    assert len(transport.sent)==1


def test_d10_early_internaldate_with_late_inbox_readback_is_not_early_delivery(prepared):
    final,args,transport,at,bundle=prepared
    send(prepared)
    cutoff=datetime.fromisoformat(final['prediction_cutoff'])
    record=delivery.verify_self_mail_arrival(final,**args,now=lambda:cutoff+timedelta(seconds=1))
    assert record['user_delivery_verified'] is True
    assert record['user_received_at'] is None and record['USER_ACKNOWLEDGED'] is None
    assert all(datetime.fromisoformat(t)<cutoff for t in record['provider_message_internal_dates'])
    assert datetime.fromisoformat(record['arrival_readback_observed_at'])>cutoff
    assert record['delivered_before_cutoff'] is False


def test_d10_missing_provider_readback_date_does_not_prove_deadline(prepared):
    final,args,transport,at,bundle=prepared
    send(prepared)
    received=transport.received
    def without_provider_date(identifier):
        value=received(identifier);value.pop('_provider_readback_date');return value
    transport.received=without_provider_date
    record=delivery.verify_self_mail_arrival(final,**args,now=lambda:at)
    assert record['user_delivery_verified'] is True
    assert record['delivery_deadline_evidence_complete'] is False
    assert record['delivered_before_cutoff'] is False


def test_private_journal_must_never_write_under_public_repository(prepared):
    final,args,transport,at,bundle=prepared
    with pytest.raises(ValueError,match='OUTSIDE_REPOSITORY_REQUIRED'):
        send(prepared,private_store=ROOT/'runtime/forbidden-test-mail')
    assert transport.identity_calls==0 and not transport.sent


def test_private_store_with_public_permissions_is_rejected(prepared):
    final,args,transport,at,bundle=prepared
    Path(args['private_store']).mkdir(mode=0o755)
    Path(args['private_store']).chmod(0o755)
    with pytest.raises(ValueError,match='PRIVATE_STORE_PERMISSIONS_REQUIRED'): send(prepared)
    assert transport.identity_calls==0 and not transport.sent


def test_transport_refresh_identity_send_readback_shapes_without_network(monkeypatch):
    calls=[]
    def request(url,**kwargs):
        calls.append((url,kwargs))
        if url.endswith('/token'): return {'access_token':'offline-token'},None
        if url.endswith('/userinfo'): return {'sub':'offline-owner-sub','email_verified':True},None
        if url.endswith('/send'): return {'id':'offline-id'},'provider-time'
        return {'id':'offline-id','raw':'b2ZmbGluZQ=='},None
    transport=delivery.GmailSelfTransport(client_id='offline-client',client_secret='offline-secret',refresh_token='offline-refresh')
    monkeypatch.setattr(transport,'_request',request)
    assert transport.identity()['email_verified'] is True
    assert transport.send(b'exact raw MIME')=={'id':'offline-id','provider_date':'provider-time'}
    assert transport.received('offline-id')['id']=='offline-id'
    assert len(calls)==4 and sum(url.endswith('/token') for url,kw in calls)==1
    assert json.loads(calls[2][1]['data'])=={'raw':base64.urlsafe_b64encode(b'exact raw MIME').decode()}
    assert all(kw.get('headers',{}).get('Authorization')=='Bearer offline-token' for url,kw in calls[1:])


def test_transport_rejects_caller_chosen_endpoint_without_io():
    with pytest.raises(ValueError,match='PROVIDER_ENDPOINT_INVALID'):
        delivery.GmailSelfTransport._request('https://example.invalid/steal-token')

"""Publish an exact canonical JRA tree with signed payload binding and honest delivery state."""
import argparse
import base64
from copy import deepcopy
from datetime import datetime, timezone
import json
import sys
from pathlib import Path
import urllib.request

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from jra_production_postresult import verify_final, _sha
from jra_ticket_tree_renderer import render_ticket_tree


def canonical_bytes(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()


def signed_payload(final):
    # FINAL_VERIFIED is necessarily recorded after the FINAL was signed.
    package=deepcopy(final['final_prediction_package'])
    package.get('execution_stage_manifest',{}).pop('FINAL_VERIFIED',None)
    ticket=final['final_ticket']
    return {'race_id':final['race_id'],'no_bet':ticket['no_bet'],
            'krs_required':True,'krs_executable':True,
            'krs_run_receipt':final['krs_run_receipt'],
            'final_prediction_package':package,'ticket_transport':ticket['tickets'],
            'final_ticket':ticket,'final_freeze_timestamp':final['final_freeze_timestamp']}


def verify_signed_final(final, health, contract):
    verify_final(final)
    signer=health.get('receipt_signer') or {}
    if (health.get('status')!='READY' or signer.get('ready') is not True
            or (health.get('engine') or {}).get('sha256')!=contract['engine_sha256']
            or (health.get('parameter_map') or {}).get('sha256')!=contract['parameter_map_sha256']):
        raise ValueError('JRA_DELIVERY_RUNTIME_TRUST_MISMATCH')
    envelope=final['final_receipt'];receipt=envelope['receipt']
    if (receipt.get('phase')!='FINAL' or receipt.get('status')!='PASS'
            or receipt.get('race_id')!=final['race_id'] or receipt.get('errors')
            or envelope.get('signer_key_id')!=signer['key_id']
            or envelope.get('signature_alg')!='Ed25519'
            or envelope.get('receipt_sha256')!=_sha(receipt)
            or final.get('final_receipt_sha256')!=_sha(receipt)):
        raise ValueError('JRA_DELIVERY_FINAL_RECEIPT_BINDING_INVALID')
    Ed25519PublicKey.from_public_bytes(base64.b64decode(signer['public_key_b64'],validate=True)).verify(
        base64.b64decode(envelope['signature'],validate=True),canonical_bytes(receipt))
    if receipt.get('artifact_sha256')!=_sha(signed_payload(final)):
        raise ValueError('JRA_DELIVERY_SIGNED_TICKET_PAYLOAD_MISMATCH')
    return True


def build_publication(final, *, health, contract, published_at, run_url):
    verify_signed_final(final,health,contract)
    when=datetime.fromisoformat(published_at.replace('Z','+00:00'))
    if when.tzinfo is None:raise ValueError('JRA_DELIVERY_TIMEZONE_REQUIRED')
    try:
        tree=render_ticket_tree(final)
    except Exception:
        from jra_presentation import _fallback
        tree={'text':_fallback(final),'ticket_count':len(final['final_ticket']['tickets']),
              'total_investment':sum(t['stake'] for t in final['final_ticket']['tickets'])}
    before=when<datetime.fromisoformat(final['scheduled_post_at'])
    record={'profile':'KM-JRA-CANONICAL-FINAL-PUBLICATION-v1','race_id':final['race_id'],
            'final_sha256':final['sha256'],'final_receipt_sha256':final['final_receipt_sha256'],
            'final_signed_at':final['final_receipt']['receipt']['timestamp'],
            'channel':'GITHUB_CANONICAL_AND_STEP_SUMMARY','run_url':run_url,
            'rendered_at':published_at,'rendered_before_post':before,
            'published_at':None,'published_before_post':None,'publication_state':'RENDER_AVAILABLE',
            'ticket_count':tree['ticket_count'],'total_investment':tree['total_investment'],
            'tree_sha256':__import__('hashlib').sha256(tree['text'].encode()).hexdigest(),
            'signature_verified':True,'signed_payload_bound':True,
            'notification_sent_at':None,'user_received_at':None,'user_delivery_verified':False,
            'actual_purchase_status':'UNVERIFIED'}
    record['sha256']=_sha(record)
    return record,tree['text']


class GmailSelfTransport:
    """Inactive adapter. Credentials and Owner activation are never inferred.

    The caller must first obtain explicit Owner approval, a private OAuth client
    with gmail.send plus openid/email, and (only for Inbox verification) readonly.
    Existing CLI/Actions do not instantiate this class or call the sender below.
    """
    def __init__(self, *, client_id, client_secret, refresh_token):
        self.credentials = (client_id, client_secret, refresh_token)
        self.access_token = None

    @staticmethod
    def _request(url, *, data=None, headers=None):
        from urllib.parse import urlsplit
        allowed = {'oauth2.googleapis.com', 'openidconnect.googleapis.com', 'gmail.googleapis.com'}
        if urlsplit(url).scheme != 'https' or urlsplit(url).hostname not in allowed:
            raise ValueError('JRA_DELIVERY_PROVIDER_ENDPOINT_INVALID')
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *args, **kwargs):
                return None
        opener = urllib.request.build_opener(NoRedirect())
        with opener.open(urllib.request.Request(url, data=data, headers=headers or {}), timeout=20) as r:
            if not 200 <= r.status < 300:
                raise ValueError('JRA_DELIVERY_PROVIDER_HTTP_FAILURE')
            return json.load(r), r.headers.get('Date')

    def _headers(self):
        from urllib.parse import urlencode
        if self.access_token is None:
            client, secret, refresh = self.credentials
            if not all(isinstance(v, str) and v and '\n' not in v and '\r' not in v
                       for v in (client, secret, refresh)):
                raise ValueError('JRA_DELIVERY_PRIVATE_OAUTH_REQUIRED')
            value, _ = self._request('https://oauth2.googleapis.com/token', data=urlencode({
                'grant_type':'refresh_token', 'client_id':client,
                'client_secret':secret, 'refresh_token':refresh}).encode(),
                headers={'Content-Type':'application/x-www-form-urlencoded'})
            token = value.get('access_token')
            if not isinstance(token, str) or not token or any(c in token for c in '\r\n'):
                raise ValueError('JRA_DELIVERY_OAUTH_RESPONSE_INVALID')
            self.access_token = token
        return {'Authorization':'Bearer ' + self.access_token}

    def identity(self):
        value, _ = self._request('https://openidconnect.googleapis.com/v1/userinfo', headers=self._headers())
        return value

    def send(self, raw):
        data, when = self._request('https://gmail.googleapis.com/gmail/v1/users/me/messages/send',
            data=json.dumps({'raw':base64.urlsafe_b64encode(raw).decode()}).encode(),
            headers={**self._headers(), 'Content-Type':'application/json'})
        return {'id':data.get('id'), 'provider_date':when}

    def received(self, message_id):
        from urllib.parse import quote
        value, when = self._request('https://gmail.googleapis.com/gmail/v1/users/me/messages/'
            + quote(message_id, safe='') + '?format=raw', headers=self._headers())
        return {**value,'_provider_readback_date':when}


def _self_delivery_authorization(authorization):
    """Validate a separate Owner-controlled activation record, never race input.

    Structural validation does not prove that Owner approval exists. Activation
    must be added to the real private execution configuration after that approval;
    this candidate creates no approval, token, config, webhook or workflow step.
    """
    from email.utils import parseaddr
    import hashlib
    import re
    a = authorization or {}
    if (a.get('enabled') is not True or a.get('actor') != 'GMAIL_SELF'
            or a.get('scope') != 'JRA_SIGNED_FINAL_COMPLETE_BODY'
            or not isinstance(a.get('owner_approval_ref'), str) or not a['owner_approval_ref'].strip()
            or a.get('actor_code_sha256') != hashlib.sha256(Path(__file__).read_bytes()).hexdigest()):
        raise ValueError('JRA_DELIVERY_OWNER_ACTIVATION_REQUIRED')
    email = a.get('account_email')
    subject = a.get('account_sub')
    if (not isinstance(email, str) or not re.fullmatch(r'[^\s<>@,;]+@[^\s<>@,;]+', email)
            or parseaddr(email)[1] != email
            or not isinstance(subject, str) or not subject or len(subject) > 255):
        raise ValueError('JRA_DELIVERY_OWNER_SELF_IDENTITY_REQUIRED')
    return a


def _complete_delivery_plan(final, directory, root, part_bytes):
    import hashlib
    from jra_presentation import read_presentation, complete_body
    if type(part_bytes) is not int or not 256 <= part_bytes <= 1024 * 1024:
        raise ValueError('JRA_DELIVERY_PART_SIZE_INVALID')
    bundle = read_presentation(directory, final=final, root=root,
                               expected_race_id=final['race_id'], expected_final_sha256=final['sha256'])
    body = complete_body(bundle, final)
    chunks, current, size = [], [], 0
    for char in body:
        width = len(char.encode())
        if current and size + width > part_bytes:
            chunks.append(''.join(current)); current, size = [], 0
        current.append(char); size += width
    if current:
        chunks.append(''.join(current))
    if not chunks or ''.join(chunks) != body:
        raise ValueError('JRA_DELIVERY_INCOMPLETE_BODY')
    return {'race_id':final['race_id'], 'final_sha256':final['sha256'],
            'source_sha256':bundle['manifest']['source_sha256'],
            'authority':bundle['manifest']['authority'], 'body_sha256':hashlib.sha256(body.encode()).hexdigest(),
            'prediction_cutoff':bundle['detail']['prediction_cutoff'], 'chunks':chunks}


def _self_delivery_identity(transport, authorization):
    i = transport.identity()
    if (i.get('sub') != authorization['account_sub'] or i.get('email_verified') is not True
            or str(i.get('email', '')).casefold() != authorization['account_email'].casefold()):
        raise ValueError('JRA_DELIVERY_AUTHENTICATED_SELF_MISMATCH')


def _delivery_time(value):
    v = datetime.fromisoformat(value.replace('Z','+00:00')) if isinstance(value, str) else value
    if not isinstance(v, datetime) or v.tzinfo is None:
        raise ValueError('JRA_DELIVERY_TIMEZONE_REQUIRED')
    return v


def _write_private_delivery(path, value):
    import os
    import tempfile
    if path.is_symlink(): raise ValueError('JRA_DELIVERY_PRIVATE_RECEIPT_SYMLINK')
    value['sha256'] = _sha({k:v for k,v in value.items() if k!='sha256'})
    fd, name = tempfile.mkstemp(prefix='.receipt-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
            stream.flush(); os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name): os.unlink(name)


def send_complete_self_mail(final, *, presentation_dir, root, private_store,
                            authorization=None, transport=None, now=None, part_bytes=250000):
    """Candidate, opt-in self-only transport; no caller is wired in Production.

    The durable claim is written before the first send. Unknown/partial outcomes
    require review; they never trigger a retry or unconditional Race resend.
    Provider acceptance is not Inbox arrival or a human acknowledgement.
    """
    import hashlib
    import re
    from email.message import EmailMessage
    from email.policy import SMTP
    from email.utils import format_datetime
    a = _self_delivery_authorization(authorization)
    if transport is None: raise ValueError('JRA_DELIVERY_PRIVATE_TRANSPORT_REQUIRED')
    root, store = Path(root).resolve(), Path(private_store).resolve()
    if store == root or root in store.parents:
        raise ValueError('JRA_DELIVERY_PRIVATE_STORE_OUTSIDE_REPOSITORY_REQUIRED')
    plan = _complete_delivery_plan(final, presentation_dir, root, part_bytes)
    if a.get('authority') != plan['authority']:
        raise ValueError('JRA_DELIVERY_OWNER_AUTHORITY_MISMATCH')
    clock = now or (lambda: datetime.now(timezone.utc))
    cutoff = _delivery_time(plan['prediction_cutoff'])
    key = hashlib.sha256((plan['race_id']+'\0'+a['account_sub']).encode()).hexdigest()
    store.mkdir(mode=0o700, parents=True, exist_ok=True)
    if store.stat().st_mode & 0o077:
        raise ValueError('JRA_DELIVERY_PRIVATE_STORE_PERMISSIONS_REQUIRED')
    claim, receipt_path = store/(key+'.claim.json'), store/(key+'.receipt.json')
    if claim.is_symlink() or receipt_path.is_symlink():
        raise ValueError('JRA_DELIVERY_PRIVATE_RECEIPT_SYMLINK')
    if claim.exists():
        previous = json.loads(claim.read_text())
        if previous != {k:plan[k] for k in ('race_id','final_sha256','source_sha256','body_sha256')}:
            raise ValueError('JRA_DELIVERY_IMMUTABLE_CLAIM_CONFLICT')
        if receipt_path.exists():
            prior = json.loads(receipt_path.read_text())
            if (prior.get('sha256') == _sha({k:v for k,v in prior.items() if k!='sha256'})
                    and all(prior.get(k)==plan[k] for k in ('race_id','final_sha256','source_sha256','body_sha256'))
                    and prior.get('account_sub_sha256')==hashlib.sha256(a['account_sub'].encode()).hexdigest()
                    and prior.get('destination_sha256')==hashlib.sha256(a['account_email'].casefold().encode()).hexdigest()
                    and prior.get('part_bytes')==part_bytes
                    and prior.get('NOTIFICATION_SENT') is True):
                return prior
        raise ValueError('JRA_DELIVERY_PRIOR_ATTEMPT_REVIEW_REQUIRED')
    if _delivery_time(clock()) >= cutoff: raise ValueError('JRA_DELIVERY_CUTOFF_EXPIRED')
    _self_delivery_identity(transport, a)
    if _delivery_time(clock()) >= cutoff: raise ValueError('JRA_DELIVERY_CUTOFF_EXPIRED')
    try:
        import os
        fd=os.open(claim,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w',encoding='utf-8') as stream:
            json.dump({k:plan[k] for k in ('race_id','final_sha256','source_sha256','body_sha256')}, stream)
            stream.flush(); __import__('os').fsync(stream.fileno())
    except FileExistsError:
        raise ValueError('JRA_DELIVERY_PRIOR_ATTEMPT_REVIEW_REQUIRED') from None
    record = {k:plan[k] for k in ('race_id','final_sha256','source_sha256','body_sha256','prediction_cutoff')}
    record.update(profile='KM-JRA-OWNER-SELF-DELIVERY-CANDIDATE-v1', private_only=True,
        actor='GMAIL_SELF', owner_approval_ref=a['owner_approval_ref'], actor_code_sha256=a['actor_code_sha256'],
        account_sub_sha256=hashlib.sha256(a['account_sub'].encode()).hexdigest(),
        destination_sha256=hashlib.sha256(a['account_email'].casefold().encode()).hexdigest(),
        part_bytes=part_bytes, part_count=len(plan['chunks']), parts=[], NOTIFICATION_SENT=False,
        execution_origin='UNWIRED_OWNER_SELF_DELIVERY_CANDIDATE', autonomous_completion_claim=False,
        DESTINATION_ARRIVAL_CONFIRMED=None, USER_ACKNOWLEDGED=None,
        user_delivery_verified=False, user_received_at=None, delivery_state='DELIVERY_UNKNOWN')
    _write_private_delivery(receipt_path, record)
    for number, chunk in enumerate(plan['chunks'], 1):
        if _delivery_time(clock()) >= cutoff:
            record['failure_class']='CUTOFF_EXPIRED';_write_private_delivery(receipt_path,record)
            raise ValueError('JRA_DELIVERY_CUTOFF_EXPIRED')
        message=EmailMessage(policy=SMTP)
        message['To']=message['From']=a['account_email']
        message['Subject']=f"KeibaMetrics {plan['race_id']} [{number}/{len(plan['chunks'])}]"
        message['Date']=format_datetime(_delivery_time(clock()))
        for field,value in (('Final',plan['final_sha256']),('Source',plan['source_sha256']),
                            ('Body',plan['body_sha256'])):
            message['X-KeibaMetrics-'+field+'-SHA256']=value
        message['X-KeibaMetrics-Part']=f"{number}/{len(plan['chunks'])}"
        message.set_content(chunk, charset='utf-8')
        message.add_attachment(chunk.encode(),maintype='text',subtype='plain',
            filename=f"{plan['race_id']}-{number}-of-{len(plan['chunks'])}.txt")
        raw=message.as_bytes()
        part={'number':number,'sha256':hashlib.sha256(chunk.encode()).hexdigest(),
              'mime_sha256':hashlib.sha256(raw).hexdigest(),'attempted_at':_delivery_time(clock()).isoformat(),
              'provider_message_id':None, 'accepted':False}
        record['parts'].append(part);_write_private_delivery(receipt_path,record)
        try:
            response=transport.send(raw)
            identifier=response.get('id')
            if (not isinstance(identifier,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}',identifier)
                    or any(p.get('provider_message_id')==identifier for p in record['parts'][:-1])):
                raise ValueError('INVALID_PROVIDER_ACCEPTANCE')
        except Exception as exc:
            record['failure_class']='UNKNOWN_SEND_OUTCOME:'+type(exc).__name__
            _write_private_delivery(receipt_path,record)
            raise ValueError('JRA_DELIVERY_SEND_OUTCOME_UNKNOWN_NO_RETRY') from None
        part.update(provider_message_id=identifier, provider_date=response.get('provider_date'),
                    accepted=True, observed_at=_delivery_time(clock()).isoformat())
        _write_private_delivery(receipt_path,record)
    record['NOTIFICATION_SENT']=True
    record['send_observed_before_cutoff']=all(_delivery_time(p['observed_at'])<cutoff for p in record['parts'])
    _write_private_delivery(receipt_path,record)
    return record


def verify_self_mail_arrival(final, *, presentation_dir, root, private_store,
                             authorization=None, transport=None, part_bytes=250000, now=None):
    """Inbox/MIME readback only; this never sends or marks a human ACK."""
    import hashlib
    import re
    from email import policy
    from email.parser import BytesParser
    from email.utils import parsedate_to_datetime
    a=_self_delivery_authorization(authorization)
    if a.get('readback_authorized') is not True or transport is None:
        raise ValueError('JRA_DELIVERY_OWNER_INBOX_READBACK_REQUIRED')
    root,store=Path(root).resolve(),Path(private_store).resolve()
    if store == root or root in store.parents:
        raise ValueError('JRA_DELIVERY_PRIVATE_STORE_OUTSIDE_REPOSITORY_REQUIRED')
    plan=_complete_delivery_plan(final,presentation_dir,root,part_bytes)
    if a.get('authority')!=plan['authority']:
        raise ValueError('JRA_DELIVERY_OWNER_AUTHORITY_MISMATCH')
    key=hashlib.sha256((plan['race_id']+'\0'+a['account_sub']).encode()).hexdigest()
    path=store/(key+'.receipt.json')
    if path.is_symlink(): raise ValueError('JRA_DELIVERY_PRIVATE_RECEIPT_SYMLINK')
    record=json.loads(path.read_text())
    if (record.get('sha256')!=_sha({k:v for k,v in record.items() if k!='sha256'})
            or any(record.get(k)!=plan[k] for k in ('race_id','final_sha256','source_sha256','body_sha256'))
            or record.get('NOTIFICATION_SENT') is not True
            or record.get('account_sub_sha256')!=hashlib.sha256(a['account_sub'].encode()).hexdigest()
            or record.get('destination_sha256')!=hashlib.sha256(a['account_email'].casefold().encode()).hexdigest()
            or record.get('part_bytes')!=part_bytes
            or record.get('part_count')!=len(plan['chunks'])
            or len(record.get('parts') or [])!=len(plan['chunks'])):
        raise ValueError('JRA_DELIVERY_RECEIPT_OR_PART_SET_INVALID')
    _self_delivery_identity(transport,a)
    clock=now or (lambda:datetime.now(timezone.utc))
    received=[];observations=[];provider_observations=[];identifiers=set()
    for number,(part,chunk) in enumerate(zip(record['parts'],plan['chunks']),1):
        identifier=part.get('provider_message_id')
        if not identifier or identifier in identifiers or part.get('number')!=number or part.get('accepted') is not True:
            raise ValueError('JRA_DELIVERY_RECEIPT_OR_PART_SET_INVALID')
        identifiers.add(identifier);data=transport.received(identifier)
        observations.append(_delivery_time(clock()))
        try:
            provider_observations.append(_delivery_time(parsedate_to_datetime(data.get('_provider_readback_date'))))
        except (TypeError,ValueError,AttributeError):
            provider_observations.append(None)
        if data.get('id')!=identifier or 'INBOX' not in data.get('labelIds',[]):
            raise ValueError('JRA_DELIVERY_DESTINATION_NOT_OBSERVED')
        raw=base64.urlsafe_b64decode(data['raw']+'='*(-len(data['raw'])%4))
        message=BytesParser(policy=policy.default).parsebytes(raw)
        if (len(message.get_all('To',[]))!=1 or len(message.get_all('From',[]))!=1
                or str(message['To']).casefold()!=a['account_email'].casefold()
                or str(message['From']).casefold()!=a['account_email'].casefold()
                or message.get_all('Cc') or message.get_all('Bcc')
                or message.get_all('X-KeibaMetrics-Part')!=[f"{number}/{len(plan['chunks'])}"]):
            raise ValueError('JRA_DELIVERY_RECEIVED_DESTINATION_OR_PART_INVALID')
        for field,value in (('Final',plan['final_sha256']),('Source',plan['source_sha256']),('Body',plan['body_sha256'])):
            headers=message.get_all('X-KeibaMetrics-'+field+'-SHA256',[])
            actual=str(headers[0]).strip() if len(headers)==1 else ''
            if not re.fullmatch(r'[0-9a-f]{64}',actual) or actual!=value:
                raise ValueError('JRA_DELIVERY_RECEIVED_SOURCE_BINDING_INVALID')
        attachments=list(message.iter_attachments())
        if len(attachments)!=1 or attachments[0].get_payload(decode=True)!=chunk.encode():
            raise ValueError('JRA_DELIVERY_RECEIVED_BODY_INCOMPLETE')
        stamp=data.get('internalDate')
        if not isinstance(stamp,str) or not stamp.isascii() or not stamp.isdigit():
            raise ValueError('JRA_DELIVERY_RECEIVED_TIMESTAMP_INVALID')
        observed=datetime.fromtimestamp(int(stamp)/1000,timezone.utc)
        if observed<_delivery_time(final['final_receipt']['receipt']['timestamp']):
            raise ValueError('JRA_DELIVERY_RECEIVED_TIMESTAMP_INVALID')
        received.append(observed)
    cutoff=_delivery_time(plan['prediction_cutoff'])
    timing_proven=(all(t is not None for t in provider_observations)
                   and all(t<cutoff for t in received+observations+provider_observations))
    record.update(DESTINATION_ARRIVAL_CONFIRMED=True,user_delivery_verified=True,
                  user_received_at=None,
                  provider_message_internal_dates=[t.isoformat() for t in received],
                  arrival_readback_observed_at=max(observations).isoformat(),
                  provider_readback_dates=[t.isoformat() if t else None for t in provider_observations],
                  delivery_deadline_evidence_complete=all(t is not None for t in provider_observations),
                  delivered_before_cutoff=timing_proven,
                  verified_body_sha256=plan['body_sha256'])
    _write_private_delivery(path,record)
    return record


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--final',required=True);p.add_argument('--output-dir',required=True)
    p.add_argument('--run-url',required=True);p.add_argument('--published-ref')
    p.add_argument('--readback-only',action='store_true',help='Render an existing Signed FINAL with archived verification material; no live Health or publication.')
    p.add_argument('--expected-race-id');p.add_argument('--expected-final-sha256');p.add_argument('--expected-authority')
    display=p.add_mutually_exclusive_group()
    display.add_argument('--complete-body',dest='complete_body',action='store_true',help='Output verified Full20, roles, exact tickets and evidence (default).')
    display.add_argument('--compact-body',dest='complete_body',action='store_false',help='Output the original compact saved text unchanged.')
    p.set_defaults(complete_body=True)
    a=p.parse_args()
    if a.readback_only and a.published_ref:
        p.error('--readback-only cannot publish availability')
    final=json.loads(Path(a.final).read_text())
    out=Path(a.output_dir)
    from jra_presentation import build_presentation, save_presentation, read_presentation, complete_body
    if (out/'presentation.json').exists() and not a.published_ref:
        # A completed answer is recovered before any current Health or SOURCE
        # call. Recheck original signatures with the historical trusted key.
        bundle=read_presentation(out,final=final,expected_race_id=a.expected_race_id,
            expected_final_sha256=a.expected_final_sha256,expected_authority=a.expected_authority)
        print(complete_body(bundle,final) if a.complete_body else bundle['text'],end='')
        sys.exit(0)
    if a.readback_only:
        from jra_presentation import archived_trust
        health,contract=archived_trust(final)
        bundle=save_presentation(out,build_presentation(final,health=health,contract=contract,
            generated_at=datetime.now(timezone.utc).isoformat(),expected_race_id=a.expected_race_id,
            expected_final_sha256=a.expected_final_sha256,expected_authority=a.expected_authority))
        print(complete_body(bundle,final) if a.complete_body else bundle['text'],end='')
        sys.exit(0)
    from family_authority_guard import resolve_current_authority
    root=Path(__file__).resolve().parents[1]
    _,authority=resolve_current_authority(root=root,now=datetime.now(timezone.utc))
    contracts=json.loads((root/authority['common_family_components']['family_runtime_contracts_profile']).read_text())
    contract=contracts['families']['JRA']
    with urllib.request.urlopen(contract['external_endpoint'].rstrip('/')+'/health',timeout=20) as response:
        health=json.load(response)
    out.mkdir(parents=True,exist_ok=True)
    # Never modify the FINAL or old publication receipt. A separate derivative
    # survives response interruption and can be read without multi-MB SOURCE.
    bundle=save_presentation(out,build_presentation(final,health=health,contract=contract,
        generated_at=datetime.now(timezone.utc).isoformat(),expected_race_id=a.expected_race_id,
        expected_final_sha256=a.expected_final_sha256,expected_authority=a.expected_authority))
    record,tree=build_publication(final,health=health,contract=contract,
                                 published_at=datetime.now(timezone.utc).isoformat(),run_url=a.run_url)
    # Existing publication is read back, not re-timestamped as a fresh delivery.
    path=out/'publication.json'
    if path.exists():
        old=json.loads(path.read_text())
        if old.get('sha256')!=_sha({k:v for k,v in old.items() if k!='sha256'}):
            raise ValueError('JRA_DELIVERY_PUBLICATION_HASH_INVALID')
        if ((out/'canonical_tree.txt').read_text()!=tree or
                old.get('final_sha256')!=record['final_sha256'] or old.get('tree_sha256')!=record['tree_sha256']):
            raise ValueError('JRA_DELIVERY_IMMUTABLE_PUBLICATION_CONFLICT')
    else:
        (out/'canonical_tree.txt').write_text(tree)
        path.write_text(json.dumps(record,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    if a.published_ref:
        import re
        if not re.fullmatch(r'[0-9a-f]{40}',a.published_ref):raise ValueError('JRA_DELIVERY_GIT_REF_INVALID')
        if not re.fullmatch(r'KM-JRA-[A-Z]{3}-[0-9]{8}-R[0-9]{2}',final['race_id']):raise ValueError('JRA_DELIVERY_RACE_ID_INVALID')
        base='https://raw.githubusercontent.com/b03la013-max/keibametrics-runtime/'+a.published_ref
        final_url=base+'/runtime/final_artifacts/'+final['race_id']+'.json'
        tree_url=base+'/runtime/jra_delivery/'+final['race_id']+'/canonical_tree.txt'
        with urllib.request.urlopen(final_url,timeout=20) as response:remote=json.load(response)
        verify_signed_final(remote,health,contract)
        if remote['sha256']!=final['sha256']:raise ValueError('JRA_DELIVERY_REMOTE_FINAL_MISMATCH')
        with urllib.request.urlopen(tree_url,timeout=20) as response:remote_tree=response.read()
        if remote_tree!=tree.encode():raise ValueError('JRA_DELIVERY_REMOTE_TREE_MISMATCH')
        observed=datetime.now(timezone.utc)
        receipt={'race_id':final['race_id'],'final_sha256':final['sha256'],
                 'tree_sha256':record['tree_sha256'],'published_ref':a.published_ref,
                 'channel':'GITHUB_CANONICAL','final_url':final_url,'tree_url':tree_url,
                 'availability_verified_at':observed.isoformat(),
                 'availability_verified_before_post':observed<datetime.fromisoformat(final['scheduled_post_at']),
                 'http_status':200,'user_delivery_verified':False,'user_received_at':None}
        receipt['sha256']=_sha(receipt)
        readback=out/'availability_receipt.json'
        if readback.exists():
            old=json.loads(readback.read_text())
            if (old.get('sha256')!=_sha({k:v for k,v in old.items() if k!='sha256'})
                    or old.get('final_sha256')!=final['sha256'] or old.get('tree_sha256')!=record['tree_sha256']):
                raise ValueError('JRA_DELIVERY_AVAILABILITY_RECEIPT_INVALID')
        else:readback.write_text(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
        # Availability is not notification, destination arrival or user ACK.
        presentation_url=base+'/runtime/jra_delivery/'+final['race_id']+'/'
        for name in ('presentation.json','presentation_detail.json','presentation.md'):
            with urllib.request.urlopen(presentation_url+name,timeout=20) as response:
                remote_bytes=response.read()
            if remote_bytes!=(out/name).read_bytes():
                raise ValueError('JRA_PRESENTATION_REMOTE_READBACK_MISMATCH:'+name)
        read_presentation(out,final=final,expected_race_id=final['race_id'],expected_final_sha256=final['sha256'])
        observed=datetime.now(timezone.utc)
        availability={'race_id':final['race_id'],'final_sha256':final['sha256'],
                      'presentation_sha256':bundle['manifest']['sha256'],'published_ref':a.published_ref,
                      'presentation_url':presentation_url+'presentation.md',
                      'availability_verified_at':observed.isoformat(),
                      'availability_verified_before_post':observed<datetime.fromisoformat(final['scheduled_post_at']),
                      'FINAL_VERIFIED':True,'RENDER_READY':True,'CANONICAL_AVAILABLE':True,
                      'NOTIFICATION_SENT':None,'DESTINATION_ARRIVAL_CONFIRMED':None,
                      'USER_ACKNOWLEDGED':None,'delivery_state':'DELIVERY_UNKNOWN',
                      'user_delivery_verified':False,'user_received_at':None}
        availability['sha256']=_sha(availability)
        target=out/'presentation_availability.json'
        if target.exists():
            old=json.loads(target.read_text())
            if (old.get('sha256')!=_sha({k:v for k,v in old.items() if k!='sha256'})
                    or old.get('presentation_sha256')!=bundle['manifest']['sha256']):
                raise ValueError('JRA_PRESENTATION_AVAILABILITY_CONFLICT')
        else:target.write_text(json.dumps(availability,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(complete_body(bundle,final) if a.complete_body else bundle['text'],end='')

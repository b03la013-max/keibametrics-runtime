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


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--final',required=True);p.add_argument('--output-dir',required=True)
    p.add_argument('--run-url',required=True);p.add_argument('--published-ref')
    p.add_argument('--readback-only',action='store_true',help='Render an existing Signed FINAL with archived verification material; no live Health or publication.')
    p.add_argument('--expected-race-id');p.add_argument('--expected-final-sha256');p.add_argument('--expected-authority')
    a=p.parse_args()
    if a.readback_only and a.published_ref:
        p.error('--readback-only cannot publish availability')
    final=json.loads(Path(a.final).read_text())
    out=Path(a.output_dir)
    from jra_presentation import build_presentation, save_presentation, read_presentation
    if (out/'presentation.json').exists() and not a.published_ref:
        # A completed answer is recovered before any current Health or SOURCE
        # call. Recheck original signatures with the historical trusted key.
        bundle=read_presentation(out,final=final,expected_race_id=a.expected_race_id,
            expected_final_sha256=a.expected_final_sha256,expected_authority=a.expected_authority)
        print(bundle['text'],end='')
        sys.exit(0)
    if a.readback_only:
        from jra_presentation import archived_trust
        health,contract=archived_trust(final)
        bundle=save_presentation(out,build_presentation(final,health=health,contract=contract,
            generated_at=datetime.now(timezone.utc).isoformat(),expected_race_id=a.expected_race_id,
            expected_final_sha256=a.expected_final_sha256,expected_authority=a.expected_authority))
        print(bundle['text'],end='')
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
    print(bundle['text'],end='')

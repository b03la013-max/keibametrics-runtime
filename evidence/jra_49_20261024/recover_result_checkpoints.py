"""Execute authorized JRA evidence recovery from provider-owned original ZIPs.

No prediction, SOURCE, FINAL, old RESULT or old Learning bytes are overwritten.
Missing Learning bodies receive new recovery IDs and the real creation clock.
"""
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import zipfile

PINNED_KEY='UhjfD9zFt+e77/9JUB19R6/XFC3SG4pM5twHBqfUSzI='

def read(path):
    return json.loads(path.read_text())

def sha(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()

def write_new(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if path.read_bytes()!=data:raise ValueError('EXISTING_ORIGINAL_CONFLICT:'+str(path))
        return
    with path.open('xb') as stream:stream.write(data)

def encode(value):
    return (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()

def prepare_one(observation, source_root, archive_root):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from post_result_learning import build_post_result_review
    from jra_delivery import verify_signed_final
    from family_authority_guard import resolve_current_authority
    run=observation['run'];artifact=observation['artifact'];run_id=run['id']
    archive=archive_root/(str(run_id)+'.zip');raw=archive.read_bytes()
    assert artifact['digest']=='sha256:'+hashlib.sha256(raw).hexdigest(), 'PROVIDER_ARCHIVE_DIGEST_MISMATCH'
    assert artifact['expired'] is False and artifact['workflow_run']['id']==run_id
    assert artifact['workflow_run']['head_sha']==run['head_sha']
    assert run['repository']['full_name']==run['head_repository']['full_name']=='b03la013-max/keibametrics-runtime'
    assert run['head_branch']=='main' and run['path']=='.github/workflows/km-formal-result-runner.yml'
    assert artifact['name']==f'verified-result-checkpoint-{run_id}-{run["run_attempt"]}'
    with zipfile.ZipFile(archive) as z:
        expected={'result_request.json','result_receipt_envelope.json','result_summary.json'}
        names=z.namelist();assert len(names)==3 and set(names)==expected,'CHECKPOINT_MEMBER_AMBIGUOUS'
        blobs={name:z.read(name) for name in expected}
    payload=json.loads(blobs['result_request.json']);envelope=json.loads(blobs['result_receipt_envelope.json']);summary=json.loads(blobs['result_summary.json'])
    rid=payload['race_id'];assert rid.startswith('KM-JRA-') and '-20261024-' in rid
    assert payload['result_lane']=='PRODUCTION' and summary['status']=='RESULT_E2E_PASS' and summary['verified'] is True
    assert summary['race_id']==rid
    receipt=envelope['receipt'];assert receipt['race_id']==rid and receipt['phase']=='RESULT' and receipt['status']=='PASS' and receipt['errors']==[]
    assert envelope['signer_key_id']=='KM-RUNTIME-ED25519-20260917' and envelope['signature_alg']=='Ed25519'
    assert sha(receipt)==envelope['receipt_sha256']==summary['receipt_sha256']
    assert sha(payload)==receipt['artifact_sha256']==summary['artifact_sha256']
    key=Ed25519PublicKey.from_public_bytes(base64.b64decode(PINNED_KEY));key.verify(base64.b64decode(envelope['signature']),canonical(receipt))
    verification={'valid':True,'method':'OFFLINE_ED25519_PINNED_PUBLIC_KEY_AND_INDEPENDENT_PROVIDER_ARCHIVE',
                  'current_external_verify':'NOT_EXECUTED_AUTO_REVIEW_REJECTED',
                  'original_workflow_verified_result':summary['verified']}
    assert payload==read(source_root/'runtime/results'/(rid+'.json')), 'CANONICAL_RESULT_REQUEST_CHANGED'
    final=read(source_root/'runtime/final_artifacts'/(rid+'.json'))
    assert final['sha256']==payload['frozen_prediction_ref']['immutable_final_sha256']
    assert final['final_receipt_sha256']==payload['frozen_prediction_ref']['final_receipt_sha256']
    _,authority=resolve_current_authority(root=source_root)
    contract=read(source_root/authority['common_family_components']['family_runtime_contracts_profile'])['families']['JRA']
    health={'status':'READY','receipt_signer':{'ready':True,'key_id':'KM-RUNTIME-ED25519-20260917','public_key_b64':PINNED_KEY},'engine':{'sha256':contract['engine_sha256']},'parameter_map':{'sha256':contract['parameter_map_sha256']}}
    verify_signed_final(final,health,contract)
    review=build_post_result_review(payload,final)
    assert review['sha256']==summary['automatic_review_sha256'], 'ORIGINAL_REVIEW_NOT_DETERMINISTICALLY_REPRODUCED'
    return {'race_id':rid,'run':run,'artifact':artifact,'blobs':blobs,'payload':payload,'envelope':envelope,'summary':summary,'review':review,'verification':verification}

def persist_one(item, source_root, destination):
    from execution_store import persist_phase,require_public_storage
    from post_result_learning import build_learning_state
    rid=item['race_id'];run=item['run'];run_id=run['id'];summary=item['summary']
    stage=destination/'recovery-staging'/str(run_id)
    if (stage/'recovery_record.json').exists():
        previous=read(stage/'recovery_record.json')
        assert previous['sha256']==sha({k:v for k,v in previous.items() if k!='sha256'})
        assert previous['result_receipt_sha256']==item['envelope']['receipt_sha256']
        for name,data in item['blobs'].items():assert (stage/name).read_bytes()==data
        expected_review=encode(item['review'])
        write_new(stage/'reproduced_review.json',expected_review)
        canonical_review=source_root/'runtime/reviews_auto'/(rid+'-AUTO.json')
        if canonical_review.exists():assert read(canonical_review)==item['review']
        else:write_new(destination/'runtime/reviews_auto'/(rid+'-AUTO.json'),expected_review)
        expected_state=previous.get('new_learning_state_sha256')
        if expected_state:
            stage_state=stage/'fresh_recovery_learning_state.json'
            canonical_state=destination/'runtime/learning_states'/(rid+'.json')
            original_state=source_root/'runtime/learning_states'/(rid+'.json')
            candidates=[p for p in (stage_state,canonical_state,original_state) if p.exists()]
            assert candidates,'RECOVERY_LEARNING_BYTES_MISSING_CANNOT_RECREATE_OLD_CLOCK'
            state=read(candidates[0])
            assert state['sha256']==expected_state==sha({k:v for k,v in state.items() if k!='sha256'})
            for candidate in candidates:assert read(candidate)==state,'RECOVERY_LEARNING_REPLACEMENT_CONFLICT'
            write_new(stage_state,encode(state))
            if not original_state.exists():write_new(canonical_state,encode(state))
        stored=persist_phase(rid+'-LIVE-R1','RESULT','original-recovery-'+str(run_id),stage,root=destination/'runtime/executions',github_sha=run['head_sha'])
        return {**previous,'phase_manifest_sha256':stored['manifest']['manifest_sha256']}
    # Existing canonical states have their own immutable lineage; recovery never replaces them.
    existing_state=source_root/'runtime/learning_states'/(rid+'.json')
    existing_dest=destination/'runtime/learning_states'/(rid+'.json')
    recovery_state=None
    if existing_state.exists():
        recovery_state=read(existing_state);assert recovery_state['sha256']==sha({k:v for k,v in recovery_state.items() if k!='sha256'})
        assert recovery_state['race_id']==rid and recovery_state['source_review_sha256']==item['review']['sha256']
        state_class='EXISTING_CANONICAL_STATE_UNCHANGED'
    elif existing_dest.exists():
        recovery_state=read(existing_dest);assert recovery_state['sha256']==sha({k:v for k,v in recovery_state.items() if k!='sha256'})
        assert recovery_state['state_id']==rid+'-LEARNING-RECOVERY-'+str(run_id)
        assert recovery_state['race_id']==rid and recovery_state['source_review_sha256']==item['review']['sha256']
        assert recovery_state['recovery_lineage']=={'source_result_receipt_sha256':item['envelope']['receipt_sha256'],'source_workflow_run_id':run_id,'original_unrecovered_learning_sha256':summary['learning_state_sha256'],'original_learning_bytes_recovered':False,'creation_class':'NEW_POSTRESULT_STATE_AT_REAL_RECOVERY_TIME','retroactive_consumption_credit':0}
        created=datetime.fromisoformat(recovery_state['effective_time'].replace('Z','+00:00'))
        archived=datetime.fromisoformat(item['artifact']['created_at'].replace('Z','+00:00'))
        assert archived < created <= datetime.now(timezone.utc),'RECOVERY_EFFECTIVE_TIME_OUTSIDE_REAL_CREATION_INTERVAL'
        state_class='NEW_RECOVERY_STATE_REAL_TIME_NOT_ORIGINAL_STATE'
    elif rid=='KM-JRA-KYO-20261024-R07':
        state_class='REFUND_CORRECTION_PENDING_NO_NEW_ADMITTED_STATE'
    else:
        now=datetime.now(timezone.utc).isoformat()
        recovery_state=build_learning_state(item['review'],effective_time=now)
        recovery_state['state_id']=rid+'-LEARNING-RECOVERY-'+str(run_id)
        recovery_state['recovery_lineage']={'source_result_receipt_sha256':item['envelope']['receipt_sha256'],'source_workflow_run_id':run_id,'original_unrecovered_learning_sha256':summary['learning_state_sha256'],'original_learning_bytes_recovered':False,'creation_class':'NEW_POSTRESULT_STATE_AT_REAL_RECOVERY_TIME','retroactive_consumption_credit':0}
        recovery_state['sha256']=sha({k:v for k,v in recovery_state.items() if k!='sha256'})
        require_public_storage(recovery_state);write_new(existing_dest,encode(recovery_state))
        state_class='NEW_RECOVERY_STATE_REAL_TIME_NOT_ORIGINAL_STATE'
    review_path=destination/'runtime/reviews_auto'/(rid+'-AUTO.json')
    main_review=source_root/'runtime/reviews_auto'/(rid+'-AUTO.json')
    if main_review.exists():assert read(main_review)==item['review'],'CANONICAL_REVIEW_CONFLICT'
    else:write_new(review_path,encode(item['review']))
    for name,data in item['blobs'].items():write_new(stage/name,data)
    # Original provider archive clock authenticates old receipts, never this new state clock.
    recovery={'race_id':rid,'operation':'RECOVER_VERIFIED_ORIGINAL_RESULT_WITHOUT_RESIGNING','original_workflow_run_id':run_id,'original_workflow_head_sha':run['head_sha'],'provider_artifact_id':item['artifact']['id'],'provider_archive_digest':item['artifact']['digest'],'provider_server_created_at':item['artifact']['created_at'],'result_receipt_sha256':item['envelope']['receipt_sha256'],'result_signature_verified_offline':True,'result_verification':item['verification'],'review_sha256':item['review']['sha256'],'review_matches_original_summary':True,'original_learning_sha256':summary['learning_state_sha256'],'original_learning_bytes_recovered':False,'learning_recovery_class':state_class,'new_learning_state_id':recovery_state.get('state_id') if recovery_state else None,'new_learning_state_sha256':recovery_state.get('sha256') if recovery_state else None,'new_learning_effective_time':recovery_state.get('effective_time') if recovery_state else None,'new_prediction_run':False,'new_result_signature':False,'old_artifacts_overwritten':False,'live_next_race_consumption_credit':0}
    recovery['sha256']=sha(recovery)
    if recovery_state:write_new(stage/'fresh_recovery_learning_state.json',encode(recovery_state))
    write_new(stage/'reproduced_review.json',encode(item['review']))
    # This final marker is written only after both canonical and staged bodies exist.
    write_new(stage/'recovery_record.json',encode(recovery))
    stored=persist_phase(rid+'-LIVE-R1','RESULT','original-recovery-'+str(run_id),stage,root=destination/'runtime/executions',github_sha=run['head_sha'])
    return {**recovery,'phase_manifest_sha256':stored['manifest']['manifest_sha256']}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-root',type=Path,required=True);ap.add_argument('--archives',type=Path,required=True);ap.add_argument('--destination',type=Path,required=True);ap.add_argument('--execute',action='store_true');args=ap.parse_args()
    sys.path[:0]=[str(args.source_root/'runtime'),str(args.source_root/'runtime/jra_source_runtime')]
    observations=read(args.archives/'provider_observations.json')
    with ThreadPoolExecutor(max_workers=4) as pool:items=list(pool.map(lambda x:prepare_one(x,args.source_root,args.archives),observations))
    assert len(items)==20 and len({x['race_id'] for x in items})==20
    if not args.execute:
        print(json.dumps({'status':'ALL_ORIGINALS_VERIFIED_READY_FOR_EVIDENCE_RECOVERY','race_count':len(items),'review_sha_match':len(items),'no_result_reissue':True,'races':[x['race_id'] for x in items]},ensure_ascii=False));return
    records=[persist_one(item,args.source_root,args.destination) for item in items]
    out={'profile':'JRA-20261024-ORIGINAL-RESULT-RECOVERY','observed_at':datetime.now(timezone.utc).isoformat(),'verified_original_result_count':len(records),'fresh_learning_state_count':sum(x['new_learning_state_id'] is not None for x in records),'refund_correction_pending':['KM-JRA-KYO-20261024-R07'],'prediction_reexecution_count':0,'result_resigning_count':0,'live_learning_consumption_credit':0,'records':records}
    report_path=args.destination/'evidence/jra_49_20261024/result_original_recovery.json'
    if report_path.exists():
        previous=read(report_path);assert previous['records']==records
        assert previous['sha256']==sha({k:v for k,v in previous.items() if k!='sha256'})
        out=previous
    else:
        out['sha256']=sha(out);write_new(report_path,encode(out))
    print(json.dumps({k:v for k,v in out.items() if k!='records'},ensure_ascii=False))

if __name__=='__main__':main()

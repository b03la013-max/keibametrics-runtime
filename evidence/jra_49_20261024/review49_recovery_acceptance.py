"""Independent network-free read-only audit of the completed recovery batch."""
from pathlib import Path
import base64
from datetime import datetime, timezone
import hashlib
import json
import zipfile
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

root = Path('/workspace/scratch/c3703925e24c')
dest = root/'result-recovery-data'
arc = root/'result-recovery-checkpoints'


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(',', ':')).encode()).hexdigest()


def read(path):
    return json.loads(path.read_text())


observations = read(arc/'provider_observations.json')
report = read(dest/'evidence/jra_49_20261024/result_original_recovery.json')
assert report['sha256'] == sha({k:v for k,v in report.items() if k != 'sha256'})
now = datetime.now(timezone.utc)
rows = []
for observation in observations:
    run = observation['run']; run_id = run['id']; artifact = observation['artifact']
    archive = arc/(str(run_id)+'.zip')
    assert artifact['digest'] == 'sha256:'+hashlib.sha256(archive.read_bytes()).hexdigest()
    with zipfile.ZipFile(archive) as z:
        blobs = {name:z.read(name) for name in z.namelist()}
    payload = json.loads(blobs['result_request.json'])
    envelope = json.loads(blobs['result_receipt_envelope.json'])
    summary = json.loads(blobs['result_summary.json']); rid = payload['race_id']
    receipt = envelope['receipt']
    assert sha(receipt) == envelope['receipt_sha256']
    assert sha(payload) == receipt['artifact_sha256']
    Ed25519PublicKey.from_public_bytes(base64.b64decode(
        'UhjfD9zFt+e77/9JUB19R6/XFC3SG4pM5twHBqfUSzI=')).verify(
        base64.b64decode(envelope['signature']), json.dumps(receipt,
            ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())
    phase = dest/'runtime/executions'/(rid+'-LIVE-R1')/'RESULT/runs'/('original-recovery-'+str(run_id))
    manifest = read(phase/'manifest.json')
    original_manifest_bytes = json.dumps({k:v for k,v in manifest.items() if k != 'manifest_sha256'},
        ensure_ascii=False, sort_keys=True, indent=2).encode()
    assert manifest['manifest_sha256'] == hashlib.sha256(original_manifest_bytes).hexdigest()
    for name, body in blobs.items():
        assert (phase/name).read_bytes() == body
    for name, metadata in manifest['files'].items():
        body = (phase/name).read_bytes()
        assert hashlib.sha256(body).hexdigest() == metadata['sha256']
        assert len(body) == metadata['bytes']
    recovery = read(phase/'recovery_record.json')
    assert recovery['sha256'] == sha({k:v for k,v in recovery.items() if k != 'sha256'})
    assert recovery['result_receipt_sha256'] == envelope['receipt_sha256']
    assert recovery['result_verification']['current_external_verify'] == 'NOT_EXECUTED_AUTO_REVIEW_REJECTED'
    review = read(phase/'reproduced_review.json')
    assert review['sha256'] == sha({k:v for k,v in review.items() if k != 'sha256'}) == summary['automatic_review_sha256']
    assert read(dest/'runtime/reviews_auto'/(rid+'-AUTO.json')) == review
    state_path = dest/'runtime/learning_states'/(rid+'.json')
    if rid == 'KM-JRA-KYO-20261024-R07':
        assert not state_path.exists() and recovery['new_learning_state_sha256'] is None
    else:
        state = read(state_path)
        assert read(phase/'fresh_recovery_learning_state.json') == state
        assert state['sha256'] == sha({k:v for k,v in state.items() if k != 'sha256'}) == recovery['new_learning_state_sha256']
        assert state['state_id'] == rid+'-LEARNING-RECOVERY-'+str(run_id)
        assert state['race_id'] == rid and state['source_review_sha256'] == review['sha256']
        lineage = state['recovery_lineage']
        assert lineage['source_result_receipt_sha256'] == envelope['receipt_sha256']
        assert lineage['source_workflow_run_id'] == run_id
        assert lineage['original_unrecovered_learning_sha256'] == summary['learning_state_sha256'] != state['sha256']
        assert lineage['retroactive_consumption_credit'] == 0 and state['production_change_authorized'] is False
        effective = datetime.fromisoformat(state['effective_time'])
        assert datetime.fromisoformat(artifact['created_at'].replace('Z','+00:00')) < effective <= now
    rows.append({'race_id':rid, 'original_run_id':run_id, 'original_result_exact_bytes':True,
        'offline_ed25519_verified':True, 'phase_file_integrity':True, 'original_review_sha_match':True,
        'fresh_state_exists':state_path.exists(), 'next_race_consumption_credit':0})
out = {'reviewed_at':now.isoformat(), 'result_originals_verified':len(rows),
    'new_recovery_state_count':sum(x['fresh_state_exists'] for x in rows), 'network_requests':0,
    'new_result_signatures':0, 'retrospective_learning_consumption_credit':0,
    'refund_correction_pending':['KM-JRA-KYO-20261024-R07'], 'archive_bytes_unchanged':True,
    'records':rows}
out['sha256'] = sha(out)
path = root/'independent_review_49_recovery_acceptance.json'
path.write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k != 'records'}, ensure_ascii=False))

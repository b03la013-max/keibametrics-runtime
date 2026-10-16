"""Read-only audit of the eight named incidents; never calls runtime execution APIs.

Usage: PYTHONPATH=runtime:. python <this-file> <checkout-root> <output-directory>
Outputs are audit evidence only. No canonical execution record is modified.
"""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from runtime.execution_store import resolve_phase
from runtime.family_authority_guard import resolve_current_authority

root, out = map(lambda s: Path(s).resolve(), sys.argv[1:3])
out.mkdir(parents=True, exist_ok=True)
def read(p):
    return json.loads(p.read_text(encoding='utf-8'))
def digest(b):
    return hashlib.sha256(b).hexdigest()
def canonical(o):
    return json.dumps(o, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
def save(name, o):
    (out / name).write_text(json.dumps(o, ensure_ascii=False, indent=2) + '\n')
def git(*args):
    return subprocess.check_output(['git', *args], cwd=root, text=True).strip()

health = read(out / 'runtime_health.json')
assert health['http_status'] == 200 and health['assessment']['status'] == 'PASS'
anchor = health['health']['receipt_public_key_b64']
assert anchor == 'jqWqOYlmhXXmpv/nR7lx3c2n/S5shDYava/WJVxn4kE='
key = Ed25519PublicKey.from_public_bytes(base64.b64decode(anchor))
api = read(out / 'github_observations.json')
runs = {r['id']: r for r in api['success_runs']}
authority_path, authority = resolve_current_authority(root=root)
inventory = {}
rows = []

for day, n, runid, label in [('20261015',8,38711152951,'R08'), ('20261015',10,38720317619,'R10'), ('20261016',1,38855562125,'R01')]:
    eid = f'KM-LOCAL-KAW-{day}-R{n:02d}-LIVE-R1'
    phases, envelopes = {}, {}
    for phase in ('SOURCE', 'FORMAL', 'RESULT'):
        p = resolve_phase(eid, phase, root=root/'runtime/executions')
        assert p is not None
        phases[phase] = {'latest':p['latest'], 'manifest_declared_github_sha':p['manifest']['github_sha'], 'verified_file_count':len(p['manifest']['files'])}
        for name in p['manifest']['files']:
            f=p['run_dir']/name
            inventory[str(f.relative_to(root))] = digest(f.read_bytes())
        for name in ('source_receipt_envelope.json','pre_krs_receipt_envelope.json','krs_receipt_envelope.json','final_receipt_envelope.json','result_receipt_envelope.json'):
            f=p['run_dir']/name
            if not f.exists():
                continue
            e=read(f); rec=e['receipt']; stage=rec['phase']
            assert rec['race_id']==eid
            assert rec['status']=={'SOURCE':'SOURCE_FROZEN','KRS_RUN':'EXECUTED'}.get(stage,'PASS')
            assert digest(canonical(rec))==e['receipt_sha256']
            assert digest(canonical(e['artifact']))==rec['artifact_sha256']
            assert e['signature_alg']=='Ed25519'
            assert e['signer_key_id']==health['health']['receipt_signer_key_id']
            key.verify(base64.b64decode(e['signature']),canonical(rec))
            assert rec['engine_sha256']==health['health']['engine_sha256']
            assert rec['parameter_map_sha256']==health['health']['parameter_map_sha256']
            if stage in envelopes:
                assert envelopes[stage]['receipt_sha256']==e['receipt_sha256']
            envelopes[stage]={**e,'path':str(f.relative_to(root))}
    intent_path=root/'runtime/formal_intents'/f'{eid}.json'
    intent=read(intent_path)
    request_path=root/'runtime/race_key_requests'/f'KAW-{day}-R{n:02d}-LIVE-R1.json'
    fields=read(request_path)
    final, result = envelopes['FINAL'], envelopes['RESULT']
    a=final['artifact']; ticket=a['final_ticket']
    assert result['artifact']['frozen_refs']['final_receipt_sha256']==final['receipt_sha256']
    assert result['artifact']['frozen_refs']['final_ticket_sha256']==digest(canonical(ticket))
    assert datetime.fromisoformat(final['receipt']['timestamp']) < datetime.fromisoformat(fields['prediction_cutoff'])
    assert datetime.fromisoformat(a['final_freeze_timestamp']) < datetime.fromisoformat(fields['scheduled_post_at'])
    assert ticket['total_investment']==sum(t['stake'] for t in ticket['tickets'])
    assert a['source_receipt_sha256']==envelopes['SOURCE']['receipt_sha256']
    assert a['krs_receipt_sha256']==envelopes['KRS_RUN']['receipt_sha256']
    tree=root/'runtime/execution_reports'/eid/'delivery/canonical_tree.txt'
    r=runs[runid]
    rows.append({'race_date':fields['race_date'],'race_no':n,'execution_id':eid,
        'outcome':'SIGNED_FINAL_AND_RESULT_VERIFIED','original_chat_tool_name':None,'original_chat_tool_input':None,
        'original_registration_http_status':None,'http_note':'Commit and Run are observed; raw registration HTTP response was not retained.',
        'race_key_path':str(request_path.relative_to(root)),'registered_fields':fields,
        'registration_commit':r['head_sha'],'registration_commit_timestamp':r['head_commit']['timestamp'],
        'workflow_run_id':runid,'workflow_event':r['event'],'workflow_created_at':r['created_at'],
        'workflow_conclusion':r['conclusion'],'trigger_sha':r['head_sha'],
        'actual_entry_checkout_sha':api['actual_entry_checkout'][label]['checkout_sha'],
        'formal_intent':str(intent_path.relative_to(root)), 'formal_intent_file_sha256':digest(intent_path.read_bytes()),
        'current_authority_in_intent':intent['current_authority_manifest'], 'owner_scope':'LOCAL/KAW',
        'checkpoint_inventory':phases,
        'signed_stages':{stage:{'path':e['path'],'timestamp':e['receipt']['timestamp'],'receipt_status':e['receipt']['status'],
            'runtime_revision_sha':e['receipt']['github_revision'],'receipt_sha256':e['receipt_sha256'],
            'artifact_sha256':e['receipt']['artifact_sha256'],'signature_sha_identity_verification':'PASS'} for stage,e in envelopes.items()},
        'signed_execution_stage_manifest':a['execution_stage_manifest'],
        'final_freeze_at':a['final_freeze_timestamp'],'ticket_count':len(ticket['tickets']),
        'tickets_by_type':dict(Counter(t['bet_type'] for t in ticket['tickets'])),
        'total_investment':ticket['total_investment'],'final_ticket_sha256':digest(canonical(ticket)),
        'settlement':result['artifact']['settlement'], 'result_binding_to_original_final':'PASS',
        'tree_file_sha256':digest(tree.read_bytes()) if tree.exists() else None,
        'chat_emission_evidence':'PR282/evidence/family_audit_20261016/kaw_r01_delivery_observation_1433JST.json' if n==1 and day=='20261016' else None,
        'independent_delivery_receipt':None,'user_received_at':None,'actual_purchase_pfs':'UNKNOWN',
        'autonomous_scheduler_success':False if day=='20261016' else None,
        'first_distinguishing_boundary':'MAIN_RACE_KEY_COMMIT_AND_PUSH_RUN_OBSERVED'})

known_reported = {
 ('20261015',6):{'reported_message_times':['2026-10-15T08:12:38Z','2026-10-15T08:15:55Z'],'reported_post_at':'2026-10-15T17:25:00+09:00'},
 ('20261015',7):{'reported_message_times':['2026-10-15T08:38:48Z']},
 ('20261015',9):{'reported_message_times':['2026-10-15T09:59:03Z'],'reported_post_at':'2026-10-15T19:05:00+09:00','reported_cutoff':'2026-10-15T19:03:00+09:00'},
 ('20261015',11):{'reported_message_times':['2026-10-15T11:07:30Z'],'reported_post_at':'2026-10-15T20:15:00+09:00','reported_cutoff':'2026-10-15T20:13:00+09:00'},
 ('20261016',7):{'reported_message_times':['2026-10-16T08:48:56Z','2026-10-16T08:49:37Z'],'plan_post_at':'2026-10-16T18:00:00+09:00','plan_cutoff':'2026-10-16T17:58:00+09:00'},
}
keys=[]
for p in (root/'runtime/race_key_requests').glob('*.json'):
    keys.append((p,read(p)))
for (day,n),reported in known_reported.items():
    eid=f'KM-LOCAL-KAW-{day}-R{n:02d}-LIVE-R1'; iso=f'{day[:4]}-{day[4:6]}-{day[6:]}'
    refs=[str(p.relative_to(root)) for p,d in keys if d.get('race_date')==iso and str(d.get('race_no'))==str(n) and d.get('venue_id')=='KAW']
    prefix=eid.rsplit('-R1',1)[0]
    refs += [str(p.relative_to(root)) for p in (root/'runtime/formal_intents').glob(prefix+'-R*.json')]
    refs += [str(p.relative_to(root)) for p in (root/'runtime/executions').glob(prefix+'-R*')]
    assert not refs, ('Unexpected record requires reclassification',eid,refs)
    rows.append({'race_date':iso,'race_no':n,'derived_execution_id':eid,'execution_id_observed':False,
        'outcome':'OPERATIONAL_FAILURE_NO_CANONICAL_EXECUTION_OBSERVED_BY_DEADLINE',
        'original_chat_tool_name':None,'original_chat_tool_input':None,'original_tool_error':None,
        'original_registration_http_status':None,'original_registration_request_reached_github':'UNKNOWN',
        'original_attempt_at':None,'registration_commit':None,'workflow_run_id':None,'dispatch_at':None,
        'final_at':None,'delivery_at':None,'original_authority_binding':None,'original_scope_binding':None,
        'original_cutoff':None,'root_cause':'UNDETERMINED_ORIGINAL_TOOL_TRACE_NOT_RETRIEVABLE',
        'raw_safety_rejection_reproduced':False,'claimed_rejection_source':'Prior assistant prose, not raw tool response',
        'reported_context_not_execution_timestamps':reported,'canonical_refs_found':refs,
        'search_scope':'main request payload identity, all same-race intent/execution revisions; Actions API UTC 2026-10-15..16, all 321 returned runs',
        'external_runtime_store_absence_proven':False,
        'first_distinguishing_boundary':'NO_CANONICAL_RACE_KEY_COMMIT_OR_EXECUTION_OBSERVED',
        'repair_state':'NO_CAUSALLY_SUPPORTED_CODE_PATCH; ORIGINAL_CONNECTOR_TRACE_REQUIRED',
        'safe_checkpoint_resume':None,'retroactive_final_authorized':False,'actual_purchase_pfs':'UNKNOWN',
        'new_future_attempt_required':True})

rows.sort(key=lambda r:(r['race_date'],r['race_no']))
save('race_comparison.json',{'observed_at':datetime.now(timezone.utc).isoformat(),
    'main_sha':git('rev-parse','HEAD'),'current_authority':authority['manifest_id'],
    'authority_path':str(authority_path.relative_to(root)),
    'denominator':8,'signed_final_and_result':3,'operational_nonexecution_failures':5,
    'registration_and_signed_final_rate':3/8,'unknown_future_repair_trial_success_rate':'N/A_NOT_ATTEMPTED',
    'independent_delivery_success_rate':None,'signature_count_verified':15,
    'root_cause_closed':False,'all_user_goals_complete':False,'races':rows})
save('protected_file_hashes.json',inventory)
print(json.dumps({'races':len(rows),'verified_receipts':15,'protected_files':len(inventory),'root_cause_closed':False}))

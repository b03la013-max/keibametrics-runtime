"""Read-only audit of canonical historical records; never signs or dispatches."""
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'runtime')]
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from runtime.family_authority_guard import resolve_current_authority
from runtime.jra_ticket_tree_renderer import render_ticket_tree
from runtime.mec_r4_shadow import settle_ticket_list

OUT = Path(__file__).parent
MAIN = '7997b4b860f76e4719a9d5bd65aa442f3bdf9afc'
def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)
def sha(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def write(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
def load(path):
    return json.loads((ROOT / path).read_text())
def ts(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))

health = load(OUT.relative_to(ROOT) / 'runtime_health.json')
assert health['assessment']['status'] == 'PASS'
assert health['health']['receipt_signer_key_id'] == 'KM-LOCAL-RUNTIME-ED25519-20260922'
key = Ed25519PublicKey.from_public_bytes(base64.b64decode(health['health']['receipt_public_key_b64']))
files = git('ls-tree', '-r', '--name-only', MAIN).decode().splitlines()
observations = load(OUT.relative_to(ROOT) / 'github_runtime_observations.json')
runs = {1:38855562125, 2:38859938474, 6:38873003494, 9:38881777914, 12:38895197802}
rows = []
verified = []
for n in range(1, 13):
    eid = f'KM-LOCAL-KAW-20261016-R{n:02}-LIVE-R1'
    related = [p for p in files if eid in p or f'KAW-20261016-R{n:02}-' in p]
    row = {'race_no':n, 'execution_id':eid, 'canonical_main_sha':MAIN, 'discovery':'OBSERVED_IN_OFFICIAL_DAY_PLAN', 'paths':related, 'actual_purchase_pfs':'UNKNOWN'}
    if n not in runs:
        assert not related
        row.update(first_unproven_stage='RACE_KEY_REGISTRATION', actual_failure_origin='UNKNOWN', original_error=None, original_failure_at=None, executor=None, run_id=None, artifact=None, failure_sha=None, registration_refusal_reported=n in (7,10,11), formal_recommendation_pfs=None)
        row['stages'] = {s:'NOT_OBSERVED' for s in ['RaceKey','FormalIntent','SOURCE','Numerical','Static','PRE_KRS','KRS','MEC','Capital','FINAL','Delivery']}
        rows.append(row)
        continue
    run = runs[n]
    formal = Path(f'runtime/executions/{eid}/FORMAL/runs/race-key-{run}-formal')
    resultdir = Path(f'runtime/executions/{eid}/RESULT/runs/race-key-{run}-result')
    envelopes = {}
    for name, phase, folder in [('source','SOURCE',formal), ('pre_krs','PRE_KRS',formal), ('krs','KRS_RUN',formal), ('final','FINAL',formal), ('result','RESULT',resultdir)]:
        path = folder / (name + '_receipt_envelope.json')
        env = load(path)
        rec = env['receipt']
        # Actual phase names are checked explicitly, not inferred from filename.
        expected = {'KRS_RUN','KRS'} if name == 'krs' else {phase}
        expected_status = {'source':'SOURCE_FROZEN','krs':'EXECUTED'}.get(name, 'PASS')
        assert rec['phase'] in expected and rec['race_id'] == eid and rec['status'] == expected_status
        assert env['signer_key_id'] == health['health']['receipt_signer_key_id']
        key.verify(base64.b64decode(env['signature']), json.dumps(rec,ensure_ascii=False,sort_keys=True,separators=(',', ':')).encode())
        assert sha(rec) == env['receipt_sha256'] and sha(env['artifact']) == rec['artifact_sha256']
        assert (ROOT / path).read_bytes() == git('show', MAIN + ':' + str(path))
        verified.append({'path':str(path),'receipt_sha256':env['receipt_sha256'],'artifact_sha256':rec['artifact_sha256']})
        envelopes[name] = env
    final, result = envelopes['final'], envelopes['result']
    assert result['artifact']['frozen_refs']['final_receipt_sha256'] == final['receipt_sha256']
    facts = dict(result['artifact']['official_result']); facts['top3'] = facts['finish_order'][:3]
    settlement = settle_ticket_list(final['artifact']['final_ticket']['tickets'], {'official_result':facts})
    summary = load(resultdir / 'result_summary.json')
    learning = load(resultdir / 'learning_state.json')
    reflection = load(resultdir / 'race_day_fast_reflection.json')
    for k in ['investment','return','profit_loss','pfs']:
        assert abs(settlement[k] - summary[k]) < 0.001
        assert abs(settlement[k] - reflection['settlement'][k]) < 0.001
    assert learning['final_receipt_sha256'] == final['receipt_sha256']
    assert learning['result_receipt_sha256'] == result['receipt_sha256']
    assert reflection['production_change_authorized'] is False
    intent = load(f'runtime/formal_intents/{eid}.json')
    cutoff = ts(intent['prediction_cutoff'])
    assert ts(final['receipt']['timestamp']) < cutoff
    tree = render_ticket_tree(final['artifact'])
    assert tree['total_investment'] == settlement['investment']
    treepath = OUT / f'R{n:02}-canonical-tree.txt'; treepath.write_text(tree['text']+'\n')
    jobs = next(x['jobs'] for x in observations['jobs'] if x['run_id'] == run)
    entry = next(x for x in jobs if x['name'].startswith('entry '))
    row.update(run_id=run, run_event='push', scheduler_success=False, settlement=settlement, reflection_status=reflection['status'], learning_final_bound=True, receipt_count=5, final_at=final['receipt']['timestamp'], cutoff=intent['prediction_cutoff'], final_cutoff_margin_seconds=(cutoff-ts(final['receipt']['timestamp'])).total_seconds(), source_to_final_seconds=(ts(final['receipt']['timestamp'])-ts(envelopes['source']['receipt']['timestamp'])).total_seconds(), entry_start_to_final_seconds=(ts(final['receipt']['timestamp'])-ts(entry['started_at'])).total_seconds(), ticket_count=tree['ticket_count'], tree_sha256=hashlib.sha256((tree['text']+'\n').encode()).hexdigest(), final_receipt_sha256=final['receipt_sha256'], github_canonical_saved=True, notification_sent='UNKNOWN', user_received_at=None, delivery_verified=False, first_material_prediction_failure=reflection['first_material_failure'])
    rows.append(row)
write('race_stage_audit.json', {'main_sha':MAIN,'denominator':12,'formal_count':5,'signed_receipts_verified':verified,'rows':rows,'formal_recommendation':{'investment':sum(r['settlement']['investment'] for r in rows if 'settlement'in r),'return':sum(r['settlement']['return'] for r in rows if 'settlement'in r)},'actual_purchase_pfs':'UNKNOWN','missing_race_pfs':None,'new_runtime_signatures':0,'new_dispatches':0})
protected = [p for p in git('diff','--name-only',MAIN,'HEAD').decode().splitlines() if p.startswith(('runtime/executions/','runtime/formal_intents/','runtime/race_key_requests/','profiles/','runtime/local_physical/')) or ('oos' in p.lower() and p.endswith('.json'))]
assert not protected, protected
write('preservation.json', {'base_main':MAIN,'head_tree':git('rev-parse','HEAD^{tree}').decode().strip(),'protected_changed_paths':protected,'receipt_body_byte_comparisons':25,'authority':resolve_current_authority()[1]['manifest_id'],'prediction_policy_changes':0,'historical_oos_changes':0})
print(json.dumps({'races':12,'formal':5,'receipt_verifications':len(verified),'protected_diff':protected,'timing_seconds':[{k:r[k] for k in ('race_no','entry_start_to_final_seconds','source_to_final_seconds','final_cutoff_margin_seconds')} for r in rows if 'settlement'in r]}))

"""Durable, Race-local handoff for post-publication Shadow work. No Production writes."""
import argparse
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from jra_role_learning_shadow import digest, instant, persist_shadow, POLICY

PROFILE = 'KM-JRA-DELIVERY-FIRST-SHADOW-CHECKPOINT-v1'
MODEL = 'research/jra_conditional_rank/model.json'
CODES = ('runtime/jra_role_learning_shadow.py', 'runtime/jra_conditional_rank_shadow.py')


def verify_frozen_inputs(root, request, final):
    from evidence_feature_compiler import verify_attestation
    root = Path(root)
    # The pinned original request must reproduce the signed FINAL's frozen inputs.
    # Fail closed rather than synthesize missing feature values from later data.
    mapping=json.loads((root/'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json').read_text())
    verify_attestation(final['evidence_feature_compiler_attestation'],final['race_id'],final['source_snapshot_sha256'],request['runners'],mapping)
    frozen=final['final_prediction_package']['index_provenance_replay']['runners']
    derived={'DCR':'dcr_score','TPI':'tpi_final','ZAI_WIN':'zai_win','ZAI_PLACE':'zai_place','SRI':'sri','F3S':'f3s','T3I':'t3i'}
    for runner in request['runners']:
        old=frozen[str(runner['runner_id'])]
        for key,part in runner['canonical_components'].items():
            expected=old[derived[key]] if key in derived else old['base_final_values'][key]
            if abs(expected-part['value'])>2e-6:raise ValueError('SHADOW_CHECKPOINT_FROZEN_FULL20')
    if request.get('pair_dispositions')!=final.get('pair_dispositions') or request['static_prediction']['roles']!=final['static_prediction']['roles']:
        raise ValueError('SHADOW_CHECKPOINT_FROZEN_ROLES_PAIRS')


def pack(root, request, final, *, created_at=None):
    root = Path(root)
    states = [json.loads(p.read_text()) for p in sorted((root/'runtime/learning_states').glob('*.json'))]
    model = json.loads((root/MODEL).read_text())
    out = {'profile':PROFILE, 'race_id':final['race_id'], 'request':request, 'final':final,
           'request_sha256':digest(request), 'final_sha256':final['sha256'],
           'source_sha256':request['source_snapshot_sha256'],
           'runner_universe_sha256':digest(sorted(str(r['runner_id']) for r in request['runners'])),
           'prediction_cutoff':request['prediction_cutoff'], 'model_sha256':model['sha256'],
           'policy_sha256':digest(POLICY),
           'code_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in CODES},
           'learning_states':states, 'learning_input_sha256':digest(states),
           'created_at':created_at or datetime.now(timezone.utc).isoformat(),
           'production_effect':'NONE', 'oos_eligible':False}
    out['sha256'] = digest(out)
    validate(root, out)
    return out


def validate(root, checkpoint):
    root = Path(root); c = checkpoint; q = c['request']; f = c['final']
    if c.get('sha256') != digest({k:v for k,v in c.items() if k!='sha256'}) or c.get('profile') != PROFILE:
        raise ValueError('SHADOW_CHECKPOINT_HASH_OR_PROFILE')
    rid = c['race_id']
    if not re.fullmatch(r'KM-JRA-[A-Z]{3}-[0-9]{8}-R[0-9]{2}', rid):
        raise ValueError('SHADOW_CHECKPOINT_RACE')
    if (q['race_id'] != rid or f['race_id'] != rid or q.get('family_id') != 'JRA'
            or q.get('temporal_mode') != 'FORMAL-PRE-RACE' or q.get('acceptance_only')
            or f.get('temporal_mode') != 'FORMAL-PRE-RACE'
            or c['request_sha256'] != digest(q) or c['final_sha256'] != f['sha256']
            or f['sha256'] != digest({k:v for k,v in f.items() if k!='sha256'})
            or c['source_sha256'] != q['source_snapshot_sha256'] or c['source_sha256'] != f['source_snapshot_sha256']
            or c['prediction_cutoff'] != q['prediction_cutoff'] or c['prediction_cutoff'] != f['prediction_cutoff']
            or c['runner_universe_sha256'] != digest(sorted(str(r['runner_id']) for r in q['runners']))
            or set(map(str,f['static_prediction']['ranking'])) != {str(r['runner_id']) for r in q['runners']}
            or c['learning_input_sha256'] != digest(c['learning_states'])):
        raise ValueError('SHADOW_CHECKPOINT_INPUT_BINDING')
    verify_frozen_inputs(root,q,f)
    if c['policy_sha256'] != digest(POLICY) or c['code_sha256'] != {p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in CODES}:
        raise ValueError('SHADOW_CHECKPOINT_CODE_POLICY')
    model = json.loads((root/MODEL).read_text())
    if model['sha256'] != digest({k:v for k,v in model.items() if k!='sha256'}) or model['sha256'] != c['model_sha256']:
        raise ValueError('SHADOW_CHECKPOINT_MODEL')
    if not instant(q['source_snapshot']['source_freeze_at']) <= instant(f['final_freeze_timestamp']) <= instant(c['created_at']):
        raise ValueError('SHADOW_CHECKPOINT_CHRONOLOGY')
    return c


def write_once(path, obj):
    """Atomic addition; duplicate identical checkpoint is a resume, differing bytes HOLD."""
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
    with tempfile.NamedTemporaryFile(mode='w',dir=path.parent,delete=False) as tmp:
        temp = Path(tmp.name); tmp.write(raw); tmp.flush(); os.fsync(tmp.fileno())
    try:
        try: os.link(temp,path)
        except FileExistsError:
            if json.loads(path.read_text()) != obj: raise ValueError('IMMUTABLE_SHADOW_CHECKPOINT_CONFLICT')
    finally: temp.unlink()


def execute(root, checkpoint, *, verify_final, clock=None):
    """Worker is bounded by its own Actions job; no thread/future in Production."""
    root = Path(root); c = validate(root,checkpoint)
    now = clock or (lambda: datetime.now(timezone.utc).isoformat())
    cutoff = instant(c['prediction_cutoff'])
    if instant(now()) > cutoff: raise ValueError('SHADOW_CHECKPOINT_AFTER_CUTOFF')
    verify_final(c['final'])  # original cryptographic signed-payload/Capital checks
    destination = root/'runtime/role_rescue_shadow'/(c['race_id']+'.json')
    if destination.exists():
        old = json.loads(destination.read_text())
        if (old.get('sha256') != digest({k:v for k,v in old.items() if k!='sha256'})
                or old.get('delivery_checkpoint_sha256') != c['sha256']):
            raise ValueError('IMMUTABLE_SHADOW_CHECKPOINT_CONFLICT')
        return old
    with tempfile.TemporaryDirectory() as folder:
        scratch = Path(folder); (scratch/MODEL).parent.mkdir(parents=True)
        (scratch/MODEL).write_bytes((root/MODEL).read_bytes())
        for i,s in enumerate(c['learning_states']):
            path=scratch/'runtime/learning_states'/f'{i}.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(s))
        out = persist_shadow(scratch,c['request'],c['final'],observed_at=now())
        out['delivery_checkpoint_sha256'] = c['sha256']
        out['prediction_input_sha256'] = digest({'request_sha256':c['request_sha256'], 'learning_states':c['learning_states']})
        out['checkpoint_learning_input_sha256'] = c['learning_input_sha256']
        out['sha256'] = digest({k:v for k,v in out.items() if k!='sha256'})
        # Late computation never publishes a new frozen artifact, regardless of its start time.
        if instant(now()) > cutoff: raise ValueError('SHADOW_CHECKPOINT_FINISHED_AFTER_CUTOFF')
        write_once(destination,out)
        return out


def restore(root, checkpoint, shadow, *, witness):
    """Restore exact archived bytes only with original independent pre-cutoff proof."""
    c=validate(root,checkpoint)
    if (shadow.get('sha256') != digest({k:v for k,v in shadow.items() if k!='sha256'})
            or shadow.get('delivery_checkpoint_sha256') != c['sha256']
            or shadow.get('baseline_final_sha256') != c['final_sha256']
            or shadow.get('source_sha256') != c['source_sha256']
            or shadow.get('prediction_cutoff') != c['prediction_cutoff']
            or shadow.get('checkpoint_learning_input_sha256') != c['learning_input_sha256']
            or not witness(shadow).get('verified')):
        raise ValueError('SHADOW_RESTORE_ORIGINAL_WITNESS_REQUIRED')
    write_once(Path(root)/'runtime/role_rescue_shadow'/(c['race_id']+'.json'),shadow)
    return shadow


def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--checkpoint');g.add_argument('--request');p.add_argument('--final');p.add_argument('--root',default='.');p.add_argument('--restore-shadow');a=p.parse_args()
    from jra_delivery import verify_signed_final
    from family_authority_guard import resolve_current_authority
    import urllib.request
    root=Path(a.root).resolve();_,authority=resolve_current_authority(root=root)
    contract=json.loads((root/authority['common_family_components']['family_runtime_contracts_profile']).read_text())['families']['JRA']
    with urllib.request.urlopen(contract['external_endpoint'].rstrip('/')+'/health',timeout=20) as response:health=json.load(response)
    if a.request:
        if not a.final:raise ValueError('SHADOW_CHECKPOINT_FINAL_REQUIRED')
        c=pack(root,json.loads(Path(a.request).read_text()),json.loads(Path(a.final).read_text()))
        write_once(root/'shadow-output'/c['race_id']/'shadow_input.json',c)
    else:c=json.loads(Path(a.checkpoint).read_text())
    if a.restore_shadow:
        from jra_role_learning_shadow import actions_pre_result_witness
        verify_signed_final(c['final'],health,contract)
        restore(root,c,json.loads(Path(a.restore_shadow).read_text()),witness=actions_pre_result_witness)
        print('ORIGINAL_PRE_CUTOFF_SHADOW_RESTORED_NO_RECOMPUTATION');return
    out=execute(root,c,verify_final=lambda f:verify_signed_final(f,health,contract))
    target=root/'shadow-output'/c['race_id']/'role_learning_shadow.json';write_once(target,out)
    # MEC R4 remains a separately stored research artifact, after Delivery as well.
    try:
        from mec_r4_shadow import build_mec_r4_shadow
        mec=build_mec_r4_shadow(c['final'])
        if instant(datetime.now(timezone.utc).isoformat()) <= instant(c['prediction_cutoff']):
            write_once(root/'runtime/mec_shadow_artifacts'/(c['race_id']+'.json'),mec)
    except Exception as exc:
        print('MEC_R4_SHADOW_HOLD:'+type(exc).__name__)
    print(json.dumps({'race_id':c['race_id'],'shadow_sha256':out['sha256'],'oos_eligible':False,'status':'PENDING_INDEPENDENT_ARCHIVE_WITNESS'}))


if __name__=='__main__':main()

"""Durable, Race-local handoff for post-publication Shadow work. No Production writes."""
import argparse
import io
import zipfile
import subprocess
import hashlib
import json
import os
import re
import tempfile
import time
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
           'actions_checkpoint_context':{k:os.environ.get(v) for k,v in {'repository':'GITHUB_REPOSITORY','run_id':'GITHUB_RUN_ID','run_attempt':'GITHUB_RUN_ATTEMPT','head_sha':'GITHUB_SHA'}.items()},
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


def prepare(root, request, final, *, created_at=None):
    """Resume the original immutable handoff; never resnapshot Learning on retry."""
    path = Path(root)/'shadow-output'/final['race_id']/'shadow_input.json'
    if path.exists():
        old = validate(root, json.loads(path.read_text()))
        if old['request'] != request or old['final'] != final:
            raise ValueError('IMMUTABLE_SHADOW_CHECKPOINT_CONFLICT')
        return old
    checkpoint = pack(root, request, final, created_at=created_at)
    write_once(path, checkpoint)
    return checkpoint


def archived_checkpoint(root, request, final, run, artifact, archive):
    """Only authenticated provider metadata + digest may restore an input handoff."""
    from jra_role_learning_shadow import WITNESS_REPO
    if (run.get('repository',{}).get('full_name')!=WITNESS_REPO
        or run.get('head_repository',{}).get('full_name')!=WITNESS_REPO
        or run.get('head_branch')!='main'
        or run.get('path')!='.github/workflows/km-formal-request-runner.yml'
        or run.get('event') not in {'push','workflow_dispatch'}
        or str(run.get('id'))!=os.environ.get('GITHUB_RUN_ID')
        or run.get('head_sha')!=os.environ.get('GITHUB_SHA')):
        raise ValueError('SHADOW_RESUME_PROVIDER_IDENTITY')
    attempt=run.get('run_attempt')
    if type(attempt) is not int or not 0<attempt<int(os.environ['GITHUB_RUN_ATTEMPT']):
        raise ValueError('SHADOW_RESUME_ATTEMPT')
    if (artifact.get('name')!='krs-shadow-checkpoint-'+str(run['id'])+'-'+str(attempt)
        or artifact.get('workflow_run',{}).get('id')!=run['id']
        or artifact.get('workflow_run',{}).get('head_sha')!=run['head_sha']
        or artifact.get('expired') is not False
        or len(archive)>32*1024*1024
        or artifact.get('digest')!='sha256:'+hashlib.sha256(archive).hexdigest()):
        raise ValueError('SHADOW_RESUME_ARCHIVE_BINDING')
    name=final['race_id']+'/shadow_input.json'
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        members=[i for i in z.infolist() if i.filename==name]
        if len(members)!=1 or members[0].file_size>16*1024*1024:
            raise ValueError('SHADOW_RESUME_ARCHIVE_MEMBER')
        c=validate(root,json.loads(z.read(members[0])))
    ctx=c.get('actions_checkpoint_context',{})
    # A later attempt may rearchive the ORIGINAL checkpoint; its own origin stays fixed.
    if (ctx.get('repository')!=WITNESS_REPO or str(ctx.get('run_id'))!=str(run['id'])
        or ctx.get('head_sha')!=run['head_sha'] or not str(ctx.get('run_attempt','')).isdigit()
        or not 0<int(ctx['run_attempt'])<=attempt or c['request']!=request or c['final']!=final
        or not instant(run['created_at'])<=instant(c['created_at'])<=instant(artifact['created_at'])
            <=instant(artifact['updated_at'])<=instant(c['prediction_cutoff'])):
        raise ValueError('SHADOW_RESUME_ORIGINAL_INPUT_OR_TIME')
    return c


def recover_previous(root, request, final, *, verify_final, api=None, witness=None):
    """Same execution, fresh Runner. No retries on provider refusal; no new Learning snapshot."""
    from jra_role_learning_shadow import WITNESS_REPO, actions_pre_result_witness, utility_artifact_name
    rid=os.environ.get('GITHUB_RUN_ID','');attempt=os.environ.get('GITHUB_RUN_ATTEMPT','')
    if not rid.isdigit() or not attempt.isdigit():raise ValueError('SHADOW_RESUME_EXECUTION_ID')
    if int(attempt)==1:return None
    if api is None:
        def api(path):
            return subprocess.check_output(['gh','api','--hostname','github.com','repos/'+WITNESS_REPO+'/'+path],timeout=20)
    items=json.loads(api('actions/runs/'+rid+'/artifacts?per_page=100'))
    if items.get('total_count',len(items['artifacts']))>100:raise ValueError('SHADOW_RESUME_INCOMPLETE_ARTIFACT_LIST')
    artifacts=items['artifacts']; candidates=[]
    for a in artifacts:
        m=re.fullmatch('krs-shadow-checkpoint-'+rid+r'-([0-9]+)',a.get('name',''))
        if m and 0<int(m[1])<int(attempt):candidates.append((int(m[1]),a))
    if not candidates:raise ValueError('SHADOW_RESUME_ORIGINAL_CHECKPOINT_MISSING')
    selected=min(n for n,a in candidates);matches=[a for n,a in candidates if n==selected]
    if len(matches)!=1:raise ValueError('SHADOW_RESUME_AMBIGUOUS_CHECKPOINT')
    a=matches[0]
    def download(a):
        if type(a.get('id')) is not int or not 0<a.get('size_in_bytes',0)<=32*1024*1024:
            raise ValueError('SHADOW_RESUME_ARCHIVE_SIZE')
        return api('actions/artifacts/'+str(a['id'])+'/zip')
    run=json.loads(api('actions/runs/'+rid+'/attempts/'+str(selected)))
    c=archived_checkpoint(root,request,final,run,a,download(a))
    verify_final(c['final'])
    shadows=[]
    for n in range(1,int(attempt)):
        matches=[a for a in artifacts if a.get('name')==utility_artifact_name(rid,n)]
        if len(matches)>1:raise ValueError('SHADOW_RESUME_AMBIGUOUS_OUTPUT')
        if not matches:continue
        a=matches[0];raw=download(a)
        if a.get('digest')!='sha256:'+hashlib.sha256(raw).hexdigest():raise ValueError('SHADOW_RESUME_OUTPUT_DIGEST')
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            entries=[i for i in z.infolist() if i.filename==c['race_id']+'/role_learning_shadow.json']
            if len(entries)>1:raise ValueError('SHADOW_RESUME_DUPLICATE_MEMBER')
            if not entries:continue
            if entries[0].file_size>8*1024*1024:raise ValueError('SHADOW_RESUME_OUTPUT_SIZE')
            shadows.append(json.loads(z.read(entries[0])))
    if shadows and any(s!=shadows[0] for s in shadows):raise ValueError('SHADOW_RESUME_CONFLICTING_FROZEN_OUTPUT')
    if shadows:restore(root,c,shadows[0],witness=witness or actions_pre_result_witness)
    write_once(Path(root)/'shadow-output'/c['race_id']/'shadow_input.json',c)
    return c


def learning_effect(shadow):
    """Observed input/ticket differences, not a prediction-improvement claim."""
    accepted = shadow['learning_intake']['accepted']
    from jra_role_learning_shadow import ticket_key
    base = shadow['arms']['PRODUCTION']; learned = shadow['arms']['LEARNING_ON']
    before = {ticket_key(t) for t in base['tickets']}
    after = {ticket_key(t) for t in learned['tickets']}
    return {'accepted_state_bindings': accepted, 'accepted_count': len(accepted),
            'accepted_input_sha256': digest(accepted), 'without_learning_input_sha256': digest([]),
            'input_values_changed': bool(accepted),
            'applied_arm': shadow.get('learning_applied_to_arm'),
            'numerical_rank_or_role_effect': 'NONE_FIXED_MODEL',
            'added_ordered_pairs': [list(v) for k,v in sorted(after-before) if k=='EXACTA'],
            'added_ordered_thirds': [list(v) for k,v in sorted(after-before) if k=='TRIFECTA'],
            'added_ticket_count': len(after-before), 'removed_ticket_count': len(before-after),
            'capital_difference': learned['required_capital']-base['required_capital'],
            'utility_improvement': 'PENDING_RESULT_AND_INDEPENDENT_OOS_WITNESS'}


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
            or shadow.get('runner_universe_sha256') != c['runner_universe_sha256']
            or shadow.get('prediction_input_sha256') != digest({'request_sha256':c['request_sha256'],'learning_states':c['learning_states']})
            or shadow.get('code_sha256') != c['code_sha256'][CODES[0]]
            or (shadow.get('additional_input_sha256') and shadow['additional_input_sha256'].get(MODEL) != c['model_sha256'])
            or not witness(shadow).get('verified')):
        raise ValueError('SHADOW_RESTORE_ORIGINAL_WITNESS_REQUIRED')
    write_once(Path(root)/'runtime/role_rescue_shadow'/(c['race_id']+'.json'),shadow)
    return shadow


def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--checkpoint');g.add_argument('--request');p.add_argument('--final');p.add_argument('--root',default='.');p.add_argument('--restore-shadow');p.add_argument('--prepare-only',action='store_true');a=p.parse_args()
    from jra_delivery import verify_signed_final
    from family_authority_guard import resolve_current_authority
    import urllib.request
    root=Path(a.root).resolve()
    # Raw worker clocks are diagnostic; only the provider archive is an independent witness.
    started=time.monotonic()
    trace={'started_at':datetime.now(timezone.utc).isoformat(), 'production_effect':'NONE',
           'clock_trust':'WORKER_SELF_REPORTED_NOT_INDEPENDENT_FREEZE_PROOF',
           'oos_eligible':False, 'status':'STARTED', 'events':[]}
    run_id=os.environ.get('GITHUB_RUN_ID','local')
    attempt=os.environ.get('GITHUB_RUN_ATTEMPT','local')
    if not all(re.fullmatch(r'[0-9]+|local',x) for x in (run_id,attempt)):
        raise ValueError('SHADOW_TELEMETRY_EXECUTION_ID')
    worker_path=root/'shadow-output'/('worker-'+run_id+'-'+attempt)
    early=dict(trace);early['sha256']=digest(early)
    if not worker_path.with_suffix('.started.json').exists():
        write_once(worker_path.with_suffix('.started.json'),early)
    checkpoint=None
    health_cache={}
    def verify_original(f):
        if not health_cache:
            _,authority=resolve_current_authority(root=root)
            contract=json.loads((root/authority['common_family_components']['family_runtime_contracts_profile']).read_text())['families']['JRA']
            with urllib.request.urlopen(contract['external_endpoint'].rstrip('/')+'/health',timeout=20) as response:health=json.load(response)
            health_cache.update(health=health,contract=contract)
        return verify_signed_final(f,health_cache['health'],health_cache['contract'])
    try:
        if a.request:
            if not a.final:raise ValueError('SHADOW_CHECKPOINT_FINAL_REQUIRED')
            request=json.loads(Path(a.request).read_text());final=json.loads(Path(a.final).read_text())
            checkpoint=recover_previous(root,request,final,verify_final=verify_original) if int(os.environ.get('GITHUB_RUN_ATTEMPT','1'))>1 else None
            checkpoint=checkpoint or prepare(root,request,final)
        else:checkpoint=validate(root,json.loads(Path(a.checkpoint).read_text()))
        c=checkpoint
        trace.update(race_id=c['race_id'], checkpoint_sha256=c['sha256'],
                     source_sha256=c['source_sha256'], runner_universe_sha256=c['runner_universe_sha256'],
                     prediction_cutoff=c['prediction_cutoff'], code_sha256=c['code_sha256'],
                     model_sha256=c['model_sha256'], policy_sha256=c['policy_sha256'])
        trace['events'].append({'stage':'CHECKPOINT_READY','at':datetime.now(timezone.utc).isoformat()})
        trace['actions_context']={k:os.environ.get(v) for k,v in
            {'run_id':'GITHUB_RUN_ID','run_attempt':'GITHUB_RUN_ATTEMPT','head_sha':'GITHUB_SHA','job':'GITHUB_JOB'}.items()}
        start_record=dict(trace)
        start_record['sha256']=digest(start_record)
        attempt=os.environ.get('GITHUB_RUN_ATTEMPT','local')
        start_path=root/'shadow-output'/c['race_id']/('execution-'+str(attempt)+'-started.json')
        if start_path.exists():
            previous=json.loads(start_path.read_text())
            if (previous.get('sha256')!=digest({k:v for k,v in previous.items() if k!='sha256'})
                    or previous.get('checkpoint_sha256')!=c['sha256']):
                raise ValueError('IMMUTABLE_SHADOW_EXECUTION_CONFLICT')
        else:write_once(start_path,start_record)
        verify_original(c['final'])
        if a.prepare_only:
            trace['status']='DURABLE_CHECKPOINT_PREPARED'
            return
        if a.restore_shadow:
            from jra_role_learning_shadow import actions_pre_result_witness
            verify_original(c['final'])
            out=restore(root,c,json.loads(Path(a.restore_shadow).read_text()),witness=actions_pre_result_witness)
            trace['status']='RESTORED_ORIGINAL_WITNESS_NO_RECOMPUTATION'
        elif (root/'runtime/role_rescue_shadow'/(c['race_id']+'.json')).exists():
            from jra_role_learning_shadow import actions_pre_result_witness
            verify_original(c['final'])
            out=restore(root,c,json.loads((root/'runtime/role_rescue_shadow'/(c['race_id']+'.json')).read_text()),witness=actions_pre_result_witness)
            trace['status']='RESTORED_ORIGINAL_WITNESS_NO_RECOMPUTATION'
        else:
            trace['events'].append({'stage':'COMPUTE_START','at':datetime.now(timezone.utc).isoformat()})
            out=execute(root,c,verify_final=verify_original)
            trace['status']='FROZEN_PENDING_INDEPENDENT_ARCHIVE_WITNESS'
        target=root/'shadow-output'/c['race_id']/'role_learning_shadow.json';write_once(target,out)
        trace['events'].append({'stage':'SHADOW_SAVED','at':datetime.now(timezone.utc).isoformat()})
        trace.update(shadow_sha256=out['sha256'],learning_effect=learning_effect(out))
        # MEC R4 remains a separately stored research artifact, after Delivery as well.
        try:
            from mec_r4_shadow import build_mec_r4_shadow
            mec=build_mec_r4_shadow(c['final'])
            if instant(datetime.now(timezone.utc).isoformat()) <= instant(c['prediction_cutoff']):
                write_once(root/'runtime/mec_shadow_artifacts'/(c['race_id']+'.json'),mec)
        except Exception as exc:
            trace['mec_status']='HOLD:'+type(exc).__name__
        print(json.dumps({'race_id':c['race_id'],'shadow_sha256':out['sha256'],'oos_eligible':False,'status':trace['status']}))
    except Exception as exc:
        trace.update(status='FAILED',error_type=type(exc).__name__,reason=str(exc)[:180])
        raise
    finally:
        trace.update(finished_at=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-started)
        if checkpoint:
            trace['seconds_before_cutoff_at_finish']=(instant(checkpoint['prediction_cutoff'])-instant(trace['finished_at'])).total_seconds()
            # Attempts have distinct telemetry; immutable forecast/checkpoint bytes stay unchanged.
            attempt=os.environ.get('GITHUB_RUN_ATTEMPT','local')
            path=root/'shadow-output'/checkpoint['race_id']/('execution-'+str(attempt)+('-prepare' if a.prepare_only else '')+'.json')
            trace['sha256']=digest(trace)
            try:write_once(path,trace)
            except (OSError,ValueError) as exc:print('SHADOW_TELEMETRY_SAVE_HOLD:'+type(exc).__name__)
        else:
            trace['sha256']=digest(trace)
            try:write_once(worker_path.with_suffix('.failed.json'),trace)
            except (OSError,ValueError) as exc:print('SHADOW_TELEMETRY_SAVE_HOLD:'+type(exc).__name__)


if __name__=='__main__':main()

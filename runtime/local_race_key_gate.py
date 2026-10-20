"""Verify minimal race-key handoff without conflating SOURCE with signed FINAL."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import hashlib
import base64
import os
import re
import tempfile
from pathlib import Path

from runtime import formal_execution_orchestrator as o
from runtime.local_race_key_intake import aware


class RaceKeyGateError(ValueError):
    pass


def readback_final(execution_id, job_status='readback', *, repo_root=None,
                   allow_network=True, _verified_final_response=None):
    """Recover canonical LOCAL content; never generate or POST a prediction.

    A first read verifies Ed25519 with the existing canonical Gateway GET key.
    Later reads bind the saved derivative to the exact immutable SOURCE/FINAL
    manifests and current Gateway configuration. They claim historical content
    verification, not a new signature check or recipient acknowledgement.
    The private response argument is used only after terminal_state's existing
    /verify succeeds; it creates the same saved answer during initial execution.
    No key is persisted as a new trust anchor.
    """
    now = datetime.now(timezone.utc)
    report = {'execution_id':execution_id,'observed_at':now.isoformat(),
        'workflow_job_status':job_status,'final_exists':False,'signed_final_pass':False,
        'prestart_final_pass':False,'render_available':False,'prestart_delivery_pass':False,
        'user_received_at':None,'delivery_authority':'UNPROVEN','actual_purchase_pfs':'UNKNOWN',
        'prediction_reexecution':False,'new_runtime_post':False,'production_changed':False}
    try:
        if (not re.fullmatch(r'[A-Za-z0-9_.-]{1,180}', str(execution_id))
                or execution_id in {'.','..'}):
            raise RaceKeyGateError('READBACK_EXECUTION_ID_INVALID')
        root = Path(repo_root or o.ROOT)
        report['final_exists']=(root/'runtime/executions'/execution_id/'FORMAL/LATEST.json').exists()
        formal = o.resolve_phase(execution_id,'FORMAL',root=root/'runtime/executions')
        if formal is None:
            return {**report,'status':'NO_SIGNED_FINAL','reason':'SIGNED_FINAL_CHECKPOINT_MISSING'}
        if 'final_receipt_envelope.json' not in formal['manifest']['files']:
            return {**report,'final_exists':False,'status':'NO_SIGNED_FINAL','reason':'SIGNED_FINAL_CHECKPOINT_MISSING'}
        report['final_exists'] = True
        source = o.resolve_phase(execution_id,'SOURCE',root=root/'runtime/executions')
        if source is None:
            raise RaceKeyGateError('READBACK_SIGNED_SOURCE_MISSING')
        final = o._load_checkpoint_json(formal,'final_receipt_envelope.json') or {}
        signed_source = o._load_checkpoint_json(source,'source_receipt_envelope.json') or {}
        flags = o._load_checkpoint_json(formal,'receipt_verifications.json') or {}
        temporal = o._load_checkpoint_json(formal,'final_before_post_verification.json') or {}
        if any(flags.get(p) is not True for p in ('SOURCE','PRE_KRS','KRS_RUN','FINAL')):
            raise RaceKeyGateError('READBACK_ORIGINAL_VERIFICATIONS_INCOMPLETE')
        from runtime.execution_gateway import family_config, load_gateway, request_json, assess_runtime_health
        gateway = load_gateway(root/'profiles/current_execution_gateway.json')
        cfg = family_config('LOCAL',gateway)
        def digest(value):
            return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,
                separators=(',',':')).encode()).hexdigest()
        def stamp(value):
            t=datetime.fromisoformat(str(value).replace('Z','+00:00'))
            if t.tzinfo is None:
                raise RaceKeyGateError('READBACK_TIMEZONE_REQUIRED')
            return t
        for envelope,phase,status in ((signed_source,'SOURCE','SOURCE_FROZEN'),(final,'FINAL','PASS')):
            receipt,artifact=envelope.get('receipt') or {},envelope.get('artifact') or {}
            if (receipt.get('family')!='LOCAL' or receipt.get('phase')!=phase
                    or receipt.get('status')!=status or receipt.get('errors')
                    or receipt.get('race_id')!=execution_id or artifact.get('race_id',execution_id)!=execution_id
                    or envelope.get('signature_alg')!='Ed25519'
                    or envelope.get('signer_key_id')!=cfg['receipt_signer_key_id']
                    or receipt.get('engine_sha256')!=cfg['engine_sha256']
                    or receipt.get('parameter_map_sha256')!=cfg['parameter_map_sha256']
                    or digest(receipt)!=envelope.get('receipt_sha256')
                    or digest(artifact)!=receipt.get('artifact_sha256') or not envelope.get('signature')):
                raise RaceKeyGateError('READBACK_RECEIPT_IDENTITY_OR_HASH_MISMATCH:'+phase)
        artifact=final['artifact']; receipt=final['receipt']; src=signed_source['artifact']
        if (artifact.get('source_receipt_sha256')!=signed_source['receipt_sha256']
                or artifact.get('source_snapshot_sha256')!=src.get('source_snapshot_sha256')
                or temporal.get('execution_id')!=execution_id or temporal.get('race_id')!=execution_id
                or temporal.get('final_receipt_sha256')!=final['receipt_sha256']
                or temporal.get('verified') is not True):
            raise RaceKeyGateError('READBACK_SOURCE_OR_TEMPORAL_LINEAGE_MISMATCH')
        cutoff=stamp(src['prediction_cutoff']);post=stamp(temporal['scheduled_post_at'])
        frozen=stamp(artifact['final_freeze_timestamp']);signed=stamp(receipt['timestamp'])
        if not stamp(src['source_freeze_at'])<=stamp(signed_source['receipt']['timestamp'])<=frozen<=signed<cutoff<post:
            raise RaceKeyGateError('READBACK_FINAL_NOT_BEFORE_CUTOFF')
        if signed>now:
            raise RaceKeyGateError('READBACK_FUTURE_SIGNATURE_TIME')
        from runtime.jra_ticket_tree_renderer import render_ticket_tree
        tree=render_ticket_tree(artifact)
        payload={'canonical_tree':tree['text'],'rendered_ticket_count':tree['ticket_count'],
            'rendered_investment':tree['total_investment'],
            'rendered_stakes':sorted({t['stake'] for t in tree['reflattened_tickets']}),
            'canonical_prediction':{'current_authority':artifact.get('current_authority_manifest'),
                'formal_grade':artifact.get('formal_grade'),
                'prediction_package':artifact.get('final_prediction_package') or {},
                'final_ticket':artifact.get('final_ticket'),'actual_purchase':'UNKNOWN',
                'krs_receipt':artifact.get('krs_receipt_sha256'),'missing_display_fields_are_unknown':True},
            'final_receipt_sha256':final['receipt_sha256'],
            'original_final_artifact_sha256':receipt['artifact_sha256'],
            'freeze_time':artifact['final_freeze_timestamp'],'final_signed_at':receipt['timestamp'],
            'prediction_cutoff':src['prediction_cutoff'],'scheduled_post_at':temporal['scheduled_post_at'],
            'signature':final['signature'],'signature_alg':final['signature_alg'],
            'signer_key_id':final['signer_key_id']}
        bindings={'execution_id':execution_id,'source_manifest_sha256':source['latest']['manifest_sha256'],
            'formal_manifest_sha256':formal['latest']['manifest_sha256'],
            'source_envelope_sha256':digest(signed_source),'final_envelope_sha256':digest(final),
            'gateway_configuration_sha256':digest(cfg)}
        target=root/'runtime/execution_reports'/execution_id/'delivery'
        saved_path=target/'canonical_presentation.json'
        saved=None
        reused=saved_path.exists()
        if reused:
            saved=json.loads(saved_path.read_text(encoding='utf-8'))
            # A correctness rollout changes the Gateway bundle, not this
            # immutable signed race. Verify the old derivative first, then
            # use one separate render per Gateway binding. The new binding
            # still requires a fresh trusted-key check before offline reuse.
            old_bindings=saved.get('bindings') or {}
            if old_bindings.get('gateway_configuration_sha256')!=bindings['gateway_configuration_sha256']:
                if (saved.get('schema')!='KM-LOCAL-CANONICAL-PRESENTATION-v1'
                        or saved.get('sha256')!=digest({k:v for k,v in saved.items() if k!='sha256'})
                        or {k:v for k,v in old_bindings.items() if k!='gateway_configuration_sha256'}
                           !={k:v for k,v in bindings.items() if k!='gateway_configuration_sha256'}
                        or saved.get('payload')!=payload
                        or saved.get('verification',{}).get('valid') is not True
                        or saved.get('verification',{}).get('method') not in
                           {'CANONICAL_GATEWAY_GET_ED25519','EXISTING_REMOTE_FINAL_VERIFY'}
                        or stamp(saved['created_at'])<signed or stamp(saved['created_at'])>now):
                    raise RaceKeyGateError('SAVED_PRESENTATION_CANONICAL_BINDING_MISMATCH')
                target=target/'runtime_revisions'/bindings['gateway_configuration_sha256']
                saved_path=target/'canonical_presentation.json'
                reused=saved_path.exists()
                saved=json.loads(saved_path.read_text(encoding='utf-8')) if reused else None
        if saved is not None:
            if (saved.get('schema')!='KM-LOCAL-CANONICAL-PRESENTATION-v1'
                    or saved.get('sha256')!=digest({k:v for k,v in saved.items() if k!='sha256'})
                    or saved.get('bindings')!=bindings or saved.get('payload')!=payload
                    or saved.get('verification',{}).get('valid') is not True
                    or saved.get('verification',{}).get('method') not in
                       {'CANONICAL_GATEWAY_GET_ED25519','EXISTING_REMOTE_FINAL_VERIFY'}
                    or stamp(saved['created_at'])<signed or stamp(saved['created_at'])>now):
                raise RaceKeyGateError('SAVED_PRESENTATION_CANONICAL_BINDING_MISMATCH')
        elif _verified_final_response is not None:
            if _verified_final_response.get('valid') is not True:
                raise RaceKeyGateError('READBACK_REMOTE_SIGNATURE_VERIFICATION_REQUIRED')
            verification={'valid':True,'method':'EXISTING_REMOTE_FINAL_VERIFY'}
        elif allow_network:
            status,health=request_json(cfg['external_endpoint'].rstrip('/')+'/health',
                                       method='GET',timeout=20,attempts=1)
            if status>=300 or assess_runtime_health(health,'LOCAL',gateway,root)['status']!='PASS':
                raise RaceKeyGateError('READBACK_CANONICAL_GATEWAY_HEALTH_REQUIRED')
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
            key=Ed25519PublicKey.from_public_bytes(base64.b64decode(health['receipt_public_key_b64'],validate=True))
            for envelope in (signed_source,final):
                key.verify(base64.b64decode(envelope['signature'],validate=True),
                    json.dumps(envelope['receipt'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
            verification={'valid':True,'method':'CANONICAL_GATEWAY_GET_ED25519',
                          'gateway_bundle_fingerprint':assess_runtime_health(health,'LOCAL',gateway,root)['bundle_fingerprint_actual']}
        else:
            raise RaceKeyGateError('INITIAL_READBACK_VERIFICATION_REQUIRED')
        tree_path=target/'canonical_tree.txt';tree_bytes=(tree['text']+'\n').encode()
        restore_tree=not tree_path.exists() or tree_path.read_bytes()!=tree_bytes
        if saved is None:
            target.mkdir(parents=True,exist_ok=True)
            saved={'schema':'KM-LOCAL-CANONICAL-PRESENTATION-v1','created_at':now.isoformat(),
                   'bindings':bindings,'payload':payload,'verification':verification}
            saved['sha256']=digest(saved)
            # Atomic create-if-absent: a killed/concurrent worker cannot publish
            # a partial answer or replace the first successful timestamp.
            with tempfile.NamedTemporaryFile(dir=target,delete=False) as temp:
                temp.write((json.dumps(saved,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode())
                temp_path=Path(temp.name)
            try:
                try:os.link(temp_path,saved_path)
                except FileExistsError:
                    return readback_final(execution_id,job_status,repo_root=root,allow_network=False)
            finally:temp_path.unlink(missing_ok=True)
        if restore_tree:
            with tempfile.NamedTemporaryFile(dir=target,delete=False) as temp:
                temp.write(tree_bytes);tree_temp=Path(temp.name)
            try:os.replace(tree_temp,tree_path)
            finally:tree_temp.unlink(missing_ok=True)
        return {**report,**payload,'status':'SIGNED_FINAL_RENDER_AVAILABLE_DELIVERY_UNPROVEN',
            'signed_final_pass':True,'prestart_final_pass':True,'render_available':True,
            'readback_only':True,'readback_time':now.isoformat(),
            'render_generated_at':saved['created_at'],'presentation_sha256':saved['sha256'],
            'canonical_tree_ref':str(tree_path.relative_to(root)),
            'canonical_presentation_ref':str(saved_path.relative_to(root)),
            'tree_sha256':hashlib.sha256(tree['text'].encode()).hexdigest(),
            'persisted_tree_sha256':hashlib.sha256(tree_bytes).hexdigest(),
            'capital_compatibility':artifact.get('capital_policy_decision',{}).get('compatibility'),
            'verification_scope':'SAVED_CANONICAL_CONTENT_NOT_NEW_SIGNATURE' if reused else 'VERIFIED_CANONICAL_READBACK',
            'fresh_signature_verification':not reused,
            'fresh_external_verify':_verified_final_response,
            'new_runtime_post':_verified_final_response is not None,
            'prediction_post_count':0,'verification_post_count':int(_verified_final_response is not None),
            'derivative_tree_restored':restore_tree,
            'publication_status':'LOCAL_READBACK_ONLY_REMOTE_AVAILABILITY_UNVERIFIED',
            'delivery_time':None,'delivered_content_sha256':None}
    except Exception as exc:
        return {**report,'status':'HOLD_READBACK','reason':f'{type(exc).__name__}:{exc}'}


def certify(request: dict, entry_report: dict) -> dict:
    eid = request["execution_id"]
    source = o.resolve_phase(eid, "SOURCE")
    if source is None:
        raise RaceKeyGateError("SIGNED_SOURCE_CHECKPOINT_MISSING")
    o.validate_source_checkpoint(Path(source["run_dir"]), request)
    signed_source = o._load_checkpoint_json(source, "source_receipt_envelope.json")
    if not signed_source or not signed_source.get("receipt_sha256"):
        raise RaceKeyGateError("SIGNED_SOURCE_RECEIPT_MISSING")

    # A signed, coherent race universe can still be the WRONG start time if
    # the manual five-field trigger was supplied incorrectly. Never turn such
    # a SOURCE into a formal pre-race basis.
    artifact = signed_source.get("artifact") or {}
    official = artifact.get("source_race_context") or {}
    official_day = str(official.get("race_date") or "").replace("/", "-")
    if (official.get("venue_id") != request.get("venue_id")
            or official_day != request.get("race_date")
            or str(official.get("race_no")) != str(request.get("race_no"))):
        raise RaceKeyGateError("SIGNED_SOURCE_OFFICIAL_RACE_IDENTITY_MISMATCH")
    start = (artifact.get("normalized_evidence") or {}).get("start_time") or {}
    expected = aware(request.get("scheduled_post_at"), "SCHEDULED_POST")
    cutoff = aware(request.get("prediction_cutoff"), "PREDICTION_CUTOFF")
    if (start.get("authority") != "NAR_OFFICIAL" or start.get("cutoff_relation") != "PRE_CUTOFF"
            or str(start.get("value") or "") != expected.strftime("%H:%M")):
        raise RaceKeyGateError("SIGNED_SOURCE_OFFICIAL_POST_TIME_MISMATCH")
    try:
        frozen = datetime.fromisoformat(str(artifact["source_freeze_at"]).replace("Z", "+00:00"))
    except (KeyError, TypeError, ValueError) as exc:
        raise RaceKeyGateError("SOURCE_FREEZE_TIMESTAMP_INVALID") from exc
    if frozen.tzinfo is None or frozen.astimezone(timezone.utc) >= cutoff.astimezone(timezone.utc):
        raise RaceKeyGateError("SIGNED_SOURCE_FROZEN_AFTER_CUTOFF")

    status = str(entry_report.get("status") or "")
    report = {
        "execution_id": eid,
        "source_verified": True,
        "source_receipt_sha256": signed_source["receipt_sha256"],
        "formal_final_proven": False,
        "completion": False,
        "production_prediction_changed": False,
        "prestart_delivery_pass": False,
        "service_completion": False,
        "user_received_at": None,
    }
    if status == "HOLD":
        code = str(entry_report.get("code") or "")
        normal_source_holds = {"STATIC_PREDICTION_FREEZE_REQUIRED", "ANALYSIS_ONLY_SOURCE_COMPLETE"}
        deadline_hold = (code == "DEADLINE_HOLD:FORMAL_INCOMPLETE"
                         and entry_report.get("prestart_deadline_expired") is True)
        if code not in normal_source_holds and not deadline_hold:
            raise RaceKeyGateError("UNEXPECTED_FORMAL_HOLD:" + code)
        if entry_report.get("formal_final_proven") is True:
            raise RaceKeyGateError("SOURCE_ONLY_FALSE_FINAL_CLAIM")
        # The SOURCE signature, official race clock, and pre-cutoff freeze
        # were verified above. Missing FORMAL must not falsify signed SOURCE.
        state = ("SOURCE_VERIFIED_FORMAL_DEADLINE_HOLD" if deadline_hold
                 else "SOURCE_VERIFIED_STATIC_PENDING")
        return {**report, "status": state, "reason": code}
    if o.completion_exit_code(entry_report) != 0:
        raise RaceKeyGateError("FORMAL_EXECUTION_NOT_COMPLETE:" + status)
    formal = o.resolve_phase(eid, "FORMAL")
    if formal is None:
        raise RaceKeyGateError("SIGNED_FINAL_CHECKPOINT_MISSING")
    flags = o._load_checkpoint_json(formal, "receipt_verifications.json") or {}
    temporal = o._load_checkpoint_json(formal, "final_before_post_verification.json") or {}
    final = o._load_checkpoint_json(formal, "final_receipt_envelope.json") or {}
    if (flags.get("SOURCE") is not True or flags.get("PRE_KRS") is not True
            or flags.get("KRS_RUN") is not True or flags.get("FINAL") is not True
            or temporal.get("verified") is not True or final.get("receipt_sha256") is None
            or (final.get("receipt") or {}).get("status") != "PASS"):
        raise RaceKeyGateError("SIGNED_FINAL_VERIFICATION_REQUIRED")
    if str(temporal.get("execution_id")) != eid or str(temporal.get("race_id")) != eid:
        raise RaceKeyGateError("FINAL_TEMPORAL_RACE_MISMATCH")
    return {**report, "status": "FULL_LIFECYCLE_EXECUTION_PASS",
            "formal_final_proven": True, "completion": True,
            "final_receipt_sha256": final["receipt_sha256"]}


def terminal_state(execution_id: str, job_status: str) -> dict:
    """Receipt state is independent of Actions exit and user delivery evidence."""
    if (o.ROOT/'runtime/execution_reports'/execution_id/'delivery/canonical_presentation.json').is_file():
        return readback_final(execution_id,job_status,allow_network=False)
    now=datetime.now(timezone.utc)
    report={'execution_id':execution_id,'observed_at':now.isoformat(),'workflow_job_status':job_status,
            'signed_final_pass':False,'prestart_final_pass':False,'render_available':False,
            'prestart_delivery_pass':False,'user_received_at':None,'delivery_authority':'UNPROVEN',
            'actual_purchase_pfs':None,'production_changed':False}
    phase=o.resolve_phase(execution_id,'FORMAL')
    if phase is None:
        return {**report,'status':'TERMINAL_ERROR' if job_status=='failure' else 'NO_SIGNED_FINAL',
                'reason':'SIGNED_FINAL_CHECKPOINT_MISSING'}
    final=o._load_checkpoint_json(phase,'final_receipt_envelope.json') or {}
    flags=o._load_checkpoint_json(phase,'receipt_verifications.json') or {}
    temporal=o._load_checkpoint_json(phase,'final_before_post_verification.json') or {}
    if final.get('receipt',{}).get('status')!='PASS' or flags.get('FINAL') is not True:
        return {**report,'status':'HOLD','reason':'FINAL_VERIFICATION_REQUIRED'}
    # Persisted boolean flags are historical observations, not a fresh proof.
    # Reuse the canonical Gateway verifier; never accept an envelope's own key.
    from runtime.execution_gateway import family_config, request_json
    endpoint = family_config('LOCAL')['external_endpoint'].rstrip('/')
    http, verification = request_json(endpoint+'/verify', method='POST', payload=final,
                                      timeout=20, attempts=1)
    if (http >= 300 or verification.get('valid') is not True
            or final.get('receipt', {}).get('race_id') != execution_id):
        return {**report, 'status': 'HOLD', 'reason': 'FINAL_FRESH_SIGNATURE_OR_IDENTITY_REQUIRED'}
    return readback_final(execution_id,job_status,allow_network=False,
                          _verified_final_response=verification)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request")
    parser.add_argument("--terminal-only",action="store_true")
    parser.add_argument("--readback-only",action="store_true")
    parser.add_argument("--execution-id")
    parser.add_argument("--job-status")
    parser.add_argument("--report")
    parser.add_argument("--output", required=True)
    parser.add_argument("--github-output")
    parser.add_argument("--github-summary")
    args = parser.parse_args()
    if args.terminal_only or args.readback_only:
        try:
            result=(readback_final(args.execution_id,args.job_status) if args.readback_only
                    else terminal_state(args.execution_id,args.job_status))
        except Exception as exc:
            result={'execution_id':args.execution_id,'status':'TERMINAL_ERROR','reason':str(exc),
                    'prestart_delivery_pass':False,'observed_at':datetime.now(timezone.utc).isoformat()}
        if args.report and Path(args.report).is_file():
            try:
                entry = json.loads(Path(args.report).read_text(encoding='utf-8'))
                result['entry_report_ref'] = args.report
                result['execution_failure'] = {k:entry.get(k) for k in (
                    'status','first_failed_phase','first_failed_code','code','failure','first_failure_observed_at')}
            except (OSError, ValueError, AttributeError) as exc:
                result['entry_report_read_error'] = str(exc)
        if args.github_summary:
            # Use this invocation's freshly verified render, never a stale file
            # left by an earlier successful verification.
            included = (result.get('signed_final_pass') is True
                        and result.get('prestart_final_pass') is True
                        and result.get('render_available') is True
                        and isinstance(result.get('canonical_tree'), str))
            content = f"### {args.execution_id}\n\nStatus: {result['status']}\n\n"
            if included:
                content += (f"FINAL receipt: {result['final_receipt_sha256']}\n\n"
                            f"FINAL artifact: {result.get('original_final_artifact_sha256')}\n\n"
                            + result['canonical_tree'] + '\n')
            else:
                content += f"Canonical FINAL withheld: {result.get('reason') or result['status']}\n"
            target = Path(args.github_summary)
            with target.open('a', encoding='utf-8') as handle:
                handle.write(content)
            result['github_summary'] = {
                'status':'WRITTEN_FOR_ACTIONS_JOB_SUMMARY_NOT_USER_RECEIPT',
                'written_at':datetime.now(timezone.utc).isoformat(),
                'content_sha256':hashlib.sha256(content.encode()).hexdigest(),
                'canonical_final_included':included,
                'final_receipt_sha256':result.get('final_receipt_sha256') if included else None,
                'final_artifact_sha256':result.get('original_final_artifact_sha256') if included else None}
        target=Path(args.output);target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        if args.github_output:
            with Path(args.github_output).open('a',encoding='utf-8') as handle:
                handle.write('final_exists='+str(result.get('final_exists') is True).lower()+'\n')
                handle.write('render_available='+str(result.get('render_available') is True).lower()+'\n')
        print(json.dumps(result,ensure_ascii=False))
        return 0
    req = json.loads(Path(args.request).read_text(encoding="utf-8"))
    entry = json.loads(Path(args.report).read_text(encoding="utf-8"))
    result = certify(req, entry)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.github_output:
        with Path(args.github_output).open("a", encoding="utf-8") as output:
            output.write("execution_id=" + req["execution_id"] + "\n")
            output.write("formal_ready=" + str(result["formal_final_proven"]).lower() + "\n")
            output.write("source_verified=true\n")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

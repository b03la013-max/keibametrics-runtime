"""Verify minimal race-key handoff without conflating SOURCE with signed FINAL."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import hashlib
from pathlib import Path

from runtime import formal_execution_orchestrator as o
from runtime.local_race_key_intake import aware


class RaceKeyGateError(ValueError):
    pass


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
    from runtime.jra_ticket_tree_renderer import render_ticket_tree
    tree=render_ticket_tree(final['artifact'])
    target=o.ROOT/'runtime/execution_reports'/execution_id/'delivery'
    target.mkdir(parents=True,exist_ok=True)
    (target/'canonical_tree.txt').write_text(tree['text']+'\n',encoding='utf-8')
    package = final['artifact'].get('final_prediction_package') or {}
    report['canonical_prediction'] = {
        'current_authority': final['artifact'].get('current_authority_manifest'),
        'formal_grade': final['artifact'].get('formal_grade'),
        'prediction_package': package,
        'final_ticket': final['artifact'].get('final_ticket'),
        'actual_purchase': 'UNKNOWN',
        'krs_receipt': (o._load_checkpoint_json(phase, 'krs_receipt_envelope.json') or {}).get('receipt_sha256'),
        'missing_display_fields_are_unknown': True,
    }
    report['canonical_tree'] = tree['text']
    report['canonical_tree_ref'] = str((target/'canonical_tree.txt').relative_to(o.ROOT))
    report['fresh_external_verify'] = verification
    report.update(signed_final_pass=True,prestart_final_pass=temporal.get('verified') is True,
                  render_available=True,render_generated_at=now.isoformat(),
                  rendered_ticket_count=tree['ticket_count'],rendered_investment=tree['total_investment'],
                  tree_sha256=hashlib.sha256(tree['text'].encode()).hexdigest(),
                  persisted_tree_sha256=hashlib.sha256((tree['text']+'\n').encode()).hexdigest(),
                  original_final_artifact_sha256=final['receipt'].get('artifact_sha256'),
                  freeze_time=final['receipt'].get('timestamp'),
                  rendered_stakes=sorted({t['stake'] for t in tree['reflattened_tickets']}),
                  readback_time=now.isoformat(),
                  delivered_content_sha256=None,
                  delivery_time=None,
                  final_receipt_sha256=final['receipt_sha256'],
                  capital_compatibility=final['artifact'].get('capital_policy_decision',{}).get('compatibility'),
                  status='SIGNED_FINAL_RENDER_AVAILABLE_DELIVERY_UNPROVEN')
    return report

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request")
    parser.add_argument("--terminal-only",action="store_true")
    parser.add_argument("--execution-id")
    parser.add_argument("--job-status")
    parser.add_argument("--report")
    parser.add_argument("--output", required=True)
    parser.add_argument("--github-output")
    args = parser.parse_args()
    if args.terminal_only:
        try:
            result=terminal_state(args.execution_id,args.job_status)
        except Exception as exc:
            result={'execution_id':args.execution_id,'status':'TERMINAL_ERROR','reason':str(exc),
                    'prestart_delivery_pass':False,'observed_at':datetime.now(timezone.utc).isoformat()}
        target=Path(args.output);target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
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

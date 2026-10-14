"""Explicit SOURCE-first LOCAL entry. No prediction authority is inferred."""
from __future__ import annotations
import argparse
import copy
from datetime import date
import re
import json
from pathlib import Path
from runtime import formal_execution_orchestrator as o
from runtime.local_fullnumerical_production import materialize_production
from runtime.local_numerical_authority_gate import assess
from runtime.local_static_input_resolver import resolve as resolve_static_input, input_packet
from runtime.local_race_key_shadow_owner import compile_shadow, ShadowOwnerError


def run(intent, *, output, run_id, github_sha=None):
    request = copy.deepcopy(intent)
    if request.get('family_id', 'LOCAL') != 'LOCAL':
        raise ValueError('RACE_ENTRY_FAMILY_NOT_LOCAL')
    request['family_id'] = 'LOCAL'
    if not request.get('execution_id') and not request.get('race_id'):
        venue = str(request.get('venue_id') or '').upper()
        day = date.fromisoformat(str(request.get('race_date') or '').replace('/', '-'))
        number = request.get('race_no')
        if not re.fullmatch(r'[A-Z]{3}', venue) or isinstance(number, bool) or not isinstance(number, int) or not 1 <= number <= 99:
            raise ValueError('RACE_ENTRY_IDENTITY_INVALID')
        request['venue_id'] = venue
        request['race_date'] = day.isoformat()
        request['race_id'] = request['execution_id'] = f'KM-LOCAL-{venue}-{day:%Y%m%d}-R{number:02d}-LIVE-R1'
    request['execution_id'] = o.derive_execution_id(request)
    if request.get('race_id') not in (None, request['execution_id']):
        raise ValueError('RACE_ENTRY_IDENTITY_MISMATCH')
    request['race_id'] = request['execution_id']
    authority_context = o.validate_request_context(request)
    if isinstance(authority_context, dict):
        if not request.get("current_authority_manifest"):
            request["current_authority_manifest"] = authority_context["current_authority_manifest"]
    # Existing verified pre-cutoff SOURCE remains usable; reacquisition after
    # cutoff is forbidden. A late entry never creates a historical prediction.
    saved = o.resolve_phase(request['execution_id'], 'SOURCE')
    if saved is None:
        o.check_deadline(request, phase='SOURCE')
    request.update(execution_phase='SOURCE', analysis_only=True)
    o._write(output/'race_intent.json', request)
    source_report = o.orchestrate(request, run_id=run_id, github_sha=github_sha,
                                  runtime_out=output/'source', tmp_root=output/'tmp')
    saved = o.resolve_phase(request['execution_id'], 'SOURCE')
    o.validate_source_checkpoint(saved['run_dir'], request)
    source = o._load_checkpoint_json(saved, 'source_receipt_envelope.json')
    numeric_request = copy.deepcopy(request)
    numeric_request['runners'] = source['artifact']['official_runner_universe']['runners']
    authority = assess()
    if authority['status'] != 'READY':
        raise ValueError('PRODUCTION_NUMERICAL_AUTHORITY_NOT_READY')
    numerical = materialize_production(source['artifact'], numeric_request, authority['required_indices'])
    o._write(output/'numerical_materialization.json', numerical)
    report = {'status': 'HOLD', 'first_failed_phase': 'STATIC_FREEZE',
              'code': 'STATIC_PREDICTION_FREEZE_REQUIRED', 'completion': False,
              'execution_id': request['execution_id'], 'source': source_report,
              'source_receipt_sha256': source['receipt_sha256'],
              'numerical_diagnostic_only': True, 'prediction_reexecution': False,
              'formal_final_proven': False, 'no_bet_decision': False}
    if numerical.get('strict_full_numerical_ready') is not True:
        report.update(first_failed_phase='NUMERICAL', code='FULL_NUMERICAL_CLOSURE_REQUIRED')
        o._write(output/'entry_report.json', report)
        return report
    # Look up the exact canonical race ourselves; C2 is not a prerequisite
    # for the existing chat-owned frozen-input path.
    discovery_request = copy.deepcopy(request)
    for key in ('family_id', 'execution_id', 'race_id', 'current_authority_manifest'):
        discovery_request.setdefault(key, request.get(key))
    formal, resolution = resolve_static_input(discovery_request, source)
    report['owner_resolution'] = resolution
    generation_allowed = True
    try:
        o.check_deadline(request, phase='FORMAL')
    except o.FormalOrchestrationError as exc:
        generation_allowed = False
        report.update(code=str(exc), prestart_deadline_expired=True)
    o._write(output/'static_owner_input.json', input_packet(request, source, resolution,
                                                          generation_allowed=generation_allowed and intent.get('analysis_only') is not True))
    # A deterministic, explicitly NON-PRODUCTION candidate can be frozen for
    # forward OOS while the authoritative chat-owned Static is absent. It may
    # never fill formal, final_prediction_package, or any Production ticket.
    if formal is None and generation_allowed and intent.get('analysis_only') is not True:
        try:
            shadow = compile_shadow(request, source, numerical)
            o._write(output/'shadow_prediction.json', shadow)
            report['shadow_owner'] = {
                'status': 'FROZEN_NON_PRODUCTION',
                'profile': shadow['profile'],
                'sha256': shadow['sha256'],
                'paper_ticket_count': shadow['paper_ticket_count'],
                'production_prediction_changed': False,
                'formal_final_proven': False,
            }
        except (ShadowOwnerError, KeyError, ValueError) as exc:
            report['shadow_owner'] = {
                'status': 'HOLD',
                'reason': str(exc),
                'formal_final_proven': False,
                'production_prediction_changed': False,
            }
    if formal is not None and intent.get('analysis_only') is True:
        report.update(code='ANALYSIS_ONLY_SOURCE_COMPLETE', first_failed_phase=None)
    if formal is not None and generation_allowed and intent.get('analysis_only') is not True:
        formal.pop('execution_phase', None)
        formal.pop('analysis_only', None)
        report = o.orchestrate(formal, run_id=run_id, github_sha=github_sha,
                              runtime_out=output/'formal', tmp_root=output/'tmp')
        report['owner_resolution'] = resolution
    o._write(output/'entry_report.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--github-sha')
    args = parser.parse_args()
    output = Path(args.output).resolve()
    try:
        report = run(json.loads(Path(args.request).read_text()), output=output,
                     run_id=args.run_id, github_sha=args.github_sha)
    except (o.FormalOrchestrationError, ValueError, KeyError) as exc:
        report = {'status': 'HOLD', 'completion': False, 'code': str(exc), 'formal_final_proven': False}
        o._write(output/'entry_report.json', report)
    print(json.dumps(report, ensure_ascii=False, default=str))
    return o.completion_exit_code(report)


if __name__ == '__main__':
    raise SystemExit(main())

"""Explicit SOURCE-first LOCAL entry. No prediction authority is inferred."""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
from runtime import formal_execution_orchestrator as o
from runtime.local_fullnumerical_production import materialize_production
from runtime.local_numerical_authority_gate import assess


def run(intent, *, output, run_id, github_sha=None):
    request = copy.deepcopy(intent)
    if request.get('family_id', 'LOCAL') != 'LOCAL':
        raise ValueError('RACE_ENTRY_FAMILY_NOT_LOCAL')
    request['family_id'] = 'LOCAL'
    request['execution_id'] = o.derive_execution_id(request)
    if request.get('race_id') not in (None, request['execution_id']):
        raise ValueError('RACE_ENTRY_IDENTITY_MISMATCH')
    request['race_id'] = request['execution_id']
    o.validate_request_context(request)
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
              'code': 'PRODUCTION_STATIC_OWNER_REQUIRED', 'completion': False,
              'execution_id': request['execution_id'], 'source': source_report,
              'source_receipt_sha256': source['receipt_sha256'],
              'numerical_diagnostic_only': True, 'prediction_reexecution': False,
              'formal_final_proven': False, 'no_bet_decision': False}
    if numerical.get('strict_full_numerical_ready') is not True:
        report.update(first_failed_phase='NUMERICAL', code='FULL_NUMERICAL_CLOSURE_REQUIRED')
        o._write(output/'entry_report.json', report)
        return report
    # Approved frozen Static is the only route into the original formal owner.
    if intent.get('static_prediction_frozen') is True and isinstance(intent.get('static_prediction'), dict):
        formal = copy.deepcopy(intent)
        formal.update(family_id='LOCAL', execution_id=request['execution_id'], race_id=request['race_id'])
        formal.pop('execution_phase', None)
        formal.pop('analysis_only', None)
        o.check_deadline(formal, phase='FORMAL')
        report = o.orchestrate(formal, run_id=run_id, github_sha=github_sha,
                              runtime_out=output/'formal', tmp_root=output/'tmp')
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

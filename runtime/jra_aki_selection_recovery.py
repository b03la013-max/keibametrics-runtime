"""Recompute an AKI NO_BET from the original verified SOURCE, never a late FINAL."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from jra_execution_maturity_bridge import prepare_production_numerical, load_current_authority
from jra_aki_no_bet_terminal import record_selection_failure, build_aki_no_bet_terminal
from jra_aki_capital_preflight import sha
from jra_production_blocker_classifier import classify_production_blockers


def recover(intent, source_env, *, source_receipt_verified=False):
    now = datetime.now(timezone.utc)
    cutoff = datetime.fromisoformat(intent['prediction_cutoff'].replace('Z', '+00:00'))
    if intent.get('acceptance_only') is True:
        raise ValueError('RECOVERY_REQUIRES_ORIGINAL_LIVE_INTENT')
    preparation_intent = dict(intent)
    if now > cutoff:
        # Existing acceptance mode supplies a reproducible historical Static
        # basis. The new terminal will carry the real post-cutoff clock.
        preparation_intent['acceptance_only'] = True
    authority = load_current_authority()
    if intent.get('current_authority_manifest') != authority.get('manifest_id'):
        raise ValueError('RECOVERY_AUTHORITY_CHANGED_REVIEW_REQUIRED')
    report = prepare_production_numerical(preparation_intent, source_env,
                                          source_execution_id=intent['execution_id'],
                                          current_authority=authority)
    if report.get('production_full_numerical_ready') is not True:
        raise ValueError('RECOVERY_FULL20_NOT_CLOSED')
    if not report.get('static_owner_executable_diagnostic'):
        # Preparation may cross the cutoff after starting in LIVE mode. Do
        # not backdate a live Static. Reconstruct only a labelled historical
        # diagnostic basis over the original pre-cutoff SOURCE and Full20.
        if datetime.now(timezone.utc) <= cutoff:
            raise ValueError('RECOVERY_STATIC_OWNER_NOT_EXECUTABLE')
        from jra_static_owner_executable import compile_static_owner
        checkpoint = report['source_checkpoint_manifest']
        report['static_owner_executable_diagnostic'] = compile_static_owner(
            report['prepared_numerical_request'],
            source_snapshot_sha256=checkpoint['source_snapshot_sha256'],
            source_receipt_sha256=checkpoint['receipt_sha256'],
            frozen_at=checkpoint['source_freeze_at'], prediction_cutoff=intent['prediction_cutoff'])
        report['recovery_static_basis'] = 'HISTORICAL_DIAGNOSTIC_ONLY / NOT_LIVE_STATIC_FREEZE'
    q = dict(report['prepared_numerical_request'])
    source = source_env['artifact']
    q.update(family_id='JRA', race_id=intent['race_id'], prediction_cutoff=intent['prediction_cutoff'],
             source_snapshot_sha256=source['source_snapshot_sha256'],
             static_prediction=report['static_owner_executable_diagnostic']['static_prediction'])
    record_selection_failure(report, q, source, authority)
    report['auto_handoff_error'] = report['aki_selection_failure']['diagnostic']['code']
    classification = classify_production_blockers(report,
        owner_status=report['static_owner_activation_status'])
    report['production_blocker_classification'] = classification
    report['first_blocked_stage'] = classification['first_actual_blocked_stage']
    report['production_auto_handoff_ready'] = False
    report['production_full_pipeline_ready'] = False
    report['sha256'] = sha({k:v for k,v in report.items() if k != 'sha256'})
    created = datetime.now(timezone.utc)
    return build_aki_no_bet_terminal(intent, report,
        source_receipt_verified=source_receipt_verified, created_at=created.isoformat(),
        lineage='LIVE' if created <= cutoff else 'HISTORICAL_DIAGNOSTIC')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--intent', required=True)
    p.add_argument('--source-envelope', required=True)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    from verify_source_envelope import verify
    assert verify(a.source_envelope)['valid'] is True
    terminal = recover(json.loads(Path(a.intent).read_text()),
                       json.loads(Path(a.source_envelope).read_text()), source_receipt_verified=True)
    target = Path(a.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(terminal, ensure_ascii=False, sort_keys=True, indent=2)+'\n')
    print(json.dumps({k:terminal[k] for k in ('race_id', 'decision_reason', 'lineage',
          'created_at', 'required_index_count', 'total_investment', 'sha256')}, ensure_ascii=False))

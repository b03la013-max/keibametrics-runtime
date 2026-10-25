"""Actual admitted corpus -> environment model -> isolated A/B/C/D diagnostics.

No acquisition or Production write. Real OIDC is required in CI; no verifier
substitution exists in this entry point. Historical comparisons are explicitly
post-capture, even though their label partitions are chronological.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'runtime'), str(ROOT / 'runtime/jra_source_runtime')]

from family_authority_guard import resolve_current_authority
from jra_pedigree_corpus import _verified_source, _attested, _horse_identity, build_corpus
from jra_bvi_environment import build_environment_dataset
from jra_bvi_env_shadow import train_model, evaluate_chronological, predict, sha, PROTOCOL_SHA256
from jra_bvi_shadow_comparison import append_environment_arm, execute_diagnostic_downstream


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def source_for_request(req):
    directory = ROOT / 'runtime/executions' / req['source_execution_id'] / 'SOURCE'
    for path in sorted(directory.glob('runs/*/source_receipt_envelope.json')):
        checked = _verified_source(path)
        if checked and checked['source_snapshot_sha256'] == req['source_snapshot_sha256']:
            if not _attested(path, not_after=datetime.fromisoformat(req['prediction_cutoff'])):
                raise ValueError('BVI_ENV_REAL_SOURCE_ORIGINAL_CUTOFF_OIDC_INVALID')
            return path, json.loads(path.read_text())
    raise ValueError('BVI_ENV_REAL_SOURCE_UNRESOLVED')


def target_environment(source, req, *, diagnostic_cutoff):
    """Only observations in this exact signed race, never venue-name inference."""
    detail = source['jra_official_race_card_detail']
    context = detail.get('race_context') or {}
    observed = detail.get('race_environment') or {}
    race = req['race']
    if (context.get('race_date') != req['race_date']
            or context.get('distance_m') != race['distance']
            or context.get('surface') != race['surface']):
        raise ValueError('BVI_ENV_TARGET_RACE_CONTEXT_MISMATCH')
    if context.get('going') and observed.get('going') and context['going'] != observed['going']:
        raise ValueError('BVI_ENV_TARGET_GOING_CONFLICT')
    if context.get('weather') and observed.get('weather') and context['weather'] != observed['weather']:
        raise ValueError('BVI_ENV_TARGET_WEATHER_CONFLICT')
    return {'race_date': req['race_date'], 'venue': race['venue'],
        'surface': race['surface'], 'distance_m': race['distance'],
        'field_size': len(req['runners']), 'race_name': race['race_name'],
        'going': context.get('going') or observed.get('going'),
        'inner_outer': context.get('course_variant'),
        'weather': context.get('weather') or observed.get('weather'),
        'rainfall_mm': None, 'moisture_pct': None, 'cushion_value': None,
        'source_snapshot_sha256': source['source_snapshot_sha256'],
        'source_observed_at': source['source_freeze_at'],
        'prediction_cutoff': diagnostic_cutoff,
        'original_prediction_cutoff': req['prediction_cutoff'],
        'classification': 'POST_CAPTURE_DIAGNOSTIC_INPUT_NOT_ORIGINAL_PRE_RACE_EVIDENCE'}


def guarded_external(path, payload, timeout):
    # Recheck at every new simulation launch, not just workflow start. Reads of
    # a completed run's signature are allowed; new simulations never consume
    # protected Oct25 Production capacity. No deploy or purchase is performed.
    day = datetime.now(timezone(timedelta(hours=9))).date().isoformat()
    if path == '/krs/execute' and day in ('2026-10-17', '2026-10-18', '2026-10-25'):
        raise ValueError('BVI_ENV_EXTERNAL_DIAGNOSTIC_DEFER_PRODUCTION_DATE')
    from scripts.jra_bvi_pipeline_real_acceptance import external_call
    return external_call(path, payload, timeout)


def diagnostic_metrics(comparison, req, official):
    from jra_bvi_oos_metrics import preregister, evaluate
    top = [str(x) for x in official['top3']]
    settled = {'arms': {}}
    for name, arm in comparison['arms'].items():
        owner = arm['owner']; ranking = list(map(str, owner['static_prediction']['ranking']))
        cols = owner['active_columns']
        settled['arms'][name] = {
            'settlement': arm['diagnostic_virtual_settlement'],
            'ordered_pair_semantic_capture': any(str(p['head']) == top[0] and str(p['second']) == top[1]
                and p['status'] != 'EXCLUDE' for p in owner['pair_dispositions']),
            'exact_semantic_capture': any(tuple(str(p[k]) for k in ('head', 'second', 'third')) == tuple(top)
                and p['status'] != 'EXCLUDE' for p in owner['third_dispositions']),
            'ordered_pair_capture': 'EXACTA' in arm['diagnostic_virtual_settlement']['hit_types'],
            'exact_capture': 'TRIFECTA' in arm['diagnostic_virtual_settlement']['hit_types'],
            'krs_utility': arm['krs_result_utility'],
        }
        arm['historical_diagnostic_metrics'] = {'winner_rank': ranking.index(top[0]) + 1,
            'winner_discovery_recall': int(top[0] in cols['W']),
            'p2_capture': top[1] in cols['P2'], 'p3_capture': top[2] in cols['P3'],
            'top3_mean_rank': sum(ranking.index(r) + 1 for r in top) / 3,
            'candidate_width': len(set().union(*(set(v) for v in cols.values()))),
            'false_positive_candidates': len(set().union(*(set(v) for v in cols.values())) - set(top))}
    pre = {'race_id': req['race_id'], 'comparison': comparison, 'market_ranking': None,
           'comparison_protocol': preregister(comparison)}
    return evaluate(pre, official, settled)


def run(output_dir, *, abc_artifact=None, run_external=False):
    started = datetime.now(timezone.utc)
    cutoff = started.isoformat()
    authority_path, authority = resolve_current_authority(ROOT)
    code = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    target_day = '2026-10-25'
    corpus = build_corpus(ROOT, prediction_cutoff=cutoff, race_date=target_day)
    dataset = build_environment_dataset(ROOT, prediction_cutoff=cutoff, race_date=target_day)
    if not dataset['source_counts'].get('oidc_harvests'):
        raise ValueError('BVI_ENV_NO_REAL_OIDC_HARVEST_ADMITTED')
    assert len(dataset['rows']) == corpus['run_count']
    assert dataset['manifest_sha256'] == corpus['manifest_sha256']
    # Derived datasets never persist duplicate original corpus or source HTML.
    summary = {k: v for k, v in dataset.items() if k not in ('rows',)}
    summary.update(code_git_sha=code, current_authority=authority['manifest_id'],
        authority_file_sha256=hashlib.sha256(authority_path.read_bytes()).hexdigest(),
        generated_at=datetime.now(timezone.utc).isoformat())
    save(output_dir / 'environment_coverage.json', summary)
    historical_model = train_model(dataset, train_before='2026-08-01')
    chronological = evaluate_chronological(dataset, train_before='2026-08-01',
        validation_before='2026-09-01', test_before='2026-10-24')
    save(output_dir / 'historical_model.json', historical_model)
    save(output_dir / 'chronological_diagnostic.json', chronological)
    prospective_model = train_model(dataset, train_before=target_day)
    from scripts.jra_bvi_pipeline_forward_shadow import environment_model_publication
    publication = environment_model_publication(prospective_model, root=ROOT,
        code_git_sha=os.environ.get('ENV_MODEL_CODE_SHA') or None)
    save(output_dir / 'bvi_env_model_publication.json', publication)
    reports = []
    if abc_artifact is not None:
        previous = json.loads(abc_artifact.read_text())
        mapping = json.loads((ROOT / 'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json').read_text())
        for old in previous['reports']:
            rid = old['race_id']
            req = json.loads(sorted((ROOT / 'runtime/requests').glob('*' + rid.removeprefix('KM-JRA-') + '*FORMAL.json'))[-1].read_text())
            source_path, envelope = source_for_request(req)
            source = envelope['artifact']
            comparison = deepcopy(old['comparison'])
            actual = datetime.now(timezone.utc)
            diagnostic_cutoff = (actual + timedelta(minutes=25)).isoformat()
            environment = target_environment(source, req, diagnostic_cutoff=diagnostic_cutoff)
            card = {str(r.get('runner_id') or r.get('horse_no')): r
                    for r in source['jra_official_race_card_detail']['runners']}
            history = (source.get('jra_official_horse_history') or {}).get('runners') or {}
            predictions = {}
            for runner_id, raw in card.items():
                runner = {k: raw.get(k) for k in ('horse_name', 'sire', 'dam', 'damsire')}
                runner.update(runner_id=runner_id, horse_id=_horse_identity(runner),
                              runs=(history.get(runner_id) or {}).get('runs') or [])
                predictions[runner_id] = predict(historical_model, runner, environment)
            before = sha(comparison['arms'])
            append_environment_arm(comparison, req, mapping, predictions=predictions,
                model_sha=historical_model['model_sha256'], source_artifact=source,
                current_authority=authority, root=ROOT, calculated_at=actual.isoformat(),
                diagnostic_cutoff=diagnostic_cutoff)
            d = comparison['arms']['D_BVI_ENV_SHADOW']
            assert before == sha({k: v for k, v in comparison['arms'].items() if k != 'D_BVI_ENV_SHADOW'})
            official = json.loads((ROOT / 'runtime/results' / (rid + '.json')).read_text())['official_result']
            if run_external:
                execute_diagnostic_downstream({'arms': {'D_BVI_ENV_SHADOW': d}}, req, official, guarded_external)
            report = {'race_id': rid, 'classification': 'POST_CAPTURE_DIAGNOSTIC_NOT_FORWARD_OOS',
                'source_file_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
                'source_snapshot_sha256': source['source_snapshot_sha256'],
                'original_prediction_cutoff': req['prediction_cutoff'],
                'diagnostic_created_at': actual.isoformat(), 'environment': environment,
                'predictions': predictions, 'comparison': comparison,
                'abc_previous_real_execution_reused_without_change': True,
                'forward_oos_increment': 0, 'production_rewritten': False}
            if run_external:
                report['metrics'] = diagnostic_metrics(comparison, req, official)
            reports.append(report)
    pooled = {}
    if reports and run_external:
        from pfs_grand_review import _aggregate, _robustness
        for name in reports[0]['comparison']['arms']:
            rows = []
            for report in reports:
                settlement = report['comparison']['arms'][name]['diagnostic_virtual_settlement']
                rows.append({'race_id': report['race_id'], 'date': report['race_id'].split('-')[3],
                    'investment': settlement['investment'], 'return': settlement['return'],
                    'profit_loss': settlement['profit_loss'],
                    'hit_but_loss': bool(settlement['return'] and settlement['profit_loss'] < 0)})
            pooled[name] = {'aggregate': _aggregate(rows), 'robustness': _robustness(rows)}
    result = {'profile': 'KM-JRA-BVI-ENV-REAL-ACCEPTANCE-v1', 'code_git_sha': code,
        'created_at': datetime.now(timezone.utc).isoformat(), 'started_at': cutoff,
        'protocol_sha256': PROTOCOL_SHA256,
        'classification': 'ACTUAL_CORPUS_AND_CURRENT_RESEARCH_MODEL / NOT_FORWARD_OOS',
        'reader_run_count': corpus['run_count'], 'environment_row_count': len(dataset['rows']),
        'reader_manifest_sha256': corpus['manifest_sha256'], 'coverage': dataset['coverage'],
        'going_recovered_runs': dataset['going_recovered_runs'],
        'historical_model_sha256': historical_model['model_sha256'],
        'prospective_model_sha256': prospective_model['model_sha256'],
        'publication_sha256': publication['sha256'], 'races': reports,
        'diagnostic_pooled_pfs': pooled,
        'd_krs_executions': sum(r['comparison']['arms']['D_BVI_ENV_SHADOW']['krs_simulation_executed'] for r in reports),
        'future_race_freezes': 0, 'forward_oos_eligible_races': 0, 'required_forward_races': 30,
        'forward_oos_status': 'FORWARD OOS PENDING', 'predictive_improvement_demonstrated': False,
        'production_policy_change': 'NONE', 'production_effect': 'NONE', 'purchase_authority': False}
    save(output_dir / 'acceptance.json', result)
    return {k: v for k, v in result.items() if k != 'races'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'runtime_out/bvi_env')
    parser.add_argument('--abc-artifact', type=Path)
    parser.add_argument('--run-external', action='store_true')
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir, abc_artifact=args.abc_artifact,
                         run_external=args.run_external), ensure_ascii=False))

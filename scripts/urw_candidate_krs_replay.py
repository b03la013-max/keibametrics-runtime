"""Offline historical URW contract diagnostic, never a dispatcher or OOS freeze.

Requires the original seven Actions archives and the independently pinned Engine
reference. No network calls, keys, signing, policy fitting or Runtime requests.
Forecast/Engine outputs are persisted before the separate result-label pass.
"""
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from zipfile import ZipFile
import argparse
import base64
import gzip
import hashlib
import json
import subprocess
import sys
import time
import copy

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'runtime')]
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from runtime.local_fullnumerical_production import materialize_production
from runtime.local_numerical_authority_gate import assess
from runtime.local_race_key_shadow_owner import compile_urw_candidate, audit_urw_candidate_paper_pipeline, _sha
from runtime.krs_prediction_utility import build_krs_prediction_utility, evaluate_against_result
from runtime.mec_r4_shadow import settle_ticket_list

ENGINE = '9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421'
PARAMETERS = 'd8c027ee5bcc8fd3d2c248e8059b341776be38910e833d7589f09ab817c161f5'
KEY = 'jqWqOYlmhXXmpv/nR7lx3c2n/S5shDYava/WJVxn4kE='
ARCHIVES = {
    35831609334: '65c7b3b61f1034ee7744a074014e7343f2f681416630aa9d7a783da818693c9d',
    35840245134: '57fbecf198a2093ab350c0a504d1996c6935ee5db66be554d37b97a17fba2c56',
    35845291112: 'b95ac312dc2658e1ba264eb293f71a2e3aa1f20da9d1002c9c51199024962bcc',
    35847691817: '3729ecbd26afbf3e8437804a23242940b4d25383484f3c236ba1336ec5d152ab',
    35961138259: 'ed759ed1086c72f6c5a16c07cedc76c5a35a2f52a7857062b7796d4a9d4bc04c',
    35978840734: '848612bed0b2d79bb191ee40a24318ff0af3b2d56349b5b66795acb084cb3dce',
    35984798580: '557b93a09b31f59dd1db364f3124d2a28df4c222c8dd1296f9e24aec92512e8a',
}


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n')


def audit_index_consumption(numerical):
    """Result-blind finite interventions on the existing Candidate baseline.

    These unsigned 0/100 counterfactuals measure code dependence, not plausible
    feature changes, predictive value, calibration or Production authority.
    Preserve RULED-NEUTRAL state and provenance; never save as materialized
    SOURCE or feed these synthetic values to the Runtime/Engine.
    """
    from runtime.local_krs_bridge_candidate import build_candidate_prediction_structure_derived as predict
    rows=numerical['runners']
    base=predict({'runners':copy.deepcopy(rows)})['candidate_static_prediction']
    scores={x['runner_id']:x for x in base['runner_scores']}
    indices=[]
    for name in numerical['required_indices']:
        cells=[]
        for offset,row in enumerate(rows):
            rid=str(row['runner_id']);cell=row['canonical_components'][name]
            interventions=[]
            for value in (0,100):
                changed=copy.deepcopy(rows)
                changed[offset]['canonical_components'][name]['value']=value
                observed=predict({'runners':changed})['candidate_static_prediction']
                score=next(x for x in observed['runner_scores'] if x['runner_id']==rid)
                interventions.append({'unsigned_synthetic_value':value,
                    'role_score_deltas':{k:score[k]-scores[rid][k] for k in ('w_score','p2_score','p3_score')},
                    'ranking_changed':observed['ranking']!=base['ranking'],
                    'roles_changed':observed['roles']!=base['roles']})
            cells.append({'runner_id':rid,'value':cell['value'],'terminal_status':cell['terminal_status'],
                'rule_id':cell['rule_id'],'mapping_version':cell['mapping_version'],
                'evidence_refs':cell['evidence_refs'],'source_fact':cell['source_fact'],
                'cell_sha256':_sha(cell),'interventions':interventions,
                'production_consumption_authorized':False})
        indices.append({'index':name,'cells':cells,
            'candidate_score_dependence':any(any(v!=0 for v in q['role_score_deltas'].values()) for c in cells for q in c['interventions']),
            'ranking_changed_cases':sum(q['ranking_changed'] for c in cells for q in c['interventions']),
            'role_changed_cases':sum(q['roles_changed'] for c in cells for q in c['interventions'])})
    out={'classification':'UNSIGNED_SYNTHETIC_CODE_SENSITIVITY_NOT_PREDICTIVE_VALUE_NOT_OOS',
        'race_id':numerical['race_id'],'source_snapshot_sha256':numerical['production_evidence_compiler']['source_snapshot_sha256'],
        'original_numeric_provenance_sha256':numerical['index_provenance_hash'],
        'candidate_baseline':base,'indices':indices,'index_count':len(indices),
        'score_consumed_indices':[x['index'] for x in indices if x['candidate_score_dependence']],
        'production_consumption_authorized':False,'runtime_post_count':0,
        'prediction_value_increment':'UNKNOWN_REQUIRES_FROZEN_FORWARD_COMPARISON'}
    out['sha256']=_sha(out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--archives', type=Path, required=True)
    ap.add_argument('--engine', type=Path)
    ap.add_argument('--baseline-outputs', type=Path)
    ap.add_argument('--evidence-audit-only', action='store_true')
    ap.add_argument('--prior-predictions', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    params = ROOT / 'runtime/local_physical/parameter_map_v0.1-provisional.json'
    if not args.evidence_audit_only:
        if args.engine is None or args.baseline_outputs is None:
            ap.error('--engine and --baseline-outputs required for Engine replay')
        assert hashlib.sha256(args.engine.read_bytes()).hexdigest() == ENGINE
    assert hashlib.sha256(params.read_bytes()).hexdigest() == PARAMETERS
    args.output.mkdir(parents=True, exist_ok=False)
    key = Ed25519PublicKey.from_public_bytes(base64.b64decode(KEY))
    rows, forecasts = [], {}
    started = datetime.now(timezone.utc).isoformat()
    for run, digest in ARCHIVES.items():
        archive = args.archives / f'urw-history-{run}.zip'
        assert hashlib.sha256(archive.read_bytes()).hexdigest() == digest
        with ZipFile(archive) as z:
            source = json.loads(z.read('source_receipt_envelope.json'))
        assert source['signer_key_id'] == 'KM-LOCAL-RUNTIME-ED25519-20260922'
        assert source['receipt_sha256'] == _sha(source['receipt'])
        assert source['receipt']['artifact_sha256'] == _sha(source['artifact'])
        key.verify(base64.b64decode(source['signature']), json.dumps(
            source['receipt'], ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())
        rid = source['receipt']['race_id']
        stored = json.loads((ROOT / 'runtime/family_requests' / f'{rid}.json').read_text())
        request = {k: stored[k] for k in ('race_id', 'race_date', 'race_no', 'venue_id',
                                        'scheduled_post_at', 'prediction_cutoff')}
        request.update(family_id='LOCAL', execution_id=rid)
        row = {'race_id': rid, 'archive_run_id': run, 'archive_sha256': digest,
               'source_receipt_sha256': source['receipt_sha256']}
        rows.append(row)
        try:
            numerical = materialize_production(source['artifact'], {
                **request, 'runners': source['artifact']['official_runner_universe']['runners']},
                assess()['required_indices'])
            row['numerical_cells'] = 29 * len(numerical['runners'])
            candidate = compile_urw_candidate(request, source, numerical, historical_replay=True)
            paper = audit_urw_candidate_paper_pipeline(candidate, numerical)
            forecasts[rid] = {'candidate': candidate, 'paper': paper}
            if args.evidence_audit_only:
                forecasts[rid]['index_consumption_audit']=audit_index_consumption(numerical)
            row.update(status='CANDIDATE_REPLAY', candidate_sha256=candidate['sha256'],
                       candidate_krs_input_sha256=paper['candidate_krs_input_sha256'])
            dump(args.output / f'{rid}.input.json', paper['candidate_krs_input'])
        except ValueError as exc:
            row.update(status='HOLD', first_failed_stage='URW_STATIC_CANDIDATE', error=str(exc))

    if args.evidence_audit_only:
        prior=json.loads(gzip.decompress(args.prior_predictions.read_bytes()))['forecasts'] if args.prior_predictions else {}
        for row in rows:
            rid=row['race_id']
            if rid not in forecasts:
                continue
            f=forecasts[rid];candidate=f['candidate'];scenario=candidate['urw_scenario_prediction']
            if prior:
                old=prior[rid]
                row['same_ranking_and_roles_as_prior_identity_replay']=(candidate['ranking']==old['candidate']['ranking'] and candidate['role_columns']==old['candidate']['role_columns'])
                row['same_engine_input_as_prior_identity_replay']=f['paper']['candidate_krs_input_sha256']==old['paper']['candidate_krs_input_sha256']
                assert row['same_ranking_and_roles_as_prior_identity_replay'] and row['same_engine_input_as_prior_identity_replay']
            row.update(score_consumed_indices=f['index_consumption_audit']['score_consumed_indices'],
                strict_p2_order_edges=sum(len(x['partial_order_edges']) for x in scenario['head_local_p2'].values()),
                strict_p3_order_edges=sum(len(x['partial_order_edges']) for x in scenario['pair_conditioned_p3'].values()),
                material_exact_count=sum(e['material_exact_evidence'] for x in scenario['pair_conditioned_p3'].values() for e in x['evaluations'].values()),
                source_bound_condition_translations=len(candidate['urw_evidence']))
        artifact={'classification':'HISTORICAL_EVIDENCE_AND_UNSIGNED_CODE_SENSITIVITY_NOT_FORWARD',
                  'forecasts':forecasts,'created_at':datetime.now(timezone.utc).isoformat()}
        packed=gzip.compress(json.dumps(artifact,ensure_ascii=False,sort_keys=True).encode(),mtime=0)
        (args.output/'evidence_audit.json.gz').write_bytes(packed)
        report={'classification':artifact['classification'],'selected_denominator':len(rows),
            'candidate_completed':len(forecasts),'held':len(rows)-len(forecasts),
            'races':rows,'artifact_sha256':hashlib.sha256(packed).hexdigest(),
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'genuine_forward_oos':0,'new_engine_runs':0,'runtime_post_count':0,
            'prediction_quality_improvement':'NOT_PROVEN','production_changes':False,
            'limits':'0/100 unsigned interventions measure Candidate code dependence only, not feature plausibility or incremental prediction value. Neutral states preserved. Existing six-race Engine evidence reusable only where exact Engine input SHA and roles match; no new quality claim.'}
        report['sha256']=_sha(report)
        dump(args.output/'report.json',report)
        print(json.dumps({k:v for k,v in report.items() if k!='races'}))
        return

    def simulate(rid):
        wall = time.perf_counter()
        with (args.output / f'{rid}.log').open('w') as log:
            subprocess.run([sys.executable, str(args.engine.resolve()),
                str(args.output / f'{rid}.input.json'), '--output', str(args.output / f'{rid}.output.json'),
                '--csv', str(args.output / f'{rid}.csv'), '--params', str(params),
                '--runs', '5000', '--seed', '1', '--short'], stdout=log, stderr=subprocess.STDOUT,
                timeout=180, check=True)
        raw = json.loads((args.output / f'{rid}.output.json').read_text())
        snap = raw['snapshot']
        assert snap['prediction_id'] == rid and snap['racecourse'] == '浦和'
        assert snap['date'] == forecasts[rid]['candidate']['race_date']
        assert snap['race_no'] == forecasts[rid]['candidate']['race_no']
        assert snap['run_count'] == 5000
        return rid, raw, time.perf_counter() - wall

    with ThreadPoolExecutor(max_workers=3) as pool:
        for rid, raw, seconds in pool.map(simulate, forecasts):
            forecasts[rid]['engine_output'] = raw
            forecasts[rid]['utility'] = build_krs_prediction_utility(
                forecasts[rid]['paper']['semantic_request'], {'status': 'EXECUTED', 'output': raw})
            forecasts[rid]['offline_wall_seconds'] = seconds
    snapshots = [x['engine_output']['snapshot']['simulation_snapshot_id'] for x in forecasts.values()]
    assert len(snapshots) == len(set(snapshots))
    before_labels = {'classification': 'RETROSPECTIVE_CANDIDATE_NOT_FORWARD_OOS',
                     'completed_at': datetime.now(timezone.utc).isoformat(), 'forecasts': forecasts}
    frozen_bytes = json.dumps(before_labels, ensure_ascii=False, sort_keys=True).encode()
    (args.output / 'predictions_before_labels.json.gz').write_bytes(gzip.compress(frozen_bytes, mtime=0))

    # Labels cannot influence compilation, simulation, role proposals or tickets.
    for row in rows:
        rid = row['race_id']
        matches = sorted((ROOT / 'runtime/family_result_requests').glob(
            rid.replace('-FORMAL-R1', '') + '-RESULT-R*.json'))
        labels = json.loads(matches[-1].read_text())
        assert labels['race_id'] == rid
        row['label'] = {'path': str(matches[-1].relative_to(ROOT)),
            'file_sha256': hashlib.sha256(matches[-1].read_bytes()).hexdigest(),
            'official_result_verified_recorded': labels.get('official_result_verified') is True,
            'fresh_official_refetch_verified': False, 'top3': labels['finish_order'][:3]}
        if rid not in forecasts:
            row['recommended_pfs'] = 'N/A'
            continue
        f = forecasts[rid]
        actual = list(map(int, labels['finish_order'][:3]))
        row.update(snapshot=f['engine_output']['snapshot'], offline_wall_seconds=f['offline_wall_seconds'],
            evaluation=evaluate_against_result(f['utility'], actual, static_ranking=f['candidate']['ranking']),
            semantic_virtual_settlement=settle_ticket_list(f['paper']['mec_contract_result']['tickets'],
                {'official_result': {'top3': labels['finish_order'][:3], 'payouts': labels['payouts']}}))
        old = json.loads((args.baseline_outputs / f'{rid}.output.json').read_text())
        old_utility = build_krs_prediction_utility(f['paper']['semantic_request'], {'status': 'EXECUTED', 'output': old})
        row['anonymous_baseline_snapshot'] = old['snapshot']
        row['anonymous_baseline_evaluation'] = evaluate_against_result(
            old_utility, actual, static_ranking=f['candidate']['ranking'])
        row['nonveto_shadow_role_hits'] = {role: role in f['utility']['shadow_role_registry'][str(horse)]
                                         for role, horse in zip(('W', 'P2', 'P3'), actual)}
        row['false_shadow_additions'] = {k: row['evaluation'][k] for k in
            ('false_pair_addition_count', 'false_exact_addition_count', 'proposal_width')}
    completed = [r for r in rows if r['status'] != 'HOLD']
    report = {'classification': 'HISTORICAL_DIAGNOSTIC_NOT_PRODUCTION_NOT_OOS',
        'started_at': started, 'prediction_pass_completed_before_labels_at': before_labels['completed_at'],
        'prediction_pass_sha256': hashlib.sha256(frozen_bytes).hexdigest(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'engine_sha256': ENGINE, 'parameter_map_sha256': PARAMETERS,
        'selected_denominator': len(rows), 'candidate_completed': len(completed), 'held': len(rows)-len(completed),
        'requested_runs_per_completed_race': 5000, 'master_seed': 1,
        'unique_race_bound_snapshot_count': len(set(snapshots)),
        'anonymous_baseline_snapshot_count': len({r['anonymous_baseline_snapshot']['simulation_snapshot_id'] for r in completed}),
        'static_role_hits': {role: sum(next(x for x in r['evaluation']['rank_comparison'] if x['role']==role)['static_role_hit'] for r in completed) for role in ('W','P2','P3')},
        'nonveto_shadow_role_hits': {role: sum(r['nonveto_shadow_role_hits'][role] for r in completed) for role in ('W','P2','P3')},
        'quality_disposition': 'HOLD_UNCALIBRATED_ROLE_EXPANSION_NOT_PURCHASE_AUTHORITY',
        'races': rows, 'genuine_forward_oos': 0, 'runtime_post_count': 0,
        'new_paid_api_requests': 0, 'signed_final_count': 0, 'actual_purchase_pfs': 'UNKNOWN',
        'production_changes': False, 'physics_or_parameters_changed': False,
        'limits': 'Seven retrievable historical archives, one retained HOLD; mixed stored-label provenance, no fresh official refetch. Seed namespace repair changes simulation draws. Role unions widen coverage and do not establish discrimination, calibration, incremental PFS or material Exact. No ticket additions or numeric effects are fitted from results.'}
    report['sha256'] = _sha(report)
    dump(args.output / 'report.json', report)
    print(json.dumps({k:v for k,v in report.items() if k!='races'}, ensure_ascii=False))


if __name__ == '__main__':
    main()

"""Read frozen evidence; explain the 16 positive-stake W misses without rescoring.

AKI categories are independently replayed from frozen indices and SOURCE and
must match the original compiler receipt. This diagnostic replay grants no
Production or forward-OOS authority. Existing candidate definitions stay fixed.
"""
from collections import Counter
from pathlib import Path
from statistics import median
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from jra_aki_v21_features import compile_features
from jra_role_rescue_shadow import build_role_rescue_shadow

D = ROOT / 'runtime/daily_reviews/JRA-2026-10-17'
INDICES = 'HPI SSI CFI RFI BVI JTI CSI TRI BWI GCI PRI KGI VMI DCR TPI ZAI_WIN ZAI_PLACE SRI F3S T3I'.split()
# Read-only decomposition of JRA-ZAI-WIN-v1.0, not an alternative score.
WEIGHTS = dict(HPI=.20, SSI=.17, CFI=.10, RFI=.08, JTI=.05, CSI=.05,
               TRI=.05, BWI=.05, GCI=.08, PRI=.12, KGI=.05)


def load(path):
    return json.loads((ROOT / path).read_text())


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main():
    ledger = load(D / 'audit_ledger.json')
    cohort = [r for r in ledger['races'] if (r.get('settlement') or {}).get('investment', 0) > 0]
    misses = [r for r in cohort if r['prediction']['W'] is False]
    assert len(cohort) == 19 and len(misses) == 16
    policy_path = 'profiles/jra_aki_v21_components_20261011_v1.json'
    policy = load(policy_path)['feature_compiler_policy']
    inputs = {}
    rows = []
    for r in misses:
        rid = r['race_id']; refs = r['artifact_refs']
        req, final, source = (load(refs[k]) for k in ('request', 'final', 'source'))
        for k in ('request', 'final', 'source'):
            inputs[refs[k]] = digest(refs[k])
        # This replay never reads the target result to build AKI features.
        replay = compile_features(req, source['artifact'], policy)
        assert replay['aki_compiler_receipt'] == req['aki_compiler_receipt'], rid
        winner = str(r['official_result']['top3'][0])
        by_id = {str(h['runner_id']): h for h in req['runners']}
        h = by_id[winner]; cc = h['canonical_components']
        ranking = final['static_prediction']['ranking']; head = str(ranking[0])
        headcc = by_id[head]['canonical_components']
        cells = {}
        for key in INDICES:
            item = cc[key]; value = item['value']
            field = [x['canonical_components'][key]['value'] for x in by_id.values()]
            better = sum(v > value for v in field); tied = sum(v == value for v in field)
            cells[key] = {'value': value, 'descending_rank_interval': [better + 1, better + tied],
                'tied_runner_count': tied, 'field_median': median(field), 'selected_head_value': headcc[key]['value'],
                'rule_id': item.get('rule_id'), 'mapping_version': item.get('mapping_version'),
                'source_fact': item.get('source_fact'),
                'evidence_count': len(item.get('evidence_refs', [])),
                'source_field': f'runners[runner_id={winner}].canonical_components.{key}',
                'components': [{k: v for k, v in c.items() if k != 'evidence_refs'} for c in item.get('components', [])]}
        assert len(cells) == 20
        delta = {k: round(w * (cc[k]['value'] - headcc[k]['value']), 8) for k, w in WEIGHTS.items()}
        assert abs(sum(delta.values()) - (cc['ZAI_WIN']['value'] - headcc['ZAI_WIN']['value'])) < .00002
        fact = replay['aki_selection_features']['runners'][winner]['W']
        raw = fact['source_fact']; trigger = req['aki_column_selection']['triggers']['W']
        checks = {'role_quality_floor': raw['value'] >= policy['role_quality_floor'],
            'at_least_two_support_groups': raw['support_group_count'] >= 2,
            'within_base_gap': raw['normalized_gap'] <= policy['column_gap']['W']['BASE'],
            'within_review_gap': raw['normalized_gap'] <= policy['column_gap']['W']['REVIEW']}
        registry = [x for x in req['role_registry'] if str(x['runner_id']) == winner and x['column'] == 'W']
        assert len(registry) == 1 and registry[0]['status'] == 'EXCLUDED'
        assert winner not in list(map(str, req['aki_column_selection']['columns']['W']))
        utility = r['krs']['utility']
        proposals = final['krs_prediction_utility'].get('actionable_role_proposals', [])
        rescue = [p for p in proposals if str(p.get('horse_no')) == winner and p.get('proposal') == 'ADD_W_SHADOW']
        shadow = build_role_rescue_shadow(final)
        selected = [p for p in shadow['selected_proposals'] if p['proposal'] == 'ADD_W_SHADOW']
        features = h.get('evidence_features') or {}
        insufficient = [k for k, v in cc.items() if v.get('information_status') == 'INFORMATION_INSUFFICIENT_DCR_ART3']
        pace = {k: v for k, v in features.items() if any(s in k.lower() for s in ('pace', 'position', 'closing', 'tactic', 'corner', 'running', 'sectional'))}
        bvi = cc['BVI']
        measured = [c for c in bvi.get('components', []) if any(str(x).startswith('JRA_PEDIGREE_CORPUS:') for x in c.get('evidence_refs', []))]
        classes = {
            'Evidence不足': {'state': 'OBSERVED_MISSING_COMPONENTS' if insufficient else 'NOT_ESTABLISHED_AS_CAUSE', 'missing_index_components': insufficient,
                'note': 'Computed indices and observed features do not prove predictive evidence sufficiency.'},
            'Numerical Discrimination不足': {'state': 'OBSERVED_RANK_MISS / CAUSAL_DEFECT_UNDETERMINED', 'zai_win_rank': ranking.index(winner) + 1},
            'Static Ranking不足': {'state': 'OBSERVED_RANK_MISS', 'winner_rank': ranking.index(winner) + 1},
            'AKI W列選定による脱落': {'state': 'OBSERVED_RULE_EXCLUSION / NOT_PROVEN_IMPLEMENTATION_BUG', 'category': fact['category'],
                'pre_aki_production_W_role_loss': 'UNDETERMINED: no separately bound pre-AKI Production role snapshot'},
            'KRS救済未活用': {'state': 'OBSERVED_UNUSED_FROZEN_W_RESCUE' if rescue else 'NO_ACTIONABLE_WINNER_RESCUE', 'production_conversion': 0},
            'Venue固有Mechanism不足': {'state': 'UNDETERMINED', 'canon_revision': 'HOLD', 'reason': 'No multi-day frozen venue-specific controlled contrast'}}
        rows.append({'race_id': rid, 'venue': r['venue'], 'winner': winner, 'winner_name': h.get('name'),
            'static_rank': ranking.index(winner) + 1, 'W_column': req['aki_column_selection']['columns']['W'],
            'first_material_failure': r['first_material_failure'], 'dominant_pfs_loss_owner': r['dominant_pfs_loss_owner'],
            'all20': cells, 'zai_win_gap_decomposition_against_static_head': {'head': head, 'weighted_base_value_deltas': delta,
                'notice': 'Existing formula contribution differences only; no recomputation or replacement of frozen scores; not causal effects.'},
            'aki': {'compiler_receipt_replay': 'EXACT_MATCH', 'winner_W_fact': fact, 'original_registry': registry[0],
                'trigger': trigger, 'existing_policy_checks': checks, 'policy_sha256': digest(policy_path)},
            'bvi': {'value': bvi['value'], 'coverage_weight': bvi.get('coverage_weight'), 'measured_pedigree_components': measured,
                'DCR_only': not bool(measured), 'direct_ZAI_WIN_coefficient': 0,
                'notice': 'Shared pedigree features may enter other base indices. BVI scalar contribution is not a causal prediction/PFS effect.'},
            'frozen_krs': {'rank_comparison': utility.get('rank_comparison'), 'winner_actionable_rescues': rescue,
                'one_per_column_selected_W': selected, 'selected_shadow_captures_winner': any(str(p['horse_no']) == winner for p in selected),
                'raw_output_ref': r['krs']['raw_output_ref'], 'raw_output_sha_verified': r['krs']['raw_output_sha_verified'],
                'winner_only_evaluation_includes_unique_first_place_in_dead_heat': r['official_result']['top3_display_order_is_not_unique'],
                'order_metrics_eligible': not r['official_result']['top3_display_order_is_not_unique']},
            'pre_race_pace_position_closing_evidence': pace, 'classification': classes,
            'artifact_refs': refs, 'source_snapshot_sha256': req['source_snapshot_sha256'],
            'temporal_eligibility': r['temporal_eligibility'], 'lane': 'POST_RESULT_DIAGNOSTIC / NOT_FORWARD_OOS'})
    out = {'profile': 'JRA-OCT17-WINNER-DISCOVERY-16-REVIEW-v1', 'cohort': '19 positive-stake frozen Production FINAL; 16 W misses',
        'production_policy_change': False, 'historical_forward_oos_credit': 0,
        'classification_note': 'Six axes overlap; observed exclusion does not prove causal overcompression. Winner-only KRS audit includes KYO12 unique first place; earlier order-eligible KRS aggregate excluded its ambiguous P2/P3. Do not replace those denominators.',
        'summary': {'cohort_count': len(cohort), 'winner_misses': len(rows), 'index_cells_traced': len(rows) * 20,
            'aki_compiler_exact_matches': len(rows), 'winner_W_categories': dict(Counter(x['aki']['winner_W_fact']['category'] for x in rows)),
            'failed_aki_checks': dict(Counter(k for x in rows for k, passed in x['aki']['existing_policy_checks'].items() if not passed)),
            'actionable_unused_winner_rescues': sum(bool(x['frozen_krs']['winner_actionable_rescues']) for x in rows),
            'one_per_column_shadow_winner_rescues': sum(x['frozen_krs']['selected_shadow_captures_winner'] for x in rows),
            'measured_bvi_winners': sum(not x['bvi']['DCR_only'] for x in rows)},
        'rows': rows, 'input_sha256': inputs, 'definition_sha256': {p: digest(p) for p in [policy_path,
            'runtime/jra_aki_v21_features.py', 'runtime/jra_index_provenance_builder.py', 'runtime/jra_role_rescue_shadow.py']}}
    (D / 'winner_discovery_16_review.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
    lines = ['# Winner Discovery 16件の証拠追跡', '', '正投資19件中のW候補外16件。20指数320セルを凍結値のまま追跡し、同値は順位区間で表示する。AKIの診断再実行は既存Compiler Receipt全体の一致を要求し、未知未来OOSへ算入しない。', '',
        '| Race | 勝馬 | Static順位 | W分類 / Trigger | 不成立条件 | KRS事前W救済 | 固定Shadow W救済 |', '|---|---|---:|---|---|---|---|']
    for x in rows:
        failures = ', '.join(k for k, v in x['aki']['existing_policy_checks'].items() if not v)
        lines.append(f"| {x['race_id']} | {x['winner']} {x['winner_name']} | {x['static_rank']} | {x['aki']['winner_W_fact']['category']} / {x['aki']['trigger']} | {failures} | {bool(x['frozen_krs']['winner_actionable_rescues'])} | {x['frozen_krs']['selected_shadow_captures_winner']} |")
    lines += ['', '詳細JSONに各馬20指数、選定Headとの差分、Rule、出典フィールド、血統Component、展開Evidence、KRS原提案、6軸分類を保存した。指数の弱さ、Static順位、規則どおりのW除外は同じ因果欠陥と断定しない。BVIは実利用と増分効用を分離し、Venueは全場HOLD。', '',
        '今回のWinner-only診断は京都12Rの一意な1着馬も評価する。既存KRS集計が同着のP2/P3・Orderを除外した母数は変更しない。KRS救済は未採用の事前Shadow提案でありProduction的中へ加算しない。固定one-per-columnが結果馬を選ばない場合も除外せず記録する。正解Pair/Thirdを持たない役割追加からTicketやPFSを生成しない。']
    (D / 'winner_discovery_16_review.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps(out['summary'], ensure_ascii=False))


if __name__ == '__main__':
    main()

"""Recover one fixed Owner's saved real execution into explicit S1/S2 PAPER.

This is an offline transport/verification entry, not a new Selection policy.
It never executes KRS, changes a prediction, grants SOURCE/Active/Owner scope,
or turns a PROTECT Third into an exact PURCHASE orientation.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

from runtime import local_fnb_research_runtime as original
from runtime import local_fnb_semantic_closure as semantic
from runtime.local_fnb_mec_failure_localization import paper_comparison
from runtime.local_fnb_r19_chat_readback import parse_intent
from runtime.jra_ticket_tree_renderer import render_ticket_tree
from runtime.minimum_efficient_coverage import validate_mec_plan

PROFILE = 'KM-FNB-SAVED-SINGLE-OWNER-PAPER-TICKETS-20261104-R15'
PROFILES = {
    'S1': 'profiles/local_fnb_pair_local_semantic_protection_research_v0.1_20261103.json',
    'S2': 'profiles/local_fnb_unknown_paths_protection_research_v0.1_20261103.json',
}
POLICY_PINS = {
    'S1': 'f742c0be96a0f8a3f60c7d64c0c2802285f156c51c6620fea15ab4b80eb3f26a',
    'S2': 'ab3a0e6398ed0463f03011ff9007379020699086c59105acff247ab8e4c742b2',
}
REQUIRED = ('original_provider_card.html', 'parsed_provider_card.json',
    'provider_reference_capture_and_scope.json', 'race_request.json',
    'numerical/numerical_materialization.json', 'numerical/all_horse_29_index_report.md',
    'observations.json', 'context.json', 'research_prediction.json', 'execution_claim.json',
    'krs/requested_input.json', 'krs/execution_input.json', 'krs/execution_output.json',
    'krs/research_krs_receipt.json', 'csv_research_execution_manifest.json')


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + '\n').encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def _require(ok, code):
    if not ok:
        raise ValueError('FNB_SAVED_PAPER_' + code)


def _clock(value):
    dt = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    _require(dt.tzinfo is not None, 'AWARE_CLOCK_REQUIRED')
    return dt


def verify_saved_run(folder, expected_files, *, observed_at):
    """Read the immutable originals and check their existing cross-stage binds.

    expected_files is the independently recovered archive inventory scoped to
    this Race. It is a byte identity input, never a signature/admission claim.
    """
    folder = Path(folder).resolve()
    raw, docs = {}, {}
    for name in REQUIRED:
        p = folder / name
        proof = expected_files.get(name) or {}
        _require(not p.is_symlink() and p.is_file() and p.resolve().is_relative_to(folder),
                 'ORIGINAL_MISSING:' + name)
        data = p.read_bytes()
        _require(proof.get('sha256') == sha(data) and proof.get('bytes') == len(data),
                 'ORIGINAL_SHA_MISMATCH:' + name)
        raw[name] = data
        if name.endswith('.json'):
            docs[name] = json.loads(data)
    pred = docs['research_prediction.json']
    ids = semantic._validate(pred)
    request, num = docs['race_request.json'], docs['numerical/numerical_materialization.json']
    context, packet = docs['context.json'], docs['observations.json']
    parsed, capture = docs['parsed_provider_card.json'], docs['provider_reference_capture_and_scope.json']
    claim, manifest = docs['execution_claim.json'], docs['csv_research_execution_manifest.json']
    identity = parsed['race_identity']
    for obj in (request, num, context, packet, manifest):
        _require(obj.get('race_id') == pred['race_id'], 'RACE_REVISION_MISMATCH')
    for key in ('race_date', 'race_no', 'venue_id', 'scheduled_post_at'):
        _require(identity.get(key) == request.get(key), 'RAW_RACE_IDENTITY_MISMATCH:' + key)
    _require({str(r['runner_id']) for r in num['runners']} == set(ids)
             and len(num['runners']) == len(ids), 'NUMERICAL_UNIVERSE_MISMATCH')
    _require({str(r['runner_id']) for r in context['runners']} == set(ids), 'CONTEXT_UNIVERSE_MISMATCH')
    for doc in (context, packet):
        _require(doc['sha256'] == semantic._sha({k:v for k,v in doc.items() if k != 'sha256'}),
                 'CONTEXT_OR_OBSERVATION_SELF_SHA_MISMATCH')
        _require(doc['source_snapshot_sha256'] == pred['source_snapshot_sha256']
                 and doc['source_freeze_at'] == pred['source_freeze_at'], 'SOURCE_REVISION_MISMATCH')
        _require(doc['raw_card_sha256'] == sha(raw['original_provider_card.html']), 'RAW_LINEAGE_MISMATCH')
    _require(pred['input_context_sha256'] == context['sha256'], 'STATIC_CONTEXT_BINDING_MISMATCH')
    _require(num['candidate_current_state']['source_snapshot_sha256'] == pred['source_snapshot_sha256'],
             'NUMERICAL_SOURCE_REVISION_MISMATCH')
    _require(capture['capture']['sha256'] == parsed['raw_sha256'] == sha(raw['original_provider_card.html']),
             'PROVIDER_RAW_SHA_MISMATCH')
    recipe = manifest['input_recipe']
    _require(claim['recipe'] == recipe, 'CLAIM_RECIPE_MISMATCH')
    _require(recipe['raw_sha256'] == parsed['raw_sha256']
             and recipe['numerical_sha256'] == sha(original.encoded(num))
             and manifest['numerical_original_sha256'] == sha(original.encoded(num))
             and recipe['request_sha256'] == semantic._sha(request), 'NUMERICAL_SOURCE_FREEZE_MISMATCH')
    for name in ('runtime/minimum_efficient_coverage.py',
                 'runtime/capital_policy.py', 'runtime/jra_ticket_tree_renderer.py',
                 'runtime/local_fnb_semantic_closure.py', 'profiles/family_user_capital_default_20261003_R1.json'):
        _require(recipe['code_pins'][name] == sha((original.REPO / name).read_bytes()),
                 'FROZEN_DEPENDENCY_DRIFT:' + name)
    _require(pred['model_code_sha256'] == original.MODEL_SHA == recipe['model_code_sha256']
             == sha((original.REPO/'runtime/local_fnb_context_static_candidate.py').read_bytes()), 'MODEL_CODE_MISMATCH')
    required = num['candidate_full_numerical_summary']['required_indices']
    _require(len(required) == len(set(required)) == 29, 'FULL29_MANIFEST_MISSING')
    for runner in num['runners']:
        cells = runner.get('canonical_components') or {}
        _require(set(cells) == set(required), 'FULL29_CELLS_MISSING')
        _require(all(c.get('terminal_status') in ('CALCULATED', 'RULED-NEUTRAL') for c in cells.values()),
                 'NUMERICAL_TERMINAL_UNRESOLVED')
    requested, executed = docs['krs/requested_input.json'], docs['krs/execution_input.json']
    receipt, output = docs['krs/research_krs_receipt.json'], docs['krs/execution_output.json']
    _require(requested == pred['PRE_KRS_input'], 'OLD_KRS_PREDICTION_REVISION')
    _require(original.engine_input_projection(requested) == original.engine_input_projection(executed),
             'KRS_EXECUTION_INPUT_CHANGED')
    _require(receipt.get('status') == 'EXECUTED_CANONICAL_KRS' and receipt.get('process_returncode') == 0
             and receipt.get('run_count') == 5000 and receipt.get('seed') == 1
             and receipt.get('engine_sha256') == original.ENGINE_SHA
             and receipt.get('parameter_map_sha256') == original.MAP_SHA
             and receipt.get('requested_input_sha256') == sha(raw['krs/requested_input.json'])
             and receipt.get('execution_input_sha256') == sha(raw['krs/execution_input.json'])
             and receipt.get('output_sha256') == sha(raw['krs/execution_output.json']), 'REAL_KRS_RECEIPT_MISMATCH')
    original._verify_output(output, requested)
    _require(_clock(pred['source_freeze_at']) <= _clock(pred['freeze_at'])
             <= _clock(receipt['started_at']) <= _clock(receipt['completed_at']) <= _clock(observed_at),
             'FROZEN_CLOCK_CHAIN_MISMATCH')
    _require(manifest.get('KRS') == receipt, 'KRS_MANIFEST_MISMATCH')
    return {'raw':raw, 'documents':docs, 'prediction':pred, 'numerical':num, 'context':context,
            'krs_output':output, 'request':request, 'original_files':deepcopy(expected_files)}


def selection_ledger(prediction, study, *, selected_at):
    """All Pair/Third slots retain original hypotheses plus explicit decisions."""
    ids = prediction['active_runners']
    unknown = semantic._unknown(prediction)
    heads = set(prediction['column_rankings']['W']['front'])
    selected = {tuple(p['pair_id'].split('>')):p for p in study['known_pair_scoped_subplans']}
    p2 = {r['head']:r['ranking'] for r in prediction['head_local_P2']}
    p3 = {(r['head'],r['second']):r['ranking'] for r in prediction['pair_conditioned_Third']}
    p2_index = {r['head']:i for i,r in enumerate(prediction['head_local_P2'])}
    p3_index = {(r['head'],r['second']):i for i,r in enumerate(prediction['pair_conditioned_Third'])}
    w_index = {r['runner_id']:i for i,r in enumerate(prediction['column_rankings']['W']['rows'])}
    is_s2 = study['profile'] == semantic.UNKNOWN_RESEARCH_POLICY
    pairs, thirds, head_rows = [], [], []
    common = {'race_id':prediction['race_id'], 'owner_id':prediction['model_id'],
        'source_sha256':prediction['source_snapshot_sha256'], 'static_model_sha256':prediction['model_code_sha256'],
        'static_prediction_sha256':prediction['sha256'], 'static_freeze':prediction['freeze_at'],
        'selection_rule_id':study['profile'], 'selection_policy_version':study['version'],
        'selection_freeze_at':selected_at, 'production_adopted':False}
    for h in ids:
        chosen = [s for s in ids if (h,s) in selected]
        head_rows.append({**common, 'head':h, 'material_pair_seconds':chosen,
            'winner_front_eligible':h in heads, 'unknown_possible':h in unknown,
            'head_disposition':'PROTECT' if chosen else 'UNRESOLVED_UNKNOWN' if h in unknown else
                'SELECTION_HOLD_KNOWN_HEAD_WITHOUT_PAIR' if h in heads else 'RESEARCH_NONFRONT_NONSELECTION_NOT_EXCLUSION',
            'closure_complete':bool(chosen) if h in heads or h in unknown else None})
        for s in ids:
            sub = selected.get((h,s))
            u = sorted({h,s} & unknown, key=int)
            if h == s:
                status, reason = 'STRUCTURAL_INELIGIBLE', 'DUPLICATE_FINISH_POSITION'
            elif sub:
                status = 'PROTECT'
                reason = 'EXPLICIT_UNKNOWN_POSSIBILITY_PROTECTION' if u else 'FIXED_MODEL_HEAD_LOCAL_PARETO_FRONT_PROTECTION'
            elif u and not is_s2:
                status, reason = 'UNRESOLVED_UNKNOWN', 'S1_DOES_NOT_SELECT_UNKNOWN_PATHS'
            else:
                status, reason = 'RESEARCH_NONSELECTION', 'OUTSIDE_DECLARED_FRONT_POLICY_NOT_ABILITY_OR_STRUCTURAL_EXCLUSION'
            local_rank = next((r for r in p2.get(h,{}).get('rows',[]) if r['runner_id'] == s), None)
            pairs.append({**common, 'head':h, 'second':s, 'head_local_p2_rank':deepcopy(local_rank),
                'winner_path':deepcopy(prediction['runner_world_stage_basis'].get(h)),
                'evidence_refs':(['research_prediction.json#/head_local_P2/' + str(p2_index[h])]
                    if h in p2_index else ['research_prediction.json#/column_rankings/W/rows/' + str(w_index[h])])
                    + ['context.json#/runners/' + str(ids.index(h)), 'context.json#/runners/' + str(ids.index(s))],
                'pair_eligibility':'DISTINCT_LISTED_RUNNERS_NOT_QUALIFIED_ACTIVE' if h != s else 'DUPLICATE',
                'material_selection_status':status, 'reason':reason, 'unknown_participants':u})
            effective = set(sub['effective_pair_scoped_p3']) if sub else set()
            for t in ids:
                u3 = sorted({h,s,t} & unknown, key=int)
                if len({h,s,t}) < 3:
                    state3, reason3 = 'STRUCTURAL_INELIGIBLE', 'DUPLICATE_FINISH_POSITION'
                elif sub and t in effective:
                    state3, reason3 = 'PROTECT', 'PAIR_LOCAL_OR_GLOBAL_FLOOR_SET_PROTECTION_NO_EXACT_PURCHASE'
                elif u3 and not is_s2:
                    state3, reason3 = 'UNRESOLVED_UNKNOWN', 'S1_DOES_NOT_SELECT_UNKNOWN_PATHS'
                else:
                    state3, reason3 = 'RESEARCH_NONSELECTION', 'OUTSIDE_DECLARED_PAIR_THIRD_POLICY_NOT_STRUCTURAL_EXCLUSION'
                rank3 = next((r for r in p3.get((h,s),{}).get('rows',[]) if r['runner_id'] == t), None)
                thirds.append({**common, 'head':h, 'second':s, 'third':t,
                    'pair_conditioned_p3_rank':deepcopy(rank3), 'material_selection_status':state3,
                    'reason':reason3, 'unknown_participants':u3,
                    'global_active_p3':t in prediction['column_rankings']['P3']['front'],
                    'pair_local_front':t in p3.get((h,s),{}).get('front',[]),
                    'evidence_refs':(['research_prediction.json#/pair_conditioned_Third/' + str(p3_index[(h,s)])]
                        if (h,s) in p3_index else ['research_prediction.json#/column_rankings/W/rows/' + str(w_index[h])])
                        + ['context.json#/runners/' + str(ids.index(t))], 'exact_orientation_purchase':False})
    missing = [r['head'] for r in head_rows if r['head'] in heads and not r['material_pair_seconds']]
    _require(not missing, 'MATERIAL_W_WITHOUT_PAIR:' + ','.join(missing))
    return {'profile':PROFILE + '-MATERIAL-SELECTION-LEDGER', **common,
        'heads':head_rows, 'pairs':pairs, 'thirds':thirds,
        'all_pair_slots':len(pairs), 'all_third_slots':len(thirds),
        'known_material_heads_closed':True, 'unknown_evidence_resolved':False,
        'unknown_selection_terminal_under_profile':is_s2,
        'structural_exclusion_is_duplicate_positions_only':True}


def construct_single_owner(inputs, *, authorization_ref, evaluated_at):
    """S1/S2 are two selection studies of ONE Owner, never B/C Owners."""
    pred = inputs['prediction']
    compared = paper_comparison(pred, evaluated_at=evaluated_at, authorization_ref=authorization_ref)
    results = {}
    for label, path in PROFILES.items():
        profile_bytes = (original.REPO / path).read_bytes()
        _require(sha(profile_bytes) == POLICY_PINS[label], 'SELECTION_PROFILE_DRIFT:' + label)
        profile = json.loads(profile_bytes)
        study = compared['studies'][profile['profile']]
        for sub in study['known_pair_scoped_subplans']:
            validate_mec_plan(sub['canonical_plan'])
            _require(not sub['canonical_plan']['uncovered_active_w_heads']
                     and not sub['canonical_plan']['orphan_thirds'], 'STRICT_SCOPED_MEC_NOT_CLOSED')
        ledger = selection_ledger(pred, study, selected_at=evaluated_at)
        methods = study['methods']
        for method, value in methods.items():
            roundtrip = render_ticket_tree({'final_ticket':{'tickets':value['tickets'],
                'no_bet':value['method_zero_selection']},
                'capital_policy_decision':{'decision':'AKI_REFERENCE_ONLY'},
                'final_prediction_package':{'validation_status':'UNVALIDATED'}})
            _require(roundtrip['text'] == value['canonical_tree'], 'CANONICAL_TREE_CHANGED')
            value['canonical_ticket_sha256'] = sha(encoded(value['tickets']))
            value['canonical_tree_sha256'] = sha(value['canonical_tree'].encode())
            value['reflattened_tickets'] = roundtrip['reflattened_tickets']
            value['material_exact_orientation_selected'] = False
            # Capital is advisory for an unadopted PAPER study. The full MEC
            # proposal is kept even if the existing hard budget returns PAPER.
            value['paper_ticket_computed'] = bool(value['tickets'])
            value['formal_selected_ticket'] = False
            value['computed_whole_race_no_bet'] = False
            value['available_unspent_cash'] = value['capital_limit']
        results[label] = {'profile':profile['profile'], 'profile_sha256':sha(profile_bytes),
            'profile_path':path, 'selection_module_sha256':sha((original.REPO/'runtime/local_fnb_semantic_closure.py').read_bytes()),
            'selection_freeze_at':evaluated_at, 'ledger':ledger, 'paper_result':study,
            'strict_pair_scoped_mec_verified':bool(study['known_pair_scoped_subplans']),
            'scope_is_paper_not_adopted_owner':True}
    request = inputs['request']
    expired = _clock(evaluated_at) >= _clock(request['prediction_cutoff'])
    return {'profile':PROFILE, 'race_id':pred['race_id'], 'revision':'R15.1-SAVED-PAPER-TICKETS',
        'recovery_code_sha256':sha(Path(__file__).read_bytes()),
        'classification':'POSTCUTOFF_DIAGNOSTIC_PAPER_NOT_OOS' if expired else
            'PRE_CUTOFF_UNQUALIFIED_LISTED_RUNNER_PAPER_NOT_RECOMMENDATION_NOT_OOS',
        'calculated_at':evaluated_at, 'scheduled_post_at':request['scheduled_post_at'],
        'prediction_cutoff':request['prediction_cutoff'], 'cutoff_basis':request.get('cutoff_basis'),
        'owner_count':1, 'owner_id':pred['model_id'], 'independent_BC':False,
        'source_snapshot_sha256':pred['source_snapshot_sha256'],
        'raw_sha256':sha(inputs['raw']['original_provider_card.html']),
        'source_fetched_at':pred['source_freeze_at'], 'static_freeze_at':pred['freeze_at'],
        'static_model_sha256':pred['model_code_sha256'], 'static_prediction_sha256':pred['sha256'],
        'krs_receipt':deepcopy(inputs['documents']['krs/research_krs_receipt.json']),
        'krs_reused_without_execution':True, 'new_krs_executions':0,
        'listed_count':len(pred['active_runners']), 'active_verified':False,
        'qualified_source':False, 'formal_owner_or_selection_adopted':False,
        'source_qualification_preserved':deepcopy(inputs['documents']['provider_reference_capture_and_scope.json']),
        'studies':results, 'original_strict_mec_hold_lifted':False,
        'formal_selected_ticket':False, 'computed_no_bet':False,
        'recipient_ack_verified':False, 'natural_delivery_verified':False,
        'actual_purchase':False, 'PFS':None, 'registered_OOS_increment':0}


def render_complete(inputs, recovered):
    pred, num, krs = inputs['prediction'], inputs['numerical'], inputs['krs_output']
    lines = ['# 船橋｜固定1 Owner・S1/S2独立PAPER全券面', '',
        '分類：' + recovered['classification'],
        '未採用SelectionのPAPER比較です。正式推薦・確定Active・実購入・配送ACKは成立していません。',
        'S1/S2は同じ予測Ownerへの別選択方針です。独立B/Cではなく、合算購入もしません。',
        'UNKNOWNは弱い馬という意味ではありません。SSR/LSR/Z4Rは未較正出現率で、実勝率・EVではありません。', '',
        '|項目|原本値|', '|---|---|']
    for key in ('race_id','revision','scheduled_post_at','prediction_cutoff','cutoff_basis','source_fetched_at',
        'source_snapshot_sha256','raw_sha256','static_freeze_at','static_model_sha256','static_prediction_sha256','calculated_at'):
        lines.append('|' + key + '|' + str(recovered.get(key)) + '|')
    lines += ['', f"掲載{recovered['listed_count']}頭。最終Active集合は未検証。KRSは保存済み5,000回・seed1を再利用し、新規実行0回。",
        '独立した第2予測Ownerは未成立です。以下は固定1 Ownerの全馬予測です。', '',
        '## 全馬W/P2/P3・UNKNOWN・KRS', '',
        '|馬番|馬名|W順位（範囲）|P2順位（範囲）|P3順位（範囲）|Role|SSR-W|SSR-P2|SSR-P3|LSR|Z4R-W/P2/P3|',
        '|---:|---|---|---|---|---|---:|---:|---:|---:|---|']
    kr = {str(r['horse_no']):r for r in krs['summary']}
    cr = {col:{r['runner_id']:r for r in pred['column_rankings'][col]['rows']} for col in ('W','P2','P3')}
    for runner in num['runners']:
        rid = str(runner['runner_id']); r = kr[rid]
        ranks = []
        for col in ('W','P2','P3'):
            row = cr[col][rid]; interval = row['rank_interval']
            ranks.append(f"{row['rank'] if row['rank'] is not None else 'UNKNOWN'}（{interval['min']}–{interval['max']}）")
        values = [str(rid), runner['name'], *ranks, ','.join(pred['roles'][rid]) or '既知非Front（構造除外ではない）',
            *[str(r[k]) for k in ('SSR-W','SSR-P2','SSR-P3','LSR')],
            '/'.join(str(r[k]) for k in ('Z4R-W','Z4R-P2','Z4R-P3'))]
        lines.append('|' + '|'.join(values) + '|')
    lines += ['', '## 展開・Head-local P2・Pair-conditioned Third',
        '展開は船橋過去走の通過順に基づく仮説です。現在の戦術意図・実測加速度・砂の影響・当日バイアスはUNKNOWN。']
    for r in inputs['context']['runners']:
        worlds = sorted({p['world_hypothesis'] for p in r.get('paths',[])})
        lines.append(f"- {r['runner_id']}番 {r['name']}：{','.join(worlds) or 'UNKNOWN'}／過去観測{r['input_observations']}走／6 Stage={json.dumps(r.get('stage_cost_topology'),ensure_ascii=False)}")
    for row in pred['head_local_P2']:
        lines.append(f"- W {row['head']} → Head-local P2：{','.join(row['ranking']['front']) or 'なし'}")
    for row in pred['pair_conditioned_Third']:
        lines.append(f"- Pair {row['head']}→{row['second']} → Third：{','.join(row['ranking']['front']) or 'なし'}")
    for label, result in recovered['studies'].items():
        study = result['paper_result']
        lines += ['', '## ' + label + '｜' + result['profile'],
            'Profile SHA：' + result['profile_sha256'], 'Module SHA：' + result['selection_module_sha256'],
            f"Material Pair {study['candidate_material_pair_count']}件／Pair-local Third {study['candidate_material_conditional_third_count']}件。",
            '全Pair/Third判断とStrict MEC実Request・Planは同梱JSONに全件保存。三連単のPURCHASE方向選択は0件。']
        for method in ('EXACTA','TRIO','TRIFECTA'):
            m = study['methods'][method]
            lines += ['', '### ' + {'EXACTA':'馬単','TRIO':'三連複','TRIFECTA':'三連単'}[method],
                f"{m['point_count']}点／全票100円／PAPER必要額 {m['paper_required_capital']:,}円／必要最小MEC {m['paper_required_capital']:,}円。",
                f"独立予算上限 {m['capital_limit']:,}円／仮に全票を選ぶ場合の未使用 {m['unused_capital']:,}円／超過 {m['capital_shortfall']:,}円。",
                f"Capital判定 {m['capital_policy']['decision']}。正式投資0円・実購入0円・未支出の現金枠 {m['available_unspent_cash']:,}円。",
                '結論：' + (m['zero_reason'] + '（この方式の計算済み0点。Race全体のNO-BETではない）' if m['method_zero_selection'] else
                    '予算超過PAPER。意味的被覆を圧縮せず全票を表示。' if m['capital_shortfall'] else 'PAPER券面計算済み。正式推薦ではない。'),
                'Ticket SHA：' + m['canonical_ticket_sha256'], 'Tree SHA：' + m['canonical_tree_sha256'],
                '', '```text', m['canonical_tree'], '```']
    lines += ['', '## 全馬29指数・各セル状態・欠測根拠', '',
        inputs['raw']['numerical/all_horse_29_index_report.md'].decode(), '',
        '## 到達・結論',
        '保存済み原本とKRSの実バイトを検証し、S1/S2のPAPER券面を生成しました。',
        'SOURCE資格・最終Active・FNB正式Owner・Selection採用・本人ACKは未成立。LEVEL 2/3、自然配送、正式NO-BET、正式PFSは0。',
        '三連単の非ゼロ生成には、着順方向をPURCHASEとして選択する別の判断根拠が必要です。既存PROTECT規則を変更していません。']
    return '\n'.join(lines) + '\n'


def recover(folder, expected_files, destination, *, authorization_ref, evaluated_at=None):
    _require(not any(os.environ.get(k,'').lower() not in ('','false','0') for k in ('CI','GITHUB_ACTIONS')),
             'REAL_PRIVATE_ORIGINALS_PUBLIC_CI_FORBIDDEN')
    evaluated_at = evaluated_at or datetime.now(timezone.utc).isoformat()
    _require(bool(authorization_ref), 'CURRENT_RESEARCH_AUTHORIZATION_REQUIRED')
    inputs = verify_saved_run(folder, expected_files, observed_at=evaluated_at)
    target = original._private_root(Path(destination).resolve() / inputs['prediction']['race_id'])
    receipt_path = target/'recovery_receipt.json'
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_bytes())
        for name, proof in receipt['files'].items():
            data = (target/name).read_bytes()
            _require(proof == {'bytes':len(data),'sha256':sha(data)}, 'SAVED_RECOVERY_SHA_MISMATCH:' + name)
        recovered = json.loads((target/'recovered_paper_tickets.json').read_bytes())
        _require(json.loads((target/'saved_inputs_inventory.json').read_bytes()) == expected_files
                 and recovered['race_id'] == inputs['prediction']['race_id']
                 and recovered['static_prediction_sha256'] == inputs['prediction']['sha256']
                 and recovered.get('recovery_code_sha256') == sha(Path(__file__).read_bytes())
                 and all(s['profile_sha256'] == POLICY_PINS[label] for label,s in recovered['studies'].items()),
                 'SAVED_RECOVERY_INPUT_REVISION_MISMATCH')
        return recovered, {**receipt, 'reused_existing_recovery':True}
    recovered = construct_single_owner(inputs, authorization_ref=authorization_ref, evaluated_at=evaluated_at)
    files = {'saved_inputs_inventory.json':encoded(expected_files),
        'recovered_paper_tickets.json':encoded(recovered),
        'COMPLETE_PREDICTION_AND_ALL_TICKETS.md':render_complete(inputs,recovered).encode()}
    inventory = {}
    for name, data in files.items():
        saved = original._immutable(target / name,data)
        _require((target/name).read_bytes() == data, 'LOCAL_READBACK_CHANGED')
        inventory[name] = {'bytes':len(data),'sha256':saved['sha256']}
    receipt = {'profile':PROFILE+'-READBACK', 'race_id':recovered['race_id'],
        'classification':recovered['classification'], 'calculated_at':evaluated_at,
        'original_files_verified':len(REQUIRED), 'files':inventory,
        'local_original_readback':True, 'new_krs_executions':0,
        'recipient_ack_verified':False, 'prestart_qualified_delivery_verified':False,
        'formal_selected_ticket':False, 'computed_no_bet':False,
        'S1_S2_not_two_owners':True, 'registered_OOS_increment':0}
    original._immutable(target/'recovery_receipt.json',encoded(receipt))
    return recovered, receipt


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--saved-root', required=True)
    p.add_argument('--archive-manifest-sha256', required=True)
    p.add_argument('--query', required=True)
    p.add_argument('--destination', required=True)
    p.add_argument('--authorization-ref', required=True)
    a = p.parse_args(argv)
    root = Path(a.saved_root).resolve()
    manifest_bytes = (root/'SHA256_MANIFEST.json').read_bytes()
    _require(sha(manifest_bytes) == a.archive_manifest_sha256, 'ARCHIVE_INVENTORY_SHA_MISMATCH')
    intent = parse_intent(a.query)
    prefix = 'executions/' + intent['race_date'].replace('-','') + f"/R{intent['race_no']:02d}/"
    manifest = json.loads(manifest_bytes)
    expected = {k[len(prefix):]:v for k,v in manifest.items() if k.startswith(prefix)}
    result, receipt = recover(root/prefix,expected,a.destination,authorization_ref=a.authorization_ref)
    print(json.dumps({'race_id':result['race_id'], 'classification':result['classification'],
        'owner_count':1,'new_krs_executions':0,'local_original_readback':receipt['local_original_readback'],
        'methods':{s:{k:v['point_count'] for k,v in r['paper_result']['methods'].items()}
            for s,r in result['studies'].items()},'formal_selected_ticket':False,'recipient_ack_verified':False}))


if __name__ == '__main__':
    main()

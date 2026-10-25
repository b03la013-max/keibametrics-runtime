"""Small, deterministic read model of an immutable signed JRA FINAL.

No dispatch, scoring, signing, purchase, notification or acknowledgement API.
Creation verifies the original. Readback verifies the original signatures with
the archived trusted public key and compares the saved display with that FINAL.
No live Health request, prediction calculation or new signature is involved.
"""
from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path

import base64
import re
from jra_ticket_tree_renderer import render_ticket_tree, BET_LABEL


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def text_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def archived_trust(final, root=None):
    """Reuse the existing witnessed signer, never a key supplied by a derivative.

    This snapshot is historical public verification material, not a claim that
    the current process is READY. Unknown keys require their own accepted
    archive; an arbitrary public key beside a Presentation is not a trust root.
    """
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    raw = (root / 'evidence/jra_bvi_phase3_20261017/runtime_health.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != 'e39b362fdf7def09e3cfdfb2a1a00e36e1feea2c4c29af75756973b5d3c35628':
        raise ValueError('JRA_PRESENTATION_ARCHIVED_TRUST_INVALID')
    health = json.loads(raw)['krs']['body']
    authority = final['final_prediction_package']['execution_stage_manifest']['SIGNED_SOURCE_RECEIPT_VERIFIED']['current_authority_manifest']
    if not re.fullmatch(r'KM-FAMILY-CURRENT-AUTHORITY-[0-9]{8}-R[0-9]+', authority):
        raise ValueError('JRA_PRESENTATION_AUTHORITY_INVALID')
    profile = json.loads((root / 'profiles' / (authority.replace('-', '_') + '.json')).read_text())
    if profile.get('manifest_id') != authority:
        raise ValueError('JRA_PRESENTATION_AUTHORITY_INVALID')
    contract = json.loads((root / profile['common_family_components']['family_runtime_contracts_profile']).read_text())['families']['JRA']
    return health, contract


def _receipt(envelope, signer, race, phase):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    r = envelope['receipt']
    if (envelope.get('receipt_sha256') != digest(r) or r.get('race_id') != race
            or envelope.get('signer_key_id') != signer['key_id']
            or envelope.get('signature_alg') != 'Ed25519'
            or r.get('errors') or r.get('status') != ('EXECUTED' if phase == 'KRS' else 'PASS')
            or (phase != 'KRS' and r.get('phase') != phase)):
        raise ValueError('JRA_PRESENTATION_RECEIPT_BINDING_INVALID:' + phase)
    Ed25519PublicKey.from_public_bytes(base64.b64decode(signer['public_key_b64'], validate=True)).verify(
        base64.b64decode(envelope['signature'], validate=True),
        json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())
    return {**r, 'signature_verified': True, 'receipt_sha256': envelope['receipt_sha256']}


def _fallback(final):
    # A failed pretty renderer must not lose the already frozen exact ledger.
    # Use the existing renderer's validator in normal operation. On an actual
    # rendering exception preserve every signed row verbatim without grouping.
    tickets = final['final_ticket']['tickets']
    seen = set()
    lines = ['買い目（正本券面の個別表示）']
    for t in tickets:
        b, s, stake = t['bet_type'], t['selection'], t['stake']
        n = 1 if b in ('WIN', 'PLACE') else 2 if b in ('WIDE', 'QUINELLA', 'EXACTA') else 3
        if (b not in BET_LABEL or len(s) != n or len(set(s)) != n
                or any(type(x) is not int or x < 1 for x in s)
                or type(stake) is not int or stake <= 0 or stake % 100):
            raise ValueError('JRA_PRESENTATION_TICKET_INVALID')
        key = (b, tuple(s) if b in ('EXACTA', 'TRIFECTA') else tuple(sorted(s)))
        if key in seen:
            raise ValueError('JRA_PRESENTATION_DUPLICATE_TICKET')
        seen.add(key)
        lines.append(f"{BET_LABEL[b]} {'→'.join(map(str, s))}　{stake}円")
    if final['final_ticket']['no_bet'] and tickets:
        raise ValueError('JRA_PRESENTATION_NO_BET_WITH_TICKETS')
    lines.append(f"合計 {len(tickets)}点・{sum(t['stake'] for t in tickets)}円")
    return '\n'.join(lines)


def build_presentation(final, *, health, contract, generated_at,
                       expected_race_id=None, expected_final_sha256=None,
                       expected_authority=None, _saved_fallback_error=None):
    from jra_delivery import verify_signed_final
    verify_signed_final(final, health, contract)
    p = final['final_prediction_package']
    source = p['execution_stage_manifest']['SIGNED_SOURCE_RECEIPT_VERIFIED']
    temporal = p['execution_stage_manifest']['PRE_FINAL_TEMPORAL_VERIFIED']
    authority = source['current_authority_manifest']
    for wanted, actual in ((expected_race_id, final['race_id']),
                           (expected_final_sha256, final['sha256']),
                           (expected_authority, authority)):
        if wanted is not None and wanted != actual:
            raise ValueError('JRA_PRESENTATION_EXPECTED_BASIS_MISMATCH')
    # Presentation never trusts unsigned convenience mirrors over signed data.
    if (final['static_prediction']['ranking'] != p['ranking']
            or final['static_prediction']['roles'] != p['roles']
            or final['capital_policy_decision'] != p['capital_policy_decision']
            or final['source_snapshot_sha256'] != p['source_snapshot_sha256']
            or final['scheduled_post_at'] != temporal['scheduled_post_at']
            or final['prediction_cutoff'] != source['prediction_cutoff']
            or final['venue_id'] != p['execution_stage_manifest']['VENUE_AUTHORITY_RESOLVED']['venue_canonical']
            or final['static_prediction'].get('aki_jra_v21') != (p.get('official_aki_verification') or {}).get('calculation')):
        raise ValueError('JRA_PRESENTATION_FINAL_MIRROR_MISMATCH')
    ledger = p.get('bvi_consumption_ledger') or {}
    for key in ('pair_dispositions', 'third_dispositions'):
        bound = (ledger.get('downstream_artifact_hashes') or {}).get(key)
        if not bound or bound != digest(final[key]):
            raise ValueError('JRA_PRESENTATION_SEMANTIC_BINDING_MISMATCH:' + key)
    receipts = {'FINAL': _receipt(final['final_receipt'], health['receipt_signer'], final['race_id'], 'FINAL'),
                'PRE_KRS': _receipt(final['pre_krs_receipt'], health['receipt_signer'], final['race_id'], 'PRE_KRS'),
                'KRS': _receipt(final['krs_run_receipt'], health['receipt_signer'], final['race_id'], 'KRS')}
    krs = receipts['KRS']
    if (krs.get('engine_sha256') != contract['engine_sha256']
            or krs.get('parameter_map_sha256') != contract['parameter_map_sha256']
            or krs['receipt_sha256'] != p['execution_stage_manifest']['KRS_EXECUTION_VERIFIED']['receipt_sha256']
            or receipts['PRE_KRS']['receipt_sha256'] != p['execution_stage_manifest']['PRE_KRS_VERIFIED']['receipt_sha256']
            or type(krs.get('actual_run_count')) is not int or krs['actual_run_count'] <= 0):
        raise ValueError('JRA_PRESENTATION_KRS_BINDING_INVALID')
    when = datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
    if when.tzinfo is None:
        raise ValueError('JRA_PRESENTATION_TIMEZONE_REQUIRED')
    mode, error = 'CANONICAL_TREE', None
    try:
        if _saved_fallback_error is not None:
            raise RuntimeError('Saved exact-ledger rendering mode')
        tree = render_ticket_tree(final)['text']
    except Exception as exc:
        tree = _fallback(final)
        mode, error = 'EXACT_TICKET_LEDGER_FALLBACK', type(exc).__name__ + ':' + str(exc)
        if _saved_fallback_error is not None:
            error = _saved_fallback_error
    capital = p['capital_policy_decision']
    status = 'PAPER' if capital.get('paper_only') or capital.get('decision') == 'PAPER' else 'NO_BET' if final['final_ticket']['no_bet'] else 'FINAL'
    names = {str(r['runner_id']): r.get('runner_name') for r in ledger.get('runners', [])}
    runners = p['index_provenance_replay']['runners']
    ranking = []
    for i, number in enumerate(p['ranking'], 1):
        r = runners[str(number)]
        indices = dict(r['base_final_values'])
        indices.update({k: r[v] for k, v in {'TPI':'tpi_final', 'SRI':'sri', 'F3S':'f3s',
                       'T3I':'t3i', 'DCR':'dcr_score', 'ZAI_WIN':'zai_win', 'ZAI_PLACE':'zai_place'}.items()})
        ranking.append({'rank': i, 'number': str(number), 'name': names.get(str(number)),
                        'indices': indices, 'roles': p['roles'].get(str(number), [])})
    tickets = deepcopy(final['final_ticket']['tickets'])
    count, total = len(tickets), sum(t['stake'] for t in tickets)
    if type(final['final_ticket'].get('total_investment')) is not int or total != final['final_ticket']['total_investment']:
        raise ValueError('JRA_PRESENTATION_FROZEN_TOTAL_MISMATCH')
    if len(p['ranking']) != len(set(map(str, p['ranking']))) or set(map(str, p['ranking'])) != set(runners):
        raise ValueError('JRA_PRESENTATION_RUNNER_UNIVERSE_MISMATCH')
    if any(len(r['indices']) != 20 for r in ranking):
        raise ValueError('JRA_PRESENTATION_FULL20_INCOMPLETE')
    if final['final_ticket']['no_bet'] and tickets:
        raise ValueError('JRA_PRESENTATION_NO_BET_WITH_TICKETS')
    base = 'https://github.com/b03la013-max/keibametrics-runtime/blob/main'
    final_url = base + '/runtime/final_artifacts/' + final['race_id'] + '.json'
    detail_url = base + '/runtime/jra_delivery/' + final['race_id'] + '/presentation_detail.json'
    # There is no notification or destination receipt in this publication path.
    delivery = {'FINAL_VERIFIED': True, 'RENDER_READY': True, 'CANONICAL_AVAILABLE': None,
                'NOTIFICATION_SENT': None, 'DESTINATION_ARRIVAL_CONFIRMED': None,
                'USER_ACKNOWLEDGED': None, 'state': 'DELIVERY_UNKNOWN',
                'user_delivery_verified': False, 'user_received_at': None,
                'actual_purchase_status': 'UNVERIFIED'}
    detail = {'race_id': final['race_id'], 'venue': final['venue_id'],
              'scheduled_post_at': final['scheduled_post_at'], 'prediction_cutoff': final['prediction_cutoff'],
              'temporal_mode': final['temporal_mode'], 'status': status, 'authority': authority,
              'validation_status': p.get('validation_status'), 'ranking': ranking,
              'aki': p.get('official_aki_package'), 'aki_calculation': p['official_aki_verification']['calculation'],
              'external_observation': p.get('aki_information_gate'),
              'columns': p.get('aki_column_selection'), 'roles': p['roles'],
              'pairs': final['pair_dispositions'], 'thirds': final['third_dispositions'],
              'tickets': tickets, 'ticket_count': count, 'total_investment': total,
              'by_bet_type': {b: {'count': sum(t['bet_type'] == b for t in tickets),
                                     'stake': sum(t['stake'] for t in tickets if t['bet_type'] == b)}
                              for b in sorted({t['bet_type'] for t in tickets})},
              'capital': capital, 'mec_reference': {'ticket_count': p['minimum_efficient_coverage']['ticket_count'],
                         'required_capital': p['minimum_efficient_coverage']['minimum_required_capital']},
              'numerical': p['actual_numerical_calculation'], 'receipts': receipts,
              'source': source, 'bvi_counts': ledger.get('counts'),
              'bvi_static_execution_proof': ledger.get('static_execution_proof'),
              'execution_stages': p['execution_stage_manifest'],
              'render_mode': mode, 'renderer_error': error, 'canonical_tree': tree,
              'generated_at': generated_at, 'presentation_before_post': when < datetime.fromisoformat(final['scheduled_post_at']),
              'delivery': delivery, 'final_url': final_url, 'detail_url': detail_url,
              'all_calculation_evidence': {'url': final_url, 'json_pointer': '/final_prediction_package/index_provenance_replay'}}
    lines = [f"{final['race_id']}／発走 {final['scheduled_post_at']}",
             f"正式状態 {status}／{final['temporal_mode']}／検証 {p.get('validation_status')}",
             f"Authority {authority}", '正式全馬順位（ZAI_WIN／ZAI_PLACE／TPI／BVI）']
    for r in ranking:
        v = r['indices']
        lines.append(f"{r['rank']}. {r['number']} {r['name'] or '馬名未収録'}：{v['ZAI_WIN']:.3f}／{v['ZAI_PLACE']:.3f}／{v['TPI']:.3f}／{v['BVI']:.3f}")
    lines += [f"AKI {detail['aki_calculation']['total']}／各軸 {detail['aki_calculation']['axes']}",
              f"W/P2/P3 {p['aki_column_selection']['columns']}",
              tree, f"Capital {capital['mode']}／{capital['decision']}／正式券面 {count}点・{total}円／実購入 UNVERIFIED",
              f"MEC参考 {detail['mec_reference']['ticket_count']}点・{detail['mec_reference']['required_capital']}円（正式券面と別）",
              f"Full20 {p['actual_numerical_calculation']['calculated_count']}/{p['actual_numerical_calculation']['required_count']}／外部KRS実行 {krs['actual_run_count']}／FINAL・PRE_KRS・KRS署名照合PASS",
              f"SOURCE {p['source_snapshot_sha256']}／BVI {ledger.get('counts')}",
              f"FINAL {final_url}", f"全20指数・Pair/Third・Receipt・実行証跡 {detail_url}",
              'Delivery：表示生成済み。公開読戻し・通知送信・到達・ACKは別証跡。ユーザー到達未検証。']
    text = '\n'.join(lines) + '\n'
    proof = ledger.get('static_execution_proof') or {}
    manifest = {'profile': 'KM-JRA-FINAL-PRESENTATION-v1', 'race_id': final['race_id'],
                'execution_id': source['execution_id'], 'authority': authority,
                'final_sha256': final['sha256'], 'final_receipt_sha256': final['final_receipt_sha256'],
                'source_sha256': p['source_snapshot_sha256'], 'source_receipt_sha256': source['receipt_sha256'],
                'policy_sha256': proof.get('owner_code_sha256'), 'policy_fingerprint': proof.get('policy_fingerprint'),
                'generated_at': generated_at, 'text_sha256': text_hash(text), 'detail_sha256': digest(detail),
                'signature_verified_at_creation': True, 'new_signature_issued': False,
                'user_delivery_verified': False}
    manifest['sha256'] = digest(manifest)
    return {'manifest': manifest, 'detail': detail, 'text': text}


def _read_saved(directory, *, expected_race_id=None, expected_final_sha256=None):
    out = Path(directory)
    m = json.loads((out / 'presentation.json').read_text())
    d = json.loads((out / 'presentation_detail.json').read_text())
    text = (out / 'presentation.md').read_text()
    if (m.get('sha256') != digest({k:v for k,v in m.items() if k != 'sha256'})
            or m.get('text_sha256') != text_hash(text) or m.get('detail_sha256') != digest(d)
            or m.get('race_id') != d.get('race_id')
            or (expected_race_id is not None and m['race_id'] != expected_race_id)
            or (expected_final_sha256 is not None and m['final_sha256'] != expected_final_sha256)):
        raise ValueError('JRA_PRESENTATION_SAVED_BINDING_INVALID')
    return {'manifest': m, 'detail': d, 'text': text}


def read_presentation(directory, *, final, expected_race_id=None,
                      expected_final_sha256=None, expected_authority=None, root=None):
    """Return stored bytes only after validating their signed canonical basis.

    Re-projecting the frozen values checks the derivative; it never runs SOURCE,
    scoring, KRS, ticket construction, Capital, signing or publication.
    """
    saved = _read_saved(directory, expected_race_id=expected_race_id,
                        expected_final_sha256=expected_final_sha256)
    health, contract = archived_trust(final, root)
    detail = saved['detail']
    mode = detail.get('render_mode')
    if mode not in {'CANONICAL_TREE', 'EXACT_TICKET_LEDGER_FALLBACK'}:
        raise ValueError('JRA_PRESENTATION_RENDER_MODE_INVALID')
    fallback_error = detail.get('renderer_error') if mode == 'EXACT_TICKET_LEDGER_FALLBACK' else None
    if mode == 'EXACT_TICKET_LEDGER_FALLBACK' and not isinstance(fallback_error, str):
        raise ValueError('JRA_PRESENTATION_RENDER_MODE_INVALID')
    expected = build_presentation(final, health=health, contract=contract,
        generated_at=saved['manifest']['generated_at'], expected_race_id=expected_race_id,
        expected_final_sha256=expected_final_sha256, expected_authority=expected_authority,
        _saved_fallback_error=fallback_error)
    if saved != expected:
        raise ValueError('JRA_PRESENTATION_CANONICAL_PROJECTION_MISMATCH')
    return saved


def save_presentation(directory, bundle):
    out = Path(directory)
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'presentation.json').exists():
        old = _read_saved(out, expected_race_id=bundle['manifest']['race_id'],
                                expected_final_sha256=bundle['manifest']['final_sha256'])
        for key in set(old['detail']) | set(bundle['detail']):
            if key not in ('generated_at', 'presentation_before_post') and old['detail'].get(key) != bundle['detail'].get(key):
                raise ValueError('JRA_PRESENTATION_IMMUTABLE_CONTENT_CONFLICT:' + key)
        if old['text'] != bundle['text']:
            raise ValueError('JRA_PRESENTATION_IMMUTABLE_TEXT_CONFLICT')
        # Saved generation time is immutable; a retry returns original bytes.
        return old
    if (out / 'presentation_detail.json').exists():
        # Recover an interrupted multi-file write using its original creation
        # time only when all immutable content agrees with the verified FINAL.
        old = json.loads((out / 'presentation_detail.json').read_text())
        for key in set(old) | set(bundle['detail']):
            if key not in ('generated_at', 'presentation_before_post') and old.get(key) != bundle['detail'].get(key):
                raise ValueError('JRA_PRESENTATION_PARTIAL_WRITE_CONFLICT:' + key)
        bundle = deepcopy(bundle)
        bundle['detail'] = old
        bundle['manifest']['generated_at'] = old['generated_at']
        bundle['manifest']['detail_sha256'] = digest(old)
        bundle['manifest']['sha256'] = digest({k:v for k,v in bundle['manifest'].items() if k != 'sha256'})
    for name, body in [('presentation_detail.json', json.dumps(bundle['detail'], ensure_ascii=False, sort_keys=True, indent=2)+'\n'),
                       ('presentation.md', bundle['text']),
                       ('presentation.json', json.dumps(bundle['manifest'], ensure_ascii=False, sort_keys=True, indent=2)+'\n')]:
        path = out / name
        if path.exists() and path.read_text() != body:
            raise ValueError('JRA_PRESENTATION_PARTIAL_WRITE_CONFLICT')
        path.write_text(body)
    return bundle


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Read saved presentation; no execution or notification.')
    parser.add_argument('--directory', required=True)
    parser.add_argument('--expected-race-id', required=True)
    parser.add_argument('--expected-final-sha256', required=True)
    parser.add_argument('--final', required=True)
    parser.add_argument('--expected-authority')
    args = parser.parse_args()
    print(read_presentation(args.directory, final=json.loads(Path(args.final).read_text()),
                            expected_race_id=args.expected_race_id,
                            expected_final_sha256=args.expected_final_sha256,
                            expected_authority=args.expected_authority)['text'], end='')

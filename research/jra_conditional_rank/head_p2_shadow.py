"""Four-parameter residual head/P2 interaction. Research only; no runner wiring."""
import json, math, hashlib
from pathlib import Path
from datetime import datetime, timezone
from probability_shadow import scores, softmax, forecast, instant, sha

ROOT = Path(__file__).resolve().parents[2]
ID = 'JRA-HEAD-P2-INTERACTION-20261018-R1'
FEATURES = ('position_quality', 'pace_resilience', 'closing_quality', 'course_geometry_fit')
MAPPING = ROOT / 'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json'
POLICY = {'candidate_id': ID, 'feature_pairs': [[0, 0], [1, 2], [2, 0], [3, 3]],
          'normalization': '(registered category score - 50)/50; unavailable interaction=0, not WEAK',
          'loss': 'race-balanced conditional P2 softmax NLL with frozen rank offset',
          'l2': 1., 'iterations': 500, 'step': .15, 'temperature': 1.,
          'third': 'unchanged exclusion-only P3', 'purchase_authority': False,
          'production_effect': 'NONE', 'automatic_promotion': False}


def evidence_vectors(runners):
    scale = json.loads(MAPPING.read_text())['category_scale']
    out, missing = {}, {}
    for runner in runners:
        rid = str(runner['runner_id'])
        if rid in out:
            raise ValueError('HEAD_P2_DUPLICATE_RUNNER')
        vals, absent = [], []
        for key in FEATURES:
            item = runner.get('evidence_features', {}).get(key, {})
            usable = (item.get('result_derived') is False and item.get('evidence_refs')
                      and item.get('category') in scale and item.get('source_authority') == 'JRA_OFFICIAL')
            vals.append((scale[item['category']] - 50) / 50 if usable else None)
            if not usable:
                absent.append(key)
        out[rid], missing[rid] = vals, absent
    return out, missing


def interaction(x, head, second):
    if head == second or head not in x or second not in x:
        raise ValueError('HEAD_P2_INVALID_PAIR')
    return [x[head][a] * x[second][b] if x[head][a] is not None and x[second][b] is not None else 0.
            for a, b in POLICY['feature_pairs']]


def fit_interaction(rows, base_model):
    from evidence_feature_compiler import verify_attestation
    expected = base_model['rank_model']['training_manifest']
    if not rows or {r['race_id'] for r in rows} != {r['race_id'] for r in expected} or len(rows) != len(expected):
        raise ValueError('HEAD_P2_TRAINING_MANIFEST')
    by_id = {m['race_id']: m for m in expected}
    cache = []
    bindings = []
    for row in rows:
        m = by_id[row['race_id']]
        if (row['q']['source_snapshot_sha256'] != m['source_sha256']
                or row['f']['sha256'] != m['final_sha256'] or sha(row['r']) != m['result_sha256']):
            raise ValueError('HEAD_P2_TRAINING_CONTENT')
        q, f, result = row['q'], row['f'], row['r']
        if (f['sha256'] != sha({k:v for k,v in f.items() if k != 'sha256'})
                or any(obj.get('race_id') != row['race_id'] for obj in (q, f, result))
                or row['top3'] != list(map(str, result['official_result']['top3']))
                or row['runners'] != q['runners'] or f['source_snapshot_sha256'] != m['source_sha256']
                or result['frozen_prediction_ref']['immutable_final_sha256'] != f['sha256']):
            raise ValueError('HEAD_P2_FROZEN_LABEL_INPUT_BINDING')
        att = verify_attestation(f['evidence_feature_compiler_attestation'], row['race_id'], m['source_sha256'],
                                 row['runners'], json.loads(MAPPING.read_text()))
        replay = f['final_prediction_package']['index_provenance_replay']['runners']
        derived = {'DCR':'dcr_score','TPI':'tpi_final','ZAI_WIN':'zai_win', 'ZAI_PLACE':'zai_place',
                   'SRI':'sri','F3S':'f3s','T3I':'t3i'}
        for runner in row['runners']:
            frozen = replay[str(runner['runner_id'])]
            for key, part in runner['canonical_components'].items():
                expected_value = frozen[derived[key]] if key in derived else frozen['base_final_values'][key]
                if abs(part['value']-expected_value) > 2e-6:
                    raise ValueError('HEAD_P2_FROZEN_FULL20_BINDING')
        bindings.append({'race_id':row['race_id'],'request_sha256':sha(q),'compiler_attestation_sha256':att['sha256']})
        x, _ = evidence_vectors(row['runners'])
        h, target = row['top3'][:2]
        offset = scores(row['runners'], base_model['rank_model'])['P2']
        features = {s: interaction(x, h, s) for s in x if s != h}
        cache.append((features, offset, target))
    weights = [0.] * 4
    for _ in range(POLICY['iterations']):
        grad = weights.copy()  # fixed L2=1
        for features, offset, target in cache:
            p = softmax({s: offset[s] + sum(a*b for a, b in zip(weights, v)) for s, v in features.items()}, 1.)
            for j in range(4):
                grad[j] += (sum(p[s]*features[s][j] for s in p)-features[target][j]) / len(cache)
        weights = [w-POLICY['step']*g for w, g in zip(weights, grad)]
    model = {'candidate_id': ID, 'weights': weights, 'policy': POLICY, 'policy_sha256': sha(POLICY),
             'base_model_sha256': base_model['sha256'], 'mapping_sha256': hashlib.sha256(MAPPING.read_bytes()).hexdigest(),
             'training_manifest': expected, 'created_at': datetime.now(timezone.utc).isoformat(),
             'training_input_bindings':bindings,
             'designed_after_oct18_results': True, 'oos_eligible': False, 'production_effect': 'NONE'}
    model['sha256'] = sha(model)
    return model


def predict(runners, base_model, model):
    if (base_model.get('sha256') != sha({k:v for k,v in base_model.items() if k != 'sha256'})
            or base_model['rank_model'].get('sha256') != sha({k:v for k,v in base_model['rank_model'].items() if k != 'sha256'})
            or model.get('sha256') != sha({k:v for k,v in model.items() if k != 'sha256'})
            or model.get('candidate_id') != ID or model.get('policy_sha256') != sha(POLICY)
            or sha(model.get('policy')) != sha(POLICY)
            or model.get('base_model_sha256') != base_model['sha256']
            or model.get('training_manifest') != base_model['rank_model']['training_manifest']
            or model.get('mapping_sha256') != hashlib.sha256(MAPPING.read_bytes()).hexdigest()):
        raise ValueError('HEAD_P2_MODEL_BINDING')
    w = model['weights']
    if len(w) != 4 or any(type(v) not in (int, float) or not math.isfinite(v) for v in w):
        raise ValueError('HEAD_P2_WEIGHTS')
    sc = scores(runners, base_model['rank_model'])
    x, missing = evidence_vectors(runners)
    p = softmax(sc['W'], 1.)
    p2, p3, joint = {}, {}, {}
    marg = {role: {h: 0. for h in p} for role in ('W', 'P2', 'P3')}
    marg['W'] = p.copy()
    for h, ph in p.items():
        logits = {s: sc['P2'][s]+sum(a*b for a, b in zip(w, interaction(x, h, s))) for s in p if s != h}
        p2[h] = softmax(logits, 1.)
        for s, ps in p2[h].items():
            key = h+'>'+s
            p3[key] = softmax(sc['P3'], 1., (h, s))
            marg['P2'][s] += ph*ps
            for t, pt in p3[key].items():
                joint[key+'>'+t] = ph*ps*pt
                marg['P3'][t] += ph*ps*pt
    return {'marginals': marg, 'head_p2': p2, 'pair_third': p3, 'ordered_joint': joint,
            'missing_evidence': missing, 'evidence_input_sha256': sha(x)}


def freeze(request, base_model, model, *, observed_at=None):
    # Reuse existing strict chronology/manifest guards. Inference never receives RESULT.
    base = forecast(request, base_model, observed_at=observed_at)
    created = instant(model['created_at'])
    if not instant(base_model['created_at']) <= created < instant(request['source_snapshot']['source_freeze_at']):
        raise ValueError('HEAD_P2_NOT_BEFORE_SOURCE')
    out = predict(request['runners'], base_model, model)
    for key in ('race_id', 'source_sha256', 'runner_universe_sha256', 'prediction_cutoff', 'observed_at'):
        out[key] = base[key]
    out.update(candidate_id=ID, model_sha256=model['sha256'], policy_sha256=sha(POLICY),
               code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               base_code_sha256=base['code_sha256'], production_effect='NONE',
               oos_eligible=False, ev_kelly_authority=False, tickets_created=0,
               status='RESEARCH_ONLY_NO_AUTOMATIC_RUNNER_CONNECTION')
    out['sha256'] = sha(out)
    return out

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


EXPOSURE_POLICY = {'candidate_id':'JRA-HEAD-P2-EQUAL-EXPOSURE-20261018-R1',
                  'ordering':'EXACTA joint W/P2 mass; TRIFECTA joint mass; TRIO sum over orientations; numeric tie-break',
                  'exposure':'same bet-type counts and original stake multiset, no added capital',
                  'probabilities_calibrated':False, 'ev_kelly_authority':False,
                  'production_effect':'NONE', 'automatic_promotion':False}


def matched_exposure(distribution, final):
    """Research allocation for the existing unit/interaction models, never an EV decision.

    Identical ordering is applied to both arms. A known-outcome replay is exploration,
    and this function cannot create a forward freeze or purchase instruction.
    """
    from itertools import permutations
    from collections import Counter
    if final.get('sha256') != sha({k:v for k,v in final.items() if k!='sha256'}):
        raise ValueError('HEAD_EXPOSURE_FINAL_HASH')
    ids=set(map(str,final['static_prediction']['ranking']))
    if len(ids)<3 or set(distribution['marginals']['W'])!=ids:
        raise ValueError('HEAD_EXPOSURE_UNIVERSE')
    def probability_vector(values, universe):
        if (set(values)!=universe or any(type(v) not in (int,float) or not math.isfinite(v)
                or not 0<=v<=1 for v in values.values()) or abs(sum(values.values())-1.)>1e-8):
            raise ValueError('HEAD_EXPOSURE_PROBABILITY_VECTOR')
    if set(distribution['marginals'])!={'W','P2','P3'}:
        raise ValueError('HEAD_EXPOSURE_MARGINAL_ROLES')
    for values in distribution['marginals'].values():probability_vector(values,ids)
    joint=distribution['ordered_joint']
    expected={'>'.join(p) for p in permutations(ids,3)}
    if set(joint)!=expected or set(distribution['head_p2'])!=ids:
        raise ValueError('HEAD_EXPOSURE_JOINT_UNIVERSE')
    orders={kind:{} for kind in ('EXACTA','TRIO','TRIFECTA')}
    for h in ids:
        p2=distribution['head_p2'][h]
        probability_vector(p2,ids-{h})
        for s in p2:
            thirds=distribution['pair_third'][h+'>'+s]
            probability_vector(thirds,ids-{h,s})
            pair=distribution['marginals']['W'][h]*p2[s]
            orders['EXACTA'][(int(h),int(s))]=pair
            for t,pt in thirds.items():
                key=(int(h),int(s),int(t));mass=joint[h+'>'+s+'>'+t]
                if (type(mass) not in (int,float) or not math.isfinite(mass) or mass<0
                        or abs(mass-pair*pt)>1e-10):raise ValueError('HEAD_EXPOSURE_JOINT_MASS')
                orders['TRIFECTA'][key]=mass
                trio=tuple(sorted(key));orders['TRIO'][trio]=orders['TRIO'].get(trio,0.)+mass
    if abs(sum(joint.values())-1.)>1e-8:raise ValueError('HEAD_EXPOSURE_NORMALIZATION')
    for i,role in enumerate(('W','P2','P3')):
        for horse in ids:
            mass=sum(p for key,p in joint.items() if key.split('>')[i]==horse)
            if abs(mass-distribution['marginals'][role][horse])>1e-8:
                raise ValueError('HEAD_EXPOSURE_MARGINAL_MASS')
    tickets=final['final_ticket']['tickets'];keys=[]
    for ticket in tickets:
        kind=ticket['bet_type'];sel=tuple(ticket['selection']);stake=ticket['stake']
        if (kind not in orders or type(stake) is not int or stake<=0 or stake%100
                or sel not in orders[kind] or (kind,sel) in keys):
            raise ValueError('HEAD_EXPOSURE_BASELINE_TICKET')
        keys.append((kind,sel))
    if sum(t['stake'] for t in tickets)!=final['final_ticket']['total_investment']:
        raise ValueError('HEAD_EXPOSURE_BASELINE_BUDGET')
    out=[]
    for kind in orders:
        originals=[t for t in tickets if t['bet_type']==kind]
        ranked=sorted(orders[kind],key=lambda sel:(-orders[kind][sel],sel))
        out.extend({'bet_type':kind,'selection':list(sel),'stake':t['stake']}
                   for sel,t in zip(ranked,originals))
    assert Counter((t['bet_type'],t['stake']) for t in out)==Counter((t['bet_type'],t['stake']) for t in tickets)
    result={'policy':EXPOSURE_POLICY,'policy_sha256':sha(EXPOSURE_POLICY),
            'baseline_final_sha256':final['sha256'], 'race_id':final['race_id'],
            'source_sha256':final['source_snapshot_sha256'],
            'tickets':out,'ticket_count':len(out),'required_capital':sum(t['stake'] for t in out),
            'added_capital':0,'purchase_authority':False,'oos_eligible':False,
            'classification':'RESEARCH_COMPARISON_REQUIRES_SEPARATE_PRE_RESULT_FREEZE'}
    result['sha256']=sha(result)
    return result

"""Owner-enacted v2.1 evidence compiler; no probabilities or synthetic facts.

Full20 is verified upstream. SOURCE is never modified or re-signed. Derived
categories carry the original SOURCE hash and Full20 dependency digest.
"""
from copy import deepcopy
from statistics import pstdev
import math
from jra_aki_capital_preflight import AKICapitalError, sha
from jra_aki_v21 import _time


def compile_features(request, source, policy):
    if request.get('source_snapshot_sha256') != source.get('source_snapshot_sha256'):
        raise AKICapitalError('AKI_COMPILER_SOURCE_MISMATCH')
    cutoff = _time(source['prediction_cutoff'])
    if _time(source['source_freeze_at']) > cutoff:
        raise AKICapitalError('AKI_COMPILER_LATE_SOURCE')
    rows = request.get('runners') or []
    values, refs = {}, {}
    required = policy['required_indices']
    for row in rows:
        rid = str(row['runner_id'])
        if rid in values:
            raise AKICapitalError('AKI_COMPILER_DUPLICATE_RUNNER')
        cc = row.get('canonical_components') or {}
        if set(cc) != set(required):
            raise AKICapitalError('AKI_COMPILER_FULL20_INCOMPLETE:' + rid)
        values[rid], refs[rid] = {}, []
        for key in required:
            component = cc[key]
            v = component.get('value')
            if (isinstance(v, bool) or not isinstance(v, (int, float))
                    or not math.isfinite(v) or not 0 <= v <= 100
                    or not component.get('rule_id') or not component.get('mapping_version')
                    or not component.get('source_fact') or not component.get('evidence_refs')):
                raise AKICapitalError('AKI_COMPILER_INDEX_INVALID:' + rid + ':' + key)
            values[rid][key] = v
            refs[rid].extend(component['evidence_refs'])
    if len(values) < 3:
        raise AKICapitalError('AKI_COMPILER_INSUFFICIENT_FIELD')
    dependency = sha(rows)
    # Compact lineage references, with complete index provenance still retained
    # in request runners. Never copy the entire SOURCE into every combination.
    def fact(category, raw, evidence=None):
        return {'status': 'OBSERVED', 'category': category,
                'source_snapshot_sha256': source['source_snapshot_sha256'],
                'observed_at': source['source_freeze_at'],
                'evidence_refs': evidence or ['FULL20:' + dependency],
                'source_fact': raw, 'dependency_sha256': dependency,
                'derivation': 'OWNER_ENACTED_FULL20_OR_SIGNED_SOURCE_CATEGORY'}
    def band(x, edges):
        return 'LOW' if x < edges[0] else 'MID' if x < edges[1] else 'HIGH'
    metric = {'W': 'ZAI_WIN', 'P2': 'ZAI_PLACE', 'P3': 'T3I'}
    ranks = {c: sorted(values, key=lambda r: (-values[r][k], r)) for c,k in metric.items()}
    # Use the competitive upper half. A weak outlier must not inflate every
    # near-contender margin and cause a full-field ticket expansion.
    scales = {c: max(policy['dispersion_floor'], pstdev(
        [values[r][k] for r in ranks[c][:(len(values)+1)//2]]))
        for c,k in metric.items()}
    gaps = {c: {r: (values[ranks[c][0]][metric[c]] - v[metric[c]]) / scales[c]
                for r,v in values.items()} for c in metric}
    top = ranks['W'][0]
    facts = {}
    for c in metric:
        rank = ranks[c]
        gap = gaps[c][rank[1]]
        near = sum(gaps[c][r] <= policy['near_gap'] for r in rank[1:])
        facts[c + '_separation'] = fact(band(gap, policy['separation_edges']),
                                             {'normalized_top_gap': gap, 'scale': scales[c], 'metric': metric[c]})
        facts[c + '_density'] = fact(band(near, policy['density_edges']), {'near_rivals': near})
    for name, keys in policy['axis_evidence_groups'].items():
        quality = min(values[top][k] for k in keys)
        facts[name] = fact(band(quality, policy['quality_edges']), {'axis': top, 'indices': {k: values[top][k] for k in keys}})
    for c in ('P2','P3'):
        # Independent place-capable contenders outside the tight W cluster.
        threats = sum(gaps[c][r] <= policy['tail_threat_gap'] and gaps['W'][r] > policy['near_gap']
                      and sum(values[r][k] >= policy['support_floor'] for k in policy['support_groups'][c]) >= 2
                      for r in values)
        facts[c + '_tail_threats'] = fact(band(threats, policy['tail_threat_edges']), {'supported_tail_threat_count': threats})
    inversions = sum((ranks['W'].index(a)-ranks['W'].index(b)) *
                     (ranks['P3'].index(a)-ranks['P3'].index(b)) < 0
                     for i,a in enumerate(ranks['W']) for b in ranks['W'][i+1:])
    discordance = inversions / (len(values)*(len(values)-1)/2)
    facts['rank_discordance'] = fact(band(discordance, policy['discordance_edges']), {'kendall_inversion_fraction': discordance})
    conflicts = source.get('conflicts') or []
    facts['source_conflict'] = fact('HIGH' if conflicts else 'LOW', {'signed_source_conflicts': conflicts}, ['SOURCE:' + source['source_snapshot_sha256']])
    # A single snapshot cannot prove external stability. Availability has an
    # explicit category and epistemic gate; its risk charge is not a measured
    # odds/going change or a calibrated probability.
    series = source.get('aki_external_observations') or []
    external = 'UNOBSERVABLE'
    if series:
        if len(series) < 2:
            raise AKICapitalError('AKI_EXTERNAL_TWO_OBSERVATIONS_REQUIRED')
        previous = None
        for obs in series:
            at = _time(obs.get('observed_at'))
            if (at > min(cutoff,_time(source['source_freeze_at'])) or (previous is not None and at <= previous)
                    or obs.get('production_fact_authority') is not True
                    or obs.get('source_authority') != 'JRA_OFFICIAL'
                    or not obs.get('evidence_refs') or not obs.get('source_fact')
                    or not isinstance(obs.get('win_odds'), dict) or set(obs['win_odds']) != set(values)
                    or not obs.get('going')):
                raise AKICapitalError('AKI_EXTERNAL_OBSERVATION_INVALID')
            for v in obs['win_odds'].values():
                if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v <= 0:
                    raise AKICapitalError('AKI_EXTERNAL_ODDS_INVALID')
            previous = at
        first, last = series[0], series[-1]
        if (_time(last['observed_at'])-_time(first['observed_at'])).total_seconds() < policy['external_min_interval_seconds']:
            raise AKICapitalError('AKI_EXTERNAL_INTERVAL_TOO_SHORT')
        change = max(abs(last['win_odds'][r]/first['win_odds'][r]-1) for r in values)
        external = 'HIGH' if first['going'] != last['going'] else band(change,policy['external_change_edges'])
        raw_external = {'max_odds_relative_change': change, 'going_before': first['going'], 'going_after': last['going']}
        erefs = sorted(set(r for obs in series for r in obs['evidence_refs']))
    else:
        raw_external = {'availability': 'NO_AUTHORIZED_TWO_SNAPSHOT_SERIES', 'observed_change': None}
        erefs = ['SOURCE:' + source['source_snapshot_sha256'] + ':aki_external_observations:ABSENT']
    facts['external_state'] = fact(external,raw_external,erefs)
    stable = (facts['W_separation']['category'] == 'HIGH'
              and all(facts[k]['category'] == 'HIGH' for k in policy['axis_evidence_groups'])
              and external == 'LOW' and not conflicts)
    facts['solid_confirmation'] = fact('CONFIRMED' if stable else 'NOT_CONFIRMED',
                                       {'separated_head_and_all_axis_groups_strong_and_observed_stable': stable})
    second_anchor = next(r for r in ranks['P2'] if r != top)
    third_anchor = next(r for r in ranks['P3'] if r not in {top, second_anchor})
    anchors = {'W':top,'P2':second_anchor,'P3':third_anchor}
    runners = {}
    for r,v in values.items():
        runners[r] = {}
        for c in metric:
            support = sum(v[k] >= policy['support_floor'] for k in policy['support_groups'][c])
            role_gap = max(0, (values[anchors[c]][metric[c]] - v[metric[c]]) / scales[c])
            qualified = v[metric[c]] >= policy['role_quality_floor'] and support >= 2
            category = ('MAIN' if qualified and role_gap <= policy['column_gap'][c]['BASE'] else
                        'ALTERNATIVE' if qualified and role_gap <= policy['column_gap'][c]['REVIEW'] else 'OTHER')
            runners[r][c] = fact(category, {'runner_id': r, 'metric': metric[c], 'value':v[metric[c]],
                                    'normalized_gap':role_gap, 'anchor_runner':anchors[c], 'scale':scales[c], 'support_group_count':support},
                                    ['FULL20:' + dependency + ':' + r])
    # Pair/Third semantics depend on column-positive evidence, not duplicate
    # probability claims. Only potential selected runners need combinations.
    potential = {c:[r for r in values if runners[r][c]['category'] != 'OTHER'] for c in metric}
    pairs,thirds = {},{}
    for h in potential['W']:
        for s in potential['P2']:
            if h == s: continue
            key = h+'>'+s
            pairs[key] = {'compatible':fact('YES', {'head_role_supported':h,'second_role_supported':s,'distinct':True})}
            for t in potential['P3']:
                if t in {h,s}: continue
                thirds[key+'>'+t] = {'compatible':fact('YES', {'head':h,'second':s,'third_role_supported':t,'distinct':True})}
    out = deepcopy(source)
    out['aki_evidence_features'] = facts
    out['aki_selection_features'] = {'runners':runners,'pairs':pairs,'thirds':thirds}
    gate = {'status':'LIMITED' if external == 'UNOBSERVABLE' else 'KNOWN',
            'action':'PAPER' if external == 'UNOBSERVABLE' or conflicts else 'ALLOW',
            'reason':'EXTERNAL_VARIATION_UNOBSERVABLE' if external == 'UNOBSERVABLE' else 'SOURCE_CONFLICT' if conflicts else 'OBSERVED_EXTERNAL_SERIES',
            'source_snapshot_sha256':source['source_snapshot_sha256']}
    out['aki_compiler_receipt'] = {'full20_sha256': dependency,'policy_sha256':sha(policy),
                                 'feature_sha256':sha({'axes':facts,'selection':out['aki_selection_features']}),
                                 'signed_source_enriched':False,'information_gate':gate}
    return out

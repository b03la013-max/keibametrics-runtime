"""Distinguish positive source failures from unknown/unpublished information."""
from collections import Counter


def acquisition_failure(rid, source, runner, features, mapping):
    card=next((r for r in (source.get('jra_official_race_card_detail') or {}).get('runners',[])
        if str(r.get('runner_id') or r.get('horse_no'))==str(rid)),{})
    payload=source.get('jra_official_horse_history') or {}
    history=(payload.get('runners') or {}).get(str(rid)) or {}
    parents=history.get('pedigree') or {}
    if all(card.get(k) or parents.get(k) for k in ('sire','damsire')):return None
    # A sparse pool, an absent legacy field, or NO_PRIOR_RUNS is not a fetch failure.
    errors=[str(x) for x in payload.get('errors') or []]
    failed=any(x.startswith('JRA_HORSE_HISTORY_FAILED:'+str(rid)+':') for x in errors)
    # Missing profile tokens alone cannot distinguish parser failure from an
    # officially unlinked/unpublished profile; never certify either cause.
    if not failed:return None
    from jra_evidence_to_base_production import _profile_for_runner
    profile=_profile_for_runner(runner)
    weights=mapping['index_profiles'][profile]['BVI']
    covered=sum(float(w) for k,w in weights.items() if features.get(k) is not None)
    if covered+1e-12>=float(mapping['profiles'][profile]['minimum_index_coverage_weight']):return None
    return 'SOURCE_ACQUISITION_FAILED'


def classify_block(reason):
    reason=str(reason)
    if 'IDENTITY' in reason or 'PEDIGREE_MATCH' in reason:return 'BLOCKED_IDENTITY'
    if 'SOURCE_ACQUISITION_FAILED' in reason:return 'BLOCKED_SOURCE_ACQUISITION'
    if any(x in reason for x in ('NOT_PRODUCTION','RULE','CATEGORY','EVALUATOR','FEATURE_EVIDENCE','FEATURE_SOURCE_FACT')):
        return 'BLOCKED_RULE_OR_EVALUATOR'
    return 'BLOCKED_REQUIRED_FEATURE'


def summarize(partial):
    rows=[]
    for rid,row in partial['runners'].items():
        cell=row['indices']['BVI']
        if cell['status']=='BLOCKED':kind=classify_block(cell['reason'])
        elif 'DCR-ART3' in cell['rule_id']:
            kind='MEASURED_PLUS_DCR' if cell['components'] else 'DCR_ONLY_CAUSE_UNDETERMINED'
        else:kind='MEASURED'
        rows.append({'runner_id':rid,'profile':row['profile'],'status':kind,'value':cell['value'],
            'reason':cell.get('reason'),'cause_certified_officially_unpublished':False})
    keys=('MEASURED','MEASURED_PLUS_DCR','DCR_ONLY_CAUSE_UNDETERMINED','BLOCKED_REQUIRED_FEATURE',
        'BLOCKED_SOURCE_ACQUISITION','BLOCKED_RULE_OR_EVALUATOR','BLOCKED_IDENTITY')
    counts=Counter(r['status'] for r in rows)
    return {'runners':rows,'counts':{k:counts[k] for k in keys},
        'absence_alone_proves_official_nonpublication':False}

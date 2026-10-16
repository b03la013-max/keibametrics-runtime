"""Profile and controlled-arm measurements on authenticated frozen comparisons."""
from collections import Counter
from jra_bvi_consumption import sha
from jra_evidence_to_base_production import _profile_for_runner
from jra_index_provenance_builder import BASE
from jra_bvi_shadow_comparison import PEDIGREE_FEATURES

ARMS=('A_CURRENT','B_PEDIGREE_ENHANCED_SHADOW','C_BLOODLINE_ABLATION')
PROFILES=('NEWCOMER','LOW_CAREER','ESTABLISHED')


def preregister(comparison):
    lists={k:comparison['arms'][k]['diagnostic_tickets'] for k in ARMS}
    n=min(len(v) for v in lists.values())
    return {'profile':'KM-JRA-BVI-CONTROLLED-COMPARISON-v1',
        'equal_budget':'NORMALIZE_WHOLE_FROZEN_ARM_TO_COMMON_UNIT_BUDGET; FRACTIONAL_DIAGNOSTIC_ONLY',
        'equal_ticket_rule':'FROZEN_PREFIX_COMMON_MIN_COUNT','equal_ticket_count':n,
        'equal_ticket_subset_hashes':{k:sha(v[:n]) for k,v in lists.items()},
        'selection_uses_results':False,'production_effect':'NONE'}


def evaluate(pre, official, settled):
    from mec_r4_shadow import settle_ticket_list
    top=[str(x) for x in official['top3']];arms=pre['comparison']['arms']
    profiles={str(r['runner_id']):_profile_for_runner(r) for r in arms['A_CURRENT']['numerical_runners']}
    if len(profiles)!=len(arms['A_CURRENT']['numerical_runners']):raise ValueError('BVI_OOS_DUPLICATE_RUNNER')
    for a in arms.values():
        if set(profiles)!={str(r['runner_id']) for r in a['numerical_runners']}:raise ValueError('BVI_OOS_RUNNER_UNIVERSE_CHANGED')
    output={};base={str(r['runner_id']):r for r in arms['A_CURRENT']['numerical_runners']}
    for name,arm in arms.items():
        ranking=[str(x) for x in arm['owner']['static_prediction']['ranking']]
        cols=arm['owner']['active_columns'];candidates=set().union(*(set(map(str,v)) for v in cols.values()))
        current={str(r['runner_id']):r for r in arm['numerical_runners']}
        changes=[]
        for rid,r in current.items():
            before=base[rid]['evidence_features'];after=r['evidence_features']
            for feature in sorted(set(before)|set(after)):
                if feature not in PEDIGREE_FEATURES and before.get(feature)!=after.get(feature):changes.append([rid,feature])
        if name=='B_PEDIGREE_ENHANCED_SHADOW' and changes:
            raise ValueError('BVI_OOS_ENHANCED_NON_PEDIGREE_INPUT_CHANGED')
        groups={}
        for profile in PROFILES:
            ids={rid for rid,p in profiles.items() if p==profile}
            hit_targets={role:top[i] for i,role in enumerate(('W','P2','P3')) if profiles.get(top[i])==profile}
            groups[profile]={'runner_count':len(ids),
                'index_changed_vs_a':{key:sum(current[r]['canonical_components'][key]['value']!=base[r]['canonical_components'][key]['value'] for r in ids) for key in next(iter(base.values()))['canonical_components']},
                'bvi_changed_vs_a':sum(current[r]['canonical_components']['BVI']['value']!=base[r]['canonical_components']['BVI']['value'] for r in ids),
                'rank_changed_vs_a':sum(ranking.index(r)!=list(map(str,arms['A_CURRENT']['owner']['static_prediction']['ranking'])).index(r) for r in ids),
                'pedigree_feature_rows':sum(any(k in current[r]['evidence_features'] for k in PEDIGREE_FEATURES) for r in ids),
                'false_positive_candidates':len((candidates&ids)-set(top)),
                'target_roles':{role:{'n':1,'captured':rid in set(map(str,cols[role])),
                    'rank':ranking.index(rid)+1,'market_rank':list(map(str,pre['market_ranking'])).index(rid)+1 if pre.get('market_ranking') else None}
                    for role,rid in hit_targets.items()}}
        other_base_changes={key:[rid for rid in profiles if current[rid]['canonical_components'][key]['value']!=base[rid]['canonical_components'][key]['value']]
            for key in BASE if key!='BVI'}
        other_base_changes={key:ids for key,ids in other_base_changes.items() if ids}
        bvi_changes=sum(current[rid]['canonical_components']['BVI']['value']!=base[rid]['canonical_components']['BVI']['value'] for rid in profiles)
        s=settled['arms'][name]['settlement'];cost=s['investment']
        output[name]={'profiles':groups,'non_bvi_feature_changes_vs_a':changes,
            'pedigree_features_only_comparison':not changes,
            'other_base_index_changes_vs_a':other_base_changes,
            'bvi_only_causal_comparison':bool(bvi_changes and not changes and not other_base_changes),
            'equal_budget_protocol_preregistered':pre.get('comparison_protocol') is not None,
            'equal_budget_return_per_yen':s['return']/cost if cost else None,
            'equal_budget_status':'NORMALIZED_DIAGNOSTIC_NOT_PURCHASE' if cost else 'NO_BET_NO_NORMALIZATION'}
    protocol=pre.get('comparison_protocol')
    equal_ticket={'status':'NOT_PREREGISTERED','arms':{}}
    if protocol is not None:
        if protocol!=preregister(pre['comparison']):raise ValueError('BVI_OOS_COMPARISON_PROTOCOL_MISMATCH')
        n=protocol['equal_ticket_count'];payout={'official_result':{'top3':official['top3'],
            'payouts':{k:v['per_100_yen'] for k,v in official['payouts'].items()}}}
        if n:
            equal_ticket={'status':'FROZEN_PREFIX_DIAGNOSTIC','ticket_count':n,
                'arms':{name:settle_ticket_list(arms[name]['diagnostic_tickets'][:n],payout) for name in ARMS}}
        else:equal_ticket={'status':'COMMON_WIDTH_ZERO_NO_COMPARISON','ticket_count':0,'arms':{}}
    return {'race_id':pre['race_id'],'race_profile':next(iter(set(profiles.values()))) if len(set(profiles.values()))==1 else 'MIXED',
        'profiles':dict(Counter(profiles.values())),'arms':output,'equal_ticket':equal_ticket,
        'causal_scope':'PEDIGREE_FEATURES_CAN_FEED_MULTIPLE_BASE_INDICES; NEITHER_B_NOR_C_IS_AUTOMATICALLY_BVI_SCALAR_ONLY',
        'predictive_improvement_demonstrated':False,'automatic_promotion':False}


def aggregate(evaluations):
    result={name:{p:{'runner_count':0,'bvi_changed_vs_a':0,'rank_changed_vs_a':0,'pedigree_feature_rows':0,
        'false_positive_candidates':0,'target_roles':{role:{'n':0,'captured':0,'rank_sum':0,'market_n':0,'market_rank_sum':0} for role in ('W','P2','P3')}} for p in PROFILES} for name in ARMS}
    for e in evaluations:
        for name in ARMS:
            for p,g in e['arms'][name]['profiles'].items():
                out=result[name][p]
                for k in ('runner_count','bvi_changed_vs_a','rank_changed_vs_a','pedigree_feature_rows','false_positive_candidates'):out[k]+=g[k]
                for role,values in g['target_roles'].items():
                    target=out['target_roles'][role];target['n']+=1;target['captured']+=int(values['captured']);target['rank_sum']+=values['rank']
                    if values['market_rank'] is not None:target['market_n']+=1;target['market_rank_sum']+=values['market_rank']
    normalized={}
    for name in ARMS:
        values=[e['arms'][name]['equal_budget_return_per_yen'] for e in evaluations
                if e['arms'][name]['equal_budget_protocol_preregistered'] and e['arms'][name]['equal_budget_return_per_yen'] is not None]
        normalized[name]={'n':len(values),'mean_return_per_common_budget_unit':sum(values)/len(values) if values else None}
    return {'preregistered_equal_budget':normalized,'race_count':len(evaluations),'arms':result,
        'race_profile_counts':dict(Counter(e['race_profile'] for e in evaluations)),
        'equal_ticket_preregistered_races':sum(e['equal_ticket']['status']=='FROZEN_PREFIX_DIAGNOSTIC' for e in evaluations),
        'mixed_race_capital_attribution':'NOT_ALLOCATED_TO_INDIVIDUAL_HORSE_PROFILES',
        'improvement_demonstrated':False}

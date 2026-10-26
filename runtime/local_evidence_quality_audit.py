"""Read-only evidence quality, separate from numerical and purchase policy.

No score is recomputed or overwritten. A known component calculation is not
proof that its construct (jockey skill, kickback tolerance, etc.) was measured.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import datetime, timezone
import copy
import hashlib
import json
from pathlib import Path
import re

BASE9=('HPI-L','CFIg-L','RFIg-L','BVIg-L','JTI-L','CSI-L','BWI-L','DCR','NCI')
PROXY_COMPONENTS={
    'opponent_strength':'CLASS_AND_FIELD_SIZE_NOT_INDEPENDENT_OPPONENT_RECORDS',
    'course_geometry':'DIRECTION_AND_SURFACE_PROXY_NOT_MEASURED_GEOMETRY',
    'draw_style_fit':'HORSE_NUMBER_AND_FIRST_CALL_INTERACTION_NOT_FRAME_CAUSAL_EFFECT',
    'third_corner_progression':'FIRST_TO_LAST_CALL_PROXY_NOT_IDENTIFIED_THIRD_CORNER',
    'kickback_traffic_tolerance':'NONFRONT_FINISH_PROXY_NOT_OBSERVED_KICKBACK_OR_TRAFFIC',
    'jockey_reproducibility':'SAME_HORSE_RIDER_HISTORY_NOT_INDEPENDENT_JOCKEY_EFFECT',
    'transfer_preparation':'VENUE_DIVERSITY_PROXY_NOT_OBSERVED_PREPARATION',
    'layoff_preparation':'INTERVAL_RULE_NOT_OBSERVED_TRAINING',
    'rotation_management':'INTERVAL_DISPERSION_RULE_NOT_STABLE_MANAGEMENT_CAUSAL_EFFECT',
    'fatigue_rebound':'INTERVAL_AND_WEIGHT_CHANGE_PROXY_NOT_OBSERVED_FATIGUE',
    'venue_recent':'SAME_HORSE_HISTORY_NOT_JOCKEY_VENUE_POPULATION',
    'distance_record':'SAME_HORSE_HISTORY_NOT_JOCKEY_DISTANCE_POPULATION',
    'position_acquisition_skill':'SAME_HORSE_FIRST_CALL_PROXY_NOT_ABILITY_ADJUSTED_JOCKEY_EFFECT',
    'progression_timing_skill':'SAME_HORSE_FIRST_LAST_CALL_PROXY_NOT_OBSERVED_TIMING',
    'favorite_reliability':'SAME_HORSE_POPULARITY_SUBSET_NOT_ABILITY_ADJUSTED_JOCKEY_EFFECT',
    'longshot_record':'SAME_HORSE_POPULARITY_SUBSET_NOT_ABILITY_ADJUSTED_JOCKEY_EFFECT',
}
SHARED_EVIDENCE_GROUPS={
    'HPI_CFI_FINISH':('recent_finish','same_venue','same_distance','similar_distance'),
    'CFI_RFI_POSITIONS':('draw_style_fit','position_acquisition','position_maintenance','third_corner_progression'),
    'HPI_NCI_CLASS':('class_level','opponent_strength','previous_class','recent_opponent_class','transfer_class'),
    'JTI_RFI_RIDER':('venue_recent','distance_record','position_acquisition_skill','progression_timing_skill','jockey_reproducibility'),
    'CSI_CCI_COMMENT':('cci_specificity',),
    'CSI_TRI_TRAINING':('tri_vertical_comparison',),
}
DERIVED_INDEX_INPUTS={
    'PRI':['TPI-L','SRI-L','HPI-L','CFIg-L','RFIg-L'],
    'OPI-V':['TPI-L','SRI-L','HPI-L','CFIg-L','RFIg-L'],
    'TPI-L':['HPI-L','CFIg-L','RFIg-L','BVIg-L','JTI-L','CSI-L','BWI-L','NCI','EVI/CEV'],
    'SRI-L':['TPI-L','RFIg-L','EVI/CEV','CFIg-L','NCI','BWI-L','JTI-L','CSI-L','DCR'],
    'F3S-L':['SRI-L','TPI-L','EVI/CEV','RFIg-L','CFIg-L','NCI','T3I-L'],
    'URP':['DRS'],'W-AKI':['DCR','URP','PRI'],'P2-AKI':['DCR','PRI','URP'],
    'P3-AKI':['DCR','PRI','URP'],'ASI':['W-AKI','DCR'],
    'T3I-L':['OPI-V','TRI','DRS'],
    'ZAI-WIN':['TPI-L','SRI-L','EVI/CEV','CFIg-L','NCI','DCR'],
    'ZAI-PLACE':['TPI-L','SRI-L','EVI/CEV','CFIg-L','RFIg-L','DCR'],
    'RSI':['ZAI-WIN','ZAI-PLACE','T3I-L','PRI','DCR'],
    'WCI':['ZAI-WIN','SRI-L','ASI','W-AKI'],
}
DERIVED_FEATURE_INPUTS={
    'EVI/CEV':['position_acquisition','position_maintenance','third_corner_progression','leadership_stalk_acceptance','kickback_traffic_tolerance','going_adaptation','course_geometry','going_fit'],
    'CCI':['cci_specificity'],'TRI':['tri_vertical_comparison'],'DRS':['class_change_pressure'],
    'HCS':['class_level','opponent_strength','recent_finish'],
    'W-AKI':['running_style_repro'],'ASI':['position_maintenance'],
    'T3I-L':['same_distance','third_corner_progression','position_maintenance','good_weight_range'],
}

def sha(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,
                                   separators=(',',':'),allow_nan=False).encode()).hexdigest()

def _clock(value):
    d=datetime.fromisoformat(value.replace('Z','+00:00'))
    if d.tzinfo is None:raise ValueError('QUALITY_TIMESTAMP_WITHOUT_ZONE')
    return d.astimezone(timezone.utc)

def history_course_observation(start):
    """Only printed markers; a venue name does not invent direction or sand."""
    text=str(start.get('going_observed') or '')
    marker=re.search(r'(内|外|左|右)(?=(?:ダート|ダ|芝))',text)
    token=marker[1] if marker else None
    return {'printed_text':text,'printed_marker':token,
            'course_family_observed':{'内':'INNER','外':'OUTER','左':'LEFT','右':'RIGHT'}.get(token),
            'direction_explicit':{'左':'LEFT','右':'RIGHT'}.get(token),
            'source_direction_field':start.get('direction'),
            'surface_observed':start.get('surface'),
            'going_observed':start.get('going'),
            'sand_regime':'UNKNOWN_NOT_IN_PRINTED_SUMMARY',
            'geometry_dimensions':'UNKNOWN_NOT_IN_PRINTED_SUMMARY'}

def passing_path_observation(start):
    positions=start.get('content_positions') or []
    named=start.get('named_corner_positions')
    # Unlabelled arrays may contain two calls for a one-turn race. Their count
    # alone never identifies the 2nd/3rd/4th corners.
    return {'positions':copy.deepcopy(positions),'call_count':len(positions),
            'first_last_call_observed':bool(positions),
            'named_corners':copy.deepcopy(named) if isinstance(named,dict) else None,
            'complete_2_3_4_corner_path':isinstance(named,dict) and all(
                named.get(k) is not None for k in ('2','3','4')),
            'third_corner_identity':'OBSERVED_NAMED' if isinstance(named,dict) and named.get('3') is not None else 'UNKNOWN_UNLABELLED_CALLS'}

def component_quality(index, component, feature):
    missing=bool(component.get('missing'))
    coverage=component.get('coverage')
    coverage=0.0 if coverage is None else float(coverage)
    if not 0<=coverage<=1:raise ValueError('QUALITY_COVERAGE_RANGE')
    reason=PROXY_COMPONENTS.get(component['component'])
    return {'component':component['component'],'missing':missing,
            'evidence_class':'D' if missing else 'C' if reason else 'B',
            'reason':('MISSING_OR_INCOMPARABLE_RETAINED_AS_UNKNOWN' if missing else reason or 'DETERMINISTIC_REGISTERED_RULE_OVER_OBSERVED_FACTS_UNCALIBRATED'),
            'weight':component['weight'],'coverage':coverage,
            'score':component['score'],'score_is_measurement':False,
            'raw_metric':copy.deepcopy(feature.get('raw_metric')),
            'source_fact':feature.get('source_fact'),
            'source_timestamp':feature.get('source_timestamp'),
            'evidence_refs':copy.deepcopy(feature.get('evidence_refs',[])),
            'rule_id':component.get('rule_id')}

def audit_runner(numerical_runner, race, cutoff):
    before=sha(numerical_runner);features=numerical_runner['evidence_features']
    indices=numerical_runner['candidate_indices'];base={}
    for name in BASE9:
        cell=indices[name];components=[component_quality(name,c,features[c['component']]) for c in cell['components']]
        total=sum(c['weight'] for c in components);observed=sum(c['weight'] for c in components if not c['missing'])
        adjusted=sum(c['weight']*c['coverage'] for c in components if not c['missing'])
        base[name]={'terminal_status':cell['terminal_status'],'value':cell['value'],
                    'component_count':len(components),'nonmissing_component_count':sum(not c['missing'] for c in components),
                    'missing_component_count':sum(c['missing'] for c in components),
                    'true_observed_component_fraction':sum(not c['missing'] for c in components)/len(components),
                    'weighted_observed_share':observed/total,'coverage_adjusted_weighted_share':adjusted/total,
                    'legacy_observed_weight_fraction':cell.get('observed_weight_fraction'),
                    'legacy_fraction_semantics':'NUMERICAL_DENOMINATOR_SHARE_INCLUDES_NEUTRAL_WHEN_LEGACY_POLICY',
                    'components':components,'score_and_evidence_quality_are_separate':True}
    times=[f['source_timestamp'] for f in features.values() if f.get('source_timestamp')]
    post=[s for s in times if _clock(s)>_clock(cutoff)]
    if post:raise ValueError('QUALITY_POSTCUTOFF_COMPONENT_SOURCE')
    raw=numerical_runner['raw_candidate_evidence'];starts=raw.get('starts') or []
    current_venue={'OHI':'大井','URW':'浦和','FNB':'船橋','KAW':'川崎'}.get(race.get('venue_id'),race.get('venue_id'))
    comparable=[]
    for start in starts:
        going_match=(start.get('going')==race.get('going')) if start.get('going') and race.get('going') else None
        comparable.append({'provider_race_id':start.get('provider_race_id'),'date':start.get('date'),
            'venue':start.get('venue'),'distance':start.get('distance'),'surface':start.get('surface'),
            'same_venue':str(start.get('venue') or '').removesuffix('ナ')==current_venue,
            'same_distance':start.get('distance')==race.get('distance'),
            'same_surface':start.get('surface')==race.get('surface'),
            'same_going':going_match,'historical_going':start.get('going'),'current_going':race.get('going'),
            'historical_class_text':start.get('race_name'),'current_class_text':race.get('class') or race.get('race_name'),
            'historical_class_ordinal':start.get('class_score'),
            'cfi_performance_basis':'EXISTING_UNADJUSTED_NORMALIZED_FINISH_AVERAGE_NOT_CLASS_ADJUSTED_TIME',
            'age_class_going_equivalence_not_asserted':True})
    shared={}
    for group,names in SHARED_EVIDENCE_GROUPS.items():
        present={n:features[n] for n in names if n in features and not features[n].get('missing')}
        refs={n:set(f.get('evidence_refs') or []) for n,f in present.items()}
        shared[group]={'components_nonmissing':list(present),
            'shared_refs':sorted(set.intersection(*refs.values())) if len(refs)>1 else [],
            'independent_source_claim':False,
            'overcounting_magnitude':'NOT_IDENTIFIED_WITHOUT_ABLATION_NO_WEIGHT_CHANGE'}
    neutral=[n for n in BASE9 if indices[n]['terminal_status']=='RULED-NEUTRAL']
    derived={n:{'terminal_status':c['terminal_status'],'value':c['value'],
                'missingness_fraction':c.get('missingness_fraction'),'source_fact':c['source_fact'],
                'evidence_refs':c['evidence_refs'],
                'direct_index_inputs':DERIVED_INDEX_INPUTS.get(n,[]),
                'direct_feature_inputs':DERIVED_FEATURE_INPUTS.get(n,[]),
                'direct_neutral_index_inputs':[i for i in DERIVED_INDEX_INPUTS.get(n,[]) if indices[i]['terminal_status']=='RULED-NEUTRAL'],
                'direct_missing_feature_inputs':[i for i in DERIVED_FEATURE_INPUTS.get(n,[]) if features[i]['missing']],
                'cross_runner_population_inputs':({'scope':'ALL_RUNNERS_IN_SAME_FROZEN_RACE',
                    'ranking_basis_indices':['TPI-L','SRI-L','HPI-L','CFIg-L','RFIg-L'],
                    'market_rank_basis':'OFFICIAL_CURRENT_POPULARITY_NOT_KRS_SSR',
                    'this_runner_official_market_rank':raw.get('popularity')}
                    if n in ('PRI','OPI-V') else None),
                'base9_neutral_context_not_direct_dependency':neutral,
                'external_or_environment_inputs_not_fully_observed':'PRI/OPI-V use official market rank and computed internal rank; URP/AKI use field density/competition. See original source_fact.',
                'calculated_does_not_mean_full_measurement':True}
             for n,c in indices.items() if n not in BASE9}
    result={'runner_id':str(numerical_runner['runner_id']),'name':numerical_runner['name'],
            'race_id':race['provider_race_id'],'base9':base,'derived20':derived,
            'derived_calculated_while_some_base_neutral':sum(c['terminal_status']=='CALCULATED' for c in derived.values()) if neutral else 0,
            'shared_evidence_audit':shared,'history_course_facts':[history_course_observation(s) for s in starts],
            'passing_path_facts':[passing_path_observation(s) for s in starts],
            'course_comparability':comparable,
            'current_course_family':race.get('course_family'),'current_going':race.get('going'),'current_body_weight':raw.get('current_body_weight'),
            'current_body_weight_change':raw.get('current_body_weight_change'),
            'draw_style_inputs':{'horse_no':raw.get('horse_no'),'frame_no':raw.get('frame_no'),
                                 'current_rule_uses':'HORSE_NUMBER_PERCENTILE_WITH_FIRST_CALL_SCORE_NOT_FRAME_NUMBER',
                                 'causal_frame_advantage_measured':False},
            'jockey_independent_population_source_count':0,
            'same_horse_jockey_history_only':True,'post_cutoff_components':len(post)}
    result['timestamp_missing_components']=sum(not f.get('source_timestamp') for f in features.values())
    if sha(numerical_runner)!=before:raise ValueError('QUALITY_MUTATED_ORIGINAL_RUNNER')
    return result

def audit_day(root,index_path):
    """Read saved observations/numerical cells; never fit, run Engine or POST."""
    root=Path(root);index=json.loads(Path(index_path).read_text());rows=[];before={}
    for item in index['rows']:
        folder=root/item['revision'];files={n:folder/n for n in ('observation.json','numerical.json','prediction-original.json')}
        for p in files.values():before[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
        o=json.loads(files['observation.json'].read_text());n=json.loads(files['numerical.json'].read_text());f=json.loads(files['prediction-original.json'].read_text())
        from runtime.ohi_single_race_research import verify_observation
        verify_observation(o,folder.with_name(folder.name+'.source'))
        if o['race']['provider_race_id']!=item['race_id'] or o['race']!=f['race'] or f['sha256']!=item['prediction_sha256'] or f['sha256']!=sha({k:v for k,v in f.items() if k!='sha256'}):
            raise ValueError('QUALITY_RACE_OR_PREDICTION_IDENTITY')
        if o['sha256']!=f['source_sha256'] or o['sha256']!=sha({k:v for k,v in o.items() if k!='sha256'}):
            raise ValueError('QUALITY_SOURCE_IDENTITY')
        ids={str(x['runner_id']) for x in o['facts']}
        if ids!={str(x['runner_id']) for x in n['runners']} or len(ids)!=len(n['runners']):raise ValueError('QUALITY_RUNNER_UNIVERSE')
        if any(n['race'].get(k)!=o['race'].get(k) for k in ('provider_race_id','race_date','race_no','venue_id','distance')):
            raise ValueError('QUALITY_NUMERICAL_RACE_IDENTITY')
        if n['candidate_evidence_compiler']['source_snapshot_sha256']!=o['sha256'] or n['input_observation']['raw_sha256']!=o['source']['raw_sha256']:
            raise ValueError('QUALITY_NUMERICAL_SOURCE_IDENTITY')
        facts={str(x['runner_id']):x for x in o['facts']}
        for runner in n['runners']:
            rid=str(runner['runner_id'])
            if runner['name']!=facts[rid]['name'] or runner['candidate_indices']!=f['numerical_cells'][rid]:
                raise ValueError('QUALITY_NUMERICAL_RUNNER_OR_FROZEN_CELL_IDENTITY')
            if any(_clock(x['source_timestamp'])>_clock(f['freeze_at']) for x in runner['evidence_features'].values() if x.get('source_timestamp')):
                raise ValueError('QUALITY_COMPONENT_AFTER_ORIGINAL_FREEZE')
        rows.append({'race_no':o['race']['race_no'],'race':o['race'],'source_sha256':o['sha256'],
                     'prediction_sha256':f['sha256'],'numerical_file_sha256':before[str(files['numerical.json'])],
                     'source_receipts':o['receipts'],'freeze_at':f['freeze_at'],'card_raw_sha256':o['source']['raw_sha256'],
                     'card_age_at_freeze_seconds':(_clock(f['freeze_at'])-_clock(o['source']['fetched_at'])).total_seconds(),
                     'runners':[audit_runner(r,o['race'],o['race']['prediction_cutoff']) for r in n['runners']]})
    all_runners=[h for r in rows for h in r['runners']]
    by_index={}
    for idx in BASE9:
        cells=[h['base9'][idx] for h in all_runners];comps=[c for cell in cells for c in cell['components']]
        by_index[idx]={'runner_count':len(cells),'component_count':len(comps),
                       'nonmissing_components':sum(not c['missing'] for c in comps),
                       'missing_components':sum(c['missing'] for c in comps),
                       'nonmissing_fraction':sum(not c['missing'] for c in comps)/len(comps),
                       'mean_weighted_observed_share':sum(c['weighted_observed_share'] for c in cells)/len(cells),
                       'mean_coverage_adjusted_weighted_share':sum(c['coverage_adjusted_weighted_share'] for c in cells)/len(cells),
                       'terminal_counts':dict(Counter(c['terminal_status'] for c in cells)),
                       'evidence_classes':dict(Counter(c['evidence_class'] for c in comps))}
    terminal=Counter(c['terminal_status'] for h in all_runners for c in [*h['base9'].values(),*h['derived20'].values()])
    cfi=defaultdict(Counter)
    for h in all_runners:
        for c in h['base9']['CFIg-L']['components']:cfi[c['component']]['missing' if c['missing'] else 'nonmissing']+=1
    history=[x for h in all_runners for x in h['history_course_facts']];passing=[x for h in all_runners for x in h['passing_path_facts']]
    out={'schema':'LOCAL-EVIDENCE-QUALITY-READONLY-AUDIT-v1-20261027',
         'classification':'POSTRESULT_INFORMATION_AUDIT_NOT_PREDICTION_NOT_FORWARD_OOS',
         'race_count':len(rows),'runner_count':len(all_runners),'base9_summary':by_index,
         'terminal_counts':dict(terminal),'cfi_components':{k:dict(v) for k,v in cfi.items()},
         'history_course_summary':{'starts':len(history),'printed_course_marker_count':sum(x['printed_marker'] is not None for x in history),
                                   'explicit_direction_count':sum(x['direction_explicit'] is not None for x in history),
                                   'source_direction_known_count':sum(x['source_direction_field'] in ('LEFT','RIGHT') for x in history),
                                   'going_observed_count':sum(x['going_observed'] is not None for x in history)},
         'passing_path_summary':{'starts':len(passing),'has_calls':sum(x['call_count']>0 for x in passing),
                                 'complete_named_2_3_4_count':sum(x['complete_2_3_4_corner_path'] for x in passing),
                                 'call_count_distribution':dict(Counter(x['call_count'] for x in passing))},
         'calculated_derived_cells_with_neutral_base_present':sum(h['derived_calculated_while_some_base_neutral'] for h in all_runners),
         'independent_card_raw_sha_count':len({r['card_raw_sha256'] for r in rows}),
         'card_source_age_at_freeze_seconds':{'minimum':min(r['card_age_at_freeze_seconds'] for r in rows),'maximum':max(r['card_age_at_freeze_seconds'] for r in rows)},
         'rules_weights_formulas_modified':False,'production_authority':False,'registered_oos_credit':0,
         'original_files_sha256':before,'races':rows}
    for p,digest in before.items():
        if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=digest:raise ValueError('QUALITY_MUTATED_ORIGINAL_FILE')
    out['sha256']=sha(out);return out


def main():
    import argparse
    from runtime.ohi_single_race_research import private_root,write
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--original-root',required=True);p.add_argument('--index',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();target=private_root(a.output)
    if target.exists():raise ValueError('QUALITY_AUDIT_REVISION_EXISTS')
    report=audit_day(a.original_root,a.index);write(target,report)
    print(json.dumps({'sha256':report['sha256'],'races':report['race_count'],
                     'runners':report['runner_count'],'terminal_counts':report['terminal_counts']}))


if __name__=='__main__':main()

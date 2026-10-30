"""Replay registered role criteria as explanation, without changing any role.

Uses the same authority-bound compiler and category rules. Result labels,
market-driven promotion, and new selection thresholds are not inputs.
"""
from pathlib import Path
from datetime import date
import hashlib
import json
import re


def support_lineage(runner, role, policy):
    """Describe existing support groups; shared SOURCE bytes prove no independence.

    No score, rule, threshold or selection is changed. A horse/date overlap is
    a dependency diagnostic, not an accepted permanent race identity.
    """
    cells=runner['canonical_components'];features=runner.get('evidence_features') or {}
    groups=[];events={}
    for index in policy['support_groups'][role]:
        cell=cells[index];components=cell.get('components') or []
        names=sorted({c['feature'] for c in components if c.get('feature')})
        references=sorted({str(ref) for c in components for ref in c.get('evidence_refs',[])})
        for ref in references:
            # Only the explicit same-runner history identity is an event.
            # Snapshot fetch dates and person-stat periods are not horse runs.
            match=re.fullmatch(r'JRA_OFFICIAL_HISTORY:'+re.escape(str(runner['runner_id']))+
                r':(\d{4}-\d{2}-\d{2}):\d+:\d+',ref)
            if match:
                try:day=date.fromisoformat(match[1]).isoformat()
                except ValueError:continue
                events.setdefault(day,set()).add(index)
        groups.append({'index':index,'value':cell['value'],
            'support_floor_satisfied':cell['value']>=policy['support_floor'],
            'rule_id':cell.get('rule_id'),'features':names,'evidence_refs':references,
            'missing_feature_objects':[n for n in names if n not in features]})
    return {'registered_index_groups':groups,
        'shared_horse_date_dependencies':[{'runner_id':str(runner['runner_id']),
            'prior_date':day,'index_groups':sorted(indices)} for day,indices in sorted(events.items()) if len(indices)>1],
        'independent_event_identity_proven':False,
        'interpretation':'Registered index support count is not a count of independently identified horses/races.',
        'production_effect':'NONE'}

from jra_aki_v21_features import compile_features
from jra_aki_v21 import sha


def _newcomer_categories(request, source, enriched, components, authority, root):
    """Explain the distinct, already-enacted PAPER observation-channel policy."""
    from jra_aki_dispatch import apply_authorized_v21,_observed
    activation=authority['family_scoped_authority']['JRA']['newcomer_aki_paper_activation']
    if hashlib.sha256((root/'runtime/jra_aki_dispatch.py').read_bytes()).hexdigest()!=activation['runtime_sha256']:
        raise ValueError('ROLE_AUDIT_NEWCOMER_CODE_MISMATCH')
    policy=json.loads((root/activation['policy_path']).read_text())
    if sha(policy)!=activation['policy_sha256']:
        raise ValueError('ROLE_AUDIT_NEWCOMER_POLICY_MISMATCH')
    replay=apply_authorized_v21(request,source,authority,root=root)
    if replay['role_registry']!=request['role_registry']:
        raise ValueError('ROLE_AUDIT_NEWCOMER_SELECTION_MISMATCH')
    axes=replay['official_aki_verification']['calculation']['axes']
    risk=(100-axes['ASI'])/100
    by_id={str(r['runner_id']):r['canonical_components'] for r in request['runners']}
    for rid,facts in enriched['aki_selection_features']['runners'].items():
        cc=by_id[rid];channels=[]
        if any(_observed(cc[k]) and cc[k]['value']>=policy['pedigree_quality_floor'] for k in ('CFI','BVI')):
            channels.append('PEDIGREE')
        if any(_observed(cc[k]) for k in ('JTI','CSI')):channels.append('HUMAN_OFFICIAL_STATS')
        if _observed(cc['BWI']):channels.append('CURRENT_PHYSIQUE')
        eligible='PEDIGREE' in channels and len(channels)>=policy['minimum_observed_channels']
        for role,fact in facts.items():
            raw=fact['source_fact'];limits=components['feature_compiler_policy']['column_gap'][role]
            maximum=limits['REVIEW']+policy['axis_risk_gap_extension']*risk
            qualified=eligible and raw['value']>=policy['role_quality_floor']
            fact['category']=('MAIN' if qualified and raw['normalized_gap']<=limits['BASE'] else
                              'ALTERNATIVE' if qualified and raw['normalized_gap']<=maximum else 'OTHER')
            raw.update(observed_channels=channels,observation_channel_count=len(channels),
                newcomer_review_gap=maximum,newcomer_policy_sha256=activation['policy_sha256'])


def build_role_exclusion_audit(request, authority, root):
    root=Path(root)
    activation=authority['family_scoped_authority']['JRA']['aki_v21_activation']
    for path,key in [('runtime/jra_aki_v21.py','runtime_sha256'),
                     ('runtime/jra_aki_v21_features.py','feature_compiler_sha256')]:
        if hashlib.sha256((root/path).read_bytes()).hexdigest()!=activation[key]:
            raise ValueError('ROLE_AUDIT_AUTHORITY_CODE_MISMATCH:'+path)
    registries={}
    for key in ('components','columns'):
        spec=activation[key]
        registries[key]=json.loads((root/spec['path']).read_text())
        if sha(registries[key])!=spec['sha256']:
            raise ValueError('ROLE_AUDIT_REGISTRY_HASH_MISMATCH:'+key)
    source=request['source_snapshot']
    if source.get('race_id')!=request.get('race_id'):
        raise ValueError('ROLE_AUDIT_SOURCE_RACE_MISMATCH')
    if sha(source)!=request['source_snapshot_sha256']:
        raise ValueError('ROLE_AUDIT_SOURCE_HASH_MISMATCH')
    source={**source,'source_snapshot_sha256':request['source_snapshot_sha256']}
    enriched=compile_features(request,source,
                              registries['components']['feature_compiler_policy'])
    if request['aki_column_selection'].get('newcomer_policy'):
        _newcomer_categories(request,source,enriched,registries['components'],authority,root)
    compiled=enriched['aki_selection_features']['runners']
    by_runner={str(r['runner_id']):r for r in request['runners']}
    metric={'W':'ZAI_WIN','P2':'ZAI_PLACE','P3':'T3I'}
    rank={role:sorted(by_runner,key=lambda rid:(-by_runner[rid]['canonical_components'][index]['value'],rid))
          for role,index in metric.items()}
    selection=request['aki_column_selection']
    if selection['registry_sha256']!=activation['columns']['sha256']:
        raise ValueError('ROLE_AUDIT_SELECTION_REGISTRY_MISMATCH')
    rows=[]
    for role,mode in selection['triggers'].items():
        rules=list(registries['columns']['columns'][role]['BASE'])
        if mode=='REVIEW':
            rules+=registries['columns']['columns'][role]['REVIEW']
        for runner in request['static_prediction']['ranking']:
            rid=str(runner)
            evaluations=[]
            for rule in rules:
                tests=[]
                for criterion in rule['all_of']:
                    name=criterion['feature'];fact=compiled[rid][name]
                    tests.append({'feature':name,'expected_category':criterion['category'],
                        'observed_category':fact['category'],
                        'satisfied':fact['category']==criterion['category'],
                        'source_fact':fact['source_fact'],'evidence_refs':fact['evidence_refs']})
                evaluations.append({'rule_id':rule['rule_id'],
                    'satisfied':all(t['satisfied'] for t in tests),'criteria':tests})
            matched=[e['rule_id'] for e in evaluations if e['satisfied']]
            saved=next(x for x in request['role_registry'] if str(x['runner_id'])==rid and x['column']==role)
            if set(matched)!={x['rule_id'] for x in saved['rule_matches']}:
                raise ValueError('ROLE_AUDIT_REPLAY_MISMATCH:'+rid+':'+role)
            rows.append({'runner_id':rid,'column':role,'saved_status':saved['status'],
                'eligible_under_registered_rules':bool(matched),
                'review_mode':mode,'matched_rule_ids':matched,'rule_evaluations':evaluations,
                'relative_priority':{'metric':metric[role],'rank':rank[role].index(rid)+1,
                    **compiled[rid][role]['source_fact']},
                'positive_criteria':[{'rule_id':e['rule_id'],**t} for e in evaluations for t in e['criteria'] if t['satisfied']],
                'unmet_criteria':[{'rule_id':e['rule_id'],**t} for e in evaluations for t in e['criteria'] if not t['satisfied']],
                'support_lineage':support_lineage(by_runner[rid],role,registries['components']['feature_compiler_policy']),
                'missing_context_features':[n for n in ('same_course_fit','same_distance_fit','surface_fit','going_fit')
                    if n not in (by_runner[rid].get('evidence_features') or {})],
                'missing_context_is_not_new_admission_gate':True,
                'candidate_revision':selection['registry_sha256']})
    audit={'profile':'KM-JRA-REGISTERED-ROLE-EXPLANATION-v1','race_id':request['race_id'],
        'source_snapshot_sha256':request['source_snapshot_sha256'],
        'registry_sha256':selection['registry_sha256'],'status':'REPLAY_MATCHED',
        'role_cell_count':len(rows),'rows':rows,'production_effect':'NONE',
        'alternative_winner_selection_changed':False,'automatic_promotion':False}
    audit['sha256']=sha(audit)
    return audit

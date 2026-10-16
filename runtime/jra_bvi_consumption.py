"""Replay-only BVI consumption proof. Does not alter policy or numerical values."""
import hashlib
import json
import math
from collections import Counter
try:
    from .jra_evidence_to_base_production import _weighted_index, _profile_for_runner
except ImportError:
    from jra_evidence_to_base_production import _weighted_index, _profile_for_runner


def sha(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def build_bvi_consumption(request, mapping, source_artifact=None):
    source_artifact=source_artifact or {}
    if source_artifact and (source_artifact.get('race_id')!=request['race_id'] or
            (request.get('source_snapshot_sha256') and request['source_snapshot_sha256']!=source_artifact.get('source_snapshot_sha256'))):
        raise ValueError('BVI_CONSUMPTION_SOURCE_BINDING_MISMATCH')
    cards={str(r.get('runner_id') or r.get('horse_no')):r for r in (source_artifact.get('jra_official_race_card_detail') or {}).get('runners',[])}
    histories=(source_artifact.get('jra_official_horse_history') or {}).get('runners') or {}
    rows=[]
    for runner in request['runners']:
        rid=str(runner['runner_id']); features=runner['evidence_features']
        card=cards.get(rid) or {};hist=histories.get(rid) or {};parents=hist.get('pedigree') or {}
        pedigree={k:card.get(k) or parents.get(k) for k in ('sire','dam','damsire')}
        for key in pedigree:
            if card.get(key) and parents.get(key) and card[key]!=parents[key]:
                raise ValueError('BVI_CONSUMPTION_PEDIGREE_IDENTITY_CONFLICT:'+rid+':'+key)
        profile=_profile_for_runner(runner)
        replay=_weighted_index('BVI',profile,features,mapping)
        cell=runner['canonical_components']['BVI']
        if type(cell['value']) not in (int,float) or not math.isfinite(cell['value']) or abs(cell['value']-replay['value'])>1e-6:
            raise ValueError('BVI_CONSUMPTION_NUMERICAL_MISMATCH:'+rid)
        weights=mapping['index_profiles'][profile]['BVI']
        dcr=bool(replay.get('adjustments'))
        denominator=sum(float(w) for w in weights.values()) if dcr else replay['coverage_weight']
        parts=[]
        for c in replay['components']:
            spec=features[c['feature']]
            parts.append({**c,'observation_count':spec.get('observation_count'),
                'source_authority':spec.get('source_authority'),
                'observed_at':spec.get('observed_at'),
                'value_contribution':c['weight']*(c['category_score']-(50 if dcr else 0))/denominator})
        baseline=50.0 if dcr else 0.0
        if abs(baseline+sum(x['value_contribution'] for x in parts)-cell['value'])>1e-6:
            raise ValueError('BVI_CONSUMPTION_CONTRIBUTION_MISMATCH:'+rid)
        rows.append({'runner_id':rid,'runner_name':runner.get('name'),
            'horse_identity_reference':runner.get('horse_id'),
            'official_horse_id':runner.get('official_horse_id'),
            'official_horse_id_status':'SUPPLIED_NOT_INDEPENDENTLY_RESOLVED' if runner.get('official_horse_id') else 'UNKNOWN',
            'pedigree_reference':pedigree,
            'source_observed_at':source_artifact.get('source_freeze_at'),
            'source_available_at_evidence':'SIGNED_SOURCE_FREEZE_UPPER_BOUND' if source_artifact else 'UNKNOWN',
            'profile':profile,'bvi_value':cell['value'],'bvi_artifact_sha256':sha(cell),
            'feature_snapshot_sha256':sha(features),'mapping_version':mapping['mapping_id'],
            'components':parts,'baseline':baseline,
            'observed_weight':replay['coverage_weight'],
            'missing_features':[k for k in weights if features.get(k) is None],
            'consumption_class':('MEASURED_PLUS_DCR' if dcr else 'MEASURED') if parts else 'DCR_ONLY',
            'missing_cause':'NOT_INDEPENDENTLY_ESTABLISHED_BY_LEGACY_FEATURE_ABSENCE' if dcr else None,
            'dcr_applied':dcr,'numerical_replay':'PASS'})
    result={'profile':'KM-JRA-BVI-CONSUMPTION-PROOF-v1','race_id':request['race_id'],
        'production_authority':request.get('current_authority') or request.get('base_index_mapping_authority'),
        'source_snapshot_sha256':request.get('source_snapshot_sha256') or source_artifact.get('source_snapshot_sha256'),
        'static_owner_activation_binding':request.get('static_owner_activation_binding'),
        'mapping_content_sha256':sha(mapping),
        'index_provenance_hash':request.get('index_provenance_hash'),
        'static_bvi_input_sha256':sha({str(r['runner_id']):r['canonical_components']['BVI'] for r in request['runners']}),
        'downstream_artifact_hashes':{key:sha(request[key]) for key in ('static_prediction','role_registry','pair_dispositions','third_dispositions','krs_input_data') if key in request},
        'static_freeze_timestamp':request.get('static_freeze_timestamp'),
        'runners':rows,'counts':dict(Counter(x['consumption_class'] for x in rows)),
        'propagation':{'direct_derived':['TPI'],'indirect_derived':['SRI','F3S','T3I'],
            'no_direct_bvi_term':['ZAI_WIN','ZAI_PLACE'],
            'static_winner_ranking':'ZAI_WIN; BVI-only change does not directly change W ranking'},
        'prediction_improvement_demonstrated':False,'capital_improvement_demonstrated':False}
    result['sha256']=sha(result)
    return result

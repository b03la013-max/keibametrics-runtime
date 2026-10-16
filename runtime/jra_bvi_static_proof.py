"""Bind an actual, independently replayed Static execution to frozen BVI input."""
from pathlib import Path
import hashlib
from copy import deepcopy
from jra_bvi_consumption import sha
from jra_static_owner_executable import compile_static_owner, PROFILE

ROOT=Path(__file__).resolve().parents[1]


def static_input(request):
    return {'family_id':request['family_id'],'race_id':request['race_id'],
        'base_index_mapping_authority':request['base_index_mapping_authority'],
        'runners':[{'runner_id':r['runner_id'],'canonical_components':{
            key:{**{k:cell.get(k) for k in ('value','mapping_version','rule_id','evidence_refs','source_fact')},
                'candidate_only':cell.get('candidate_only') is True,
                'production_authority':cell.get('production_authority') is not False}
            for key,cell in r['canonical_components'].items()}} for r in request['runners']]}


def semantic_output(request):
    return {k:request[k] for k in ('static_prediction','role_registry','pair_dispositions','third_dispositions','purchased_heads')}


def build_static_proof(prepared, owner, formal_request, authority, root=ROOT, *, execution_class="REPLAY_VERIFIED; CALLER_OWNS_TEMPORAL_GATE"):
    if prepared['race_id']!=formal_request['race_id'] or owner['race_id']!=prepared['race_id']:
        raise ValueError('BVI_STATIC_PROOF_RACE_MISMATCH')
    replay=compile_static_owner(prepared,source_snapshot_sha256=owner['source_snapshot_sha256'],
        source_receipt_sha256=owner['source_receipt_sha256'],frozen_at=owner['frozen_at'],
        prediction_cutoff=formal_request['prediction_cutoff'])
    if owner!=replay:
        raise ValueError('BVI_STATIC_PROOF_EXECUTION_REPLAY_MISMATCH')
    if static_input(prepared)!=static_input(formal_request):
        raise ValueError('BVI_STATIC_PROOF_NUMERICAL_HANDOFF_CHANGED')
    from jra_static_owner_forward_oos import fingerprint
    codes=('runtime/jra_static_owner_executable.py','runtime/jra_aki_v21.py','runtime/jra_aki_v21_features.py')
    result={'execution_class':execution_class,
        'profile':'KM-JRA-BVI-STATIC-CONSUMPTION-v1','race_id':prepared['race_id'],
        'owner_profile':PROFILE,'owner_code_sha256':hashlib.sha256((ROOT/codes[0]).read_bytes()).hexdigest(),
        'policy_fingerprint':sha({'authority':authority,'numerical_and_source_policy':fingerprint(ROOT),'files':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in codes}}),
        'source_snapshot_sha256':owner['source_snapshot_sha256'],'source_receipt_sha256':owner['source_receipt_sha256'],
        'static_input_sha256':sha(static_input(prepared)),
        'bvi_input':{str(r['runner_id']):r['canonical_components']['BVI']['value'] for r in prepared['runners']},
        'bvi_input_sha256':sha({str(r['runner_id']):r['canonical_components']['BVI'] for r in prepared['runners']}),
        'computed_at':owner['frozen_at'],'prediction_cutoff':formal_request['prediction_cutoff'],
        'raw_owner_output_sha256':sha(owner),'formal_semantic_output_sha256':sha(semantic_output(formal_request)),
        'full_ranking':deepcopy(formal_request['static_prediction']['ranking']),
        'roles':deepcopy(formal_request['static_prediction']['roles']),
        'ordered_pairs_sha256':sha(formal_request['pair_dispositions']),
        'pair_conditioned_thirds_sha256':sha(formal_request['third_dispositions']),
        'alternative_winner':'NOT_SEPARATELY_EMITTED_BY_CURRENT_OWNER',
        'execution_replay':'PASS','predictive_improvement_demonstrated':False}
    result['sha256']=sha(result);return result


def verify_static_proof(proof, request):
    if (proof.get('sha256')!=sha({k:v for k,v in proof.items() if k!='sha256'})
            or proof.get('race_id')!=request['race_id']
            or proof.get('source_snapshot_sha256')!=request['source_snapshot_sha256']
            or proof.get('static_input_sha256')!=sha(static_input(request))
            or proof.get('formal_semantic_output_sha256')!=sha(semantic_output(request))):
        raise ValueError('BVI_STATIC_PROOF_BINDING_INVALID')
    return True

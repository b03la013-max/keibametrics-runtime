"""Measurement-only bloodline ablation, using the existing numerical consumers.

No arm is a FINAL or has purchase authority. Enhanced equals Current until an
eligible, separately frozen richer official input is supplied; no invented gain.
"""
import copy
from jra_evidence_to_base_production import attach_production_ledger_to_request
from jra_index_provenance_builder import materialize_index_provenance
from jra_static_owner_executable import compile_static_owner
from jra_krs_input_builder_production import build_krs_input

PEDIGREE_FEATURES = frozenset(('pedigree_surface', 'pedigree_distance', 'pedigree_class',
    'maternal_class_signal', 'sire_track_signal', 'sire_newcomer_signal',
    'physical_pedigree_fit', 'sprint_pedigree'))


def compare(prepared, mapping, *, source_sha, receipt_sha, algorithm_freeze_at, cutoff,
            enhanced_features=None):
    """Recompute A/B/C; caller owns temporal authentication and freeze publication.

    Removing a pedigree-derived distance_fit also ablates its CFI contribution.
    C retains the authorized missing-information DCR policy, never a new weight.
    KRS inputs are evaluated, not a claim that simulation/MEC/Capital executed.
    """
    arms = {}
    for name in ('A_CURRENT', 'B_PEDIGREE_ENHANCED_SHADOW', 'C_BLOODLINE_ABLATION'):
        req = copy.deepcopy(prepared)
        for runner in req['runners']:
            features = runner['evidence_features']
            if name.startswith('B_') and enhanced_features is not None:
                # Non-pedigree information remains identical in every arm.
                for key, spec in enhanced_features.get(str(runner['runner_id']), {}).items():
                    if key in PEDIGREE_FEATURES:
                        features[key] = copy.deepcopy(spec)
            if name.startswith('C_'):
                runner['evidence_features'] = {k:v for k,v in features.items()
                    if k not in PEDIGREE_FEATURES
                    and v.get('source_authority') != 'JRA_OFFICIAL_POINT_IN_TIME_CORPUS'}
        req = materialize_index_provenance(attach_production_ledger_to_request(req, mapping))
        owner = compile_static_owner(req, source_snapshot_sha256=source_sha,
            source_receipt_sha256=receipt_sha, frozen_at=algorithm_freeze_at,
            prediction_cutoff=cutoff)
        krs = build_krs_input(req)['krs_input_data']
        arms[name] = {'owner': owner, 'krs_input': krs,
            'bvi': {str(r['runner_id']):r['canonical_components']['BVI'] for r in req['runners']},
            'numerical_provenance_sha256':req['index_provenance_hash'],
            'candidate_only': True, 'production_authority': False, 'purchase_authority': False,
            'krs_simulation_executed': False, 'mec_executed': False,
            'ticket_count': None, 'capital_required': None}
    return {'arms': arms, 'enhanced_input_distinct': enhanced_features is not None,
        'same_runner_universe': True, 'same_mapping_and_cutoff': True,
        'production_effect': 'NONE', 'predictive_improvement_demonstrated': False}

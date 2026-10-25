from copy import deepcopy
from pathlib import Path
import json
import pytest
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))
from jra_bvi_consumption import build_bvi_consumption
from jra_evidence_to_base_production import attach_production_ledger_to_request
from jra_index_provenance_builder import materialize_index_provenance
ROOT=Path(__file__).resolve().parents[1]

def inputs():
    req=json.loads(next((ROOT/'runtime/requests').glob('*KYO-20261011-R07*FORMAL.json')).read_text())
    mapping=json.loads((ROOT/'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json').read_text())
    return req,mapping

def test_actual_bvi_contributions_reconstruct_every_canonical_value_without_mutation():
    req,mapping=inputs();before=deepcopy(req);out=build_bvi_consumption(req,mapping)
    assert req==before
    assert len(out['runners'])==len(req['runners'])
    for row in out['runners']:
        assert row['baseline']+sum(c['value_contribution'] for c in row['components'])==pytest.approx(row['bvi_value'],abs=1e-6)
    assert not out['prediction_improvement_demonstrated']

def test_dcr_only_never_claims_measured_pedigree_or_officially_unpublished():
    req,mapping=inputs()
    for runner in req['runners']:
        for key in mapping['index_profiles']['ESTABLISHED']['BVI']:
            runner['evidence_features'].pop(key,None)
        for profile in mapping['index_profiles'].values():
            for key in profile['BVI']:runner['evidence_features'].pop(key,None)
    req=materialize_index_provenance(attach_production_ledger_to_request(req,mapping))
    out=build_bvi_consumption(req,mapping)
    assert all(r['bvi_value']==50 and r['consumption_class']=='DCR_ONLY' and r['components']==[] for r in out['runners'])

def test_tampered_bvi_is_rejected():
    req,mapping=inputs();req['runners'][0]['canonical_components']['BVI']['value']+=1
    with pytest.raises(ValueError,match='NUMERICAL_MISMATCH'):build_bvi_consumption(req,mapping)


def test_frozen_corpus_snapshot_binding_is_trace_only_and_rejects_tamper():
    from jra_bvi_consumption import sha
    req,mapping=inputs();before=deepcopy(req['runners'])
    refs=['ATTESTED_HARVEST:'+'a'*64]
    req.setdefault('source_to_evidence_feature_compiler',{})['pedigree_corpus_manifest']={
        'snapshots':refs,'snapshot_count':1,'manifest_sha256':sha(refs)}
    out=build_bvi_consumption(req,mapping)
    assert out['corpus_artifact_lineage_status']=='FROZEN_SNAPSHOT_LIST_BOUND'
    assert req['runners']==before
    req['source_to_evidence_feature_compiler']['pedigree_corpus_manifest']['snapshots']=['tampered']
    with pytest.raises(ValueError,match='CORPUS_MANIFEST_BINDING_INVALID'):build_bvi_consumption(req,mapping)


@pytest.mark.parametrize('venue,no',[('TKY','03'),('TKY','04'),('NGT','03'),('NGT','04')])
def test_oct17_real_formal_bridge_annotations_preserve_frozen_static(venue,no):
    from jra_bvi_static_proof import verify_static_proof
    from jra_bvi_consumption import sha
    p=ROOT/'runtime/requests'/f'KM-JRA-{venue}-20261017-R{no}-LIVE-R1-FORMAL.json'
    req=json.loads(p.read_text());before=deepcopy(req)
    # Reproduce the original production hash mismatch, then exercise the same
    # Numerical -> BVI consumption boundary reached by the real Formal runner.
    literal={k:req[k] for k in ('static_prediction','role_registry','pair_dispositions','third_dispositions','purchased_heads')}
    assert sha(literal)!=req['bvi_static_consumption_proof']['formal_semantic_output_sha256']
    replay=materialize_index_provenance(req)
    assert verify_static_proof(req['bvi_static_consumption_proof'],replay)
    out=build_bvi_consumption(replay,json.loads((ROOT/'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json').read_text()))
    assert out['static_execution_proof_status']=='BOUND_ACTUAL_EXECUTION'
    assert len(out['runners'])==len(req['runners']) and req==before


@pytest.mark.parametrize('change',['ranking','pair','BVI','receipt','checkpoint','extra_prediction_field'])
def test_oct17_proof_repair_still_rejects_real_input_tampering(change):
    from jra_bvi_static_proof import verify_static_proof
    req=json.loads((ROOT/'runtime/requests/KM-JRA-TKY-20261017-R03-LIVE-R1-FORMAL.json').read_text())
    if change=='ranking':req['static_prediction']['ranking'].reverse()
    elif change=='pair':req['pair_dispositions'][0]['second']='999'
    elif change=='BVI':req['runners'][0]['canonical_components']['BVI']['value']+=1
    elif change=='receipt':req['static_prediction']['source_basis_receipt_sha256']='f'*64
    elif change=='checkpoint':req['source_checkpoint_manifest']['sha256']='f'*64
    else:req['static_prediction']['unapproved_prediction_adjustment']=1
    with pytest.raises(ValueError,match='BVI_STATIC_PROOF_'):
        verify_static_proof(req['bvi_static_consumption_proof'],req)

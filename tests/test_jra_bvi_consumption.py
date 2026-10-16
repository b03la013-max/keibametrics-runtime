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

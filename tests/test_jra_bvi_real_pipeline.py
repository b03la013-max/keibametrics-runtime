"""Integration with stored real Kyoto numerical data; independent OIDC is CI-owned."""
from copy import deepcopy
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from jra_bvi_shadow_comparison import compare
from jra_index_provenance_builder import materialize_index_provenance


def test_real_kyoto_full20_replay_and_bloodline_ablation_do_not_mutate_final():
    mapping=json.loads((ROOT/'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json').read_text())
    for no in ('07','12'):
        req=json.loads(sorted((ROOT/'runtime/requests').glob(f'*KYO-20261011-R{no}*FORMAL.json'))[-1].read_text())
        original=deepcopy(req)
        out=compare(req,mapping,source_sha=req['source_snapshot_sha256'],receipt_sha='0'*64,
                    algorithm_freeze_at=req['static_freeze_timestamp'],cutoff=req['prediction_cutoff'])
        assert req==original
        a=out['arms']['A_CURRENT']; b=out['arms']['B_PEDIGREE_ENHANCED_SHADOW'];c=out['arms']['C_BLOODLINE_ABLATION']
        assert a['bvi']==b['bvi']
        assert not out['enhanced_input_distinct']
        for row in req['runners']:
            rid=row['runner_id']
            assert a['bvi'][rid]['value']==row['canonical_components']['BVI']['value']
            assert c['bvi'][rid]['value']==50
            assert c['bvi'][rid]['information_status']=='INFORMATION_INSUFFICIENT_DCR_ART3'
            assert c['bvi'][rid]['components']==[]
        assert not c['purchase_authority'] and c['ticket_count'] is None
        replay=materialize_index_provenance(req)
        for old,new in zip(req['runners'],replay['runners']):
            for key in old['canonical_components']:
                assert old['canonical_components'][key]['value']==new['canonical_components'][key]['value']
            assert 'components' in new['canonical_components']['BVI']

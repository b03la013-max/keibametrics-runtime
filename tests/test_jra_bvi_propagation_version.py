import sys
sys.path.insert(0, "runtime")
from jra_bvi_consumption import _bvi_propagation

V10 = {'direct_derived': ['TPI'], 'indirect_derived': ['SRI', 'F3S', 'T3I'],
       'no_direct_bvi_term': ['ZAI_WIN', 'ZAI_PLACE'],
       'static_winner_ranking': 'ZAI_WIN; BVI-only change does not directly change W ranking'}


def test_v10_wording_unchanged_for_1114():
    assert _bvi_propagation('KM-JRA-TKY-20261114-R12') == V10


def test_frozen_1115_artifacts_keep_original_wording():
    assert _bvi_propagation('KM-JRA-KYO-20261115-R04') == V10


def test_v11_describes_direct_bvi_term_from_1116():
    p = _bvi_propagation('KM-JRA-KYO-20261121-R04')
    assert p['zai_formula_version'] == 'v1.1'
    assert p['no_direct_bvi_term'] == []
    assert 'ZAI_WIN' in p['direct_derived'] and 'ZAI_PLACE' in p['direct_derived']
    assert p['zai_bvi_weight']['ZAI_WIN'] > 0 and p['zai_bvi_weight']['ZAI_PLACE'] > 0

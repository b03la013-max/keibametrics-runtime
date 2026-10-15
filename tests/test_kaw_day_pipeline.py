"""Real frozen regressions; new conversion remains post-event and PAPER."""
import gzip,json,copy,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from runtime.local_race_key_shadow_owner import compile_candidate_portfolio
from runtime.local_race_key_shadow_owner import settle_ticket_capital_portfolios
ROOT=Path(__file__).resolve().parents[1]

def report():return json.loads(gzip.decompress((ROOT/'research/kaw_day_20261014/candidate_comparison.json.gz').read_bytes()))


def test_all_12_including_missing_and_failed_cases_remain_in_denominator():
    r=json.loads((ROOT/'research/kaw_day_20261014/execution_audit.json').read_text())
    assert [x['race_no'] for x in r['rows']]==list(range(1,13))
    assert r['summary']=={'signed_final_count':5,'result_count':5,'delivery_proven_count':0,'missing_execution_count':4}
    assert all(x['external_verify']['valid'] for x in r['receipts'])


def test_four_original_pfs_receipt_refs_and_independent_ticket_types():
    r=json.loads(gzip.decompress((ROOT/'research/kaw_day_20261014/performance.json.gz').read_bytes()))
    expected={4:(22900,5130),5:(25600,13910),11:(14400,0),12:(16800,0)}
    for x in r:
        a=x['arms']['PRODUCTION'];assert (a['settlement']['investment'],a['settlement']['return'])==expected[x['race_no']]
        assert x['actual_purchase']=='UNKNOWN'
        if x['race_no'] in [4,5]:
            assert a['capture']['exact'] is True and a['capture']['trio'] is False


def test_column_selection_success_and_failure_saved_without_outcome_fill():
    rows=report()
    r4=next(r for r in rows if '-R04-' in r['race_id']);r11=next(r for r in rows if '-R11-' in r['race_id'])
    assert r4['arms']['v0.1']['settlements']['HEAD_LOCAL_COLUMNS']['capture']['exact']
    assert not r11['arms']['v0.1']['settlements']['HEAD_LOCAL_COLUMNS']['capture']['exact']
    for row in rows:
        assert row['genuine_forward_count']==0 and row['temporal_class']=='POST_EVENT_CONVERSION_REPLAY'
        for arm in row['arms'].values():
            assert arm['frozen_prediction_reproduced']
            p=arm['portfolio'];assert not p['production_authority']
            assert p['budget'] is None
            for scenario in arm['budget_scenarios'].values():
                for cell in scenario.values():
                    cap=cell['capital']
                    if cap['no_bet']:assert cell['settlement']['investment']==0
                    else:assert cell['settlement']['investment']<=cap['capital_limit']


def test_no_signed_final_or_delivery_inferred_from_successful_job(monkeypatch):
    from runtime import local_race_key_gate as gate
    monkeypatch.setattr(gate.o,'resolve_phase',lambda *args:None)
    state=gate.terminal_state('MISSING','success')
    assert state['status']=='NO_SIGNED_FINAL'
    assert not state['signed_final_pass'] and not state['prestart_delivery_pass']


def test_candidate_settlement_rejects_unverified_or_wrong_final_lineage():
    final={'receipt_sha256':'f','artifact':{'final_prediction_package':{}}}
    result={'artifact':{'frozen_refs':{'final_receipt_sha256':'wrong'}}}
    with pytest.raises(ValueError,match='SIGNATURE'):settle_ticket_capital_portfolios(final,result,signatures_verified=False)
    with pytest.raises(ValueError,match='LINEAGE'):settle_ticket_capital_portfolios(final,result,signatures_verified=True)


def test_saved_final_flags_cannot_override_fresh_signature_failure(monkeypatch):
    from runtime import local_race_key_gate as gate
    from runtime import execution_gateway as gateway
    monkeypatch.setattr(gate.o, 'resolve_phase', lambda *a: {'run_dir': 'unused'})
    values = {'final_receipt_envelope.json': {'receipt': {'status': 'PASS', 'race_id': 'race'}},
              'receipt_verifications.json': {'FINAL': True},
              'final_before_post_verification.json': {'verified': True}}
    monkeypatch.setattr(gate.o, '_load_checkpoint_json', lambda p, name: values[name])
    monkeypatch.setattr(gateway, 'request_json', lambda *a, **k: (200, {'valid': False}))
    result = gate.terminal_state('race', 'success')
    assert result['status'] == 'HOLD'
    assert result['signed_final_pass'] is False
    assert result['render_available'] is False
    assert result['prestart_delivery_pass'] is False

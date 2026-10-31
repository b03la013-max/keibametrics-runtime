import hashlib
import json
import sys
from pathlib import Path
import unittest
from copy import deepcopy
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from jra_production_postresult import (
    build_result_request, build_settlement_correction, settle_final, verify_final, ProductionPostResultError, _sha,
)
from post_result_learning import build_post_result_review


def final(decision="EXECUTE_RECOMMENDATION_PORTFOLIO", receipt_ts="2026-10-11T06:30:00+00:00"):
    tickets = [
        {"bet_type": "EXACTA", "selection": [4, 2], "stake": 100},
        {"bet_type": "EXACTA", "selection": [2, 4], "stake": 100},
        {"bet_type": "TRIFECTA", "selection": [4, 2, 6], "stake": 100},
    ]
    f = {
        "race_id": "KM-JRA-TKY-20261011-R11", "family_id": "JRA",
        "temporal_mode": "FORMAL-PRE-RACE",
        "prediction_cutoff": "2026-10-11T06:20:00+00:00",
        "scheduled_post_at": "2026-10-11T06:45:00+00:00",
        "static_prediction": {"ranking": ["4", "2", "6", "1"]},
        "final_prediction_package": {"roles": {"4": ["W", "P2", "P3"], "2": ["W", "P2", "P3"], "6": ["P3"]},
                                     "validation_status": "UNVALIDATED"},
        "capital_policy_decision": {"decision": decision},
        "final_ticket": {"tickets": tickets, "total_investment": 300, "no_bet": False},
        "final_receipt": {"receipt": {"timestamp": receipt_ts}},
        "final_receipt_sha256": "f" * 64,
    }
    f["sha256"] = _sha(f)
    return f


OFFICIAL = {"top3": [4, 2, 6], "payouts": {
    "EXACTA": {"selection": [4, 2], "per_100_yen": 1230},
    "TRIO": {"selection": [2, 4, 6], "per_100_yen": 2210},
    "TRIFECTA": {"selection": [4, 2, 6], "per_100_yen": 9870}}}
EVIDENCE = {"parsed": {"runners": [{"horse_no": h, "finish": i + 1} for i, h in enumerate([4, 2, 6, 1])]},
            "url": "https://www.jra.go.jp/x", "sha256": "a" * 64, "captured_at": "2026-10-11T07:00:00+00:00"}

WITHDRAWAL_OFFICIAL={"top3":[4,2,1],"refund_runner_ids":[6],"payouts":{
    "EXACTA":{"selection":[4,2],"per_100_yen":1230},
    "TRIO":{"selection":[1,2,4],"per_100_yen":2210},
    "TRIFECTA":{"selection":[4,2,1],"per_100_yen":9870}}}


class TestProductionPostResult(unittest.TestCase):
    def test_settles_exact_frozen_tickets_and_separates_purchase(self):
        s = settle_final(final(), OFFICIAL)
        self.assertEqual(s["total_investment"], 300)
        self.assertEqual(s["total_payout"], 1230 + 9870)
        self.assertEqual(s["actual_purchase_status"], "UNVERIFIED")
        self.assertIsNone(s['actual_purchase_pfs'])
        self.assertEqual(s['capital_exposure_class'],'RECOMMENDATION')
        self.assertEqual(len(s["winning_tickets"]), 2)

    def test_request_feeds_canonical_review(self):
        f = final()
        req = build_result_request(f, OFFICIAL, EVIDENCE)
        self.assertEqual(req["official_result"]["finish_order"], [4, 2, 6, 1])
        self.assertEqual(req["frozen_prediction_ref"]["immutable_final_sha256"], f["sha256"])
        review = build_post_result_review(req, f)
        self.assertEqual(review["race_id"], f["race_id"])

    def test_tampered_or_late_final_rejected(self):
        f = final()
        f["final_ticket"]["total_investment"] = 200
        with self.assertRaisesRegex(ProductionPostResultError, "HASH_INVALID"):
            verify_final(f)
        with self.assertRaisesRegex(ProductionPostResultError, "AFTER_POST"):
            verify_final(final(receipt_ts="2026-10-11T06:46:00+00:00"))


if __name__ == "__main__":
    unittest.main()


def test_refunds_use_official_withdrawn_runner_and_net_risk_denominator():
    f=final(); before=deepcopy(f)
    official={**deepcopy(WITHDRAWAL_OFFICIAL),"non_finishers":[
        {"horse_no":6,"finish_status":"EXCLUDED"}]}
    # The affected trifecta must be returned once, never both won and returned.
    s=settle_final(f,official)
    assert s['total_investment']==300 and s['refund']==100
    assert s['effective_investment']==200 and s['total_payout']==1230
    assert s['profit_loss']==1030 and s['pfs']==615
    assert len(s['refunded_tickets'])==1 and len(s['winning_tickets'])==1
    assert f==before
    req=build_result_request(f,official,EVIDENCE)
    review=build_post_result_review(req,f)
    assert review['capital']['refund']==100 and review['capital']['effective_investment']==200
    assert review['capital']['profit_loss']==1030 and review['capital']['pfs']==615


def test_wholly_refunded_or_zero_stake_has_undefined_pfs():
    f=final();f['final_ticket'].update(tickets=[f['final_ticket']['tickets'][-1]],total_investment=100)
    s=settle_final(f,WITHDRAWAL_OFFICIAL)
    assert s['refund']==100 and s['effective_investment']==0
    assert s['total_payout']==0 and s['profit_loss']==0 and s['pfs'] is None
    f=final();f['final_ticket'].update(tickets=[],total_investment=0,no_bet=True)
    s=settle_final(f,OFFICIAL)
    assert s['pfs'] is None and s['gross_stake_pfs'] is None


@pytest.mark.parametrize('status',['DID_NOT_FINISH','DISQUALIFIED'])
def test_noncompletion_and_disqualification_are_not_withdrawal_refunds(status):
    official={**OFFICIAL,'refund_runner_ids':[6],
              'non_finishers':[{'horse_no':6,'finish_status':status}]}
    with pytest.raises(ProductionPostResultError,match='NONCANCELLATION_REFUND_FORBIDDEN'):
        settle_final(final(),official)


def test_refund_correction_is_a_separate_audit_and_keeps_original_bytes():
    f=final(); original=build_result_request(f,OFFICIAL,EVIDENCE)
    unchanged=json.dumps([f,original],ensure_ascii=False,sort_keys=True)
    corrected=WITHDRAWAL_OFFICIAL
    audit=build_settlement_correction(f,original,corrected,EVIDENCE,
                                    audited_at='2026-10-11T07:10:00+00:00')
    assert audit['corrected_settlement']['refund']==100
    assert audit['original_settlement']['refund']==0
    assert audit['signed_result_correction']=='NOT_ISSUED'
    assert audit['old_learning_unchanged'] and audit['original_frozen_prediction_unchanged']
    assert audit['sha256']==_sha({k:v for k,v in audit.items() if k!='sha256'})
    assert json.dumps([f,original],ensure_ascii=False,sort_keys=True)==unchanged
    with pytest.raises(ProductionPostResultError,match='CHRONOLOGY'):
        build_settlement_correction(f,original,corrected,EVIDENCE,
                                    audited_at='2026-10-11T06:59:59+00:00')


def test_legacy_zero_refund_review_hash_is_unchanged_by_refund_support():
    req=build_result_request(final(),OFFICIAL,EVIDENCE)
    req['settlement'].pop('effective_investment')
    review=build_post_result_review(req,final())
    assert 'refund' not in review['capital'] and 'effective_investment' not in review['capital']


def _portable_source_checkpoint(tmp_path):
    """Small synthetic crypto fixture; no private Raw or retained key files."""
    import base64
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from execution_store import persist_phase
    f = final()
    race = f['race_id']
    execution = race + '-LIVE-R1'
    active = [{'runner_id': n, 'horse_no': int(n), 'status': 'ACTIVE'}
              for n in f['static_prediction']['ranking']]
    source = {'race_id': race, 'family_id': 'JRA', 'source_freeze_at': '2026-10-11T06:00:00Z',
              'official_runner_universe': {'runners': active},
              'jra_declared_runner_universe': {'runners': active + [
                  {'runner_id': '13', 'horse_no': 13, 'status': 'CANCELLED'}]}}
    source['source_snapshot_sha256'] = _sha(source)
    receipt = {'race_id': race, 'family': 'JRA', 'phase': 'SOURCE', 'status': 'PASS',
               'errors': [], 'artifact_sha256': _sha(source)}
    key = Ed25519PrivateKey.generate()
    envelope = {'artifact': source, 'receipt': receipt, 'receipt_sha256': _sha(receipt),
                'github_repository': 'b03la013-max/keibametrics-runtime',
                'signature_alg': 'Ed25519',
                'signer_trust_class': 'GITHUB_ACTIONS_EPHEMERAL_ED25519_PLUS_GITHUB_OIDC_ATTESTATION',
                'receipt_public_key_b64': base64.b64encode(key.public_key().public_bytes(
                    serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode(),
                'signature': base64.b64encode(key.sign(json.dumps(receipt, ensure_ascii=False,
                    sort_keys=True, separators=(',', ':')).encode())).decode()}
    stage = {'execution_id': execution, 'receipt_sha256': envelope['receipt_sha256'],
             'source_snapshot_sha256': source['source_snapshot_sha256']}
    f['source_snapshot_sha256'] = source['source_snapshot_sha256']
    f['final_prediction_package']['execution_stage_manifest'] = {
        'SIGNED_SOURCE_RECEIPT_VERIFIED': stage}
    f['sha256'] = _sha({k: v for k, v in f.items() if k != 'sha256'})
    checkpoint = tmp_path / 'synthetic_input'
    checkpoint.mkdir()
    (checkpoint / 'source_receipt_envelope.json').write_text(json.dumps(envelope))
    stored = persist_phase(execution, 'SOURCE', 'synthetic-1', checkpoint,
                           root=tmp_path / 'runtime/executions')
    return f, Path(stored['path']) / 'source_receipt_envelope.json'


def test_portable_source_checkpoint_binds_crypto_declared_active_and_ticket_exposure(tmp_path, monkeypatch):
    import jra_production_postresult as module
    import jra_pedigree_corpus as trust
    f, path = _portable_source_checkpoint(tmp_path)
    calls = []
    monkeypatch.setattr(trust, '_attested', lambda p, **kw: calls.append((p, kw)) or True)
    declared, cancelled = module._source_bound_result_universe(tmp_path, f)
    assert set(declared) == {'1', '2', '4', '6', '13'} and cancelled == {'13'}
    assert calls[0][0] == path
    assert calls[0][1]['signer'] == 'km-jra-source-first-runner.yml'
    assert calls[0][1]['not_after'].isoformat() == f['prediction_cutoff']
    f['final_ticket']['tickets'][0]['selection'] = [4, 13]
    with pytest.raises(ValueError, match='FROZEN_TICKET_OUTSIDE_ACTIVE_SOURCE'):
        module._source_bound_result_universe(tmp_path, f)


def test_portable_source_oidc_failure_or_original_bytes_tamper_is_not_accepted(tmp_path, monkeypatch):
    import jra_production_postresult as module
    import jra_pedigree_corpus as trust
    f, path = _portable_source_checkpoint(tmp_path)
    monkeypatch.setattr(trust, '_attested', lambda *a, **k: False)
    with pytest.raises(ValueError, match='SOURCE_OIDC_NOT_VERIFIED'):
        module._source_bound_result_universe(tmp_path, f)
    path.write_text('{}')
    with pytest.raises(ValueError, match='EXECUTION_STORE_FILE_HASH_MISMATCH'):
        module._source_bound_result_universe(tmp_path, f)


def _portable_normal_process(tmp_path, monkeypatch, parsed):
    import jra_production_postresult as module
    import jra_candidate_postresult_closedloop as result_module
    from datetime import datetime, timezone
    f = final()
    output = tmp_path / 'runtime/final_artifacts' / (f['race_id'] + '.json')
    output.parent.mkdir(parents=True)
    output.write_text(json.dumps(f))
    monkeypatch.setattr(module, 'verify_archived_final_signature', lambda *a, **k: None)
    monkeypatch.setattr(module.subprocess, 'check_output', lambda *a, **k: '2026-10-11T06:00:00+00:00')
    monkeypatch.setattr(module, '_intent_for', lambda *a: {
        'race_date': '2026-10-11', 'race_no': 11, 'jra_source': {'jra_meeting_key': '0520260403'}})
    def source_must_not_be_called(*a):
        raise AssertionError('NORMAL_RESULT_NEW_SOURCE_GATE')
    monkeypatch.setattr(module, '_source_bound_result_universe', source_must_not_be_called)
    evidence = {'parsed': parsed,
                'text': '払戻金 単勝 4 200円 馬単 4-2 1230円 3連複 2-4-6 2210円 3連単 4-2-6 9870円',
                'url': 'https://www.jra.go.jp/JRADB/accessS.html', 'sha256': 'a' * 64,
                'captured_at': '2026-10-11T07:00:00Z'}
    monkeypatch.setattr(result_module, 'fetch_jra_result', lambda *a: evidence)
    return module.process(tmp_path, f['race_id'], now=datetime(2026, 10, 11, 8, tzinfo=timezone.utc))


def test_portable_normal_old_checkpoint_needs_no_new_source_or_oidc_gate(tmp_path, monkeypatch):
    parsed = {'official': True, 'runners': [
        {'runner_id': str(n), 'horse_no': n, 'finish': i + 1} for i, n in enumerate([4, 2, 6, 1])],
        'non_finishers': []}
    assert _portable_normal_process(tmp_path, monkeypatch, parsed) == 'RESULT_REQUEST_WRITTEN'


def test_portable_duplicate_normal_universe_uses_old_strict_path(tmp_path, monkeypatch):
    parsed = {'official': True, 'runners': [
        {'runner_id': str(n), 'horse_no': n, 'finish': i + 1} for i, n in enumerate([4, 2, 6, 1, 1])],
        'non_finishers': []}
    with pytest.raises(ValueError, match='RUNNER_UNIVERSE_MISMATCH'):
        _portable_normal_process(tmp_path, monkeypatch, parsed)

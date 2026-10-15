import copy
import hashlib
import json
import multiprocessing
import pathlib
import sys

import pytest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "runtime"))
import execution_store as store
import openai_prediction_owner_candidate as owner
from test_openai_prediction_owner_candidate import sample


def reserve_worker(args):
    root, key, limit = args
    try:
        store.update_api_reservation(root, month="2026-10", race_id="A", request_sha=key,
                                     amount=1, monthly_limit=limit, race_limit=limit)
        return "RESERVED"
    except store.ExecutionStoreError as e:
        return str(e)


@pytest.mark.parametrize("limit,unique,expected", [(0, True, 0), (3, True, 3), (8, False, 1)])
def test_shared_store_concurrent_reservation(tmp_path, limit, unique, expected):
    keys = [hashlib.sha256(str(i if unique else 0).encode()).hexdigest() for i in range(12)]
    with multiprocessing.get_context("fork").Pool(4) as workers:
        results = workers.map(reserve_worker, [(str(tmp_path), key, limit) for key in keys])
    assert results.count("RESERVED") == expected
    if expected:
        rows = json.loads((tmp_path / "api-budget.json").read_text())["requests"]
        assert sum(r["reserved"] for r in rows.values()) <= limit


def test_crash_timeout_and_429_never_release_unknown_cost(tmp_path):
    k = hashlib.sha256(b"request").hexdigest()
    args = dict(root=tmp_path, month="2026-10", race_id="A", request_sha=k,
                amount=2, monthly_limit=2, race_limit=2)
    store.update_api_reservation(**args)
    store.update_api_reservation(**args, action="START")
    # A crashed Worker leaves STARTED durable; retry cannot re-reserve.
    with pytest.raises(store.ExecutionStoreError, match="DUPLICATE"):
        store.update_api_reservation(**args)
    row = store.update_api_reservation(**args, action="UNKNOWN")
    assert row["actual"] is None and row["reserved"] == 2
    with pytest.raises(store.ExecutionStoreError, match="BUDGET-HOLD"):
        store.update_api_reservation(**{**args, "request_sha": hashlib.sha256(b"retry").hexdigest()})
    with pytest.raises(store.ExecutionStoreError, match="TRANSITION"):
        store.update_api_reservation(**args, action="SETTLE", actual=3)
    store.update_api_reservation(**args, action="SETTLE", actual=0)
    # Confirmed zero bill does not automatically reopen or repeat request.
    with pytest.raises(store.ExecutionStoreError, match="DUPLICATE"):
        store.update_api_reservation(**args)


def test_corrupt_budget_ledger_is_terminal(tmp_path):
    (tmp_path / "api-budget.json").write_text('{"requests":{}}')
    assert reserve_worker((str(tmp_path), hashlib.sha256(b"x").hexdigest(), 2)) == "BUDGET_LEDGER_INCONSISTENT_HOLD"


def test_historical_resume_never_generates_or_refreezes(sample, tmp_path, monkeypatch):
    context, config, _, call, now = sample
    context["execution_class"] = "HISTORICAL_BEHAVIORAL_COMPARISON"
    saved = owner.execute(context, config, root=tmp_path, call=call, now=now)
    original = copy.deepcopy(saved)
    monkeypatch.setattr(owner.urllib.request, "urlopen", lambda *a, **k: pytest.fail("network forbidden"))
    reused = owner.resume_historical_candidate(saved, context, config, root=tmp_path)
    assert reused["api_requests"] == 0 and reused["candidate"] == original
    assert saved == original and reused["count_increment"] == 0
    for field in ("race_id", "execution_id", "prediction_cutoff", "release_deadline_at"):
        altered = copy.deepcopy(saved)
        altered["lineage"][field] = "changed"
        with pytest.raises(owner.CandidateHold, match="BASIS_MISMATCH"):
            owner.resume_historical_candidate(altered, context, config, root=tmp_path)
    for field in ("input_sha256", "prediction_output_sha256", "current_authority_sha256", "model_identifier", "policy_sha256"):
        altered = copy.deepcopy(saved)
        altered["lineage"][field] = "changed"
        with pytest.raises(owner.CandidateHold, match="BASIS_MISMATCH"):
            owner.resume_historical_candidate(altered, context, config, root=tmp_path)
    context["source_verification"] = {"verified": False}
    with pytest.raises(owner.CandidateHold, match="CONTRACT_HOLD"):
        owner.resume_historical_candidate(saved, context, config, root=tmp_path)


def zero_call_worker(_):
    owner.urllib.request.urlopen = lambda *a, **k: (_ for _ in ()).throw(AssertionError("network forbidden"))
    try:
        owner.responses_call({}, timeout=1)
    except owner.CandidateHold as e:
        return str(e)


def test_zero_budget_concurrent_provider_boundary():
    with multiprocessing.get_context("fork").Pool(4) as workers:
        assert workers.map(zero_call_worker, range(12)) == ["API-BILLING-HOLD"] * 12


def test_shadow_preparation_requires_validated_historical_binding(sample, tmp_path):
    context, config, _, call, now = sample
    context["execution_class"] = "HISTORICAL_BEHAVIORAL_COMPARISON"
    saved = owner.execute(context, config, root=tmp_path, call=call, now=now)
    artifact = owner.prepare_shadow_receipt(saved, context, config, root=tmp_path)
    assert artifact["shadow_status"] == "HISTORICAL_REPLAY / NON-PRODUCTION / UNSIGNED"
    assert artifact["output_sha256"] == owner.digest(saved["prediction"])
    assert artifact["static_freeze_time"] == saved["lineage"]["freeze_timestamp"]
    saved["prediction_semantics"]["static_prediction"]["ranking"] = ["changed"]
    with pytest.raises(owner.CandidateHold, match="BASIS_MISMATCH"):
        owner.prepare_shadow_receipt(saved, context, config, root=tmp_path)


def test_workers_cannot_change_shared_limits(tmp_path):
    key = hashlib.sha256(b"first").hexdigest()
    args = dict(root=tmp_path, month="2026-10", race_id="A", request_sha=key,
                amount=1, monthly_limit=1, race_limit=1)
    store.update_api_reservation(**args)
    with pytest.raises(store.ExecutionStoreError, match="LIMIT_BASIS_MISMATCH"):
        store.update_api_reservation(**{**args, "monthly_limit": 20, "race_limit": 20,
                                        "request_sha": hashlib.sha256(b"second").hexdigest()})


def test_saved_source_signature_anchor_and_tamper(tmp_path):
    from jra_source_runtime.verify_source_envelope import verify
    root = pathlib.Path(__file__).resolve().parents[1]
    source = root / "runtime/executions/LOCAL-KM-LOCAL-FNB-20261001-R08-LIVE-R1-EXEC/SOURCE/runs/36840937924/source_receipt_envelope.json"
    envelope = json.loads(source.read_text())
    anchor = "jqWqOYlmhXXmpv/nR7lx3c2n/S5shDYava/WJVxn4kE="
    signer = "KM-LOCAL-RUNTIME-ED25519-20260922"
    assert verify(source, trusted_public_key_b64=anchor, trusted_signer_key_id=signer)["valid"]
    with pytest.raises(ValueError, match="TRUST_ANCHOR"):
        verify(source, trusted_public_key_b64="", trusted_signer_key_id=signer)
    with pytest.raises(ValueError, match="TRUST_ANCHOR"):
        verify(source, trusted_public_key_b64=anchor, trusted_signer_key_id="wrong")
    envelope["artifact"]["formal_ready"] = False
    changed = tmp_path / "changed.json"
    changed.write_text(json.dumps(envelope))
    with pytest.raises(ValueError, match="ARTIFACT_SHA"):
        verify(changed, trusted_public_key_b64=anchor, trusted_signer_key_id=signer)


def crash_worker(root, started):
    import os
    args = dict(root=root, month="2026-10", race_id="A", request_sha=hashlib.sha256(b"crash").hexdigest(),
                amount=1, monthly_limit=1, race_limit=1)
    store.update_api_reservation(**args)
    if started:
        store.update_api_reservation(**args, action="START")
    os._exit(17)


@pytest.mark.parametrize("started,state", [(False, "RESERVED"), (True, "STARTED")])
def test_actual_worker_exit_keeps_durable_reservation(tmp_path, started, state):
    child = multiprocessing.get_context("fork").Process(target=crash_worker, args=(str(tmp_path), started))
    child.start()
    child.join(timeout=5)
    assert child.exitcode == 17
    key = hashlib.sha256(b"crash").hexdigest()
    row = json.loads((tmp_path / "api-budget.json").read_text())["requests"][key]
    assert row["state"] == state and row["actual"] is None
    assert reserve_worker((str(tmp_path), key, 1)) == "DUPLICATE_REQUEST_HOLD"

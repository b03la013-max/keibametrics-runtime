import copy
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from runtime.execution_store import ExecutionStoreError, verify_result_reuse

ROOT = Path(__file__).resolve().parents[1]
EID = "LOCAL-KM-LOCAL-FNB-20261001-R08-LIVE-R1-EXEC"


def control():
    store = ROOT / "runtime/executions" / EID
    result = json.loads(next((store / "RESULT/runs").glob("*/result_receipt_envelope.json")).read_text())
    final = json.loads(next((store / "FORMAL/runs").glob("*/final_receipt_envelope.json")).read_text())
    payload = {"race_id": result["receipt"]["race_id"], "official_result": result["artifact"]["official_result"],
               "settlement": {k: result["artifact"]["settlement"][k] for k in (
                   "status", "investment", "settled_investment", "return")},
               "pfs_authority": "FROZEN-RECOMMENDATION"}
    return result, final, payload


def test_historical_control_reuse_is_not_a_new_settlement():
    result, final, payload = control()
    verdict = verify_result_reuse(result, final, payload, {"verified": True})
    assert verdict["status"] == "VERIFIED_REUSE"
    assert verdict["result_resigning"] is verdict["settlement_reexecution"] is False


@pytest.mark.parametrize("verified", [True, False])
def test_same_request_partial_result_automatically_runs_downstream_recovery(tmp_path, monkeypatch, verified):
    from runtime import formal_execution_orchestrator as orchestrator
    request = {"family_id": "LOCAL", "race_id": "CONTROL", "phase": "RESULT"}
    bound = {**request, "execution_id": orchestrator.derive_execution_id(request)}
    previous = {"run_dir": tmp_path, "latest": {"manifest_sha256": "frozen-manifest"}}
    monkeypatch.setattr(orchestrator, "resolve_phase", lambda *a: previous)
    files = {"result_checkpoint_basis.json": {"request_sha256": orchestrator._sha_obj(bound)},
             "receipt_verifications.json": {"RESULT": verified}, "result_receipt_envelope.json": {"receipt": {"phase": "RESULT"}}}
    monkeypatch.setattr(orchestrator, "_load_checkpoint_json", lambda p, filename: files.get(filename))
    monkeypatch.setattr(orchestrator, "materialize_phase", lambda *a: previous)
    completions = iter([{"complete": False}, {"complete": True, "execution_class": "STRICT-FULL"}])
    monkeypatch.setattr(orchestrator, "verify_execution_completion", lambda *a, **k: next(completions))
    calls = []
    monkeypatch.setattr(orchestrator, "run_phase", lambda *a, **k: calls.append((a, k)) or {"phase": "RESULT"})
    report = orchestrator.orchestrate(request, run_id="resume", github_sha="test",
                                      runtime_out=tmp_path / "out", tmp_root=tmp_path / "tmp")
    assert report["prediction_reexecution"] is False
    assert len(calls) == 1 and calls[0][0][1] == "RESULT"
    assert calls[0][1]["resume_result"] is previous


def test_same_workflow_retries_preserved_result_transport_without_new_prediction(tmp_path, monkeypatch):
    from runtime import formal_execution_orchestrator as orchestrator
    request = {"phase": "RESULT", "race_id": "CONTROL"}
    monkeypatch.setattr(orchestrator, "acquire_official_result_request", lambda *a, **k: request)
    monkeypatch.setattr(orchestrator, "time", type("Clock", (), {"monotonic": staticmethod(lambda: 0),
                                                                "sleep": staticmethod(lambda n: None)}))
    calls = []
    def execute(req, **kwargs):
        assert req is request
        calls.append(req)
        if len(calls) == 1:
            raise orchestrator.FormalOrchestrationError(json.dumps({
                "signed_result_preserved": True, "failure_class": "RUNTIME_TRANSPORT"}))
        return {"status": "ALREADY_COMPLETE", "prediction_reexecution": False}
    monkeypatch.setattr(orchestrator, "orchestrate", execute)
    result = orchestrator.resume_official_result({}, run_id="r", github_sha="s", runtime_out=tmp_path,
                                                 tmp_root=tmp_path, wait_seconds=30)
    assert len(calls) == 2 and result["prediction_reexecution"] is False


@pytest.mark.parametrize("case", ["signature", "race", "phase", "final", "outcome", "payout", "amount", "authority"])
def test_recovery_cannot_change_verified_lineage_or_finances(case):
    result, final, payload = map(copy.deepcopy, control())
    verification = {"verified": True}
    if case == "signature": verification = {"valid": True}
    if case == "race": result["receipt"]["race_id"] = "OTHER"
    if case == "phase": result["receipt"]["phase"] = "FINAL"
    if case == "final": final["receipt_sha256"] = "different"
    if case == "outcome": payload["official_result"]["finish_order"] = [1, 2, 3]
    if case == "payout": payload["official_result"]["payouts"]["EXACTA"] += 100
    if case == "amount": payload["settlement"]["return"] += 100
    if case == "authority": payload["pfs_authority"] = "ACTUAL-PURCHASE"
    with pytest.raises(ExecutionStoreError):
        verify_result_reuse(result, final, payload, verification)


@pytest.mark.skipif(os.environ.get("KM_ALLOW_OFFICIAL_READ_TEST") != "1", reason="Explicit external Runtime test")
def test_real_runtime_downstream_recovery_fresh_process(tmp_path):
    # Actual signed historical control and actual external /verify. No new
    # /result, SOURCE, Prediction, KRS, OOS entry or Production repository write.
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    for path in (ROOT / "runtime").glob("*.py"):
        (runtime / path.name).symlink_to(path)
    for folder in ("profiles", "mapping", "governance"):
        (tmp_path / folder).symlink_to(ROOT / folder, target_is_directory=True)
    # Read the unmodified immutable FINAL store; isolate every output/ledger
    # write and hold research in this downstream recovery control.
    (runtime / "executions").mkdir()
    result, _, payload = control()
    (tmp_path / "signed_result.json").write_text(json.dumps(result))
    request = {"family_id": "LOCAL", "execution_id": EID, "race_id": payload["race_id"],
               "phase": "RESULT", "temporal_mode": "RESULT", "acceptance_only": True,
               **payload["official_result"], "pfs_authority": "FROZEN-RECOMMENDATION"}
    (tmp_path / "request.json").write_text(json.dumps(request))
    wrapper = '''
import json, pathlib, runpy, sys
sys.path.insert(0, "runtime")
import execution_gateway, execution_store
root=pathlib.Path(sys.argv[1])
sys.path.insert(1,str(root/"runtime"))
sys.path.insert(1,str(root/"runtime/local_physical"))
from local_physical.nar_source_manifest import _result_source, LOCAL_BABA_CODES
from local_physical.source_acquisition import fetch_source
from formal_execution_orchestrator import parse_official_result_snapshot
identity={"venue_id":"FNB","race_date":"2026/10/01","race_no":8}
spec=_result_source("FNB",LOCAL_BABA_CODES["FNB"],"2026/10/01",8)
snapshot, errors=fetch_source(spec,"")
assert not errors and snapshot["final_url"]==spec["url"]
order,payouts=parse_official_result_snapshot(snapshot,identity,range(1,11))
signed=json.load(open("signed_result.json"))
official=signed["artifact"]["official_result"]
assert order[:len(official["finish_order"])]==official["finish_order"]
assert payouts==official["payouts"]
json.dump({"source":spec["url"],"raw_sha256":snapshot["raw_sha256"],
           "observed_at":snapshot["fetched_at"],"signed_result_match":True},
          open("official_recovery_observation.json","w"))
original=execution_gateway.request_json
def verify_only(url, **kwargs):
    if not url.endswith("/verify"):
        raise RuntimeError("TEST_FORBIDS_NEW_RESULT_OR_PREDICTION")
    return original(url, **kwargs)
execution_gateway.request_json=verify_only
original_materialize=execution_store.materialize_phase
def frozen_final_only(eid, phase, destination, **kwargs):
    assert phase == "FORMAL"
    result=original_materialize(eid, phase, destination, root=root/"runtime/executions")
    pathlib.Path(destination,"local_forward_measurement_pre_result.json").unlink(missing_ok=True)
    return result
execution_store.materialize_phase=frozen_final_only
sys.argv=["result-worker","request.json"]
runpy.run_module("runtime.local_result_from_signed_final",run_name="__main__")
'''
    (tmp_path / "recover.py").write_text(wrapper)
    env = {**os.environ, "KM_RESULT_REUSE_PATH": str(tmp_path / "signed_result.json")}
    proc = subprocess.run([sys.executable, "recover.py", str(ROOT)], cwd=tmp_path, env=env,
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr[-2000:]
    out = tmp_path / "runtime_out"
    assert json.loads((out / "result_recovery.json").read_text())["result_resigning"] is False
    assert json.loads((tmp_path / "official_recovery_observation.json").read_text())["signed_result_match"] is True
    assert json.loads((out / "result_receipt_envelope.json").read_text()) == result
    state = json.loads((out / "learning_state.json").read_text())
    assert state["race_id"] == payload["race_id"] and state["execution_id"] == EID
    assert state["production_policy_change"] is False
    assert json.loads((out / "forward_tracker_terminal.json").read_text())["status"] == "HOLD"

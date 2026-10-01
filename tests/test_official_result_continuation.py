import base64
import copy
import datetime as dt
import gzip
import hashlib
import json
import pathlib
import os
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "runtime"))
import formal_execution_orchestrator as runner


def snapshot(html):
    raw = html.encode()
    return {"http_status": 200, "official": True, "raw_sha256": hashlib.sha256(raw).hexdigest(),
            "raw_gzip_b64": base64.b64encode(gzip.compress(raw)).decode(), "content_type": "text/html; charset=utf-8"}


@pytest.fixture
def fixture():
    identity = {"venue_id": "FNB", "race_date": "2030/01/01", "race_no": 7}
    html = """<h4>2030年1月1日 船 橋 第7競走 競走成績</h4>
    <table><tr><th>着順</th><th>馬番</th><th>馬名</th></tr>
    <tr><td>1</td><td>6</td><td>A</td></tr>
    <tr><td>2</td><td>1</td><td>B</td></tr>
    <tr><td>3</td><td>2</td><td>C</td></tr></table>
    <table><tr><td>馬連単</td><td>6-1</td><td>940円</td><td>1人気</td></tr>
    <tr><td>三連複</td><td>1-2-6</td><td>2,220円</td><td>10人気</td></tr>
    <tr><td>三連単</td><td>6-1-2</td><td>8,760円</td><td>27人気</td></tr></table>"""
    return html, identity


def test_official_finish_and_payout_selections_verified(fixture):
    html, identity = fixture
    order, payouts = runner.parse_official_result_snapshot(snapshot(html), identity, [1, 2, 6])
    assert order == [6, 1, 2]
    assert payouts == {"EXACTA": 940, "TRIO": 2220, "TRIFECTA": 8760}


@pytest.mark.parametrize("case", ["wrong_race", "wrong_date", "wrong_venue", "dead_heat", "wrong_pair",
                               "missing_payout", "refund", "unknown_runner", "tamper"])
def test_ambiguous_result_never_settled(fixture, case):
    html, identity = fixture
    if case == "wrong_race": html = html.replace("第7", "第8")
    if case == "wrong_date": html = html.replace("1月1日", "1月2日")
    if case == "wrong_venue": html = html.replace("船 橋", "大井")
    if case == "dead_heat": html = html.replace("<td>2</td><td>1", "<td>1</td><td>1")
    if case == "wrong_pair": html = html.replace("6-1</td>", "1-6</td>")
    if case == "missing_payout": html = html.replace("三連単", "未確定")
    if case == "refund": html = html.replace("940円", "返還")
    if case == "unknown_runner": html = html.replace("<td>6</td>", "<td>9</td>")
    snap = snapshot(html)
    if case == "tamper": snap["raw_sha256"] = "invalid"
    with pytest.raises(runner.FormalOrchestrationError):
        runner.parse_official_result_snapshot(snap, identity, [1, 2, 6])


def test_real_archived_official_html_positive_control_without_new_settlement():
    # Offline parser regression only: does not manufacture Future/OOS evidence.
    root = pathlib.Path(__file__).resolve().parents[1]
    p = next((root / "runtime/executions/LOCAL-KM-LOCAL-FNB-20261001-R08-LIVE-R1-EXEC/SOURCE/runs").glob("*/source_receipt_envelope.json"))
    artifact = json.loads(p.read_text())["artifact"]
    snap = next(s for s in artifact["sources"] if s["source_id"].endswith("R07-RESULT"))
    identity = {"venue_id": "FNB", "race_date": "2026/10/01", "race_no": 7}
    order, payouts = runner.parse_official_result_snapshot(snap, identity, range(1, 13))
    assert order[:3] == [6, 1, 2]
    assert payouts == {"EXACTA": 940, "TRIO": 2220, "TRIFECTA": 8760}


def test_result_resume_never_invokes_prediction_and_duplicate_reuses_request(tmp_path, monkeypatch):
    calls = []
    request = {"execution_id": "A", "race_id": "A", "phase": "RESULT"}
    monkeypatch.setattr(runner, "acquire_official_result_request", lambda *a, **k: request)
    def result_only(intent, **kwargs):
        calls.append(intent)
        assert intent["phase"] == "RESULT"
        return {"status": "ALREADY_COMPLETE", "prediction_reexecution": False}
    monkeypatch.setattr(runner, "orchestrate", result_only)
    monkeypatch.setattr(runner, "execute_prediction_owner", lambda *a, **k: pytest.fail("Prediction rerun"))
    for _ in range(2):
        report = runner.resume_official_result({}, run_id="r", github_sha="sha", runtime_out=tmp_path,
                                              tmp_root=tmp_path)
        assert report["prediction_reexecution"] is False
    assert calls == [request, request]


def test_pending_result_has_no_completion_success(tmp_path, monkeypatch):
    def pending(*a, **k):
        raise runner.FormalOrchestrationError("OFFICIAL_RESULT_PAYOUT_NOT_READY")
    monkeypatch.setattr(runner, "acquire_official_result_request", pending)
    report = runner.resume_official_result({"execution_id": "A", "family_id": "LOCAL", "race_id": "A"},
                                          run_id="r", github_sha="s", runtime_out=tmp_path, tmp_root=tmp_path)
    assert report["status"] == "WAITING_OFFICIAL_RESULT"
    assert runner.completion_exit_code(report) != 0


@pytest.mark.parametrize("marker", ["審議中", "成績未確定", "着順未確定", "払戻未確定", "結果未確定"])
def test_provisional_official_page_with_complete_tables_cannot_settle(fixture, marker):
    html, identity = fixture
    with pytest.raises(runner.FormalOrchestrationError, match="OFFICIAL_RESULT_NOT_FINAL"):
        runner.parse_official_result_snapshot(snapshot(html + '<p>' + marker + '</p>'), identity, [1, 2, 6])


def test_provisional_state_waits_without_prediction_or_zero_settlement(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "acquire_official_result_request", lambda *a, **k: (_ for _ in ()).throw(
        runner.FormalOrchestrationError("OFFICIAL_RESULT_NOT_FINAL")))
    monkeypatch.setattr(runner, "orchestrate", lambda *a, **k: pytest.fail("Premature settlement"))
    report = runner.resume_official_result({"execution_id": "A", "family_id": "LOCAL", "race_id": "A"},
                                          run_id="r", github_sha="s", runtime_out=tmp_path, tmp_root=tmp_path)
    assert report["status"] == "WAITING_OFFICIAL_RESULT"
    assert report["prediction_reexecution"] is False
    assert "settlement" not in report


def test_dns_resolution_pending_preserves_wait_state(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "acquire_official_result_request", lambda *a, **k: (_ for _ in ()).throw(
        runner.FormalOrchestrationError("OFFICIAL_RESULT_TRANSPORT_PENDING")))
    report = runner.resume_official_result({"execution_id": "A", "family_id": "LOCAL", "race_id": "A"},
                                          run_id="r", github_sha="s", runtime_out=tmp_path, tmp_root=tmp_path)
    assert report["status"] == "WAITING_OFFICIAL_RESULT"
    assert runner.completion_exit_code(report) != 0


def test_cancelled_race_does_not_become_zero_settlement(fixture):
    html, identity = fixture
    with pytest.raises(runner.FormalOrchestrationError, match="CANCELLATION_HOLD"):
        runner.parse_official_result_snapshot(snapshot(html + '<p>競走取り止め</p>'), identity, [1, 2, 6])


@pytest.mark.skipif(os.environ.get("KM_ALLOW_OFFICIAL_READ_TEST") != "1", reason="Explicit read-only network test")
def test_real_official_nar_acquisition_in_fresh_process():
    # Known historical identity tests acquisition only, never prediction or OOS.
    physical = str(pathlib.Path(__file__).resolve().parents[1] / "runtime/local_physical")
    sys.path.insert(0, physical)
    from local_physical.nar_source_manifest import _result_source, LOCAL_BABA_CODES
    from local_physical.source_acquisition import fetch_source
    identity = {"venue_id": "FNB", "race_date": "2026/10/01", "race_no": 7}
    spec = _result_source("FNB", LOCAL_BABA_CODES["FNB"], "2026/10/01", 7)
    snap, errors = fetch_source(spec, "")
    assert not errors and snap["final_url"] == spec["url"]
    order, payouts = runner.parse_official_result_snapshot(snap, identity, range(1, 13))
    assert order[:3] == [6, 1, 2]
    assert payouts == {"EXACTA": 940, "TRIO": 2220, "TRIFECTA": 8760}


def test_post_signed_failure_preserves_verified_result_without_duplicate_settlement(tmp_path, monkeypatch):
    import execution_store
    from types import SimpleNamespace
    monkeypatch.setattr(execution_store, "DEFAULT_ROOT", tmp_path / "store")
    output = tmp_path / "out"
    request = {"execution_id": "A-EXEC", "family_id": "LOCAL", "race_id": "A"}
    def fail_after_signature(*a, **kw):
        (output / "result_receipt_envelope.json").write_text(json.dumps({"receipt": {"phase": "RESULT", "race_id": "A"}}))
        (output / "receipt_verifications.json").write_text(json.dumps({"RESULT": True}))
        return SimpleNamespace(returncode=1, stdout="", stderr="learning failed")
    monkeypatch.setattr(runner.subprocess, "run", fail_after_signature)
    with pytest.raises(runner.FormalOrchestrationError) as error:
        runner.run_phase(request, "RESULT", run_id="test", github_sha="sha", runtime_out=output, tmp_root=tmp_path)
    assert json.loads(str(error.value))["signed_result_preserved"] is True
    resolved = execution_store.resolve_phase("A-EXEC", "RESULT")
    assert runner._load_checkpoint_json(resolved, "result_checkpoint_basis.json") == {"request_sha256": runner._sha_obj(request)}
    assert runner._load_checkpoint_json(resolved, "post_signed_result_failure.json")["duplicate_settlement_forbidden"] is True

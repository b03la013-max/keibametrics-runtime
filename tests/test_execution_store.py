import json
import pathlib

import pytest

from runtime.execution_store import (
    ExecutionStoreError,
    materialize_phase,
    persist_phase,
    resolve_phase,
)


def test_execution_store_persists_and_resolves_latest(tmp_path: pathlib.Path):
    root = tmp_path / "executions"
    out = tmp_path / "runtime_out"
    out.mkdir()
    (out / "source_receipt_envelope.json").write_text('{"receipt_sha256":"abc"}', encoding="utf-8")
    (out / "source_verification.json").write_text('{"valid":true}', encoding="utf-8")

    persisted = persist_phase(
        "LOCAL-URW-20260926-R01-EXEC",
        "SOURCE",
        "1001",
        out,
        root=root,
        github_sha="deadbeef",
    )
    assert persisted["latest"]["run_id"] == "1001"

    resolved = resolve_phase("LOCAL-URW-20260926-R01-EXEC", "SOURCE", root=root)
    assert resolved is not None
    assert resolved["manifest"]["github_sha"] == "deadbeef"

    dest = tmp_path / "materialized"
    materialize_phase("LOCAL-URW-20260926-R01-EXEC", "SOURCE", dest, root=root)
    assert json.loads((dest / "source_receipt_envelope.json").read_text())["receipt_sha256"] == "abc"


def test_execution_store_keeps_history_and_advances_pointer(tmp_path: pathlib.Path):
    root = tmp_path / "executions"
    for run_id, value in (("1001", "a"), ("1002", "b")):
        out = tmp_path / ("out-" + run_id)
        out.mkdir()
        (out / "final_receipt_envelope.json").write_text(
            json.dumps({"receipt_sha256": value}), encoding="utf-8"
        )
        persist_phase("E", "FORMAL", run_id, out, root=root)

    resolved = resolve_phase("E", "FORMAL", root=root)
    assert resolved["latest"]["run_id"] == "1002"
    assert (root / "E" / "FORMAL" / "runs" / "1001").exists()
    assert (root / "E" / "FORMAL" / "runs" / "1002").exists()


def test_execution_store_detects_file_tamper(tmp_path: pathlib.Path):
    root = tmp_path / "executions"
    out = tmp_path / "out"
    out.mkdir()
    (out / "final_receipt_envelope.json").write_text('{"x":1}', encoding="utf-8")
    persisted = persist_phase("E", "FORMAL", "1001", out, root=root)
    run_dir = pathlib.Path(persisted["path"])
    (run_dir / "final_receipt_envelope.json").write_text('{"x":2}', encoding="utf-8")

    with pytest.raises(ExecutionStoreError, match="FILE_HASH_MISMATCH"):
        resolve_phase("E", "FORMAL", root=root)

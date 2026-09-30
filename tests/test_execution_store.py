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


def _checkpoint(tmp_path, run_id='1', value='a'):
    out = tmp_path / ('out-' + run_id)
    out.mkdir(exist_ok=True)
    (out / 'final_receipt_envelope.json').write_text(json.dumps({'value': value}))
    return out


def test_same_run_retry_preserves_manifest_bytes(tmp_path):
    root = tmp_path / 'store'
    out = _checkpoint(tmp_path)
    first = persist_phase('E', 'FORMAL', '1', out, root=root)
    before = {p.name: p.read_bytes() for p in pathlib.Path(first['path']).iterdir()}
    retry = persist_phase('E', 'FORMAL', '1', out, root=root)
    assert first['latest'] == retry['latest']
    assert before == {p.name: p.read_bytes() for p in pathlib.Path(retry['path']).iterdir()}


def test_same_run_changed_payload_does_not_overwrite(tmp_path):
    root = tmp_path / 'store'
    out = _checkpoint(tmp_path)
    persist_phase('E', 'FORMAL', '1', out, root=root)
    _checkpoint(tmp_path, value='different')
    with pytest.raises(ExecutionStoreError, match='IMMUTABLE_RUN_CONFLICT'):
        persist_phase('E', 'FORMAL', '1', out, root=root)
    resolved = resolve_phase('E', 'FORMAL', root=root)
    assert json.loads((resolved['run_dir'] / 'final_receipt_envelope.json').read_text())['value'] == 'a'


def test_old_run_retry_cannot_roll_back_pointer(tmp_path):
    root = tmp_path / 'store'
    one = _checkpoint(tmp_path, '1')
    two = _checkpoint(tmp_path, '2', 'b')
    persist_phase('E', 'FORMAL', '1', one, root=root)
    persist_phase('E', 'FORMAL', '2', two, root=root)
    persist_phase('E', 'FORMAL', '1', one, root=root)
    assert resolve_phase('E', 'FORMAL', root=root)['latest']['run_id'] == '2'


def test_copy_failure_does_not_publish_partial_run(tmp_path, monkeypatch):
    import runtime.execution_store as store
    root = tmp_path / 'store'
    persist_phase('E', 'FORMAL', '1', _checkpoint(tmp_path, '1'), root=root)
    def interrupted(*args):
        raise OSError('interrupted copy')
    monkeypatch.setattr(store.shutil, 'copy2', interrupted)
    with pytest.raises(OSError):
        persist_phase('E', 'FORMAL', '2', _checkpoint(tmp_path, '2'), root=root)
    assert resolve_phase('E', 'FORMAL', root=root)['latest']['run_id'] == '1'
    assert not (root / 'E/FORMAL/runs/2').exists()


def test_cross_execution_pointer_is_rejected(tmp_path):
    root = tmp_path / 'store'
    persist_phase('E', 'FORMAL', '1', _checkpoint(tmp_path), root=root)
    persist_phase('OTHER', 'FORMAL', '1', _checkpoint(tmp_path), root=root)
    pointer = root / 'E/FORMAL/LATEST.json'
    data = json.loads(pointer.read_text())
    data['run_path'] = 'OTHER/FORMAL/runs/1'
    pointer.write_text(json.dumps(data))
    with pytest.raises(ExecutionStoreError, match='RUN_PATH_MISMATCH'):
        resolve_phase('E', 'FORMAL', root=root)


def test_truncated_pointer_is_classified(tmp_path):
    root = tmp_path / 'store'
    persist_phase('E', 'FORMAL', '1', _checkpoint(tmp_path), root=root)
    (root / 'E/FORMAL/LATEST.json').write_text('{')
    with pytest.raises(ExecutionStoreError, match='POINTER_INVALID'):
        resolve_phase('E', 'FORMAL', root=root)


def test_materialization_excludes_unbound_extra_file(tmp_path):
    root = tmp_path / 'store'
    result = persist_phase('E', 'FORMAL', '1', _checkpoint(tmp_path), root=root)
    (pathlib.Path(result['path']) / 'stale_prediction.json').write_text('{"stale":true}')
    dest = tmp_path / 'restored'
    materialize_phase('E', 'FORMAL', dest, root=root)
    assert not (dest / 'stale_prediction.json').exists()
    assert (dest / 'final_receipt_envelope.json').exists()

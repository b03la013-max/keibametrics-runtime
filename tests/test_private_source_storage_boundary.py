"""Exercise the actual public persistence boundaries, including failure uploads."""
import ast
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from runtime import execution_store as store
from runtime import formal_execution_orchestrator as orchestrator

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = {"provider": "NANKAN_OFFICIAL", "artifact": {"raw_gzip_b64": "private-body"}}


@pytest.mark.parametrize("payload", [
    PRIVATE,
    {"provider": "NANKAN_OFFICIAL", "artifact": {"runners": [{"horse_no": 1}]}},
    {"source_authority": "NAR_OFFICIAL", "source_url": "https://www.nankankeiba.com/syousai/2026102118080310.do",
     "raw_gzip_b64": "private-body"},
    {"error": json.dumps(PRIVATE)},
    {"public_redistribution_authorized": True, **PRIVATE},
    {"public_redistribution_authorized": False, "answer_required_parts": ["private-answer"]},
    {"reference": {"public_redistribution_authorized": False, "message": "private-answer"}},
    {"license_document_text": "private-agreement"},
    {"licence_document_text": "private-agreement"},
    {"licence_evidence": {"text": "private-agreement"}},
    {"license_evidence": "private-agreement"},
    {"licence_evidence": "private-agreement"},
])
def test_private_content_cannot_be_published(payload):
    with pytest.raises(store.ExecutionStoreError, match="PRIVATE_.*PUBLIC_STORAGE_FORBIDDEN"):
        store.require_public_storage(payload)


def test_metadata_and_existing_nar_source_remain_usable():
    for payload in (
        {"provider": "NANKAN_OFFICIAL", "raw_sha256": "a" * 64, "status": "EVIDENCE_NOT_CONNECTED"},
        {"license_evidence": {"sha256": "b" * 64, "ref": "private-evidence-reference"}},
        {"provider": "NAR_OFFICIAL", "artifact": {"raw_gzip_b64": "existing-nar-source"}},
        json.loads((ROOT / 'profiles/local_information_source_registry_v1.10_20260924.json').read_text()),
    ):
        store.require_public_storage(payload)


def test_persist_checks_entire_batch_before_creating_store(tmp_path):
    incoming = tmp_path / "incoming"
    incoming.mkdir()
    (incoming / "a-public.json").write_text('{"status":"PASS"}')
    (incoming / "z-private.json").write_text(json.dumps(PRIVATE))
    target = tmp_path / "store"
    with pytest.raises(store.ExecutionStoreError, match="PRIVATE_SOURCE"):
        store.persist_phase("E", "SOURCE", "1", incoming, root=target)
    assert not target.exists()


def test_materialize_refuses_old_private_checkpoint_before_copy(tmp_path):
    incoming = tmp_path / "incoming"
    incoming.mkdir()
    artifact = incoming / "source.json"
    artifact.write_text('{"status":"PASS"}')
    root = tmp_path / "store"
    saved = store.persist_phase("E", "SOURCE", "1", incoming, root=root)
    run = Path(saved['path'])
    # Model a legacy checkpoint whose byte inventory is consistent but whose
    # content must no longer be materialized into a public output directory.
    raw = json.dumps(PRIVATE).encode()
    (run / artifact.name).write_bytes(raw)
    manifest = json.loads((run / 'manifest.json').read_text())
    manifest['files'][artifact.name] = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
    (run / 'manifest.json').write_text(json.dumps(manifest))
    pointer = run.parents[1] / 'LATEST.json'
    latest = json.loads(pointer.read_text())
    latest['manifest_sha256'] = hashlib.sha256((run / 'manifest.json').read_bytes()).hexdigest()
    pointer.write_text(json.dumps(latest))
    destination = tmp_path / 'materialized'
    with pytest.raises(store.ExecutionStoreError, match="PRIVATE_SOURCE"):
        store.materialize_phase('E', 'SOURCE', destination, root=root)
    assert not destination.exists()


def test_orchestrator_does_not_truncate_or_delete_before_rejection(tmp_path):
    target = tmp_path / 'report.json'
    target.write_text('original')
    with pytest.raises(ValueError, match="PRIVATE_SOURCE"):
        orchestrator._write(target, PRIVATE)
    assert target.read_text() == 'original'
    incoming = tmp_path / 'incoming'
    incoming.mkdir()
    (incoming / 'a.json').write_text('{"status":"PASS"}')
    (incoming / 'z.json').write_text(json.dumps(PRIVATE))
    destination = tmp_path / 'old-output'
    destination.mkdir()
    (destination / 'keep.json').write_text('original')
    with pytest.raises(ValueError, match="PRIVATE_SOURCE"):
        orchestrator._copy_json_dir(incoming, destination)
    assert [(p.name, p.read_text()) for p in destination.iterdir()] == [('keep.json', 'original')]


def test_legacy_runner_persist_rejects_before_open(tmp_path):
    # Loading this legacy script would execute a live workflow. Extract only
    # its real persistence function, without running the entrypoint.
    tree = ast.parse((ROOT / 'runtime/non_jra_formal_runner.py').read_text())
    persist = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'persist')
    namespace = {'json': json, 'os': __import__('os')}
    exec(compile(ast.Module(body=[persist], type_ignores=[]), '<actual-runner-persist>', 'exec'), namespace)
    target = tmp_path / 'output.json'
    with pytest.raises(ValueError, match="PRIVATE_SOURCE"):
        namespace['persist'](str(target), PRIVATE)
    assert not target.exists()


def test_artifact_gate_rejects_unreviewed_raw_and_symlinks(tmp_path):
    (tmp_path / 'raw.html').write_text('private-body')
    with pytest.raises(store.ExecutionStoreError, match="UNREVIEWED_FILE"):
        store.require_public_artifact_paths([tmp_path])
    # The JSON-only option is reserved for workflows whose upload path is
    # explicitly restricted to JSON, never the entire directory.
    (tmp_path / 'report.json').write_text(json.dumps(PRIVATE))
    with pytest.raises(store.ExecutionStoreError, match="PRIVATE_SOURCE"):
        store.require_public_artifact_paths([tmp_path], json_only=True)
    (tmp_path / 'link.json').symlink_to(tmp_path / 'report.json')
    with pytest.raises(store.ExecutionStoreError, match="SYMLINK"):
        store.require_public_artifact_paths([tmp_path], json_only=True)


@pytest.mark.parametrize('name', [
    'km-formal-single-entry.yml', 'km-family-non-jra-formal-runner.yml',
    'km-local-source-first-entry.yml', 'km-local-result-from-signed-final.yml',
])
def test_always_upload_requires_successful_public_gate_and_json_paths(name):
    workflow = yaml.safe_load((ROOT / '.github/workflows' / name).read_text())
    checked_uploads = 0
    for job in workflow['jobs'].values():
        steps = job['steps']
        for index, step in enumerate(steps):
            if not str(step.get('uses', '')).startswith('actions/upload-artifact@'):
                continue
            gates = [s for s in steps[:index] if s.get('id') == 'public_storage']
            assert len(gates) == 1
            assert gates[0]['if'] == 'always()'
            assert 'assert-public' in gates[0]['run']
            assert "steps.public_storage.outcome == 'success'" in step['if']
            assert all(path.endswith('.json') for path in step['with']['path'].splitlines())
            checked_uploads += 1
    assert checked_uploads


@pytest.mark.parametrize('private_output', [False, True])
def test_chat_body_stays_private_while_public_output_gets_hold(tmp_path, monkeypatch, private_output):
    from runtime import local_race_entry as entry
    if not private_output:
        (tmp_path / '.git').mkdir()
    output = tmp_path / 'entry-out'
    monkeypatch.setattr(entry, '_chat_final', lambda intent: (None, []))
    monkeypatch.setattr(entry, 'chat_formal_status', lambda intent: {
        'status': 'BLOCKED', 'first_failed_stage': 'SOURCE', 'code': 'NOT_ADMITTED'})
    monkeypatch.setattr(entry, '_chat_reference', lambda *args, **kwargs: ({
        'execution_id': 'PRIVATE-REFERENCE', 'public_redistribution_authorized': False,
        'answer_required_parts': ['secret-original-tickets'], 'reference_readback_only': True,
    }, 'secret-original-tickets'))
    report = entry.run_chat({'family_id': 'LOCAL', 'venue_id': 'URW', 'race_date': '2026-10-21', 'race_no': 10},
                            output=output, run_id='readback')
    for path in output.iterdir():
        assert ('secret-original-tickets' in path.read_text()) == private_output
        if private_output:
            assert path.stat().st_mode & 0o777 == 0o600
    assert report['formal_final_proven'] is False
    assert report['delivery']['user_acknowledgement_verified'] is False
    if not private_output:
        assert report['status'] == 'PRIVATE_REFERENCE_STORAGE_HOLD'
    else:
        again = entry.run_chat({'family_id': 'LOCAL', 'venue_id': 'URW',
            'race_date': '2026-10-21', 'race_no': 10}, output=output, run_id='readback-again')
        assert json.loads((output/'chat_entry_report.json').read_text()) == again
        assert 'secret-original-tickets' in (output/'chat_response.md').read_text()
        assert not list(output.glob('.chat-delivery-*'))

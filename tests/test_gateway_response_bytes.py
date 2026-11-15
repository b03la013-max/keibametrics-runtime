"""Private local transport tests; real observed FAIL is never called live success."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import pytest

MODULE = Path(__file__).resolve().parents[1] / 'runtime/local_fnb_gateway_response_bytes.py'
spec = importlib.util.spec_from_file_location('gateway_response_bytes', MODULE)
gateway = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gateway)


@pytest.fixture
def real_evidence():
    name = os.environ.get('KM_TEST_ACTUAL_FNB_ATTEMPT_ROOT')
    if not name:
        pytest.skip('Explicit private actual-evidence directory required')
    base = Path(name)
    return base, base / 'daily_autonomy_work/evidence/family_audit_20261016/runtime_health.json'


def call(raw, name, tmp_path, trust, kind='DOM_TEXT_RECONSTRUCTION',
         expected_race_id='KM-LOCAL-FNB-20261103-R07-LIVE-R1'):
    return gateway.save_response_bytes(raw, private_root=tmp_path, name=name,
        metadata={'capture_kind': kind, 'actor': 'PRIVATE_LOCAL_TEST_NO_NETWORK'},
        trust_path=trust, trust_sha256=hashlib.sha256(trust.read_bytes()).hexdigest(),
        expected_race_id=expected_race_id)


def test_actual_swagger_integer_float_loss_is_rejected_and_exact_bytes_retained(real_evidence, tmp_path):
    base, trust = real_evidence
    raw = (base / 'current_source_attempts/R07_GATEWAY_SOURCE_ENVELOPE_FAIL.json').read_bytes()
    with pytest.raises(ValueError, match='GATEWAY_RESPONSE_ARTIFACT_SHA_MISMATCH'):
        call(raw, 'rejected_swagger.json', tmp_path, trust)
    assert (tmp_path / 'rejected_swagger.json').read_bytes() == raw
    capture = json.loads((tmp_path / 'rejected_swagger.json.capture.json').read_bytes())
    assert capture['capture_kind'] == 'DOM_TEXT_RECONSTRUCTION'
    assert capture['source_admitted'] is False
    assert capture['original_http_transport_proven_here'] is False
    forensic = json.loads((base / 'current_source_attempts/R07_ARTIFACT_SHA_TRANSFER_FORENSICS.json').read_bytes())
    assert forensic['changed_field_count'] == 18
    assert forensic['diagnostic_full_artifact_sha_matches_signed_original_pin'] is True
    assert forensic['corrected_SOURCE_or_envelope_written'] is False


def test_actual_verified_failure_keeps_failure_and_dom_provenance(real_evidence, tmp_path):
    base, trust = real_evidence
    raw = (base / 'current_source_attempts/NANKAN_R07_PRIVATE_CAPTURE_ENVELOPE_FAIL.json').read_bytes()
    result = call(raw, 'signed_failure.json', tmp_path, trust,
                  expected_race_id='KM-LOCAL-FNB-20261103-R07-PRIVATE-CAPTURE-R1')
    assert result['receipt_status'] == 'FAIL'
    assert result['receipt_errors']
    assert result['source_admitted'] is False
    assert result['original_http_body_attested_by_caller'] is False
    assert result['original_http_transport_proven_here'] is False
    assert Path(result['path']).read_bytes() == raw
    assert result['sha256'] == hashlib.sha256(raw).hexdigest()
    assert call(raw, 'signed_failure.json', tmp_path, trust,
                expected_race_id='KM-LOCAL-FNB-20261103-R07-PRIVATE-CAPTURE-R1') == result


def test_synthetic_byte_preservation_and_reserialization_conflict(tmp_path):
    # Synthetic bytes test transport storage only: no signature or live claim.
    raw = b'{"test_synthetic":true,"zero":0.0,"weight":57.0,"other":1}\n'
    saved = gateway._preserve(tmp_path, 'synthetic.bytes', raw)
    assert Path(saved['path']).read_bytes() == raw
    parsed = json.loads(raw)
    assert type(parsed['zero']) is float and type(parsed['weight']) is float
    normalized = b'{"test_synthetic":true,"zero":0,"weight":57,"other":1}\n'
    with pytest.raises(ValueError, match='IMMUTABLE_BYTES_CONFLICT'):
        gateway._preserve(tmp_path, 'synthetic.bytes', normalized)
    assert Path(saved['path']).read_bytes() == raw


def test_private_storage_forbids_git_and_symlink(tmp_path):
    repo = tmp_path / 'repo'
    (repo / '.git').mkdir(parents=True)
    with pytest.raises(ValueError, match='PRIVATE_STORE_REQUIRED'):
        gateway._preserve(repo, 'raw.bytes', b'test synthetic')
    link = tmp_path / 'linked'
    link.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(ValueError, match='PRIVATE_STORE_REQUIRED'):
        gateway._preserve(link, 'raw.bytes', b'test synthetic')


def load_cli():
    path = MODULE.parent.parent / 'scripts/capture_gateway_response.py'
    spec = importlib.util.spec_from_file_location('gateway_bytes_cli', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cli_inputs(tmp_path, trust, race_id):
    config = tmp_path / 'test_synthetic_config.json'
    config.write_text(json.dumps({'families': {'LOCAL': {'external_endpoint': 'https://gateway.invalid'}}}))
    request = tmp_path / 'test_identity_request.json'
    request.write_text(json.dumps({'race_id': race_id}))
    flags = []
    for option, path in [('gateway-config', config), ('request', request), ('trust', trust)]:
        flags += ['--' + option, str(path), '--' + option + '-sha256', hashlib.sha256(path.read_bytes()).hexdigest()]
    return flags + ['--private-root', str(tmp_path / 'private'), '--name', 'response.json']


def test_cli_dns_failure_is_explicit_without_network_or_synthetic_success(tmp_path, monkeypatch, capsys):
    cli = load_cli()
    trust = tmp_path / 'test_synthetic_unused_trust.json'
    trust.write_text('{}')
    class MockOpener:
        def open(self, request, timeout):
            raise cli.urllib.error.URLError(cli.socket.gaierror(-2, 'synthetic DNS test'))
    monkeypatch.setattr(cli.urllib.request, 'build_opener', lambda *args: MockOpener())
    monkeypatch.setattr(cli.sys, 'argv', ['capture'] + cli_inputs(tmp_path, trust, 'TEST-SYNTHETIC-NO-LIVE-RACE'))
    assert cli.main() == 2
    result = json.loads(capsys.readouterr().out)
    assert result['reason'] == 'GATEWAY_CLIENT_DNS_RESOLUTION_FAILED'
    assert result['source_admitted'] is False
    assert not (tmp_path / 'private/response.json').exists()


def test_cli_save_bytes_keeps_explicit_dom_provenance_and_actual_failure(real_evidence, tmp_path, monkeypatch, capsys):
    cli = load_cli()
    base, trust = real_evidence
    original = base / 'current_source_attempts/NANKAN_R07_PRIVATE_CAPTURE_ENVELOPE_FAIL.json'
    metadata = tmp_path / 'capture.json'
    metadata.write_text(json.dumps({'capture_kind': 'DOM_TEXT_RECONSTRUCTION', 'actor': 'PRIVATE_OFFLINE_TEST'}))
    flags = cli_inputs(tmp_path, trust, 'KM-LOCAL-FNB-20261103-R07-PRIVATE-CAPTURE-R1')
    for option, path in [('response-bytes', original), ('capture-metadata', metadata)]:
        flags += ['--' + option, str(path), '--' + option + '-sha256', hashlib.sha256(path.read_bytes()).hexdigest()]
    monkeypatch.setattr(cli.sys, 'argv', ['capture'] + flags)
    assert cli.main() == 2  # Signed FAIL remains failure, never SOURCE admission.
    result = json.loads(capsys.readouterr().out)
    assert result['receipt_status'] == 'FAIL'
    assert result['capture_metadata']['capture_kind'] == 'DOM_TEXT_RECONSTRUCTION'
    assert result['original_http_body_attested_by_caller'] is False
    assert Path(result['path']).read_bytes() == original.read_bytes()

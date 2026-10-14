"""Execute the existing canary status serializer without GitHub/network writes."""
import json
from pathlib import Path
import textwrap

import pytest

from runtime import family_authority_guard

WORKFLOW = Path(__file__).resolve().parents[1] / '.github/workflows/km-local-execution-canary.yml'


@pytest.mark.parametrize('ready', [True, False, None, 'absent_local', 'absent_boundary'])
@pytest.mark.parametrize('assessment', ['PASS', 'FAIL', None])
def test_canary_reports_current_numerical_authority_not_full_prediction(tmp_path, monkeypatch, ready, assessment):
    profile = tmp_path / 'profiles'
    profile.mkdir()
    (tmp_path / 'runtime_out').mkdir()
    (tmp_path / 'runtime').mkdir()
    local = {'numerical_consumption_boundary': {'prediction_authority': False, 'krs_input_authority': False}}
    if ready is not None:
        local['numerical_authority_status'] = 'READY / RULES BOUND' if ready else 'NOT_READY / RULES UNBOUND'
    if ready == 'absent_boundary':
        local.pop('numerical_consumption_boundary')
    if ready == 'absent_local':
        local = {}
    current = {'manifest_id': 'CURRENT-TEST', 'status': 'ACTIVE / CURRENT-AUTHORITY', 'effective_at': '2020-01-01T00:00:00Z', 'family_scoped_authority': {'LOCAL': local}}
    future = dict(current, manifest_id='FUTURE-TEST', effective_at='2099-01-01T00:00:00Z')
    for name, item in [('current', current), ('future', future)]:
        (profile / ('KM_FAMILY_CURRENT_AUTHORITY_' + name + '.json')).write_text(json.dumps(item))
    (profile / 'current_execution_gateway.json').write_text(json.dumps({'profile_id': 'GW', 'policy': {'production_numerical_authority_ready': True}}))
    (tmp_path / 'runtime_out/execution_gateway_canary.json').write_text(json.dumps({'assessment': {'status': assessment}, 'health': {}}))
    original = family_authority_guard.resolve_current_authority
    monkeypatch.setattr(family_authority_guard, 'resolve_current_authority', lambda: original(root=tmp_path))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('RUN_ID', 'test')
    monkeypatch.setenv('GITHUB_SHA_VALUE', 'frozen-test')
    script = WORKFLOW.read_text().split('name: Persist latest successful canary status to canonical repo', 1)[1].split("python - <<'PY'\n", 1)[1].split('\n          PY', 1)[0]
    if assessment != 'PASS':
        with pytest.raises(ValueError, match='CANARY_ASSESSMENT_NOT_PASS'):
            exec(compile(textwrap.dedent(script), str(WORKFLOW), 'exec'), {})
        assert not (tmp_path / 'runtime/execution_gateway_canary_status.json').exists()
        return
    exec(compile(textwrap.dedent(script), str(WORKFLOW), 'exec'), {})
    status = json.loads((tmp_path / 'runtime/execution_gateway_canary_status.json').read_text())
    assert status['current_authority_manifest'] == 'CURRENT-TEST'
    assert status['production_numerical_authority'] == local.get('numerical_authority_status', 'UNKNOWN')
    assert status['numerical_consumption_boundary'] == local.get('numerical_consumption_boundary', {})
    assert status['strict_formal_full_numerical_readiness'] == 'NO'
    assert status['strict_formal_readiness_basis'] == 'NOT_PROVEN_BY_RUNTIME_HEALTH'


def test_canary_regression_is_wired_and_pr_cannot_persist_main():
    workflow = WORKFLOW.read_text()
    assert 'tests/test_execution_gateway_canary_status.py' in workflow
    persist = workflow.split('name: Persist latest successful canary status to canonical repo', 1)[1]
    assert "if: github.event_name != 'pull_request'" in persist


@pytest.mark.parametrize("future_only", [True, False])
def test_existing_resolver_does_not_invent_missing_current_authority(tmp_path, future_only):
    (tmp_path / "profiles").mkdir()
    if future_only:
        (tmp_path / "profiles/KM_FAMILY_CURRENT_AUTHORITY_future.json").write_text(json.dumps({"manifest_id": "FUTURE", "status": "CURRENT-AUTHORITY", "effective_at": "2099-01-01T00:00:00Z"}))
    with pytest.raises(family_authority_guard.FamilyAuthorityError, match="CURRENT_AUTHORITY_RESOLUTION_EMPTY"):
        family_authority_guard.resolve_current_authority(root=tmp_path)

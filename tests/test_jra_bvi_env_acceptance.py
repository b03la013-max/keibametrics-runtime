"""Read-only real SOURCE target projection; not OIDC or Forward OOS evidence."""
import json
from pathlib import Path
import pytest
from scripts.jra_bvi_env_acceptance import target_environment

ROOT = Path(__file__).resolve().parents[1]


def real_target():
    request = json.loads(sorted((ROOT / 'runtime/requests').glob('*KYO-20261011-R07*FORMAL.json'))[-1].read_text())
    source = json.loads(next((ROOT / 'runtime/executions' / request['source_execution_id'] / 'SOURCE').rglob('source_receipt_envelope.json')).read_text())['artifact']
    return request, source


def test_actual_environment_is_exact_target_source_not_venue_inference():
    request, source = real_target()
    env = target_environment(source, request, diagnostic_cutoff='2026-10-24T14:30:00+00:00')
    assert env['going'] == '良' and env['inner_outer'] == '外'
    assert env['weather'] == '晴'
    assert env['field_size'] == len(request['runners'])
    assert env['cushion_value'] is None and env['moisture_pct'] is None
    assert env['original_prediction_cutoff'] != env['prediction_cutoff']
    assert env['source_snapshot_sha256'] == request['source_snapshot_sha256']


def test_conflicting_target_going_is_not_silently_resolved():
    request, source = real_target()
    source['jra_official_race_card_detail']['race_environment']['going'] = '不良'
    with pytest.raises(ValueError, match='TARGET_GOING_CONFLICT'):
        target_environment(source, request, diagnostic_cutoff='2026-10-24T14:30:00+00:00')

"""Synthetic transport/semantic tests; never real SOURCE or LIVE claims."""
from copy import deepcopy
import importlib.util
from pathlib import Path

import pytest

from runtime import local_fnb_csv_research_runtime as runtime
from runtime.local_fnb_csv_source_admission import assess
from runtime.local_fnb_context_static_candidate import build_context, sha


def fixture():
    path = Path(__file__).with_name('test_local_fnb_csv_source_admission.py')
    spec = importlib.util.spec_from_file_location('_csv_runtime_synthetic', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    args, _, _ = module.inputs()
    return args, assess(**args)


def test_original_csv_observations_preserve_unknown_history_and_no_signature():
    args, assessment = fixture()
    packet = runtime.observation_packet(assessment['parsed_reference'],raw=args['raw'],
        generated_at=args['now'].isoformat(),source_snapshot_sha256='a'*64)
    assert packet['observation_transport_format'] == 'ORIGINAL_CSV_ZIP_NOT_HTML'
    assert packet['raw_to_normalized_tables_equal'] is True
    assert packet['source_receipt_sha256'] is None
    assert packet['prestart_generation'] is False
    assert all(row['historical_fnb_observations'] == [] for row in packet['runners'])
    context = build_context(packet,generated_at=args['now'].isoformat())
    assert all(row['status'] == 'UNKNOWN' for row in context['runners'])
    assert packet['sha256'] == sha({k:v for k,v in packet.items() if k!='sha256'})


def test_csv_observation_replay_rejects_changed_raw_and_changed_parsed_fields():
    args, assessment = fixture()
    parsed = assessment['parsed_reference']
    with pytest.raises(ValueError):
        runtime.observation_packet(parsed,raw=args['raw']+b'tamper',
            generated_at=args['now'].isoformat(),source_snapshot_sha256='a'*64)
    changed = deepcopy(parsed)
    changed['runners'][0]['horse_name'] = '変更した合成馬'
    with pytest.raises(ValueError,match='RAW_REPLAY_OR_OUTCOME_MISMATCH'):
        runtime.observation_packet(changed,raw=args['raw'],
            generated_at=args['now'].isoformat(),source_snapshot_sha256='a'*64)


def test_csv_observations_cannot_precede_actual_capture():
    args, assessment = fixture()
    with pytest.raises(ValueError,match='BEFORE_CAPTURE|CAPTURE_IN_FUTURE'):
        runtime.observation_packet(assessment['parsed_reference'],raw=args['raw'],
            generated_at='2026-11-03T03:18:00+00:00',source_snapshot_sha256='a'*64)


def test_admitted_source_freeze_remains_distinct_from_earlier_zip_capture():
    args, assessment = fixture()
    packet = runtime.observation_packet(assessment['parsed_reference'],raw=args['raw'],
        generated_at=args['now'].isoformat(),source_snapshot_sha256='a'*64,
        source_freeze_at=args['freeze_at'])
    assert packet['source_freeze_at'] == args['freeze_at']
    assert packet['source_freeze_at'] != assessment['parsed_reference']['capture']['captured_at']
    with pytest.raises(ValueError,match='BEFORE_CAPTURE'):
        runtime.observation_packet(assessment['parsed_reference'],raw=args['raw'],
            generated_at=args['now'].isoformat(),source_snapshot_sha256='a'*64,
            source_freeze_at='2026-11-03T03:22:00+00:00')


def test_candidate_bridge_aliases_change_no_scores_or_original_objects():
    original = {'race_id':'R','race_no':2,'race_date':'2026-11-03','race':{'distance_m':1200},
        'candidate_current_state':{'official_going':None},
        'candidate_environment':{'front_candidate_count':0},
        'runners':[{'canonical_components':{'HPI-L':{'value':52.0}}}]}
    out = runtime._bridge_aliases(original)
    assert out['runners'] == original['runners']
    assert out['numerical_current_state'] == original['candidate_current_state']
    assert out['numerical_environment'] == original['candidate_environment']
    assert out['race']['race_no'] == 2
    assert 'race_no' not in original['race']
    with pytest.raises(ValueError,match='RACE_CONFLICT'):
        runtime._bridge_aliases({**original,'race':{'race_no':8}})


def test_qualified_entry_does_not_erase_missing_profile_adoption():
    args, assessment = fixture()
    with pytest.raises(ValueError,match='PROFILE_NOT_ADOPTED'):
        runtime.run_qualified(assessment,args['request'],binding=None,source_receipt={},
            private_root='unused',engine='unused',params='unused',
            owner_decision_path='unused',owner_decision_sha256='a'*64)


def test_preliminary_field_identity_rejects_external_numerical_runner_injection():
    args, assessment = fixture()
    with pytest.raises(ValueError,match='PRELIMINARY_IDENTITY_MISMATCH'):
        runtime.run_preliminary({'race_id':args['request']['race_id'],'race_date':'2026-11-03',
            'runners':[{'runner_id':'99'}]},assessment['parsed_reference'],args['raw'],
            args['request'],private_root='unused',engine='unused',params='unused')

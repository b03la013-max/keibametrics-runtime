"""Synthetic transport/semantic tests; never real SOURCE or LIVE claims."""
from copy import deepcopy
import importlib.util
import json
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


def test_exact_signed_receipt_and_assessment_bytes_survive_private_save_and_inventory(tmp_path):
    assessment={'classification':'SYNTHETIC_NOT_SOURCE','source_candidate':{'raw_sha256':'a'*64}}
    receipt={'receipt':{'race_id':'SYNTHETIC'},'signature':'SYNTHETIC_NOT_A_SIGNATURE'}
    assessment_raw=b'{ "classification": "SYNTHETIC_NOT_SOURCE", "source_candidate": {"raw_sha256": "'+b'a'*64+b'"} }\n'
    receipt_raw=b'{\n  "signature": "SYNTHETIC_NOT_A_SIGNATURE", "receipt": {"race_id":"SYNTHETIC"}\n}\n'
    originals={'csv_source_assessment.json':runtime._source_original(assessment,assessment_raw,'CSV_ASSESSMENT'),
        'csv_source_receipt_envelope.json':runtime._source_original(receipt,receipt_raw,'SYNTHETIC_ONLY')}
    metadata=runtime._save_source_originals(tmp_path,originals)
    assert (tmp_path/'csv_source_assessment.json').read_bytes()==assessment_raw
    assert (tmp_path/'csv_source_receipt_envelope.json').read_bytes()==receipt_raw
    assert metadata['csv_source_receipt_envelope.json']['representation']=='EXACT_SUPPLIED_JSON_BYTES'
    inventory=[{'path':p.name,'sha256':runtime.common.digest(p.read_bytes())}
        for p in tmp_path.iterdir() if p.is_file()]
    manifest=tmp_path/'manifest.json'
    manifest.write_bytes(runtime.common.encoded({'private_artifacts':inventory}))
    runtime.common._verify_saved_manifest(manifest)
    (tmp_path/'csv_source_receipt_envelope.json').write_bytes(b'changed')
    with pytest.raises(ValueError,match='ORIGINAL_BYTES_CHANGED'):
        runtime.common._verify_saved_manifest(manifest)


def test_original_bytes_must_match_the_actual_mapping_used_by_source_verifier():
    with pytest.raises(ValueError,match='MAPPING_BYTES_MISMATCH'):
        runtime._source_original({'receipt':'actually-verified'},b'{"receipt":"other"}','SOURCE_RECEIPT')
    with pytest.raises(ValueError,match='JSON_INVALID'):
        runtime._source_original({},b'not-json','SOURCE_RECEIPT')


def test_mapping_only_input_is_serialized_without_claiming_original_transport_bytes():
    original=runtime._source_original({'signature':'synthetic'},None,'SOURCE_RECEIPT')
    assert json.loads(original['raw'])=={'signature':'synthetic'}
    assert original['provenance']['representation']=='CANONICAL_ENCODING_OF_SUPPLIED_MAPPING_NOT_TRANSPORT_BODY'
    assert original['provenance']['signature_or_source_qualification_issued_here'] is False


def test_qualified_source_save_cannot_omit_verified_receipt_original(tmp_path):
    with pytest.raises(ValueError,match='ORIGINALS_REQUIRED_OR_CHANGED'):
        runtime._save_source_originals(tmp_path,{'csv_source_assessment.json':runtime._source_original({},None,'CSV')})


def test_provider_reference_engine_pin_rejects_before_any_engine_call(tmp_path,monkeypatch):
    """Synthetic reference wiring only; no real SOURCE, Owner or Engine run."""
    from unittest.mock import Mock
    from test_local_fnb_provider_independence_r14 import fixture_card
    raw,capture,race=fixture_card()
    monkeypatch.setattr(runtime.common,'verify_private_owner_decision',lambda *a,**k:(
        {'classification':'SYNTHETIC_PRIVATE_REFERENCE_ONLY'},b'SYNTHETIC_OWNER_DECISION'))
    # These test placeholders are not installed trust or Engine files. The
    # real entry keeps the existing immutable Engine/map pin checks.
    monkeypatch.setattr(runtime.common,'_pinned',lambda *a,**k:None)
    engine=Mock(side_effect=AssertionError('MISMATCHED_PIN_MUST_STOP_BEFORE_ENGINE'))
    monkeypatch.setattr(runtime.common,'execute_krs',engine)
    with pytest.raises(ValueError,match='PINNED_ENGINE_INPUT_PROJECTION_MISMATCH_BEFORE_EXECUTION'):
        runtime.run_provider_reference(raw,capture=capture,race=race,
            private_root=tmp_path/'private',engine='SYNTHETIC_NOT_AN_ENGINE',params='SYNTHETIC_NOT_PARAMETERS',
            owner_decision_path='SYNTHETIC_NOT_AN_APPROVAL',owner_decision_sha256='a'*64,
            expected_engine_projection_sha256='0'*64)
    engine.assert_not_called()


@pytest.mark.parametrize('checks_before_expiry',[0,3])
def test_reference_publication_cutoff_rejects_initial_or_pre_engine_expiry(tmp_path,monkeypatch,
                                                                       checks_before_expiry):
    """Synthetic clock boundary; no future execution or Active acceptance."""
    from datetime import datetime,timedelta
    from unittest.mock import Mock
    from test_local_fnb_provider_independence_r14 import fixture_card
    raw,capture,race=fixture_card()
    cutoff=datetime.fromisoformat('2026-11-06T14:40:00+09:00')
    calls=[]
    def clock():
        calls.append(True)
        return cutoff-timedelta(seconds=1) if len(calls)<=checks_before_expiry else cutoff
    monkeypatch.setattr(runtime.common,'_actual_clock',clock)
    monkeypatch.setattr(runtime.common,'verify_private_owner_decision',lambda *a,**k:(
        {'classification':'SYNTHETIC_PRIVATE_REFERENCE_ONLY'},b'SYNTHETIC_OWNER_DECISION'))
    monkeypatch.setattr(runtime.common,'_pinned',lambda *a,**k:None)
    engine=Mock(side_effect=AssertionError('EXPIRED_REFERENCE_MUST_NOT_CALL_ENGINE'))
    monkeypatch.setattr(runtime.common,'execute_krs',engine)
    with pytest.raises(ValueError,match='PRIVATE_PRESTART_CUTOFF_EXPIRED_NOT_NO_BET'):
        runtime.run_provider_reference(raw,capture=capture,race=race,
            private_root=tmp_path/'private',engine='SYNTHETIC_NOT_AN_ENGINE',params='SYNTHETIC_NOT_PARAMETERS',
            owner_decision_path='SYNTHETIC_NOT_AN_APPROVAL',owner_decision_sha256='a'*64,
            require_reference_publication_cutoff=True)
    assert len(calls)==checks_before_expiry+1
    engine.assert_not_called()

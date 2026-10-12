import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime'))
from jra_newcomer_replay import build


def test_historical_replay_requires_mec_without_creating_live_final():
    seen={}
    def prepare(q, env, *, source_execution_id):
        seen.update(q)
        assert source_execution_id=='ORIGINAL'
        return {'production_full_numerical_ready':True}
    def compile(q, env, report, **kwargs):
        assert kwargs['frozen_at']=='2026-10-12T03:03:18+00:00'
        return dict(q,aki_information_gate={'action':'PAPER'})
    with patch('jra_newcomer_replay.load_current_authority',return_value={'manifest_id':'R51'}), \
         patch('jra_newcomer_replay.prepare_production_numerical',side_effect=prepare), \
         patch('jra_newcomer_replay.compile_production_auto_handoff',side_effect=compile), \
         patch('jra_newcomer_replay.build_formal_request',side_effect=lambda q,e,**k:q), \
         patch('jra_newcomer_replay.verify_formal_request_binding'):
        out=build({'execution_id':'ORIGINAL','temporal_mode':'FORMAL-PRE-RACE'},
                  {'artifact':{'source_freeze_at':'2026-10-12T03:03:18+00:00'}})
    assert seen['mec_profile']=='KM-FAMILY-MINIMUM-EFFICIENT-COVERAGE-20260921-R3'
    assert out['temporal_mode']=='POST-START-REPLAY'
    assert out['acceptance_only'] is True
    assert out['execution_id'].endswith('R51-R2')
    assert out['original_pre_race_execution_id']=='ORIGINAL'
    assert out['replay_computed_at']!='2026-10-12T03:03:18+00:00'

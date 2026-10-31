"""Zero-stake RESULT acceptance must bind the whole frozen runner universe."""
from copy import deepcopy
import pytest
from test_jra_no_bet_postresult_learning import build_input, run
from test_jra_production_no_bet_terminal import fixtures, PRE
from jra_production_no_bet_terminal import build_no_bet_terminal
from jra_no_bet_postresult_learning import build_no_bet_learning, JRANoBetLearningError, _hash


def rehash(result):
    result['sha256']=_hash({k:v for k,v in result.items() if k not in ('sha256','race_no','source_snapshot_sha256')})


def four_runner_input():
    request, report=fixtures()
    for rid in ('3','4'):
        report['runner_universe'].append(rid)
        report['partial_production_base_calculation']['runners'][rid]=deepcopy(report['partial_production_base_calculation']['runners']['2'])
    report['partial_production_base_calculation']['calculated_base_cells']=4
    report['partial_production_base_calculation']['blocked_base_cells']=48
    terminal=build_no_bet_terminal(request,report,source_receipt_verified=True,created_at=PRE)
    _,result=build_input()
    return terminal,result


def test_correctly_hashed_top3_only_is_not_complete_four_runner_result():
    terminal,result=four_runner_input()
    with pytest.raises(JRANoBetLearningError,match='UNIVERSE'):
        run(terminal,result)


def test_non_finisher_is_accounted_without_inventing_rank_or_pfs():
    terminal,result=four_runner_input()
    result['non_finishers']=[{'runner_id':'4','horse_no':4,'finish_status':'DID_NOT_FINISH'}]
    rehash(result);before=deepcopy((terminal,result));out=run(terminal,result)
    assert (terminal,result)==before
    assert out['official_finish_count']==3
    assert out['official_non_finisher_count']==1
    assert out['official_runner_universe_count']==4
    assert out['pfs'] is None and out['production_effect']=='NONE'


@pytest.mark.parametrize('row',[
    {'runner_id':'4','horse_no':4,'finish_status':'UNKNOWN'},
    {'runner_id':'4','horse_no':5,'finish_status':'DID_NOT_FINISH'},
    {'runner_id':'2','horse_no':2,'finish_status':'DID_NOT_FINISH'},
    {'runner_id':'5','horse_no':5,'finish_status':'CANCELLED'},
])
def test_unbound_or_conflicting_non_finisher_is_rejected(row):
    terminal,result=four_runner_input();result['non_finishers']=[row];rehash(result)
    with pytest.raises(JRANoBetLearningError):run(terminal,result)


def test_capture_between_decision_and_scheduled_post_is_not_postresult():
    terminal,result=build_input()
    with pytest.raises(JRANoBetLearningError,match='CHRONOLOGY'):
        build_no_bet_learning(terminal,result,race_no=5,acquired_at='2026-10-10T12:20:00+09:00',scheduled_post_at='2026-10-10T12:25:00+09:00',result_source_snapshot_sha256='a'*64,official_capture_verified=True)


def test_caller_and_result_cannot_jointly_select_another_race():
    terminal,result=build_input();result['race_no']=6
    with pytest.raises(JRANoBetLearningError,match='IDENTITY'):
        build_no_bet_learning(terminal,result,race_no=6,acquired_at='2026-10-10T13:00:00+09:00',result_source_snapshot_sha256='a'*64,official_capture_verified=True)


def test_dead_heat_is_preserved_with_complete_frozen_universe():
    terminal,result=four_runner_input()
    result['runners'].append({'runner_id':'4','horse_no':4,'finish':3})
    result['runner_count']=4;rehash(result);out=run(terminal,result)
    assert out['official_top3_orders']==[[2,3,1],[2,3,4]]
    assert out['official_top3_is_legacy_representative'] is True
    assert out['official_runner_universe_count']==4
    assert out['pfs'] is None

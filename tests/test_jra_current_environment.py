"""Actual Kyoto11 two-point pages, with no external fetch or prediction."""
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/jra_source_runtime')]
from jra_source_runtime.jra_current_environment import bind_latest_environment,FIELD
from jra_source_runtime.jra_observed_context import resolve_observed_context
from jra_source_runtime.source_acquisition import sha_obj


def original():
    q=json.loads((ROOT/'runtime/requests/KM-JRA-KYO-20261025-R11-LIVE-R1-FORMAL.json').read_text())
    return q['source_snapshot'],q['prediction_cutoff']


def test_latest_actual_official_going_reaches_all_new_context_consumers():
    source,cutoff=original();before=deepcopy(source)
    assert resolve_observed_context(source)['going']=='稍重'
    fresh=bind_latest_environment(deepcopy(source),cutoff)
    ctx=resolve_observed_context(fresh)
    assert ctx['going']=='良' and ctx['context_source_kind']=='OFFICIAL_REOBSERVATION'
    assert fresh['jra_current_environment_reconciliation']['changes']=={
        'going':{'previous':'稍重','current':'良'}}
    assert ctx['context_source_snapshot_sha256']=='61b1c72b05c3687d8f34ac599a005dcbdff9cb031233e85a02bb70ccbe819d0c'
    assert fresh['jra_official_race_card_detail']==source['jra_official_race_card_detail']
    assert fresh['sources']==source['sources'] and source==before
    # Existing feature and KRS entry points read the same context resolver.
    from jra_krs_input_builder_production import _source_context
    bound_request={'race_id':fresh['race_id'],'source_snapshot':fresh,
        'source_snapshot_sha256':sha_obj({k:v for k,v in fresh.items() if k!='source_snapshot_sha256'}),
        'prediction_cutoff':cutoff}
    assert _source_context(bound_request)[0]['going']=='良'
    assert resolve_observed_context(source)['going']=='稍重'  # old signed view unchanged


@pytest.mark.parametrize('case',['raw','post_cutoff','unofficial','ambiguous_snapshot',
    'active_name','active_id','series_hash','late_second','wrong_first','cutoff'])
def test_current_context_fails_before_mutation_on_bad_evidence(case):
    source,cutoff=original();value=deepcopy(source)
    snap=next(s for s in value['sources'] if s.get('source_id')=='JRA-OFFICIAL-RACE-CARD-DETAIL-REOBSERVATION')
    if case=='raw':snap['raw_sha256']='0'*64
    elif case=='post_cutoff':snap['cutoff_relation']='POST_CUTOFF'
    elif case=='unofficial':snap['official']=False
    elif case=='ambiguous_snapshot':value['sources'].append(deepcopy(snap))
    elif case=='active_name':value['jra_official_runner_universe']['runners'][0]['canonical_name']='別馬'
    elif case=='active_id':value['jra_official_runner_universe']['runners'][0]['runner_id']='99'
    elif case=='series_hash':value['aki_external_observations_sha256']='0'*64
    elif case=='late_second':
        value['aki_external_observations'][1]['observed_at']='2026-10-25T16:00:00+09:00'
        value['aki_external_observations_sha256']=sha_obj(value['aki_external_observations'])
    elif case=='wrong_first':
        value['aki_external_observations'][0]['going']='不良'
        value['aki_external_observations_sha256']=sha_obj(value['aki_external_observations'])
    elif case=='cutoff':cutoff='2026-10-25T13:00:00+09:00'
    before=deepcopy(value)
    with pytest.raises(ValueError):bind_latest_environment(value,cutoff)
    assert value==before


def test_marker_tampering_is_not_an_opt_in_to_rewrite_old_source():
    source,cutoff=original();fresh=bind_latest_environment(deepcopy(source),cutoff)
    fresh[FIELD]['observed_at']='2026-10-25T14:00:00+09:00'
    with pytest.raises(ValueError):resolve_observed_context(fresh)
    fresh[FIELD]['sha256']=sha_obj({k:v for k,v in fresh[FIELD].items() if k!='sha256'})
    with pytest.raises(ValueError):resolve_observed_context(fresh)


def test_absent_second_observation_stays_unknown_without_another_fetch():
    source,cutoff=original();source['aki_external_observation_status']['status']='UNAVAILABLE'
    before=deepcopy(source)
    assert bind_latest_environment(source,cutoff)==before
    assert FIELD not in source and resolve_observed_context(source)['going']=='稍重'


def test_same_going_for_the_other_eight_originals_is_not_changed():
    for no in (4,5,6,7,8,9,10,12):
        q=json.loads((ROOT/f'runtime/requests/KM-JRA-KYO-20261025-R{no:02d}-LIVE-R1-FORMAL.json').read_text())
        source=q['source_snapshot'];before=deepcopy(source)
        fresh=bind_latest_environment(deepcopy(source),q['prediction_cutoff'])
        assert resolve_observed_context(fresh)['going']==resolve_observed_context(source)['going']
        assert fresh['jra_current_environment_reconciliation']['changes']=={} and source==before

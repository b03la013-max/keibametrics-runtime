"""OHI connection and PR136 accounting regressions, never Live evidence."""
import copy
from datetime import datetime, timezone
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'runtime')]
from runtime.local_race_entry import resolve_chat_intent, run_chat
from runtime import local_race_entry as entry
from local_result_settlement import (
    LocalSettlementError, settle_frozen_tickets, settle_structured_research,
    STRUCTURED_RESEARCH_PROFILE,
)


def structured():
    # PR136's 1st-place tie fixture, deliberately not claimed official Raw.
    return {'finish_rank_groups': [{'rank': 1, 'runners': [1, 2]},
                                  {'rank': 3, 'runners': [3]}],
        'refund_runner_ids': [4, 5], 'refund_authority': 'TEST-ONLY-PR136-REVIEW',
        'winning_selections': {
            'EXACTA': [{'selection': [1, 2], 'payout_per_100': 500},
                      {'selection': [2, 1], 'payout_per_100': 600}],
            'TRIO': [{'selection': [1, 2, 3], 'payout_per_100': 300}],
            'TRIFECTA': [{'selection': [1, 2, 3], 'payout_per_100': 1000},
                        {'selection': [2, 1, 3], 'payout_per_100': 1200}]}}


def portfolio():
    return {'total_investment': 400, 'tickets': [
        {'bet_type': 'EXACTA', 'selection': [1, 2], 'stake': 100},
        {'bet_type': 'EXACTA', 'selection': [2, 1], 'stake': 100},
        {'bet_type': 'TRIO', 'selection': [3, 1, 2], 'stake': 100},
        {'bet_type': 'TRIFECTA', 'selection': [4, 5, 1], 'stake': 100}]}


def settle(t=None, o=None):
    return settle_structured_research(t or portfolio(), o or structured(),
        profile=STRUCTURED_RESEARCH_PROFILE, runner_ids=[1, 2, 3, 4, 5])


def test_structured_multiple_wins_and_one_refund_per_ticket_immutable():
    t, o = portfolio(), structured(); before = copy.deepcopy((t, o))
    s = settle(t, o)
    assert (t, o) == before
    assert (s['investment'], s['winning_return'], s['refund'], s['return']) == (400, 1400, 100, 1500)
    assert s['effective_stake'] == 300 and len(s['refunded_tickets']) == 1
    assert len(s['winning_tickets']) == 3
    assert s['production_authority'] is False and s['new_forward_oos_credit'] == 0


@pytest.mark.parametrize('change', [
    lambda t,o: t['tickets'][0].update(stake=100.9),
    lambda t,o: t['tickets'].append(copy.deepcopy(t['tickets'][0])),
    lambda t,o: t.update(total_investment=999),
    lambda t,o: o['winning_selections']['EXACTA'][0].update(payout_per_100=float('nan')),
    lambda t,o: o['winning_selections']['EXACTA'][0].update(payout_per_100=True),
    lambda t,o: o['winning_selections']['EXACTA'].pop(),
    lambda t,o: o.update(refund_authority=None),
    lambda t,o: o.update(refund_authority=True),
    lambda t,o: o['refund_runner_ids'].append(1),
    lambda t,o: o['finish_rank_groups'][1].update(rank=2),
    lambda t,o: o['refund_runner_ids'].pop(),
])
def test_structured_rejects_pr136_unsafe_edges_and_unknown_states(change):
    t,o=portfolio(),structured(); change(t,o)
    with pytest.raises(LocalSettlementError): settle(t,o)


@pytest.mark.parametrize('field', ['winning_selections', 'finish_rank_groups'])
def test_new_fields_do_not_silently_enter_old_flat_contract(field):
    o={'finish_order':[1,2,3], 'payouts':{'EXACTA':500,'TRIO':300}, field:structured()[field]}
    with pytest.raises(LocalSettlementError, match='NONFLAT'): settle_frozen_tickets(portfolio(),o)


def test_structured_requires_explicit_profile_and_all_runner_census():
    with pytest.raises(LocalSettlementError, match='PROFILE'):
        settle_structured_research(portfolio(),structured(),profile='LOCAL-FORMAL',runner_ids=[1,2,3,4,5])
    o=structured();o['refund_runner_ids']=[4];o['nonfinishers']=[{'runner_id':5,'status':'DNF'}]
    assert settle(o=o)['refund']==100
    o['nonfinishers'][0]['status']='UNKNOWN'
    with pytest.raises(LocalSettlementError,match='NONFINISHERS'):settle(o=o)
    for alias in ('finish_order','payouts','top3','dead_heat'):
        o=structured();o[alias]=[5,4,3] if alias!='payouts' else {'EXACTA':1}
        with pytest.raises(LocalSettlementError,match='ALIAS'):settle(o=o)


def test_ohi_normal_request_and_urw_keep_venue_identity():
    now=datetime(2026,10,25,16,tzinfo=timezone.utc)
    assert resolve_chat_intent('大井2Rのケイバメトリクス調査願います',now=now)['venue_id']=='OHI'
    assert resolve_chat_intent('浦和2Rのケイバメトリクス調査願います',now=now)['venue_id']=='URW'
    assert resolve_chat_intent('2026/10/07 大井2R',now=now)['race_date']=='2026-10-07'
    for q in ['大井2R 浦和', '大井2R 大井3R', '川崎2R', '明日の大井2R', '10月7日 大井2R', '10/7 大井2R']:
        with pytest.raises(ValueError):resolve_chat_intent(q,now=now)


def test_ohi_without_scope_never_calls_urw_source_or_dispatch(tmp_path,monkeypatch):
    monkeypatch.setattr(entry,'_chat_final',lambda i:(None,[]))
    monkeypatch.setattr(entry,'_chat_reference',lambda *a,**k:pytest.fail('URW reference leaked to OHI'))
    monkeypatch.setattr(entry,'chat_formal_status',lambda i:{'status':'BLOCKED',
        'blockers':[{'stage':'AUTHORIZATION','code':'VENUE_OWNER_NOT_AUTHORIZED'}]})
    report=run_chat({'family_id':'LOCAL','venue_id':'OHI','race_date':'2026-10-26','race_no':2},
                    output=tmp_path,run_id='test-not-live')
    assert report['completion'] is False and report['formal_final_proven'] is False
    assert 'NO-BETではありません' in report['message']
    assert report['reference']['status']=='NOT_APPLICABLE'


def test_ohi_dispatch_transport_does_not_grant_kaw_owner_scope(tmp_path):
    from runtime import local_race_day_dispatcher as dispatcher
    import json
    from runtime.family_authority_guard import resolve_current_authority
    from runtime.execution_gateway import family_config
    owner=json.loads((ROOT/'profiles/local_production_static_owner_20261014_v1.json').read_text())
    assert owner['venues']==['KAW']
    now=datetime(2026,10,25,16,tzinfo=timezone.utc)
    plan={'family_id':'LOCAL','venue_id':'OHI','race_date':'2026-10-26','plan_sha256':'TEST-NOT-A-PLAN'}
    approval={'family_id':'LOCAL','venue_id':'OHI','race_date':'2026-10-26',
        'current_authority_manifest':resolve_current_authority(now=now)[1]['manifest_id'],
        'destination':family_config('LOCAL')['external_endpoint'].rstrip('/'),
        'plan_sha256':plan['plan_sha256'],'enabled':True,'owner_approval_ref':'TEST',
        'scheduled_execution_authorized':True,'existing_runtime_usage_cost_authorized':True,
        'data_scope':'INTENT_SOURCE_STATIC_PRE_KRS_KRS_FINAL_RESULT_SETTLEMENT'}
    with pytest.raises(ValueError,match='OWNER_SCOPE_SCHEDULE_OR_COST_APPROVAL_REQUIRED'):
        dispatcher.authorization(approval,plan,ROOT,now)

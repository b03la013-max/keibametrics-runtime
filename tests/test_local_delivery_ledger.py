from datetime import datetime, timedelta, timezone

from runtime.local_autopilot import delivery_ledger as dl, formal_eval as fe

JST = timezone(timedelta(hours=9))


def _q(sent):
    return {'race_date': '2026-11-17', 'discovered_at': '2026-11-16T21:00:00+09:00', 'races': {'OHI_01': {
        'venue_name': '大井', 'race_no': 1, 'post_current': '2026-11-17T15:00:00+09:00', 'status': 'PRESTART_PUSH_VERIFIED',
        'source_fetched_at': '2026-11-17T14:30:00+09:00', 'delivered_rev': 'OHI_01.r2', 'delivery_attempts': 1,
        'editions': [{'edition': '直前版', 'rev': 'OHI_01.r2', 'frozen_at': '2026-11-17T14:30:01+09:00',
                      'delivery': {'COMMITTED': '2026-11-17T05:30:10Z', 'PUSH_VERIFIED': '2026-11-17T05:30:10Z',
                                   'USER_DELIVERY_SENT': sent, 'DELIVERY_READBACK_VERIFIED': True}}]}}}


def test_prestart_vs_late(tmp_path):
    now = datetime(2026, 11, 17, 16, 0, tzinfo=JST)
    ok = dl.build(_q('2026-11-17T05:31:00Z'), tmp_path, now)['summary']
    late = dl.build(_q('2026-11-17T06:01:00Z'), tmp_path, now)['summary']   # 15:01 JST, after the post
    assert ok['paper']['submitted_prestart'] == 1 and ok['posted_without_prestart_paper_delivery'] == []
    assert late['paper']['submitted'] == 1 and late['paper']['submitted_prestart'] == 0
    assert late['posted_without_prestart_paper_delivery'] == ['OHI_01']
    assert ok['paper']['user_reached_owner_confirmed'] == 0      # post + read-back is not proof of reading


def test_waiting_is_not_a_stop(tmp_path):
    q = _q('NOT_CONNECTED')
    early = dl.build(q, tmp_path, datetime(2026, 11, 17, 14, 40, tzinfo=JST))
    assert early['races'][0]['first_stop'] is None and early['races'][0]['waiting_for'] == 'DELIVERY_SUBMITTED'
    assert early['races'][0]['recovery']['retry_eligible'] is True
    after = dl.build(q, tmp_path, datetime(2026, 11, 17, 15, 5, tzinfo=JST))
    assert after['summary']['first_stops'] == {'OHI_01': 'DELIVERY_SUBMITTED'}


def test_formal_settle_ordered_and_refund():
    res = {'payouts': {'EXACTA': {'11-10': 740}, 'TRIO': {'5-10-11': 2110}}, 'non_starters': [3]}
    t = [{'bet_type': 'EXACTA', 'selection': [11, 10]}, {'bet_type': 'EXACTA', 'selection': [10, 11]},
         {'bet_type': 'TRIO', 'selection': [11, 5, 10]}, {'bet_type': 'TRIO', 'selection': [3, 5, 10]}]
    s = fe.settle(t, res)
    assert s['invest'] == 300 and s['payout'] == 2850 and len(s['hits']) == 2

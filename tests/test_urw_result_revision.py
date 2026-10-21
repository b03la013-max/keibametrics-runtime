"""Synthetic official-layout witnesses and strict refund settlement."""
import copy
import hashlib

import pytest

from runtime import urw_nankan_reference_source as n
from runtime.mec_r4_shadow import settle_ticket_list


def case(status='競走除外',note='返還:4号馬'):
    race={'provider':'NANKAN_OFFICIAL','venue_id':'URW','race_no':1,'race_date':'2026-10-19',
          'provider_race_id':'2026101918070101','distance':1400,'program_runner_count':4,
          'scheduled_post_at':'2026-10-19T12:20:00+09:00'}
    facts=[{'runner_id':str(i),'name':f'自作{i}'} for i in range(1,5)]
    rows=''.join(f'<tr><td>{i}</td><td>{i}</td><td>{i}</td><td>自作{i}</td></tr>' for i in range(1,4))
    rows+=f'<tr><td>-</td><td>4</td><td>4</td><td>自作4</td><td>{status}</td></tr>'
    payout=''.join(f'<tr><th>{bt}</th><td>{sel}</td><td>{pay}</td><td>1</td></tr>'
                   for bt,sel,pay in [('馬単','1-2','500'),('三連複','1-2-3','900'),('三連単','1-2-3','2,200')])
    raw=(f'<meta charset="utf-8"><p class="nk23_c-tab1__subtitle">1R 2026年10月19日 浦和競馬 ダ1,400m (3頭) 発走時刻12:20</p>'
         '<table><tr><th>着</th><th>枠</th><th>馬番</th><th>馬名</th></tr>'+rows+'</table>'
         '<table><tr><th></th><th>組番</th><th>金額</th><th>人気</th></tr>'+payout+
         f'<tr><th>備考</th><td colspan="3">{note}</td></tr></table>').encode()
    return race,facts,raw


def parse(race,facts,raw):
    receipt={'url':n.ORIGIN+'/result/'+race['provider_race_id']+'.do','http_status':200,
             'fetched_at':'2026-10-19T04:00:00+00:00','raw_sha256':hashlib.sha256(raw).hexdigest()}
    return n.parse_result(raw,race,facts,receipt,race_id='KM-LOCAL-URW-20261019-R01-TEST')


def test_complete_witness_preserves_explicit_refund_and_private_boundary():
    result=parse(*case())
    assert result['official_result']['refunded_runner_ids']==['4']
    assert result['private_storage_required']
    assert result['public_redistribution_authorized'] is False
    assert result['active_verified'] is False
    assert result['official_result']['payouts']['TRIFECTA']==2200


@pytest.mark.parametrize('change',['count','venue','provider','name','refund_note','missing_payout','numeric_cancel'])
def test_incomplete_or_contradictory_witness_holds(change):
    race,facts,raw=case()
    if change=='count':race['program_runner_count']=5
    if change=='venue':race['venue_id']='KAW'
    if change=='provider':race['provider']='NAR_OFFICIAL'
    if change=='name':facts[0]['name']='別馬'
    if change=='refund_note':raw=raw.replace('返還:4号馬'.encode(),'未知の返還'.encode())
    if change=='missing_payout':raw=raw.replace(b'<td>500</td>',b'<td>-</td>')
    if change=='numeric_cancel':raw=raw.replace('<td>自作1</td>'.encode(),'<td>自作1</td><td>出走取消</td>'.encode())
    with pytest.raises(n.NankanError):parse(race,facts,raw)


def test_dnf_does_not_infer_a_refund_and_nonfinish_unknown_holds():
    result=parse(*case(status='競走中止',note=''))
    assert result['official_result']['refunded_runner_ids']==[]
    with pytest.raises(n.NankanError):parse(*case(status='UNKNOWN',note=''))


def test_refund_is_separate_from_hit_and_missing_payout_is_never_zero():
    result=parse(*case())
    tickets=[{'bet_type':'EXACTA','selection':[1,2],'stake':100},
             {'bet_type':'EXACTA','selection':[1,4],'stake':100}]
    settled=settle_ticket_list(tickets,result,require_resolved_refunds=True)
    assert settled['return']==600 and settled['winnings']==500 and settled['refund']==100
    assert settled['by_bet_type']['EXACTA']['refunded_ticket_count']==1
    for payout in (None,0,-100,float('nan')):
        missing=copy.deepcopy(result);missing['official_result']['payouts']['EXACTA']=payout
        assert settle_ticket_list(tickets,missing,require_resolved_refunds=True)['return'] is None


def test_partial_refund_metadata_or_strict_missing_refund_is_hold():
    ts=[{'bet_type':'EXACTA','selection':[1,4],'stake':100}]
    for official in ({'top3':[1,2,3]}, {'top3':[1,2,3],'refunded_runner_ids':[4]},
                     {'top3':[1,2,3],'refund_status':'UNRESOLVED'}):
        out=settle_ticket_list(ts,{'official_result':official},require_resolved_refunds=True)
        assert out['status']=='HOLD_REFUND_UNRESOLVED' and out['return'] is None
    partial={'official_result':{'top3':[1,2,3],'refunded_runner_ids':[4]}}
    assert settle_ticket_list(ts,partial)['return'] is None

"""Authored synthetic provider pages; no original website HTML or live HTTP."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime,timedelta
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.error

import pytest
from runtime import urw_nankan_reference_source as n

DAY='2026-10-22';NOW=datetime.fromisoformat('2026-10-19T23:30:00+09:00')
DAY_ID='20261022180704'
CAL=('<meta charset="UTF-8"><a href="/program/'+DAY_ID+'.do">TEST_SYNTHETIC_ONLY 浦和</a>').encode()


def program():
    rows=''.join(f'<li class="nk23_c-block01__list__item"><span class="nk23_c-block01__label">{number}R</span>'
        f'<span>12:{20+(number-1)*30:02} 1300m 2頭</span><a class="nk23_c-block01__list__title" href="/syousai/{DAY_ID}{number:02}.do">自作C3</a></li>' for number in (1,2))
    return ('<meta charset="UTF-8"><p>2026年10月22日</p><h3 class="nk23_c-block01__info__title">浦和競馬</h3><ul>'+rows+'</ul>').encode()


def card(number=1,*,preview=True,cancelled=False):
    rows=[]
    for horse in (1,2):
        venue='浦和' if horse==1 else '船橋'
        rows.append(f'<tr><td class="umaban">{horse}</td><td class="pr-umaName-textRound"><p>父名を混ぜない</p><a href="/uma_info/{horse}.do"><span>テスト{horse}</span></a><p>母名を混ぜない</p></td>'
            '<td class="cs-g1"><a href="/kis_info/1.do">試験騎手</a><span class="nk23_u-text12">54.0</span></td>'
            f'<td class="cs-odds">{"取消" if horse==1 and cancelled else "-"}</td>'
            f'<td class="cs-z1"><p class="nk23_u-d-flex"><span>1着</span><span>{venue}26.9.20</span><span>良外ダ1300</span></p>'
            '<a class="race_name_len" href="/result/2026092018070101.do">自作C3</a><span class="popularity">10頭1番1人気</span><p class="position"><span>1</span><span>2</span><span>1</span></p></td></tr>')
    header=f'<p class="nk23_c-tab1__subtitle">{number}R 2026年10月22日 第7回 浦和競馬 第4日 ダ1,300m (2頭) 発走時刻12:{20+(number-1)*30:02}</p>'
    fake='<table id="tb-sample" class="tb-shousai hidden"><tbody><tr><td>トウキョウスター 2022年</td></tr></tbody></table>' if preview else ''
    return ('<meta charset="UTF-8">'+header+'<table class="nk23_c-table22__table tb-shousai nk24"><tbody>'+''.join(rows)+'</tbody></table>'+fake).encode()


def detailed_card():
    """Authored fact rows with provider-labelled fields, never original HTML."""
    raw=card().decode()
    raw=raw.replace('<p>父名を混ぜない</p>',
        '<p class="nk23_u-text12">自作父</p>')
    raw=raw.replace('<p>母名を混ぜない</p>',
        '<p class="nk23_u-text10">牝4 鹿毛</p><p class="nk23_u-text10">自作母</p><p class="nk23_u-text10">(自作母父)</p>')
    raw=raw.replace('54.0</span></td>',
        '▲51.0</span><a href="/cho_info/1.do">自作調教師</a></td><td class="cs-g2">481 ±0</td>')
    raw=raw.replace('<span class="popularity">10頭1番1人気</span>',
        '<p class="nk23_u-text10"><span class="popularity">10頭 1番 1人気</span> 試験騎手 54.0</p>'
        '<p class="nk23_u-text10">479kg 自作相手</p>'
        '<p class="nk23_u-text10">1:30.1 (1.6) 3F 39.8 (7)</p>')
    return raw.encode()


def parsed_detailed_card(raw=None):
    race=n.parse_program(program(),n.ORIGIN+'/program/'+DAY_ID+'.do',DAY)[0]
    return race,n.parse_card(raw or detailed_card(),race,n.ORIGIN+'/uma_shosai/'+DAY_ID+'01.do')


@pytest.mark.parametrize('printed,expected',[
    ('良外ダ1300','良'),('重外ダ1300','重'),('稍外ダ1300','稍重'),
    ('不外ダ1300','不良'),('稍重ダ1300','稍重'),('不良内ダ1300','不良'),
    ('稍芝1300','稍重'),('不明外ダ1300',None),('稍未確認ダ1300',None),
])
def test_provider_going_abbreviations_preserve_the_printed_witness(printed,expected):
    raw=detailed_card().decode().replace('良外ダ1300',printed).encode()
    _,rows=parsed_detailed_card(raw)
    assert all(r['starts'][0]['going']==expected for r in rows)
    assert all(r['starts'][0]['going_observed']==printed for r in rows)
    assert all(r['active_verified'] is False for r in rows)


@pytest.mark.parametrize('unnumbered', [False, True])
def test_current_card_explicit_scratch_reduces_current_numbered_universe(unnumbered):
    # A post-change 1-head program may still print two rows, one marked
    # 取 消 in place of the original horse number. This is an unsigned,
    # synthetic PARSER test, not Formal ACTIVE/Owner promotion.
    race=n.parse_program(program(),n.ORIGIN+'/program/'+DAY_ID+'.do',DAY)[0]
    race['program_runner_count']=1
    raw=card(cancelled=True).decode().replace('(2頭)','(1頭)')
    if unnumbered:
        raw=raw.replace('<td class="umaban">1</td>',
                        '<td class="umaban">取 消</td>',1)
    excluded=[]
    rows=n.parse_card(raw.encode(),race,n.ORIGIN+'/uma_shosai/'+DAY_ID+'01.do',
                      excluded_rows=excluded)
    assert [r['runner_id'] for r in rows]==['2']
    assert len(excluded)==1 and excluded[0]['name']=='テスト1'
    assert excluded[0]['status']=='CANCELLED' and excluded[0]['active_verified'] is False
    assert excluded[0]['provider_horse_id']=='1'
    assert excluded[0]['runner_id']==(None if unnumbered else '1')


@pytest.mark.parametrize('bad_marker', ['欠場','UNKNOWN',''])
def test_unknown_unnumbered_current_horse_cannot_be_silently_dropped(bad_marker):
    race=n.parse_program(program(),n.ORIGIN+'/program/'+DAY_ID+'.do',DAY)[0]
    race['program_runner_count']=1
    raw=card(cancelled=True).decode().replace('(2頭)','(1頭)').replace(
        '<td class="umaban">1</td>',f'<td class="umaban">{bad_marker}</td>',1)
    with pytest.raises(n.NankanError,match='NANKAN_HORSE_NUMBER_UNKNOWN'):
        n.parse_card(raw.encode(),race,n.ORIGIN+'/uma_shosai/'+DAY_ID+'01.do')


def test_unexplained_runner_number_gap_is_not_a_cancellation():
    race=n.parse_program(program(),n.ORIGIN+'/program/'+DAY_ID+'.do',DAY)[0]
    raw=card().replace(b'<td class="umaban">2</td>',b'<td class="umaban">3</td>')
    with pytest.raises(n.NankanError,match='UNEXPLAINED_RUNNER_NUMBER_GAP'):
        n.parse_card(raw,race,n.ORIGIN+'/uma_shosai/'+DAY_ID+'01.do')


def test_observed_urw_win_place_odds_and_fixed_change_links_use_same_client_scope():
    assert n.url_scope(n.ORIGIN+'/odds/202610201807020501.do')
    assert n.url_scope(n.ORIGIN+'/henko_info/00000000000000.do')
    for path in ('/odds/202610201907020501.do','/odds/202610201807020502.do',
                 '/odds/202610201807029901.do','/henko_info/20261020180702.do'):
        with pytest.raises(n.NankanError,match='URL_SCOPE_HOLD'):n.url_scope(n.ORIGIN+path)


def current_receipt(raw,url,*,fetched=None):
    return {'provider':n.PROVIDER,'url':url,'http_status':200,
        'fetched_at':fetched or DAY+'T12:10:00+09:00','raw_sha256':hashlib.sha256(raw).hexdigest()}


def current_odds_page(*,time='12:09',row2=True,unknown=False,cancelled=False):
    head=n.DOM(n.decode(card())).root.all('p','nk23_c-tab1__subtitle')[0].text()
    win='-' if unknown else '1.7';place='-' if unknown else '1.1-1.7'
    if cancelled:win=place='取消'
    rows=f'<tr><th>1</th><td>1</td><td>テスト1</td><td>{win}</td><td>{place}</td></tr>'
    if row2:rows+='<tr><td>2</td><td>テスト2</td><td>3.9</td><td>1.5-2.0</td></tr>'
    return (f'<meta charset="UTF-8"><p class="nk23_c-tab1__subtitle">{head}</p>'
        f'<span class="btn_now_time_break">{time} 現在</span>'
        '<table class="nk23_c-table04__table"><tr><th>枠番</th><th>馬番</th><th>馬名</th><th>単勝</th><th>複勝</th></tr>'
        +rows+'</table>').encode()


def current_changes_page():
    def change(rid,kind,details):
        return f'<div class="nk23_c-block01__list2__item"><p class="nk23_c-block01__tag">{kind}</p>'\
            f'<p><span class="nk23_c-block01__txt2">{rid}番</span><a href="/uma_info/{rid}.do">テスト{rid}</a></p>'\
            f'<p class="nk23_c-block01__text2">{details}</p></div>'
    changes=change(1,'出走取消','自作理由')+change(2,'騎手変更','<a href="/kis_info/3.do">旧騎手</a>→<a href="/kis_info/4.do">新騎手</a>')
    return ('<meta charset="UTF-8"><div>2026年10月22日<h3 class="nk23_c-block01__info__title">第7回 浦和競馬 第4日 の変更情報</h3></div>'
        f'<li id="01" class="nk23_c-block01__list__item"><span class="nk23_c-block01__label">1R</span>'
        f'<a href="/syousai/{DAY_ID}01.do">出走表</a>{changes}</li>'
        '<li id="02" class="nk23_c-block01__list__item"><span>別Raceの不正な文字列は対象外</span></li>').encode()


def statistics_card(*,rate='3.2%',wins='3',starts='93',labels='1200<br>1300<br>1400<br>1500<br>浦1400'):
    def counts(cls,percent,num,total):
        return f'<td class="{cls}"><span class="is-percent">{percent}</span>'\
            f'<span class="is-number">{num}</span><span class="is-total">{total}</span></td>'
    header='<thead><tr><th class="cs-ai1">騎手とコースの相性 (勝率)</th>'\
        '<th class="cs-ai2">騎手と調教師の相性 (勝率)</th>'\
        '<th class="cs-anl">種牡馬 分析 (勝率/連対率)</th>'\
        f'<th class="cs-anl">{labels}</th></tr></thead>'
    cells=counts('cs-ai1',rate,wins,starts)+counts('cs-ai2','10.0%','3','30')
    cells+='<td class="cs-anl mk-sire"><p class="is-grPercent__item">18.8% 11.8% 16.8% 14.5% 33.3%</p>'\
        '<p class="is-grPercent__item">29.2% 29.4% 28.3% 19.4% 33.3%</p></td>'
    raw=detailed_card().decode().replace('<tbody>',header+'<tbody>',1)
    return raw.replace('</tr>',cells+'</tr>').encode()


def test_current_odds_observes_complete_membership_and_preserves_unsigned_scope():
    race,facts=parsed_detailed_card();raw=current_odds_page();url=n.ORIGIN+'/odds/'+DAY_ID+'0101.do'
    result=n.parse_current_odds(raw,race,current_receipt(raw,url),facts)
    assert result['runner_count']==2 and result['betting_membership_observed_count']==2
    assert result['provider_display_at']==DAY+'T12:09:00+09:00'
    assert result['source_fetched_at']==DAY+'T12:10:00+09:00'
    assert result['observed_before_reference_cutoff'] is True and result['active_verified'] is False
    assert result['signed_source_claim'] is False and result['production_authority'] is False
    raw=current_odds_page(unknown=True)
    missing=n.parse_current_odds(raw,race,current_receipt(raw,url),facts)
    assert missing['betting_membership_observed_count']==1 and missing['runners'][0]['win_odds'] is None
    raw=current_odds_page(cancelled=True)
    scratched=n.parse_current_odds(raw,race,current_receipt(raw,url),facts)
    assert scratched['runners'][0]['status']=='CANCELLED' and scratched['active_verified'] is False
    late=n.parse_current_odds(raw,race,current_receipt(raw,url,fetched=DAY+'T12:30:00+09:00'),facts)
    assert late['observed_before_reference_cutoff'] is False


def test_one_digit_provider_clock_is_normalized_and_invalid_clock_is_held():
    race,facts=parsed_detailed_card();raw=current_odds_page(time='9:09');url=n.ORIGIN+'/odds/'+DAY_ID+'0101.do'
    result=n.parse_current_odds(raw,race,current_receipt(raw,url,fetched=DAY+'T09:10:00+09:00'),facts)
    assert result['provider_display_at']==DAY+'T09:09:00+09:00'
    raw=current_odds_page(time='24:09')
    with pytest.raises(n.NankanError,match='PROVIDER_TIME_INVALID'):
        n.parse_current_odds(raw,race,current_receipt(raw,url),facts)


@pytest.mark.parametrize('kind',['odds','changes','statistics'])
@pytest.mark.parametrize('damage',['provider','venue','date_identity','race_identity','empty','duplicate','count'])
def test_current_fact_parsers_require_consistent_urw_context_and_nonempty_unique_universe(kind,damage):
    race,facts=parsed_detailed_card()
    if damage=='provider':race['provider']='NAR_OFFICIAL'
    elif damage=='venue':race['venue_id']='KAW'
    elif damage=='date_identity':race['race_date']='2026-10-21'
    elif damage=='race_identity':race['provider_race_id']=DAY_ID+'02'
    elif damage=='empty':facts=[]
    elif damage=='duplicate':facts=[facts[0],facts[0]]
    elif damage=='count':facts=facts[:1]
    if kind=='odds':
        raw=current_odds_page();url=n.ORIGIN+'/odds/'+race['provider_race_id']+'01.do';parser=n.parse_current_odds
    elif kind=='changes':
        raw=current_changes_page();url=n.ORIGIN+'/henko_info/00000000000000.do';parser=n.parse_current_changes
    else:
        raw=statistics_card();url=n.ORIGIN+'/uma_shosai/'+race['provider_race_id']+'.do';parser=n.parse_provider_statistics
    with pytest.raises(n.NankanError):parser(raw,race,current_receipt(raw,url),facts)


def test_provider_statistics_preserve_labels_counts_and_unknown_definitions_without_index_conversion():
    raw=statistics_card();race,facts=parsed_detailed_card(raw);url=n.ORIGIN+'/uma_shosai/'+DAY_ID+'01.do'
    result=n.parse_provider_statistics(raw,race,current_receipt(raw,url),facts)
    assert result['runner_count']==2 and result['declared_facts_sha256']==n.sha(facts)
    assert result['raw_sha256']==hashlib.sha256(raw).hexdigest()
    row=result['runners'][0]
    assert (row['rider_course']['wins'],row['rider_course']['starts'],row['rider_course']['win_rate_percent'])==(3,93,3.2)
    assert row['rider_course']['count_rate_consistency']=='MATCHES_DISPLAY_PRECISION'
    assert row['rider_trainer']['provider_definition']=='騎手と調教師の相性 (勝率)'
    assert row['rider_trainer']['target_period'] is None
    assert row['sire_analysis']['sample_count'] is None
    assert row['sire_analysis']['conditions'][4]=={'provider_label':'浦1400',
        'win_rate_percent':33.3,'quinella_rate_percent':33.3,'win_rate_display':'33.3%','quinella_rate_display':'33.3%'}
    assert result['canonical_index_transform_applied'] is False and result['forecast_recalculation_performed'] is False
    assert result['signed_source_claim'] is False and result['production_authority'] is False
    assert n.parse_card(raw,race,url)==facts


def test_provider_missing_statistics_and_zero_denominators_remain_unknown():
    race,facts=parsed_detailed_card();raw=detailed_card();url=n.ORIGIN+'/uma_shosai/'+DAY_ID+'01.do'
    result=n.parse_provider_statistics(raw,race,current_receipt(raw,url),facts)
    assert result['runners'][0]['rider_course']['win_rate_percent'] is None
    assert result['runners'][0]['sire_analysis']['conditions']==[]
    raw=statistics_card(rate='0.0%',wins='0',starts='0');race,facts=parsed_detailed_card(raw)
    result=n.parse_provider_statistics(raw,race,current_receipt(raw,url),facts)
    assert result['runners'][0]['rider_course']['count_rate_consistency']=='UNDEFINED_ZERO_STARTS'


@pytest.mark.parametrize('damage',['rate_count','count_range','rate_range','sire_labels','sire_rate_order','facts','day','raw_hash'])
def test_provider_statistics_reject_inconsistent_counts_labels_identity_and_hash(damage):
    raw=statistics_card();race,facts=parsed_detailed_card(raw);url=n.ORIGIN+'/uma_shosai/'+DAY_ID+'01.do'
    if damage=='rate_count':raw=statistics_card(wins='4')
    elif damage=='count_range':raw=statistics_card(wins='94')
    elif damage=='rate_range':raw=statistics_card(rate='100.1%')
    elif damage=='sire_labels':raw=statistics_card(labels='1200<br>1300')
    elif damage=='sire_rate_order':raw=raw.replace(b'29.2%',b'10.0%')
    elif damage=='facts':facts[0]['name']='別馬'
    elif damage=='day':raw=raw.replace('2026年10月22日'.encode(),'2026年10月21日'.encode())
    meta=current_receipt(raw,url)
    if damage=='raw_hash':meta['raw_sha256']='0'*64
    with pytest.raises(n.NankanError):n.parse_provider_statistics(raw,race,meta,facts)


@pytest.mark.parametrize('damage',['day','race','name','missing','future_clock','raw_hash'])
def test_current_odds_rejects_wrong_identity_missing_universe_and_future_update(damage):
    race,facts=parsed_detailed_card();raw=current_odds_page();url=n.ORIGIN+'/odds/'+DAY_ID+'0101.do'
    if damage=='day':raw=raw.replace('2026年10月22日'.encode(),'2026年10月21日'.encode())
    elif damage=='race':url=n.ORIGIN+'/odds/'+DAY_ID+'0201.do'
    elif damage=='name':raw=raw.replace('テスト1'.encode(),'別馬'.encode())
    elif damage=='missing':raw=current_odds_page(row2=False)
    elif damage=='future_clock':raw=current_odds_page(time='12:11')
    meta=current_receipt(raw,url)
    if damage=='raw_hash':meta['raw_sha256']='0'*64
    with pytest.raises(n.NankanError):n.parse_current_odds(raw,race,meta,facts)


def test_change_items_are_bound_to_target_race_and_absence_never_confirms_active():
    race,facts=parsed_detailed_card();raw=current_changes_page();url=n.ORIGIN+'/henko_info/00000000000000.do'
    result=n.parse_current_changes(raw,race,current_receipt(raw,url),facts)
    assert len(result['items'])==2 and result['items'][0]['status']=='CANCELLED'
    assert result['items'][1]['change_type']=='騎手変更'
    assert result['items'][1]['jockey_names_observed']==['旧騎手','新騎手']
    assert result['active_verified'] is False and result['absence_is_no_change_authority'] is False
    absent=raw.replace(b'id="01"',b'id="03"')
    observed=n.parse_current_changes(absent,race,current_receipt(absent,url),facts)
    assert observed['items']==[] and observed['target_race_row_present'] is False


@pytest.mark.parametrize('damage',['day','venue','race_url','name'])
def test_change_item_identity_disagreement_is_held(damage):
    race,facts=parsed_detailed_card();raw=current_changes_page();url=n.ORIGIN+'/henko_info/00000000000000.do'
    if damage=='day':raw=raw.replace('2026年10月22日'.encode(),'2026年10月21日'.encode())
    elif damage=='venue':raw=raw.replace('浦和競馬'.encode(),'船橋競馬'.encode())
    elif damage=='race_url':raw=raw.replace((DAY_ID+'01.do').encode(),(DAY_ID+'02.do').encode())
    elif damage=='name':raw=raw.replace('テスト1'.encode(),'別馬'.encode())
    with pytest.raises(n.NankanError):n.parse_current_changes(raw,race,current_receipt(raw,url),facts)


def test_existing_snapshot_schema_adapter_stays_unsigned_and_not_admitted():
    from runtime.local_physical.source_acquisition import verify_source_artifact
    race,_=parsed_detailed_card();raw=detailed_card()
    meta={'provider':n.PROVIDER,'source_authority':n.PROVIDER,'http_status':200,
        'url':n.ORIGIN+'/uma_shosai/'+DAY_ID+'01.do','fetched_at':NOW.isoformat(),
        'raw_sha256':hashlib.sha256(raw).hexdigest(),
        'source_policy':{'usage_scope':'USER_PERSONAL_NONCOMMERCIAL_PRIVATE_ONLY_NOT_PUBLIC_REDISTRIBUTION'}}
    out=n.build_unsigned_source_snapshot(raw,race,meta,race_id='TEST-SYNTHETIC-UNSIGNED')
    assert out['schema']=='KM-SOURCE-SNAPSHOT-v1' and out['provider']==n.PROVIDER
    assert out['sources'][0]['authority']==n.PROVIDER
    assert out['sources'][0]['raw_sha256']==meta['raw_sha256']
    assert len(out['parsed_nankan_facts'])==2
    assert all(out[k] is False for k in ('formal_ready','active_verified','signed_source_claim','production_authority'))
    assert 'active_runner_universe' not in out and 'official_runner_universe' not in out
    assert verify_source_artifact(out)==(False,['SOURCE_NOT_FORMAL_READY'])
    bad=dict(meta,raw_sha256='0'*64)
    with pytest.raises(n.NankanError,match='RAW_HASH'):
        n.build_unsigned_source_snapshot(raw,race,bad,race_id='TEST-SYNTHETIC-UNSIGNED')
    bad=dict(meta,signed_source_claim=True)
    with pytest.raises(n.NankanError,match='AUTHORITY_HOLD'):
        n.build_unsigned_source_snapshot(raw,race,bad,race_id='TEST-SYNTHETIC-UNSIGNED')
    with pytest.raises(n.NankanError,match='PROVIDER_OR_VENUE'):
        n.build_unsigned_source_snapshot(raw,dict(race,venue_id='KAW'),meta,race_id='TEST-SYNTHETIC-UNSIGNED')
    other=dict(race,provider_race_id=DAY_ID+'02')
    with pytest.raises(n.NankanError,match='PROVIDER_RACE_IDENTITY'):
        n.build_unsigned_source_snapshot(raw,other,dict(meta,url=n.ORIGIN+'/uma_shosai/'+DAY_ID+'02.do'),
            race_id='TEST-SYNTHETIC-UNSIGNED')


def test_current_weight_apprentice_load_pedigree_and_history_are_observed_facts():
    _,rows=parsed_detailed_card()
    r=rows[0];past=r['starts'][0]
    assert r['current_body_weight']==481 and r['current_body_weight_change']==0
    assert r['current_load']==51.0 and r['current_jockey']=='試験騎手'
    assert (r['sire'],r['dam'],r['damsire'],r['age'])==('自作父','自作母','自作母父',4)
    assert r['trainer']=='自作調教師' and r['active_verified'] is False
    assert 'CURRENT_BODY_WEIGHT_UNKNOWN' not in r['missingness']
    assert past['content_time_text']=='1:30.1' and past['content_final3f']==39.8
    assert (past['ride_body_weight'],past['ride_carried_weight'],past['ride_jockey'],past['ride_popularity'])==(479,54.0,'試験騎手',1)
    assert past['margin']==0.0 and past['winning_margin']==1.6 and past['winner'] is None
    # The same displayed difference is a deficit only for a non-winner.
    _,losers=parsed_detailed_card(detailed_card().replace(b'<span>1',b'<span>3'))
    assert losers[0]['starts'][0]['margin']==1.6


def test_missing_or_malformed_optional_weight_is_not_taken_from_other_numbers():
    raw=detailed_card().replace(b'481 \xc2\xb10',b'UNKNOWN 999')
    _,rows=parsed_detailed_card(raw)
    assert rows[0]['current_body_weight'] is None and rows[0]['current_body_weight_change'] is None
    assert 'CURRENT_BODY_WEIGHT_UNKNOWN' in rows[0]['missingness']
    duplicate=detailed_card().replace(b'<td class="cs-g2">',b'<td class="cs-g2">999 +0</td><td class="cs-g2">')
    with pytest.raises(n.NankanError,match='BODY_WEIGHT_NOT_UNIQUE'):parsed_detailed_card(duplicate)


def test_parsed_fact_compiler_reuses_existing_arithmetic_without_formal_authority(monkeypatch):
    from runtime import local_nar_evidence_candidate as c
    from runtime.local_fullnumerical_candidate import materialize_candidate
    race,rows=parsed_detailed_card()
    for row in rows:
        row.update(race_card_source_id='TEST_SYNTHETIC_ONLY',race_card_snapshot_sha256='a'*64,race_card_fetched_at=NOW.isoformat())
    raw_field={r['runner_id']:r for r in rows}
    source={'provider':n.PROVIDER,'production_authority':False,'source_snapshot_sha256':'a'*64,'source_freeze_at':NOW.isoformat()}
    request={'race':{**race,'venue':'URW','class':'C3'},'runners':[{'runner_id':r['runner_id'],'name':r['name']} for r in rows]}
    compiled=c.compile_parsed_candidate_evidence(source,request,raw_field)
    past=compiled['runners'][0]['raw_candidate_evidence']['starts'][0]
    assert past['content_time_seconds']==90.1 and past['finish_score']==100.0 and past['class_score']==52.0
    assert compiled['candidate_evidence_compiler']['production_authority'] is False
    assert not compiled['runners'][0]['evidence_features']['good_weight_range']['missing']
    assert compiled['runners'][0]['evidence_features']['good_weight_range']['evidence_refs']==['TEST_SYNTHETIC_ONLY','a'*64]
    assert compiled['runners'][0]['evidence_features']['sire_fit']['missing']
    numerical=materialize_candidate(compiled)
    assert numerical['candidate_full_numerical_summary']['required_count']==58
    assert numerical['candidate_full_numerical_summary']['unresolved_count']==0
    assert numerical['candidate_full_numerical_summary']['production_authority'] is False
    # The established NAR wrapper uses exactly the same post-extraction path.
    monkeypatch.setattr(c,'parse_race_card',lambda _:deepcopy(raw_field))
    assert c.compile_candidate_evidence(source,request)==compiled


def test_urw_numerical_recency_is_date_ordered_and_never_uses_future_history():
    from runtime import local_nar_evidence_candidate as c
    from runtime.local_fullnumerical_candidate import materialize_candidate
    race,rows=parsed_detailed_card()
    for row in rows:
        row.update(race_card_source_id='TEST_SYNTHETIC_ONLY',race_card_snapshot_sha256='b'*64,race_card_fetched_at=NOW.isoformat())
        older=deepcopy(row['starts'][0]);older.update(date='26.08.20',finish=8,content_positions=[8,7,6])
        row['starts'].append(older)
    source={'provider':n.PROVIDER,'production_authority':False,'source_snapshot_sha256':'b'*64,'source_freeze_at':NOW.isoformat()}
    request={'race':{**race,'venue':'URW','class':'C3'},'runners':[{'runner_id':r['runner_id'],'name':r['name']} for r in rows]}
    raw={r['runner_id']:r for r in rows}
    original=deepcopy(raw)
    first=materialize_candidate(c.compile_parsed_candidate_evidence(source,request,raw))
    reverse=deepcopy(raw)
    for row in reverse.values():row['starts'].reverse()
    second=materialize_candidate(c.compile_parsed_candidate_evidence(source,request,reverse))
    assert first==second and raw==original
    future=deepcopy(raw);future['1']['starts'][0]['date']='26.10.20'
    with pytest.raises(c.LocalCandidateEvidenceError,match='AFTER_AVAILABLE_ASOF'):
        c.compile_parsed_candidate_evidence(source,request,future)
    for date_text in ('UNKNOWN','26.99.01'):
        unknown=deepcopy(raw);unknown['1']['starts'][0]['date']=date_text
        compiled=c.compile_parsed_candidate_evidence(source,request,unknown)
        facts=compiled['runners'][0]['raw_candidate_evidence']
        assert len(facts['undated_starts'])==1 and len(facts['starts'])==1


@pytest.mark.parametrize('damage',['request_duplicate','raw_identity_mismatch'])
def test_shared_fact_compiler_cannot_collapse_duplicate_or_conflicting_runner_ids(damage):
    from runtime import local_nar_evidence_candidate as c
    race,rows=parsed_detailed_card()
    request={'race':{**race,'venue':'URW'},'runners':[{'runner_id':r['runner_id'],'name':r['name']} for r in rows]}
    raw={r['runner_id']:r for r in rows}
    if damage=='request_duplicate':
        request['runners'].append(deepcopy(request['runners'][0]))
        message='REQUEST_RUNNER_ID_DUPLICATE'
    else:
        raw['1']['runner_id']='2'
        message='RAW_RUNNER_ID_MISMATCH'
    with pytest.raises(c.LocalCandidateEvidenceError,match=message):
        c.compile_parsed_candidate_evidence({'production_authority':False},request,raw)


class Clock:
    def __init__(self):self.tick=0.
    def __call__(self):return self.tick
    def sleep(self,seconds):self.tick+=seconds


class Response:
    status=200
    def __init__(self,url,raw,kind='text/html'):self.url=url;self.raw=raw;self.headers={'Content-Type':kind}
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def geturl(self):return self.url
    def read(self,count):return self.raw[:count]


class Opener:
    def __init__(self,clock,*,robots=404,location=None,second_redirect=False,fail_race=None,cancelled=False):
        self.clock=clock;self.calls=[];self.robots=robots;self.location=location
        self.second_redirect=second_redirect;self.fail_race=fail_race;self.cancelled=cancelled
    def open(self,request,timeout):
        url=request.full_url;self.calls.append((self.clock(),url,request.get_header('User-agent')))
        assert request.get_method()=='GET'
        if url==n.ROBOTS:
            if type(self.robots) is int:raise urllib.error.HTTPError(url,self.robots,'test',{},None)
            return Response(url,self.robots,'text/plain')
        if url==n.CALENDAR:return Response(url,CAL)
        if '/program/' in url:return Response(url,program())
        number=int(url[-5:-3])
        if '/syousai/' in url:
            if number==self.fail_race:raise OSError('TEST_SOURCE_FAILURE')
            raise n.ObservedRedirect(url,self.location or n.ORIGIN+f'/uma_shosai/{DAY_ID}{number:02}.do',302)
        if self.second_redirect:raise n.ObservedRedirect(url,url,302)
        return Response(url,card(number,cancelled=self.cancelled))


def client(tmp_path,**kwargs):
    clock=Clock();opener=Opener(clock,**kwargs)
    return n.Client(cache=tmp_path/'policy',opener=opener,clock=clock,sleep=clock.sleep,now=lambda:NOW),opener


def captured(tmp_path,**kwargs):
    c,o=client(tmp_path,**kwargs);output=tmp_path/'private'
    result=n.capture_race(DAY,1,output,client=c,now=lambda:NOW)
    return output,result,c,o


def rewrite(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False))


def test_cold_private_source_to_full_reference_and_offline_same_byte_readback(tmp_path,monkeypatch):
    output,(manifest,evidence,prediction,body),_,opener=captured(tmp_path)
    assert len(opener.calls)==5 and all(b[0]-a[0]>=10 for a,b in zip(opener.calls,opener.calls[1:]))
    assert manifest['runner_count']==2 and evidence['provider']=='NANKAN_OFFICIAL'
    assert evidence['sources'][0]['source_policy']['classification']=='ROBOTS_ABSENT_HTTP_404_NOT_DENIAL'
    assert prediction['model_sha256'] is None and prediction['unknown_runner_ids']==['2']
    assert prediction['temporal_class']=='INJECTED_CLOCK_CONTRACT_TEST'
    assert 'トウキョウスター' not in body and '父名を混ぜない' not in body
    assert '|1|テスト1|1位|' in body and '|2|テスト2|UNKNOWN|' in body
    assert all(part in body for part in ('展開見立て','参考上位','不確実性','最終結論','PAST_START_2_UNKNOWN'))
    monkeypatch.setattr(n,'render_private_reference',lambda *args:pytest.fail('readback must not re-render'))
    class Offline:
        def get(self,*args):pytest.fail('readback must not fetch')
    again=n.capture_race(DAY,1,output,client=Offline(),now=lambda:NOW+timedelta(days=10))
    assert again[0]==manifest and again[3]==body
    (output/'publication.json').unlink()
    assert n.capture_race(DAY,1,output,client=Offline(),now=lambda:NOW+timedelta(days=10))[0]==manifest


def test_legacy_freeze_without_scratch_witness_uses_its_frozen_parser_facts(tmp_path,monkeypatch):
    output,(_,evidence,prediction,body),_,_=captured(tmp_path)
    evidence.pop('explicit_card_exclusions')
    for row in evidence['runners']:
        row.pop('age',None)
    evidence['sha256']=n.sha({k:v for k,v in evidence.items() if k!='sha256'})
    prediction['input_sha256']=evidence['sha256']
    prediction['sha256']=n.sha({k:v for k,v in prediction.items() if k!='sha256'})
    parts=json.loads((output/'answer_parts.json').read_text())
    parts.update(input_sha256=evidence['sha256'],forecast_sha256=prediction['sha256'])
    for name,value in [('reference_evidence.json',evidence),('reference_prediction.json',prediction),
                       ('answer_parts.json',parts),('publication.json',n.publication_for(evidence,prediction,body,parts))]:
        rewrite(output/name,value)
    before={p.name:p.read_bytes() for p in output.iterdir() if p.is_file()}
    monkeypatch.setattr(n,'parse_card',lambda *a,**kw:pytest.fail('legacy readback must retain the original parser facts'))
    assert n.readback(output,DAY,1)[3]==body
    assert before=={p.name:p.read_bytes() for p in output.iterdir() if p.is_file()}


def test_current_refresh_recomputes_changed_universe_without_overwriting_or_duplicate_revision(tmp_path,monkeypatch):
    output,(_,_,original,body),c,_=captured(tmp_path)
    before={p.name:p.read_bytes() for p in output.iterdir() if p.is_file()}
    class ChangedCard:
        def get(self,url):
            meta,raw=c.get(url)
            if '/program/' in url:raw=raw.replace(b'2'+bytes('頭','utf-8'),b'1'+bytes('頭','utf-8'),1)
            if '/uma_shosai/' in url:
                raw=card(cancelled=True).decode().replace('(2頭)','(1頭)').replace(
                    '<td class="umaban">1</td>','<td class="umaban">取 消</td>',1).encode()
            meta['raw_sha256']=hashlib.sha256(raw).hexdigest()
            return meta,raw
    refreshed=n.capture_race(DAY,1,output,client=ChangedCard(),now=lambda:NOW,refresh=True)
    assert [r['runner_id'] for r in refreshed[1]['runners']]==['2']
    assert refreshed[1]['explicit_card_exclusions'][0]['provider_horse_id']=='1'
    assert refreshed[2]['reference_ranking']==[] and refreshed[2]['unknown_runner_ids']==['2']
    assert original['reference_ranking']==['1'] and '|1|テスト1|' not in refreshed[3]
    assert body==(output/'readback.txt').read_text()
    assert before=={p.name:p.read_bytes() for p in output.iterdir() if p.is_file()}
    revisions=list((output/'revisions').iterdir());assert len(revisions)==1
    (revisions[0]/'publication.json').unlink()
    monkeypatch.setattr(n,'compile_private_reference',lambda *a,**kw:pytest.fail('same source must reuse its revision'))
    assert n.capture_race(DAY,1,output,client=ChangedCard(),now=lambda:NOW,refresh=True)==refreshed
    assert list((output/'revisions').iterdir())==revisions
    class Offline:
        def get(self,url):pytest.fail('post-cutoff refresh must stop before HTTP')
    with pytest.raises(n.NankanError,match='CUTOFF_HOLD'):
        n.capture_race(DAY,1,output,client=Offline(),now=lambda:datetime.fromisoformat(refreshed[0]['race']['prediction_cutoff']),refresh=True)


@pytest.mark.parametrize('damage',['provider','future','http','calendar_hash','redirect_identity'])
def test_current_refresh_revalidates_fresh_observations_before_reusing_same_source(tmp_path,damage):
    output,_,c,_=captured(tmp_path)
    class DamagedCurrent:
        def get(self,url):
            if damage=='redirect_identity' and '/syousai/' in url:
                try:c.get(url)
                except n.ObservedRedirect as exc:
                    exc.receipt['source_url']=n.ORIGIN+'/syousai/'+DAY_ID+'02.do'
                    raise
            meta,raw=c.get(url)
            if '/uma_shosai/' in url:
                if damage=='provider':meta['provider']='OTHER_PROVIDER'
                if damage=='future':meta['fetched_at']=(NOW+timedelta(seconds=1)).isoformat()
                if damage=='http':meta['http_status']=500
            if url==n.CALENDAR and damage=='calendar_hash':meta['raw_sha256']='0'*64
            return meta,raw
    with pytest.raises(n.NankanError):
        n.capture_race(DAY,1,output,client=DamagedCurrent(),now=lambda:NOW,refresh=True)


@pytest.mark.parametrize('location',[n.ORIGIN+'/uma_shosai/2026102218070402.do',
    'https://evil.invalid/uma_shosai/'+DAY_ID+'01.do',n.ORIGIN+'/uma_shosai/'+DAY_ID+'01.do?token=secret',
    n.ORIGIN+'/syousai/'+DAY_ID+'01.do'])
def test_only_observed_same_race_canonical_transition_is_accepted(tmp_path,location):
    c,o=client(tmp_path,location=location)
    with pytest.raises(n.NankanError,match='CANONICAL_TRANSITION_HOLD'):n.capture_race(DAY,1,tmp_path/'private',client=c,now=lambda:NOW)
    assert not any('/uma_shosai/' in url for _,url,_ in o.calls)


@pytest.mark.parametrize('robots,code',[(b'User-agent: *\nDisallow: /\n','ROBOTS_DISALLOWED'),(503,'ROBOTS_UNKNOWN')])
def test_robots_denial_or_server_failure_does_not_fetch_calendar(tmp_path,robots,code):
    c,o=client(tmp_path,robots=robots)
    with pytest.raises(n.NankanError,match=code):n.capture_race(DAY,1,tmp_path/'private',client=c,now=lambda:NOW)
    assert [url for _,url,_ in o.calls]==[n.ROBOTS]


def test_crawl_delay_and_cache_tamper_fail_closed(tmp_path):
    c,o=client(tmp_path,robots=b'User-agent: *\nAllow: /\nCrawl-delay: 20\n')
    c.get(n.CALENDAR)
    assert o.calls[1][0]-o.calls[0][0]>=20
    path=tmp_path/'policy/robots.json';state=json.loads(path.read_text());state['text']='User-agent: *\nAllow: /\n';rewrite(path,state)
    with pytest.raises(n.NankanError,match='ROBOTS_UNKNOWN'):c.get(n.CALENDAR)
    assert len(o.calls)==2


def test_second_redirect_is_not_followed(tmp_path):
    c,o=client(tmp_path,second_redirect=True)
    with pytest.raises(n.NankanError,match='SECOND_REDIRECT_HOLD'):n.capture_race(DAY,1,tmp_path/'private',client=c,now=lambda:NOW)
    assert len(o.calls)==5


def test_history_before_target_but_after_actual_capture_is_not_available_evidence(tmp_path):
    original,_=client(tmp_path)
    class FutureHistory:
        def get(self,url):
            meta,raw=original.get(url)
            if '/uma_shosai/' in url:
                raw=raw.replace(b'26.9.20',b'26.10.21').replace(b'/result/20260920',b'/result/20261021')
                meta['raw_sha256']=hashlib.sha256(raw).hexdigest()
            return meta,raw
    with pytest.raises(n.NankanError,match='HISTORY_AFTER_ACTUAL_CAPTURE'):
        n.capture_race(DAY,1,tmp_path/'private',client=FutureHistory(),now=lambda:NOW)
    assert not (tmp_path/'private/publication.json').exists()


@pytest.mark.parametrize('damage',['raw','wrong_race','time','formal','truncate','rank'])
def test_private_checkpoint_detects_tampering_even_if_publication_rehashed(tmp_path,damage):
    output,(manifest,evidence,prediction,body),_,_=captured(tmp_path)
    if damage=='raw':(output/'card.html.gz').write_bytes(gzip.compress(b'wrong original'))
    if damage=='wrong_race':evidence['race']['race_no']=2
    if damage=='time':prediction['generation_completed_at']=evidence['race']['scheduled_post_at']
    if damage=='formal':prediction['formal_final_proven']=True
    if damage in ('truncate','rank'):
        body=body.split('最終結論')[0] if damage=='truncate' else body.replace('|1|テスト1|1位|','|1|テスト1|2位|')
        (output/'readback.txt').write_text(body)
    evidence['sha256']=n.sha({k:v for k,v in evidence.items() if k!='sha256'})
    prediction['sha256']=n.sha({k:v for k,v in prediction.items() if k!='sha256'})
    rewrite(output/'reference_evidence.json',evidence);rewrite(output/'reference_prediction.json',prediction)
    manifest.update(input_sha256=evidence['sha256'],forecast_sha256=prediction['sha256'],answer_sha256=hashlib.sha256(body.encode()).hexdigest())
    manifest['sha256']=n.sha({k:v for k,v in manifest.items() if k!='sha256'});rewrite(output/'publication.json',manifest)
    with pytest.raises(n.NankanError):n.readback(output,DAY,1)


def test_concurrent_same_race_captures_only_once(tmp_path):
    c,o=client(tmp_path)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _:n.capture_race(DAY,1,tmp_path/'private',client=c,now=lambda:NOW),range(2)))
    assert len(o.calls)==5 and results[0][0]==results[1][0] and results[0][3]==results[1][3]


def test_day_shares_discovery_and_holds_one_race_without_stopping_next(tmp_path):
    c,o=client(tmp_path,fail_race=1)
    status=n.capture_day(DAY,tmp_path/'private',client=c,now=lambda:NOW)
    assert status['cohort_race_numbers']==[1,2] and status['discovered_count']==2
    assert status['reference_complete_count']==1 and status['races'][0]['status']=='HOLD'
    assert status['races'][1]['status']=='PRIVATE_REFERENCE_COMPLETE'
    assert sum(url==n.CALENDAR for _,url,_ in o.calls)==1
    assert sum('/program/' in url for _,url,_ in o.calls)==1


@pytest.mark.parametrize('name',['cohort.json','calendar.html.gz','program.html.gz','status.json.tmp'])
def test_day_private_checkpoint_never_follows_symlink(tmp_path,name):
    c,_=client(tmp_path);root=tmp_path/'private'
    n.capture_day(DAY,root,client=c,now=lambda:NOW)
    target=root/DAY/name;outside=tmp_path/'unrelated-original'
    if target.exists():target.rename(outside)
    else:outside.write_bytes(b'unchanged private file')
    original=outside.read_bytes();target.symlink_to(outside)
    with pytest.raises(n.NankanError,match='SYMLINK'):
        n.capture_day(DAY,root,client=c,now=lambda:NOW)
    assert outside.read_bytes()==original


@pytest.mark.parametrize('entry',['race_lock','day_lock','dangling_cohort'])
def test_private_worker_and_dangling_cohort_symlinks_hold_before_http(tmp_path,entry):
    c,o=client(tmp_path);root=tmp_path/'private'
    n.private_directory(root)
    folder=root if entry=='race_lock' else n.private_directory(root/DAY)
    outside=tmp_path/'outside-must-not-be-created'
    name='cohort.json' if entry=='dangling_cohort' else 'worker.lock'
    (folder/name).symlink_to(outside)
    with pytest.raises(n.NankanError,match='SYMLINK'):
        if entry=='race_lock':n.capture_race(DAY,1,root,client=c,now=lambda:NOW)
        else:n.capture_day(DAY,root,client=c,now=lambda:NOW)
    assert not o.calls and not outside.exists()


def test_day_rehashed_cohort_provider_or_race_change_is_rejected(tmp_path):
    c,_=client(tmp_path);root=tmp_path/'private'
    n.capture_day(DAY,root,client=c,now=lambda:NOW)
    path=root/DAY/'cohort.json';cohort=json.loads(path.read_text())
    cohort['races'][0]['venue_id']='KAW';cohort['sha256']=n.sha({k:v for k,v in cohort.items() if k!='sha256'})
    rewrite(path,cohort)
    with pytest.raises(n.NankanError,match='COHORT_IDENTITY'):
        n.capture_day(DAY,root,client=c,now=lambda:NOW)


def test_private_output_rejects_git_public_and_symlink(tmp_path):
    repo=tmp_path/'repo';repo.mkdir();(repo/'.git').mkdir()
    with pytest.raises(n.NankanError,match='INSIDE_GIT'):n.private_directory(repo/'private')
    with pytest.raises(n.NankanError,match='PARENT_PATH'):n.private_directory(tmp_path/'missing'/'..'/'repo'/'private')
    with pytest.raises(n.NankanError,match='PUBLIC_OUTPUT'):n.private_directory(tmp_path/'public'/'private')
    link=tmp_path/'link';link.symlink_to(tmp_path/'other',target_is_directory=True)
    with pytest.raises(n.NankanError,match='SYMLINK'):n.private_directory(link/'private')


def test_completed_after_cutoff_does_not_create_publication(tmp_path):
    output,(manifest,evidence,_,_),_,_=captured(tmp_path)
    raw=[gzip.decompress((output/name).read_bytes()) for name in ('calendar.html.gz','program.html.gz','card.html.gz')]
    times=iter([NOW,NOW,datetime.fromisoformat(evidence['race']['prediction_cutoff'])])
    with pytest.raises(n.NankanError,match='COMPLETED_AFTER_CUTOFF'):
        n.freeze_observations(tmp_path/'late',DAY,1,deepcopy(evidence['sources']),raw,clock=lambda:next(times))
    assert not (tmp_path/'late/publication.json').exists()


def test_cancelled_horse_remains_listed_but_not_top_or_pace(tmp_path):
    _,(_,_,prediction,body),_,_=captured(tmp_path,cancelled=True)
    assert prediction['runners'][0]['status']=='CANCELLED' and '1' not in prediction['reference_ranking']
    assert '|1|テスト1|取消・除外|' in body
    assert '近走で前方通過の確認できる2番' in body


def test_cli_help_is_available_without_optional_crypto_dependency():
    root=Path(__file__).resolve().parents[1]
    result=subprocess.run([sys.executable,'-S','-m','runtime.urw_nankan_reference_source','--help'],cwd=root,capture_output=True,text=True)
    assert result.returncode==0 and '--all-races' in result.stdout and '--import-observations' in result.stdout


def test_fixed_five_module_private_cli_cold_parse_freeze_and_readback(tmp_path):
    root=Path(__file__).resolve().parents[1];deployment=tmp_path/'isolated';deployment.mkdir()
    for name in ('runtime/urw_nankan_reference_source.py','runtime/urw_reference_source_policy.py',
                 'runtime/local_production_static_owner.py','runtime/local_nar_evidence_candidate.py',
                 'runtime/local_physical/nar_source_manifest.py'):
        target=deployment/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(root/name,target)
    values={'day':DAY,'now':NOW.isoformat(),'day_id':DAY_ID,
            'calendar':CAL.decode(),'program':program().decode(),'card':detailed_card().decode()}
    (deployment/'synthetic.json').write_text(json.dumps(values))
    script='''
import hashlib,json,sys,urllib.request
from pathlib import Path
from datetime import datetime
from runtime import urw_nankan_reference_source as n
x=json.loads(Path('synthetic.json').read_text());now=datetime.fromisoformat(x['now'])
raw=[x[key].encode() for key in ('calendar','program','card')]
urls=[n.CALENDAR,n.ORIGIN+'/program/'+x['day_id']+'.do',n.ORIGIN+'/uma_shosai/'+x['day_id']+'01.do']
sources=[dict(url=url,http_status=200,fetched_at=now.isoformat(),raw_sha256=hashlib.sha256(body).hexdigest()) for url,body in zip(urls,raw)]
sources.insert(2,dict(source_url=n.ORIGIN+'/syousai/'+x['day_id']+'01.do',location=urls[-1],http_status=302,fetched_at=now.isoformat()))
def offline(*a,**k):raise AssertionError('NO_HTTP_ALLOWED')
urllib.request.OpenerDirector.open=offline
result=n.freeze_observations(Path.cwd()/'private',x['day'],1,sources,raw,now=now,clock=lambda:now)
again=n.readback(Path.cwd()/'private',x['day'],1)
assert again==result and result[1]['runners'][0]['current_body_weight']==481
assert not any(name.startswith('cryptography') for name in sys.modules)
assert result[1]['signed_source_claim'] is False and result[2]['production_authority'] is False
print(json.dumps({'runners':result[0]['runner_count'],'readback_same':True}))
'''
    result=subprocess.run([sys.executable,'-S','-c',script],cwd=deployment,
                          env={**os.environ,'PYTHONPATH':''},capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    assert json.loads(result.stdout)=={'runners':2,'readback_same':True}

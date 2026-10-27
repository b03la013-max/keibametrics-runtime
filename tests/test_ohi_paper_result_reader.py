"""Portable research-reader regressions; no private official Raw or predictions."""
import copy,json
import pytest
from scripts.ohi_paper_day_review import digest, parse_rendered_result, settle_owner, review_day


def example(*, excluded=False, extra=False, refund=True):
    ids=['1','2','3']+(['4'] if excluded else [])
    original={'race':{'provider_race_id':'2026102720110201','race_no':1,'race_date':'2026-10-27'},
        'all_runners':[{'runner_id':i,'name':'Horse'+i,'provider_horse_id':'H'+i} for i in ids],
        'source_sha256':'not-used-without-observation','sha256':'frozen-prediction',
        'owners':{},'portfolios':{}}
    source={'changes':{'items':[]}}
    if extra:
        source['changes']['items']=[{'runner_id':'5','provider_horse_id':'H5','name':'Horse5','status':'CANCELLED'}]
    source['sha256']=digest(source)
    original['source_sha256']=source['sha256']
    lines=['1R 2026年10月27日 第11回 大井競馬 第2日 発走時刻14:22',
        '着 | 枠 | 馬番 | 馬名 | 性齢 | 負担 | 馬体重 | 増減 | 騎手 | 調教師 | タイム | 着差 | 上がり3F | コーナー通過順 | 人気']
    for no in ('1','2','3'):
        lines.append(f'{no} | {no} | {no} | Horse{no} | 牡3 | 56 | 450kg | 0 | Rider | Trainer | 1:40.0 | - | 39.0 | - | {no}')
    if excluded:lines.append('- | 4 | 4 | Horse4 | 牝3 | 54 | 440kg | 0 | Rider | Trainer | - | 競走除外 | - | - |')
    if extra:lines.append('- | 5 | 5 | Horse5 | 牝3 | 54 | - | - | Rider | Trainer | - | 出走取消 | - | - |')
    lines += ['#### タイム','#### 通過順','3角 | (1,2),3',
        '#### 払戻金',' | 組番 | 金額 | 人気','馬単 | 1-2 | 500 | 1',
        '三連複 | 1-2-3 | 700 | 1','三連単 | 1-2-3 | 1,000 | 1',
        '備考 | '+('返還：4号馬' if excluded and refund else '')]
    text='https://www.nankankeiba.com/result/2026102720110201.do\n【turnFixtureview0】\n'
    text+='\n'.join(f'L{i}: {s}' for i,s in enumerate(lines))
    doc={'race_no':1,'text':text,'retrieved_at':'2026-10-27T13:00:00+00:00',
        'provider':'NANKAN_OFFICIAL',
        'classification':'OFFICIAL_WEB_RENDERED_RETRIEVAL_NOT_RAW_HTML_NOT_SIGNED_RESULT'}
    return doc,original,source


def test_plain_result_keeps_research_and_actual_start_unknown():
    d,o,s=example();before=copy.deepcopy((d,o,s));r=parse_rendered_result(d,o)
    assert r['result_header_post_time']=='14:22'
    assert r['actual_off_time_independently_observed'] is False
    assert r['formal_signed_result'] is False
    assert r['corner_passages']=={'3角':'(1,2),3'}
    assert r['official']['refund_runner_ids']==[] and (d,o,s)==before


def test_dash_exclusion_with_explicit_refund_preserves_frozen_four():
    d,o,s=example(excluded=True);r=parse_rendered_result(d,o)
    assert r['frozen_runner_count']==4 and r['official']['refund_runner_ids']==['4']
    o['portfolios']['TEST']={'tickets':[{'bet_type':'EXACTA','selection':['1','4'],'stake':100}],
        'capital':{'no_bet':False,'capital_limit':10000,'required_capital':100},'mec':{'tickets':[]}}
    x=settle_owner(o,'TEST',r)
    assert (x['refund'],x['winning_return'],x['profit_loss'])==(100,0,0)
    assert x['minimum_required_mec']==100


def test_missing_explicit_refund_is_hold():
    d,o,s=example(excluded=True,refund=False)
    with pytest.raises(ValueError,match='REFUND_AUTHORITY'):parse_rendered_result(d,o)


def test_wrong_refund_runner_is_hold():
    d,o,s=example(excluded=True);d['text']=d['text'].replace('返還：4号馬','返還：3号馬')
    with pytest.raises(ValueError,match='REFUND_AUTHORITY'):parse_rendered_result(d,o)


def test_frozen_prestart_cancelled_outsider_needs_exact_source():
    d,o,s=example(extra=True)
    with pytest.raises(ValueError,match='RUNNER_IDENTITY'):parse_rendered_result(d,o)
    r=parse_rendered_result(d,o,prestart_observation=s)
    assert r['official_observed_state_count']==4 and r['frozen_runner_count']==3
    assert r['prestart_excluded_outside_frozen_universe'][0]['runner_id']=='5'
    assert r['official']['refund_runner_ids']==[]


def test_prestart_source_tampering_rejected():
    d,o,s=example(extra=True);s['changes']['items'][0]['name']='AnotherHorse'
    with pytest.raises(ValueError,match='PRESTART_SOURCE_SHA'):parse_rendered_result(d,o,prestart_observation=s)


def test_prestart_exclusion_cannot_be_result_finisher():
    d,o,s=example(extra=True)
    d['text']=d['text'].replace('- | 5 | 5 | Horse5','4 | 5 | 5 | Horse5').replace('出走取消','-')
    with pytest.raises(ValueError,match='PREEXCLUSION_STATUS'):parse_rendered_result(d,o,prestart_observation=s)


def test_unnumbered_cancellation_does_not_assign_missing_number():
    d,o,s=example(extra=True);s['changes']['items'][0]['runner_id']=None
    s.pop('sha256');s['sha256']=digest(s);o['source_sha256']=s['sha256']
    with pytest.raises(ValueError,match='RUNNER_IDENTITY'):parse_rendered_result(d,o,prestart_observation=s)


@pytest.mark.parametrize('needle,replacement,reason',[
    ('/result/2026102720110201.do','/result/2026102720110202.do','URL_RACE'),
    ('1R 2026年10月27日','1R 2026年10月26日','DATED_VENUE'),
    ('備考 | ','備考 | 別途確認が必要','SPECIAL_REMARK'),
    ('3 | 3 | 3 | Horse3','3 | 3 | 3 | WrongHorse','RUNNER_IDENTITY'),
    ('3 | 3 | 3 | Horse3','3 | 3 | 2 | Horse3','DUPLICATE_RUNNER'),
])
def test_identity_and_unknown_remark_fail_closed(needle,replacement,reason):
    d,o,s=example();d['text']=d['text'].replace(needle,replacement)
    with pytest.raises(ValueError,match=reason):parse_rendered_result(d,o)


def test_contradictory_numeric_rank_and_exclusion_rejected():
    d,o,s=example(excluded=True);d['text']=d['text'].replace('- | 4 | 4 | Horse4','4 | 4 | 4 | Horse4')
    with pytest.raises(ValueError,match='CONTRADICTORY'):parse_rendered_result(d,o)


def test_alternate_provider_and_raw_claim_rejected():
    d,o,s=example();d['provider']='NAR_OFFICIAL'
    with pytest.raises(ValueError,match='PROVENANCE'):parse_rendered_result(d,o)
    d['provider']='NANKAN_OFFICIAL';d['classification']='RAW_HTTP_OR_SIGNED_RESULT'
    with pytest.raises(ValueError,match='PROVENANCE'):parse_rendered_result(d,o)


def test_duplicate_refund_number_rejected():
    d,o,s=example(excluded=True);d['text']=d['text'].replace('返還：4号馬','返還：4,4号馬')
    with pytest.raises(ValueError,match='DUPLICATE_REFUND'):parse_rendered_result(d,o)


def test_zero_stake_is_null_pfs():
    d,o,s=example();r=parse_rendered_result(d,o)
    o['portfolios']['TEST']={'tickets':[],'capital':{'no_bet':True,'capital_limit':10000,'required_capital':10300},'mec':{'tickets':[]}}
    x=settle_owner(o,'TEST',r)
    assert x['pfs'] is None and x['refund']==0 and x['execution_status']=='CALCULATED_NO_BET'
    assert x['minimum_required_mec']==10300


@pytest.mark.parametrize('field',['race_no','race_id','revision','prediction_sha256'])
def test_duplicate_index_identity_refused_before_readback(tmp_path,field):
    row={'race_no':1,'race_id':'2026102720110201','revision':'one','prediction_sha256':'a'}
    second={'race_no':2,'race_id':'2026102720110202','revision':'two','prediction_sha256':'b'}
    second[field]=row[field]
    p=tmp_path/'index.json';p.write_text(json.dumps({'race_date':'2026-10-27','rows':[row,second]}))
    with pytest.raises(ValueError,match='INDEX_DUPLICATE'):review_day(p,tmp_path,tmp_path)


@pytest.mark.parametrize('field,value',[('race_date','2026-10-28'),('race_id','2026102620110101'),('race_no',2)])
def test_index_day_race_binding_checked_against_frozen(tmp_path,monkeypatch,field,value):
    d,o,s=example();o['sha256']='frozen'
    import scripts.ohi_paper_day_review as module
    monkeypatch.setattr(module,'readback',lambda path:(o,''))
    index={'race_date':'2026-10-27','rows':[{'race_no':1,'race_id':'2026102720110201','revision':'one','prediction_sha256':'frozen'}]}
    if field=='race_date':index[field]=value
    else:index['rows'][0][field]=value
    p=tmp_path/'index.json';p.write_text(json.dumps(index))
    with pytest.raises(ValueError,match='INDEX_RACE_IDENTITY'):review_day(p,tmp_path,tmp_path)

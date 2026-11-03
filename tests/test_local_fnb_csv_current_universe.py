"""Synthetic independent card/odds current-status candidates, no adoption."""
from datetime import datetime, timezone, timedelta
import csv
import hashlib
import io
import zipfile

import pytest
from runtime import local_fnb_csv_current_universe as u
from runtime.local_nar_csv_reference import SCHEMAS

NOW=datetime(2026,11,4,3,1,tzinfo=timezone.utc)
REQUEST={'venue_id':'FNB','race_date':'2026-11-04','race_no':1,
         'scheduled_post_at':'2026-11-04T14:40:00+09:00',
         'prediction_cutoff':'2026-11-04T14:35:00+09:00'}
LIMITS={'max_fetch_age_seconds':300,'max_archive_age_seconds':300}


def archive(tables):
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w') as z:
        for kind,rows in tables.items():
            s=io.StringIO(newline='');w=csv.writer(s);w.writerow(SCHEMAS[kind])
            for row in rows:w.writerow([row.get(k,'') for k in SCHEMAS[kind]])
            z.writestr('20261104_'+kind+'.csv',s.getvalue().encode('utf-8-sig'))
    return b.getvalue()


def fixtures(*, prices=('2.0','3.0'),cancel=False,finished=False,age=60):
    race=dict(競馬場='船橋',競走年月日='20261104',レース番号='1',発走時刻='1440',
              頭数='2',距離='1200',芝ダート区分='ダート',回り='左')
    horses=[]
    for no in (1,2):
        row=dict(競馬場='船橋',競走年月日='20261104',レース番号='1',馬番=str(no),
            馬名='合成馬'+str(no),騎手名='合成騎手',人気='1')
        if cancel and no==2:row.update(着差='出走取消',タイム='0')
        if finished and no==1:row.update(着順='1',タイム='1120')
        horses.append(row)
    card=archive({'racelist':[race],'horselist':horses})
    odds=archive({'odds':[dict(競馬場='船橋',競走年月日='20261104',レース番号='1',
        賭式='単勝',番号1=str(no),オッズ=price) for no,price in enumerate(prices,1)]})
    def capture(raw,url,kind):
        return {'provider':'NAR_OFFICIAL_CSV','http_status':200,'source_url':url,'final_url':url,
            'raw_sha256':hashlib.sha256(raw).hexdigest(),'captured_at':(NOW-timedelta(seconds=1)).isoformat(),
            'retrieval_method':'AUTHORIZED_HTTP_GET',
            'content_disposition':'attachment; filename="20261104_'+str(int((NOW-timedelta(seconds=age)).timestamp()))+'_'+kind+'.zip"'}
    return dict(race_raw=card,race_receipt=capture(card,u.DAILY_URL,'race'),request=REQUEST,
        freeze_at=NOW.isoformat(),odds_raw=odds,odds_receipt=capture(odds,u.DAILY_ODDS_URL,'odds'),
        freshness_limits=LIMITS)


def test_matching_positive_single_win_set_is_unsigned_candidate_only():
    result=u.assess_current_universe(**fixtures())
    assert result['complete_current_universe_candidate'] is True
    assert [r['status'] for r in result['rows']]==['ACTIVE','ACTIVE']
    assert result['source_admitted'] is result['profile_adopted'] is result['signature_verified'] is False
    assert result['production_consumers_authorized'] is False
    assert result['no_future_change_guarantee'] is True


@pytest.mark.parametrize('quote',['0','0.0','','nan','Infinity','-1'])
def test_zero_or_invalid_quote_never_confirms_active_or_inactive(quote):
    result=u.assess_current_universe(**fixtures(prices=('2.0',quote)))
    assert result['complete_current_universe_candidate'] is False
    assert result['rows'][1]['status']=='ACTIVE_DECLARED'
    assert result['rows'][1]['independent_win_quote']['state']=='UNKNOWN'


def test_absent_independent_odds_is_unknown_not_inactive():
    kw=fixtures();kw.update(odds_raw=None,odds_receipt=None)
    result=u.assess_current_universe(**kw)
    assert result['complete_current_universe_candidate'] is False
    assert [r['status'] for r in result['rows']]==['ACTIVE_DECLARED','ACTIVE_DECLARED']


def test_explicit_scratch_removed_from_candidate_active_set_without_outcome_leak():
    result=u.assess_current_universe(**fixtures(prices=('2.0','0.0'),cancel=True))
    assert result['complete_current_universe_candidate'] is True
    assert result['rows'][1]['status']=='CANCELLED'
    assert result['positive_win_ids']==['1']


def test_same_snapshot_explicit_scratch_positive_quote_is_real_conflict():
    result=u.assess_current_universe(**fixtures(cancel=True))
    assert result['complete_current_universe_candidate'] is False
    assert result['true_observed_conflicts']==['EXPLICIT_SCRATCH_WITH_POSITIVE_WIN_QUOTE:2']


def test_fetch_does_not_reset_archive_snapshot_age_and_no_implicit_policy():
    result=u.assess_current_universe(**fixtures(age=1000))
    assert result['complete_current_universe_candidate'] is False
    assert result['snapshots'][0]['fetch_age_seconds']==1
    assert result['snapshots'][0]['archive_age_seconds']==1000
    kw=fixtures();kw['freshness_limits']=None
    assert u.assess_current_universe(**kw)['complete_current_universe_candidate'] is False


def test_finished_race_cannot_be_candidate_current_field():
    with pytest.raises(ValueError,match='ACTUAL_RACE_RESULT_PRESENT'):
        u.assess_current_universe(**fixtures(finished=True))


def test_raw_mutation_or_crossday_archive_cannot_be_qualified():
    kw=fixtures();kw['race_receipt']['raw_sha256']='0'*64
    with pytest.raises(ValueError,match='ORIGINAL_CAPTURE_UNVERIFIED'):
        u.assess_current_universe(**kw)
    kw=fixtures();kw['odds_receipt']['content_disposition']=kw['odds_receipt']['content_disposition'].replace('20261104_','20261105_')
    with pytest.raises(ValueError,match='ARCHIVE_DAY_OR_TIMESTAMP'):
        u.assess_current_universe(**kw)

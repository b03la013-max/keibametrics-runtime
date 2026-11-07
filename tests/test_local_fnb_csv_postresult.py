"""Synthetic adapter checks; qualified SOURCE/result verifiers are not issued."""
import csv
from copy import deepcopy
from datetime import datetime,timezone
import hashlib
import io
import json
import zipfile

import pytest
from runtime import local_fnb_csv_postresult as result
from runtime import local_fnb_research_runtime as private
from runtime.local_nar_csv_reference import SCHEMAS

NOW=datetime(2026,11,3,14,0,tzinfo=timezone.utc)
RACE={'venue_id':'FNB','race_date':'2026-11-03','race_no':1}


def original(*,tie=False):
    identity={'競馬場':'船橋','競走年月日':'20261103','レース番号':'1'}
    race={**dict.fromkeys(SCHEMAS['racelist'],''),**identity,'発走時刻':'1445',
          '距離':'1200','芝ダート区分':'ダート','回り':'左','頭数':'3'}
    horses=[{**dict.fromkeys(SCHEMAS['horselist'],''),**identity,'馬番':str(no),
             '馬名':f'SYNTHETIC{no}','着順':str(1 if tie and no==2 else no)} for no in (1,2,3)]
    pay={**dict.fromkeys(SCHEMAS['payback'],''),**identity,
         '馬単組番1':'1','馬単組番2':'2','馬単払戻金（円）':'1200',
         '３連複組番馬番1':'1','３連複組番馬番2':'2','３連複組番馬番3':'3','３連複払戻金（円）':'500',
         '３連単組番馬番1':'1','３連単組番馬番2':'2','３連単組番馬番3':'3','３連単払戻金（円）':'2000'}
    payrows=[pay]
    if tie:
        payrows.append({**pay,'馬単組番1':'2','馬単組番2':'1','馬単払戻金（円）':'1800',
            '３連単組番馬番1':'2','３連単組番馬番2':'1','３連単払戻金（円）':'2800'})
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w') as archive:
        for kind,rows in [('racelist',[race]),('horselist',horses),('payback',payrows)]:
            text=io.StringIO(newline='');writer=csv.writer(text)
            writer.writerow(SCHEMAS[kind]);writer.writerows([[row[k] for k in SCHEMAS[kind]] for row in rows])
            archive.writestr('20261103_'+kind+'.csv',text.getvalue().encode('utf-8-sig'))
    raw=buffer.getvalue()
    capture={'provider':'NAR_OFFICIAL_CSV','http_status':200,'raw_sha256':hashlib.sha256(raw).hexdigest(),
        'source_url':'https://www.keiba.go.jp/KeibaWeb/DataDownload/RaceDataDownload?type=daily',
        'captured_at':NOW.isoformat(),'retrieval_method':'AUTHORIZED_HTTP_GET',
        'usage_qualification':{'classification':'SYNTHETIC_NOT_PROVIDER_PERMISSION'}}
    return raw,capture


def parsed(tie=False):
    raw,capture=original(tie=tie)
    return result.parse_result(raw,capture=capture,race=RACE,now=NOW)


def frozen(tmp_path,method='EXACTA'):
    value={**RACE,'race_id':'KM-LOCAL-FNB-20261103-R01-SYNTHETIC',
        'classification':private.PRESTART_CLASSIFICATION,'freeze_at':'2026-11-03T14:30:00+09:00',
        'prediction_cutoff':'2026-11-03T14:40:00+09:00','scheduled_post_at':'2026-11-03T14:45:00+09:00',
        'selection_complete':True,'method':method,'final_ticket':{'total_investment':300,'tickets':[
            {'bet_type':'EXACTA','selection':[1,2],'stake':200},
            {'bet_type':'EXACTA','selection':[1,3],'stake':100}]}}
    if method=='TRIO':value['final_ticket']={'total_investment':100,'tickets':[
            {'bet_type':'TRIO','selection':[3,1,2],'stake':100}]}
    if method=='TRIFECTA':value['final_ticket']={'total_investment':200,'tickets':[
            {'bet_type':'TRIFECTA','selection':[2,1,3],'stake':100},
            {'bet_type':'TRIFECTA','selection':[1,3,2],'stake':100}]}
    path=tmp_path/'frozen.json';raw=private.encoded(value);path.write_bytes(raw)
    return value,path,hashlib.sha256(raw).hexdigest()


def qualified(candidate,refunds=None):
    return {'result_sha256':candidate['sha256'],'published_payouts_complete':True,
        'refund_completeness_verified':True,'refunded_runner_ids':refunds or [],
        'evidence_original_sha256':'a'*64}


def settle(candidate,tmp_path,*,qualifier=None,method='EXACTA'):
    value,path,digest=frozen(tmp_path,method)
    return result.settle_frozen(candidate,path,expected_sha256=digest,
        verify_frozen=lambda **kwargs:True,
        verify_result=qualifier or (lambda **kwargs:qualified(candidate)),
        private_root=tmp_path/'settlement',now=NOW)


def test_original_result_columns_and_payout_orientation_preserved():
    candidate=parsed()
    assert candidate['unique_top3']==[1,2,3]
    assert candidate['payouts_per_100']['EXACTA']=={'1>2':1200}
    assert candidate['payouts_per_100']['TRIO']=={'1>2>3':500}
    assert candidate['payout_field_evidence'][0]['csv_row']==2
    assert candidate['official_result_admission_verified'] is False
    assert candidate['PFS'] is None


def test_dead_heat_preserves_both_published_ordered_combinations():
    candidate=parsed(tie=True)
    assert candidate['unique_top3'] is None
    assert candidate['finish_groups'][0]=={'finish':1,'runners':[1,2]}
    assert candidate['payouts_per_100']['EXACTA']=={'1>2':1200,'2>1':1800}
    assert candidate['payouts_per_100']['TRIFECTA']['2>1>3']==2800


def test_absent_frozen_prediction_stays_uncomputed_and_pfs_null(tmp_path):
    value=result.settle_frozen(parsed(),None,expected_sha256=None,verify_frozen=None,
        verify_result=None,private_root=tmp_path,now=NOW)
    assert value['status']=='UNCOMPUTED_NO_FROZEN_PREDICTION'
    assert value['PFS'] is None and value['computed_no_bet'] is False


def test_settlement_uses_stakes_and_each_method_without_combining_recommendations(tmp_path):
    settled=settle(parsed(),tmp_path)
    assert settled['investment']==300 and settled['return']==2400
    assert settled['profit_loss']==2100 and settled['PFS']=='800'
    assert settled['formal_result_signature_issued'] is False
    receipt=settled['private_original'];raw=__import__('pathlib').Path(receipt['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==receipt['sha256']


def test_refund_evidence_required_and_refund_excluded_from_denominator(tmp_path):
    candidate=parsed()
    with pytest.raises(ValueError,match='REFUND_QUALIFICATION'):
        settle(candidate,tmp_path,qualifier=lambda **kwargs:{})
    settled=settle(candidate,tmp_path,qualifier=lambda **kwargs:qualified(candidate,[3]))
    assert settled['refund']==100 and settled['effective_investment']==200
    assert settled['return']==2400 and settled['PFS']=='1200'


def test_deadheat_returns_from_exact_published_ticket_payouts(tmp_path):
    settled=settle(parsed(tie=True),tmp_path,method='TRIFECTA')
    assert settled['return']==2800 and settled['method']=='TRIFECTA'


def test_prestart_or_incomplete_ticket_original_cannot_be_manufactured(tmp_path):
    candidate=parsed();value,path,digest=frozen(tmp_path)
    value['selection_complete']=False;raw=private.encoded(value);path.write_bytes(raw)
    with pytest.raises(ValueError,match='UNCOMPUTED_OR_INCOMPLETE'):
        result.settle_frozen(candidate,path,expected_sha256=hashlib.sha256(raw).hexdigest(),
            verify_frozen=lambda **kwargs:True,verify_result=lambda **kwargs:qualified(candidate),
            private_root=tmp_path/'out',now=NOW)
    value['selection_complete']=True;value['freeze_at']=value['prediction_cutoff']
    raw=private.encoded(value);path.write_bytes(raw)
    with pytest.raises(ValueError,match='PRESTART_TIME'):
        result.settle_frozen(candidate,path,expected_sha256=hashlib.sha256(raw).hexdigest(),
            verify_frozen=lambda **kwargs:True,verify_result=lambda **kwargs:qualified(candidate),
            private_root=tmp_path/'out',now=NOW)


def test_mutation_wrong_raw_or_unverified_source_holds(tmp_path):
    raw,capture=original();capture['raw_sha256']='b'*64
    with pytest.raises(ValueError,match='PROVENANCE'):
        result.parse_result(raw,capture=capture,race=RACE,now=NOW)
    candidate=parsed();candidate['payouts_per_100']['EXACTA']['1>2']=9999
    with pytest.raises(ValueError,match='HASH_MISMATCH'):
        settle(candidate,tmp_path)


def test_methods_cannot_be_combined_in_one_frozen_portfolio(tmp_path):
    candidate=parsed();value,path,digest=frozen(tmp_path)
    value['final_ticket']['tickets'][1]={'bet_type':'TRIO','selection':[1,2,3],'stake':100}
    raw=private.encoded(value);path.write_bytes(raw)
    with pytest.raises(ValueError,match='INCOMPLETE_TICKETS'):
        result.settle_frozen(candidate,path,expected_sha256=hashlib.sha256(raw).hexdigest(),
            verify_frozen=lambda **kwargs:True,verify_result=lambda **kwargs:qualified(candidate),
            private_root=tmp_path/'out',now=NOW)


def test_zero_ticket_requires_verified_computed_no_bet_reason(tmp_path):
    candidate=parsed();value,path,digest=frozen(tmp_path)
    value['final_ticket']={'tickets':[],'total_investment':0}
    def call():
        raw=private.encoded(value);path.write_bytes(raw)
        return result.settle_frozen(candidate,path,expected_sha256=hashlib.sha256(raw).hexdigest(),
            verify_frozen=lambda **kwargs:True,verify_result=lambda **kwargs:qualified(candidate),
            private_root=tmp_path/'out',now=NOW)
    with pytest.raises(ValueError,match='INCOMPLETE_TICKETS'):call()
    value.update(computed_no_bet=True,no_bet_reason='SYNTHETIC_COMPLETED_SELECTION_NO_BET')
    settled=call()
    assert settled['computed_no_bet'] is True and settled['PFS'] is None


def test_cancelled_runner_omitted_from_csv_requires_qualified_refund_identity(tmp_path):
    candidate=parsed()
    candidate['runner_outcomes']=[row for row in candidate['runner_outcomes'] if row['runner_id']!=3]
    candidate['sha256']=result.sha({k:v for k,v in candidate.items() if k!='sha256'})
    with pytest.raises(ValueError,match='RUNNER_NOT_IN_RESULT_UNIVERSE'):
        settle(candidate,tmp_path)
    settled=settle(candidate,tmp_path,qualifier=lambda **kwargs:qualified(candidate,[3]))
    assert settled['refund']==100 and settled['effective_investment']==200

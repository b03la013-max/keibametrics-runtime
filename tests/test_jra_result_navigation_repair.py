"""All transport cases use a mocked official opener; no provider HTTP traffic."""
import base64
import copy
import hashlib
import http.cookiejar
import io
import json
from email.message import Message
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/jra_source_runtime')]
import jra_candidate_postresult_closedloop as candidate
import jra_pedigree_harvest as harvest
import jra_same_day_results as result

DATE='2026-10-25'
KEY='0420260404'
ENTRY='pw01sli00MOCK/AB'
DAY='pw01srl00'+KEY+'20261025/CD'
RACE='pw01sde01'+KEY+'1120261025/EF'
ARCHIVE='pw01skl00OBSERVED/AB'
CALENDAR="doAction('/JRADB/accessS.html','"+ENTRY+"') doAction('/JRADB/accessS.html','"+ARCHIVE+"')"
DAY_HTML=RACE+' pw01sde01'+KEY+'1220261025/AA'


def result_body(*,date='2026年10月25日（日曜）',meeting='4回新潟4日',race='11レース'):
    rows=''.join('<tr><td>'+str(i)+'</td><td>'+str(n)+'</td><td>馬'+str(n)+'</td><td>1 2</td></tr>'
                 for i,n in enumerate([4,8,3],1))
    return ('<html>'+date+' '+meeting+' '+race+
            ' 発走時刻：15時20分 天候 晴 芝 良 コース：1,200 メートル （芝・左）'
            '<table><tr><th>着順</th><th>馬番</th><th>馬名</th><th>コーナー通過順位</th></tr>'+rows+'</table>'
            ' 払戻金 単勝 4 200 円 馬単 4-8 400 円 3連複 3-4-8 500 円 3連単 4-8-3 600 円 勝馬の紹介</html>')


class Response:
    def __init__(self,url,body,*,cookie=False):
        self.url=url;self.data=io.BytesIO(body.encode());self.status=200
        self.headers=Message();self.headers['content-type']='text/html; charset=UTF-8'
        self.headers['Date']='Wed, 28 Oct 2026 00:00:00 GMT'
        if cookie:self.headers['Set-Cookie']='MOCK_SESSION=retained; Path=/; Secure'
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def geturl(self):return self.url
    def info(self):return self.headers
    def read1(self,n):return self.data.read(n)


def install(monkeypatch, responses):
    calls=[];processors=[]
    class Opener:
        def __init__(self,*handlers):
            processors.extend(handlers)
            self.jar=next(h.cookiejar for h in handlers if isinstance(h,urllib.request.HTTPCookieProcessor))
        def open(self,request,timeout):
            self.jar.add_cookie_header(request)
            body=request.data.decode() if request.data else None
            calls.append({'url':request.full_url,'method':request.get_method(),'body':body,
                          'referer':request.get_header('Referer'),'cookie':request.get_header('Cookie'),
                          'ua':request.get_header('User-agent')})
            value=responses[len(calls)-1]
            if isinstance(value,BaseException):raise value
            out=Response(request.full_url,value,cookie=len(calls)==1)
            self.jar.extract_cookies(out,request)
            return out
    monkeypatch.setattr(harvest.urllib.request,'build_opener',lambda *handlers:Opener(*handlers))
    monkeypatch.setattr(harvest.time,'sleep',lambda _:None)
    return calls,processors


def test_t2_current_result_endpoint_cookie_referer_and_raw_identity(monkeypatch):
    calls,handlers=install(monkeypatch,[CALENDAR,DAY,DAY_HTML,result_body()])
    out=candidate.fetch_jra_result(DATE,KEY,11)
    assert len(calls)==4 and len([h for h in handlers if isinstance(h,urllib.request.HTTPCookieProcessor)])==1
    assert calls[0]['method']=='GET' and calls[0]['referer'] is None
    for i,token in enumerate([ENTRY,DAY,RACE],1):
        assert calls[i]['url']=='https://www.jra.go.jp/JRADB/accessS.html'
        assert calls[i]['method']=='POST'
        assert urllib.parse.parse_qs(calls[i]['body'])=={'cname':[token]}
        assert calls[i]['referer']==calls[i-1]['url']
        assert calls[i]['cookie']=='MOCK_SESSION=retained'
        assert calls[i]['ua']==harvest.UA
    raw=base64.b64decode(out['raw_base64'])
    assert hashlib.sha256(raw).hexdigest()==out['sha256']
    assert out['identity']=={'race_date':DATE,'meeting_key':KEY,'venue':'新潟','meeting_no':4,'meeting_day':4,'race_no':11}
    assert out['parsed']['runner_count']==3
    assert [x['stage'] for x in out['navigation']]==['RESULT_CALENDAR','RESULT_ENTRY','RESULT_DAY','RESULT_DETAIL']


def archive_form():
    return ('<select name="kaisaiY_list"><option value="2026">2026</option></select>'
            '<select name="kaisaiM_list"><option value="10">10</option></select>'
            'var yearMonth = "202611"; objParam["2610"]="BC";'
            'pw01skl00 pw01skl10 Number(arg) >= yearMonth objParam[String(arg).substring(2,6)]')


def test_t3_archive_uses_only_observed_form_checksum_and_same_session(monkeypatch):
    calls,_=install(monkeypatch,[CALENDAR,'pw01srl00052026040320261031/AA',archive_form(),DAY,DAY_HTML,result_body()])
    out=candidate.fetch_jra_result(DATE,KEY,11)
    assert len(calls)==6
    assert [urllib.parse.parse_qs(x['body'])['cname'][0] for x in calls[1:]]==[
        ENTRY,ARCHIVE,'pw01skl10202610/BC',DAY,RACE]
    assert out['identity']['meeting_key']==KEY
    assert all(x['cookie']=='MOCK_SESSION=retained' for x in calls[1:])


@pytest.mark.parametrize('body',[
    '<html>Service unavailable</html>',
    result_body(date='2026年10月24日（土曜）'),
    result_body(meeting='4回東京4日'),
    result_body(meeting='3回新潟4日'),
    result_body(meeting='4回新潟3日'),
    result_body(race='12レース'),
    result_body(race='12レース')+RACE,  # even the expected token cannot override printed identity
])
def test_t4_t6_unrelated_or_other_result_body_never_accepted(monkeypatch,body):
    calls,_=install(monkeypatch,[CALENDAR,DAY,DAY_HTML,body])
    with pytest.raises(result.OfficialResultNavigationError,match='PRINTED_IDENTITY'):
        candidate.fetch_jra_result(DATE,KEY,11)
    assert len(calls)==4


def test_t5_403_stops_without_retries_or_archive_bypass(monkeypatch):
    denied=urllib.error.HTTPError('https://www.jra.go.jp/keiba/calendar2026/2026/10/1025.html',403,'Forbidden',{},None)
    calls,_=install(monkeypatch,[denied])
    with pytest.raises(urllib.error.HTTPError) as caught:candidate.fetch_jra_result(DATE,KEY,11)
    assert caught.value.code==403 and caught.value.first_failed_stage=='RESULT_CALENDAR'
    assert len(calls)==1


@pytest.mark.parametrize('responses,code',[
    (['<html>Unknown calendar layout</html>'],'ENTRY_TOKEN_NOT_OBSERVED'),
    (["doAction('/JRADB/accessS.html','"+ENTRY+"')",'<html>Unknown listing</html>'],'ARCHIVE_SELECTION_REQUIRED'),
    ([CALENDAR,'<html>Unknown listing</html>','<html>Unknown form</html>'],'ARCHIVE_FORM_NOT_OBSERVED'),
    ([CALENDAR,'<html>Unknown listing</html>',archive_form(),'<html>Unknown archive listing</html>'],'DAY_TOKEN_NOT_OBSERVED'),
    ([CALENDAR,'pw01srl00052026040320261025/AA'],'MEETING_KEY_MISMATCH'),
    ([CALENDAR,DAY,'<html>Unknown day body</html>'],'DAY_HTML_UNRECOGNIZED'),
])
def test_navigation_causes_are_distinct_without_unobserved_raw_claims(monkeypatch,responses,code):
    calls,_=install(monkeypatch,responses)
    with pytest.raises(result.OfficialResultNavigationError,match=code) as caught:
        candidate.fetch_jra_result(DATE,KEY,11)
    assert caught.value.error_code.startswith('JRA_RESULT_')
    assert len(calls)==len(responses)


def test_t7_same_session_can_capture_two_requested_races_without_reopening_day(monkeypatch):
    calls,_=install(monkeypatch,[CALENDAR,DAY,DAY_HTML,result_body(),result_body(race='12レース')])
    session=result._open_day(DATE,KEY)
    first=candidate.fetch_jra_result(DATE,KEY,11,session=session)
    second=candidate.fetch_jra_result(DATE,KEY,12,session=session)
    assert first['identity']['race_no']==11 and second['identity']['race_no']==12
    assert len(calls)==5
    with pytest.raises(result.OfficialResultNavigationError,match='SESSION_TARGET'):
        candidate.fetch_jra_result('2026-10-24',KEY,11,session=session)
    assert len(calls)==5


def test_result_not_published_is_pending_only_after_valid_day_navigation(monkeypatch):
    calls,_=install(monkeypatch,[CALENDAR,DAY,DAY_HTML])
    with pytest.raises(candidate.PendingOfficialResult) as caught:
        candidate.fetch_jra_result(DATE,KEY,10)
    assert caught.value.first_failed_stage=='RESULT_RACE_SELECTION' and len(calls)==3


def test_raw_observation_reuses_original_time_and_refuses_corruption(tmp_path,monkeypatch):
    install(monkeypatch,[CALENDAR,DAY,DAY_HTML,result_body()])
    evidence=candidate.fetch_jra_result(DATE,KEY,11)
    rid='KM-JRA-NGT-20261025-R11';path=tmp_path/'official_result_observation.json'
    first=candidate.persist_official_result_observation(path,rid,evidence)
    original=path.read_bytes();second=copy.deepcopy(evidence);second['captured_at']='2099-01-01T00:00:00Z'
    assert candidate.persist_official_result_observation(path,rid,second)==first
    assert path.read_bytes()==original
    bad=copy.deepcopy(evidence);bad['raw_base64']=base64.b64encode(b'other').decode()
    with pytest.raises(ValueError,match='RAW_SHA_MISMATCH'):
        candidate.persist_official_result_observation(path,rid,bad)
    with pytest.raises(ValueError,match='CAPTURE_RACE_MISMATCH'):
        candidate.build_official_result_observation('KM-JRA-NGT-20261025-R12',evidence)
    bad=copy.deepcopy(evidence);bad['identity']['meeting_no']=3
    with pytest.raises(ValueError,match='RAW_IDENTITY_BINDING'):
        candidate.build_official_result_observation(rid,bad)
    bad=copy.deepcopy(evidence);bad['url']='https://unapproved.example/RESULT'
    with pytest.raises(ValueError,match='CAPTURE_ENDPOINT_INVALID'):
        candidate.build_official_result_observation(rid,bad)
    assert path.read_bytes()==original


def test_full_runner_universe_and_strict_positive_payouts():
    raw=result_body().encode()
    parsed=result.parse_result_detail(raw,'text/html; charset=UTF-8')
    with pytest.raises(ValueError,match='RUNNER_UNIVERSE'):
        candidate.verify_official_result(parsed,'払戻金 単勝 4 200 円 馬単 4-8 400 円 3連複 3-4-8 500 円 3連単 4-8-3 600 円',['3','4','8','9'])
    official={'top3':[4,8,3],'payouts':{'EXACTA':{'selection':[4,8],'per_100_yen':0}}}
    with pytest.raises(ValueError,match='OFFICIAL_PAYOUT_INVALID'):
        candidate.official_payout_entries(official,'EXACTA')


def test_existing_candidate_bundle_is_not_already_settled_if_partial_or_corrupt(tmp_path):
    rid='KM-JRA-NGT-20261025-R11'
    folder=tmp_path/'runtime/source_candidate_oos'/rid;folder.mkdir(parents=True)
    settlement={'race_id':rid,'official_result_source_sha256':'RAW'}
    settlement['sha256']=candidate.canonical_sha(settlement)
    evaluation={'race_id':rid,'settlement_sha256':settlement['sha256']}
    evaluation['sha256']=candidate.canonical_sha(evaluation)
    learning={'race_id':rid,'settlement_sha256':settlement['sha256']}
    learning['sha256']=candidate.canonical_sha(learning)
    observation={'race_id':rid,'raw_sha256':'RAW'}  # legacy metadata is preserved
    for name,value in [('result_evaluation',evaluation),('settlement',settlement),('learning',learning)]:
        (folder/(name+'.json')).write_text(json.dumps(value))
    with pytest.raises(ValueError,match='BUNDLE_INCOMPLETE'):
        candidate.process(tmp_path,rid)
    (folder/'official_result_observation.json').write_text(json.dumps(observation))
    original={p:p.read_bytes() for p in folder.iterdir()}
    assert candidate.process(tmp_path,rid)=='ALREADY_SETTLED'
    assert original=={p:p.read_bytes() for p in original}
    learning['settlement_sha256']='OTHER'
    (folder/'learning.json').write_text(json.dumps(learning))
    with pytest.raises(ValueError,match='BUNDLE_SHA_MISMATCH'):
        candidate.process(tmp_path,rid)


@pytest.mark.parametrize('rn',[11,12])
def test_observed_payout_header_dom_is_identity_positive_not_http_raw(rn):
    from bs4 import BeautifulSoup
    fixture=json.loads((ROOT/'tests/fixtures/jra_20261025_ngt1112_payout_rendered_dom.json').read_text())
    row=next(r for r in fixture['races'] if r['id']==f'harai_{rn}R')
    raw=row['html'].encode()
    identity=result.validate_result_identity(raw,'text/html; charset=UTF-8',KEY,'20261025',rn)
    assert identity['race_no']==rn and identity['meeting_key']==KEY
    assert 'raw_http_bytes' not in identity  # DOM regression never claims live/raw provenance
    soup=BeautifulSoup(row['html'],'html.parser')
    soup.select_one('.race_number img')['alt']=f'{12 if rn==11 else 11}レース'
    # Correct target number elsewhere on the same page cannot override header.
    soup.append(BeautifulSoup(f'<p>{rn}レース {RACE}</p>','html.parser'))
    with pytest.raises(result.OfficialResultNavigationError,match='PRINTED_IDENTITY_MISMATCH'):
        result.validate_result_identity(str(soup).encode(),'text/html; charset=UTF-8',KEY,'20261025',rn)


def test_result_timestamp_is_body_completion_not_before_request(monkeypatch):
    install(monkeypatch,[CALENDAR,DAY,DAY_HTML,result_body()])
    class Clock(harvest._dt.datetime):
        @classmethod
        def now(cls,tz=None):return cls(2026,10,28,0,0,30,tzinfo=tz)
    monkeypatch.setattr(harvest._dt,'datetime',Clock)
    monkeypatch.setattr(candidate,'utcnow',lambda:'2026-10-28T00:00:00Z')
    out=candidate.fetch_jra_result(DATE,KEY,11)
    assert out['captured_at']=='2026-10-28T00:00:30+00:00'


def test_package_runtime_import_does_not_require_source_directory_on_sys_path():
    import os
    import subprocess
    code='''
import sys,urllib.error
sys.path.insert(0,sys.argv[1]+'/runtime')
from jra_source_runtime import jra_same_day_results as r,jra_pedigree_harvest as h
class Client:
    def __init__(self,**kwargs):self.last_response={}
    def get(self,path):raise urllib.error.HTTPError('https://www.jra.go.jp'+path,403,'Mock refusal',{},None)
    def post(self,*args):raise AssertionError('MUST_NOT_POST')
h._Client=Client
try:r._open_day('2026-10-25','0420260404')
except urllib.error.HTTPError as exc:assert exc.code==403
else:raise AssertionError('MUST_STOP')
identity=r.validate_result_identity(('2026年10月25日（日曜）4回新潟4日 11レース<table></table>').encode(),'text/html; charset=UTF-8','0420260404','20261025',11)
assert identity['race_no']==11
'''
    env={k:v for k,v in os.environ.items() if k not in {'PYTHONPATH','GH_TOKEN','GITHUB_TOKEN'}}
    out=subprocess.run([sys.executable,'-P','-c',code,str(ROOT)],env=env,text=True,capture_output=True,timeout=20)
    assert out.returncode==0,out.stdout+out.stderr


def test_legacy_identity_after_uppercase_result_table_cannot_be_borrowed():
    raw=('<TABLE><tr><td>other result</td></tr></TABLE>'
         '<p>2026年10月25日（日曜）4回新潟4日 11レース</p>').encode()
    with pytest.raises(result.OfficialResultNavigationError,match='IDENTITY_NOT_OBSERVED'):
        result.validate_result_identity(raw,'text/html; charset=UTF-8',KEY,'20261025',11)


@pytest.mark.parametrize('mutation',[
    {'race_date':'2026-10-24'},
    {'race_no':12},
    {'race_no':11.5},
    {'jra_source':{'jra_meeting_key':'0520260404'}},
    {'race_date':'2025-10-25','jra_source':{'jra_meeting_key':'0420250404'}},
])
def test_candidate_intent_cannot_route_frozen_id_to_another_result_before_http(tmp_path,monkeypatch,mutation):
    rid='KM-JRA-NGT-20261025-R11'
    folder=tmp_path/'runtime/source_candidate_oos'/rid;folder.mkdir(parents=True)
    pre={'race_id':rid,'source_snapshot_sha256':'MOCK_SOURCE','oos_eligible':True,
         'candidate_final_verified':True,'candidate_final_receipt_sha256':'MOCK_RECEIPT',
         'candidate_final_receipt_timestamp':'2026-10-25T05:00:00Z',
         'scheduled_post_at':'2026-10-25T15:20:00+09:00'}
    pre['sha256']=candidate.canonical_sha(pre)
    final={'race_id':rid,'source_snapshot_sha256':'MOCK_SOURCE','candidate_only':True,
           'production_effect':'NONE','final_receipt':{'receipt_sha256':'MOCK_RECEIPT'}}
    final['sha256']=candidate.canonical_sha(final)
    (folder/'pre_result.json').write_text(json.dumps(pre));(folder/'candidate_final.json').write_text(json.dumps(final))
    intents=tmp_path/'runtime/jra_formal_intents';intents.mkdir()
    intent={'race_id':rid,'race_date':DATE,'venue_id':'NGT','race_no':11,'jra_source':{'jra_meeting_key':KEY}}
    intent.update(mutation);(intents/(rid+'-LIVE-R1.json')).write_text(json.dumps(intent))
    import subprocess
    monkeypatch.setattr(subprocess,'check_output',lambda *a,**k:'2026-10-24T00:00:00Z')
    monkeypatch.setattr(candidate,'fetch_jra_result',lambda *a,**k:pytest.fail('MUST_NOT_FETCH_OTHER_RESULT'))
    before={p:p.read_bytes() for p in folder.iterdir()}
    with pytest.raises(ValueError,match='RESULT_TARGET_(RACE_ID_MISMATCH|REFERENCE_INVALID)'):
        candidate.process(tmp_path,rid)
    assert before=={p:p.read_bytes() for p in folder.iterdir()}


def test_shared_result_target_is_canonical_and_does_not_complete_a_clock():
    target=candidate.validate_result_target('KM-JRA-NGT-20261025-R11',DATE,KEY,11)
    assert target['meeting_no']==4 and target['meeting_day']==4
    assert not set(target)&{'scheduled_post_at','prediction_cutoff','effective_time'}
    for number in [True,0,13,'11',11.5]:
        with pytest.raises(ValueError,match='REFERENCE_INVALID'):
            candidate.validate_result_target('KM-JRA-NGT-20261025-R11',DATE,KEY,number)

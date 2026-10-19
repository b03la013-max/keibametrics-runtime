"""Authored synthetic provider pages; no original website HTML or live HTTP."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime,timedelta
import gzip
import hashlib
import json
from pathlib import Path
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

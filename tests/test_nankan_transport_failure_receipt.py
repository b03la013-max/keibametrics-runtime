"""Offline negative tests; exceptions and pages are authored, not live traffic."""
from datetime import datetime,timedelta,timezone
import json
from pathlib import Path
import socket
import ssl
import urllib.error
import pytest

from runtime import urw_nankan_reference_source as n

NOW=datetime(2026,10,27,2,0,tzinfo=timezone.utc)

class Clock:
    def __init__(self):self.tick=0.;self.sleeps=[]
    def __call__(self):return self.tick
    def sleep(self,delay):self.sleeps.append(delay);self.tick+=delay
    def now(self):return NOW+timedelta(seconds=self.tick)

class Response:
    status=200
    def __init__(self,url,raw=b'<html>authored</html>',kind='text/html'):
        self.url=url;self.raw=raw;self.headers={'Content-Type':kind}
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def geturl(self):return self.url
    def read(self,count):return self.raw[:count]

class Opener:
    def __init__(self,clock,robots=None,data=None):
        self.clock=clock;self.robots=list(robots or []);self.data=list(data or []);self.calls=[]
    def open(self,request,timeout):
        self.calls.append((self.clock(),request.full_url,dict(request.header_items()),timeout,request.get_method()))
        seq=self.robots if request.full_url==n.ROBOTS else self.data
        if seq:
            answer=seq.pop(0)
            if isinstance(answer,BaseException):raise answer
            return answer
        if request.full_url==n.ROBOTS:raise urllib.error.HTTPError(n.ROBOTS,404,'authored',{},None)
        return Response(request.full_url)

def dns():return urllib.error.URLError(socket.gaierror(-3,'Temporary failure in name resolution'))
def tls():return urllib.error.URLError(ssl.SSLCertVerificationError(1,'certificate verify failed'))

def client(tmp_path,robots=None,data=None,mod=n):
    clock=Clock();opener=Opener(clock,robots,data)
    return mod.Client(cache=tmp_path/'cache',opener=opener,clock=clock,sleep=clock.sleep,now=clock.now),clock,opener

def failed(c):
    with pytest.raises(n.NankanError) as got:c.get(n.CALENDAR)
    return got.value


@pytest.mark.parametrize('error,classification,leaf',[
    (dns(),'DNS_ERROR','gaierror'),(tls(),'TLS_ERROR','SSLCertVerificationError'),
    (urllib.error.HTTPError(n.ROBOTS,403,'authored',{},None),'HTTP_ERROR','HTTPError'),
    (urllib.error.HTTPError(n.ROBOTS,503,'authored',{},None),'HTTP_ERROR','HTTPError'),
    (n.ObservedRedirect(n.ROBOTS,n.ORIGIN+'/elsewhere',302),'REDIRECT_CONFLICT','ObservedRedirect'),
])
def test_robots_first_failure_remains_exact_in_cached_rethrow(tmp_path,error,classification,leaf):
    c,clock,opener=client(tmp_path,[error])
    one=failed(c);clock.tick+=2;two=failed(c)
    a=one.receipt['failure_observation'];b=two.receipt['failure_observation']
    assert a==b and a['classification']==classification and a['leaf_exception_type']==leaf
    assert a['url']==n.ROBOTS and a['phase']=='ROBOTS' and a['observed_at']==NOW.isoformat()
    assert one.receipt['cached_failure'] is False and two.receipt['cached_failure'] is True
    assert two.__cause__ is None
    assert len(opener.calls)==1
    state=json.loads((tmp_path/'cache/robots.json').read_text())
    assert state['next_at']==10 and state['expires_at']==30

def test_first_and_latest_failure_are_separate_without_automatic_retry(tmp_path):
    c,clock,opener=client(tmp_path,[dns(),tls()])
    first=failed(c);assert len(opener.calls)==1
    clock.tick=31
    second=failed(c)
    assert len(opener.calls)==2
    assert second.receipt['failure_observation']==first.receipt['failure_observation']
    assert second.receipt['last_failure_observation']['classification']=='TLS_ERROR'
    assert second.receipt['last_failure_observation']['observed_at']==(NOW+timedelta(seconds=31)).isoformat()

def test_legacy_cached_failure_does_not_invent_missing_first_cause(tmp_path):
    c,clock,opener=client(tmp_path)
    c.cache.mkdir()
    (c.cache/'robots.json').write_text(json.dumps({'failure':'SOURCE_POLICY_ROBOTS_UNKNOWN','expires_at':30,'next_at':10}))
    error=failed(c)
    assert error.receipt['cached_failure'] is True
    assert error.receipt['failure_observation'] is None
    assert error.receipt['last_failure_observation'] is None
    assert opener.calls==[]

def test_expired_legacy_failure_does_not_relabel_new_cause_as_the_unknown_first(tmp_path):
    c,clock,opener=client(tmp_path,[dns()])
    c.cache.mkdir()
    (c.cache/'robots.json').write_text(json.dumps({'failure':'SOURCE_POLICY_ROBOTS_UNKNOWN','expires_at':30,'next_at':10}))
    clock.tick=31;error=failed(c)
    assert error.receipt['failure_observation'] is None
    assert error.receipt['last_failure_observation']['classification']=='DNS_ERROR'
    assert error.receipt['last_failure_observation']['observed_at']==(NOW+timedelta(seconds=31)).isoformat()
    assert len(opener.calls)==1

def test_robots_404_success_clears_failed_observation_and_keeps_300_second_ttl(tmp_path):
    c,clock,opener=client(tmp_path,[dns(),urllib.error.HTTPError(n.ROBOTS,404,'authored',{},None)])
    failed(c);clock.tick=31
    receipt,raw=c.get(n.CALENDAR)
    state=json.loads((c.cache/'robots.json').read_text())
    assert state['expires_at']==331
    assert all(k not in state for k in ('failure','failure_observation','last_failure_observation'))
    assert receipt['source_policy']['classification']=='ROBOTS_ABSENT_HTTP_404_NOT_DENIAL'
    assert not receipt['formal_source_claim'] and not receipt['production_authority']
    assert opener.calls[-1][0]-opener.calls[-2][0]==10

@pytest.mark.parametrize('error,classification',[(dns(),'DNS_ERROR'),(tls(),'TLS_ERROR'),
    (urllib.error.HTTPError(n.CALENDAR,403,'authored',{},None),'HTTP_ERROR')])
def test_data_network_exception_keeps_original_type_and_observation(tmp_path,error,classification):
    c,clock,opener=client(tmp_path,data=[error])
    with pytest.raises(type(error)) as got:c.get(n.CALENDAR)
    assert got.value is error
    observation=error.receipt['failure_observation']
    assert observation['classification']==classification and observation['url']==n.CALENDAR
    assert observation['phase']=='DATA_GET' and observation['observed_at']==(NOW+timedelta(seconds=10)).isoformat()
    assert not error.receipt['formal_source_claim'] and not error.receipt['public_redistribution_authorized']
    assert len(opener.calls)==2

def test_data_redirect_not_followed_and_receipt_classified(tmp_path):
    redir=n.ObservedRedirect(n.CALENDAR,'https://unapproved.invalid/private?token=authored',302)
    c,clock,opener=client(tmp_path,data=[redir])
    with pytest.raises(n.ObservedRedirect) as got:c.get(n.CALENDAR)
    assert got.value is redir and len(opener.calls)==2
    assert redir.receipt['failure_observation']['classification']=='REDIRECT_CONFLICT'
    assert redir.receipt['location']=='https://unapproved.invalid/private?token=authored'
    assert not redir.receipt['production_authority']

def test_retry_after_is_unchanged_and_never_immediate_internal_retry(tmp_path):
    error=urllib.error.HTTPError(n.ROBOTS,503,'authored',{'Retry-After':'90'},None)
    c,clock,opener=client(tmp_path,[error]);first=failed(c)
    state=json.loads((c.cache/'robots.json').read_text())
    assert state['next_at']==state['expires_at']==90
    clock.tick=45;two=failed(c)
    assert two.receipt['cached_failure'] and first.receipt['failure_observation']==two.receipt['failure_observation']
    assert len(opener.calls)==1

def test_user_agent_scope_and_headers_unchanged(tmp_path):
    c,clock,opener=client(tmp_path)
    c.get(n.CALENDAR)
    for _,url,headers,timeout,method in opener.calls:
        assert headers['User-agent']==n.USER_AGENT and method=='GET' and timeout==15
        assert headers['Accept-encoding']=='identity'
    with pytest.raises(n.NankanError,match='URL_SCOPE'):c.get(n.ORIGIN+'/blood/1.do')
    with pytest.raises(n.NankanError,match='URL_SCOPE'):c.get('https://unapproved.invalid/calendar/000000.do')
    assert len(opener.calls)==2

def test_robots_denial_still_stops_before_data(tmp_path):
    c,clock,opener=client(tmp_path,[Response(n.ROBOTS,b'User-agent: *\nDisallow: /\n','text/plain')])
    with pytest.raises(n.NankanError,match='ROBOTS_DISALLOWED'):c.get(n.CALENDAR)
    assert len(opener.calls)==1


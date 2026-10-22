"""Private, unsigned URW reference from observed NANKAN official links.

Separate provider evidence; never a NAR SOURCE, Static, KRS, ticket or FINAL.
Original HTML/history tables and the derived full answer stay outside Git.
No automatic HTTP redirect following: only one observed syousai -> uma_shosai
302 with exactly the same provider Race ID is separately checked and requested.
"""
from __future__ import annotations
import argparse
from datetime import date, datetime, timedelta, timezone
import fcntl
import gzip
import hashlib
from html.parser import HTMLParser
import inspect
import json
import math
import os
from pathlib import Path
import re
import tempfile
import time
import unicodedata
import urllib.error
from urllib.parse import urljoin, urlsplit
import urllib.request

from runtime.urw_reference_source_policy import USER_AGENT, robots_decision, _retry_at

ORIGIN='https://www.nankankeiba.com'
CALENDAR=ORIGIN+'/calendar/000000.do'
ROBOTS=ORIGIN+'/robots.txt'
TERMS=ORIGIN+'/info/usage/'
JST=timezone(timedelta(hours=9))
PROFILE='KM-URW-NANKAN-PRIVATE-REFERENCE-v1'
PROVIDER='NANKAN_OFFICIAL'
MAX_BYTES=1500000


def sha(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def utcnow():return datetime.now(timezone.utc)
def norm(value):return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',str(value))).strip()


class NankanError(ValueError):
    def __init__(self,code,**receipt):
        self.receipt={'code':code,**receipt};super().__init__(code)


class ObservedRedirect(NankanError):
    def __init__(self,source,location,status):
        super().__init__('NANKAN_OBSERVED_REDIRECT',source_url=source,location=location,http_status=status)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        raise ObservedRedirect(req.full_url,newurl,code)


def url_scope(url):
    p=urlsplit(url)
    if (p.scheme!='https' or p.netloc!='www.nankankeiba.com' or p.query or p.fragment
            or not re.fullmatch(r'/(?:calendar/\d{6}|program/\d{14}|(?:syousai|uma_shosai|result)/\d{16}'
                r'|odds/\d{8}18\d{4}(?:0[1-9]|1[0-2])01|henko_info/00000000000000)\.do|/robots\.txt',p.path)):
        raise NankanError('NANKAN_URL_SCOPE_HOLD')
    return p


def private_directory(folder):
    path=Path(folder)
    if not path.is_absolute():raise NankanError('NANKAN_PRIVATE_ABSOLUTE_OUTPUT_REQUIRED')
    if '..' in path.parts:raise NankanError('NANKAN_PRIVATE_PARENT_PATH_FORBIDDEN')
    for ancestor in [path,*path.parents]:
        if ancestor.is_symlink():raise NankanError('NANKAN_PRIVATE_SYMLINK_OUTPUT_FORBIDDEN')
        if (ancestor/'.git').exists():raise NankanError('NANKAN_PRIVATE_OUTPUT_INSIDE_GIT_FORBIDDEN')
    if any(part in {'public','dist','local_reference','local_reference_delivery','.github'} for part in path.parts):
        raise NankanError('NANKAN_PUBLIC_OUTPUT_FORBIDDEN')
    path.mkdir(parents=True,exist_ok=True,mode=0o700)
    if any(ancestor.is_symlink() or (ancestor/'.git').exists() for ancestor in [path,*path.parents]):
        raise NankanError('NANKAN_PRIVATE_OUTPUT_CHANGED_DURING_CREATION')
    if path.stat().st_mode & 0o077:raise NankanError('NANKAN_OUTPUT_PERMISSIONS_NOT_PRIVATE')
    return path


def immutable(path,raw):
    if path.is_symlink():raise NankanError('NANKAN_PRIVATE_SYMLINK_OUTPUT_FORBIDDEN')
    if path.exists():
        if path.read_bytes()!=raw:raise NankanError('NANKAN_PRIVATE_IMMUTABLE_CONFLICT')
        return
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as stream:stream.write(raw)


def save_json(path,obj):immutable(path,(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode())


def private_lock(path):
    if path.is_symlink():raise NankanError('NANKAN_PRIVATE_SYMLINK_OUTPUT_FORBIDDEN')
    return os.fdopen(os.open(path,os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600),'a')


def reference_metadata(meta):
    flags=('formal_source_claim','signed_source_claim','production_authority','public_redistribution_authorized')
    if (meta.get('provider',PROVIDER)!=PROVIDER or meta.get('source_authority',PROVIDER)!=PROVIDER
            or any(meta.get(key,False) is not False for key in flags)):
        raise NankanError('NANKAN_SOURCE_PROVIDER_OR_AUTHORITY_HOLD')
    return {**meta,'provider':PROVIDER,'source_authority':PROVIDER,**{key:False for key in flags}}


def build_unsigned_source_snapshot(raw,race,card_receipt,*,race_id):
    """Prepare existing SOURCE-schema bytes without admitting a new consumer.

    This optional repository adapter makes no HTTP request and never signs.
    The standalone reference CLI does not import the physical Runtime. NANKAN
    identity and private-use limits survive the conversion; formal_ready stays
    false until the separately reviewed provider/Runtime admission exists.
    """
    from runtime.local_physical.source_acquisition import (
        snapshot_from_bytes,_merge_evidence,sha_obj,SOURCE_PROFILE,SOURCE_SCHEMA)
    meta=reference_metadata(card_receipt)
    if race.get('provider')!=PROVIDER or race.get('venue_id')!='URW':
        raise NankanError('NANKAN_UNSIGNED_RACE_PROVIDER_OR_VENUE')
    number=race.get('race_no')
    day=str(race.get('race_date','')).replace('-','')
    if (type(number) is not int or not 1<=number<=12 or len(day)!=8
            or not re.fullmatch(re.escape(day)+r'18\d{4}'+f'{number:02d}',str(race.get('provider_race_id','')))):
        raise NankanError('NANKAN_UNSIGNED_PROVIDER_RACE_IDENTITY')
    if (not str(race_id).strip() or meta.get('http_status')!=200
            or hashlib.sha256(raw).hexdigest()!=meta.get('raw_sha256')):
        raise NankanError('NANKAN_UNSIGNED_SNAPSHOT_IDENTITY_OR_RAW_HASH')
    policy=meta.get('source_policy') or {}
    if policy.get('usage_scope')!='USER_PERSONAL_NONCOMMERCIAL_PRIVATE_ONLY_NOT_PUBLIC_REDISTRIBUTION':
        raise NankanError('NANKAN_UNSIGNED_PRIVATE_SCOPE_REQUIRED')
    try:
        observed=datetime.fromisoformat(str(meta['fetched_at']).replace('Z','+00:00'))
        cutoff=datetime.fromisoformat(race['prediction_cutoff'])
        if observed.tzinfo is None or cutoff.tzinfo is None or observed>=cutoff or observed>utcnow():
            raise ValueError('PRESTART_OBSERVATION_REQUIRED')
    except (KeyError,ValueError,TypeError) as exc:
        raise NankanError('NANKAN_UNSIGNED_OBSERVATION_TIME') from exc
    runners=parse_card(raw,race,meta['url'])
    verify_history_asof(runners,meta['fetched_at'])
    spec={'source_id':'NANKAN-CARD:'+race['provider_race_id'],'url':meta['url'],
        'source_class':'OFFICIAL_RACE_CARD_CURRENT_STATE_BODY_WEIGHT',
        'authority':PROVIDER,'priority':100,'official':True,'required':True,
        'extract':[{'field':'raw_identity','type':'meta','name':'raw_sha256','required':True}]}
    snap,errors=snapshot_from_bytes(spec,raw,final_url=meta['url'],status_code=200,
        fetched_at=meta['fetched_at'],prediction_cutoff=race['prediction_cutoff'],
        headers={'content-type':'text/html'})
    if errors:raise NankanError('NANKAN_UNSIGNED_SNAPSHOT_EXTRACTION',errors=errors)
    snap['source_access_policy']=policy
    snap['snapshot_sha256']=sha_obj({k:v for k,v in snap.items() if k!='snapshot_sha256'})
    normalized,conflicts,errors=_merge_evidence([snap])
    if errors:raise NankanError('NANKAN_UNSIGNED_SNAPSHOT_MERGE',errors=errors)
    bundle=[{k:snap[k] for k in ('source_id','raw_sha256','snapshot_sha256','fetched_at','final_url')}]
    out={'schema':SOURCE_SCHEMA,'profile':SOURCE_PROFILE,'provider':PROVIDER,
        'race_id':str(race_id),'source_race_context':{k:race[k] for k in ('venue_id','race_date','race_no')},
        'prediction_cutoff':race['prediction_cutoff'],'scheduled_post_at':race['scheduled_post_at'],
        'source_freeze_at':utcnow().isoformat(),'required_source_manifest':[spec],
        'required_source_manifest_sha256':sha_obj([spec]),'sources':[snap],
        'raw_source_bundle_sha256':sha_obj(bundle),'normalized_evidence':normalized,
        'normalized_evidence_sha256':sha_obj(normalized),'conflicts':conflicts,
        'missing_required_sources':[],'stale_sources':[],'post_cutoff_sources':[],
        'parsed_nankan_facts':runners,'formal_ready':False,'errors':[],
        'active_verified':False,'formal_source_claim':False,'signed_source_claim':False,
        'production_authority':False,'public_redistribution_authorized':False}
    out['source_snapshot_sha256']=sha_obj(out)
    return out


class Client:
    """Same-origin robots, process-shared interval, no retry/credential/proxy changes."""
    def __init__(self,*,cache=None,opener=None,clock=time.time,sleep=time.sleep,now=utcnow):
        self.cache=Path(cache or (Path(tempfile.gettempdir())/f'km-nankan-policy-{os.getuid()}'))
        self.opener=opener or urllib.request.build_opener(NoRedirect())
        self.clock=clock;self.sleep=sleep;self.now=now

    def _wait(self,state):
        wait=max(0,state.get('next_at',0)-self.clock())
        if wait>30:raise NankanError('SOURCE_POLICY_RETRY_NOT_READY',retry_after_seconds=wait)
        if wait:self.sleep(wait)
        if self.clock()+.001<state.get('next_at',0):raise NankanError('SOURCE_POLICY_RETRY_NOT_READY')

    def get(self,url):
        url_scope(url)
        self.cache.mkdir(parents=True,exist_ok=True,mode=0o700)
        with (self.cache/'lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            cache=self.cache/'robots.json'
            try:
                state=json.loads(cache.read_text()) if cache.exists() else {}
                if not isinstance(state,dict):raise ValueError('CACHE_TYPE')
                if any(type(state[key]) not in (int,float) or not math.isfinite(state[key])
                       for key in ('next_at','expires_at','robots_fetched_clock') if key in state):raise ValueError('CACHE_CLOCK')
                if state.get('robots_status')==200 and (not isinstance(state.get('text'),str)
                    or hashlib.sha256(state['text'].encode()).hexdigest()!=state.get('text_sha256')):raise ValueError('CACHE_HASH')
                if state.get('robots_status')==404 and state.get('text') is not None:raise ValueError('CACHE_404_BODY')
            except (OSError,ValueError) as exc:raise NankanError('SOURCE_POLICY_ROBOTS_UNKNOWN') from exc
            def persist():cache.write_text(json.dumps(state,sort_keys=True)+'\n')
            if self.clock()>=state.get('expires_at',0):
                self._wait(state);state['next_at']=self.clock()+10
                req=urllib.request.Request(ROBOTS,headers={'User-Agent':USER_AGENT,'Accept':'text/plain','Accept-Encoding':'identity'},method='GET')
                try:
                    with self.opener.open(req,timeout=15) as response:
                        if response.geturl()!=ROBOTS or response.status!=200:raise ValueError('ROBOTS_RESPONSE')
                        headers={k.lower():v for k,v in response.headers.items()}
                        if headers.get('content-type','').split(';')[0].strip().lower()!='text/plain':raise ValueError('ROBOTS_CONTENT_TYPE')
                        raw=response.read(131073)
                        if len(raw)>131072:raise ValueError('ROBOTS_MAX_BYTES')
                        text=raw.decode('utf-8-sig');robots_decision(text,url)
                        state.update(robots_status=200,text=text,robots_sha256=hashlib.sha256(raw).hexdigest(),
                                     text_sha256=hashlib.sha256(text.encode()).hexdigest())
                except urllib.error.HTTPError as exc:
                    state['next_at']=max(state['next_at'],_retry_at(exc.headers,self.clock()))
                    if exc.code==404:
                        state.update(robots_status=404,text=None,robots_sha256=None)
                    else:
                        state.update(robots_status=exc.code,failure='SOURCE_POLICY_ROBOTS_UNKNOWN',expires_at=max(self.clock()+30,state['next_at']))
                        persist();raise NankanError('SOURCE_POLICY_ROBOTS_UNKNOWN',robots_url=ROBOTS,http_status=exc.code) from exc
                except (OSError,ValueError,ObservedRedirect) as exc:
                    state.update(failure='SOURCE_POLICY_ROBOTS_UNKNOWN',expires_at=self.clock()+30)
                    persist();raise NankanError('SOURCE_POLICY_ROBOTS_UNKNOWN',robots_url=ROBOTS) from exc
                state.pop('failure',None);state['expires_at']=self.clock()+300;state['checked_at']=self.now().isoformat()
                state['robots_fetched_clock']=self.clock();persist()
            if state.get('failure'):raise NankanError(state['failure'],robots_url=ROBOTS)
            if state.get('robots_status')==404:
                decision={'allowed':True,'crawl_delay_seconds':10,'matched_rule':'ROBOTS_ABSENT_HTTP_404_NOT_DENIAL'}
            elif state.get('robots_status')==200:
                try:decision=robots_decision(state['text'],url)
                except (KeyError,ValueError) as exc:raise NankanError('SOURCE_POLICY_ROBOTS_UNKNOWN') from exc
            else:raise NankanError('SOURCE_POLICY_ROBOTS_UNKNOWN')
            policy={'robots_url':ROBOTS,'status':state['robots_status'],'classification':decision['matched_rule'],
                    'robots_sha256':state.get('robots_sha256'),'checked_at':state['checked_at'],
                    'terms_url':TERMS,'usage_scope':'USER_PERSONAL_NONCOMMERCIAL_PRIVATE_ONLY_NOT_PUBLIC_REDISTRIBUTION'}
            if not decision['allowed']:raise NankanError('SOURCE_POLICY_ROBOTS_DISALLOWED',target_url=url,source_policy=policy)
            state['next_at']=max(state.get('next_at',0),state['robots_fetched_clock']+max(10,decision['crawl_delay_seconds']))
            self._wait(state);state['next_at']=self.clock()+max(10,decision['crawl_delay_seconds']);persist()
            req=urllib.request.Request(url,headers={'User-Agent':USER_AGENT,'Accept':'text/html','Accept-Encoding':'identity'},method='GET')
            try:
                with self.opener.open(req,timeout=15) as response:
                    if response.status!=200 or response.geturl()!=url:raise NankanError('NANKAN_RESPONSE_IDENTITY_HOLD')
                    headers={k.lower():v for k,v in response.headers.items()}
                    if headers.get('content-type','').split(';')[0].strip().lower()!='text/html':raise NankanError('NANKAN_CONTENT_TYPE_HOLD')
                    if headers.get('content-encoding','identity').lower() not in ('','identity'):raise NankanError('NANKAN_ENCODING_HOLD')
                    raw=response.read(MAX_BYTES+1)
                    if len(raw)>MAX_BYTES:raise NankanError('NANKAN_MAX_BYTES')
            except ObservedRedirect as exc:
                exc.receipt.update(fetched_at=self.now().isoformat(),source_policy=policy)
                exc.receipt=reference_metadata(exc.receipt)
                raise
            except urllib.error.HTTPError as exc:
                state['next_at']=max(state['next_at'],_retry_at(exc.headers,self.clock()));persist();raise
            return reference_metadata({'url':url,'http_status':200,'fetched_at':self.now().isoformat(),
                    'raw_sha256':hashlib.sha256(raw).hexdigest(),'source_policy':policy}),raw


class Node:
    def __init__(self,tag='',attrs=(),parent=None):self.tag=tag;self.attrs=dict(attrs);self.parent=parent;self.children=[]
    def all(self,tag=None,cls=None):
        out=[]
        for child in self.children:
            if isinstance(child,Node):
                if (tag is None or child.tag==tag) and (cls is None or cls in child.attrs.get('class','').split()):out.append(child)
                out.extend(child.all(tag,cls))
        return out
    def text(self):
        if self.tag in {'script','style'}:return ''
        return norm(' '.join(child.text() if isinstance(child,Node) else child for child in self.children))


class DOM(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True);self.root=Node();self.stack=[self.root];self.feed(text)
    def handle_starttag(self,tag,attrs):
        if tag in {'tr','td','th','li'}:
            boundaries={'tr':{'table'},'td':{'tr'},'th':{'tr'},'li':{'ul','ol'}}[tag]
            for index in range(len(self.stack)-1,0,-1):
                if self.stack[index].tag in boundaries:break
                if self.stack[index].tag==tag:
                    self.stack=self.stack[:index];break
        node=Node(tag,attrs,self.stack[-1]);self.stack[-1].children.append(node)
        if tag not in {'br','img','input','meta','link','hr','source','wbr'}:self.stack.append(node)
    def handle_endtag(self,tag):
        for index in range(len(self.stack)-1,0,-1):
            if self.stack[index].tag==tag:self.stack=self.stack[:index];break
    def handle_data(self,data):self.stack[-1].children.append(data)


def decode(raw):
    head=raw[:2048].decode('ascii',errors='ignore')
    charset=re.search(r'charset\s*=\s*["\']?([\w-]+)',head,re.I)
    codec='cp932' if charset and charset[1].lower() in {'shift_jis','shift-jis','sjis'} else 'utf-8'
    try:return raw.decode(codec,errors='strict')
    except UnicodeError as exc:raise NankanError('NANKAN_HTML_DECODE_UNKNOWN') from exc


def program_link(raw,day):
    links={urljoin(CALENDAR,node.attrs.get('href','')) for node in DOM(decode(raw)).root.all('a')}
    chosen=[url for url in links if re.fullmatch(re.escape(ORIGIN)+'/program/'+day.replace('-','')+r'18\d{4}\.do',url)]
    if len(chosen)!=1:raise NankanError('NANKAN_CALENDAR_URW_DAY_NOT_UNIQUE')
    return chosen[0]


def parse_program(raw,url,day,*,condition_observations=None):
    url_scope(url);provider_day_id=urlsplit(url).path.rsplit('/',1)[1][:-3]
    if not provider_day_id.startswith(day.replace('-','')+'18'):raise NankanError('NANKAN_PROGRAM_DAY_IDENTITY')
    dom=DOM(decode(raw)).root
    headings=dom.all('h3','nk23_c-block01__info__title')
    if not any('浦和競馬' in node.text() for node in headings):raise NankanError('NANKAN_PROGRAM_VENUE_BODY_REQUIRED')
    y,m,d=map(int,day.split('-'))
    if f'{y}年{m}月{d}日' not in dom.text():raise NankanError('NANKAN_PROGRAM_DATE_BODY_REQUIRED')
    races=[]
    for item in dom.all('li','nk23_c-block01__list__item'):
        anchors=item.all('a','nk23_c-block01__list__title');labels=item.all('span','nk23_c-block01__label')
        if len(anchors)!=1 or len(labels)!=1:raise NankanError('NANKAN_PROGRAM_RACE_ROW_HOLD')
        number=re.fullmatch(r'(\d{1,2})R',labels[0].text())
        if not number:raise NankanError('NANKAN_PROGRAM_RACE_NUMBER_HOLD')
        n=int(number[1]);card=urljoin(url,anchors[0].attrs.get('href',''));url_scope(card)
        if card!=ORIGIN+'/syousai/'+provider_day_id+f'{n:02d}.do':raise NankanError('NANKAN_PROGRAM_CARD_LINK_IDENTITY')
        text=item.text();post=re.search(r'\b(\d{1,2}:\d{2})\b',text);distance=re.search(r'\b(\d{3,4})m\b',text);count=re.search(r'(\d{1,2})頭',text)
        if not post or not distance or not count:raise NankanError('NANKAN_PROGRAM_RACE_FACTS_UNKNOWN')
        scheduled=datetime.fromisoformat(day+'T'+post[1]+':00+09:00')
        races.append({'provider':PROVIDER,'provider_day_id':provider_day_id,'provider_race_id':provider_day_id+f'{n:02d}',
            'venue_id':'URW','race_date':day,'race_no':n,'race_name':anchors[0].text(),
            'scheduled_post_at':scheduled.isoformat(),'prediction_cutoff':(scheduled-timedelta(seconds=120)).isoformat(),
            'cutoff_basis':'LOCAL_REFERENCE_POLICY_POST_MINUS_120_SECONDS_NOT_PROVIDER_OFFICIAL_CUTOFF',
            'distance':int(distance[1]),'surface':'DIRT','program_runner_count':int(count[1]),'observed_card_url':card})
    if [r['race_no'] for r in races]!=list(range(1,len(races)+1)) or not 1<=len(races)<=12:raise NankanError('NANKAN_PROGRAM_ALL_RACES_NOT_PROVEN')
    if condition_observations is not None:
        # Current meeting conditions belong to this dated venue header only.
        # Keep the default race identity/schema unchanged and let the caller
        # bind this Raw observation to the independently checked program receipt.
        headers=[]
        for detail in dom.all('div','nk23_c-block01__info__detail'):
            children=[node for node in detail.children if isinstance(node,Node)]
            dates=[node.text() for node in children if node.tag=='p'
                   and 'nk23_c-block01__info__text' in node.attrs.get('class','').split()]
            titles=[node.text() for node in children if node.tag=='h3'
                    and 'nk23_c-block01__info__title' in node.attrs.get('class','').split()]
            if (dates==[f'{y}年{m}月{d}日'] and len(titles)==1
                    and re.fullmatch(r'(?:第\d+回\s+)?浦和競馬(?:\s+第\d+日)?',titles[0])):
                headers.append(detail)
        status=('CURRENT_URW_HEADER_MATCHED' if len(headers)==1 else
            'CURRENT_URW_HEADER_NOT_FOUND' if not headers else 'CURRENT_URW_HEADER_NOT_UNIQUE')
        observed={'provider':PROVIDER,'venue_id':'URW','race_date':day,'provider_day_id':provider_day_id,
            'source_url':url,'source_raw_sha256':hashlib.sha256(raw).hexdigest(),
            'header_scope_status':status,'raw_header':headers[0].text() if len(headers)==1 else None,
            'weather':None,'track_condition':None,'weather_observed':None,'track_condition_observed':None,
            'weather_reason':status,'track_condition_reason':status}
        if len(headers)==1:
            labels=[node.text() for node in headers[0].children if isinstance(node,Node) and node.tag=='p'
                    and 'nk23_c-block01__info__texts' in node.attrs.get('class','').split()]
            match=re.fullmatch(r'天候\s*:\s*(\S+)\s+馬場\s*:\s*(\S+)',labels[0]) if len(labels)==1 else None
            if match:
                weather,going=match.groups();observed.update(weather_observed=weather,track_condition_observed=going)
                observed['weather']=weather if weather in ('晴','曇','雨','雪','小雨','小雪') else None
                ground=re.fullmatch(r'(?:ダート|ダ)?(不良|稍重|良|重|不|稍)',going)
                observed['track_condition']=({'不':'不良','稍':'稍重'}.get(ground[1],ground[1]) if ground else None)
                for key,printed in (('weather',weather),('track_condition',going)):
                    observed[key+'_reason']=('OBSERVED_CURRENT_HEADER_LABEL' if observed[key] is not None else
                        'UNPUBLISHED_HEADER_MARKER' if printed in ('-','―','ー','UNKNOWN') else 'UNSUPPORTED_HEADER_VALUE')
            else:
                observed.update(weather_reason='CURRENT_HEADER_CONDITION_LABELS_UNSUPPORTED',
                    track_condition_reason='CURRENT_HEADER_CONDITION_LABELS_UNSUPPORTED')
        condition_observations.update(observed)
    return races


def one(nodes,code):
    if len(nodes)!=1:raise NankanError(code)
    return nodes[0]


def parse_result(raw,race,facts,receipt,*,race_id):
    """Normalize a witnessed official result, including explicit horse refunds.

    Private research evidence only. A complete declared universe is checked;
    DNF/DQ is not a refund. Unknown notes, ties or absent payouts fail closed.
    This does not admit/sign SOURCE or retrospectively certify ACTIVE.
    """
    day=str(race.get('race_date','')).replace('-','');number=race.get('race_no')
    if (race.get('provider')!=PROVIDER or race.get('venue_id')!='URW'
            or type(number) is not int or not 1<=number<=12
            or not re.fullmatch(r'\d{8}',day)
            or not re.fullmatch(re.escape(day)+r'18\d{4}'+f'{number:02d}',str(race.get('provider_race_id','')))
            or not str(race_id).startswith(f'KM-LOCAL-URW-{day}-R{number:02d}')
            or type(race.get('program_runner_count')) is not int
            or len(facts)!=race['program_runner_count']):
        raise NankanError('NANKAN_RESULT_DECLARED_CONTEXT_HOLD')
    reference_metadata(receipt)
    expected=ORIGIN+'/result/'+race['provider_race_id']+'.do'
    url_scope(expected)
    if (receipt.get('url')!=expected or receipt.get('http_status')!=200
            or receipt.get('raw_sha256')!=hashlib.sha256(raw).hexdigest()):
        raise NankanError('NANKAN_RESULT_RAW_RECEIPT_HOLD')
    try:
        observed=datetime.fromisoformat(receipt['fetched_at'])
        post=datetime.fromisoformat(race['scheduled_post_at'])
        if observed.tzinfo is None or observed>utcnow() or observed<=post:raise ValueError()
    except (KeyError,ValueError,TypeError) as exc:
        raise NankanError('NANKAN_RESULT_POSTSTART_TIME_HOLD') from exc
    dom=DOM(decode(raw)).root
    _verify_race_header(dom,race,verify_runner_count=False)
    tables=[t for t in dom.all('table') if t.all('tr') and
            [x.text() for x in t.all('tr')[0].all('th')][:4]==['着','枠','馬番','馬名']]
    names={str(x['runner_id']):x['name'] for x in facts}
    if len(names)!=len(facts):raise NankanError('NANKAN_RESULT_DUPLICATE_DECLARED_ID')
    finish=[];nonfinish=[];seen=set()
    statuses={'出走取消':'SCRATCHED','競走除外':'EXCLUDED','競走中止':'DNF','失格':'DISQUALIFIED'}
    for tr in one(tables,'NANKAN_RESULT_TABLE_HOLD').all('tr')[1:]:
        cells=[x.text() for x in tr.all('td')]
        if not cells:continue
        if len(cells)<4 or cells[2] not in names or names[cells[2]]!=cells[3] or cells[2] in seen:
            raise NankanError('NANKAN_RESULT_RUNNER_IDENTITY_HOLD')
        rid=cells[2];seen.add(rid)
        if cells[0].isdigit():
            if any(x in statuses for x in cells):raise NankanError('NANKAN_RESULT_FINISH_STATUS_CONFLICT_HOLD')
            finish.append({'runner_id':rid,'rank':int(cells[0]),'name':cells[3]})
        else:
            observed_status=[x for x in cells if x in statuses]
            if len(observed_status)!=1:raise NankanError('NANKAN_RESULT_NONFINISH_UNKNOWN_HOLD')
            nonfinish.append({'runner_id':rid,'name':cells[3],'status':statuses[observed_status[0]],
                              'observed_status':observed_status[0]})
    finish.sort(key=lambda x:x['rank'])
    if (seen!=set(names) or len(finish)<3 or [x['rank'] for x in finish[:3]]!=[1,2,3]
            or len({x['rank'] for x in finish})!=len(finish)):
        raise NankanError('NANKAN_RESULT_UNIVERSE_OR_TIE_HOLD')
    vertical=[t for t in dom.all('table') if t.all('tr') and
              [x.text() for x in t.all('tr')[0].all('th')]==['','組番','金額','人気']]
    payouts={};notes=[];top=[int(x['runner_id']) for x in finish[:3]]
    for tr in one(vertical,'NANKAN_RESULT_PAYOUT_TABLE_HOLD').all('tr')[1:]:
        hs=tr.all('th');ds=tr.all('td')
        if not hs:continue
        label=hs[0].text()
        if label=='備考':
            notes.append(one(ds,'NANKAN_RESULT_REFUND_NOTE_HOLD').text());continue
        if label not in ('馬単','三連複','三連単'):continue
        bt={'馬単':'EXACTA','三連複':'TRIO','三連単':'TRIFECTA'}[label]
        target=top[:2] if bt=='EXACTA' else sorted(top) if bt=='TRIO' else top
        if (bt in payouts or len(ds)<2 or not re.fullmatch(r'\d+(?:-\d+){1,2}',ds[0].text())
                or list(map(int,ds[0].text().split('-')))!=target
                or not re.fullmatch(r'[\d,]+',ds[1].text())):
            raise NankanError('NANKAN_RESULT_PAYOUT_SELECTION_HOLD')
        payouts[bt]=int(ds[1].text().replace(',',''))
        if payouts[bt]<=0:raise NankanError('NANKAN_RESULT_PAYOUT_VALUE_HOLD')
    if set(payouts)!={'EXACTA','TRIO','TRIFECTA'} or len(notes)!=1:
        raise NankanError('NANKAN_RESULT_PAYOUT_OR_REFUND_NOTE_MISSING_HOLD')
    note=notes[0];refunded=set()
    if note not in ('','-','なし','返還なし'):
        # Accept only an explicitly enumerated horse-number refund, not a
        # blanket inference from non-finish or a partially understood note.
        if not re.fullmatch(r'返還\s*:\s*\d+号馬(?:\s*[、,・]\s*\d+号馬)*',note):
            raise NankanError('NANKAN_RESULT_REFUND_NOTE_UNKNOWN_HOLD',observed_note=note)
        refunded=set(re.findall(r'(\d+)号馬',note))
    excluded={x['runner_id'] for x in nonfinish if x['status'] in ('SCRATCHED','EXCLUDED')}
    if refunded!=excluded:raise NankanError('NANKAN_RESULT_REFUND_STATUS_DISAGREEMENT_HOLD')
    official={'status':'OFFICIAL','top3':top,'payouts':payouts,
              'refund_status':'RESOLVED','refunded_runner_ids':sorted(refunded,key=int),
              'refund_evidence':{'raw_sha256':receipt['raw_sha256'],'observed_note':note},
              'nonfinish_rows':nonfinish}
    out={'schema':'KM-URW-OBSERVED-RESULT-REVISION-v1','race_id':race_id,
         'provider':PROVIDER,'source_authority':PROVIDER,'private_storage_required':True,
         'public_redistribution_authorized':False,
         'race_date':race['race_date'],'race_no':race['race_no'],
         'finish_order':[x['runner_id'] for x in finish],'finish_rows':finish,
         'official_result_verified':True,'official_result':official,'payouts':payouts,
         'source_url':expected,'source_raw_sha256':receipt['raw_sha256'],
         'observed_at':receipt['fetched_at'],'source_receipt_sha256':sha(receipt),
         'formal_source_claim':False,'signed_source_claim':False,'production_authority':False,
         'active_verified':False,'actual_purchase':False}
    out['sha256']=sha(out)
    return out


def _verify_race_header(dom,race,*,verify_runner_count=True):
    header=one(dom.all('p','nk23_c-tab1__subtitle'),'NANKAN_CARD_HEADER_UNKNOWN').text()
    y,m,d=map(int,race['race_date'].split('-'))
    if not re.search(rf'{y}年{m}月{d}日',header) or '浦和競馬' not in header or not re.match(rf'{race["race_no"]}R\b',header):
        raise NankanError('NANKAN_CARD_BODY_IDENTITY')
    if (not re.search(rf'(?<![\d,])(?:{race["distance"]:,}|{race["distance"]})m(?![A-Za-z0-9])',header)
            or race['scheduled_post_at'][11:16] not in header
            or (verify_runner_count and f'{race["program_runner_count"]}頭' not in header)):
        raise NankanError('NANKAN_CARD_PROGRAM_FACT_MISMATCH')
    return header


def _history_observation(run,*,slot,race,source_raw_sha256,source_url,provider_horse_id):
    """Read a displayed slot; local evidence identity never impersonates a result ID.

    Nonordinary events remain available for audit, outside the ordinary starts
    consumed by the existing numerical/Owner contracts. Receipt time belongs to
    the enclosing snapshot; this byte parser does not manufacture one.
    """
    raw=run.text() if run is not None else ''
    provenance={'identity_type':'LOCAL_RAW_HISTORY_SLOT','source_raw_sha256':source_raw_sha256,
        'source_url':source_url,'provider_horse_id':provider_horse_id,'history_slot':slot,
        'provider_result_url':None}
    observation={'slot':slot,'classification':'UNSUPPORTED','status':'UNKNOWN','event_type':'UNKNOWN',
        'ordinary_start_eligible':False,'reason':None,'raw':raw,'record':None,'provenance':provenance}
    def unsupported(reason):
        observation['reason']=reason
        return observation
    if run is None:
        observation.update(classification='ABSENT',reason='HISTORY_SLOT_ABSENT');return observation
    if not raw:
        observation.update(classification='EMPTY',reason='HISTORY_SLOT_EMPTY');return observation
    heads=run.all('p','nk23_u-d-flex')
    if not heads:return unsupported('HISTORY_DESCRIPTOR_MISSING')
    if len(heads)!=1:raise NankanError('NANKAN_HISTORY_DESCRIPTOR_NOT_UNIQUE')
    spans=[node for node in heads[0].children if isinstance(node,Node) and node.tag=='span']
    if len(spans)!=3:raise NankanError('NANKAN_HISTORY_DESCRIPTOR_UNKNOWN')
    date_match=re.fullmatch(r'(.+?)(\d{2,4})\.(\d{1,2})\.(\d{1,2})',spans[1].text())
    if not date_match:raise NankanError('NANKAN_HISTORY_DATE_UNKNOWN')
    venue,year,month,day=date_match.groups();year=int(year)+(2000 if len(year)==2 else 0)
    try:when=date(year,int(month),int(day))
    except ValueError as exc:raise NankanError('NANKAN_HISTORY_DATE_UNKNOWN') from exc
    if when>=date.fromisoformat(race['race_date']):raise NankanError('NANKAN_POST_RACE_HISTORY_FORBIDDEN')
    provenance['history_date']=when.isoformat()
    provenance['local_evidence_id']=sha({'source_raw_sha256':source_raw_sha256,
        'provider_horse_id':provider_horse_id,'history_slot':slot,'history_date':when.isoformat()})
    titles=run.all('a','race_name_len')+run.all('p','race_name_len')
    if len(titles)>1:raise NankanError('NANKAN_HISTORY_RACE_NOT_UNIQUE')
    title=titles[0] if titles else None
    rid=None
    if title is not None and title.tag=='a':
        match=re.fullmatch(r'/result/(\d{16})\.do',title.attrs.get('href',''))
        if not match or not match[1].startswith(when.strftime('%Y%m%d')):
            raise NankanError('NANKAN_HISTORY_PROVIDER_IDENTITY')
        rid=match[1];provenance['provider_result_url']=ORIGIN+title.attrs['href']
    marker=spans[0].text().replace(' ','')
    finish=re.match(r'^(\d{1,2})着',marker)
    status=('TRIAL' if marker=='能試' else 'EXCLUDED' if marker in ('除外','競走除外','取消','出走取消')
        else 'DNF' if marker in ('中止','競走中止') else 'FINISHED' if finish else 'UNKNOWN')
    name=title.text() if title else None
    kind='TRIAL' if status=='TRIAL' else 'JUMP' if name and '障害' in name else 'FLAT'
    dist=re.search(r'(\d{3,4})\s*$',spans[2].text())
    # Only explicitly labelled paragraphs supply optional facts. Missing values
    # remain missing; no count, jockey or clock is inferred from another number.
    paragraphs=[node.text() for node in run.children if isinstance(node,Node) and node.tag=='p']
    rides=[re.fullmatch(r'(\d+)頭\s+(\d+)番\s+(?:(\d+)人気\s+)?(.+?)\s+([☆▲△◇★]?\s*\d{2}(?:\.\d+)?)',text)
           for text in paragraphs]
    rides=[m for m in rides if m]
    if len(rides)>1:raise NankanError('NANKAN_HISTORY_RIDE_NOT_UNIQUE')
    ride=rides[0] if rides else None
    popularity=run.all('span','popularity')
    field=re.search(r'(\d+)頭',popularity[0].text()) if popularity else None
    field_size=int(field[1]) if field else int(ride[1]) if ride else None
    if field and ride and int(field[1])!=int(ride[1]):raise NankanError('NANKAN_HISTORY_FIELD_SIZE_CONFLICT')
    bodyweights=[re.fullmatch(r'(\d{3,4})kg(?:\s+(.+))?',text) for text in paragraphs]
    bodyweights=[m for m in bodyweights if m]
    if len(bodyweights)>1:raise NankanError('NANKAN_HISTORY_BODY_WEIGHT_NOT_UNIQUE')
    past_bw=bodyweights[0] if bodyweights else None
    clocks=[re.fullmatch(r'((?:\d+:)?\d{2,3}\.\d)(?:\s+\(([+-]?\d+(?:\.\d+)?)\))?(?:\s+3F\s+(\d{2}\.\d)(?:\s+\(\d+\))?)?',text)
            for text in paragraphs]
    clocks=[m for m in clocks if m]
    if len(clocks)>1:raise NankanError('NANKAN_HISTORY_TIME_NOT_UNIQUE')
    clock=clocks[0] if clocks else None
    positions=[]
    for p in run.all('p','position'):
        positions=[int(node.text()) for node in p.all('span') if re.fullmatch(r'\d{1,2}',node.text())]
    going_label=re.fullmatch(r'(不良|稍重|良|重|不|稍)(?:内|外)?(?:ダート|ダ|芝)\s*\d{3,4}',spans[2].text())
    going=({'不':'不良','稍':'稍重'}.get(going_label[1],going_label[1]) if going_label else None)
    start={'date':when.strftime('%y.%m.%d'),'venue':venue,'provider_race_id':rid,
        'surface':'DIRT' if 'ダ' in spans[2].text() else 'TURF' if '芝' in spans[2].text() else 'UNKNOWN',
        'distance':int(dist[1]) if dist else None,'finish':int(finish[1]) if finish else None,
        'field_size':field_size,'content_positions':positions,'race_name':name,
        'going_observed':spans[2].text(),'raw':raw,'provider':PROVIDER,'going':going,'direction':'UNKNOWN',
        'horse_no':int(ride[2]) if ride else None,'ride_popularity':int(ride[3]) if ride and ride[3] else None,
        'ride_jockey':ride[4] if ride else None,
        'ride_carried_weight':float(re.sub(r'^[☆▲△◇★]\s*','',ride[5])) if ride else None,
        'ride_body_weight':int(past_bw[1]) if past_bw else None,
        'content_time_text':clock[1] if clock else None,'content_final3f':float(clock[3]) if clock and clock[3] else None,
        # A winner's printed difference is the runner-up margin, not a deficit.
        'margin':(0.0 if finish and int(finish[1])==1 else float(clock[2])) if clock and clock[2] else None,
        'winning_margin':float(clock[2]) if clock and clock[2] and finish and int(finish[1])==1 else None,
        'winner':past_bw[2] if past_bw and (not finish or int(finish[1])!=1) else None}
    if field_size is not None and (not 1<=field_size<=18
            or start['finish'] is not None and not 1<=start['finish']<=field_size
            or any(not 1<=p<=field_size for p in positions)):
        raise NankanError('NANKAN_HISTORY_RANGE_HOLD')
    observation.update(status=status,event_type=kind,record=start)
    if status=='TRIAL':observation.update(classification='TRIAL',reason='NONORDINARY_TRIAL')
    elif status=='EXCLUDED':observation.update(classification='EXCLUDED',reason='PAST_EVENT_NOT_STARTED')
    elif kind=='JUMP':observation.update(classification='JUMP',reason='NONORDINARY_JUMP')
    elif status=='UNKNOWN':return unsupported('HISTORY_FINISH_STATUS_UNKNOWN')
    elif title is None or not name:return unsupported('HISTORY_RACE_NAME_MISSING')
    elif start['surface']=='UNKNOWN':return unsupported('HISTORY_SURFACE_UNKNOWN')
    else:observation.update(classification='ORDINARY_START',ordinary_start_eligible=True,
        reason='ORDINARY_DNF_FINISH_UNKNOWN' if status=='DNF' else 'OBSERVED_ORDINARY_START')
    return observation


def parse_card(raw,race,url,*,excluded_rows=None):
    if url!=ORIGIN+'/uma_shosai/'+race['provider_race_id']+'.do':raise NankanError('NANKAN_CARD_URL_IDENTITY')
    dom=DOM(decode(raw)).root;raw_sha256=hashlib.sha256(raw).hexdigest()
    _verify_race_header(dom,race)
    table=one([node for node in dom.all('table','tb-shousai') if node.attrs.get('id')!='tb-sample'
               and 'hidden' not in node.attrs.get('class','').split()],'NANKAN_ACTUAL_HISTORY_TABLE_REQUIRED')
    body=one(table.all('tbody'),'NANKAN_ACTUAL_HISTORY_BODY_REQUIRED');runners=[]
    exclusions=[]
    for row in [node for node in body.children if isinstance(node,Node) and node.tag=='tr']:
        no=one(row.all('td','umaban'),'NANKAN_HORSE_NUMBER_REQUIRED').text()
        cell=one(row.all('td','pr-umaName-textRound'),'NANKAN_HORSE_NAME_CELL_REQUIRED')
        anchors=[node for node in cell.all('a') if re.fullmatch(r'/uma_info/\d+\.do',node.attrs.get('href',''))]
        horse=one(anchors,'NANKAN_HORSE_IDENTITY_REQUIRED');name=horse.text()
        if not name:raise NankanError('NANKAN_HORSE_NAME_UNKNOWN')
        if not re.fullmatch(r'[1-9]|1[0-6]',no):
            # A current official card can show 取 消 instead of a numerical
            # horse number. This is an *explicitly unnumbered* scratch, never
            # a new numerical runner ID or proof of all other horses being ACTIVE.
            marker=norm(no).replace(' ','')
            if marker not in ('取消','除外','出走取消','競走除外'):
                raise NankanError('NANKAN_HORSE_NUMBER_UNKNOWN')
            exclusions.append({'runner_id':None,'name':name,
                'provider_horse_id':horse.attrs['href'].split('/')[-1][:-3],
                'observed_marker':no,'status':'CANCELLED',
                'reason':'EXPLICIT_UNNUMBERED_OFFICIAL_CARD_CANCELLATION',
                'active_verified':False})
            continue
        group=one(row.all('td','cs-g1'),'NANKAN_CURRENT_RIDER_CELL_REQUIRED')
        jockeys=[node.text() for node in group.all('a') if node.attrs.get('href','').startswith('/kis_info/')]
        loads=[re.sub(r'^[☆▲△◇★]\s*','',node.text()) for node in group.all('span','nk23_u-text12')
               if re.fullmatch(r'[☆▲△◇★]?\s*\d{2}(?:\.\d+)?',node.text())]
        weights=row.all('td','cs-g2')
        if len(weights)>1:raise NankanError('NANKAN_CURRENT_BODY_WEIGHT_NOT_UNIQUE')
        weight=re.fullmatch(r'(\d{3,4})(?:\s+([+-]?\d+|±0))?',weights[0].text()) if weights else None
        current_bw=int(weight[1]) if weight else None
        current_bw_change=(0 if weight[2]=='±0' else int(weight[2])) if weight and weight[2] is not None else None
        sire=next((node.text() for node in cell.children if isinstance(node,Node) and node.tag=='p'
                   and 'nk23_u-text12' in node.attrs.get('class','').split()),None)
        details=[node.text() for node in cell.children if isinstance(node,Node) and node.tag=='p'
                 and 'nk23_u-text10' in node.attrs.get('class','').split()]
        sex_age=details[0] if details else None
        age_match=re.match(r'^[牡牝セ騸](\d{1,2})\b',sex_age or '')
        trainers=[node.text() for node in group.all('a') if node.attrs.get('href','').startswith('/cho_info/')]
        frames=[node for node in row.all('td','waku') if 'cs-wakuBanR' not in node.attrs.get('class','').split()]
        frame=frames[0].text() if len(frames)==1 else ''
        starts=[];missing=[];observations=[]
        for slot in range(1,6):
            cells=row.all('td',f'cs-z{slot}')
            run=one(cells,'NANKAN_HISTORY_SLOT_NOT_UNIQUE') if cells else None
            observed=_history_observation(run,slot=slot,race=race,
                source_raw_sha256=raw_sha256,source_url=url,
                provider_horse_id=horse.attrs['href'].split('/')[-1][:-3])
            observations.append(observed)
            if observed['ordinary_start_eligible']:
                start=observed['record'];starts.append(start)
                if not start['distance'] or not start['content_positions']:
                    missing.append(f'PAST_START_{slot}_DISTANCE_OR_POSITIONS_UNKNOWN')
            elif observed['classification']=='UNSUPPORTED':
                missing.append(f"PAST_START_{slot}_UNSUPPORTED_{observed['reason']}")
            elif observed['classification'] in ('ABSENT','EMPTY'):
                missing.append(f'PAST_START_{slot}_UNKNOWN')
        slot_counts={'slots':len(observations),'nonempty':sum(bool(x['raw']) for x in observations),
            'ordinary_starts':len(starts),
            'nonordinary':sum(x['classification'] in ('TRIAL','JUMP','EXCLUDED') for x in observations),
            'unsupported':sum(x['classification']=='UNSUPPORTED' for x in observations),
            'empty':sum(x['classification']=='EMPTY' for x in observations),
            'absent':sum(x['classification']=='ABSENT' for x in observations)}
        statuses=[node.text() for node in row.all('td','cs-odds')]
        cancelled=any(re.fullmatch(r'(?:取消|除外)',text) for text in statuses)
        runners.append({'runner_id':no,'horse_no':int(no),'name':name,'provider_horse_id':horse.attrs['href'].split('/')[-1][:-3],
            'frame_no':int(frame) if re.fullmatch(r'[1-8]',frame) else None,
            'status':'CANCELLED' if cancelled else 'ACTIVE_DECLARED','active_verified':False,
            'current_jockey':jockeys[0] if len(jockeys)==1 else 'UNKNOWN','current_load':float(loads[0]) if len(loads)==1 else None,
            'current_body_weight':current_bw,'current_body_weight_change':current_bw_change,
            'sex_age':sex_age,'age':int(age_match[1]) if age_match else None,
            'sire':sire,'dam':details[1] if len(details)>1 else None,
            'damsire':re.sub(r'^\(|\)$','',details[2]) if len(details)>2 else None,
            'trainer':trainers[0] if len(trainers)==1 else None,
            'current_odds':'UNKNOWN','odds':None,'popularity':None,'starts':starts,
            'history_observations':observations,'history_slot_counts':slot_counts,
            'missingness':missing+['CURRENT_ACTIVE_NOT_VERIFIED','CURRENT_ODDS_UNKNOWN']
                +(['CURRENT_BODY_WEIGHT_UNKNOWN'] if current_bw is None else [])
                +(['CURRENT_BODY_WEIGHT_CHANGE_UNKNOWN'] if current_bw_change is None else [])})
    ids=[r['runner_id'] for r in runners]
    if len(set(ids))!=len(ids) or len(set(r['name'] for r in runners))!=len(ids):
        raise NankanError('NANKAN_ALL_RUNNER_UNIVERSE_MISMATCH')
    # The program may advertise only currently numbered runners even when the
    # HTML retains an explicitly CANCELLED, still-numbered historical row.
    # When the program and table counts already match, preserve the original
    # declared+cancelled semantics and immutable original behavior.
    if len(runners)!=race['program_runner_count']:
        numbered_active=[r for r in runners if r['status']!='CANCELLED']
        if len(numbered_active)!=race['program_runner_count']:
            raise NankanError('NANKAN_ALL_RUNNER_UNIVERSE_MISMATCH')
        for row in runners:
            if row['status']=='CANCELLED':
                exclusions.append({'runner_id':row['runner_id'],'name':row['name'],
                    'provider_horse_id':row['provider_horse_id'],
                    'observed_marker':'CANCELLED_IN_CARD_ODDS',
                    'status':'CANCELLED','reason':'EXPLICIT_NUMBERED_OFFICIAL_CARD_CANCELLATION',
                    'active_verified':False})
        runners=numbered_active
    identities=[row['provider_horse_id'] for row in runners+exclusions]
    if len(set(identities))!=len(identities) or len(set(row['name'] for row in runners+exclusions))!=len(identities):
        raise NankanError('NANKAN_SCRATCH_IDENTITY_DUPLICATE')
    numbered={int(row['runner_id']) for row in runners+exclusions if row['runner_id'] is not None}
    unexplained=set(range(1,max(numbered,default=0)+1))-numbered
    if len(unexplained)>sum(row['runner_id'] is None for row in exclusions):
        raise NankanError('NANKAN_UNEXPLAINED_RUNNER_NUMBER_GAP')
    if excluded_rows is not None:
        excluded_rows.extend(exclusions)
    return runners


def _unsigned_current_observation(raw,race,receipt,expected_url,kind):
    number=race.get('race_no');day=str(race.get('race_date','')).replace('-','')
    if (race.get('provider')!=PROVIDER or race.get('venue_id')!='URW' or type(number) is not int
            or not 1<=number<=12 or len(day)!=8
            or not re.fullmatch(re.escape(day)+r'18\d{4}'+f'{number:02d}',str(race.get('provider_race_id','')))):
        raise NankanError('NANKAN_CURRENT_RACE_CONTEXT_MISMATCH')
    meta=reference_metadata(receipt)
    if (meta.get('url')!=expected_url or meta.get('http_status')!=200
            or hashlib.sha256(raw).hexdigest()!=meta.get('raw_sha256')):
        raise NankanError('NANKAN_CURRENT_OBSERVATION_IDENTITY_OR_RAW_HASH')
    try:
        fetched=datetime.fromisoformat(meta['fetched_at'])
        cutoff=datetime.fromisoformat(race['prediction_cutoff'])
        if fetched.tzinfo is None or cutoff.tzinfo is None:raise ValueError('TIMEZONE')
    except (KeyError,TypeError,ValueError) as exc:
        raise NankanError('NANKAN_CURRENT_OBSERVATION_TIME_UNKNOWN') from exc
    return {'provider':PROVIDER,'observation_type':kind,'race':race,'source_url':expected_url,
        'raw_sha256':meta['raw_sha256'],'source_fetched_at':meta['fetched_at'],
        'source_policy':meta.get('source_policy'),'observed_before_reference_cutoff':fetched<cutoff,
        'formal_source_claim':False,'signed_source_claim':False,'production_authority':False,
        'active_verified':False,'public_redistribution_authorized':False}


def _declared_current_facts(race,declared_facts):
    if not isinstance(declared_facts,list) or not declared_facts or len(declared_facts)!=race['program_runner_count']:
        raise NankanError('NANKAN_CURRENT_DECLARED_UNIVERSE_REQUIRED')
    declared={str(r['runner_id']):r for r in declared_facts}
    if len(declared)!=len(declared_facts):raise NankanError('NANKAN_CURRENT_DECLARED_ID_DUPLICATE')
    return declared


def parse_current_odds(raw,race,receipt,declared_facts):
    """Observed win/place membership only; never a signed ACTIVE universe."""
    url=ORIGIN+'/odds/'+race['provider_race_id']+'01.do';url_scope(url)
    result=_unsigned_current_observation(raw,race,receipt,url,'PRIVATE_UNSIGNED_OFFICIAL_ODDS_MEMBERSHIP')
    dom=DOM(decode(raw)).root;_verify_race_header(dom,race)
    table=one(dom.all('table','nk23_c-table04__table'),'NANKAN_WIN_PLACE_ODDS_TABLE_REQUIRED')
    declared=_declared_current_facts(race,declared_facts)
    rows=[]
    for row in table.all('tr'):
        cells=[node.text() for node in row.children if isinstance(node,Node) and node.tag=='td']
        if not cells:continue
        if len(cells) not in (3,4) or not re.fullmatch(r'[1-9]|1[0-6]',cells[0]):
            raise NankanError('NANKAN_ODDS_ROW_IDENTITY_UNKNOWN')
        rid,name=cells[:2]
        if rid not in declared or declared[rid]['name']!=name:raise NankanError('NANKAN_ODDS_DECLARED_NAME_MISMATCH')
        cancelled=any(value.replace(' ','') in ('取消','取止','除外','出走取消','競走除外') for value in cells[2:])
        win=float(cells[2]) if not cancelled and re.fullmatch(r'\d+(?:\.\d+)?',cells[2]) else None
        place=re.fullmatch(r'(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)',cells[3]) if len(cells)==4 and not cancelled else None
        low,high=(float(place[1]),float(place[2])) if place else (None,None)
        present=win is not None and win>0 and low is not None and 0<low<=high
        rows.append({'runner_id':rid,'name':name,'status':'CANCELLED' if cancelled else 'ACTIVE_DECLARED',
            'win_odds':win,'place_odds_low':low,'place_odds_high':high,
            'betting_membership_observed':present,'active_verified':False,
            'missingness':[] if present or cancelled else ['CURRENT_ODDS_MEMBERSHIP_UNKNOWN']})
    if len(rows)!=len(declared) or len({r['runner_id'] for r in rows})!=len(rows) or {r['runner_id'] for r in rows}!=set(declared):
        raise NankanError('NANKAN_ODDS_DECLARED_UNIVERSE_MISMATCH')
    times={match[1] for node in dom.all('span','btn_now_time_break')
           if (match:=re.fullmatch(r'(\d{1,2}:\d{2})\s*現在',node.text()))}
    if len(times)>1:raise NankanError('NANKAN_ODDS_PROVIDER_TIME_NOT_UNIQUE')
    try:
        hour,minute=map(int,next(iter(times)).split(':')) if times else (None,None)
        provider_at=datetime.combine(date.fromisoformat(race['race_date']),datetime.min.time(),JST).replace(hour=hour,minute=minute) if times else None
    except ValueError as exc:
        raise NankanError('NANKAN_ODDS_PROVIDER_TIME_INVALID') from exc
    if provider_at and provider_at>datetime.fromisoformat(result['source_fetched_at']):
        raise NankanError('NANKAN_ODDS_PROVIDER_TIME_AFTER_CAPTURE')
    result.update(runners=rows,runner_count=len(rows),declared_facts_sha256=sha(declared_facts),
        provider_display_at=provider_at.isoformat() if provider_at else None,
        provider_display_time_status='OBSERVED' if provider_at else 'UNKNOWN',
        betting_membership_observed_count=sum(r['betting_membership_observed'] for r in rows))
    result['sha256']=sha(result);return result


def parse_current_changes(raw,race,receipt,declared_facts):
    """Read target-race change facts; absence never grants ACTIVE authority."""
    url=ORIGIN+'/henko_info/00000000000000.do'
    result=_unsigned_current_observation(raw,race,receipt,url,'PRIVATE_UNSIGNED_OFFICIAL_CHANGE_ITEMS')
    dom=DOM(decode(raw)).root
    heading=one(dom.all('h3','nk23_c-block01__info__title'),'NANKAN_CHANGES_VENUE_HEADER_REQUIRED')
    y,m,d=map(int,race['race_date'].split('-'))
    if '浦和競馬' not in heading.text() or f'{y}年{m}月{d}日' not in heading.parent.text():
        raise NankanError('NANKAN_CHANGES_DAY_OR_VENUE_MISMATCH')
    # A missing race row is UNKNOWN. Preserve the provider's explicit day-wide
    # notice separately, within the same dated venue block, without granting
    # ACTIVE, Admission or Production authority.
    block=heading.parent
    while block and 'nk23_c-block01' not in block.attrs.get('class','').split():
        block=block.parent

    def block_nodes(tag,cls=None):
        nodes=(block or dom).all(tag,cls)
        if block is None:return nodes  # Legacy row fixtures have no venue block.
        owned=[]
        for node in nodes:
            parent=node.parent
            while parent is not None and 'nk23_c-block01' not in parent.attrs.get('class','').split():
                parent=parent.parent
            if parent is block:owned.append(node)
        return owned

    notices=[node for node in block_nodes('p','nk23_c-text02')
             if node.text()=='本日開催に変更情報がありません'] if block else []
    if len(notices)>1:raise NankanError('NANKAN_CHANGES_NO_CHANGE_NOTICE_NOT_UNIQUE')
    no_changes=bool(notices)
    if no_changes and datetime.fromisoformat(result['source_fetched_at']).astimezone(JST).date().isoformat()!=race['race_date']:
        raise NankanError('NANKAN_CHANGES_CURRENT_DAY_MISMATCH')
    if no_changes and (block_nodes('li','nk23_c-block01__list__item')
                       or block_nodes('div','nk23_c-block01__list2__item')):
        raise NankanError('NANKAN_CHANGES_NO_CHANGE_NOTICE_CONTRADICTION')
    clocks=[node for node in block_nodes('span') if node.attrs.get('id')=='nowDateSpan'] if block else []
    if len(clocks)>1:raise NankanError('NANKAN_CHANGES_PROVIDER_TIME_NOT_UNIQUE')
    provider_at=None
    if clocks:
        match=re.fullmatch(r'(\d{4})年(\d{1,2})月(\d{1,2})日 (\d{1,2}):(\d{2})現在',clocks[0].text())
        try:
            if not match:raise ValueError('DISPLAY_TIME')
            provider_at=datetime(*map(int,match.groups()),tzinfo=JST)
        except ValueError as exc:
            raise NankanError('NANKAN_CHANGES_PROVIDER_TIME_INVALID') from exc
        if provider_at.date().isoformat()!=race['race_date']:
            raise NankanError('NANKAN_CHANGES_PROVIDER_TIME_DAY_MISMATCH')
        if provider_at>datetime.fromisoformat(result['source_fetched_at']):
            raise NankanError('NANKAN_CHANGES_PROVIDER_TIME_AFTER_CAPTURE')
    declared=_declared_current_facts(race,declared_facts);items=[];target_rows=0
    for row in block_nodes('li','nk23_c-block01__list__item'):
        if row.attrs.get('id')!=f"{race['race_no']:02d}":continue
        target_rows+=1
        label=one(row.all('span','nk23_c-block01__label'),'NANKAN_CHANGE_RACE_LABEL_REQUIRED').text()
        if label!=str(race['race_no'])+'R':raise NankanError('NANKAN_CHANGE_RACE_LABEL_MISMATCH')
        links={node.attrs.get('href') for node in row.all('a')}
        if '/syousai/'+race['provider_race_id']+'.do' not in links:
            raise NankanError('NANKAN_CHANGE_CARD_IDENTITY_MISMATCH')
        for change in row.all('div','nk23_c-block01__list2__item'):
            kind=one(change.all('p','nk23_c-block01__tag'),'NANKAN_CHANGE_TYPE_REQUIRED').text()
            number=one(change.all('span','nk23_c-block01__txt2'),'NANKAN_CHANGE_HORSE_NUMBER_REQUIRED').text()
            match=re.fullmatch(r'(\d{1,2})番',number)
            horse=one([a for a in change.all('a') if re.fullmatch(r'/uma_info/\d+\.do',a.attrs.get('href',''))],
                      'NANKAN_CHANGE_HORSE_IDENTITY_REQUIRED')
            rid=match[1] if match else None;original=declared.get(rid)
            if not original or original['name']!=horse.text() or horse.attrs['href']!='/uma_info/'+original['provider_horse_id']+'.do':
                raise NankanError('NANKAN_CHANGE_DECLARED_IDENTITY_MISMATCH')
            details=' '.join(node.text() for node in change.all('p','nk23_c-block01__text2'))
            items.append({'runner_id':rid,'name':horse.text(),'change_type':kind,
                'status':'CANCELLED' if kind in ('競走除外','出走取消') else 'ACTIVE_DECLARED',
                'jockey_names_observed':[a.text() for a in change.all('a') if a.attrs.get('href','').startswith('/kis_info/')],
                'change_detail_observed':details,'active_verified':False})
    if target_rows>1:raise NankanError('NANKAN_CHANGE_RACE_ROWS_NOT_UNIQUE')
    if no_changes and target_rows:raise NankanError('NANKAN_CHANGES_NO_CHANGE_NOTICE_CONTRADICTION')
    result.update(items=items,target_race_row_present=bool(target_rows),declared_facts_sha256=sha(declared_facts),
        explicit_no_changes_today_observed=no_changes,
        target_race_change_status=('CHANGE_ITEMS_OBSERVED' if items else
                                  'EXPLICIT_NO_CHANGES_TODAY' if no_changes else 'UNKNOWN'),
        provider_display_at=provider_at.isoformat() if provider_at else None,
        provider_display_time_status='OBSERVED' if provider_at else 'UNKNOWN',
        absence_is_no_change_authority=False)
    result['sha256']=sha(result);return result


def parse_provider_statistics(raw,race,receipt,declared_facts):
    """Preserve provider-labelled statistics without creating index scores.

    The displayed count/rate pairs and sire-analysis labels are observations.
    A missing period or denominator stays unknown; no BVI/JTI transformation
    or addition to an existing forecast is performed here.
    """
    url=ORIGIN+'/uma_shosai/'+race['provider_race_id']+'.do'
    result=_unsigned_current_observation(raw,race,receipt,url,'PRIVATE_UNSIGNED_PROVIDER_STATISTICS')
    declared=_declared_current_facts(race,declared_facts)
    observed=parse_card(raw,race,url)
    if sha(observed)!=sha(declared_facts):raise NankanError('NANKAN_STATISTICS_DECLARED_FACTS_MISMATCH')
    verify_history_asof(observed,result['source_fetched_at'])
    dom=DOM(decode(raw)).root
    table=one([node for node in dom.all('table','tb-shousai') if node.attrs.get('id')!='tb-sample'
        and 'hidden' not in node.attrs.get('class','').split()],'NANKAN_ACTUAL_HISTORY_TABLE_REQUIRED')
    body=one(table.all('tbody'),'NANKAN_ACTUAL_HISTORY_BODY_REQUIRED')

    def definition(cls):
        nodes=table.all('th',cls)
        if len(nodes)>1:raise NankanError('NANKAN_STATISTICS_DEFINITION_NOT_UNIQUE')
        return nodes[0].text() if nodes else None

    def percentage(text):
        match=re.fullmatch(r'(\d+(?:\.\d+)?)%',text)
        if not match:return None,None
        value=float(match[1])
        if not 0<=value<=100:raise NankanError('NANKAN_STATISTICS_RATE_RANGE_HOLD')
        precision=len(match[1].split('.')[1]) if '.' in match[1] else 0
        return value,0.5*10**-precision

    def count_rate(row,cls,meaning):
        cells=row.all('td',cls)
        if len(cells)>1:raise NankanError('NANKAN_STATISTICS_CELL_NOT_UNIQUE')
        cell=cells[0] if cells else None
        out={'provider_definition':meaning,'target_period':None,
            'target_period_status':'UNKNOWN_NOT_PRINTED_IN_STATISTICS_FIELD',
            'displayed_text':cell.text() if cell else None,'win_rate_percent':None,
            'wins':None,'starts':None,'count_rate_consistency':'UNKNOWN','missingness':[]}
        if not cell:
            out['missingness']=['PROVIDER_STATISTICS_FIELD_NOT_PRESENT'];return out
        values={}
        for name,selector in (('rate','is-percent'),('wins','is-number'),('starts','is-total')):
            nodes=cell.all('span',selector)
            if len(nodes)>1:raise NankanError('NANKAN_STATISTICS_VALUE_NOT_UNIQUE')
            values[name]=nodes[0].text() if nodes else ''
        rate,tolerance=percentage(values['rate']);out['win_rate_percent']=rate
        for key in ('wins','starts'):
            if re.fullmatch(r'\d+',values[key]):out[key]=int(values[key])
            elif re.fullmatch(r'-\d+',values[key]):raise NankanError('NANKAN_STATISTICS_COUNT_RANGE_HOLD')
        wins,starts=out['wins'],out['starts']
        if wins is not None and starts is not None:
            if not 0<=wins<=starts:raise NankanError('NANKAN_STATISTICS_COUNT_RANGE_HOLD')
            if starts==0:
                if rate not in (None,0):raise NankanError('NANKAN_STATISTICS_COUNT_RATE_MISMATCH')
                out['count_rate_consistency']='UNDEFINED_ZERO_STARTS'
            elif rate is not None:
                if abs(100*wins/starts-rate)>tolerance+1e-9:raise NankanError('NANKAN_STATISTICS_COUNT_RATE_MISMATCH')
                out['count_rate_consistency']='MATCHES_DISPLAY_PRECISION'
        if rate is None:out['missingness'].append('WIN_RATE_UNKNOWN')
        if wins is None:out['missingness'].append('WINS_UNKNOWN')
        if starts is None:out['missingness'].append('STARTS_UNKNOWN')
        return out

    course_definition=definition('cs-ai1');stable_definition=definition('cs-ai2')
    sire_headers=table.all('th','cs-anl')
    sire_definitions=[node.text() for node in sire_headers if '勝率/連対率' in node.text()]
    if len(sire_definitions)>1:raise NankanError('NANKAN_SIRE_STATISTICS_DEFINITION_NOT_UNIQUE')
    label_sets=[]
    for node in sire_headers:
        lines=[];parts=[]
        for child in node.children:
            if isinstance(child,Node) and child.tag=='br':
                if norm(''.join(parts)):lines.append(norm(''.join(parts)))
                parts=[]
            else:parts.append(child.text() if isinstance(child,Node) else child)
        if norm(''.join(parts)):lines.append(norm(''.join(parts)))
        if lines and all(re.fullmatch(r'[^\s%/]*\d{3,4}',line) for line in lines):label_sets.append(lines)
    if len(label_sets)>1:raise NankanError('NANKAN_SIRE_STATISTICS_LABELS_NOT_UNIQUE')
    labels=label_sets[0] if label_sets else []
    if len(set(labels))!=len(labels):raise NankanError('NANKAN_SIRE_STATISTICS_LABELS_NOT_UNIQUE')
    rows=[]
    for row in [node for node in body.children if isinstance(node,Node) and node.tag=='tr']:
        rid=one(row.all('td','umaban'),'NANKAN_HORSE_NUMBER_REQUIRED').text()
        original=declared.get(rid)
        if not original:raise NankanError('NANKAN_STATISTICS_DECLARED_IDENTITY_MISMATCH')
        analysis={'provider_definition':sire_definitions[0] if sire_definitions else None,
            'target_period':None,'target_period_status':'UNKNOWN_NOT_PRINTED_IN_STATISTICS_FIELD',
            'sample_count':None,'sample_count_status':'UNKNOWN_NOT_PRINTED_IN_STATISTICS_FIELD',
            'conditions':[],'missingness':[]}
        cells=row.all('td','mk-sire')
        if len(cells)>1:raise NankanError('NANKAN_SIRE_STATISTICS_CELL_NOT_UNIQUE')
        if cells:
            if not labels or not sire_definitions:raise NankanError('NANKAN_SIRE_STATISTICS_LABELS_REQUIRED')
            rates=cells[0].all('p','is-grPercent__item')
            if len(rates)!=2:raise NankanError('NANKAN_SIRE_STATISTICS_RATE_ROWS_REQUIRED')
            win_rates,quinella_rates=[node.text().split() for node in rates]
            if len(win_rates)!=len(labels) or len(quinella_rates)!=len(labels):
                raise NankanError('NANKAN_SIRE_STATISTICS_LABEL_RATE_MISMATCH')
            for label,win,quinella in zip(labels,win_rates,quinella_rates):
                wr,_=percentage(win);qr,_=percentage(quinella)
                if wr is not None and qr is not None and wr>qr:raise NankanError('NANKAN_SIRE_STATISTICS_RATE_ORDER_HOLD')
                analysis['conditions'].append({'provider_label':label,'win_rate_percent':wr,'quinella_rate_percent':qr,
                    'win_rate_display':win,'quinella_rate_display':quinella})
                if wr is None or qr is None:analysis['missingness'].append('RATE_UNKNOWN:'+label)
        else:analysis['missingness']=['PROVIDER_SIRE_STATISTICS_FIELD_NOT_PRESENT']
        rows.append({'runner_id':rid,'name':original['name'],'provider_horse_id':original['provider_horse_id'],
            'rider_course':count_rate(row,'cs-ai1',course_definition),
            'rider_trainer':count_rate(row,'cs-ai2',stable_definition),'sire_analysis':analysis})
    result.update(runners=rows,runner_count=len(rows),declared_facts_sha256=sha(declared_facts),
        canonical_index_transform_applied=False,forecast_recalculation_performed=False)
    result['sha256']=sha(result);return result


def compile_private_reference(evidence,*,now=None):
    from runtime.local_production_static_owner import _runner_facts
    now=now or utcnow();race=evidence['race'];cutoff=datetime.fromisoformat(race['prediction_cutoff'])
    if evidence.get('provider')!=PROVIDER or evidence.get('sha256')!=sha({k:v for k,v in evidence.items() if k!='sha256'}):
        raise NankanError('NANKAN_REFERENCE_EVIDENCE_HASH_OR_PROVIDER')
    if not datetime.fromisoformat(evidence['source_frozen_at'])<=now<cutoff:raise NankanError('NANKAN_REFERENCE_CUTOFF_HOLD')
    race_day=datetime.fromisoformat(race['race_date']+'T00:00:00+09:00')
    facts={r['runner_id']:_runner_facts(r,venue_name='浦和',distance=race['distance'],race_day=race_day) for r in evidence['runners']}
    def key(rid):return tuple(-float(facts[rid][name]) if facts[rid][name] is not None else 0 for name in (
        'exact_wins','exact_podiums','exact_best_finish_share','venue_best_finish_share','recent_dirt_finish_share','dirt_best_finish_share'))
    ordered=sorted([r['runner_id'] for r in evidence['runners'] if r['status']!='CANCELLED'],key=lambda rid:(key(rid),int(rid)))
    ranked=[rid for rid in ordered if facts[rid]['exact_races']];ranks={};previous=None
    for index,rid in enumerate(ranked,1):
        if key(rid)!=previous:rank=index
        ranks[rid]=rank;previous=key(rid)
    result={'profile':PROFILE,'provider':PROVIDER,'race':race,'input_sha256':evidence['sha256'],'frozen_at':now.isoformat(),
        'parser_sha256':evidence['parser_sha256'],'method_components_sha256':sha({'runner_facts':inspect.getsource(_runner_facts),'order':inspect.getsource(compile_private_reference)}),
        'reference_ranking':ranked,'unknown_runner_ids':[rid for rid in ordered if rid not in ranks],
        'runners':[{**row,'reference_rank':ranks.get(row['runner_id']),'facts':facts[row['runner_id']]} for row in evidence['runners']],
        'formal_final_proven':False,'production_authority':False,'krs_executed':False,'canonical_tickets':None,
        'public_redistribution_authorized':False,'user_delivery_verified':False,
        'model_sha256':None,'model_sha256_status':'NO_FITTED_MODEL_OBSERVED_RECORD_COMPARATOR_ONLY',
        'observation_mode':evidence['observation_mode'],'temporal_class':evidence['temporal_class']}
    result['sha256']=sha(result);return result


def verify_history_asof(runners,card_fetched_at):
    fetched=datetime.fromisoformat(card_fetched_at)
    if fetched.tzinfo is None:raise NankanError('NANKAN_CAPTURE_TIMEZONE_REQUIRED')
    captured_day=fetched.astimezone(JST).date()
    if any(datetime.strptime(start['date'],'%y.%m.%d').date()>captured_day
           for row in runners for start in (row['starts']+
               [x['record'] for x in row.get('history_observations',[]) if x['record'] is not None])):
        raise NankanError('NANKAN_HISTORY_AFTER_ACTUAL_CAPTURE_FORBIDDEN')


def render_private_reference(evidence,prediction):
    race=evidence['race'];lines=[f"REFERENCE ONLY / PRIVATE：{race['race_date']} 浦和{race['race_no']}R {race['race_name']}",
        f"浦和ダート{race['distance']}m／発走予定{race['scheduled_post_at']}／参考締切{race['prediction_cutoff']}",
        'FORMAL未成立。NANKAN独立参考情報。正式指数・Static・KRS・Signed FINAL・購入認可ではありません。',
        '実行区分：'+evidence['observation_mode'],
        f"取得凍結：{evidence['source_frozen_at']}／参考生成：{prediction['frozen_at']}",
        '|馬番|馬名|参考評価|根拠・条件差・UNKNOWN|','|---|---|---|---|']
    leaders=[]
    for row in prediction['runners']:
        rid=row['runner_id'];facts=row['facts'];latest=row['starts'][0] if row['starts'] else None
        ground=(f"直近{latest['date']} {latest['venue']} {latest['distance'] or 'UNKNOWN'}m {latest['finish'] or 'UNKNOWN'}/{latest['field_size'] or 'UNKNOWN'}着、通過{latest['content_positions'] or 'UNKNOWN'}。" if latest else '近走UNKNOWN。')
        ground+=f"直近取得走内の浦和同距離{facts['exact_races']}走、1着{facts['exact_wins']}回・3着内{facts['exact_podiums']}回。"
        if latest and latest['distance'] is not None:ground+=f"距離変更{race['distance']-latest['distance']:+}m。"
        ground+='当日Active未検証・オッズUNKNOWN。'
        if isinstance(row.get('current_body_weight'),int):
            ground+=f"出馬表の馬体重{row['current_body_weight']}kg"
            change=row.get('current_body_weight_change')
            ground+=(f"（増減{change:+}kg）。" if isinstance(change,int) else '（増減UNKNOWN）。')
        else:ground+='馬体重UNKNOWN。'
        ground+=('同場同距離の比較根拠不足。' if row['reference_rank'] is None else '')
        ground+='出走状態：'+row['status']+'（取消の確定は明示表示分のみ）。'
        if row['missingness']:ground+='欠測：'+','.join(row['missingness'])+'。'
        label='取消・除外' if row['status']=='CANCELLED' else str(row['reference_rank'])+'位' if row['reference_rank'] else 'UNKNOWN'
        lines.append(f"|{rid}|{row['name']}|{label}|{ground}|")
        if row['status']!='CANCELLED' and latest and latest['content_positions'] and latest['content_positions'][0]<=3:leaders.append(rid)
    names={r['runner_id']:r['name'] for r in prediction['runners']}
    ranks={r['runner_id']:r['reference_rank'] for r in prediction['runners']}
    tops=[rid for rid in prediction['reference_ranking'] if ranks[rid] is not None and ranks[rid]<=3]
    lines+=['展開見立て：'+('近走で前方通過の確認できる'+','.join(leaders)+'番が位置取得候補。競合時の消耗と位置維持は未確定。' if leaders else '先行位置の根拠不足によりUNKNOWN。'),
        '参考上位：'+('、'.join(rid+'番'+names[rid] for rid in tops) if tops else '比較可能な同場同距離根拠不足のためUNKNOWN'),
        '不確実性：直近最大5走の観測順位であり、較正勝率ではありません。全キャリア、未観測の当日変更・馬場、表示後の更新は未確認。馬体重は取得時点の出馬表表示です。UNKNOWNは能力不足を意味しません。',
        '出典：'+evidence['sources'][-1]['url'],f"Evidence SHA：{evidence['sha256']}／Parser SHA：{evidence['parser_sha256']}",
        f"Method SHA：{prediction['method_components_sha256']}",
        '最終結論：'+('参考上位を中心に条件適合を比較します。' if tops else '順位確定に必要な同条件根拠が不足しています。')+'正式予測は未成立。REFERENCE ONLY・私的利用限定です。']
    return '\n\n'.join(lines)+'\n'


def validate_checkpoint(folder,evidence,prediction,body,parts,day,number):
    """Validate frozen records/parts; never fetch, re-rank or re-render a forecast."""
    race=evidence['race']
    for record in (evidence,prediction):
        if (record.get('sha256')!=sha({k:v for k,v in record.items() if k!='sha256'})
                or record.get('profile')!=PROFILE or record.get('provider')!=PROVIDER
                or record['race']!=race or race['race_date']!=day or race['race_no']!=number
                or race.get('venue_id')!='URW' or not race['provider_race_id'].startswith(day.replace('-','')+'18')
                or not race['provider_race_id'].endswith(f'{number:02d}')):
            raise NankanError('NANKAN_READBACK_BINDING_HOLD')
    if (any(evidence.get(key) is not False for key in ('formal_source_claim','signed_source_claim','production_authority','public_redistribution_authorized'))
            or any(prediction.get(key) is not False for key in ('formal_final_proven','production_authority','krs_executed','public_redistribution_authorized','user_delivery_verified'))
            or prediction.get('canonical_tickets') is not None):raise NankanError('NANKAN_NONFORMAL_BOUNDARY_HOLD')
    before=datetime.fromisoformat(evidence['source_frozen_at']);frozen=datetime.fromisoformat(prediction['frozen_at'])
    completed=datetime.fromisoformat(prediction['generation_completed_at']);cutoff=datetime.fromisoformat(race['prediction_cutoff'])
    post=datetime.fromisoformat(race['scheduled_post_at'])
    times=[datetime.fromisoformat(source['fetched_at']) for source in evidence['sources']]
    if (any(point.tzinfo is None for point in [*times,before,frozen,completed,cutoff,post])
            or times!=sorted(times) or not max(times)<=before<=frozen<=completed<cutoff<post
            or prediction['observation_mode']!=evidence['observation_mode'] or prediction['temporal_class']!=evidence['temporal_class']):
        raise NankanError('NANKAN_READBACK_TEMPORAL_HOLD')
    if prediction['input_sha256']!=evidence['sha256'] or parts.get('input_sha256')!=evidence['sha256'] or parts.get('forecast_sha256')!=prediction['sha256']:
        raise NankanError('NANKAN_READBACK_INPUT_HOLD')
    if (prediction.get('model_sha256') is not None
            or prediction.get('model_sha256_status')!='NO_FITTED_MODEL_OBSERVED_RECORD_COMPARATOR_ONLY'):
        raise NankanError('NANKAN_MODEL_CLASSIFICATION_HOLD')
    expected_program=ORIGIN+'/program/'+race['provider_day_id']+'.do'
    expected_card=ORIGIN+'/uma_shosai/'+race['provider_race_id']+'.do'
    if (evidence['sources'][0]['url']!=CALENDAR or evidence['sources'][1]['url']!=expected_program
            or evidence['sources'][2].get('source_url')!=ORIGIN+'/syousai/'+race['provider_race_id']+'.do'
            or evidence['sources'][2].get('http_status')!=302 or evidence['sources'][2].get('location')!=expected_card
            or evidence['sources'][3]['url']!=expected_card):raise NankanError('NANKAN_READBACK_SOURCE_IDENTITY_HOLD')
    for source in evidence['sources']:reference_metadata(source)
    evrows=evidence['runners'];prrows=prediction['runners']
    verify_history_asof(evrows,evidence['sources'][3]['fetched_at'])
    # Bind the explicit scratch set to the immutable pre-cutoff raw card,
    # not merely to a self-hashed evidence JSON or a post-race result.
    # Legacy freezes predate this witness and retain their original parser's
    # facts. Reinterpreting them with newly added fields changes the record.
    if 'explicit_card_exclusions' in evidence:
        card_path=folder/'card.html.gz'
        if card_path.is_symlink():raise NankanError('NANKAN_PRIVATE_RAW_PATH_HOLD')
        card_bytes=gzip.decompress(card_path.read_bytes())
        observed_exclusions=[]
        observed_rows=parse_card(card_bytes,race,expected_card,excluded_rows=observed_exclusions)
        identity=lambda rows:[{key:row[key] for key in ('runner_id','name','provider_horse_id','status')} for row in rows]
        if (identity(observed_rows)!=identity(evrows)
                or evidence['explicit_card_exclusions']!=observed_exclusions):
            raise NankanError('NANKAN_SCRATCH_RAW_REPLAY_MISMATCH')
    if ([{key:row[key] for key in ('runner_id','name','status')} for row in evrows]
            !=[{key:row[key] for key in ('runner_id','name','status')} for row in prrows]
            or len(evrows)!=race['program_runner_count'] or len({r['runner_id'] for r in evrows})!=len(evrows)):
        raise NankanError('NANKAN_READBACK_RUNNER_UNIVERSE_HOLD')
    unknown=[];ranked=[]
    for original,row in zip(evrows,prrows):
        if {key:row[key] for key in original}!=original:raise NankanError('NANKAN_READBACK_RUNNER_FACTS_HOLD')
        label='取消・除外' if row['status']=='CANCELLED' else str(row['reference_rank'])+'位' if row['reference_rank'] else 'UNKNOWN'
        if f"|{row['runner_id']}|{row['name']}|{label}|" not in body:raise NankanError('NANKAN_READBACK_RUNNER_ROW_HOLD')
        if row['status']!='CANCELLED':
            (unknown if row['reference_rank'] is None else ranked).append(row['runner_id'])
        if (row['reference_rank'] is None)!=(row['facts']['exact_races']==0) and row['status']!='CANCELLED':
            raise NankanError('NANKAN_READBACK_UNKNOWN_MAPPING_HOLD')
        if any(datetime.strptime(start['date'],'%y.%m.%d').date()>=date.fromisoformat(day) for start in row['starts']):
            raise NankanError('NANKAN_POST_RACE_HISTORY_FORBIDDEN')
    if set(unknown)!=set(prediction['unknown_runner_ids']) or set(ranked)!=set(prediction['reference_ranking']):raise NankanError('NANKAN_READBACK_RANKING_UNIVERSE_HOLD')
    if (not isinstance(parts.get('required_parts'),list) or not parts['required_parts']
            or any(part not in body for part in parts['required_parts'])
            or any(word not in body for word in ('REFERENCE ONLY','展開見立て','参考上位','不確実性','最終結論'))):
        raise NankanError('NANKAN_READBACK_INCOMPLETE_HOLD')
    for source,name in zip((evidence['sources'][0],evidence['sources'][1],evidence['sources'][3]),('calendar.html.gz','program.html.gz','card.html.gz')):
        file=folder/name
        if file.is_symlink() or source.get('private_raw_path')!=name or source.get('http_status')!=200:
            raise NankanError('NANKAN_PRIVATE_RAW_PATH_HOLD')
        try:raw=gzip.decompress(file.read_bytes())
        except (OSError,EOFError,ValueError) as exc:raise NankanError('NANKAN_PRIVATE_RAW_INTEGRITY_HOLD') from exc
        if hashlib.sha256(raw).hexdigest()!=source['raw_sha256']:raise NankanError('NANKAN_PRIVATE_RAW_INTEGRITY_HOLD')


def publication_for(evidence,prediction,body,parts):
    result={'profile':PROFILE,'provider':PROVIDER,'race':evidence['race'],'input_sha256':evidence['sha256'],
        'forecast_sha256':prediction['sha256'],'answer_sha256':hashlib.sha256(body.encode()).hexdigest(),
        'answer_parts_sha256':sha(parts),'frozen_at':prediction['frozen_at'],'completed_at':prediction['generation_completed_at'],
        'observation_mode':evidence['observation_mode'],'temporal_class':evidence['temporal_class'],
        'runner_count':len(evidence['runners']),'formal_final_proven':False,'chat_render_verified':False,
        'public_redistribution_authorized':False,'source_scope':'PRIVATE_ORIGINAL_AND_DERIVED_ANSWER'}
    result['sha256']=sha(result);return result


def readback(output,day,number,*,resume=False):
    folder=private_directory(output)
    for name in ('reference_evidence.json','reference_prediction.json','readback.txt','answer_parts.json','publication.json'):
        if (folder/name).is_symlink():raise NankanError('NANKAN_PRIVATE_SYMLINK_OUTPUT_FORBIDDEN')
    evidence=json.loads((folder/'reference_evidence.json').read_text());prediction=json.loads((folder/'reference_prediction.json').read_text())
    body=(folder/'readback.txt').read_text();parts=json.loads((folder/'answer_parts.json').read_text())
    validate_checkpoint(folder,evidence,prediction,body,parts,day,number)
    expected=publication_for(evidence,prediction,body,parts)
    if resume and not (folder/'publication.json').exists():save_json(folder/'publication.json',expected)
    manifest=json.loads((folder/'publication.json').read_text())
    if manifest!=expected:raise NankanError('NANKAN_PUBLICATION_HASH_OR_BOUNDARY_HOLD')
    return manifest,evidence,prediction,body


def freeze_observations(folder,day,number,sources,raws,*,now=None,clock=utcnow,
                        observation_mode='REPLAY_REFERENCE_FROM_ALREADY_FETCHED_PRIVATE_BYTES'):
    folder=private_directory(folder);now=now or clock()
    sources=[reference_metadata(source) for source in sources]
    program=program_link(raws[0],day)
    if sources[0]['url']!=CALENDAR or sources[1]['url']!=program:raise NankanError('NANKAN_OBSERVED_LINK_CHAIN_REQUIRED')
    races=parse_program(raws[1],program,day);race=next((r for r in races if r['race_no']==number),None)
    if race is None:raise NankanError('NANKAN_RACE_NOT_IN_OFFICIAL_PROGRAM')
    if (date.fromisoformat(day)<now.astimezone(JST).date() or now>=datetime.fromisoformat(race['prediction_cutoff'])
            or any(datetime.fromisoformat(s['fetched_at'])>now for s in sources)):
        raise NankanError('NANKAN_REFERENCE_PRESTART_ONLY')
    if len(sources)!=4 or len(raws)!=3 or any(s.get('http_status')!=200 for s in (sources[0],sources[1],sources[3])):
        raise NankanError('NANKAN_OBSERVATION_HTTP_HOLD')
    canonical=ORIGIN+'/uma_shosai/'+race['provider_race_id']+'.do'
    redirect=sources[2]
    if (redirect.get('http_status')!=302 or redirect.get('source_url')!=race['observed_card_url']
            or redirect.get('location')!=canonical or sources[3]['url']!=canonical):raise NankanError('NANKAN_CANONICAL_TRANSITION_HOLD')
    excluded=[]
    runners=parse_card(raws[2],race,canonical,excluded_rows=excluded)
    verify_history_asof(runners,sources[3]['fetched_at'])
    for index,(source,raw) in enumerate(zip((sources[0],sources[1],sources[3]),raws)):
        if source['raw_sha256']!=hashlib.sha256(raw).hexdigest():raise NankanError('NANKAN_OBSERVATION_HASH_HOLD')
        name=('calendar','program','card')[index]+'.html.gz';immutable(folder/name,gzip.compress(raw,mtime=0))
        source['private_raw_path']=name
    evidence={'profile':PROFILE,'provider':PROVIDER,'race':race,'sources':sources,'runners':runners,
        'explicit_card_exclusions':excluded,
        'source_frozen_at':now.isoformat(),'parser_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'formal_source_claim':False,'signed_source_claim':False,'production_authority':False,
        'public_redistribution_authorized':False,'page_update_time_claim':'UNKNOWN_NOT_FETCH_TIME',
        'listed_runner_count':len(runners),'active_verified':False,'observation_mode':observation_mode,
        'temporal_class':'ACTUAL_UTC_COMPLETION_CHECKED_PRIVATE_ONLY' if clock is utcnow else 'INJECTED_CLOCK_CONTRACT_TEST'}
    evidence['sha256']=sha(evidence);prediction=compile_private_reference(evidence,now=clock())
    body=render_private_reference(evidence,prediction)
    completed=clock()
    if completed>=datetime.fromisoformat(race['prediction_cutoff']):raise NankanError('NANKAN_REFERENCE_COMPLETED_AFTER_CUTOFF')
    prediction['generation_completed_at']=completed.isoformat();prediction['sha256']=sha({k:v for k,v in prediction.items() if k!='sha256'})
    parts={'input_sha256':evidence['sha256'],'forecast_sha256':prediction['sha256'],'required_parts':body.rstrip('\n').split('\n\n')}
    validate_checkpoint(folder,evidence,prediction,body,parts,day,number)
    publication=publication_for(evidence,prediction,body,parts)
    save_json(folder/'reference_evidence.json',evidence);save_json(folder/'reference_prediction.json',prediction)
    immutable(folder/'readback.txt',body.encode());save_json(folder/'answer_parts.json',parts);save_json(folder/'publication.json',publication)
    return readback(folder,day,number)


def capture_race(day,number,output,*,client=None,now=utcnow,prediction_cutoff=None,refresh=False):
    folder=private_directory(output)
    with private_lock(folder/'worker.lock') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        return _capture_locked(day,number,folder,client=client,now=now,prediction_cutoff=prediction_cutoff,refresh=refresh)


def _capture_locked(day,number,folder,*,client,now,prediction_cutoff,refresh=False):
    prior=None
    if (folder/'publication.json').exists():
        prior=readback(folder,day,number)
        if not refresh:return prior
        if now()>=datetime.fromisoformat(prior[0]['race']['prediction_cutoff']):
            raise NankanError('NANKAN_REFERENCE_CUTOFF_HOLD')
    checkpoints=('reference_evidence.json','reference_prediction.json','readback.txt','answer_parts.json')
    if not prior and all((folder/name).exists() for name in checkpoints):
        prior=readback(folder,day,number,resume=True)
        if not refresh:return prior
        if now()>=datetime.fromisoformat(prior[0]['race']['prediction_cutoff']):
            raise NankanError('NANKAN_REFERENCE_CUTOFF_HOLD')
    if not prior and any((folder/name).exists() for name in (*checkpoints,'calendar.html.gz','program.html.gz','card.html.gz')):
        raise NankanError('NANKAN_PARTIAL_PRIVATE_CAPTURE_HOLD_NO_REGENERATION')
    if prediction_cutoff and now()>=datetime.fromisoformat(prediction_cutoff):raise NankanError('NANKAN_REFERENCE_CUTOFF_HOLD')
    if date.fromisoformat(day)<now().astimezone(JST).date() or type(number) is not int or not 1<=number<=12:
        raise NankanError('NANKAN_REFERENCE_CURRENT_OR_FUTURE_URW_REQUIRED')
    client=client or Client();calendar,raw_calendar=client.get(CALENDAR)
    program_url=program_link(raw_calendar,day);program,raw_program=client.get(program_url)
    races=parse_program(raw_program,program_url,day);race=next((r for r in races if r['race_no']==number),None)
    if not race:raise NankanError('NANKAN_RACE_NOT_IN_OFFICIAL_PROGRAM')
    if prediction_cutoff and prediction_cutoff!=race['prediction_cutoff']:raise NankanError('NANKAN_DISCOVERED_CUTOFF_MISMATCH')
    if now()>=datetime.fromisoformat(race['prediction_cutoff']):raise NankanError('NANKAN_REFERENCE_CUTOFF_HOLD')
    try:client.get(race['observed_card_url'])
    except ObservedRedirect as exc:redirect=dict(exc.receipt)
    else:raise NankanError('NANKAN_EXPECTED_SUPPORTED_CANONICAL_TRANSITION_REQUIRED')
    expected=ORIGIN+'/uma_shosai/'+race['provider_race_id']+'.do'
    if (redirect.get('http_status')!=302 or redirect.get('source_url')!=race['observed_card_url']
            or redirect.get('location')!=expected):raise NankanError('NANKAN_CANONICAL_TRANSITION_HOLD')
    url_scope(redirect['location'])
    # This is an explicit, policy-checked GET of the observed Location, not an
    # HTTP library redirect follow or a fabricated URL. A second redirect holds.
    try:card,raw_card=client.get(redirect['location'])
    except ObservedRedirect as exc:raise NankanError('NANKAN_SECOND_REDIRECT_HOLD') from exc
    if refresh:
        # One immutable revision for this race/cutoff/raw observation. The
        # original publication stays intact, including on later readback.
        current=[reference_metadata(s) for s in (calendar,program,redirect,card)]
        observed=now();times=[datetime.fromisoformat(s['fetched_at']) for s in current]
        if (any(t.tzinfo is None for t in times) or times!=sorted(times)
                or max(times)>observed or observed>=datetime.fromisoformat(race['prediction_cutoff'])):
            raise NankanError('NANKAN_CURRENT_OBSERVATION_TIME_HOLD')
        for meta,raw,url in zip((current[0],current[1],current[3]),
                (raw_calendar,raw_program,raw_card),(CALENDAR,program_url,expected)):
            if meta.get('http_status')!=200 or meta.get('url')!=url:
                raise NankanError('NANKAN_OBSERVATION_HTTP_HOLD')
            if hashlib.sha256(raw).hexdigest()!=meta['raw_sha256']:
                raise NankanError('NANKAN_OBSERVATION_HASH_HOLD')
        verify_history_asof(parse_card(raw_card,race,card['url']),card['fetched_at'])
        if prior and (prior[1]['race']==race
                and prior[1]['sources'][3]['raw_sha256']==card['raw_sha256']):return prior
        revisions=private_directory(folder/'revisions')
        key=sha({'provider_race_id':race['provider_race_id'],
                 'prediction_cutoff':race['prediction_cutoff'],'source_sha256':card['raw_sha256']})
        target=revisions/key
        if target.exists():
            if not all((target/name).exists() for name in checkpoints):
                raise NankanError('NANKAN_PARTIAL_PRIVATE_CAPTURE_HOLD_NO_REGENERATION')
            saved=readback(target,day,number,resume=True)
            if saved[1]['race']!=race:raise NankanError('NANKAN_CURRENT_REVISION_RACE_MISMATCH')
            return saved
        if len(list(revisions.iterdir()))>=3:raise NankanError('NANKAN_PRIVATE_REVISION_LIMIT_REACHED')
        folder=private_directory(target)
    return freeze_observations(folder,day,number,[calendar,program,redirect,card],
                               [raw_calendar,raw_program,raw_card],clock=now,
                               observation_mode='COLD_OFFICIAL_SOURCE_PRIVATE_REFERENCE_NOT_FORMAL_NOT_CHAT_DELIVERY')


def capture_day(day,private_root,*,client=None,now=utcnow):
    folder=private_directory(private_directory(private_root)/day)
    with private_lock(folder/'worker.lock') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        return _capture_day_locked(day,private_root,client=client,now=now)


def _capture_day_locked(day,private_root,*,client,now):
    """Reuse one observed calendar/program cohort; isolate each private Race."""
    root=private_directory(private_root);folder=private_directory(root/day);client=client or Client()
    cache={}
    class DayClient:
        def get(self,url):
            shared=url==CALENDAR or re.fullmatch(re.escape(ORIGIN)+r'/program/\d{14}\.do',url)
            if shared and url in cache:
                meta,raw=cache[url];return dict(meta),raw
            result=client.get(url)
            if shared:cache[url]=(dict(result[0]),result[1])
            return result
    shared=DayClient();cohort_path=folder/'cohort.json'
    if any((folder/name).is_symlink() for name in ('cohort.json','calendar.html.gz','program.html.gz')):
        raise NankanError('NANKAN_PRIVATE_SYMLINK_OUTPUT_FORBIDDEN')
    if cohort_path.exists():
        cohort=json.loads(cohort_path.read_text())
        if (cohort.get('sha256')!=sha({k:v for k,v in cohort.items() if k!='sha256'}) or cohort.get('race_date')!=day
                or cohort.get('profile')!=PROFILE or cohort.get('provider')!=PROVIDER or len(cohort.get('sources',[]))!=2):
            raise NankanError('NANKAN_PRIVATE_COHORT_INTEGRITY_HOLD')
        observations=[]
        for meta,name in zip(cohort['sources'],('calendar.html.gz','program.html.gz')):
            reference_metadata(meta)
            raw=gzip.decompress((folder/name).read_bytes())
            if hashlib.sha256(raw).hexdigest()!=meta['raw_sha256']:raise NankanError('NANKAN_PRIVATE_COHORT_INTEGRITY_HOLD')
            cache[meta['url']]=(meta,raw)
            observations.append(raw)
        if (cohort['sources'][0]['url']!=CALENDAR or program_link(observations[0],day)!=cohort['sources'][1]['url']
                or parse_program(observations[1],cohort['sources'][1]['url'],day)!=cohort['races']):
            raise NankanError('NANKAN_PRIVATE_COHORT_IDENTITY_HOLD')
        races=cohort['races']
    else:
        if date.fromisoformat(day)<now().astimezone(JST).date():raise NankanError('NANKAN_REFERENCE_CURRENT_OR_FUTURE_URW_REQUIRED')
        calendar,raw_calendar=shared.get(CALENDAR);program_url=program_link(raw_calendar,day)
        program,raw_program=shared.get(program_url);races=parse_program(raw_program,program_url,day)
        cohort={'profile':PROFILE,'provider':PROVIDER,'race_date':day,'races':races,
                'sources':[reference_metadata(calendar),reference_metadata(program)]}
        cohort['sha256']=sha(cohort)
        immutable(folder/'calendar.html.gz',gzip.compress(raw_calendar,mtime=0));immutable(folder/'program.html.gz',gzip.compress(raw_program,mtime=0));save_json(cohort_path,cohort)
    status={'profile':PROFILE,'provider':PROVIDER,'race_date':day,'cohort_sha256':cohort['sha256'],
        'cohort_race_numbers':[race['race_no'] for race in races],'discovered_count':len(races),'races':[],
        'formal_final_count':0,'chat_render_verified':False,'public_redistribution_authorized':False}
    for race in races:
        try:
            manifest,_,_,_=capture_race(day,race['race_no'],folder/f'R{race["race_no"]:02d}',client=shared,now=now,prediction_cutoff=race['prediction_cutoff'])
            row={'race_no':race['race_no'],'status':'PRIVATE_REFERENCE_COMPLETE','forecast_sha256':manifest['forecast_sha256'],'runner_count':manifest['runner_count']}
        except (NankanError,OSError,ValueError,KeyError) as exc:
            code=exc.receipt['code'] if isinstance(exc,NankanError) else type(exc).__name__
            row={'race_no':race['race_no'],'status':'HOLD','code':code,'first_failed_stage':'DATA_SOURCE_POLICY' if code.startswith('SOURCE_POLICY_') else 'REFERENCE_CAPTURE_OR_READBACK'}
        status['races'].append(row)
    status['reference_complete_count']=sum(row['status']=='PRIVATE_REFERENCE_COMPLETE' for row in status['races'])
    status['observed_at']=now().isoformat();status['sha256']=sha(status)
    path=folder/'status.json';temporary=folder/'status.json.tmp'
    if path.is_symlink() or temporary.is_symlink():raise NankanError('NANKAN_PRIVATE_SYMLINK_OUTPUT_FORBIDDEN')
    with os.fdopen(os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_TRUNC|os.O_NOFOLLOW,0o600),'w') as stream:json.dump(status,stream,sort_keys=True)
    temporary.replace(path);return status


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--race-date',required=True)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--race-no',type=int);group.add_argument('--all-races',action='store_true')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--import-observations',type=Path,
        help='Private JSON record of three already-fetched raw paths and four source receipts; HTTP0 replay')
    parser.add_argument('--refresh-current-official',action='store_true',
        help='Check current official card before cutoff; preserve original and deduplicate private revisions')
    parser.add_argument('--personal-noncommercial-private-only',action='store_true',required=True)
    args=parser.parse_args()
    try:
        if args.refresh_current_official and (args.all_races or args.import_observations):
            raise NankanError('NANKAN_REFRESH_REQUIRES_ONE_CURRENT_OFFICIAL_RACE')
        if args.all_races:
            if args.import_observations:raise NankanError('NANKAN_IMPORT_REQUIRES_ONE_RACE')
            status=capture_day(args.race_date,args.output)
            print(json.dumps({key:status[key] for key in ('provider','race_date','discovered_count','reference_complete_count','formal_final_count','chat_render_verified','sha256')},sort_keys=True))
            return 0 if status['reference_complete_count']==status['discovered_count'] else 2
        if (args.output/'publication.json').exists() and not args.refresh_current_official:
            manifest,_,prediction,_=readback(args.output,args.race_date,args.race_no)
        elif args.import_observations:
            obj=json.loads(args.import_observations.read_text());raws=[]
            for source in obj['raw_gzip_paths']:
                path=Path(source)
                if not path.is_absolute() or path.is_symlink():raise NankanError('NANKAN_IMPORT_PRIVATE_PATH_HOLD')
                raws.append(gzip.decompress(path.read_bytes()))
            manifest,_,prediction,_=freeze_observations(args.output,args.race_date,args.race_no,obj['sources'],raws)
        else:
            manifest,_,prediction,_=capture_race(args.race_date,args.race_no,args.output,refresh=args.refresh_current_official)
        print(json.dumps({'status':'PRIVATE_REFERENCE_COMPLETE_NOT_CHAT_DELIVERED','provider':PROVIDER,
            'race_date':args.race_date,'race_no':args.race_no,'runner_count':manifest['runner_count'],
            'unknown_count':len(prediction['unknown_runner_ids']),'input_sha256':manifest['input_sha256'],
            'forecast_sha256':manifest['forecast_sha256'],'answer_sha256':manifest['answer_sha256'],
            'formal_final_proven':False,'public_redistribution_authorized':False},sort_keys=True));return 0
    except (NankanError,OSError,ValueError,KeyError) as exc:
        print(json.dumps({'status':'HOLD_PRIVATE_REFERENCE','code':exc.receipt['code'] if isinstance(exc,NankanError) else type(exc).__name__,
            'formal_final_proven':False,'public_redistribution_authorized':False},sort_keys=True));return 2


if __name__=='__main__':raise SystemExit(main())

"""Existing bounded private public-card transport, never formal admission.

Exact observed card URLs only, >=61 seconds per origin, no redirect/denial
retry, no app/prediction/detail or NAR fallback. Source credentials and signed
qualification, when actually available, are separate pinned private originals.
"""
from copy import deepcopy
from pathlib import Path
from datetime import datetime,timezone,timedelta
import fcntl,json,os,re
from urllib.parse import urlsplit
import urllib.request,urllib.error

from runtime.local_fnb_r20_chat_completion import ProducerHold
from runtime import local_fnb_research_runtime as common

UA='KeibaMetricsPrivateResearch/0.1 (personal noncommercial research; no wagering)'
ROBOTS_SHA='6f9346b23d28e4fb6b00298546bc30e463a4925a8248e9112018a04ab56641c0'

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None


class BoundedCardProducer:
    def __init__(self, *, root,observed_cards,robots_path,actor_id,reference_scope=None):
        if any(os.environ.get(k,'').lower() not in ('','false','0') for k in ('CI','GITHUB_ACTIONS')):
            raise ProducerHold('SOURCE','PRIVATE_PROVIDER_ACQUISITION_PUBLIC_CI_FORBIDDEN')
        self.root=common._private_root(root);self.cards=observed_cards;self.actor_id=actor_id
        self.robots_path=Path(robots_path)
        self.reference_scope=deepcopy(reference_scope)
    def _capture(self, *, intent, now, expected_url=None):
        require=lambda ok,code:None if ok else (_ for _ in ()).throw(ProducerHold('SOURCE',code))
        day=intent.get('race_date')
        require(intent.get('venue_id')=='FNB', 'BOUNDED_CARD_DATED_SCOPE_NOT_AUTHORIZED')
        if day not in ('2026-11-04','2026-11-05','2026-11-06'):
            # Only the qualified fetch entry can leave the old campaign.
            # Preserve the same origin state and the legacy direct entry's scope.
            scope=self.reference_scope or {}
            require(expected_url is not None and day==scope.get('race_date')
                and scope.get('actor_id')==self.actor_id
                and now.astimezone(timezone(timedelta(hours=9))).date().isoformat()==day
                and common._stamp(scope['effective_from'])<=common._stamp(now)
                    <common._stamp(scope['effective_until']),
                'BOUNDED_CARD_DATED_SCOPE_NOT_AUTHORIZED')
            common._pinned(scope['permission_original_path'],scope['permission_sha256'])
            require((self.root/'LAST_ATTEMPT.json').is_file(),
                'REFERENCE_EXISTING_RAKUTEN_ORIGIN_STATE_REQUIRED')
        key=intent['race_date']+'-R'+str(intent['race_no']).zfill(2);spec=self.cards.get(key) or {}
        url=spec.get('url','');p=urlsplit(url);m=re.fullmatch(r'/race_card/list/RACEID/(\d{18})',p.path)
        require(expected_url is None or expected_url==url,'BOUNDED_EXACT_OBSERVED_CARD_URL_REQUIRED')
        require(p.scheme=='https' and p.netloc=='keiba.rakuten.co.jp' and not p.query and not p.fragment
            and m and m[1][:8]==intent['race_date'].replace('-','') and m[1][8:10]=='19'
            and int(m[1][-2:])==intent['race_no'],'BOUNDED_EXACT_OBSERVED_CARD_URL_REQUIRED')
        require(spec.get('observed_program_raw_sha256') and self.robots_path.is_file()
            and common.digest(self.robots_path.read_bytes())==ROBOTS_SHA,'BOUNDED_OBSERVED_PROGRAM_AND_ROBOTS_REQUIRED')
        require(not (self.root/'PROVIDER_REFUSED_STOP.json').exists(),'SOURCE_PROVIDER_REFUSAL_STOP_NO_RETRY')
        fd=os.open(self.root/'.origin_rate.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
        try:
            fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            rate=self.root/'LAST_ATTEMPT.json'
            if rate.exists():
                previous=json.loads(rate.read_bytes());elapsed=(now-datetime.fromisoformat(previous['attempted_at'])).total_seconds()
                require(elapsed>=61,'SOURCE_PROVIDER_MINIMUM_61_SECOND_INTERVAL')
            from runtime.local_fnb_day_supervisor import put
            put(rate,{'attempted_at':now.isoformat(),'race':key,'url':url,'retries':0})
            request=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'text/html'})
            try:
                with urllib.request.build_opener(_NoRedirect()).open(request,timeout=25) as response:
                    raw=response.read(4_000_001);status=response.status;final=response.url
            except urllib.error.HTTPError as e:
                put(self.root/'PROVIDER_REFUSED_STOP.json',{'http_status':e.code,'observed_at':datetime.now(timezone.utc).isoformat(),
                    'no_retry':True,'race':key,'raw_not_promoted':True})
                raise ProducerHold('SOURCE','SOURCE_PROVIDER_HTTP_FAILURE_STOP_NO_RETRY') from e
            except OSError as e:raise ProducerHold('SOURCE','SOURCE_PROVIDER_TRANSPORT_FAILED_NO_RETRY') from e
            captured_at=datetime.now(timezone.utc)
            require(status==200 and final==url and 0<len(raw)<=4_000_000,'SOURCE_ORIGINAL_RESPONSE_OR_REDIRECT_UNVERIFIED')
            capture={'url':url,'final_url':final,'http_status':status,'sha256':common.digest(raw),'size':len(raw),
                'started_at':now.isoformat(),'completed_at':captured_at.isoformat(),'user_agent':UA,
                'rate_interval_seconds':61,'no_retry':True,'qualified_SOURCE':False,'Active_verified':False}
            tag=common.digest(common.encoded(capture));path=self.root/key/tag;path.mkdir(parents=True,mode=0o700)
            # A parser failure must retain its actual HTTP evidence; otherwise
            # debugging the same Raw requires an unnecessary second request.
            for name,data in [('original.html',raw),('capture.json',common.encoded(capture))]:
                common._immutable(path/name,data)
            return raw,capture,path,tag
        finally:os.close(fd)

    def fetch(self, *, url, intent, now):
        """The existing bounded origin transport for an admitted ProviderBinding."""
        raw,capture,_,_=self._capture(intent=intent,now=now,expected_url=url)
        return {'raw':raw,'http_status':capture['http_status'],'final_url':capture['final_url'],
            'retrieval_method':'HTTPS_GET_ORIGINAL_RESPONSE','content_type':'text/html',
            'captured_at':capture['completed_at'],'access_policy':{'decision':'ALLOW',
                'robots_sha256':ROBOTS_SHA,'user_agent':UA,'rate_interval_seconds':61,
                'no_retry':True,'qualified_SOURCE':False}}

    def __call__(self, *, intent,private_root,now):
        from runtime.local_fnb_rakuten_reference import parse_card
        raw,capture,path,tag=self._capture(intent=intent,now=now)
        captured_at=datetime.fromisoformat(capture['completed_at'])
        parsed=parse_card(raw,capture=capture,race=intent,now=captured_at)
        common._immutable(path/'parsed.json',common.encoded(parsed))
        post=datetime.fromisoformat(parsed['race_identity']['scheduled_post_at'])
        cutoff=post-timedelta(seconds=300)
        if captured_at>=cutoff:
            raise ProducerHold('SOURCE','PRESTART_CUTOFF_EXPIRED_DIAGNOSTIC_REQUIRED')
        rid='KM-LOCAL-FNB-'+intent['race_date'].replace('-','')+'-R'+str(intent['race_no']).zfill(2)+'-ALT-R17-'+tag[:12]
        if intent.get('race_id'):
            if not re.fullmatch(re.escape(rid.split('-ALT-')[0])+r'(?:-[A-Za-z0-9_]+)*',intent['race_id']):
                raise ProducerHold('SOURCE','BOUNDED_DAY_DISCOVERY_REVISION_INVALID')
            rid=intent['race_id']
        race_request={**intent,'family_id':'LOCAL','race_id':rid,'scheduled_post_at':post.isoformat(),
            'prediction_cutoff':cutoff.isoformat(),'race':{'venue':'船橋','distance_m':parsed['race_identity']['distance_m'],
                'surface':parsed['race_identity']['surface'],'direction':'LEFT','class':parsed['race_identity']['race_name']}}
        return {'raw':raw,'capture':capture,'request':race_request,'actor_id':self.actor_id,
            'source_envelope':None,'permission_original':None,'current_state_original':None,
            'private_http_original':str(path/'original.html'),'formal_qualification_not_inferred':True}

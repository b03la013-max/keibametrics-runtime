"""Original public Rakuten card facts -> existing LOCAL research inputs.

No network, SOURCE signature, Provider licence, Active guarantee or Selection
authority is issued here. Provider horse IDs stay in their own namespace.
The unchanged shared numerical consumer owns every score and coefficient.
"""
from __future__ import annotations
from datetime import date, datetime, timezone, timedelta
from html.parser import HTMLParser
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlsplit

PROVIDER = 'RAKUTEN_KEIBA'
PROFILE = 'KM-FNB-RAKUTEN-ORIGINAL-CARD-FACTS-v1-20261104'
CLASSIFICATION = 'PRIVATE_PROVIDER_REFERENCE_NOT_QUALIFIED_SOURCE_NOT_ACTIVE_NOT_OOS'


def compact(s):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', str(s or '')))


class Node:
    def __init__(self, tag='', attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []

    def walk(self):
        for child in self.children:
            if isinstance(child, Node):
                yield child
                yield from child.walk()

    def find(self, tag=None, cls=None):
        return [n for n in self.walk() if (tag is None or n.tag == tag)
                and (cls is None or cls in n.attrs.get('class', '').split())]

    def chunks(self):
        for child in self.children:
            if isinstance(child, str):
                if child.strip(): yield child.strip()
            elif child.tag not in ('script', 'style'):
                yield from child.chunks()

    def text(self):
        return ' '.join(self.chunks())


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.root = Node(); self.stack = [self.root]
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs); self.stack[-1].children.append(n)
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:
            self.stack.append(n)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(Node(tag, attrs))

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]; break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def one(nodes, code):
    if len(nodes) != 1: raise ValueError('RAKUTEN_' + code + '_AMBIGUOUS')
    return nodes[0]


def _stamp(s):
    t = datetime.fromisoformat(str(s).replace('Z','+00:00'))
    if t.tzinfo is None: raise ValueError('RAKUTEN_AWARE_TIME_REQUIRED')
    return t


def parse_card(raw, *, capture, race, now=None):
    """Reparse raw bytes, observed header and row-local history; no name joins."""
    if not isinstance(raw, bytes) or not 0 < len(raw) <= 4_000_000:
        raise ValueError('RAKUTEN_ORIGINAL_BYTE_LIMIT')
    digest = hashlib.sha256(raw).hexdigest()
    url = capture.get('source_url', capture.get('url'))
    p = urlsplit(str(url)); match = re.fullmatch(r'/race_card/list/RACEID/(\d{18})',p.path)
    if (p.scheme != 'https' or p.netloc != 'keiba.rakuten.co.jp' or p.query or p.fragment
            or not match or capture.get('http_status') != 200
            or capture.get('raw_sha256',capture.get('sha256')) != digest
            or capture.get('final_url',url) != url):
        raise ValueError('RAKUTEN_ORIGINAL_CAPTURE_URL_OR_HASH_INVALID')
    day = date.fromisoformat(race['race_date']); number = race['race_no']
    if type(number) is not int or not 1 <= number <= 12 or race.get('venue_id') != 'FNB':
        raise ValueError('RAKUTEN_FNB_RACE_IDENTITY_REQUIRED')
    ident = match[1]
    if ident[:8] != day.strftime('%Y%m%d') or ident[8:10] != '19' or int(ident[-2:]) != number:
        raise ValueError('RAKUTEN_URL_RACE_IDENTITY_CONFLICT')
    captured = _stamp(capture.get('captured_at',capture.get('completed_at')))
    observed = now or datetime.now(timezone.utc)
    if captured > observed: raise ValueError('RAKUTEN_CAPTURE_IN_FUTURE')
    root = Document(raw.decode('utf-8',errors='strict')).root
    heading = one(root.find('h1'),'HEADING').text()
    if compact(heading) != f'船橋競馬場{number}R出馬表':
        raise ValueError('RAKUTEN_OBSERVED_RACE_NUMBER_CONFLICT')
    note = one(root.find(cls='raceNote'),'RACE_NOTE')
    text = compact(note.text())
    if f'{day.year}年{day.month}月{day.day}日' not in text or '船橋競馬' not in text:
        raise ValueError('RAKUTEN_OBSERVED_DATE_VENUE_CONFLICT')
    dm = re.search(r'([ダ芝])([\d,]+)m',text)
    tm = re.search(r'発走時刻(\d{1,2}):(\d{2})',text)
    if not dm or not tm: raise ValueError('RAKUTEN_POST_DISTANCE_UNOBSERVED')
    post = datetime.combine(day,datetime.min.time(),tzinfo=timezone(timedelta(hours=9))).replace(hour=int(tm[1]),minute=int(tm[2]))
    if captured >= post or observed >= post:
        raise ValueError('RAKUTEN_FUTURE_CARD_REFERENCE_REQUIRED')
    identity = {'venue_id':'FNB','race_date':day.isoformat(),'race_no':number,
        'distance_m':int(dm[2].replace(',','')),'surface':{'ダ':'DIRT','芝':'TURF'}[dm[1]],
        'scheduled_post_at':post.isoformat(), 'race_name':one(note.find('h2'),'RACE_NAME').text()}
    for key in ('distance_m','surface'):
        if race.get(key) is not None and race[key] != identity[key]:
            raise ValueError('RAKUTEN_INTENT_CONDITION_CONFLICT_'+key.upper())
    if race.get('scheduled_post_at') and _stamp(race['scheduled_post_at']) != post:
        raise ValueError('RAKUTEN_POST_INTENT_CONFLICT')
    body = one(root.find('tbody','raceCard'),'CARD_BODY')
    rows = [n for n in body.children if isinstance(n,Node) and n.tag=='tr'
            and any(c.attrs.get('class')=='number' for c in n.children if isinstance(c,Node))]
    runners=[]; prior_frame=None
    for row in rows:
        cells=[c for c in row.children if isinstance(c,Node) and c.tag in ('th','td')]
        def cell(cls): return one([c for c in cells if cls in c.attrs.get('class','').split()],cls.upper())
        rid=int(compact(cell('number').text()))
        frame=[c for c in cells if 'position' in c.attrs.get('class','').split()]
        if frame: prior_frame=int(compact(one(frame,'FRAME').text()))
        if prior_frame is None: raise ValueError('RAKUTEN_FRAME_SPAN_UNRESOLVED')
        namecell=cell('name'); main=one(namecell.find(cls='mainHorse'),'HORSE_NAME')
        name=main.text(); link=one(main.find('a'),'HORSE_LINK').attrs.get('href','')
        hm=re.fullmatch(r'https://keiba\.rakuten\.co\.jp/horse_detail/detail/HORSEID/(\d+)',link)
        if not hm: raise ValueError('RAKUTEN_PROVIDER_NATIVE_ID_UNOBSERVED')
        direct=[x.strip() for x in namecell.children if isinstance(x,str) and x.strip()]
        if len(direct)!=2: raise ValueError('RAKUTEN_PARENT_NAMES_AMBIGUOUS')
        append=one(namecell.find(cls='append'),'HORSE_APPEND'); append_text=list(append.chunks())
        damsire=re.fullmatch(r'[(（](.*)[)）]',append_text[0])
        dob=re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})生',append.text())
        if not damsire or not dob: raise ValueError('RAKUTEN_DOB_DAMSIRE_UNOBSERVED')
        dob=date(*(int(x) for x in dob.groups())).isoformat()
        profile=cell('profile'); parts=list(profile.chunks())
        sexage=re.fullmatch(r'([牡牝セ騸])(\d+)',compact(parts[0]))
        load=re.fullmatch(r'\d+(?:\.\d+)?',compact(parts[2]))
        if not sexage or not load: raise ValueError('RAKUTEN_SEX_AGE_LOAD_UNOBSERVED')
        jockey_anchor=one(profile.find('a'),'JOCKEY')
        jockey=jockey_anchor.text()
        jockey_url=jockey_anchor.attrs.get('href','')
        jm=re.fullmatch(r'https://keiba\.rakuten\.co\.jp/jockey/detail/JOCKEYID/(\d+)',jockey_url)
        weight=compact(cell('weightDistance').text()); bw=re.fullmatch(r'(\d{3,4})(?:[(（]([+-]?\d+)[)）])?',weight)
        rate=compact(one(namecell.find(cls='rate'),'MARKET').text()); odds=re.match(r'(\d+(?:\.\d+)?)',rate)
        popularity=re.search(r'[(（](\d+)人気[)）]',rate)
        current={'runner_id':str(rid),'horse_no':rid,'frame_no':prior_frame,'name':name,
            'provider_horse_id':hm[1],'provider_horse_id_namespace':PROVIDER,
            'official_horse_id':None,'sire':direct[0],'dam':direct[1],'damsire':damsire[1],
            'date_of_birth':dob,'sex_age':parts[0],'age':int(sexage[2]),'current_load':float(load[0]),
            'current_jockey':jockey,'trainer':parts[-1],
            'provider_jockey_id':jm[1] if jm else None,
            'provider_jockey_id_namespace':PROVIDER if jm else None,
            'provider_jockey_url':jockey_url if jm else None,
            'current_body_weight':int(bw[1]) if bw else None,
            'current_body_weight_change':int(bw[2]) if bw and bw[2] else None,
            'odds':float(odds[1]) if odds and float(odds[1])>0 else None,
            'popularity':int(popularity[1]) if popularity else None,
            'starts':[], 'non_completed_history':[],
            'race_card_source_id':PROVIDER+'-'+digest,'race_card_snapshot_sha256':digest,
            'race_card_fetched_at':captured.isoformat()}
        for slot,c in enumerate(cells[7 if frame else 6:12 if frame else 11],1):
            # Exactly the five history cells, including empty/cancelled slots.
            if 'race' not in c.attrs.get('class','').split(): continue
            chunks=list(c.chunks()); alltext=' '.join(chunks)
            info=one(c.find(cls='firstInfo'),'HISTORY_FIRST_INFO')
            finish=one(info.find(cls='place'),'HISTORY_FINISH').text()
            event=re.search(r'([^\s]+)\s+(\d{2})\.(\d{2})\.(\d{2})',alltext)
            if not event: raise ValueError('RAKUTEN_HISTORY_DATE_UNOBSERVED')
            event_day=date(2000+int(event[2]),int(event[3]),int(event[4]))
            if event_day>=day or event_day>captured.astimezone(timezone(timedelta(hours=9))).date():
                raise ValueError('RAKUTEN_FUTURE_HISTORY_FORBIDDEN')
            evidence={'provider':PROVIDER,'source_url':url,'raw_sha256':digest,'captured_at':captured.isoformat(),
                'runner_number':rid,'history_slot':slot,'provider_horse_id':hm[1],
                'locator':f'tbody.raceCard/runner[{rid}]/history[{slot}]'}
            # Preserve a native identity only when this same history cell
            # actually prints the canonical Provider link. Names/dates alone
            # do not create an ID, and a Provider ID is not an official ID.
            history_name=one(c.find(cls='raceName'),'HISTORY_NAME')
            native_links=[a.attrs.get('href','') for a in history_name.find('a')
                if re.fullmatch(r'https://keiba\.rakuten\.co\.jp/race_performance/list/RACEID/\d{18}',a.attrs.get('href',''))]
            if len(native_links)>1:
                raise ValueError('RAKUTEN_HISTORY_NATIVE_RACE_LINK_AMBIGUOUS')
            native_url=native_links[0] if native_links else None
            native_id=native_url.rsplit('/',1)[-1] if native_url else None
            if native_id and native_id[:8]!=event_day.strftime('%Y%m%d'):
                raise ValueError('RAKUTEN_HISTORY_NATIVE_RACE_DATE_CONFLICT')
            native_identity={'provider_race_id':native_id,
                'provider_race_id_namespace':PROVIDER if native_id else None,
                'provider_race_url':native_url}
            if native_id:
                evidence['native_race_identity']={**native_identity,
                    'locator':f'tbody.raceCard/runner[{rid}]/history[{slot}]/.raceName/a@href',
                    'raw_sha256':digest,'captured_at':captured.isoformat()}
            if not finish.isdigit():
                current['non_completed_history'].append({'date':event_day.isoformat(),'printed_status':finish,
                    **native_identity,'provenance':evidence})
                continue
            field=one(info.find(cls='numberInfo'),'HISTORY_FIELD').text(); fs=re.fullmatch(r'(\d+)頭',compact(field))
            course=re.search(r'(?<!\d)(\d{3,4})([左右直]?)([ダ芝])',alltext)
            if not fs or not course: raise ValueError('RAKUTEN_HISTORY_FIELD_DISTANCE_UNOBSERVED')
            n,f=int(fs[1]),int(finish)
            if not 1<=f<=n: raise ValueError('RAKUTEN_HISTORY_FINISH_OUTSIDE_FIELD')
            pos=[s for s in chunks if re.fullmatch(r'\d+(?:-\d+)+',s)]
            if len(pos)>1: raise ValueError('RAKUTEN_POSITION_SEQUENCE_AMBIGUOUS')
            positions=list(map(int,pos[0].split('-'))) if pos else []
            if any(not 1<=v<=n for v in positions): raise ValueError('RAKUTEN_POSITION_OUTSIDE_FIELD')
            time_margin=re.search(r'((?:\d+:)?\d{2,3}\.\d)\s+\((\d+(?:\.\d+)?)\)',alltext)
            body_weight=re.search(r'(?<!\d)(\d{3,4})k\s+\d+番',alltext)
            go=one(info.find(cls='stateInfo'),'HISTORY_GOING').text()
            race_name=history_name.text()
            after_date=alltext.split(event[0],1)[-1]
            descriptor=after_date.split(course[0],1)[0].strip()
            ride=re.search(re.escape(course[0])+r'\s+(\d+|-)人\s+(.+?)\s+(\d+(?:\.\d+)?)\s+(?:(?:\d+:)?\d{2,3}\.\d\s+\(|\d{3,4}k)',alltext)
            run={'date':event_day.strftime('%y.%m.%d'),'event_date':event_day.isoformat(),
                'venue':event[1],'finish':f,'field_size':n,'distance':int(course[1]),
                **native_identity,
                'direction':{'左':'LEFT','右':'RIGHT','直':'STRAIGHT'}.get(course[2]),
                'surface':{'ダ':'DIRT','芝':'TURF'}[course[3]],
                'going':{'稍':'稍重','不':'不良'}.get(go,go),
                'race_name':descriptor or race_name,'content_positions':positions,
                'content_time_text':time_margin[1] if time_margin else '',
                'margin':0.0 if f==1 and time_margin else float(time_margin[2]) if time_margin else None,
                'printed_time_difference':float(time_margin[2]) if time_margin else None,
                'margin_transform':'WINNER_SELF_DIFFERENCE_ZERO_ELSE_PRINTED_DIFFERENCE_TO_WINNER',
                'ride_body_weight':int(body_weight[1]) if body_weight else None,
                'ride_jockey':ride[2] if ride else '',
                'ride_carried_weight':float(ride[3]) if ride else None,
                'ride_popularity':int(ride[1]) if ride and ride[1].isdigit() else None,
                'provenance':evidence}
            current['starts'].append(run)
        current['field_provenance']={k:{'provider':PROVIDER,'source_url':url,'raw_sha256':digest,
            'captured_at':captured.isoformat(),'locator':f'tbody.raceCard/runner[{rid}]/{k}',
            'transform':'PRINTED_FACT_EXTRACTION_NOT_OFFICIAL_ID_PROMOTION',
            'status':'OBSERVED' if v is not None else 'UNKNOWN','conflict':'NOT_CROSS_SOURCE_RECONCILED'}
            for k,v in current.items() if k not in ('starts','non_completed_history','field_provenance')}
        for key in ('provider_jockey_id','provider_jockey_id_namespace','provider_jockey_url'):
            current['field_provenance'][key]['locator']=f'tbody.raceCard/runner[{rid}]/profile/a@href'
        runners.append(current)
    ids=[r['runner_id'] for r in runners]
    if len(ids)<2 or len(ids)!=len(set(ids)) or set(map(int,ids))!=set(range(1,len(ids)+1)):
        raise ValueError('RAKUTEN_LISTED_UNIVERSE_INCOMPLETE_OR_DUPLICATE')
    # Read only the current Race header. Historical stateInfo cells are not
    # observations of today's weather or going.
    header_text = note.text()
    weather = re.search(r'天候\s*[:：]\s*(小雨|小雪|晴|曇|雨|雪)(?:\s|$)', header_text)
    going = re.search(r'(?:ダ|芝)\s*[:：]\s*(稍重|不良|良|重)(?:\s|$)', header_text)
    conditions = {'weather':weather[1] if weather else None,
                  'going':going[1] if going else None}
    return {'profile':PROFILE,'classification':CLASSIFICATION,'race_identity':identity,
        'provider':PROVIDER,'raw_sha256':digest,'captured_at':captured.isoformat(),'source_url':url,
        'current_conditions':conditions,
        'runners':runners,'listed_count':len(runners),'active_universe_verified':False,
        'current_changes_verified':False,'formal_source_admitted':False,
        'automated_use_licence_issued_here':False,'independent_upstream_sources_proven':False}


def materialize_reference(raw, *, capture, race, generated_at=None, repo_root=None,
                          active_runner_ids=None):
    """Connect observed facts to existing formulas and the fixed model format.

    This is the explicitly unqualified private reference route, not an alternate
    SOURCE admission. Unknown weather, going, Active status and ID mappings
    remain unknown. Only actually printed FNB histories feed the fixed context.
    An admitted caller may provide its separately verified Active IDs before
    field-relative arithmetic. This argument grants no Active qualification.
    """
    from runtime.local_nar_evidence_candidate import compile_parsed_candidate_evidence
    from runtime.local_fullnumerical_candidate import materialize_candidate
    from runtime.local_fnb_r8_arithmetic_29 import verify_29
    from runtime.local_fnb_context_static_candidate import OBSERVATION_PROFILE, CANON, CLASSIFICATION as MODEL_CLASS
    from runtime.local_fnb_multisource import sha
    from runtime.local_fnb_research_runtime import _stamp
    root=Path(repo_root or Path(__file__).resolve().parents[1])
    generated=_stamp(generated_at or datetime.now(timezone.utc))
    if generated>datetime.now(timezone.utc): raise ValueError('RAKUTEN_REFERENCE_GENERATION_IN_FUTURE')
    parsed=parse_card(raw,capture=capture,race=race,now=generated)
    identity=parsed['race_identity'];post=_stamp(identity['scheduled_post_at']);captured=_stamp(parsed['captured_at'])
    if generated<captured:raise ValueError('RAKUTEN_REFERENCE_BEFORE_CAPTURE')
    snapshot=sha(parsed)
    request={'family_id':'LOCAL','venue_id':'FNB','race_date':identity['race_date'],
        'race_no':identity['race_no'],'race_id':'KM-LOCAL-FNB-'+identity['race_date'].replace('-','')
            +'-R'+str(identity['race_no']).zfill(2)+'-RAKUTEN-REFERENCE-R14',
        'classification':CLASSIFICATION,'scheduled_post_at':identity['scheduled_post_at'],
        'prediction_cutoff':(post-timedelta(seconds=300)).isoformat(),
        'cutoff_basis':'EXISTING_PRIVATE_OWNER_300S_REFERENCE_NOT_ACTIVE_OR_SOURCE_ADMISSION',
        'race':{'venue':'船橋','distance_m':identity['distance_m'],'surface':identity['surface'],
            'direction':'LEFT','class':identity['race_name'],'name':identity['race_name']},
        'runners':[{'runner_id':r['runner_id'],'name':r['name']} for r in parsed['runners']]}
    if race.get('race_id') is not None:
        prefix='KM-LOCAL-FNB-'+identity['race_date'].replace('-','')+'-R'+str(identity['race_no']).zfill(2)
        if not re.fullmatch(re.escape(prefix)+r'-RAKUTEN-REFERENCE-[A-Za-z0-9_-]+',str(race['race_id'])):
            raise ValueError('RAKUTEN_REFERENCE_REVISION_IDENTITY_INVALID')
        request['race_id']=race['race_id']
    source={'schema':PROFILE,'classification':CLASSIFICATION,'source_freeze_at':parsed['captured_at'],
        'source_snapshot_sha256':snapshot,'sources':[{'source_id':PROVIDER+'-'+parsed['raw_sha256'],
            'snapshot_sha256':snapshot,'raw_sha256':parsed['raw_sha256'],'format':'text/html',
            'requested_url':parsed['source_url'],'fetched_at':parsed['captured_at'],'official':False,'authority':PROVIDER}],
        'normalized_evidence':{key:{'value':parsed['current_conditions'][field],
            'source_id':PROVIDER+'-'+parsed['raw_sha256'],'raw_sha256':parsed['raw_sha256'],
            'fetched_at':parsed['captured_at'],'locator':'div.raceNote',
            'qualification':'REFERENCE_ONLY_NOT_SOURCE_ADMISSION'}
            for key,field in (('track_condition','going'),('weather','weather'))},
        'active_runner_universe_verified':False,'formal_source_admitted':False,
        'production_numeric_consumers_authorized':False}
    numerical_runners=parsed['runners']
    if active_runner_ids is not None:
        listed={r['runner_id'] for r in parsed['runners']}
        if (not isinstance(active_runner_ids,(list,tuple)) or len(active_runner_ids)<2
                or any(type(rid) is not str or rid not in listed for rid in active_runner_ids)
                or len(set(active_runner_ids))!=len(active_runner_ids)):
            raise ValueError('RAKUTEN_EXPLICIT_ACTIVE_SUBSET_INVALID')
        selected=set(active_runner_ids)
        numerical_runners=[r for r in parsed['runners'] if r['runner_id'] in selected]
        request['runners']=[r for r in request['runners'] if r['runner_id'] in selected]
    raw_field={r['runner_id']:deepcopy(r) for r in numerical_runners}
    registry_path=root/'mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json'
    mapping_path=root/'mapping/local_full_numerical_mapping_v0.1_candidate_20260923.json'
    compiled=compile_parsed_candidate_evidence(source,request,raw_field,registry_path)
    # Every component records the original Provider/row inputs. This supplements
    # the unchanged score, never transforms a reference into licensed evidence.
    for runner in compiled['runners']:
        facts=raw_field[runner['runner_id']]
        for feature in runner['evidence_features'].values():
            feature['provider_input_provenance']={'provider':PROVIDER,'raw_sha256':parsed['raw_sha256'],
                'captured_at':parsed['captured_at'],'runner_number':facts['horse_no'],
                'current_fields':deepcopy(facts['field_provenance']),
                'history_rows':[deepcopy(x['provenance']) for x in facts['starts']],
                'qualification':'REFERENCE_ONLY_NOT_SOURCE_ADMISSION'}
    numerical=materialize_candidate(compiled,registry_path,mapping_path)
    registry=json.loads(registry_path.read_bytes());mapping=json.loads(mapping_path.read_bytes())
    arithmetic=verify_29(numerical,registry,mapping)
    if arithmetic['status']!='29_OF_29_RECORDED_FEATURE_ARITHMETIC_PASS':
        raise ValueError('RAKUTEN_EXISTING_29_ARITHMETIC_HOLD')
    observations=[]
    for runner in numerical_runners:
        starts=[x for x in runner['starts'] if compact(x['venue'])=='船橋' and x['content_positions']]
        observations.append({'runner_id':runner['runner_id'],'name':runner['name'],
            'historical_fnb_observations':[{'event_date':x['event_date'],'field_size':x['field_size'],
                'finish':x['finish'],'distance_m':x['distance'],
                'same_distance':x['distance']==identity['distance_m'],
                'printed_position_sequence':deepcopy(x['content_positions']),
                'source_raw_sha256':parsed['raw_sha256'],'source_fetched_at':parsed['captured_at'],
                'provider_row_provenance':deepcopy(x['provenance'])} for x in starts],
            'historical_evidence_status':'PRINTED_PROVIDER_SAME_HORSE_ROW_NOT_OFFICIAL_ID_JOIN' if starts else 'UNKNOWN'})
    packet={'profile':OBSERVATION_PROFILE,'venue_canon':CANON,'classification':MODEL_CLASS,
        'race_id':request['race_id'],'generated_at':generated.isoformat(),'source_freeze_at':parsed['captured_at'],
        'source_snapshot_sha256':snapshot,'source_receipt_sha256':None,'raw_card_sha256':parsed['raw_sha256'],
        'raw_to_normalized_tables_equal':True,'observation_transport_format':'RAKUTEN_ORIGINAL_HTTP_HTML_NOT_NAR',
        'source_signature_verification':'NOT_PRESENT_NOT_CLAIMED','prestart_generation':False,
        'header':{'distance':identity['distance_m'],'surface':identity['surface'],'direction':'LEFT',
            'scheduled_post_at':identity['scheduled_post_at']},'runners':observations,
        'counts':{'active_runners':len(observations),
            'historical_fnb_starts':sum(len(r['historical_fnb_observations']) for r in observations)},
        'computational_field_semantics':'PROVIDER_LISTED_RUNNERS_NOT_ACTIVE_PROOF',
        'formal_context_ready':False,'owner_scope_granted':False,'forward_oos_credit':0}
    packet['sha256']=sha(packet)
    # The existing executor reads only these two aliases for listed identities.
    execution_parsed={**parsed,'capture':deepcopy(capture),'runners':[
        {**deepcopy(r),'runner_number':r['horse_no']} for r in parsed['runners']]}
    return {'numerical':numerical,'parsed':execution_parsed,'request':request,'raw':raw,
        'source':source,'raw_field':raw_field,'observation_packet':packet,
        'generated_at':generated.isoformat(),'arithmetic29':arithmetic,
        'provider_reference_only':True}


def publish_saved_reference(*, intent, source_folder, paper_folder, exact_folder,
                            destination, current_card_folder=None, now=None):
    """Present existing real calculations independently of Formal admission.

    This small adapter reuses the saved-input verifier and immutable store.
    It runs no calculator, Owner, KRS, Selection, signer or notification. A new
    observation is compared with the original inputs, never substituted into
    their frozen calculations. Material changes require a separate revision.
    """
    from runtime import local_fnb_saved_paper_tickets as saved
    from runtime.local_fnb_saved_exact_paper import read_previous
    from runtime import local_fnb_research_runtime as common
    from runtime.local_reference_delivery import sha
    observed = _stamp(now or datetime.now(timezone.utc))
    source_folder, exact_folder = Path(source_folder), Path(exact_folder)
    previous, inventory, _ = read_previous(paper_folder)
    inputs = saved.verify_saved_run(source_folder, inventory, observed_at=observed.isoformat())
    request, pred = inputs['request'], inputs['prediction']
    if any(request.get(k) != intent.get(k) for k in ('venue_id','race_date','race_no')):
        raise ValueError('REFERENCE_SAVED_RACE_IDENTITY_MISMATCH')
    cutoff = _stamp(request['prediction_cutoff'])
    if observed >= cutoff:
        raise ValueError('REFERENCE_NEW_PUBLICATION_AFTER_CUTOFF_DIAGNOSTIC_REQUIRED')
    # Reuse the existing immutable Exact receipt, including its complete S1/S2
    # predecessor. No new selection or reinterpretation of a zero portfolio.
    receipt = json.loads((exact_folder/'exact_recovery_receipt.json').read_bytes())
    for name, proof in receipt['files'].items():
        path = exact_folder/name
        if path.is_symlink() or not path.resolve().is_relative_to(exact_folder.resolve()):
            raise ValueError('REFERENCE_ORIGINAL_PATH_INVALID')
        data = path.read_bytes()
        if proof != {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}:
            raise ValueError('REFERENCE_EXACT_ORIGINAL_HASH_MISMATCH')
    exact = json.loads((exact_folder/'exact_paper_portfolio.json').read_bytes())
    if (exact['race_id'] != pred['race_id'] or previous['race_id'] != pred['race_id']
            or exact['static_prediction_sha256'] != pred['sha256']
            or exact['source_snapshot_sha256'] != pred['source_snapshot_sha256']
            or exact['KRS_output_sha256'] != hashlib.sha256(inputs['raw']['krs/execution_output.json']).hexdigest()
            or _stamp(exact['selected_at']) > observed):
        raise ValueError('REFERENCE_PREDICTION_SELECTION_REVISION_MISMATCH')
    original = inputs['documents']['parsed_provider_card.json']
    card_folder = Path(current_card_folder) if current_card_folder else None
    capture = json.loads((card_folder/'capture.json').read_bytes()) if card_folder else original['capture']
    raw = (card_folder/'original.html').read_bytes() if card_folder else inputs['raw']['original_provider_card.html']
    card = parse_card(raw, capture=capture, race=intent, now=observed)
    # These are the actual facts consumed by the unchanged numerical/context
    # producers. Provenance timestamps and market observations are not facts
    # that can silently refresh a frozen model.
    ignored = {'field_provenance','provenance','race_card_source_id','race_card_snapshot_sha256',
               'race_card_fetched_at','runner_number','odds','popularity'}
    def facts(value):
        if isinstance(value, dict):
            return {k:facts(v) for k,v in value.items() if k not in ignored}
        if isinstance(value, list):
            return [facts(v) for v in value]
        return value
    # Older saved parser versions omitted native IDs already present in their
    # pinned Raw. Fill only those missing identity fields from that same Raw;
    # preserve every previously parsed value and every calculation binding.
    # This keeps real identity changes material without rerunning unchanged KRS
    # merely because the current parser exposes more provenance.
    old_card = parse_card(inputs['raw']['original_provider_card.html'],
                          capture=original['capture'], race=intent, now=observed)
    native_ids = {'provider_jockey_id','provider_jockey_id_namespace','provider_jockey_url',
                  'provider_race_id','provider_race_id_namespace','provider_race_url'}
    def complete_saved_identity(value, reparsed):
        if isinstance(value, dict) and isinstance(reparsed, dict):
            return {**{k:complete_saved_identity(v, reparsed.get(k)) for k,v in value.items()},
                    **{k:v for k,v in reparsed.items() if k in native_ids and k not in value}}
        if isinstance(value, list) and isinstance(reparsed, list) and len(value)==len(reparsed):
            return [complete_saved_identity(v, r) for v,r in zip(value,reparsed)]
        return value
    original_runners = complete_saved_identity(original['runners'], old_card['runners'])
    consumed_state = inputs['numerical']['candidate_current_state']
    consumed_conditions = {'going':consumed_state.get('official_going') or None,
                           'weather':consumed_state.get('official_weather') or None}
    if (card['race_identity'] != original['race_identity']
            or facts(card['runners']) != facts(original_runners)
            or card['current_conditions'] != consumed_conditions):
        raise ValueError('REFERENCE_MATERIAL_INPUT_CHANGE_NEW_CALCULATION_REVISION_REQUIRED')
    note = one(Document(raw.decode('utf-8')).root.find(cls='raceNote'),'RACE_NOTE').text()
    # A visible row marker can prevent stale reuse. Absence is only an observed
    # page fact, never certification of the final Active set or changes feed.
    tbody = one(Document(raw.decode('utf-8')).root.find('tbody','raceCard'),'CARD_BODY')
    # Current withdrawal status belongs to the current profile/number cells;
    # past-start withdrawals elsewhere in a row must not exclude today's horse.
    withdrawn = [r.text()[:150] for r in tbody.children if isinstance(r, Node) and r.tag == 'tr'
                 and any(re.search(r'取消|除外', c.text()) or
                         re.search(r'cancel|exclude|scratch', c.attrs.get('class',''), re.I)
                         for c in r.children if isinstance(c, Node) and c.tag in ('td','th')
                         and any(k in c.attrs.get('class','').split() for k in ('number','name','profile','weightDistance')))]
    if withdrawn:
        raise ValueError('REFERENCE_CURRENT_WITHDRAWAL_NEW_REVISION_REQUIRED')
    ranks = {c:{r['runner_id']:r for r in pred['column_rankings'][c]['rows']} for c in ('W','P2','P3')}
    krs = {str(r['horse_no']):r for r in inputs['krs_output']['summary']}
    summary = inputs['numerical']['candidate_full_numerical_summary']
    def jp(value): return _stamp(value).astimezone(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M:%S JST')
    fresh_observation = card_folder is not None
    lines = [f"# 船橋{intent['race_no']}R｜独立REFERENCE", '',
        '分類：REFERENCE／非Production／正式署名なし／登録OOS加点0。',
        f"{request['race_date']} {request['race']['name']}／発走 {jp(request['scheduled_post_at'])}／Cutoff {jp(request['prediction_cutoff'])}",
        f"計算SOURCE取得 {jp(pred['source_freeze_at'])}／Static Freeze {jp(pred['freeze_at'])}",
        f"出走表の照合に用いた取得時刻 {jp(card['captured_at'])}／今回の本文保存 {jp(observed)}",
        ('今回取得した出走表と元計算の掲載馬・履歴・騎手・斤量・馬体重を照合し一致。'
         if fresh_observation else '保存済み出走表を再利用。当日変更の最新照合は未実施。'),
        f"掲載{card['listed_count']}頭。現在欄に取消・除外表示を認めず。専用変更一覧と最終Activeは未認証。",
        '観測したRaceヘッダー：'+note,
        '今回の出走表取得時刻で元の指数・KRSの時刻を更新していません。印字天候・馬場は元計算で消費した値と照合済みです。',
        f"29指数×{card['listed_count']}頭={summary['required_count']}セル：算出{summary['calculated_count']}、規定中立{summary['ruled_neutral_count']}、未解決{summary['unresolved_count']}。",
        f"欠測構成要素{summary['candidate_neutral_missing_component_count']}。正式Full29完了ではありません。", '',
        '|馬番|馬名|W参考順位|P2参考順位|P3参考順位|参考Role|SSR-W|SSR-P2|SSR-P3|',
        '|---:|---|---|---|---|---|---:|---:|---:|']
    required_parts=[]
    for horse in card['runners']:
        rid=horse['runner_id']
        rank_values=[str(ranks[c][rid]['rank']) if ranks[c][rid]['rank'] is not None else 'UNKNOWN' for c in ('W','P2','P3')]
        row='|'+ '|'.join([rid,horse['name'],*rank_values,','.join(pred['roles'][rid]) or '既知・非Front',
            *[f"{krs[rid][key]:.4f}" for key in ('SSR-W','SSR-P2','SSR-P3')]])+'|'
        lines.append(row);required_parts.append(row)
    lines += ['', '順位は同順位を含む既存Pareto評価です。UNKNOWNは弱いという意味ではありません。',
        'W参考候補：'+','.join(pred['column_rankings']['W']['front']),
        'P2参考候補：'+','.join(pred['column_rankings']['P2']['front']),
        'P3参考候補：'+','.join(pred['column_rankings']['P3']['front']),
        'UNKNOWN保護：'+','.join(pred['column_rankings']['W']['unknown_protected']),
        '', '## 展開・不確実性',
        '船橋過去走の通過順による既存World仮説を再利用。現在の戦術意図・当日バイアスはUNKNOWN。']
    for horse in inputs['context']['runners']:
        worlds=sorted({p['world_hypothesis'] for p in horse.get('paths',[])})
        lines.append(f"- {horse['runner_id']}番：{','.join(worlds) or 'UNKNOWN'}／船橋過去観測{horse['input_observations']}走。")
    for row in pred['head_local_P2']:
        lines.append(f"- W {row['head']} → P2：{','.join(row['ranking']['front']) or 'UNKNOWN'}")
    for row in pred['pair_conditioned_Third']:
        lines.append(f"- Pair {row['head']}→{row['second']} → P3：{','.join(row['ranking']['front']) or 'UNKNOWN'}")
    lines += ['', 'KRS：既存Engine v1.1.0、5000回・seed1の実出力を再利用。新規実行0。SSRは未較正の出現率で実勝率・EVではありません。',
        '', '## 最終参考結論',
        '既知のW/P2/P3候補は上記のとおり。UNKNOWN馬を一律に下位へ置かず、候補数と予算上限を保った独立PAPER案として扱います。',
        'FORMALは別系列。SOURCE/Active資格、正式Owner採用、署名、配送接続を本REFERENCEで代替しません。',
        '', '## 元の全29指数・全Role・S1/S2/R16全券面とStake（元の分類・時刻を保持）',
        (exact_folder/'COMPLETE_PREDICTION_AND_ALL_TICKETS.md').read_text()]
    body='\n'.join(lines)+'\n'
    manifest={'classification':'REFERENCE','venue_id':'FNB','race_date':request['race_date'],
        'race_no':request['race_no'],'race_id':pred['race_id'],'revision':'REFERENCE-'+card['raw_sha256'][:16],
        'scheduled_post_at':request['scheduled_post_at'],'prediction_cutoff':request['prediction_cutoff'],
        'prepared_at':observed.isoformat(),'forecast_frozen_at':pred['freeze_at'],
        'source_fetched_at':pred['source_freeze_at'],'source_sha256':pred['source_snapshot_sha256'],
        'source_raw_sha256':hashlib.sha256(inputs['raw']['original_provider_card.html']).hexdigest(),
        'observation_capture':capture,'observation_raw_sha256':card['raw_sha256'],
        'current_observation_compared':fresh_observation,'input_facts_unchanged':True,
        'active_verified':False,'current_changes_feed_verified':False,'runner_count':card['listed_count'],
        'runners':[{'runner_id':r['runner_id'],'name':r['name']} for r in card['runners']],
        'model_sha256':pred['model_code_sha256'],'static_sha256':pred['sha256'],
        'KRS_output_sha256':exact['KRS_output_sha256'],'KRS_runs':5000,'KRS_seed':1,'new_KRS':0,
        'formal_final_proven':False,'signed_final_claim':False,'recipient_delivery_ack':False,
        'natural_delivery_verified':False,'actual_purchase':False,'registered_OOS_increment':0,
        'required_parts':required_parts,'body_sha256':hashlib.sha256(body.encode()).hexdigest(),
        'selected_paper_tickets':{k:{'ticket_sha256':v['ticket_sha256'],'points':v['point_count'],
            'required_MEC':v['required_MEC'],'within_cap_amount':v['within_existing_cap_eligible_paper_amount']}
            for k,v in exact['portfolio']['methods'].items()}}
    manifest['sha256']=sha(manifest)
    folder=common._private_root(Path(destination)/'references'/request['race_date']/f"R{request['race_no']:02d}"/manifest['revision'])
    # Idempotent calls retain the original preparation time and frozen body.
    # The same observation bytes can also be consumed by a corrected, separate
    # calculation revision. Never return the previous calculation's body then.
    calculation_keys=('race_id','source_sha256','source_raw_sha256','model_sha256',
                      'static_sha256','KRS_output_sha256','selected_paper_tickets')
    if (folder/'manifest.json').exists():
        previous_publication=read_saved_reference(folder,intent,now=observed)
        if all(previous_publication['manifest'].get(k)==manifest[k] for k in calculation_keys):
            return previous_publication
        manifest['revision']+='-'+sha({k:manifest[k] for k in calculation_keys})[:16]
        manifest['sha256']=sha({k:v for k,v in manifest.items() if k!='sha256'})
        folder=common._private_root(folder.parent/manifest['revision'])
        if (folder/'manifest.json').exists():
            previous_publication=read_saved_reference(folder,intent,now=observed)
            if not all(previous_publication['manifest'].get(k)==manifest[k] for k in calculation_keys):
                raise ValueError('REFERENCE_PREDICTION_SELECTION_REVISION_MISMATCH')
            return previous_publication
    common._immutable(folder/'observation.html',raw)
    common._immutable(folder/'answer.md',body.encode())
    common._immutable(folder/'manifest.json',common.encoded(manifest))
    return read_saved_reference(folder,intent,now=observed)


def read_saved_reference(folder, intent, *, now=None):
    """Verify the frozen bytes; never rerun or retimestamp their prediction."""
    from runtime.local_reference_delivery import sha
    from runtime.local_fnb_research_runtime import _private_root
    folder=Path(folder);observed=_stamp(now or datetime.now(timezone.utc))
    _private_root(folder)
    manifest=json.loads((folder/'manifest.json').read_bytes())
    body=(folder/'answer.md').read_text();raw=(folder/'observation.html').read_bytes()
    if (manifest.get('sha256') != sha({k:v for k,v in manifest.items() if k!='sha256'})
            or any(manifest.get(k)!=intent.get(k) for k in ('venue_id','race_date','race_no'))
            or manifest.get('classification')!='REFERENCE'
            or hashlib.sha256(body.encode()).hexdigest()!=manifest['body_sha256']
            or hashlib.sha256(raw).hexdigest()!=manifest['observation_raw_sha256']
            or any(part not in body for part in manifest['required_parts'])
            or any(part not in body for part in ('W参考候補：','P2参考候補：','P3参考候補：',
                '## 最終参考結論','## 元の全29指数・全Role・S1/S2/R16全券面とStake'))
            or len(manifest['required_parts'])!=manifest['runner_count']
            or any(manifest.get(k) is not False for k in ('formal_final_proven','signed_final_claim',
                'recipient_delivery_ack','natural_delivery_verified','actual_purchase'))):
        raise ValueError('REFERENCE_FROZEN_PUBLICATION_INTEGRITY_HOLD')
    capture=manifest['observation_capture']
    card=parse_card(raw,capture=capture,race=intent,
        now=_stamp(capture.get('completed_at') or capture.get('captured_at')))
    if ([{'runner_id':r['runner_id'],'name':r['name']} for r in card['runners']]!=manifest['runners']
            or any(not part.startswith('|'+r['runner_id']+'|'+r['name']+'|')
                for part,r in zip(manifest['required_parts'],manifest['runners']))
            or not _stamp(manifest['source_fetched_at'])<=_stamp(manifest['forecast_frozen_at'])
                <=_stamp(manifest['prepared_at'])< _stamp(manifest['prediction_cutoff'])
            or _stamp(card['captured_at'])>_stamp(manifest['prepared_at'])
            or _stamp(manifest['prepared_at'])>observed):
        raise ValueError('REFERENCE_FROZEN_IDENTITY_OR_TIME_HOLD')
    return {'status':'VERIFIED_REFERENCE_BODY_READY_TO_RENDER','classification':'REFERENCE',
        'intent':intent,'manifest':manifest,'body':body,'body_sha256':manifest['body_sha256'],
        'private_readback_verified':True,'prestart_at_readback':observed<_stamp(manifest['prediction_cutoff']),
        'new_prediction_executed':False,'formal_final_proven':False,'recipient_delivery_ack':False,
        'source_age_seconds_at_readback':(observed-_stamp(manifest['source_fetched_at'])).total_seconds(),
        'observation_age_seconds_at_readback':(observed-_stamp(card['captured_at'])).total_seconds(),
        'source_within_existing_600s':0 <= (observed-_stamp(manifest['source_fetched_at'])).total_seconds() <= 600,
        'observation_within_existing_600s':0 <= (observed-_stamp(card['captured_at'])).total_seconds() <= 600,
        'registered_oos_increment':0,'publication_folder':str(folder)}

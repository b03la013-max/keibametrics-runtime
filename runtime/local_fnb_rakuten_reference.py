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
        jockey=one(profile.find('a'),'JOCKEY').text()
        weight=compact(cell('weightDistance').text()); bw=re.fullmatch(r'(\d{3,4})(?:[(（]([+-]?\d+)[)）])?',weight)
        rate=compact(one(namecell.find(cls='rate'),'MARKET').text()); odds=re.match(r'(\d+(?:\.\d+)?)',rate)
        popularity=re.search(r'[(（](\d+)人気[)）]',rate)
        current={'runner_id':str(rid),'horse_no':rid,'frame_no':prior_frame,'name':name,
            'provider_horse_id':hm[1],'provider_horse_id_namespace':PROVIDER,
            'official_horse_id':None,'sire':direct[0],'dam':direct[1],'damsire':damsire[1],
            'date_of_birth':dob,'sex_age':parts[0],'age':int(sexage[2]),'current_load':float(load[0]),
            'current_jockey':jockey,'trainer':parts[-1],
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
            if not finish.isdigit():
                current['non_completed_history'].append({'date':event_day.isoformat(),'printed_status':finish,'provenance':evidence})
                continue
            field=one(info.find(cls='numberInfo'),'HISTORY_FIELD').text(); fs=re.fullmatch(r'(\d+)頭',compact(field))
            course=re.search(r'(?<!\d)(\d{3,4})([左右直])([ダ芝])',alltext)
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
            race_name=one(c.find(cls='raceName'),'HISTORY_NAME').text()
            after_date=alltext.split(event[0],1)[-1]
            descriptor=after_date.split(course[0],1)[0].strip()
            ride=re.search(re.escape(course[0])+r'\s+(\d+|-)人\s+(.+?)\s+(\d+(?:\.\d+)?)\s+(?:(?:\d+:)?\d{2,3}\.\d\s+\(|\d{3,4}k)',alltext)
            run={'date':event_day.strftime('%y.%m.%d'),'event_date':event_day.isoformat(),
                'venue':event[1],'finish':f,'field_size':n,'distance':int(course[1]),
                'direction':{'左':'LEFT','右':'RIGHT','直':'STRAIGHT'}[course[2]],
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
        runners.append(current)
    ids=[r['runner_id'] for r in runners]
    if len(ids)<2 or len(ids)!=len(set(ids)) or set(map(int,ids))!=set(range(1,len(ids)+1)):
        raise ValueError('RAKUTEN_LISTED_UNIVERSE_INCOMPLETE_OR_DUPLICATE')
    return {'profile':PROFILE,'classification':CLASSIFICATION,'race_identity':identity,
        'provider':PROVIDER,'raw_sha256':digest,'captured_at':captured.isoformat(),'source_url':url,
        'runners':runners,'listed_count':len(runners),'active_universe_verified':False,
        'current_changes_verified':False,'formal_source_admitted':False,
        'automated_use_licence_issued_here':False,'independent_upstream_sources_proven':False}


def materialize_reference(raw, *, capture, race, generated_at=None, repo_root=None):
    """Connect observed facts to existing formulas and the fixed model format.

    This is the explicitly unqualified private reference route, not an alternate
    SOURCE admission. Unknown weather, going, Active status and ID mappings
    remain unknown. Only actually printed FNB histories feed the fixed context.
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
    source={'schema':PROFILE,'classification':CLASSIFICATION,'source_freeze_at':parsed['captured_at'],
        'source_snapshot_sha256':snapshot,'sources':[{'source_id':PROVIDER+'-'+parsed['raw_sha256'],
            'snapshot_sha256':snapshot,'raw_sha256':parsed['raw_sha256'],'format':'text/html',
            'requested_url':parsed['source_url'],'fetched_at':parsed['captured_at'],'official':False,'authority':PROVIDER}],
        'normalized_evidence':{'track_condition':{'value':None},'weather':{'value':None}},
        'active_runner_universe_verified':False,'formal_source_admitted':False,
        'production_numeric_consumers_authorized':False}
    raw_field={r['runner_id']:deepcopy(r) for r in parsed['runners']}
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
    for runner in parsed['runners']:
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

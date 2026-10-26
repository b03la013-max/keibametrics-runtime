"""Explicit OHI private SOURCE v2. No Formal/registered-v2 admission.

The original v1 acceptance remains available. Market observations are audit
only and are never copied into numerical/Owner/Capital price inputs.
"""
from __future__ import annotations
import copy,re,math
from datetime import datetime,date,timezone,timedelta
from urllib.parse import urljoin,urlsplit
from runtime import ohi_nankan_private_source as v1
from runtime.urw_nankan_reference_source import url_scope,Client,NankanError,DOM,Node,decode,one,sha,ORIGIN

SOURCE_PROFILE='OHI-NANKAN-PRIVATE-SINGLE-SCOPED-CHANGES-MARKET-v2-20261026'

def ohi_url_scope(url):
    p=urlsplit(url)
    if (p.scheme=='https' and p.netloc=='www.nankankeiba.com' and not p.query and not p.fragment
            and re.fullmatch(r'/odds/\d{8}20\d{4}(?:0[1-9]|1[0-2])01\.do',p.path)):
        return p
    return url_scope(url)

class OhiClient(Client):
    # Same transport, robots decision, User-Agent, interval and credentials.
    validate_url=staticmethod(ohi_url_scope)

def history_observation(run,**kwargs):
    # Real R02 shows first-start trainer/jockey statistics in unused slots.
    # They are neither a previous start nor numerical race evidence.
    if run is not None and run.text().startswith('初出走時勝率'):
        text=run.text()
        if not re.fullmatch(r'初出走時勝率 騎手 (?:\d+(?:\.\d+)?|-) 調教師 (?:\d+(?:\.\d+)?|-)',text):
            raise NankanError('OHI_FIRST_START_STATISTICS_SHAPE_UNKNOWN')
        if run.all('a','race_name_len') or run.all('p','race_name_len'):
            raise NankanError('OHI_STATISTICS_AND_HISTORY_CONTRADICTION')
        slot=kwargs['slot'];horse=kwargs['provider_horse_id']
        return dict(slot=slot,classification='ABSENT',status='UNKNOWN',event_type='NOT_A_START',
            ordinary_start_eligible=False,reason='FIRST_START_STATISTICS_NOT_RACE_HISTORY',raw=text,record=None,
            provenance=dict(identity_type='LOCAL_RAW_HISTORY_SLOT',source_raw_sha256=kwargs['source_raw_sha256'],
                source_url=kwargs['source_url'],provider_horse_id=horse,history_slot=slot,provider_result_url=None))
    return v1._history_observation(run,**kwargs)

def _change_block(raw,receipt,race):
    if receipt['url']!=ORIGIN+'/henko_info/00000000000000.do' or v1.hashlib.sha256(raw).hexdigest()!=receipt['raw_sha256']:
        raise NankanError('OHI_CHANGE_RAW_OR_URL_IDENTITY')
    dom=DOM(v1.complete_document(raw)).root
    h=one(dom.all('h3','nk23_c-block01__info__title'),'OHI_CHANGES_VENUE_UNIQUE')
    if '大井競馬' not in h.text():raise NankanError('OHI_CHANGES_OTHER_VENUE')
    v1._dated_header(h,race['race_date'])
    block=h
    while block is not None and 'nk23_c-block01' not in block.attrs.get('class','').split():block=block.parent
    if block is None:raise NankanError('OHI_DATED_CHANGE_BLOCK_UNKNOWN')
    def owned(tag,cls=None):
        out=[]
        for n in block.all(tag,cls):
            p=n.parent
            while p is not None and 'nk23_c-block01' not in p.attrs.get('class','').split():p=p.parent
            if p is block:out.append(n)
        return out
    content=one(owned('div','nk23_c-tab4__content'),'OHI_COMPLETE_CHANGE_CONTENT_REQUIRED')
    shown=one([n for n in owned('span') if n.attrs.get('id')=='nowDateSpan'],'OHI_PROVIDER_CHANGE_TIMESTAMP_REQUIRED').text()
    m=re.fullmatch(r'(\d{4})年(\d{1,2})月(\d{1,2})日\s*(\d{1,2}):(\d{2})現在',shown)
    if not m:raise NankanError('OHI_CHANGE_TIME_UNKNOWN')
    provider=datetime(*map(int,m.groups()),tzinfo=timezone(timedelta(hours=9)))
    if provider.date().isoformat()!=race['race_date'] or provider>datetime.fromisoformat(receipt['fetched_at']):raise NankanError('OHI_CHANGE_TIMESTAMP_CONTRADICTION')
    if datetime.fromisoformat(receipt['fetched_at']).astimezone(provider.tzinfo).date()!=provider.date():raise NankanError('OHI_CHANGE_OBSERVED_DAY_MISMATCH')
    return content,owned,provider

def scoped_changes(raw,receipt,race,declared,program_races):
    content,owned,provider=_change_block(raw,receipt,race)
    notices=[p for p in owned('p','nk23_c-text02') if p.text()=='本日開催に変更情報がありません']
    rows=owned('li','nk23_c-block01__list__item')
    if notices:
        # Delegate the original exact no-change contract without relabelling.
        result=v1.dated_changes(raw,receipt,race)
        return {**result,'contract':SOURCE_PROFILE,'target_not_listed_is_no_change':False}
    if not rows:raise NankanError('OHI_COMPLETE_CHANGE_LIST_STATE_UNKNOWN')
    if any(row not in content.all('li','nk23_c-block01__list__item') for row in rows):raise NankanError('OHI_CHANGE_ROW_OUTSIDE_CONTENT')
    programs={str(r['race_no']):r for r in program_races};seen=set();items=[];observed=[]
    by_horse={d['provider_horse_id']:d for d in declared}
    for row in rows:
        label=one(row.all('span','nk23_c-block01__label'),'OHI_CHANGE_RACE_LABEL_REQUIRED').text()
        match=re.fullmatch(r'(\d{1,2})R',label)
        number=match[1] if match else None
        if number not in programs or number in seen or row.attrs.get('id')!=f'{int(number):02d}':raise NankanError('OHI_CHANGE_RACE_IDENTITY')
        seen.add(number);pr=programs[number]
        if {a.attrs.get('href') for a in row.all('a') if a.attrs.get('href','').startswith('/syousai/')}!={'/syousai/'+pr['provider_race_id']+'.do'}:raise NankanError('OHI_CHANGE_RACE_LINK_IDENTITY')
        changes=row.all('div','nk23_c-block01__list2__item')
        if not changes:raise NankanError('OHI_EMPTY_CHANGE_RACE_ROW')
        target=int(number)==race['race_no']
        for c in changes:
            kind=one(c.all('p','nk23_c-block01__tag'),'OHI_CHANGE_KIND_REQUIRED').text()
            observed.append(dict(race_no=int(number),change_type=kind,raw=c.text()))
            if not target:continue
            if kind in ('競走取り止め','競走取止','取止','取り止め'):raise NankanError('OHI_TARGET_RACE_ABANDONED')
            if kind not in ('出走取消','競走除外','騎手変更'):raise NankanError('OHI_UNSUPPORTED_TARGET_CHANGE:'+kind)
            no=one(c.all('span','nk23_c-block01__txt2'),'OHI_CHANGE_NUMBER_REQUIRED').text()
            m=re.fullmatch(r'(\d{1,2})番',no)
            if not m:raise NankanError('OHI_CHANGE_NUMBER_UNKNOWN')
            horse=one([a for a in c.all('a') if re.fullmatch(r'/uma_info/\d+\.do',a.attrs.get('href',''))],'OHI_CHANGE_HORSE_REQUIRED')
            hid=horse.attrs['href'].split('/')[-1][:-3];d=by_horse.get(hid)
            if d is None or d['name']!=horse.text() or d.get('runner_id') not in (None,m[1]):raise NankanError('OHI_CHANGE_HORSE_IDENTITY')
            riders=[a.text() for a in c.all('a') if a.attrs.get('href','').startswith('/kis_info/')]
            if kind=='騎手変更':
                before=[];after=[]
                for detail in c.all('p','nk23_c-block01__text2'):
                    label=detail.text();names=[a.text() for a in detail.all('a') if a.attrs.get('href','').startswith('/kis_info/')]
                    if re.match(r'^変更前(?:\s|[:：])',label):before+=names
                    if re.match(r'^変更後(?:\s|[:：])',label):after+=names
                if len(before)!=1 or len(after)!=1 or len(riders)!=2 or d.get('current_jockey')!=after[0]:raise NankanError('OHI_CHANGED_JOCKEY_DIRECTION_OR_CARD_NOT_UPDATED')
            items.append(dict(runner_id=m[1],provider_horse_id=hid,name=d['name'],change_type=kind,
                status='CANCELLED' if kind!='騎手変更' else 'ACTIVE_DECLARED',jockey_names_observed=riders,raw=c.text(),active_verified=False))
    if len({(i['runner_id'],i['change_type']) for i in items})!=len(items):raise NankanError('OHI_DUPLICATE_TARGET_CHANGE')
    return dict(contract=SOURCE_PROFILE,status='TARGET_CHANGE_ITEMS_OBSERVED' if items else 'OTHER_RACE_CHANGES_OBSERVED_TARGET_UNLISTED',
        provider_display_at=provider.isoformat(),source=receipt,items=items,all_race_items=observed,
        active_verified=False,absence_is_no_change=False,target_not_listed_is_no_change=False)

def market_menu(card,card_url,race):
    def walk(n):
        yield n
        for c in n.children:
            if isinstance(c,Node):yield from walk(c)
    menu=one([n for n in walk(DOM(v1.complete_document(card)).root) if n.attrs.get('data-menu')=='odds'],'OHI_MARKET_MENU_REQUIRED')
    href=menu.attrs.get('href');disabled='is-disable' in menu.attrs.get('class','').split()
    if disabled and not href:return dict(status='MARKET_UNAVAILABLE_UI_DISABLED_NO_LINK',observation=menu.attrs,url=None)
    expected=ORIGIN+'/odds/'+race['provider_race_id']+'01.do'
    if disabled or not href or urljoin(card_url,href)!=expected:raise NankanError('OHI_OBSERVED_MARKET_LINK_CONTRADICTION')
    ohi_url_scope(expected)
    return dict(status='OFFICIAL_MARKET_LINK_OBSERVED',observation=menu.attrs,url=expected)

def observed_market(raw,receipt,race,declared):
    v1.complete_document(raw);dom=DOM(decode(raw)).root;v1._verify_race_header(dom,race,verify_runner_count=False)
    if receipt['url']!=ORIGIN+'/odds/'+race['provider_race_id']+'01.do' or v1.hashlib.sha256(raw).hexdigest()!=receipt['raw_sha256']:raise NankanError('OHI_ODDS_RAW_IDENTITY')
    table=one(dom.all('table','nk23_c-table04__table'),'OHI_ODDS_TABLE_REQUIRED')
    by_no={d['runner_id']:d for d in declared if d.get('runner_id')};rows=[]
    for tr in table.all('tr'):
        cells=[c.text() for c in tr.children if isinstance(c,Node) and c.tag=='td']
        if not cells:continue
        if len(cells) not in (3,4) or cells[0] not in by_no or cells[1]!=by_no[cells[0]]['name']:raise NankanError('OHI_ODDS_RUNNER_IDENTITY')
        cancelled=any(x.replace(' ','') in ('取消','出走取消','除外','競走除外') for x in cells[2:])
        if not cancelled and cells[2] not in ('-','--','---','―','－','未発売') and not re.fullmatch(r'\d+(?:\.\d+)?',cells[2]):raise NankanError('OHI_ODDS_PRICE_STATE_UNKNOWN')
        win=float(cells[2]) if not cancelled and re.fullmatch(r'\d+(?:\.\d+)?',cells[2]) else None
        place=re.fullmatch(r'(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)',cells[3]) if len(cells)==4 and not cancelled else None
        if len(cells)==4 and not cancelled and not place and cells[3] not in ('-','--','---','―','－','未発売'):raise NankanError('OHI_PLACE_ODDS_STATE_UNKNOWN')
        lo,hi=(float(place[1]),float(place[2])) if place else (None,None)
        if any(x is not None and not math.isfinite(x) for x in (win,lo,hi)):raise NankanError('OHI_ODDS_NONFINITE')
        if win is not None and win<=0 or lo is not None and not 0<lo<=hi:raise NankanError('OHI_ODDS_VALUE_INVALID')
        rows.append(dict(runner_id=cells[0],provider_horse_id=by_no[cells[0]]['provider_horse_id'],name=cells[1],status='CANCELLED' if cancelled else 'ACTIVE_DECLARED',win_odds=win,place_low=lo,place_high=hi,betting_membership_observed=bool(win and lo)))
    if len({r['runner_id'] for r in rows})!=len(rows) or {r['runner_id'] for r in rows}!=set(by_no):raise NankanError('OHI_ODDS_UNIVERSE_MISMATCH')
    return dict(status='MARKET_PRICES_OBSERVED_AUDIT_ONLY' if any(r['win_odds'] is not None for r in rows) else 'MARKET_ROWS_OBSERVED_PRICES_UNPUBLISHED',source=receipt,rows=rows,prices_consumed=False,active_verified=False)

def observe(race,card,cardmeta,changes,chgmeta,receipts,*,program_races,odds=None):
    for raw,meta in [(card,cardmeta),(changes,chgmeta)]+([odds] if odds else []):
        if meta.get('http_status')!=200 or v1.hashlib.sha256(raw).hexdigest()!=meta['raw_sha256']:raise NankanError('OHI_V2_RAW_RECEIPT_MISMATCH')
        if (meta.get('source_policy') or {}).get('usage_scope')!='USER_PERSONAL_NONCOMMERCIAL_PRIVATE_ONLY_NOT_PUBLIC_REDISTRIBUTION':raise NankanError('OHI_PRIVATE_SOURCE_SCOPE_REQUIRED')
    ex=[];cardobs={};facts=v1.parse_single_card(card,race,cardmeta['url'],excluded_rows=ex,card_observations=cardobs,history_parser=history_observation)
    declared=facts+ex;ch=scoped_changes(changes,chgmeta,race,declared,program_races)
    cancels={i['provider_horse_id']:i for i in ch['items'] if i['status']=='CANCELLED'}
    card_cancelled={d['provider_horse_id'] for d in declared if d['status']=='CANCELLED'}
    if card_cancelled!=set(cancels):raise NankanError('OHI_CARD_DATED_CANCELLATION_CONTRADICTION')
    # An unnumbered Card scratch obtains its number only from the explicit
    # dated official change item with the identical provider horse ID.
    declared=[{**d,'runner_id':cancels[d['provider_horse_id']]['runner_id']}
        if d.get('runner_id') is None else d for d in declared]
    menu=market_menu(card,cardmeta['url'],race)
    if menu['url']:
        if odds is None:raise NankanError('OHI_OBSERVED_ODDS_REQUIRED')
        market=observed_market(*odds,race,declared)
        if {r['provider_horse_id'] for r in market['rows'] if r['status']=='CANCELLED'}!=card_cancelled:raise NankanError('OHI_ODDS_CARD_CANCELLATION_CONTRADICTION')
        market['observation']=menu['observation']
    else:
        if odds is not None:raise NankanError('OHI_UNOBSERVED_ODDS_FORBIDDEN')
        market={**menu,'prices':None,'betting_membership':None,'prices_consumed':False}
    active=[f for f in facts if f['status']=='ACTIVE_DECLARED']
    if not active:raise NankanError('OHI_NO_DECLARED_RUNNERS')
    for f in active:
        for start in f['starts']:
            if datetime.strptime(start['date'],'%y.%m.%d').date()>datetime.fromisoformat(cardmeta['fetched_at']).date():raise NankanError('OHI_HISTORY_AFTER_CAPTURE')
    from runtime.ohi_single_race_research import PROFILE,seal
    return seal(dict(profile=PROFILE,source_profile=SOURCE_PROFILE,race=race,program_races=program_races,
        facts=active,declared_facts=declared,excluded_runners=ex,source=cardmeta,changes=ch,receipts=receipts,
        card_observation=cardobs,market=market,runner_universe_basis='DATED_OFFICIAL_CARD_AND_SCOPED_CHANGE_LIST_OBSERVATION_NOT_VERIFIED_ACTIVE',
        active_verified=False,formal_source_claim=False,signed_source_claim=False,production_authority=False,formal_forward_oos_credit=0))

"""OHI-only unsigned private SOURCE adapter; no Formal/NAR/URW admission.

History and frame correctness helpers are byte-preserved from PR329
291b141613bc114fea729fbfb0dcd6c579546aa4. OHI identity is independently
validated; no venue relabelling or mutation of the old URW module occurs.
"""
from __future__ import annotations
from datetime import date, datetime, timedelta, timezone
import hashlib,json,re,unicodedata
from urllib.parse import urljoin
from runtime.urw_nankan_reference_source import (
    Client,ObservedRedirect,DOM,Node,decode,norm,one,sha,NankanError,ORIGIN,reference_metadata)
PROFILE='OHI-NANKAN-PRIVATE-SINGLE-CARD-DATED-CHANGES-v1-20261026'
PROVIDER='NANKAN_OFFICIAL'

def complete_document(raw):
    text=decode(raw)
    if not re.search(r'</body>\s*</html>\s*$',text,re.I) or len(re.findall(r'<body(?:\s|>)',text,re.I))!=1 or len(re.findall(r'</main\s*>',text,re.I))!=1:
        raise NankanError('OHI_INCOMPLETE_OFFICIAL_DOCUMENT')
    return text

def _dated_header(h,day):
    dates=h.parent.all('p','nk23_c-block01__info__text')
    if len(dates)!=1:raise NankanError('OHI_DATED_HEADER_REQUIRED')
    match=re.fullmatch(r'(\d{4})年(\d{1,2})月(\d{1,2})日',dates[0].text())
    if not match or date(*map(int,match.groups())).isoformat()!=day:raise NankanError('OHI_HEADER_DATE_MISMATCH')
    return True

def _verify_race_header(dom,race,*,verify_runner_count=True):
    rid=race.get('provider_race_id','');day=race['race_date'].replace('-','')
    if race.get('venue_id')!='OHI' or race.get('provider')!=PROVIDER or not re.fullmatch(day+r'20[0-9]{4}'+f"{race['race_no']:02d}",rid):
        raise NankanError('OHI_PROVIDER_RACE_IDENTITY')
    text=one(dom.all('p','nk23_c-tab1__subtitle'),'OHI_CARD_HEADER_REQUIRED').text()
    y,m,d=map(int,race['race_date'].split('-'))
    if not re.search(rf'{y}年{m}月{d}日',text) or '大井競馬' not in text or not re.match(rf'{race["race_no"]}R\b',text):
        raise NankanError('OHI_CARD_DATE_VENUE_RACE_MISMATCH')
    if not re.search(rf'(?<![\d,])(?:{race["distance"]:,}|{race["distance"]})m',text) or race['scheduled_post_at'][11:16] not in text:
        raise NankanError('OHI_CARD_PROGRAM_FACT_MISMATCH')
    if verify_runner_count and f"{race['program_runner_count']}頭" not in text:
        raise NankanError('OHI_CARD_PROGRAM_COUNT_MISMATCH')
    expected='内' if race['course_family']=='INNER_RIGHT' else '外' if race['course_family']=='OUTER_RIGHT' else '左'
    if (f'({expected})' not in text and not (expected=='左' and re.search(r'\(左(?:外)?\)',text))):raise NankanError('OHI_CURRENT_COURSE_FAMILY_UNKNOWN')
    return text

def parse_program(raw,url,day):
    if not re.fullmatch(re.escape(ORIGIN)+'/program/'+day.replace('-','')+r'20[0-9]{4}\.do',url):raise NankanError('OHI_PROGRAM_URL_IDENTITY')
    dom=DOM(complete_document(raw)).root;headers=dom.all('h3','nk23_c-block01__info__title')
    y,m,d=map(int,day.split('-'))
    if len(headers)!=1 or '大井競馬' not in headers[0].text():raise NankanError('OHI_PROGRAM_BODY_IDENTITY')
    _dated_header(headers[0],day)
    day_id=url.rsplit('/',1)[1][:-3];out=[]
    for item in dom.all('li','nk23_c-block01__list__item'):
        label=one(item.all('span','nk23_c-block01__label'),'OHI_RACE_LABEL_REQUIRED').text();match=re.fullmatch(r'(\d{1,2})R',label)
        if not match:raise NankanError('OHI_RACE_NUMBER_UNKNOWN')
        n=int(match[1]);a=one(item.all('a','nk23_c-block01__list__title'),'OHI_PROGRAM_CARD_REQUIRED')
        card=urljoin(url,a.attrs.get('href',''));text=item.text()
        clock=re.search(r'\b(\d{1,2}:\d{2})\b',text);distance=re.search(r'\b(\d{3,4})m\b',text);count=re.search(r'(\d{1,2})頭',text)
        if card!=ORIGIN+'/syousai/'+day_id+f'{n:02d}.do' or not all((clock,distance,count)):raise NankanError('OHI_PROGRAM_FACTS_REQUIRED')
        post=datetime.fromisoformat(day+'T'+clock[1]+':00+09:00');dist=int(distance[1])
        # Existing OHI physical course family map, not a score adjustment.
        family='LEFT' if dist==1650 else 'INNER_RIGHT' if dist in (1500,1600) else 'OUTER_RIGHT' if dist in (1000,1200,1400,1700,1800,2000,2400,2600) else 'UNKNOWN'
        out.append(dict(provider=PROVIDER,venue_id='OHI',race_date=day,race_no=n,provider_race_id=day_id+f'{n:02d}',provider_day_id=day_id,race_name=a.text(),scheduled_post_at=post.isoformat(),prediction_cutoff=(post-timedelta(seconds=300)).isoformat(),cutoff_basis='EXISTING_OHI_LOCAL_POST_MINUS_300_SECONDS_RESEARCH_NOT_OFFICIAL_SALES',distance=dist,course_family=family,surface='DIRT',program_runner_count=int(count[1]),observed_card_url=card))
    if [r['race_no'] for r in out]!=list(range(1,len(out)+1)) or not 1<=len(out)<=12:raise NankanError('OHI_ALL_RACES_NOT_PROVEN')
    return out

def dated_changes(raw,receipt,race):
    if receipt['url']!=ORIGIN+'/henko_info/00000000000000.do' or hashlib.sha256(raw).hexdigest()!=receipt['raw_sha256']:raise NankanError('OHI_CHANGE_RAW_OR_URL_IDENTITY')
    dom=DOM(complete_document(raw)).root;h=one(dom.all('h3','nk23_c-block01__info__title'),'OHI_CHANGES_VENUE_UNIQUE')
    block=h
    while block is not None and 'nk23_c-block01' not in block.attrs.get('class','').split():block=block.parent
    if block is None:raise NankanError('OHI_DATED_CHANGE_BLOCK_UNKNOWN')
    def owned(tag,cls=None):
        out=[]
        for node in block.all(tag,cls):
            parent=node.parent
            while parent is not None and 'nk23_c-block01' not in parent.attrs.get('class','').split():parent=parent.parent
            if parent is block:out.append(node)
        return out
    y,m,d=map(int,race['race_date'].split('-'))
    if '大井競馬' not in h.text():raise NankanError('OHI_CHANGES_OTHER_DATE_OR_VENUE')
    _dated_header(h,race['race_date'])
    notices=[p for p in owned('p','nk23_c-text02') if re.fullmatch(r'本日開催に変更情報がありません',p.text())]
    content=one(owned('div','nk23_c-tab4__content'),'OHI_COMPLETE_CHANGE_CONTENT_REQUIRED')
    if len(notices)!=1 or notices[0] not in content.all('p','nk23_c-text02'):raise NankanError('OHI_EXPLICIT_NO_CHANGE_CONTENT_REQUIRED')
    rows=owned('li','nk23_c-block01__list__item')+owned('div','nk23_c-block01__list2__item')
    if len(notices)!=1 or rows:raise NankanError('OHI_CHANGES_REQUIRE_ITEM_ADAPTER_OR_EXPLICIT_DATED_NO_CHANGES')
    shown=one([x for x in owned('span') if x.attrs.get('id')=='nowDateSpan'],'OHI_PROVIDER_CHANGE_TIMESTAMP_REQUIRED').text()
    match=re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日\s*(\d{1,2}:\d{2})現在',shown)
    if not match:raise NankanError('OHI_CHANGE_TIME_UNKNOWN')
    provider=datetime.fromisoformat(f'{int(match[1]):04d}-{int(match[2]):02d}-{int(match[3]):02d}T{match[4]}:00+09:00')
    observed=datetime.fromisoformat(receipt['fetched_at'])
    if provider.date()!=date.fromisoformat(race['race_date']) or provider>observed:raise NankanError('OHI_CHANGE_TIMESTAMP_CONTRADICTION')
    return dict(status='EXPLICIT_NO_CHANGES_TODAY',provider_display_at=provider.isoformat(),source=receipt,items=[],active_verified=False,absence_is_no_change=False)

def parse_single_card(raw,race,url,*,excluded_rows=None,card_observations=None):
    complete_document(raw)
    rows=_parse_card(raw,race,url,excluded_rows=excluded_rows,single_card=True,card_observations=card_observations)
    for row in rows:
        for run in row['starts']:
            when=datetime.strptime(run['date'],'%y.%m.%d').date()
            if when>=date.fromisoformat(race['race_date']):raise NankanError('OHI_HISTORY_NOT_PRESTART')
    return rows

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

def _parse_card(raw,race,url,*,excluded_rows=None,single_card=False,card_observations=None):
    if url!=ORIGIN+'/uma_shosai/'+race['provider_race_id']+'.do':raise NankanError('NANKAN_CARD_URL_IDENTITY')
    dom=DOM(decode(raw)).root;raw_sha256=hashlib.sha256(raw).hexdigest()
    header=_verify_race_header(dom,race,verify_runner_count=not single_card)
    header_count=None
    if single_card:
        counts=re.findall(r'\((\d{1,2})頭\)',header)
        if len(counts)!=1:raise NankanError('NANKAN_SINGLE_CARD_HEADER_COUNT_UNKNOWN')
        header_count=int(counts[0])
    table=one([node for node in dom.all('table','tb-shousai') if node.attrs.get('id')!='tb-sample'
               and 'hidden' not in node.attrs.get('class','').split()],'NANKAN_ACTUAL_HISTORY_TABLE_REQUIRED')
    body=one(table.all('tbody'),'NANKAN_ACTUAL_HISTORY_BODY_REQUIRED');runners=[]
    exclusions=[];active_frame=None;frame_remaining=0
    horse_rows=[node for node in body.children if isinstance(node,Node) and node.tag=='tr']
    for row_index,row in enumerate(horse_rows):
        no=one(row.all('td','umaban'),'NANKAN_HORSE_NUMBER_REQUIRED').text()
        cell=one(row.all('td','pr-umaName-textRound'),'NANKAN_HORSE_NAME_CELL_REQUIRED')
        anchors=[node for node in cell.all('a') if re.fullmatch(r'/uma_info/\d+\.do',node.attrs.get('href',''))]
        horse=one(anchors,'NANKAN_HORSE_IDENTITY_REQUIRED');name=horse.text()
        if not name:raise NankanError('NANKAN_HORSE_NAME_UNKNOWN')
        # The actual frame cell can span consecutive horse rows. The right
        # display copy must not establish a second span or advance the count.
        # Consume physical rows, including explicitly unnumbered scratches.
        frames=[node for node in row.all('td','waku') if 'cs-wakuBanR' not in node.attrs.get('class','').split()]
        if len(frames)>1:raise NankanError('NANKAN_FRAME_CELL_NOT_UNIQUE')
        if frames:
            if frame_remaining:raise NankanError('NANKAN_FRAME_ROWSPAN_OVERLAP')
            cell_frame=frames[0];span=cell_frame.attrs.get('rowspan','1');label=cell_frame.text()
            if not re.fullmatch(r'[1-9][0-9]?',span) or int(span)>len(horse_rows)-row_index:
                raise NankanError('NANKAN_FRAME_ROWSPAN_INVALID')
            if not re.fullmatch(r'[1-8]',label) and label not in ('','-','−','－'):
                raise NankanError('NANKAN_FRAME_VALUE_INVALID')
            active_frame=int(label) if re.fullmatch(r'[1-8]',label) else None
            frame_remaining=int(span)
        frame=active_frame if frame_remaining else None
        if frame_remaining:
            frame_remaining-=1
            if not frame_remaining:active_frame=None
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
            'frame_no':frame,
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
    if frame_remaining:raise NankanError('NANKAN_FRAME_ROWSPAN_INCOMPLETE')
    ids=[r['runner_id'] for r in runners]
    if len(set(ids))!=len(ids) or len(set(r['name'] for r in runners))!=len(ids):
        raise NankanError('NANKAN_ALL_RUNNER_UNIVERSE_MISMATCH')
    # The program may advertise only currently numbered runners even when the
    # HTML retains an explicitly CANCELLED, still-numbered historical row.
    # When the program and table counts already match, preserve the original
    # declared+cancelled semantics and immutable original behavior.
    observed_numbered_count=len(runners)
    explicit_unnumbered_count=sum(row['runner_id'] is None for row in exclusions)
    if single_card and header_count not in {len(runners),len(runners)+explicit_unnumbered_count,
                                          sum(row['status']!='CANCELLED' for row in runners)}:
        raise NankanError('NANKAN_SINGLE_CARD_HEADER_UNIVERSE_MISMATCH')
    if len(runners)!=race['program_runner_count']:
        numbered_active=[r for r in runners if r['status']!='CANCELLED']
        includes_unnumbered=(single_card and explicit_unnumbered_count
                            and len(runners)+explicit_unnumbered_count==race['program_runner_count'])
        if len(numbered_active)!=race['program_runner_count'] and not includes_unnumbered:
            raise NankanError('NANKAN_ALL_RUNNER_UNIVERSE_MISMATCH')
        for row in ([] if includes_unnumbered else runners):
            if row['status']=='CANCELLED':
                exclusions.append({'runner_id':row['runner_id'],'name':row['name'],
                    'provider_horse_id':row['provider_horse_id'],
                    'observed_marker':'CANCELLED_IN_CARD_ODDS',
                    'status':'CANCELLED','reason':'EXPLICIT_NUMBERED_OFFICIAL_CARD_CANCELLATION',
                    'active_verified':False})
        if not includes_unnumbered:runners=numbered_active
    identities=[row['provider_horse_id'] for row in runners+exclusions]
    if len(set(identities))!=len(identities) or len(set(row['name'] for row in runners+exclusions))!=len(identities):
        raise NankanError('NANKAN_SCRATCH_IDENTITY_DUPLICATE')
    numbered={int(row['runner_id']) for row in runners+exclusions if row['runner_id'] is not None}
    unexplained=set(range(1,max(numbered,default=0)+1))-numbered
    if len(unexplained)>sum(row['runner_id'] is None for row in exclusions):
        raise NankanError('NANKAN_UNEXPLAINED_RUNNER_NUMBER_GAP')
    if excluded_rows is not None:
        excluded_rows.extend(exclusions)
    if single_card and card_observations is not None:
        def basis(count):
            if count==observed_numbered_count:return 'NUMBERED_CARD_ROWS'
            if count==observed_numbered_count+explicit_unnumbered_count:
                return 'NUMBERED_CARD_ROWS_PLUS_EXPLICIT_UNNUMBERED_CANCELLATIONS'
            return 'NUMBERED_NONCANCELLED_CARD_ROWS'
        card_observations.update(source_url=url,source_raw_sha256=raw_sha256,
            program_runner_count_observed=race['program_runner_count'],
            card_header_runner_count_observed=header_count,
            numbered_runner_count_observed=observed_numbered_count,
            explicit_unnumbered_exclusion_count=explicit_unnumbered_count,
            prediction_runner_count=len(runners),program_count_basis=basis(race['program_runner_count']),
            card_header_count_basis=basis(header_count),missing_runner_numbers_assigned=False)
    return runners

"""Private Work transport for two explicit URW execution contracts.

No model, selector, Engine, capital policy, registration or ledger is rewritten.
REGISTERED_V2 retains whole-day/checkpoint admission. Explicit
SINGLE_RACE_NONPRODUCTION reuses only immutable calculation pins and writes a
separate private store, with no registered cohort or OOS credit.
The ordinary entry can prepare an artifact, but only actual private byte
readback admits its publication. A local completion is never delivery proof.
"""
from __future__ import annotations

import argparse
import copy
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import fcntl
import gzip
import hashlib
from itertools import combinations, permutations
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
from urllib.parse import urljoin
from types import SimpleNamespace
from zipfile import ZipFile, ZIP_DEFLATED

from runtime.urw_nankan_reference_source import (
    parse_card, parse_program, verify_history_asof, private_directory,
    private_lock, save_json, immutable, capture_race, Client, ORIGIN,
    parse_current_odds, parse_current_changes, DOM, decode, reference_metadata, url_scope, JST)
from runtime.urw_paper_selection import POLICY, sha, _check_sha, canonical_tickets, select_portfolio
from runtime.local_nar_evidence_candidate import compile_parsed_candidate_evidence
from runtime.local_fullnumerical_candidate import materialize_candidate
from runtime.local_race_key_shadow_owner import predict_conditioned_owner, URW_CANON
from runtime.local_krs_bridge_candidate import build_candidate_krs
from runtime.krs_prediction_utility import build_krs_prediction_utility
from runtime.jra_ticket_tree_renderer import render_ticket_tree
from scripts.urw_candidate_krs_replay import parsed_owner_feature_pack, freeze_owner_forward_comparison
from scripts import urw_paper_selection_replay as registered

ENGINE='9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421'
PARAMETERS='d8c027ee5bcc8fd3d2c248e8059b341776be38910e833d7589f09ab817c161f5'
ARMS=('BASELINE','CANDIDATE')
METHODS=('P0S1','P0S1_NO_KRS','TOP4_BOX_DIAGNOSTIC')
ROOT=Path(__file__).resolve().parents[1]
SINGLE_MODE='SINGLE_RACE_NONPRODUCTION'
SINGLE_CLASS='SINGLE_RACE_PRESTART_NONPRODUCTION_NOT_REGISTERED_OOS'
CARD_CHANGES_PROFILE='URW-SINGLE-CARD-DATED-CHANGES-NO-MARKET-20261023-v1'
CARD_CHANGES_PROFILE_PATH=ROOT/'profiles/urw_single_card_dated_changes_no_market_20261023_v1.json'
RACE_SCOPED_PROFILE='URW-SINGLE-RACE-SCOPED-CHANGES-NO-MARKET-20261023-v2'
RACE_SCOPED_PROFILE_PATH=ROOT/'profiles/urw_single_race_scoped_changes_no_market_20261023_v2.json'

def read(path): return json.loads(Path(path).read_text())
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc)
def seal(value):
    body={k:v for k,v in value.items() if k!='sha256'}
    return {**body,'sha256':sha(body)}

def single_source_profile(c):
    """Explicit opt-in only. This never grants old v2 or formal admission."""
    if c.get('single_source_profile') is None:return None
    paths={CARD_CHANGES_PROFILE:CARD_CHANGES_PROFILE_PATH,RACE_SCOPED_PROFILE:RACE_SCOPED_PROFILE_PATH}
    if c.get('execution_mode')!=SINGLE_MODE or c['single_source_profile'] not in paths:
        raise ValueError('SINGLE_RACE_SOURCE_PROFILE_SCOPE')
    path=paths[c['single_source_profile']]
    if c.get('single_source_profile_sha256')!=digest(path):
        raise ValueError('SINGLE_RACE_SOURCE_PROFILE_PIN')
    profile=read(path)
    if (profile['id']!=c['single_source_profile'] or profile['execution_mode']!=SINGLE_MODE
            or profile['selection_policy_sha256']!=sha(POLICY) or POLICY['price_or_ev_used'] is not False
            or profile['source_max_age_seconds']!=600
            or any(profile[key] is not False for key in ('formal_verified_active','registered_v2_admission',
                'production_authority','actual_purchase','price_consumers_authorized','oddsjs_source_authorized'))):
        raise ValueError('SINGLE_RACE_SOURCE_PROFILE_CONSUMER_SCOPE')
    if profile['id']==RACE_SCOPED_PROFILE and (profile.get('unknown_changes_accepted') is not False
            or profile.get('target_unlisted_is_official_no_change_guarantee') is not False
            or profile.get('krs_parallel_workers')!=2 or profile.get('krs_max_wall_seconds')!=300
            or profile.get('delivery_reserve_seconds')!=30):
        raise ValueError('SINGLE_RACE_SCOPED_OPERATIONAL_CONTRACT')
    return {'id':profile['id'],'file_sha256':digest(path),'contract':profile}

def source_profile_path(profile):
    return {CARD_CHANGES_PROFILE:CARD_CHANGES_PROFILE_PATH,
            RACE_SCOPED_PROFILE:RACE_SCOPED_PROFILE_PATH}[profile['id']]

def configuration(path):
    path=Path(path);private_directory(path.parent)
    if path.is_symlink() or path.stat().st_mode&0o077:raise ValueError('PAPER_CONNECTION_PRIVATE_CONFIG')
    c=read(path);reg=read(c['registration']);_check_sha(reg)
    if c.get('execution_mode','REGISTERED_V2') not in ('REGISTERED_V2',SINGLE_MODE):
        raise ValueError('PAPER_UNKNOWN_EXECUTION_CONTRACT')
    profile=single_source_profile(c)
    if c.get('execution_mode')==SINGLE_MODE and (not c.get('current_source_root')
            or Path(c['store']).resolve()==Path(c.get('registered_store',c['store'])).resolve()):
        raise ValueError('SINGLE_RACE_EXPLICIT_SEPARATE_STORE_REQUIRED')
    if c.get('execution_mode')==SINGLE_MODE:
        ledger=Path(reg['canonical_ledger_path']).resolve()
        for target in (Path(c['store']).resolve(),Path(c['current_source_root']).resolve()):
            if target.is_relative_to(ledger) or ledger.is_relative_to(target):
                raise ValueError('SINGLE_RACE_STORE_OVERLAPS_V2_LEDGER')
    if (type(c.get('seed')) is not int or type(c.get('runs')) is not int
            or c['runs']!=5000 or c['seed']!=1):raise ValueError('PAPER_EXISTING_SIMULATION_CONTRACT')
    if (reg['policy']!=POLICY or reg['policy_sha256']!=sha(POLICY)
            or (c.get('execution_mode')!=SINGLE_MODE and reg['code_sha256']!=registered.code_pins())):
        raise ValueError('PAPER_REGISTERED_CODE_OR_POLICY_CHANGED')
    if digest(c['engine'])!=ENGINE or digest(c['parameters'])!=PARAMETERS:
        raise ValueError('PAPER_PINNED_ENGINE_OR_PARAMETERS')
    models=read(c['model_bundle'])['models']
    for arm in ARMS:
        _check_sha(models[arm])
        if models[arm]['sha256']!=reg['models'][arm]:raise ValueError('PAPER_REGISTERED_MODEL_CHANGED')
        if profile and models[arm]['sha256']!=profile['contract']['prediction_models'][arm]:
            raise ValueError('SINGLE_RACE_SOURCE_PROFILE_MODEL_SCOPE')
    private_directory(c['store'])
    return c,reg,models

def current_raw(folder,key,url,client):
    """Persist one authorized observation; propagate errors, never invent rows."""
    raw_path=folder/(key+'.raw.html');receipt_path=folder/(key+'.receipt.json')
    if raw_path.exists() and receipt_path.exists():
        raw=raw_path.read_bytes();receipt=read(receipt_path)
    else:
        receipt,raw=client.get(url);immutable(raw_path,raw);save_json(receipt_path,receipt)
    require_current_raw(raw,receipt,url)
    return receipt,raw

def require_current_raw(raw,receipt,url):
    reference_metadata(receipt)
    policy=receipt.get('source_policy',{})
    observed=datetime.fromisoformat(receipt['fetched_at'])
    if (receipt.get('url')!=url or receipt.get('http_status')!=200
            or receipt.get('raw_sha256')!=hashlib.sha256(raw).hexdigest()
            or policy.get('usage_scope')!='USER_PERSONAL_NONCOMMERCIAL_PRIVATE_ONLY_NOT_PUBLIC_REDISTRIBUTION'
            or policy.get('status') not in (200,404)
            or 'DISALLOW' in policy.get('classification','').upper()):
        raise ValueError('SINGLE_RACE_CURRENT_RAW_PERMISSION_OR_IDENTITY')
    if observed.tzinfo is None or observed>now() or now().timestamp()-observed.timestamp()>600:
        raise ValueError('SINGLE_RACE_CURRENT_CHANGE_OBSERVATION_EXPIRED')

def observed_odds_link(card_raw,race):
    nodes=[n for n in DOM(decode(card_raw)).root.all() if n.attrs.get('data-menu')=='odds']
    if len(nodes)!=1:raise ValueError('SINGLE_RACE_OFFICIAL_ODDS_MENU_NOT_UNIQUE')
    node=nodes[0];href=node.attrs.get('href');disabled='is-disable' in node.attrs.get('class','').split()
    result={'tag':node.tag,'attributes':dict(node.attrs),'disabled':disabled,'href_observed':href,
        'card_raw_sha256':hashlib.sha256(card_raw).hexdigest()}
    if disabled and not href:return {**result,'status':'OFFICIAL_ODDS_UI_DISABLED_NO_HREF','url':None}
    if disabled or not href:raise ValueError('SINGLE_RACE_OFFICIAL_ODDS_LINK_UNRESOLVED')
    url=urljoin(ORIGIN,href);url_scope(url)
    if url!=ORIGIN+'/odds/'+race['provider_race_id']+'01.do':
        raise ValueError('SINGLE_RACE_OFFICIAL_ODDS_LINK_UNSUPPORTED')
    return {**result,'status':'OBSERVED_CANONICAL_ODDS_LINK','url':url}

def scoped_raw(raw,receipt,url,race,*,historical=False):
    """Original receipt validation; a historical import never renews its time."""
    if not historical:
        require_current_raw(raw,receipt,url)
        return
    reference_metadata(receipt)
    policy=receipt.get('source_policy',{});observed=datetime.fromisoformat(receipt['fetched_at'])
    cutoff=datetime.fromisoformat(race['prediction_cutoff'])
    if (observed.tzinfo is None or cutoff.tzinfo is None or now()<cutoff or observed>=cutoff or observed>now()
            or receipt.get('url')!=url or receipt.get('http_status')!=200
            or receipt.get('raw_sha256')!=hashlib.sha256(raw).hexdigest()
            or policy.get('usage_scope')!='USER_PERSONAL_NONCOMMERCIAL_PRIVATE_ONLY_NOT_PUBLIC_REDISTRIBUTION'
            or policy.get('status') not in (200,404) or 'DISALLOW' in policy.get('classification','').upper()):
        raise ValueError('SINGLE_RACE_HISTORICAL_RAW_OR_RECEIPT_MISMATCH')

def scoped_changes(raw,race,receipt,facts,program_races,*,excluded_rows=(),historical=False):
    """Versioned SINGLE observation, not an official no-change guarantee.

    The old parser/profile continues to return UNKNOWN for an unlisted race.
    This consumer also observes the complete dated list and all programme IDs.
    """
    from runtime import urw_nankan_reference_source as native
    url=ORIGIN+'/henko_info/00000000000000.do'
    scoped_raw(raw,receipt,url,race,historical=historical)
    result=native._unsigned_current_observation(raw,race,receipt,url,'PRIVATE_UNSIGNED_RACE_SCOPED_CHANGE_ITEMS')
    text=decode(raw)
    if not re.search(r'</body\s*>',text,re.I) or not re.search(r'</html\s*>\s*$',text,re.I):
        raise ValueError('SINGLE_RACE_CHANGE_LIST_INCOMPLETE_DOCUMENT')
    dom=DOM(text).root;y,m,d=map(int,race['race_date'].split('-'))
    headings=[n for n in dom.all('h3','nk23_c-block01__info__title')
              if '浦和競馬' in n.text() and f'{y}年{m}月{d}日' in n.parent.text()]
    if len(headings)!=1:raise ValueError('SINGLE_RACE_CHANGES_DATED_VENUE_NOT_UNIQUE')
    block=headings[0].parent
    while block and 'nk23_c-block01' not in block.attrs.get('class','').split():block=block.parent
    if block is None:raise ValueError('SINGLE_RACE_CHANGES_DATED_BLOCK_REQUIRED')
    def owned(tag,cls=None):
        out=[]
        for node in block.all(tag,cls):
            parent=node.parent
            while parent and 'nk23_c-block01' not in parent.attrs.get('class','').split():parent=parent.parent
            if parent is block:out.append(node)
        return out
    if len(owned('div','nk23_c-tab4__content'))!=1:
        raise ValueError('SINGLE_RACE_CHANGE_LIST_COMPLETE_CONTAINER_REQUIRED')
    if datetime.fromisoformat(receipt['fetched_at']).astimezone(JST).date().isoformat()!=race['race_date']:
        raise ValueError('SINGLE_RACE_CHANGES_CAPTURE_DAY_MISMATCH')
    notices=[n for n in owned('p','nk23_c-text02') if n.text()=='本日開催に変更情報がありません']
    if len(notices)>1:raise ValueError('SINGLE_RACE_CHANGE_LIST_NOTICE_NOT_UNIQUE')
    clocks=[n for n in owned('span') if n.attrs.get('id')=='nowDateSpan'];provider_at=None
    if len(clocks)>1:raise ValueError('SINGLE_RACE_CHANGES_PROVIDER_TIME_NOT_UNIQUE')
    if clocks:
        match=re.fullmatch(r'(\d{4})年(\d{1,2})月(\d{1,2})日 (\d{1,2}):(\d{2})現在',clocks[0].text())
        if not match:raise ValueError('SINGLE_RACE_CHANGES_PROVIDER_TIME_INVALID')
        provider_at=datetime(*map(int,match.groups()),tzinfo=JST)
        if provider_at.date().isoformat()!=race['race_date'] or provider_at>datetime.fromisoformat(receipt['fetched_at']):
            raise ValueError('SINGLE_RACE_CHANGES_PROVIDER_TIME_MISMATCH')
    by_race={r['race_no']:r for r in program_races}
    if (len(by_race)!=len(program_races) or race['race_no'] not in by_race
            or any(r.get('race_date')!=race['race_date'] or r.get('venue_id')!='URW' for r in program_races)):
        raise ValueError('SINGLE_RACE_CHANGES_PROGRAM_UNIVERSE_MISMATCH')
    target=by_race[race['race_no']]
    if target.get('race_status')=='CANCELLED':raise ValueError('SINGLE_RACE_TARGET_CANCELLED_IN_PROGRAM')
    for key in ('provider_race_id','distance','program_runner_count','scheduled_post_at','prediction_cutoff'):
        if target.get(key)!=race.get(key):raise ValueError('SINGLE_RACE_CHANGES_PROGRAM_CARD_CONTRADICTION:'+key)
    if (race['program_runner_count'] not in (len(facts),len(facts)+len(excluded_rows))
            or len({f['provider_horse_id'] for f in facts})!=len(facts)):
        raise ValueError('SINGLE_RACE_CHANGES_CARD_UNIVERSE_MISMATCH')
    explicit=list(excluded_rows);declared={f['provider_horse_id']:f for f in [*facts,*explicit]}
    if len(declared)!=len(facts)+len(explicit) or any(f.get('status')!='CANCELLED' for f in explicit):
        raise ValueError('SINGLE_RACE_CHANGES_EXCLUDED_UNIVERSE_MISMATCH')
    rows=owned('li','nk23_c-block01__list__item')
    if notices and rows:raise ValueError('SINGLE_RACE_CHANGES_NO_CHANGE_NOTICE_CONTRADICTION')
    if notices and any(r.get('race_status')=='CANCELLED' for r in program_races):
        raise ValueError('SINGLE_RACE_CHANGES_PROGRAM_STATUS_CONTRADICTION')
    items=[];observed_rows=[];seen=set();target_present=False
    race_cancel=re.compile(r'(?:競走|レース|開催)?(?:取り止め|取止め|取止|中止)')
    def only(nodes,code):
        if len(nodes)!=1:raise ValueError(code)
        return nodes[0]
    for row in rows:
        number=row.attrs.get('id','')
        if not re.fullmatch(r'0[1-9]|1[0-2]',number):raise ValueError('SINGLE_RACE_CHANGE_ROW_RACE_NUMBER_UNKNOWN')
        no=int(number)
        if no in seen or no not in by_race:raise ValueError('SINGLE_RACE_CHANGE_ROW_PROGRAM_MISMATCH')
        seen.add(no);expected=by_race[no]
        if only(row.all('span','nk23_c-block01__label'),'SINGLE_RACE_CHANGE_ROW_LABEL_REQUIRED').text()!=f'{no}R':
            raise ValueError('SINGLE_RACE_CHANGE_ROW_LABEL_MISMATCH')
        changes=row.all('div','nk23_c-block01__list2__item')
        kinds=[only(n.all('p','nk23_c-block01__tag'),'SINGLE_RACE_CHANGE_KIND_REQUIRED').text() for n in changes]
        cancelled=any(race_cancel.fullmatch(k) for k in kinds) or (not changes and bool(race_cancel.search(row.text())))
        links={urljoin(ORIGIN,n.attrs.get('href','')) for n in row.all('a')}
        card_links={link for link in links if '/syousai/' in link}
        expected_link=ORIGIN+'/syousai/'+expected['provider_race_id']+'.do'
        linkless_cancelled=not card_links and cancelled
        if card_links!={expected_link} and not linkless_cancelled:
            raise ValueError('SINGLE_RACE_CHANGE_ROW_CARD_IDENTITY_MISMATCH')
        if expected.get('race_status')=='CANCELLED' and not cancelled:
            raise ValueError('SINGLE_RACE_CHANGE_PROGRAM_STATUS_CONTRADICTION')
        if no==race['race_no']:
            target_present=True
            if cancelled:raise ValueError('SINGLE_RACE_TARGET_CANCELLED_IN_CHANGES')
        if not changes and not cancelled:raise ValueError('SINGLE_RACE_CHANGE_ROW_CONTENT_UNKNOWN')
        observed_rows.append({'race_no':no,'provider_race_id':expected['provider_race_id'],
            'race_status':'CANCELLED' if cancelled else 'CHANGE_ITEMS_OBSERVED','change_types':kinds,
            'observed_text':row.text(),'program_race_status':expected.get('race_status'),
            'observed_card_link':expected_link if card_links else None,
            'race_identity_basis':'UNIQUE_PROGRAM_ROW_AND_EXPLICIT_CANCELLATION'
                if linkless_cancelled else 'OBSERVED_PROGRAM_CARD_LINK'})
        if cancelled:continue
        for node,kind in zip(changes,kinds):
            printed=only(node.all('span','nk23_c-block01__txt2'),'SINGLE_RACE_CHANGE_HORSE_NUMBER_REQUIRED').text()
            match=re.fullmatch(r'(\d{1,2})番',printed)
            horse=only([a for a in node.all('a') if re.fullmatch(r'/uma_info/\d+\.do',a.attrs.get('href',''))],
                       'SINGLE_RACE_CHANGE_HORSE_IDENTITY_REQUIRED')
            if not match or not horse.text():raise ValueError('SINGLE_RACE_CHANGE_HORSE_IDENTITY_UNKNOWN')
            jockeys=[a.text() for a in node.all('a') if a.attrs.get('href','').startswith('/kis_info/')]
            if no!=race['race_no']:continue
            if kind not in ('出走取消','競走除外','騎手変更') or (kind=='騎手変更' and len(jockeys)!=2):
                raise ValueError('SINGLE_RACE_CHANGE_ITEM_UNSUPPORTED')
            provider_id=horse.attrs['href'].split('/')[-1][:-3];original=declared.get(provider_id)
            if (not original or original['name']!=horse.text()
                    or (original.get('runner_id') is not None and str(original['runner_id'])!=match[1])):
                raise ValueError('SINGLE_RACE_CHANGE_DECLARED_IDENTITY_MISMATCH')
            excluded=provider_id in {f['provider_horse_id'] for f in explicit}
            if excluded and kind not in ('出走取消','競走除外'):
                raise ValueError('SINGLE_RACE_CHANGE_EXCLUDED_HORSE_CONTRADICTION')
            items.append({'runner_id':match[1],'name':horse.text(),'provider_horse_id':provider_id,
                'change_type':kind,'status':'CANCELLED' if kind in ('出走取消','競走除外') else 'ACTIVE_DECLARED',
                'jockey_names_observed':jockeys,'change_detail_observed':' '.join(n.text() for n in node.all('p','nk23_c-block01__text2')),
                'explicit_card_exclusion':excluded,'active_verified':False})
    state=('CHANGE_ITEMS_OBSERVED' if items else 'EXPLICIT_NO_CHANGES_TODAY' if notices else
           'OTHER_RACE_CHANGES_OBSERVED_TARGET_UNLISTED' if observed_rows and not target_present else 'UNKNOWN')
    if state=='UNKNOWN':raise ValueError('SINGLE_RACE_DATED_CHANGES_UNKNOWN')
    result.update(items=items,target_race_row_present=target_present,declared_facts_sha256=sha(facts),
        explicit_card_exclusions_sha256=sha(explicit),explicit_no_changes_today_observed=bool(notices),
        target_race_change_status=state,observed_race_rows=observed_rows,
        list_completeness={'status':'DATED_VENUE_BLOCK_AND_ALL_LISTED_ROWS_VALIDATED',
            'complete_html_document':True,'program_race_count':len(program_races),'listed_change_race_count':len(rows)},
        provider_display_at=provider_at.isoformat() if provider_at else None,
        provider_display_time_status='OBSERVED' if provider_at else 'UNKNOWN',
        absence_is_no_change_authority=False,official_target_no_change_guarantee=False,
        historical_diagnostic=historical)
    cancelled_races=sorted({r['race_no'] for r in program_races if r.get('race_status')=='CANCELLED'}|
        {r['race_no'] for r in observed_rows if r['race_status']=='CANCELLED'})
    result['reconciled_program_status']={'planned_race_count':len(program_races),
        'scheduled_race_count':len(program_races)-len(cancelled_races),'cancelled_race_count':len(cancelled_races),
        'cancelled_race_nos':cancelled_races,'basis':'ORIGINAL_PROGRAM_PLUS_OBSERVED_CHANGE_ITEMS',
        'original_program_rewritten':False}
    return seal(result)

def card_changes_observations(c,folder,evidence,card_raw,facts,client,*,historical=False):
    """New price-free SOURCE contract, separate from the old acceptance path."""
    profile=single_source_profile(c);race=evidence['race']
    if not profile:raise ValueError('SINGLE_RACE_EXPLICIT_SOURCE_PROFILE_REQUIRED')
    scoped=profile['id']==RACE_SCOPED_PROFILE
    if historical and not scoped:raise ValueError('SINGLE_RACE_HISTORICAL_PROFILE_REQUIRED')
    for i,name in ((0,'calendar.html.gz'),(1,'program.html.gz'),(3,'card.html.gz')):
        receipt=evidence['sources'][i]
        data=gzip.decompress((folder/name).read_bytes())
        if scoped:scoped_raw(data,receipt,receipt['url'],race,historical=historical)
        else:require_current_raw(data,receipt,receipt['url'])
    card_parser=parse_card
    if scoped:
        from runtime.urw_nankan_reference_source import parse_single_card
        card_parser=parse_single_card
    if facts!=card_parser(card_raw,race,evidence['sources'][3]['url']):
        raise ValueError('SINGLE_RACE_CARD_FACTS_NOT_BOUND_TO_RAW')
    if (race['program_runner_count'] not in ((len(facts),len(facts)+len(evidence.get('explicit_card_exclusions',()))) if scoped else (len(facts),))
            or len({x['provider_horse_id'] for x in facts})!=len(facts)
            or any(not re.fullmatch(r'\d+',x['provider_horse_id']) or not x['name']
                   or x['status'] not in ('ACTIVE_DECLARED','CANCELLED') for x in facts)):
        raise ValueError('SINGLE_RACE_CURRENT_CARD_UNIVERSE_UNRESOLVED')
    # Changes are fetched and parsed even when the market is not published.
    if historical:
        receipt=read(folder/'changes.receipt.json');raw=(folder/'changes.raw.html').read_bytes()
    else:receipt,raw=current_raw(folder,'changes',ORIGIN+'/henko_info/00000000000000.do',client)
    if scoped:
        from runtime.urw_nankan_reference_source import parse_single_program
        program=gzip.decompress((folder/'program.html.gz').read_bytes())
        races=parse_single_program(program,evidence['sources'][1]['url'],race['race_date'])
        changes=scoped_changes(raw,race,receipt,facts,races,
            excluded_rows=evidence.get('explicit_card_exclusions',()),historical=historical)
    else:changes=parse_current_changes(raw,race,receipt,facts)
    accepted=(profile['contract']['changes_accepted_states'] if scoped else
              ('EXPLICIT_NO_CHANGES_TODAY','CHANGE_ITEMS_OBSERVED'))
    if (datetime.fromisoformat(receipt['fetched_at']).astimezone(JST).date().isoformat()!=race['race_date']
            or changes['target_race_change_status'] not in accepted):
        raise ValueError('SINGLE_RACE_DATED_CHANGES_UNKNOWN')
    if any(item['status']!='CANCELLED' and not item.get('jockey_names_observed') for item in changes['items']):
        raise ValueError('SINGLE_RACE_CURRENT_CHANGE_UNRESOLVED')
    link=observed_odds_link(card_raw,race)
    if not historical:save_json(folder/'odds-menu-observation.json',link)
    odds=None;market_reason=link['status']
    if link['url']:
        saved_404=False
        if historical and not (folder/'odds.receipt.json').exists():
            error_path=folder/'odds.http-error.raw.html';meta_path=folder/'odds.http-error.receipt.json'
            if not error_path.is_file() or not meta_path.is_file():
                raise ValueError('SINGLE_RACE_HISTORICAL_MARKET_EVIDENCE_MISSING')
            error=error_path.read_bytes();meta=read(meta_path);stamp=datetime.fromisoformat(meta['observed_at'])
            if (meta.get('url')!=link['url'] or meta.get('http_status')!=404
                    or meta.get('raw_sha256')!=hashlib.sha256(error).hexdigest()
                    or meta.get('scope')!='HTTP_ERROR_NOT_A_PRICE_OR_MEMBERSHIP_OBSERVATION'
                    or stamp.tzinfo is None or stamp>=datetime.fromisoformat(race['prediction_cutoff']) or stamp>now()):
                raise ValueError('SINGLE_RACE_HISTORICAL_MARKET_404_BINDING')
            saved_404=True;market_reason='OBSERVED_CANONICAL_ODDS_LINK_HTTP_404'
        try:
            if saved_404:odds_receipt=odds_raw=None
            elif historical:
                odds_receipt=read(folder/'odds.receipt.json');odds_raw=(folder/'odds.raw.html').read_bytes()
                scoped_raw(odds_raw,odds_receipt,link['url'],race,historical=True)
            else:odds_receipt,odds_raw=current_raw(folder,'odds',link['url'],client)
        except urllib.error.HTTPError as exc:
            # Only an actual 404 on the observed canonical link is eligible.
            # 403, robots denials, timeouts and malformed 200 HTML propagate.
            if exc.code!=404:raise
            error=exc.read();immutable(folder/'odds.http-error.raw.html',error)
            save_json(folder/'odds.http-error.receipt.json',{'url':link['url'],'http_status':404,
                'observed_at':now().isoformat(),'raw_sha256':hashlib.sha256(error).hexdigest(),
                'scope':'HTTP_ERROR_NOT_A_PRICE_OR_MEMBERSHIP_OBSERVATION'})
            market_reason='OBSERVED_CANONICAL_ODDS_LINK_HTTP_404'
        else:
            if not saved_404:
                if scoped:
                    from runtime.urw_nankan_reference_source import parse_single_odds
                    odds=parse_single_odds(odds_raw,race,odds_receipt,facts,
                        excluded_rows=evidence.get('explicit_card_exclusions',()),
                        card_observation=evidence.get('card_observation'))
                else:odds=parse_current_odds(odds_raw,race,odds_receipt,facts)
    market={'status':'MARKET_OBSERVED' if odds is not None else 'MARKET_UNAVAILABLE',
        'reason':None if odds is not None else market_reason,'official_menu':link,
        'price_used':False,'odds_independent_reconciliation':odds is not None,
        'betting_membership_observed':None if odds is None else
            odds['betting_membership_observed_count']==len(facts),
        'price_data_location':'current_observations.odds.runners' if odds is not None else None,
        'missing_prices_are_zero':False}
    if odds is None and market_reason not in profile['contract']['market_unavailable_accepted_states']:
        raise ValueError('SINGLE_RACE_MARKET_STATE_NOT_ADMITTED')
    # No missing rows or fabricated membership are supplied to the reconciler.
    observations={'changes':changes,'market':market}
    if odds is not None:observations['odds']=odds
    if not historical:save_json(folder/'source-contract-observation.json',seal({'profile':profile,'observations':observations}))
    return observations,profile

def current_jockey_identity(card_raw,changes_raw,fact):
    """Join observed provider links, never guess abbreviated-name equality."""
    horse_link='/uma_info/'+fact['provider_horse_id']+'.do'
    card=DOM(decode(card_raw)).root;changes=DOM(decode(changes_raw)).root
    rows=[row for table in card.all('table','tb-shousai') if table.attrs.get('id')!='tb-sample'
          for row in table.all('tr') if any(a.attrs.get('href')==horse_link for a in row.all('a'))
          and any(n.text()==fact['runner_id'] for n in row.all('td','umaban'))]
    items=[d for d in changes.all('div','nk23_c-block01__list2__item')
           if any(a.attrs.get('href')==horse_link for a in d.all('a'))]
    if len(rows)!=1 or len(items)!=1:raise ValueError('SINGLE_RACE_JOCKEY_PROVIDER_IDENTITY_AMBIGUOUS')
    card_riders=[a for group in rows[0].all('td','cs-g1') for a in group.all('a')
                 if a.attrs.get('href','').startswith('/kis_info/')]
    change_riders=[a for a in items[0].all('a') if a.attrs.get('href','').startswith('/kis_info/')]
    if (len(card_riders)!=1 or len(change_riders)!=2
            or card_riders[0].text()!=fact['current_jockey']
            or card_riders[0].attrs['href']!=change_riders[-1].attrs['href']):
        raise ValueError('SINGLE_RACE_JOCKEY_CHANGE_CARD_RECONCILIATION_REQUIRED')
    return {'runner_id':fact['runner_id'],'provider_horse_id':fact['provider_horse_id'],
        'card_name':card_riders[0].text(),'change_from_name':change_riders[0].text(),
        'change_to_name':change_riders[-1].text(),'provider_jockey_link':card_riders[0].attrs['href'],
        'basis':'EXACT_OBSERVED_PROVIDER_ID_MATCH_NOT_NAME_PREFIX_OR_MODEL_CHANGE'}

def _single_observation(c,folder,evidence,*,historical=False):
    race=evidence['race'];source=evidence['sources'][3]
    card_raw=gzip.decompress((folder/'card.html.gz').read_bytes())
    if hashlib.sha256(card_raw).hexdigest()!=source['raw_sha256']:raise ValueError('SINGLE_RACE_CURRENT_CARD_RAW_HASH')
    profile=single_source_profile(c);scoped=bool(profile and profile['id']==RACE_SCOPED_PROFILE)
    card_parser=parse_card;card_observation={}
    if scoped:
        from runtime.urw_nankan_reference_source import parse_single_card
        card_parser=parse_single_card
    exclusions=[]
    facts=(card_parser(card_raw,race,source['url'],excluded_rows=exclusions,card_observations=card_observation)
           if scoped else card_parser(card_raw,race,source['url'],excluded_rows=exclusions))
    verify_history_asof(facts,source['fetched_at'])
    reparse={'original_evidence_sha256':evidence['sha256'],'original_parser_sha256':evidence['parser_sha256'],
        'current_parser_sha256':digest(ROOT/'runtime/urw_nankan_reference_source.py'),
        'original_facts_sha256':sha(evidence['runners']),'current_facts_sha256':sha(facts),'original_files_modified':False}
    program_conditions=program_condition_observation(gzip.decompress((folder/'program.html.gz').read_bytes()),
        evidence['sources'][1],race,single_scoped=scoped)
    if historical:
        if not scoped or now()<datetime.fromisoformat(race['prediction_cutoff']):
            raise ValueError('SINGLE_RACE_SAVED_INPUT_DIAGNOSTIC_ONLY')
    elif (now()>=datetime.fromisoformat(race['prediction_cutoff'])
            or now().timestamp()-datetime.fromisoformat(source['fetched_at']).timestamp()>600):
        raise ValueError('SINGLE_RACE_CURRENT_SOURCE_EXPIRED_NO_BACKDATE')
    if profile:
        evidence={**evidence,'explicit_card_exclusions':exclusions,**({'card_observation':card_observation} if scoped else {})}
        observations,profile=card_changes_observations(c,folder,evidence,card_raw,facts,None if historical else Client(),historical=historical)
    else:observations,profile=legacy_current_observations(folder,race,facts,Client(),reparse),None
    odds={r['runner_id']:r for r in observations.get('odds',{}).get('runners',[])}
    changes=observations['changes'];reconciliations=[]
    for change in changes['items']:
        if change.get('explicit_card_exclusion'):continue
        original=next(r for r in facts if r['runner_id']==change['runner_id'])
        if change['status']=='CANCELLED':original['status']='CANCELLED'
        if change.get('jockey_names_observed'):
            reconciliations.append(current_jockey_identity(card_raw,(folder/'changes.raw.html').read_bytes(),original))
    for fact in facts:
        row=odds.get(fact['runner_id'])
        if row is not None:
            if row['status']=='CANCELLED':fact['status']='CANCELLED'
            if fact['status']=='CANCELLED' and row['betting_membership_observed']:
                raise ValueError('SINGLE_RACE_CANCELLED_ODDS_CONTRADICTION')
    result={'race':race,'facts':facts,'source':source,'active_verified':False,'signed_source_claim':False,
        'program_conditions':program_conditions,'current_parser_reparse':reparse,
        'current_observations':observations,'jockey_change_reconciliations':reconciliations,
        'source_evidence_sha256':evidence['sha256'],'current_source_folder':str(folder),
        **({'source_contract':profile} if profile else {}),
        'latest_change_check':('CURRENT_OFFICIAL_CARD_AND_RACE_SCOPED_DATED_CHANGES' if scoped else
            'CURRENT_OFFICIAL_CARD_AND_DATED_CHANGES_MARKET_SEPARATE' if profile else
            'CURRENT_CARD_ODDS_AND_OFFICIAL_CHANGES_OBSERVED'),
        'active_basis':('UNSIGNED_DATED_CARD_AND_CHANGES_NOT_ODDS_VERIFIED_ACTIVE' if profile else
            'UNSIGNED_CURRENT_OFFICIAL_OBSERVATIONS_NOT_FORMAL_VERIFIED_ACTIVE')}
    if scoped:
        result.update(explicit_card_exclusions=exclusions,program_status=evidence.get('program_status'),
            program_races=evidence.get('program_races'),card_observation=card_observation,source_imported_at=now().isoformat(),
            original_receipts=evidence['sources'],historical_diagnostic=historical,
            current_source_freshness_claim=not historical)
    return result


def current_single_observation(c,day,number):
    """One independent Race; new v2 acquisition never reuses an expired receipt."""
    folder=private_directory(Path(c['current_source_root'])/day/f'R{number:02}')
    profile=single_source_profile(c)
    if profile and profile['id']==RACE_SCOPED_PROFILE:
        from runtime.urw_nankan_reference_source import capture_single_race
        evidence,folder=capture_single_race(day,number,folder,client=Client())
    else:_,evidence,_,_=capture_race(day,number,folder,client=Client())
    return _single_observation(c,folder,evidence)


def saved_single_observation(c,day,number):
    """The same v2 adapter consumes original saved bytes, post-cutoff only."""
    from runtime.urw_nankan_reference_source import parse_single_program, program_link, CALENDAR
    profile=single_source_profile(c)
    if not profile or profile['id']!=RACE_SCOPED_PROFILE:raise ValueError('SINGLE_RACE_SAVED_INPUT_PROFILE_REQUIRED')
    key=day+f'/R{number:02}'
    path=c.get('single_saved_source_folders',{}).get(key)
    if not path:raise ValueError('SINGLE_RACE_SAVED_INPUT_NOT_CONFIGURED')
    from runtime.urw_paper_archive import _private_path
    folder=_private_path(path,directory=True)
    evidence_path=folder/'single-source-evidence.json'
    if not evidence_path.is_file():evidence_path=folder/'reference_evidence.json'
    evidence=read(evidence_path);_check_sha(evidence)
    sources=evidence['sources'];program=gzip.decompress((folder/'program.html.gz').read_bytes())
    races=parse_single_program(program,sources[1]['url'],day)
    race=next((r for r in races if r['race_no']==number),None)
    if race is None:raise ValueError('SINGLE_RACE_SAVED_INPUT_RACE_NOT_IN_PROGRAM')
    if race.get('race_status')=='CANCELLED':raise ValueError('SINGLE_RACE_TARGET_CANCELLED_IN_PROGRAM')
    cutoff=datetime.fromisoformat(race['prediction_cutoff'])
    if now()<cutoff:raise ValueError('SINGLE_RACE_SAVED_INPUT_DIAGNOSTIC_ONLY')
    for name in ('race_date','race_no','provider_race_id','distance','program_runner_count','scheduled_post_at','prediction_cutoff'):
        if evidence['race'].get(name)!=race.get(name):raise ValueError('SINGLE_RACE_SAVED_INPUT_RACE_MISMATCH:'+name)
    calendar=gzip.decompress((folder/'calendar.html.gz').read_bytes())
    if sources[0]['url']!=CALENDAR or program_link(calendar,day)!=sources[1]['url']:
        raise ValueError('SINGLE_RACE_SAVED_INPUT_OBSERVED_PROGRAM_LINK')
    canonical=ORIGIN+'/uma_shosai/'+race['provider_race_id']+'.do'
    if (sources[2].get('http_status')!=302 or sources[2].get('source_url')!=race['observed_card_url']
            or sources[2].get('location')!=canonical or sources[3]['url']!=canonical):
        raise ValueError('SINGLE_RACE_SAVED_INPUT_OBSERVED_CARD_TRANSITION')
    metadata={**evidence,'race':race,'program_races':races}
    result=_single_observation(c,folder,metadata,historical=True)
    result['saved_input_binding']={'evidence_file_sha256':digest(evidence_path),'evidence_file_name':evidence_path.name,
        'original_source_times':[s['fetched_at'] for s in sources],
        'imported_at':result['source_imported_at'],'classification':'POSTCUTOFF_SAVED_SOURCE_IMPORT',
        'original_files_modified':False,'live_freshness_asserted':False}
    return result


def legacy_current_observations(folder,race,facts,client,reparse):
    """Unchanged c08 odds/changes acceptance for configurations without opt-in."""
    observations={}
    for key,url,parser in (
            ('odds',ORIGIN+'/odds/'+race['provider_race_id']+'01.do',parse_current_odds),
            ('changes',ORIGIN+'/henko_info/00000000000000.do',parse_current_changes)):
        raw_path=folder/(key+'.raw.html');receipt_path=folder/(key+'.receipt.json')
        if raw_path.exists() and receipt_path.exists():
            raw=raw_path.read_bytes();receipt=read(receipt_path)
        else:
            receipt,raw=client.get(url);immutable(raw_path,raw);save_json(receipt_path,receipt)
        observed=datetime.fromisoformat(receipt['fetched_at'])
        if observed>now() or now().timestamp()-observed.timestamp()>600:
            raise ValueError('SINGLE_RACE_CURRENT_CHANGE_OBSERVATION_EXPIRED')
        observations[key]=parser(raw,race,receipt,facts)
        version=sha({'parser':reparse['current_parser_sha256'],'raw':hashlib.sha256(raw).hexdigest(),
            'receipt':sha(receipt),'declared_facts':sha(facts)})
        save_json(folder/(key+'.parsed-'+version+'.json'),observations[key])
    return observations

def program_condition_observation(raw,receipt,race,*,single_scoped=False):
    """Carry observed program conditions into existing unsigned consumers."""
    observed=datetime.fromisoformat(receipt['fetched_at']);cutoff=datetime.fromisoformat(race['prediction_cutoff'])
    expected_url=ORIGIN+'/program/'+race['provider_race_id'][:-2]+'.do'
    if (observed.tzinfo is None or observed>now() or observed>=cutoff
            or receipt.get('url')!=expected_url or receipt.get('http_status')!=200
            or hashlib.sha256(raw).hexdigest()!=receipt.get('raw_sha256')):
        raise ValueError('PAPER_PROGRAM_CONDITION_RAW_RECEIPT_OR_TIME')
    conditions={}
    if single_scoped:
        from runtime.urw_nankan_reference_source import parse_single_program
        rows=parse_single_program(raw,receipt['url'],race['race_date'],condition_observations=conditions)
    else:rows=parse_program(raw,receipt['url'],race['race_date'],condition_observations=conditions)
    expected=next((row for row in rows if row['race_no']==race['race_no']),None)
    if expected is None or any(expected[key]!=race[key] for key in
            ('provider_race_id','distance','program_runner_count','scheduled_post_at','prediction_cutoff')):
        raise ValueError('PAPER_PROGRAM_CARD_CONTEXT')
    values={key:conditions[key] for key in ('weather','track_condition')
        if conditions.get(key+'_reason')=='OBSERVED_CURRENT_HEADER_LABEL' and conditions.get(key)}
    return seal({'values':values,'source':copy.deepcopy(receipt),'source_refs':[receipt['url']],
        'observed_at':receipt['fetched_at'],'parsed_header':conditions,
        'provenance':'OBSERVED_NANKAN_PROGRAM_NOT_SIGNED_SOURCE'})


def source_observation(source_root, day, number, *, diagnostic_reparse=False):
    root=Path(source_root);folder=root/f'sources/R{number:02}'
    evidence=read(folder/'reference_evidence.json');_check_sha(evidence)
    race=evidence['race'];receipt=read(folder/'card.receipt.json');raw=(folder/'card.raw.html').read_bytes()
    provider_id=race.get('provider_race_id','')
    observed=datetime.fromisoformat(receipt['fetched_at'])
    if (observed.tzinfo is None or observed>now()
            or observed>=datetime.fromisoformat(race['prediction_cutoff'])):
        raise ValueError('PAPER_SOURCE_NOT_AVAILABLE_BEFORE_CUTOFF')
    if (race.get('race_date')!=day or race.get('race_no')!=number or race.get('venue_id')!='URW'
            or not provider_id.startswith(day.replace('-','')+'18') or not provider_id.endswith(f'{number:02}')
            or receipt['raw_sha256']!=hashlib.sha256(raw).hexdigest()
            or receipt not in evidence['sources'] or receipt.get('http_status')!=200
            or receipt.get('source_policy',{}).get('usage_scope')!='USER_PERSONAL_NONCOMMERCIAL_PRIVATE_ONLY_NOT_PUBLIC_REDISTRIBUTION'):
        raise ValueError('PAPER_SOURCE_RAW_RECEIPT_OR_RACE_IDENTITY')
    facts=parse_card(raw,race,receipt['url']);verify_history_asof(facts,receipt['fetched_at'])
    if diagnostic_reparse and now()<datetime.fromisoformat(race['prediction_cutoff']):
        raise ValueError('PAPER_HISTORICAL_REPARSE_REQUIRES_POSTCUTOFF')
    if not diagnostic_reparse and facts!=evidence['runners']:raise ValueError('PAPER_RAW_PARSE_DIFFERS_FROM_SAVED_FACTS')
    ids=[f['runner_id'] for f in facts]
    if len(ids)!=len(set(ids)):raise ValueError('PAPER_DUPLICATE_DECLARED_RUNNER')
    program=(root/'program/program.raw.html').read_bytes();pr=read(root/'program/program.receipt.json')
    if hashlib.sha256(program).hexdigest()!=pr['raw_sha256']:raise ValueError('PAPER_PROGRAM_RAW_RECEIPT')
    conditions=program_condition_observation(program,pr,race) if diagnostic_reparse else None
    if not diagnostic_reparse:
        rows=parse_program(program,pr['url'],day)
        expected=next((r for r in rows if r['race_no']==number),None)
        if expected is None or any(expected[k]!=race[k] for k in ('provider_race_id','distance','program_runner_count','scheduled_post_at','prediction_cutoff')):
            raise ValueError('PAPER_PROGRAM_CARD_CONTEXT')
    result={'race':race,'facts':facts,'source':receipt,'active_verified':False,'signed_source_claim':False}
    if conditions is not None:result['program_conditions']=conditions
    if diagnostic_reparse:
        result['historical_reparse']={'classification':'POSTCUTOFF_REPARSE_OF_GENUINE_PRESTART_RAW',
            'original_evidence_sha256':evidence['sha256'],'original_facts_sha256':sha(evidence['runners']),
            'original_parser_sha256':evidence['parser_sha256'],'current_facts_sha256':sha(facts),
            'current_parser_sha256':digest(ROOT/'runtime/urw_nankan_reference_source.py'),
            'reparsed_at':now().isoformat(),'original_files_modified':False}
    return result

def numerical(observation, race_id):
    """Thin fact transport into the byte-unchanged, shared 63-rule compiler."""
    o=observation;race={**o['race'],'class':o['race']['race_name'],'venue':'URW'}
    facts=[]
    for fact in o['facts']:
        if fact['status']!='ACTIVE_DECLARED':continue
        row=copy.deepcopy(fact)
        row.update(race_card_source_id='NANKAN-CARD:'+race['provider_race_id'],
            race_card_snapshot_sha256=o['source']['raw_sha256'],race_card_fetched_at=o['source']['fetched_at'])
        facts.append(row)
    if len(facts)<3:raise ValueError('PAPER_INSUFFICIENT_DECLARED_RUNNERS')
    req={'family_id':'LOCAL','venue_id':'URW','provider':'NANKAN_OFFICIAL','race_id':race_id,'race':race,
        'runners':[{'runner_id':f['runner_id'],'name':f['name']} for f in facts],
        'production_authority':False,'signed_source_claim':False,'formal_source_claim':False,'active_verified':False,
        'input_observation':{'raw_sha256':o['source']['raw_sha256'],'source_fetched_at':o['source']['fetched_at'],'source_url':o['source']['url']}}
    conditions=o.get('program_conditions') or {}
    if conditions:
        _check_sha(conditions)
        req['input_observation'].update(program_conditions_sha256=conditions['sha256'],
            program_raw_sha256=conditions['source']['raw_sha256'],program_observed_at=conditions['observed_at'])
    normalized={key:{'value':conditions['values'][key],'source_refs':conditions['source_refs']}
        for key in ('weather','track_condition') if conditions.get('values',{}).get(key)}
    source={'source_snapshot_sha256':o['source']['raw_sha256'],'source_freeze_at':o['source']['fetched_at'],'normalized_evidence':normalized}
    n=materialize_candidate(compile_parsed_candidate_evidence(source,req,{f['runner_id']:f for f in facts}))
    n=seal({k:v for k,v in n.items() if k!='sha256'})
    s=n['candidate_full_numerical_summary']
    if not s['numeric_transport_complete'] or s['terminalized_count']!=len(facts)*29 or s['unresolved_count']:
        raise ValueError('PAPER_FULL29_NOT_TERMINAL')
    return n

def original_portfolio(pred):
    template={'semantic_request':{'family_id':'LOCAL','race_id':pred['race_id'],
        'runners':[{'runner_id':x} for x in pred['ranking']],
        'capital_policy':{'mode':'HARD_RACE_BUDGET','max_race_capital':0,'insufficient_action':'PAPER'}}}
    return registered._research_mec(pred,template)

def krs_input(n,pred,*,seed,runs):
    rows=copy.deepcopy(n['runners'])
    for row in rows:row['candidate_static_roles']=pred['role_columns'][str(row['runner_id'])]
    race={**n['race'],'prediction_id':n['race_id'],'racecourse':'浦和','date':n['race']['race_date'],
          'course_rule_version':URW_CANON,'surface':'dirt','course':'left'}
    return build_candidate_krs({**n,'race':race,'runners':rows,'seed':seed,'run_count':runs})['candidate_krs_input_data']

def simulate(folder, c, data, race_id, number, day,*,timeout_seconds=None):
    inp=folder/'krs.input.json';out=folder/'krs.output.json';receipt=folder/'engine.receipt.json'
    save_json(inp,data)
    if receipt.exists():
        r=read(receipt);_check_sha(r)
        if r['input_sha256']!=sha(data) or r['output_file_sha256']!=digest(out):raise ValueError('PAPER_ENGINE_REUSE_BINDING')
        return read(out),r
    if any((folder/name).exists() for name in ('engine.log','krs.output.json','krs.csv')):
        raise ValueError('PAPER_INTERRUPTED_ENGINE_ATTEMPT_PRESERVED_NO_DUPLICATE_RUN')
    start=now();wall=time.monotonic()
    with (folder/'engine.log').open('x') as log:
        try:
            subprocess.run([sys.executable,c['engine'],str(inp),'--output',str(out),'--csv',str(folder/'krs.csv'),
                '--params',c['parameters'],'--runs',str(c['runs']),'--seed',str(c['seed']),'--short'],
                stdout=log,stderr=subprocess.STDOUT,timeout=300 if timeout_seconds is None else timeout_seconds,check=True)
        except (subprocess.TimeoutExpired,subprocess.CalledProcessError) as exc:
            if timeout_seconds is None:raise
            save_json(folder/'engine-failure.json',{'status':'SINGLE_RACE_KRS_EXECUTION_FAILED',
                'started_at':start.isoformat(),'failed_at':now().isoformat(),'timeout_seconds':timeout_seconds,
                'error_type':type(exc).__name__,'completed_output_claim':False,'no_bet':False,
                'partial_attempt_preserved':True})
            raise ValueError('SINGLE_RACE_KRS_EXECUTION_FAILED:'+type(exc).__name__) from exc
    output=read(out);s=output['snapshot']
    if (s.get('prediction_id')!=race_id or s.get('date')!=day or s.get('race_no')!=number
            or s.get('run_count')!=c['runs'] or s.get('master_seed')!=c['seed']
            or {str(r['horse_no']) for r in output['summary']}!={str(r['horse_no']) for r in data['horses']}):
        raise ValueError('PAPER_ENGINE_SNAPSHOT_OR_UNIVERSE')
    r=seal({'started_at':start.isoformat(),'completed_at':now().isoformat(),'wall_seconds':time.monotonic()-wall,
        'engine_sha256':ENGINE,'parameter_map_sha256':PARAMETERS,'input_sha256':sha(data),
        'output_file_sha256':digest(out),'run_count':c['runs'],'master_seed':c['seed'],
        'external_signed_receipt':False,'actual_engine_executed':True})
    save_json(receipt,r);return output,r

def tree(pred,tickets):
    result=render_ticket_tree({'static_prediction':{'ranking':pred['ranking']},
        'final_ticket':{'tickets':tickets,'no_bet':not tickets},'capital_policy_decision':{'decision':'PAPER'}})
    if canonical_tickets(result['reflattened_tickets'])!=canonical_tickets(tickets):raise ValueError('PAPER_DELIVERY_TREE_MISMATCH')
    return result

def calculation_pins(c,models):
    result={'execution_head':registered.head(),
        'code_sha256':{name:digest(ROOT/name) for name in (*registered.CODE_FILES,
            'runtime/local_nar_evidence_candidate.py','runtime/local_fullnumerical_candidate.py',
            'runtime/urw_registered_paper_entry.py','runtime/krs_prediction_utility.py',
            'mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json',
            'mapping/local_full_numerical_mapping_v0.1_candidate_20260923.json')},
        'models':{arm:models[arm]['sha256'] for arm in ARMS},'policy_sha256':sha(POLICY),
        'model_bundle_file_sha256':digest(c['model_bundle']),
        'engine_sha256':digest(c['engine']),'parameters_sha256':digest(c['parameters']),
        'master_seed':c['seed'],'run_count':c['runs']}
    profile=single_source_profile(c)
    if profile:result['source_contract']=profile
    return result

def price_free_consumer_audit(observation,numerical,pack):
    """Check the real consumer inputs; do not alter a value or missing rule."""
    values={rid:{key:features.get(key) for key in ('INDEX:PRI','INDEX:OPI-V')}
            for rid,features in pack['runners'].items()}
    if (any(f.get('odds') is not None or f.get('popularity') is not None for f in observation['facts'])
            or any(value is not None for row in values.values() for value in row.values())
            or POLICY['price_or_ev_used'] is not False):
        raise ValueError('SINGLE_RACE_SOURCE_PROFILE_PRICE_CONSUMER_DETECTED')
    return seal({'source_contract_sha256':observation['source_contract']['file_sha256'],
        'numerical_sha256':numerical['sha256'],'feature_pack_sha256':pack['sha256'],
        'market_observations_kept_outside_numerical_and_owner_inputs':True,
        'market_index_feature_values':values,'selector_price_or_ev_used':False,
        'price_or_probability_imputation_performed':False})

def portfolio_inactive_ids(observation,prediction):
    inactive=[f['runner_id'] for f in observation['facts'] if f['status']!='ACTIVE_DECLARED']
    if observation.get('source_contract'):
        # Numerical already removed these horses. The selector accepts only
        # exclusions inside its own universe; never reinsert a scratched horse.
        if set(inactive)&set(prediction['ranking']):raise ValueError('PAPER_INACTIVE_RUNNER_REACHED_OWNER')
        return []
    return inactive

def single_stage_clock(observation,stage,*,reserve_seconds=0,require_pre_cutoff=True):
    """Check actual input-use time. Historical imports grant no fresh claim."""
    profile=observation.get('source_contract')
    if not profile or profile['id']!=RACE_SCOPED_PROFILE:return None
    current=now();cutoff=datetime.fromisoformat(observation['race']['prediction_cutoff'])
    if observation.get('historical_diagnostic'):
        return {'stage':stage,'observed_at':current.isoformat(),'historical_diagnostic':True,
            'live_freshness_asserted':False,'prediction_cutoff':cutoff.isoformat()}
    values=[s['fetched_at'] for i,s in enumerate(observation['original_receipts']) if i in (0,1,3)]
    values+=[v['source_fetched_at'] for k,v in observation['current_observations'].items()
             if k in ('changes','odds')]
    times=[datetime.fromisoformat(v) for v in values]
    if any(t.tzinfo is None or t>current for t in times):raise ValueError('SINGLE_RACE_SOURCE_USE_TIME_UNKNOWN:'+stage)
    expiry=min(t.timestamp()+600 for t in times)
    if current.timestamp()>=expiry:raise ValueError('SINGLE_RACE_SOURCE_EXPIRED_AT_USE:'+stage)
    if require_pre_cutoff and current>=cutoff:raise ValueError('SINGLE_RACE_CUTOFF_BEFORE_STAGE:'+stage)
    remaining=min(expiry,cutoff.timestamp())-current.timestamp()
    if reserve_seconds and remaining<=reserve_seconds:
        raise ValueError('SINGLE_RACE_DELIVERY_BUDGET_EXHAUSTED:'+stage)
    return {'stage':stage,'observed_at':current.isoformat(),'historical_diagnostic':False,
        'source_expires_at':datetime.fromtimestamp(expiry,timezone.utc).isoformat(),
        'prediction_cutoff':cutoff.isoformat(),'remaining_seconds':remaining,
        'delivery_reserve_seconds':reserve_seconds,'live_freshness_asserted':True}

def record_stage_clock(observation,stage,events,folder,**kwargs):
    try:record=single_stage_clock(observation,stage,**kwargs)
    except ValueError as exc:
        save_json(folder/('pipeline-failure-'+stage+'.json'),{'stage':stage,'failed_at':now().isoformat(),
            'reason':str(exc),'prediction_cutoff':observation['race']['prediction_cutoff'],
            'source_fetched_at':observation['source']['fetched_at'],'source_imported_at':observation.get('source_imported_at'),
            'preceding_stage_observations':events,'forward_completion':False,'no_bet':False})
        raise
    events.append(record)
    return record


def prepare(config_path, intent):
    os.umask(0o077)
    c,reg,models=configuration(config_path);day=intent['race_date'];number=intent['race_no']
    single=c.get('execution_mode')==SINGLE_MODE
    pins=calculation_pins(c,models)
    profile=single_source_profile(c);scoped=bool(profile and profile['id']==RACE_SCOPED_PROFILE)
    scoped_saved=scoped and day+f'/R{number:02}' in c.get('single_saved_source_folders',{})
    if scoped and c.get('source_root'):raise ValueError('SINGLE_RACE_SCOPED_LEGACY_SOURCE_ROOT_FORBIDDEN')
    saved_diagnostic=False
    if single and not scoped and c.get('allow_postcutoff_diagnostic') and c.get('source_root'):
        path=Path(c['source_root'])/f'sources/R{number:02}/reference_evidence.json'
        if path.is_file():
            race=read(path)['race']
            saved_diagnostic=(race.get('race_date')==day and race.get('race_no')==number
                and now()>=datetime.fromisoformat(race['prediction_cutoff']))
    obs=(saved_single_observation(c,day,number) if scoped_saved else
        source_observation(c['source_root'],day,number,diagnostic_reparse=True) if saved_diagnostic else
        current_single_observation(c,day,number) if single else source_observation(c['source_root'],day,number))
    cutoff=datetime.fromisoformat(obs['race']['prediction_cutoff']);diagnostic=now()>=cutoff
    if diagnostic and not c.get('allow_postcutoff_diagnostic'):raise ValueError('PAPER_PAST_CUTOFF_NO_NEW_FORWARD')
    stage_times=[]
    if scoped:stage_times.append(single_stage_clock(obs,'SOURCE_READY'))
    # Live operation cannot skip the existing whole-day/checkpoint admission.
    if not diagnostic and not single:
        if c.get('current_v2_live_ledger_latestness')!='INDEPENDENT_PRIVATE_READBACK_VERIFIED':
            raise ValueError('PAPER_CURRENT_LIVE_LEDGER_LATESTNESS_NOT_VERIFIED')
        if not Path(reg['canonical_ledger_path']).is_dir():
            raise ValueError('PAPER_CURRENT_CANONICAL_LEDGER_NOT_RESTORED')
        ledger=registered._registered_context(reg)
        registered._verify_checkpoint(reg,ledger,SimpleNamespace(ledger_checkpoint=Path(c['checkpoint']),expected_checkpoint_sha256=c['checkpoint_sha256']))
        day_record=read(ledger/f'day-{day}.json');_check_sha(day_record)
        if day_record['registration_sha256']!=reg['sha256']:raise ValueError('PAPER_DAY_REGISTRATION')
    request_key=sha({'date':day,'number':number,'registration':reg['sha256'],'source':obs['source']['raw_sha256'],
        'current_observations':sha(obs.get('current_observations',{})),
        'program_conditions':sha(obs.get('program_conditions',{})),
        'calculation_dependencies':pins,
        'caller':digest(__file__),'seed':c['seed'],'runs':c['runs'],
        'classification':'DIAGNOSTIC' if diagnostic else SINGLE_CLASS if single else 'FORWARD'})
    folder=private_directory(Path(c['store'])/'races'/day/f'R{number:02}'/request_key)
    with private_lock(folder/'request.lock') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if (folder/'complete.json').exists():return read(folder/'complete.json')
        manifest={'calculation_pins':pins,'source_sha256':obs['source']['raw_sha256'],
            'execution_contract':SINGLE_MODE if single else 'REGISTERED_V2'}
        if obs.get('source_contract'):manifest['source_contract']=obs['source_contract']
        manifest_path=folder/'calculation-manifest.json'
        if manifest_path.exists():
            prior=read(manifest_path);_check_sha(prior)
            if {key:prior.get(key) for key in manifest}!=manifest:raise ValueError('PAPER_RESUME_CALCULATION_MANIFEST_MISMATCH')
        else:save_json(manifest_path,seal({**manifest,'started_at':now().isoformat()}))
        if obs.get('source_contract'):
            immutable(folder/'source-contract-profile.json',source_profile_path(obs['source_contract']).read_bytes())
        race_id=f'KM-LOCAL-URW-{day.replace("-","")}-R{number:02}-'+('DIAGNOSTIC' if diagnostic else 'SINGLE-NONPRODUCTION' if single else 'FORWARD-RESEARCH')+'-R1'
        observation_path=folder/'source-observation.json'
        if observation_path.exists():
            prior=read(observation_path)
            def original_binding(value):
                value=copy.deepcopy(value)
                if 'historical_reparse' in value:value['historical_reparse'].pop('reparsed_at',None)
                value.pop('source_imported_at',None)
                if 'saved_input_binding' in value:value['saved_input_binding'].pop('imported_at',None)
                return value
            if original_binding(prior)!=original_binding(obs):raise ValueError('PAPER_RESUME_SOURCE_OBSERVATION_MISMATCH')
            obs=prior
        else:save_json(observation_path,obs)
        npath=folder/'numerical.json'
        if scoped:record_stage_clock(obs,'NUMERICAL_INPUT_USE',stage_times,folder)
        if not npath.exists():save_json(npath,numerical(obs,race_id))
        n=read(npath);_check_sha(n);pack=parsed_owner_feature_pack(n)
        if obs.get('source_contract'):
            save_json(folder/'price-free-consumer-audit.json',price_free_consumer_audit(obs,n,pack))
        compath=folder/'comparison.json'
        if scoped:record_stage_clock(obs,'OWNER_INPUT_USE',stage_times,folder)
        if not compath.exists():
            if diagnostic:
                predictions={a:predict_conditioned_owner(m,pack,historical_replay=True) for a,m in models.items()}
                comparison=seal({'classification':'POSTCUTOFF_DIAGNOSTIC_NOT_A_PRESTART_FREEZE','race_id':race_id,
                    'race_date':day,'scheduled_post_at':obs['race']['scheduled_post_at'],'prediction_cutoff':cutoff.isoformat(),
                    'created_at':now().isoformat(),'feature_pack':pack,'models':models,'predictions':predictions,
                    'protocol':reg['existing_owner_protocol_unchanged'],'production_authority':False,'forward_oos_credit':0})
                save_json(compath,comparison)
            else:freeze_owner_forward_comparison(pack,models['BASELINE'],models['CANDIDATE'],protocol=reg['existing_owner_protocol_unchanged'],output=compath)
        comparison=read(compath);_check_sha(comparison);arms={};audits={}
        parallel={}
        if scoped:
            clock=record_stage_clock(obs,'KRS_INPUT_USE',stage_times,folder,
                reserve_seconds=profile['contract']['delivery_reserve_seconds'])
            timeout=profile['contract']['krs_max_wall_seconds']
            if not diagnostic:timeout=min(timeout,clock['remaining_seconds']-clock['delivery_reserve_seconds'])
            with ThreadPoolExecutor(max_workers=profile['contract']['krs_parallel_workers']) as workers:
                jobs={arm:workers.submit(simulate,private_directory(folder/arm),c,
                    krs_input(n,comparison['predictions'][arm],seed=c['seed'],runs=c['runs']),race_id,number,day,
                    timeout_seconds=timeout) for arm in ARMS}
                parallel={arm:job.result() for arm,job in jobs.items()}
            record_stage_clock(obs,'SELECTION_INPUT_USE',stage_times,folder,require_pre_cutoff=False)
        for arm in ARMS:
            af=private_directory(folder/arm);pred=comparison['predictions'][arm];original=original_portfolio(pred)
            data=krs_input(n,pred,seed=c['seed'],runs=c['runs'])
            output,er=parallel[arm] if scoped else simulate(af,c,data,race_id,number,day)
            utility=build_krs_prediction_utility(original['semantic_request'],{'status':'EXECUTED','output':output})
            ref={'original_prediction_sha256':pred['sha256'],'original_comparison_sha256':comparison['sha256'],
                'immutable_original_mec_sha256':original['mec']['sha256'],'immutable_semantic_sha256':sha(original['semantic_request']),
                'krs_utility_sha256':utility['sha256'],'krs_snapshot_sha256':sha(utility['snapshot']),
                'krs_master_seed':c['seed'],'krs_input_sha256':sha(data),'krs_output_file_sha256':er['output_file_sha256']}
            ts=canonical_tickets(original['mec']['tickets']);inactive=portfolio_inactive_ids(obs,pred)
            selected=select_portfolio(pred,ts,source_ref=ref,krs_utility=utility,excluded_runner_ids=inactive)
            off=select_portfolio(pred,ts,source_ref=ref,excluded_runner_ids=inactive)
            ranked=[h for h in pred['ranking'] if h not in inactive][:4]
            top4=canonical_tickets([{'bet_type':'EXACTA','selection':list(map(int,x)),'stake':100} for x in permutations(ranked,2)]+
                [{'bet_type':'TRIO','selection':list(map(int,x)),'stake':100} for x in combinations(ranked,3)])
            methods={'P0S1':{'selection':selected,'tickets':selected['selected_tickets']},
                'P0S1_NO_KRS':{'selection':off,'tickets':off['selected_tickets']},
                'TOP4_BOX_DIAGNOSTIC':{'tickets':top4,'no_bet_reason':None if top4 else 'FEWER_THAN_TWO_ELIGIBLE_TOP4_RUNNERS'}}
            for value in methods.values():value['tree']=tree(pred,value['tickets'])
            audits[arm]=seal({'race_id':race_id,'source_snapshot_sha256':obs['source']['raw_sha256'],
                'reference_static':pred,'master_seed':c['seed'],'started_at':er['started_at'],'completed_at':er['completed_at'],
                'snapshot':output['snapshot'],'semantic_request':original['semantic_request'],'mec':original['mec'],
                'krs_utility':utility,'krs_input_sha256':sha(data),'krs_output_file_sha256':er['output_file_sha256'],
                'ticket_tree':tree(pred,ts),'production_authority':False})
            arms[arm]={'prediction':pred,'original_mec':original,'engine_receipt':er,'krs_utility':utility,'methods':methods}
        forward=None
        if not diagnostic and not single:
            # The registered writer, not this transport, owns reservation/day budgets.
            bundle=folder/'forward-input.json';save_json(bundle,{'frozen':comparison,'audits':audits,'observation':obs})
            forward=private_directory(folder/'registered-freeze')
            existing=forward/'research-selection-freeze.json'
            if existing.exists():
                old=read(existing);_check_sha(old)
                events=registered._ledger_events(reg,Path(reg['canonical_ledger_path']))
                matching=[e for e in events if e.get('artifact_sha256')==old['sha256']
                    and e.get('status')=='FROZEN_PENDING_INDEPENDENT_ANCHOR']
                if len(matching)!=1 or old['input_bundle_sha256']!=sha(read(bundle)):
                    raise ValueError('PAPER_ORPHAN_FORWARD_ARTIFACT_NOT_ADMITTED')
            else:
                registered.freeze(SimpleNamespace(registration=Path(c['registration']),ledger=Path(reg['canonical_ledger_path']),
                    ledger_checkpoint=Path(c['checkpoint']),expected_checkpoint_sha256=c['checkpoint_sha256'],input_bundle=bundle,output=forward))
            accepted=read(forward/'research-selection-freeze.json')
            for arm in ARMS:
                view=accepted['views'][arm]
                for method,key in (('P0S1','P0S1'),('P0S1_NO_KRS','P0S1_NO_KRS')):
                    s=view['cells'][key]['selection'] if method=='P0S1' else view[key]
                    arms[arm]['methods'][method]={'selection':s,'tickets':s['selected_tickets'],'tree':tree(arms[arm]['prediction'],s['selected_tickets'])}
            registered.checkpoint(SimpleNamespace(registration=Path(c['registration']),output=folder/'checkpoint-after.json'))
        completed_clock=now()
        late_single=bool(scoped and single and not diagnostic and completed_clock>=cutoff)
        if not diagnostic and completed_clock>=cutoff and not late_single:
            raise ValueError('PAPER_CALCULATION_COMPLETED_AFTER_CUTOFF_NOT_FORWARD')
        if single and not diagnostic:
            raw_folder=private_directory(folder/'current-source-originals')
            for source_file in Path(obs['current_source_folder']).iterdir():
                if source_file.is_file() and source_file.name!='worker.lock':
                    immutable(raw_folder/source_file.name,source_file.read_bytes())
            immutable(folder/'execution-caller.py',Path(__file__).read_bytes())
        if calculation_pins(c,models)!=pins:raise ValueError('PAPER_CALCULATION_DEPENDENCIES_CHANGED_DURING_RUN')
        artifact_clock=now()
        if scoped and single and not diagnostic and artifact_clock>=cutoff:late_single=True
        artifact=seal({'classification':'POSTCUTOFF_DIAGNOSTIC_NOT_FORWARD' if diagnostic or late_single else SINGLE_CLASS if single else 'REGISTERED_FORWARD_PAPER_PENDING_PRIVATE_SAVE',
            'race_id':race_id,'provider_race_id':obs['race']['provider_race_id'],'race_date':day,'race_no':number,
            'created_at':artifact_clock.isoformat(),'prediction_cutoff':cutoff.isoformat(),'registration_sha256':reg['sha256'],
            'registered_head':reg['registered_head'],'execution_head':pins['execution_head'],
            'calculation_pins':pins,'calculation_manifest_sha256':read(folder/'calculation-manifest.json')['sha256'],
            'caller_sha256':digest(__file__),'source':obs['source'],'race':obs['race'],
            'numerical':n,'comparison':comparison,'arms':arms,'production_authority':False,'signed_final_claim':False,
            'forward_oos_credit':0,'private_storage_required':True,'public_redistribution_authorized':False,'actual_purchase':False,
            'original_v2_ledger_mutated':not diagnostic and not single,'current_active_verified':False,
            'registered_research_admitted':not diagnostic and not single,
            'registration_reference_scope':'IMMUTABLE_CALCULATION_PINS_ONLY_NO_COHORT_ADMISSION' if single else 'REGISTERED_V2',
            'source_observation':obs,
            **({'source_contract':obs['source_contract'],'revision':'SOURCE-'+request_key} if obs.get('source_contract') else {}),
            'source_latest_change_check':obs.get('latest_change_check','NOT_PERFORMED_SAVED_ASOF_ONLY'),'formal_quality_credit':0})
        if scoped:
            artifact=seal({**artifact,'pipeline_timing':{'source_imported_at':obs['source_imported_at'],
                'source_fetched_at':obs['source']['fetched_at'],'stage_observations':stage_times,
                'calculation_completed_at':completed_clock.isoformat(),'prediction_cutoff':cutoff.isoformat(),
                'precutoff_calculation_complete':not diagnostic and not late_single,
                'prediction_id_changed_after_calculation':False,'delivery_verified':False,
                'late_completion_diagnostic':late_single}})
            # A finished calculation is retained for inspection, but expired
            # observations cannot become a usable prestart original.
            if not diagnostic and not late_single:
                try:record_stage_clock(obs,'LOCAL_SAVE',stage_times,folder,require_pre_cutoff=False)
                except ValueError:
                    save_json(folder/'source-expired-calculation-diagnostic.json',seal({**artifact,
                        'classification':'SINGLE_RACE_SOURCE_EXPIRED_CALCULATION_NOT_FORWARD',
                        'precutoff_delivery_eligible':False,'forward_completion':False}))
                    raise
        artifact=seal(artifact)
        save_json(folder/'calculation.json',artifact)
        body=render(artifact);immutable(folder/'readback.txt',body.encode())
        archive=folder/'private-artifact.zip'
        files=[p for p in folder.rglob('*') if p.is_file() and p.name not in ('request.lock','private-artifact.zip')]
        manifest={str(p.relative_to(folder)):{'bytes':p.stat().st_size,'sha256':digest(p)} for p in files}
        with ZipFile(archive,'x',compression=ZIP_DEFLATED) as z:
            for p in files:z.write(p,str(p.relative_to(folder)))
            z.writestr('BYTE_MANIFEST.json',json.dumps(manifest,ensure_ascii=False,sort_keys=True))
        result=seal({'status':'PRIVATE_SAVE_REQUIRED','race_id':race_id,'race_date':day,'race_no':number,
            'folder':str(folder),'archive':str(archive),'archive_sha256':digest(archive),'artifact_sha256':artifact['sha256'],
            'source_sha256':artifact['source']['raw_sha256'],'revision':artifact_revision(artifact),
            'answer_sha256':digest(folder/'readback.txt'),'classification':artifact['classification'],
            'completed_at':now().isoformat(),'chat_render_verified':False,'user_received':False})
        if scoped:
            result=seal({**result,'local_archive_completed_before_cutoff':now()<cutoff,
                'precutoff_delivery_verified':False,'source_fetched_at':obs['source']['fetched_at'],
                'prediction_cutoff':cutoff.isoformat(),'calculation_completed_at':completed_clock.isoformat(),
                'cold_postcutoff_execution':False,'late_completion_diagnostic':late_single})
        save_json(folder/'complete.json',result);return result

def portfolio_status(prediction,method):
    """Validate a calculated portfolio; absent data is never a zero-ticket result."""
    if (not isinstance(method,dict) or method.get('status')=='NOT_CALCULATED'
            or not isinstance(method.get('tickets'),list) or not isinstance(method.get('tree'),dict)):
        raise ValueError('PAPER_PORTFOLIO_NOT_CALCULATED')
    tickets=method['tickets'];expected=tree(prediction,tickets)
    if expected!=method['tree']:raise ValueError('PAPER_CATALOG_TREE_CHANGED')
    if any(str(h) not in prediction['ranking'] for t in tickets for h in t['selection']):
        raise ValueError('PAPER_PORTFOLIO_RUNNER_OUTSIDE_OWNER')
    stake=sum(t['stake'] for t in tickets);selection=method.get('selection')
    budget=POLICY['race_cap_yen']
    if selection is not None:
        if canonical_tickets(selection['selected_tickets'])!=canonical_tickets(tickets):
            raise ValueError('PAPER_SELECTION_TICKETS_MISMATCH')
        budget=selection['race_budget_yen']
        if (selection['used_budget_yen']!=stake or selection['unused_budget_yen']!=budget-stake
                or selection['no_bet'] is not (not tickets)):
            raise ValueError('PAPER_PORTFOLIO_ACCOUNTING_MISMATCH')
    if type(budget) is not int or budget>POLICY['race_cap_yen'] or not 0<=stake<=budget:
        raise ValueError('PAPER_PORTFOLIO_RESEARCH_BUDGET_MISMATCH')
    reason=(selection or {}).get('no_bet_reason') or method.get('no_bet_reason')
    if not tickets and not reason:raise ValueError('PAPER_EMPTY_PORTFOLIO_WITHOUT_CALCULATED_NO_BET_REASON')
    return {'count':len(tickets),'stake':stake,'unused':budget-stake,
        'state':'NO-BET' if not tickets else '計算済・研究票','no_bet_reason':reason}


def calculated_portfolios(artifact):
    result={}
    for arm in ARMS:
        view=artifact.get('arms',{}).get(arm,{})
        for method in METHODS:
            result[arm,method]=portfolio_status(view.get('prediction',{}),view.get('methods',{}).get(method))
    return result


def render(artifact):
    a=artifact;n=a['numerical'];s=n['candidate_full_numerical_summary'];b=a['arms']['BASELINE'];c=a['arms']['CANDIDATE']
    def clock_text(value):
        return datetime.fromisoformat(value).astimezone(JST).isoformat() if a.get('source_contract') else value
    portfolios=calculated_portfolios(a)
    names={str(r['runner_id']):r['name'] for r in n['runners']}
    for view in (b,c):
        pred=view['prediction']
        if (len(pred['ranking'])!=len(names) or set(pred['ranking'])!=set(names)
                or any(rid not in pred['role_columns'] or rid not in pred['missingness'] for rid in names)
                or any(set(pred.get('rankings_by_role',{}).get(role,[]))!=set(names) for role in ('W','P2','P3'))
                or len(view['krs_utility']['summary'])!=len(names)
                or {str(row['horse_no']) for row in view['krs_utility']['summary']}!=set(names)):
            raise ValueError('PAPER_ALL_HORSE_PRESENTATION_INCOMPLETE')
    lines=[f"浦和{a['race_no']}R｜{a['race_date']}｜{a['classification']}",
        f"Provider {a['provider_race_id']} / Race {a['race_id']}",
        f"計算保存時刻 {clock_text(a['created_at'])} / 参考Cutoff {clock_text(a['prediction_cutoff'])}",
        f"SOURCE原取得 {clock_text(a['source']['fetched_at'])}。変更確認：{a.get('source_latest_change_check','未検証')}。正式Verified Activeではありません。",
        ('FORMAL HOLD。期限後の新計算はDiagnosticであり、事前予測・正式FINAL・未知未来OOSに算入しません。' if a['classification'].startswith('POSTCUTOFF') else
         '通常単一Raceの発走前・非Production計算。v2研究登録への算入なし／台帳・日予算予約変更なし／OOS加点0。正式署名・購入認可ではありません。' if a['classification']==SINGLE_CLASS else
         'REGISTERED PAPER / 非Production。正式署名・購入認可ではありません。'),
        f"全{len(names)}頭×29={s['required_count']}セル：実計算{s['calculated_count']}、規則中立{s['ruled_neutral_count']}、未解決{s['unresolved_count']}。",
        f"numeric_transport_complete={s.get('numeric_transport_complete','未記録')} / full_numerical_complete={s.get('full_numerical_complete','未記録')}。",
        f"元観測成分の平均coverage={s.get('mean_real_component_coverage','未記録')} / 中立化された欠測成分数={s.get('candidate_neutral_missing_component_count','未記録')}。セルの終端処理と観測充足率は別です。",
        '全馬登録モデル評価（UNKNOWNは観測不足であり能力不足ではありません）',
        '|馬番・馬名|B順位|C順位|B Role|C Role|入力pack観測数|欠測|','|---|---:|---:|---|---|---|---|']
    if a.get('source_contract'):
        frozen=a.get('comparison',{}).get('frozen_at') or a.get('comparison',{}).get('created_at') or a['created_at']
        lines.insert(3,'発走予定 '+clock_text(a['race']['scheduled_post_at'])+' / Static Freeze '+clock_text(frozen))
    for rid in sorted(names,key=int):
        pb=b['prediction'];pc=c['prediction']
        missing=' / '.join(arm+': '+(','.join(pred['missingness'][rid])+'（観測不足）' if pred['missingness'][rid] else 'なし')
            for arm,pred in (('B',pb),('C',pc)))
        features=a.get('comparison',{}).get('feature_pack',{}).get('runners',{}).get(rid)
        coverage=(f"{sum(value is not None for value in features.values())}/{len(features)}" if features is not None else '未記録')
        if a.get('source_contract'):
            missing+=f" / UNKNOWN件数 B={len(pb['missingness'][rid])},C={len(pc['missingness'][rid])}"
        lines.append(f"|{rid} {names[rid]}|{pb['ranking'].index(rid)+1}|{pc['ranking'].index(rid)+1}|{','.join(pb['role_columns'][rid]) or '—'}|{','.join(pc['role_columns'][rid]) or '—'}|{coverage}|UNKNOWN {missing}|")
    lines.append('入力pack観測数は元の特徴キー集合が分母です。Ownerが消費する学習済み特徴スロット数とは区別します。')
    lines+=['研究6系列は独立会計。6案の合算を購入推奨としません。単位100円、1系列上限2,000円。',
            '|Owner / 方式|点数|仮想額|未使用額|状態|','|---|---:|---:|---:|---|']
    for arm in ARMS:
        for method in METHODS:
            state=portfolios[arm,method]
            lines.append(f"|{arm}/{method}|{state['count']}|{state['stake']}円|{state['unused']}円|{state['state']}|")
    for arm in ARMS:
        x=a['arms'][arm];pred=x['prediction'];er=x['engine_receipt'];u=x['krs_utility']
        lines.append(f"\n{arm}｜W/P2/P3")
        fits=a.get('comparison',{}).get('models',{}).get(arm,{}).get('fits',[])
        if len(fits)==3:
            lines.append('Owner学習済み特徴スロット数（条件付き展開後・観測数ではない）：'+
                ' / '.join(role+'='+str(len(set(fit['feature_names']))) for role,fit in zip(('W','P2','P3'),fits)))
        for role in ('W','P2','P3'):lines.append(role+' = '+','.join(h for h in pred['rankings_by_role'][role] if role in pred['role_columns'][h]))
        lines.append(f"KRS {er['run_count']}回 / seed {er['master_seed']} / 実完了 {clock_text(er['completed_at'])}")
        lines.append(f"展開・KRS：先導候補{u['snapshot'].get('primary_leader_no','UNKNOWN')}番／SIM-DCR {u['snapshot'].get('SIM-DCR','UNKNOWN')}／検証シナリオ {','.join(u.get('scenario_worlds',[]))}。判断区分{u['utility_class']}。")
        lines.append('SSR-W / SSR-P2 / SSR-P3（未較正のシミュレーション支持値。実勝率・EVではない）')
        for row in sorted(u['summary'],key=lambda r:int(r['horse_no'])):
            lines.append(f"{row['horse_no']}: {row['SSR-W']:.4f} / {row['SSR-P2']:.4f} / {row['SSR-P3']:.4f}")
        for method in METHODS:
            m=x['methods'][method];lines.append('\n'+arm+' / '+method+'｜全選択票・各Stake')
            lines.append(m['tree']['text'])
            for ticket in m['tickets']:
                lines.append('└─ '+ticket['bet_type']+' '+('→' if ticket['bet_type'] in ('EXACTA','TRIFECTA') else '・').join(map(str,ticket['selection']))+f"：{ticket['stake']}円")
            state=portfolios[arm,method]
            lines.append(f"合計{state['count']}点 / 試算{state['stake']}円 / 未使用{state['unused']}円 / {state['state']}"+
                (f"：{state['no_bet_reason']}" if not state['count'] else ''))
            if 'selection' in m:
                se=m['selection'];lines.append(f"Core/Protection={se['tier_spend_yen']} / 未使用{se['unused_budget_yen']}円 / NO-BET理由={se['no_bet_reason']}")
    lines+=['\n最終結論：登録済みモデル・既存選択Policyによる計算結果です。購入推奨・性能合格ではありません。',
        '全29指数・各Provenance・非選択票・完全KRSは同一の私有原本に保存。',
        '計算固定参照ID（研究算入とは別） '+a['registration_sha256'],'原本Artifact SHA '+a['sha256'],'SOURCE Raw SHA '+a['source']['raw_sha256']]
    if a.get('calculation_pins'):
        pins=a['calculation_pins']
        lines+=['実行コードHEAD '+pins['execution_head'],'計算依存Manifest SHA '+a['calculation_manifest_sha256'],
            'モデルSHA '+json.dumps(pins['models'],sort_keys=True),'Policy SHA '+pins['policy_sha256'],
            'Engine SHA '+pins['engine_sha256']+' / Parameter SHA '+pins['parameters_sha256']]
    if a.get('source_contract'):
        profile=a['source_contract'];market=a['source_observation']['current_observations']['market']
        lines+=['発走予定 '+a['race']['scheduled_post_at'],'Revision '+str(a.get('revision',artifact_revision(a))),
            'SOURCE受入れprofile '+profile['id'],
            'SOURCE契約SHA '+profile['file_sha256'],'市場状態 '+market['status']+' / '+str(market['reason']),
            '出走根拠：同時点の公式Program・Cardと日付付き公式変更。正式Verified Active・署名SOURCEではありません。',
            '価格消費なし。価格・betting membership未観測を0や確認済みへ補完していません。']
    return '\n'.join(lines)+'\n'

def publish(config_path, complete_path, readback_zip, storage_receipt_path):
    c,reg,_=configuration(config_path);complete=read(complete_path);_check_sha(complete)
    folder=Path(complete['folder']);private_directory(folder)
    if digest(readback_zip)!=complete['archive_sha256'] or digest(complete['archive'])!=complete['archive_sha256']:
        raise ValueError('PAPER_EXTERNAL_READBACK_BYTE_MISMATCH')
    receipt=read(storage_receipt_path)
    if not receipt.get('storage_id') or not receipt.get('provider_created_at') or receipt.get('readback_sha256')!=digest(readback_zip):
        raise ValueError('PAPER_EXTERNAL_STORAGE_RECEIPT_MISSING')
    with ZipFile(readback_zip) as z:
        manifest=json.loads(z.read('BYTE_MANIFEST.json'))
        if set(z.namelist())!=set(manifest)|{'BYTE_MANIFEST.json'}:raise ValueError('PAPER_REMOTE_ARCHIVE_MEMBERS')
        for name,ref in manifest.items():
            raw=z.read(name)
            if len(raw)!=ref['bytes'] or hashlib.sha256(raw).hexdigest()!=ref['sha256']:raise ValueError('PAPER_REMOTE_ARCHIVE_BYTES')
        artifact=json.loads(z.read('calculation.json'));_check_sha(artifact)
        if artifact['sha256']!=complete['artifact_sha256'] or z.read('readback.txt')!=(folder/'readback.txt').read_bytes():
            raise ValueError('PAPER_REMOTE_CALCULATION_OR_ANSWER_MISMATCH')
        artifact_binding(artifact,complete)
        if not artifact['classification'].startswith('POSTCUTOFF'):
            if (datetime.fromisoformat(receipt['provider_created_at'])>=datetime.fromisoformat(artifact['prediction_cutoff'])
                    or now()>=datetime.fromisoformat(artifact['prediction_cutoff'])):
                raise ValueError('PAPER_EXTERNAL_SAVE_OR_READBACK_AFTER_CUTOFF')
            if artifact['classification']!=SINGLE_CLASS and 'checkpoint-after.json' not in manifest:raise ValueError('PAPER_UPDATED_CHECKPOINT_MISSING')
    single=(artifact['classification']==SINGLE_CLASS or
        artifact.get('registration_reference_scope')=='IMMUTABLE_CALCULATION_PINS_ONLY_NO_COHORT_ADMISSION')
    if single and c.get('execution_mode')!=SINGLE_MODE:raise ValueError('SINGLE_RACE_PUBLICATION_CONTRACT_MISMATCH')
    checkpoint_sha=None if single else (manifest['checkpoint-after.json']['sha256']
                    if not artifact['classification'].startswith('POSTCUTOFF') else c['checkpoint_sha256'])
    pub=seal({**complete,'status':'VERIFIED_PRIVATE_RESEARCH_READBACK','storage':receipt,
        'source_sha256':artifact.get('source',{}).get('raw_sha256'),'revision':artifact_revision(artifact),
        'registration_sha256':reg['sha256'],'private_storage_required':True,'public_redistribution_authorized':False,
        'checkpoint_file_sha256':checkpoint_sha,
        'checkpoint_scope':'NOT_APPLICABLE_NO_V2_LEDGER_MUTATION' if single else 'INITIAL_SNAPSHOT_NOT_CURRENT_LIVE_LEDGER' if artifact['classification'].startswith('POSTCUTOFF') else 'UPDATED_CHECKPOINT_INCLUDED_IN_READBACK_ARCHIVE',
        'published_at':now().isoformat(),'formal_final_proven':False,'forward_oos_credit':0})
    dest=private_directory(Path(c['store'])/'publications'/complete['race_date']/f"R{complete['race_no']:02}")
    save_json(dest/(complete['artifact_sha256']+'.json'),pub)
    return pub


def artifact_binding(artifact,pointer):
    for field in ('race_date','race_no','race_id','classification'):
        if artifact.get(field)!=pointer.get(field):raise ValueError('PAPER_CATALOG_ARTIFACT_IDENTITY_MISMATCH:'+field)
    for field,value in (('source_sha256',artifact.get('source',{}).get('raw_sha256')),
                        ('revision',artifact_revision(artifact))):
        if field in pointer and pointer[field]!=value:raise ValueError('PAPER_CATALOG_ARTIFACT_IDENTITY_MISMATCH:'+field)


def artifact_revision(artifact):
    if 'revision' in artifact:return str(artifact['revision'])
    match=re.search(r'-R(\d+)$',artifact['race_id'])
    return match.group(1) if match else None


def readback_matches(artifact,intent):
    values={'classification':artifact['classification'],'artifact_sha256':artifact['sha256'],
        'source_sha256':artifact.get('source',{}).get('raw_sha256'),'revision':artifact_revision(artifact)}
    return all(str(values[key])==str(intent[key]) for key in values if intent.get(key) is not None)


def read_delivery(config_path,intent):
    c,reg,_=configuration(config_path);root=Path(c['store'])/'publications'/intent['race_date']/f"R{intent['race_no']:02}"
    rows=[]
    for p in root.glob('*.json'):
        pub=read(p);_check_sha(pub)
        if pub['registration_sha256']!=reg['sha256'] or pub['race_no']!=intent['race_no'] or pub['race_date']!=intent['race_date']:
            raise ValueError('PAPER_CATALOG_RACE_OR_REGISTRATION_MIX')
        folder=Path(pub['folder']);private_directory(folder)
        if not folder.resolve().is_relative_to((Path(c['store'])/'races'/intent['race_date']/f"R{intent['race_no']:02}").resolve()):
            raise ValueError('PAPER_CATALOG_FOLDER_OUTSIDE_RACE_STORE')
        if digest(folder/'readback.txt')!=pub['answer_sha256']:raise ValueError('PAPER_CATALOG_ANSWER_SHA')
        artifact=read(folder/'calculation.json');_check_sha(artifact)
        if artifact['sha256']!=pub['artifact_sha256']:raise ValueError('PAPER_CATALOG_ARTIFACT_SHA')
        if artifact['classification']!=pub['classification']:raise ValueError('PAPER_CATALOG_CLASSIFICATION_MISMATCH')
        artifact_binding(artifact,pub)
        if c.get('execution_mode')==SINGLE_MODE:
            if artifact['classification']!=SINGLE_CLASS and not (c.get('allow_postcutoff_diagnostic')
                    and artifact['classification'].startswith('POSTCUTOFF')
                    and artifact.get('registration_reference_scope')=='IMMUTABLE_CALCULATION_PINS_ONLY_NO_COHORT_ADMISSION'):continue
            if artifact.get('registered_research_admitted') is not False or artifact.get('original_v2_ledger_mutated') is not False:
                raise ValueError('SINGLE_RACE_CANNOT_CLAIM_V2_ADMISSION')
        elif artifact['classification']==SINGLE_CLASS:
            raise ValueError('SINGLE_RACE_CANNOT_ENTER_REGISTERED_CATALOG')
        if artifact['classification'].startswith('POSTCUTOFF') and now()<datetime.fromisoformat(artifact['prediction_cutoff']):continue
        # Validate every independent portfolio, then select an exact original.
        calculated_portfolios(artifact)
        if not readback_matches(artifact,intent):continue
        rows.append((pub,artifact))
    if not rows:return None
    # A later diagnostic must not replace a valid pre-cutoff registered freeze.
    # Upload time cannot turn stale SOURCE into a newer prediction Revision.
    def order(row):
        pointer,artifact=row
        def timestamp(value):return datetime.fromisoformat(value).timestamp() if value else float('-inf')
        return (not artifact['classification'].startswith('POSTCUTOFF'),
            timestamp(artifact.get('source',{}).get('fetched_at')),
            timestamp(artifact.get('created_at')),timestamp(pointer.get('published_at')))
    pub,artifact=max(rows,key=order)
    body=(Path(pub['folder'])/'readback.txt').read_text()
    if pub['storage'].get('url'):body+='\n本人用完全原本：'+pub['storage']['url']+'\n'
    return {**pub,'body':body,'execution_id':pub['race_id'],'source_contract':artifact.get('source_contract'),
        'prediction_cutoff':artifact.get('prediction_cutoff'),
        'source_fetched_at':artifact.get('source',{}).get('fetched_at'),
        'calculation_created_at':artifact.get('created_at'),
        'prediction_reexecution':False,'answer_required_parts':[body],
        'delivery':{'chat_render_verified':False,'user_acknowledgement_verified':False}}

def main():
    os.umask(0o077);p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',required=True)
    sub=p.add_subparsers(dest='action',required=True)
    for name in ('prepare','read'):
        q=sub.add_parser(name);q.add_argument('--query',required=True)
        if name=='read':
            for field in ('classification','artifact-sha256','source-sha256','revision'):q.add_argument('--'+field)
    q=sub.add_parser('publish');q.add_argument('--complete',required=True);q.add_argument('--readback',required=True);q.add_argument('--receipt',required=True)
    a=p.parse_args()
    if a.action=='publish':result=publish(a.config,a.complete,a.readback,a.receipt)
    else:
        from runtime.local_race_entry import resolve_chat_intent
        intent=resolve_chat_intent(a.query)
        if a.action=='read':intent.update({field:getattr(a,field) for field in
            ('classification','artifact_sha256','source_sha256','revision') if getattr(a,field) is not None})
        result=prepare(a.config,intent) if a.action=='prepare' else read_delivery(a.config,intent)
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()

"""Observed race identity and transfer provenance, not a new ability model.

JV-Data place codes: https://jra-van.jp/dlb/sdv/sdk/JV-Data4901.pdf
Collector/provider identity is not evidence of the organiser of a past start.
Unscoped numeric codes and partial name matches never establish JRA identity.
"""
from __future__ import annotations
import re
import unicodedata
from typing import Any

JRA_NAMES = ('札幌','函館','福島','新潟','東京','中山','中京','京都','阪神','小倉')
JV_JRA = {f'{i:02d}':name for i,name in enumerate(JRA_NAMES,1)}
LOCAL_NAMES = {'門別','帯広','帯広ば','北見','岩見沢','旭川','盛岡','水沢','上山','三条',
               '足利','宇都宮','高崎','浦和','船橋','大井','川崎','金沢','笠松','名古屋',
               '園田','姫路','益田','福山','高知','佐賀','荒尾','中津','紀三井寺'}
JV_LOCAL = dict(zip([str(i) for i in range(31,49)],
    ['北見','岩見沢','帯広','旭川','盛岡','水沢','上山','三条','足利','宇都宮','高崎',
     '浦和','船橋','大井','川崎','金沢','笠松','名古屋']))
JV_LOCAL.update(dict(zip([str(i) for i in range(50,60)],
    ['園田','姫路','益田','福山','高知','佐賀','荒尾','中津','札幌地方','函館地方'])))
JV_LOCAL.update({'30':'門別','49':'紀三井寺','60':'新潟地方','61':'中京地方'})
# NAR/NANKAN has a different namespace. Only these verified South Kanto
# codes are accepted here; all other code-only NAR starts stay UNKNOWN.
NANKAN_CODES = {'18':'浦和','19':'船橋','20':'大井','21':'川崎'}
JRA_COLLECTORS = {'JRA','JRA_OFFICIAL','JRA_VAN','JRAVAN','JV_DATA'}
NAR_COLLECTORS = {'NAR','NAR_OFFICIAL','NANKAN_OFFICIAL'}


def norm(value: Any) -> str:
    return re.sub(r'\s+','',unicodedata.normalize('NFKC',str(value or ''))).upper()


def classify_start(start: dict) -> dict:
    """Resolve compatible explicit name/code witnesses; conflicts stay unknown."""
    witnesses=[]
    name=norm(start.get('venue') or start.get('racecourse') or start.get('venue_name'))
    clean=re.sub(r'競馬場$','',name)
    local_aliases={alias:place+'地方' for place in ('札幌','函館','新潟','中京')
                   for alias in (place+'(地方)',place+'地方','地方'+place,
                                 place+'競馬場(地方競馬)')}
    if clean in local_aliases:
        witnesses.append(('LOCAL',local_aliases[clean],'EXPLICIT_LOCAL_PLACE_NAME'))
    else:
        jra_name=re.sub(r'^(?:JRA|J)','',clean)
        if jra_name in JRA_NAMES:
            witnesses.append(('JRA',jra_name,'EXACT_JRA_PLACE_NAME'))
        elif clean in LOCAL_NAMES:
            witnesses.append(('LOCAL',clean,'EXACT_LOCAL_PLACE_NAME'))
    provider=norm(start.get('provider'))
    namespace=norm(start.get('venue_code_namespace') or start.get('place_code_namespace'))
    if not namespace and provider in JRA_COLLECTORS:namespace='JV_DATA'
    if not namespace and provider in NAR_COLLECTORS:namespace='NAR'
    code=start.get('venue_code',start.get('place_code',start.get('racecourse_code')))
    code_text=norm(code)
    if isinstance(code,int) and not isinstance(code,bool):code_text=f'{code:02d}'
    code_witness=False
    if namespace in {'JV_DATA','JRA_VAN','JRA'}:
        if code_text in JV_JRA:witnesses.append(('JRA',JV_JRA[code_text],'SCOPED_JV_PLACE_CODE'))
        elif code_text in JV_LOCAL:witnesses.append(('LOCAL',JV_LOCAL[code_text],'SCOPED_JV_PLACE_CODE'))
    elif namespace in {'NAR','NANKAN'} and code_text in NANKAN_CODES:
        witnesses.append(('LOCAL',NANKAN_CODES[code_text],'SCOPED_NAR_PLACE_CODE'))
    rid=str(start.get('provider_race_id') or '')
    if provider in JRA_COLLECTORS and re.fullmatch(r'\d{12}',rid) and rid[4:6] in JV_JRA:
        witnesses.append(('JRA',JV_JRA[rid[4:6]],'JRA_RACE_ID_PLACE_CODE'))
    elif provider in NAR_COLLECTORS and re.fullmatch(r'\d{16}',rid) and rid[8:10] in NANKAN_CODES:
        witnesses.append(('LOCAL',NANKAN_CODES[rid[8:10]],'NAR_RACE_ID_PLACE_CODE'))
    code_witness=any(w[2] in {'SCOPED_JV_PLACE_CODE','SCOPED_NAR_PLACE_CODE'} for w in witnesses)
    unresolved_code=bool(code_text and namespace and not code_witness)
    families={w[0] for w in witnesses};places={w[1] for w in witnesses}
    conflict=len(families)>1 or len(places)>1
    family='CONFLICT' if conflict else 'UNKNOWN' if unresolved_code else next(iter(families)) if families else 'UNKNOWN'
    return {'family':family,'canonical_venue':next(iter(places)) if len(places)==1 else None,
            'is_jra':True if family=='JRA' else False if family=='LOCAL' else None,
            'witnesses':[{'family':f,'venue':v,'basis':b} for f,v,b in witnesses],
            'collector_provider':start.get('provider'),'raw_venue':start.get('venue'),
            'raw_code':code,'code_namespace':namespace or None,
            'unresolved_scoped_code':unresolved_code,
            'provider_is_race_organiser_assumption':False}


def transfer_facts(starts: list[dict]) -> dict:
    """Recent observed race sequence cannot prove registration or transfer date."""
    identities=[classify_start(s) for s in starts]
    has_jra=any(x['family']=='JRA' for x in identities)
    unknown=any(x['family'] in {'UNKNOWN','CONFLICT'} for x in identities)
    latest=identities[0] if identities else None
    leading_local=0
    for item in identities:
        if item['family']=='LOCAL':leading_local+=1
        else:break
    return {
        'observed_jra_history':True if has_jra else None if unknown or not starts else False,
        'lifetime_jra_history':True if has_jra else None,
        'latest_start_identity':latest,
        'latest_observed_start_is_jra':latest['is_jra'] if latest else None,
        'observed_local_starts_since_most_recent_jra':leading_local if has_jra and not unknown else None,
        'actual_registration_transfer_date':None,
        'actual_registration_transfer_first_start':None,
        'actual_transfer_status':'UNKNOWN_REGISTRATION_EVIDENCE_NOT_PRESENT',
        'history_window_complete':False,
        'start_identities':identities,
        'nci_branch_meaning':'PREVIOUS_OBSERVED_START_FAMILY_NOT_CONFIRMED_REGISTRATION_TRANSFER',
    }

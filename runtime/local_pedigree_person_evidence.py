"""Read-only pedigree/person evidence audit. No BVI/JTI numeric consumption.

Current-field history is a selected sample, never a full venue population.
Official person totals describe opportunity plus performance, not rider skill.
"""
from __future__ import annotations
import base64
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
import re
import unicodedata
from urllib.parse import urlsplit, parse_qs
from runtime.local_physical.nar_source_manifest import LOCAL_BABA_CODES, VENUE_NAMES

LOCAL_VENUES = {'浦和','船橋','大井','川崎','門別','盛岡','水沢','金沢','笠松','名古屋','園田','姫路','高知','佐賀'}
SIGNER = 'KM-LOCAL-RUNTIME-ED25519-20260922'
TRUSTED_PUBLIC_KEY_B64 = 'jqWqOYlmhXXmpv/nR7lx3c2n/S5shDYava/WJVxn4kE='
VENUE_CODES = {VENUE_NAMES[k]:v for k,v in LOCAL_BABA_CODES.items()}

def sha(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def stamp(value):
    t=datetime.fromisoformat(str(value).replace('Z','+00:00'))
    if t.tzinfo is None:raise ValueError('EVIDENCE_AWARE_TIME_REQUIRED')
    return t.astimezone(timezone.utc)

def name(value):
    return ''.join(unicodedata.normalize('NFKC',str(value or '')).split())

def rider_name(value):
    # Affiliation removal only. Abbreviations and surnames are not expanded.
    return re.sub(r'\([^()]*\)$','',name(value))

def audit_reference_dataset(manifest, raw, as_of):
    if hashlib.sha256(raw).hexdigest()!=manifest['sha256']:raise ValueError('PEDIGREE_REFERENCE_SHA')
    cutoff=stamp(as_of)
    if stamp(manifest['available_at'])>cutoff:raise ValueError('PEDIGREE_REFERENCE_POST_CUTOFF')
    data=json.loads(raw);annual=data['annual'];supplement=data['supplement']
    if len(annual)!=manifest['annual_rows'] or len(supplement)!=manifest['supplement_rows']:raise ValueError('PEDIGREE_REFERENCE_ROW_COUNT')
    for row in annual+supplement:
        if row['終了日']>=cutoff.date().isoformat():raise ValueError('PEDIGREE_REFERENCE_PERIOD_NOT_PRESTART')
    required={'出走回数','勝利回数','二着回数','三着回数','競馬場','距離','馬場状態','産駒恒久ID','Raw_SHA','Source_Receipt'}
    missing=Counter(k for row in annual+supplement for k in required if row.get(k) is None)
    return {'dataset_id':manifest['dataset_id'],'sha256':manifest['sha256'],'available_at':manifest['available_at'],
            'annual_rows':len(annual),'supplement_rows':len(supplement),
            'source_urls':sorted({r['出典URL'] for r in annual+supplement}),
            'missing_required_statistic_rows':dict(sorted(missing.items())),
            'selection':'PRIZE_TOP50_AND_OVERLAPPING_PARTIAL_SUPPLEMENTS',
            'official_population_verified':False,'formal_bvi_eligible':False,
            'score_consumption':False,'existing_aei_research_not_reimplemented':True}

def selected_history_cohort(originals):
    records={};excluded=Counter();source_refs={}
    for original in originals:
        if original.get('sha256')!=sha({k:v for k,v in original.items() if k!='sha256'}):raise ValueError('FROZEN_ORIGINAL_HASH')
        if original.get('production_authority') is not False:raise ValueError('RESEARCH_ORIGINAL_REQUIRED')
        cutoff=stamp(original['race']['prediction_cutoff']);observed=stamp(original['source_fetched_at'])
        if observed>cutoff:raise ValueError('HISTORY_POST_CUTOFF_SOURCE')
        source_refs[original['source_sha256']]={'fetched_at':original['source_fetched_at'],'cutoff':original['race']['prediction_cutoff']}
        for horse in original['all_runners']:
            for run in horse['starts']:
                day=datetime.strptime(run['date'],'%y.%m.%d').date()
                if day>=cutoff.date():excluded['TARGET_OR_FUTURE_DATE']+=1;continue
                if run.get('venue') not in LOCAL_VENUES:excluded['NONLOCAL_OR_UNKNOWN_VENUE']+=1;continue
                rid=run.get('provider_race_id')
                if not isinstance(rid,str) or not re.fullmatch(r'\d{16}',rid):excluded['RACE_ID_UNKNOWN']+=1;continue
                if rid[:8]!=day.strftime('%Y%m%d') or rid[8:10]!=VENUE_CODES[run['venue']]:raise ValueError('HISTORY_RACE_DATE_VENUE_IDENTITY')
                finish=run.get('finish')
                if type(finish) is not int or finish<1:excluded['FINISH_UNKNOWN_NOT_ZERO']+=1;continue
                key=(horse['provider_horse_id'],rid)
                row={'horse_id':horse['provider_horse_id'],'horse_name':horse['name'],'race_id':rid,'date':day.isoformat(),
                     'venue':run['venue'],'distance':run.get('distance'),'going':run.get('going'),'surface':run.get('surface'),
                     'finish':finish,'sire':name(horse.get('sire')),'damsire':name(horse.get('damsire')),
                     'rider':rider_name(run.get('ride_jockey')),'popularity':run.get('ride_popularity'),
                     'source_refs':[original['source_sha256']]}
                if key in records:
                    prior=records[key]
                    if {k:v for k,v in prior.items() if k!='source_refs'}!={k:v for k,v in row.items() if k!='source_refs'}:raise ValueError('HISTORY_DUPLICATE_CONFLICT')
                    prior['source_refs']=sorted(set(prior['source_refs']+row['source_refs']))
                else:records[key]=row
    rows=list(records.values());groups=[]
    for field in ('sire','damsire','rider'):
        indexed=defaultdict(list)
        for r in rows:
            if r[field] and r['distance'] is not None and r['going'] and r['surface']:
                indexed[(r[field],r['venue'],r['distance'],r['going'],r['surface'])].append(r)
        for condition, members in sorted(indexed.items()):
            n=len(members);wins=sum(r['finish']==1 for r in members);top2=sum(r['finish']<=2 for r in members);top3=sum(r['finish']<=3 for r in members)
            groups.append({'group_field':field,'name':condition[0],'venue':condition[1],'distance':condition[2],'going':condition[3],'surface':condition[4],
                'unique_horses':len({r['horse_id'] for r in members}),'race_count':len({r['race_id'] for r in members}),'starts':n,
                'wins':wins,'top2':top2,'top3':top3,'win_rate':wins/n,'top2_rate':top2/n,'top3_rate':top3/n,
                'period_start':min(r['date'] for r in members),'period_end':max(r['date'] for r in members),
                'source_refs':sorted({s for r in members for s in r['source_refs']}),
                'comparison_population':'NONE_CURRENT_FIELD_SELECTED_HISTORY_ONLY','score_eligible':False,
                'small_sample_is_not_low_suitability':True})
    return {'records':rows,'groups':groups,'excluded':dict(excluded),'source_receipts':source_refs,
            'scope':'CURRENT_FIELD_SELECTED_HISTORY_NOT_FULL_POPULATION','formal_bvi_eligible':False,
            'jti_independent_skill_identified':False,'score_consumption':False}

def audit_signed_riders(envelope, public_key_b64, as_of, parse_person):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    r=envelope['receipt'];a=envelope['artifact'];cutoff=stamp(as_of)
    if public_key_b64!=TRUSTED_PUBLIC_KEY_B64:raise ValueError('PERSON_TRUSTED_AUTHORITY_REQUIRED')
    if (envelope.get('signature_alg')!='Ed25519' or envelope.get('signer_key_id')!=SIGNER
            or r.get('phase')!='SOURCE' or r.get('family')!='LOCAL' or r.get('status')!='SOURCE_FROZEN'
            or r.get('errors') or sha(r)!=envelope.get('receipt_sha256') or sha(a)!=r.get('artifact_sha256')):
        raise ValueError('PERSON_SIGNED_SOURCE_BINDING')
    Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key_b64,validate=True)).verify(
        base64.b64decode(envelope['signature'],validate=True),json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
    if stamp(r['timestamp'])>cutoff:raise ValueError('PERSON_RECEIPT_POST_CUTOFF')
    registry=a['nar_entity_registry'];profiles=[];seen=set()
    for s in a.get('sources',[]):
        if s.get('source_class')!='OFFICIAL_RIDER_PROFILE':continue
        if not s.get('raw_gzip_b64'):continue
        p=urlsplit(s['final_url']);query=parse_qs(p.query);ids=query.get('k_riderLicenseNo',[])
        if (p.scheme!='https' or p.netloc!='www.keiba.go.jp' or p.path!='/KeibaWeb/DataRoom/RiderMark'
                or p.fragment or set(query)!={'k_riderLicenseNo'} or len(ids)!=1):raise ValueError('PERSON_PROVIDER_LICENSE_URL')
        if ids[0] in seen:raise ValueError('PERSON_DUPLICATE_LICENSE_PROFILE')
        seen.add(ids[0])
        if s.get('official') is not True or s.get('authority')!='NAR_OFFICIAL' or s.get('http_status')!=200 or s.get('cutoff_relation')!='PRE_CUTOFF':raise ValueError('PERSON_SOURCE_NOT_ELIGIBLE')
        if stamp(s['fetched_at'])>cutoff or stamp(s['fetched_at'])>stamp(r['timestamp']):raise ValueError('PERSON_SOURCE_POST_CUTOFF_OR_RECEIPT')
        raw=gzip.decompress(base64.b64decode(s['raw_gzip_b64'],validate=True))
        if hashlib.sha256(raw).hexdigest()!=s['raw_sha256'] or sha({k:v for k,v in s.items() if k!='snapshot_sha256'})!=s['snapshot_sha256']:raise ValueError('PERSON_RAW_OR_SNAPSHOT_HASH')
        if ('/J0'+ids[0]+'.jpg').encode() not in raw:raise ValueError('PERSON_RAW_LICENSE_MARKER')
        matches=[x for x in registry if x.get('rider_license_no')==ids[0]]
        names={rider_name(x['rider_name']) for x in matches}
        if len(names)!=1:raise ValueError('PERSON_LICENSE_NAME_AMBIGUOUS')
        parsed=parse_person(s);expected=a['auxiliary_evidence']['profiles']['riders'][ids[0]]
        if parsed!=expected:raise ValueError('PERSON_RAW_REPARSE_DIFFERS')
        for row in parsed['performance_rows']:
            values=[row.get(k) for k in ('first','second','third','fourth','fifth','unplaced','total')]
            if any(type(v) is not int or v<0 for v in values) or sum(values[:-1])!=values[-1]:raise ValueError('PERSON_STATISTIC_COUNTS_INVALID')
        profiles.append({'license_no':ids[0],'name':next(iter(names)),'source_id':s['source_id'],'url':s['final_url'],
              'fetched_at':s['fetched_at'],'raw_sha256':s['raw_sha256'],'snapshot_sha256':s['snapshot_sha256'],
              'receipt_sha256':envelope['receipt_sha256'],'parsed':parsed,
              'published_at':None,'publication_time_basis':'NOT_PUBLISHED_IN_CAPTURED_PROFILE_METADATA',
              'age_seconds_at_asof':(cutoff-stamp(s['fetched_at'])).total_seconds(),
              'historical_profile_not_current_form':True,
              'same_venue_statistics_available':False,'distance_statistics_available':False,
              'riding_opportunity_adjusted_skill':'NOT_IDENTIFIED','score_consumption':False})
    return {'profiles':profiles,'crypto_verified':True,'receipt_sha256':envelope['receipt_sha256'],
            'available_at':r['timestamp'],'as_of':as_of,'formal_jti_consumption':False}

def current_rider_links(originals, rider_audit):
    by_name=defaultdict(list)
    for row in rider_audit['profiles']:by_name[row['name']].append(row)
    links=[]
    for original in originals:
        for horse in original['all_runners']:
            matches=by_name[rider_name(horse.get('current_jockey'))]
            declared_license=horse.get('nar_rider_license_no')
            matched=next((x for x in matches if x['license_no']==declared_license),None) if declared_license else None
            links.append({'race_id':original['race']['provider_race_id'],'runner_id':horse['runner_id'],
                'jockey':horse.get('current_jockey'),'candidate_official_license_ids':[x['license_no'] for x in matches],
                'connection':'LICENSE_VERIFIED' if matched else ('NAME_ONLY_NOT_CROSS_PROVIDER_VERIFIED' if len(matches)==1 else 'UNKNOWN_OR_AMBIGUOUS'),
                'strict_index_consumption':False,'reason':'CURRENT_CARD_NAR_LICENSE_CROSSWALK_REQUIRED; INDEPENDENT_PERSON_STATS_NOT_SAME_HORSE_HISTORY'})
    return links

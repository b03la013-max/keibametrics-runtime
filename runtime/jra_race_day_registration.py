"""Official JRA cohort/intake registration, separate from live dispatch and SOURCE."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re
from pathlib import Path
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'runtime/jra_source_runtime'))
from jra_race_day_resolver import build_intent, venue_code, VENUES, official_jump_race
from formal_request_validator import REQUIRED_INDEX_KEYS


def sha(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def automatic_row_hold(row):
    """Strict current-row eligibility only for the new automatic Plan lane."""
    if official_jump_race(row):
        return 'JUMP','SCOPE_HOLD','DEDICATED_OWNER_MANIFEST_ENGINE_SCOPE_NOT_ESTABLISHED'
    surface=re.sub(r'\s+','',unicodedata.normalize('NFKC',str(row.get('surface') or '')))
    if surface not in {'芝','ダ','ダート'}:
        return 'UNKNOWN','SCOPE_HOLD','OFFICIAL_RACE_TYPE_UNKNOWN'
    if (type(row.get('field_size')) is not int or not 1<=row['field_size']<=18 or
            not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d',str(row.get('post_time') or '')) or
            not isinstance(row.get('raw'),str) or not row['raw'].strip()):
        return 'FLAT','SOURCE_HOLD','OFFICIAL_RACE_HEADER_INCOMPLETE'
    return None


def build_registrations(discovery, authority, *, observed_at, universe_snapshot=None,
                        automatic_generation=None):
    if discovery.get('status') != 'DISCOVERED' or not discovery.get('venues'):
        raise ValueError('OFFICIAL_ALL_RACES_NOT_PROVEN')
    if datetime.fromisoformat(observed_at).tzinfo is None:
        raise ValueError('REGISTRATION_TIMEZONE_REQUIRED')
    jra=authority['family_scoped_authority']['JRA']
    owner=jra['production_static_owner_activation']
    if owner.get('status') not in {'OWNER_AUTHORIZED_UNVALIDATED','PRODUCTION_AUTHORIZED'}:
        raise ValueError('JRA_STATIC_OWNER_NOT_AUTHORIZED')
    day=discovery['race_date']; registrations={}; entries=[]; seen=set()
    management=[]; scope_exclusions=[]
    snapshots={v['venue_id']:v for v in (universe_snapshot or {}).get('venues',[])}
    for venue in discovery['venues']:
        rows=venue.get('races') or []
        numbers=[x['race_no'] for x in rows]
        if not rows or numbers!=list(range(1,len(rows)+1)):
            raise ValueError('OFFICIAL_RACE_SEQUENCE_NOT_PROVEN')
        vid=VENUES[venue_code(venue['venue'])][0]
        if automatic_generation is not None and not re.fullmatch(
                venue_code(venue['venue'])+day[:4]+r'\d{4}',str(venue.get('meeting_key') or '')):
            raise ValueError('OFFICIAL_MEETING_IDENTITY_NOT_PROVEN')
        if vid in seen:raise ValueError('OFFICIAL_VENUE_DUPLICATED')
        seen.add(vid); eligible_numbers=[]
        for row in rows:
            rid=f"KM-JRA-{vid}-{day.replace('-','')}-R{row['race_no']:02d}"
            management.append(rid)
            hold=automatic_row_hold(row) if automatic_generation is not None else (
                ('JUMP','SCOPE_HOLD','DEDICATED_OWNER_MANIFEST_ENGINE_SCOPE_NOT_ESTABLISHED')
                if official_jump_race(row) else None)
            if hold:
                kind,status,reason=hold
                held={'race_id':rid,'race_type':kind,
                      'status':'SOURCE_HOLD' if status=='SOURCE_HOLD' else 'HOLD',
                      'action':'EXCLUDE_FROM_FLAT_DISPATCH_ONLY',
                      'reason':reason,
                      'source':'OFFICIAL_DAY_ROW_DISCIPLINE',
                      'historical_signed_artifacts_changed':False,
                      'venue':venue['venue'],'race_no':row['race_no'],
                      'title':row.get('title'),'official_day_row':row.get('raw')}
                if re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d',str(row.get('post_time') or '')):
                    held['post']=datetime.fromisoformat(day+'T'+row['post_time']+':00+09:00').isoformat()
                scope_exclusions.append(held)
                continue
            if type(row.get('field_size')) is not int or not 1<=row['field_size']<=18:
                raise ValueError('OFFICIAL_FIELD_SIZE_NOT_PROVEN')
            intent=build_intent(race_date=day,venue=vid,race_no=row['race_no'],
                                meeting_key=venue['meeting_key'],race=row)
            intent['current_authority_manifest']=authority['manifest_id']
            eligible_numbers.append(row['race_no'])
            universe=next((r for r in snapshots.get(vid,{}).get('races',[])
                           if r['race_no']==row['race_no']),None)
            registrations[intent['race_id']]={
                'profile':'KM-JRA-PREREGISTERED-INTAKE-v1','family_id':'JRA',
                'race_id':intent['race_id'],'execution_id':intent['execution_id'],
                'registered_at':observed_at,'current_authority_manifest':authority['manifest_id'],
                'source_discovery_sha256':sha(discovery),'source_meeting_key':venue['meeting_key'],
                'intake_intent':intent,'required_index_manifest':list(REQUIRED_INDEX_KEYS),
                'planned_required_cells':20*row['field_size'],'executed_cells':0,
                'authorized_static_owner':deepcopy(owner),
                'official_runner_snapshot':deepcopy(universe),
                'runner_universe_status':(universe or {}).get('status','PENDING_OFFICIAL_PDF'),
                'active_runner_authority':'FRESH_SIGNED_RACE_DAY_SOURCE_REQUIRED',
                'planned_dispatch_window':{
                    'open':(datetime.fromisoformat(intent['scheduled_post_at'])-timedelta(minutes=55)).isoformat(),
                    'close':(datetime.fromisoformat(intent['scheduled_post_at'])-timedelta(minutes=30)).isoformat()},
                'formal_status':'REGISTERED_INTAKE_ONLY','source_executed':False,
                'static_frozen':False,'dispatch_acknowledged':False,'user_delivery_verified':False,
            }
        if eligible_numbers:entries.append({'venue':venue['venue'],'races':eligible_numbers})
    plan={'race_date':day,'family_id':'JRA','entries':entries,'run_count':5000,
          'dispatch_window_minutes_before_post':[55,30],
          'cohort':{'source_discovery_sha256':sha(discovery),'registered_at':observed_at,
                    'race_ids':sorted(registrations),'race_count':len(registrations),
                    'current_authority_manifest':authority['manifest_id']}}
    if scope_exclusions or automatic_generation is not None:
        plan['management_race_ids']=sorted(management)
        plan['scope_exclusions']=scope_exclusions
    if automatic_generation is not None:
        plan['automatic_generation']=deepcopy(automatic_generation)
    plan['cohort']['sha256']=sha(plan['cohort'])
    plan['plan_sha256']=sha(plan)
    for record in registrations.values():
        record['cohort_sha256']=plan['cohort']['sha256']
        record['plan_sha256']=plan['plan_sha256'];record['sha256']=sha(record)
    return plan,registrations


def verify_registration(record, plan, *, race_id, official_post):
    if record.get('sha256')!=sha({k:v for k,v in record.items() if k!='sha256'}):
        raise ValueError('JRA_REGISTRATION_HASH_MISMATCH')
    cohort=plan['cohort']
    if plan.get('plan_sha256')!=sha({k:v for k,v in plan.items() if k!='plan_sha256'}):
        raise ValueError('JRA_DAY_PLAN_HASH_MISMATCH')
    if cohort.get('sha256')!=sha({k:v for k,v in cohort.items() if k!='sha256'}):
        raise ValueError('JRA_COHORT_HASH_MISMATCH')
    intent=record['intake_intent']
    if (record.get('family_id')!='JRA' or record.get('race_id')!=race_id
            or intent.get('race_id')!=race_id or intent.get('race_date')!=plan['race_date']
            or race_id not in cohort['race_ids'] or record.get('cohort_sha256')!=cohort['sha256']
            or record.get('plan_sha256')!=plan['plan_sha256']
            or record.get('current_authority_manifest')!=cohort['current_authority_manifest']):
        raise ValueError('JRA_REGISTRATION_COHORT_BINDING_MISMATCH')
    if official_post.tzinfo is None or official_post.date().isoformat()!=plan['race_date']:
        raise ValueError('JRA_OFFICIAL_POST_DATE_OR_TIMEZONE_MISMATCH')
    return {'registered_post':intent['scheduled_post_at'],
            'observed_official_post':official_post.isoformat(),
            'post_changed':datetime.fromisoformat(intent['scheduled_post_at'])!=official_post,
            'source':'FRESH_JRA_OFFICIAL_DAY_ROW','cohort_identity_unchanged':True}


def persist_registrations(root,plan,records):
    """Immutable per-race intake. Never writes the live intent push-trigger root."""
    root=Path(root);paths=[]
    for rid,record in records.items():
        path=root/'runtime/jra_race_registrations'/plan['race_date']/(rid+'.json')
        if path.exists() and json.loads(path.read_text())!=record:
            raise ValueError('JRA_REGISTRATION_ALREADY_EXISTS_DIFFERENT:'+rid)
        paths.append((path,record))
    plan_path=root/'runtime/jra_race_day_plan'/(plan['race_date']+'.json')
    if plan_path.exists() and json.loads(plan_path.read_text())!=plan:
        raise ValueError('JRA_DAY_PLAN_ALREADY_EXISTS_DIFFERENT')
    for path,value in paths+[(plan_path,plan)]:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    return len(records)

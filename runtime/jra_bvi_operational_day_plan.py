"""Future-only official priority census with an explicit, narrower dispatch scope.

The fixed ENV code accepts its existing ``all_races`` management census.  That
is not a prediction cohort or authority to dispatch an obstacle race.  This
adapter reuses the existing intake builder's official identity checks, discards
its in-memory registrations, and records the eligible entries separately.
Existing plans and the five published ENV source files are never rewritten.
"""
from copy import deepcopy
from datetime import datetime, timedelta
import json
from pathlib import Path
import re
import unicodedata

from jra_race_day_registration import build_registrations, sha

PROFILE = 'KM-JRA-OFFICIAL-PRIORITY-CENSUS-v1'
DISPATCH_SCOPE = 'EXPLICIT_ELIGIBLE_ENTRIES_ONLY'
JUMP = re.compile(r'障害|グランド[JＪ]|大障害|(?:ハイ|スプリング|サマー|オータム|ウインター)ジャンプ|[JＪ][･・. ]?[GＧ][ⅠⅡⅢ123１２３]')


def row_hold(row):
    text = unicodedata.normalize('NFKC', ' '.join(str(row.get(k) or '') for k in ('title','raw','surface')))
    surface = re.sub(r'\s+', '', unicodedata.normalize('NFKC', str(row.get('surface') or '')))
    if JUMP.search(text) or surface in {'芝ダ','芝→ダート','芝→ダ','障害'}:
        return {'race_type':'JUMP','status':'SCOPE_HOLD',
                'reason':'DEDICATED_JUMP_OWNER_MANIFEST_ENGINE_SCOPE_NOT_ESTABLISHED'}
    if surface not in {'芝','ダ','ダート'}:
        return {'race_type':'UNKNOWN','status':'SCOPE_HOLD','reason':'OFFICIAL_RACE_TYPE_UNKNOWN'}
    return None


def _official_census(discovery):
    from jra_race_day_resolver import VENUES, venue_code, parse_day_rows
    day=discovery.get('race_date'); datetime.strptime(day,'%Y-%m-%d')
    venues=discovery.get('venues')
    if (discovery.get('status')!='DISCOVERED' or not isinstance(venues,list)
            or not 1<=len(venues)<=3):
        raise ValueError('BVI_PRIORITY_OFFICIAL_MEETING_UNIVERSE_INVALID')
    entries=[]; held=[]; facts={}; seen=set()
    for venue in venues:
        code=venue_code(venue['venue']); vid=VENUES[code][0]; rows=venue.get('races')
        if (vid in seen or venue.get('venue_id')!=vid or not isinstance(rows,list)
                or len(rows)!=12 or any(type(r.get('race_no')) is not int for r in rows)
                or [r.get('race_no') for r in rows]!=list(range(1,13))
                or not re.fullmatch(code+day[:4]+r'\d{4}',str(venue.get('meeting_key') or ''))):
            raise ValueError('BVI_PRIORITY_COMPLETE_OFFICIAL_MEETING_REQUIRED')
        seen.add(vid)
        eligible=[]
        for row in rows:
            if (not isinstance(row.get('raw'),str) or not row['raw'].strip()
                    or not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d',str(row.get('post_time') or ''))
                    or type(row.get('field_size')) is not int or not 1<=row['field_size']<=18):
                raise ValueError('BVI_PRIORITY_OFFICIAL_HEADER_REQUIRED')
            parsed=parse_day_rows([row['raw']])
            if (len(parsed)!=1 or any(parsed[0].get(k)!=row.get(k) for k in
                    ('post_time','surface','distance_m','field_size','title'))):
                raise ValueError('BVI_PRIORITY_OFFICIAL_HEADER_FIELDS_MISMATCH')
            rid=f"KM-JRA-{vid}-{day.replace('-','')}-R{row['race_no']:02d}"
            post=datetime.fromisoformat(day+'T'+row['post_time']+':00+09:00')
            facts[rid]={'post':post.isoformat(),'race_no':row['race_no'],'venue':venue['venue'],
                        'title':row.get('title'),'official_day_row':row['raw'],
                        'dispatch_window_open':(post-timedelta(minutes=55)).isoformat(),
                        'dispatch_window_close':(post-timedelta(minutes=30)).isoformat()}
            decision=row_hold(row)
            if decision:
                held.append({'race_id':rid,**decision,'action':'EXCLUDE_FROM_FLAT_DISPATCH_ONLY'})
            else: eligible.append(row['race_no'])
        entries.append({'venue':venue['venue'],'races':eligible})
    if len(facts) not in (12,24,36):raise ValueError('BVI_PRIORITY_CENSUS_SIZE_UNSUPPORTED')
    return facts,entries,held


def build_plan(discovery, authority, *, observed_at):
    observed = datetime.fromisoformat(observed_at)
    if (observed.tzinfo is None or observed.utcoffset()!=timedelta(hours=9)
            or observed.date().isoformat()!=discovery.get('race_date')):
        raise ValueError('BVI_PRIORITY_PLAN_OBSERVATION_DATE_OR_TIMEZONE')
    effective=datetime.fromisoformat(authority['effective_at'])
    if effective.tzinfo is None or effective>observed:
        raise ValueError('BVI_PRIORITY_PLAN_AUTHORITY_NOT_EFFECTIVE')
    # Reuse existing official date, venue, sequence, field and intent checks.
    # These objects are not persisted as registrations or prediction authority.
    base, _ = build_registrations(discovery, authority, observed_at=observed_at)
    facts,entries,held=_official_census(discovery)
    plan={k:deepcopy(base[k]) for k in ('race_date','family_id','run_count','dispatch_window_minutes_before_post')}
    plan.update(profile=PROFILE, all_races=True, dispatch_scope=DISPATCH_SCOPE,
        current_authority_manifest=authority['manifest_id'],observed_at=observed_at,
        entries=entries,management_race_ids=sorted(facts),scope_exclusions=held,
        official_discovery=deepcopy(discovery),official_discovery_sha256=sha(discovery),
        official_schedule_facts=facts,
        forward_oos_preregistration={'profile':PROFILE,'purpose':'OPERATIONAL_PRIORITY_CENSUS_ONLY',
            'not_prediction_cohort_registration':True,'target_race_count':len(facts),
            'targets':[{'race_id':rid,'oos_eligible':False} for rid in sorted(facts)]},
        production_policy_change='NONE',source_or_prediction_created=False,
        intake_registrations_created=0,forward_oos_increment=0)
    plan['plan_sha256']=sha(plan)
    return plan


def validate_plan(plan):
    if (plan.get('profile') != PROFILE or plan.get('dispatch_scope') != DISPATCH_SCOPE
            or plan.get('all_races') is not True or plan.get('cohort')
            or plan.get('plan_sha256') != sha({k:v for k,v in plan.items() if k!='plan_sha256'})):
        raise ValueError('BVI_PRIORITY_PLAN_MARKER_OR_HASH_INVALID')
    discovery=plan.get('official_discovery') or {}
    observed=datetime.fromisoformat(plan.get('observed_at') or '')
    if (plan.get('family_id')!='JRA' or discovery.get('race_date')!=plan.get('race_date')
            or discovery.get('status')!='DISCOVERED'
            or observed.tzinfo is None or observed.utcoffset()!=timedelta(hours=9)
            or observed.date().isoformat()!=plan.get('race_date')
            or not isinstance(plan.get('current_authority_manifest'),str)
            or not plan['current_authority_manifest']
            or plan.get('run_count')!=5000
            or plan.get('dispatch_window_minutes_before_post')!=[55,30]
            or plan.get('production_policy_change')!='NONE'
            or plan.get('source_or_prediction_created') is not False
            or plan.get('intake_registrations_created')!=0 or plan.get('forward_oos_increment')!=0
            or plan.get('official_discovery_sha256')!=sha(discovery)):
        raise ValueError('BVI_PRIORITY_DISCOVERY_BINDING_INVALID')
    facts=plan.get('official_schedule_facts') or {}
    expected,entries,held=_official_census(discovery)
    ids=sorted(expected); reg=plan.get('forward_oos_preregistration') or {}
    if (len(ids) not in (12,24,36) or facts!=expected or plan.get('management_race_ids')!=ids
            or plan.get('entries')!=entries or plan.get('scope_exclusions')!=held
            or reg!={'profile':PROFILE,'purpose':'OPERATIONAL_PRIORITY_CENSUS_ONLY',
                'not_prediction_cohort_registration':True,'target_race_count':len(ids),
                'targets':[{'race_id':rid,'oos_eligible':False} for rid in ids]}):
        raise ValueError('BVI_PRIORITY_CENSUS_OR_DISPATCH_BINDING_INVALID')
    return True


def refresh_census_schedule(plan, schedule, days, *, resolve):
    """Refresh all official facts, including held rows, without expanding dispatch."""
    validate_plan(plan)
    discovery=deepcopy(plan['official_discovery'])
    for venue in discovery['venues']:
        name=venue['venue']
        if name not in days:
            try:days[name]=resolve(plan['race_date'],name)
            except Exception as exc:days[name]=exc
        value=days[name]
        if isinstance(value,Exception):raise value
        venue['meeting_key'],venue['races']=value
    facts,_,fresh_holds=_official_census(discovery)
    if set(facts)!=set(plan['official_schedule_facts']):
        raise ValueError('BVI_PRIORITY_CURRENT_CENSUS_IDENTITY_CHANGED')
    held={r['race_id']:r for r in plan['scope_exclusions']}
    held.update({r['race_id']:r for r in fresh_holds})
    for rid,row in facts.items():
        schedule[rid]={**row}
        if rid in held:schedule[rid]['scope_decision']=deepcopy(held[rid])
    return schedule


def persist_future_plan(root, plan):
    validate_plan(plan); path=Path(root)/'runtime/jra_race_day_plan'/(plan['race_date']+'.json')
    path.parent.mkdir(parents=True,exist_ok=True)
    # Exclusive create: a previously saved Owner plan is never normalized in place.
    with path.open('x',encoding='utf-8') as output:
        output.write(json.dumps(plan,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    return path


def ensure_future_plan(root, race_date, *, default_all, cache, meetings, resolve, observed_clock):
    root=Path(root); path=root/'runtime/jra_race_day_plan'/(race_date+'.json')
    if path.exists() or not default_all:return True
    days=cache.setdefault('days',{})
    try:
        if 'meetings' not in cache:
            try:cache['meetings']=meetings(race_date)
            except Exception as exc:cache['meetings']=exc
        venues=cache['meetings']
        if isinstance(venues,Exception):raise venues
        if not isinstance(venues,(list,tuple)) or len(set(venues))!=len(venues):
            raise ValueError('BVI_PRIORITY_OFFICIAL_MEETING_UNIVERSE_INVALID')
        if not venues:return True
        discovery={'status':'DISCOVERED','race_date':race_date,'venues':[]}
        for venue in venues:
            if venue not in days:
                try:days[venue]=resolve(race_date,venue)
                except Exception as exc:days[venue]=exc
            value=days[venue]
            if isinstance(value,Exception):raise value
            key,rows=value
            from jra_race_day_resolver import VENUES, venue_code
            discovery['venues'].append({'venue':venue,'venue_id':VENUES[venue_code(venue)][0],
                                       'meeting_key':key,'races':rows})
        from family_authority_guard import resolve_current_authority
        observed=observed_clock(); _,authority=resolve_current_authority(root,now=observed)
        plan=build_plan(discovery,authority,observed_at=observed.isoformat())
        persist_future_plan(root,plan)
        return True
    except FileExistsError:
        # A concurrent Owner plan wins. Existing byte content is retained;
        # ordinary tick/verifiers resolve that plan, never our in-memory proposal.
        return True
    except Exception as exc:
        failure={'profile':PROFILE,'race_date':race_date,'status':'BLOCKED',
            'first_failed_operation':'OFFICIAL_PRIORITY_PLAN_BOOTSTRAP',
            'reason':type(exc).__name__+':'+str(exc),'observed_at':observed_clock().isoformat(),
            'source_or_prediction_created':False,'forward_oos_increment':0}
        output=root/'runtime_out/jra_bvi_day_plan_failure.json';output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(failure,ensure_ascii=False,indent=2)+'\n')
        return False

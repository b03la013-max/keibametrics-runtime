"""Evaluate Book facts with existing JRA bands without claiming provider approval.

The resulting observations are diagnostic-only and cannot be passed as signed
SOURCE or Production evidence. Preserve every observation's capture provenance.
"""
from datetime import date
import math
import re
try:
    from .jra_evidence_feature_normalizer_production import percentile_band, comment_band, workout_final_1f_band
except ImportError:
    from jra_evidence_feature_normalizer_production import percentile_band, comment_band, workout_final_1f_band


def evaluate(intake):
    if intake.get('official_universe_matched') is not True:
        raise ValueError('BOOK_OFFICIAL_UNIVERSE_REQUIRED')
    if intake.get('provider') != 'KEIBABOOK_SMART_PREMIUM':
        raise ValueError('BOOK_PROVIDER_REQUIRED')
    facts = intake['facts']
    universe = {r['runner_id']: r['name'] for r in facts['ability']}
    for kind in ('workout', 'stable'):
        rows = facts[kind]
        if len(rows) != len(universe) or {r['runner_id']:r['name'] for r in rows} != universe:
            raise ValueError('BOOK_FACT_UNIVERSE_MISMATCH')
    sources = {s['kind']:s for s in intake['sources']}
    if set(sources) != {'ability','workout','stable'}:
        raise ValueError('BOOK_CAPTURE_PROVENANCE_REQUIRED')
    race_day = date.fromisoformat(intake['race_date'])
    observations = {rid:{} for rid in universe}
    blocked = []
    def emit(rid, feature, category, rule, kind, facts_used):
        observations[rid][feature] = {
            'category':category, 'rule_id':rule, 'source_authority':'KEIBABOOK_SMART_PREMIUM',
            'production_authority':False, 'temporal_mode':intake['temporal_mode'],
            'evidence_refs':[sources[kind]['raw_sha256']],
            'captured_at':sources[kind]['captured_at'], 'facts_used':facts_used,
        }
    means = {}
    for r in facts['ability']:
        runs = sorted(r['prior_runs'],key=lambda x:x['date'],reverse=True)[:4]
        values=[]
        for run in runs:
            if date.fromisoformat(run['date']) >= race_day:
                raise ValueError('BOOK_TARGET_OR_FUTURE_RESULT_FORBIDDEN')
            value = run.get('speed_index')
            if type(value) in (float,int) and math.isfinite(value) and 1 <= value <= 150:
                values.append(value)
        if len(values)>=2:
            means[r['runner_id']]=sum(values)/len(values)
    for rid, mean in means.items():
        if len(means)<4:break
        percentile=(sum(x<mean for x in means.values())+(sum(x==mean for x in means.values())-1)/2)/(len(means)-1)
        emit(rid,'recent_speed',percentile_band(percentile),'JRA-EVIDENCE-PERCENTILE-RECENT-SPEED-v1','ability',{'mean':mean,'peer_count':len(means),'percentile':percentile})
    for r in facts['workout']:
        rid=r['runner_id']
        if r.get('assessment'):
            emit(rid,'workout_capability',comment_band(r['assessment']),'JRA-WORKOUT-CAPABILITY-COMMENT-v1','workout',{'assessment':r['assessment']})
        selected=[]
        for row in r['observed_workouts']:
            if row.get('previous_workout'):continue
            dm=re.search(r'(\d{1,2})[／/](\d{1,2})',row.get('date_course',''))
            if not dm:continue
            try:day=date(race_day.year,int(dm[1]),int(dm[2]))
            except ValueError:continue
            # Yearless New Year rows are ambiguous; no prior-year inference.
            if day>=race_day or (race_day-day).days>60:continue
            raw_course=row['date_course']
            course='CW' if 'ＣＷ' in raw_course or 'CW' in raw_course else '坂' if '坂' in raw_course else None
            value=row.get('final1f')
            if course and type(value) in (float,int) and math.isfinite(value) and 8<=value<=20:
                selected.append((day,course,value))
        if selected:
            day,course,value=max(selected,key=lambda x:x[0])
            emit(rid,'workout_speed',workout_final_1f_band(value,course),'JRA-WORKOUT-FINAL1F-BAND-v1','workout',{'date':day.isoformat(),'course':course,'final1f':value})
    for r in facts['stable']:
        comment=r.get('trainer_comment','')
        if comment:
            emit(r['runner_id'],'stable_readiness',comment_band(comment),'JRA-STABLE-COMMENT-BAND-v1','stable',{'trainer_comment':comment})
    for rid,row in observations.items():
        for name in ('recent_speed','workout_capability','workout_speed','stable_readiness'):
            if name not in row:blocked.append({'runner_id':rid,'feature':name,'reason':'INSUFFICIENT_COMPARABLE_OBSERVATIONS'})
    return {'profile':'JRA-KEIBABOOK-REGISTERED-BAND-CONFORMANCE-v1','runner_count':len(universe),
            'observations':observations,'blocked':blocked,'production_authority':False,
            'signed_source':False,'signed_final_issued':False,'oos_increment':0,
            'remaining_gates':['REGISTERED_PROVIDER_CONFORMANCE_APPROVAL','AUTHENTIC_PRE_CUTOFF_SIGNED_SOURCE','FULL20_FEATURE_CLOSURE','STATIC_OWNER_FORWARD_OOS_AND_INDEPENDENT_RECEIPT']}

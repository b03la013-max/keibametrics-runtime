"""Temporal intake for a prospective SHADOW comparison, never a score updater.

Original historical states lacking an effective time are explicitly ineligible.
Candidate findings can be read as review context; they cannot authorize policy.
"""
from copy import deepcopy
from collections import Counter
from datetime import datetime
import hashlib
import json


def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,
        separators=(',',':'),allow_nan=False).encode()).hexdigest()


def instant(value):
    when=datetime.fromisoformat(value.replace('Z','+00:00'))
    if when.tzinfo is None:raise ValueError('LEARNING_TIMEZONE_REQUIRED')
    return when


def build_shadow_learning_intake(states, *, race_id, source_freeze, cutoff, observed_at):
    freeze,limit,observed=map(instant,[source_freeze,cutoff,observed_at])
    if freeze>limit or observed>limit:
        raise ValueError('LEARNING_INTAKE_AFTER_CUTOFF')
    # The snapshot is fixed before SOURCE. Later events wait for the next race.
    boundary=min(freeze,observed)
    accepted=[];excluded=[]
    counts=Counter(s.get('state_id') for s in states)
    for original in states:
        state=deepcopy(original);sid=state.get('state_id');reason=None
        if not sid or counts[sid]>1:reason='MISSING_OR_DUPLICATE_STATE_ID'
        elif state.get('sha256')!=digest({k:v for k,v in state.items() if k!='sha256'}):reason='STATE_HASH_MISMATCH'
        elif state.get('race_id')==race_id:reason='TARGET_RACE_LEARNING_FORBIDDEN'
        elif not str(state.get('race_id','')).startswith('KM-JRA-'):reason='FAMILY_SCOPE_MISMATCH'
        elif not state.get('effective_time'):reason='EFFECTIVE_TIME_UNVERIFIED'
        else:
            try:
                effective=instant(state['effective_time'])
                if effective>=boundary:reason='NOT_AVAILABLE_BEFORE_SOURCE_FREEZE'
                elif state.get('learning_validity') not in ('FAMILY-CANDIDATE','VENUE-PERSISTENT-CANDIDATE'):
                    reason='VALIDITY_NOT_ADMITTED_FOR_FORWARD_SHADOW'
                elif state.get('learning_validity')=='VENUE-PERSISTENT-CANDIDATE' and state['race_id'].split('-')[2]!=race_id.split('-')[2]:
                    reason='VENUE_SCOPE_MISMATCH'
            except (ValueError,TypeError,IndexError):reason='INVALID_EFFECTIVE_TIME_OR_SCOPE'
        if reason:excluded.append({'state_id':sid,'reason':reason})
        else:accepted.append({'state_id':sid,'race_id':state['race_id'],'state_sha256':state['sha256'],
            'effective_time':state['effective_time'],'use':'SHADOW_REVIEW_CONTEXT_ONLY',
            'numeric_or_policy_application':False})
    record={'race_id':race_id,'source_freeze':source_freeze,'cutoff':cutoff,'observed_at':observed_at,
        'accepted':accepted,'excluded':excluded,'status':'SHADOW_INTAKE_RECORDED',
        'production_effect':'NONE','prediction_application':'NOT APPLIED',
        'same_day_facts_reused':False,'historical_artifacts_modified':False}
    record['sha256']=digest(record)
    return record

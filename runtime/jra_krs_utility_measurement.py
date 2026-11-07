"""Explicit JRA measurement correction; preserve preregistered Common code bytes.

Used by the day audit. Production caller activation and a corrected measurement
cohort require Owner review; this module never edits a frozen Utility or FINAL.
"""
from copy import deepcopy
from krs_prediction_utility import (
    build_krs_prediction_utility as _build,
    evaluate_against_result as _evaluate,
    _request_static_roles,
)
from hashlib import sha256
import json

REVISION='KM-JRA-KRS-ROLE-MEASUREMENT-CORRECTION-20261017'

def build_krs_prediction_utility(request, response):
    report=_build(request,response)
    if request.get('family_id')!='JRA':
        return report
    roles=_request_static_roles(request)
    for row in report['summary']:
        row['static_roles']=sorted(roles.get(int(row['horse_no']),set()))
    report['measurement_revision']=REVISION
    report['role_rank_metrics']={'W':'SSR-W','P2':'SSR-P2','P3':'SSR-T3'}
    report['corrected_measurement_forward_cohort']='PENDING_OWNER_PREREGISTRATION; NEVER RETROACTIVELY POOLED'
    report['sha256']=sha256(json.dumps({k:v for k,v in report.items() if k!='sha256'},ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return report

def evaluate_against_result(utility, actual_top3, *, static_ranking=None, static_roles=None, p3_rank_metric='SSR-T3'):
    corrected=deepcopy(utility)
    for row in corrected.get('summary',[]):
        if static_roles is not None:
            horse=row['horse_no']
            row['static_roles']=list(static_roles.get(str(horse),static_roles.get(horse,[])) or [])
        if p3_rank_metric!='SSR-P3':
            row.setdefault('ranks',{})['SSR-P3']=row.get('ranks',{}).get(p3_rank_metric)
    return _evaluate(corrected,actual_top3,static_ranking=static_ranking)

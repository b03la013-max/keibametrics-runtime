"""JRA binding repair around the shared, preregistered cross-family evaluator.

The shared file is frozen by LOCAL's forward protocol. Preserve its exact bytes
and behaviour; resolve JRA's actual frozen Roles and proposal metric here.
"""
from copy import deepcopy
import hashlib,json
from krs_prediction_utility import (build_krs_prediction_utility as _build,
    evaluate_against_result as _evaluate, _request_static_roles)


def build_krs_prediction_utility(request,response):
    out=_build(request,response)
    if request.get('family_id')!='JRA':return out
    roles=_request_static_roles(request)
    for row in out['summary']:
        row['static_roles']=sorted(roles.get(int(row['horse_no']),set()))
    out['role_rank_metrics']={'W':'SSR-W','P2':'SSR-P2','P3':'SSR-T3'}
    out['measurement_binding_revision']='JRA-ROLE-BINDING-20261018-R1'
    out['sha256']=hashlib.sha256(json.dumps({k:v for k,v in out.items() if k!='sha256'},
        ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return out


def evaluate_against_result(utility,actual_top3,*,static_ranking=None,static_roles=None):
    if len(actual_top3)!=3 or len(set(map(int,actual_top3)))!=3:
        raise ValueError('ACTUAL_TOP3_INVALID')
    if not str(utility.get('race_id','')).startswith('KM-JRA-'):
        return _evaluate(utility,actual_top3,static_ranking=static_ranking)
    measured=deepcopy(utility)
    for row in measured.get('summary') or []:
        if static_roles is not None:
            row['static_roles']=sorted(static_roles.get(str(row['horse_no']),[]) or [])
        ranks=row.get('ranks') or {}
        # The legacy shared evaluator reads SSR-P3. JRA's frozen proposal
        # producer uses SSR-T3, so adapt only the copied diagnostic view.
        ranks['SSR-P3']=ranks.get('SSR-T3')
    out=_evaluate(measured,actual_top3,static_ranking=static_ranking)
    out['role_rank_metrics']={'W':'SSR-W','P2':'SSR-P2','P3':'SSR-T3'}
    out['measurement_binding_revision']='JRA-ROLE-BINDING-20261018-R1'
    return out

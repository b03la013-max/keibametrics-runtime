"""Fixed-width incremental KRS role review, NON-PRODUCTION.

Never adds a Pair/Third, changes an AKI column, or constructs a bet.
Absent observed KRS output is not an invitation to simulate a proposal.
"""
from copy import deepcopy
from jra_learning_intake import digest

METRICS={'W':'SSR-W','P2':'SSR-P2','P3':'SSR-T3'}

def build_role_rescue_shadow(final):
    static=final['static_prediction'];ranking=list(map(str,static['ranking']))
    roles={str(h):list(v) for h,v in static.get('roles',{}).items()}
    utility=final.get('krs_prediction_utility')
    if not isinstance(utility,dict) or not final.get('krs_run_receipt'):
        raise ValueError('ACTUAL_KRS_EVIDENCE_REQUIRED')
    proposals=utility.get('actionable_role_proposals')
    if not isinstance(proposals,list):raise ValueError('PERSISTED_KRS_PROPOSALS_REQUIRED')
    selected=[]
    for role,metric in METRICS.items():
        eligible=[]
        for p in proposals:
            horse=str(p.get('horse_no'));rank=p.get('krs_rank')
            if p.get('proposal')!=f'ADD_{role}_SHADOW' or p.get('actionable') is not True:continue
            if horse not in ranking:raise ValueError('KRS_RUNNER_UNIVERSE_MISMATCH')
            if role in roles.get(horse,[]):continue
            if p.get('basis')!=metric or not isinstance(rank,int) or isinstance(rank,bool) or rank<1:
                raise ValueError('KRS_PROPOSAL_RANK_CONTRACT_MISMATCH')
            eligible.append(p)
        if eligible:
            selected.append(deepcopy(min(eligible,key=lambda p:(p['krs_rank'],int(p['horse_no'])))))
    out={'candidate_id':'JRA-KRS-UNIQUE-ROLE-REVIEW-ONE-PER-COLUMN-v1',
        'race_id':final['race_id'],'baseline_final_sha256':final['sha256'],
        'krs_receipt_sha256':final['krs_run_receipt']['receipt_sha256'],
        'role_rank_metrics':dict(METRICS),'max_additions_per_column':1,
        'selected_proposals':selected,'production_effect':'NONE','actual_added_capital':0,
        'ticket_conversion':'NOT ACTIVATED; distinct Pair/Third feasibility review remains mandatory',
        'warning':'Rank/frequency is not a calibrated probability or EV.'}
    out['sha256']=digest(out)
    return out

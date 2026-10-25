"""Outcome-blind research portfolios and post-result evaluation.

No function in the portfolio construction path accepts a result or payout.  The
default comparison preserves the original bet-type counts and stake multisets.
This module has no Production purchase, policy, or promotion authority.
"""
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import itertools
import json
import math
import statistics

BET_LENGTH = {'EXACTA': 2, 'TRIO': 3, 'TRIFECTA': 3}
POLICY = {
    'candidate_id': 'JRA-CAPITAL-COMPARISON-20261024-R1',
    'classification': 'POST_RESULT_EXPLORATION_NOT_FORWARD_OOS',
    'default_exposure': 'same frozen bet-type counts and original per-type stake sequence',
    'tie_break': 'descending result-blind priority then numeric selection',
    'insufficient_pool': 'original frozen ticket fallback',
    'portfolio_construction_accepts_result': False,
    'calibrated_probability_or_ev_used': False,
    'purchase_authority': False,
    'production_effect': 'NONE',
    'automatic_promotion': False,
    'minimum_forward_distinct_races': 60,
    'minimum_forward_days': 3,
    'minimum_forward_venues': 2,
}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def key(ticket):
    kind = str(ticket['bet_type']).upper()
    selection = tuple(map(int, ticket['selection']))
    return kind, tuple(sorted(selection)) if kind == 'TRIO' else selection


def validate_tickets(tickets, universe):
    seen = set()
    for ticket in tickets:
        kind, selection = key(ticket)
        if (kind not in BET_LENGTH or len(selection) != BET_LENGTH[kind]
                or len(set(selection)) != len(selection)
                or not set(map(str, selection)) <= set(universe)):
            raise ValueError('RESEARCH_TICKET_UNIVERSE_OR_TYPE')
        if (kind, selection) in seen:
            raise ValueError('RESEARCH_DUPLICATE_TICKET')
        seen.add((kind, selection))
        if 'stake' in ticket and (type(ticket['stake']) is not int
                or ticket['stake'] <= 0 or ticket['stake'] % 100):
            raise ValueError('RESEARCH_STAKE_INVALID')


def _binding(final, request, metadata=None):
    if final.get('sha256') != digest({k:v for k,v in final.items() if k != 'sha256'}):
        raise ValueError('RESEARCH_FINAL_HASH')
    if final['race_id'] != request['race_id']:
        raise ValueError('RESEARCH_RACE_BINDING')
    if (final['source_snapshot_sha256'] != request['source_snapshot_sha256']
            or final['prediction_cutoff'] != request['prediction_cutoff']):
        raise ValueError('RESEARCH_SOURCE_CUTOFF_BINDING')
    universe = {str(r['runner_id']) for r in request['runners']}
    if universe != set(map(str, final['static_prediction']['ranking'])):
        raise ValueError('RESEARCH_RUNNER_BINDING')
    metadata = metadata or {}
    for field, expected in [('source_sha256', request['source_snapshot_sha256']),
                            ('runner_universe_sha256', digest(sorted(universe))),
                            ('prediction_cutoff', request['prediction_cutoff']),
                            ('feature_input_sha256', digest(request['runners']))]:
        if metadata.get(field) not in (None, expected):
            raise ValueError('RESEARCH_CANDIDATE_' + field.upper())
    return universe


def ranked_tickets(rankings, *, head_local_p2=None, pair_conditioned_third=None):
    """Enumerate the same ex-ante head/pair universe without reading labels."""
    rr = {r:list(map(str, rankings[r])) for r in ('W','P2','P3')}
    universe = set(rr['W'])
    if any(len(v) != len(universe) or set(v) != universe for v in rr.values()):
        raise ValueError('RESEARCH_RANK_UNIVERSE')
    candidates = {}
    for wr, head in enumerate(rr['W'], 1):
        p2 = (head_local_p2 or {}).get(head) or [s for s in rr['P2'] if s != head]
        if set(map(str,p2)) != universe-{head}:
            raise ValueError('RESEARCH_HEAD_CONDITIONING')
        for sr, second in enumerate(map(str,p2), 1):
            candidates[('EXACTA',(int(head),int(second)))] = -(wr+sr)
            thirds = (pair_conditioned_third or {}).get(head+'>'+second) or [t for t in rr['P3'] if t not in (head,second)]
            if set(map(str,thirds)) != universe-{head,second}:
                raise ValueError('RESEARCH_PAIR_CONDITIONING')
            for tr, third in enumerate(map(str,thirds), 1):
                selection = (int(head),int(second),int(third)); score = -(wr+sr+tr)
                candidates[('TRIFECTA',selection)] = score
                trio = ('TRIO',tuple(sorted(selection)))
                candidates[trio] = max(score,candidates.get(trio,-math.inf))
    return [{'bet_type':kind,'selection':list(sel),'priority_score':score}
            for (kind,sel),score in candidates.items()]


def matched_exposure(final, request, candidates, *, candidate_id, metadata=None,
                     diversity=False, bet_type_mix=False):
    """Preserve budget/count; default also preserves exact per-type exposure."""
    universe = _binding(final, request, metadata)
    original = final['final_ticket']['tickets']
    validate_tickets(original, universe)
    if sum(t['stake'] for t in original) != final['final_ticket']['total_investment']:
        raise ValueError('RESEARCH_FROZEN_CAPITAL')
    # Paper/NO-BET cannot obtain a positive research budget through this path.
    allowed = {key(t)[0] for t in original}
    scores = {}
    for ticket in candidates:
        validate_tickets([ticket], universe)
        k = key(ticket)
        score = ticket.get('priority_score',0)
        if type(score) not in (float,int) or not math.isfinite(score):
            raise ValueError('RESEARCH_PRIORITY_INVALID')
        if k[0] in allowed:
            scores[k] = max(score,scores.get(k,-math.inf))
    for ticket in original:
        scores.setdefault(key(ticket),-1e30)
    grouped = {kind:[k for k in scores if k[0] == kind] for kind in allowed}
    for kind, pool in grouped.items():
        pool.sort(key=lambda k:(-scores[k],k[1]))
        if diversity:
            # A fixed round-robin across pre-existing heads/pairs; no winner input.
            queues=defaultdict(list)
            for k in pool:queues[k[1][:2] if kind == 'TRIFECTA' else k[1][:1]].append(k)
            order=sorted(queues,key=lambda q:(-max(scores[k] for k in queues[q]),q))
            pool=[]
            while any(queues.values()):
                for q in order:
                    if queues[q]:pool.append(queues[q].pop(0))
            grouped[kind]=pool
    selected=[]
    if bet_type_mix:
        order=sorted(allowed)
        while len(selected)<len(original) and any(grouped.values()):
            for kind in order:
                if grouped[kind] and len(selected)<len(original):selected.append(grouped[kind].pop(0))
        stakes=[t['stake'] for t in original]
        tickets=[{'bet_type':k[0],'selection':list(k[1]),'stake':stake} for k,stake in zip(selected,stakes)]
    else:
        tickets=[]
        for kind in sorted(allowed):
            source=[t for t in original if key(t)[0] == kind]
            chosen=grouped[kind][:len(source)]
            tickets.extend({'bet_type':k[0],'selection':list(k[1]),'stake':t['stake']} for k,t in zip(chosen,source))
    validate_tickets(tickets, universe)
    same_type = Counter(key(t)[0] for t in tickets) == Counter(key(t)[0] for t in original)
    same_stakes = {k:sorted(t['stake'] for t in tickets if key(t)[0]==k) for k in allowed} == {k:sorted(t['stake'] for t in original if key(t)[0]==k) for k in allowed}
    if (len(tickets)!=len(original) or sum(t['stake'] for t in tickets)!=sum(t['stake'] for t in original)
            or (not bet_type_mix and not (same_type and same_stakes))):
        raise ValueError('RESEARCH_EXPOSURE_NOT_MATCHED')
    out={'candidate_id':candidate_id,'race_id':final['race_id'],'tickets':tickets,
         'ticket_count':len(tickets),'investment':sum(t['stake'] for t in tickets),
         'same_budget':True,'same_total_point_count':True,'same_bet_type_counts':same_type,
         'same_bet_type_stake_multisets':same_stakes,'permitted_bet_types_unchanged':True,
         'original_final_sha256':final['sha256'],'source_sha256':request['source_snapshot_sha256'],
         'runner_universe_sha256':digest(sorted(universe)),'prediction_cutoff':request['prediction_cutoff'],
         'feature_input_sha256':digest(request['runners']),
         'original_final_freeze_timestamp':final.get('final_freeze_timestamp'),
         'candidate_metadata':deepcopy(metadata or {}),
         'policy_sha256':digest({**POLICY,'diversity':diversity,'bet_type_mix':bet_type_mix}),
         'classification':'POST_RESULT_EXPLORATION_NOT_FORWARD_OOS','purchase_authority':False,
         'production_effect':'NONE'}
    out['sha256']=digest(out)
    return out


def concentration(tickets):
    total=sum(t['stake'] for t in tickets)
    heads=Counter();pairs=Counter();kinds=Counter()
    for ticket in tickets:
        kind,sel=key(ticket);kinds[kind]+=ticket['stake']
        if kind != 'TRIO':heads[str(sel[0])]+=ticket['stake'];pairs['>'.join(map(str,sel[:2]))]+=ticket['stake']
    ordered=sum(heads.values())
    return {'investment':total,'by_bet_type':dict(kinds),'ordered_investment':ordered,
            'by_ordered_head':dict(heads),'by_ordered_pair':dict(pairs),
            'max_head_share_of_ordered':max(heads.values(),default=0)/ordered if ordered else None,
            'max_pair_share_of_ordered':max(pairs.values(),default=0)/ordered if ordered else None,
            'largest_bet_type_share':max(kinds.values(),default=0)/total if total else None}


def settle(tickets, official, *, settlement_fn):
    return settlement_fn({'final_ticket':{'tickets':deepcopy(tickets),
        'total_investment':sum(t['stake'] for t in tickets)}},deepcopy(official))


def evaluate_portfolio(final, portfolio, official, *, settlement_fn):
    original=final['final_ticket']['tickets'];tickets=portfolio['tickets']
    baseline=settle(original,official,settlement_fn=settlement_fn)
    candidate=settle(tickets,official,settlement_fn=settlement_fn)
    old={key(t):t['stake'] for t in original};new={key(t):t['stake'] for t in tickets}
    added=[{**t,'stake':t['stake']-old.get(key(t),0)} for t in tickets if t['stake']>old.get(key(t),0)]
    removed=[{**t,'stake':t['stake']-new.get(key(t),0)} for t in original if t['stake']>new.get(key(t),0)]
    add=settle(added,official,settlement_fn=settlement_fn);sub=settle(removed,official,settlement_fn=settlement_fn)
    old_return=baseline['total_payout'];new_return=candidate['total_payout']
    winning_added_stake=sum(t['stake'] for t in add['winning_tickets'])
    return {'baseline':baseline,'candidate':candidate,
            'redeployed_stake':sum(t['stake'] for t in added),
            'added_return':add['total_payout'],'removed_return':sub['total_payout'],
            'false_positive_redeployed_stake':sum(t['stake'] for t in added)-winning_added_stake-add.get('refund',0),
            'unique_ticket_rescue':old_return==0 and new_return>0,
            'unique_ticket_harm':old_return>0 and new_return==0,
            'net_return_delta':new_return-old_return,
            'baseline_profitable':baseline['profit_loss']>0,
            'candidate_profitable':candidate['profit_loss']>0,
            'baseline_hit_but_loss':old_return>0 and baseline['profit_loss']<0,
            'candidate_hit_but_loss':new_return>0 and candidate['profit_loss']<0,
            'added_tickets':added,'removed_tickets':removed}


def cash_metrics(rows):
    """Explicit zero-exposure/null PFS, refund-aware drawdown, robust tail checks."""
    rows=sorted(rows,key=lambda r:(r['post_at'],r['race_id']))
    invested=[r for r in rows if r['investment']>0]
    effective=sum(r.get('effective_investment',r['investment']) for r in invested)
    inv=sum(r['investment'] for r in invested);ret=sum(r['return'] for r in invested)
    refund=sum(r.get('refund',0) for r in invested)
    equity=peak=drawdown=0;longest=streak=0
    for row in invested:
        net=row['return']+row.get('refund',0)-row['investment']
        equity+=net;peak=max(peak,equity);drawdown=max(drawdown,peak-equity)
        streak=streak+1 if row['return']==0 and row.get('effective_investment',row['investment'])>0 else 0
        longest=max(longest,streak)
    winners=sorted(invested,key=lambda r:(-r['return'],r['race_id']))
    excluded={}
    for count in [1,2,3]:
        rest=winners[count:];den=sum(r.get('effective_investment',r['investment']) for r in rest)
        excluded[str(count)]={'removed_races':[r['race_id'] for r in winners[:count]],
            'pfs':100*sum(r['return'] for r in rest)/den if den else None}
    pfs_values=[100*r['return']/r.get('effective_investment',r['investment']) for r in invested if r.get('effective_investment',r['investment'])>0]
    return {'race_count':len(rows),'invested_races':len(invested),'zero_exposure_races':len(rows)-len(invested),
            'investment':inv,'refund':refund,'effective_investment':effective,'return':ret,
            'profit_loss':ret+refund-inv,'pfs':100*ret/effective if effective else None,
            'gross_investment_return_ratio':100*ret/inv if inv else None,
            'median_race_pfs':statistics.median(pfs_values) if pfs_values else None,
            'profitable_races':sum(r['return']+r.get('refund',0)>r['investment'] for r in invested),
            'hit_but_loss_races':sum(0<r['return']<r.get('effective_investment',r['investment']) for r in invested),
            'all_losing_races':sum(r['return']==0 and r.get('effective_investment',r['investment'])>0 for r in invested),
            'all_losing_rate':sum(r['return']==0 and r.get('effective_investment',r['investment'])>0 for r in invested)/len(invested) if invested else None,
            'zero_exposure_rate':(len(rows)-len(invested))/len(rows) if rows else None,
            'largest_return_share':max((r['return'] for r in invested),default=0)/ret if ret else None,
            'maximum_drawdown':drawdown,'longest_zero_return_streak':longest,
            'rolling_window_status':{f'R{n}':{'status':'PENDING_INSUFFICIENT_INVESTED_RACES' if len(invested)<n else 'AVAILABLE_POST_RESULT_ONLY',
                'observed_invested_races':len(invested),'required_races':n} for n in (30,100)},
            'capital_turnover':'UNKNOWN_INITIAL_BANKROLL_NOT_SUPPLIED',
            'largest_returns_excluded':excluded,'actual_purchase':'UNVERIFIED',
            'pfs_authority':'FROZEN_OR_RESEARCH_RECOMMENDATION_VIRTUAL_ONLY'}

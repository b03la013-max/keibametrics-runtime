"""Pre-cutoff, result-blind JRA role/learning sidecar; no Production authority.

Designed after 2026-10-18. That day is exploration/regression, never forward OOS.
Existing KRS proposals are hypotheses, not probabilities or purchase orders.
"""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
import io
import zipfile
import subprocess
import re
from pathlib import Path

CANDIDATE_ID = 'JRA-ROLE-LEARNING-20261018-R1'
OOS_SCOPE = 'CONDITIONAL_RANK_EQUAL_EXPOSURE_ONLY'
EVIDENCE_GROUPS = {
 'course': {'same_course_fit','same_course_distance_quality','course_geometry_fit','similar_geometry_fit','distance_fit','same_distance_fit'},
 'class_form': {'class_performance','recent_form','recent_consistency','opponent_strength','hidden_class'},
 'closing': {'closing_quality','closing_speed','pace_fit','pace_suitability'},
 'bloodline': {'pedigree_surface','pedigree_distance','pedigree_class','sire_track_signal','maternal_class_signal'}}
POLICY = {'candidate_id': CANDIDATE_ID,
          'positive_categories': ['POSITIVE', 'STRONG', 'VERY_STRONG', 'EXCEPTIONAL'],
          'minimum_distinct_observed_features': 2,
          'minimum_distinct_evidence_groups': 2, 'evidence_groups': {k:sorted(v) for k,v in EVIDENCE_GROUPS.items()},
          'arms': ['PRODUCTION', 'WINNER_REAUDIT', 'HEAD_LOCAL_P2', 'PAIR_THIRD',
                   'KRS_ACTIONABLE', 'LEARNING_ON', 'CORE_PROTECTION'],
          'training_end': '2026-10-18', 'automatic_promotion': False,
          'minimum_distinct_races': 60, 'minimum_days': 3, 'minimum_venues': 2}

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def instant(value):
    t = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if t.tzinfo is None:
        raise ValueError('SHADOW_TIMEZONE_REQUIRED')
    return t

def intake(states, *, race_id, source_freeze, cutoff, observed_at):
    boundary = min(instant(source_freeze), instant(observed_at))
    if boundary > instant(cutoff) or instant(observed_at) > instant(cutoff):
        raise ValueError('LEARNING_AFTER_CUTOFF')
    counts = Counter(s.get('state_id') for s in states if isinstance(s, dict))
    accepted, excluded = [], []
    for s in states:
        reason = None
        sid = s.get('state_id') if isinstance(s, dict) else None
        if not sid or counts[sid] != 1: reason = 'MISSING_OR_DUPLICATE_ID'
        elif s.get('sha256') != digest({k:v for k,v in s.items() if k != 'sha256'}): reason = 'HASH_MISMATCH'
        elif not str(s.get('race_id', '')).startswith('KM-JRA-'): reason = 'FAMILY_SCOPE'
        elif s['race_id'] == race_id: reason = 'SAME_RACE_LEAKAGE'
        elif not s.get('effective_time'): reason = 'EFFECTIVE_TIME_UNVERIFIED'
        elif s.get('learning_validity') not in {'FAMILY-CANDIDATE', 'VENUE-PERSISTENT-CANDIDATE'}: reason = 'POLICY_NOT_ADMITTED'
        else:
            try:
                if instant(s['effective_time']) >= boundary: reason = 'NOT_AVAILABLE_BEFORE_SOURCE'
                elif s['learning_validity'] == 'VENUE-PERSISTENT-CANDIDATE' and s['race_id'].split('-')[2] != race_id.split('-')[2]: reason = 'VENUE_SCOPE'
            except (ValueError, TypeError, IndexError): reason = 'INVALID_TIME_OR_SCOPE'
        if reason:
            excluded.append({'state_id': sid, 'reason': reason})
        else:
            accepted.append({'state_id': sid, 'state_sha256': s['sha256'], 'source_race_id': s['race_id'],
                             'effective_time': s['effective_time'], 'reference_metrics': deepcopy(s.get('reference_metrics') or {})})
    return {'accepted': accepted, 'excluded': excluded, 'boundary': boundary.isoformat(),
            'scope': 'SHADOW_ONLY', 'production_effect': 'NONE'}

def ticket_key(t):
    kind = t['bet_type'].upper()
    sel = tuple(map(int, t['selection']))
    return kind, tuple(sorted(sel)) if kind == 'TRIO' else sel

def support(row):
    # Only recorded, observed features qualify. DCR-only numeric neutral is not evidence.
    features = row.get('evidence_features') or {}
    return sorted(k for k,v in features.items() if isinstance(v, dict)
                  and v.get('category') in POLICY['positive_categories'] and v.get('evidence_refs')
                  and not v.get('result_derived') and v.get('production_authority') is not False)

def build_shadow(request, final, *, states=(), observed_at=None, historical=False):
    observed_at = observed_at or datetime.now(timezone.utc).isoformat()
    cutoff = request['prediction_cutoff']; source = request['source_snapshot']
    source_freeze = source['source_freeze_at']
    when = instant(observed_at)
    if not historical and when > instant(cutoff): raise ValueError('SHADOW_FREEZE_AFTER_CUTOFF')
    if instant(source_freeze) > instant(cutoff): raise ValueError('SOURCE_AFTER_CUTOFF')
    if request['race_id'] != final['race_id'] or not request['race_id'].startswith('KM-JRA-'):
        raise ValueError('SHADOW_RACE_IDENTITY')
    if final.get('sha256') != digest({k:v for k,v in final.items() if k!='sha256'}):
        raise ValueError('SHADOW_FINAL_HASH_INVALID')
    if final.get('source_snapshot_sha256') != request['source_snapshot_sha256'] or final.get('prediction_cutoff') != cutoff:
        raise ValueError('SHADOW_FINAL_SOURCE_OR_CUTOFF_MISMATCH')
    if set(map(str,final['static_prediction']['ranking'])) != {str(r['runner_id']) for r in request['runners']}:
        raise ValueError('SHADOW_RUNNER_UNIVERSE_MISMATCH')
    # static_freeze_timestamp is the legacy cutoff barrier. The actual
    # computation clock is static_computed_at; do not pretend they are equal.
    if not historical and not (instant(source_freeze) <= instant(request['static_computed_at'])
            <= instant(final['final_freeze_timestamp']) <= when <= instant(cutoff)):
        raise ValueError('SHADOW_COMPUTATION_CHRONOLOGY_INVALID')
    if source.get('source_snapshot_sha256') not in (None, request['source_snapshot_sha256']):
        raise ValueError('SHADOW_SOURCE_BINDING')
    utility = final.get('krs_prediction_utility') or {}
    if not final.get('krs_run_receipt') or utility.get('race_id') != final['race_id']:
        raise ValueError('OBSERVED_KRS_REQUIRED')
    runners = {str(r['runner_id']): r for r in request['runners']}
    roles = deepcopy(final['static_prediction']['roles'])
    base = deepcopy(final['final_ticket']['tickets'])
    baseline = {ticket_key(t) for t in base}
    active_pairs = {(str(p['head']), str(p['second'])) for p in request.get('pair_dispositions', [])
                    if p.get('status') in {'PURCHASE', 'PROTECT'}}
    links = intake(list(states), race_id=request['race_id'], source_freeze=source_freeze,
                   cutoff=cutoff, observed_at=observed_at) if not historical else {'accepted': [], 'excluded': [], 'scope': 'NO_HISTORICAL_LEARNING_RECONSTRUCTION'}
    learn_w = any(s['reference_metrics'].get('first_material_failure') == 'PREDICTION_ROLE_W' for s in links['accepted'])
    proposals = utility.get('role_proposals') or []
    evidence = {rid: support(r) for rid,r in runners.items()}
    eligible = {rid for rid, feats in evidence.items() if len(feats) >= POLICY['minimum_distinct_observed_features']
                and sum(bool(set(feats)&group) for group in EVIDENCE_GROUPS.values()) >= POLICY['minimum_distinct_evidence_groups']}
    winner = {str(p['horse_no']) for p in proposals if p['proposal'] == 'ADD_W_SHADOW'
              and str(p['horse_no']) in eligible and {'P2','P3'} & set(roles.get(str(p['horse_no']), []))}
    # Pair/third proposals must be observed in the frozen KRS output, not synthesized from results.
    pair_proposals = list({(p['head'],p['second']):p for p in
        (utility.get('ordered_pair_proposals') or []) + (utility.get('actionable_ordered_pair_proposals') or [])}.values())
    third_proposals = list({(p['head'],p['second'],p['third']):p for p in
        (utility.get('pair_third_proposals') or []) + (utility.get('actionable_pair_third_proposals') or [])}.values())
    actionable_pairs = {(str(p['head']),str(p['second'])) for p in utility.get('actionable_ordered_pair_proposals') or []}
    actionable_thirds = {(str(p['head']),str(p['second']),str(p['third'])) for p in utility.get('actionable_pair_third_proposals') or []}
    arms = {}
    for name in POLICY['arms']:
        tickets = deepcopy(base)
        if name == 'CORE_PROTECTION':
            if any(t.get('mec_tier') or t.get('tier') for t in base):
                tickets = [t for t in tickets if str(t.get('mec_tier') or t.get('tier')).upper() in {'CORE','PROTECTION'}]
        pairs = set(active_pairs)
        selected = []
        def add(kind, selection, reason):
            selection = list(map(int, selection))
            if len(set(selection)) != len(selection) or any(str(h) not in runners for h in selection):
                raise ValueError('SHADOW_PROPOSAL_UNIVERSE')
            t = {'bet_type': kind, 'selection': selection, 'stake': 100, 'shadow_reason': reason}
            if ticket_key(t) not in {ticket_key(x) for x in tickets}:
                tickets.append(t); selected.append(t)
        if name in {'WINNER_REAUDIT','HEAD_LOCAL_P2','KRS_ACTIONABLE','LEARNING_ON'}:
            for p in pair_proposals:
                h,s = str(p['head']),str(p['second'])
                permitted = ((name == 'WINNER_REAUDIT' or (name == 'LEARNING_ON' and learn_w)) and h in winner and s in eligible)
                permitted |= name == 'HEAD_LOCAL_P2' and 'W' in roles.get(h, []) and 'P3' in roles.get(s, []) and s in eligible
                permitted |= name == 'KRS_ACTIONABLE' and (h,s) in actionable_pairs
                if permitted: pairs.add((h,s)); add('EXACTA',[h,s],name)
        if name in {'WINNER_REAUDIT','HEAD_LOCAL_P2','PAIR_THIRD','KRS_ACTIONABLE','LEARNING_ON'}:
            for p in third_proposals:
                h,s,t = str(p['head']),str(p['second']),str(p['third'])
                if (h,s) not in pairs: continue
                permitted = t in eligible if name != 'KRS_ACTIONABLE' else (h,s,t) in actionable_thirds
                if name == 'LEARNING_ON' and not learn_w: permitted = False
                if permitted:
                    add('TRIFECTA',[h,s,t],name); add('TRIO',[h,s,t],name)
        keys = {ticket_key(t) for t in tickets}
        arms[name] = {'tickets': tickets, 'ticket_count': len(tickets),
                      'required_capital': sum(t['stake'] for t in tickets),
                      'added_ticket_count': len(keys-baseline), 'removed_ticket_count': len(baseline-keys),
                      'added_capital': sum(t['stake'] for t in tickets if ticket_key(t) not in baseline),
                      'selection_evidence': selected}
    normalized_source = digest(source)
    out = {'candidate_id': CANDIDATE_ID, 'race_id': request['race_id'], 'production_effect': 'NONE',
           'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'policy_fingerprint': digest(POLICY),
           'authority_manifest': request['current_authority_manifest'], 'source_sha256': request['source_snapshot_sha256'],
           'source_payload_sha256': normalized_source, 'runner_universe_sha256': digest(sorted(runners)),
           'prediction_cutoff': cutoff, 'observed_at': observed_at, 'baseline_final_sha256': final['sha256'],
           'krs_receipt_sha256': final['krs_run_receipt']['receipt_sha256'], 'learning_intake': links,
           'signature_trust': 'INHERITS_CALLER_VERIFIED_FINAL_AND_KRS; MODULE_DOES_NOT_VERIFY_SIGNATURES',
           'learning_state_bindings': links['accepted'], 'learning_applied_to_arm': 'LEARNING_ON' if learn_w else None,
           'positive_feature_ids': evidence, 'arms': arms, 'result_input_allowed': False,
           'venue_context': deepcopy(source.get('jra_race_context') or {}),
           'venue_mechanism_status': 'OBSERVED_FEATURE_REAUDIT_ONLY; missing downhill/rail/position measurements not synthesized',
           'model_market_disagreement': market_disagreement(request, final),
           'oos_eligible': False,
           'temporally_eligible': not historical and when.astimezone(timezone.utc).date().isoformat() > POLICY['training_end'],
           'eligibility_status': 'PENDING_INDEPENDENT_PRE_RESULT_PERSISTENCE_WITNESS',
           'classification': 'EXPLORATION_REGRESSION_NOT_OOS' if historical else 'PRE_CUTOFF_SHADOW',
           'freeze_trust': 'CALLER_MUST_PERSIST_PRE_RESULT_AND_VERIFY_GIT_OR_ARTIFACT_WITNESS',
           'promotion': 'HOLD', 'metrics_are_calibrated_probabilities': False}
    out['sha256'] = digest(out)
    return out

def market_disagreement(request, final):
    obs=request['source_snapshot'].get('jra_official_market_observation') or {}
    rank={str(h):i+1 for i,h in enumerate(final['static_prediction']['ranking'])}
    rows=[{'runner_id':str(r['runner_id']),'static_rank':rank.get(str(r['runner_id'])),
           'market_rank':r.get('popularity_rank'),
           'rank_gap':rank.get(str(r['runner_id']))-r['popularity_rank'] if rank.get(str(r['runner_id'])) is not None and isinstance(r.get('popularity_rank'),int) else None}
          for r in obs.get('runners') or []]
    return {'captured_at':obs.get('captured_at'),'rows':rows,'use':'AUDIT_ONLY_NOT_MARKET_SELECTION',
            'calibrated_probability':False,'automatic_axis_change':False}

def persist_shadow(root, request, final, *, observed_at=None):
    root = Path(root); path = root/'runtime/role_rescue_shadow'/(''+final['race_id']+'.json')
    if path.exists():
        old = json.loads(path.read_text())
        if old.get('sha256') != digest({k:v for k,v in old.items() if k!='sha256'}) or old.get('baseline_final_sha256') != final['sha256']:
            raise ValueError('IMMUTABLE_SHADOW_CONFLICT')
        return old
    states = [json.loads(p.read_text()) for p in sorted((root/'runtime/learning_states').glob('*.json'))]
    out = build_shadow(request, final, states=states, observed_at=observed_at)
    model_path=root/'research/jra_conditional_rank/model.json'
    if model_path.exists():
        try:
            from jra_conditional_rank_shadow import compare, exposure_portfolio
            out['conditional_rank_comparison']=compare(request,json.loads(model_path.read_text()))
            out['conditional_rank_portfolio']=exposure_portfolio(out['conditional_rank_comparison'],final)
            out['additional_code_sha256']={'runtime/jra_conditional_rank_shadow.py':out['conditional_rank_comparison']['code_sha256']}
            out['additional_input_sha256']={'research/jra_conditional_rank/model.json':out['conditional_rank_comparison']['model_sha256']}
        except (ValueError,KeyError,TypeError) as exc:
            out['conditional_rank_comparison']={'status':'HOLD','reason':type(exc).__name__+':'+str(exc),'production_effect':'NONE'}
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        out['actions_freeze_context'] = {k: os.environ.get(v) for k,v in {
            'repository':'GITHUB_REPOSITORY','run_id':'GITHUB_RUN_ID',
            'run_attempt':'GITHUB_RUN_ATTEMPT','head_sha':'GITHUB_SHA'}.items()}
        out['sha256'] = digest({k:v for k,v in out.items() if k!='sha256'})
    out['sha256']=digest({k:v for k,v in out.items() if k!='sha256'})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=2)+'\n')
    return out

def settle_shadow(shadow, result):
    """Settle every frozen arm, with independent pre-result persistence still required."""
    from jra_production_postresult import settle_final
    if shadow.get('sha256') != digest({k:v for k,v in shadow.items() if k!='sha256'}):
        raise ValueError('SHADOW_HASH_INVALID')
    if result['race_id'] != shadow['race_id']:
        raise ValueError('SHADOW_RESULT_IDENTITY')
    if result.get('frozen_prediction_ref',{}).get('immutable_final_sha256') != shadow['baseline_final_sha256']:
        raise ValueError('SHADOW_RESULT_FINAL_BINDING')
    official=result['official_result']
    if instant(official['captured_at']) <= instant(shadow['observed_at']):
        raise ValueError('SHADOW_RESULT_NOT_AFTER_FREEZE')
    baseline=shadow['arms']['PRODUCTION'];budget=baseline['required_capital'];n=baseline['ticket_count']
    arms={}
    for name,arm in shadow['arms'].items():
        f={'final_ticket':{'tickets':arm['tickets'],'total_investment':arm['required_capital']}}
        settled=settle_final(f,official)
        prefix=arm['tickets'][:n]
        p=settle_final({'final_ticket':{'tickets':prefix,'total_investment':sum(t['stake'] for t in prefix)}},official)
        baseline_keys={ticket_key(t) for t in baseline['tickets']}
        extra=[t for t in arm['tickets'] if ticket_key(t) not in baseline_keys]
        extra_settled=settle_final({'final_ticket':{'tickets':extra,'total_investment':sum(t['stake'] for t in extra)}},official)
        added_winning_stake=sum(t['stake'] for t in extra_settled['winning_tickets'])
        arms[name]={**settled,'added_capital':arm['added_capital'],
            'added_winning_stake':added_winning_stake,
            'false_positive_cost':sum(t['stake'] for t in extra)-added_winning_stake,
            'added_ticket_return':extra_settled['total_payout'],
            'actual_ticket_count':len(arm['tickets']),'equal_ticket_actual_count':len(prefix),
            'equal_ticket_target_count':n,'equal_ticket_count_matched':len(prefix)==n,
            'equal_budget_fractional_return':settled['total_payout']*budget/arm['required_capital'] if arm['required_capital'] else None,
            'equal_ticket_frozen_prefix_return':p['total_payout'],
            'comparison_note':'Fractional equal-budget and fixed prefix are diagnostics, not real stake instructions.'}
    out={'candidate_id':shadow['candidate_id'],'race_id':shadow['race_id'],
         'shadow_sha256':shadow['sha256'],'source_sha256':shadow['source_sha256'],
         'code_sha256':shadow['code_sha256'],'policy_fingerprint':shadow['policy_fingerprint'],
         'official_raw_sha256':official['raw_sha256'],'arms':arms,
         'oos_eligible':False,'eligibility_status':'PENDING_INDEPENDENT_PRE_RESULT_PERSISTENCE_WITNESS',
         'production_effect':'NONE','automatic_promotion':False}
    rank=shadow.get('conditional_rank_comparison') or {}
    if rank.get('role_rankings'):
        if rank.get('sha256')!=digest({k:v for k,v in rank.items() if k!='sha256'}):raise ValueError('RANK_NESTED_HASH_INVALID')
        actual=list(map(str,official['top3']))
        if rank.get('model_policy_sha256'):
            from jra_conditional_rank_shadow import evaluate_comparison
            out['conditional_rank_evaluation']=evaluate_comparison(rank,actual)
        else:
            out['conditional_rank_evaluation']={'candidate_id':rank['candidate_id'],'status':'LEGACY_RANK_ONLY_NO_POLICY_BINDING'}
    portfolio=shadow.get('conditional_rank_portfolio') or {}
    if portfolio:
        from jra_conditional_rank_shadow import _validate_rank_universe
        universe=_validate_rank_universe(rank)
        if any(str(h) not in universe for t in portfolio['tickets'] for h in t['selection']):raise ValueError('EXPOSURE_TICKET_UNIVERSE')
        if portfolio.get('sha256')!=digest({k:v for k,v in portfolio.items() if k!='sha256'}):raise ValueError('EXPOSURE_PORTFOLIO_HASH')
        from collections import Counter
        if (portfolio.get('baseline_final_sha256')!=shadow['baseline_final_sha256']
            or portfolio.get('rank_comparison_sha256')!=rank.get('sha256')
            or portfolio.get('model_sha256')!=rank.get('model_sha256')
            or portfolio.get('required_capital')!=budget or portfolio.get('ticket_count')!=n
            or len(portfolio['tickets'])!=n
            or Counter((t['bet_type'],t['stake']) for t in portfolio['tickets'])!=Counter((t['bet_type'],t['stake']) for t in baseline['tickets'])):
            raise ValueError('EXPOSURE_BASELINE_OR_BUDGET_MISMATCH')
        pf={'final_ticket':{'tickets':portfolio['tickets'],'total_investment':portfolio['required_capital']}}
        ps=settle_final(pf,official);base_return=arms['PRODUCTION']['total_payout']
        base_keys={ticket_key(t) for t in baseline['tickets']};new_keys={ticket_key(t) for t in portfolio['tickets']}
        old_stake={ticket_key(t):t['stake'] for t in baseline['tickets']};new_stake={ticket_key(t):t['stake'] for t in portfolio['tickets']}
        extra=[{**t,'stake':t['stake']-old_stake.get(ticket_key(t),0)} for t in portfolio['tickets'] if t['stake']>old_stake.get(ticket_key(t),0)]
        removed=[{**t,'stake':t['stake']-new_stake.get(ticket_key(t),0)} for t in baseline['tickets'] if t['stake']>new_stake.get(ticket_key(t),0)]
        def subsettle(ts):return settle_final({'final_ticket':{'tickets':ts,'total_investment':sum(t['stake'] for t in ts)}},official)
        added=subsettle(extra);lost=subsettle(removed)
        out['conditional_rank_portfolio_result']={**ps,'candidate_id':portfolio['candidate_id'],'policy_sha256':portfolio['policy_sha256'],
          'portfolio_sha256':portfolio['sha256'],'added_capital':portfolio['required_capital']-baseline['required_capital'],
          'same_point_count':len(portfolio['tickets'])==len(baseline['tickets']),
          'false_positive_cost':sum(t['stake'] for t in extra)-sum(t['stake'] for t in added['winning_tickets']),
          'increased_allocation_return':added['total_payout'],'decreased_allocation_return':lost['total_payout'],
          'redeployed_capital':sum(t['stake'] for t in extra),'added_ticket_count':len(new_keys-base_keys),'removed_ticket_count':len(base_keys-new_keys),
          'net_payout_increment':ps['total_payout']-base_return,'baseline_return':base_return,
          'oos_eligible':False,'production_effect':'NONE','actual_purchase':'UNVERIFIED'}
    out['sha256']=digest(out)
    return out

def persist_shadow_result(root, result):
    root=Path(root);rid=result['race_id'];pre=root/'runtime/role_rescue_shadow'/(rid+'.json')
    if not pre.exists():return None
    path=root/'runtime/role_rescue_shadow_results'/(rid+'.json')
    if path.exists():
        old=json.loads(path.read_text());shadow=json.loads(pre.read_text())
        canonical=root/'runtime/results'/(rid+'.json')
        if (shadow.get('sha256')!=digest({k:v for k,v in shadow.items() if k!='sha256'})
                or old.get('sha256')!=digest({k:v for k,v in old.items() if k!='sha256'})
                or old.get('shadow_sha256')!=shadow.get('sha256')
                or old.get('source_sha256')!=shadow.get('source_sha256')
                or old.get('official_raw_sha256')!=result['official_result']['raw_sha256']
                or result['frozen_prediction_ref']['immutable_final_sha256']!=shadow['baseline_final_sha256']
                or (old.get('result_request_sha256')!=digest(result) if 'result_request_sha256' in old
                    else not canonical.exists() or json.loads(canonical.read_text())!=result)):
            raise ValueError('IMMUTABLE_SHADOW_RESULT_CONFLICT')
        write_status(root/'runtime/role_rescue_shadow_status.json',records_dir=path.parent)
        return old  # Legacy qualification is retained as recorded, never re-signed/relabelled.
    out=settle_shadow(json.loads(pre.read_text()),result)
    shadow=json.loads(pre.read_text())
    witness=actions_pre_result_witness(shadow)
    out['persistence_witness']=witness
    out['result_request_sha256']=digest(result)
    out['oos_candidate_id']=shadow.get('oos_candidate_id')
    out['oos_preregistration_sha256']=shadow.get('oos_preregistration_sha256')
    out['prediction_input_sha256']=shadow.get('prediction_input_sha256')
    registration=witness.get('preregistration') or {}
    out['preregistration_verified']=bool(witness.get('preregistration_verified') is True
        and registration.get('archive_and_pins_verified') is True and registration.get('owner_approval_verified') is True)
    out['oos_eligibility_scope']=(witness.get('preregistration') or {}).get('eligibility_scope')
    out['oos_pin_fingerprint']=(witness.get('preregistration') or {}).get('pin_fingerprint')
    out['role_learning_arms_oos_eligible']=None
    out['role_learning_arms_eligibility_status']='NOT_ESTABLISHED_BY_RANK_COHORT; STATE_EXISTENCE_BEFORE_SOURCE_REQUIRES_SEPARATE_EVIDENCE'
    out['oos_eligible']=bool(witness.get('verified') and out['preregistration_verified']
        and out['oos_eligibility_scope']==OOS_SCOPE and shadow.get('temporally_eligible')
        and instant(shadow['observed_at']).date().isoformat()>POLICY['training_end']
        and shadow.get('classification')=='PRE_CUTOFF_SHADOW')
    if out.get('conditional_rank_evaluation'):
        out['conditional_rank_evaluation']['oos_eligible']=out['oos_eligible']
    if out.get('conditional_rank_portfolio_result'):
        out['conditional_rank_portfolio_result']['oos_eligible']=out['oos_eligible']
    out['eligibility_status']='FORWARD_OOS_ELIGIBLE' if out['oos_eligible'] else 'PENDING_PREREGISTRATION_AND_INDEPENDENT_CONTENT_WITNESS'
    out['sha256']=digest({k:v for k,v in out.items() if k!='sha256'})
    if path.exists():
        if json.loads(path.read_text())!=out:raise ValueError('IMMUTABLE_SHADOW_RESULT_CONFLICT')
    else:
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    write_status(root/'runtime/role_rescue_shadow_status.json',records_dir=path.parent)
    return out

def write_status(path='runtime/role_rescue_shadow_status.json', *, records_dir=None):
    """Rebuild only the disposable view from immutable per-race records."""
    path=Path(path)
    records_dir=Path(records_dir) if records_dir is not None else path.parent/'role_rescue_shadow_results'
    records=[json.loads(p.read_text()) for p in sorted(records_dir.glob('*.json'))]
    ids=[r['race_id'] for r in records]
    if len(ids)!=len(set(ids)):raise ValueError('DUPLICATE_SHADOW_RACE')
    def witnessed(r):
        witness=r.get('persistence_witness') or {};registration=witness.get('preregistration') or {}
        return bool(r.get('oos_eligible') and r.get('preregistration_verified')
            and witness.get('verified') and registration.get('verified')
            and registration.get('archive_and_pins_verified') is True and registration.get('owner_approval_verified') is True
            and r.get('oos_eligibility_scope')==registration.get('eligibility_scope')==OOS_SCOPE
            and re.fullmatch(r'[0-9a-f]{64}',str(r.get('oos_pin_fingerprint','')))
            and r.get('oos_pin_fingerprint')==registration.get('pin_fingerprint')
            and r.get('oos_candidate_id')==registration.get('candidate_id')
            and r.get('oos_preregistration_sha256')==registration.get('registration_sha256')
            and r.get('oos_candidate_id') and r.get('oos_preregistration_sha256'))
    pins={}
    for r in records:
        if witnessed(r):pins.setdefault(r['oos_candidate_id'],set()).add(r['oos_pin_fingerprint'])
    conflicted={cid for cid,values in pins.items() if len(values)>1}
    def qualified(r):return witnessed(r) and r['oos_candidate_id'] not in conflicted
    cohorts={}
    for r in records:
        cid=r.get('oos_candidate_id') or 'LEGACY_UNREGISTERED'
        cohort=cohorts.setdefault(cid,{'distinct_races':0,'forward_oos_verified_races':0,'days':set(),'venues':set()})
        cohort['distinct_races']+=1;cohort['forward_oos_verified_races']+=qualified(r)
        if qualified(r):cohort['days'].add(r['race_id'].split('-')[3]);cohort['venues'].add(r['race_id'].split('-')[2])
    for cohort in cohorts.values():
        cohort['days']=sorted(cohort['days']);cohort['venues']=sorted(cohort['venues'])
        cohort['minimum_distinct_races']=60;cohort['minimum_days']=3;cohort['minimum_venues']=2
        cohort['automatic_promotion']=False
        cohort['eligibility_scope']=OOS_SCOPE if cohort['forward_oos_verified_races'] else None
    for cid,cohort in cohorts.items():
        cohort['pin_fingerprints']=sorted(pins.get(cid,set()))
        cohort['eligibility_status']='COHORT_PIN_CONFLICT' if cid in conflicted else 'COLLECTING_NO_AUTOMATIC_PROMOTION'
    tracker={'candidate_id':CANDIDATE_ID,'distinct_races':len(ids),'forward_oos_verified_races':sum(qualified(r) for r in records),
             'legacy_recorded_eligible_races':sum(bool(r.get('oos_eligible')) and not r.get('preregistration_verified') for r in records),
             'unqualified_recorded_claims':sum(bool(r.get('oos_eligible')) and not qualified(r) for r in records),
             'cohorts':cohorts,
             'promotion_denominator':'PER_COHORT_ONLY; legacy/global totals never satisfy a new cohort gate',
             'status':'COLLECTING_NO_AUTOMATIC_PROMOTION','automatic_promotion':False,
             'results':[{**{k:r[k] for k in ('race_id','sha256','policy_fingerprint')},
                         'oos_candidate_id':r.get('oos_candidate_id'),'recorded_oos_eligible':r.get('oos_eligible'),
                         'oos_eligible':qualified(r)} for r in records]}
    tracker['sha256']=digest(tracker)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(tracker,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    return tracker

def pre_result_witness(root,shadow):
    """Verify an actual tracked addition, never infer birth from a shallow root."""
    path='runtime/role_rescue_shadow/'+shadow['race_id']+'.json'
    def git(*args):
        return subprocess.check_output(['git',*args],cwd=root,text=True,stderr=subprocess.DEVNULL).strip()
    try:
        commit=git('log','--diff-filter=A','-1','--format=%H','--',path)
        if not commit:raise ValueError('SHADOW_NOT_COMMITTED')
        parents=git('cat-file','-p',commit).split('\n')
        parent=next((x.split()[1] for x in parents if x.startswith('parent ')),None)
        if not parent:raise ValueError('SHADOW_WITNESS_NO_PARENT')
        git('cat-file','-e',parent)
        frozen=json.loads(git('show',commit+':'+path))
        if frozen!=shadow:raise ValueError('SHADOW_CHANGED_SINCE_FREEZE')
        timestamp=git('show','-s','--format=%cI',commit)
        if not (instant(shadow['observed_at']) <= instant(timestamp) <= instant(shadow['prediction_cutoff'])):
            raise ValueError('SHADOW_COMMITTED_AFTER_CUTOFF_OR_BEFORE_OBSERVATION')
        return {'verified':False,'git_history_correlated':True,'status':'GIT_TIME_ONLY_NOT_INDEPENDENT_SERVER_WITNESS',
                'commit_sha':commit,'committed_at':timestamp,
                'scope':'Committer timestamps are mutable; cannot establish independent pre-result receipt.'}
    except (subprocess.CalledProcessError,ValueError,StopIteration):
        return {'verified':False,'status':'UNVERIFIED_PRE_RESULT_PERSISTENCE'}


WITNESS_REPO = 'b03la013-max/keibametrics-runtime'

def utility_artifact_name(run_id, attempt):
    if not str(run_id).isdigit() or not str(attempt).isdigit() or int(attempt)<1:
        raise ValueError('WITNESS_EXECUTION_ID')
    return 'krs-utility-'+str(run_id)+('' if int(attempt)==1 else '-attempt-'+str(attempt))


def _registration_scope(reg):
    keys=('sidecar_code_sha256','rank_code_sha256','checkpoint_code_sha256','model_sha256',
          'model_policy_sha256','portfolio_policy_sha256','role_policy_fingerprint','model_candidate_id',
          'sidecar_candidate_id','portfolio_candidate_id','current_authority_manifest','eligibility_scope')
    fingerprint=digest({k:reg[k] for k in keys})
    scope=digest({'candidate_id':reg['candidate_id'],'pin_fingerprint':fingerprint,
        'target_race_ids':reg['target_race_ids'],'input_scope':reg.get('input_scope'),
        'conditional_p2':reg.get('conditional_p2'),'production_effect':reg['production_effect'],
        'minimum_forward_distinct_races':60,'minimum_forward_days':3,'minimum_forward_venues':2,
        'no_automatic_promotion':True,'actual_purchase_authority':False,'notification_authority':False})
    return fingerprint,scope


def _owner_endpoint(ref):
    match=re.fullmatch(re.escape('https://github.com/'+WITNESS_REPO+'/pull/')+
        r'([1-9][0-9]*)#(issuecomment|pullrequestreview)-([1-9][0-9]*)',str(ref))
    if not match:raise ValueError('OWNER_PROVIDER_REFERENCE_REQUIRED')
    pr,kind,number=match.groups()
    return ('issues/comments/'+number if kind=='issuecomment' else 'pulls/'+pr+'/reviews/'+number),pr,kind,int(number)


def _owner_body(record):
    if not isinstance(record,dict) or not isinstance(record.get('body'),str):raise ValueError('OWNER_EXPLICIT_SCOPE_APPROVAL_REQUIRED')
    body=record['body'].strip()
    if body.startswith('```json\n') and body.endswith('\n```'):body=body[8:-4]
    out=json.loads(body)
    if not isinstance(out,dict):raise ValueError('OWNER_EXPLICIT_SCOPE_APPROVAL_REQUIRED')
    return out


def _read_owner_approval(reg, api):
    import base64
    endpoint,_,_,_=_owner_endpoint(reg.get('owner_approval_ref'))
    record=json.loads(api(endpoint));body=_owner_body(record);head=body['approved_head_sha']
    if not re.fullmatch(r'[0-9a-f]{40}',str(head)):raise ValueError('OWNER_EXACT_HEAD_REQUIRED')
    hashes={}
    for path in ('runtime/jra_role_learning_shadow.py','runtime/jra_conditional_rank_shadow.py','runtime/jra_shadow_checkpoint.py'):
        content=base64.b64decode(json.loads(api('contents/'+path+'?ref='+head))['content'])
        hashes[path]=hashlib.sha256(content).hexdigest()
    model=json.loads(base64.b64decode(json.loads(api('contents/research/jra_conditional_rank/model.json?ref='+head))['content']))
    from jra_conditional_rank_shadow import policy_sha
    if model.get('sha256')!=digest({k:v for k,v in model.items() if k!='sha256'}):raise ValueError('OWNER_HEAD_MODEL_HASH')
    return {'endpoint':endpoint,'record':record,'approved_head_sha':head,'code_sha256':hashes,
            'model_sha256':model['sha256'],'model_policy_sha256':policy_sha(model)}


def snapshot_preregistration_owner_approvals(root, output):
    """Existing CI archives authenticated read-only provider responses before SOURCE."""
    def api(path):return subprocess.check_output(['gh','api','--hostname','github.com',
        'repos/'+WITNESS_REPO+'/'+path],timeout=30,stderr=subprocess.DEVNULL)
    records={}
    for path in sorted((Path(root)/'runtime/jra_race_day_plan').glob('*.json')):
        reg=json.loads(path.read_text()).get('forward_oos_preregistration') or {}
        if not isinstance(reg,dict) or reg.get('active') is not True or not reg.get('owner_approval_ref'):continue
        try:records[reg['owner_approval_ref']]=_read_owner_approval(reg,api)
        except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError) as exc:
            records[str(reg['owner_approval_ref'])]={'error':type(exc).__name__}
    Path(output).write_text(json.dumps(records,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    return records


def _preregistration_proof(shadow, proof):
    """Bind the existing day-plan cohort to an EARLIER CI archive, not producer time."""
    try:
        reg=shadow.get('oos_preregistration')
        if not isinstance(reg,dict) or not isinstance(proof,dict):raise ValueError('PREREGISTRATION_PROOF_MISSING')
        if (shadow.get('oos_preregistration_sha256')!=digest(reg)
                or reg.get('sha256')!=digest({k:v for k,v in reg.items() if k!='sha256'})):
            raise ValueError('PREREGISTRATION_HASH')
        if reg.get('active') is not True or reg.get('status')!='OWNER_APPROVED_PREREGISTRATION':
            raise ValueError('PREREGISTRATION_INACTIVE_OR_OWNER_APPROVAL_MISSING')
        cid=reg.get('candidate_id');rank=shadow.get('conditional_rank_comparison') or {};portfolio=shadow.get('conditional_rank_portfolio') or {}
        if (not isinstance(cid,str) or not re.fullmatch(r'JRA-[A-Z0-9-]{5,100}',cid)
                or cid==rank.get('candidate_id') or shadow.get('oos_candidate_id')!=cid
                or reg.get('model_candidate_id')!=rank.get('candidate_id')
                or reg.get('sidecar_candidate_id')!=shadow.get('candidate_id')
                or reg.get('portfolio_candidate_id')!=portfolio.get('candidate_id')
                or reg.get('current_authority_manifest')!=shadow.get('authority_manifest')
                or shadow['race_id'] not in reg.get('target_race_ids',[])):
            raise ValueError('PREREGISTRATION_COHORT_OR_MODEL_IDENTITY')
        if (reg.get('minimum_forward_distinct_races')!=60 or reg.get('minimum_forward_days')!=3
                or reg.get('minimum_forward_venues')!=2 or reg.get('no_automatic_promotion') is not True
                or reg.get('eligibility_scope')!=OOS_SCOPE or shadow.get('oos_eligibility_scope')!=OOS_SCOPE
                or reg.get('production_effect')!='NONE' or reg.get('actual_purchase_authority') is not False
                or reg.get('notification_authority') is not False):
            raise ValueError('PREREGISTRATION_SCOPE')
        pins={'sidecar_code_sha256':shadow['code_sha256'],'rank_code_sha256':rank['code_sha256'],
              'checkpoint_code_sha256':shadow['oos_checkpoint_code_sha256'],
              'model_sha256':rank['model_sha256'],'model_policy_sha256':rank['model_policy_sha256'],
              'portfolio_policy_sha256':portfolio['policy_sha256'],'role_policy_fingerprint':shadow['policy_fingerprint']}
        if any(reg.get(k)!=v for k,v in pins.items()):raise ValueError('PREREGISTRATION_CODE_MODEL_POLICY_PIN')
        pin_fingerprint,approval_scope=_registration_scope(reg)
        r=proof['run'];a=proof['artifact'];raw=proof['archive'];pointer=shadow['oos_preregistration_witness']
        if not all(isinstance(x,dict) for x in (r,a,pointer)) or not isinstance(raw,bytes):
            raise ValueError('PREREGISTRATION_PROVIDER_TYPE')
        if (r.get('repository',{}).get('full_name')!=WITNESS_REPO
                or r.get('head_repository',{}).get('full_name')!=WITNESS_REPO or r.get('head_branch')!='main'
                or r.get('path')!='.github/workflows/km-jra-learning-binding-audit.yml'
                or r.get('event') not in {'push','workflow_dispatch'} or r.get('conclusion')!='success'
                or not re.fullmatch(r'[0-9a-f]{40}',str(r.get('head_sha','')))
                or r.get('id')!=pointer.get('run_id') or a.get('id')!=pointer.get('artifact_id')
                or r.get('run_attempt',1)!=pointer.get('run_attempt',1)
                or a.get('name')!='jra-learning-mechanical-'+str(r['id'])
                or a.get('workflow_run',{}).get('id')!=r['id']
                or a.get('workflow_run',{}).get('head_sha')!=r.get('head_sha') or a.get('expired') is not False
                or len(raw)>32*1024*1024 or a.get('digest')!='sha256:'+hashlib.sha256(raw).hexdigest()):
            raise ValueError('PREREGISTRATION_PROVIDER_IDENTITY_OR_DIGEST')
        boundary=instant(shadow['source_freeze_at'])
        if not (instant(reg['registered_at'])<=instant(r['created_at'])<=instant(a['created_at'])
                <=instant(a['updated_at'])<boundary<=instant(shadow['prediction_cutoff'])):
            raise ValueError('PREREGISTRATION_NOT_INDEPENDENTLY_AVAILABLE_BEFORE_SOURCE')
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            def member(name):
                entries=[i for i in z.infolist() if i.filename==name]
                if len(entries)!=1 or entries[0].file_size>8*1024*1024:raise ValueError('PREREGISTRATION_ARCHIVE_MEMBER')
                return z.read(entries[0])
            day=shadow['race_id'].split('-')[3];day=day[:4]+'-'+day[4:6]+'-'+day[6:]
            plan=json.loads(member('runtime/jra_race_day_plan/'+day+'.json'))
            if plan.get('forward_oos_preregistration')!=reg:raise ValueError('PREREGISTRATION_FROZEN_BODY')
            for path,pin in [('runtime/jra_role_learning_shadow.py','sidecar_code_sha256'),
                             ('runtime/jra_conditional_rank_shadow.py','rank_code_sha256'),
                             ('runtime/jra_shadow_checkpoint.py','checkpoint_code_sha256')]:
                if hashlib.sha256(member(path)).hexdigest()!=reg[pin]:raise ValueError('PREREGISTRATION_FROZEN_CODE')
            model=json.loads(member('research/jra_conditional_rank/model.json'))
            from jra_conditional_rank_shadow import policy_sha
            if (model.get('sha256')!=digest({k:v for k,v in model.items() if k!='sha256'})
                    or model.get('sha256')!=reg['model_sha256'] or model.get('candidate_id')!=reg['model_candidate_id']
                    or policy_sha(model)!=reg['model_policy_sha256']):raise ValueError('PREREGISTRATION_FROZEN_MODEL')
            try:archived_owner=json.loads(member('oos-owner-approval-proofs.json')).get(reg.get('owner_approval_ref'))
            except (ValueError,TypeError,KeyError):archived_owner=None
        owner_verified=False;owner_reason='OWNER_PROVIDER_APPROVAL_UNVERIFIED'
        try:
            owner=archived_owner;record=proof.get('owner_approval_record')
            endpoint,pr,kind,number=_owner_endpoint(reg.get('owner_approval_ref'))
            if not isinstance(owner,dict) or not isinstance(record,dict):raise ValueError('OWNER_PROVIDER_SNAPSHOT_MISSING')
            saved=owner['record']
            if (any(record.get(k)!=saved.get(k) for k in ('id','body','html_url','state','commit_id','submitted_at',
                    'created_at','updated_at','pull_request_url','issue_url'))
                    or (record.get('user') or {}).get('login')!=(saved.get('user') or {}).get('login')):
                raise ValueError('OWNER_APPROVAL_CHANGED_SINCE_REGISTRATION_ARCHIVE')
            body=_owner_body(record)
            if (owner.get('endpoint')!=endpoint or record.get('id')!=number
                    or record.get('html_url')!=reg['owner_approval_ref']
                    or (record.get('user') or {}).get('login','').casefold()!=WITNESS_REPO.split('/')[0].casefold()
                    or body.get('decision')!='APPROVE_PROSPECTIVE_SHADOW_PREREGISTRATION'
                    or body.get('candidate_id')!=cid or body.get('scope_sha256')!=approval_scope
                    or body.get('approved_head_sha')!=owner.get('approved_head_sha')
                    or not re.fullmatch(r'[0-9a-f]{40}',str(owner.get('approved_head_sha','')))):
                raise ValueError('OWNER_IDENTITY_OR_EXPLICIT_SCOPE_MISMATCH')
            api_url='https://api.github.com/repos/'+WITNESS_REPO+'/'
            if kind=='pullrequestreview':
                if (record.get('state')!='APPROVED' or record.get('commit_id')!=owner['approved_head_sha']
                        or record.get('pull_request_url')!=api_url+'pulls/'+pr):raise ValueError('OWNER_REVIEW_NOT_APPROVED')
                approved_at=instant(record['submitted_at'])
            else:
                if record.get('issue_url')!=api_url+'issues/'+pr:raise ValueError('OWNER_COMMENT_PR_IDENTITY')
                approved_at=instant(record['updated_at'])
                if instant(record['created_at'])>approved_at:raise ValueError('OWNER_COMMENT_CHRONOLOGY')
            if not approved_at<=instant(reg['registered_at'])<instant(a['created_at']):raise ValueError('OWNER_APPROVAL_AFTER_REGISTRATION')
            expected_codes={path:reg[key] for path,key in (
                ('runtime/jra_role_learning_shadow.py','sidecar_code_sha256'),
                ('runtime/jra_conditional_rank_shadow.py','rank_code_sha256'),
                ('runtime/jra_shadow_checkpoint.py','checkpoint_code_sha256'))}
            if (owner.get('code_sha256')!=expected_codes or owner.get('model_sha256')!=reg['model_sha256']
                    or owner.get('model_policy_sha256')!=reg['model_policy_sha256']):raise ValueError('OWNER_APPROVED_HEAD_PIN_MISMATCH')
            owner_verified=True;owner_reason='OWNER_EXACT_SCOPE_PROVIDER_APPROVAL_AND_EARLIER_ARCHIVE_BOUND'
        except (ValueError,KeyError,TypeError) as exc:owner_reason=str(exc)
        return {'verified':owner_verified,'archive_and_pins_verified':True,'owner_approval_verified':owner_verified,
                'status':owner_reason,
                'candidate_id':cid,'registration_sha256':digest(reg),'run_id':r['id'],'artifact_id':a['id'],
                'eligibility_scope':OOS_SCOPE,
                'pin_fingerprint':pin_fingerprint,
                'owner_approval_scope_sha256':approval_scope,
                'server_created_at':a['created_at'],'archive_digest':a['digest'],
                'owner_approval_ref':reg.get('owner_approval_ref')}
    except (ValueError,KeyError,TypeError,OSError,zipfile.BadZipFile) as exc:
        return {'verified':False,'archive_and_pins_verified':False,'owner_approval_verified':False,
                'status':str(exc),'candidate_id':shadow.get('oos_candidate_id')}


def verify_actions_artifact(shadow, run, artifact, archive, code_bytes, *, registration_proof=None):
    """Bind GitHub server receipt time to exact archived Shadow bytes.

    Inputs are fetched from the fixed repository API by actions_pre_result_witness;
    callers must not substitute self-reported JSON as provider evidence.
    """
    ctx=shadow.get('actions_freeze_context') or {}
    if shadow.get('sha256') != digest({k:v for k,v in shadow.items() if k!='sha256'}):
        raise ValueError('WITNESS_SHADOW_HASH_INVALID')
    nested=shadow.get('conditional_rank_comparison') or {}
    if nested.get('role_rankings'):
        if (nested.get('sha256')!=digest({k:v for k,v in nested.items() if k!='sha256'})
                or nested.get('candidate_id')!='JRA-CONDITIONAL-RANK-20261018-R1'
                or shadow.get('additional_code_sha256')!={'runtime/jra_conditional_rank_shadow.py':nested.get('code_sha256')}
                or shadow.get('additional_input_sha256')!={'research/jra_conditional_rank/model.json':nested.get('model_sha256')}
                or nested.get('source_sha256')!=shadow['source_sha256']
                or nested.get('runner_universe_sha256')!=shadow['runner_universe_sha256']
                or nested.get('prediction_cutoff')!=shadow['prediction_cutoff']):
            raise ValueError('WITNESS_NESTED_RANK_BINDING_INVALID')
    portfolio=shadow.get('conditional_rank_portfolio') or {}
    if portfolio:
        from jra_conditional_rank_shadow import EXPOSURE_POLICY
        if (portfolio.get('sha256')!=digest({k:v for k,v in portfolio.items() if k!='sha256'})
            or portfolio.get('policy_sha256')!=digest(EXPOSURE_POLICY) or portfolio.get('policy')!=EXPOSURE_POLICY
            or portfolio.get('rank_comparison_sha256')!=nested.get('sha256')
            or portfolio.get('model_policy_sha256')!=nested.get('model_policy_sha256')
            or portfolio.get('model_sha256')!=nested.get('model_sha256')
            or portfolio.get('baseline_final_sha256')!=shadow['baseline_final_sha256']
            or any(portfolio.get(k)!=shadow.get(k) for k in ('race_id','source_sha256','runner_universe_sha256','prediction_cutoff'))):
            raise ValueError('WITNESS_EXPOSURE_BINDING_INVALID')
    if shadow.get('candidate_id')!=CANDIDATE_ID or shadow.get('policy_fingerprint')!=digest(POLICY):
        raise ValueError('WITNESS_CANDIDATE_POLICY_MISMATCH')
    if ctx.get('repository') != WITNESS_REPO or str(run['id']) != str(ctx.get('run_id')):
        raise ValueError('WITNESS_RUN_IDENTITY')
    if (run.get('repository',{}).get('full_name') != WITNESS_REPO
            or run.get('head_repository',{}).get('full_name') != WITNESS_REPO
            or run.get('head_branch') != 'main' or run.get('head_sha') != ctx.get('head_sha')
            or run.get('path') != '.github/workflows/km-formal-request-runner.yml'
            or run.get('event') not in {'push','workflow_dispatch'}
            or run.get('conclusion') != 'success'
            or str(run.get('run_attempt')) != str(ctx.get('run_attempt'))):
        raise ValueError('WITNESS_UNTRUSTED_WORKFLOW')
    if hashlib.sha256(code_bytes).hexdigest()!=shadow['code_sha256']:
        raise ValueError('WITNESS_CODE_MISMATCH')
    if (artifact.get('name') != utility_artifact_name(run['id'],run['run_attempt'])
            or artifact.get('workflow_run',{}).get('id') != run['id']
            or artifact.get('workflow_run',{}).get('head_sha') != run['head_sha']
            or artifact.get('expired') is not False):
        raise ValueError('WITNESS_ARTIFACT_IDENTITY')
    if not (instant(run['created_at']) <= instant(shadow['observed_at'])
            <= instant(artifact['created_at']) <= instant(artifact['updated_at'])
            <= instant(shadow['prediction_cutoff'])):
        raise ValueError('WITNESS_SERVER_RECEIPT_AFTER_CUTOFF_OR_BAD_CHRONOLOGY')
    if len(archive)>32*1024*1024 or artifact.get('digest') != 'sha256:'+hashlib.sha256(archive).hexdigest():
        raise ValueError('WITNESS_ARCHIVE_DIGEST')
    name=shadow['race_id']+'/role_learning_shadow.json'
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        entries=[i for i in z.infolist() if i.filename==name]
        if len(entries)!=1 or entries[0].file_size>8*1024*1024:
            raise ValueError('WITNESS_ARCHIVE_MEMBER')
        if json.loads(z.read(entries[0])) != shadow:
            raise ValueError('WITNESS_FROZEN_CONTENT_MISMATCH')
        if 'oos_preregistration' in shadow:
            name=shadow['race_id']+'/shadow_input.json';members=[i for i in z.infolist() if i.filename==name]
            if len(members)!=1 or members[0].file_size>16*1024*1024:raise ValueError('WITNESS_PREREGISTRATION_CHECKPOINT')
            c=json.loads(z.read(members[0]));q=c['request']
            if (c.get('sha256')!=digest({k:v for k,v in c.items() if k!='sha256'})
                    or c['sha256']!=shadow.get('delivery_checkpoint_sha256')
                    or c.get('oos_preregistration')!=shadow['oos_preregistration']
                    or c.get('oos_preregistration_witness')!=shadow.get('oos_preregistration_witness')
                    or c.get('oos_checkpoint_code_sha256')!=shadow.get('oos_checkpoint_code_sha256')
                    or c.get('request_sha256')!=digest(q)
                    or any(c.get(k)!=shadow.get(v) for k,v in (
                        ('race_id','race_id'),('source_sha256','source_sha256'),
                        ('runner_universe_sha256','runner_universe_sha256'),('prediction_cutoff','prediction_cutoff'),
                        ('final_sha256','baseline_final_sha256'),('learning_input_sha256','checkpoint_learning_input_sha256')))
                    or q.get('source_snapshot_sha256')!=shadow['source_sha256']
                    or shadow.get('prediction_input_sha256')!=digest({'request_sha256':c['request_sha256'],'learning_states':c['learning_states']})
                    or q['source_snapshot']['source_freeze_at']!=shadow.get('source_freeze_at')):
                raise ValueError('WITNESS_PREREGISTRATION_CHECKPOINT_BINDING')
    registration=_preregistration_proof(shadow,registration_proof)
    return {'verified':True,'status':'GITHUB_ARTIFACT_SERVER_RECEIPT_AND_CONTENT_VERIFIED',
            'repository':WITNESS_REPO,'run_id':run['id'],'artifact_id':artifact['id'],
            'server_created_at':artifact['created_at'],'server_updated_at':artifact['updated_at'],
            'archive_digest':artifact['digest'],'shadow_sha256':shadow['sha256'],
            'preregistration_verified':registration['verified'],'preregistration':registration,
            'scope':'Pre-cutoff persistence only; predictive improvement and promotion remain separate.'}

def actions_pre_result_witness(shadow):
    """Read-only provider verification; missing credentials/expired evidence fail closed."""
    import base64
    ctx=shadow.get('actions_freeze_context') or {}
    if ctx.get('repository') != WITNESS_REPO or not str(ctx.get('run_id','')).isdigit():
        return {'verified':False,'status':'MISSING_ACTIONS_FREEZE_CONTEXT'}
    def api(path, *, timeout=30):
        return subprocess.check_output(['gh','api','--hostname','github.com',
            'repos/'+WITNESS_REPO+'/'+path],timeout=timeout,stderr=subprocess.DEVNULL)
    try:
        rid=str(ctx['run_id']);attempt=str(ctx.get('run_attempt',''))
        utility_artifact_name(rid,attempt)
        run=json.loads(api('actions/runs/'+rid+'/attempts/'+attempt))
        artifacts=json.loads(api('actions/runs/'+rid+'/artifacts?per_page=100'))['artifacts']
        matches=[a for a in artifacts if a.get('name')==utility_artifact_name(rid,attempt)]
        if len(matches)!=1:raise ValueError('WITNESS_ARTIFACT_NOT_UNIQUE')
        artifact=matches[0]
        if type(artifact.get('id')) is not int or not 0<artifact.get('size_in_bytes',0)<=32*1024*1024:
            raise ValueError('WITNESS_ARTIFACT_SIZE_OR_ID')
        code=json.loads(api('contents/runtime/jra_role_learning_shadow.py?ref='+run['head_sha']))
        code_bytes=base64.b64decode(code['content'],validate=False)
        for path,expected in shadow.get('additional_code_sha256',{}).items():
            if path!='runtime/jra_conditional_rank_shadow.py':raise ValueError('WITNESS_UNREGISTERED_CODE')
            obj=json.loads(api('contents/'+path+'?ref='+run['head_sha']))
            if hashlib.sha256(base64.b64decode(obj['content'])).hexdigest()!=expected:raise ValueError('WITNESS_ADDITIONAL_CODE_MISMATCH')
        for path,expected in shadow.get('additional_input_sha256',{}).items():
            if path!='research/jra_conditional_rank/model.json':raise ValueError('WITNESS_UNREGISTERED_INPUT')
            obj=json.loads(api('contents/'+path+'?ref='+run['head_sha']))
            model=json.loads(base64.b64decode(obj['content']))
            if digest({k:v for k,v in model.items() if k!='sha256'})!=expected or model.get('sha256')!=expected:raise ValueError('WITNESS_MODEL_INPUT_MISMATCH')
            if (shadow.get('conditional_rank_comparison') or {}).get('model_policy_sha256'):
                from jra_conditional_rank_shadow import policy_sha
                if shadow['conditional_rank_comparison']['model_policy_sha256']!=policy_sha(model):raise ValueError('WITNESS_MODEL_POLICY_MISMATCH')
        registration_proof=None
        if 'oos_preregistration' in shadow:
            obj=json.loads(api('contents/runtime/jra_shadow_checkpoint.py?ref='+run['head_sha']))
            checkpoint_code=base64.b64decode(obj['content'])
            if hashlib.sha256(checkpoint_code).hexdigest()!=shadow.get('oos_checkpoint_code_sha256'):
                raise ValueError('WITNESS_CHECKPOINT_CODE_MISMATCH')
            pointer=shadow.get('oos_preregistration_witness') or {}
            if not isinstance(pointer,dict):pointer={}
            if (type(pointer.get('run_id')) is int and pointer['run_id']>0
                    and type(pointer.get('artifact_id')) is int and pointer['artifact_id']>0):
                try:
                    prior_attempt=pointer.get('run_attempt',1)
                    if type(prior_attempt) is not int or prior_attempt<1:raise ValueError('PREREGISTRATION_ATTEMPT')
                    prior_run=json.loads(api('actions/runs/'+str(pointer['run_id'])+'/attempts/'+str(prior_attempt),timeout=10))
                    prior_artifact=json.loads(api('actions/artifacts/'+str(pointer['artifact_id']),timeout=10))
                    prior_zip=api('actions/artifacts/'+str(pointer['artifact_id'])+'/zip',timeout=10)
                    registration_proof={'run':prior_run,'artifact':prior_artifact,'archive':prior_zip}
                    try:
                        endpoint,*_=_owner_endpoint(shadow['oos_preregistration'].get('owner_approval_ref'))
                        registration_proof['owner_approval_record']=json.loads(api(endpoint,timeout=10))
                    except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError):pass
                except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError):
                    registration_proof=None  # Missing proof affects only Shadow qualification.
        archive=api('actions/artifacts/'+str(artifact['id'])+'/zip')
        return verify_actions_artifact(shadow,run,artifact,archive,code_bytes,registration_proof=registration_proof)
    except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError,zipfile.BadZipFile) as exc:
        return {'verified':False,'status':'UNVERIFIED_GITHUB_ARTIFACT_WITNESS','reason':type(exc).__name__+':'+str(exc)[:180]}

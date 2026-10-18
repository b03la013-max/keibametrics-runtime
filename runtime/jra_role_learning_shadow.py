"""Pre-cutoff, result-blind JRA role/learning sidecar; no Production authority.

Designed after 2026-10-18. That day is exploration/regression, never forward OOS.
Existing KRS proposals are hypotheses, not probabilities or purchase orders.
"""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import subprocess
from pathlib import Path

CANDIDATE_ID = 'JRA-ROLE-LEARNING-20261018-R1'
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
        arms[name]={**settled,'added_capital':arm['added_capital'],
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
    out['sha256']=digest(out)
    return out

def persist_shadow_result(root, result):
    root=Path(root);rid=result['race_id'];pre=root/'runtime/role_rescue_shadow'/(rid+'.json')
    if not pre.exists():return None
    out=settle_shadow(json.loads(pre.read_text()),result)
    shadow=json.loads(pre.read_text())
    witness=pre_result_witness(root,shadow)
    out['persistence_witness']=witness
    # Git committer dates can be backdated. A local history match cannot prove
    # provider receipt before cutoff; server-side artifact witness is separate.
    out['oos_eligible']=False
    out['eligibility_status']='PENDING_SERVER_TIMESTAMP_AND_ARTIFACT_CONTENT_WITNESS'
    out['sha256']=digest({k:v for k,v in out.items() if k!='sha256'})
    path=root/'runtime/role_rescue_shadow_results'/(rid+'.json')
    if path.exists():
        if json.loads(path.read_text())!=out:raise ValueError('IMMUTABLE_SHADOW_RESULT_CONFLICT')
    else:
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    records=[json.loads(p.read_text()) for p in sorted(path.parent.glob('*.json'))]
    ids=[r['race_id'] for r in records]
    if len(ids)!=len(set(ids)):raise ValueError('DUPLICATE_SHADOW_RACE')
    tracker={'candidate_id':CANDIDATE_ID,'distinct_races':len(ids),'forward_oos_verified_races':sum(r['oos_eligible'] for r in records),
             'status':'COLLECTING_NO_AUTOMATIC_PROMOTION','automatic_promotion':False,
             'results':[{k:r[k] for k in ('race_id','sha256','policy_fingerprint','oos_eligible')} for r in records]}
    tracker['sha256']=digest(tracker)
    (root/'runtime/role_rescue_shadow_status.json').write_text(json.dumps(tracker,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    return out

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

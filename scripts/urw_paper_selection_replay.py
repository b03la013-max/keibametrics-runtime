"""Private result revision, four-cell replay and forward research Freeze CLI.

No deployment, source admission, signing, actual purchase or Production entry.
Replay keeps the original archive and the old accounting adapters unchanged.
The forward command accepts no result/market label argument and uses wall time.
"""
from __future__ import annotations

import argparse
import ast
import copy
from datetime import datetime, timezone
from fractions import Fraction
import gzip
import hashlib
from itertools import combinations, permutations
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
from runtime.urw_paper_selection import (POLICY,sha,_check_sha,canonical_tickets,
                                         select_portfolio,p1_role_hypotheses)
from runtime.urw_nankan_reference_source import (parse_result,private_directory,save_json,
                                                private_lock,DOM,decode,Node,one)
from runtime.minimum_efficient_coverage import build_mec_plan,validate_mec_plan
from runtime.capital_policy import resolve_capital_policy
from runtime.mec_r4_shadow import settle_ticket_list
from runtime.jra_ticket_tree_renderer import render_ticket_tree

ARMS=('BASELINE','CANDIDATE')
CELLS=('P0S0','P0S1','P1S0','P1S1')
CODE_FILES=('runtime/urw_paper_selection.py','scripts/urw_paper_selection_replay.py',
            'scripts/urw_candidate_krs_replay.py',
            'runtime/urw_nankan_reference_source.py','runtime/mec_r4_shadow.py',
            'runtime/local_krs_bridge_candidate.py','runtime/local_race_key_shadow_owner.py',
            'runtime/minimum_efficient_coverage.py','runtime/capital_policy.py',
            'runtime/jra_ticket_tree_renderer.py')


def read(path):return json.loads(Path(path).read_text())
def file_sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def sealed(obj):return {**obj,'sha256':sha(obj)}
def now():return datetime.now(timezone.utc)
def code_pins():return {p:file_sha(ROOT/p) for p in CODE_FILES}
def head():return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()


def verify_bundle(frozen,audits,observation,*,forward=False):
    """Bind existing Freeze objects, not a new SOURCE/Production admission."""
    pack=frozen['feature_pack'];race=observation['race']
    for value in (frozen,pack,*frozen['models'].values(),*frozen['predictions'].values(),*audits.values()):
        _check_sha(value)
    def aware(value):
        dt=datetime.fromisoformat(value)
        if dt.tzinfo is None:raise ValueError('RESEARCH_CONTEXT_TIMEZONE')
        return dt
    if (pack['venue_id']!='URW' or race['venue_id']!='URW' or race['provider']!='NANKAN_OFFICIAL'
            or frozen['race_date']!=pack['race_date'] or pack['race_date']!=race['race_date']
            or frozen['race_id']!=pack['race_id']
            or frozen['prediction_cutoff']!=pack['prediction_cutoff']
            or pack['prediction_cutoff']!=race['prediction_cutoff']
            or frozen['scheduled_post_at']!=pack['scheduled_post_at']
            or pack['scheduled_post_at']!=race['scheduled_post_at']
            or frozen['same_source_snapshot_sha256']!=pack['source_snapshot_sha256']
            or observation['source']['raw_sha256']!=pack['source_snapshot_sha256']
            or aware(observation['source']['fetched_at'])!=aware(pack['source_observed_at'])):
        raise ValueError('RESEARCH_FREEZE_CONTEXT_BINDING')
    number=race['race_no'];day=pack['race_date'].replace('-','')
    import re
    if (not re.fullmatch(re.escape(day)+r'18\d{4}'+f'{number:02d}',race['provider_race_id'])
            or not frozen['race_id'].startswith(f'KM-LOCAL-URW-{day}-R{number:02d}')):
        raise ValueError('RESEARCH_RACE_PROVIDER_IDENTITY')
    if set(audits)!=set(ARMS) or set(frozen['models'])!=set(ARMS) or set(frozen['predictions'])!=set(ARMS):
        raise ValueError('RESEARCH_ARM_UNIVERSE')
    # Reuse the existing preregistration function, not a second quality policy.
    owner_nodes=[n for n in ast.parse((ROOT/'scripts/urw_candidate_krs_replay.py').read_text()).body
                 if isinstance(n,ast.FunctionDef) and n.name=='owner_forward_protocol']
    owner_env={'_sha':sha}
    exec(compile(ast.Module(body=owner_nodes,type_ignores=[]),'existing_owner_protocol','exec'),owner_env)
    if frozen['protocol']!=owner_env['owner_forward_protocol'](frozen['models']['BASELINE'],frozen['models']['CANDIDATE']):
        raise ValueError('RESEARCH_EXISTING_OWNER_PROTOCOL_CHANGED')
    for arm in ARMS:
        pred=frozen['predictions'][arm];model=frozen['models'][arm];a=audits[arm]
        if (pred['model_sha256']!=model['sha256'] or pred['feature_sha256']!=pack['sha256']
                or pred['race_id']!=frozen['race_id'] or a['race_id']!=frozen['race_id']
                or pred['venue_id']!='URW' or pred['prediction_cutoff']!=frozen['prediction_cutoff']
                or a['source_snapshot_sha256']!=pack['source_snapshot_sha256']
                or a['snapshot']['prediction_id']!=frozen['race_id']
                or a['snapshot']['date']!=pack['race_date'] or a['snapshot']['race_no']!=number
                or a['snapshot']['master_seed']!=a['master_seed']
                or not aware(model['training_max_post_at'])<aware(pack['scheduled_post_at'])
                or not aware(model['trained_at'])<=aware(pred['frozen_at'])
                or not aware(pack['source_observed_at'])<=aware(pred['frozen_at'])<=aware(frozen['frozen_at'])<aware(frozen['prediction_cutoff'])
                or not aware(frozen['frozen_at'])<=aware(a['started_at'])<=aware(a['completed_at'])<aware(frozen['prediction_cutoff'])):
            raise ValueError('RESEARCH_MODEL_PREDICTION_AUDIT_CONTEXT')
        if forward and aware(a['completed_at'])>now():
            raise ValueError('FORWARD_AUDIT_COMPLETION_IS_IN_THE_FUTURE')
        if model.get('production_authority') is not False or pred.get('production_authority') is not False:
            raise ValueError('RESEARCH_NON_PRODUCTION_REQUIRED')
        from runtime.local_race_key_shadow_owner import predict_conditioned_owner
        reproduced=predict_conditioned_owner(model,pack,historical_replay=not forward)
        keys=('ranking','rankings_by_role','role_columns','role_widths','winner_model_mass',
              'p2_model_mass_given_head','p3_model_mass_given_pair','ordered_pairs','ordered_triples',
              'hard_role_exclusions','material_exact_evidence')
        if any(pred[k]!=reproduced[k] for k in keys):
            raise ValueError('RESEARCH_REGISTERED_MODEL_OUTPUT_REPRODUCTION')
        if {h:set(v) for h,v in pred['missingness'].items()}!={h:set(v) for h,v in reproduced['missingness'].items()}:
            raise ValueError('RESEARCH_REGISTERED_MODEL_MISSINGNESS_REPRODUCTION')


def existing_functions(helper):
    """Reuse pinned existing evaluation code without importing its old CLI.

    Only the known original function definitions are executed; the legacy
    refund-HOLD wrapper itself is not modified or silently reinterpreted.
    """
    from runtime.local_race_key_shadow_owner import _sha
    from runtime.post_result_learning import build_post_result_review,build_learning_state
    from runtime.krs_prediction_utility import evaluate_against_result
    helper=Path(helper)
    pins={'evaluate_observed_oos.py':'b92c10aba7e1b0dd4577c10a21a7c0e12cf84652778b022f5f3bad2db5b9370d',
          'frozen_ticket_attribution.py':'dcaa001215dc691b790b1cbead7faf2d6b1cee664fd3982a5ab18648ce6b5e59'}
    for name,digest in pins.items():
        if file_sha(helper/name)!=digest:raise ValueError('EXISTING_PRIVATE_EVALUATOR_PIN_CHANGED')
    env={'Fraction':Fraction,'json':json,'hashlib':hashlib,'datetime':datetime,'timezone':timezone,
         'DOM':DOM,'decode':decode,'Node':Node,'one':one,'ARMS':ARMS,
         'canon':lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode(),
         'sha':lambda b:hashlib.sha256(b).hexdigest(),'_sha':_sha,
         'build_post_result_review':build_post_result_review,'build_learning_state':build_learning_state,
         'evaluate_against_result':evaluate_against_result,'re':__import__('re')}
    def load(path,names=None):
        nodes=[n for n in ast.parse(Path(path).read_text()).body if isinstance(n,ast.FunctionDef)
               and (names is None or n.name in names)]
        if names is not None and {n.name for n in nodes}!=set(names):raise ValueError('EXISTING_FUNCTION_MISSING')
        exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),env)
    load(ROOT/'scripts/urw_candidate_krs_replay.py',('owner_forward_protocol','evaluate_owner_forward_comparison'))
    env['owner_namespace']=env
    load(helper/'evaluate_observed_oos.py',('require_frozen_bindings','verify_observation','tickets_sorted',
         'expand','ratio','qnumber','analytic_finance','overlap'))
    load(helper/'frozen_ticket_attribution.py')
    return env


def _research_mec(pred, original):
    """The SAME original S0 cartesian-PROTECT rule, only on new P1 roles."""
    req=copy.deepcopy(original['semantic_request']);roles=pred['role_columns']
    req['static_prediction']={'ranking':pred['ranking'],'roles':roles,'production_authority':False}
    req['role_registry']=[{'runner_id':h,'column':r,'status':'CORE','production_authority':False}
                          for h,rs in roles.items() for r in rs]
    req['pair_dispositions']=[];req['third_dispositions']=[]
    for h,hrs in roles.items():
        if 'W' not in hrs:continue
        for s,srs in roles.items():
            if h==s or 'P2' not in srs:continue
            req['pair_dispositions'].append({'head':h,'second':s,'status':'PROTECT',
                'reason':'UNAPPROVED_P1_SAME_S0_PAIR_RULE','production_authority':False})
            for t,trs in roles.items():
                if t in (h,s) or 'P3' not in trs:continue
                req['third_dispositions'].append({'head':h,'second':s,'third':t,'status':'PROTECT',
                    'reason':'UNAPPROVED_P1_SAME_S0_SET_RULE_NOT_EXACT','production_authority':False})
    mec=build_mec_plan(req);validate_mec_plan(mec)
    return {'semantic_request':req,'mec':mec,'capital':resolve_capital_policy(req,mec)}


def build_views(frozen,audits,observation,remaining):
    """No labels here. Identical function is called by Replay and forward CLI."""
    verify_bundle(frozen,audits,observation)
    inactive={'CANCELLED','SCRATCHED','EXCLUDED','WITHDRAWN'}
    if any(x.get('status') not in inactive|{'ACTIVE_DECLARED'} for x in observation['facts']):
        raise ValueError('RESEARCH_CURRENT_RUNNER_STATUS_UNKNOWN')
    excluded=[str(x['runner_id']) for x in observation['facts'] if x['status'] in inactive]
    views={}
    for arm in ARMS:
        a=audits[arm];p=frozen['predictions'][arm];_check_sha(a);_check_sha(p)
        if a['reference_static']!=p or p['feature_sha256']!=frozen['feature_pack']['sha256']:
            raise ValueError('RESEARCH_FREEZE_AUDIT_BINDING')
        ts=canonical_tickets(a['ticket_tree']['reflattened_tickets'])
        if canonical_tickets(a['mec']['tickets'])!=ts:raise ValueError('RESEARCH_ORIGINAL_TREE_MEC_MISMATCH')
        ref={'original_comparison_sha256':frozen['sha256'],'original_prediction_sha256':p['sha256'],
             'original_audit_sha256':a['sha256'],'immutable_original_mec_sha256':a['mec']['sha256'],
             'immutable_semantic_sha256':sha(a['semantic_request']),
             'krs_utility_sha256':a['krs_utility']['sha256'],
             'krs_snapshot_sha256':sha(a['krs_utility']['snapshot']),
             'krs_master_seed':a['master_seed'],'krs_input_sha256':a['krs_input_sha256'],
             'krs_output_file_sha256':a['krs_output_file_sha256']}
        cells={'P0S0':{'tickets':ts,'prediction':p,'immutable_source_ref':ref}}
        # First stage executes P0S1 before constructing any P1 alternative.
        s1=select_portfolio(p,ts,source_ref=ref,krs_utility=a['krs_utility'],
                            excluded_runner_ids=excluded,
                            day_remaining_yen=remaining[arm]['P0S1'])
        no_krs=select_portfolio(p,ts,source_ref=ref,excluded_runner_ids=excluded,
                                day_remaining_yen=remaining[arm]['P0S1_NO_KRS'])
        cells['P0S1']={'tickets':s1['selected_tickets'],'prediction':p,'selection':s1}
        p1=p1_role_hypotheses(p,frozen['feature_pack'],observation)
        rebuilt=_research_mec(p1['prediction'],a)
        # Verify this adapter reproduces S0 tickets on the frozen P0 roles.
        if canonical_tickets(_research_mec(p,a)['mec']['tickets'])!=ts:
            raise ValueError('RESEARCH_S0_REPRODUCTION_DISAGREES_WITH_ORIGINAL')
        p1tickets=canonical_tickets(rebuilt['mec']['tickets'])
        pref={**ref,'new_research_mec_sha256':rebuilt['mec']['sha256'],
              'new_research_role_hypotheses_sha256':p1['sha256']}
        p1s1=select_portfolio(p1['prediction'],p1tickets,source_ref=pref,krs_utility=a['krs_utility'],
                              excluded_runner_ids=excluded,
                              day_remaining_yen=remaining[arm]['P1S1'])
        cells['P1S0']={'tickets':p1tickets,'prediction':p1['prediction'],'role_hypotheses':p1,
                       'research_mec':rebuilt,'immutable_source_ref':pref}
        cells['P1S1']={'tickets':p1s1['selected_tickets'],'prediction':p1['prediction'],'selection':p1s1}
        for cell in cells.values():
            cell['display']={'classification':'SEPARATE_RESEARCH_NOT_ORIGINAL_VENUE_CANONICAL',
                             'original_prediction_sha256':p['sha256'],
                             'tree':render_ticket_tree({'static_prediction':{'ranking':cell['prediction']['ranking']},
                                 'final_ticket':{'tickets':cell['tickets'],'no_bet':not cell['tickets']},
                                 'capital_policy_decision':{'decision':'PAPER'}})}
        diagnostic_ranking=[h for h in p['ranking'] if h not in excluded]
        views[arm]={'cells':cells,'P0S1_NO_KRS':no_krs,
                    'TOP4_BOX_DIAGNOSTIC':canonical_tickets(
                        [{'bet_type':'EXACTA','selection':list(map(int,x)),'stake':100}
                         for x in permutations(diagnostic_ranking[:4],2)]+
                        [{'bet_type':'TRIO','selection':list(map(int,x)),'stake':100}
                         for x in combinations(diagnostic_ranking[:4],3)])}
    return views


def _finance(tickets,result):
    return settle_ticket_list(tickets,result,require_resolved_refunds=True)


def _summary(finances,denominator,*,planned_investment=None):
    known=len(finances)==denominator and bool(finances) and all(f['status']=='SETTLED' and f['return'] is not None for f in finances)
    observed_investment=sum(f['investment'] for f in finances)
    investment=observed_investment if planned_investment is None else planned_investment
    ret=sum(f['return'] for f in finances) if known else None
    cash=POLICY['initial_research_cash_yen'];balance=cash;peak=cash;dd=0
    if known:
        for f in finances:
            balance+=f['profit_loss'];peak=max(peak,balance);dd=max(dd,peak-balance)
    max_return=max((f['return'] for f in finances),default=0) if known else None
    max_race=max(finances,key=lambda f:f['return']) if known else None
    return {'fixed_denominator':denominator,'resolved':sum(f['status']=='SETTLED' for f in finances),
            'missing_or_held':denominator-sum(f['status']=='SETTLED' for f in finances),
            'observed_partial_return_not_full_day':sum(f['return'] for f in finances if f['return'] is not None),
            'observed_investment':observed_investment,
            'investment':investment,'return':ret,'refund':sum(f['refund'] for f in finances) if known else None,
            'profit_loss':ret-investment if known else None,'pfs':100*ret/investment if known and investment else None,
            'participating_races':sum(f['investment']>0 for f in finances),'participation_rate':sum(f['investment']>0 for f in finances)/denominator,
            'unused_of_research_day_cap':max(0,POLICY['day_cap_yen']-investment),
            'research_day_cap_exceeded_by_original_S0_reference':investment>POLICY['day_cap_yen'],
            'common_initial_research_cash_yen':cash,'final_research_balance':balance if known else None,
            'maximum_drawdown_yen':dd if known else None,'maximum_return_yen':max_return,
            'profit_loss_excluding_largest_return':ret-max_return-investment if known else None,
            'profit_loss_excluding_largest_return_race':ret-max_return-investment+max_race['investment'] if known else None,
            'performance_pass':False,'actual_purchase':False}


def _trace(frozen,audits,numeric,result):
    from runtime.local_krs_bridge_candidate import _structure_upper_cluster
    baseline=frozen['feature_pack']['baseline'];actual=list(map(str,result['official_result']['top3']))
    sensitivities={}
    for role,key,floor in (('W','w_score',1),('P2','p2_score',2),('P3','p3_score',3)):
        rows=baseline['runner_scores'];original,_=_structure_upper_cluster(rows,key,min_active=floor)
        max_delta=0;max_change=0
        for i in range(len(rows)):
            for sign in (-1,1):
                changed=copy.deepcopy(rows);changed[i][key]+=sign*1e-6
                chosen,_=_structure_upper_cluster(changed,key,min_active=floor)
                max_delta=max(max_delta,abs(len(chosen)-len(original)))
                max_change=max(max_change,len(set(chosen)^set(original)))
        sensitivities[role]={'absolute_score_perturbation':1e-6,'max_width_change':max_delta,
                              'max_role_membership_symmetric_difference':max_change,
                              'unstable_in_tested_neighborhood':bool(max_change)}
    arms={}
    for arm,a in audits.items():
        pred=frozen['predictions'][arm];roles=pred['role_columns'];loss=[]
        for role,rid in zip(('W','P2','P3'),actual):
            initial=rid in baseline[role];final=role in roles[rid]
            loss.append({'actual_role':role,'runner_id':rid,'initial_structure_has_role':initial,
                         'owner_has_role':final,'owner_rank':pred['rankings_by_role'][role].index(rid)+1,
                         'first_observed_loss':'STRUCTURE_CLUSTER' if not initial and not final else
                             'CONDITIONAL_OWNER_REORDER_WITH_INHERITED_WIDTH' if initial and not final else None,
                         'causal_status':'OBSERVED_STAGE_MEMBERSHIP_NOT_A_CAUSAL_EFFECT_ESTIMATE'})
        pair=a['semantic_request']['pair_dispositions'];third=a['semantic_request']['third_dispositions']
        model=frozen['models'][arm]
        coefficient_use=[]
        for depth,fit in enumerate(model['fits']):
            coefficient_use.append({'stage':('W','P2','P3')[depth],
                'features':[{ 'name':k,'coefficient':w,'training_scale':s,
                              'observed_runner_count':sum(frozen['feature_pack']['runners'][rid].get(k) is not None for rid in roles)
                              if k.startswith('INDEX:') or k.startswith('STAGE:') else None,
                              'effective_when_observed':bool(w and s)}
                             for k,w,s in zip(fit['feature_names'],fit['coefficients'],fit['training_scales'])]})
        arms[arm]={'model_sha256':pred['model_sha256'],'prediction_sha256':pred['sha256'],
            'initial_structure_width':{r:len(baseline[r]) for r in ('W','P2','P3')},
            'owner_inherits_same_width':pred['role_widths'],
            'semantic_pair_count':len(pair),'semantic_third_count':len(third),
            'all_pairs_protected':all(x['status']=='PROTECT' for x in pair),
            'all_thirds_protected':all(x['status']=='PROTECT' for x in third),
            'first_purchase_expansion':'OBSERVED_PAPER_WRAPPER_CARTESIAN_ROLE_TO_PROTECT',
            'original_wrapper_source_bytes':'UNKNOWN_NOT_PRESENT_IN_ORIGINAL_ARCHIVE',
            'reconstructed_S0_ticket_set_exact_match':True,
            'candidate_joint_values_used_by_S0_purchase_selector':False,
            'krs_utility_in_original_capitalized_selection':False,
            'original_krs_argument_not_authority_to_purchase':True,
            'semantic_only_closure_is_not_itself_purchase':True,
            'stake_rule':'100_YEN_EACH_REQUIRED_MEC_TICKET_NOT_BUDGET_FILL',
            'capital_decision':a['capital']['decision'],
            'actual_investment':0,'actual_role_loss_trace':loss,'coefficient_consumption':coefficient_use,
            'numerical_terminal_counts':{s:sum(c['terminal_status']==s for row in numeric['runners']
                                             for c in row['canonical_components'].values())
                                         for s in ('CALCULATED','RULED_NEUTRAL')}}
    return {'status':'OBSERVED_ARTIFACT_TRACE_WITH_EXPLICIT_UNKNOWN_WRAPPER','arms':arms,
            'cluster_sensitivity':sensitivities,'prohibited_claims':['29_INDICES_ALL_EFFECTIVE','ONE_DAY_QUALITY_PASS']}


def replay(args):
    out=private_directory(args.output);helpers=existing_functions(args.analysis_helper)
    protocol=read(args.equal_budget);_check_sha(protocol)
    utility=read(args.utility);_check_sha(utility)
    archive_hash=file_sha(args.archive_zip)
    if archive_hash!=protocol['original_archive_sha256'] or utility['source_archive_sha256']!=archive_hash:
        raise ValueError('ORIGINAL_ARCHIVE_OR_UTILITY_BINDING')
    uarms={(x['race_no'],x['owner']):x for x in utility['arms']}
    rows=[];holds=[];planned=[]
    remaining={a:{k:POLICY['day_cap_yen'] for k in ('P0S1','P1S1','P0S1_NO_KRS')} for a in ARMS}
    for budget in protocol['races']:
        no=budget['race_no'];rd=private_directory(out/f'R{no:02}')
        frozen=read(args.archive/f'frozen/R{no:02}/comparison.freeze.json')
        obs=read(args.archive/f'frozen/R{no:02}/source-observation.json')
        numeric=read(args.archive/f'frozen/R{no:02}/numerical.json')
        audits={a:read(args.archive/f'paper/R{no:02}/{a}/downstream.audit.json') for a in ARMS}
        helpers['require_frozen_bindings'](frozen,numeric,audits,budget)
        views=build_views(frozen,audits,obs,remaining)
        save_json(rd/'outcome-blind-research-views.json',views)
        planned.append({'race_no':no,'arms':{arm:{
            **{cell:sum(t['stake'] for t in views[arm]['cells'][cell]['tickets']) for cell in CELLS},
            'original':sum(t['stake'] for t in views[arm]['cells']['P0S0']['tickets']),
            'equal_fixed_integer':sum(t['stake'] for t in helpers['expand'](budget['arms'][arm]['fixed_integer_reference_groups'])),
            'utility_separate':sum(t['stake'] for t in uarms[(no,arm)]['research_tickets']),
            'P0S1_NO_KRS':views[arm]['P0S1_NO_KRS']['used_budget_yen'],
            'TOP4_BOX_DIAGNOSTIC':sum(t['stake'] for t in views[arm]['TOP4_BOX_DIAGNOSTIC'])}
            for arm in ARMS}})
        for arm in ARMS:
            for k in remaining[arm]:
                s=views[arm]['cells'][k]['selection'] if k in ('P0S1','P1S1') else views[arm][k]
                remaining[arm][k]=s['day_budget_remaining_yen']
        # Labels become accessible only AFTER the complete prediction/selection
        # outputs have been saved. A missing official witness stays in denominator.
        try:
            raw=gzip.decompress((args.results/f'R{no:02}.html.gz').read_bytes())
            receipt=read(args.results/f'R{no:02}.receipt.json')
            result=parse_result(raw,obs['race'],obs['facts'],receipt,race_id=frozen['race_id'])
            helpers['verify_observation'](frozen,obs,result,raw)
        except (FileNotFoundError,ValueError) as exc:
            holds.append({'race_no':no,'status':'HOLD_OFFICIAL_RESULT_WITNESS','reason':str(exc)})
            continue
        save_json(rd/'official-result-R2.json',result)
        primary=helpers['evaluate_owner_forward_comparison'](frozen,result)
        entry={'race_no':no,'race_id':frozen['race_id'],'official_result_sha256':result['sha256'],
               'official_source':{k:result[k] for k in ('source_url','source_raw_sha256','observed_at')},
               'top3':result['official_result']['top3'],'refund_ids':result['official_result']['refunded_runner_ids'],
               'original_prediction_metrics':primary,'arms':{},'trace':_trace(frozen,audits,numeric,result)}
        for arm in ARMS:
            v=views[arm];a=audits[arm];pred=frozen['predictions'][arm];actual=list(map(str,result['official_result']['top3']))
            original=_finance(v['cells']['P0S0']['tickets'],result)
            ref=_finance(helpers['expand'](budget['arms'][arm]['fixed_integer_reference_groups']),result)
            analytic=helpers['analytic_finance'](original,budget['arms'][arm])
            if result['official_result']['refunded_runner_ids']:
                # Same pre-fixed SRS portfolios, but variance must include many
                # refunded tickets; the old single-winning-ticket shortcut cannot.
                for bt,bucket in analytic['matched_race_and_bet_type_integer_portfolio_ensemble']['by_bet_type'].items():
                    ts=[t for t in v['cells']['P0S0']['tickets'] if t['bet_type']==bt]
                    m=len(ts);n=Fraction(budget['arms'][arm]['matched_type_inclusion_probabilities'][bt]['numerator'],
                                       budget['arms'][arm]['matched_type_inclusion_probabilities'][bt]['denominator'])*m
                    vals=[Fraction(str(_finance([t],result)['return'])) for t in ts]
                    variance=n*(m-n)/(m*(m-1))*(sum(y*y for y in vals)-sum(vals)**2/m) if m>1 else Fraction(0)
                    bucket['return_variance']=helpers['qnumber'](variance)
                    bucket['variance_method']='FINITE_POPULATION_SRS_INCLUDING_EXPLICIT_REFUNDS'
            cf=uarms[(no,arm)]
            if cf['original_tickets']!=canonical_tickets(v['cells']['P0S0']['tickets']) or cf['comparison_freeze_sha256']!=frozen['sha256']:
                raise ValueError('UTILITY_ORIGINAL_BINDING_CHANGED')
            finances={k:_finance(c['tickets'],result) for k,c in v['cells'].items()}
            no_krs=_finance(v['P0S1_NO_KRS']['selected_tickets'],result)
            top4=_finance(v['TOP4_BOX_DIAGNOSTIC'],result)
            uf=_finance(cf['research_tickets'],result)
            utility_diff=helpers['build_ticket_attribution'](
                {'BASELINE':{'ticket_tree':{'reflattened_tickets':cf['original_tickets']}},
                 'CANDIDATE':{'ticket_tree':{'reflattened_tickets':cf['research_tickets']}}},
                result,{'BASELINE':original,'CANDIDATE':uf},_finance)
            decisions={}
            for cell,c in v['cells'].items():
                ts=c['tickets'];ps=c['prediction'];o=v['cells']['P0S0']['tickets']
                target_keys={('EXACTA',tuple(result['official_result']['top3'][:2])),
                             ('TRIO',tuple(sorted(result['official_result']['top3']))),
                             ('TRIFECTA',tuple(result['official_result']['top3']))}
                key=lambda t:(t['bet_type'],tuple(t['selection']))
                oldkeys={key(t) for t in o};newkeys={key(t) for t in ts}
                decisions[cell]={'lost_original_winning_tickets':[list(k) for k in sorted((oldkeys-newkeys)&target_keys)],
                    'rescued_winning_tickets':[list(k) for k in sorted((newkeys-oldkeys)&target_keys)],
                    'role_capture':{r:r in ps['role_columns'][h] for r,h in zip(('W','P2','P3'),actual)},
                    'tier_finance':{tier:_finance([t for t in ts if any(x['selected'] and x['selection_detail']['tier']==tier
                        and canonical_tickets([x['original_ticket']])[0]['selection']==t['selection']
                        and x['original_ticket']['bet_type']==t['bet_type'] for x in c.get('selection',{}).get('candidate_ledger',[]))],result)
                        for tier in ('CORE','PROTECTION')} if 'selection' in c else None}
            review_view={'race_id':frozen['race_id'],'sha256':sha(v['cells']['P0S0']),
                         'final_prediction_package':{'roles':pred['role_columns'],'ranking':pred['ranking']},
                         'static_prediction':{'ranking':pred['ranking']},'krs_prediction_utility':a['krs_utility'],
                         'minimum_efficient_coverage':a['mec'],
                         'final_ticket':{'tickets':v['cells']['P0S0']['tickets'],'total_investment':original['investment']}}
            sr={**original,'status':'COMPLETE' if original['status']=='SETTLED' else 'PENDING'}
            review=helpers['build_post_result_review']({'race_id':frozen['race_id'],'official_result':result['official_result'],
                  'frozen_prediction_ref':{'final_status':'UNSIGNED_SHADOW_NOT_FORMAL'},'settlement':sr},review_view)
            learning=helpers['build_learning_state'](review,effective_time=result['observed_at'])
            entry['arms'][arm]={'original':original,'equal_fixed_integer':ref,'equal_analytic':analytic,
                'utility_separate':uf,'utility_vs_original':utility_diff,'experiments':finances,
                'P0S1_NO_KRS':no_krs,'TOP4_BOX_DIAGNOSTIC':top4,'selection_losses_and_rescues':decisions,
                'all_runner_outcome_join':[{'runner_id':h,'actual_rank':next((r['rank'] for r in result['finish_rows'] if r['runner_id']==h),None),
                    'original_rank':pred['ranking'].index(h)+1,'original_roles':rs,
                    'direct_history_unknown':frozen['feature_pack']['runners'][h].get('STAGE:direct_finish') is None,
                    'p1_review':next(x for x in v['cells']['P1S0']['role_hypotheses']['all_runner_review'] if x['runner_id']==h)}
                    for h,rs in pred['role_columns'].items()],
                'post_result_review':review,'learning_state_context_only':learning,
                'learning_consumed_into_model_or_policy':False}
        entry['original_ticket_attribution']=helpers['build_ticket_attribution'](
            audits,result,{a:entry['arms'][a]['original'] for a in ARMS},_finance)
        entry['sha256']=sha(entry);save_json(rd/'settlement-and-analysis-R2.json',entry);rows.append(entry)
    summary={'classification':'OFFICIAL_RECONCILED_RESULT_REVISION_AND_POSTHOC_POLICY_DEVELOPMENT',
             'created_at':now().isoformat(),'fixed_denominator':12,'observed_races':len(rows),'holds':holds,
             'planned_race_investments_including_missing_results':planned,
             'original_archive_sha256':archive_hash,'original_archive_sha256_after':file_sha(args.archive_zip),
             'equal_budget_protocol_sha256':protocol['sha256'],'utility_sha256':utility['sha256'],
             'execution_head':head(),'code_sha256':code_pins(),'policy':POLICY,'policy_sha256':sha(POLICY),
             'arms':{},'races':rows,'formal_quality_eligible':0,'production_authority':False,
             'signed_final_count':0,'actual_purchase_finance':'UNKNOWN_NOT_INFERRED_FROM_PAPER',
             'performance_pass':False,'private_storage_required':True,'public_redistribution_authorized':False}
    for arm in ARMS:
        values=[r['arms'][arm] for r in rows]
        def total(key):return sum(p['arms'][arm][key] for p in planned)
        summary['arms'][arm]={'original':_summary([v['original'] for v in values],12,planned_investment=total('original')),
             'user_reported_10_race_scope':_summary([r['arms'][arm]['original'] for r in rows if r['race_no'] not in (1,4)],10,
                 planned_investment=sum(p['arms'][arm]['original'] for p in planned if p['race_no'] not in (1,4))),
             'equal_fixed_integer':_summary([v['equal_fixed_integer'] for v in values],12,planned_investment=total('equal_fixed_integer')),
             'utility_separate':_summary([v['utility_separate'] for v in values],12,planned_investment=total('utility_separate')),
             **{k:_summary([v['experiments'][k] for v in values],12,planned_investment=total(k)) for k in CELLS},
             'P0S1_NO_KRS':_summary([v['P0S1_NO_KRS'] for v in values],12,planned_investment=total('P0S1_NO_KRS')),
             'TOP4_BOX_DIAGNOSTIC':_summary([v['TOP4_BOX_DIAGNOSTIC'] for v in values],12,planned_investment=total('TOP4_BOX_DIAGNOSTIC'))}
    if summary['original_archive_sha256_after']!=archive_hash:raise ValueError('ORIGINAL_ARCHIVE_CHANGED')
    save_json(out/'result-revision-and-policy-replay.json',sealed(summary))
    print(json.dumps({'output':str(out),'observed_races':len(rows),'holds':len(holds),'arms':summary['arms']},ensure_ascii=False))


def register(args):
    frozen=read(args.model_bundle);_check_sha(frozen)
    for model in frozen['models'].values():_check_sha(model)
    ledger=private_directory(args.ledger)
    if list(ledger.iterdir()):raise ValueError('NEW_REGISTRATION_REQUIRES_NEW_EMPTY_PRIVATE_LEDGER')
    registration=sealed({'schema':'URW-SELECTION-RESEARCH-PREREGISTRATION-v1','registered_at':now().isoformat(),
        'cohort':'NEXT_CONTIGUOUS_ELIGIBLE_URW_RACES_AFTER_REGISTRATION_EXCLUDE_20261021',
        'minimum_races':60,'minimum_dates':5,'policy':POLICY,'policy_sha256':sha(POLICY),
        'models':{a:frozen['models'][a]['sha256'] for a in ARMS},'canonical_ledger_path':str(ledger.resolve()),
        'code_sha256':code_pins(),'registered_head':head(),'existing_owner_protocol_unchanged':frozen['protocol'],
        'evaluation':['RANK_ROLE_PAIR_THIRD','SAME_BUDGET_FINANCE','TICKET_CAPTURE_EFFICIENCY',
                      'CORE_PROTECTION','KRS_RESCUE_AND_HARM','PARTICIPATION_AND_OPPORTUNITY_COST',
                      'DAILY_DRAWDOWN','REMOVE_MAX_PAYOUT_ROBUSTNESS','TOP4_DIAGNOSTIC_INCREMENT'],
        'selection_primary':{'contrast':'P0S1_MINUS_SAME_OWNER_TOP4_BOX_NET_PROFIT',
            'budget_basis':'SAME_AVAILABLE_RESEARCH_CAP_UNSPENT_CASH_RETAINED_NOT_EQUAL_SPEND',
            'arms':'BASELINE_AND_CANDIDATE_SEPARATE_NO_BEST_ARM_PER_RACE',
            'interval':'EXISTING_DATE_CLUSTER_BOOTSTRAP_10000_SEED_20261020',
            'review_threshold':'LOWER_95_PERCENT_BOUND_STRICTLY_ABOVE_ZERO',
            'guardrails':'REPORT_ROLE_CAPTURE_HIT_LOSS_PARTICIPATION_PROTECTION_AND_MAX_RETURN_ROBUSTNESS',
            'S0_comparison':'UNCAPPED_ORIGINAL_REFERENCE_NOT_FAIR_SAME_SPEND_PERFORMANCE_PROOF'},
        'fixed_denominator':'ALL_ELIGIBLE_ATTEMPTS_INCLUDE_FAILURES_HOLDS_AND_NO_BET',
        'model_or_policy_changes':'NEW_REGISTRATION_AND_SEPARATE_COHORT',
        'performance_pass':'NEVER_FROM_DEVELOPMENT_DAY_REQUIRES_FULL_COHORT_REVIEW',
        'formal_quality_credit':0,'automatic_production_promotion':False,'actual_purchase':False,
        'private_storage_required':True,'public_redistribution_authorized':False})
    private_directory(args.output.parent);save_json(args.output,registration)
    save_json(ledger/'initialization.json',sealed({'registration_sha256':registration['sha256'],
             'canonical_ledger_path':str(ledger.resolve())}))
    print(json.dumps({'registration':str(args.output),'sha256':registration['sha256']}))


def register_day(args):
    """Bind the existing official whole-day plan before its first cutoff."""
    from runtime.local_reference_day import verify_plan
    reg=read(args.registration);_check_sha(reg)
    raw=args.day_plan.read_bytes()
    plan=json.loads(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw)
    verify_plan(plan,plan['race_date'])
    if (reg['code_sha256']!=code_pins() or reg['policy']!=POLICY
            or plan['race_date']<=POLICY['development_date_excluded_from_future_quality']
            or min(datetime.fromisoformat(r['fields']['prediction_cutoff']) for r in plan['races'])<=now()):
        raise ValueError('FORWARD_DAY_PLAN_NOT_PREREGISTERED_BEFORE_FIRST_CUTOFF')
    ledger=Path(reg['canonical_ledger_path'])
    init=read(ledger/'initialization.json');_check_sha(init)
    if init['registration_sha256']!=reg['sha256']:raise ValueError('FORWARD_LEDGER_INITIALIZATION')
    record=sealed({'registration_sha256':reg['sha256'],'registered_at':now().isoformat(),
                   'existing_official_day_plan':plan,'source_plan_file_sha256':file_sha(args.day_plan),
                   'fixed_denominator':len(plan['races']),'production_authority':False})
    save_json(ledger/f'day-{plan["race_date"]}.json',record)
    print(json.dumps({'registered_day':plan['race_date'],'fixed_denominator':record['fixed_denominator']}))


def cohort_status(args):
    """Read planned races as well as invoked ones; never select successes only."""
    reg=read(args.registration);_check_sha(reg);ledger=Path(reg['canonical_ledger_path']);events=[];parent=None
    for path in sorted(ledger.glob('event-*.json')):
        e=read(path);_check_sha(e)
        if e['registration_sha256']!=reg['sha256'] or e['parent_event_sha256']!=parent or e['sequence']!=len(events)+1:
            raise ValueError('FORWARD_LEDGER_CHAIN')
        events.append(e);parent=e['sha256']
    rows=[]
    for path in sorted(ledger.glob('day-*.json')):
        day=read(path);_check_sha(day)
        if day['registration_sha256']!=reg['sha256']:raise ValueError('FORWARD_DAY_PLAN_REGISTRATION')
        for race in day['existing_official_day_plan']['races']:
            f=race['fields'];es=[e for e in events if e['race_date']==f['race_date'] and e['race_no']==f['race_no']]
            state=es[-1]['status'] if es else ('HOLD_NOT_INVOKED' if datetime.fromisoformat(f['prediction_cutoff'])<=now() else 'PENDING_PRE_CUTOFF')
            rows.append({'race_date':f['race_date'],'race_no':f['race_no'],'status':state})
    value=sealed({'registration_sha256':reg['sha256'],'planned_fixed_denominator':len(rows),'races':rows,
                  'performance_pass':False,'formal_quality_credit':0})
    private_directory(args.output.parent);save_json(args.output,value)
    print(json.dumps({'cohort_status':str(args.output),'fixed_denominator':len(rows)}))


def freeze(args):
    import fcntl
    reg=read(args.registration);_check_sha(reg)
    if reg['policy']!=POLICY or reg['code_sha256']!=code_pins():raise ValueError('PREREGISTERED_CODE_OR_POLICY_CHANGED')
    if str(args.ledger.resolve())!=reg['canonical_ledger_path']:raise ValueError('FORWARD_CANONICAL_LEDGER_REQUIRED')
    init=read(args.ledger/'initialization.json');_check_sha(init)
    if init['registration_sha256']!=reg['sha256']:raise ValueError('FORWARD_LEDGER_INITIALIZATION')
    bundle=read(args.input_bundle)
    if set(bundle)!={'frozen','audits','observation'}:raise ValueError('FORWARD_BUNDLE_KEYS_NO_RESULTS_ALLOWED')
    frozen=bundle['frozen'];pack=frozen['feature_pack'];obs=bundle['observation']
    started=now();registered=datetime.fromisoformat(reg['registered_at'])
    private_directory(args.ledger);private_directory(args.output)
    with private_lock(args.ledger/'ledger.lock') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        events=[];parent=None
        for path in sorted(args.ledger.glob('event-*.json')):
            event=read(path);_check_sha(event)
            if (event['registration_sha256']!=reg['sha256'] or event['parent_event_sha256']!=parent
                    or event['sequence']!=len(events)+1):raise ValueError('FORWARD_LEDGER_CHAIN')
            events.append(event);parent=event['sha256']
        race_no=obs['race']['race_no']
        if any(x['race_date']==pack['race_date'] and x['race_no']==race_no for x in events):
            raise ValueError('FORWARD_DUPLICATE_RACE_ATTEMPT')
        remaining={a:{k:POLICY['day_cap_yen'] for k in ('P0S1','P1S1','P0S1_NO_KRS')} for a in ARMS}
        for row in events:
            if row['race_date']==pack['race_date'] and row.get('remaining') is not None:remaining=row['remaining']
        def append_event(value):
            value=sealed({**value,'registration_sha256':reg['sha256'],
                          'parent_event_sha256':events[-1]['sha256'] if events else None,
                          'sequence':len(events)+1})
            save_json(args.ledger/f'event-{len(events)+1:04d}.json',value)
            events.append(value)
            return value
        attempt={'race_id':frozen['race_id'],'race_date':pack['race_date'],'race_no':race_no,
                 'attempted_at':started.isoformat()}
        day_error=None
        try:
            day=read(args.ledger/f'day-{pack["race_date"]}.json');_check_sha(day)
            if day['registration_sha256']!=reg['sha256']:raise ValueError('FORWARD_DAY_PLAN_REGISTRATION')
            planned=next(r['fields'] for r in day['existing_official_day_plan']['races'] if r['fields']['race_no']==race_no)
            post=datetime.fromisoformat(planned['scheduled_post_at'])
            if post.tzinfo is None:raise ValueError('FORWARD_PLAN_TIMEZONE')
            attempt['reserved_scheduled_post_at']=post.isoformat()
        except (ValueError,KeyError,FileNotFoundError,StopIteration) as exc:
            day_error=exc
        reserved=copy.deepcopy(remaining)
        for arm in ARMS:
            for cell in reserved[arm]:reserved[arm][cell]-=min(POLICY['race_cap_yen'],reserved[arm][cell])
        # Persist BEFORE producing any Freeze. A killed process keeps its whole
        # reservation and cannot retry the race or silently reset the day cap.
        reservation=append_event({**attempt,'status':'ATTEMPT_RESERVED','remaining':reserved})
        attempt['reservation_sha256']=reservation['sha256']
        try:
            cutoff=datetime.fromisoformat(frozen['prediction_cutoff'])
            if day_error is not None:raise day_error
            if any(planned[k]!=pack[k] for k in ('venue_id','race_date','prediction_cutoff','scheduled_post_at')):
                raise ValueError('FORWARD_PLAN_RACE_CONTEXT')
            def no_labels(value):
                if isinstance(value,dict):
                    if set(value)&{'official_result','finish_order','payouts','settlement','actual_top3','result_labels'}:
                        raise ValueError('FORWARD_RESULT_LABELS_FORBIDDEN')
                    for x in value.values():no_labels(x)
                elif isinstance(value,list):
                    for x in value:no_labels(x)
            no_labels(bundle)
            if (pack['race_date']<=POLICY['development_date_excluded_from_future_quality'] or
                    not registered<=datetime.fromisoformat(frozen['frozen_at'])<=started<cutoff
                    or not datetime.fromisoformat(pack['source_observed_at'])<=started
                    or {a:frozen['models'][a]['sha256'] for a in ARMS}!=reg['models']):
                raise ValueError('FORWARD_CLOCK_MODEL_OR_COHORT_HOLD')
            _check_sha(pack)
            if obs['source']['raw_sha256']!=pack['source_snapshot_sha256']:raise ValueError('FORWARD_SOURCE_BINDING')
            verify_bundle(frozen,bundle['audits'],obs,forward=True)
            post=datetime.fromisoformat(frozen['scheduled_post_at'])
            previous_posts=[datetime.fromisoformat(e.get('validated_scheduled_post_at') or e['reserved_scheduled_post_at'])
                            for e in events if e['sha256']!=reservation['sha256']
                            and (e.get('validated_scheduled_post_at') or e.get('reserved_scheduled_post_at'))]
            if previous_posts and post<=max(previous_posts):
                raise ValueError('FORWARD_RACE_ORDER_OR_OLD_INPUT')
            attempt['validated_scheduled_post_at']=frozen['scheduled_post_at']
            views=build_views(frozen,bundle['audits'],obs,remaining)
            completed=now()
            if completed>=cutoff:raise ValueError('FORWARD_COMPLETED_AFTER_CUTOFF')
            for arm in ARMS:
                for k in remaining[arm]:
                    s=views[arm]['cells'][k]['selection'] if k in ('P0S1','P1S1') else views[arm][k]
                    remaining[arm][k]=s['day_budget_remaining_yen']
            artifact=sealed({'classification':'FORWARD_UNSIGNED_SELECTION_RESEARCH_NOT_FINAL',
                'race_id':frozen['race_id'],'frozen_at':completed.isoformat(),
                'prediction_cutoff':frozen['prediction_cutoff'],'registration_sha256':reg['sha256'],
                'input_bundle_sha256':sha(bundle),'views':views,'remaining':remaining,
                'independent_timestamp':'PENDING_EXTERNAL_ANCHOR_NOT_SELF_CERTIFIED',
                'formal_quality_credit':0,'production_authority':False,'signed_final_claim':False,
                'actual_purchase':False,'private_storage_required':True,'public_redistribution_authorized':False})
            save_json(args.output/'research-selection-freeze.json',artifact)
            attempt.update(status='FROZEN_PENDING_INDEPENDENT_ANCHOR',artifact_sha256=artifact['sha256'],remaining=remaining)
        except Exception as exc:
            attempt.update(status='HOLD_RETAINED_IN_DENOMINATOR',reason=str(exc),remaining=remaining)
            raise
        finally:
            # Every admitted attempt, including failed/late Freeze, is retained.
            # Private immutable events are the ledger; no mutable budget index.
            append_event({**attempt,'event_type':'COMPLETION'})
    print(json.dumps({'freeze':str(args.output/'research-selection-freeze.json'),'status':attempt['status']}))


def main():
    os.umask(0o077)
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('replay')
    for flag in ('archive','archive-zip','equal-budget','utility','analysis-helper','results','output'):
        p.add_argument('--'+flag,type=Path,required=True)
    p.set_defaults(run=replay)
    p=sub.add_parser('register');p.add_argument('--model-bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True);p.set_defaults(run=register)
    p=sub.add_parser('register-day');p.add_argument('--registration',type=Path,required=True);p.add_argument('--day-plan',type=Path,required=True);p.set_defaults(run=register_day)
    p=sub.add_parser('cohort-status');p.add_argument('--registration',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.set_defaults(run=cohort_status)
    p=sub.add_parser('freeze')
    for flag in ('input-bundle','registration','ledger','output'):p.add_argument('--'+flag,type=Path,required=True)
    p.set_defaults(run=freeze)
    a=parser.parse_args();a.run(a)


if __name__=='__main__':main()

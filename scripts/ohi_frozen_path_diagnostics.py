"""Read-only OHI frozen Prediction->Role->Ticket diagnostics.

Labels are evaluation-only private inputs. No Owner, Engine, fit, selection or
ticket construction is executed. No result/price is sent to an input pipeline.
"""
from __future__ import annotations
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from runtime.ohi_single_race_research import readback
from runtime.local_krs_bridge_candidate import _structure_upper_cluster

OWNERS = ('BASELINE', 'OHI_FIXED_CANDIDATE')
ENGINE_SHA = '9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421'


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(',', ':')).encode()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def diff_paths(a, b, prefix=''):
    if type(a) is not type(b): return [prefix]
    if isinstance(a, dict):
        return [p for k in sorted(set(a)|set(b)) for p in
                ([prefix+'/'+k] if k not in a or k not in b else diff_paths(a[k], b[k], prefix+'/'+k))]
    if isinstance(a, list):
        if len(a) != len(b): return [prefix+'/length']
        return [p for i,(x,y) in enumerate(zip(a,b)) for p in diff_paths(x,y,prefix+'/'+str(i))]
    return [] if a == b else [prefix]


def roles(pred): return pred.get('role_columns') or pred['roles']
def role_ids(pred, column): return [i for i in pred['ranking'] if column in roles(pred)[i]]


def top3_labels(labels):
    """Accept a private diagnostic list or independently collected full results."""
    rows=labels.get('races',{}) if labels else {}
    if isinstance(rows,list):
        out={}
        for row in rows:
            number=int(row['race_no'])
            if number in out:raise ValueError('LABEL_DUPLICATE_RACE')
            out[number]=row
        return out
    if not isinstance(rows,dict):raise ValueError('LABEL_RACES_REQUIRED')
    out={}
    for number,row in rows.items():
        if int(number) in out:raise ValueError('LABEL_DUPLICATE_RACE')
        groups=[];slots=0
        for group in row['finish_groups']:
            groups.append(list(map(str,group)));slots+=len(group)
            if slots>=3:break
        out[int(number)]={**row,'rank_groups':groups}
    return out


def verify_label_identity(label,race):
    """A matching runner number alone cannot bind an outcome to a Race."""
    if not label:return
    if label.get('provider_race_id')!=race['provider_race_id']:
        raise ValueError('LABEL_PROVIDER_RACE_IDENTITY')
    for key in ('race_no','race_date','venue_id'):
        if key in label and label[key]!=race[key]:
            raise ValueError('LABEL_RACE_CONTEXT:'+key)
    if 'source_url' in label and label['source_url']!='https://www.nankankeiba.com/result/'+race['provider_race_id']+'.do':
        raise ValueError('LABEL_RESULT_URL_IDENTITY')


def cluster_sensitivity(rows,key,floor):
    selected,_=_structure_upper_cluster(rows,key,min_active=floor)
    changes=[]
    # One last-place unit of the stored six-decimal bridge scores. Diagnostic
    # finite difference only, never a new selection width/tolerance policy.
    for i,row in enumerate(rows):
        for sign in (-1,1):
            altered=copy.deepcopy(rows);altered[i][key]+=sign*0.000001
            chosen,_=_structure_upper_cluster(altered,key,min_active=floor)
            if set(chosen)!=set(selected):changes.append({'runner_id':row['runner_id'],
                'score_delta':sign*0.000001,'original_width':len(selected),'perturbed_width':len(chosen),
                'removed':sorted(set(selected)-set(chosen),key=int),'added':sorted(set(chosen)-set(selected),key=int)})
    return changes


def numeric_rank(mapping, runner):
    order=sorted(mapping, key=lambda i:(-mapping[i],int(i)))
    return order.index(runner)+1


def ticket_identity(t):
    kind=t['bet_type'];s=tuple(map(str,t['selection']))
    return kind,tuple(sorted(s,key=int)) if kind=='TRIO' else s


def matching_tickets(tickets, groups):
    h=groups[0][0];seconds=groups[1]
    trio=set(i for g in groups for i in g)
    exact=tuple(g[0] for g in groups) if len(groups)==3 and all(len(g)==1 for g in groups) else None
    matched={'EXACTA':[], 'TRIO':[], 'TRIFECTA':[]}
    for t in tickets:
        kind,s=ticket_identity(t)
        hit=(kind=='EXACTA' and len(s)==2 and s[0]==h and s[1] in seconds)
        hit=hit or (kind=='TRIO' and len(trio)==3 and set(s)==trio)
        hit=hit or (kind=='TRIFECTA' and exact is not None and s==exact)
        if hit:matched[kind].append(copy.deepcopy(t))
    return matched


def first_path_loss(pred, portfolio, groups):
    """First observable loss of required role path, not a causal ability claim."""
    h=groups[0][0];seconds=groups[1];r=roles(pred)
    if 'W' not in r[h]: return 'W_ROLE_BOUNDARY'
    if not all('P2' in r[i] for i in seconds): return 'P2_ROLE_BOUNDARY'
    independent_third=len(groups)==3 and len(groups[2])==1
    if independent_third and 'P3' not in r[groups[2][0]]:return 'P3_ROLE_BOUNDARY'
    pairset={(str(p['head']),str(p['second'])) for p in portfolio['semantic_request']['pair_dispositions']}
    if not all((h,s) in pairset for s in seconds):return 'PAIR_PROJECTION'
    if independent_third:
        thirdset={(str(t['head']),str(t['second']),str(t['third'])) for t in portfolio['semantic_request']['third_dispositions']}
        if (h,seconds[0],groups[2][0]) not in thirdset:return 'THIRD_PROJECTION'
    mec=matching_tickets(portfolio['mec']['tickets'],groups)
    if not any(mec.values()):return 'MEC_TICKET_CONVERSION'
    if portfolio['capital']['no_bet']:return 'CAPITAL_FULL_MEC_REJECTED'
    selected=matching_tickets(portfolio['tickets'],groups)
    if not any(selected.values()):return 'SELECTED_TICKET'
    return 'PATH_RETAINED_SETTLEMENT_AND_RETURN_QUALITY_SEPARATE'


def engine_role_usage(engine_path):
    p=Path(engine_path);raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=ENGINE_SHA:raise ValueError('ENGINE_CODE_SHA_MISMATCH')
    tree=ast.parse(raw.decode());users=[]
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and any(
                isinstance(n,ast.Attribute) and n.attr=='static_roles' for n in ast.walk(node)):
            users.append(node.name)
    return {'engine_sha256':ENGINE_SHA,'static_roles_attribute_consumers':sorted(set(users)),
        'audit_only_role_fields':set(users)<={'role_audit_triggers','run_all'}}


def krs_audit(folder, result, engine_info):
    inputs={o:load(folder/o/'input.json') for o in OWNERS}
    outputs={o:load(folder/o/'output.json') for o in OWNERS}
    receipts={o:load(folder/o/'receipt.json') for o in OWNERS}
    for owner in OWNERS:
        receipt=receipts[owner]
        if (receipt['input_sha256']!=sha(inputs[owner]) or receipt['output_sha256']!=sha(outputs[owner])
                or receipt['runs']!=5000 or receipt['seed']!=1
                or not receipt['actual_engine_executed'] or receipt['engine_sha256']!=ENGINE_SHA):
            raise ValueError('KRS_RECEIPT_BINDING:'+owner)
        if sha({k:v for k,v in receipt.items() if k!='sha256'})!=receipt['sha256']:
            raise ValueError('KRS_RECEIPT_SELF_HASH:'+owner)
    physical=copy.deepcopy(inputs)
    for value in physical.values():
        for h in value['horses']:h.pop('static_roles',None)
    metrics=lambda out:[{k:r[k] for k in ('horse_no','SSR-W','SSR-P2','SSR-P3','SSR-T3','LSR')}
        for r in out['summary']]
    return {'classification':'OBSERVED', 'receipts_verified':True,
        'input_sha256':{o:receipts[o]['input_sha256'] for o in OWNERS},
        'input_difference_paths':diff_paths(inputs[OWNERS[0]],inputs[OWNERS[1]]),
        'physical_input_equal_after_audit_roles_removed':physical[OWNERS[0]]==physical[OWNERS[1]],
        'ssr_lsr_metrics_equal':metrics(outputs[OWNERS[0]])==metrics(outputs[OWNERS[1]]),
        'engine_role_usage':engine_info,
        'selection_consumption':{o:result['portfolios'][o]['krs_selection_effect'] for o in OWNERS},
        'actual_krs_selection_intervention_count':0,
        'incremental_predictive_value':'NOT_IDENTIFIED_NO_KRS_SELECTION_INTERVENTION',
        'same_seed_same_physical_input_is_bug':False,
        'owner_specific_physics_coupling':'NOT_PRESENT_OWNER_ROLES_ARE_AUDIT_METADATA_ONLY'}


def owner_row(result, owner, groups):
    pred=result['owners'][owner];port=result['portfolios'][owner];r=roles(pred)
    columns={c:role_ids(pred,c) for c in ('W','P2','P3')}
    value={'owner':owner,'role_widths':{c:len(v) for c,v in columns.items()},'columns':columns,
        'selected_ticket_count':len(port['tickets']), 'selected_stake':sum(t['stake'] for t in port['tickets']),
        'minimum_mec_ticket_count':len(port['mec']['tickets']),
        'minimum_mec_capital':port['capital']['required_capital'],
        'capital_limit':port['capital']['capital_limit'],
        'budget_excess':max(0,port['capital']['required_capital']-port['capital']['capital_limit']),
        'capital_state':'CALCULATED_NO_BET' if port['capital']['no_bet'] else 'CALCULATED_PAPER_SELECTED',
        'actual_unspent_research_cap':port['capital']['capital_limit']-sum(t['stake'] for t in port['tickets']),
        'conditional_model_values_are_purchase_inputs':False,
        'mec_projection':'ALL_DISTINCT_W_X_P2_X_P3_PROTECT_WITH_COMMON_MEC_COMPRESSION',
        'classification':'OBSERVED','correctness_or_policy':'ROLE_WIDTH_AND_SCORE_POLICY_AS_IMPLEMENTED_NOT_AUTOMATIC_BUG'}
    if owner=='BASELINE':value['role_boundary']=pred['role_width_policy']
    else:
        value['role_boundary']={'method':'INHERITED_BASELINE_COLUMN_COUNTS_ON_CANDIDATE_MARGINAL_RANKS',
            'widths':pred['role_widths'],'rankings_by_role':pred['rankings_by_role']}
    if groups is None:return value
    h=groups[0][0];second=groups[1];union={i for g in groups for i in g}
    independent_third=len(groups)==3 and len(groups[2])==1
    second_capture={i:'P2' in r[i] for i in second}
    value['evaluation']={'winner_rank':pred['ranking'].index(h)+1,'winner_top1':pred['ranking'][0]==h,
        'W_capture':'W' in r[h], 'P2_capture_by_rank2_runner':second_capture,
        'P2_capture':all(second_capture.values()),
        'P3_capture':('P3' in r[groups[2][0]]) if independent_third else None,
        'P3_applicability':'INDEPENDENT_RANK3' if independent_third else 'NO_INDEPENDENT_THIRD_SECOND_PLACE_TIE',
        'ranking_top3_unordered_set':set(pred['ranking'][:3])==union,
        'role_union_top3_set':union<={i for i,v in r.items() if v},
        'ordered_role_capture':('W' in r[h] and all(second_capture.values()) and 'P3' in r[groups[2][0]]) if independent_third else None,
        'purchased':matching_tickets(port['tickets'],groups),
        'mec_counterfactual_matches':matching_tickets(port['mec']['tickets'],groups),
        'first_required_path_loss':first_path_loss(pred,port,groups),
        'failure_cause_from_outcome_alone':'UNKNOWN_NO_CAUSAL_ABILITY_OR_ENVIRONMENT_LABEL',
        'ticket_hit_is_profitability':'UNKNOWN_REQUIRES_VERIFIED_PAYOUT_ACCOUNTING'}
    if owner!='BASELINE' and independent_third:
        s=second[0];t=groups[2][0]
        value['evaluation']['conditional_ranks_on_evaluation_prefix']={
            'W_rank':numeric_rank(pred['winner_model_mass'],h),
            'P2_rank_given_actual_head':numeric_rank(pred['p2_model_mass_given_head'][h],s),
            'P3_rank_given_actual_pair':numeric_rank(pred['p3_model_mass_given_pair'][h+'>'+s],t),
            'evaluation_only_prefix_never_sent_to_prediction':True}
    return value


def build(root, labels, *, engine_path, model_path):
    base=Path(root);model=load(model_path);engine_info=engine_role_usage(engine_path)
    labels_by_no=top3_labels(labels)
    records=[];total_unknown={};all_calculated=all_neutral=all_unresolved=0;observed_features={}
    for number in range(1,13):
        folder=base/('live-r01-v1' if number==1 else f'live-r{number:02d}-v2')
        before={str(p.relative_to(folder)):hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.rglob('*') if p.is_file()}
        result,_=readback(folder);label=labels_by_no.get(number) or {};groups=label.get('rank_groups');ids={str(r['runner_id']) for r in result['all_runners']}
        verify_label_identity(label,result['race'])
        if groups is not None and (len(groups)<2 or len(groups[0])!=1 or any(i not in ids for g in groups for i in g)
                or len([i for g in groups for i in g])!=len({i for g in groups for i in g})):
            raise ValueError('LABEL_RANK_GROUP_OR_UNIVERSE')
        n=result['numerical_summary'];all_calculated+=n['calculated_count'];all_neutral+=n['ruled_neutral_count'];all_unresolved+=n['unresolved_count']
        unknown={}
        for f in result['all_runners']:
            rid=f['runner_id'];cells=result['numerical_cells'][rid]
            neutral={k:{'terminal_status':c['terminal_status'],'missingness_fraction':c.get('missingness_fraction'),
                       'evidence_refs':c.get('evidence_refs'),'components':c.get('components')}
                     for k,c in cells.items() if c['terminal_status']=='RULED-NEUTRAL'}
            unknown[rid]={'name':f['name'],'history_count':len(f['starts']),'source_missingness':f['missingness'],
                'neutral_cells':neutral,'neutral_count':len(neutral)}
            for k in neutral:total_unknown[k]=total_unknown.get(k,0)+1
        b=result['owners']['BASELINE'];c=result['owners']['OHI_FIXED_CANDIDATE']
        features=load(folder/'features.json')
        for row in features['runners'].values():
            for name,value in row.items():observed_features[name]=observed_features.get(name,0)+int(value is not None)
        widths_equal=all(len(b[r])==c['role_widths'][r]==len(role_ids(c,r)) for r in ('W','P2','P3'))
        boundary_replay={}
        for role, key, floor in [('W','w_score',1),('P2','p2_score',2),('P3','p3_score',3)]:
            chosen,diag=_structure_upper_cluster(b['runner_scores'],key,min_active=floor)
            boundary_replay[role]={'same_members_as_frozen':set(chosen)==set(b[role]),'diagnostic':diag,
                'six_decimal_perturbation_changes':cluster_sensitivity(b['runner_scores'],key,floor)}
        after={str(p.relative_to(folder)):hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.rglob('*') if p.is_file()}
        if before!=after:raise ValueError('FROZEN_ORIGINAL_MUTATED')
        records.append({'race_no':number,'provider_race_id':result['race']['provider_race_id'],
            'classification':result['classification'],'source_sha256':result['source_sha256'],
            'prediction_sha256':result['sha256'],'freeze_at':result['freeze_at'],
            'source_fetched_at':result['source_fetched_at'],'cutoff':result['race']['prediction_cutoff'],
            'execution_manifest':load(folder/'execution-manifest.json'),'original_files_unchanged':True,
            'rank_groups':groups,'label_verification':label.get('verification_status') or (labels.get('verification') if labels else None),
            'label_independently_matched':label.get('official_page_independently_matched'),
            'label_source_url':label.get('source_url'),'label_record_sha256':sha(label) if label else None,
            'candidate_inherits_baseline_widths':widths_equal,'baseline_cluster_replay':boundary_replay,
            'owners':[owner_row(result,owner,groups) for owner in OWNERS],
            'krs':krs_audit(folder,result,engine_info),'unknown_by_runner':unknown})
    fits=[]
    for depth,fit in enumerate(model['fits']):
        fits.append({'role':('W','P2','P3')[depth],
            'feature_names':fit['feature_names'],
            'observed_runner_count_by_feature':{name:observed_features.get(name,0) for name in fit['feature_names']},
            'zero_weight_or_zero_training_scale':[k for k,s,w in zip(fit['feature_names'],fit['training_scales'],fit['coefficients']) if not s or not w],
            'available_does_not_mean_contributes':True})
    out={'classification':'POST_RESULT_READ_ONLY_DIAGNOSTIC_NOT_FORWARD_OOS',
        'rows':records,'owner_row_count':sum(len(r['owners']) for r in records),
        'summary':{'races':len(records),'calculated_cells':all_calculated,'neutral_cells':all_neutral,
            'unresolved_cells':all_unresolved,'neutral_by_index':total_unknown,
            'width_inheritance_count':sum(r['candidate_inherits_baseline_widths'] for r in records),
            'same_physical_krs_inputs_count':sum(r['krs']['physical_input_equal_after_audit_roles_removed'] for r in records),
            'same_ssr_lsr_count':sum(r['krs']['ssr_lsr_metrics_equal'] for r in records)},
        'model_sha256':model['sha256'],'model_feature_consumption':fits,
        'implementation_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
            ('runtime/local_krs_bridge_candidate.py','runtime/local_race_key_shadow_owner.py','runtime/ohi_single_race_research.py')},
        'production_changes':False,'engine_reexecutions':0,'owner_reexecutions':0,
        'research_policy_added':False,'performance_improvement_claim':False}
    out['sha256']=sha(out);return out


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input-root',required=True);p.add_argument('--labels');p.add_argument('--engine-path',required=True)
    p.add_argument('--model-path',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();dest=Path(a.output).resolve()
    if dest.is_relative_to(ROOT):raise ValueError('PRIVATE_REPORT_OUTSIDE_CODE_REQUIRED')
    if dest.exists():raise ValueError('DIAGNOSTIC_OUTPUT_EXISTS')
    result=build(a.input_root,load(a.labels) if a.labels else None,engine_path=a.engine_path,model_path=a.model_path)
    dest.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'sha256':result['sha256'],'summary':result['summary']},ensure_ascii=False))


if __name__=='__main__':main()

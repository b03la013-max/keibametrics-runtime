"""Existing KAW day audit extended to the signed 2026-10-16 cohort.

Only immutable inputs are read. All newly computed arms are historical replay,
never extra Forward OOS or replacement FINALs. Network/signing is not used.
"""
import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from aki_adaptive_purchase_shadow import verify_signed_final_binding
from family_conversion_diagnostics import measure_capital_conversion
from family_pfs_improvement import classify_dominant_pfs_loss_owner
from local_aki_columns import build, decision, build_role_rescue, freeze_role_rescue, sha
from local_fullnumerical_production import materialize_production
from mec_r4_shadow import settle_ticket_list
from post_result_learning import _coverage
from tools.local_aki_matched_comparison import portfolio

RUNS={1:38855562125,2:38859938474,6:38873003494,9:38881777914,12:38895197802}
# Independently observed canonical Runtime key, not any envelope's own key.
KEY='jqWqOYlmhXXmpv/nR7lx3c2n/S5shDYava/WJVxn4kE='
KEY_REF='PR282@664d76126457cea9239d7ad24c0c52ced5418609/evidence/autonomous_completion_20261016/current_production.json#health'


def read(n,name,raw_root=None,root=ROOT):
    if raw_root:return json.loads((Path(raw_root)/f'{n:02}-{name}.json').read_text())
    rid=f'KM-LOCAL-KAW-20261016-R{n:02}-LIVE-R1';run=RUNS[n]
    if name=='intent':p=f'runtime/formal_intents/{rid}.json'
    elif name=='static_owner':p=f'runtime/local_production_static_owner_records/{rid}.json'
    elif name=='terminal':p=f'runtime/execution_reports/{rid}/terminal-{run}.json'
    else:
        phase='RESULT' if name=='result_receipt_envelope' else 'FORMAL'
        suffix='result' if phase=='RESULT' else 'formal'
        p=f'runtime/executions/{rid}/{phase}/runs/race-key-{run}-{suffix}/{name}.json'
    return json.loads((root/p).read_text())


def signed(envelope,phase,rid):
    rec=envelope['receipt'];payload=json.dumps(rec,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    Ed25519PublicKey.from_public_bytes(base64.b64decode(KEY)).verify(base64.b64decode(envelope['signature']),payload)
    if (sha(rec)!=envelope['receipt_sha256'] or sha(envelope['artifact'])!=rec['artifact_sha256']
            or rec['race_id']!=rid or rec['phase']!=phase
            or envelope['signer_key_id']!='KM-LOCAL-RUNTIME-ED25519-20260922'):
        raise ValueError('SIGNED_LINEAGE_INVALID:'+rid+':'+phase)
    return envelope


def settle(tickets,result):
    facts=copy.deepcopy(result['artifact']['official_result'])
    facts['top3']=facts['finish_order'][:3]
    return settle_ticket_list(tickets,{'official_result':facts})


def metrics(rows):
    inv=sum(r['investment'] for r in rows);ret=sum(r['return'] for r in rows)
    equity=peak=dd=0
    for r in rows:
        equity+=r['profit_loss'];peak=max(peak,equity);dd=max(dd,peak-equity)
    return {'races':len(rows),'investment':inv,'return':ret,'profit_loss':ret-inv,
        'pfs_pct':ret/inv*100 if inv else None,'max_drawdown':dd,
        'total_loss_count':sum(r['investment']>0 and r['return']==0 for r in rows),
        'no_bet_count':sum(r['investment']==0 for r in rows)}


def audit(raw_root=None):
    rows=[];fixtures=[]
    for n in range(1,13):
        rid=f'KM-LOCAL-KAW-20261016-R{n:02}-LIVE-R1'
        if n not in RUNS:
            rows.append({'race_no':n,'race_id':rid,'canonical_final':'NOT_OBSERVED',
                'race_key':'NOT_OBSERVED','first_stop':'RACE_KEY_REGISTRATION',
                'original_error':'UNKNOWN','refusal_reported':n in {7,10,11},
                'formal_pfs':None,'official_result':'PENDING_READ_ONLY_OFFICIAL_FETCH',
                'global_runtime_store_enumerated':False})
            continue
        load=lambda name:read(n,name,raw_root)
        req=load('intent');f=signed(load('final_receipt_envelope'),'FINAL',rid)
        result=signed(load('result_receipt_envelope'),'RESULT',rid)
        source=signed(load('source_receipt_envelope'),'SOURCE',rid)
        pre=signed(load('pre_krs_receipt_envelope'),'PRE_KRS',rid)
        krs=signed(load('krs_receipt_envelope'),'KRS_RUN',rid)
        art=f['artifact'];src=source['artifact'];owner=load('static_owner');ku=load('krs_prediction_utility')
        if (result['artifact']['frozen_refs']['final_receipt_sha256']!=f['receipt_sha256']
                or art['source_receipt_sha256']!=source['receipt_sha256']
                or art['krs_receipt_sha256']!=krs['receipt_sha256']
                or pre['artifact']['input_sha256']!=krs['artifact']['input_sha256']
                or art['final_prediction_package']['ranking']!=req['static_prediction']['ranking']
                or art['final_prediction_package']['roles']!=req['static_prediction']['roles']):
            raise ValueError('FROZEN_CHAIN_MISMATCH:'+rid)
        from datetime import datetime
        cutoff=datetime.fromisoformat(req['prediction_cutoff'])
        if any(datetime.fromisoformat(e['receipt']['timestamp'])>=cutoff for e in (source,pre,krs,f)):
            raise ValueError('PRE_CUTOFF_CHAIN_REQUIRED:'+rid)
        q=materialize_production(src,req,req['required_indices'])
        recorded=load('index_provenance_manifest')['rows']
        values={(str(r['runner_id']),key):value['value'] for r in q['runners'] for key,value in r['candidate_indices'].items()}
        if any(values[(str(r['runner_id']),r['index'])]!=r['value'] for r in recorded):
            raise ValueError('INDEX_RECALCULATION_MISMATCH:'+rid)
        baseline=art['final_ticket']['tickets'];bs=settle(baseline,result)
        old=result['artifact']['settlement']
        if (bs['investment'],bs['return'])!=(old['investment'],old['return']):
            raise ValueError('SETTLEMENT_MISMATCH:'+rid)
        original_aki=load('aki_adaptive_purchase_shadow_pre_result')
        verify_signed_final_binding(f,original_aki)
        q['source_snapshot_sha256']=src['source_snapshot_sha256']
        top=list(result['artifact']['official_result']['finish_order'][:3]);h,s,t=map(str,top)
        roles=req['static_prediction']['roles'];pair=next((x for x in req['pair_dispositions'] if (str(x['head']),str(x['second']))==(h,s)),None)
        third=next((x for x in req['third_dispositions'] if tuple(str(x[k]) for k in ('head','second','third'))==(h,s,t)),None)
        original_review=result['artifact']['automatic_post_result_review']
        arms={'PRODUCTION':{'tickets':baseline},'STATIC_PLUS_KRS_DIAGNOSTIC':{'tickets':copy.deepcopy(baseline)},
              'ORIGINAL_AKI':{'tickets':original_aki['candidate_tickets'],'frozen_role_columns':original_aki['selected_role_columns']}}
        for mode,label in [(None,'PR262_REFERENCE'),('HEAD_LOCAL_VNEXT_R1','PR265_R1_REJECTED'),('HEAD_LOCAL_VNEXT_R2','PR265_R2_REJECTED')]:
            qq=copy.deepcopy(q)
            if mode:qq['aki_column_candidate']=mode
            selected=build(qq,src);dd=decision(qq,selected)
            arms[label]={'selection':selected,'tickets':dd['paper_tickets'],
                'forward_admission':'REJECTED' if mode else 'NOT_PROMOTED'}
        for include,label in [(False,'OWNER_DIVERSITY_R3'),(True,'OWNER_DIVERSITY_KRS_R3')]:
            selected=build_role_rescue(q,src,owner,ku,include_krs=include)
            dd=decision(q,selected)
            freeze=freeze_role_rescue(q,selected,dd['paper_tickets'],evaluation_mode='HISTORICAL_REPLAY',
                policy_sha256=sha(json.loads((ROOT/'profiles/family_integrated_shadow_20261016_R1.json').read_text())))
            arms[label]={'selection':selected,'tickets':dd['paper_tickets'],'freeze':freeze}
        finite=copy.deepcopy(q);finite['capital_policy']={'mode':'HARD_RACE_BUDGET','max_race_capital':10000,'insufficient_action':'NO_BET'}
        sel=build_role_rescue(finite,src,owner,ku,include_krs=True);fd=decision(finite,sel)
        arms['FINITE_CAPITAL_10000']={'selection':sel,'tickets':fd['paper_tickets'],'capital':fd['capital'],
            'budget_basis':'EXISTING_FAMILY_DEFAULT; PAPER counterfactual, not personal-bankroll evidence'}
        pairadds=ku.get('actionable_ordered_pair_proposals',[])
        roleadds=ku.get('actionable_role_proposals',[])
        krsmeasure={
            'unique_w_rescue':any(str(x['horse_no'])==h and x['proposal']=='ADD_W_SHADOW' for x in roleadds) and 'W' not in roles[h],
            'unique_p2_rescue':any(str(x['horse_no'])==s and x['proposal']=='ADD_P2_SHADOW' for x in roleadds) and 'P2' not in roles[s],
            'unique_pair_rescue':any((str(x['head']),str(x['second']))==(h,s) for x in pairadds) and not _coverage(art,top)['ordered_pair_ticket_coverage'],
            'nonwinning_w_additions':[x['horse_no'] for x in roleadds if x['proposal']=='ADD_W_SHADOW' and str(x['horse_no'])!=h],
            'nonwinning_p2_additions':[x['horse_no'] for x in roleadds if x['proposal']=='ADD_P2_SHADOW' and str(x['horse_no'])!=s],
            'false_deletion_count':0,'direct_production_additions':0,
            'notice':'Nonwinning additions are observed false positives, not proof of causal harm or real win probabilities.'}
        for label,a in arms.items():
            columns=({c:a['selection']['columns'][c]['selected'] for c in ('W','P2','P3')}
                if 'selection' in a else a.get('frozen_role_columns') or
                {c:[rid for rid,rr in roles.items() if c in rr] for c in ('W','P2','P3')})
            a['role_capture']={c:v in set(map(str,columns[c])) for c,v in zip(('W','P2','P3'),(h,s,t))}
            a['nonwinning_w_heads']=[v for v in columns['W'] if str(v)!=h]
            a['selected_column_widths']={c:len(columns[c]) for c in ('W','P2','P3')}
            a['settlement']=settle(a['tickets'],result)
            a['coverage']=_coverage({'final_ticket':{'tickets':a['tickets'],'total_investment':a['settlement']['investment']}},top)
            a['capital_burden_delta']=a['settlement']['investment']-bs['investment']
            a['pfs_increment_pp']=(a['settlement']['pfs']-bs['pfs']) if a['settlement'].get('pfs') is not None else None
            a['lost_baseline_winning_types']=sorted(set(bs['hit_types'])-set(a['settlement']['hit_types']))
            if a['tickets']:
                identity=['KAW','2026-10-16',n];maximum=max(len(baseline),len(a['tickets']));minimum=min(len(baseline),len(a['tickets']))
                a['matched']={mode:{'candidate':settle(portfolio(a['tickets'],identity,units,count=count),result),
                    'production':settle(portfolio(baseline,identity,units,count=count),result)}
                    for mode,units,count in [('equal_budget_full_coverage',maximum,None),('equal_budget_equal_count',minimum,minimum)]}
            else:a['matched']={'status':'NO_BET_RETAINED_IN_DENOMINATOR','no_bet_opportunity_cost_return':bs['return'],'avoided_baseline_loss':-bs['profit_loss']}
        terminal=load('terminal');numerical=load('numerical_materialization_summary')
        row={'race_no':n,'race_id':rid,'canonical_final':'VERIFIED','run':RUNS[n],
            'run_event':'push','scheduler_success':False,'final_at':f['receipt']['timestamp'],'result_at':result['receipt']['timestamp'],
            'signed_receipts_verified':5,'final_receipt_sha256':f['receipt_sha256'],'result_receipt_sha256':result['receipt_sha256'],
            'source_snapshot_sha256':src['source_snapshot_sha256'],'official_top3':top,'static_ranking':req['static_prediction']['ranking'],
            'role_capture':{c:c in roles[v] for c,v in zip(('W','P2','P3'),(h,s,t))},
            'pair_disposition':pair,'third_disposition':third,'coverage':_coverage(art,top),
            'first_material_failure':original_review['failure_localization']['first_material_failure'],
            'dominant_pfs_loss':classify_dominant_pfs_loss_owner(original_review),
            'delivery':{'github_saved':True,'notification_sent':'UNKNOWN','user_received_at':terminal.get('user_received_at'),
                'prestart_delivery_pass':terminal.get('prestart_delivery_pass'),'render_at':terminal.get('render_generated_at')},
            'numerical':numerical['numeric_coverage'],
            'numerical_provenance':[ {k:x.get(k) for k in ('runner_id','index','value','terminal_status','rule_id','evidence_refs','missingness_fraction')} for x in recorded],
            'numerical_consumed_by_production_static':False,
            'numeric_incremental_value':'NOT_IDENTIFIABLE_FROM_THIS_SINGLE_DAY; NOT_CONNECTED_BY_AUTHORITY',
            'krs_incremental':krsmeasure,'source_manifest':[{'source_class':x.get('source_class'),'cutoff_relation':x.get('cutoff_relation'),'fetched_at':x.get('fetched_at')} for x in src['sources']],
            'capital_conversion':measure_capital_conversion(req,art['final_ticket'],art['final_prediction_package'],ku),
            'arms':arms,'new_forward_oos_count':0,'actual_purchase_pfs':None}
        rows.append(row)
        fixtures.append({'race_id':rid,'race_no':n,'run':RUNS[n],'final_receipt_sha256':f['receipt_sha256'],
            'final_artifact_sha256':f['receipt']['artifact_sha256'],'result_receipt_sha256':result['receipt_sha256'],
            'fixture_class':{1:'EXACT_HIT/CAPITAL_EFFICIENCY',2:'TIEBREAK_ONLY_NONINFORMATIVE',6:'P2_MISS/KRS_PAIR_RESCUE',9:'W_MISS/P2_MISS/KRS_WINNER_RESCUE',12:'W_MISS/REVERSED_EXACT/KRS_FALSE_ADDITION'}[n]})
    good=[r for r in rows if r['canonical_final']=='VERIFIED'];labels=list(good[0]['arms'])
    report={'schema':'KM-FAMILY-INTEGRATED-REGRESSION-20261016-R1','status':'HISTORICAL_REPLAY_ONLY',
        'baseline_main_sha':'fa8daf81fbac6ad4e183b042ff6af3fd7d93603f','trusted_signer_key_ref':KEY_REF,
        'meeting_denominator':12,'canonical_formal_completed':len(good),'canonical_formal_rate':len(good)/12,
        'independently_acknowledged_delivery':0,'delivery_unknown_count':len(good),
        'future_approved_denominator':None,'new_forward_oos_count':0,
        'fixed_four':metrics([r['arms']['PRODUCTION']['settlement'] for r in good if r['race_no'] in {1,6,9,12}]),
        'signed_five':metrics([r['arms']['PRODUCTION']['settlement'] for r in good]),
        'aggregates':{label:metrics([r['arms'][label]['settlement'] for r in good]) for label in labels},
        'stage_funnel':{stage:{'verified':5,'denominator':12,'rate':5/12} for stage in ['RaceKey','Intent','SignedSource','Static','KRS','Final','ResultSettlementLearning']},
        'discovery':{'verified':12,'denominator':12,'evidence':'PR282 signed official plan c316b452b4fba1bf40a334607469681442e56a1b4b7c80005955e48410ee60ba; discovery is not dispatch approval'},
        'role_coverage':{c:{'captured':sum(r['role_capture'][c] for r in good),'denominator':5} for c in ['W','P2','P3']},
        'policy_role_and_conversion':{label:{'denominator':5,
            'roles':{c:sum(r['arms'][label]['role_capture'][c] for r in good) for c in ['W','P2','P3']},
            'ordered_pair':sum(r['arms'][label]['coverage']['ordered_pair_ticket_coverage'] for r in good),
            'exact':sum(r['arms'][label]['coverage']['ordered_exact_ticket_coverage'] for r in good),
            'purchased_trio':sum(r['arms'][label]['coverage']['purchased_trio_ticket_coverage'] for r in good)} for label in labels},
        'p3_selectivity_notice':'All active runners received P3; 5/5 is not discrimination evidence.',
        'rows':rows,'fixtures':fixtures,'production_changed':False,'original_oos_changed':False,
        'protection':'No new signing, dispatch, purchase, merge, deployment or activation.'}
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--raw-root');p.add_argument('--out',default='research/kaw_v26_20261016/integrated_regression.json')
    args=p.parse_args();report=audit(args.raw_root);out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('canonical_formal_completed','fixed_four','signed_five','aggregates')},ensure_ascii=False))

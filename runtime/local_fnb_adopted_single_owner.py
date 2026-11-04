"""Existing frozen Owner/R16/MEC computation behind explicit adoption gates.

No default signer or adoption exists. Internal research provenance is retained;
only a separately verified future Owner decision can authorize its consumption.
"""
from copy import deepcopy
from pathlib import Path
from datetime import datetime,timezone

from runtime import local_fnb_research_runtime as common
from runtime.local_fnb_alternative_connection import require,sha,encoded,stamp,compact


def materialize_inputs(captured,request,source, *, generated_at):
    """Reuse existing 29 formulas; retain their research provenance labels."""
    from runtime.local_fnb_rakuten_reference import materialize_reference
    loaded=materialize_reference(captured['raw'],capture=captured['capture'],
        race={k:request[k] for k in ('venue_id','race_date','race_no')},generated_at=generated_at)
    num=deepcopy(loaded['numerical']);num['race_id']=request['race_id']
    active=set(source['artifact']['active_runner_ids'])
    num['runners']=[r for r in num['runners'] if str(r['runner_id']) in active]
    num['required_indices']=num['candidate_full_numerical_summary']['required_indices']
    num['strict_full_numerical_ready']=all(len(r['canonical_components'])==29 and all(c['terminal_status'] in
        ('CALCULATED','RULED-NEUTRAL') for c in r['canonical_components'].values()) for r in num['runners'])
    num['consumer_adoption']={'decision_sha256':captured['owner_adoption_envelope']['receipt_sha256'],
        'scope':'FNB_ONLY','prior_internal_research_labels_retained':True,'new_numerical_policy':False}
    require({str(r['runner_id']) for r in num['runners']}==active,'NUMERICAL','SINGLE_OWNER_ACTIVE_NUMERICAL_COVERAGE_LOST')
    packet=deepcopy(loaded['observation_packet']);packet.update(race_id=request['race_id'],
        source_receipt_sha256=captured['source_envelope']['receipt_sha256'],
        source_freeze_at=source['artifact']['source_freeze_at'])
    packet['runners']=[r for r in packet['runners'] if r['runner_id'] in active]
    packet['counts']['active_runners']=len(active);packet.pop('sha256');packet['sha256']=compact(packet)
    return loaded,num,packet


def render_body(num,request,prediction,output,executed,review,methods,loaded,captured_source):
    from runtime.local_fnb_r13_private_numeric_document import render_full_numeric
    from runtime import local_fnb_exact_orientation_research as exact
    numeric_doc=deepcopy(num)
    for row in numeric_doc['runners']:row.setdefault('numerical_missing_components',row.get('candidate_missing_components',[]))
    numeric=render_full_numeric(numeric_doc,classification='ADOPTED_SINGLE_OWNER_FUTURE_EXECUTION',
        race_id=request['race_id'],source_description='採用済み代替Provider。資格・Active・署名はSOURCE Receiptで検証。')['body']
    by={str(r['horse_no']):r for r in output['summary']}
    ranks={c:{r['runner_id']:r for r in prediction['column_rankings'][c]['rows']} for c in ('W','P2','P3')}
    lines=['# 船橋｜単独固定Owner・全馬・全券面',request['race_id'],
        '正式受入は同梱Signed FINAL検証による。未較正・実勝率/EVなし・各方式は独立代替案。',
        '|項目|値|','|---|---|',*['|'+k+'|'+str(v)+'|' for k,v in {'発走':request['scheduled_post_at'],
            'Cutoff':request['prediction_cutoff'],'SOURCE取得':loaded['parsed']['captured_at'],
            'SOURCE SHA':prediction['source_snapshot_sha256'],'Raw SHA':sha(captured_source['raw']),
            'Static Freeze':prediction['freeze_at'],'Revision':request['race_id'],'Model SHA':common.MODEL_SHA,
            'KRS input SHA':sha(encoded(executed)),'KRS output SHA':sha(encoded(output)),
            'Selection':exact.PROFILE,'Selection SHA':sha(encoded(review))}.items()],
        '|馬番|馬名|W順位|P2順位|P3順位|Role|SSR-W/P2/P3|LSR|Z4R-W/P2/P3|','|---|---|---|---|---|---|---|---|---|']
    for runner in num['runners']:
        rid=str(runner['runner_id']);k=by[rid]
        lines.append('|'+ '|'.join([rid,runner['name'],*[str(ranks[c][rid]['rank']) if ranks[c][rid]['rank'] is not None else
            'UNKNOWN '+str(ranks[c][rid]['rank_interval']) for c in ('W','P2','P3')],','.join(prediction['roles'][rid]),
            '/'.join(str(k[c]) for c in ('SSR-W','SSR-P2','SSR-P3')),str(k['LSR']),
            '/'.join(str(k[c]) for c in ('Z4R-W','Z4R-P2','Z4R-P3'))])+'|')
    lines+=['展開：歴史的World/Stageの条件付き仮説。現戦術・実測加速・因果的競合はUNKNOWN。',
        'KRS：実5000回seed1。Supportは未較正、共同確率・EVではありません。',numeric]
    for name in ('EXACTA','TRIO','TRIFECTA'):
        row=methods[name]
        lines+=['## '+name,'既存Capital判定 '+row['capital_policy']['decision'],
            '必要MEC '+str(sum(t['stake'] for t in row['full_semantic_tickets']))+'円／上限 '+str(row['capital_policy']['capital_limit'])+'円',
            '選択 '+str(len(row['tickets']))+'点／投資 '+str(sum(t['stake'] for t in row['tickets']))+'円',
            '資金非選択 '+str(row['capital_nonselected_coverage'])+'点（意味的被覆を原本へ保持）',row['canonical_tree']]
    return '\n\n'.join(lines)+'\n'


def execute(*,request,admitted_source,adopted_owner,captured_source,private_root,now,
            engine,params,sign_final=None,clock=None,krs_cache=None,cache_receipt_sha256=None):
    """Concrete existing 29→Static→KRS→R16→MEC→Capital→body, one Owner.

    The caller must pass the live adapter's admitted source/Owner decision.
    This function independently checks those gates again before computation.
    A missing signer fails before any Engine call, never emits a fake FINAL.
    """
    from runtime.local_fnb_alternative_connection import source_assessment,owner_adoption
    from runtime.local_fnb_context_static_candidate import build_context,predict
    from runtime.local_fnb_csv_research_runtime import _bridge_aliases
    from runtime import local_fnb_semantic_closure as semantic
    from runtime import local_fnb_exact_orientation_research as exact
    from runtime.capital_policy import resolve_capital_policy
    from runtime.jra_ticket_tree_renderer import render_ticket_tree
    clock=clock or (lambda:datetime.now(timezone.utc))
    trust=captured_source.get('trust')
    source=source_assessment(captured_source,intent={k:request[k] for k in ('venue_id','race_date','race_no')},now=clock(),trust=trust)
    require(source['source_admitted'] and source['artifact']==admitted_source['artifact'],'SOURCE','SINGLE_OWNER_SOURCE_RECHECK_FAILED')
    owner=owner_adoption(captured_source.get('owner_adoption_envelope'),request=request,
        source=source['artifact'],trust=trust,now=clock())
    require(owner==adopted_owner,'OWNER','SINGLE_OWNER_ADOPTION_RECHECK_FAILED')
    require(callable(sign_final),'FINAL','EXISTING_ADOPTED_FINAL_SIGNER_NOT_CONNECTED')
    require(owner.get('numerical_registry_sha256')==sha((common.REPO/'mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json').read_bytes())
        and owner.get('numerical_mapping_sha256')==sha((common.REPO/'mapping/local_full_numerical_mapping_v0.1_candidate_20260923.json').read_bytes()),
        'NUMERICAL','FNB_EXISTING_NUMERICAL_DEFINITIONS_NOT_EXPLICITLY_BOUND')
    def before():
        value=clock();require(stamp(value)<stamp(request['prediction_cutoff']),'TIME','SINGLE_OWNER_CUTOFF_REACHED_NO_PUBLICATION');return stamp(value)
    materialized_at=before().isoformat()
    loaded,num,packet=materialize_inputs(captured_source,request,source,generated_at=materialized_at)
    active=set(source['artifact']['active_runner_ids'])
    context=build_context(packet,generated_at=before().isoformat())
    upstream,bridge=common.build_upstream(_bridge_aliases(num),numerical_sha256=sha(encoded(num)))
    prediction=predict(context,frozen_at=before().isoformat(),upstream_krs_input=upstream)
    folder=common._private_root(Path(private_root)/'adopted_single_owner_computation'/request['race_id'])
    for name,value in [('request.json',request),('numerical.json',num),('observations.json',packet),
            ('context.json',context),('static_prediction.json',prediction),('hsv_bridge.json',bridge)]:
        common._immutable(folder/name,encoded(value))
    before();receipt=common.execute_krs(prediction['PRE_KRS_input'],engine=engine,params=params,
        destination=folder/'krs',cache=krs_cache,cache_receipt_sha256=cache_receipt_sha256)
    import json
    output=json.loads((folder/'krs/execution_output.json').read_bytes())
    executed=json.loads((folder/'krs/execution_input.json').read_bytes());before()
    selected_at=before().isoformat();s2=semantic.research_unknown_path_protection(prediction,evaluated_at=selected_at)
    freeze={'profile':exact.PROFILE,'module_sha256':exact.MODULE_SHA,'profile_sha256':sha(exact.PROFILE_PATH.read_bytes()),
        'frozen_at':adopted_owner['effective_from'],'formal_adoption_receipt_sha256':captured_source['owner_adoption_envelope']['receipt_sha256']}
    review=exact.evaluate(prediction,context,output,s2,freeze=freeze,evaluated_at=selected_at)
    full=exact.construct(prediction,context,output,review,s2,freeze=freeze,evaluated_at=selected_at)
    methods={}
    for name,row in full['methods'].items():
        proposed=row['tickets'];capital=resolve_capital_policy(semantic.original_request(prediction),
            {'minimum_required_capital':sum(t['stake'] for t in proposed),'profile':exact.PROFILE,
             'sha256':sha(encoded(proposed)),'material_coverage_ratio':1.0})
        tickets=proposed if capital['decision']=='EXECUTE_FULL_MEC' else []
        plans=([r['strict_plan'] for r in full['strict_MEC_exact_pair_plans']] if name=='TRIFECTA' else
            [r['canonical_plan'] for r in s2['known_pair_scoped_subplans']])
        tree=render_ticket_tree({'final_ticket':{'tickets':tickets,'no_bet':not tickets},
            'capital_policy_decision':capital,'final_prediction_package':{'validation_status':'UNVALIDATED'}})
        methods[name]={'tickets':tickets,'full_semantic_tickets':proposed,'capital_policy':capital,
            'strict_MEC_plans':plans,'canonical_tree':tree['text'],
            'capital_nonselected_coverage':len(proposed)-len(tickets),'whole_race_NO_BET':False}
    body=render_body(num,request,prediction,output,executed,review,methods,loaded,captured_source);before()
    artifact={'race_id':request['race_id'],'owner_count':1,'model_code_sha256':common.MODEL_SHA,
        'source_receipt_sha256':captured_source['source_envelope']['receipt_sha256'],
        'active_universe_sha256':source['artifact']['active_universe_sha256'],
        'static_freeze_at':prediction['freeze_at'],'final_freeze_at':before().isoformat(),
        'numerical_sha256':sha(encoded(num)),'KRS_input_sha256':sha(encoded(executed)),
        'KRS_output_sha256':sha(encoded(output)),'selection_decision_sha256':sha(encoded(review)),
        'method_ticket_sha256':{n:sha(encoded(r['tickets'])) for n,r in methods.items()},'body_sha256':sha(body.encode()),
        'actual_purchase':False,'registered_OOS_increment':0}
    result={'final_envelope':sign_final(phase='FINAL',race_id=request['race_id'],status='PASS',artifact=deepcopy(artifact)),
        'numerical':num,'observations':packet,'materialized_at':materialized_at,'krs_requested_input':prediction['PRE_KRS_input'],'krs_execution_input':executed,'krs_output':output,
        'methods':methods,'body':body,'prediction':prediction,'context':context,'selection_review':review,
        'selection_freeze':freeze,'base_S2':s2,'full_semantic_portfolio':full,'KRS_receipt':receipt,
        'full_body_verification':{'all29_cells':len(active)*29,'all_roles_included':True,
            'all_selected_tickets_included':True,'body_sha256':sha(body.encode())}}
    for name,value in [('computed_result.json',result),('selection_review.json',review),('full_semantic_portfolio.json',full)]:
        common._immutable(folder/name,encoded(value))
    return result

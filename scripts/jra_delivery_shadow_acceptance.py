"""Local fault-injection latency evidence over an unchanged real signed FINAL."""
import argparse, hashlib, json, statistics, sys, time, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'runtime')]
from jra_delivery import build_publication
from family_authority_guard import resolve_current_authority


def run(health):
    rid='KM-JRA-TKY-20261018-R11';path=ROOT/'runtime/final_artifacts'/(rid+'.json')
    frozen=path.read_bytes();final=json.loads(frozen)
    request=json.loads((ROOT/'runtime/requests'/(rid+'-LIVE-R1-FORMAL.json')).read_text())
    _,authority=resolve_current_authority();contract=json.loads((ROOT/authority['common_family_components']['family_runtime_contracts_profile']).read_text())['families']['JRA']
    before=[];after=[]
    for _ in range(5):
        start=time.perf_counter();time.sleep(.2)
        build_publication(final,health=health,contract=contract,published_at=health['timestamp'],run_url='MECHANICAL_LOCAL_NO_PUBLICATION')
        before.append(time.perf_counter()-start)
        start=time.perf_counter()
        publication,_=build_publication(final,health=health,contract=contract,published_at=health['timestamp'],run_url='MECHANICAL_LOCAL_NO_PUBLICATION')
        after.append(time.perf_counter()-start)
    assert path.read_bytes()==frozen
    report={'profile':'JRA-DELIVERY-SHADOW-ISOLATION-ACCEPTANCE-20261018',
            'classification':'MECHANICAL_LOCAL_INJECTED_DELAY_NOT_LIVE_OR_FORWARD_OOS',
            'race_id':rid,'final_file_sha256':hashlib.sha256(frozen).hexdigest(),
            'signed_payload_verified':publication['signature_verified'],'production_final_unchanged':True,
            'injected_shadow_seconds':.2,'samples':5,'before_seconds':before,'after_seconds':after,
            'before_median_seconds':statistics.median(before),'after_median_seconds':statistics.median(after),
            'measurement':'Signed FINAL available -> local cryptographic verification/render, no Shadow serialization/learning/model work before publication',
            'live_signed_final_to_canonical_http_or_user_receipt_seconds':'UNKNOWN_NOT_DEPLOYED',
            'genuine_forward_oos_races':0,'live_learning_consumption':0,'external_publication_performed':False,
            'workflow_design':'Existing formal-run publishes first; independent bounded shadow-run consumes durable production artifact; Single Entry reads production artifact without whole-run wait',
            'retained_models_and_72_plan':'UNCHANGED','merge':'HOLD_NEW_HEAD_OWNER_APPROVAL_REQUIRED',
            'code_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['runtime/jra_shadow_checkpoint.py','runtime/jra_formal_artifact_wait.py','.github/workflows/km-formal-request-runner.yml','.github/workflows/km-jra-formal-single-entry.yml']}}
    dest=ROOT/'evidence/jra_p0_20261018/DELIVERY_SHADOW_ISOLATION.json';dest.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:report[k] for k in ['classification','signed_payload_verified','before_median_seconds','after_median_seconds','production_final_unchanged']}))


def learning_mechanical(root=ROOT):
    """Reproducible retrospective probe; synthetic creation time grants no live eligibility."""
    from datetime import timedelta
    from jra_role_learning_shadow import build_shadow, digest, instant, POLICY
    from jra_shadow_checkpoint import learning_effect
    from post_result_learning import build_post_result_review, build_learning_state
    root=Path(root); inventory={}; rows=[]; cache={}
    def read(relative):
        if relative not in cache:
            raw=(root/relative).read_bytes()
            inventory[relative]=hashlib.sha256(raw).hexdigest()
            cache[relative]=json.loads(raw)
        return cache[relative]
    for venue in ('TKY','KYO','NGT'):
        for number in range(2,13):
            rid=f'KM-JRA-{venue}-20261018-R{number:02d}'
            request_path=f'runtime/requests/{rid}-LIVE-R1-FORMAL.json'
            final_path=f'runtime/final_artifacts/{rid}.json'
            if not (root/request_path).exists() or not (root/final_path).exists():continue
            request,final=read(request_path),read(final_path)
            states=[]; sources=[]
            for previous in range(1,number):
                source_race=f'KM-JRA-{venue}-20261018-R{previous:02d}'
                sf=f'runtime/final_artifacts/{source_race}.json';sr=f'runtime/results/{source_race}.json'
                if not (root/sf).exists() or not (root/sr).exists():continue
                source_final,result=read(sf),read(sr)
                synthetic=instant(result['official_result']['captured_at'])+timedelta(seconds=1)
                if synthetic>=instant(request['source_snapshot']['source_freeze_at']):continue
                review=build_post_result_review(result,source_final)
                state=build_learning_state(review,effective_time=synthetic.isoformat())
                states.append(state)
                sources.append({'source_race':source_race,'result_path':sr,'final_path':sf,
                    'result_file_sha256':inventory[sr],'final_file_sha256':inventory[sf],
                    'official_result_captured_at':result['official_result']['captured_at'],
                    'review_sha256':review['sha256'],'synthetic_state':state,
                    'state_creation_time_is_simulated':True})
            if not states:continue
            observed=final['final_freeze_timestamp']
            off=build_shadow(request,final,states=[],observed_at=observed)
            on=build_shadow(request,final,states=states,observed_at=observed)
            effect=learning_effect(on)
            assert off['arms']['PRODUCTION']==on['arms']['PRODUCTION']
            rows.append({'target_race':rid,'request_path':request_path,'final_path':final_path,
                'request_file_sha256':inventory[request_path],'final_file_sha256':inventory[final_path],
                'source_sha256':request['source_snapshot_sha256'],'runner_universe_sha256':on['runner_universe_sha256'],
                'source_freeze_at':request['source_snapshot']['source_freeze_at'],
                'prediction_cutoff':request['prediction_cutoff'],'synthetic_shadow_observed_at':observed,
                'source_states':sources,'checkpoint_learning_input_sha256':digest(states),
                'prediction_input_sha256_on':digest({'request_sha256':digest(request),'learning_states':states}),
                'prediction_input_sha256_off':digest({'request_sha256':digest(request),'learning_states':[]}),
                'shadow_content_sha256_on':on['sha256'],'shadow_content_sha256_off':off['sha256'],
                'effect':effect,'production_arm_unchanged':True})
    for relative,expected in inventory.items():
        assert hashlib.sha256((root/relative).read_bytes()).hexdigest()==expected,relative
    out={'profile':'JRA-LEARNING-ON-OFF-MECHANICAL-20261018',
         'classification':'RETROSPECTIVE_REAL_INPUTS_SIMULATED_STATE_CREATION_AND_SHADOW_TIME_NOT_LIVE_NOT_OOS',
         'time_rule':'same-venue prior RESULT captured_at + 1 second, strictly before target SOURCE freeze; simulated availability only',
         'independent_time_verified':False,'signature_reverified_in_this_probe':False,
         'live_learning_consumption':0,'genuine_forward_oos_races':0,'production_effect':'NONE',
         'policy_fingerprint':digest(POLICY),'input_inventory_file_sha256':inventory,
         'code_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in
             ['scripts/jra_delivery_shadow_acceptance.py','runtime/jra_role_learning_shadow.py','runtime/jra_shadow_checkpoint.py','runtime/post_result_learning.py']},
         'targets':len(rows),'accepted_binding_occurrences':sum(r['effect']['accepted_count'] for r in rows),
         'ticket_changed_targets':sum(r['effect']['added_ticket_count']>0 for r in rows),
         'added_ticket_count':sum(r['effect']['added_ticket_count'] for r in rows),
         'added_virtual_capital':sum(r['effect']['capital_difference'] for r in rows),
         'comparison_limit':'LEARNING_ON rescue adds capital; not the separate equal-budget rank portfolio and not predictive improvement',
         'rows':rows}
    out['sha256']=digest(out)
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--health');p.add_argument('--learning-mechanical',action='store_true');p.add_argument('--output');a=p.parse_args()
    if a.learning_mechanical:
        if not a.output:p.error('--learning-mechanical requires --output')
        report=learning_mechanical()
        Path(a.output).write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
        print(json.dumps({k:report[k] for k in ('classification','targets','accepted_binding_occurrences','ticket_changed_targets','added_ticket_count','added_virtual_capital','sha256')}))
    else:
        if not a.health:p.error('--health is required for the Delivery latency probe')
        run(json.loads(Path(a.health).read_text()))

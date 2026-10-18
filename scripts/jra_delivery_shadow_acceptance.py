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


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--health',required=True);a=p.parse_args();run(json.loads(Path(a.health).read_text()))

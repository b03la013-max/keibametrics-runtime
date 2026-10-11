"""Source-bound CLI for the discovery candidate. Always produces PAPER."""
import argparse, json, pathlib, sys, time
from build_ledger import ROOT, digest, read, timestamp
from selector import risk_coupled_select

def run(request):
    if request.get('family_id')!='JRA' or request.get('static_prediction',{}).get('production_authority') is not True:
        raise ValueError('BLOCKED_NON_PRODUCTION_JRA_LANE')
    source=request.get('source_snapshot',{})
    if not request.get('source_snapshot_sha256') or source.get('source_snapshot_sha256',request['source_snapshot_sha256'])!=request['source_snapshot_sha256']:
        raise ValueError('SOURCE_BINDING_MISMATCH')
    freeze,cutoff=timestamp(source.get('source_freeze_at')),timestamp(source.get('prediction_cutoff'))
    if not freeze or not cutoff or freeze>cutoff:raise ValueError('SOURCE_TIME_INVALID')
    policy=read(ROOT/'profiles/jra_aki_v21_components_20261011_v1.json')
    # Reuse the enacted evidence compiler to validate all twenty components and
    # source lineage. No synthetic provenance is manufactured for old Candidate.
    sys.path.insert(0,str(ROOT/'runtime'))
    from jra_aki_v21_features import compile_features
    full_source={**source,'source_snapshot_sha256':request['source_snapshot_sha256']}
    compiled=compile_features(request,full_source,policy['feature_compiler_policy'])
    scores={str(r['runner_id']):{k:v['value'] for k,v in r['canonical_components'].items()} for r in request['runners']}
    start=time.perf_counter()
    selected=risk_coupled_select(scores,budget=(request.get('capital_policy') or {}).get('race_budget'))
    elapsed=time.perf_counter()-start
    return {'profile':'KM-JRA-AXIS-COUPLED-WIDTH-DISCOVERY-20261011-R1','race_id':request['race_id'],
            'classification':'UNSIGNED_RESEARCH_SHADOW / NOT_FORMAL_FINAL / NO_OOS_CREDIT',
            'source_snapshot_sha256':request['source_snapshot_sha256'],'full20_sha256':digest(request['runners']),
            'selector_sha256':__import__('hashlib').sha256((ROOT/'research/adaptive_width/selector.py').read_bytes()).hexdigest(),
            'mapping_authority':'POSTHOC_RESEARCH_CONSTANTS_NOT_PRODUCTION_AKI_AUTHORITY',
            'compiled_information_gate':compiled['aki_compiler_receipt']['information_gate'],
            'production_change':False,'purchase_authorized':False,'selection':selected,'selector_elapsed_seconds':elapsed}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--request',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
    out=run(read(pathlib.Path(args.request)));pathlib.Path(args.output).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'race_id':out['race_id'],'points':out['selection']['ticket_count'],'decision':out['selection']['decision'],'seconds':out['selector_elapsed_seconds']}))

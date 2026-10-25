"""Read saved Kyoto originals and audit the proposed P0 corrections offline."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/jra_source_runtime')]
from formal_request_validator import ticket_capital_metrics
from formal_temporal_audit import build_temporal_audit
from jra_role_exclusion_audit import build_role_exclusion_audit
from post_result_learning import build_post_result_review,_sha


def audit(root):
    root=Path(root)
    authority=json.loads((root/'profiles/KM_FAMILY_CURRENT_AUTHORITY_20261012_R51.json').read_text())
    rows=[];originals={}
    for no in range(4,13):
        rid=f'KM-JRA-KYO-20261025-R{no:02d}'
        values=[]
        for relative in ('runtime/final_artifacts/'+rid+'.json',
                         'runtime/requests/'+rid+'-LIVE-R1-FORMAL.json',
                         'runtime/results/'+rid+'.json'):
            path=root/relative;raw=path.read_bytes()
            originals[relative]=hashlib.sha256(raw).hexdigest();values.append(json.loads(raw))
        final,request,result=values
        if final['sha256']!=_sha({k:v for k,v in final.items() if k!='sha256'}):
            raise ValueError('ORIGINAL_FINAL_HASH_INVALID:'+rid)
        if result['frozen_prediction_ref']['immutable_final_sha256']!=final['sha256']:
            raise ValueError('RESULT_FINAL_BINDING_INVALID:'+rid)
        roles=build_role_exclusion_audit(request,authority,root)
        temporal=build_temporal_audit(request,request['source_snapshot'],final['final_freeze_timestamp'])
        metrics=ticket_capital_metrics(final['final_ticket']['tickets'])
        review=build_post_result_review(result,final,review_semantics='DECISION_AWARE_V2')
        if metrics['total_investment']!=final['final_ticket']['total_investment']:
            raise ValueError('FINAL_TICKET_TOTAL_MISMATCH:'+rid)
        rows.append({'race_id':rid,'role_replay':roles['status'],'role_cell_count':roles['role_cell_count'],
            'role_explanation_sha256':roles['sha256'],'temporal_audit':temporal,'actual_capital':metrics,
            'original_audit_investment':final['final_prediction_package']['prediction_utility_metrics'].get('total_investment'),
            'legacy_review_sha256':build_post_result_review(result,final)['sha256'],
            'candidate_review_sha256':review['sha256'],
            'candidate_first_material_failure':review['failure_localization']['first_material_failure'],
            'pfs':review['capital']['pfs']})
    if any(hashlib.sha256((root/path).read_bytes()).hexdigest()!=digest for path,digest in originals.items()):
        raise ValueError('ORIGINAL_BYTES_CHANGED')
    out={'classification':'POST_RESULT_CORRECTNESS_AUDIT_NOT_FORWARD_OOS',
        'race_count':len(rows),'runner_count':sum(r['role_cell_count'] for r in rows)//3,
        'role_cells_replayed':sum(r['role_cell_count'] for r in rows),
        'actual_investment':sum(r['actual_capital']['total_investment'] for r in rows),
        'production_effect':'NONE','original_raw_sha256':originals,'races':rows,
        'historical_signed_records_rewritten':0,'forward_oos_increment':0}
    out['sha256']=_sha(out)
    return out


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data-root',type=Path,default=ROOT)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=audit(args.data_root);args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in {'original_raw_sha256','races'}},ensure_ascii=False))


if __name__=='__main__':main()

"""Unsigned mechanical replay, never overwrites or promotes a signed FINAL."""
import argparse
import json
import time
from pathlib import Path
from jra_aki_v21 import apply_authorized_v21
from jra_aki_capital_preflight import verify_aki_ticket_binding
from minimum_efficient_coverage import build_mec_plan
from capital_policy import resolve_capital_policy


def replay(request, authority, root):
    source = {**request['source_snapshot'], 'source_snapshot_sha256':request['source_snapshot_sha256']}
    start = time.perf_counter()
    selected = apply_authorized_v21(request,source,authority,root=root)
    mec = build_mec_plan(selected)
    binding = verify_aki_ticket_binding(selected,mec,source=source,current_authority=authority,root=root)
    return {'classification':'UNSIGNED_POST_RESULT_MECHANICAL_REPLAY / NO_OOS / NOT_PRODUCTION_FINAL',
            'race_id':request['race_id'],'calculation':selected['static_prediction']['aki_jra_v21'],
            'selection':selected['aki_column_selection'],
            'mec':{'ticket_count':mec['ticket_count'],'capital':mec['minimum_required_capital'],
                   'by_type':{b:sum(t['bet_type']==b for t in mec['tickets']) for b in ['EXACTA','TRIFECTA','TRIO']}},
            'binding':binding,'capital':resolve_capital_policy(selected,mec),
            'compiler_receipt':selected['aki_compiler_receipt'],
            'elapsed_seconds':time.perf_counter()-start}


if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--request',required=True)
    ap.add_argument('--authority',required=True)
    ap.add_argument('--output',required=True)
    args=ap.parse_args()
    report=replay(json.loads(Path(args.request).read_text()),json.loads(Path(args.authority).read_text()),Path(__file__).resolve().parents[1])
    Path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'ticket_count':report['mec']['ticket_count'],'capital':report['mec']['capital'],'decision':report['capital']['decision'],'seconds':report['elapsed_seconds']}))

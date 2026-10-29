"""Append a traceable unsigned day-review revision; never edit original states."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from jra_learning_intake import digest

def main():
    directory=ROOT/'runtime/daily_reviews/JRA-2026-10-17'
    closure=json.loads((directory/'execution_assurance_closure.json').read_text())
    matrix=json.loads((directory/'prediction_failure_matrix.json').read_text())
    evidence={r['race_id']:r for r in closure['learning']}
    fingerprint=digest({'learning':closure['learning'],'failures':matrix['rows']})
    now=datetime.now(timezone.utc).isoformat();index=[]
    for row in matrix['rows']:
        p=ROOT/'runtime/learning_states/jra_day_review_20261017'/f"{row['race_id']}.json"
        state=json.loads(p.read_text())
        if state.get('assurance_review',{}).get('evidence_fingerprint')!=fingerprint:
            previous=state['sha256'];state['effective_time']=now
            state['assurance_review']={'previous_review_state_sha256':previous,
                'evidence_fingerprint':fingerprint,'reviewed_at':now,
                'signed_learning_timing':evidence[row['race_id']],
                'first_material_failure':row['first_material_failure'],
                'next_prediction_consumption':'NOT VERIFIED','numeric_application':False,
                'correctness_delivery':'PR #305 / OWNER REVIEW PENDING',
                'forbidden':'No backdating, no historical prediction rewrite, no automatic policy application'}
            state['sha256']=digest({k:v for k,v in state.items() if k!='sha256'})
            p.write_text(json.dumps(state,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
        index.append({'race_id':row['race_id'],'sha256':state['sha256'],'path':str(p.relative_to(ROOT)),
                      'effective_time':state['effective_time']})
    out={'effective_time':max(s['effective_time'] for s in index),'states':index,'recorded':len(index),
        'signed_or_consumed_by_next_race':'NOT VERIFIED','original_learning_states_unchanged':True,
        'production_change_authorized':False,'purpose':'SHADOW review intake readiness; no numerical application'}
    (directory/'next_race_learning_index.json').write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print('Review revisions saved:',len(index))

if __name__=='__main__':main()

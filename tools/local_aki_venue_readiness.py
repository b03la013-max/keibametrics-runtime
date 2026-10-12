"""All LOCAL venue evidence inventory; absence is never synthetic acceptance."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from family_authority_guard import load_authority
from local_physical.nar_source_manifest import LOCAL_BABA_CODES


def assess(corpus):
    _,authority=load_authority()
    routes=json.loads((ROOT/'profiles/venue_chat_routes_20261008_R38.json').read_text())
    route={r['venue_id']:r for r in routes['venues'] if r['family']=='LOCAL'}
    externally_verified={'OHI':2,'FNB':1,'KAW':1}
    venues=[]
    for v in sorted(LOCAL_BABA_CODES):
        rows=[r for r in corpus['races'] if r.get('identity',[None])[0]==v]
        eligible=[r for r in rows if not r.get('acceptance_only') and r.get('replay_status')=='PAPER']
        aliases={tuple(r['identity']) for r in eligible}
        reasons={}
        for r in rows:
            for reason in r.get('missing',[]):reasons[reason]=reasons.get(reason,0)+1
            if r.get('exclusion_reason'):reasons[r['exclusion_reason']]=reasons.get(r['exclusion_reason'],0)+1
        venues.append({'venue_id':v,'name':route[v]['name'],'baba_code':LOCAL_BABA_CODES[v],
            'route_registered':True,'identified_execution_ids':len(rows),'eligible_unique_frozen_source_races':len(aliases),
            'real_external_aki_final_races':externally_verified.get(v,0),'missing_or_hold_reasons':reasons,
            'status':'REAL_REPLAY_PROOF / VENUE_CALIBRATION_PENDING' if externally_verified.get(v) else 'WAITING_ELIGIBLE_SIGNED_PRESTART_SOURCE',
            'prestart_source_replacement_with_postresult_forbidden':True,
            'production_consumption_authorized':False,'unknown_future_oos_count':0})
    return {'status':'NOT_ALL_VENUES_ACCEPTED / EVIDENCE_INVENTORY','current_authority':authority['manifest_id'],
        'production_boundary':authority['family_scoped_authority']['LOCAL']['numerical_consumption_boundary'],
        'required_venue_count':len(venues),'real_external_verified_venues':3,'venues':venues,
        'BAN':'EXCLUDED / SEPARATE_FAMILY','all_venue_completion':False,'automatic_promotion':False}

if __name__=='__main__':
    folder=ROOT/'research/local_aki_columns_20261012'
    x=assess(json.loads((folder/'corpus_audit.json').read_text()))
    (folder/'venue_readiness.json').write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'required':x['required_venue_count'],'verified':x['real_external_verified_venues'],
        'counts':{v['venue_id']:v['eligible_unique_frozen_source_races'] for v in x['venues']}},ensure_ascii=False))

"""Known-result replay: Static ranking with vs without Keibabook bands (NON-PRODUCTION).

Usage: python runtime/analysis/jra_keibabook_impact_replay.py <private keibabook_bands.json>
Baseline recomputation must reproduce the frozen Static ranking."""
import json,sys,glob,copy
sys.path[:0]=['runtime','runtime/jra_source_runtime']
from jra_evidence_to_base_production import load_mapping, build_production_ledger
from jra_index_provenance_builder import zai_win_value
from jra_external_pack_builder import build_packs
from jra_supplemental_evidence_pack import apply_supplemental_evidence_pack
mp=load_mapping('mapping/jra_base_index_evidence_mapping_v1.0_20260921.json')
kb=json.load(open(sys.argv[1]))
packs=build_packs(None,None,ingested_at=kb['captured_at'],keibabook=kb)
def ranking(rid,runners):
    led=build_production_ledger(rid,runners,mp)
    vals={str(rr):{k:v['value'] for k,v in r['base_indices'].items()} for rr,r in led['runners'].items()}
    z={k:zai_win_value(v,'v1.1') for k,v in vals.items()}
    return sorted(z,key=lambda k:-z[k]),vals
out=[]
for p in sorted(glob.glob('runtime/requests/KM-JRA-*-20261115-R*-LIVE-R1-FORMAL.json')):
    req=json.load(open(p));rid=req['race_id']
    if rid not in packs: continue
    try:
        fin=json.load(open(f'runtime/final_artifacts/{rid}.json'));res=json.load(open(f'runtime/results/{rid}.json'))['official_result']['finish_order']
    except FileNotFoundError: continue
    base,bv=ranking(rid,copy.deepcopy(req['runners']))
    froz=[str(x) for x in fin['static_prediction']['ranking']]
    r2=copy.deepcopy(req);r2['prediction_cutoff']=r2.get('prediction_cutoff') or fin['prediction_cutoff']
    # apply KB features only where official/BLOODB did not already provide them
    pk=copy.deepcopy(packs[rid])
    for no,feats in list(pk['runner_features'].items()):
        have=next((r['evidence_features'] for r in r2['runners'] if str(r['runner_id'])==no),{})
        for f in list(feats):
            if f in have: feats.pop(f)
    from jra_external_pack_builder import sha
    pk['pack_sha256']=sha({k:v for k,v in pk.items() if k!='pack_sha256'})
    r2,_=apply_supplemental_evidence_pack(r2,pk,mp)
    new,nv=ranking(rid,r2['runners'])
    w=str(res[0])
    out.append({'race':rid[7:],'reproduces_frozen':base==froz,'winner_rank_before':base.index(w)+1,'winner_rank_after':new.index(w)+1,
                'top3_before':sum(str(x) in base[:3] for x in res[:3]),'top3_after':sum(str(x) in new[:3] for x in res[:3]),
                'TRI_mean_before':round(sum(v['TRI'] for v in bv.values())/len(bv),1),'TRI_mean_after':round(sum(v['TRI'] for v in nv.values())/len(nv),1)})
print(json.dumps(out,ensure_ascii=False))

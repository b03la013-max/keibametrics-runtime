from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PROD=json.loads((ROOT/"mapping/jra_base_index_evidence_mapping_v1.0_20260921.json").read_text())
SHADOW=json.loads((ROOT/"mapping/jra_base_index_semantic_shadow_v0.1_20260921.json").read_text())
OUTCOMES=json.loads((ROOT/"runtime/shadow/hsn_20260921_r10_r12_outcomes.json").read_text())
REQS=[
 ROOT/"runtime/requests/KM-JRA-HSN-20260921-R10.json",
 ROOT/"runtime/requests/KM-JRA-HSN-20260921-R11.json",
 ROOT/"runtime/requests/KM-JRA-HSN-20260921-R12.json",
]
BASE=["HPI","SSI","CFI","RFI","BVI","JTI","CSI","TRI","BWI","GCI","PRI","KGI","VMI"]
METRICS=["TPI","ZAI_WIN","ZAI_PLACE","F3S","T3I"]

def profile(r):
    n=int(r.get("career_starts",0 if r.get("newcomer") else 4))
    if n<=0:return "NEWCOMER"
    if n<=3:return "LOW_CAREER"
    return "ESTABLISHED"

def score(r,f):
    e=(r.get("evidence_features") or {}).get(f)
    if not e:return None
    return float(PROD["category_scale"][str(e["category"]).upper()])

def wmean(r,weights):
    n=c=0.0
    for f,w in weights.items():
        s=score(r,f)
        if s is None:continue
        n+=s*float(w); c+=float(w)
    if c<=0: raise ValueError(f"NO_COVERAGE:{r['runner_id']}")
    return n/c,c

def dcr(r,p):
    total=0.0
    feats=r.get("evidence_features") or {}
    for spec in PROD["dcr"].values():
        feat=spec.get("feature")
        e=feats.get(feat) if feat else None
        if e:
            total+=float(spec["max_points"])*float(PROD["category_scale"][str(e["category"]).upper()])/100.0
            continue
        fb=spec.get("newcomer_fallback_feature")
        if p=="NEWCOMER" and fb and feats.get(fb):
            e=feats[fb]
            total+=float(spec["max_points"])*float(PROD["category_scale"][str(e["category"]).upper()])/100.0
            continue
        if p=="NEWCOMER" and "newcomer_default_points" in spec:
            total+=float(spec["newcomer_default_points"])
            continue
        raise ValueError(f"DCR_UNRESOLVED:{r['runner_id']}")
    return total

def condition_weak_set(req):
    surf=str((req.get("race") or {}).get("surface","")).lower()
    dist=float((req.get("race") or {}).get("distance",0) or 0)
    if surf=="dirt" and dist<=1600:
        return SHADOW["weak_penalty_sets"]["DIRT_SPRINT_MILE"]["indices"]
    if surf=="turf" and dist>=1800:
        return SHADOW["weak_penalty_sets"]["TURF_MIDDLE_LONG"]["indices"]
    return SHADOW["weak_penalty_sets"]["DEFAULT"]["indices"]

def derive(v,dcr_score,weak_set):
    ordered=sorted(v[x] for x in weak_set)
    weak=.40*max(0.0,60.0-ordered[0])+.20*max(0.0,65.0-ordered[1])
    tpi_base=(v["HPI"]*.15+v["SSI"]*.14+v["CFI"]*.10+v["RFI"]*.10+v["BVI"]*.05+
              v["JTI"]*.06+v["CSI"]*.05+v["TRI"]*.07+v["BWI"]*.06+v["GCI"]*.08+
              v["PRI"]*.08+v["KGI"]*.06)
    tpi=50.0+(tpi_base-weak-50.0)*(.70+.30*dcr_score/100.0)
    zw=(v["HPI"]*.20+v["SSI"]*.17+v["CFI"]*.10+v["RFI"]*.08+v["JTI"]*.05+
        v["CSI"]*.05+v["TRI"]*.05+v["BWI"]*.05+v["GCI"]*.08+v["PRI"]*.12+v["KGI"]*.05)
    zp=(v["HPI"]*.16+v["SSI"]*.14+v["CFI"]*.10+v["RFI"]*.14+v["JTI"]*.05+
        v["CSI"]*.06+v["TRI"]*.05+v["BWI"]*.08+v["GCI"]*.08+v["PRI"]*.08+v["KGI"]*.06)
    sri=zp*.45+tpi*.25+v["RFI"]*.10+v["PRI"]*.08+v["KGI"]*.07+v["BWI"]*.05
    scenario=v["PRI"]*.35+v["CFI"]*.25+v["GCI"]*.20+v["SSI"]*.12+v["RFI"]*.08
    f3s=zw*.30+zp*.25+tpi*.25+sri*.15+scenario*.05
    t3i=zp*.35+tpi*.20+v["RFI"]*.15+v["PRI"]*.10+v["GCI"]*.08+v["CFI"]*.07+v["VMI"]*.05
    return {"TPI":tpi,"ZAI_WIN":zw,"ZAI_PLACE":zp,"SRI":sri,"F3S":f3s,"T3I":t3i,"weak_penalty":weak}

def weights_for(p,arm):
    if arm=="CONTROL":
        return PROD["index_profiles"][p]
    if p=="NEWCOMER":
        return PROD["index_profiles"][p]
    w={}
    for idx in BASE:
        if idx in SHADOW["index_profiles"][p]:
            w[idx]=SHADOW["index_profiles"][p][idx]
        else:
            w[idx]=PROD["index_profiles"][p][idx]
    return w

def compute(req,arm):
    rows=[]
    for r in req["runners"]:
        p=profile(r); v={}; cov={}
        ww=weights_for(p,arm)
        for idx in BASE:
            z,c=wmean(r,ww[idx])
            v[idx]=z; cov[idx]=c
        rows.append({"runner":r,"profile":p,"v":v,"coverage":cov,"dcr":dcr(r,p)})
    if arm in {"PRI_REL","FULL"}:
        ordered=sorted(rows,key=lambda x:x["v"]["PRI"],reverse=True)
        n=len(ordered)
        rel={str(x["runner"]["runner_id"]):(50.0 if n==1 else 100.0*(n-1-i)/(n-1)) for i,x in enumerate(ordered)}
        for x in rows:
            rid=str(x["runner"]["runner_id"])
            x["v"]["PRI"]=.75*x["v"]["PRI"]+.25*rel[rid]
            x["pri_field_percentile"]=rel[rid]
    weak=condition_weak_set(req) if arm in {"COND_WEAK","FULL"} else PROD["weak_penalty_major_indices"]
    for x in rows:
        if arm in {"VMI","PRI_REL","COND_WEAK","FULL"}:
            temp=dict(x["v"]); temp["VMI"]=50.0
            pre=derive(temp,x["dcr"],weak)["TPI"]
            mr=score(x["runner"],"market_rank")
            x["v"]["VMI"]=max(0.0,min(100.0,50.0+pre-(mr if mr is not None else 50.0)))
        x["derived"]=derive(x["v"],x["dcr"],weak)
        cv=list(x["coverage"].values())
        x["coverage_mean"]=sum(cv)/len(cv)
        x["coverage_min"]=min(cv)
    return rows

def rank_map(rows,metric):
    return {str(x["runner"]["runner_id"]):i+1 for i,x in enumerate(sorted(rows,key=lambda y:y["derived"][metric],reverse=True))}

per_race={}
agg={arm:{m:[] for m in METRICS} for arm in ["CONTROL","SEMANTIC","VMI","PRI_REL","COND_WEAK","FULL"]}
for path in REQS:
    req=json.loads(path.read_text())
    rid=req["race_id"]
    actual=OUTCOMES["races"][rid]["top3"]
    per_race[rid]={"actual_top3":actual,"arms":{}}
    for arm in agg:
        rows=compute(req,arm)
        block={}
        for m in METRICS:
            rm=rank_map(rows,m)
            ranks=[rm[str(x)] for x in actual]
            block[m]=ranks
            agg[arm][m].extend(ranks)
        per_race[rid]["arms"][arm]=block

aggregate={}
for arm,metrics in agg.items():
    aggregate[arm]={}
    for m,ranks in metrics.items():
        aggregate[arm][m]={
            "mean_actual_top3_rank":round(sum(ranks)/len(ranks),6),
            "top3_hits":sum(1 for x in ranks if x<=3),
            "top5_hits":sum(1 for x in ranks if x<=5),
            "n":len(ranks),
        }

out={
 "experiment_id":"KM-JRA-BASE-INDEX-SEMANTIC-SHADOW-20260921-R1",
 "status":"SHADOW / DEVELOPMENT-REPLAY / NON-PRODUCTION",
 "production_control":"JRA-EVIDENCE-TO-BASE-MAPPING-v1.0-PRODUCTION-20260921",
 "shadow_mapping":SHADOW["mapping_id"],
 "races":[str(x.relative_to(ROOT)) for x in REQS],
 "outcomes":OUTCOMES["evaluation_id"],
 "arms":{
   "CONTROL":"production v1.0",
   "SEMANTIC":"responsibility-boundary cleanup only",
   "VMI":"SEMANTIC + value-mismatch VMI",
   "PRI_REL":"VMI + race-relative PRI",
   "COND_WEAK":"VMI + condition-specific weak set",
   "FULL":"SEMANTIC + VMI + race-relative PRI + condition-specific weak set + separate coverage diagnostics",
 },
 "per_race":per_race,
 "aggregate":aggregate,
 "promotion_decision":"REJECT",
 "promotion_reason":"Only three same-day development races; FULL is mixed and regresses HSN R11 T3I. Unknown-future OOS and downstream ticket/PFS comparison are absent.",
}
print(json.dumps(out,ensure_ascii=False,sort_keys=True))

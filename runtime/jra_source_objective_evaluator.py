from __future__ import annotations

import copy
import datetime as dt
import hashlib
import json
import math
import statistics
from typing import Any, Dict, List

PROFILE = "KM-JRA-SOURCE-OBJECTIVE-EVALUATOR-v0.1-20260926"
STATUS = "SHADOW / NON-PRODUCTION / OBJECTIVE-SOURCE-DIAGNOSTIC / NO-AUTO-PROMOTION"
BASE = ["HPI","SSI","CFI","RFI","BVI","JTI","CSI","TRI","BWI","GCI","PRI","KGI","VMI"]
DERIVED = ["DCR","TPI","ZAI_WIN","ZAI_PLACE","SRI","F3S","T3I"]
RECENCY = [0.40,0.30,0.20,0.10]
NEUTRAL = 64.0

def _sha(x:Any)->str:
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()

def _clamp(x:float,lo:float=0.0,hi:float=100.0)->float:
    return max(lo,min(hi,float(x)))

def _mean(xs):
    a=[float(x) for x in xs if x is not None]
    return None if not a else sum(a)/len(a)

def _std(xs):
    a=[float(x) for x in xs if x is not None]
    return None if len(a)<2 else statistics.pstdev(a)

def _weighted(xs):
    total=weight=0.0
    for i,x in enumerate(list(xs)[:4]):
        if x is None: continue
        w=RECENCY[i]
        total += float(x)*w
        weight += w
    return None if weight<=0 else total/weight

def _finish_score(finish,field):
    if finish is None or field is None or int(field)<=1: return None
    return _clamp(100.0*(int(field)-int(finish))/(int(field)-1))

def _class_score(text):
    t=str(text or "").upper().replace(" ","")
    table=[
      (("GⅠ","GI","G1","JPNⅠ","JPNI","JPN1"),96.0),
      (("GⅡ","GII","G2","JPNⅡ","JPNII","JPN2"),92.0),
      (("GⅢ","GIII","G3","JPNⅢ","JPNIII","JPN3"),88.0),
      (("リステッド","L"),84.0),
      (("オープン","OPEN"),82.0),
      (("3勝クラス","３勝クラス"),78.0),
      (("2勝クラス","２勝クラス"),74.0),
      (("1勝クラス","１勝クラス"),70.0),
      (("未勝利","新馬"),54.0),
    ]
    for keys,val in table:
        if any(k in t for k in keys): return val
    return None

def _interval_score(days):
    if days is None:return None
    d=int(days)
    if 14<=d<=42:return 85.0
    if 8<=d<=70:return 72.0
    if 71<=d<=120:return 60.0
    if d<8:return 58.0
    return 52.0

def _positions(raw):
    if isinstance(raw,list):
        return [int(x) for x in raw if str(x).isdigit()]
    s=str(raw or "")
    if not s:return []
    # Current JRA detail parser also stores a compact raw sequence. For compact
    # values we only use one-digit calls; ambiguous >=10 calls remain unusable.
    if any(ch in s for ch in "-, /"):
        import re
        return [int(x) for x in re.findall(r"\d+",s)]
    if s.isdigit() and all(int(ch)<=9 for ch in s):
        return [int(ch) for ch in s]
    return []

def _going_group(x):
    s=str(x or "")
    if s in {"重","不良"}:return "WET"
    if s=="稍重":return "INTERMEDIATE"
    if s=="良":return "DRY"
    return "UNKNOWN"

def _same_going(a,b):
    ga,gb=_going_group(a),_going_group(b)
    if "UNKNOWN" in {ga,gb}:return False
    return ga==gb or ({ga,gb}<={"WET","INTERMEDIATE"})

def _category(score,mapping):
    anchors=mapping["category_scale"]
    return min(anchors,key=lambda k:abs(float(anchors[k])-float(score)))

def _feature(score,feature,refs,fact,mapping,*,coverage=1.0,missing=False,raw=None,authority="JRA_OFFICIAL_OBJECTIVE_CANDIDATE"):
    sc=NEUTRAL if score is None else _clamp(score)
    return {
      "feature":feature,
      "score":round(sc,6),
      "category":_category(sc,mapping),
      "candidate_rule_id":"KM-JRA-SOURCE-OBJECTIVE-"+feature.upper().replace("_","-")+"-v0.1",
      "evidence_refs":sorted(set(str(x) for x in refs if x)),
      "source_fact":str(fact),
      "coverage":round(_clamp(float(coverage)*100.0)/100.0,6),
      "missing":bool(missing or score is None),
      "candidate_only":True,
      "production_authority":False,
      "prediction_authority":False,
      "authority":authority,
      "raw_metric":raw,
    }

def _all_mapping_features(mapping):
    out=set()
    for prof in mapping["index_profiles"].values():
        for weights in prof.values():out.update(weights)
    for d in mapping.get("dcr",{}).values():
        if d.get("feature"):out.add(d["feature"])
        if d.get("newcomer_fallback_feature"):out.add(d["newcomer_fallback_feature"])
    return out

def _profile(starts):
    if starts is None:return None
    n=int(starts)
    return "NEWCOMER" if n<=0 else ("LOW_CAREER" if n<=3 else "ESTABLISHED")

def _detail_map(source):
    d=source.get("jra_official_race_card_detail") or {}
    return {str(x.get("runner_id") or x.get("horse_no")):x for x in d.get("runners") or []}

def _history_map(source):
    d=source.get("jra_official_horse_history") or {}
    return {str(k):v for k,v in (d.get("runners") or {}).items()}

def _current_going(source):
    d=source.get("jra_official_race_card_detail") or {}
    env=d.get("race_environment") or {}
    if env.get("going"):return env.get("going")
    ev=source.get("normalized_evidence") or {}
    for k in ("track_condition","going","race_track_condition"):
        v=ev.get(k)
        if isinstance(v,dict) and v.get("value"):return v.get("value")
    return None

def _recent_metrics(x,source,history=None):
    runs=list(x.get("recent_runs") or [])
    history_runs=list((history or {}).get("runs") or [])
    all_runs=history_runs if history_runs else runs
    ctx=source.get("jra_race_context") or {}
    venue=str(ctx.get("venue_name") or "")
    distance=ctx.get("distance_m")
    surface=ctx.get("surface")
    going=_current_going(source)
    finish_scores=[_finish_score(r.get("finish"),r.get("field_size")) for r in runs]
    class_scores=[_class_score(r.get("race_class_text")) for r in runs]
    margin_scores=[]
    first_scores=[]; last_scores=[]; progression=[]; nonfront_perf=[]; front_perf=[]
    for r,fs in zip(runs,finish_scores):
        m=r.get("margin")
        if m is None: margin_scores.append(None)
        else:
            mv=float(m)
            margin_scores.append(100.0 if mv<=0 else 100.0*math.exp(-mv/2.0))
        pos=_positions(r.get("passing_positions") or r.get("passing_positions_raw"))
        n=r.get("field_size")
        if pos and n and int(n)>1:
            a=_finish_score(pos[0],n); z=_finish_score(pos[-1],n)
            first_scores.append(a); last_scores.append(z)
            progression.append(_clamp(50+(z-a)/2))
            if pos[0]<=3:front_perf.append(fs)
            else:nonfront_perf.append(fs)
        else:
            first_scores.append(None); last_scores.append(None); progression.append(None)
    all_finish=[_finish_score(r.get("finish"),r.get("field_size")) for r in all_runs]
    same_course=[(r,all_finish[i]) for i,r in enumerate(all_runs) if venue and str(r.get("venue") or "")==venue]
    same_distance=[(r,all_finish[i]) for i,r in enumerate(all_runs) if distance is not None and r.get("distance_m")==distance]
    same_surface=[(r,all_finish[i]) for i,r in enumerate(all_runs) if surface and str(r.get("surface") or "")==str(surface)]
    same_going_rows=[(r,all_finish[i]) for i,r in enumerate(all_runs) if going and _same_going(r.get("going"),going)]
    race_date=str((source.get("source_race_context") or {}).get("race_date") or "")
    rotation=None
    if runs and runs[0].get("date") and race_date:
        try:rotation=(dt.date.fromisoformat(race_date)-dt.date.fromisoformat(str(runs[0]["date"]))).days
        except Exception:rotation=None
    bws=[r.get("body_weight") for r in all_runs if r.get("body_weight") is not None]
    return {
      "runs":runs,"history_runs":all_runs,"finish_scores":finish_scores,"class_scores":class_scores,"margin_scores":margin_scores,
      "first_scores":first_scores,"last_scores":last_scores,"progression":progression,
      "front_perf":front_perf,"nonfront_perf":nonfront_perf,
      "same_course":same_course,"same_distance":same_distance,"same_surface":same_surface,"same_going":same_going_rows,
      "rotation_days":rotation,"bodyweights":bws,
    }

def _rank_score(value,values,*,lower_better=False):
    xs=[float(x) for x in values if x is not None]
    if value is None or len(xs)<2:return None
    v=float(value)
    # Mid-rank percentile, stable under ties.
    better=sum(1 for x in xs if (x<v if lower_better else x>v))
    equal=sum(1 for x in xs if x==v)
    rank=better+(equal-1)/2
    return _clamp(100.0*(len(xs)-1-rank)/(len(xs)-1))

def _missing(feature,mapping,reason):
    return _feature(None,feature,[],reason,mapping,coverage=0.0,missing=True,raw=None,authority="MISSING_SOURCE")

def _build_runner_features(rid,x,metrics,source,mapping,field_context):
    ref=source.get("jra_official_race_card_detail_sha256")
    uref=source.get("jra_official_runner_universe_sha256")
    refs=[ref,uref,f"JRA:DETAIL:{rid}"]
    features={}
    def put(name,score,fact,coverage=1.0,raw=None):
        features[name]=_feature(score,name,refs,fact,mapping,coverage=coverage,raw=raw)
    runs=metrics["runs"]; fs=metrics["finish_scores"]
    put("recent_performance",_weighted(fs),f"recency-weighted normalized finish scores={fs}",min(1,len(runs)/4),fs)
    put("official_recent_quality",_weighted(fs),f"official recent normalized finish scores={fs}",min(1,len(runs)/4),fs)
    top3=sum(1 for r in runs if r.get("finish") is not None and int(r["finish"])<=3)
    put("recent_consistency",100.0*top3/len(runs) if runs else None,f"top3={top3}/{len(runs)}",min(1,len(runs)/4),{"top3":top3,"n":len(runs)})
    put("class_performance",_weighted(metrics["class_scores"]),f"recent class ordinals={metrics['class_scores']}",min(1,len([x for x in metrics["class_scores"] if x is not None])/4),metrics["class_scores"])
    opp=[]
    for i,r in enumerate(runs):
        cs=metrics["class_scores"][i]
        n=r.get("field_size")
        if cs is None or n is None:opp.append(None)
        else:opp.append(_clamp(.75*cs+.25*_clamp(50+(int(n)-8)*4)))
    put("opponent_strength",_weighted(opp),f"class+field opponent proxy={opp}",min(1,len([x for x in opp if x is not None])/4),opp)
    put("finish_margin",_weighted(metrics["margin_scores"]),f"winner-margin exponential scores={metrics['margin_scores']}",min(1,len([x for x in metrics["margin_scores"] if x is not None])/4),metrics["margin_scores"])
    st=_std(fs)
    put("speed_reliability",None if st is None else _clamp(100-1.6*st),f"normalized-finish std={st}",min(1,len([x for x in fs if x is not None])/3),st)
    cmean=_mean([r.get("final3f") for r in runs if r.get("final3f") is not None])
    put("closing_quality",_rank_score(cmean,field_context["closing_means"],lower_better=True),f"field-relative mean final3F={cmean}",min(1,len([r for r in runs if r.get("final3f") is not None])/3),cmean)
    def perf(rows):
        vals=[v for _,v in rows if v is not None]
        return _mean(vals),min(1,len(vals)/3)
    v,c=perf(metrics["same_course"]); put("same_course_fit",v,"same-course recent normalized finish",c,v)
    v,c=perf(metrics["same_distance"]); put("same_distance_fit",v,"same-distance recent normalized finish",c,v)
    vals=[z for z in [perf(metrics["same_course"])[0],perf(metrics["same_distance"])[0]] if z is not None]
    put("same_course_distance_quality",_mean(vals),"same-course/distance combined recent quality",min(1,(len(metrics["same_course"])+len(metrics["same_distance"]))/4),vals)
    v,c=perf(metrics["same_surface"]); put("surface_fit",v,"same-surface recent normalized finish",c,v)
    v,c=perf(metrics["same_going"]); put("going_fit",v,"same-going-group recent normalized finish",c,v)
    put("rotation_fit",_interval_score(metrics["rotation_days"]),f"days since last start={metrics['rotation_days']}",1 if metrics["rotation_days"] is not None else 0,metrics["rotation_days"])
    put("layoff_readiness",_interval_score(metrics["rotation_days"]),f"days since last start={metrics['rotation_days']}",1 if metrics["rotation_days"] is not None else 0,metrics["rotation_days"])
    bw=metrics["bodyweights"]; bwstd=_std(bw)
    put("bodyweight_history_quality",None if bwstd is None else _clamp(100-2*bwstd),f"recent bodyweight std={bwstd}",min(1,len(bw)/3),bwstd)
    cur=x.get("current_body_weight")
    if cur is not None and bw:
        lo,hi=min(bw),max(bw)
        dist=0 if lo<=cur<=hi else min(abs(cur-lo),abs(cur-hi))
        score=88 if dist==0 else 74 if dist<=5 else 64 if dist<=10 else 54
    else:score=None
    put("bodyweight_range_fit",score,f"current={cur}; recent range={min(bw) if bw else None}-{max(bw) if bw else None}",min(1,len(bw)/3),{"current":cur,"history":bw})
    delta=x.get("current_body_weight_change")
    if delta is None:bd=None
    else:
        a=abs(float(delta)); bd=82 if a<=4 else 74 if a<=8 else 64 if a<=12 else 54 if a<=16 else 44
    put("bodyweight_delta_fit",bd,f"official current bodyweight delta={delta}",1 if delta is not None else 0,delta)
    w=x.get("assigned_weight")
    put("weight_load_fit",_rank_score(w,field_context["weights"],lower_better=True),f"field-relative assigned weight={w}",1 if w is not None else 0,w)
    pop=x.get("popularity_rank")
    put("market_rank",_rank_score(pop,field_context["popularities"],lower_better=True),f"official popularity rank={pop}",1 if pop is not None else 0,pop)
    first=metrics["first_scores"]; prog=metrics["progression"]
    put("gate_quality",_weighted(first),f"first-call normalized positions={first}",min(1,len([z for z in first if z is not None])/4),first)
    put("dash_quality",_weighted(first),f"early-position normalized scores={first}",min(1,len([z for z in first if z is not None])/4),first)
    put("position_quality",_weighted(metrics["last_scores"]),f"last-call normalized positions={metrics['last_scores']}",min(1,len([z for z in metrics["last_scores"] if z is not None])/4),metrics["last_scores"])
    pst=_std(first)
    put("position_reproducibility",None if pst is None else _clamp(100-1.5*pst),f"early-position std={pst}",min(1,len([z for z in first if z is not None])/3),pst)
    put("pressure_resilience",_mean(metrics["nonfront_perf"]),f"performance when first call >3={metrics['nonfront_perf']}",min(1,len(metrics["nonfront_perf"])/3),metrics["nonfront_perf"])
    put("progression_ability",_weighted(prog),f"early-to-late progression scores={prog}",min(1,len([z for z in prog if z is not None])/4),prog)
    # Similar geometry / direction from current venue and recent venue are intentionally
    # conservative: only same-course evidence is used until a venue-canon geometry
    # binding is supplied.
    if "same_course_fit" in features and not features["same_course_fit"]["missing"]:
        for n in ("similar_geometry_fit","turn_direction_fit","course_geometry_fit"):
            features[n]=copy.deepcopy(features["same_course_fit"])
            features[n]["feature"]=n
            features[n]["candidate_rule_id"]="KM-JRA-SOURCE-OBJECTIVE-"+n.upper().replace("_","-")+"-v0.1"
            features[n]["source_fact"]="Conservative same-course proxy pending explicit Venue Canon geometry binding."
    # Relative draw/style proxy uses current frame/horse number and early-position history.
    early=_weighted(first); no=x.get("horse_no")
    n=field_context["field_size"]
    if early is not None and no and n>1:
        inner=100*(n-int(no))/(n-1)
        draw=_clamp(64+((early-50)/50)*((inner-50)/2))
    else:draw=None
    put("draw_course_fit",draw,f"candidate draw/style interaction early={early}, horse_no={no}/{n}",0.5 if draw is not None else 0,{"early":early,"horse_no":no})
    # Horse-jockey continuity can be evaluated only when recent jockey was parsed.
    curj=str(x.get("jockey") or "")
    hrows=metrics.get("history_runs") or runs
    hfinish=[_finish_score(r.get("finish"),r.get("field_size")) for r in hrows]
    jrows=[(r,hfinish[i]) for i,r in enumerate(hrows) if curj and str(r.get("jockey") or "")==curj]
    put("jockey_horse_fit",_mean([v for _,v in jrows]),f"same jockey recent runs={len(jrows)}",min(1,len(jrows)/3),[v for _,v in jrows])
    # Current official detail contains identities but not population statistics.
    # All such features remain explicit missingness.
    all_features=_all_mapping_features(mapping)
    unresolved_reasons={
      "recent_speed":"No normalized speed figure is published in the official detail source.",
      "pace_resilience":"No registered production pace-resilience evaluator is encoded for raw calls.",
      "pedigree_surface":"Pedigree identities exist but no historical population fit table is source-verified.",
      "pedigree_distance":"Pedigree identities exist but no historical population fit table is source-verified.",
      "pedigree_class":"Pedigree identities exist but no historical population fit table is source-verified.",
      "physical_pedigree_fit":"Pedigree identities exist but no historical population fit table is source-verified.",
      "maternal_class_signal":"Maternal identities exist but no historical population fit table is source-verified.",
      "sire_track_signal":"Sire identity exists but no historical track-rate table is source-verified.",
      "sire_newcomer_signal":"Sire identity exists but no historical newcomer-rate table is source-verified.",
      "sprint_pedigree":"Pedigree identity exists but no sprint-rate table is source-verified.",
      "jockey_quality":"Jockey identity exists but no signed quantitative jockey-stat adapter is bound.",
      "jockey_venue_fit":"No signed jockey-by-venue quantitative adapter is bound.",
      "jockey_style_fit":"No registered jockey-style quantitative adapter is bound.",
      "trainer_jockey_fit":"No signed trainer-jockey quantitative adapter is bound.",
      "trainer_quality":"Trainer identity exists but no signed quantitative trainer-stat adapter is bound.",
      "stable_trainer_class":"Trainer identity exists but no signed quantitative trainer-stat adapter is bound.",
      "stable_readiness":"No authorized stable-comment source is bound.",
      "target_intent":"No authorized stable-comment source is bound.",
      "stable_comment_state":"No authorized stable-comment source is bound.",
      "preparation_continuity":"No signed training/stable continuity adapter is bound.",
      "workout_capability":"No signed workout source is bound.",
      "workout_speed":"No signed workout source is bound.",
      "workout_partner_level":"No signed workout source is bound.",
      "workout_finish":"No signed workout source is bound.",
      "workout_consistency":"No signed workout source is bound.",
      "workout_load":"No signed workout source is bound.",
      "training_comments_quality":"No signed workout/comment source is bound.",
      "physical_readiness":"Bodyweight alone is insufficient for full physical-readiness authority.",
      "body_condition_comment":"No authorized paddock/body-condition comment source is bound.",
      "equipment_effect":"No equipment history adapter is bound.",
      "same_day_track_fit":"Same-day bias is shadow until a horse-style binding evaluator is OOS-validated.",
      "track_bias_fit":"Same-day bias is shadow until a horse-style binding evaluator is OOS-validated.",
      "weather_fit":"JMA current weather has no horse-specific historical weather fit adapter.",
      "forward_speed_comment":"No authorized comment/pace-map source is bound.",
      "market_stability":"Only one official market snapshot is available in this Source artifact.",
      "market_mismatch":"Requires a promoted model-vs-market evaluator.",
      "expert_support":"No authorized expert-source adapter is bound.",
      "external_index_support":"TSL remains third-party shadow and is excluded from objective Production candidate.",
      "hidden_class":"No promoted hidden-class evaluator is encoded.",
      "distance_fit":"Same-distance evidence is already represented; no independent pedigree/history blend evaluator is promoted.",
    }
    for f in sorted(all_features):
        if f not in features:
            features[f]=_missing(f,mapping,unresolved_reasons.get(f,"No deterministic source evaluator is currently authorized for this feature."))
    return features

def _candidate_indices(features,profile,mapping):
    out={}
    minimum=float(mapping["profiles"][profile]["minimum_index_coverage_weight"])
    for idx,weights in mapping["index_profiles"][profile].items():
        obs_num=obs_w=diag_num=0.0
        comps=[]
        for f,w in weights.items():
            spec=features[f]; ww=float(w)
            diag_num += spec["score"]*ww
            if not spec["missing"]:
                obs_num += spec["score"]*ww; obs_w += ww
            comps.append({"feature":f,"weight":ww,"score":spec["score"],"missing":spec["missing"],"coverage":spec["coverage"]})
        out[idx]={
          "observed_score":round(obs_num/obs_w,6) if obs_w>0 else None,
          "diagnostic_neutralized_score":round(diag_num/sum(float(w) for w in weights.values()),6),
          "observed_weight":round(obs_w,6),
          "minimum_required_weight":minimum,
          "coverage_pass":obs_w+1e-12>=minimum,
          "components":comps,
        }
    return out

def _derived(base,features,mapping):
    vals={k:base[k]["diagnostic_neutralized_score"] for k in BASE}
    def fscore(name): return features[name]["score"]
    dcr=25*fscore("official_recent_quality")/100 + 20*fscore("same_course_distance_quality")/100 + 15*fscore("training_comments_quality")/100 + 15*fscore("bodyweight_history_quality")/100 + 15*fscore("same_day_track_fit")/100 + 10*fscore("market_stability")/100
    major=sorted(vals[x] for x in mapping["weak_penalty_major_indices"])
    l1,l2=major[0],major[1]
    weak=.40*max(0,60-l1)+.20*max(0,65-l2)
    factor=.70+.30*dcr/100
    tpi_base=vals["HPI"]*.15+vals["SSI"]*.14+vals["CFI"]*.10+vals["RFI"]*.10+vals["BVI"]*.05+vals["JTI"]*.06+vals["CSI"]*.05+vals["TRI"]*.07+vals["BWI"]*.06+vals["GCI"]*.08+vals["PRI"]*.08+vals["KGI"]*.06
    tpi=50+(tpi_base-weak-50)*factor
    zw=vals["HPI"]*.20+vals["SSI"]*.17+vals["CFI"]*.10+vals["RFI"]*.08+vals["JTI"]*.05+vals["CSI"]*.05+vals["TRI"]*.05+vals["BWI"]*.05+vals["GCI"]*.08+vals["PRI"]*.12+vals["KGI"]*.05
    zp=vals["HPI"]*.16+vals["SSI"]*.14+vals["CFI"]*.10+vals["RFI"]*.14+vals["JTI"]*.05+vals["CSI"]*.06+vals["TRI"]*.05+vals["BWI"]*.08+vals["GCI"]*.08+vals["PRI"]*.08+vals["KGI"]*.06
    sri=zp*.45+tpi*.25+vals["RFI"]*.10+vals["PRI"]*.08+vals["KGI"]*.07+vals["BWI"]*.05
    scenario=vals["PRI"]*.35+vals["CFI"]*.25+vals["GCI"]*.20+vals["SSI"]*.12+vals["RFI"]*.08
    f3s=zw*.30+zp*.25+tpi*.25+sri*.15+scenario*.05
    t3i=zp*.35+tpi*.20+vals["RFI"]*.15+vals["PRI"]*.10+vals["GCI"]*.08+vals["CFI"]*.07+vals["VMI"]*.05
    return {k:round(v,6) for k,v in {"DCR":dcr,"TPI":tpi,"ZAI_WIN":zw,"ZAI_PLACE":zp,"SRI":sri,"F3S":f3s,"T3I":t3i}.items()}

def build_source_objective_candidate(source_artifact:Dict[str,Any],request_runners:List[Dict[str,Any]],mapping:Dict[str,Any])->Dict[str,Any]:
    detail=_detail_map(source_artifact)
    history=_history_map(source_artifact)
    if not detail:
        return {"profile":PROFILE,"status":STATUS,"available":False,"reason":"JRA_OFFICIAL_RACE_CARD_DETAIL_MISSING","production_effect":"NONE"}
    runners=[r for r in request_runners or []]
    byid={str(r.get("runner_id") or r.get("horse_no")):r for r in runners}
    metrics={rid:_recent_metrics(x,source_artifact,history.get(rid)) for rid,x in detail.items()}
    closing_means=[_mean([z.get("final3f") for z in m["runs"] if z.get("final3f") is not None]) for m in metrics.values()]
    weights=[x.get("assigned_weight") for x in detail.values()]
    pops=[x.get("popularity_rank") for x in detail.values()]
    field_context={"field_size":len(detail),"closing_means":closing_means,"weights":weights,"popularities":pops}
    out={}
    for rid,x in detail.items():
        r=byid.get(rid,{})
        starts=((x.get("career_record") or {}).get("starts"))
        if starts is None:starts=r.get("career_starts")
        p=_profile(starts)
        if p is None:
            out[rid]={"runner_name":x.get("horse_name"),"error":"CAREER_STARTS_UNKNOWN"}
            continue
        feats=_build_runner_features(rid,x,metrics[rid],source_artifact,mapping,field_context)
        base=_candidate_indices(feats,p,mapping)
        drv=_derived(base,feats,mapping)
        observed=sum(1 for z in feats.values() if not z["missing"])
        out[rid]={
          "runner_name":x.get("horse_name"),
          "profile":p,
          "feature_count":len(feats),
          "observed_feature_count":observed,
          "missing_feature_count":len(feats)-observed,
          "features":feats,
          "base_indices":base,
          "derived_indices":drv,
          "all_20_diagnostic_values":{**{k:v["diagnostic_neutralized_score"] for k,v in base.items()},**drv},
          "formal_production_ready":all(v["coverage_pass"] for v in base.values()) and all(not feats[f]["missing"] for f in mapping["dcr"][k].get("feature",[]) for k in []),
        }
    # Candidate ranking is measurement-only and never alters Production roles.
    rank=sorted(
      [(rid,(rr.get("derived_indices") or {}).get("ZAI_WIN")) for rid,rr in out.items() if (rr.get("derived_indices") or {}).get("ZAI_WIN") is not None],
      key=lambda z:(-float(z[1]),int(z[0]) if str(z[0]).isdigit() else str(z[0]))
    )
    result={
      "profile":PROFILE,"status":STATUS,"available":True,
      "source_snapshot_sha256":source_artifact.get("source_snapshot_sha256"),
      "official_detail_sha256":source_artifact.get("jra_official_race_card_detail_sha256"),
      "official_horse_history_sha256":source_artifact.get("jra_official_horse_history_sha256"),
      "official_horse_history_runner_count":len(history),
      "mapping_id":mapping.get("mapping_id"),
      "runner_count":len(out),"runners":out,
      "candidate_ranking":[{"rank":i+1,"runner_id":rid,"zai_win_diagnostic":round(float(v),6)} for i,(rid,v) in enumerate(rank)],
      "production_effect":"NONE",
      "limitations":[
        "Diagnostic neutralized values fill missing components only for SHADOW comparability; they are never Production evidence.",
        "Observed coverage is reported separately and retains UNKNOWN as missing.",
        "Pedigree population, jockey/trainer statistics, workout, comments and market time-series require separate signed adapters.",
        "TSL is excluded from this objective candidate and remains a separate third-party shadow."
      ],
    }
    result["sha256"]=_sha(result)
    return result

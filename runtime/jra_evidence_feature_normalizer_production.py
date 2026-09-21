from __future__ import annotations

class EvidenceNormalizationError(ValueError):
    pass

CATEGORIES = {"EXCEPTIONAL","VERY_STRONG","STRONG","POSITIVE","NEUTRAL","MIXED","CAUTION","WEAK","VERY_WEAK"}

def feature(category, evidence_refs, source_fact, rule_id):
    category=str(category).upper().strip()
    if category not in CATEGORIES:
        raise EvidenceNormalizationError(f"BAD_CATEGORY:{category}")
    if not isinstance(evidence_refs,list) or not evidence_refs:
        raise EvidenceNormalizationError("EVIDENCE_REFS_REQUIRED")
    if not str(source_fact).strip() or not str(rule_id).strip():
        raise EvidenceNormalizationError("SOURCE_FACT_AND_RULE_ID_REQUIRED")
    return {"category":category,"evidence_refs":[str(x) for x in evidence_refs],"source_fact":str(source_fact),"rule_id":str(rule_id)}

def percentile_band(p):
    p=float(p)
    if p>=0.95:return "EXCEPTIONAL"
    if p>=0.85:return "VERY_STRONG"
    if p>=0.70:return "STRONG"
    if p>=0.55:return "POSITIVE"
    if p>=0.40:return "NEUTRAL"
    if p>=0.25:return "MIXED"
    if p>=0.15:return "CAUTION"
    if p>=0.05:return "WEAK"
    return "VERY_WEAK"

def rate_band(rate):
    r=float(rate)
    if r>=0.30:return "VERY_STRONG"
    if r>=0.20:return "STRONG"
    if r>=0.14:return "POSITIVE"
    if r>=0.08:return "NEUTRAL"
    if r>=0.04:return "MIXED"
    return "WEAK"

def market_rank_band(rank, field_size):
    rank=int(rank); n=max(1,int(field_size)); q=rank/n
    if rank==1:return "VERY_STRONG"
    if q<=0.20:return "STRONG"
    if q<=0.40:return "POSITIVE"
    if q<=0.67:return "NEUTRAL"
    if q<=0.85:return "MIXED"
    return "WEAK"

def bodyweight_delta_band(delta_kg):
    d=abs(float(delta_kg))
    if d<=4:return "STRONG"
    if d<=10:return "POSITIVE"
    if d<=18:return "NEUTRAL"
    if d<=28:return "CAUTION"
    return "WEAK"

def comment_band(text):
    t=str(text)
    very=["絶好","抜群","文句なし","充実"]
    strong=["上向","良化","楽しみ","期待","順調","好調","仕上がり良好","動き良"]
    caution=["使いつつ","緩い","展開の助け","一変までは","様子","半信半疑","慣れ"]
    if any(x in t for x in very): return "VERY_STRONG"
    if any(x in t for x in strong): return "STRONG"
    if any(x in t for x in caution): return "CAUTION"
    return "NEUTRAL"

def workout_final_1f_band(seconds, course):
    s=float(seconds); c=str(course).upper()
    if "CW" in c or "ＣＷ" in c:
        if s<=11.5:return "EXCEPTIONAL"
        if s<=11.8:return "VERY_STRONG"
        if s<=12.1:return "STRONG"
        if s<=12.5:return "POSITIVE"
        if s<=12.9:return "NEUTRAL"
        return "CAUTION"
    if "坂" in c or "HILL" in c:
        if s<=12.1:return "EXCEPTIONAL"
        if s<=12.4:return "VERY_STRONG"
        if s<=12.7:return "STRONG"
        if s<=13.0:return "POSITIVE"
        if s<=13.5:return "NEUTRAL"
        return "CAUTION"
    return "NEUTRAL"

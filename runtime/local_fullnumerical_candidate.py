from __future__ import annotations

import copy
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any, Dict, Iterable, List

EVIDENCE_REGISTRY = "mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json"
MAPPING_REGISTRY = "mapping/local_full_numerical_mapping_v0.1_candidate_20260923.json"

REQUIRED = [
    "HPI-L","CFIg-L","RFIg-L","BVIg-L","JTI-L","CSI-L","BWI-L","DCR","NCI","TPI-L",
    "EVI/CEV","CCI","TRI","PRI","OPI-V","DRS","URP","HCS","ZAI-WIN","ZAI-PLACE",
    "SRI-L","T3I-L","F3S-L","WCI","W-AKI","P2-AKI","P3-AKI","ASI","RSI"
]


class LocalCandidateNumericalError(ValueError):
    pass


def _load(path: str | Path) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _sha(x: Any) -> str:
    return hashlib.sha256(
        json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _clamp(x: float) -> float:
    return max(0.0, min(100.0, float(x)))


def _mean(*xs: float) -> float:
    vals = [float(x) for x in xs]
    return sum(vals) / len(vals)


def _observed_only(mapping: Dict[str, Any]) -> bool:
    return str(((mapping.get("missing_semantics") or {}).get("policy") or "")).upper() == "OBSERVED_ONLY_RENORMALIZE"


def _mean_features(runner: Dict[str, Any], names: Iterable[str], mapping: Dict[str, Any]) -> tuple[float, float]:
    feats=[_feature(runner,n) for n in names]
    if not _observed_only(mapping):
        return _mean(*[float(x["score"]) for x in feats]), sum(bool(x.get("missing")) for x in feats)/max(1,len(feats))
    known=[float(x["score"]) for x in feats if not x.get("missing")]
    missing_fraction=sum(bool(x.get("missing")) for x in feats)/max(1,len(feats))
    return ((52.0 if not known else sum(known)/len(known)), missing_fraction)


def _feature(runner: Dict[str, Any], name: str) -> Dict[str, Any]:
    x = (runner.get("evidence_features") or {}).get(name)
    if not isinstance(x, dict):
        raise LocalCandidateNumericalError(f"FEATURE_MISSING:{runner.get('runner_id')}:{name}")
    v = x.get("score")
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(float(v)):
        raise LocalCandidateNumericalError(f"FEATURE_SCORE_INVALID:{runner.get('runner_id')}:{name}:{v}")
    if not 0 <= float(v) <= 100:
        raise LocalCandidateNumericalError(f"FEATURE_SCORE_OUT_OF_RANGE:{runner.get('runner_id')}:{name}:{v}")
    if not x.get("rule_id") or not x.get("evidence_refs") or not x.get("source_fact"):
        raise LocalCandidateNumericalError(f"FEATURE_PROVENANCE_INCOMPLETE:{runner.get('runner_id')}:{name}")
    return x


def _index(mapping_id: str, name: str, value: float, refs: Iterable[str], fact: str,
           *, rule_id: str, components: List[Dict[str, Any]] | None = None,
           missing_fraction: float = 0.0, exact_canon_formula: bool = False) -> Dict[str, Any]:
    return {
        "terminal_status": "CALCULATED",
        "value": round(_clamp(value), 6),
        "rule_id": rule_id,
        "mapping_version": mapping_id,
        "evidence_refs": sorted(set(str(x) for x in refs if x)),
        "source_fact": fact,
        "candidate_only": True,
        "production_authority": False,
        "calibration_status": "UNCALIBRATED_CANDIDATE",
        "exact_canon_formula": bool(exact_canon_formula),
        "missingness_fraction": round(max(0.0, min(1.0, float(missing_fraction))), 6),
        "components": components or [],
    }


def _weighted_base(runner: Dict[str, Any], idx: str, weights: Dict[str, float], mapping_id: str, mapping: Dict[str, Any]) -> Dict[str, Any]:
    total = 0.0
    denom = 0.0
    total_weight = 0.0
    refs: List[str] = []
    facts: List[str] = []
    comps: List[Dict[str, Any]] = []
    missing_weight = 0.0
    observed_only = _observed_only(mapping)
    for comp, w in weights.items():
        f = _feature(runner, comp)
        score = float(f["score"])
        w = float(w)
        total_weight += w
        refs.extend(f["evidence_refs"])
        is_missing=bool(f.get("missing"))
        facts.append(f"{comp}={score:.3f}" + ("[UNKNOWN-EXCLUDED]" if is_missing and observed_only else ("[UNKNOWN]" if is_missing else "")))
        if is_missing:
            missing_weight += w
        if not (observed_only and is_missing):
            total += score * w
            denom += w
        comps.append({
            "component": comp, "weight": w, "score": score,
            "missing": is_missing, "coverage": f.get("coverage"),
            "rule_id": f.get("rule_id"), "evidence_refs": f.get("evidence_refs"),
            "included_in_numeric_denominator": not (observed_only and is_missing),
        })
    if total_weight <= 0:
        raise LocalCandidateNumericalError(f"BAD_WEIGHT_SUM:{idx}")
    all_missing=denom<=0
    value=52.0 if all_missing else total/denom
    out=_index(
        mapping_id, idx, value, refs,
        "weighted candidate component ledger: " + " | ".join(facts),
        rule_id=(f"LOCAL-NUM-CAND-v0.3-{idx.replace('/','_')}-OBSERVED-ONLY-WEIGHTED" if observed_only
                 else f"LOCAL-NUM-CAND-v0.1-{idx.replace('/','_')}-WEIGHTED"),
        components=comps, missing_fraction=missing_weight/total_weight
    )
    out["missing_policy"]="OBSERVED_ONLY_RENORMALIZE" if observed_only else "LEGACY_NEUTRAL_INCLUDED"
    out["observed_weight_fraction"]=round(0.0 if total_weight<=0 else denom/total_weight,6)
    out["all_components_unknown"]=bool(all_missing)
    if all_missing:
        out["source_fact"] += " | all components UNKNOWN; 52 retained as transport-only value with confidence zero."
    return out


def _get(cc: Dict[str, Dict[str, Any]], name: str) -> float:
    try:
        return float(cc[name]["value"])
    except Exception as e:
        raise LocalCandidateNumericalError(f"INDEX_VALUE_MISSING:{name}") from e


def _refs(cc: Dict[str, Dict[str, Any]], names: Iterable[str]) -> List[str]:
    ans: List[str] = []
    for n in names:
        ans.extend((cc.get(n) or {}).get("evidence_refs") or [])
    return sorted(set(ans))


def _missing(cc: Dict[str, Dict[str, Any]], names: Iterable[str]) -> float:
    vals = [float((cc.get(n) or {}).get("missingness_fraction", 0)) for n in names]
    return 0.0 if not vals else sum(vals)/len(vals)


def _weighted_indices(cc: Dict[str, Dict[str, Any]], pairs: Iterable[tuple[str,float]], mapping: Dict[str,Any]) -> tuple[float,float]:
    rows=[(str(n),float(w)) for n,w in pairs]
    if not _observed_only(mapping):
        return sum(_get(cc,n)*w for n,w in rows), _missing(cc,[n for n,_ in rows])
    usable=[(n,w) for n,w in rows if float((cc.get(n) or {}).get("missingness_fraction",0.0)) < 1.0]
    if not usable:
        return 52.0,1.0
    den=sum(w for _,w in usable)
    if den<=0:
        return 52.0,1.0
    return sum(_get(cc,n)*w for n,w in usable)/den, _missing(cc,[n for n,_ in rows])


def _mean_indices(cc: Dict[str, Dict[str, Any]], names: Iterable[str], mapping: Dict[str,Any]) -> tuple[float,float]:
    ns=[str(n) for n in names]
    if not _observed_only(mapping):
        return _mean(*[_get(cc,n) for n in ns]), _missing(cc,ns)
    usable=[n for n in ns if float((cc.get(n) or {}).get("missingness_fraction",0.0)) < 1.0]
    if not usable:
        return 52.0,1.0
    return _mean(*[_get(cc,n) for n in usable]), _missing(cc,ns)


def _rank_desc(rows: List[Dict[str, Any]], getter) -> Dict[str, int]:
    ordered = sorted(rows, key=lambda r: (-float(getter(r)), int(r["runner_id"])))
    return {str(r["runner_id"]): i+1 for i, r in enumerate(ordered)}


def _rank_percentile(rank: int, n: int) -> float:
    if n <= 1:
        return 0.0
    return (rank-1)/(n-1)


def materialize_candidate(request: Dict[str, Any],
                          evidence_registry_path: str | Path = EVIDENCE_REGISTRY,
                          mapping_registry_path: str | Path = MAPPING_REGISTRY) -> Dict[str, Any]:
    reg = _load(evidence_registry_path)
    mapping = _load(mapping_registry_path)
    if "CANDIDATE" not in str(reg.get("status", "")) or "CANDIDATE" not in str(mapping.get("status", "")):
        raise LocalCandidateNumericalError("CANDIDATE_AUTHORITY_REQUIRED")
    if (request.get("candidate_evidence_compiler") or {}).get("result_derived_features") not in {0, None}:
        raise LocalCandidateNumericalError("RESULT_DERIVED_FEATURE_CONTAMINATION")
    runners = copy.deepcopy(request.get("runners") or [])
    if len(runners) < 2:
        raise LocalCandidateNumericalError("RUNNERS_REQUIRED")

    weights = reg["common_component_sets"]
    mapping_id = mapping["mapping_id"]
    base_names = ["HPI-L","CFIg-L","RFIg-L","BVIg-L","JTI-L","CSI-L","BWI-L","DCR","NCI"]

    # First pass: common weighted indices and source-derived diagnostics independent of market rank.
    for r in runners:
        cc: Dict[str, Dict[str, Any]] = {}
        for idx in base_names:
            cc[idx] = _weighted_base(r, idx, weights[idx], mapping_id, mapping)

        evi_components = ["position_acquisition","position_maintenance","third_corner_progression",
                          "leadership_stalk_acceptance","kickback_traffic_tolerance",
                          "going_adaptation","course_geometry","going_fit"]
        evi_feats = [_feature(r, x) for x in evi_components]
        evi_value,evi_missing = _mean_features(r,evi_components,mapping)
        cc["EVI/CEV"] = _index(
            mapping_id, "EVI/CEV", evi_value,
            [z for x in evi_feats for z in x["evidence_refs"]],
            "equal-mean candidate EVI factors: " + ",".join(evi_components),
            rule_id="LOCAL-NUM-CAND-v0.1-EVI-CEV-EQUAL-FACTOR",
            components=[{"component":n,"score":float(x["score"]),"missing":bool(x.get("missing"))}
                        for n,x in zip(evi_components,evi_feats)],
            missing_fraction=evi_missing
        )

        # CCI/TRI remain numerical neutral when their actual official sources are absent.
        cci = _feature(r, "cci_specificity")
        tri = _feature(r, "tri_vertical_comparison")
        cc["CCI"] = _index(mapping_id, "CCI", cci["score"], cci["evidence_refs"],
                           "candidate CCI from rule-bound comment specificity; neutral means source unavailable, not weak.",
                           rule_id="LOCAL-NUM-CAND-v0.1-CCI-SPECIFICITY",
                           missing_fraction=1.0 if cci.get("missing") else 0.0)
        cc["TRI"] = _index(mapping_id, "TRI", tri["score"], tri["evidence_refs"],
                           "candidate TRI from rule-bound training vertical comparison; neutral means source unavailable, not weak.",
                           rule_id="LOCAL-NUM-CAND-v0.1-TRI-VERTICAL",
                           missing_fraction=1.0 if tri.get("missing") else 0.0)

        drs_f = _feature(r, "class_change_pressure")
        cc["DRS"] = _index(mapping_id, "DRS", drs_f["score"], drs_f["evidence_refs"],
                           "candidate class-easing diagnostic from NCI class-change pressure.",
                           rule_id="LOCAL-NUM-CAND-v0.1-DRS-CLASS-CHANGE",
                           missing_fraction=1.0 if drs_f.get("missing") else 0.0)

        front_count = float((request.get("candidate_environment") or {}).get("front_candidate_count") or 0)
        field_size = len(runners)
        front_pressure = _clamp(100*front_count/max(1, field_size))
        urp_val = _mean(100-_get(cc, "DRS"), front_pressure)
        cc["URP"] = _index(mapping_id, "URP", urp_val, _refs(cc, ["DRS"]),
                           f"candidate promotion/reproducibility pressure: inverse DRS + front pressure={front_pressure:.3f}",
                           rule_id="LOCAL-NUM-CAND-v0.1-URP-EQUAL-RISK",
                           missing_fraction=_missing(cc, ["DRS"]))

        hpi_parts = ["class_level","opponent_strength","recent_finish"]
        hf = [_feature(r,x) for x in hpi_parts]
        hcs_value,hcs_missing = _mean_features(r,hpi_parts,mapping)
        cc["HCS"] = _index(mapping_id, "HCS", hcs_value,
                           [z for x in hf for z in x["evidence_refs"]],
                           "candidate hidden-class support from class/opponent/recent-content factors.",
                           rule_id=("LOCAL-NUM-CAND-v0.3-HCS-OBSERVED-ONLY" if _observed_only(mapping) else "LOCAL-NUM-CAND-v0.1-HCS-EQUAL"),
                           missing_fraction=hcs_missing)

        # Exact TPI-L formula from LOCAL canon; only the min-major penalty magnitude is inherited from
        # the existing production materializer and is not re-tuned here.
        hpi=_get(cc,"HPI-L"); cfi=_get(cc,"CFIg-L"); rfi=_get(cc,"RFIg-L")
        bvi=_get(cc,"BVIg-L"); jti=_get(cc,"JTI-L"); csi=_get(cc,"CSI-L")
        bwi=_get(cc,"BWI-L"); nci=_get(cc,"NCI"); evi=_get(cc,"EVI/CEV")
        linear,tpi_missing=_weighted_indices(cc,[
            ("HPI-L",0.18),("CFIg-L",0.16),("RFIg-L",0.14),("BVIg-L",0.08),
            ("JTI-L",0.08),("CSI-L",0.08),("BWI-L",0.08),("NCI",0.10),("EVI/CEV",0.10)
        ],mapping)
        major_names=["HPI-L","CFIg-L","RFIg-L","NCI","EVI/CEV","BWI-L"]
        major_values=[_get(cc,nm) for nm in major_names if (not _observed_only(mapping) or float((cc.get(nm) or {}).get("missingness_fraction",0))<1.0)]
        min_major=min(major_values) if major_values else 52.0
        penalty=max(0.0,(60.0-min_major)*0.5)
        cc["TPI-L"] = _index(
            mapping_id, "TPI-L", linear-penalty,
            _refs(cc, ["HPI-L","CFIg-L","RFIg-L","BVIg-L","JTI-L","CSI-L","BWI-L","NCI","EVI/CEV"]),
            f"LOCAL canon TPI linear={linear:.6f};min_major={min_major:.6f};penalty={penalty:.6f}",
            rule_id="LOCAL-TPI-L-v4.13R1-CANDIDATE-BINDING",
            missing_fraction=tpi_missing,
            exact_canon_formula=not _observed_only(mapping)
        )

        # SRI exact coefficient structure; uncertainty penalty remains explicitly candidate-only because
        # the canon defines the penalty concept but not a fixed coefficient.
        dcr=_get(cc,"DCR")
        sri_linear,sri_missing=_weighted_indices(cc,[
            ("TPI-L",0.20),("RFIg-L",0.18),("EVI/CEV",0.18),("CFIg-L",0.15),
            ("NCI",0.12),("BWI-L",0.10),("JTI-L",0.05),("CSI-L",0.02)
        ],mapping)
        sri_penalty=max(0.0,(60.0-dcr)*0.25)
        cc["SRI-L"] = _index(
            mapping_id, "SRI-L", sri_linear-sri_penalty,
            _refs(cc, ["TPI-L","RFIg-L","EVI/CEV","CFIg-L","NCI","BWI-L","JTI-L","CSI-L","DCR"]),
            f"LOCAL SRI coefficient structure; linear={sri_linear:.6f}; candidate uncertainty penalty={sri_penalty:.6f}",
            rule_id="LOCAL-NUM-CAND-v0.1-SRI-CANON-COEFFICIENTS-CANDIDATE-PENALTY",
            missing_fraction=max(sri_missing,_missing(cc, ["DCR"]))
        )

        r["candidate_indices"] = cc

    # Cross-runner ability rank is market-free.
    ability_rank = _rank_desc(runners, lambda r: _mean(
        _get(r["candidate_indices"],"TPI-L"),
        _get(r["candidate_indices"],"SRI-L"),
        _get(r["candidate_indices"],"HPI-L"),
        _get(r["candidate_indices"],"CFIg-L"),
        _get(r["candidate_indices"],"RFIg-L"),
    ))
    n=len(runners)
    market_rows = [r for r in runners if (r.get("raw_candidate_evidence") or {}).get("popularity") is not None]
    market_rank = {str(r["runner_id"]): int(r["raw_candidate_evidence"]["popularity"]) for r in market_rows}

    # Second pass: market diagnostics, role-risk diagnostics, final exact/candidate derived indices.
    for r in runners:
        rid=str(r["runner_id"]); cc=r["candidate_indices"]
        ar=ability_rank[rid]
        mr=market_rank.get(rid)
        if mr is None:
            pri=52.0; opi=52.0; market_missing=1.0
            market_fact="official market rank unavailable; canonical neutral diagnostic."
        else:
            ap=_rank_percentile(ar,n); mp=_rank_percentile(mr,n)
            pri=_clamp(100*(1-abs(ap-mp)))
            opi=_clamp(50+50*(mp-ap))
            market_missing=0.0
            market_fact=f"candidate ability rank={ar}/{n}; official market rank={mr}/{n}"
        odds_ref=[(r.get("raw_candidate_evidence") or {}).get("race_card_source_id")]
        cc["PRI"]=_index(mapping_id,"PRI",pri,odds_ref,market_fact,
                         rule_id="LOCAL-NUM-CAND-v0.1-PRI-RANK-ALIGNMENT",missing_fraction=market_missing)
        cc["OPI-V"]=_index(mapping_id,"OPI-V",opi,odds_ref,market_fact,
                           rule_id="LOCAL-NUM-CAND-v0.1-OPI-V-RANK-GAP",missing_fraction=market_missing)

        uncertainty=100-_get(cc,"DCR")
        divergence=100-pri
        front_count=float((request.get("candidate_environment") or {}).get("front_candidate_count") or 0)
        front_pressure=_clamp(100*front_count/max(1,n))
        style_repro=float(_feature(r,"running_style_repro")["score"])
        path_narrowness=100-style_repro
        waki=_mean(uncertainty,_get(cc,"URP"),front_pressure,divergence,path_narrowness)
        cc["W-AKI"]=_index(mapping_id,"W-AKI",waki,_refs(cc,["DCR","URP","PRI"]),
                            f"equal candidate W risk: uncertainty={uncertainty:.3f},URP={_get(cc,'URP'):.3f},front={front_pressure:.3f},market divergence={divergence:.3f},path narrowness={path_narrowness:.3f}",
                            rule_id="LOCAL-NUM-CAND-v0.1-W-AKI-EQUAL-RISK",
                            missing_fraction=_missing(cc,["DCR","URP","PRI"]))

        role_competition=_clamp(100*(n-1)/max(1,12))
        p2aki=_mean(uncertainty, role_competition, divergence, _get(cc,"URP"))
        p3aki=_mean(uncertainty, _clamp(role_competition+10), divergence, _get(cc,"URP"))
        cc["P2-AKI"]=_index(mapping_id,"P2-AKI",p2aki,_refs(cc,["DCR","PRI","URP"]),
                             "equal candidate second-column outsider-shift risk.",
                             rule_id="LOCAL-NUM-CAND-v0.1-P2-AKI-EQUAL-RISK",
                             missing_fraction=_missing(cc,["DCR","PRI","URP"]))
        cc["P3-AKI"]=_index(mapping_id,"P3-AKI",p3aki,_refs(cc,["DCR","PRI","URP"]),
                             "equal candidate third-column outsider-intrusion risk.",
                             rule_id="LOCAL-NUM-CAND-v0.1-P3-AKI-EQUAL-RISK",
                             missing_fraction=_missing(cc,["DCR","PRI","URP"]))

        friction_risk=100-float(_feature(r,"position_maintenance")["score"])
        asi=100-_mean(waki,uncertainty,friction_risk)
        cc["ASI"]=_index(mapping_id,"ASI",asi,_refs(cc,["W-AKI","DCR"]),
                         f"100 - mean(W-AKI, uncertainty, position-maintenance risk={friction_risk:.3f})",
                         rule_id="LOCAL-NUM-CAND-v0.1-ASI-RISK-COMPLEMENT",
                         missing_fraction=_missing(cc,["W-AKI","DCR"]))

        sd=float(_feature(r,"same_distance")["score"])
        prog=float(_feature(r,"third_corner_progression")["score"])
        hold=float(_feature(r,"position_maintenance")["score"])
        gwr=float(_feature(r,"good_weight_range")["score"])
        t3i=_mean(opi,sd,prog,hold,_get(cc,"TRI"),_get(cc,"DRS"),gwr)
        cc["T3I-L"]=_index(mapping_id,"T3I-L",t3i,
                            _refs(cc,["OPI-V","TRI","DRS"]) +
                            _feature(r,"same_distance")["evidence_refs"] +
                            _feature(r,"third_corner_progression")["evidence_refs"] +
                            _feature(r,"position_maintenance")["evidence_refs"] +
                            _feature(r,"good_weight_range")["evidence_refs"],
                            "equal candidate T3I: price/same-distance/progression/hold/training/easing/bodyweight.",
                            rule_id="LOCAL-NUM-CAND-v0.1-T3I-EQUAL-FACTOR",
                            missing_fraction=(market_missing +
                                sum(bool(_feature(r,x).get("missing")) for x in ["same_distance","third_corner_progression","position_maintenance","good_weight_range"]) +
                                _missing(cc,["TRI","DRS"])*2)/7)

        # Exact F3S coefficient formula from LOCAL canon.
        f3s,f3s_missing=_weighted_indices(cc,[
            ("SRI-L",0.25),("TPI-L",0.20),("EVI/CEV",0.18),("RFIg-L",0.14),
            ("CFIg-L",0.12),("NCI",0.06),("T3I-L",0.05)
        ],mapping)
        cc["F3S-L"]=_index(mapping_id,"F3S-L",f3s,
                            _refs(cc,["SRI-L","TPI-L","EVI/CEV","RFIg-L","CFIg-L","NCI","T3I-L"]),
                            "LOCAL canon exact F3S coefficient formula.",
                            rule_id="LOCAL-F3S-L-v4.13R1-CANDIDATE-BINDING",
                            missing_fraction=f3s_missing,
                            exact_canon_formula=not _observed_only(mapping))

        # Pre-probability role suitability scores. These are scores only, never probabilities.
        zai_win,zai_win_missing=_mean_indices(cc,["TPI-L","SRI-L","EVI/CEV","CFIg-L","NCI","DCR"],mapping)
        zai_place,zai_place_missing=_mean_indices(cc,["TPI-L","SRI-L","EVI/CEV","CFIg-L","RFIg-L","DCR"],mapping)
        cc["ZAI-WIN"]=_index(mapping_id,"ZAI-WIN",zai_win,_refs(cc,["TPI-L","SRI-L","EVI/CEV","CFIg-L","NCI","DCR"]),
                              "candidate pre-probability winner suitability score; never probability.",
                              rule_id=("LOCAL-NUM-CAND-v0.3-ZAI-WIN-OBSERVED-ONLY" if _observed_only(mapping) else "LOCAL-NUM-CAND-v0.1-ZAI-WIN-EQUAL"),missing_fraction=zai_win_missing)
        cc["ZAI-PLACE"]=_index(mapping_id,"ZAI-PLACE",zai_place,_refs(cc,["TPI-L","SRI-L","EVI/CEV","CFIg-L","RFIg-L","DCR"]),
                                "candidate pre-probability place suitability score; never probability.",
                                rule_id=("LOCAL-NUM-CAND-v0.3-ZAI-PLACE-OBSERVED-ONLY" if _observed_only(mapping) else "LOCAL-NUM-CAND-v0.1-ZAI-PLACE-EQUAL"),missing_fraction=zai_place_missing)

        role_spread=max(zai_win,zai_place,t3i)-min(zai_win,zai_place,t3i)
        role_dispersion_risk=_clamp(role_spread*2.5)
        rsi=_mean(role_dispersion_risk,divergence,uncertainty)
        cc["RSI"]=_index(mapping_id,"RSI",rsi,_refs(cc,["ZAI-WIN","ZAI-PLACE","T3I-L","PRI","DCR"]),
                         f"candidate role-column mismatch risk spread={role_spread:.3f}, market divergence={divergence:.3f}, uncertainty={uncertainty:.3f}",
                         rule_id="LOCAL-NUM-CAND-v0.1-RSI-EQUAL-RISK",
                         missing_fraction=_missing(cc,["ZAI-WIN","ZAI-PLACE","T3I-L","PRI","DCR"]))

        wci=_mean(zai_win,_get(cc,"SRI-L"),asi,100-waki)
        cc["WCI"]=_index(mapping_id,"WCI",wci,_refs(cc,["ZAI-WIN","SRI-L","ASI","W-AKI"]),
                         "candidate win-closing diagnostic; not a direct win-bet trigger.",
                         rule_id="LOCAL-NUM-CAND-v0.1-WCI-EQUAL",missing_fraction=_missing(cc,["ZAI-WIN","SRI-L","ASI","W-AKI"]))

        missing=[x for x in REQUIRED if x not in cc]
        if missing:
            raise LocalCandidateNumericalError(f"INDEX_CLOSURE_MISSING:{rid}:{missing}")
        r["canonical_components"]={name:cc[name] for name in REQUIRED}
        r["candidate_missing_policy"]=((mapping.get("missing_semantics") or {}).get("policy") or "LEGACY_NEUTRAL_INCLUDED")
        r["candidate_index_sha256"]=_sha(r["canonical_components"])

    out=copy.deepcopy(request)
    out["runners"]=runners
    required_count=len(runners)*len(REQUIRED)
    rows=[]
    for r in runners:
        for name in REQUIRED:
            spec=r["canonical_components"][name]
            if not isinstance(spec.get("value"),(int,float)) or not math.isfinite(float(spec["value"])):
                raise LocalCandidateNumericalError(f"NON_NUMERIC_INDEX:{r['runner_id']}:{name}")
            rows.append({"runner_id":str(r["runner_id"]),"index":name,"value":spec["value"],"rule_id":spec["rule_id"]})

    out["candidate_full_numerical_summary"]={
        "required_indices":REQUIRED,
        "required_count":required_count,
        "calculated_count":len(rows),
        "unresolved_count":0,
        "full_numerical_complete":len(rows)==required_count,
        "mapping_id":mapping_id,
        "evidence_registry_id":reg["registry_id"],
        "production_authority":False,
        "calibration_status":"UNCALIBRATED_CANDIDATE",
        "result_derived_features":0,
        "candidate_neutral_missing_component_count":sum(int(r.get("candidate_missing_count",0)) for r in runners),
        "mean_real_component_coverage":round(sum(float(r.get("candidate_feature_coverage_ratio",0)) for r in runners)/len(runners),6),
        "missing_policy":((mapping.get("missing_semantics") or {}).get("policy") or "LEGACY_NEUTRAL_INCLUDED"),
        "evidence_routing_change":bool(mapping.get("evidence_routing_change",False)),
        "weight_change_from_v01":mapping.get("weight_change_from_v01"),
    }
    out["candidate_index_terminalization_sha256"]=_sha(rows)
    out["candidate_index_provenance_sha256"]=_sha([r["canonical_components"] for r in runners])
    out["candidate_full_numerical_summary"]["sha256"]=_sha(out["candidate_full_numerical_summary"])
    if mapping.get("candidate_role_weights"):
        out["candidate_role_weight_profile"]=copy.deepcopy(mapping["candidate_role_weights"])
        out["candidate_role_weight_profile_sha256"]=_sha(out["candidate_role_weight_profile"])
    return out

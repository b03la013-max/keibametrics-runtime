"""Deterministic JRA Static Owner: ranks + AKI-JRA v2 structured widths.

Converts a verified Production-formula Full20 ledger into a frozen,
source-bound rank / role / pair / third decision. Ticket WIDTH is no longer a
fixed score cluster: it follows ケイバメトリクス中央版 v1.1 第II部 AKI-JRA v2
(W-AKI / P-AKI / ASI / RSI -> AKI band -> 1-2-5 ... 3-6-12 formation, with
the §35 rules: ASI<65 no single head, W-AKI>=60 two-plus heads, RSI>=60 row
promotion). Every AKI term is computed from the frozen Full20 indices only
(no market or post-cutoff input) and recorded with its parts. It is NOT
authorized to issue Production tickets until Current Authority admits this
exact code fingerprint. It never imports Candidate numerical material.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import hashlib
import json
import math

from jra_index_provenance_builder import BASE, DERIVED, FORMULA_REGISTRY

PROFILE = "JRA-STATIC-PREDICTION-OWNER-AKI-JRA-v2-20261011"
MAPPING = "JRA-EVIDENCE-TO-BASE-MAPPING-v1.0-PRODUCTION-20260921"
REQUIRED = set(BASE) | set(DERIVED)
COLUMNS = ("W", "P2", "P3")


class JRAStaticOwnerError(ValueError):
    pass


def _sha(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _time(v):
    try:
        d = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
        return d if d.tzinfo else None
    except (TypeError, ValueError):
        return None


def _measure(row, name):
    v = row["canonical_components"][name]["value"]
    return float(v)


def _rank(runners, metric):
    return sorted((str(x["runner_id"]) for x in runners),
                  key=lambda rid: (-next(_measure(row, metric) for row in runners if str(row["runner_id"]) == rid),
                                   int(rid) if rid.isdigit() else rid))


def _clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


# AKI-JRA v2 band -> (1着, 2着, 3着) column sizes (中央版 v1.1 §33/§34).
AKI_BANDS = (
    (35.0, "堅い", (1, 2, 5), (1, 2, 5)),
    (50.0, "標準", (1, 3, 7), (2, 3, 6)),
    (65.0, "紐荒れ", (1, 4, 8), (2, 4, 8)),
    (80.0, "軸崩壊警戒", (2, 5, 10), (3, 5, 9)),
    (101.0, "大波乱", (3, 6, 12), (3, 6, 12)),
)


def aki_jra_v2(runners):
    """AKI-JRA v2 from frozen Full20 indices only (deterministic, recorded).

    Production indices are compressed (typical race SD ~4-7 points), so gaps
    and 'below field' tests are expressed relative to the race's own spread
    and median instead of absolute points.
    """
    from statistics import median, pstdev
    val = {str(r["runner_id"]): {k: _measure(r, k) for k in r["canonical_components"]} for r in runners}
    n = len(val)
    ids_ = list(val)
    zw = _rank(runners, "ZAI_WIN")
    zp = _rank(runners, "ZAI_PLACE")
    t3 = _rank(runners, "T3I")
    top, axis = zw[0], zp[0]

    def sd(key):
        return max(pstdev([val[r][key] for r in ids_]) if n > 1 else 1.0, 0.5)

    def below_median(rid, key):
        return val[rid][key] < median(val[r][key] for r in ids_)

    z = [val[r]["ZAI_WIN"] for r in zw]
    g = (z[0] - z[1]) / sd("ZAI_WIN") if n > 1 else 9.0
    parts_w = {"base": 25.0}
    parts_w["head_gap_sd"] = 25.0 if g < 0.1 else 18.0 if g < 0.25 else 10.0 if g < 0.5 else 4.0 if g < 1.0 else 0.0
    parts_w["contenders_within_half_sd"] = min(20.0, 5.0 * sum(
        1 for r in zw[1:] if val[r]["ZAI_WIN"] >= z[0] - 0.5 * sd("ZAI_WIN")))
    parts_w["top_information_reliability_below_median"] = 8.0 if below_median(top, "DCR") else 0.0
    parts_w["top_recent_form_below_median"] = 6.0 if below_median(top, "RFI") else 0.0
    parts_w["top_course_fit_below_median"] = 6.0 if below_median(top, "CFI") else 0.0
    parts_w["top_class_below_median"] = 6.0 if below_median(top, "KGI") else 0.0
    sri_order = _rank(runners, "SRI")
    sri_gap = ((val[sri_order[0]]["SRI"] - val[sri_order[1]]["SRI"]) / sd("SRI")) if n > 1 else 9.0
    parts_w["solid_finish_correction"] = -(10.0 if g >= 1.0 else 0.0) - (
        6.0 if sri_order[0] == top and sri_gap >= 0.5 else 0.0)
    w_aki = _clamp(sum(parts_w.values()))

    tv = [val[r]["T3I"] for r in t3]
    third = tv[2] if n > 2 else tv[-1]
    parts_p = {"base": 25.0}
    parts_p["dense_contenders_near_third"] = min(30.0, 6.0 * sum(
        1 for r in t3[3:] if val[r]["T3I"] >= third - 0.5 * sd("T3I")))
    parts_p["field_size"] = 8.0 if n >= 16 else 5.0 if n >= 13 else -8.0 if n <= 9 else 0.0
    parts_p["strong_outsiders"] = min(18.0, 6.0 * sum(1 for r in t3[:5] if zp.index(r) >= 5))
    parts_p["top_vs_rest_gap"] = -8.0 if n > 5 and (tv[2] - tv[5]) >= sd("T3I") else 0.0
    p_aki = _clamp(sum(parts_p.values()))

    zpv = [val[r]["ZAI_PLACE"] for r in zp]
    margin = (zpv[0] - zpv[1]) / sd("ZAI_PLACE") if n > 1 else 9.0
    parts_a = {"base": 60.0, "axis_margin_sd": round(25.0 * min(1.0, margin), 3)}
    parts_a["axis_information_reliability_below_median"] = -8.0 if below_median(axis, "DCR") else 0.0
    parts_a["axis_recent_form_below_median"] = -6.0 if below_median(axis, "RFI") else 0.0
    parts_a["axis_course_fit_below_median"] = -6.0 if below_median(axis, "CFI") else 0.0
    parts_a["axis_is_win_top"] = 5.0 if axis == top else 0.0
    asi = _clamp(sum(parts_a.values()))

    k = min(8, n)
    disp = sum(abs(zp.index(r) - t3.index(r)) for r in zp[:k]) / k
    promoted = [r for r in t3[:4] if zp.index(r) >= 6]
    rsi = _clamp(disp * 12.5 + 10.0 * len(promoted))

    total = _clamp(0.35 * w_aki + 0.35 * p_aki + 0.20 * rsi)
    for limit, label, single, multi in AKI_BANDS:
        if total < limit:
            band, form = label, (multi if w_aki >= 45 else single)
            break
    h, s2, s3 = form
    rules = []
    if asi < 65 and h < 2:
        h = 2
        rules.append("ASI<65: single head forbidden (§35-1)")
    if w_aki >= 60 and h < 2:
        h = 2
        rules.append("W-AKI>=60: 2-3 head candidates (§27)")
    if w_aki >= 50 and h < 2:
        h = 2
        rules.append("W-AKI>=50: a non-◎ winner line (§35-2)")
    if rsi >= 60:
        s2 += 1
        rules.append("RSI>=60: promote one 3rd-row runner to the 2nd row (§35-3)")
    h, s2, s3 = min(h, n), min(max(s2, h), n), min(max(s3, s2 + 1), n)
    return {
        "profile": "KM-JRA-AKI-JRA-v2-FROM-FULL20-20261011",
        "basis": "中央版 v1.1 第II部 §26-35; deterministic proxies over frozen Full20 indices only (no market, no post-cutoff input); UNVALIDATED",
        "W_AKI": round(w_aki, 3), "W_AKI_parts": parts_w,
        "P_AKI": round(p_aki, 3), "P_AKI_parts": parts_p,
        "ASI": round(asi, 3), "ASI_parts": parts_a, "ASI_axis": axis,
        "RSI": round(rsi, 3), "RSI_parts": {"mean_row_displacement_top8": round(disp, 3),
                                            "third_row_promotion_candidates": promoted},
        "AKI_JRA_v2": round(total, 3), "band": band,
        "formation": {"heads": h, "seconds": s2, "thirds": s3, "base_type": "-".join(map(str, form))},
        "rules_applied": rules,
        "big_upset_mode": False,
        "big_upset_note": "§35-8 requires danger-favourite and strong-longshot evidence not computable from Full20 alone; never enabled here",
    }


def compile_static_owner(request, *, source_snapshot_sha256, source_receipt_sha256,
                         frozen_at, prediction_cutoff):
    if request.get("family_id") != "JRA":
        raise JRAStaticOwnerError("JRA_ONLY")
    if not source_snapshot_sha256 or not source_receipt_sha256:
        raise JRAStaticOwnerError("SIGNED_SOURCE_BASIS_REQUIRED")
    freeze, cutoff = _time(frozen_at), _time(prediction_cutoff)
    if freeze is None or cutoff is None or freeze > cutoff:
        raise JRAStaticOwnerError("STATIC_FREEZE_AFTER_PREDICTION_CUTOFF")
    runners = request.get("runners")
    if not isinstance(runners, list) or len(runners) < 2:
        raise JRAStaticOwnerError("FULL_RUNNER_UNIVERSE_REQUIRED")
    ids = [str(x.get("runner_id") or "") for x in runners]
    if not all(ids) or len(ids) != len(set(ids)):
        raise JRAStaticOwnerError("RUNNER_UNIVERSE_INVALID")
    mapping = request.get("base_index_mapping_authority") or {}
    if mapping.get("production_authority") is not True or mapping.get("mapping_id") != MAPPING:
        raise JRAStaticOwnerError("PRODUCTION_NUMERICAL_AUTHORITY_REQUIRED")
    for row in runners:
        rid = str(row["runner_id"])
        cc = row.get("canonical_components") or {}
        if set(cc) != REQUIRED:
            raise JRAStaticOwnerError("FULL20_NOT_AVAILABLE:" + rid)
        for index, spec in cc.items():
            v = spec.get("value")
            if isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v) or not 0 <= v <= 100:
                raise JRAStaticOwnerError(f"INDEX_INVALID:{rid}:{index}")
            if spec.get("candidate_only") is True or spec.get("production_authority") is False:
                raise JRAStaticOwnerError(f"CANDIDATE_NUMERICAL_FORBIDDEN:{rid}:{index}")
            rule_mapping = MAPPING if index in BASE else FORMULA_REGISTRY
            if spec.get("mapping_version") != rule_mapping or not spec.get("rule_id") or not spec.get("evidence_refs") or not spec.get("source_fact"):
                raise JRAStaticOwnerError(f"INDEX_PROVENANCE_INVALID:{rid}:{index}")
    rank_w = _rank(runners, "ZAI_WIN")
    rank_p2 = _rank(runners, "ZAI_PLACE")
    rank_p3 = _rank(runners, "T3I")
    aki = aki_jra_v2(runners)
    f = aki["formation"]
    heads = rank_w[:f["heads"]]
    # §33/§34 formation semantics: with one head (1着固定) the 2着/3着 rows
    # exclude it; with several heads (頭入替) the heads also fill rows 2-3.
    pool2 = [r for r in rank_p2 if r not in heads]
    seconds = (pool2[:f["seconds"]] if len(heads) == 1
               else (heads + pool2)[:max(f["seconds"], len(heads))])
    if aki["RSI"] >= 60:
        # §35-3: the extra 2nd-row slot goes to the best 3rd-row (T3I) runner.
        promote = next((r for r in rank_p3 if r not in seconds and r not in heads), None)
        if promote is not None and seconds:
            seconds = seconds[:-1] + [promote] if len(seconds) >= f["seconds"] else seconds + [promote]
    pool3 = [r for r in rank_p3 if r not in seconds and (len(heads) > 1 or r not in heads)]
    thirds = (seconds + pool3)[:max(f["thirds"], len(seconds))]
    active = {"W": heads, "P2": seconds, "P3": thirds}
    role_registry = [
        {"runner_id": rid, "column": col,
         "status": "CORE" if rid == active[col][0] else "PROTECTED" if rid in active[col] else "EXCLUDED",
         "reason": f"AKI_JRA_V2_{aki['band']}_{aki['formation']['base_type']}",
         "authority": PROFILE, "production_authority": False}
        for rid in ids for col in COLUMNS
    ]
    pairs = []
    thirds_disp = []
    for h in heads:
        for s_ in [rid for rid in seconds if rid != h]:
            pairs.append({"head": h, "second": s_, "status": "PURCHASE",
                          "reason": "AKI_FORMATION_ROW2", "authority": PROFILE, "production_authority": False})
            for t in [rid for rid in thirds if rid not in {h, s_}]:
                thirds_disp.append({"head": h, "second": s_, "third": t, "status": "PURCHASE",
                                    "reason": "AKI_FORMATION_ROW3", "authority": PROFILE,
                                    "production_authority": False})
    thirds = thirds_disp
    sp = {
        "ranking": rank_w,
        "roles": {rid: [col for col in COLUMNS if rid in active[col]] for rid in rank_w},
        "aki_jra_v2": aki,
        "status": "FROZEN-PRE-KRS / CANDIDATE",
        "authority": PROFILE,
        "production_authority": False,
    }
    result = {
        "profile": PROFILE,
        "race_id": request.get("race_id"),
        "source_snapshot_sha256": source_snapshot_sha256,
        "source_receipt_sha256": source_receipt_sha256,
        "frozen_at": frozen_at,
        "static_prediction": sp,
        "role_registry": role_registry,
        "pair_dispositions": pairs,
        "third_dispositions": thirds,
        "purchased_heads": active["W"],
        "active_columns": active,
        "aki_jra_v2": aki,
        "full_index_count": len(runners) * 20,
        "candidate_policy": True,
        "production_authority": False,
        "purchase_authority": False,
        "promotion_gate": "FROZEN_UNKNOWN_FUTURE_OOS_PLUS_CURRENT_AUTHORITY",
    }
    result["sha256"] = _sha(result)
    return result

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KRS-Engine v1.1.0
KeibaMetrics Race Simulation Engine

Implements the stage-based simulation architecture described in
"ケイバメトリクス・レースシミュレーション規格 v1.1-KRS".

IMPORTANT:
- Simulation frequencies (SSR/LSR/Z4R) are UNCALIBRATED simulation occurrence rates.
- They are NOT win/place probabilities and MUST NOT be used directly for EV.
- The default parameter map is explicitly provisional and must be calibrated out-of-sample.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple

ENGINE_VERSION = "1.1.0"
DEFAULT_PARAMETER_MAP_VERSION = "0.1-provisional"
UNCALIBRATED_NOTICE = (
    "KRS simulation occurrence rates are uncalibrated. "
    "SSR/LSR/Z4R are NOT real-world probabilities and are NOT EV inputs."
)


# -----------------------------
# Utilities
# -----------------------------

def clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def safe_mean(xs: Iterable[float], default: float = 50.0) -> float:
    vals = [float(x) for x in xs if x is not None]
    return statistics.mean(vals) if vals else default


def normalize01(x: float) -> float:
    return clamp(float(x), 0.0, 100.0) / 100.0


def weighted_mean(items: Iterable[Tuple[float, float]], default: float = 50.0) -> float:
    num = 0.0
    den = 0.0
    for value, weight in items:
        if value is None or weight <= 0:
            continue
        num += float(value) * float(weight)
        den += float(weight)
    return num / den if den > 0 else default


def percentile(sorted_vals: Sequence[float], p: float) -> float:
    if not sorted_vals:
        return float("nan")
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])
    p = max(0.0, min(1.0, p))
    idx = p * (len(sorted_vals) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return float(sorted_vals[lo])
    frac = idx - lo
    return float(sorted_vals[lo]) * (1 - frac) + float(sorted_vals[hi]) * frac


def rank_desc(values: Mapping[int, float]) -> Dict[int, int]:
    order = sorted(values, key=lambda k: (-values[k], k))
    return {horse_no: i + 1 for i, horse_no in enumerate(order)}


def rank_asc(values: Mapping[int, float]) -> Dict[int, int]:
    order = sorted(values, key=lambda k: (values[k], k))
    return {horse_no: i + 1 for i, horse_no in enumerate(order)}


def stable_hash_int(*parts: Any, modulo: int = 2**31 - 1) -> int:
    s = "|".join(str(x) for x in parts).encode("utf-8")
    return int(hashlib.sha256(s).hexdigest()[:16], 16) % modulo


def categorical_choice(rng: random.Random, weights: Mapping[str, float]) -> str:
    clean = {k: max(0.0, float(v)) for k, v in weights.items()}
    total = sum(clean.values())
    if total <= 0:
        keys = list(clean) or ["standard"]
        return rng.choice(keys)
    r = rng.random() * total
    acc = 0.0
    for key, weight in clean.items():
        acc += weight
        if r <= acc:
            return key
    return next(reversed(clean))


def normal_score(rng: random.Random, mean: float, sd: float) -> float:
    return clamp(rng.gauss(mean, max(0.01, sd)))


def ensure_score_map(h: Mapping[str, Any], keys: Sequence[str], neutral: float = 50.0) -> Dict[str, float]:
    return {key: clamp(float(h.get(key, neutral))) for key in keys}


# -----------------------------
# Validation / defaults
# -----------------------------

HSV_KEYS = [
    "base_competitive_ability", "class_strength", "condition_fit", "distance_fit", "surface_fit",
    "gate_reliability", "initial_acceleration", "position_intent", "inside_cut_ability",
    "outside_press_ability", "leader_need", "stalk_acceptance", "crowd_tolerance",
    "early_position_hold", "midrace_hold", "progression_ceiling", "progression_timing",
    "corner_acceleration", "traffic_escape", "sustained_speed", "pressure_tolerance",
    "front_friction_tolerance", "long_move_tolerance", "final_reserve", "deceleration_risk",
    "training_state", "bodyweight_state", "layoff_uncertainty", "comment_state", "data_confidence",
]

STATIC_KEYS = [
    "tpi", "zai_win", "zai_place", "sri", "t3i", "f3s", "w_aki", "p2_aki", "p3_aki", "asi", "rsi"
]


def default_parameter_map() -> Dict[str, Any]:
    """Provisional, explicitly uncalibrated parameter map.

    Values are implementation coefficients, not empirically proven racing constants.
    They are separated from the engine so they can be replaced by calibrated maps.
    """
    return {
        "parameter_map_version": DEFAULT_PARAMETER_MAP_VERSION,
        "status": "PROVISIONAL_UNCALIBRATED",
        "score_noise": {
            "gate_sd": 8.0,
            "acquisition_sd": 6.0,
            "maintenance_sd": 5.0,
            "progression_sd": 6.0,
            "final_sd": 5.0,
        },
        "common_shock_sd": {
            "pace": 8.0,
            "track_speed": 5.0,
            "inside_bias": 7.0,
            "outside_bias": 7.0,
            "congestion": 8.0,
        },
        "strategy_adjustment": {
            "aggressive": {"intent": 10.0, "position_cost": 7.0, "progression": 2.0},
            "standard": {"intent": 0.0, "position_cost": 0.0, "progression": 0.0},
            "conservative": {"intent": -9.0, "position_cost": -3.0, "progression": 5.0},
        },
        "stage_weights": {
            "gate": {
                "gate_reliability": 0.70,
                "initial_acceleration": 0.30,
            },
            "acquisition": {
                "gate": 0.24,
                "initial_acceleration": 0.24,
                "position_intent": 0.18,
                "inside_cut_ability": 0.08,
                "outside_press_ability": 0.08,
                "stalk_acceptance": 0.08,
                "crowd_tolerance": 0.10,
            },
            "leader": {
                "acquisition": 0.52,
                "leader_need": 0.25,
                "initial_acceleration": 0.15,
                "outside_press_ability": 0.08,
            },
            "maintenance": {
                "early_position_hold": 0.28,
                "midrace_hold": 0.25,
                "sustained_speed": 0.17,
                "pressure_tolerance": 0.15,
                "front_friction_tolerance": 0.15,
            },
            "progression": {
                "progression_ceiling": 0.28,
                "progression_timing": 0.14,
                "corner_acceleration": 0.22,
                "traffic_escape": 0.16,
                "long_move_tolerance": 0.20,
            },
            "final_ability": {
                "base_competitive_ability": 0.38,
                "class_strength": 0.14,
                "condition_fit": 0.15,
                "distance_fit": 0.13,
                "surface_fit": 0.10,
                "sustained_speed": 0.10,
            },
            "state_resilience": {
                "training_state": 0.27,
                "bodyweight_state": 0.23,
                "comment_state": 0.12,
                "data_confidence": 0.18,
                "final_reserve": 0.20,
            },
        },
        "cost_coefficients": {
            "position_cost_scale": 0.22,
            "friction_cost_scale": 0.26,
            "pace_cost_scale": 0.22,
            "path_cost_scale": 0.18,
            "progression_cost_scale": 0.20,
        },
        "pace": {
            "base": 50.0,
            "front_candidate_add": 2.2,
            "leader_need_add": 1.6,
            "competition_add": 7.0,
            "scenario_low_shift": -12.0,
            "scenario_high_shift": 14.0,
        },
        "path": {
            "inside_gate_fraction": 0.33,
            "outside_gate_fraction": 0.33,
            "inside_bias_effect": 5.0,
            "outside_bias_effect": 5.0,
            "congestion_effect": 6.0,
        },
        "position": {
            "front_band_fraction": 0.34,
            "mid_band_fraction": 0.67,
            "rank_momentum": 3.0,
            "leader_bonus": 3.5,
        },
        "ers": {
            "initial_base": 62.0,
            "reserve_weight": 0.25,
            "state_weight": 0.15,
            "min": 5.0,
            "max": 100.0,
        },
        "uncertainty": {
            "low_dcr_mix_to_neutral": 0.35,
            "high_dcr_mix_to_neutral": 0.05,
            "neutral": 50.0,
        },
        "audit": {
            "sim_xdi_rank_gap": 2,
            "top_role_rank": 3,
            "robust_a_scenario_share": 0.80,
            "robust_b_scenario_share": 0.60,
            "robust_c_scenario_share": 0.35,
        },
        "convergence": {
            "batch_size": 1000,
            "max_ssr_change_pp": 2.0,
            "top_rank_stability_count": 2,
        },
        "display": {
            "percent_decimals": 1,
            "top_combinations": 20,
        },
    }


def load_parameter_map(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return default_parameter_map()
    with open(path, "r", encoding="utf-8") as f:
        user = json.load(f)
    base = default_parameter_map()
    deep_update(base, user)
    return base


def deep_update(base: MutableMapping[str, Any], patch: Mapping[str, Any]) -> MutableMapping[str, Any]:
    for k, v in patch.items():
        if isinstance(v, Mapping) and isinstance(base.get(k), MutableMapping):
            deep_update(base[k], v)  # type: ignore[index]
        else:
            base[k] = deepcopy(v)
    return base


def validate_input(data: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if "race" not in data:
        errors.append("Missing 'race'.")
    if "environment" not in data:
        errors.append("Missing 'environment'.")
    horses = data.get("horses")
    if not isinstance(horses, list) or len(horses) < 2:
        errors.append("'horses' must contain at least two horses.")
        return errors
    seen = set()
    for i, horse in enumerate(horses):
        if "horse_no" not in horse:
            errors.append(f"horses[{i}] missing horse_no")
            continue
        n = int(horse["horse_no"])
        if n in seen:
            errors.append(f"Duplicate horse_no: {n}")
        seen.add(n)
        if "hsv" not in horse:
            errors.append(f"horse {n} missing hsv")
    return errors


# -----------------------------
# Data classes
# -----------------------------

@dataclass
class Horse:
    horse_no: int
    name: str
    gate_no: int
    hsv: Dict[str, float]
    static: Dict[str, float]
    pzr: Dict[str, float]
    static_roles: List[str]
    notes: List[str]
    hsv_provenance: Dict[str, List[Dict[str, Any]]]
    conditional_branches: List[Dict[str, Any]]
    evidence: Dict[str, Any]
    uncertainty_scale: float


@dataclass
class RunHorseState:
    horse_no: int
    strategy: str
    conditional_branch: str
    interaction_scenario: str
    gate_score: float
    acquisition_score: float
    leader_acquisition_score: float
    leader_survival_score: float
    position_cost: float
    early_rank: int
    mid_score: float
    mid_rank: int
    progression_score: float
    progression_cost: float
    corner_rank: int
    ers: float
    final_score: float
    finish_rank: int
    path_cost: float
    friction_cost: float
    pace_cost: float


# -----------------------------
# Engine
# -----------------------------

class KRSEngine:
    def __init__(self, data: Mapping[str, Any], params: Mapping[str, Any]):
        errs = validate_input(data)
        if errs:
            raise ValueError("\n".join(errs))
        self.data = deepcopy(dict(data))
        self.params = deepcopy(dict(params))
        self.race = dict(self.data["race"])
        self.env = dict(self.data["environment"])
        self.config = dict(self.data.get("simulation", {}))
        self.horses = self._build_horses(self.data["horses"])
        self.field_size = len(self.horses)
        self.master_seed = int(self.config.get("master_seed", 20260811))
        self.run_count = int(self.config.get("run_count", 5000))
        self.batch_size = int(self.config.get("batch_size", self.params["convergence"]["batch_size"]))
        self.seed_replicates = int(self.config.get("seed_replicates", 3))
        self.seed_stability_runs = int(self.config.get("seed_stability_runs", min(2000, max(500, self.run_count // 2))))
        self.scenario_runs = int(self.config.get("scenario_runs", min(2000, max(500, self.run_count // 5))))
        self.primary_leader_no = self._resolve_primary_leader()
        self.role_zones = self._resolve_role_zones()
        self.sim_dcr = self._calculate_sim_dcr()

    def _build_horses(self, raw_horses: Sequence[Mapping[str, Any]]) -> List[Horse]:
        horses: List[Horse] = []
        for h in raw_horses:
            hsv = ensure_score_map(h.get("hsv", {}), HSV_KEYS)
            static = ensure_score_map(h.get("static", {}), STATIC_KEYS)
            pzr = dict(h.get("pzr", {"aggressive": 1.0, "standard": 1.0, "conservative": 1.0}))
            if not pzr:
                pzr = {"aggressive": 1.0, "standard": 1.0, "conservative": 1.0}
            provenance_raw = h.get("hsv_provenance", {})
            provenance: Dict[str, List[Dict[str, Any]]] = {}
            if isinstance(provenance_raw, Mapping):
                for param, records in provenance_raw.items():
                    if isinstance(records, Mapping):
                        records = [records]
                    if isinstance(records, list):
                        provenance[str(param)] = [dict(r) for r in records if isinstance(r, Mapping)]
            branches = [dict(x) for x in h.get("conditional_branches", []) if isinstance(x, Mapping)]
            evidence = dict(h.get("evidence", {})) if isinstance(h.get("evidence", {}), Mapping) else {}
            uncertainty_scale = max(0.5, min(3.0, float(h.get("uncertainty_scale", 1.0))))
            horses.append(Horse(
                horse_no=int(h["horse_no"]),
                name=str(h.get("name", f"Horse {h['horse_no']}")),
                gate_no=int(h.get("gate_no", h["horse_no"])),
                hsv=hsv,
                static=static,
                pzr={str(k): max(0.0, float(v)) for k, v in pzr.items()},
                static_roles=[str(x).upper() for x in h.get("static_roles", [])],
                notes=[str(x) for x in h.get("notes", [])],
                hsv_provenance=provenance,
                conditional_branches=branches,
                evidence=evidence,
                uncertainty_scale=uncertainty_scale,
            ))
        horses.sort(key=lambda x: x.horse_no)
        return horses

    def _resolve_primary_leader(self) -> int:
        explicit = self.env.get("primary_leader_no")
        if explicit is not None:
            return int(explicit)
        return max(self.horses, key=lambda h: (h.hsv["leader_need"], h.hsv["initial_acceleration"])).horse_no

    def _resolve_role_zones(self) -> Dict[str, int]:
        zones = dict(self.env.get("gci_role_zones", {}))
        # These are race-specific INPUTS, not global KRS constants.
        w = int(zones.get("w_max_rank", max(1, math.ceil(self.field_size * 0.25))))
        p2 = int(zones.get("p2_max_rank", max(w, math.ceil(self.field_size * 0.45))))
        p3 = int(zones.get("p3_max_rank", max(p2, math.ceil(self.field_size * 0.65))))
        return {
            "w_max_rank": max(1, min(self.field_size, w)),
            "p2_max_rank": max(1, min(self.field_size, p2)),
            "p3_max_rank": max(1, min(self.field_size, p3)),
        }

    def _calculate_sim_dcr(self) -> float:
        explicit = self.data.get("sim_dcr")
        if explicit is not None:
            return clamp(float(explicit))
        # Use horse data confidence + environment confidence if available.
        horse_conf = safe_mean(h.hsv["data_confidence"] for h in self.horses)
        env_conf = float(self.env.get("gci_confidence", 60.0))
        similar = float(self.env.get("similar_condition_confidence", 55.0))
        latest = float(self.env.get("freshness_confidence", 60.0))
        return clamp(weighted_mean([
            (horse_conf, 0.45), (env_conf, 0.25), (similar, 0.15), (latest, 0.15)
        ]))

    def _effective_hsv(self, horse: Horse) -> Dict[str, float]:
        """Low confidence mixes unknown parameters toward neutral instead of simply widening noise."""
        dcr = normalize01(horse.hsv["data_confidence"])
        low_mix = float(self.params["uncertainty"]["low_dcr_mix_to_neutral"])
        high_mix = float(self.params["uncertainty"]["high_dcr_mix_to_neutral"])
        neutral = float(self.params["uncertainty"]["neutral"])
        mix = low_mix * (1.0 - dcr) + high_mix * dcr
        out = {}
        for k, v in horse.hsv.items():
            # Keep uncertainty descriptors themselves un-mixed.
            if k in {"data_confidence", "layoff_uncertainty"}:
                out[k] = v
            else:
                out[k] = (1.0 - mix) * v + mix * neutral
        return out

    def _horse_noise_scale(self, hsv: Mapping[str, float], base_sd: float, uncertainty_scale: float = 1.0) -> float:
        # Instability from layoff, low confidence, and upstream career/position uncertainty.
        # uncertainty_scale is an INPUT-side uncertainty multiplier, not a calibrated ability penalty.
        uncertainty = (100.0 - hsv["data_confidence"]) / 100.0
        layoff = hsv["layoff_uncertainty"] / 100.0
        return base_sd * (0.75 + 0.35 * uncertainty + 0.20 * layoff) * max(0.5, min(3.0, uncertainty_scale))

    def _select_interaction(self, rng: random.Random) -> Dict[str, Any]:
        interactions = self.env.get("leadership_interactions", [])
        if not isinstance(interactions, list) or not interactions:
            return {"name": "base", "weight": 1.0}
        weights = {}
        by_name = {}
        for i, raw in enumerate(interactions):
            if not isinstance(raw, Mapping):
                continue
            item = dict(raw)
            name = str(item.get("name", f"interaction_{i+1}"))
            weights[name] = max(0.0, float(item.get("weight", 1.0)))
            by_name[name] = item
        if not by_name:
            return {"name": "base", "weight": 1.0}
        chosen = categorical_choice(rng, weights)
        out = dict(by_name[chosen])
        out.setdefault("name", chosen)
        return out

    def _select_conditional_branch(self, rng: random.Random, horse: Horse, interaction_name: str) -> Dict[str, Any]:
        eligible: List[Dict[str, Any]] = []
        for raw in horse.conditional_branches:
            item = dict(raw)
            required = item.get("when_interaction")
            if required is not None:
                allowed = [str(required)] if isinstance(required, str) else [str(x) for x in required]
                if interaction_name not in allowed:
                    continue
            eligible.append(item)
        if not eligible:
            return {"name": "base", "weight": 1.0}
        weights = {str(x.get("name", f"branch_{i+1}")): max(0.0, float(x.get("weight", 1.0))) for i, x in enumerate(eligible)}
        by_name = {str(x.get("name", f"branch_{i+1}")): x for i, x in enumerate(eligible)}
        name = categorical_choice(rng, weights)
        out = dict(by_name[name])
        out.setdefault("name", name)
        return out

    def _apply_branch_hsv(self, hsv: Mapping[str, float], branch: Mapping[str, Any]) -> Dict[str, float]:
        out = dict(hsv)
        overrides = branch.get("hsv_overrides", {})
        if isinstance(overrides, Mapping):
            for k, v in overrides.items():
                if k in out:
                    out[k] = clamp(float(v))
        adjustments = branch.get("hsv_adjustments", {})
        if isinstance(adjustments, Mapping):
            for k, v in adjustments.items():
                if k in out:
                    out[k] = clamp(out[k] + float(v))
        return out

    def _scenario_common_shocks(self, rng: random.Random, scenario: str) -> Dict[str, float]:
        sds = self.params["common_shock_sd"]
        shocks = {
            "pace": rng.gauss(0, sds["pace"]),
            "track_speed": rng.gauss(0, sds["track_speed"]),
            "inside_bias": rng.gauss(0, sds["inside_bias"]),
            "outside_bias": rng.gauss(0, sds["outside_bias"]),
            "congestion": rng.gauss(0, sds["congestion"]),
        }
        if scenario == "low_friction":
            shocks["pace"] += float(self.params["pace"]["scenario_low_shift"])
            shocks["congestion"] -= 8.0
        elif scenario == "high_friction":
            shocks["pace"] += float(self.params["pace"]["scenario_high_shift"])
            shocks["congestion"] += 10.0
        return shocks

    def _strategy(self, rng: random.Random, horse: Horse, branch: Optional[Mapping[str, Any]] = None) -> str:
        if branch and isinstance(branch.get("strategy_weights"), Mapping):
            return categorical_choice(rng, branch["strategy_weights"])
        return categorical_choice(rng, horse.pzr)

    def provenance_audit(self) -> Dict[str, Any]:
        horses_out = {}
        overall_duplicate = 0
        missing = 0
        for h in self.horses:
            fact_to_params: Dict[str, List[str]] = defaultdict(list)
            parameter_coverage = 0
            for param in HSV_KEYS:
                records = h.hsv_provenance.get(param, [])
                if records:
                    parameter_coverage += 1
                for r in records:
                    fid = r.get("fact_id") or r.get("duplicate_fact_id")
                    if fid:
                        fact_to_params[str(fid)].append(param)
            duplicates = {fid: sorted(set(params)) for fid, params in fact_to_params.items() if len(set(params)) > 1}
            overall_duplicate += len(duplicates)
            if parameter_coverage == 0:
                missing += 1
            horses_out[h.horse_no] = {
                "name": h.name,
                "provenance_parameter_coverage": parameter_coverage,
                "provenance_parameter_total": len(HSV_KEYS),
                "duplicate_fact_ids": duplicates,
                "OFOI_status": "REVIEW" if duplicates else ("LEGACY_NO_PROVENANCE" if parameter_coverage == 0 else "PASS"),
            }
        return {
            "status": "REVIEW" if overall_duplicate else ("LEGACY_INPUT" if missing == len(self.horses) else "PASS"),
            "duplicate_fact_groups": overall_duplicate,
            "horses_without_provenance": missing,
            "horses": horses_out,
            "note": "Duplicate fact IDs are an audit warning. v1.1 does not silently alter supplied HSV values; revise upstream mapping or branch the condition explicitly.",
        }

    def evidence_independence_audit(self) -> Dict[str, Any]:
        out = {}
        review = 0
        for h in self.horses:
            static_ids = {str(x) for x in h.evidence.get("static_fact_ids", [])}
            krs_ids = {str(x) for x in h.evidence.get("krs_fact_ids", [])}
            overlap = sorted(static_ids & krs_ids)
            denom = max(1, len(static_ids | krs_ids))
            ratio = len(overlap) / denom
            status = "REVIEW_SHARED_EVIDENCE" if overlap else ("UNDECLARED" if not static_ids and not krs_ids else "PASS")
            if overlap:
                review += 1
            out[h.horse_no] = {
                "name": h.name,
                "status": status,
                "shared_fact_ids": overlap,
                "shared_ratio": ratio,
                "note": "Static-KRS agreement from shared facts is structural consistency, not an independent second vote.",
            }
        return {"status": "REVIEW" if review else "PASS_OR_UNDECLARED", "horses": out}

    def _path_score_adjustment(self, horse: Horse, hsv: Mapping[str, float], shocks: Mapping[str, float]) -> Tuple[float, float]:
        n = self.field_size
        gate_frac = (horse.gate_no - 0.5) / max(1, n)
        inside_thr = float(self.params["path"]["inside_gate_fraction"])
        outside_thr = 1.0 - float(self.params["path"]["outside_gate_fraction"])
        adjustment = 0.0
        path_cost = 0.0
        if gate_frac <= inside_thr:
            inside_fit = hsv["inside_cut_ability"] + 0.5 * hsv["crowd_tolerance"]
            adjustment += (inside_fit - 50.0) * 0.08
            adjustment += shocks["inside_bias"] * 0.30
            path_cost += max(0.0, 50.0 - inside_fit) * 0.07
        elif gate_frac >= outside_thr:
            outside_fit = hsv["outside_press_ability"] + 0.4 * hsv["sustained_speed"]
            adjustment += (outside_fit - 50.0) * 0.06
            adjustment += shocks["outside_bias"] * 0.30
            path_cost += max(0.0, 50.0 - outside_fit) * 0.06
        else:
            adjustment += (hsv["crowd_tolerance"] - 50.0) * 0.04
        path_cost += max(0.0, shocks["congestion"]) * (100.0 - hsv["traffic_escape"]) / 100.0 * 0.08
        return adjustment, max(0.0, path_cost)

    def _compute_pace_level(self, shocks: Mapping[str, float], acquisition_rank: Mapping[int, int], leader_no: int, scenario: str) -> float:
        front_candidates = int(self.env.get("front_candidate_count", 0))
        if front_candidates <= 0:
            front_candidates = sum(1 for h in self.horses if h.hsv["position_intent"] >= 60 or h.hsv["leader_need"] >= 60)
        leader_need_count = int(self.env.get("leader_need_count", 0))
        if leader_need_count <= 0:
            leader_need_count = sum(1 for h in self.horses if h.hsv["leader_need"] >= 70)
        top_front = max(2, math.ceil(self.field_size * float(self.params["position"]["front_band_fraction"])))
        competition = sum(1 for h in self.horses if acquisition_rank[h.horse_no] <= top_front and h.hsv["leader_need"] >= 60)
        pace = float(self.params["pace"]["base"])
        pace += front_candidates * float(self.params["pace"]["front_candidate_add"])
        pace += leader_need_count * float(self.params["pace"]["leader_need_add"])
        pace += max(0, competition - 1) * float(self.params["pace"]["competition_add"])
        pace += float(self.env.get("gci_pace_adjustment", 0.0))
        pace += shocks["pace"]
        if scenario == "leader_success":
            pace -= 4.0
        elif scenario == "leader_failure":
            pace += 6.0
        return clamp(pace)

    def simulate_run(self, run_seed: int, scenario: str = "natural") -> Dict[str, Any]:
        rng = random.Random(run_seed)
        shocks = self._scenario_common_shocks(rng, scenario)
        weights = self.params["stage_weights"]
        noise_cfg = self.params["score_noise"]
        strategy_cfg = self.params["strategy_adjustment"]

        interaction = self._select_interaction(rng)
        interaction_name = str(interaction.get("name", "base"))
        branches: Dict[int, Dict[str, Any]] = {h.horse_no: self._select_conditional_branch(rng, h, interaction_name) for h in self.horses}
        hsv_map: Dict[int, Dict[str, float]] = {
            h.horse_no: self._apply_branch_hsv(self._effective_hsv(h), branches[h.horse_no]) for h in self.horses
        }
        strategies: Dict[int, str] = {h.horse_no: self._strategy(rng, h, branches[h.horse_no]) for h in self.horses}

        # Stage 0: gate
        gate_scores: Dict[int, float] = {}
        for h in self.horses:
            hsv = hsv_map[h.horse_no]
            mean = weighted_mean([
                (hsv["gate_reliability"], weights["gate"]["gate_reliability"]),
                (hsv["initial_acceleration"], weights["gate"]["initial_acceleration"]),
            ])
            sd = self._horse_noise_scale(hsv, float(noise_cfg["gate_sd"]), h.uncertainty_scale * float(branches[h.horse_no].get("uncertainty_scale", 1.0)))
            gate_scores[h.horse_no] = normal_score(rng, mean, sd)

        # Stage 1: acquisition
        acquisition_scores: Dict[int, float] = {}
        position_costs: Dict[int, float] = {}
        path_costs: Dict[int, float] = {}
        for h in self.horses:
            hsv = hsv_map[h.horse_no]
            strategy = strategies[h.horse_no]
            adj = strategy_cfg.get(strategy, strategy_cfg["standard"])
            path_adj, path_cost = self._path_score_adjustment(h, hsv, shocks)
            acq_mean = weighted_mean([
                (gate_scores[h.horse_no], weights["acquisition"]["gate"]),
                (hsv["initial_acceleration"], weights["acquisition"]["initial_acceleration"]),
                (hsv["position_intent"] + float(adj["intent"]), weights["acquisition"]["position_intent"]),
                (hsv["inside_cut_ability"], weights["acquisition"]["inside_cut_ability"]),
                (hsv["outside_press_ability"], weights["acquisition"]["outside_press_ability"]),
                (hsv["stalk_acceptance"], weights["acquisition"]["stalk_acceptance"]),
                (hsv["crowd_tolerance"], weights["acquisition"]["crowd_tolerance"]),
            ]) + path_adj
            if scenario == "leader_success" and h.horse_no == self.primary_leader_no:
                acq_mean += 10.0
            elif scenario == "leader_failure" and h.horse_no == self.primary_leader_no:
                acq_mean -= 18.0
            acq_mean += float(branches[h.horse_no].get("acquisition_adjustment", 0.0))
            ia = interaction.get("acquisition_adjustments", {})
            if isinstance(ia, Mapping):
                acq_mean += float(ia.get(str(h.horse_no), ia.get(h.horse_no, 0.0)))
            sd = self._horse_noise_scale(hsv, float(noise_cfg["acquisition_sd"]), h.uncertainty_scale * float(branches[h.horse_no].get("uncertainty_scale", 1.0)))
            acquisition_scores[h.horse_no] = normal_score(rng, acq_mean, sd)
            effort = max(0.0, hsv["position_intent"] + float(adj["intent"]) - acquisition_scores[h.horse_no])
            position_cost = effort * float(self.params["cost_coefficients"]["position_cost_scale"])
            position_cost += max(0.0, float(adj["position_cost"]))
            position_costs[h.horse_no] = position_cost
            path_costs[h.horse_no] = path_cost

        acquisition_rank = rank_desc(acquisition_scores)

        # Leader determination
        leader_scores: Dict[int, float] = {}
        for h in self.horses:
            hsv = hsv_map[h.horse_no]
            leader_scores[h.horse_no] = weighted_mean([
                (acquisition_scores[h.horse_no], weights["leader"]["acquisition"]),
                (hsv["leader_need"], weights["leader"]["leader_need"]),
                (hsv["initial_acceleration"], weights["leader"]["initial_acceleration"]),
                (hsv["outside_press_ability"], weights["leader"]["outside_press_ability"]),
            ]) + rng.gauss(0, 3.0)
        if scenario == "leader_success":
            leader_scores[self.primary_leader_no] += 25.0
        elif scenario == "leader_failure":
            leader_scores[self.primary_leader_no] -= 30.0
        lsa = interaction.get("leader_score_adjustments", {})
        if isinstance(lsa, Mapping):
            for n in list(leader_scores):
                leader_scores[n] += float(lsa.get(str(n), lsa.get(n, 0.0)))
        leader_no = max(leader_scores, key=leader_scores.get)
        leader_acquisition_scores = dict(leader_scores)

        pace_level = self._compute_pace_level(shocks, acquisition_rank, leader_no, scenario)
        pace_level = clamp(pace_level + float(interaction.get("pace_shift", 0.0)))
        front_cut = max(2, math.ceil(self.field_size * float(self.params["position"]["front_band_fraction"])))

        # Initialize ERS
        ers: Dict[int, float] = {}
        state_resilience: Dict[int, float] = {}
        for h in self.horses:
            hsv = hsv_map[h.horse_no]
            # v1.1 structural safeguard: data_confidence controls shrinkage/noise/SIM-DCR,
            # not the horse's physical residual ability. The legacy provisional map entry is
            # retained for backward file compatibility but is intentionally excluded here.
            state_resilience[h.horse_no] = weighted_mean([
                (hsv[k], v) for k, v in weights["state_resilience"].items() if k != "data_confidence"
            ])
            ers[h.horse_no] = clamp(
                float(self.params["ers"]["initial_base"])
                + (hsv["final_reserve"] - 50.0) * float(self.params["ers"]["reserve_weight"])
                + (state_resilience[h.horse_no] - 50.0) * float(self.params["ers"]["state_weight"]),
                float(self.params["ers"]["min"]), float(self.params["ers"]["max"]),
            )

        # Leadership Survival is separated from Leadership Acquisition.
        # It reuses existing maintenance evidence and final_reserve; no new calibrated coefficient map is introduced.
        leader_survival_scores: Dict[int, float] = {}
        for h in self.horses:
            hsv = hsv_map[h.horse_no]
            maintenance_base = weighted_mean([(hsv[k], v) for k, v in weights["maintenance"].items()])
            surv = safe_mean([maintenance_base, hsv["final_reserve"]])
            surv += float(branches[h.horse_no].get("survival_adjustment", 0.0))
            sa = interaction.get("survival_adjustments", {})
            if isinstance(sa, Mapping):
                surv += float(sa.get(str(h.horse_no), sa.get(h.horse_no, 0.0)))
            leader_survival_scores[h.horse_no] = clamp(surv)

        # Stage 2-3: friction / pace / maintenance
        friction_costs: Dict[int, float] = {}
        pace_costs: Dict[int, float] = {}
        mid_scores: Dict[int, float] = {}
        for h in self.horses:
            hsv = hsv_map[h.horse_no]
            r = acquisition_rank[h.horse_no]
            is_front = r <= front_cut
            friction_pressure = max(0.0, pace_level - 50.0)
            if is_front:
                friction_pressure += max(0.0, shocks["congestion"]) * 0.45
                friction_pressure += max(0.0, 70.0 - hsv["stalk_acceptance"]) * 0.10 if h.horse_no != leader_no else 0.0
            else:
                friction_pressure *= 0.35
            friction_resistance = 0.55 * hsv["front_friction_tolerance"] + 0.45 * hsv["pressure_tolerance"]
            friction_cost = max(0.0, friction_pressure * (100.0 - friction_resistance) / 100.0)
            friction_cost *= float(self.params["cost_coefficients"]["friction_cost_scale"])
            friction_cost += float(branches[h.horse_no].get("friction_adjustment", 0.0))
            fa = interaction.get("friction_adjustments", {})
            if isinstance(fa, Mapping):
                friction_cost += float(fa.get(str(h.horse_no), fa.get(h.horse_no, 0.0)))
            friction_cost = max(0.0, friction_cost)
            friction_costs[h.horse_no] = friction_cost

            pace_cost = max(0.0, pace_level - hsv["sustained_speed"])
            pace_cost *= (1.0 if is_front else 0.75)
            pace_cost *= float(self.params["cost_coefficients"]["pace_cost_scale"])
            pace_costs[h.horse_no] = pace_cost

            ers[h.horse_no] = clamp(
                ers[h.horse_no]
                - position_costs[h.horse_no]
                - path_costs[h.horse_no] * float(self.params["cost_coefficients"]["path_cost_scale"])
                - friction_cost
                - pace_cost
                + (state_resilience[h.horse_no] - 50.0) * 0.03,
                float(self.params["ers"]["min"]), float(self.params["ers"]["max"]),
            )

            maint_mean = weighted_mean([
                (hsv[k], v) for k, v in weights["maintenance"].items()
            ])
            tactical = (front_cut + 1 - min(r, front_cut + 1)) * float(self.params["position"]["rank_momentum"])
            if h.horse_no == leader_no:
                survival_factor = min(1.0, max(0.0, leader_survival_scores[h.horse_no] / 50.0))
                tactical += float(self.params["position"]["leader_bonus"]) * survival_factor
            mid_mean = (
                0.38 * acquisition_scores[h.horse_no]
                + 0.42 * maint_mean
                + 0.20 * ers[h.horse_no]
                + tactical
                - friction_cost * 1.8
                - pace_cost * 1.3
            )
            sd = self._horse_noise_scale(hsv, float(noise_cfg["maintenance_sd"]), h.uncertainty_scale * float(branches[h.horse_no].get("uncertainty_scale", 1.0)))
            mid_scores[h.horse_no] = normal_score(rng, mid_mean, sd)

        mid_rank = rank_desc(mid_scores)

        # Stage 4-5: progression and corner rank
        progression_scores: Dict[int, float] = {}
        progression_costs: Dict[int, float] = {}
        corner_scores: Dict[int, float] = {}
        for h in self.horses:
            hsv = hsv_map[h.horse_no]
            strategy = strategies[h.horse_no]
            adj = strategy_cfg.get(strategy, strategy_cfg["standard"])
            prog_mean = weighted_mean([(hsv[k], v) for k, v in weights["progression"].items()])
            prog_mean += float(adj["progression"])
            # High pace can create progression opportunity, but only if horse can tolerate it.
            prog_mean += max(0.0, pace_level - 55.0) * (hsv["pressure_tolerance"] / 100.0) * 0.10
            prog_mean -= max(0.0, shocks["congestion"]) * (100.0 - hsv["traffic_escape"]) / 100.0 * 0.08
            sd = self._horse_noise_scale(hsv, float(noise_cfg["progression_sd"]), h.uncertainty_scale * float(branches[h.horse_no].get("uncertainty_scale", 1.0)))
            progression_scores[h.horse_no] = normal_score(rng, prog_mean, sd)
            move_intensity = max(0.0, progression_scores[h.horse_no] - 50.0)
            progression_cost = move_intensity * (100.0 - hsv["long_move_tolerance"]) / 100.0
            progression_cost *= float(self.params["cost_coefficients"]["progression_cost_scale"])
            progression_costs[h.horse_no] = progression_cost
            ers[h.horse_no] = clamp(
                ers[h.horse_no] - progression_cost + (hsv["long_move_tolerance"] - 50.0) * 0.015,
                float(self.params["ers"]["min"]), float(self.params["ers"]["max"]),
            )
            # Mid-position + progression + reserve determine 4-corner position.
            corner_scores[h.horse_no] = (
                0.52 * mid_scores[h.horse_no]
                + 0.30 * progression_scores[h.horse_no]
                + 0.18 * ers[h.horse_no]
                + rng.gauss(0, 2.0)
            )
        corner_rank = rank_desc(corner_scores)

        # Stage 6: final performance
        final_scores: Dict[int, float] = {}
        for h in self.horses:
            hsv = hsv_map[h.horse_no]
            ability = weighted_mean([(hsv[k], v) for k, v in weights["final_ability"].items()])
            z4_tactical = (self.field_size - corner_rank[h.horse_no]) / max(1, self.field_size - 1) * 8.0
            leader_tactical = 0.0
            if h.horse_no == leader_no and corner_rank[h.horse_no] <= self.role_zones["w_max_rank"]:
                leader_tactical = 2.0 * min(1.0, max(0.0, leader_survival_scores[h.horse_no] / 50.0))
            decel = hsv["deceleration_risk"] * max(0.0, 60.0 - ers[h.horse_no]) / 100.0 * 0.18
            final_mean = (
                0.52 * ability
                + 0.26 * ers[h.horse_no]
                + 0.12 * corner_scores[h.horse_no]
                + 0.10 * state_resilience[h.horse_no]
                + z4_tactical
                + leader_tactical
                + shocks["track_speed"] * (hsv["surface_fit"] - 50.0) / 100.0 * 0.15
                - decel
            )
            sd = self._horse_noise_scale(hsv, float(noise_cfg["final_sd"]), h.uncertainty_scale * float(branches[h.horse_no].get("uncertainty_scale", 1.0)))
            final_scores[h.horse_no] = normal_score(rng, final_mean, sd)

        finish_rank = rank_desc(final_scores)

        horse_states: Dict[int, RunHorseState] = {}
        for h in self.horses:
            horse_states[h.horse_no] = RunHorseState(
                horse_no=h.horse_no,
                strategy=strategies[h.horse_no],
                conditional_branch=str(branches[h.horse_no].get("name", "base")),
                interaction_scenario=interaction_name,
                gate_score=gate_scores[h.horse_no],
                acquisition_score=acquisition_scores[h.horse_no],
                leader_acquisition_score=leader_acquisition_scores[h.horse_no],
                leader_survival_score=leader_survival_scores[h.horse_no],
                position_cost=position_costs[h.horse_no],
                early_rank=acquisition_rank[h.horse_no],
                mid_score=mid_scores[h.horse_no],
                mid_rank=mid_rank[h.horse_no],
                progression_score=progression_scores[h.horse_no],
                progression_cost=progression_costs[h.horse_no],
                corner_rank=corner_rank[h.horse_no],
                ers=ers[h.horse_no],
                final_score=final_scores[h.horse_no],
                finish_rank=finish_rank[h.horse_no],
                path_cost=path_costs[h.horse_no],
                friction_cost=friction_costs[h.horse_no],
                pace_cost=pace_costs[h.horse_no],
            )

        order = [n for n, _ in sorted(finish_rank.items(), key=lambda kv: kv[1])]
        return {
            "seed": run_seed,
            "scenario": scenario,
            "interaction_scenario": interaction_name,
            "interaction": interaction,
            "leader_no": leader_no,
            "pace_level": pace_level,
            "shocks": shocks,
            "order": order,
            "states": horse_states,
        }

    def _aggregate_runs(self, runs: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        n = len(runs)
        finish_counts = {h.horse_no: Counter() for h in self.horses}
        leader_counts = Counter()
        pos1 = defaultdict(list)
        pos3 = defaultdict(list)
        pos4 = defaultdict(list)
        ers_vals = defaultdict(list)
        strategy_counts = {h.horse_no: Counter() for h in self.horses}
        branch_counts = {h.horse_no: Counter() for h in self.horses}
        interaction_counts = Counter()
        leader_acq_vals = defaultdict(list)
        leader_surv_vals = defaultdict(list)
        z4_counts = {h.horse_no: Counter() for h in self.horses}
        exacta_counts = Counter()
        trifecta_counts = Counter()
        pace_vals = []

        for run in runs:
            order = run["order"]
            if len(order) >= 2:
                exacta_counts[(order[0], order[1])] += 1
            if len(order) >= 3:
                trifecta_counts[(order[0], order[1], order[2])] += 1
            leader_counts[run["leader_no"]] += 1
            interaction_counts[run.get("interaction_scenario", "base")] += 1
            pace_vals.append(run["pace_level"])
            for h in self.horses:
                s: RunHorseState = run["states"][h.horse_no]
                finish_counts[h.horse_no][s.finish_rank] += 1
                pos1[h.horse_no].append(s.early_rank)
                pos3[h.horse_no].append(s.mid_rank)
                pos4[h.horse_no].append(s.corner_rank)
                ers_vals[h.horse_no].append(s.ers)
                strategy_counts[h.horse_no][s.strategy] += 1
                branch_counts[h.horse_no][s.conditional_branch] += 1
                leader_acq_vals[h.horse_no].append(s.leader_acquisition_score)
                leader_surv_vals[h.horse_no].append(s.leader_survival_score)
                if s.corner_rank <= self.role_zones["w_max_rank"]:
                    z4_counts[h.horse_no]["W"] += 1
                if s.corner_rank <= self.role_zones["p2_max_rank"]:
                    z4_counts[h.horse_no]["P2"] += 1
                if s.corner_rank <= self.role_zones["p3_max_rank"]:
                    z4_counts[h.horse_no]["P3"] += 1

        ssr = {}
        positions = {}
        for h in self.horses:
            c = finish_counts[h.horse_no]
            ssr[h.horse_no] = {
                "SSR-W": c[1] / n,
                "SSR-P2": c[2] / n,
                "SSR-P3": c[3] / n,
                "SSR-T3": (c[1] + c[2] + c[3]) / n,
                "LSR": leader_counts[h.horse_no] / n,
                "Z4R-W": z4_counts[h.horse_no]["W"] / n,
                "Z4R-P2": z4_counts[h.horse_no]["P2"] / n,
                "Z4R-P3": z4_counts[h.horse_no]["P3"] / n,
            }
            for label, vals in [("1角", pos1[h.horse_no]), ("3角", pos3[h.horse_no]), ("4角", pos4[h.horse_no])]:
                vals_sorted = sorted(vals)
                positions.setdefault(h.horse_no, {})[label] = {
                    "median": statistics.median(vals_sorted),
                    "p25": percentile(vals_sorted, 0.25),
                    "p75": percentile(vals_sorted, 0.75),
                }
            positions[h.horse_no]["ERS"] = {
                "median": statistics.median(ers_vals[h.horse_no]),
                "p25": percentile(sorted(ers_vals[h.horse_no]), 0.25),
                "p75": percentile(sorted(ers_vals[h.horse_no]), 0.75),
            }
            positions[h.horse_no]["strategy_share"] = {
                k: v / n for k, v in strategy_counts[h.horse_no].items()
            }
            positions[h.horse_no]["conditional_branch_share"] = {
                k: v / n for k, v in branch_counts[h.horse_no].items()
            }
            positions[h.horse_no]["Leadership-Acquisition"] = {
                "median": statistics.median(leader_acq_vals[h.horse_no]),
                "p25": percentile(sorted(leader_acq_vals[h.horse_no]), 0.25),
                "p75": percentile(sorted(leader_acq_vals[h.horse_no]), 0.75),
            }
            positions[h.horse_no]["Leadership-Survival"] = {
                "median": statistics.median(leader_surv_vals[h.horse_no]),
                "p25": percentile(sorted(leader_surv_vals[h.horse_no]), 0.25),
                "p75": percentile(sorted(leader_surv_vals[h.horse_no]), 0.75),
            }

        topn = int(self.params["display"]["top_combinations"])
        exacta = [
            {"W": a, "P2": b, "count": c, "frequency": c / n}
            for (a, b), c in exacta_counts.most_common(topn)
        ]
        trifecta = [
            {"W": a, "P2": b, "P3": c3, "count": c, "frequency": c / n}
            for (a, b, c3), c in trifecta_counts.most_common(topn)
        ]
        return {
            "run_count": n,
            "ssr": ssr,
            "positions": positions,
            "pace": {
                "median": statistics.median(pace_vals),
                "p25": percentile(sorted(pace_vals), 0.25),
                "p75": percentile(sorted(pace_vals), 0.75),
            },
            "leadership_interaction_share": {k: v / n for k, v in interaction_counts.items()},
            "top_exacta_occurrence": exacta,
            "top_trifecta_occurrence": trifecta,
        }

    def run_batch(self, run_count: int, master_seed: int, scenario: str = "natural") -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        runs: List[Dict[str, Any]] = []
        for i in range(run_count):
            run_seed = stable_hash_int(master_seed, scenario, i, self.race.get("prediction_id", ""))
            runs.append(self.simulate_run(run_seed, scenario=scenario))
        return self._aggregate_runs(runs), runs

    def convergence_audit(self, runs: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        if not runs:
            return {"status": "NO_RUNS"}
        batch_size = max(100, self.batch_size)
        checkpoints = []
        prev_ssr = None
        for end in range(batch_size, len(runs) + 1, batch_size):
            agg = self._aggregate_runs(runs[:end])
            ssr_w = {n: agg["ssr"][n]["SSR-W"] for n in agg["ssr"]}
            ssr_t3 = {n: agg["ssr"][n]["SSR-T3"] for n in agg["ssr"]}
            cp = {
                "runs": end,
                "ssr_w_rank": rank_desc(ssr_w),
                "ssr_t3_rank": rank_desc(ssr_t3),
            }
            if prev_ssr is not None:
                cp["max_ssr_w_change_pp"] = max(abs(ssr_w[n] - prev_ssr[n]) for n in ssr_w) * 100.0
            checkpoints.append(cp)
            prev_ssr = ssr_w
        if len(runs) % batch_size != 0:
            agg = self._aggregate_runs(runs)
            ssr_w = {n: agg["ssr"][n]["SSR-W"] for n in agg["ssr"]}
            ssr_t3 = {n: agg["ssr"][n]["SSR-T3"] for n in agg["ssr"]}
            cp = {
                "runs": len(runs),
                "ssr_w_rank": rank_desc(ssr_w),
                "ssr_t3_rank": rank_desc(ssr_t3),
            }
            if prev_ssr is not None:
                cp["max_ssr_w_change_pp"] = max(abs(ssr_w[n] - prev_ssr[n]) for n in ssr_w) * 100.0
            checkpoints.append(cp)

        threshold = float(self.params["convergence"]["max_ssr_change_pp"])
        last_changes = [c.get("max_ssr_w_change_pp", float("inf")) for c in checkpoints[-2:]]
        converged = bool(last_changes) and all(x <= threshold for x in last_changes if math.isfinite(x))
        return {
            "status": "CONVERGED" if converged else "REVIEW",
            "threshold_pp_provisional": threshold,
            "checkpoints": checkpoints,
        }

    def seed_stability_audit(self) -> Dict[str, Any]:
        if self.seed_replicates <= 1:
            return {"status": "SKIPPED", "replicates": 1}
        reps = []
        for i in range(self.seed_replicates):
            seed = stable_hash_int(self.master_seed, "stability", i)
            agg, _ = self.run_batch(self.seed_stability_runs, seed, "natural")
            ssr_w = {n: agg["ssr"][n]["SSR-W"] for n in agg["ssr"]}
            ssr_t3 = {n: agg["ssr"][n]["SSR-T3"] for n in agg["ssr"]}
            reps.append({"seed": seed, "ssr_w": ssr_w, "ssr_t3": ssr_t3, "w_rank": rank_desc(ssr_w), "t3_rank": rank_desc(ssr_t3)})
        stats = {}
        for h in self.horses:
            vals = [r["ssr_w"][h.horse_no] for r in reps]
            ranks = [r["w_rank"][h.horse_no] for r in reps]
            stats[h.horse_no] = {
                "ssr_w_mean": statistics.mean(vals),
                "ssr_w_sd": statistics.pstdev(vals) if len(vals) > 1 else 0.0,
                "w_rank_min": min(ranks),
                "w_rank_max": max(ranks),
            }
        top1s = [min(r["w_rank"], key=r["w_rank"].get) for r in reps]
        status = "STABLE" if len(set(top1s)) == 1 else "REVIEW"
        return {"status": status, "replicates": reps, "horse_stats": stats}

    def scenario_analysis(self) -> Dict[str, Any]:
        scenarios = ["natural", "low_friction", "high_friction", "leader_success", "leader_failure"]
        out = {}
        for s in scenarios:
            seed = stable_hash_int(self.master_seed, "scenario", s)
            runs = self.scenario_runs if s != "natural" else min(self.scenario_runs, self.run_count)
            agg, _ = self.run_batch(runs, seed, s)
            out[s] = agg
        return out

    def robustness_rank(self, scenarios: Mapping[str, Any]) -> Dict[int, str]:
        scenario_names = list(scenarios)
        top_role_rank = int(self.params["audit"]["top_role_rank"])
        shares = {}
        for h in self.horses:
            count = 0
            for s in scenario_names:
                ssr = scenarios[s]["ssr"]
                t3_rank = rank_desc({n: ssr[n]["SSR-T3"] for n in ssr})
                w_rank = rank_desc({n: ssr[n]["SSR-W"] for n in ssr})
                if t3_rank[h.horse_no] <= top_role_rank or w_rank[h.horse_no] <= top_role_rank:
                    count += 1
            shares[h.horse_no] = count / max(1, len(scenario_names))
        a = float(self.params["audit"]["robust_a_scenario_share"])
        b = float(self.params["audit"]["robust_b_scenario_share"])
        c = float(self.params["audit"]["robust_c_scenario_share"])
        result = {}
        for n, share in shares.items():
            result[n] = "A" if share >= a else "B" if share >= b else "C" if share >= c else "D"
        return result

    def sim_xdi(self, base_agg: Mapping[str, Any]) -> List[Dict[str, Any]]:
        ssr = base_agg["ssr"]
        static_tpi = {h.horse_no: h.static["tpi"] for h in self.horses}
        static_zwin = {h.horse_no: h.static["zai_win"] for h in self.horses}
        static_zplace = {h.horse_no: h.static["zai_place"] for h in self.horses}
        sim_w = {n: ssr[n]["SSR-W"] for n in ssr}
        sim_t3 = {n: ssr[n]["SSR-T3"] for n in ssr}
        tpi_rank = rank_desc(static_tpi)
        zwin_rank = rank_desc(static_zwin)
        zplace_rank = rank_desc(static_zplace)
        sim_w_rank = rank_desc(sim_w)
        sim_t3_rank = rank_desc(sim_t3)
        gap_thr = int(self.params["audit"]["sim_xdi_rank_gap"])
        out = []
        for h in self.horses:
            w_gap = zwin_rank[h.horse_no] - sim_w_rank[h.horse_no]
            t3_gap = zplace_rank[h.horse_no] - sim_t3_rank[h.horse_no]
            tpi_gap = tpi_rank[h.horse_no] - sim_w_rank[h.horse_no]
            if abs(w_gap) >= gap_thr or abs(t3_gap) >= gap_thr or abs(tpi_gap) >= gap_thr:
                direction = []
                if w_gap > 0 or tpi_gap > 0:
                    direction.append("SIM_UP_W")
                if w_gap < 0 or tpi_gap < 0:
                    direction.append("SIM_DOWN_W")
                if t3_gap > 0:
                    direction.append("SIM_UP_T3")
                if t3_gap < 0:
                    direction.append("SIM_DOWN_T3")
                out.append({
                    "horse_no": h.horse_no,
                    "name": h.name,
                    "static_tpi_rank": tpi_rank[h.horse_no],
                    "static_zai_win_rank": zwin_rank[h.horse_no],
                    "static_zai_place_rank": zplace_rank[h.horse_no],
                    "sim_ssr_w_rank": sim_w_rank[h.horse_no],
                    "sim_ssr_t3_rank": sim_t3_rank[h.horse_no],
                    "rank_gaps": {"W_vs_ZWIN": w_gap, "T3_vs_ZPLACE": t3_gap, "W_vs_TPI": tpi_gap},
                    "direction": direction,
                    "note": "SIM-XDI is an audit trigger, not an automatic role change.",
                })
        return out

    def role_audit_triggers(self, base_agg: Mapping[str, Any], robustness: Mapping[int, str]) -> List[Dict[str, Any]]:
        ssr = base_agg["ssr"]
        w_rank = rank_desc({n: ssr[n]["SSR-W"] for n in ssr})
        p2_rank = rank_desc({n: ssr[n]["SSR-P2"] for n in ssr})
        p3_rank = rank_desc({n: ssr[n]["SSR-P3"] for n in ssr})
        t3_rank = rank_desc({n: ssr[n]["SSR-T3"] for n in ssr})
        top_role = int(self.params["audit"]["top_role_rank"])
        triggers = []
        for h in self.horses:
            current = set(h.static_roles)
            flags = []
            if w_rank[h.horse_no] <= top_role and "W" not in current and robustness[h.horse_no] in {"A", "B"}:
                flags.append("W1R_REAUDIT")
            if p2_rank[h.horse_no] <= top_role and "P2" not in current and base_agg["ssr"][h.horse_no]["Z4R-P2"] >= 0.40:
                flags.append("LS2_REAUDIT")
            if (p3_rank[h.horse_no] <= top_role or t3_rank[h.horse_no] <= top_role) and "P3" not in current:
                flags.append("T3R_REAUDIT")
            if h.static["zai_place"] >= 70 and w_rank[h.horse_no] > top_role + 1:
                flags.append("WAX_SIM_CHECK")
            # Extreme-SIM-XDI: a statically protected role falling to the lower half is a mandatory input re-audit, not deletion permission.
            lower_half = max(2, math.ceil(self.field_size / 2))
            if current and t3_rank[h.horse_no] > lower_half:
                flags.append("EXTREME_SIM_XDI_INPUT_REAUDIT")
            if flags:
                triggers.append({
                    "horse_no": h.horse_no,
                    "name": h.name,
                    "static_roles": sorted(current),
                    "triggers": flags,
                    "robustness": robustness[h.horse_no],
                    "ranks": {"SSR-W": w_rank[h.horse_no], "SSR-P2": p2_rank[h.horse_no], "SSR-P3": p3_rank[h.horse_no], "SSR-T3": t3_rank[h.horse_no]},
                    "note": "Re-audit only. Final W/P2/P3 remains governed by v4.6 and course rules.",
                })
        return triggers

    def run_all(self) -> Dict[str, Any]:
        base_agg, base_runs = self.run_batch(self.run_count, self.master_seed, "natural")
        convergence = self.convergence_audit(base_runs)
        seed_stability = self.seed_stability_audit()
        scenarios = self.scenario_analysis()
        robustness = self.robustness_rank(scenarios)
        sim_xdi = self.sim_xdi(base_agg)
        role_triggers = self.role_audit_triggers(base_agg, robustness)
        provenance = self.provenance_audit()
        evidence_independence = self.evidence_independence_audit()

        # Add robustness into summary
        for n, r in robustness.items():
            base_agg["ssr"][n]["Robustness"] = r

        horse_index = {h.horse_no: h for h in self.horses}
        horse_summary = []
        for n in sorted(base_agg["ssr"]):
            horse_summary.append({
                "horse_no": n,
                "name": horse_index[n].name,
                **base_agg["ssr"][n],
                "positions": base_agg["positions"][n],
                "static_roles": horse_index[n].static_roles,
            })

        snapshot_id = str(self.race.get("simulation_snapshot_id") or f"SIM-{stable_hash_int(self.race.get('prediction_id','NA'), self.master_seed, self.run_count):010d}")
        return {
            "engine": {
                "name": "KRS-Engine",
                "engine_version": ENGINE_VERSION,
                "parameter_map_version": self.params.get("parameter_map_version", DEFAULT_PARAMETER_MAP_VERSION),
                "parameter_status": self.params.get("status", "PROVISIONAL_UNCALIBRATED"),
                "krs_spec_version": self.race.get("krs_version", "v1.1-KRS"),
                "common_rule_version": self.race.get("common_rule_version", "v4.6"),
                "uncalibrated_notice": UNCALIBRATED_NOTICE,
            },
            "snapshot": {
                "prediction_id": self.race.get("prediction_id"),
                "simulation_snapshot_id": snapshot_id,
                "racecourse": self.race.get("racecourse"),
                "date": self.race.get("date"),
                "race_no": self.race.get("race_no"),
                "distance": self.race.get("distance"),
                "class": self.race.get("class"),
                "field_size": self.field_size,
                "course_rule_version": self.race.get("course_rule_version"),
                "master_seed": self.master_seed,
                "run_count": self.run_count,
                "SIM-DCR": self.sim_dcr,
                "role_zones": self.role_zones,
                "primary_leader_no": self.primary_leader_no,
                "finalization_status": self.race.get("finalization_status", "PROVISIONAL"),
            },
            "environment": self.env,
            "summary": horse_summary,
            "pace_distribution": base_agg["pace"],
            "leadership_interaction_share": base_agg.get("leadership_interaction_share", {}),
            "top_exacta_occurrence": base_agg["top_exacta_occurrence"],
            "top_trifecta_occurrence": base_agg["top_trifecta_occurrence"],
            "convergence_audit": convergence,
            "seed_stability_audit": seed_stability,
            "scenario_analysis": scenarios,
            "SIM-XDI": sim_xdi,
            "role_audit_triggers": role_triggers,
            "RGC_SIM_provenance_audit": provenance,
            "evidence_independence_audit": evidence_independence,
            "warnings": [
                UNCALIBRATED_NOTICE,
                "Default coefficients are provisional implementation values, not validated racing constants.",
                "Do not derive EV from SSR or combination occurrence frequencies without separate out-of-sample calibration.",
                "CONVERGED/STABLE means numerical stability for the supplied inputs and provisional map, not racing-model correctness.",
                "KRS v1.1 protects static roles from automatic deletion: Extreme SIM-XDI triggers input/scenario re-audit.",
            ],
        }


# -----------------------------
# Output helpers
# -----------------------------

def write_summary_csv(result: Mapping[str, Any], path: Path) -> None:
    fields = [
        "horse_no", "name", "SSR-W", "SSR-P2", "SSR-P3", "SSR-T3", "LSR",
        "Z4R-W", "Z4R-P2", "Z4R-P3", "Robustness", "1角_median", "3角_median", "4角_median", "ERS_median"
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in result["summary"]:
            w.writerow({
                "horse_no": row["horse_no"],
                "name": row["name"],
                "SSR-W": row["SSR-W"],
                "SSR-P2": row["SSR-P2"],
                "SSR-P3": row["SSR-P3"],
                "SSR-T3": row["SSR-T3"],
                "LSR": row["LSR"],
                "Z4R-W": row["Z4R-W"],
                "Z4R-P2": row["Z4R-P2"],
                "Z4R-P3": row["Z4R-P3"],
                "Robustness": row["Robustness"],
                "1角_median": row["positions"]["1角"]["median"],
                "3角_median": row["positions"]["3角"]["median"],
                "4角_median": row["positions"]["4角"]["median"],
                "ERS_median": row["positions"]["ERS"]["median"],
            })


def print_short(result: Mapping[str, Any]) -> None:
    snap = result["snapshot"]
    print("KRS-Engine v" + result["engine"]["engine_version"])
    print(f"snapshot={snap['simulation_snapshot_id']}  runs={snap['run_count']}  seed={snap['master_seed']}  SIM-DCR={snap['SIM-DCR']:.1f}")
    print("※ SSR/LSR/Z4R = 未較正シミュレーション出現率（勝率・EVではありません）")
    print()
    rows = sorted(result["summary"], key=lambda r: (-r["SSR-W"], r["horse_no"]))
    print(f"{'馬':>3} {'馬名':<18} {'SSR-W':>7} {'SSR-T3':>8} {'LSR':>7} {'Z4W':>7} {'Rob':>4}")
    for r in rows:
        print(f"{r['horse_no']:>3} {r['name'][:18]:<18} {r['SSR-W']*100:>6.1f}% {r['SSR-T3']*100:>7.1f}% {r['LSR']*100:>6.1f}% {r['Z4R-W']*100:>6.1f}% {r['Robustness']:>4}")
    print()
    print("Convergence:", result["convergence_audit"]["status"], " Seed stability:", result["seed_stability_audit"]["status"])
    if result["SIM-XDI"]:
        print("SIM-XDI:", ", ".join(str(x["horse_no"]) for x in result["SIM-XDI"]))
    if result["role_audit_triggers"]:
        print("Role re-audit:", ", ".join(f"{x['horse_no']}:{'/'.join(x['triggers'])}" for x in result["role_audit_triggers"]))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="KRS-Engine v1.1.0 - KeibaMetrics Race Simulation Engine")
    parser.add_argument("input", help="Input JSON file")
    parser.add_argument("--params", help="Parameter map JSON (optional)")
    parser.add_argument("--output", help="Output JSON path")
    parser.add_argument("--csv", help="Summary CSV path")
    parser.add_argument("--runs", type=int, help="Override simulation run count")
    parser.add_argument("--seed", type=int, help="Override master seed")
    parser.add_argument("--short", action="store_true", help="Print compact summary")
    args = parser.parse_args(argv)

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)
    if args.runs is not None:
        data.setdefault("simulation", {})["run_count"] = args.runs
    if args.seed is not None:
        data.setdefault("simulation", {})["master_seed"] = args.seed
    params = load_parameter_map(args.params)
    engine = KRSEngine(data, params)
    result = engine.run_all()

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=lambda x: x.__dict__), encoding="utf-8")
    if args.csv:
        out_csv = Path(args.csv)
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        write_summary_csv(result, out_csv)
    if args.short or not args.output:
        print_short(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

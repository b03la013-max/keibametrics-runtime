"""Unpromoted bloodline pooling; pure incumbent evaluators imported read-only.

The admitted-input reconstruction is an offline forensic projection of a prior
CI report. It does not replace OIDC verification, certify permanent identities,
backdate availability or produce Forward OOS. The published D bytes are read
only and remain the separate incumbent cohort.
"""
from __future__ import annotations

import argparse
import copy
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import random
import re
import sys
import unicodedata

PROFILE = "KM-JRA-BVI-HIERARCHICAL-RESIDUAL-v0.1-CANDIDATE-20261025"
PROTOCOL = {
    "profile": PROFILE,
    "classification": "POST_CAPTURE_RESEARCH / UNVALIDATED / NO_PRODUCTION_OR_PURCHASE_AUTHORITY",
    "split": ["2026-08-01", "2026-09-01", "2026-10-24"],
    "label": "1-(finish-1)/(field_size-1)",
    "identity": "NAME_SIRE_DAM_COMPOSITE; NOT_INDEPENDENT_OFFICIAL_ID",
    "controls": "EXISTING_FIXED_CONTROL_RIDGE; CLASS/FIELD/STRICTLY_EARLIER_INDIVIDUAL_FORM/ENVIRONMENT",
    "general_order": ["sire", "damsire", "sire_damsire_pair"],
    "environment_order": ["sire_surface", "damsire_surface", "sire_venue", "damsire_venue",
                          "sire_distance", "damsire_distance", "sire_going", "damsire_going"],
    "prior_effect": 0.0,
    "prior_effective_horses": {"GENERAL": 12.0, "PAIR": 24.0, "ENVIRONMENT": 24.0, "SEASON": 24.0},
    "pooling": "NORMAL_NORMAL_RESIDUAL_MEANS_WITH_FIXED_ZERO_PARENT_RESIDUAL_PRIOR",
    "weight": "1 / training_runs_per_exact_composite_horse",
    "distance_bucket_metres": 400,
    "uncertainty": "HORSE_CLUSTER_RESIDUAL_SANDWICH_PROXY; NOT_CALIBRATED_INTERVAL",
    "weather": "EXCLUDED", "meeting_progress": "MISSING_EXACT_MEETING_EVIDENCE; EXCLUDED",
    "opponent_strength": "UNAVAILABLE_EXACT_RACE_BOUND_OPPONENT_LABELS; NOT_CONTROLLED",
    "season": "CALENDAR_QUARTER_ABLATION_ONLY; NO_WEATHER_INFERENCE",
    "negative_control": "TRAIN_HORSE_PARENT_PAIR_PERMUTATION_FIXED_SEED_20261025",
    "hyperparameter_search": False,
    "publication": "RESEARCH_ONLY_NOT_FORWARD_PREREGISTRATION",
    "automatic_promotion": False,
}
VENUES = {"札幌", "函館", "福島", "新潟", "東京", "中山", "中京", "京都", "阪神", "小倉"}
GOINGS = {"良", "稍重", "重", "不良"}


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_fixed_module(repository):
    sys.path.insert(0, str(repository / "runtime"))
    spec = importlib.util.spec_from_file_location("incumbent_bvi_env_readonly", repository / "runtime/jra_bvi_env_shadow.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def is_explicit_jump(row):
    name = unicodedata.normalize("NFKC", str(row.get("race_name") or "")).upper()
    surface = str(row.get("surface_raw") or row.get("surface") or "")
    return bool("障" in surface or ("芝" in surface and "ダ" in surface)
                or re.search(r"障害|ジャンプ|ハイJ|グランドJ|スプリングJ|東京HJ|京都HJ|中山GJ|新潟JS|阪神JS|牛若丸JS|ペガサスJS|J[・.]?G(?:I{1,3}|[123])", name))


def reconstruct(repository, coverage_paths, output_dir):
    """Project only immutable files named in each prior real CI acceptance.

    This path is deliberately NOT a verifier injection into the Production
    Reader. Every result is labelled offline/post-capture/provisional.
    """
    sys.path.insert(0, str(repository / "runtime"))
    from jra_pedigree_corpus import _clean_runs, _horse_identity, _source_horses_from_verified_artifact
    # Positional labels avoid collisions when both files live in runtime_out.
    reports = {str(i): json.loads(Path(p).read_text()) for i, p in enumerate(coverage_paths)}
    files = {}
    for report in reports.values():
        for source in report["sources"].values():
            files.setdefault(source["file"], source["file_sha256"])
    parsed = {}
    for index, (relative, expected) in enumerate(sorted(files.items())):
        raw = (repository / relative).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError("FORENSIC_ORIGINAL_BYTES_MISMATCH:" + relative)
        blob = json.loads(raw)
        if "artifact" in blob:
            original = blob["artifact"]
            if original["source_snapshot_sha256"] != sha({k: v for k, v in original.items() if k != "source_snapshot_sha256"}):
                raise ValueError("FORENSIC_SOURCE_CONTENT_HASH_MISMATCH")
            entries = _source_horses_from_verified_artifact(original)
        else:
            unsigned = {k: v for k, v in blob.items() if k != "sha256"}
            digest = hashlib.sha256(json.dumps(unsigned, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
            if blob["sha256"] != digest:
                raise ValueError("FORENSIC_HARVEST_CONTENT_HASH_MISMATCH")
            entries = blob["horses"]
        # Retain compact exact original fields, never all multi-megabyte source.
        parsed[relative] = [{k: h.get(k) for k in ("horse_name", "sire", "dam", "damsire", "runs")} for h in entries]
        if index % 60 == 0:
            print("forensic files", index, "/", len(files), flush=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    summaries = []
    for label, report in reports.items():
        admitted = {}
        source_meta = defaultdict(list)
        for source in report["sources"].values():
            source_meta[source["file"]].append(source)
        base, seen, identities, conflicts = {}, defaultdict(list), {}, set()
        for relative, references in sorted(source_meta.items()):
            available = min(r["available_at_upper_bound"] for r in references)
            for horse in parsed[relative]:
                hid = _horse_identity(horse)
                if not hid:
                    continue
                identities[hid] = horse
                for run in _clean_runs(horse.get("runs") or [], date.fromisoformat(report["race_date"]), include_environment=True):
                    facts = {k: run[k] for k in ("date", "venue", "surface", "distance_m", "race_name", "finish", "field_size", "body_weight")}
                    key = hid, tuple(facts[k] for k in ("date", "venue", "surface", "distance_m", "race_name"))
                    if key in base and base[key] != facts:
                        conflicts.add(key)
                    base[key] = facts
                    seen[key].append({"going": run["going"], "surface_raw": run["surface_raw"], "available_at": available})
        rows = []
        for key, facts in base.items():
            if key in conflicts:
                continue
            hid = key[0]
            horse = identities[hid]
            obs = seen[key]
            goings = {x["going"] for x in obs if x["going"]}
            surfaces = {x["surface_raw"] for x in obs if x["surface_raw"] in ("芝", "ダ", "障", "ダート")}
            normalized_surfaces = {"ダ" if x == "ダート" else x for x in surfaces}
            surface = next(iter(normalized_surfaces)) if len(normalized_surfaces) == 1 else None
            going = next(iter(goings)) if len(goings) == 1 else None
            rows.append({**facts, "horse_id": hid, "horse_name": horse["horse_name"],
                         "sire": horse.get("sire"), "dam": horse.get("dam"), "damsire": horse.get("damsire"),
                         "surface": surface, "surface_raw": "/".join(sorted({x['surface_raw'] for x in obs if x['surface_raw']})),
                         "going": going, "available_at": max(x["available_at"] for x in obs),
                         "official_horse_id": None, "official_race_id": None,
                         "research_label_eligible": True})
        rows.sort(key=lambda r: (r["date"], r["horse_id"], r["venue"], r["distance_m"], r["race_name"]))
        if len(rows) != report["coverage"]["going"]["denominator"]:
            raise ValueError("FORENSIC_RECONSTRUCTION_DENOMINATOR_MISMATCH")
        dataset = {"classification": "FORENSIC_RECONSTRUCTION_FROM_PRIOR_CI_ADMITTED_INPUTS; NO_FRESH_OIDC; NOT_FORWARD_OOS",
                   "prediction_cutoff": report["prediction_cutoff"], "race_date": report["race_date"],
                   "manifest_sha256": report["manifest_sha256"], "prior_coverage_file_sha256": hashlib.sha256(Path(coverage_paths[int(label)]).read_bytes()).hexdigest(),
                   "rows": rows, "original_files_hash_verified": len(source_meta),
                   "independent_permanent_horse_ids": 0, "independent_official_race_labels": 0,
                   "model_training_eligibility": False, "production_effect": "NONE", "forward_oos_increment": 0}
        dataset["dataset_sha256"] = sha(dataset)
        path = output_dir / ("dataset_" + label + ".json")
        path.write_text(json.dumps(dataset, ensure_ascii=False, separators=(",", ":")) + "\n")
        summaries.append({"path": str(path), "rows": len(rows), "dataset_sha256": dataset["dataset_sha256"],
                          "coverage_manifest": report["manifest_sha256"], "prior_coverage": str(coverage_paths[int(label)])})
    return summaries


def term(row, factor):
    surface = row.get("surface")
    if factor == "season":
        return ((int(row["date"][5:7]) - 1) // 3 + 1, surface)
    if factor == "sire_damsire_pair":
        return (row.get("sire"), row.get("damsire")) if row.get("sire") and row.get("damsire") else None
    parent, _, environment = factor.partition("_")
    who = row.get(parent)
    if not who:
        return None
    if not environment:
        return (who,)
    val = row.get("distance_m") // 400 * 400 if environment == "distance" else row.get(environment)
    if val is None or val == "":
        return None
    return who, surface, val


def fit(rows, fixed, *, include_pedigree=True, include_environment=True, include_season=False):
    per_horse = Counter(r["horse_id"] for r in rows)
    weights = [1 / per_horse[r["horse_id"]] for r in rows]
    target = [r["target"] for r in rows]
    control, predicted = fixed._fit_stage(rows, weights, target, "CONTROL")
    if control.get("converged") is not True:
        raise ValueError("CANDIDATE_CONTROL_NOT_CONVERGED")
    residual = [y - p for y, p in zip(target, predicted)]
    factors = ((PROTOCOL["general_order"] if include_pedigree else [])
               + (PROTOCOL["environment_order"] if include_pedigree and include_environment else [])
               + (["season"] if include_season else []))
    stages = []
    for factor in factors:
        groups = defaultdict(list)
        for i, row in enumerate(rows):
            key = term(row, factor)
            if key is not None:
                groups[key].append(i)
        pooled = {}
        for key, members in groups.items():
            penalty = PROTOCOL["prior_effective_horses"]["PAIR" if factor == "sire_damsire_pair" else "SEASON" if factor == "season" else "ENVIRONMENT" if "_" in factor else "GENERAL"]
            wsum = math.fsum(weights[i] for i in members)
            effect = math.fsum(weights[i] * residual[i] for i in members) / (wsum + penalty)
            offspring = {rows[i]["horse_id"] for i in members}
            # Cluster aggregation prevents treating repeated runs as independent offspring.
            cluster_residual = defaultdict(float)
            for i in members:
                cluster_residual[rows[i]["horse_id"]] += weights[i] * (residual[i] - effect)
            n = len(offspring)
            variance = math.fsum(v*v for v in cluster_residual.values()) / (wsum + penalty)**2
            se = math.sqrt(variance * n / (n - 1)) if n > 1 else None
            pooled[key] = {"effect": effect, "runs": len(members), "composite_offspring": n,
                           "effective_horse_weight": wsum, "shrinkage": wsum / (wsum + penalty),
                           "standard_error_proxy": se, "permanent_independent_offspring": None}
        for i, row in enumerate(rows):
            residual[i] -= pooled.get(term(row, factor), {}).get("effect", 0)
        stages.append({"factor": factor, "terms": pooled})
    return {"control": control, "stages": stages, "training_runs": len(rows),
            "training_composite_horses": len(per_horse), "training_horse_weight": math.fsum(weights),
            "training_residual_mse": math.fsum(w*r*r for w, r in zip(weights, residual)) / math.fsum(weights)}


def predict(model, row, fixed):
    features = fixed._features(row, "CONTROL")
    score = math.fsum(t["coefficient"] * features.get(t["term"], 0) for t in model["control"]["terms"])
    components = []
    for stage in model["stages"]:
        found = stage["terms"].get(term(row, stage["factor"]))
        if found:
            score += found["effect"]
            components.append({"factor": stage["factor"], **found})
    return min(1., max(0., score)), components


def metrics(rows, predictions):
    errors = [(p - r["target"]) for p, r in zip(predictions, rows)]
    return {"n": len(rows), "composite_horses": len({r["horse_id"] for r in rows}),
            "mse": math.fsum(e*e for e in errors) / len(errors) if errors else None,
            "mae": math.fsum(abs(e) for e in errors) / len(errors) if errors else None}


def cluster_interval(rows, candidate, baseline, cluster):
    by = defaultdict(list)
    for r, c, b in zip(rows, candidate, baseline):
        by[str(r.get(cluster))].append((c-r["target"])**2 - (b-r["target"])**2)
    groups = list(by.values())
    if len(groups) < 2:
        return {"kind": "UNAVAILABLE_TOO_FEW_CLUSTERS", "n_clusters": len(groups)}
    rng = random.Random(20261025)
    values = []
    for _ in range(300):
        sample = [groups[rng.randrange(len(groups))] for _ in groups]
        values.append(math.fsum(math.fsum(g) for g in sample)/sum(map(len, sample)))
    values.sort()
    return {"kind": "CLUSTER_BOOTSTRAP_SENSITIVITY_NOT_POPULATION_CI", "cluster": cluster,
            "n_clusters": len(groups), "resamples": 300, "seed": 20261025,
            "lower_2_5pct": values[7], "upper_97_5pct": values[292], "calibrated": False}


def serialize_model(model):
    return {**{k:v for k,v in model.items() if k != "stages"},
            "stages": [{"factor": s["factor"], "terms": [{"key": list(k), **v} for k,v in sorted(s["terms"].items(),key=lambda x:str(x[0]))]} for s in model["stages"]]}


def evaluate(dataset, repository, output_dir):
    fixed = load_fixed_module(repository)
    rows, exclusions = fixed._eligible_rows(dataset)
    jumps = [r for r in rows if is_explicit_jump(r)]
    # Recompute strictly-earlier form AFTER domain exclusion. Merely removing
    # labels after the old helper would leave obstacle form in flat controls.
    flat_dataset = {**dataset, "rows": [r for r in dataset["rows"] if not is_explicit_jump(r)]}
    flat, flat_exclusions = fixed._eligible_rows(flat_dataset)
    train_boundary, val_boundary, test_boundary = PROTOCOL["split"]
    training = [r for r in flat if r["date"] < train_boundary]
    if not training:
        raise ValueError("NO_TRAINING_LABELS")
    # Priors and all penalties are fixed before examining validation/test labels.
    models = {
        "CONTROL_ONLY": fit(training, fixed, include_pedigree=False, include_environment=False),
        "GENERAL_ONLY": fit(training, fixed, include_environment=False),
        "HIERARCHICAL_ENV": fit(training, fixed),
        "HIERARCHICAL_ENV_SEASON": fit(training, fixed, include_season=True),
    }
    horse_pairs = {}
    for r in training:
        horse_pairs[r["horse_id"]] = (r.get("sire"), r.get("damsire"))
    rng = random.Random(20261025)
    ids = sorted(horse_pairs)
    pairs = [horse_pairs[h] for h in ids]
    rng.shuffle(pairs)
    permuted = dict(zip(ids, pairs))
    def randomized(row):
        r = copy.deepcopy(row)
        if row["horse_id"] in permuted:
            r["sire"], r["damsire"] = permuted[row["horse_id"]]
        else:
            # Unknown horses get a deterministic training-only parent profile.
            index = int(hashlib.sha256(row["horse_id"].encode()).hexdigest()[:12],16) % len(pairs)
            r["sire"], r["damsire"] = pairs[index]
        return r
    models["PERMUTED_PEDIGREE_NEGATIVE_CONTROL"] = fit([randomized(r) for r in training], fixed)
    train_horses = set(horse_pairs)
    train_sires = {r.get("sire") for r in training}
    sire_offspring = defaultdict(set)
    for r in training:
        sire_offspring[r.get("sire")].add(r["horse_id"])
    report = {"profile": PROFILE, "protocol": PROTOCOL, "protocol_sha256": sha(PROTOCOL),
              "classification": "POST_CAPTURE_CHRONOLOGICAL_DIAGNOSTIC; NOT_FORWARD_OOS",
              "dataset_sha256": dataset["dataset_sha256"], "corpus_manifest_sha256": dataset["manifest_sha256"],
              "dataset_acquisition_cutoff": dataset["prediction_cutoff"],
              "reconstructed_input_rows": len(dataset["rows"]), "old_surface_only_eligible": len(rows),
              "explicit_jump_excluded": len(jumps), "jump_composite_horses": len({r['horse_id'] for r in jumps}),
              "research_flat_proxy_rows": len(flat), "domain_rule": "EXPLICIT_JUMP_TEXT_OR_MIXED_SURFACE_EXCLUDED; NO_PERMANENT_RACE_QUALIFICATION",
              "training_rows": len(training), "training_composite_horses": len(train_horses),
              "eligible_permanent_horse_ids": 0, "independent_race_labels": 0,
              "production_training_eligibility": False, "partitions": {}, "input_exclusions": exclusions,
              "flat_input_exclusions": flat_exclusions,
              "opponent_strength_controlled": False, "forward_oos_increment": 0,
              "fixed_incumbent_modified": False, "production_effect": "NONE", "purchase_authority": False}
    for name, lower, upper in (("VALIDATION", train_boundary, val_boundary),("TEST", val_boundary, test_boundary)):
        chosen = [r for r in flat if lower <= r["date"] < upper]
        predictions = {arm: [predict(model, randomized(r) if arm.startswith("PERMUTED") else r, fixed)[0] for r in chosen] for arm, model in models.items()}
        partition = {"arms": {arm: metrics(chosen, p) for arm, p in predictions.items()},
                     "dependence": {"horse_overlap_with_train": len({r['horse_id'] for r in chosen}&train_horses),
                                    "sire_overlap_with_train": len({r.get('sire') for r in chosen}&train_sires),
                                    "unseen_horse_rows": sum(r['horse_id'] not in train_horses for r in chosen),
                                    "unseen_sire_rows": sum(r.get('sire') not in train_sires for r in chosen)},
                     "sensitivity": {group: cluster_interval(chosen,predictions["HIERARCHICAL_ENV"],predictions["GENERAL_ONLY"],group) for group in ("horse_id","sire")},
                     "groups": {}}
        group_indices = defaultdict(list)
        for i, r in enumerate(chosen):
            categories = {"venue":r.get("venue"),"surface":r.get("surface"),"going":r.get("going"),
                          "distance":r["distance_m"]//400*400,"career": "FIRST_OBSERVED_PROXY" if r["prior_ability_runs"]==0 else "LOW_OBSERVED_PROXY" if r["prior_ability_runs"]<=3 else "ESTABLISHED_OBSERVED_PROXY",
                          "sire_support": "LT4" if len(sire_offspring[r.get("sire")])<4 else "4_TO_19" if len(sire_offspring[r.get("sire")])<20 else "GE20",
                          "horse_seen":str(r['horse_id'] in train_horses),"sire_seen":str(r.get('sire') in train_sires)}
            for dim, value in categories.items():
                group_indices[(dim,str(value))].append(i)
        for (dim, value), indices in group_indices.items():
            rs = [chosen[i] for i in indices]
            partition["groups"].setdefault(dim,{})[value] = {arm: metrics(rs,[p[i] for i in indices]) for arm,p in predictions.items()}
        report["partitions"][name] = partition
    test = report["partitions"]["TEST"]["arms"]
    report["decision"] = "REJECT_HISTORICAL_INCREMENT" if test["HIERARCHICAL_ENV"]["mse"] >= test["GENERAL_ONLY"]["mse"] else "HOLD_UNVALIDATED_PENDING_FUTURE; HISTORICAL_ERROR_REDUCTION_ONLY"
    report["predictive_improvement_demonstrated"] = False
    output_dir.mkdir(parents=True,exist_ok=True)
    (output_dir/'candidate_evaluation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    model_record = {"profile":PROFILE,"protocol":PROTOCOL,"dataset_sha256":dataset["dataset_sha256"],
                    "classification":"POST_CAPTURE_RESEARCH_FIT; NOT_FORWARD_PUBLICATION",
                    "generated_at":datetime.now(timezone.utc).isoformat(),
                    "model_code_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    "negative_control_assignment_sha256":sha(permuted),
                    "models":{k:serialize_model(v) for k,v in models.items()},"production_authority":False,"purchase_authority":False}
    model_record['sha256']=sha(model_record)
    (output_dir/'candidate_models.json').write_text(json.dumps(model_record,ensure_ascii=False,indent=2)+'\n')
    return report


def role_audit_proposal(existing_roles, candidates):
    """One-sided, bounded P3 review proposal; never W promotion or exclusion.

    Inputs contain no outcomes. No ticket/Capital authority is produced.
    """
    out=copy.deepcopy(existing_roles)
    existing=set().union(*(set(v) for v in existing_roles.values()))
    supported=[c for c in candidates if c['runner_id'] not in existing and
               c.get('minimum_general_offspring',0)>=4 and c.get('minimum_environment_offspring',0)>=4 and
               type(c.get('environment_lower_proxy')) in (float,int) and math.isfinite(c['environment_lower_proxy']) and
               type(c.get('environment_effect')) in (float,int) and math.isfinite(c['environment_effect']) and
               c['environment_lower_proxy']>0 and c['environment_effect']>0]
    supported.sort(key=lambda c:(-c['environment_lower_proxy'],str(c['runner_id'])))
    selected=supported[:1]
    if selected:
        out.setdefault('P3',[]).append(selected[0]['runner_id'])
    return {'profile':PROFILE+'-ROLE-AUDIT','roles':out,'p3_rescue':[c['runner_id'] for c in selected],
            'candidate_width_increment':len(selected),'W_changed':False,'P2_changed':False,
            'exclusions':[],'ticket_cost':'NOT_MEASURED_NO_TICKET_AUTHORITY','production_authority':False,
            'purchase_authority':False,'rule':'MIN4_COMPOSITE_GENERAL_AND_ENVIRONMENT; LOWER_PROXY_GT0; MAX1_P3; NO_OUTCOME_INPUT'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,required=True);p.add_argument('--coverage',type=Path,action='append');p.add_argument('--output',type=Path,required=True);p.add_argument('--dataset',type=Path)
    a=p.parse_args()
    if a.coverage:
        print(json.dumps(reconstruct(a.repository,a.coverage,a.output),ensure_ascii=False),flush=True)
    if a.dataset:
        report=evaluate(json.loads(a.dataset.read_text()),a.repository,a.output)
        print(json.dumps({k:report[k] for k in ['training_rows','explicit_jump_excluded','jump_composite_horses','decision']},ensure_ascii=False))
        print(json.dumps({k:v['arms'] for k,v in report['partitions'].items()},ensure_ascii=False))


if __name__ == '__main__':
    main()

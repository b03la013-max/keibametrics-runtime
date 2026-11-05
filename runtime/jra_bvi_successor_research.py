"""Offline successor diagnostics from byte-bound Collector admissions.

This is a separate exploratory series, never fixed D or Production. Reuses
the frozen estimator without changing its policy, and never treats inherited
CI admission as fresh OIDC verification or historical capture as pre-race data.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, timedelta, timezone
import hashlib
import gzip
import json
from pathlib import Path
import random
import re
import unicodedata

from jra_bvi_env_shadow import (PROTOCOL_SHA256, VENUES, _eligible_rows, _predict_row,
                                _time, sha, train_model, verify_model)
from jra_pedigree_corpus import _clean_runs, _horse_identity

PROFILE = "KM-JRA-BVI-SUCCESSOR-EXPLORATORY-v1-20261101"
PROTOCOL = {
    "profile": PROFILE, "estimator_protocol_sha256": PROTOCOL_SHA256,
    "folds": [["2026-08-01", "2026-09-01", "2026-10-01"],
              ["2026-09-01", "2026-10-01", "2026-11-01"]],
    "primary": "TEST_NORMALIZED_FINISH_ENV_MINUS_GENERAL_MSE",
    "validation": "NO_TUNING; ALL_REGISTERED_FOLDS_RETAINED; OVERLAP_NOT_POOLED",
    "screen": "JRA10_SINGLE_SURFACE_NO_EXPLICIT_JUMP_MARKERS; NOT_CERTIFIED_FLAT",
    "uncertainty": "SEPARATE_HORSE_SIRE_AND_DATE_CLUSTER_BOOTSTRAPS; NOT_MULTIWAY_OR_CAUSAL",
    "bootstrap_replicates": 1000, "bootstrap_seed": 20261101,
    "gate": "REJECT_IF_ANY_TEST_MSE_WORSE; OTHERWISE_HOLD_QUALITY_AND_INDEPENDENT_REPLICATION",
    "causal_claim": False, "automatic_forward_admission": False,
    "production_authority": False,
}
PROTOCOL_SHA = sha(PROTOCOL)
JUMP = re.compile(r"障|ジャンプ|ハイJ|グランドJ|スプリングJ|東京HJ|京都HJ|中山GJ|新潟JS|阪神JS|牛若丸JS|ペガサスJS|J[・.]?G(?:I{1,3}|[123])")


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    path = Path(path)
    raw = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
    return json.loads(raw)


def seal(value):
    return {**value, "sha256": sha(value)}


def immutable(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if read(path) != value:
            raise ValueError("SUCCESSOR_IMMUTABLE_CONFLICT:" + str(path))
        return
    raw = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    if path.suffix == '.gz':
        raw = gzip.compress(raw,mtime=0)
    with path.open("xb") as f:
        f.write(raw)


def screen(row):
    surfaces = row.get("raw_surfaces") or [row.get("surface")]
    if any(s not in {"芝", "ダ", "ダート", "TURF", "DIRT"} for s in surfaces):
        return "NON_SINGLE_FLAT_SURFACE"
    if JUMP.search(unicodedata.normalize("NFKC", row.get("race_name") or "").upper()):
        return "EXPLICIT_NAMED_JUMP"
    if row.get("venue") not in VENUES:
        return "NON_JRA_VENUE"
    return None


def load_summary(path, observed_at):
    d = read(path)
    if d.get("sha256") != sha({k: v for k, v in d.items() if k != "sha256"}):
        raise ValueError("SUCCESSOR_SUMMARY_HASH_INVALID")
    if _time(d["created_at"]) > _time(observed_at):
        raise ValueError("SUCCESSOR_FUTURE_SUMMARY")
    if not isinstance(d.get("verified_harvest_artifacts"), list):
        raise ValueError("SUCCESSOR_ADMISSION_LIST_MISSING")
    return d


def dataset_from_summary(root, path, observed_at):
    """Exact dedicated-Harvest scope only; no all-Reader count substitution."""
    root = Path(root); d = load_summary(path, observed_at)
    target = date.fromisoformat(d["target_race_date"])
    if target > _time(observed_at).astimezone(timezone.utc).date() + timedelta(days=1):
        raise ValueError("SUCCESSOR_TARGET_BOUNDARY_TOO_FAR_IN_FUTURE")
    unique = {}; conflicts = set(); files = []; profiles = 0; clean_count = 0
    identities = set(); parent_sets = defaultdict(set); names = defaultdict(set)
    for item in d["verified_harvest_artifacts"]:
        name = item["file"]
        if not isinstance(name, str) or Path(name).name != name:
            raise ValueError("SUCCESSOR_INVALID_CORPUS_PATH")
        p = root / "runtime/pedigree_corpus" / name
        if p.is_symlink() or file_sha(p) != item["file_sha256"]:
            raise ValueError("SUCCESSOR_CORPUS_RAW_HASH_INVALID:" + name)
        obj = read(p)
        content_sha = hashlib.sha256(json.dumps({k: v for k, v in obj.items() if k != "sha256"},
                                    ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        if (content_sha != item["sha256"] or obj.get("sha256") != content_sha
                or obj.get("official") is not True or obj.get("source") != "www.jra.go.jp"):
            raise ValueError("SUCCESSOR_CORPUS_CONTENT_BINDING_INVALID")
        captured = _time(obj["harvested_at"]); verified = _time(item["oidc_verified_by"])
        if not captured <= verified <= _time(d["created_at"]) <= _time(observed_at):
            raise ValueError("SUCCESSOR_CORPUS_TIME_INVALID")
        files.append({"file": name, "file_sha256": item["file_sha256"], "content_sha256": content_sha,
                      "captured_at":captured.isoformat(), "inherited_verified_by":verified.isoformat()})
        for horse in obj["horses"]:
            hid = _horse_identity(horse); identities.add(hid); profiles += 1
            parent_sets[hid].add((horse.get("sire"), horse.get("dam"), horse.get("damsire")))
            names[horse.get("horse_name")].add((horse.get("sire"), horse.get("dam")))
            for r in _clean_runs(horse.get("runs") or [], target, include_environment=True):
                clean_count += 1
                key = (hid, r["date"], r["venue"], r["surface"], r["distance_m"], r["race_name"])
                if hid is None:
                    raise ValueError("SUCCESSOR_REQUIRED_COMPOSITE_ID_MISSING")
                row = {**r, "horse_id": hid, "sire": horse.get("sire"), "dam": horse.get("dam"),
                       "damsire": horse.get("damsire"), "available_at": verified.isoformat(),
                       "provenance": [], "raw_surfaces": [], "going_observations": []}
                if key in unique and any(unique[key].get(k) != row.get(k) for k in
                                         ("finish", "field_size", "sire", "dam", "damsire")):
                    conflicts.add(key)
                old = unique.setdefault(key, row)
                old["available_at"] = max(old["available_at"], row["available_at"], key=_time)
                old["provenance"].append(name)
                old["raw_surfaces"].append(r["surface_raw"])
                old["going_observations"].append(r["going"])
    for key in conflicts:
        unique.pop(key, None)
    if len(identities) != d["unique_composite_horses"] or len(unique) != d["unique_dedicated_prior_runs"]:
        raise ValueError("SUCCESSOR_DEDICATED_DENOMINATOR_MISMATCH")
    exclusions = Counter(); rows = []
    for _, row in sorted(unique.items(), key=lambda x: str(x[0])):
        if len(parent_sets[row["horse_id"]]) != 1:
            exclusions["PEDIGREE_IDENTITY_CONFLICT"] += 1; continue
        reason = screen(row)
        if reason:
            exclusions[reason] += 1; continue
        for k in ("provenance", "raw_surfaces"):
            row[k] = sorted(set(row[k]))
        gs = {g for g in row.pop("going_observations") if g is not None}
        row["going"] = next(iter(gs)) if len(gs) == 1 else None
        row["research_label_eligible"] = True
        rows.append(row)
    out = {"profile": PROFILE + "-DATASET", "prediction_cutoff": observed_at,
           "race_date": target.isoformat(), "rows": rows, "source_files": files,
           "manifest_sha256": sha(files), "summary_raw_sha256": file_sha(path),
           "summary_sha256": d["sha256"], "qualification": "INHERITED_CI_ADMISSION_RAW_HASH_RECHECK; NO_FRESH_OIDC",
           "counts": {"admitted_files": len(files), "profile_observations": profiles,
               "composite_identities": len(identities), "unique_prior_runs": len(unique),
               "clean_observations": clean_count, "duplicate_observations": clean_count-len(unique)-len(conflicts),
               "conflicting_run_keys": len(conflicts), "screened_rows": len(rows),
               "screened_composite_horses": len({r['horse_id'] for r in rows}),
               "same_name_multiple_parent_triples": sum(len(v)>1 for v in names.values()),
               "permanent_official_horse_ids": 0, "independent_official_labels": 0},
           "exclusions": dict(exclusions), "certified_flat": False,
           "scientific_training_qualified": False, "forward_oos_increment": 0,
           "production_effect": "NONE"}
    out["dataset_sha256"] = sha(out)
    return out


def cluster_interval(rows, deltas, field):
    """Paired loss resampling by one dependency axis at a time, not IID runs."""
    groups = defaultdict(list)
    for row, delta in zip(rows, deltas):
        value = row.get(field)
        if value is None or value == "":
            return {"clusters": None, "interval": None, "status": "MISSING_CLUSTER_ID"}
        groups[value].append(delta)
    values = [(sum(v), len(v)) for _, v in sorted(groups.items())]
    if len(values) < 2:
        return {"clusters": len(values), "interval": None, "status": "INSUFFICIENT_CLUSTERS"}
    rng = random.Random(PROTOCOL["bootstrap_seed"]); samples = []
    for _ in range(PROTOCOL["bootstrap_replicates"]):
        picked = [values[rng.randrange(len(values))] for _ in values]
        samples.append(sum(x[0] for x in picked) / sum(x[1] for x in picked))
    samples.sort()
    return {"clusters": len(values), "interval": [samples[24], samples[974]],
            "status": "EXPLORATORY_PERCENTILE_95; NOT_MULTIWAY_OR_MULTIPLICITY_CORRECTED"}


def evaluate_fold(dataset, boundaries, *, model=None):
    low, middle, high = boundaries
    if not low < middle < high <= dataset["race_date"]:
        raise ValueError("SUCCESSOR_SPLIT_INVALID")
    model = train_model(dataset, train_before=low) if model is None else model
    verify_model(model)
    if model['dataset_sha256'] != dataset['dataset_sha256'] or model['train_before'] != low:
        raise ValueError('SUCCESSOR_FOLD_MODEL_DATA_BINDING_INVALID')
    rows, exclusions = _eligible_rows(dataset)
    report = {"boundaries": boundaries, "model_sha256": model["model_sha256"],
              "training_rows_sha256": model["training_rows_sha256"],
              "training_runs": model["training_runs"], "training_composite_horses": model["training_composite_offspring"],
              "solver_converged": model["solver_converged"], "partitions": {}, "exclusions": exclusions}
    for name, start, end in (("VALIDATION",low,middle),("TEST",middle,high)):
        chosen = [r for r in rows if start <= r["date"] < end]
        errors = defaultdict(list); deltas = []
        for row in chosen:
            full, general, control, _ = _predict_row(model, row)
            for arm, value in (("GENERAL",general),("ENV",full),("CONTROL",control)):
                errors[arm].append(value/100-row["target"])
            deltas.append(errors["ENV"][-1]**2 - errors["GENERAL"][-1]**2)
        metrics = {arm: {"n":len(chosen), "mse":sum(e*e for e in es)/len(es),
                        "mae":sum(abs(e) for e in es)/len(es)} for arm,es in errors.items()}
        report["partitions"][name] = {"n":len(chosen), "composite_horses":len({r['horse_id'] for r in chosen}),
            "row_population_sha256":sha([sha(r) for r in chosen]), "metrics":metrics,
            "mse_delta":sum(deltas)/len(deltas) if deltas else None,
            "cluster_intervals":{f:cluster_interval(chosen,deltas,f) for f in ("horse_id","sire","date")},
            "train_test_horse_overlap":len({r['horse_id'] for r in chosen} &
                                            {r['horse_id'] for r in rows if r['date'] < low}),
            "inference":"DESCRIPTIVE_POST_CAPTURE_ONLY; NO_CAUSAL_OR_FORWARD_CLAIM"}
    return report


def evaluation_record(dataset, models):
    reports = [evaluate_fold(dataset,b,model=m) for b,m in zip(PROTOCOL['folds'],models)]
    if len(models)!=len(PROTOCOL['folds']):
        raise ValueError('SUCCESSOR_FOLD_MODEL_COUNT_INVALID')
    usable = all(r['solver_converged'] and r['partitions']['TEST']['n'] and
                 r['partitions']['VALIDATION']['n'] for r in reports)
    worse = any((r['partitions']['TEST']['mse_delta'] or 0)>0 for r in reports)
    decision = 'REJECTED_HISTORICAL_INCREMENT' if worse else 'INCONCLUSIVE_DATA_QUALITY_AND_REPLICATION'
    return seal({'profile':PROFILE,'protocol':PROTOCOL,'protocol_sha256':PROTOCOL_SHA,
        'folds':reports,'folds_are_not_pooled':True,'decision':decision,
        'model_fit_eligible':bool(usable),'scientific_training_qualified':False,
        'forward_oos_increment':0,'prediction_utility_success':False,'capital_pfs':None})


def candidate_record(identity, dataset, model, evaluation, folder, created_at):
    names = ['dataset.json.gz','model.json','evaluation.json','fold_models.json']
    return seal({'profile':PROFILE,'identity':identity,'created_at':created_at,
        'candidate_id':'BVI-EXP-'+sha(identity)[:20],'lifecycle_state':'HISTORICAL_TESTED',
        'status':'PARTIAL' if evaluation['model_fit_eligible'] and model['solver_converged'] else 'BLOCKED',
        'decision':evaluation['decision'], 'dataset_sha256':dataset['dataset_sha256'],
        'model_sha256':model['model_sha256'],'counts':dataset['counts'],'exclusions':dataset['exclusions'],
        'artifact_hashes':{name:file_sha(folder/name) for name in names},
        'next_cohort_state':'WAITING_ELIGIBLE_CANDIDATE',
        'blockers':['PERMANENT_IDS_AND_INDEPENDENT_RACE_LABELS_UNQUALIFIED',
            'FLAT_CLASSIFICATION_NOT_OFFICIALLY_COMPLETE','OPPONENT_AND_SELECTION_BIAS_UNCONTROLLED',
            'INDEPENDENT_REVIEW_AND_PROSPECTIVE_PUBLICATION_REQUIRED'],
        'fixed_D_changed':False,'forward_oos_increment':0,'production_effect':'NONE',
        'production_authority':False,'purchase_authority':False})


def run(root, *, summary_path=None, output=None, observed_at):
    root = Path(root).resolve(); output = Path(output or root / "research/bvi_successor")
    if not output.is_absolute(): output = root / output
    output = output.resolve()
    if (root/"research").is_symlink() or not output.is_relative_to((root/"research").resolve()):
        raise ValueError("SUCCESSOR_OUTPUT_MUST_STAY_IN_RESEARCH")
    if summary_path is None:
        choices = []
        for path in sorted((root/"runtime/pedigree_intake_receipts").glob("day-audit-*.json")):
            try:
                d = load_summary(path, observed_at)
            except (ValueError,KeyError,OSError,TypeError):
                continue
            choices.append((_time(d["created_at"]),path.name,path))
        if not choices:
            return {"status":"NOT_EXECUTED", "reason":"NO_VALID_INHERITED_COLLECTOR_SUMMARY", "forward_oos_increment":0}
        summary_path = max(choices)[2]
    dataset = dataset_from_summary(root, summary_path, observed_at)
    # The capture cutoff advances; identical acquired files need no refit.
    identity = {"files":dataset["source_files"], "target_day":dataset["race_date"],
                "protocol_sha256":PROTOCOL_SHA, "adapter_code_sha256":file_sha(__file__),
                "estimator_code_sha256":file_sha(Path(__file__).with_name('jra_bvi_env_shadow.py')),
                "parser_code_sha256":file_sha(Path(__file__).with_name('jra_pedigree_corpus.py')),
                "class_rule_code_sha256":file_sha(Path(__file__).with_name('jra_owner_authorized_feature_rules.py'))}
    key = sha(identity); folder = output / key; record_path = folder / "record.json"
    checkpoint_path = folder/'input_checkpoint.json'
    if checkpoint_path.exists():
        checkpoint = read(checkpoint_path)
        original_at = checkpoint['observed_at']
        if (checkpoint != seal({'identity':identity,'observed_at':original_at,
                                'summary':checkpoint.get('summary')})
                or _time(original_at)>_time(observed_at)):
            raise ValueError('SUCCESSOR_CHECKPOINT_INVALID')
        # Preserve the exact original summary too: later CI summaries of the
        # same files do not rewrite this diagnostic's first acquisition clock.
        checkpoint_summary = folder/'input_summary.json'
        immutable(checkpoint_summary,checkpoint['summary'])
        dataset = dataset_from_summary(root,checkpoint_summary,original_at)
        if dataset['source_files'] != identity['files'] or dataset['race_date'] != identity['target_day']:
            raise ValueError('SUCCESSOR_CHECKPOINT_INPUTS_CHANGED')
    else:
        original_at = observed_at
        checkpoint = seal({'identity':identity,'observed_at':original_at,'summary':read(summary_path)})
        immutable(checkpoint_path,checkpoint)
        # Canonical JSON bytes are used from the first attempt, not only retry.
        immutable(folder/'input_summary.json',checkpoint['summary'])
        dataset = dataset_from_summary(root,folder/'input_summary.json',original_at)
    if record_path.exists():
        old = read(record_path)
        if old.get("sha256") != sha({k:v for k,v in old.items() if k!='sha256'}) or old.get('identity') != identity:
            raise ValueError("SUCCESSOR_SAVED_RECORD_INVALID")
        for name,digest in old["artifact_hashes"].items():
            if Path(name).name != name or file_sha(folder/name) != digest:
                raise ValueError("SUCCESSOR_SAVED_ARTIFACT_CHANGED")
        model=read(folder/'model.json');verify_model(model)
        if model['dataset_sha256']!=dataset['dataset_sha256'] or read(folder/'dataset.json.gz')!=dataset:
            raise ValueError('SUCCESSOR_SAVED_DATASET_CHANGED')
        evaluation=evaluation_record(dataset,read(folder/'fold_models.json'))
        if read(folder/'evaluation.json')!=evaluation:
            raise ValueError('SUCCESSOR_SAVED_EVALUATION_CHANGED')
        if old!=candidate_record(identity,dataset,model,evaluation,folder,original_at):
            raise ValueError('SUCCESSOR_SAVED_RECORD_CONTENT_CHANGED')
        record = old
    else:
        models=[train_model(dataset,train_before=b[0]) for b in PROTOCOL['folds']]
        evaluation=evaluation_record(dataset,models)
        model = train_model(dataset, train_before=dataset['race_date'])
        verify_model(model)
        payloads = {"dataset.json.gz":dataset, "model.json":model,
                    "fold_models.json":models, "evaluation.json":evaluation}
        for name,value in payloads.items(): immutable(folder/name,value)
        record = candidate_record(identity,dataset,model,evaluation,folder,original_at)
        immutable(record_path,record)
    output.mkdir(parents=True,exist_ok=True)
    current = seal({"record":str(record_path.relative_to(root)),"record_sha256":record['sha256'],
                    "last_checked_at":observed_at,"status":record['status'],"decision":record['decision'],
                    "forward_oos_increment":0,"production_effect":"NONE"})
    (output/"current.json").write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n')
    return {**current,"candidate_id":record['candidate_id'],"new_candidate_fit":"EXPLORATORY_ONLY",
            "counts":record['counts'],"exclusions":record['exclusions'],
            "next_cohort_state":record['next_cohort_state']}

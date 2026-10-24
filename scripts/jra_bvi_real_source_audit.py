"""Recompute existing BVI from signed real SOURCE, with DCR fills disabled."""
import os
os.environ["KM_JRA_DCR_ART3_POLICY"] = "0"
import argparse
import hashlib
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from jra_pedigree_corpus import _verified_source
from jra_source_to_evidence_features import compile_source_to_features, _official_runner_map
from jra_evidence_to_base_production import load_mapping, evaluate_partial_production_base_indices

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="20261011")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    mapping = load_mapping(ROOT / "mapping/jra_base_index_evidence_mapping_v1.0_20260921.json")
    races = []
    for path in sorted((ROOT / "runtime/executions").glob(f"*{args.date}*/SOURCE/runs/*/source_receipt_envelope.json")):
        if _verified_source(path) is None:
            raise RuntimeError(f"INVALID_SOURCE:{path}")
        art = json.loads(path.read_text())["artifact"]
        request = [{"runner_id": rid, "name": r.get("name") or r.get("horse_name")}
                   for rid, r in _official_runner_map(art).items()]
        compiled = compile_source_to_features(art, request, mapping)
        runners = [dict(r, **compiled["runners"][r["runner_id"]]["factual_runner_updates"],
                        evidence_features=compiled["runners"][r["runner_id"]]["generated_production_features"])
                   for r in request]
        result = evaluate_partial_production_base_indices(art["race_id"], runners, mapping)
        cells = {r["runner_id"]: dict(name=r["name"], **result["runners"][r["runner_id"]]["indices"]["BVI"])
                 for r in runners}
        races.append(dict(race_id=art["race_id"], source=str(path.relative_to(ROOT)),
                          source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                          source_freeze_at=art["source_freeze_at"], prediction_cutoff=art["prediction_cutoff"],
                          signature_verified=True, independent_oidc_verified=False,
                          corpus=compiled["pedigree_corpus_manifest"], bvi=cells))
    cells = [c for r in races for c in r["bvi"].values()]
    report = dict(mapping_id=mapping["mapping_id"], dcr_fill_enabled=False,
                  full20_authority=False, retrospective_recalculation=True,
                  source_count=len(races), runner_source_observations=len(cells),
                  calculated=sum(c["status"] == "CALCULATED" for c in cells),
                  blocked=sum(c["status"] != "CALCULATED" for c in cells), races=races)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n")
    latest = {}
    for race in races:
        if race["race_id"] not in latest or race["source_freeze_at"] > latest[race["race_id"]]["source_freeze_at"]:
            latest[race["race_id"]] = race
    rows = [dict(race_id=r["race_id"], horse_no=k, name=v["name"], status=v["status"],
                 BVI=v.get("value"), coverage=v.get("coverage_weight"), reason=v.get("reason", ""))
            for r in latest.values() for k,v in r["bvi"].items()]
    if rows:
        with args.output.with_suffix(".csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    print(json.dumps({k:v for k,v in report.items() if k != "races"}))

if __name__ == "__main__":
    main()

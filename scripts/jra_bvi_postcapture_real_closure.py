"""Measure genuine JRA BVI offspring coverage after verified targeted capture.

Historical Kyoto R09 is used only as a fixture. The actual collection happened
AFTER its prediction cutoff. The resulting scores NEVER replace a pre-race
FINAL, create settled OOS, or claim incremental prediction utility.
"""
from __future__ import annotations
from datetime import datetime
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))
sys.path.insert(0,str(ROOT/"runtime"/"jra_source_runtime"))

from jra_pedigree_corpus import _verified_harvest, build_corpus
from jra_owner_authorized_feature_rules import owner_authorized_observations
from jra_evidence_to_base_production import _weighted_index

FILE=ROOT/"runtime/pedigree_corpus/20261011-targeted-kyo-r09-rare-sires-r1.json"
SOURCE=ROOT/"runtime/executions/KM-JRA-KYO-20261011-R09-LIVE-R2/SOURCE/runs/38112804616/source_receipt_envelope.json"
EARLY="2026-10-11T14:10:00+09:00"
AFTER="2026-10-11T15:30:00+09:00"
TARGETS=("7","13","16")


def evaluate():
    later = datetime.fromisoformat(AFTER)
    early = datetime.fromisoformat(EARLY)
    verified = _verified_harvest(FILE,not_after=later)
    if verified is None:
        raise RuntimeError("BVI_TARGETED_OFFICIAL_OIDC_OR_DIGEST_UNVERIFIED")
    if _verified_harvest(FILE,not_after=early) is not None:
        raise RuntimeError("BVI_TARGETED_HARVEST_RETROACTIVELY_VALID_FOR_R09")
    original=json.loads(SOURCE.read_text(encoding="utf-8"))["artifact"]
    rows={str(x.get("runner_id") or x.get("horse_no")):x
          for x in original["jra_official_race_card_detail"]["runners"]}
    parents={rid:(rows[rid]["sire"],rows[rid]["damsire"]) for rid in TARGETS}
    corpus=build_corpus(ROOT,prediction_cutoff=AFTER,race_date="2026-10-11",
                        exclude_race_id=original["race_id"],
                        required_sires={p[0] for p in parents.values()},
                        required_damsires={p[1] for p in parents.values()})
    if "ATTESTED_HARVEST:"+verified["sha256"] not in corpus["snapshots"]:
        raise RuntimeError("BVI_TARGETED_SIGNED_COHORT_NOT_CONSUMED")
    registry=json.loads((ROOT/"mapping/jra_evidence_feature_rule_registry_v1.3_20261010.json").read_text())
    mapping=json.loads((ROOT/"mapping/jra_base_index_evidence_mapping_v1.0_20260921.json").read_text())
    features=owner_authorized_observations(original,registry,corpus=corpus)
    results={}
    for rid in TARGETS:
        # Historical R09's signed index gate identified each as ESTABLISHED.
        # We audit that identical profile; this does not create a new forecast.
        numeric=_weighted_index("BVI","ESTABLISHED",features.get(rid,{ }),mapping)
        comps=numeric.get("components") or []
        covered=float(numeric.get("coverage_weight") or 0)
        required=float(mapping["profiles"]["ESTABLISHED"]["minimum_index_coverage_weight"])
        results[rid]={
            "horse_name":rows[rid]["horse_name"],
            "sire":parents[rid][0],"damsire":parents[rid][1],
            "observed_feature_count":len(comps),
            "coverage_weight":covered,"required_coverage_weight":required,
            "observed_bvi_complete":bool(comps and covered+1e-12>=required),
            "bvi_diagnostic_value":numeric["value"],
            "information_status":numeric.get("information_status") or "OBSERVED_RULE_COVERAGE",
            "observed_components":[{
                "feature":c["feature"],"rule_id":c["feature_rule_id"],
                "category":c["category"],"source_fact":c["source_fact"],
                "weight":c["weight"],"evidence_refs":c["evidence_refs"],
            } for c in comps],
        }
    report={
        "classification":"POST-START HISTORICAL DIAGNOSTIC / NOT PRODUCTION / NO OOS / NO BET",
        "race_id":original["race_id"],
        "original_prediction_cutoff":EARLY,
        "targeted_harvest_completed_after_original_cutoff":True,
        "postcapture_diagnostic_cutoff":AFTER,
        "cohort_sha256":verified["sha256"],
        "cohort_horse_count":verified["horse_count"],
        "oidc_attested":True,
        "corpus_manifest_sha256":corpus["manifest_sha256"],
        "verified_corpus_horses":corpus["horse_count"],
        "verified_corpus_runs":corpus["run_count"],
        "target_bvi":results,
        "historical_prediction_rewritten":False,
        "production_promotion":False,
        "oos_increment":0,
    }
    out=ROOT/"runtime_out/jra_bvi_postcapture_real_closure.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("JRA_BVI_POSTCAPTURE_CLOSURE="+json.dumps(report,ensure_ascii=False))
    return report


if __name__=="__main__":
    evaluate()

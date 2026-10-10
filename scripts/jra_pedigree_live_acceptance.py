"""Prove real signed JRA pedigree corpus is usable at a later cutoff, without replay leakage.

No purchased tickets or post-result learning are produced. This run verifies
GitHub OIDC signer and Sigstore witnessed timestamps on REAL observed files.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import json
import os
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from jra_pedigree_corpus import build_corpus, _verified_harvest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime/pedigree_corpus/20261004-results-race0-r3.json"
EARLY = "2026-10-10T18:00:00+09:00"
AFTER = "2026-10-10T23:59:59+09:00"
DATE = "2026-10-11"

def evaluate(root=ROOT, file=DATA):
    if not file.is_file():
        raise RuntimeError("JRA_REAL_SIGNED_HARVEST_MISSING")
    later = datetime.fromisoformat(AFTER)
    signed_files = sorted((ROOT/"runtime/pedigree_corpus").glob("20261004-results-race*-r3.json"))
    if len(signed_files) < 4:
        raise RuntimeError("JRA_FOUR_PUBLISHED_SIGNED_HISTORICAL_BATCHES_MISSING")
    verified = []
    for entry in signed_files:
        signed = _verified_harvest(entry, not_after=later)
        if signed is None:
            raise RuntimeError("JRA_REAL_HARVEST_OIDC_TIMESTAMP_OR_DIGEST_NOT_VERIFIED:"+entry.name)
        if signed["horse_count"] != len(signed["horses"]) or signed["horse_count"] < 30:
            raise RuntimeError("JRA_REAL_HARVEST_UNDERCOVERED:"+entry.name)
        if signed["horse_count"] / signed["horse_token_count"] < 0.9:
            raise RuntimeError("JRA_REAL_HARVEST_UNDERCOVERED:"+entry.name)
        verified.append(signed)
    if sum(j["horse_count"] for j in verified) < 181:
        raise RuntimeError("JRA_FOUR_BATCH_OFFICIAL_RUNNER_COVERAGE_MISSING")
    # A historical signed receipt can be in both; do not count as new harvest.
    early = build_corpus(root, prediction_cutoff=EARLY, race_date=DATE)
    current = build_corpus(root, prediction_cutoff=AFTER, race_date=DATE)
    for entry, signed in zip(signed_files, verified):
        sha = "ATTESTED_HARVEST:" + signed["sha256"]
        if sha in early.get("snapshots", []):
            raise RuntimeError("JRA_BACKFILL_USED_BEFORE_ACTUAL_SIGNED_CAPTURE_TIME")
        if sha not in current.get("snapshots", []):
            raise RuntimeError("JRA_BACKFILL_NOT_ACTUALLY_IN_PRODUCTION_BVI_CORPUS:"+entry.name)
    def summarize_sires(corpus):
        group = defaultdict(lambda: {"offspring": set(), "races": 0})
        for key, horse in corpus["horses"].items():
            sire = horse.get("sire")
            if not sire:
                continue
            group[sire]["offspring"].add(key)
            group[sire]["races"] += len(horse["runs"])
        # Sire sample sufficiency is necessary but NOT sufficient for all BVI
        # features: surface, distance, track and class also constrain them.
        return sum(len(g["offspring"]) >= 4 and g["races"] >= 12 for g in group.values())
    earlier_eligible=summarize_sires(early)
    eligible_raw=summarize_sires(current)
    report = {
        "classification": "POST-CAPTURE SOURCE CORPUS ACCEPTANCE / NOT OOS / NO BET",
        "verified_batch_count": len(verified),
        "verified_batch_files": [p.name for p in signed_files],
        "harvest_sha256_list": [j["sha256"] for j in verified],
        "harvested_at_list": [j["harvested_at"] for j in verified],
        "verified_by": "GITHUB_OIDC_AND_SIGSTORE_WITNESSED_TIMESTAMP",
        "fixture_horse_count": sum(j["horse_count"] for j in verified),
        "fixture_prior_runs": sum(len(x["runs"]) for j in verified for x in j["horses"]),
        "pre_capture_harvest_included": False,
        "post_capture_harvest_included": True,
        "pre_capture_corpus_horses": early["horse_count"],
        "pre_capture_corpus_runs": early["run_count"],
        "post_capture_corpus_horses": current["horse_count"],
        "post_capture_corpus_runs": current["run_count"],
        "post_capture_manifest_sha256": current["manifest_sha256"],
        "pre_capture_sire_groups_with_4_offspring_12_runs": earlier_eligible,
        "post_capture_sire_groups_with_4_offspring_12_runs": eligible_raw,
        "delta_corpus_horses": current["horse_count"]-early["horse_count"],
        "delta_corpus_runs": current["run_count"]-early["run_count"],
        "delta_sire_sample_sufficient_groups": eligible_raw-earlier_eligible,
        "production_full20_verified": False,
        "oos_increment": 0,
        "purchase_authority": False,
    }
    out=ROOT/"runtime_out/jra_pedigree_verified_acceptance.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("JRA_SIGNED_PEDIGREE_CORPUS_LIVE_ACCEPTANCE="+json.dumps(report,ensure_ascii=False))
    return report

if __name__=="__main__":
    evaluate()

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
    signed = _verified_harvest(file, not_after=later)
    if signed is None:
        raise RuntimeError("JRA_REAL_HARVEST_OIDC_TIMESTAMP_OR_DIGEST_NOT_VERIFIED")
    if signed["horse_count"] != len(signed["horses"]) or signed["horse_count"] < 30:
        raise RuntimeError("JRA_REAL_HARVEST_UNDERCOVERED")
    if signed["horse_count"] / signed["horse_token_count"] < 0.9:
        raise RuntimeError("JRA_REAL_HARVEST_UNDERCOVERED")
    # A historical signed receipt can be in both; do not count as new harvest.
    early = build_corpus(root, prediction_cutoff=EARLY, race_date=DATE)
    current = build_corpus(root, prediction_cutoff=AFTER, race_date=DATE)
    sha = "ATTESTED_HARVEST:" + signed["sha256"]
    if sha in early.get("snapshots", []):
        raise RuntimeError("JRA_BACKFILL_USED_BEFORE_ACTUAL_SIGNED_CAPTURE_TIME")
    if sha not in current.get("snapshots", []):
        raise RuntimeError("JRA_BACKFILL_NOT_ACTUALLY_IN_PRODUCTION_BVI_CORPUS")
    group = defaultdict(lambda: {"offspring": set(), "races": 0})
    for key, horse in current["horses"].items():
        sire = horse.get("sire")
        if not sire:
            continue
        group[sire]["offspring"].add(key)
        group[sire]["races"] += len(horse["runs"])
    # These are only sample-capability counts, not winning predictions.
    eligible_raw = sum(len(g["offspring"]) >= 4 and g["races"] >= 12 for g in group.values())
    report = {
        "classification": "POST-CAPTURE SOURCE CORPUS ACCEPTANCE / NOT OOS / NO BET",
        "harvest_sha256": signed["sha256"],
        "harvested_at": signed["harvested_at"],
        "verified_by": "GITHUB_OIDC_AND_SIGSTORE_WITNESSED_TIMESTAMP",
        "fixture_horse_count": signed["horse_count"],
        "fixture_prior_runs": sum(len(x["runs"]) for x in signed["horses"]),
        "pre_capture_harvest_included": False,
        "post_capture_harvest_included": True,
        "post_capture_corpus_horses": current["horse_count"],
        "post_capture_corpus_runs": current["run_count"],
        "post_capture_manifest_sha256": current["manifest_sha256"],
        "sire_groups_with_4_offspring_12_runs": eligible_raw,
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

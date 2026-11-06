"""Offline binding regression; no SOURCE mutation, signing, fetch or KRS run."""
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

import pytest

ROOT = Path(os.environ.get("KM_TEST_REPO_ROOT", Path(__file__).resolve().parents[1]))
sys.path[:0] = [str(ROOT / "runtime"), str(ROOT / "runtime/jra_source_runtime")]
from jra_source_runtime.jra_current_environment import bind_latest_environment
from jra_source_runtime.jra_observed_context import resolve_observed_context

MODULE = Path(os.environ.get("KM_ENV_OWNER_MODULE", ROOT / "runtime/jra_owner_authorized_feature_rules.py"))
spec = importlib.util.spec_from_file_location("owner_current_environment_under_test", MODULE)
owner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(owner)
REQUEST = Path(os.environ.get("KM_ENV_ORIGINAL_REQUEST", ROOT / "runtime/requests/KM-JRA-KYO-20261025-R11-LIVE-R1-FORMAL.json"))
REGISTRY = json.loads((ROOT / "mapping/jra_evidence_feature_rule_registry_v1.3_20261010.json").read_text())


def original():
    q = json.loads(REQUEST.read_text())
    source = deepcopy(q["source_snapshot"])
    # Match the compiler's already verified outer SOURCE digest binding.
    source["source_snapshot_sha256"] = q["source_snapshot_sha256"]
    return source, q["prediction_cutoff"]


def test_owner_going_uses_later_receipt_bound_official_card():
    raw_digest = hashlib.sha256(REQUEST.read_bytes()).hexdigest()
    source, cutoff = original()
    before = deepcopy(source)
    assert resolve_observed_context(source)["going"] == "稍重"
    fresh = bind_latest_environment(deepcopy(source), cutoff)
    current = resolve_observed_context(fresh)
    assert current["going"] == "良"
    assert current["context_source_snapshot_sha256"] == "61b1c72b05c3687d8f34ac599a005dcbdff9cb031233e85a02bb70ccbe819d0c"
    rows = owner.owner_authorized_observations(fresh, REGISTRY)
    fits = [r["going_fit"] for r in rows.values() if "going_fit" in r]
    assert fits
    assert all("today_going_from_receipt_bound_official_context=良;" in f["source_fact"] for f in fits)
    assert all("SOURCE-SNAPSHOT:" + current["context_source_snapshot_sha256"] in f["evidence_refs"] for f in fits)
    assert fresh["jra_official_race_card_detail"] == source["jra_official_race_card_detail"]
    assert source == before
    assert hashlib.sha256(REQUEST.read_bytes()).hexdigest() == raw_digest


def test_earlier_ground_samples_cannot_fill_current_ground_missing():
    source, cutoff = original()
    fresh = bind_latest_environment(deepcopy(source), cutoff)
    rid = "4"
    detail = next(r for r in fresh["jra_official_race_card_detail"]["runners"] if str(r["runner_id"]) == rid)
    history = fresh["jra_official_horse_history"]["runners"][rid]
    old_runs = [r for r in history["runs"] if r.get("going") == "稍重" and r.get("surface") == "芝"]
    assert len(old_runs) >= 2
    # Diagnostic fixture only: enough older-ground observations, none at 良.
    history["runs"] = deepcopy(old_runs[:2])
    detail["recent_runs"] = deepcopy(old_runs[:2])
    rows = owner.owner_authorized_observations(fresh, REGISTRY)
    assert "going_fit" not in rows[rid]


@pytest.mark.parametrize("case", ["raw", "active_identity", "post_cutoff"])
def test_owner_reuses_context_validation_and_does_not_fallback_on_bad_binding(case):
    source, cutoff = original()
    fresh = bind_latest_environment(deepcopy(source), cutoff)
    if case == "active_identity":
        fresh["jra_official_runner_universe"]["runners"][0]["canonical_name"] = "別馬"
    else:
        snap = next(s for s in fresh["sources"] if s.get("source_id") == "JRA-OFFICIAL-RACE-CARD-DETAIL-REOBSERVATION")
        if case == "raw":
            snap["raw_sha256"] = "0" * 64
        else:
            snap["cutoff_relation"] = "POST_CUTOFF"
    before = deepcopy(fresh)
    with pytest.raises(ValueError):
        owner.owner_authorized_observations(fresh, REGISTRY)
    assert fresh == before

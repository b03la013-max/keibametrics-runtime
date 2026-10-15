"""Historical R05 SOURCE used only as a parser/contract fixture, NOT OOS credit.

The actual Owner code is newly developed after that race; acceptance requires
a separate unknown-future signed live run. Any result columns are prohibited.
"""
from __future__ import annotations
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import pytest

from runtime.local_production_static_owner import build_formal_static, StaticOwnerError

ROOT = Path(__file__).resolve().parents[1]
EID = "KM-LOCAL-KAW-20261014-R05-LIVE-R1"
SOURCE = ROOT / f"runtime/executions/{EID}/SOURCE/runs/38528949555-source/source_receipt_envelope.json"
INTENT = ROOT / f"runtime/formal_intents/{EID}.json"
POLICY = ROOT / "profiles/local_production_static_owner_20261014_v1.json"


def replay_fixture():
    signed = json.loads(SOURCE.read_text(encoding="utf-8"))
    prior = json.loads(INTENT.read_text(encoding="utf-8"))
    pool = signed["artifact"]["official_runner_universe"]["runners"]
    request = {k: copy.deepcopy(prior[k]) for k in (
        "family_id", "race_id", "execution_id", "venue_id", "race_date", "race_no",
        "prediction_cutoff", "scheduled_post_at", "release_deadline_at",
        "current_authority_manifest", "temporal_mode",
    )}
    numerical = {
        "strict_full_numerical_ready": True,
        "production_numerical_authority": {"prediction_consumption_authorized": False},
        "required_indices": prior["required_indices"],
        "runners": [{"runner_id": r["runner_id"], "canonical_components": {
            "ZAI-WIN": {"value": 100 - int(r["runner_id"])*3}}} for r in pool],
    }
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    clock = datetime.fromisoformat("2026-10-14T16:34:00+09:00")
    return request, signed, numerical, policy, clock


def test_historical_official_card_parsed_only_for_contract():
    req, source, numeric, policy, now = replay_fixture()
    intent, ledger = build_formal_static(req, source, numeric, policy=policy, now=now)
    ids = [str(x["runner_id"]) for x in source["artifact"]["official_runner_universe"]["runners"]]
    assert set(intent["static_prediction"]["ranking"]) == set(ids)
    assert len(intent["static_prediction"]["ranking"]) == len(ids) == 12
    assert intent["race"]["distance"] == 900
    assert intent["race"]["surface"] == "dirt"
    assert intent["static_prediction_frozen"] is True
    assert intent["static_prediction"]["source_basis_receipt_sha256"] == source["receipt_sha256"]
    assert ledger["source_receipt_sha256"] == source["receipt_sha256"]
    assert ledger["empirical_oos_validated"] is False
    assert ledger["numerical_prediction_consumption"] is False
    assert ledger["odds_consumed"] is False and ledger["result_consumed"] is False
    assert len(intent["role_registry"]) == sum(len(x) for x in intent["static_prediction"]["roles"].values())
    assert all(p["head"] != p["second"] for p in intent["pair_dispositions"])
    assert all(len({q["head"],q["second"],q["third"]}) == 3 for q in intent["third_dispositions"])
    assert intent["capital_policy"]["mode"] == "RECOMMENDATION_ONLY"
    assert not any("AKI" in str(x) for x in intent["static_prediction"]["uncertainty"].values())


def test_numeric_values_cannot_influence_evidence_only_production_static():
    req, signed, numeric, policy, now = replay_fixture()
    i1, _ = build_formal_static(req, signed, numeric, policy=policy, now=now)
    numeric["runners"][0]["canonical_components"]["ZAI-WIN"]["value"] = -999999
    i2, _ = build_formal_static(req, signed, numeric, policy=policy, now=now)
    assert i1 == i2


@pytest.mark.parametrize("case,code", [
    ("expired", "PRESTART_STATIC_OWNER_DEADLINE_HOLD"),
    ("wrong_race", "SIGNED_SOURCE_RACE_MISMATCH"),
    ("invalid_number", "NUMERICAL_CLOSURE_ONLY_NOT_PREDICTIVE"),
    ("wrong_universe", "FULL_RUNNER_UNIVERSE_MISMATCH"),
    ("unauthorized", "STATIC_OWNER_AUTHORIZATION_MISSING"),
    ("unapproved_venue", "VENUE_OWNER_NOT_AUTHORIZED"),
    ("unsigned", "SOURCE_SIGNATURE_REQUIRED"),
    ("wrong_clock", "OFFICIAL_SOURCE_POST_MISMATCH"),
])
def test_explicit_owner_gate_and_signed_source_fail_closed(case,code):
    req, source, numeric, policy, now = replay_fixture()
    if case == "expired":
        now = datetime.fromisoformat("2026-10-14T16:40:01+09:00")
    if case == "wrong_race":
        source["receipt"]["race_id"] = "OTHER"
    if case == "invalid_number":
        numeric["strict_full_numerical_ready"] = False
    if case == "wrong_universe":
        numeric["runners"].pop()
    if case == "unauthorized":
        policy["enabled"] = False
    if case == "unapproved_venue":
        policy["venues"] = ["OHI"]
    if case == "unsigned":
        source.pop("signature")
    if case == "wrong_clock":
        req["scheduled_post_at"] = "2026-10-14T16:46:00+09:00"
    with pytest.raises(StaticOwnerError, match=code):
        build_formal_static(req, source, numeric, policy=policy, now=now)


def test_auto_owner_intent_can_be_normalized_by_existing_formal():
    from runtime import formal_execution_orchestrator as o
    request, source, numeric, policy, now = replay_fixture()
    intent, _ = build_formal_static(request, source, numeric, policy=policy, now=now)
    normalized, events = o.normalize_single_entry_intent(intent)
    assert normalized["static_prediction_frozen"] is True
    assert normalized["final_prediction_package"]
    assert normalized["static_prediction"]["ranking"] == intent["static_prediction"]["ranking"]
    assert normalized["current_authority_manifest"] == request["current_authority_manifest"]

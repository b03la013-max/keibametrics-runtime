"""Synthetic boundary regressions; fixtures are never real OIDC evidence."""
from datetime import date
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from jra_bvi_environment import _bound_profile_raw_hashes, build_environment_dataset
from jra_pedigree_corpus import HARVEST_PROFILE, _clean_runs, build_corpus

CUTOFF = "2026-10-24T21:00:00+00:00"
DAY = "2026-10-25"


def run(**extra):
    return {"date": "2026-09-01", "venue": "京都", "surface": "芝", "distance_m": 1800,
            "race_name": "2勝クラス", "finish": 2, "field_size": 12, "body_weight": 478, **extra}


def harvest(root, name, runs, *, captured="2026-10-24T12:00:00Z", horse_name="検証馬", dam="検証母"):
    path = root / "runtime/pedigree_corpus" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    obj = {"profile": HARVEST_PROFILE, "official": True, "source": "www.jra.go.jp",
           "harvested_at": captured, "horse_count": 1, "horse_token_count": 1,
           "horses": [{"horse_name": horse_name, "sire": "検証父", "dam": dam,
                       "damsire": "検証母父", "raw_sha256": "a" * 64, "runs": runs}]}
    obj["sha256"] = hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
    return path


def dataset(root, **kw):
    return build_environment_dataset(root, prediction_cutoff=CUTOFF, race_date=DAY,
                                     attestation_verifier=lambda _: True, **kw)


def test_clean_runs_retains_going_only_in_explicit_research_mode():
    raw = run(going="稍")
    old = _clean_runs([raw], date.fromisoformat(DAY))[0]
    enhanced = _clean_runs([raw], date.fromisoformat(DAY), include_environment=True)[0]
    assert "going" not in old
    assert enhanced["going"] == "稍重"
    assert enhanced["going_raw"] == "稍"
    assert {k: enhanced[k] for k in old} == old


def test_projection_preserves_default_reader_counts_manifest_and_row(tmp_path):
    harvest(tmp_path, "a.json", [run(going="良")])
    before = build_corpus(tmp_path, prediction_cutoff=CUTOFF, race_date=DAY,
                          attestation_verifier=lambda _: True)
    out = dataset(tmp_path)
    after = build_corpus(tmp_path, prediction_cutoff=CUTOFF, race_date=DAY,
                         attestation_verifier=lambda _: True)
    assert before == after
    assert out["baseline_corpus"] == {k: v for k, v in before.items() if k != "horses"}
    assert len(out["rows"]) == before["run_count"] == 1
    assert out["coverage"]["going"]["observed"] == 1
    assert out["rows"][0]["going"] == "良"
    assert out["production_effect"] == "NONE"
    assert not out["model_training_eligibility"]


def test_unknown_going_not_guessed_from_rain_weather_or_other_race(tmp_path):
    harvest(tmp_path, "a.json", [run(weather="雨", rainfall_mm=20, moisture_pct=12,
                                    cushion_value=8, inner_outer="外", going="不明")])
    out = dataset(tmp_path)
    row = out["rows"][0]
    for field in ("going", "weather", "rainfall_mm", "moisture_pct", "cushion_value", "inner_outer"):
        assert row[field] is None
    assert row["going_raw_values"] == ["不明"]
    assert out["coverage"]["going"]["missing"] == 1


def test_duplicate_horse_and_run_are_one_cluster_not_two_offspring(tmp_path):
    harvest(tmp_path, "a.json", [run(going="良"), run(going="良")])
    harvest(tmp_path, "b.json", [run(going="良")])
    out = dataset(tmp_path)
    assert len(out["rows"]) == 1
    assert out["duplicate_observations_excluded"] == 2
    sire = out["parent_distributions"]["sire"][0]
    assert sire["runs"] == 1 and sire["composite_offspring"] == 1
    assert sire["independent_official_offspring"] is None


def test_conflicting_going_quarantines_environment_not_production_run(tmp_path):
    harvest(tmp_path, "a.json", [run(going="良")])
    harvest(tmp_path, "b.json", [run(going="重")])
    out = dataset(tmp_path)
    assert out["baseline_corpus"]["run_count"] == 1
    assert out["baseline_corpus"]["run_conflict_count"] == 0
    assert out["rows"][0]["going"] is None
    assert out["coverage"]["going"]["conflict"] == 1
    assert out["rows"][0]["environment_status"]["going"] == "CONFLICT_QUARANTINED"


def test_conflicting_outcome_is_not_reintroduced_by_environment(tmp_path):
    harvest(tmp_path, "a.json", [run(going="良", finish=2)])
    harvest(tmp_path, "b.json", [run(going="良", finish=3)])
    out = dataset(tmp_path)
    assert out["rows"] == []
    assert out["baseline_corpus"]["run_conflict_count"] == 1


def test_name_only_horses_not_merged(tmp_path):
    harvest(tmp_path, "a.json", [run(going="良")], dam="母A")
    harvest(tmp_path, "b.json", [run(going="良")], dam="母B")
    out = dataset(tmp_path)
    assert len(out["rows"]) == 2
    assert len({r["horse_id"] for r in out["rows"]}) == 2
    assert out["baseline_corpus"]["identity_collision_count"] == 1


def test_post_cutoff_capture_and_target_day_outcomes_are_excluded(tmp_path):
    harvest(tmp_path, "a.json", [run(going="良"), run(date=DAY, going="重")])
    harvest(tmp_path, "late.json", [run(date="2026-09-02", going="良")],
            captured="2026-10-25T22:00:00Z")
    out = dataset(tmp_path)
    assert len(out["rows"]) == 1
    assert out["rows"][0]["date"] == "2026-09-01"
    assert out["rows"][0]["available_at"] == "2026-10-24T21:00:00+00:00"
    assert out["rows"][0]["available_at"] != out["rows"][0]["date"]


def test_no_boolean_flag_or_hash_tamper_bypasses_verification(tmp_path):
    path = harvest(tmp_path, "a.json", [run(going="良")])
    obj = json.loads(path.read_text())
    obj["horses"][0]["runs"][0]["going"] = "重"
    path.write_text(json.dumps(obj), encoding="utf-8")
    out = dataset(tmp_path)
    assert out["rows"] == []
    assert out["baseline_corpus"]["rejected_untrusted_inputs"] == 1


def test_no_injected_verifier_no_claimed_oidc_acceptance(tmp_path, monkeypatch):
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    harvest(tmp_path, "a.json", [run(going="良")])
    out = build_environment_dataset(tmp_path, prediction_cutoff=CUTOFF, race_date=DAY)
    assert out["rows"] == []


def test_mixed_surface_unknown_to_research_without_changing_old_parser(tmp_path):
    harvest(tmp_path, "a.json", [run(going="良", surface="芝ダ")])
    out = dataset(tmp_path)
    assert out["rows"][0]["surface"] is None
    assert out["baseline_corpus"]["run_count"] == 1
    assert _clean_runs([run(surface="芝ダ")], date.fromisoformat(DAY))[0]["surface"] == "芝"


def test_cname_or_self_declared_race_id_not_promoted_to_permanent_id(tmp_path):
    harvest(tmp_path, "a.json", [run(going="良", official_race_id="202605040801",
                                    result_navigation_reference="pw01sde0105")])
    out = dataset(tmp_path)
    assert out["rows"][0]["official_race_id"] is None
    assert out["rows"][0]["race_identity_status"].startswith("COMPOSITE_PROVISIONAL")
    assert out["official_permanent_horse_ids"] == 0


def test_deterministic_dataset_and_all_field_denominators(tmp_path):
    harvest(tmp_path, "a.json", [run(going="良"), run(date="2026-09-02", going="重", venue="大井")])
    one, two = dataset(tmp_path), dataset(tmp_path)
    assert one == two
    assert len(one["rows"]) == 2
    assert one["jra_10_venue_runs"] == 1
    assert all(v["denominator"] == 2 for v in one["coverage"].values())
    assert all(v["denominator"] == 1 for v in one["jra_10_venue_coverage"].values())


def test_profile_raw_hash_requires_exact_nested_snapshot_and_clock(tmp_path):
    from datetime import datetime
    profile = {"horse_name": "検証馬", "pedigree": {"sire": "父", "dam": "母", "damsire": "母父"},
               "raw_sha256": "a" * 64, "source_snapshot_sha256": "b" * 64, "runs": [run()]}
    art = {"jra_official_race_card_detail": {"runners": [{"horse_no": 1, "horse_name": "検証馬", "sire": "父", "dam": "母", "damsire": "母父"}]},
           "jra_official_horse_history": {"runners": {"1": profile}},
           "sources": [{"snapshot_sha256": "b" * 64, "raw_sha256": "a" * 64,
                        "source_id": "JRA-OFFICIAL-HORSE-HISTORY", "official": True,
                        "fetched_at": "2026-10-24T11:00:00Z"}]}
    path = tmp_path / "source.json"
    path.write_text(json.dumps({"artifact": art}), encoding="utf-8")
    frozen = datetime.fromisoformat("2026-10-24T12:00:00+00:00")
    assert list(_bound_profile_raw_hashes(path, frozen).values()) == ["a" * 64]
    art["sources"][0]["raw_sha256"] = "c" * 64
    path.write_text(json.dumps({"artifact": art}), encoding="utf-8")
    assert _bound_profile_raw_hashes(path, frozen) == {}
    _, conflicts = _bound_profile_raw_hashes(path, frozen, include_conflicts=True)
    assert set(conflicts.values()) == {"PROFILE_RAW_HASH_BINDING_CONFLICT"}
    art["sources"][0]["raw_sha256"] = "a" * 64
    art["sources"][0]["fetched_at"] = "2026-10-24T13:00:00Z"
    path.write_text(json.dumps({"artifact": art}), encoding="utf-8")
    assert _bound_profile_raw_hashes(path, frozen) == {}
    _, conflicts = _bound_profile_raw_hashes(path, frozen, include_conflicts=True)
    assert set(conflicts.values()) == {"PROFILE_RAW_FETCH_AFTER_SIGNED_FREEZE"}


def test_time_conflict_quarantines_only_env_and_other_original_can_rescue(tmp_path, monkeypatch):
    import jra_pedigree_corpus
    import jra_bvi_environment
    h = {"horse_name": "検証馬", "sire": "検証父", "dam": "検証母", "damsire": "検証母父", "runs": [run(going="重")]}
    snapshot = "d" * 64
    summary = {"race_id": "KM-JRA-KYO-20261024-R01", "source_snapshot_sha256": snapshot,
               "source_freeze_at": "2026-10-24T10:00:00Z", "horses": [h]}
    art = {"jra_official_race_card_detail": {"runners": [{"horse_no": 1, **{k: h[k] for k in ("horse_name", "sire", "dam", "damsire")}}]},
           "jra_official_horse_history": {"runners": {"1": {
               "horse_name": h["horse_name"], "pedigree": {k: h[k] for k in ("sire", "dam", "damsire")},
               "raw_sha256": "a" * 64, "source_snapshot_sha256": "b" * 64, "runs": h["runs"]}}},
           "sources": [{"snapshot_sha256": "b" * 64, "raw_sha256": "a" * 64,
                        "source_id": "JRA-OFFICIAL-HORSE-HISTORY", "official": True,
                        "fetched_at": "2026-10-24T11:00:00Z"}]}
    path = tmp_path / "runtime/executions/E/SOURCE/runs/1/source_receipt_envelope.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"artifact": art}), encoding="utf-8")
    # Deliberately synthetic Source cryptographic boundary; real acceptance
    # injects no verifier. This test concerns downstream temporal isolation.
    monkeypatch.setattr(jra_pedigree_corpus, "_verified_source", lambda _: summary)
    monkeypatch.setattr(jra_bvi_environment, "_verified_source", lambda _: summary)
    quarantined = dataset(tmp_path)
    assert quarantined["baseline_corpus"]["run_count"] == 1
    assert quarantined["environment_quarantined_rows"] == 1
    assert quarantined["rows"][0]["going"] is None
    assert not quarantined["rows"][0]["research_label_eligible"]
    assert quarantined["jra_10_venue_coverage"]["going"]["denominator"] == 1
    harvest(tmp_path, "good.json", [run(going="良")])
    rescued = dataset(tmp_path)
    assert rescued["baseline_corpus"]["run_count"] == 1
    assert rescued["environment_quarantined_rows"] == 0
    assert rescued["rows"][0]["research_label_eligible"]
    assert rescued["rows"][0]["going"] == "良"

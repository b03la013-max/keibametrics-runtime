"""Adversarial offline going-coverage tests. No external SOURCE or OIDC access."""
import copy
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("env_research_quality", ROOT / "environment_quality.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def run(*, date="2026-09-01", venue="東京", surface="芝", going="良",
        race="3歳上1勝クラス", finish=2, field=12):
    return {"date": date, "venue": venue, "surface": surface, "going": going,
            "race_name": race, "distance_m": 1600,
            "finish": finish, "field_size": field,
            "weather": "晴"}


def horse(name, rows, damsire="DAM-SIRE"):
    return {"horse_name": name, "sire": "SIRE", "dam": f"DAM-{name}",
            "damsire": damsire, "raw_sha256": "a" * 64, "runs": rows}


def saved(path, horses):
    value = {
        "profile": m.HARVEST_PROFILE,
        "source": "www.jra.go.jp",
        "official": True,
        "race_date": "2026-10-26",
        "collection_started_at": "2026-10-26T10:00:00+00:00",
        "horse_count": len(horses),
        "horses": copy.deepcopy(horses),
    }
    value["sha256"] = m.harvest_sha(value)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


def test_source_observed_vs_missing_and_obstacle_never_weather_imputed(tmp_path):
    f = saved(tmp_path / "one.json", [
        horse("A", [run(going="稍")]),
        horse("B", [run(going="", date="2026-09-02", surface="芝", race="2歳未勝利")]),
        horse("C", [run(going="芝:良/ダ:重", date="2026-09-03",
                        surface="芝・ダ", race="障害未勝利")]),
        horse("D", [run(going="晴", date="2026-09-04")]),
        horse("E", [run(going="不", date="2026-09-05")], damsire=""),
        horse("F", [run(going="良", date="2026-09-06", venue="門別")]),
    ])
    c = m.audit_snapshots([f])
    n = c["counts"]
    assert n["deduplicated_provisional_runs"] == 6
    assert n["flat_direct_going_observed"] == 2
    assert n["flat_original_going_missing"] == 1
    assert n["explicit_obstacle_or_mixed_surface_runs"] == 1
    assert n["invalid_direct_going_runs"] == 1
    assert n["non_jra_or_unsupported_surface_runs"] == 1
    assert n["flat_runs_with_missing_damsire"] == 1
    assert c["observed_direct_goings"] == {"不良": 1, "稍重": 1}
    assert not c["weather_imputation"]
    assert not c["github_oidc_reverified_by_this_audit"]
    assert c["strict_training_eligible"] == c["forward_oos_increment"] == 0
    assert c["official_horse_id_confirmed"] == c["independent_race_bound_labels_confirmed"] == 0
    assert c["sha256"] == m.canonical_sha({k:v for k,v in c.items() if k != "sha256"})


def test_duplicate_same_horse_is_one_proxy_run_not_new_offspring(tmp_path):
    x = horse("A", [run(going="良")])
    f = saved(tmp_path / "one.json", [x])
    y = copy.deepcopy(x)
    y["runs"][0]["going"] = ""
    g = saved(tmp_path / "two.json", [y])
    result = m.audit_snapshots([g, f])
    n = result["counts"]
    assert n["source_files"] == 2
    assert n["valid_provisional_observations"] == 2
    assert n["deduplicated_provisional_runs"] == 1
    assert n["repeated_provisional_observations"] == 1
    assert n["flat_direct_going_observed"] == 1
    assert n["observed_with_missing_duplicate"] == 1
    assert n.get("flat_original_going_missing", 0) == 0


@pytest.mark.parametrize("change,expected", [
    ({"going": "重"}, "conflicting_direct_going_runs"),
    ({"surface": "ダ"}, "conflicting_surface_or_label_runs"),
    ({"finish": 3}, "conflicting_surface_or_label_runs"),
    ({"going": "晴"}, "invalid_direct_going_runs"),
])
def test_conflicting_or_invalid_duplicates_never_silently_consensus(tmp_path, change, expected):
    f = saved(tmp_path / "one.json", [horse("A", [run()])])
    other = run(**change)
    g = saved(tmp_path / "two.json", [horse("A", [other])])
    count = m.audit_snapshots([f, g])["counts"]
    assert count[expected] == 1
    assert count.get("flat_direct_going_observed", 0) == 0


@pytest.mark.parametrize("mutation,expected", [
    ("tamper", "ENV_HARVEST_SELF_HASH_MISMATCH"),
    ("wrong_provider", "ENV_UNRECOGNIZED_HARVEST_PROVENANCE"),
    ("profile_without_raw_digest", "ENV_PROFILE_RAW_DIGEST_MISSING"),
    ("false_cardinality", "ENV_HARVEST_CARDINALITY_MISMATCH"),
    ("malformed_race_day", "ENV_HARVEST_RACE_DATE_INVALID"),
])
def test_false_source_integrity_or_provenance_is_hard_reject(tmp_path, mutation, expected):
    f = saved(tmp_path / "one.json", [horse("A", [run()])])
    j = json.loads(f.read_text())
    if mutation == "tamper":
        j["horses"][0]["sire"] = "TAMPERED-SIRE"
    elif mutation == "wrong_provider":
        j["source"] = "unapproved-host"
    elif mutation == "profile_without_raw_digest":
        del j["horses"][0]["raw_sha256"]
    elif mutation == "false_cardinality":
        j["horse_count"] = 2
    elif mutation == "malformed_race_day":
        j["race_date"] = "yesterday"
    if mutation != "tamper":
        j["sha256"] = m.harvest_sha(j)
    f.write_text(json.dumps(j))
    with pytest.raises(ValueError, match=expected):
        m.audit_snapshots([f])


def test_prospective_result_not_borrowed_as_historical_training_label(tmp_path):
    f = saved(tmp_path / "one.json", [horse("A", [
        run(date="2026-10-26"), run(date="2026-10-27"),
        run(date="2026-10-25"), run(date="not a date")
    ])])
    n = m.audit_snapshots([f])["counts"]
    assert n["source_run_observations"] == 4
    assert n["invalid_or_current_run_observations"] == 3
    assert n["deduplicated_provisional_runs"] == 1


def test_source_symlink_is_not_a_provenance_witness(tmp_path):
    f = saved(tmp_path / "one.json", [horse("A", [run()])])
    alias = tmp_path / "alias.json"
    alias.symlink_to(f)
    with pytest.raises(ValueError, match="ENV_SOURCE_NOT_REGULAR_FILE"):
        m.audit_snapshots([alias])


def test_absent_damsire_does_not_invent_parent_or_training_id(tmp_path):
    f = saved(tmp_path / "one.json", [horse("A", [run()], damsire="")])
    audit = m.audit_snapshots([f])
    assert audit["counts"]["flat_runs_with_missing_damsire"] == 1
    assert audit["strict_training_eligible"] == 0
    assert audit["classification"].startswith("POST_CAPTURE_RETAINED_HARVEST_SUBSET")


def replace_clock(path, **changes):
    value = json.loads(path.read_text())
    for key, updated in changes.items():
        if updated is None:
            value.pop(key, None)
        else:
            value[key] = updated
    value["sha256"] = m.harvest_sha(value)
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_claimed_producer_clock_is_not_independent_availability(tmp_path):
    finish_only = replace_clock(
        saved(tmp_path / "finish.json", [horse("A", [run()])]),
        collection_started_at=None,
        harvested_at="2026-10-26T11:00:00+00:00",
    )
    no_clock = replace_clock(
        saved(tmp_path / "missing.json", [horse("B", [run()])]),
        collection_started_at=None, harvested_at=None,
    )
    report = m.audit_snapshots([finish_only, no_clock])
    counts = report["counts"]
    assert counts["source_clock_finish_self_declared_only"] == 1
    assert counts["source_clock_no_self_declared_clock"] == 1
    assert counts["missing_source_collection_clock"] == 2
    assert counts["flat_direct_going_observed"] == 2
    assert counts["flat_direct_going_with_self_declared_clock"] == 1
    assert counts["flat_direct_going_without_self_declared_clock"] == 1
    assert counts["proxy_runs_without_self_declared_capture_clock"] == 1
    assert not report["github_oidc_reverified_by_this_audit"]
    assert report["strict_training_eligible"] == 0
    assert "NOT_INDEPENDENT_AVAILABILITY" in report["capture_clock_claim_class"]


@pytest.mark.parametrize("changes,reason", [
    ({"collection_started_at": "yesterday"}, "ENV_SOURCE_CLOCK_INVALID"),
    ({"collection_started_at": "2026-10-26T11:00:00"}, "ENV_SOURCE_CLOCK_WITHOUT_TIMEZONE"),
    ({"collection_started_at": "2026-10-26T12:00:00+00:00",
      "harvested_at": "2026-10-26T10:00:00+00:00"}, "ENV_SOURCE_CLOCK_REVERSED"),
])
def test_malformed_naive_or_reversed_producer_clock_is_rejected(tmp_path, changes, reason):
    f = saved(tmp_path / "bad-clock.json", [horse("A", [run()])])
    replace_clock(f, **changes)
    with pytest.raises(ValueError, match=reason):
        m.audit_snapshots([f])

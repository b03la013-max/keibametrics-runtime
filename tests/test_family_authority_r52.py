import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))

import family_authority_guard as g  # noqa: E402
import jra_index_provenance_builder as B  # noqa: E402

R51 = json.loads((ROOT / "profiles/KM_FAMILY_CURRENT_AUTHORITY_20261012_R51.json").read_text())
R52 = json.loads((ROOT / "profiles/KM_FAMILY_CURRENT_AUTHORITY_20261115_R52.json").read_text())


def test_r52_not_active_before_effective_time_so_race_day_keeps_r51():
    _, a = g.resolve_current_authority(ROOT, now=datetime(2026, 11, 15, 12, tzinfo=timezone.utc))
    assert a["manifest_id"] == R51["manifest_id"]


def test_r52_resolves_after_effective_time():
    _, a = g.resolve_current_authority(ROOT, now=datetime(2026, 11, 17, tzinfo=timezone.utc))
    assert a["manifest_id"] == "KM-FAMILY-CURRENT-AUTHORITY-20261115-R52"
    assert a["predecessor"] == R51["manifest_id"]


def test_r52_inherits_r51_except_jra_amendment_keys():
    changed = {k for k in R52 if R51.get(k) != R52.get(k)}
    assert changed == {"manifest_id", "status", "effective_at", "predecessor", "precedence",
                       "family_scoped_authority", "jra_owner_amendment_20261114"}
    assert R52["status"].startswith(R51["status"])
    assert R52["common_family_components"] == R51["common_family_components"]
    for fam in R51["family_scoped_authority"]:
        if fam != "JRA":
            assert R52["family_scoped_authority"][fam] == R51["family_scoped_authority"][fam]
    j51, j52 = R51["family_scoped_authority"]["JRA"], R52["family_scoped_authority"]["JRA"]
    assert {k for k in j52 if j51.get(k) != j52.get(k)} == {"tsl_authority", "zai_formula", "external_band_inputs"}


def test_r52_recorded_formula_equals_runtime_registry():
    z = R52["jra_owner_amendment_20261114"]
    assert z["zai_v1_0"]["ZAI_WIN"] == B.ZAI_WIN_WEIGHTS["v1.0"]
    assert z["zai_v1_0"]["ZAI_PLACE"] == B.ZAI_PLACE_WEIGHTS["v1.0"]
    assert z["zai_v1_1"]["ZAI_WIN"] == B.ZAI_WIN_WEIGHTS["v1.1"]
    assert z["zai_v1_1"]["ZAI_PLACE"] == B.ZAI_PLACE_WEIGHTS["v1.1"]
    assert B.ZAI_V11_EFFECTIVE_DATE == "20261115"


def test_r52_contracts_still_validate():
    for load, check in ((g.load_scope_contract, g.validate_scope_contract),
                        (g.load_lifecycle_contract, g.validate_lifecycle_contract),
                        (g.load_maturity_contract, g.validate_maturity_contract)):
        check(load(R52))

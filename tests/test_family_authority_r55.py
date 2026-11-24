import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))

import family_authority_guard as g  # noqa: E402

R54 = json.loads((ROOT / "profiles/KM_FAMILY_CURRENT_AUTHORITY_20261116_R54.json").read_text())
R55 = json.loads((ROOT / "profiles/KM_FAMILY_CURRENT_AUTHORITY_20261124_R55.json").read_text())


def test_r55_resolves_from_2026_11_26_jst_and_r54_before():
    _, a = g.resolve_current_authority(ROOT, now=datetime(2026, 11, 25, 14, 0, tzinfo=timezone.utc))
    assert a["manifest_id"] == R54["manifest_id"]
    _, a = g.resolve_current_authority(ROOT, now=datetime(2026, 11, 26, tzinfo=timezone.utc))
    assert a["manifest_id"] == R55["manifest_id"] and a["predecessor"] == R54["manifest_id"]


def test_r55_changes_only_jra_source_trust():
    assert R55["common_family_components"] == R54["common_family_components"]
    for fam in R54["family_scoped_authority"]:
        if fam != "JRA":
            assert R55["family_scoped_authority"][fam] == R54["family_scoped_authority"][fam]
    j54, j55 = R54["family_scoped_authority"]["JRA"], R55["family_scoped_authority"]["JRA"]
    assert {k for k in set(j54) | set(j55) if j54.get(k) != j55.get(k)} == {
        "source_first_formal_handoff", "source_trust_witness"}
    skip = {"manifest_id", "status", "effective_at", "predecessor", "precedence", "family_scoped_authority",
            "r55_change_declaration"}
    assert {k: v for k, v in R55.items() if k not in skip} == {k: v for k, v in R54.items() if k not in skip}
    assert R55["r55_change_declaration"]["new_numerics"] is False


def test_r55_contracts_still_validate():
    for load, check in ((g.load_scope_contract, g.validate_scope_contract),
                        (g.load_lifecycle_contract, g.validate_lifecycle_contract),
                        (g.load_maturity_contract, g.validate_maturity_contract)):
        check(load(R55))

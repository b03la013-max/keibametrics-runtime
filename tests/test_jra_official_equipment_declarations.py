import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime/jra_source_runtime"))
sys.path.insert(0, str(ROOT / "runtime"))
import jra_race_card_detail as d  # noqa: E402

ICON = '<span class="horse_icon blinker"><img src="/JRADB/img/kigo/icon_blinker.png" alt="ブリンカー着用" /></span>'


def page(rows):
    body = "".join(f'<tr><td class="waku">1</td><td class="num">{n}{ICON if b else ""}\n    </td><td class="horse">x</td></tr>'
                   for n, b in rows)
    return f"<html><body><table>{body}</table></body></html>".encode("shift_jis")


def test_declared_and_not_declared_on_complete_card():
    e = d.parse_equipment_declarations(page([(1, True), (2, False), (3, False)]), "text/html; charset=Shift_JIS",
                                       active_numbers=[1, 2, 3])
    assert e["complete"] is True and e["declared_count"] == 1
    assert e["runners"]["1"] == {"horse_no": 1, "blinker_declared": True, "state": "DECLARED"}
    assert e["runners"]["2"]["state"] == "NOT_DECLARED_ON_OFFICIAL_CARD" and e["runners"]["2"]["blinker_declared"] is False
    assert e["fact_only"] is True and e["effect_score_authority"] is False


def test_missing_cell_keeps_unknown_never_absent():
    e = d.parse_equipment_declarations(page([(1, True), (2, False)]), "text/html; charset=Shift_JIS",
                                       active_numbers=[1, 2, 3])
    assert e["complete"] is False
    assert e["runners"]["3"] == {"horse_no": 3, "blinker_declared": None, "state": "UNKNOWN"}
    # An incomplete card cannot prove absence for runners whose cell was seen either.
    assert e["runners"]["2"]["state"] == "UNKNOWN"
    assert e["runners"]["1"]["state"] == "DECLARED"


def test_conflicting_duplicate_cells_fail_closed():
    with pytest.raises(ValueError, match="CONFLICT"):
        d.parse_equipment_declarations(page([(1, True), (1, False)]), "text/html; charset=Shift_JIS", active_numbers=[1])


def test_hash_is_deterministic_and_changes_with_facts():
    a = d.parse_equipment_declarations(page([(1, True), (2, False)]), "text/html; charset=Shift_JIS", active_numbers=[1, 2])
    b = d.parse_equipment_declarations(page([(1, True), (2, False)]), "text/html; charset=Shift_JIS", active_numbers=[1, 2])
    c = d.parse_equipment_declarations(page([(1, False), (2, False)]), "text/html; charset=Shift_JIS", active_numbers=[1, 2])
    assert a["sha256"] == b["sha256"] != c["sha256"]

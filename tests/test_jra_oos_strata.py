import sys
sys.path.insert(0, "runtime/analysis")
from jra_oos_strata import conditions, going_class, keys, split, venue_rule
from pathlib import Path


def test_conditions_from_frozen_source():
    c = conditions(Path(".").resolve(), "KM-JRA-TKY-20261115-R09")
    assert c == {"surface": "ダ", "distance": 1400, "going": "良"}
    assert keys("KM-JRA-TKY-20261115-R09", c) == {"venue_surface": "TKY:ダ", "venue_surface_distance": "TKY:ダ:S",
                                                  "venue_surface_going": "TKY:ダ:DRY"}
    assert going_class("稍重") == "DAMP" and going_class("不良") == "WET"


def _rows(cells):
    rows = []
    for cell, n, eff in cells:
        v, s = cell.split(":")
        rows += [{"strata": {"venue_surface": cell, "venue_surface_distance": cell + ":M",
                             "venue_surface_going": cell + ":DRY"}, "e": eff} for _ in range(n)]
    return rows


def test_venue_rule_needs_two_decisive_cells_same_direction():
    v = lambda rows: venue_rule(split(rows, lambda r: r["e"]))["verdict"]
    assert v(_rows([("KYO:芝", 12, 1.0), ("TKY:芝", 5, 1.0)])) == "INSUFFICIENT_CELLS"
    assert v(_rows([("KYO:芝", 12, 1.0), ("TKY:芝", 12, 0.5)])) == "CONSISTENT_IMPROVEMENT"
    assert v(_rows([("KYO:芝", 12, 1.0), ("TKY:芝", 12, -0.5)])) == "MIXED"
    assert v(_rows([("KYO:芝", 12, -1.0), ("KYO:ダ", 12, -0.5)])) == "CONSISTENT_DEGRADATION"

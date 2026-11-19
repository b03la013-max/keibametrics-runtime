"""Regression 2026-11-19: nankan() filled _CACHE first, _load() then skipped the rules -> KeyError 'rules' and
every race's kametani evidence was ERROR (C7 got no records)."""
from runtime.local_autopilot import bloodline_kametani as bk


def test_rules_load_after_nankan_first():
    bk._CACHE.clear()
    bk.nankan({'sire': 'シニスターミニスター'}, {'venue_id': 'OHI', 'distance': 1200, 'going': '良'})
    assert bk.table()                       # must not raise KeyError
    bk._CACHE.clear()

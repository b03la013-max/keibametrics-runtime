"""Evaluation strata and the venue rule for JRA forward OOS (LOCAL C2/C3 port, NON-PRODUCTION).

Unit of evidence is venue x surface (芝/ダ/障): a Kyoto tendency is never carried to Hanshin.
Finer cells: venue x surface x distance band, venue x surface x going class (turf and dirt
going are separate because the surface is part of the key). Conditions come from the frozen
pre-race SOURCE (race card detail), never from the result.

Adoption rule (venue rule): a candidate effect counts only when at least two venue x surface
cells with >= MIN_CELL races each move in the same direction and none of the decisive cells
moves the other way. Cells under MIN_CELL are shown as reference only.
"""
import glob, json
from pathlib import Path

MIN_CELL = 12


def going_class(g):
    g = str(g or '')
    if '不良' in g or g.startswith('重'):
        return 'WET'
    if '稍' in g:
        return 'DAMP'
    if '良' in g:
        return 'DRY'
    return 'UNKNOWN'


def distance_band(d):
    if not d:
        return '?'
    return 'S' if d <= 1400 else ('M' if d <= 1800 else ('I' if d <= 2200 else 'L'))


def conditions(root: Path, race_id: str) -> dict:
    reqs = sorted(glob.glob(str(root / f'runtime/requests/{race_id}-LIVE-R*-FORMAL.json')))
    if not reqs:
        return {'surface': None, 'distance': None, 'going': None}
    r = json.loads(Path(reqs[-1]).read_text())
    race = r.get('race') or {}
    env = ((r.get('source_snapshot') or {}).get('jra_official_race_card_detail') or {}).get('race_environment') or {}
    return {'surface': race.get('surface') or env.get('going_surface'), 'distance': race.get('distance'),
            'going': env.get('going')}


def keys(race_id: str, c: dict) -> dict:
    v = race_id.split('-')[2]
    vs = f"{v}:{c.get('surface') or '?'}"
    return {'venue_surface': vs, 'venue_surface_distance': f"{vs}:{distance_band(c.get('distance'))}",
            'venue_surface_going': f"{vs}:{going_class(c.get('going'))}"}


def split(rows, value):
    """rows carry 'strata'; value(row) -> float effect (positive = candidate better)."""
    out = {}
    for level in ('venue_surface', 'venue_surface_distance', 'venue_surface_going'):
        cells = {}
        for r in rows:
            cells.setdefault(r['strata'][level], []).append(value(r))
        out[level] = {k: {'races': len(v), 'mean_effect': round(sum(v) / len(v), 4), 'decides': len(v) >= MIN_CELL}
                      for k, v in sorted(cells.items())}
    return out


def venue_rule(split_out) -> dict:
    cells = split_out['venue_surface']
    dec = {k: c for k, c in cells.items() if c['decides']}
    pos = [k for k, c in dec.items() if c['mean_effect'] > 0]
    neg = [k for k, c in dec.items() if c['mean_effect'] < 0]
    if len(dec) < 2:
        verdict = 'INSUFFICIENT_CELLS'
    elif len(pos) >= 2 and not neg:
        verdict = 'CONSISTENT_IMPROVEMENT'
    elif len(neg) >= 2 and not pos:
        verdict = 'CONSISTENT_DEGRADATION'
    else:
        verdict = 'MIXED'
    return {'verdict': verdict, 'decisive_cells': sorted(dec), 'improving': pos, 'degrading': neg,
            'min_cell_races': MIN_CELL}

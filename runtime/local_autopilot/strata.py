"""Race strata for evaluation (Owner 2026-11-19): venue -> venue x distance -> venue x going.

Read from the signed formal SOURCE receipt (distance / going / surface as frozen before the race), or from the
PAPER prediction's race_cond (persisted from 2026-11-19). Cells are reported with their race count; a cell
with few races is shown but never decides alone (decision rule lives in the pre-registrations).
"""
import json
from pathlib import Path

MIN_CELL = 12


def going_class(g):
    g = str(g or '')
    if '不良' in g or g == '重' or g.startswith('重'):
        return 'WET'
    if '稍' in g:
        return 'DAMP'
    if '良' in g:
        return 'DRY'
    return 'UNKNOWN'


def cond(day_dir, key):
    d = Path(day_dir)
    for p in (d / 'formal' / 'rev2' / f'{key}.source_receipt.json', d / 'formal' / f'{key}.source_receipt.json'):
        try:
            t = json.loads(p.read_text())
        except (OSError, ValueError):
            continue
        hit = _find(t)
        if hit:
            return hit
    try:
        q = json.loads((d / 'queue.json').read_text())
        ed = [e for e in q['races'][key]['editions'] if e.get('rev')]
        rc = json.loads((d / 'rev' / f"{ed[-1]['rev']}.json").read_text())['prediction'].get('race_cond') or {}
        if rc.get('distance'):
            return {'distance': int(rc['distance']), 'going': rc.get('going'), 'going_class': going_class(rc.get('going'))}
    except (OSError, ValueError, KeyError, IndexError):
        pass
    return {'distance': None, 'going': None, 'going_class': 'UNKNOWN'}


def _find(o):
    if isinstance(o, dict):
        if isinstance(o.get('distance'), (int, float)) and 'going' in o:
            return {'distance': int(o['distance']), 'going': o.get('going'), 'going_class': going_class(o.get('going'))}
        for v in o.values():
            h = _find(v)
            if h:
                return h
    elif isinstance(o, list):
        for v in o:
            h = _find(v)
            if h:
                return h
    return None


def keys(venue, c):
    return {'venue': venue, 'venue_distance': f"{venue}:{c.get('distance') or '?'}m",
            'venue_going': f"{venue}:{c.get('going_class')}"}


def split(rows, metric):
    """rows: dicts with 'strata' (from keys) ; metric(list_of_rows) -> dict. Returns {level: {cell: metric+races}}."""
    out = {}
    for level in ('venue', 'venue_distance', 'venue_going'):
        cells = {}
        for r in rows:
            cells.setdefault(r['strata'][level], []).append(r)
        out[level] = {k: dict(metric(v), races=len(v), decides=len(v) >= MIN_CELL) for k, v in sorted(cells.items())}
    return out

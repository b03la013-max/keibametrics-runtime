"""亀谷 sire rules v3 -> one pattern label per runner (B4, Drive 精読 q423, 2026-11-24).

research/kametani/sire_rules_v3.json (built by research/kametani/build_rules_v3.py) = v2 + the corrections of the
full read + 072 母父ディープ (DAMSIRE) + 089 米国型 / 090 日本型 (TYPE, the sire's country type).
label() -> 'BUY' / 'CAUTION' / 'BOTH' / 'NONE', or None when no v3 entry applies to the runner.

The label feeds ext_model as KAME3 (its own measured component KM3, NOT part of PAT), so the existing label KAME
(v2) and the PAT score stay exactly as they were; the KM3 weight starts at 0.0 (ext_connect.DEFAULT_BETA) and moves
only when the weekly hold-out refit improves (Owner 2026-11-21 13:32 EXT connection). Scenes are matched with
kametani_v2c.check (v2 keys + bornle / gapmax / nar / ds 'US|MP' / last '2-5','top3').
"""
import json

from runtime.local_autopilot import bloodline_kametani as bk
from runtime.local_autopilot import kametani_v2c as kc

PROFILE = 'KM-LOCAL-KAMETANI-V3-LABEL-v1.0-20261124'
RULES_V3 = bk.HERE / 'sire_rules_v3.json'
_C = {}


def _load():
    if 'sire' not in _C:
        d = json.loads(RULES_V3.read_text())
        _C['sire'] = {bk._n(e['name']): e for e in d['entries'] if e['kind'] == 'SIRE'}
        _C['dam'] = {bk._n(e['name']): e for e in d.get('damsire_entries') or []}
        _C['type'] = {e['country']: e for e in d.get('type_entries') or []}
        _C['profile'] = d['profile']
    return _C


def _side(alts, ctx, race):
    st = [kc.check(a, ctx, race)[0] for a in alts or []]
    return 'MATCH' in st


def evaluate(runner, race):
    """-> {'entries': [...], 'buy': bool, 'caution': bool} or None. race needs surface, distance, going, race_date."""
    t = _load()
    ctx = bk.context(runner, race)
    hits = []
    e = t['sire'].get(bk._n(runner.get('sire')))
    if e:
        hits.append(('SIRE', e))
    e = t['dam'].get(bk._n(runner.get('damsire')))
    if e:
        hits.append(('DAMSIRE', e))
    st = bk.sire_type(runner.get('sire'))
    e = t['type'].get((st or {}).get('country'))
    if e:
        hits.append(('TYPE', e))
    if not hits:
        return None
    rows = [{'kind': k, 'no': x['no'], 'name': x['name'], 'buy': _side(x.get('buy'), ctx, race),
             'caution': _side(x.get('caution'), ctx, race)} for k, x in hits]
    return {'entries': rows, 'buy': any(r['buy'] for r in rows), 'caution': any(r['caution'] for r in rows)}


def label(runner, race):
    ev = evaluate(runner, race)
    if ev is None:
        return None
    return 'BOTH' if ev['buy'] and ev['caution'] else 'BUY' if ev['buy'] else 'CAUTION' if ev['caution'] else 'NONE'

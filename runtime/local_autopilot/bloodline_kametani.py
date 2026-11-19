"""LOCAL pedigree evidence from the Owner's 亀谷敬正 血統辞典 (v2: hand-structured rules).

v1 (2026-11-18 01:10) split each 買い条件 at '／' and called a runner a buy match when ANY piece matched, so a
horse meeting only 'ダート1200m以下' of 「ダート1200m以下／母が米国型／牡馬」 was a match (C7 defect). v2 reads
research/kametani/sire_rules_v2.json: buy / caution are lists of alternative scenes (OR) whose conditions must
ALL hold (AND). A scene is MATCH only if every condition is known and true; any false condition → NO; any
unknown or NAR-unreadable condition → UNKNOWN; a scene named for JRA courses only → NOT_LOCAL.
Damsire class comes from the same dictionary (only damsires that have their own entry); 「母が◯◯」 is read
through the damsire (proxy). The author's rules are mostly JRA claims, unvalidated on NAR: evidence only.
"""
import json
import unicodedata
from pathlib import Path

PROFILE = 'KM-LOCAL-KAMETANI-PEDIGREE-EVIDENCE-v2.0-20261118'
HERE = Path(__file__).resolve().parents[2] / 'research' / 'kametani'
RULES_V1 = HERE / 'sire_rules.json'
RULES_V2 = HERE / 'sire_rules_v2.json'
WET = ('稍重', '重', '不良')
_CACHE = {}


def _n(s):
    return ''.join(unicodedata.normalize('NFKC', str(s or '')).split())


def _load():
    if 'rules' not in _CACHE:          # not `if not _CACHE`: nankan() shares the dict ('nk'), 2026-11-19 KeyError fix
        v1 = json.loads(RULES_V1.read_text())
        v2 = json.loads(RULES_V2.read_text())
        _CACHE['types'] = {_n(e['name']): e.get('type') or '' for e in v1['entries'] if e['kind'] in ('SIRE', 'DAMSIRE')}
        _CACHE['rules'] = {_n(e['name']): e for e in v2['entries'] if e['kind'] in ('SIRE', 'DAMSIRE')}
        _CACHE['sha'] = v1.get('sha256_source')
    return _CACHE


def table():
    return _load()['rules']


def sire_type(name):
    t = _load()['types'].get(_n(name))
    if not t:
        return None
    country = next((c for c in ('米国型', '欧州型', '日本型') if c in t), None)
    sunday = any(k in t for k in ('サンデー', 'ディープ', 'ステイゴールド', 'ハーツクライ', 'フジキセキ', 'ゴールドアリュール')) \
        and '非サンデー' not in t
    km = any(k in t for k in ('キングマンボ', 'キングカメハメハ'))
    return {'country': country or ('日本型' if sunday else None), 'sunday': sunday, 'kingmambo': km}


def _ds(req, dt):
    if dt is None:
        return None
    c, ss, km = dt['country'], dt['sunday'], dt['kingmambo']
    if req == 'SS':
        return ss
    if req == 'nonSS':
        return not ss
    if req == 'SS|KM':
        return ss or km
    if req == 'SS|EU':
        return ss or (None if c is None else c == '欧州型')
    if c is None:
        return None
    m = {'US': '米国型', 'EU': '欧州型', 'JP': '日本型'}
    if req in m:
        return c == m[req]
    if req.startswith('non') and req[3:] in m:
        return c != m[req[3:]]
    return None


def check(alt, ctx):
    """One scene → MATCH / NO / UNKNOWN / NOT_LOCAL, with the per-condition verdicts."""
    if alt.get('jra'):
        return 'NOT_LOCAL', {}
    st, last = ctx['starts'], (ctx['starts'][0] if ctx['starts'] else None)
    v = {}
    if 'S' in alt:
        v['S'] = ctx['surface'] == ('DIRT' if alt['S'] == 'D' else 'TURF')
    if 'd' in alt:
        v['d'] = alt['d'][0] <= ctx['distance'] <= alt['d'][1]
    if 'sex' in alt:
        v['sex'] = None if not ctx['sex'] else (ctx['sex'] in ('牡', 'セ', 'せ', '騸') if alt['sex'] == 'M' else ctx['sex'] == '牝')
    if 'ds' in alt:
        v['ds'] = _ds(alt['ds'], ctx['damsire_type'])
    if 'front' in alt:
        v['front'] = None if ctx['front'] is None else ctx['front'] == bool(alt['front'])
    if 'age' in alt:
        v['age'] = None if ctx['age'] is None else (ctx['age'] <= 3 if alt['age'] == '2-3' else ctx['age'] >= 4)
    if 'wet' in alt:
        v['wet'] = None if not ctx['going'] else (ctx['going'] in WET) == bool(alt['wet'])
    if 'new' in alt:
        v['new'] = ctx['newcomer'] == bool(alt['new'])
    if 'last' in alt:
        f = last.get('finish') if last else None
        v['last'] = None if f is None else {'lost': f >= 2, '4+': f >= 4, 'win': f == 1, 'top5': f <= 5}[alt['last']]
    if 'car' in alt:
        v['car'] = True if len(st) >= alt['car'] else (False if not st or len(st) < 4 else None)
    for k, op in (('bw', lambda w, n: w >= n), ('bwlt', lambda w, n: w < n)):
        if k in alt:
            w = last.get('ride_body_weight') if last else None
            v[k] = None if w is None else op(w, alt[k])
    if 'frame' in alt:
        f = ctx['frame']
        v['frame'] = None if f is None else alt['frame'][0] <= f <= alt['frame'][1]
    if 'chg' in alt:
        ld = last.get('distance') if last else None
        v['chg'] = None if not ld else {'short': ctx['distance'] < ld, 'ext': ctx['distance'] > ld,
                                        'notext': ctx['distance'] <= ld}[alt['chg']]
    if 'lastsurf' in alt:
        ls = last.get('surface') if last else None
        v['lastsurf'] = None if not ls else ls == ('TURF' if alt['lastsurf'] == 'T' else 'DIRT')
    if 'pop' in alt:
        p = ctx['pop']
        v['pop'] = None if p is None else (p <= 3 if alt['pop'] == 'fav' else p >= 6)
    for i, _ in enumerate(alt.get('x') or []):
        v[f'x{i}'] = None
    if any(x is False for x in v.values()):
        return 'NO', v
    return ('UNKNOWN' if any(x is None for x in v.values()) else 'MATCH'), v


def context(runner, race):
    st = runner.get('starts') or []
    pos = [s['content_positions'][0] / s['field_size'] for s in st[:3] if s.get('content_positions') and s.get('field_size')]
    return {'surface': (race.get('surface') or '').upper(), 'distance': int(race.get('distance') or 0),
            'going': race.get('going'), 'sex': (runner.get('sex_age') or '')[:1] or None, 'age': runner.get('age'),
            'damsire_type': sire_type(runner.get('damsire')), 'starts': st, 'newcomer': not st,
            'front': (min(pos) <= 0.34) if pos else None, 'pop': runner.get('popularity'),
            'frame': runner.get('frame_no')}


def evaluate(runner, race):
    e = table().get(_n(runner.get('sire')))
    if not e:
        return None
    ctx = context(runner, race)
    out = {'entry_no': e['no'], 'sire': e['name'], 'type': e.get('type'), 'damsire': runner.get('damsire'),
           'damsire_type': ctx['damsire_type']}
    for side in ('buy', 'caution'):
        rows = [(i, *check(a, ctx)) for i, a in enumerate(e.get(side) or [])]
        out[side] = {'scenes': len(rows), 'match': [i for i, s, _ in rows if s == 'MATCH'],
                     'unknown': [i for i, s, _ in rows if s == 'UNKNOWN'],
                     'not_local': [i for i, s, _ in rows if s == 'NOT_LOCAL'],
                     'verdicts': {i: {'state': s, 'conditions': v} for i, s, v in rows}}
    out['buy_match'] = bool(out['buy']['match'])
    out['caution_match'] = bool(out['caution']['match'])
    out['buy_unknown_only'] = not out['buy_match'] and bool(out['buy']['unknown'])
    return out


NANKAN = Path(__file__).resolve().parents[2] / 'research' / 'nankan' / 'sire_course_rules.json'


def nankan(runner, race):
    """南関東 sire x venue x distance (x going) claims from the Owner library (YouTube transcript)."""
    if 'nk' not in _CACHE:
        _CACHE['nk'] = json.loads(NANKAN.read_text()) if NANKAN.exists() else {'rules': [], 'lines': {}}
    doc = _CACHE['nk']
    sire, v = _n(runner.get('sire')), race.get('venue_id')
    d, g = int(race.get('distance') or 0), race.get('going')
    hits = []
    for r in doc['rules']:
        names = doc['lines'].get(r.get('sire_line'), []) if r.get('sire_line') else [r['sire']]
        if sire not in {_n(x) for x in names} or v not in r['venues']:
            continue
        if 'd' in r and not (r['d'][0] <= d <= r['d'][1]):
            continue
        if 'going' in r and g not in r['going']:
            continue
        hits.append({'id': r['id'], 'side': r['side'], 'claim': r['claim']})
    return hits


def race_evidence(race, runners):
    out = {}
    nk = {}
    for x in runners:
        h = nankan(x, race)
        if h:
            nk[str(x['horse_no'])] = h
    for x in runners:
        ev = evaluate(x, race)
        if ev:
            out[str(x['horse_no'])] = ev
    _load()
    return {'profile': PROFILE, 'rules_source_sha256': _CACHE.get('sha'), 'covered_runners': len(out),
            'runners': len(runners), 'production_effect': 'NONE (author claims, unvalidated on NAR)', 'by_horse': out,
            'nankan_sire_course': nk, 'nankan_profile': 'KM-NANKAN-SIRE-COURSE-RULES-v1.0-20261118'}

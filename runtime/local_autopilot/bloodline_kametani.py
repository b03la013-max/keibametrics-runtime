"""LOCAL pedigree evidence from the Owner's 亀谷敬正 血統辞典 (research/kametani/sire_rules.json).

Each sire entry carries the author's 買い条件 / 消し・割引条件 as text. They are matched mechanically, clause by
clause (split at '／'), against facts already on the Rakuten card: surface, distance, sex, age, damsire type
(only when the damsire itself has an entry), last finish, early position, popularity, maiden/newcomer race.
A clause matches only when every condition it names that can be read is true and none is unknown; otherwise it
is UNKNOWN. The author's rules are mostly JRA claims, unvalidated on NAR: evidence only, never a numeric input.
"""
import json
import re
import unicodedata
from pathlib import Path

PROFILE = 'KM-LOCAL-KAMETANI-PEDIGREE-EVIDENCE-v1.0-20261118'
RULES = Path(__file__).resolve().parents[2] / 'research' / 'kametani' / 'sire_rules.json'
_CACHE = {}


def _n(s):
    return ''.join(unicodedata.normalize('NFKC', str(s or '')).split())


def table():
    if 't' not in _CACHE:
        doc = json.loads(RULES.read_text())
        _CACHE['t'] = {_n(e['name']): e for e in doc['entries'] if e['kind'] in ('SIRE', 'DAMSIRE')}
        _CACHE['sha'] = doc.get('sha256_source')
    return _CACHE['t']


def sire_type(name):
    e = table().get(_n(name))
    if not e or not e.get('type'):
        return None
    t = e['type']
    country = next((c for c in ('米国型', '欧州型', '日本型') if c in t), None)
    sunday = any(k in t for k in ('サンデー', 'ディープ', 'ステイゴールド', 'ハーツ', 'ハーツクライ')) and '非サンデー' not in t
    return {'country': country or ('日本型' if sunday else None), 'sunday': sunday}


JRA_VENUES = ('東京', '中山', '中京', '京都', '阪神', '新潟', '福島', '小倉', '札幌', '函館', 'JRA', '中央')
WET = ('稍重', '重', '不良')


def _clause(c, ctx):
    if any(v in c for v in JRA_VENUES):
        return 'NOT_LOCAL'      # a JRA-course claim says nothing about NAR tracks
    checks = []
    if re.search(r'湿|雨|重馬場|道悪|脚抜き', c):
        checks.append(None if not ctx.get('going') else ctx['going'] in WET)
    if re.search(r'乾いた|良馬場|パサパサ', c):
        checks.append(None if not ctx.get('going') else ctx['going'] not in WET)
    if 'ダート' in c or '砂' in c:
        checks.append(ctx['surface'] == 'DIRT')
    elif '芝' in c:
        checks.append(ctx['surface'] == 'TURF')
    d = ctx['distance']
    for a, b in re.findall(r'(\d{3,4})m?\s*[〜~～-]\s*(\d{3,4})m', c):
        checks.append(int(a) <= d <= int(b))
    for x, rel in re.findall(r'(\d{3,4})m(以下|以上|未満|超)', c):
        x = int(x)
        checks.append({'以下': d <= x, '以上': d >= x, '未満': d < x, '超': d > x}[rel])
    if not re.search(r'\d{3,4}m(以下|以上|未満|超)|\d{3,4}m?\s*[〜~～-]', c):
        for x in re.findall(r'(\d{3,4})m', c):
            checks.append(d == int(x))
    if '牡馬' in c:
        checks.append(ctx['sex'] == '牡')
    if '牝馬' in c:
        checks.append(ctx['sex'] == '牝')
    if re.search(r'2・3歳|2歳|3歳', c):
        checks.append(ctx['age'] is not None and ctx['age'] <= 3)
    if '古馬' in c:
        checks.append(ctx['age'] is not None and ctx['age'] >= 4)
    dt = ctx['damsire_type']
    if re.search(r'母父(が)?非サンデー|母が非サンデー', c):
        checks.append(None if dt is None else not dt['sunday'])
    elif re.search(r'母父(が)?サンデー|母がサンデー', c):
        checks.append(None if dt is None else dt['sunday'])
    for k in ('米国型', '欧州型', '日本型'):
        if re.search(r'母父(が)?' + k + '|母が' + k, c):
            checks.append(None if dt is None or dt['country'] is None else dt['country'] == k)
    if '前走' in c and ('負け' in c or '凡走' in c or '4着以下' in c):
        checks.append(None if ctx['last_finish'] is None else ctx['last_finish'] >= (4 if '4着以下' in c else 2))
    if '先行' in c:
        checks.append(None if ctx['front'] is None else ctx['front'])
    if '人気馬' in c:
        checks.append(ctx['pop'] is not None and ctx['pop'] <= 3)
    if '人気薄' in c:
        checks.append(ctx['pop'] is not None and ctx['pop'] >= 6)
    if '新馬' in c and '未勝利' not in c:
        checks.append(ctx['newcomer'])
    if not checks:
        return 'UNPARSED'
    if any(x is False for x in checks):
        return 'NO'
    return 'UNKNOWN' if any(x is None for x in checks) else 'MATCH'


def evaluate(runner, race):
    e = table().get(_n(runner.get('sire')))
    if not e:
        return None
    st = runner.get('starts') or []
    pos = [s['content_positions'][0] / s['field_size'] for s in st[:3] if s.get('content_positions') and s.get('field_size')]
    ctx = {'surface': (race.get('surface') or '').upper(), 'distance': int(race.get('distance') or 0),
           'sex': (runner.get('sex_age') or ' ')[0], 'age': runner.get('age'),
           'damsire_type': sire_type(runner.get('damsire')), 'last_finish': st[0].get('finish') if st else None,
           'front': (min(pos) <= 0.34) if pos else None, 'pop': runner.get('popularity'), 'newcomer': not st,
           'going': race.get('going')}
    res = {}
    for side in ('buy', 'caution'):
        rows = [(c.strip(), _clause(c, ctx)) for c in re.split(r'[／/]', e.get(side) or '') if c.strip()]
        res[side] = {'match': [c for c, v in rows if v == 'MATCH'], 'unknown': [c for c, v in rows if v == 'UNKNOWN'],
                     'not_local': sum(1 for _, v in rows if v == 'NOT_LOCAL'),
                     'clauses': len(rows)}
    return {'entry_no': e['no'], 'sire': e['name'], 'type': e.get('type'),
            'damsire_type': ctx['damsire_type'], 'buy_match': bool(res['buy']['match']),
            'caution_match': bool(res['caution']['match']), 'buy': res['buy'], 'caution': res['caution']}


def race_evidence(race, runners):
    out = {}
    for x in runners:
        ev = evaluate(x, race)
        if ev:
            out[str(x['horse_no'])] = ev
    return {'profile': PROFILE, 'rules_source_sha256': _CACHE.get('sha'), 'covered_runners': len(out),
            'runners': len(runners), 'production_effect': 'NONE (author claims, unvalidated on NAR)', 'by_horse': out}

"""SHADOW: corrected reading of the 亀谷 sire rules v2 (Drive 精読 2026-11-21, q423 亀谷敬正の競馬血統辞典 全3,174行).

The full read of the dictionary found places where research/kametani/sire_rules_v2.json differs from the text
(GAP list in keibametrics-private-evidence drive_reading ledger q423). v2 now feeds ext_model labels, so v2 itself is
NOT edited here: this module applies the corrections on a copy and reports, per horse, whether the buy / caution
match would change. Evidence only: nothing reads this output for ranking, tickets, KRS, MEC or capital.

New condition keys (only in the patches below; v2 entries are untouched):
  bornle N   born in year <= N (born = race year - age, Japanese age)          [039 旧世代 = 2020年以前生まれ]
  gapmax N   days since the previous start <= N (start date 'YY.MM.DD')          [094 中3週以内]
  last '2-5' / 'top3'  previous finish 2..5 / 1..3                              [094 / 052]
  ds 'US|MP' damsire 米国型 or 大系統ミスタープロスペクター系: True if 米国型, otherwise UNKNOWN (the dictionary has
             no line table for non-entry damsires, so a non-US damsire cannot be shown to be non-ミスプロ)
Damsire entries (072 母父ディープインパクト) are matched on the runner's damsire name.
"""
import copy
import datetime as dt

from runtime.local_autopilot import bloodline_kametani as bk

PROFILE = 'KM-LOCAL-KAMETANI-V2-CORRECTIONS-SHADOW-v1.0-20261121'
B = 9999
SRC = 'Drive q423 亀谷敬正の競馬血統辞典（同名馬統合版）全文精読 2026-11-21'

# (id, entry no, side, op, index, payload, reason)
#   op 'merge'  : add the payload keys to alternative <index>
#   op 'replace': replace alternative <index> by the payload (a list of alternatives)
#   op 'append' : append the payload alternative
PATCHES = [
    ('C1', '023', 'caution', 'merge', 1, {'S': 'T'}, '「母父サンデー系は割引」は芝の話（ダートに掛けない）'),
    ('C2', '034', 'caution', 'merge', 0, {'ds': 'nonUS'}, '原文「狙うなら母系に米国型があるか確認」= 母父米国型は割引から外す'),
    ('C3a', '039', 'buy', 'replace', 1, [{'S': 'D', 'd': [1800, B], 'ds': 'US', 'bornle': 2020}],
     '旧世代 = 2021年生まれより前（2020年以前）。馬齢から読めるので x をやめる'),
    ('C3b', '039', 'buy', 'replace', 2, [{'S': 'D', 'd': [1800, B], 'bw': 460, 'bornle': 2020}], '同上'),
    ('C4', '052', 'caution', 'replace', 0,
     [{'ds': 'EU', 'S': 'D', 'd': [1600, B], 'pop': 'fav', 'lastsurf': 'T'},
      {'ds': 'EU', 'S': 'D', 'd': [1600, B], 'pop': 'fav', 'last': 'top3'}],
     '原文「母父欧州型×ダート1600m以上で、前走芝または前走3着以内で人気」'),
    ('C5', '058', 'caution', 'merge', 0, {'S': 'T'}, '{front:0} の消しは芝の話（ダートに掛けない）'),
    ('C6a', '075', 'buy', 'merge', 0, {'ds': 'US|MP'}, '原文「母父米国型または大系統ミスタープロスペクター系」'),
    ('C6b', '076', 'buy', 'merge', 0, {'ds': 'US|MP'}, '同上（パイロ）'),
    ('C6c', '109', 'buy', 'merge', 1, {'ds': 'US|MP'}, '原文「ダート1900m以上で母父米国型またはミスプロ系」'),
    ('C8a', '087', 'buy', 'append', None, {'car': 5}, '原文の買い条件「キャリア5戦目以降」が v2 に無い'),
    ('C8b', '106', 'buy', 'append', None, {'S': 'D', 'car': 5}, '原文の買い条件「キャリア5戦以上」が v2 に無い'),
    ('C9', '094', 'caution', 'append', None, {'S': 'D', 'age': 'old', 'gapmax': 21, 'last': '2-5', 'pop': 'fav'},
     '原文の消し「古馬混合ダートで中3週以内・前走2～5着の人気馬」が v2 に無い'),
    ('C10', '099', 'buy', 'append', None, {'S': 'D', 'd': [1600, B], 'nar': 1},
     '原文「地方では国タイプにこだわらず」（地方の母系も期待）: NAR では母父米国型を外した場面を追加'),
]
DAMSIRE = {
    'ディープインパクト': {'no': '072', 'caution': [{'S': 'D', 'd': [0, 1400], 'age': 'old', 'pop': 'fav'}],
                    'reason': 'C7 原文「母父ディープ：ダート短距離の古馬混合で人気は消し」（短距離 = 1400m以下で代用）'},
}
NEW_KEYS = ('bornle', 'gapmax', 'nar')


def _year(race):
    s = str(race.get('race_date') or race.get('date') or '')
    return int(s[:4]) if s[:4].isdigit() else None


def _date(race):
    s = ''.join(ch for ch in str(race.get('race_date') or race.get('date') or '') if ch.isdigit())
    try:
        return dt.date(int(s[:4]), int(s[4:6]), int(s[6:8])) if len(s) >= 8 else None
    except ValueError:
        return None


def _start_date(st):
    s = str((st or {}).get('date') or '')
    p = s.split('.')
    try:
        return dt.date(2000 + int(p[0]), int(p[1]), int(p[2])) if len(p) == 3 else None
    except ValueError:
        return None


def corrected_entry(e):
    """A copy of the v2 entry with this module's patches applied (v2 itself is not modified)."""
    e2 = copy.deepcopy(e)
    applied = []
    for pid, no, side, op, i, pay, _ in PATCHES:
        if e2.get('no') != no:
            continue
        alts = e2.setdefault(side, [])
        if op == 'merge' and i is not None and i < len(alts):
            alts[i] = {**alts[i], **pay}
        elif op == 'replace' and i is not None and i < len(alts):
            alts[i:i + 1] = copy.deepcopy(pay)
        elif op == 'append':
            alts.append(copy.deepcopy(pay))
        else:
            continue
        applied.append(pid)
    return e2, applied


def check(alt, ctx, race):
    """bk.check plus the new keys; same states MATCH / NO / UNKNOWN / NOT_LOCAL."""
    extra = {}
    base = {k: v for k, v in alt.items() if k not in NEW_KEYS}
    last = ctx['starts'][0] if ctx['starts'] else None
    if base.get('ds') == 'US|MP':
        dtp = ctx['damsire_type']
        extra['ds'] = None if dtp is None or dtp.get('country') != '米国型' else True
        base.pop('ds')
    if base.get('last') in ('2-5', 'top3'):
        f = last.get('finish') if last else None
        extra['last'] = None if f is None else (2 <= f <= 5 if base['last'] == '2-5' else f <= 3)
        base.pop('last')
    if 'bornle' in alt:
        y = _year(race)
        extra['bornle'] = None if y is None or ctx['age'] is None else (y - ctx['age']) <= alt['bornle']
    if 'gapmax' in alt:
        d0, d1 = _date(race), _start_date(last)
        extra['gapmax'] = None if d0 is None or d1 is None else (d0 - d1).days <= alt['gapmax']
    if 'nar' in alt:
        extra['nar'] = True        # this module only runs on NAR cards
    st, v = bk.check(base, ctx)
    if st == 'NOT_LOCAL':
        return st, v
    v = {**v, **extra}
    if any(x is False for x in v.values()):
        return 'NO', v
    return ('UNKNOWN' if any(x is None for x in v.values()) else 'MATCH'), v


def _side(alts, ctx, race):
    rows = [(i, *check(a, ctx, race)) for i, a in enumerate(alts or [])]
    return {'match': [i for i, s, _ in rows if s == 'MATCH'], 'unknown': [i for i, s, _ in rows if s == 'UNKNOWN']}


def evaluate(runner, race):
    ctx = bk.context(runner, race)
    out = {}
    e = bk.table().get(bk._n(runner.get('sire')))
    if e:
        e2, applied = corrected_entry(e)
        if applied:
            base = {s: _side(e.get(s), ctx, race) for s in ('buy', 'caution')}
            corr = {s: _side(e2.get(s), ctx, race) for s in ('buy', 'caution')}
            out['sire'] = {'entry_no': e['no'], 'name': e['name'], 'patches': applied,
                           'base_buy': bool(base['buy']['match']), 'base_caution': bool(base['caution']['match']),
                           'corr_buy': bool(corr['buy']['match']), 'corr_caution': bool(corr['caution']['match']),
                           'corr_unknown_buy': corr['buy']['unknown'], 'corr_unknown_caution': corr['caution']['unknown']}
    d = DAMSIRE.get(bk._n(runner.get('damsire')))
    if d:
        c = _side(d['caution'], ctx, race)
        out['damsire'] = {'entry_no': d['no'], 'name': runner.get('damsire'), 'patches': ['C7'],
                          'caution': bool(c['match']), 'unknown': c['unknown']}
    if not out:
        return None
    s = out.get('sire') or {}
    out['changed'] = bool(s and (s['base_buy'] != s['corr_buy'] or s['base_caution'] != s['corr_caution'])) \
        or bool(out.get('damsire', {}).get('caution'))
    return out


def race_evidence(race, runners):
    by = {}
    for x in runners:
        ev = evaluate(x, race)
        if ev:
            by[str(x['horse_no'])] = ev
    return {'profile': PROFILE, 'source': SRC, 'production_effect': 'NONE (shadow; v2 and ext_model unchanged)',
            'patches': {p[0]: p[6] for p in PATCHES} | {'C7': DAMSIRE['ディープインパクト']['reason']},
            'runners': len(runners), 'evaluated': len(by),
            'changed': sorted((k for k, v in by.items() if v['changed']), key=lambda k: int(k) if k.isdigit() else 0),
            'by_horse': by}

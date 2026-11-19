"""LOCAL popularity-structure evidence from historical results (shadow only; never consumed by ranking, tickets,
KRS, MEC or capital). Class: HISTORICAL_BACKFILL_LEARNING (not Forward OOS).

Source: Owner Drive library「地方競馬攻略一般」(YouTube 10本の読み物版, read 2026-11-19):
  ch.10 (セブンズTV) 南関東以外の地方では 1番人気頭固定・2/3番人気への三連単2点 (1->2->3, 1->3->2) が
        「体感で」よく決まる。根拠は投稿者の体感と盛岡7Rの1例だけ (UNVERIFIED)。ch.3 は逆に三連系を勧めない。
  ch.1  同じ厩舎の複数頭出しは、少なくとも1頭が出走手当目当て (ヤラズ) の可能性 (UNVERIFIED)。
This module only tallies what the official result already contains, per venue (never pooled), so both claims
can be checked on our own data:
  FAV_HEAD_TRI2  flat 100 yen x 2 tickets per race, hits / return / ROI, with Wilson 95 % on the hit rate.
  STABLE_MULTI   starts whose trainer has 2+ runners in the race, split into the stable's best-popularity
                 runner and the others, vs single-entry starts (top3 rate and market-adjusted A/E).
Popularity is the FINAL (post-race) value of the result page; at prediction time it must be the pre-race
odds snapshot (LEAK_NOTE). Anything that cannot be read (tied / missing popularity, a scratched top-3
favourite, no trifecta table) is skipped and counted, never guessed.
"""
import json
from collections import defaultdict
from pathlib import Path

from runtime.local_autopilot import hist_stats as hs

PROFILE = 'KM-LOCAL-POP-STRUCTURES-EVIDENCE-v1.0-20261119'
CLASS = hs.CLASS
NANKAN = ('URW', 'FNB', 'OHI', 'KAW')
LEAK_NOTE = hs.LEAK_NOTE


def fav_tri2(rec):
    """Raw backfill record -> one race row, or (None, reason)."""
    res = rec.get('result') or {}
    order = res.get('order') or []
    tri = (res.get('payouts') or {}).get('TRIFECTA') or {}
    gone = set(res.get('non_starters') or [])
    pops = {}
    for c in rec.get('rows') or []:
        no, p = hs._int(c.get('number')), hs._int(c.get('rank'))
        if no and p and no not in gone:
            if p in pops:
                return None, 'TIED_POPULARITY'
            pops[p] = no
    if not all(k in pops for k in (1, 2, 3)):
        return None, 'POPULARITY_MISSING'
    if len(order) < 3:
        return None, 'NO_ORDER'
    if not tri:
        return None, 'NO_TRIFECTA_TABLE'
    a, b, c = pops[1], pops[2], pops[3]
    tickets = [(a, b, c), (a, c, b)]
    hit = tuple(order[:3]) in tickets
    pay = tri.get('-'.join(map(str, order[:3])), 0) if hit else 0
    win = (res.get('payouts') or {}).get('WIN') or {}
    return {'race_id': f"{rec['venue_id']}_{rec['race_date'].replace('-', '')}_R{int(rec['race_no']):02d}",
            'venue': rec['venue_id'], 'date': rec['race_date'], 'invest': 200, 'return': pay, 'hit': hit,
            'fav_won': order[0] == a, 'top3_is_pop123': set(order[:3]) == {a, b, c},
            'fav_win_pay': win.get(str(a)) if order[0] == a else None,
            'field': len([x for x in rec.get('rows') or [] if hs._int(x.get('number')) not in gone])}, None


def summarize_tri2(rows):
    def agg(rs):
        n, h = len(rs), sum(r['hit'] for r in rs)
        inv, ret = sum(r['invest'] for r in rs), sum(r['return'] for r in rs)
        top = max((r['return'] for r in rs), default=0)
        return {'races': n, 'hits': h, 'hit_rate': round(h / n, 4) if n else None, 'hit_ci95': hs.wilson(h, n),
                'fav_win_rate': round(sum(r['fav_won'] for r in rs) / n, 4) if n else None,
                'pop123_top3_rate': round(sum(r['top3_is_pop123'] for r in rs) / n, 4) if n else None,
                'invest': inv, 'return': ret, 'roi': round(ret / inv, 3) if inv else None,
                'roi_ex_largest': round((ret - top) / inv, 3) if inv else None, 'small_sample': n < hs.MIN_N}
    by = defaultdict(list)
    for r in rows:
        by[r['venue']].append(r)
    return {'by_venue': {v: agg(rs) for v, rs in sorted(by.items())},
            'NANKAN': agg([r for r in rows if r['venue'] in NANKAN]),
            'OTHER_LOCAL': agg([r for r in rows if r['venue'] not in NANKAN and r['venue'] != 'OBI'])}


def stable_labels(race):
    """hist_stats race -> {horse no: SINGLE | MULTI_BEST | MULTI_OTHER | UNKNOWN} (pre-race facts only:
    trainer and popularity; the best is the stable's lowest popularity number)."""
    ran = [x for x in race['runners'] if x['status'] != 'SCRATCH' and x.get('no')]
    groups = defaultdict(list)
    for x in ran:
        if x.get('trainer'):
            groups[x['trainer']].append(x)
    out = {}
    for x in ran:
        g = groups.get(x.get('trainer')) if x.get('trainer') else None
        if not g:
            out[x['no']] = 'UNKNOWN'
        elif len(g) == 1:
            out[x['no']] = 'SINGLE'
        elif not all(y.get('pop') for y in g):
            out[x['no']] = 'UNKNOWN'
        else:
            out[x['no']] = 'MULTI_BEST' if x['pop'] == min(y['pop'] for y in g) else 'MULTI_OTHER'
    return out


def summarize_stable(races):
    rows = hs.starts(races)
    exp = hs.expected_top3(rows)
    lab = {}
    for rid, race in races.items():
        for no, l in stable_labels(race).items():
            lab[(rid, no)] = l
    by = defaultdict(list)
    for r in rows:
        by[(r['venue'], lab.get((r['race_id'], r['no']), 'UNKNOWN'))].append(r)
    period = hs._period(rows)
    return {f'{v}|{l}': hs.cell(rs, 'STABLE_MULTI', {'venue': v, 'label': l}, exp, 'RAKUTEN_RESULT_PAGE', period)
            for (v, l), rs in sorted(by.items())}


def build(root):
    root = Path(root)
    tri, skipped, races = [], defaultdict(int), {}
    for p in sorted((root / 'backfill' / 'results').glob('*/*.json')):
        try:
            rec = json.loads(p.read_text())
        except ValueError:
            skipped['UNREADABLE'] += 1
            continue
        if rec.get('venue_id') == 'OBI':
            skipped['BANEI_EXCLUDED'] += 1
            continue
        row, why = fav_tri2(rec)
        if row:
            tri.append(row)
        else:
            skipped[why] += 1
        try:
            races.update(hs.from_rakuten_backfill(rec))
        except (KeyError, TypeError, ValueError):
            skipped['ADAPTER_FAIL'] += 1
    if not tri and not races:
        return None
    return {'profile': PROFILE, 'class': CLASS, 'leak_note': LEAK_NOTE,
            'source': 'Drive「地方競馬攻略一般」ch.10 / ch.1 (UNVERIFIED claims); data = Rakuten result pages',
            'period': [min(r['date'] for r in tri), max(r['date'] for r in tri)] if tri else None,
            'skipped': dict(skipped), 'fav_head_tri2': summarize_tri2(tri),
            'stable_multi': summarize_stable(races) if races else {}}


def md(st):
    L = [f"# Popularity-structure evidence ({st['profile']})", '', f"- class: {st['class']}", f"- {st['leak_note']}",
         f"- period: {st['period']}", f"- skipped: {st['skipped']}", '',
         '## 1番人気頭固定 三連単2点 (1->2->3, 1->3->2), 100円均等', '',
         '| 区分 | R | 的中 | 的中率 (95%) | 1人気勝率 | 1-3人気で3着内独占 | ROI | 最大払戻除外ROI |', '|---|---|---|---|---|---|---|---|']
    t = st['fav_head_tri2']
    for k, a in [('NANKAN', t['NANKAN']), ('OTHER_LOCAL', t['OTHER_LOCAL'])] + sorted(t['by_venue'].items()):
        L.append(f"| {k}{' (n<30)' if a['small_sample'] else ''} | {a['races']} | {a['hits']} | {a['hit_rate']} {a['hit_ci95']} | "
                 f"{a['fav_win_rate']} | {a['pop123_top3_rate']} | {a['roi']} | {a['roi_ex_largest']} |")
    L += ['', '## 同厩舎の複数頭出し (STABLE_MULTI)', '', '| 場|区分 | 出走 | 3着内率 | A/E(3着内) | 単ROI | 複ROI |', '|---|---|---|---|---|---|']
    for k, c in st['stable_multi'].items():
        L.append(f"| {k}{' (n<30)' if c['small_sample'] else ''} | {c['starts']} | {c['top3']} | {c.get('ae_top3')} | "
                 f"{c['roi_win']} | {c['roi_place']} |")
    return '\n'.join(L) + '\n'


def write(root):
    st = build(root)
    if not st:
        return None
    Path(root, 'pop_structures.json').write_text(json.dumps(st, ensure_ascii=False))
    Path(root, 'pop_structures.md').write_text(md(st))
    return st


if __name__ == '__main__':
    import sys
    s = write(sys.argv[1] if len(sys.argv) > 1 else 'runtime/local_autopilot/output')
    print(md(s) if s else 'NO_DATA')

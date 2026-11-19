"""Vertical tree rendering of tickets per the Owner's 買い目表記規格（標準ツリーフォーマット）.

Rules applied: Arabic numerals (no ①), vertical ├─ / └─ trees, no horizontal 4→2,6 in the ticket body,
ワイド/馬連 = 軸 + 相手, 馬単 = 1着/2着, 三連複 = 軸/相手 or 1列目/2列目/3列目, 三連単 = 1着/2着/3着,
real point counts (duplicates and same-horse combinations removed), PAPER / 未較正 / EV算出不可 footer.
Display order keeps the prediction's order (first appearance), never a plain numeric sort.
A set that is not an exact formation is shown grouped by its first horse (1着 / 1列目), still vertical.
"""
from itertools import combinations, product

ORDERED = {'馬単', '三連単'}
SIZE = {'単勝': 1, '複勝': 1, 'ワイド': 2, '馬連': 2, '馬単': 2, '三連複': 3, '三連単': 3}
COL = {'馬単': ('1着', '2着'), '三連単': ('1着', '2着', '3着'), '三連複': ('1列目', '2列目', '3列目')}


def parse(kind, b):
    """'1-6 / 1-5' or '4→2,6→1,2,7' → list of combos (tuples, ordered for 馬単/三連単, else sorted sets)."""
    b = str(b)
    if '→' in b:
        cols = [[int(x) for x in seg.split(',') if x.strip()] for seg in b.split('→')]
        raw = [c for c in product(*cols) if len(set(c)) == len(c)]
    else:
        raw = [tuple(int(x) for x in c.split('-') if x.strip()) for c in b.split('/') if c.strip()]
    return norm(kind, raw)


def norm(kind, raw):
    out, seen = [], set()
    for c in raw:
        c = tuple(int(x) for x in c)
        if len(set(c)) != len(c):
            continue
        key = c if kind in ORDERED else tuple(sorted(c))
        if key not in seen:
            seen.add(key)
            out.append(c if kind in ORDERED else c)
    return out


def _order(combos):
    seen = []
    for c in combos:
        for h in c:
            if h not in seen:
                seen.append(h)
    return seen


def _branch(items, indent=''):
    return [f"{indent}{'└─' if i == len(items) - 1 else '├─'} {x}" for i, x in enumerate(items)]


def _expand(kind, cols):
    combos = [c for c in product(*cols) if len(set(c)) == len(c)]
    return {c for c in combos} if kind in ORDERED else {tuple(sorted(c)) for c in combos}


def _key(kind, combos):
    return {c for c in combos} if kind in ORDERED else {tuple(sorted(c)) for c in combos}


def _formation(kind, combos):
    """Smallest column formation whose expansion is exactly the set, else None."""
    target = _key(kind, combos)
    hs = _order(combos)
    n = SIZE[kind]
    if kind in ORDERED:
        cols = [list(dict.fromkeys(c[i] for c in combos)) for i in range(n)]
        return cols if _expand(kind, cols) == target else None
    best = None
    for a in range(1, min(2, len(hs)) + 1):
        for A in combinations(hs, a):
            if n == 2:
                cols = [list(A), hs]
                if _expand(kind, cols) == target:
                    return cols
                continue
            for b in range(1, min(4, len(hs)) + 1):
                for B in combinations(hs, b):
                    cols = [list(A), list(B), hs]
                    if _expand(kind, cols) == target:
                        size = len(A) + len(B)
                        if best is None or size < best[0]:
                            best = (size, cols)
    return best[1] if best else None


def render(kind, combos, label=None):
    """Lines of one bet type (title + tree)."""
    combos = norm(kind, combos)
    n = SIZE.get(kind, len(combos[0]) if combos else 1)
    title = kind + (f"（{label}）" if label else '')
    if not combos:
        return [title, '└─ なし'], 0
    if n == 1:
        return [title] + _branch([c[0] for c in combos]), len(combos)
    cols = _formation(kind, combos)
    pts = len(combos)
    if cols is not None:
        if kind in ('ワイド', '馬連'):
            axis, rest = cols[0], [h for h in cols[1] if h not in cols[0]] if len(cols[0]) == 1 else cols[1]
            sub = '' if len(cols[0]) == 1 else 'フォーメーション'
            return [kind + (f"（{label or sub}）" if (label or sub) else ''), '軸'] + _branch(axis) + ['相手'] + _branch(rest), pts
        if kind == '三連複' and len(cols[0]) + len(cols[1]) <= 3 and set(cols[1]) <= set(cols[0]) | set(cols[1]):
            axis = list(dict.fromkeys(cols[0] + (cols[1] if len(cols[1]) == 1 and cols[1][0] not in cols[0] else [])))
            full = {tuple(sorted(c)) for c in combinations(axis + [h for h in cols[2] if h not in axis], 3)
                    if set(axis) <= set(c)}
            if full == _key(kind, combos):
                rest = [h for h in cols[2] if h not in axis]
                return [f"三連複（{label or f'{len(axis)}頭軸'}）", '軸'] + _branch(axis) + ['相手'] + _branch(rest), pts
        sub = label or ('1着固定' if kind in ORDERED and len(cols[0]) == 1 else '頭入替' if kind in ORDERED else '')
        L = [kind + (f"（{sub}）" if sub else '')]
        for name, col in zip(COL[kind], cols):
            L += [name] + _branch(col)
        return L, pts
    # not a formation: group by the first horse (then the second for 3-horse bets), still vertical
    L = [title]
    heads = list(dict.fromkeys(c[0] for c in combos))
    lab = COL.get(kind, ('軸', '相手', '相手'))
    for i, h in enumerate(heads):
        last = i == len(heads) - 1
        L.append(f"{'└─' if last else '├─'} {lab[0]} {h}")
        pad = '   ' if last else '│  '
        grp = [c for c in combos if c[0] == h]
        if n == 2:
            L += _branch([c[1] for c in grp], pad)
            continue
        seconds = list(dict.fromkeys(c[1] for c in grp))
        for j, s in enumerate(seconds):
            l2 = j == len(seconds) - 1
            L.append(f"{pad}{'└─' if l2 else '├─'} {lab[1]} {s}")
            L += _branch([c[2] for c in grp if c[1] == s], pad + ('   ' if l2 else '│  '))
    return L, pts


def block(tickets, unit=100, paper=True):
    """tickets: [(kind, combos, label)] → code-block text with point/stake footer."""
    L, counts = [], []
    for kind, combos, label in tickets:
        lines, pts = render(kind, combos, label)
        L += lines
        counts.append((kind + (f"（{label}）" if label else ''), pts))
    total = sum(p for _, p in counts)
    L.append('点数')
    L += _branch([f"{k}　{p}点" for k, p in counts] + [f"合計　{total}点（{total * unit:,}円）"])
    if paper:
        L += ['購入判定', '└─ ペーパー', '確率状態', '└─ 未較正', 'EV', '└─ 算出不可']
    return '\n'.join(L), total


# ------------------------------------------------------------------ round-trip (KAW v2.4 第368条, evidence only)
_SECTIONS = {'軸', '相手', '1着', '2着', '3着', '1列目', '2列目', '3列目'}


def _depth_body(ln):
    """'│  ├─ 6' → (1, '6'); '└─ 1着 4' → (0, '1着 4')."""
    for i, ch in enumerate(ln):
        if ch in '├└':
            return i // 3, ln[i + 2:].strip()
    return None, ln.strip()


def reflatten(text):
    """Parse a block()/render() tree back into [(kind, set_of_combos)] in display order, and the footer total.
    Used only to check Canonical → Tree → Reflatten identity; never builds or changes tickets."""
    out, cur, total = [], None, None
    lines = text.split('\n')
    for k, ln in enumerate(lines):
        s = ln.strip()
        if s == '点数':
            for f in lines[k + 1:]:
                d, b = _depth_body(f)
                if b.startswith('合計'):
                    total = int(b.split('　')[1].split('点')[0])
            break
        d, body = _depth_body(ln)
        if d is None:
            base = s.split('（')[0]
            if base in SIZE:
                cur = {'kind': base, 'cols': {}, 'sec': None, 'groups': [], 'items': []}
                out.append(cur)
            elif base in _SECTIONS and cur is not None:
                cur['sec'] = base
                cur['cols'][base] = []
            continue
        if cur is None or body == 'なし':
            continue
        parts = body.split()
        if len(parts) == 2 and parts[0] in _SECTIONS:            # group header (non-formation layout)
            if d == 0:
                cur['groups'].append([int(parts[1]), []])
            else:
                cur['groups'][-1][1].append([int(parts[1]), []])
            continue
        h = int(body)
        if cur['groups']:
            g = cur['groups'][-1]
            if SIZE[cur['kind']] == 2:
                g[1].append(h)
            else:
                g[1][-1][1].append(h)
        elif cur['sec']:
            cur['cols'][cur['sec']].append(h)
        else:
            cur['items'].append(h)
    res = []
    for c in out:
        kind, n = c['kind'], SIZE[c['kind']]
        if c['groups']:
            raw = ([(a, b) for a, bs in c['groups'] for b in bs] if n == 2 else
                   [(a, b, t) for a, ss in c['groups'] for b, ts in ss for t in ts])
            combos = _key(kind, norm(kind, raw))
        elif '軸' in c['cols']:
            axis, rest = c['cols']['軸'], c['cols'].get('相手', [])
            if kind == '三連複':
                combos = {tuple(sorted(x)) for x in combinations(list(dict.fromkeys(axis + rest)), 3) if set(axis) <= set(x)}
            else:
                combos = _expand(kind, [axis, rest])
        elif c['cols']:
            combos = _expand(kind, [c['cols'].get(name, []) for name in COL[kind]])
        else:
            combos = {(h,) for h in c['items']}
        res.append((kind, combos))
    return res, total


def roundtrip(tickets, unit=100):
    """Canonical tickets → block() tree → reflatten → compare (bet type, full combo set, point total).
    Returns {'ok', 'mismatches'}; a mismatch is a display defect to report, never a reason to add or drop tickets."""
    text, total = block(tickets, unit=unit, paper=False)
    back, back_total = reflatten(text)
    want = [(kind, _key(kind, norm(kind, combos)) if SIZE.get(kind, 1) > 1 else {tuple(c) for c in norm(kind, combos)})
            for kind, combos, _ in tickets]
    mm = []
    if len(back) != len(want):
        mm.append({'what': 'bet_type_count', 'canonical': len(want), 'tree': len(back)})
    for (k1, s1), (k2, s2) in zip(want, back):
        if k1 != k2 or s1 != s2:
            mm.append({'what': 'combos', 'kind': k1, 'tree_kind': k2,
                       'missing_in_tree': sorted(s1 - s2), 'extra_in_tree': sorted(s2 - s1)})
    if back_total != total:
        mm.append({'what': 'point_total', 'canonical': total, 'tree': back_total})
    return {'ok': not mm, 'mismatches': mm}

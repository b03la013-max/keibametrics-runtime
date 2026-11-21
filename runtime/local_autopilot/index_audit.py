"""P0 index ledger + role-wise predictive audit of the 29 formal indices (ChatGPT 11/21 20:17 review; Owner
「どうしますか？」-> Claude 20:2x plan, P0). Evidence only: nothing here changes Production.

For every settled formal race (effective revision, Full29 as signed) and every index:
  * within-race AUC for 1st / top-2 / top-3 (probability that a random placed horse has a higher index value
    than a random unplaced horse in the same race; 0.5 = no information, ties count 0.5)
  * top-index hit rates: the index's best horse won / finished top 3
  * how often the index was constant across the field (neutral / no information)
and, per index, the evidence level of its formula (registry ledger):
  INITIAL_DESIGN (fixed weights, never fitted) / EXTERNAL_MEASURED (filled by ext_model from NAR A/E) /
  FORWARD_COMPARED (has a pre-registered forward comparison).
"""
import json
from collections import defaultdict
from pathlib import Path

PROFILE = 'KM-LOCAL-INDEX-AUDIT-v1.0-20261121'
EXTERNAL = {'BVIg-L', 'JTI-L', 'CSI-L', 'BWI-L', 'DCR', 'NCI', 'CCI', 'TRI'}   # slots filled since EXT v2.0
FORWARD = {'BVIg-L': 'C21 (BVI-L-R2 tertile)', 'AKI': 'C11/C12/C25', 'ZAI-WIN': 'C17 (ZAI-PLACE for P2)'}


def _j(p):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return None


def races(root, days=None):
    out = []
    for dd in sorted(Path(root).glob('20*-*-*')):
        if days and dd.name not in days:
            continue
        for f in sorted((dd / 'formal').glob('*.full29.json')):
            key = f.name.split('.')[0]
            d2 = dd / 'formal' / 'rev2'
            full = _j(d2 / f.name) or _j(f)
            res = _j(d2 / f'{key}.result.json') or _j(dd / 'formal' / f'{key}.result.json') or _j(dd / f'{key}.result.json')
            order = [int(x) for x in ((res or {}).get('order') or [])[:3]]
            if not full or len(order) < 3:
                continue
            idx = {int(r['no']): r['indices'] for r in full.get('runners') or []}
            if len(idx) >= 5:
                out.append({'day': dd.name, 'race': key, 'order': order, 'idx': idx})
    return out


def auc(vals, pos):
    p = [vals[h] for h in vals if h in pos]
    n = [vals[h] for h in vals if h not in pos]
    if not p or not n:
        return None
    s = sum(1.0 if a > b else 0.5 if a == b else 0.0 for a in p for b in n)
    return s / (len(p) * len(n))


def audit(rows):
    names = sorted({k for r in rows for v in r['idx'].values() for k, x in v.items() if isinstance(x, (int, float))})
    acc = defaultdict(lambda: defaultdict(list))
    for r in rows:
        for name in names:
            vals = {h: v.get(name) for h, v in r['idx'].items() if isinstance(v.get(name), (int, float))}
            if len(vals) < 5:
                continue
            a = acc[name]
            if len(set(vals.values())) == 1:
                a['constant'].append(1)
                continue
            a['constant'].append(0)
            for tag, pos in (('win', set(r['order'][:1])), ('top2', set(r['order'][:2])), ('top3', set(r['order'][:3]))):
                x = auc(vals, pos)
                if x is not None:
                    a[tag].append(x)
            best = max(vals, key=lambda h: (vals[h], -h))
            a['best_win'].append(best == r['order'][0])
            a['best_top3'].append(best in r['order'])
    mean = lambda v: round(sum(v) / len(v), 3) if v else None
    out = {}
    for name in names:
        a = acc[name]
        out[name] = {'races': len(a['constant']), 'constant_rate': mean(a['constant']),
                     'auc_win': mean(a['win']), 'auc_top2': mean(a['top2']), 'auc_top3': mean(a['top3']),
                     'best_win_rate': mean(a['best_win']), 'best_top3_rate': mean(a['best_top3']),
                     'evidence': ('FORWARD_COMPARED: ' + FORWARD[name]) if name in FORWARD else
                                 'EXTERNAL_MEASURED (from 2026-11-22) + INITIAL_DESIGN weights' if name in EXTERNAL else
                                 'INITIAL_DESIGN (weights never fitted)'}
    return out


def md(out, n):
    L = [f'# 29指数の台帳と役割別の効き目（P0・証拠のみ）', '',
         f'対象：正式予想 {n}R（署名済み29指数の有効版、結果確定）。AUC＝同じレースで「来た馬」が「来なかった馬」より高い値を持つ確率（0.5＝情報なし）。', '',
         '| 指数 | 全頭同値の率 | AUC 1着 | AUC 2着内 | AUC 3着内 | 最上位馬の勝率 | 最上位馬の3着内率 | 式の根拠 |', '|---|---|---|---|---|---|---|---|']
    for k, v in sorted(out.items(), key=lambda kv: -(kv[1]['auc_top3'] or 0)):
        L.append(f"| {k} | {v['constant_rate']} | {v['auc_win']} | {v['auc_top2']} | {v['auc_top3']} | "
                 f"{v['best_win_rate']} | {v['best_top3_rate']} | {v['evidence']} |")
    return '\n'.join(L) + '\n'


def write(root):
    rs = races(root)
    out = audit(rs)
    doc = {'profile': PROFILE, 'races': len(rs), 'indices': out, 'production_change': 'NONE (evidence only)'}
    (Path(root) / 'index_audit.json').write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n')
    (Path(root) / 'index_audit.md').write_text(md(out, len(rs)))
    return doc

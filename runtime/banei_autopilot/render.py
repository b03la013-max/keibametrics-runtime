"""Delivery text: marks + tree tickets per 買い目表記規格 (reuses the LOCAL tree renderer)."""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'local_autopilot'))
import ticket_tree  # noqa: E402

MARK_ORDER = ['◎', '○', '▲', '△', '穴']


def render(race_label, ev, tk, paper=False):
    L = [f"{race_label}　ケイバメトリクスばんえい v4.0-BAN", '']
    L.append('印')
    items = sorted(ev['marks'].items(), key=lambda kv: (MARK_ORDER.index(kv[1]) if kv[1] in MARK_ORDER else 9, kv[0]))
    L += ticket_tree._branch([f"{m} {n}" for n, m in items])
    L += ['F3S', '└─ ' + '-'.join(str(x) for x in ev['f3s'])]
    if ev['s3h']:
        L += ['S3H', '└─ ' + '-'.join(str(x) for x in ev['s3h'])]
    L += ['AKI', f"└─ {ev['aki']}", '券面の型', f"└─ {tk['shape']}", '']
    tickets = [('三連複', tk['trio'], None)]
    if tk['exact']:
        tickets.append(('三連単', tk['exact'], None))
    body, total = ticket_tree.block(tickets, unit=100, paper=paper)
    L.append(body)
    L += ['', f"区分　{tk['formality']}　（ZAI・AKI・ASIは未較正。確率・EVではありません）"]
    return '\n'.join(L), total

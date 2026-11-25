import json

from runtime.local_autopilot import index_health as ih


def _race(root, day, key, order, vals):
    d = root / day
    (d / 'formal').mkdir(parents=True, exist_ok=True)
    (d / f'{key}.result.json').write_text(json.dumps({'order': order}))
    (d / 'formal' / f'{key}.full29.json').write_text(json.dumps({'runners': [
        {'no': h, 'indices': v} for h, v in vals.items()]}))
    (d / 'formal' / f'{key}.summary.json').write_text(json.dumps({'ranking': [str(h) for h in order]}))


def test_good_reversed_and_weekly(tmp_path):
    for i in range(30):
        order = [(i + j) % 8 + 1 for j in range(8)]
        vals = {h: {'HPI-L': 100 - 10 * order.index(h), 'CSI-L': 10 * order.index(h) + (i % 3), 'TRI': 50.0,
                    'RSI': 10 * order.index(h)} for h in order}
        _race(tmp_path, f'2026-11-{16 + i % 7:02d}', f'OHI_{i:02d}', order, vals)
    rep = ih.evaluate(tmp_path)
    x = rep['indices']
    assert rep['races'] == 30 and x['HPI-L']['auc_top3'] == 1.0 and not x['HPI-L']['flags']
    assert 'REVERSED' in x['CSI-L']['flags'] and x['TRI']['neutral_share'] == 1.0
    assert x['RSI']['kind'] == 'RISK' and 'REVERSED' not in x['RSI']['flags']
    assert ih.weekly(tmp_path, '2026-11-23') and ih.weekly(tmp_path, '2026-11-25') is None   # same ISO week
    assert '逆に働いている指数' in ih.md(rep)

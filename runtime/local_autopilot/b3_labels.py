"""B3 candidate pattern labels (Drive reading bundle B3, due 2026-11-28; first part 2026-11-25).

Pre-registered here BEFORE any measurement; each label becomes its OWN measured component in ext_model
(cand_labels -> CAND_COMPONENTS), outside PAT, with weight 0.0 in ext_connect.DEFAULT_BETA. Only the weekly
hold-out refit (Owner 2026-11-21 13:32 EXT connection) can give one a weight, and only if the later hold-out
weeks improve. The documents decide WHICH label a horse carries; the NAR data decide how strong it is.

  INTV  出走間隔の帯 <=14 / 15-35 / 36-90 / 91+ 日
        (Drive: 園田 中2週以内 6.2% vs 5週〜3か月 12.7%, YouTube 主張・未検証)
  BWSZ  馬体重の絶対値の帯 x 性別（牝 / 牡セ）: <440 / 440-479 / 480-539 / 540+
        (Drive: 540kg以上 13.9〜14.9% vs 440kg未満 3.6〜6.4%, 牝 6.1% vs 牡せん 9.9%, 主張・未検証)
  BWPCT 前走比の増減率（%）: <=-4 / -4..-2 / -2..2 / 2..4 / >=4  (馬体重の見方: kg でなく率で見る)
  SHFR  距離短縮 x 先行経験（直近3走のどれかで初角が前1/3）: FRONT / NOFRONT（短縮のときだけ）
        (Drive 要検証1: 「前走先行経験あり×距離短縮」)
  FAVRST 上位人気（1・2番人気）の間隔が普段と違う: USUAL / LONGER / SHORTER（過去の間隔の中央値比）
        (Drive: 危険な人気馬の細目「短期休み明け 15〜35日で普段より間隔が空いた」)
"""
from __future__ import annotations

import statistics
from datetime import date

PREREG = {'registered': '2026-11-25', 'bundle': 'B3', 'labels': ['INTV', 'BWSZ', 'BWPCT', 'SHFR', 'FAVRST'],
          'rule': 'weight 0.0; adopted only via ext_model.fit_weights hold-out improvement (no manual weights)'}
COMPONENTS = {'INTV': 'ITV', 'BWSZ': 'BWS', 'BWPCT': 'BWP', 'SHFR': 'SHF', 'FAVRST': 'FRS'}


def _days(a, b):
    try:
        return (date.fromisoformat(str(a)) - date.fromisoformat(str(b))).days
    except (TypeError, ValueError):
        return None


def interval_band(days):
    if days is None or days < 0:
        return None
    return '<=14' if days <= 14 else '15-35' if days <= 35 else '36-90' if days <= 90 else '91+'


def bw_size_band(bw):
    if not bw:
        return None
    return '<440' if bw < 440 else '440-479' if bw < 480 else '480-539' if bw < 540 else '540+'


def bw_pct_band(cur_bw, last_bw):
    if not cur_bw or not last_bw:
        return None
    p = 100.0 * (cur_bw - last_bw) / last_bw
    return '<=-4' if p <= -4 else '-4..-2' if p < -2 else '-2..2' if p <= 2 else '2..4' if p < 4 else '>=4'


def sex_group(sex):
    s = str(sex or '')[:1]
    return 'F' if s == '牝' else 'MG' if s in ('牡', 'セ', 'せ', '騸') else None


def labels(cur, hist):
    """cur / hist: the same dicts as ext_model.labels (hist oldest first). -> [(name, value)]"""
    if not hist:
        return []
    out = []
    last = hist[-1]
    days = _days(cur.get('date'), last.get('date'))
    ib = interval_band(days)
    if ib:
        out.append(('INTV', ib))
    sz, sg = bw_size_band(cur.get('bw')), sex_group(cur.get('sex'))
    if sz and sg:
        out.append(('BWSZ', f'{sz}|{sg}'))
    pb = bw_pct_band(cur.get('bw'), last.get('bw'))
    if pb:
        out.append(('BWPCT', pb))
    if cur.get('distance') and last.get('distance') and cur['distance'] < last['distance']:
        ear = [p['early'] for p in hist[-3:] if p.get('early') is not None]
        if ear:
            out.append(('SHFR', 'FRONT' if min(ear) <= 0.33 else 'NOFRONT'))
    pop = cur.get('pop')
    if pop and pop <= 2 and days is not None and len(hist) >= 3:
        gaps = [g for g in (_days(hist[i]['date'], hist[i - 1]['date']) for i in range(1, len(hist))) if g and g > 0]
        if len(gaps) >= 2:
            med = statistics.median(gaps[-6:])
            out.append(('FAVRST', 'LONGER' if days >= 1.5 * med and days >= 15 else
                        'SHORTER' if days <= 0.6 * med else 'USUAL'))
    return out

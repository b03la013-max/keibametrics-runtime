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


# ---------------------------------------------------------------- B3 second part (pre-registered 2026-11-25 03時台)
"""
  LEADX   前走で逃げた（初角先頭）馬の今回: HABIT（直近5走の初角平均が前1/4）/ ONCE x 前走着順帯
          (Drive: 『前走逃げ→今回ハナを取れず番手』の着順。ext_model の LEAD=REPEAT は再逃げの常連だけで着順帯なし)
  SEASEX  季節（12-2/3-5/6-8/9-11月）x 性別（牝 / 牡セ） (YouTube #18・#19「夏は牝馬」、主張・未検証)
  REST2   休み明け2戦目（前走の前の間隔 91日以上・今回の間隔 56日以内）x 前走比の馬体重 UP/FLAT/DOWN（±2%）
          (Drive: 休み明け2戦目の増減注意・上積み、主張・未検証)
  FAVSLOW 1・2番人気 x 距離（1000m以下 SPRINT / OTHER）x 直近3走で初角が後ろ4割に入った回数 0/1/2+
          (Drive 要検証5「800/900m の出遅れ癖人気馬」、危険な人気馬の細目「前走までの出遅れ」)
  DEBUTX  初出走馬 x 性別 x 人気帯（1-2 / 3-5 / 6+）  (第374条 新馬の情報量区分の代わりに、初出走馬の
          市場の織り込みを人気帯ごとに実測する。生まれ月・兄姉成績は取得元が無く未接続)
"""
PREREG2 = {'registered': '2026-11-25T03', 'bundle': 'B3', 'labels': ['LEADX', 'SEASEX', 'REST2', 'FAVSLOW', 'DEBUTX'],
           'rule': 'weight 0.0; adopted only via ext_model.fit_weights hold-out improvement (no manual weights)'}
COMPONENTS2 = {'LEADX': 'LDX', 'SEASEX': 'SSX', 'REST2': 'RS2', 'FAVSLOW': 'FSL', 'DEBUTX': 'DBX'}


def season_of(d):
    try:
        m = int(str(d)[5:7])
    except (TypeError, ValueError):
        return None
    return 'WIN' if m in (12, 1, 2) else 'SPR' if m in (3, 4, 5) else 'SUM' if m in (6, 7, 8) else 'AUT'


def _fin(f):
    return 'NA' if not f else '1-3' if f <= 3 else '4-6' if f <= 6 else '7+'


def pop_band(pop):
    return None if not pop else '1-2' if pop <= 2 else '3-5' if pop <= 5 else '6+'


def labels2(cur, hist):
    """Second B3 part. cur / hist as in labels(). -> [(name, value)]"""
    out = []
    sg = sex_group(cur.get('sex'))
    se = season_of(cur.get('date'))
    if se and sg:
        out.append(('SEASEX', f'{se}|{sg}'))
    pop = cur.get('pop')
    if not hist:
        pb = pop_band(pop)
        if pb and sg:
            out.append(('DEBUTX', f'{sg}|{pb}'))
        return out
    last = hist[-1]
    lf = _fin(last.get('finish'))
    if last.get('early') is not None and last['early'] <= 0.0:
        ear = [p['early'] for p in hist[-5:] if p.get('early') is not None]
        habit = len(ear) >= 2 and sum(ear) / len(ear) <= 0.25
        out.append(('LEADX', f"{'HABIT' if habit else 'ONCE'}|{lf}"))
    if len(hist) >= 2:
        g_prev = _days(last.get('date'), hist[-2].get('date'))
        g_now = _days(cur.get('date'), last.get('date'))
        if g_prev is not None and g_prev >= 91 and g_now is not None and 0 < g_now <= 56:
            d = None
            if cur.get('bw') and last.get('bw'):
                p = 100.0 * (cur['bw'] - last['bw']) / last['bw']
                d = 'UP' if p > 2 else 'DOWN' if p < -2 else 'FLAT'
            out.append(('REST2', f"{d or 'NA'}|{lf}"))
    if pop and pop <= 2 and cur.get('distance'):
        k = sum(1 for p in hist[-3:] if p.get('early') is not None and p['early'] >= 0.6)
        out.append(('FAVSLOW', f"{'SPRINT' if cur['distance'] <= 1000 else 'OTHER'}|{'2+' if k >= 2 else k}"))
    return out


# ---------------------------------------------------------------- B3 third part (pre-registered 2026-11-25 06時台)
"""
  CLSFIN  クラスの「組」を含む格の移動 x 前走着順帯 x 同格以上での直近3走の最高着順
          格 = engine.class_level（A/B/C と数字、組は1つ下がるごとに -0.08）。組が括弧なし（'C2三'・'C3-10'・'C3 10組'）
          でも読む。移動 UP（今回の方が格上）/ SAME / DOWN、前走着順 1-3 / 4-6 / 7+、
          同格以上（前走以前3走のうち格が今回以上）の最高着順 1-3 / 4-6 / 7+ / NONE。
          (Drive: 地方競馬攻略一般 ch.2/6「過去3走の組×着順から実力クラスを出す」、n36。engine.class_level は組差 0.08
          だけで、組×着順の表は無かった)
  人気帯別の表（label_pop_table）: 候補ラベルの値ごとに 単勝人気帯（1-2 / 3-5 / 6+）別の 件数・3着内・期待・A/E を出す
          (Drive n259「勝率が高い≠回収率が高い」：ext_model は A/E を人気で補正するが、どの人気帯で効くかは出していなかった。
          払戻を持たないので回収率は未対応＝一部対応)
"""
import re as _re
import unicodedata as _ud

PREREG3 = {'registered': '2026-11-25T06', 'bundle': 'B3', 'labels': ['CLSFIN'],
           'rule': 'weight 0.0; adopted only via ext_model.fit_weights hold-out improvement (no manual weights)'}
COMPONENTS3 = {'CLSFIN': 'CLF'}
_KN = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}


def _kanji_num(s):
    if not s:
        return None
    if s.isdigit():
        return int(s)
    if s == '十':
        return 10
    if s.startswith('十'):
        return 10 + _KN.get(s[1:], 0)
    if '十' in s:
        a, b = s.split('十', 1)
        return _KN.get(a, 0) * 10 + (_KN.get(b, 0) if b else 0)
    return _KN.get(s)


def level_of(text):
    """Class level incl. 組 (higher = stronger). None when the text has no A/B/C class."""
    from runtime.local_autopilot import engine
    t = _ud.normalize('NFKC', str(text or ''))
    lv = engine.class_level(t)
    if lv is None:
        return None
    if _re.search(r'[\(（][一二三四五六七八九十]+[\)）]', t):
        return round(lv, 3)
    m = _re.search(r'[ABC]\s*[1-9]\s*(?:[-ー]\s*(\d{1,2})|([一二三四五六七八九十]+)|\s+(\d{1,2})組)', t)
    if m:
        g = _kanji_num(m[1] or m[2] or m[3])
        if g:
            lv -= 0.08 * (g - 1)
    return round(lv, 3)


def labels3(cur, hist):
    """Third B3 part. cur / hist carry 'lvl' (level_of of the race condition). -> [(name, value)]"""
    if not hist:
        return []
    c, last = cur.get('lvl'), hist[-1]
    p = last.get('lvl')
    if c is None or p is None:
        return []
    mv = 'UP' if c > p + 0.01 else 'DOWN' if c < p - 0.01 else 'SAME'
    best = [h.get('finish') for h in hist[-3:] if h.get('lvl') is not None and h['lvl'] >= c - 0.01 and h.get('finish')]
    return [('CLSFIN', f"{mv}|{_fin(last.get('finish'))}|{_fin(min(best)) if best else 'NONE'}")]


def label_pop_table(rows, exp, names=None):
    """Candidate label value x 単勝人気帯 -> {n, top3, exp, ae}. rows / exp as in ext_model.build (training rows and
    expectation()). Evidence only: used to see in which popularity band a label works (n259)."""
    out = {}
    for r in rows:
        e = exp.get((r['venue'], min(r['pop'], 10), r['fband']))
        pb = pop_band(r.get('pop'))
        if e is None or pb is None:
            continue
        for name, val in r.get('cand_labels') or []:
            if names and name not in names:
                continue
            d = out.setdefault(f'{name}={val}', {}).setdefault(pb, {'n': 0, 'top3': 0, 'exp': 0.0})
            d['n'] += 1
            d['top3'] += int(bool(r['top3']))
            d['exp'] += e
    for by in out.values():
        for d in by.values():
            d['exp'] = round(d['exp'], 3)
            d['ae'] = round(d['top3'] / d['exp'], 3) if d['exp'] else None
    return out


# ---------------------------------------------------------------- B3 fourth part (pre-registered 2026-11-25T09)
"""
  DEBINF  新馬・初出走馬を含むレースの「情報量区分」（第374条、n10）x その馬に過去走があるか x 人気帯
          区分は結果前に決まる：同じレースの出走馬のうち過去走のある馬の割合 0 → TIEBREAK_ONLY（全頭が初出走で
          事前の差は市場オッズのタイブレークだけ）/ 0超〜0.5未満 → PARTIAL（一部だけ比較できる）/
          0.5以上 → EVIDENCE（過去走のある馬が多数で比較できる）。初出走馬が1頭もいないレースには付けない。
          値 = '<TB|PC|ED>|<H|N>|<人気帯>'（H = 過去走あり、N = 初出走）。
          (Drive: 精度スコアリング規格 第374条 EVIDENCE_DISCRIMINATIVE / PARTIAL_COMPARABLE /
          TIEBREAK_ONLY_NONINFORMATIVE。engine.py は全頭 UNKNOWN の同点を市場オッズで割るが区分ラベルが無かった)
          cur に 'field_hist_share'（過去走のある出走馬の割合）と 'field_has_debut'（初出走馬がいるか）が要る。
"""
PREREG4 = {'registered': '2026-11-25T09', 'bundle': 'B3', 'labels': ['DEBINF'],
           'rule': 'weight 0.0; adopted only via ext_model.fit_weights hold-out improvement (no manual weights)'}
COMPONENTS4 = {'DEBINF': 'DBI'}


def info_class(share):
    if share is None:
        return None
    return 'TB' if share <= 0.0 else 'PC' if share < 0.5 else 'ED'


def field_info(n_with_hist, n_runners):
    """-> (field_hist_share, field_has_debut) for a race; (None, False) when the field is empty."""
    if not n_runners:
        return None, False
    return round(n_with_hist / n_runners, 3), n_with_hist < n_runners


def labels4(cur, hist):
    """Fourth B3 part. -> [(name, value)]"""
    if not cur.get('field_has_debut'):
        return []
    ic, pb = info_class(cur.get('field_hist_share')), pop_band(cur.get('pop'))
    if not ic or not pb:
        return []
    return [('DEBINF', f"{ic}|{'H' if hist else 'N'}|{pb}")]


"""B3 fifth part (2026-11-25 15): BMONTH（生まれ月 × 新馬戦/2歳戦）

  BMONTH  2歳馬（齢=2）のレースだけ。生まれ月の帯 M1_3（1〜3月）/ M4_5（4〜5月）/ M6P（6月以降）
          × レース区分 SHINBA（条件に「新馬」）/ 2YO（それ以外の2歳戦）× 人気帯。
          値 = '<SHINBA|2YO>|<M1_3|M4_5|M6P>|<人気帯>'。生年月日が無い馬・3歳以上には付けない。
          (Drive: YouTube『【完全攻略】新馬戦にこそお宝が眠っています』— 2歳戦の勝率 1月生まれ 11.3% → 6月以降 5.4%、
          複勝率 約1/3 → 約1/6、人気に織り込まれにくいとする主張・未検証、JRA の研究の出典は未確認。
          q313 の修正どおり新馬戦と2歳戦全体を別セルにし、人気帯で人気補正後の差を測る）
          生年月日は NAR 公式 CSV の horselist『生年月日』（hist_stats.from_nar_csv の horse_key に入っている）。
          楽天の出馬表には生年月日が無いので、当日の行では付かない（学習側の実測のみ。採用されても当日の値は中立）。
"""
PREREG5 = {'registered': '2026-11-25T15', 'bundle': 'B3', 'labels': ['BMONTH'],
           'rule': 'weight 0.0; adopted only via ext_model.fit_weights hold-out improvement (no manual weights)'}
COMPONENTS5 = {'BMONTH': 'BMO'}


def birth_month(birth):
    """'2024-03-15' / '2024/3/15' / '20240315' / 'name|2024/03/15' -> 3 (None when unreadable)."""
    import re
    s = str(birth or '')
    if '|' in s:
        s = s.rsplit('|', 1)[1]
    s = s.strip()
    m = re.fullmatch(r'(\d{4})[-/.年](\d{1,2})[-/.月](\d{1,2})日?', s) or re.fullmatch(r'(\d{4})(\d{2})(\d{2})', s)
    if not m:
        return None
    mo = int(m[2])
    return mo if 1 <= mo <= 12 else None


def month_band(mo):
    if not mo:
        return None
    return 'M1_3' if mo <= 3 else 'M4_5' if mo <= 5 else 'M6P'


def labels5(cur, hist):
    """Fifth B3 part. -> [(name, value)]"""
    try:
        age = int(cur.get('age') or 0)
    except (TypeError, ValueError):
        return []
    if age != 2:
        return []
    mb, pb = month_band(birth_month(cur.get('birth'))), pop_band(cur.get('pop'))
    if not mb or not pb:
        return []
    kind = 'SHINBA' if cur.get('shinba') else '2YO'
    return [('BMONTH', f'{kind}|{mb}|{pb}')]


# ---------------------------------------------------------------- B3 sixth part (pre-registered 2026-11-25 18時台)
"""
  危険な人気馬の細目（Drive n7『地方競馬版・危険な1番人気の見抜き方』／n79『ちょっと待て 怪しくないか？中央馬』）。
  1・2番人気の馬にだけ付ける。どれも主張・未検証で、強さは NAR データの A/E で測る。
  FAVAWAY  その場での出走経験: FIRST（過去走にこの場が無い＝初遠征・転入初戦）/ SEEN。過去走が無い馬には付けない
  FAVWET   馬場 WET（重・不良）/ DAMP（稍重）/ DRY（良）x 直近3走の初角の平均位置 CLOSER（後ろ4割以降）/ OTHER
           （n7『重不良での人気差し馬』）
  FAVLIGHT メンバー内の馬体重の相対位置: LIGHT（軽い方から1/3）/ MID / HEAVY（重い方から1/3）。
           当日馬体重のある出走馬が4頭以上のときだけ（n79『メンバー内で相対的に軽い馬体重』）
  未接続：楽逃げ圧勝→同型出現・同じ相手との比較（メンバー間の対戦表が要る）、中央でダート経験なし（中央の芝ダ履歴が要る）、
          斤量減の人気馬（ext_model の行に斤量が無い）
"""
PREREG6 = {'registered': '2026-11-25T18', 'bundle': 'B3', 'labels': ['FAVAWAY', 'FAVWET', 'FAVLIGHT'],
           'rule': 'weight 0.0; adopted only via ext_model.fit_weights hold-out improvement (no manual weights)'}
COMPONENTS6 = {'FAVAWAY': 'FAW', 'FAVWET': 'FWT', 'FAVLIGHT': 'FLT'}


def bw_rel(bw, field_bws):
    """bw: this horse; field_bws: body weights of the runners in the race (this horse included)."""
    ws = [w for w in (field_bws or []) if w]
    if not bw or len(ws) < 4:
        return None
    lighter = sum(1 for w in ws if w < bw)
    heavier = sum(1 for w in ws if w > bw)
    n = len(ws)
    if lighter < n / 3.0 and heavier >= n / 3.0:
        return 'LIGHT'
    if heavier < n / 3.0 and lighter >= n / 3.0:
        return 'HEAVY'
    return 'MID'


def _going3(g):
    g = str(g or '')
    if ('不' in g or '重' in g) and '稍' not in g:
        return 'WET'
    return 'DAMP' if '稍' in g else 'DRY' if '良' in g else None


def labels6(cur, hist):
    """Sixth B3 part (1・2番人気だけ). cur['field_bws']: 当日のメンバーの馬体重. -> [(name, value)]"""
    pop = cur.get('pop')
    if not pop or pop > 2:
        return []
    out = []
    if hist and cur.get('venue'):
        out.append(('FAVAWAY', 'SEEN' if any(p.get('venue') == cur['venue'] for p in hist) else 'FIRST'))
    g = _going3(cur.get('going'))
    ear = [p['early'] for p in (hist or [])[-3:] if p.get('early') is not None]
    if g and ear:
        out.append(('FAVWET', f"{g}|{'CLOSER' if sum(ear) / len(ear) >= 0.6 else 'OTHER'}"))
    rel = bw_rel(cur.get('bw'), cur.get('field_bws'))
    if rel:
        out.append(('FAVLIGHT', rel))
    return out


# ---------------------------------------------------------------- B3 seventh part (pre-registered 2026-11-26 12時台)
"""
  LEADCLASH 前走で逃げた（初角先頭）馬の今回: 前走の着順 WON（1着＝楽逃げ圧勝の代わり）/ LOST
            x 今回のメンバーに自分以外の「逃げ型」がいるか CLASH（1頭以上）/ ALONE。
            逃げ型 = 前走の初角が先頭、または直近5走の初角平均が前1/4（2走以上）。
            (Drive n7『楽逃げ圧勝→同型出現』、n78『前走逃げ→今回ハナを取れず番手』の着順：ハナを取れるかは事前に
            分からないので、同型がいるかを事前の代わりにする。LEADX は同型の有無を見ていなかった)
  未接続：同じ相手との比較（対戦表が要る）、斤量減の人気馬（ext_model の行に斤量が無い）
"""
PREREG7 = {'registered': '2026-11-26T12', 'bundle': 'B3', 'labels': ['LEADCLASH'],
           'rule': 'weight 0.0; adopted only via ext_model.fit_weights hold-out improvement (no manual weights)'}
COMPONENTS7 = {'LEADCLASH': 'LCL'}


def is_front_type(hist):
    """hist oldest first (dicts with 'early'). True when the last start led at the first corner, or the
    mean first-corner position of the last 5 starts (2+ known) is in the front quarter."""
    if not hist:
        return False
    if hist[-1].get('early') is not None and hist[-1]['early'] <= 0.0:
        return True
    ear = [p['early'] for p in hist[-5:] if p.get('early') is not None]
    return len(ear) >= 2 and sum(ear) / len(ear) <= 0.25


def labels7(cur, hist):
    """Seventh B3 part. cur['field_front_n']: 今回のメンバー（この馬を含む）の逃げ型の頭数. -> [(name, value)]"""
    if not hist or hist[-1].get('early') is None or hist[-1]['early'] > 0.0:
        return []
    n = cur.get('field_front_n')
    if n is None:
        return []
    others = max(0, int(n) - 1)   # this horse led last time, so it is itself counted as a front type
    won = hist[-1].get('finish') == 1
    return [('LEADCLASH', f"{'WON' if won else 'LOST'}|{'CLASH' if others >= 1 else 'ALONE'}")]


# ---------------------------------------------------------------- B3 eighth part (pre-registered 2026-11-26T15)
"""
  FAVH2H  上位人気（1・2番人気）の「同じ相手との比較」: 今回のメンバーのうち過去に同じレースで走った相手について、
          いちばん最近の対戦で先着されたか。NOMEET（対戦なし）/ BEATALL（対戦した相手には全部先着）/
          LOST1（1頭に先着された）/ LOST2+（2頭以上）。
          同じレースの判定は (日付, 場, 距離, 頭数) の一致（NAR の行と楽天の近5走で共通に持つ列。race_id を持たない
          近5走でも同じ物差しにするため。同じ日・場・距離・頭数の別レースは稀で、誤一致は残る前提）。
          (Drive n7『地方競馬版・危険な1番人気の見抜き方』の残り『同じ相手との比較』。主張・未検証。
           勝ちと負けの数や着差は使わない：事前に固定できる最小の区分にとどめる)
"""
PREREG8 = {'registered': '2026-11-26T15', 'bundle': 'B3', 'labels': ['FAVH2H'],
           'rule': 'weight 0.0; adopted only via ext_model.fit_weights hold-out improvement (no manual weights)'}
COMPONENTS8 = {'FAVH2H': 'FH2'}


def meet_key(p):
    if not p or not p.get('date') or not p.get('venue') or not p.get('distance') or not p.get('field'):
        return None
    return (str(p['date']), p['venue'], p['distance'], p['field'])


def h2h(own, opps):
    """own: this horse's history (oldest first); opps: the other runners' histories.
    -> (met, beaten_by) where beaten_by counts opponents that finished ahead in the most recent common race."""
    mine = [(meet_key(p), p.get('finish')) for p in reversed(own or []) if p.get('finish')]
    met = beaten = 0
    for oh in opps or []:
        theirs = {meet_key(p): p.get('finish') for p in (oh or []) if p.get('finish')}
        theirs.pop(None, None)
        for k, f in mine:
            if k is not None and k in theirs:
                met += 1
                beaten += 1 if theirs[k] < f else 0
                break
    return met, beaten


def labels8(cur, hist):
    """Eighth B3 part. cur['h2h'] = (met, beaten_by) against today's field, counted from pre-race histories."""
    pop, hh = cur.get('pop'), cur.get('h2h')
    if not pop or pop > 2 or not hh:
        return []
    met, beaten = hh
    v = 'NOMEET' if not met else 'BEATALL' if not beaten else 'LOST1' if beaten == 1 else 'LOST2+'
    return [('FAVH2H', v)]


# ---------------------------------------------------------------- B3 ninth part (pre-registered 2026-11-26T18)
"""
  FAVLOAD 1・2番人気の斤量の前走差（n80「斤量減の人気馬」）：今回の負担重量 − 前走の負担重量。
          DEC（−1.0kg 以下）/ SAME（−1.0〜+1.0 の間）/ INC（+1.0kg 以上）/ NOPREV（前走の斤量が無い）。値 = '<帯>|<人気>'。
          前走の斤量は NAR CSV の負担重量と楽天カードの近走欄（騎手名の後ろの斤量）だけから取る（レース前に分かる値）。
          (Drive: ちょっと待て 怪しくないか？人気ウマ、n80。FAVRST で短期休み明けは接続済み、斤量減は前走値が履歴に無く未着手だった)
  人気帯別の回収（label_pop_table の win_ret / place_ret）：払戻のあるレースだけで、候補ラベルの値×人気帯ごとに
          100円あたりの単勝・複勝の平均払戻を出す（n259「勝率が高い≠回収率が高い」の残り）。払戻は結果側の値で、
          特徴には使わず表だけに出す。証拠のみ、正式券面・重みは不変。
"""
PREREG9 = {'registered': '2026-11-26T18', 'bundle': 'B3', 'labels': ['FAVLOAD'],
           'rule': 'weight 0.0; adopted only via ext_model.fit_weights hold-out improvement (no manual weights)'}
COMPONENTS9 = {'FAVLOAD': 'FLD'}


def load_of(v):
    """'56.0' / '▲54' / 54 -> float, else None."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v) if 30 <= v <= 70 else None
    m = _re.search(r'(\d{2}(?:\.\d)?)', str(v))
    x = float(m[1]) if m else None
    return x if x is not None and 30 <= x <= 70 else None


def load_band(now, prev):
    if now is None:
        return None
    if prev is None:
        return 'NOPREV'
    d = round(now - prev, 1)
    return 'DEC' if d <= -1.0 else 'INC' if d >= 1.0 else 'SAME'


def labels9(cur, hist):
    """Ninth B3 part. cur['load'] = today's 負担重量; hist[-1]['load'] = the previous start's (pre-race histories only)."""
    pop = cur.get('pop')
    if not pop or pop > 2:
        return []
    prev = load_of(hist[-1].get('load')) if hist else None
    b = load_band(load_of(cur.get('load')), prev)
    return [('FAVLOAD', f'{b}|{pop}')] if b else []


def add_returns(table, rows, names=None):
    """n259 remainder: add win_ret / place_ret (average payout per 100 yen) to label_pop_table() output, using only rows
    whose race had payouts (r['pay_known']). Evidence only."""
    acc = {}
    for r in rows:
        if not r.get('pay_known'):
            continue
        pb = pop_band(r.get('pop'))
        if pb is None:
            continue
        for name, val in r.get('cand_labels') or []:
            if names and name not in names:
                continue
            d = acc.setdefault((f'{name}={val}', pb), [0, 0, 0])
            d[0] += 1
            d[1] += r.get('pay_win') or 0
            d[2] += r.get('pay_place') or 0
    for (lv, pb), (n, w, p) in acc.items():
        d = table.setdefault(lv, {}).setdefault(pb, {'n': 0, 'top3': 0, 'exp': 0.0, 'ae': None})
        d['n_pay'] = n
        d['win_ret'] = round(w / n, 1) if n else None
        d['place_ret'] = round(p / n, 1) if n else None
    return table

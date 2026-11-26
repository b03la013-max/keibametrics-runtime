"""B3 n92 頭別P2（勝ち馬を固定したときの2着候補）の影の計測（Drive 精読 gap_tracker B3、2026-11-26 09時台。証拠のみ）。

出典：Drive「ケイバメトリクス地方｜2026-11-21 全35R反省・PFS・P0/P1/P2」P1-1
  「高知5R、佐賀4・9Rでは勝ち馬がW内でも2着馬が8・8・9位でP2外だった。全体順位を1頭増やすだけのP2拡張では
   不足する。頭別P2候補と静的順位の対照を、同じ事前入力・予算・評価期間で比較する。」（主張・未検証）

やること（券面・役割・点数は一切変えない）：
  勝ち馬が W に居たレースだけを対象に（W に居なければ W_MISS として数えるだけ）、勝ち馬を頭に固定したとき
  2着馬が何位に来ていたかを、事前登録した並べ方（アーム）ごとに測る。予算は全アーム同じ k 頭
  （そのレースの P2 の頭数、P2 が無ければ 2）。入力は締切前に固定した PAPER の出馬表の値だけ。

アーム（PREREG、2026-11-26T09 登録。候補 2・対照 1 の同数比較。後から足すときは新しい登録日で追加し、既存は書き換えない）：
  STATIC        対照。正式／PAPER の順位から勝ち馬を除いた順（現行の P2 選びと同じ情報）
  STYLE_COND    候補。頭の脚質群（FRONT＝展開予想 逃げ/好位 または EVI≥66、それ以外 CLOSER）と同じ群の馬を
                静的順位で STYLE_SHIFT 位だけ前へ（「行った行った」「差し決着」は頭と2着の脚質が揃うという仮説）
  MARKET_COND   候補。単勝オッズの順（頭を除く）。静的順位と市場のどちらが頭固定時の2着をよく拾うかの比較
  特徴（EVI・PACE・単勝）が無い馬が半数を超えるレースでは、そのアームを UNTESTED にする（静的順位で埋めない）。

出力：race() は1レース分、aggregate() は対象レースの合計（アームごとの k 頭内率・平均順位・順位分布、
  静的では k 頭外だったのに候補では k 頭内だった「救済」と、その逆の「喪失」）。
  採用はしない。100R・2場以上で候補が STATIC を上回り、喪失が救済を下回るときだけ OWNER_DECISION として報告する。
"""
from collections import Counter

PREREG = {
    'registered_at': '2026-11-26T09:00+09:00',
    'source': 'Drive 1B1XxB3tpYHm8BedDmofU5V2-c5yDTcnypHQjbYAg-5U P1-1（gap n92）',
    'arms': ['STATIC', 'STYLE_COND', 'MARKET_COND'],
    'control': 'STATIC',
    'budget': 'k = len(P2) or 2（全アーム同じ）',
    'decision_rule': '100R・2場以上、候補の k 頭内率 > STATIC かつ 喪失 < 救済 のときだけ OWNER_DECISION として報告（自動採用なし）',
}
STYLE_SHIFT = 2
FRONT_PACE = ('逃げ', '好位')
FRONT_EVI = 66.0


def _style(f):
    if not f:
        return None
    pace = f.get('PACE')
    if pace in FRONT_PACE:
        return 'FRONT'
    if pace in ('中位', '後方'):
        return 'CLOSER'
    evi = f.get('EVI')
    if isinstance(evi, (int, float)):
        return 'FRONT' if evi >= FRONT_EVI else 'CLOSER'
    return None


def _odds(f):
    w = (f or {}).get('win')
    return float(w) if isinstance(w, (int, float)) and w > 0 else None


def arm_orders(ranking, head, feats=None):
    """勝ち馬 head を除いた2着候補の並びをアームごとに返す（UNTESTED は None）。"""
    feats = feats or {}
    rest = [h for h in ranking if h != head]
    out = {'STATIC': rest}
    n = len(rest) or 1
    hs = _style(feats.get(head))
    styles = {h: _style(feats.get(h)) for h in rest}
    if hs is None or sum(v is None for v in styles.values()) * 2 > n:
        out['STYLE_COND'] = None
    else:
        key = {h: i - (STYLE_SHIFT if styles[h] == hs else 0) for i, h in enumerate(rest)}
        out['STYLE_COND'] = sorted(rest, key=lambda h: (key[h], rest.index(h)))
    od = {h: _odds(feats.get(h)) for h in rest}
    if sum(v is None for v in od.values()) * 2 > n:
        out['MARKET_COND'] = None
    else:
        out['MARKET_COND'] = sorted(rest, key=lambda h: (od[h] if od[h] is not None else 9999.0, rest.index(h)))
    return out


def race(ranking, roles, order, feats=None, key=None):
    """ranking: 事前の順位（馬番）、roles: {馬番: ['W','P2',...]}、order: 実着順、feats: {馬番: {'PACE','EVI','win'}}。"""
    ranking = [int(x) for x in ranking or []]
    feats = {int(h): v for h, v in (feats or {}).items()}
    if len(order) < 2 or not ranking:
        return {'status': 'NO_DATA', 'key': key}
    roles = {int(h): list(v if isinstance(v, list) else [v]) for h, v in (roles or {}).items()}
    w = [h for h in ranking if 'W' in roles.get(h, [])]
    p2 = [h for h in ranking if 'P2' in roles.get(h, [])]
    k = len(p2) or 2
    win, sec = int(order[0]), int(order[1])
    if win not in w:
        return {'status': 'W_MISS', 'key': key, 'k': k}
    if sec not in ranking:
        return {'status': 'NO_DATA', 'key': key, 'reason': 'second_not_in_ranking'}
    arms = {}
    for name, seq in arm_orders(ranking, win, feats).items():
        if seq is None:
            arms[name] = {'status': 'UNTESTED'}
            continue
        rank = seq.index(sec) + 1
        arms[name] = {'status': 'TESTED', 'rank': rank, 'in_k': rank <= k, 'top_k': seq[:k]}
    return {'status': 'W_HIT', 'key': key, 'k': k, 'winner': win, 'second': sec,
            'second_in_role_P2': sec in p2, 'head_style': _style(feats.get(win)),
            'arms': arms, 'prereg': PREREG['registered_at']}


def _band(r):
    return '1-2' if r <= 2 else '3-4' if r <= 4 else '5-7' if r <= 7 else '8+'


def aggregate(items):
    items = [x for x in items or [] if isinstance(x, dict) and x.get('status') in ('W_HIT', 'W_MISS')]
    hit = [x for x in items if x['status'] == 'W_HIT']
    out = {'races': len(items), 'w_hit': len(hit), 'w_miss': len(items) - len(hit),
           'second_in_role_P2': sum(1 for x in hit if x.get('second_in_role_P2')), 'arms': {},
           'prereg': PREREG['registered_at'], 'decision_rule': PREREG['decision_rule']}
    for arm in PREREG['arms']:
        t = [x for x in hit if (x['arms'].get(arm) or {}).get('status') == 'TESTED']
        a = {'tested': len(t), 'in_k': sum(1 for x in t if x['arms'][arm]['in_k']),
             'mean_rank': round(sum(x['arms'][arm]['rank'] for x in t) / len(t), 2) if t else None,
             'rank_band': dict(Counter(_band(x['arms'][arm]['rank']) for x in t))}
        if arm != PREREG['control']:
            both = [x for x in t if (x['arms'].get('STATIC') or {}).get('status') == 'TESTED']
            a['rescued'] = sum(1 for x in both if x['arms'][arm]['in_k'] and not x['arms']['STATIC']['in_k'])
            a['lost'] = sum(1 for x in both if not x['arms'][arm]['in_k'] and x['arms']['STATIC']['in_k'])
            a['paired'] = len(both)
        out['arms'][arm] = a
    return out


def line(a):
    if not a or not a.get('w_hit'):
        return None
    parts = []
    for arm in PREREG['arms']:
        x = a['arms'].get(arm) or {}
        if not x.get('tested'):
            parts.append(f'{arm} 未検証')
            continue
        s = f"{arm} {x['in_k']}/{x['tested']}（平均{x['mean_rank']}位）"
        if 'rescued' in x:
            s += f" 救済{x['rescued']}・喪失{x['lost']}"
        parts.append(s)
    return (f"頭別P2（B3 n92・影の計測、勝ち馬W内 {a['w_hit']}R／W外 {a['w_miss']}R、2着が P2 役割 {a['second_in_role_P2']}R）："
            + '／'.join(parts))

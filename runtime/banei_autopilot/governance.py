"""KAG-BAN — Blue・Red・Purple 三チーム統治（Owner 2026-11-27 22:49「永続的に実施」、ばんえい版）。

継承: Adversarial Governance BLUE / RED / PURPLE v1.0-CANDIDATE（2026-09 策定、RED-1〜5 の五層、Purple の6裁定）。
- Blue＝本番の予想（engine・tickets）と結果後の反省（review）。ここでは作り直さない。
- Red ＝発走前に凍結した記録だけで行う機械的な反証（LEVEL-1、決定論）。規則と重大度は下の RED に事前固定。
- Blue Response・Purple 裁定＝規則に紐づけて事前固定（RESPONSE・DISPOSITION）。本番を変える裁定（ADOPT-BEFORE-FREEZE）は
  既に許可された修正（直前見直し Rev2・取消の反映）に限る。それ以外は SHADOW／EXISTING-RULE-ABSORBED／REGRESSION-ONLY／NO-CHANGE。
- 結果後の Red（反証の検証）: 発走前の指摘が、実際の最初の断線（FFL）と同じ層だったか＝指摘の当たり外れ。基準率と並べる。
- RED-5 Meta は registry（毎晩）: 一度も本番と違う券面を出していない候補・同じ設定の重複・候補の数。
独立性: ここで行うのは LEVEL-1（機械検査）だけ。LEVEL-3（別AI＝ChatGPT）の反証は Drive の全レース記録を使って行い、
その指摘への Claude の応答と Owner の判断は IMPROVEMENT_LOG に記録する（同じAIが三役を演じたものを独立監査と呼ばない）。
本番の予想・券面・購入方針は変えない。
"""

RULES_AT = '2026-11-27T23:00:00+09:00'

# id: (層, 重大度, 内容, 結果後に「当たり」とみなす FFL / 原因, Blue の応答, Purple の裁定)
RED = {
    'E1_FEED_MISSING': ('RED-1', 'P0', 'キンタロー・水分ボンバー・競馬ブックのどれかが欠けたまま予想', ('ROLE', 'C0-INFO'), 'EXISTING', 'EXISTING-RULE-ABSORBED'),
    'E2_MOISTURE_MISSING': ('RED-1', 'P1', '馬場水分が無いまま予想（ADF・SBO の水分帯が効かない）', ('ROLE',), 'ACCEPT', 'REGRESSION-ONLY'),
    'E3_JOCKEY_MISSING': ('RED-1', 'P1', '騎手が空欄の馬がいる（騎手変更の反映漏れの疑い）', ('ROLE',), 'ACCEPT', 'REGRESSION-ONLY'),
    'E4_POP_MISSING': ('RED-1', 'P2', '人気が空欄の馬がいる（穴・本命禁止の判定が効かない）', ('ROLE',), 'PARTIAL', 'REGRESSION-ONLY'),
    'E5_BARRIER_THIN': ('RED-1', 'P1', '障害の根拠（キンタロー区間秒）が未確認の馬が半数以上', ('ROLE', 'C0-INFO'), 'UNKNOWN', 'SHADOW'),
    'E6_HISTORY_THIN': ('RED-1', 'P2', '過去走の無い馬が3割以上（情報不足）', ('ROLE', 'C0-INFO'), 'UNKNOWN', 'SHADOW'),
    'P1_FAVORITE_OUT_OF_W': ('RED-2', 'P1', '1番人気が1着候補（W）に入っていない（独立した勝ち馬の見落としの疑い）', ('ROLE',), 'REBUT', 'SHADOW'),
    'P2_LOW_DISCRIMINATION': ('RED-2', 'P2', '1着の点の1位と2位の差が1未満（区別がついていないのに◎を1頭に決めている）', ('ROLE', 'EXACT'), 'PARTIAL', 'SHADOW'),
    'R1_SINGLE_W': ('RED-3', 'P2', '1着候補が1頭だけ（頭の依存）', ('ROLE', 'EXACT'), 'EXISTING', 'SHADOW'),
    'R2_MARKET_TOP3_NO_ROLE': ('RED-3', 'P1', '人気上位3頭のうち、どの役割にも入っていない馬がいる', ('ROLE', 'HEAD-P2-TERMINAL', 'PAIR-P3-TERMINAL'), 'REBUT', 'SHADOW'),
    'C1_MULTI_W_SINGLE_HEAD': ('RED-4', 'P1', '1着候補が2頭以上なのに三連単の頭が1頭だけ（判断の複数を資金で1頭にまとめている）', ('EXACT',), 'EXISTING', 'SHADOW'),
    'C2_HEAVY_COMPRESSION': ('RED-4', 'P2', '三連単の全組合せの1割未満しか買っていない（圧縮で勝ち筋が落ちやすい）', ('EXACT',), 'PARTIAL', 'SHADOW'),
    'C3_HUB_ALL_TRIO': ('RED-4', 'P2', '三連複がすべて◎を含む（◎が3着外なら全滅）', ('PAIR-P3-TERMINAL', 'HEAD-P2-TERMINAL', 'ROLE'), 'EXISTING', 'SHADOW'),
}


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def pre_race(rec):
    """発走前に凍結した記録だけで Red の機械反証を行う。返り値は governance 記録（rec に書き足して保存する）。"""
    ev, tk = rec.get('evaluation') or {}, rec.get('tickets') or {}
    rows = ev.get('rows') or []
    hits = []

    def hit(cid, evidence):
        layer, sev, what, _, resp, disp = RED[cid]
        hits.append({'id': cid, 'layer': layer, 'severity': sev, 'what': what, 'evidence': evidence,
                     'blue_response': resp, 'purple': disp})
    feeds = set(rec.get('feeds_present') or [])
    miss = [f for f in ('kintaro', 'sbo', 'keibabook') if f not in feeds]
    if miss:
        hit('E1_FEED_MISSING', {'missing': miss})
    if rec.get('moisture') is None:
        hit('E2_MOISTURE_MISSING', {})
    nj = [x['no'] for x in rows if not x.get('jockey')]
    if nj and any(x.get('jockey') for x in rows):            # 列ごと無い古い記録は対象外
        hit('E3_JOCKEY_MISSING', {'horses': nj})
    np_ = [x['no'] for x in rows if x.get('pop') is None]
    if np_ and any(x.get('pop') is not None for x in rows):
        hit('E4_POP_MISSING', {'horses': np_})
    if rows:
        un = sum(1 for x in rows if x.get('bta_evidence') == 'UNCONFIRMED')
        if un / len(rows) >= 0.5:
            hit('E5_BARRIER_THIN', {'unconfirmed': un, 'field': len(rows)})
        nh = sum(1 for x in rows if not x.get('nar_starts'))
        if nh / len(rows) >= 0.3:
            hit('E6_HISTORY_THIN', {'no_history': nh, 'field': len(rows)})
    W = [x['no'] for x in rows if x.get('role_w')]
    roles = {x['no'] for x in rows if x.get('role_w') or x.get('role_p2') or x.get('role_p3')}
    fav = next((x for x in rows if x.get('pop') == 1), None)
    if fav and fav['no'] not in W:
        hit('P1_FAVORITE_OUT_OF_W', {'no': fav['no'], 'win_rank': fav.get('win_rank')})
    ws = sorted((x['win_score'] for x in rows if _num(x.get('win_score'))), reverse=True)
    if len(ws) >= 2 and ws[0] - ws[1] < 1.0:
        hit('P2_LOW_DISCRIMINATION', {'gap': round(ws[0] - ws[1], 2)})
    if len(W) == 1:
        hit('R1_SINGLE_W', {'w': W})
    top3 = [x['no'] for x in rows if _num(x.get('pop')) and x['pop'] <= 3]
    out3 = [n for n in top3 if n not in roles]
    if out3:
        hit('R2_MARKET_TOP3_NO_ROLE', {'horses': out3})
    exact, trio = tk.get('exact') or [], tk.get('trio') or []
    heads = sorted({x[0] for x in exact})
    if len(W) >= 2 and len(heads) == 1:
        hit('C1_MULTI_W_SINGLE_HEAD', {'w': W, 'heads': heads})
    uni = (tk.get('universe') or {}).get('exact') if isinstance(tk.get('universe'), dict) else None
    if exact and _num(uni) and uni and len(exact) / uni < 0.10:
        hit('C2_HEAVY_COMPRESSION', {'bought': len(exact), 'universe': uni})
    hon = (ev.get('honmei') or {}).get('no') if isinstance(ev.get('honmei'), dict) else ev.get('honmei')
    if trio and hon is not None and all(hon in x for x in trio):
        hit('C3_HUB_ALL_TRIO', {'honmei': hon, 'trio': len(trio)})
    return {'rules_at': RULES_AT, 'independence': 'LEVEL-1（機械検査、Claude のコード）', 'frozen_at': rec.get('frozen_at'),
            'ticket_sha256': rec.get('ticket_sha256'), 'challenges': hits,
            'production_changed': False,
            'note': '発走前の機械反証。本番を変える裁定はしない（Rev2・取消の反映は既存の直前見直しが担う）'}


def post_result(gov, review):
    """結果後の Red（反証の検証）: 発走前の各指摘が、実際の最初の断線・原因と同じ層だったか。"""
    if not gov or not review:
        return None
    ffl, cause = review.get('ffl'), review.get('cause')
    out = []
    for c in gov.get('challenges') or []:
        match = RED.get(c['id'], (None, None, None, ()))[3]
        out.append({'id': c['id'], 'layer': c['layer'], 'confirmed': bool(ffl in match or cause in match or
                                                                         (cause == 'C0' and 'C0-INFO' in match))})
    return {'ffl': ffl, 'cause': cause, 'checked': out, 'any_challenge': bool(out),
            'failed': ffl not in (None, 'NONE')}


def summary(revs):
    """期間の統治の成績: 指摘ごとの 件数・当たり（同じ層で実際に断線）・当たり率と、指摘の無いレースの断線率（基準）。"""
    per, base_n, base_fail, ch_n, ch_fail = {}, 0, 0, 0, 0
    for x in revs:
        g = x.get('governance')
        if not g or 'error' in g:
            continue
        if g['any_challenge']:
            ch_n += 1
            ch_fail += int(g['failed'])
        else:
            base_n += 1
            base_fail += int(g['failed'])
        for c in g['checked']:
            d = per.setdefault(c['id'], {'layer': c['layer'], 'n': 0, 'confirmed': 0})
            d['n'] += 1
            d['confirmed'] += int(c['confirmed'])
    allg = [x['governance'] for x in revs if x.get('governance') and 'error' not in x['governance']]
    for cid, d in per.items():
        d['precision'] = round(d['confirmed'] / d['n'], 3) if d['n'] else None
        match = RED.get(cid, (None, None, None, ()))[3]
        base = [g for g in allg if g['ffl'] in match or g['cause'] in match or (g['cause'] == 'C0' and 'C0-INFO' in match)]
        d['base_rate'] = round(len(base) / len(allg), 3) if allg else None      # 指摘の有無に関係なく、その層で断線した割合
        d['lift'] = round(d['precision'] / d['base_rate'], 2) if d['precision'] is not None and d['base_rate'] else None
    return {'rules_at': RULES_AT, 'challenges': dict(sorted(per.items())),
            'races_with_challenge': ch_n, 'fail_rate_with_challenge': round(ch_fail / ch_n, 3) if ch_n else None,
            'races_without_challenge': base_n, 'fail_rate_without_challenge': round(base_fail / base_n, 3) if base_n else None}


def meta(reg, revs):
    """RED-5 Meta（毎晩）: 本番と一度も違う券面を出していない候補（効いていない）、同じ設定の重複、候補の数。"""
    import json
    active = {k: v for k, v in reg['candidates'].items() if v.get('status') == 'SHADOW'}
    diff = {k: 0 for k in active}
    seen = {k: 0 for k in active}
    for x in revs:
        for cid, s in ((x.get('shadow') or {}).items()):
            if cid in diff and isinstance(s, dict) and 'differs' in s:
                seen[cid] += 1
                diff[cid] += int(bool(s.get('differs')))
    inert = sorted(k for k in active if seen[k] >= 30 and diff[k] == 0)
    cfgs = {}
    for k, v in active.items():
        cfgs.setdefault(json.dumps(v.get('config') or {}, sort_keys=True), []).append(k)
    dup = [ks for ks in cfgs.values() if len(ks) > 1]
    return {'active': len(active), 'inert_after_30R': inert, 'duplicate_configs': dup,
            'note': '効いていない候補・重複は Purple 裁定 REJECT-WITH-REASON の材料（自動では消さない、引退は registry の 300R 規則）'}

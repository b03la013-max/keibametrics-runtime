"""KeibaMetrics BAN race-day autopilot (帯広). v4.0-BAN, Owner decisions 2026-11-18/19.

tick: discover the day's 帯広 races (楽天 baba 03) -> per race at post-35..post-6 min fetch the card,
build horses (card + NAR ledger + feeds), evaluate + compile (三連複/三連単, cap 30), render the tree,
freeze, deliver once to the dedicated BAN issue before post-5 -> after post+12 min read the official
result and settle (PFS, First Failure Layer). Every 楽天 request keeps the LOCAL >=61 s spacing.

Env: KM_BAN_OUT (default runtime/banei_autopilot/output), KM_BAN_NAR_DIR (Owner's NAR extract),
KM_BAN_FEED_DIR (collector outputs), KM_BAN_DELIVERY_ISSUE, GH_TOKEN.
"""
import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.append(str(HERE.parent / 'local_autopilot'))
sys.path.append(str(HERE.parent.parent))
import engine  # noqa: E402
import tickets  # noqa: E402
import render  # noqa: E402
import source  # noqa: E402
import kintaro  # noqa: E402
import rakuten as RK  # noqa: E402
import settle as ST  # noqa: E402

JST = timezone(timedelta(hours=9))
REPO = 'b03la013-max/keibametrics-runtime'
PRED_FROM, CUTOFF, RESULT_AFTER = 35, 5, 12          # minutes relative to post time
CHECK10 = 10                                          # 直前見直し (地方版 checkpoint10 と同じ: 発走10分前)


def now_jst():
    return datetime.now(JST)


def log(out, *a):
    line = now_jst().strftime('%H:%M:%S ') + ' '.join(str(x) for x in a)
    print(line, flush=True)
    with (out / 'autopilot_log.txt').open('a') as f:
        f.write(line + '\n')


def dump(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1, default=str) + '\n')


def _gh(method, path, body=None):
    import urllib.request
    tok = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    req = urllib.request.Request('https://api.github.com' + path, method=method,
                                 data=None if body is None else json.dumps(body).encode(),
                                 headers={'Authorization': f'Bearer {tok}', 'Accept': 'application/vnd.github+json',
                                          'Content-Type': 'application/json', 'User-Agent': 'km-ban-autopilot'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def discover(reader, day, out):
    top = reader.client.get('/')
    prefix = source.day_meeting(top, day)
    if not prefix:
        return {'day': day, 'races': {}, 'meeting': None}
    menu = source.parse_menu_ban(reader.card_page(f"{day.replace('-', '')}{source.BABA}03000001"), day)
    races = {}
    for no, rid, hhmm in menu:
        h, m = map(int, hhmm.split(':'))
        post = datetime.strptime(day, '%Y-%m-%d').replace(hour=h, minute=m, tzinfo=JST)
        races[f'{no:02d}'] = {'no': no, 'rid': rid, 'post': post.isoformat(), 'state': 'DISCOVERED'}
    q = {'day': day, 'meeting': prefix, 'races': races}
    dump(out / 'queue.json', q)
    log(out, 'DISCOVERED', prefix, len(races), 'races')
    return q


_SKILLED = {}


def predict(reader, q, key, out, hist, rev=1):
    r = q['races'][key]
    html = reader.card_page(r['rid'])
    card = source.parse_card_ban(html)
    hdr = RK.parse_header(html)
    moisture = source.moisture_from_header(html)
    feeds = {k: source.load_feed(os.environ.get('KM_BAN_FEED_DIR'), q['day'], k) for k in ('kintaro', 'sbo', 'keibabook', 'official')}
    sbo_meta = None
    try:                                                  # 水分ボンバー: 3 indices + 当日馬場水分 for every race
        import sbo as SBOMOD
        sb = source.sbo_race(SBOMOD.Client(out.parent / 'sbo_state.json'), q['day'], r['no'])
        feeds['sbo'] = {str(r['no']): {'table': sb['table']}}
        sbo_meta = {'sha256': sb['sha256'], 'horses': len(sb['table']), 'moisture': sb['moisture']}
        if moisture is None:
            moisture = sb['moisture']
    except Exception as e:                                # SBO hold / layout change -> own index only
        log(out, 'SBO_FAIL', key, f'{type(e).__name__}:{str(e)[:80]}')
    if not feeds['kintaro'].get(str(r['no'])):
        cache = Path(os.environ.get('KM_BAN_CACHE', out.parent / '.cache'))
        links = source.load_feed(os.environ.get('KM_BAN_FEED_DIR'), q['day'], 'kintaro_links')
        pdf = kintaro.fetch(q['day'], r['no'], cache / q['day'] / f"kintaro_{r['no']:02d}.pdf", url=links.get(f"{r['no']:02d}"))
        if pdf:
            try:
                feeds['kintaro'] = {**feeds['kintaro'], str(r['no']): kintaro.parse(pdf)}
            except Exception as e:                       # layout change -> REFERENCE, never a crash
                log(out, 'KINTARO_PARSE_FAIL', key, type(e).__name__)
    name = hdr.get('race_name') or ''
    import derive
    hist.get('')                                           # LazyHist: load the NAR ledger before the jockey table
    if id(hist) not in _SKILLED:
        _SKILLED[id(hist)] = derive.jockey_stats(hist)[1]
    import challengers
    import registry
    reg = registry.load(out.parent)                              # 本番の設定（自動昇格で更新される）と影の候補
    prod_cfg = reg['production'].get('config') or {}

    def rebuild():
        return source.build_horses(card, moisture, q['day'], hist, feeds, r['no'], race_name=name,
                                   skilled=derive.jockey_stats(hist)[1])
    with challengers.applied(prod_cfg):
        horses = (source.build_horses(card, moisture, q['day'], hist, feeds, r['no'], race_name=name,
                                      skilled=_SKILLED[id(hist)]) if not prod_cfg.get('cuts') else rebuild())
        race = {'moisture': moisture, 'special': any(k in name for k in ('特別', '賞', '杯', '記念')) and 'Ｃ' not in name,
                'young': '2歳' in name or '２歳' in name, 'horses': horses, 'pace': derive.race_pace(horses)}
        ev = engine.evaluate(race)
        tk = tickets.compile_race(ev)
    ev['ruleset_version'] = reg['production']['version']
    shadow = challengers.run_all(race, rebuild, reg['candidates'], prod_cfg)
    feeds_present = [k for k, v in feeds.items() if v]
    if not feeds['kintaro'].get(str(r['no'])):                 # barrier evidence missing -> not FORMAL (spec 5-3)
        tk['formality'] = 'REFERENCE-RENDERED'
    label = f"帯広{r['no']}R {r['post'][11:16]}発走"
    text, total = render.render(label, ev, tk, paper=False)
    frozen = now_jst().isoformat()
    sha = hashlib.sha256(json.dumps([tk['trio'], tk['exact']]).encode()).hexdigest()
    rec = {'race': r, 'header': hdr, 'moisture': moisture, 'pace': race['pace'], 'derive_cuts': derive.CUTS, 'sbo': sbo_meta, 'feeds_present': feeds_present, 'frozen_at': frozen,
           'ticket_sha256': sha, 'evaluation': ev, 'tickets': tk, 'text': text}
    # full ledger (SBO / キンタロー derived numbers) stays private on the Mac; the public file keeps composites only
    cache = Path(os.environ.get('KM_BAN_CACHE', out.parent / '.cache'))
    sfx = '' if rev == 1 else f'.rev{rev}'
    rec['revision'] = rev
    dump(cache / q['day'] / f'R{key}{sfx}.full.json', rec)
    PRIVATE = ('idx', 'idx_src', 'bsi', 'isv', 'barrier_mean_sec')
    pub = dict(rec, evaluation=dict(ev, rows=[{k: v for k, v in x.items() if k not in PRIVATE} for x in ev['rows']]))
    dump(out / f'R{key}{sfx}.json', pub)
    (out / f'R{key}{sfx}.md').write_text(text + '\n')
    dump(out / f'R{key}{sfx}.shadow.json', {'frozen_at': frozen, 'prereg': challengers.PREREG['registered_at'],
                                            'candidates': shadow})
    if rev != 1:
        return pub
    r.update(state='PREDICTION_COMPLETE', frozen_at=frozen, ticket_sha256=sha, points=total,
             formality=tk['formality'], moisture=moisture)
    log(out, 'PREDICTED', key, total, 'pts', tk['formality'], 'feeds', feeds_present)


def _scratched(rec):
    nos = {x['no'] for x in rec['evaluation']['rows']}
    return nos


def change_ledger(r1, r2):
    """直前見直しの変更台帳（11/22 ばんえい反省 ChatGPT P0-4、証拠のみ）：初版と見直しの各馬の騎手・馬体重・人気・
    オッズと出走の有無を before/after で残す。Rev2 にするかどうかの判定（reasons）には使わない。"""
    rows1 = {x['no']: x for x in r1['evaluation']['rows']}
    rows2 = {x['no']: x for x in r2['evaluation']['rows']}
    diffs = []
    for no in sorted(set(rows1) | set(rows2)):
        a, b = rows1.get(no), rows2.get(no)
        if a is None or b is None:
            diffs.append({'no': no, 'field': 'runner', 'before': a is not None, 'after': b is not None})
            continue
        for f in ('jockey', 'body_weight', 'pop', 'odds'):
            if f in a and f in b and a.get(f) != b.get(f):
                diffs.append({'no': no, 'field': f, 'before': a.get(f), 'after': b.get(f)})
    kinds = sorted({d['field'] for d in diffs})
    return {'rev1_frozen_at': r1.get('frozen_at'), 'rev2_received_at': r2.get('frozen_at'),
            'fields_compared': ['runner', 'jockey', 'body_weight', 'pop', 'odds'],
            'changed': kinds, 'jockey_changes': [d for d in diffs if d['field'] == 'jockey'],
            'diffs': diffs, 'evidence_only': True}


def check10(reader, q, key, out, hist):
    """直前見直し (発走10分前, 地方版 checkpoint10 と同じ型): 出馬表(取消・馬体重・オッズ)と水分ボンバーの馬場水分を取り直して
    再計算し、券面・出走馬・水分帯・区分のどれかが変わったときだけ修正版(Rev2)を保存・配信する。Rev1は残す。
    BAN-MG (spec 第5章): 水分差0.8ポイント以上または乾燥帯↔湿った帯の横断は、修正版をペーパー扱いにする。"""
    r = q['races'][key]
    rec = {'started_at': now_jst().isoformat()}
    r['check10'] = rec
    try:
        r1 = json.loads((out / f'R{key}.json').read_text())
        r2 = json.loads(json.dumps(predict(reader, q, key, out, hist, rev=2), ensure_ascii=False, default=str))
        reasons = []
        if _scratched(r1) != _scratched(r2):
            reasons.append('出走馬の変更（取消・除外）')
        m1, m2 = r1.get('moisture'), r2.get('moisture')
        b1, b2 = engine.moisture_band(m1), engine.moisture_band(m2)
        mg = (m1 is not None and m2 is not None and abs(m2 - m1) >= 0.8) or ({b1, b2} == {'DRY', 'WET'})
        if b1 != b2:
            reasons.append(f'馬場水分の区分変化 {m1}%→{m2}%')
        if r1['evaluation']['marks'] != r2['evaluation']['marks']:
            reasons.append('印の変化（馬体重・オッズ反映）')
        t1 = (sorted(map(tuple, r1['tickets']['trio'])), sorted(map(tuple, r1['tickets']['exact'])))
        t2 = (sorted(map(tuple, r2['tickets']['trio'])), sorted(map(tuple, r2['tickets']['exact'])))
        if t1 != t2:
            reasons.append('券面の変化')
        if r1['tickets']['formality'] != r2['tickets']['formality']:
            reasons.append(f"区分の変化 {r1['tickets']['formality']}→{r2['tickets']['formality']}")
        try:
            rec['changes'] = change_ledger(r1, r2)
        except Exception as e:                                    # evidence only: never blocks the T-10 check
            rec['changes'] = {'error': f'{type(e).__name__}:{str(e)[:80]}'}
        rec.update(reasons=reasons, moisture=[m1, m2], ban_mg=mg,
                   points=[r1['tickets']['points'], r2['tickets']['points']])
        if not reasons:
            rec['decision'] = 'KEEP_REVISION_1 (変更なし)'
        elif now_jst() >= datetime.fromisoformat(r['post']) - timedelta(minutes=CUTOFF):
            rec['decision'] = 'KEEP_REVISION_1 (締切に間に合わない)'
        else:
            r.update(effective='rev2', frozen_at_rev2=r2.get('frozen_at'),
                     rev1={k: r.get(k) for k in ('ticket_sha256', 'points', 'formality', 'moisture', 'frozen_at')},
                     ticket_sha256=r2['ticket_sha256'], points=r2['tickets']['points'],
                     formality=r2['tickets']['formality'], moisture=m2, paper=bool(mg))
            rec['decision'] = 'REVISION_2' + ('_PAPER (BAN-MG)' if mg else '')
            deliver(q, key, out, rev=2, reasons=reasons)
    except RK.SourceStop:
        raise
    except Exception as e:                                       # Rev1 stays valid and delivered
        rec['decision'] = f'KEEP_REVISION_1 (CHECK_FAILED:{type(e).__name__}:{str(e)[:100]})'
    rec['finished_at'] = now_jst().isoformat()
    log(out, 'CHECK10', key, rec['decision'], rec.get('reasons'))
    fetch_odds(reader, q, key, out)


def fetch_odds(reader, q, key, out):
    """発走10分前の見直しの後（配信の後）に、三連複・三連単の組合せ別オッズを取得して保存する（証拠：安すぎる買い目の検知、
    反省会の投資割れ分析）。本番の券面は変えない。"""
    r = q['races'][key]
    if r.get('odds_at'):
        return
    try:
        res = {}
        for kind, ordered in (('sanrenfuku', False), ('sanrentan', True)):
            html = reader.client.get(f"/odds/{kind}/RACEID/{r['rid']}")
            res[kind] = {'-'.join(map(str, c)): o for c, o in source.parse_odds_rank(html, ordered).items()}
        dump(out / f'R{key}.odds.json', {'fetched_at': now_jst().isoformat(), 'post': r['post'], **res})
        r['odds_at'] = now_jst().isoformat()
        log(out, 'ODDS', key, len(res['sanrenfuku']), len(res['sanrentan']))
    except RK.SourceStop:
        raise
    except Exception as e:
        log(out, 'ODDS_FAIL', key, f'{type(e).__name__}:{str(e)[:120]}')


def deliver(q, key, out, rev=1, reasons=None):
    issue = os.environ.get('KM_BAN_DELIVERY_ISSUE')
    r = q['races'][key]
    if not issue or (rev == 1 and r.get('delivered')) or (rev == 2 and r.get('delivered_rev2')):
        return
    sfx = '' if rev == 1 else '.rev2'
    text = (out / f'R{key}{sfx}.md').read_text()
    head = '' if rev == 1 else ('【修正版 Rev2' + ('・ペーパー（馬場水分の変化）' if r.get('paper') else '') + '】'
                                + '／'.join(reasons or []) + '\n\n')
    body = (f"### 🐴 帯広{r['no']}R {r['post'][11:16]}発走｜{r['formality']}{'｜修正版' if rev == 2 else ''}\n\n{head}```\n{text}```\n"
            f"<sub>ケイバメトリクスばんえい v4.0-BAN 自動予想。凍結 {(r.get('frozen_at_rev2') if rev == 2 else r['frozen_at'])[11:19]}／券面SHA `{r['ticket_sha256'][:12]}`"
            f"／未較正（確率・EVではありません）</sub>")
    try:
        c = _gh('POST', f'/repos/{REPO}/issues/{issue}/comments', {'body': body})
        if rev == 1:
            r.update(delivered=c['created_at'], delivery_url=c['html_url'])
        else:
            r.update(delivered_rev2=c['created_at'], delivery_url_rev2=c['html_url'])
        log(out, 'DELIVERED' if rev == 1 else 'DELIVERED_REV2', key, c['html_url'])
    except Exception as e:                                       # recorded, retried next tick until cutoff
        r['delivery_error'] = f'{type(e).__name__}:{str(e)[:100]}'
        log(out, 'DELIVERY_FAIL', key, r['delivery_error'])


def first_failure(tk, order):
    w, s, t = order[:3]
    tri = tuple(sorted((w, s, t)))
    if str(w) not in {str(n) for n in tk['terminal']}:          # JSON keys are strings
        return 'ROLE'
    if tri not in set(map(tuple, tk['trio'])):
        return 'PAIR-P3-TERMINAL' if any(set((w, s)) <= set(x) for x in tk['trio']) else 'HEAD-P2-TERMINAL'
    if tk['exact'] and (w, s, t) not in set(map(tuple, tk['exact'])):
        return 'EXACT'
    return 'NONE'


def settle_race(reader, q, key, out):
    r = q['races'][key]
    html = reader.result_page(r['rid'])
    res = ST.parse_result(html)
    ns = source.result_non_starters(html)                         # 取消・除外は返還（競走中止ではない）
    if ns:
        res['non_starters'] = sorted(set(res.get('non_starters') or []) | set(ns))
        res['did_not_finish'] = [n for n in (res.get('did_not_finish') or []) if n not in ns]
    if res is None:
        return
    eff = '.rev2' if r.get('effective') == 'rev2' else ''
    rec = json.loads((out / f'R{key}{eff}.json').read_text())
    tk = rec['tickets']
    trio_pay = res['payouts'].get('TRIO', {})
    ex_pay = res['payouts'].get('TRIFECTA', {})

    gone = set(res.get('non_starters') or [])               # 取消・除外 after the freeze: those tickets are refunded

    def ret(t):
        return sum(trio_pay.get(tuple(x), 0) for x in t['trio']) + sum(ex_pay.get(tuple(e), 0) for e in t['exact'])

    def eff_stake(t):                                            # 返還控除後の有効投資（FNB 第178条と同じ定義）
        return 100 * sum(1 for c in list(t['trio']) + list(t['exact']) if not (gone & set(c)))
    back = ret(tk)
    stake = eff_stake(tk)
    refund = tk['points'] * 100 - stake
    audit = None
    if eff:                                                      # Rev1 vs Rev2 (地方版 rev_audit と同じ比較)
        t1 = json.loads((out / f'R{key}.json').read_text())['tickets']
        audit = {'rev1_stake': eff_stake(t1), 'rev1_return': ret(t1), 'rev2_stake': stake, 'rev2_return': back,
                 'rev1_ffl': first_failure(t1, res['order']), 'rev2_ffl': first_failure(tk, res['order'])}
    out_res = {'order': res['order'], 'payouts': {k: {'-'.join(map(str, c)): y for c, y in v.items()}
                                                   for k, v in res['payouts'].items()},
               'stake': stake, 'return': back, 'refund': refund, 'non_starters': sorted(gone),
               'did_not_finish': sorted(res.get('did_not_finish') or []),          # 競走中止: 出走扱い・返還なし
               'pfs': round(100 * back / stake, 1) if stake else None,
               'first_failure_layer': first_failure(tk, res['order']), 'formality': r.get('formality'),
               'effective_revision': 2 if eff else 1, 'paper': bool(r.get('paper')), 'rev_audit': audit,
               'settled_at': now_jst().isoformat()}
    dump(out / f'R{key}.result.json', out_res)
    r.update(state='SETTLED', pfs=out_res['pfs'], ffl=out_res['first_failure_layer'])
    log(out, 'SETTLED', key, res['order'][:3], 'PFS', out_res['pfs'], out_res['first_failure_layer'])


def report(q, out):
    L = [f"# 帯広 {q['day']} ばんえい自動予想（v4.0-BAN）", '', '| R | 発走 | 状態 | 点数 | 区分 | 配信 | 直前見直し | PFS | 最初の断線 |',
         '|---|---|---|---|---|---|---|---|---|']
    st = sk = 0
    for k, r in sorted(q['races'].items()):
        L.append(f"| {r['no']} | {r['post'][11:16]} | {r['state']} | {r.get('points', '')} | {r.get('formality', '')} | "
                 f"{'済' if r.get('delivered') else ''} | {'修正版' if r.get('effective') == 'rev2' else ('変更なし' if r.get('check10') else '')} | "
                 f"{r.get('pfs', '')} | {r.get('ffl', '')} |")
        p = out / f'R{k}.result.json'
        if p.exists():
            d = json.loads(p.read_text())
            st += d['stake']
            sk += d['return']
    if st:
        L += ['', f"投資 {st:,}円／払戻 {sk:,}円／回収率 {100 * sk / st:.1f}%（100円均等・未較正）"]
    (out / 'README.md').write_text('\n'.join(L) + '\n')


class LazyHist(dict):
    """NAR ledger is read only when a race is actually predicted (the worker calls tick every loop)."""
    def __init__(self, d):
        super().__init__()
        self.d, self.loaded = d, False

    def get(self, k, default=None):
        if not self.loaded:
            self.update(source.nar_history(self.d))
            self.loaded = True
        return super().get(k, default)


def tick(day, out, reader, hist):
    qp = out / 'queue.json'
    q = json.loads(qp.read_text()) if qp.exists() else discover(reader, day, out)
    now = now_jst()
    # P0 (11/21 反省): 締切の近い予想・配信・直前見直しを先に終え、既走レースの精算はその後に回す
    for phase in ('urgent', 'settle'):
        for key, r in sorted(q['races'].items(), key=lambda kv: kv[1]['post']):
            post = datetime.fromisoformat(r['post'])
            now = now_jst()
            try:
                if phase == 'urgent':
                    if r['state'] == 'DISCOVERED' and post - timedelta(minutes=PRED_FROM) <= now < post - timedelta(minutes=CUTOFF + 1):
                        predict(reader, q, key, out, hist)
                        dump(qp, q)
                    if r['state'] == 'PREDICTION_COMPLETE' and not r.get('delivered') and now < post - timedelta(minutes=CUTOFF):
                        deliver(q, key, out)
                    if (r['state'] == 'PREDICTION_COMPLETE' and r.get('delivered') and not r.get('check10')
                            and post - timedelta(minutes=CHECK10) <= now < post - timedelta(minutes=CUTOFF + 1)):
                        check10(reader, q, key, out, hist)
                    if r['state'] == 'DISCOVERED' and now >= post - timedelta(minutes=CUTOFF + 1):
                        r['state'] = 'MISSED_DEADLINE'
                        log(out, 'MISSED_DEADLINE', key)
                elif r['state'] == 'PREDICTION_COMPLETE' and now >= post + timedelta(minutes=RESULT_AFTER):
                    if _urgent_soon(q, now):                      # a prediction window opens soon: settle later
                        break
                    settle_race(reader, q, key, out)
            except RK.SourceStop as e:
                log(out, 'SOURCE_HOLD', key, e)
                break
            except Exception as e:                               # one race never stops the day
                r['last_error'] = f'{type(e).__name__}:{str(e)[:160]}'
                log(out, 'ERROR', key, r['last_error'])
            dump(qp, q)
    n_set = sum(1 for r in q['races'].values() if r['state'] == 'SETTLED')
    if n_set and (q.get('reviewed_n') != n_set or not q.get('review_done')):
        try:
            import review
            fin = review.daily(out, q)
            q['reviewed_n'] = n_set
            if fin and not q.get('review_done'):
                q['review_done'] = now_jst().isoformat()
                log(out, 'REVIEW_DONE', 'daily_summary.md')
                try:                                             # 改善の仕組み: 昇格・戻す・引退・新候補
                    import registry
                    ev_ = registry.step(out.parent, log=lambda *a: log(out, *a))
                    q['improve'] = [list(e[:2]) for e in ev_]
                except Exception as e:
                    log(out, 'IMPROVE_FAIL', f'{type(e).__name__}:{str(e)[:160]}')
        except Exception as e:                                   # the review never stops the day
            log(out, 'REVIEW_FAIL', f'{type(e).__name__}:{str(e)[:160]}')
        dump(qp, q)
    report(q, out)
    return q


def _urgent_soon(q, now, within=3):
    """True when a race needs its prediction or 直前見直し within `within` minutes (a 楽天 fetch is ~61 s)."""
    for r in q['races'].values():
        post = datetime.fromisoformat(r['post'])
        if r['state'] == 'DISCOVERED' and now < post - timedelta(minutes=CUTOFF + 1) \
                and post - timedelta(minutes=PRED_FROM + within) <= now:
            return True
        if (r['state'] == 'PREDICTION_COMPLETE' and r.get('delivered') and not r.get('check10')
                and post - timedelta(minutes=CHECK10 + within) <= now < post - timedelta(minutes=CUTOFF + 1)):
            return True
    return False


def done(q):
    return all(r['state'] in ('SETTLED', 'MISSED_DEADLINE') for r in q['races'].values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--day', default=now_jst().strftime('%Y-%m-%d'))
    ap.add_argument('--loop', action='store_true')
    ap.add_argument('--until', default='23:50')
    a = ap.parse_args()
    out = Path(os.environ.get('KM_BAN_OUT', HERE / 'output')) / a.day
    out.mkdir(parents=True, exist_ok=True)
    # share the LOCAL throttle state when both autopilots run in one worker (one >=61 s budget for 楽天)
    reader = RK.Reader(Path(os.environ.get('KM_BAN_SOURCE_STATE', out.parent / 'source_state.json')))
    hist = LazyHist(os.environ.get('KM_BAN_NAR_DIR'))
    log(out, 'START', a.day)
    end = datetime.strptime(f"{a.day} {a.until}", '%Y-%m-%d %H:%M').replace(tzinfo=JST)
    while True:
        q = tick(a.day, out, reader, hist)
        if not a.loop or not q['races'] or done(q) or now_jst() >= end:
            break
        time.sleep(60)
    log(out, 'STOP', 'races', len(q['races']))


if __name__ == '__main__':
    main()

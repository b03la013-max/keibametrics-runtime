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
    menu = RK.parse_menu(reader.card_page(prefix + '01'), prefix)
    races = {}
    for no, rid, hhmm in menu:
        h, m = map(int, hhmm.split(':'))
        post = datetime.strptime(day, '%Y-%m-%d').replace(hour=h, minute=m, tzinfo=JST)
        races[f'{no:02d}'] = {'no': no, 'rid': rid, 'post': post.isoformat(), 'state': 'DISCOVERED'}
    q = {'day': day, 'meeting': prefix, 'races': races}
    dump(out / 'queue.json', q)
    log(out, 'DISCOVERED', prefix, len(races), 'races')
    return q


def predict(reader, q, key, out, hist):
    r = q['races'][key]
    html = reader.card_page(r['rid'])
    card = source.parse_card_ban(html)
    hdr = RK.parse_header(html)
    moisture = source.moisture_from_header(html)
    feeds = {k: source.load_feed(os.environ.get('KM_BAN_FEED_DIR'), q['day'], k) for k in ('kintaro', 'sbo', 'keibabook')}
    if not feeds['kintaro'].get(str(r['no'])):
        cache = Path(os.environ.get('KM_BAN_CACHE', out.parent / '.cache'))
        pdf = kintaro.fetch(q['day'], r['no'], cache / q['day'] / f"qw{q['day'].replace('-', '')}{r['no']:02d}.pdf")
        if pdf:
            try:
                feeds['kintaro'] = {**feeds['kintaro'], str(r['no']): kintaro.parse(pdf)}
            except Exception as e:                       # layout change -> REFERENCE, never a crash
                log(out, 'KINTARO_PARSE_FAIL', key, type(e).__name__)
    horses = source.build_horses(card, moisture, q['day'], hist, feeds, r['no'])
    name = hdr.get('race_name') or ''
    race = {'moisture': moisture, 'special': any(k in name for k in ('特別', '賞', '杯', '記念')) and 'Ｃ' not in name,
            'young': '2歳' in name or '２歳' in name, 'horses': horses}
    ev = engine.evaluate(race)
    tk = tickets.compile_race(ev)
    feeds_present = [k for k, v in feeds.items() if v]
    if not feeds['kintaro'].get(str(r['no'])):                 # barrier evidence missing -> not FORMAL (spec 5-3)
        tk['formality'] = 'REFERENCE-RENDERED'
    label = f"帯広{r['no']}R {r['post'][11:16]}発走"
    text, total = render.render(label, ev, tk, paper=False)
    frozen = now_jst().isoformat()
    sha = hashlib.sha256(json.dumps([tk['trio'], tk['exact']]).encode()).hexdigest()
    rec = {'race': r, 'header': hdr, 'moisture': moisture, 'feeds_present': feeds_present, 'frozen_at': frozen,
           'ticket_sha256': sha, 'evaluation': ev, 'tickets': tk, 'text': text}
    dump(out / f'R{key}.json', rec)
    (out / f'R{key}.md').write_text(text + '\n')
    r.update(state='PREDICTION_COMPLETE', frozen_at=frozen, ticket_sha256=sha, points=total,
             formality=tk['formality'], moisture=moisture)
    log(out, 'PREDICTED', key, total, 'pts', tk['formality'], 'feeds', feeds_present)


def deliver(q, key, out):
    issue = os.environ.get('KM_BAN_DELIVERY_ISSUE')
    r = q['races'][key]
    if not issue or r.get('delivered'):
        return
    text = (out / f'R{key}.md').read_text()
    body = (f"### 🐴 帯広{r['no']}R {r['post'][11:16]}発走｜{r['formality']}\n\n```\n{text}```\n"
            f"<sub>ケイバメトリクスばんえい v4.0-BAN 自動予想。凍結 {r['frozen_at'][11:19]}／券面SHA `{r['ticket_sha256'][:12]}`"
            f"／未較正（確率・EVではありません）</sub>")
    try:
        c = _gh('POST', f'/repos/{REPO}/issues/{issue}/comments', {'body': body})
        r.update(delivered=c['created_at'], delivery_url=c['html_url'])
        log(out, 'DELIVERED', key, c['html_url'])
    except Exception as e:                                       # recorded, retried next tick until cutoff
        r['delivery_error'] = f'{type(e).__name__}:{str(e)[:100]}'
        log(out, 'DELIVERY_FAIL', key, r['delivery_error'])


def first_failure(tk, order):
    w, s, t = order[:3]
    tri = tuple(sorted((w, s, t)))
    if w not in [n for n in tk['terminal']]:
        return 'ROLE'
    if tri not in set(map(tuple, tk['trio'])):
        return 'PAIR-P3-TERMINAL' if any(set((w, s)) <= set(x) for x in tk['trio']) else 'HEAD-P2-TERMINAL'
    if tk['exact'] and (w, s, t) not in set(map(tuple, tk['exact'])):
        return 'EXACT'
    return 'NONE'


def settle_race(reader, q, key, out):
    r = q['races'][key]
    res = ST.parse_result(reader.result_page(r['rid']))
    if res is None:
        return
    rec = json.loads((out / f'R{key}.json').read_text())
    tk = rec['tickets']
    trio_pay = res['payouts'].get('TRIO', {})
    ex_pay = res['payouts'].get('TRIFECTA', {})
    back = sum(trio_pay.get(tuple(t), 0) for t in tk['trio']) + sum(ex_pay.get(tuple(e), 0) for e in tk['exact'])
    stake = tk['points'] * 100
    out_res = {'order': res['order'], 'payouts': {k: {'-'.join(map(str, c)): y for c, y in v.items()}
                                                   for k, v in res['payouts'].items()},
               'stake': stake, 'return': back, 'pfs': round(100 * back / stake, 1) if stake else None,
               'first_failure_layer': first_failure(tk, res['order']), 'formality': r.get('formality'),
               'settled_at': now_jst().isoformat()}
    dump(out / f'R{key}.result.json', out_res)
    r.update(state='SETTLED', pfs=out_res['pfs'], ffl=out_res['first_failure_layer'])
    log(out, 'SETTLED', key, res['order'][:3], 'PFS', out_res['pfs'], out_res['first_failure_layer'])


def report(q, out):
    L = [f"# 帯広 {q['day']} ばんえい自動予想（v4.0-BAN）", '', '| R | 発走 | 状態 | 点数 | 区分 | 配信 | PFS | 最初の断線 |',
         '|---|---|---|---|---|---|---|---|']
    st = sk = 0
    for k, r in sorted(q['races'].items()):
        L.append(f"| {r['no']} | {r['post'][11:16]} | {r['state']} | {r.get('points', '')} | {r.get('formality', '')} | "
                 f"{'済' if r.get('delivered') else ''} | {r.get('pfs', '')} | {r.get('ffl', '')} |")
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
    for key, r in sorted(q['races'].items()):
        post = datetime.fromisoformat(r['post'])
        try:
            if r['state'] == 'DISCOVERED' and post - timedelta(minutes=PRED_FROM) <= now < post - timedelta(minutes=CUTOFF + 1):
                predict(reader, q, key, out, hist)
            if r['state'] == 'PREDICTION_COMPLETE' and not r.get('delivered') and now < post - timedelta(minutes=CUTOFF):
                deliver(q, key, out)
            if r['state'] == 'DISCOVERED' and now >= post - timedelta(minutes=CUTOFF + 1):
                r['state'] = 'MISSED_DEADLINE'
                log(out, 'MISSED_DEADLINE', key)
            if r['state'] == 'PREDICTION_COMPLETE' and now >= post + timedelta(minutes=RESULT_AFTER):
                settle_race(reader, q, key, out)
        except RK.SourceStop as e:
            log(out, 'SOURCE_HOLD', key, e)
            break
        except Exception as e:                                   # one race never stops the day
            r['last_error'] = f'{type(e).__name__}:{str(e)[:160]}'
            log(out, 'ERROR', key, r['last_error'])
        dump(qp, q)
    report(q, out)
    return q


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

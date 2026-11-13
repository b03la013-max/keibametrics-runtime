"""LOCAL race-day autopilot tick (South Kanto).

Each tick (GitHub Actions cron, every 10 min) does:
  1. discover today's South-Kanto meetings from the official NANKAN calendar
     (plan cached in output/<date>/plan.json);
  2. 朝版 (morning edition): every race without a prediction yet;
  3. 直前版 (final edition): races whose post time is 8-45 min away get a
     re-read of card (body weight, scratches) + current odds, then re-predicted.
Outputs Markdown + JSON under runtime/local_autopilot/output/<date>/.
Prediction only (PAPER). No purchase, no external notification.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from runtime.local_autopilot import engine
from runtime.local_autopilot import rakuten as rk

JST = timezone(timedelta(hours=9))
ROOT = Path(__file__).resolve().parent / 'output'
QUAD = {1: '① 絶対×妙味 → 単勝勝負', 2: '② 絶対×配当不足 → 1着固定で配当化',
        3: '③ 不安×妙味 → 複勝系（下限割れはワイド）', 4: '④ 不安×配当不足 → 軸は最小、相手・3列目で妙味'}


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1, default=str) + '\n')


def f0(x):
    return '–' if x is None else f'{x:.0f}'


def render(race, res, edition, odds_at):
    a = res['aki']
    post = race['scheduled_post_at'][11:16]
    L = [f"## {race['venue_name']}{race['race_no']}R {post}発走　{race['race_name']}",
         f"{race.get('distance') or '?'}m／{len(res['rows'])}頭　**{edition}**"
         f"（オッズ {odds_at or '未取得'}）",
         '', f"- 展開：{res['pace']}", f"- レース型（§30）：**{res['race_type']}**", '',
         '| 印 | 馬番 | 馬名 | 騎手 | 単勝 | 人気 | TPI-L | SRI-L | EVI | NCI | T3I | F3S | OPI-V | p勝(暫定) | 役割 |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for x in res['order']:
        L.append(f"| {x['mark'] or ''} | {x['no']} | {x['name']} | {x['jockey'] or ''} | "
                 f"{'' if not x['win'] else x['win']} | {x.get('pop', '')} | {f0(x['TPIF'])} | {f0(x['SRI'])} | "
                 f"{f0(x['EVI'])} | {f0(x['NCI'])} | {f0(x['T3I'])} | {f0(x['F3S'])} | {f0(x['OPI'])} | "
                 f"{x['p_win'] * 100:.0f}% | {x['role']} |")
    h = res['order'][0]
    ev = '–' if res['tan_ev'] is None else f"{res['tan_ev']:+.2f}"
    L += ['', '**本命判定エンジン（§12）**', '',
          f"- WCI {res['wci']}／本命不安 {res['fuan']}（{'、'.join(res['fuan_reasons']) or 'なし'}）／逆転候補 {res['reversal']}頭",
          f"- 信頼ゲート：**{res['gate']}**　単勝EV（暫定）：{ev}",
          f"- 象限：**{QUAD[res['quad']]}**", '',
          f"**AKI-v2（§19）** W-AKI {a['W']}／P-AKI {a['P']}／ASI {a['ASI']}／RSI {a['RSI']}／堅決着補正 −{a['katai']} → "
          f"総合 {a['total']}（タイプ{a['type']}・{a['form']}型）", '',
          '必須チェック：' + '／'.join(f"{k} {'YES' if v else 'NO'}" for k, v in res['checks'].items()), '',
          '**買い目（ペーパー）**', '', '| 券種 | 買い目 | 点数 | 資金 | 備考 |', '|---|---|---|---|---|']
    for t in res['tickets']:
        L.append(f"| {t['k']} | {t['b']} | {t['pt']} | {t['st']} | {t.get('note', '')} |")
    notes = sorted({f for x in res['rows'] for f in x['flags'] if 'NEUTRAL' in f})
    L += ['', f"<sub>未較正ペーパー。p勝はF3Sのsoftmaxと単勝人気の50:50合成。CCI（厩舎コメント）は"
              f"未取得のため中立52。複勝オッズ未取得のため複勝はワイドへルーティング。馬場：{race.get('going') or '不明'}。{' '.join(notes)}</sub>", '']
    return '\n'.join(L)


def plan_for(reader, day, out):
    path = out / 'plan.json'
    if path.exists():
        return json.loads(path.read_text())
    venues = reader.meetings(day)
    log('MEETINGS', venues)
    plan = {'race_date': day, 'created_at': datetime.now(JST).isoformat(), 'venues': {}, 'source': 'keiba.rakuten.co.jp'}
    for code, prefix in sorted(venues.items()):
        vid, vname = rk.VENUES[code]
        html = reader.card_page(prefix + '01')
        menu = rk.parse_menu(html, prefix)
        plan['venues'][vid] = [{'venue_id': vid, 'venue_name': vname, 'venue_code': code, 'race_no': n,
                                'rid': rid, 'race_date': day, 'race_name': '',
                                'scheduled_post_at': f'{day}T{hhmm.zfill(5)}:00+09:00'} for n, rid, hhmm in menu]
    dump(path, plan)
    return plan


def predict_race(reader, race, today, edition):
    html = reader.card_page(race['rid'])
    fetched = datetime.now(JST).isoformat()
    head = rk.parse_header(html)
    runners, excluded = rk.parse_card(html)
    race = dict(race, distance=head['distance'], race_name=head['race_name'], class_text=head['race_name'],
                surface=head['surface'], going=head['going'])
    odds = {r['horse_no']: {'win': r['win_odds'], 'place_low': None, 'cancelled': False} for r in runners}
    res = engine.predict(race, runners, odds, today)
    md = render(race, res, edition, fetched[11:16] + '時点' if any(r['win_odds'] for r in runners) else None)
    slim = {k: v for k, v in res.items() if k not in ('rows', 'order', 'ana')}
    slim['ranking'] = [{k: x[k] for k in ('mark', 'no', 'name', 'jockey', 'win', 'TPIF', 'SRI', 'EVI', 'NCI',
                                         'T3I', 'F3S', 'OPI', 'p_win', 'role')} for x in res['order']]
    return md, {'race': race, 'edition': edition, 'card_fetched_at': fetched, 'going': head['going'],
                'scratched': [e.get('name') for e in excluded], 'prediction': slim, 'paper': True, 'calibrated': False}


def index(out, plan):
    L = [f"# ケイバメトリクス地方版 オートパイロット {plan['race_date']}", '',
         '楽天競馬の公開出馬表（robots.txt許可範囲・60秒間隔）から v4.3 を自動計算。未較正ペーパー（購入なし）。', '']
    for venue, races in plan['venues'].items():
        L += [f"## {races[0]['venue_name']}", '', '| R | 発走 | レース | 版 | 本命 | 象限 | AKI | 買い目 |',
              '|---|---|---|---|---|---|---|---|']
        for r in races:
            p = out / f"{venue}_{r['race_no']:02d}.json"
            if p.exists():
                d = json.loads(p.read_text())
                pr = d['prediction']
                top = pr['ranking'][0]
                L.append(f"| [{r['race_no']}R]({venue}_{r['race_no']:02d}.md) | {r['scheduled_post_at'][11:16]} | "
                         f"{r['race_name']} | {d['edition']} | ◎{top['no']} {top['name']} | {pr['quad']} | "
                         f"{pr['aki']['total']}/{pr['aki']['form']} | "
                         + '<br>'.join(f"{t['k']} {t['b']}" for t in pr['tickets'][:2]) + ' |')
            else:
                err = out / f"{venue}_{r['race_no']:02d}.error.json"
                L.append(f"| {r['race_no']}R | {r['scheduled_post_at'][11:16]} | {r['race_name']} | "
                         f"{'取得失敗' if err.exists() else '未作成'} | | | | |")
        L.append('')
    (out / 'README.md').write_text('\n'.join(L) + '\n')


LOG = []


def log(*parts):
    line = datetime.now(JST).strftime('%H:%M:%S ') + ' '.join(str(p) for p in parts)
    print(line, flush=True)
    LOG.append(line)


def flush_log(out):
    out.mkdir(parents=True, exist_ok=True)
    with (out / 'autopilot_log.txt').open('a') as fh:
        fh.write('\n'.join(LOG) + '\n')
    LOG.clear()


def tick(day=None, now=None, budget_seconds=480, only=None, reader=None):
    now = now or datetime.now(JST)
    day = day or now.date().isoformat()
    try:
        return _tick(day, now, budget_seconds, only, reader)
    finally:
        flush_log(ROOT / day)


def _tick(day, now, budget_seconds, only, reader):
    today = date.fromisoformat(day)
    out = ROOT / day
    reader = reader or rk.Reader(ROOT / 'source_state.json')
    started = time.monotonic()
    try:
        plan = plan_for(reader, day, out)
    except rk.SourceStop as exc:
        log('SOURCE_STOP', exc)
        return 3
    except Exception as exc:
        log('PLAN_HOLD', type(exc).__name__, getattr(exc, 'receipt', exc), traceback.format_exc()[-800:])
        return 2
    if not plan['venues']:
        log('NO_LOCAL_MEETING', day)
        return 0
    jobs = []
    for venue, races in plan['venues'].items():
        for r in races:
            if only and r['race_no'] not in only:
                continue
            post = datetime.fromisoformat(r['scheduled_post_at'])
            stem = out / f"{venue}_{r['race_no']:02d}"
            js = stem.with_suffix('.json')
            have = json.loads(js.read_text())['edition'] if js.exists() else None
            mins = (post - now).total_seconds() / 60
            if mins < 3:
                continue
            if have != '直前版' and mins <= 45:
                jobs.append((mins, r, '直前版', stem))
            elif have is None:
                jobs.append((100 + mins, r, '朝版', stem))
    jobs.sort(key=lambda j: j[0])
    log('TICK', day, 'venues', list(plan['venues']), 'jobs', len(jobs))
    done = 0
    for _, r, edition, stem in jobs:
        if time.monotonic() - started > budget_seconds:
            log('BUDGET_STOP remaining', len(jobs) - done)
            break
        try:
            md, data = predict_race(reader, r, today, edition)
            stem.with_suffix('.md').write_text(md)
            dump(stem.with_suffix('.json'), data)
            err = stem.with_suffix('.error.json')
            if err.exists():
                err.unlink()
            log('OK', r['venue_id'], r['race_no'], edition)
        except rk.SourceStop as exc:
            log('SOURCE_STOP', exc)
            break
        except Exception as exc:
            dump(stem.with_suffix('.error.json'), {'race': r, 'error': type(exc).__name__,
                 'receipt': getattr(exc, 'receipt', str(exc)), 'at': datetime.now(JST).isoformat(),
                 'trace': traceback.format_exc()[-1500:]})
            log('HOLD', r['venue_id'], r['race_no'], type(exc).__name__, getattr(exc, 'receipt', exc))
        done += 1
    index(out, plan)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date')
    ap.add_argument('--races', help='comma-separated race numbers to restrict')
    ap.add_argument('--budget', type=int, default=480)
    a = ap.parse_args()
    only = {int(x) for x in a.races.split(',')} if a.races else None
    sys.exit(tick(a.date, budget_seconds=a.budget, only=only))


if __name__ == '__main__':
    main()

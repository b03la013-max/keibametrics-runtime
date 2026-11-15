"""KeibaMetrics LOCAL race-day autopilot (all NAR venues except ばんえい).

One `tick` = one pass over the day's race QUEUE (every discovered race is kept
with an explicit state until the day is closed):

  DISCOVERED -> SOURCE_READY -> PREDICTION_COMPLETE -> PRESTART_PUSH_VERIFIED
  (delivery ladder per revision: GENERATED/FROZEN -> COMMITTED -> PUSH_VERIFIED ->
   LINK_AVAILABLE; USER_DELIVERY_SENT / USER_REACHED / USER_ACK_VERIFIED are
   NOT_CONNECTED: a GitHub push is not proof that the user received it)
  side states: SOURCE_HOLD (access refused/held), PREDICTION_FAILURE (retried
  up to 3x), MISSED_DEADLINE (no edition before cutoff), POSTRESULT_DIAGNOSTIC
  (official result read, PAPER settlement done).

Priority inside a tick: 直前版 (post-45..post-3 min) > 朝版 (earliest post
first) > post-result settlement. Every Rakuten request keeps >=61 s spacing
(persisted in source_state.json across runs). Files are written only when
something changed, so idle ticks produce no commit.

Outputs (KM_LOCAL_AUTOPILOT_OUT, default runtime/local_autopilot/output):
  <date>/README.md            day completion gate + per-race table
  <date>/queue.json           race states, post-time changes, revisions
  <date>/<VENUE>_<RR>.md/json paper prediction (latest edition)
  <date>/<VENUE>_<RR>.shadow29.json  official 29-index arithmetic (shadow)
  <date>/<VENUE>_<RR>.result.json    official result + PAPER settlement
  <date>/metrics.jsonl, autopilot_log.txt
PAPER only: no purchase, no external notification, no Formal claim.
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import json
import os
import sys
import time
import traceback
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from runtime.local_autopilot import engine
from runtime.local_autopilot import rakuten as rk
from runtime.local_autopilot import settle

JST = timezone(timedelta(hours=9))
ROOT = Path(os.environ.get('KM_LOCAL_AUTOPILOT_OUT') or Path(__file__).resolve().parent / 'output')
QUAD = {1: '① 絶対×妙味 → 単勝勝負', 2: '② 絶対×配当不足 → 1着固定で配当化',
        3: '③ 不安×妙味 → 複勝系（下限割れはワイド）', 4: '④ 不安×配当不足 → 軸は最小、相手・3列目で妙味'}
FINAL_WINDOW_MIN = 45
CUTOFF_MIN = 3          # Rakuten closes voting 2 min before post; we freeze 3 min before
MAX_ATTEMPTS = 3
RESULT_DELAY_MIN = 20
CODE_VERSION = hashlib.sha256(b''.join(
    (Path(__file__).resolve().parent / f).read_bytes() for f in ('engine.py', 'run.py', 'rakuten.py', 'settle.py'))).hexdigest()[:12]
LOG = []


def now_jst():
    return datetime.now(JST)


def log(*parts):
    line = now_jst().strftime('%H:%M:%S ') + ' '.join(str(p) for p in parts)
    print(line, flush=True)
    LOG.append(line)


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, ensure_ascii=False, indent=1, default=str) + '\n'
    if path.exists() and path.read_text() == text:
        return False
    path.write_text(text)
    return True


def f0(x):
    return '–' if x is None else f'{x:.0f}'


# --------------------------------------------------------------------- render
# Report probability input provenance; do not alter the uncalibrated PAPER model.
def probability_source_note(rows):
    available = sum(row.get('p_market') is not None for row in rows)
    count = len(rows)
    if not available:
        return 'p勝はF3S softmaxのみ（単勝オッズ由来市場確率なし・実勝率ではない）'
    if available == count:
        return 'p勝はF3S softmaxと単勝オッズ由来市場確率の50:50合成（未較正・実勝率ではない）'
    return (f'p勝は市場確率あり{available}/{count}頭のみ50:50合成、他はF3S softmaxのみ'
            '（部分オッズ時の全頭確率合計は100%未保証・実勝率ではない）')


def render(race, res, edition, src_at, shadow=None, revision=None):
    a = res['aki']
    L = [f"## {race['venue_name']}{race['race_no']}R {race['post_current'][11:16]}発走　{race.get('race_name', '')}",
         f"{race.get('distance') or '?'}m／{len(res['rows'])}頭　**{edition}**（出馬表取得 {src_at[11:16]}／単勝オッズ {sum(x.get('win') is not None for x in res['rows'])}/{len(res['rows'])}頭）"
         + (f"　改訂理由：{revision}" if revision else ''),
         '', f"- 展開：{res['pace']}", f"- レース型（§30）：**{res['race_type']}**"]
    if race.get('scratched'):
        L.append(f"- 取消・除外：{'、'.join(race['scratched'])}（予測・買い目から除外済み）")
    if race.get('newcomers'):
        L.append(f"- 過去走なし（新馬等）：{race['newcomers']}頭 → 能力・展開系は UNKNOWN（中立52）で計算")
    missing_jockey = [x for x in res['order'] if not str(x.get('jockey') or '').strip()]
    if missing_jockey:
        names = '、'.join(f"{x['no']}番{x['name']}" for x in missing_jockey)
        L.append(f"- 騎手情報未取得：{names}（UNKNOWN／未補完。役割・券面は暫定、発走前の変更照合が必要）")
    L += ['', '| 印 | 馬番 | 馬名 | 騎手 | 単勝 | 人気 | TPI-L | SRI-L | EVI | NCI | T3I | F3S | OPI-V | p勝(暫定) | 役割 |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for x in res['order']:
        L.append(f"| {x['mark'] or ''} | {x['no']} | {x['name']} | {x['jockey'] or 'UNKNOWN（未取得）'} | "
                 f"{'' if not x['win'] else x['win']} | {x.get('pop', '')} | {f0(x['TPIF'])} | {f0(x['SRI'])} | "
                 f"{f0(x['EVI'])} | {f0(x['NCI'])} | {f0(x['T3I'])} | {f0(x['F3S'])} | {f0(x['OPI'])} | "
                 f"{x['p_win'] * 100:.0f}% | {x['role']} |")
    ev = '–' if res['tan_ev'] is None else f"{res['tan_ev']:+.2f}"
    L += ['', '**本命判定エンジン（§12）**', '',
          f"- WCI {res['wci']}／本命不安 {res['fuan']}（{'、'.join(res['fuan_reasons']) or 'なし'}）／逆転候補 {res['reversal']}頭",
          f"- 信頼ゲート：**{res['gate']}**　単勝EV（暫定・未較正。資金判断に使わない）：{ev}",
          f"- 象限：**{QUAD[res['quad']]}**", '',
          f"**AKI-v2（§19）** W-AKI {a['W']}／P-AKI {a['P']}／ASI {a['ASI']}／RSI {a['RSI']}／堅決着補正 −{a['katai']} → "
          f"総合 {a['total']}（タイプ{a['type']}・{a['form']}型）", '',
          '必須チェック：' + '／'.join(f"{k} {'YES' if v else 'NO'}" for k, v in res['checks'].items()), '',
          '**買い目（ペーパー・PAPER試算は1点100円固定。資金配分ではない）**', '',
          '| 券種 | 買い目 | 点数 | 水準 | 備考 |', '|---|---|---|---|---|']
    for t in res['tickets']:
        L.append(f"| {t['k']} | {t['b']} | {t['pt']} | {t['st']} | {t.get('note', '')} |")
    if shadow and not shadow.get('error'):
        tc = shadow['terminal_counts']
        L += ['', f"**公式29指数シャドー（FULL29_SHADOW_PAPER・正式SOURCE不成立・消費権限なし）** "
                  f"{shadow['runner_count']}頭×29＝{shadow['cells']}セル：CALCULATED {tc['CALCULATED']}／RULED-NEUTRAL {tc['RULED-NEUTRAL']}"
                  f"／未解決 {tc['UNRESOLVED'] + tc['RULED-HOLD'] + tc['NOT-APPLICABLE']}。F3S-L順：{'-'.join(map(str, shadow['f3s_order'][:6]))}。"
                  f"KRS：入力構築{'済' if shadow['krs']['input_built'] else '不可'}・実試行0（外部Engine未接続）"]
    elif shadow:
        L += ['', f"公式29指数シャドー：実行不可（{shadow['error']}）"]
    notes = sorted({f for x in res['rows'] for f in x['flags'] if 'NEUTRAL' in f})
    L += ['', f"<sub>未較正ペーパー。{probability_source_note(res['rows'])}。CCI（厩舎コメント）は"
              f"未取得のため中立52。複勝オッズ未取得のため複勝はワイドへルーティング。馬場：{race.get('going') or '不明'}。{' '.join(notes)}</sub>", '']
    return '\n'.join(L)


# ---------------------------------------------------------------------- queue
def load_queue(out):
    p = out / 'queue.json'
    return json.loads(p.read_text()) if p.exists() else None


def discover(reader, day, out, cards):
    venues = reader.meetings(day)
    log('MEETINGS', venues)
    q = {'race_date': day, 'source': 'keiba.rakuten.co.jp', 'discovered_at': now_jst().isoformat(),
         'venues': {}, 'races': {}, 'timings': {}}
    for code, prefix in sorted(venues.items()):
        vid, vname = rk.VENUES[code]
        rid1 = prefix + '01'
        html = reader.card_page(rid1)
        cards[rid1] = (html, now_jst().isoformat())  # reused as the 1R source in this tick
        menu = rk.parse_menu(html, prefix)
        q['venues'][vid] = {'name': vname, 'code': code, 'races': len(menu)}
        for n, rid, hhmm in menu:
            post = f'{day}T{hhmm.zfill(5)}:00+09:00'
            q['races'][f'{vid}_{n:02d}'] = {'venue_id': vid, 'venue_name': vname, 'race_no': n, 'rid': rid,
                'race_date': day, 'post_initial': post, 'post_current': post, 'post_changes': [],
                'status': 'DISCOVERED', 'editions': [], 'attempts': 0, 'last_error': None}
    q['timings']['plan_complete_at'] = now_jst().isoformat()
    return q


def rediscover(reader, day, q, cards):
    """Race day, queue pre-built on an earlier day: add venues listed since."""
    q['timings']['rediscovered_at'] = now_jst().isoformat()
    known = {v['code'] for v in q['venues'].values()}
    added = []
    for code, prefix in sorted(reader.meetings(day).items()):
        if code in known:
            continue
        vid, vname = rk.VENUES[code]
        rid1 = prefix + '01'
        html = reader.card_page(rid1)
        cards[rid1] = (html, now_jst().isoformat())
        menu = rk.parse_menu(html, prefix)
        q['venues'][vid] = {'name': vname, 'code': code, 'races': len(menu)}
        for n, rid, hhmm in menu:
            post = f'{day}T{hhmm.zfill(5)}:00+09:00'
            q['races'][f'{vid}_{n:02d}'] = {'venue_id': vid, 'venue_name': vname, 'race_no': n, 'rid': rid,
                'race_date': day, 'post_initial': post, 'post_current': post, 'post_changes': [],
                'status': 'DISCOVERED', 'editions': [], 'attempts': 0, 'last_error': None}
        added.append(vid)
    log('REDISCOVER', day, 'added', added)
    return True


def cutoff(r):
    return datetime.fromisoformat(r['post_current']) - timedelta(minutes=CUTOFF_MIN)


def predict(reader, r, today, edition, out, cards):
    t0 = time.monotonic()
    if r['rid'] in cards:
        html, fetched = cards.pop(r['rid'])
    else:
        html = reader.card_page(r['rid'])
        fetched = now_jst().isoformat()
    r['status'] = 'SOURCE_READY'
    r['source_fetched_at'] = fetched
    t1 = time.monotonic()
    head = rk.parse_header(html)
    # P0-5 post-time change: apply only if observed before the currently known cutoff
    if head.get('post'):
        observed = f"{r['race_date']}T{head['post'].zfill(5)}:00+09:00"
        if observed != r['post_current']:
            applied = datetime.fromisoformat(fetched) < cutoff(r)
            r['post_changes'].append({'old': r['post_current'], 'new': observed, 'observed_at': fetched, 'applied': applied})
            if applied:
                r['post_current'] = observed
            log('POST_TIME_CHANGE', r['venue_id'], r['race_no'], r['post_changes'][-1])
    runners, excluded = rk.parse_card(html)
    race = dict(r, distance=head['distance'], race_name=head['race_name'], class_text=head['race_name'],
                surface=head['surface'], going=head['going'], scheduled_post_at=r['post_current'],
                scratched=[e['name'] for e in excluded],
                newcomers=sum(1 for x in runners if not x['starts']))
    odds = {x['horse_no']: {'win': x['win_odds'], 'place_low': None, 'cancelled': False} for x in runners}
    res = engine.predict(race, runners, odds, today)
    t2 = time.monotonic()
    stem = out / f"{r['venue_id']}_{r['race_no']:02d}"
    # P0-6 revision reason
    revision = None
    prev = json.loads(stem.with_suffix('.json').read_text()) if stem.with_suffix('.json').exists() else None
    if prev:
        prev_top = prev['prediction']['ranking'][0]['no']
        if any(prev_top == x.get('horse_no') for x in excluded) or prev_top not in [x['horse_no'] for x in runners]:
            revision = f"前版の本命{prev_top}番が取消→最新出馬表で再予測"
        elif set(prev.get('scratched', [])) != set(race['scratched']):
            revision = '取消・除外の変化を反映して再予測'
        else:
            revision = '直前の馬体重・オッズ・騎手を反映して再予測'
    try:
        shadow = __import__('runtime.local_autopilot.shadow29', fromlist=['run']).run(race, runners, html, fetched)
        dump(stem.with_name(stem.name + '.shadow29.json'), shadow)
    except Exception as exc:
        shadow = {'error': f'{type(exc).__name__}:{str(exc)[:200]}'}
    t3 = time.monotonic()
    md = render(race, res, edition, fetched, shadow, revision)
    slim = {k: v for k, v in res.items() if k not in ('rows', 'order', 'ana')}
    slim['ranking'] = [{k: x[k] for k in ('mark', 'no', 'name', 'jockey', 'win', 'TPIF', 'SRI', 'EVI', 'NCI',
                                         'T3I', 'F3S', 'OPI', 'p_win', 'role')} for x in res['order']]
    saved_at = now_jst().isoformat()
    src_sha = hashlib.sha256(html.encode()).hexdigest()
    ticket_sha = hashlib.sha256(json.dumps(slim['tickets'], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    rev_n = len(r['editions']) + 1
    rev_dir = out / 'rev'
    rev_dir.mkdir(parents=True, exist_ok=True)
    while (rev_dir / f"{stem.name}.r{rev_n}.json").exists():  # never overwrite a frozen revision
        rev_n += 1
    rev_id = f"{stem.name}.r{rev_n}"
    prev_rev = r['editions'][-1].get('rev') if r['editions'] else None
    frozen = {'race_id': r['rid'], 'race_key': stem.name, 'revision_id': rev_id, 'previous_revision': prev_rev,
              'edition': edition, 'revision_reason': revision, 'source_fetched_at': fetched,
              'source_snapshot_sha256': src_sha, 'frozen_at': saved_at, 'saved_at': saved_at,
              'cutoff': cutoff(r).isoformat(), 'post_time': r['post_current'],
              'runners': [{'no': x['horse_no'], 'name': x['name']} for x in runners],
              'scratched': race['scratched'], 'roles': {'W': res['order'][0]['no'],
                                                         'P2': res['order'][1]['no'] if len(res['order']) > 1 else None,
                                                         'P3': res['order'][2]['no'] if len(res['order']) > 2 else None},
              'ticket_sha256': ticket_sha, 'prediction': slim, 'paper': True, 'calibrated': False}
    (rev_dir / f"{rev_id}.json").write_text(json.dumps(frozen, ensure_ascii=False, indent=1, default=str) + '\n')
    (rev_dir / f"{rev_id}.md").write_text(md)
    stem.with_suffix('.md').write_text(md)
    dump(stem.with_suffix('.json'), {'race': {k: race[k] for k in ('venue_id', 'venue_name', 'race_no', 'rid', 'race_date',
                                                                  'post_current', 'distance', 'race_name', 'going', 'surface')},
                                     'edition': edition, 'card_fetched_at': fetched, 'saved_at': saved_at,
                                     'revision_id': rev_id, 'source_snapshot_sha256': src_sha, 'ticket_sha256': ticket_sha,
                                     'revision': revision, 'scratched': race['scratched'], 'newcomers': race['newcomers'],
                                     'active_runners': len(runners), 'prediction': slim, 'paper': True, 'calibrated': False})
    r['status'] = 'PREDICTION_COMPLETE'
    r['editions'].append({'edition': edition, 'rev': rev_id, 'source_sha256': src_sha, 'ticket_sha256': ticket_sha,
                          'source_fetched_at': fetched, 'saved_at': saved_at, 'frozen_at': saved_at, 'revision': revision,
                          'delivery': {'GENERATED': saved_at, 'FROZEN': saved_at, 'COMMITTED': None, 'PUSH_VERIFIED': None,
                                       'LINK_AVAILABLE': None, 'USER_DELIVERY_SENT': 'NOT_CONNECTED',
                                       'USER_REACHED': 'NOT_CONNECTED', 'USER_ACK_VERIFIED': 'NOT_CONNECTED'},
                          'before_cutoff': datetime.fromisoformat(saved_at) < cutoff(r),
                          'top': res['order'][0]['no'], 'quad': res['quad'], 'aki_form': res['aki']['form']})
    r['active_runners'] = len(runners)
    r['scratched'] = race['scratched']
    r['last_error'] = None
    return {'fetch_s': round(t1 - t0, 2), 'compute_s': round(t2 - t1, 2), 'shadow_s': round(t3 - t2, 2)}


DATA_REMOTE = 'origin/local-autopilot-data'
REPO_URL = 'https://github.com/b03la013-max/keibametrics-runtime/blob/local-autopilot-data/output/'


def _git(out, *args):
    try:
        return subprocess.run(['git', '-C', str(out), *args], capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        return ''


def mark_delivery(q, out):
    """Per revision: COMMITTED (local commit containing the frozen file) and
    PUSH_VERIFIED (that commit is on the remote-tracking data branch, whose
    blob bytes equal the frozen file). Pre-cutoff status needs PUSH_VERIFIED
    before cutoff. User delivery/ACK is NOT_CONNECTED and never inferred."""
    changed = False
    for key, r in q['races'].items():
        if r['status'] == 'PRESTART_DELIVERED':  # legacy label (13 Nov): local commit time only
            r['status'] = 'PRESTART_COMMITTED_LEGACY'
            changed = True
        for e in r['editions']:
            d = e.get('delivery')
            if not d:
                continue
            # Old PAPER records stamped PUSH_VERIFIED with the commit clock,
            # not the time of remote blob readback. Preserve that historical
            # timestamp as unverified evidence; recheck the blob at a real clock.
            if d.get('PUSH_VERIFIED') and d.get('PUSH_VERIFIED_TIME_BASIS') != 'READBACK_OBSERVED_AT':
                d['PUSH_VERIFIED_LEGACY_COMMIT_CLOCK'] = d.pop('PUSH_VERIFIED')
                changed = True
            if d.get('PUSH_VERIFIED'):
                continue
            rel = f"{q['race_date']}/rev/{e['rev']}.json"
            path = out / 'rev' / f"{e['rev']}.json"
            if not d.get('COMMITTED'):
                line = _git(out, 'log', '-1', '--format=%H %cI', '--', str(path))
                if line:
                    d['COMMITTED'] = line.split()[1]
                    d['commit_sha'] = line.split()[0]
                    changed = True
            if d.get('COMMITTED'):
                line = _git(out, 'log', '-1', '--format=%H %cI', DATA_REMOTE, '--', str(path))
                if line and path.exists():
                    blob = _git(out, 'show', f"{DATA_REMOTE}:output/{rel}")
                    if blob and blob.strip() == path.read_text().strip():
                        # The Git commit's %cI is NOT the time the remote push was
                        # observed. Backdating with %cI can falsely certify a
                        # post-cutoff push as pre-start. Use the readback clock.
                        d['PUSH_VERIFIED'] = now_jst().isoformat()
                        d['PUSH_VERIFIED_TIME_BASIS'] = 'READBACK_OBSERVED_AT'
                        d['remote_commit_sha'] = line.split()[0]
                        d['LINK_AVAILABLE'] = REPO_URL + rel
                        changed = True
        pre = [e for e in r['editions'] if e.get('delivery', {}).get('PUSH_VERIFIED_TIME_BASIS') == 'READBACK_OBSERVED_AT'
               and e['delivery'].get('PUSH_VERIFIED')
               and datetime.fromisoformat(e['delivery']['PUSH_VERIFIED']) < cutoff(r)]
        if pre and r['status'] in ('PREDICTION_COMPLETE', 'SOURCE_READY', 'PRESTART_PUSH_VERIFIED'):
            observed = pre[-1]['delivery']['PUSH_VERIFIED']
            if r['status'] != 'PRESTART_PUSH_VERIFIED' or r.get('push_verified_at') != observed:
                r['status'] = 'PRESTART_PUSH_VERIFIED'
                r['push_verified_at'] = observed
                changed = True
        elif not pre and (r['status'] == 'PRESTART_PUSH_VERIFIED' or 'push_verified_at' in r):
            # Never leave a stale pre-start summary certified by the legacy
            # commit clock when observation was late or the blob mismatched.
            if r['status'] == 'PRESTART_PUSH_VERIFIED':
                r['status'] = 'PREDICTION_COMPLETE'
            r.pop('push_verified_at', None)
            changed = True
    return changed


def frozen_prediction(r, out, key):
    """The last revision frozen before cutoff (immutable rev file), else the
    legacy latest file if it was saved before cutoff (13 Nov races)."""
    pre = [e for e in r['editions'] if datetime.fromisoformat(e.get('frozen_at') or e['saved_at']) < cutoff(r)]
    for e in reversed(pre):
        if e.get('rev') and (out / 'rev' / f"{e['rev']}.json").exists():
            return out / 'rev' / f"{e['rev']}.json"
    pj = out / f'{key}.json'
    if pre and pj.exists() and datetime.fromisoformat(json.loads(pj.read_text())['saved_at']) < cutoff(r):
        return pj
    return None


def report(q, out):
    races = q['races']
    n = len(races)
    pre = [r for r in races.values() if any(e['before_cutoff'] for e in r['editions'])]
    morning = [r for r in races.values() if any(e['edition'] == '朝版' for e in r['editions'])
               or any(e['before_cutoff'] for e in r['editions'])]
    missed = [r for r in races.values() if r['status'] == 'MISSED_DEADLINE']
    fails = [r for r in races.values() if r['status'] in ('PREDICTION_FAILURE', 'SOURCE_HOLD')]
    delivered = [r for r in races.values() if r.get('push_verified_at')]
    legacy = [r for r in races.values() if r['status'] == 'PRESTART_COMMITTED_LEGACY']
    first_fail = next((f"{k} {r['last_error']}" for k, r in sorted(races.items(), key=lambda kv: kv[1]['post_current'])
                       if r.get('last_error')), 'なし')
    t = q['timings']
    pct = lambda a: f"{len(a)}/{n}（{100 * len(a) / n:.0f}%）" if n else '0/0'
    L = [f"# ケイバメトリクス地方版 オートパイロット {q['race_date']}", '',
         '楽天競馬の公開出馬表（robots.txt許可範囲・61秒間隔）から v4.3 PAPER を自動計算し、公式29指数の算術をシャドー実行。'
         '未較正・購入なし・正式Productionではない。', '',
         '## 全日Completion Gate', '',
         '| 指標 | 実績 |', '|---|---|',
         f"| 開催場Discovery | {len(q['venues'])}場（{'・'.join(v['name'] for v in q['venues'].values())}） |",
         f"| Race Discovery | {n}R |",
         f"| 発走前予測完成 | {pct(pre)} |",
         f"| 発走前GitHub push検証（実バイト照合） | {pct(delivered)}{f'（旧判定・push未検証 {len(legacy)}R）' if legacy else ''} |",
         "| 本人Delivery／到達／ACK | 未接続（GitHub保存は本人受領の証拠ではない） |",
         f"| 朝版または発走前版あり | {pct(morning)} |",
         f"| 未作成（MISSED_DEADLINE） | {len(missed)}R |",
         f"| 失敗・保留 | {len(fails)}R |", f"| 最初の失敗 | {first_fail} |",
         f"| 初回起動 / Plan完成 / 初予想 / 全Race初版完成 | {t.get('first_tick_at', '–')[11:19]} / {t.get('plan_complete_at', '–')[11:19]} / "
         f"{t.get('first_prediction_at', '–')[11:19]} / {t.get('all_first_editions_at', '未達')[11:19] if t.get('all_first_editions_at') else '未達'} |",
         f"| 最早発走 | {min((r['post_initial'] for r in races.values()), default='–')[11:16]} |",
         f"| Provider要求 | {t.get('requests', 0)}回・待機{t.get('wait_seconds', 0):.0f}秒 |", '']
    # P1-4 paper vs formal-arithmetic shadow, same race / same source snapshot
    agree = 0
    cmp_n = 0
    rho_sum = 0.0
    for key in races:
        pj, sj = out / f'{key}.json', out / f'{key}.shadow29.json'
        if pj.exists() and sj.exists():
            pr = [x['no'] for x in json.loads(pj.read_text())['prediction']['ranking']]
            sh = json.loads(sj.read_text()).get('f3s_order') or []
            common = [h for h in pr if h in sh]
            if len(common) >= 3:
                cmp_n += 1
                agree += int(pr[0] == sh[0])
                n_ = len(common)
                d2 = sum((pr.index(h) - sh.index(h)) ** 2 for h in common)
                rho_sum += 1 - 6 * d2 / (n_ * (n_ * n_ - 1))
    sh_n = sh_err = runners = cells = 0
    tc_sum = {}
    gate_sum = {}
    for key in races:
        sj = out / f'{key}.shadow29.json'
        if sj.exists():
            d = json.loads(sj.read_text())
            sh_n += 1
            runners += d.get('runner_count', 0)
            cells += d.get('cells', 0)
            for k, v in d.get('terminal_counts', {}).items():
                tc_sum[k] = tc_sum.get(k, 0) + v
            for k, v in (d.get('production_gates') or {}).get('cells', {}).items():
                gate_sum[k] = gate_sum.get(k, 0) + v
    predicted = sum(1 for r in races.values() if r['editions'])
    if predicted:
        L += ['## 公式29指数シャドー（候補算術 materialize_candidate・正式Consumerではない）', '',
              f"予想{predicted}Rのうち実行{sh_n}R／{runners}頭×29＝{cells}セル（期待値 {runners * 29}）："
              + '・'.join(f"{k} {v}" for k, v in tc_sum.items())
              + (f"。正式経路と同じセル検査：通過 {gate_sum.get('pass', 0)}／"
                 + '・'.join(f"{k} {v}" for k, v in gate_sum.items() if k != 'pass' and v) if gate_sum else '')
              + '。KRS実試行 0（外部Engine未呼出）。', '']
    if cmp_n:
        L += ['## PAPERエンジン vs 公式29指数シャドー（同一出馬表）', '',
              f"比較{cmp_n}R：◎一致 {agree}/{cmp_n}・順位相関（Spearman平均）{rho_sum / cmp_n:.2f}。"
              'シャドーは消費権限なし（Prediction/KRS/Ticket/Capital=false）。', '']
    res_rows = [r for r in races.values() if r.get('settlement')]
    if res_rows:
        inv = sum(r['settlement']['invest'] for r in res_rows)
        ref = sum(r['settlement'].get('refund', 0) for r in res_rows)
        eff = inv - ref
        pay = sum(r['settlement']['payout'] for r in res_rows)
        pend = sum(1 for r in races.values() if r['editions'] and not r.get('settlement'))
        last = max((r['settlement'].get('settled_at') or '' for r in res_rows), default='')
        L += ['## 結果照合（PAPER・1点100円・発走前に凍結した最終Revisionのみ）', '',
              f"精算{len(res_rows)}R（未精算 {pend}R・最終精算 {last[11:16] or '–'}）："
              f"◎1着 {sum(r['settlement']['win_hit'] for r in res_rows)}／◎3着内 {sum(r['settlement']['top_in3'] for r in res_rows)}"
              f"／Top3捕捉 {sum(r['settlement']['top3_capture'] for r in res_rows)}/{3 * len(res_rows)}"
              f"／Ordered Pair {sum(r['settlement']['ordered_pair'] for r in res_rows)}／完全順序 {sum(r['settlement']['exact_triple'] for r in res_rows)}", '',
              (f"投資 {inv:,}円・返還 {ref:,}円・有効投資 {eff:,}円・払戻 {pay:,}円・損益 {pay - eff:+,}円・PFS {100 * pay / eff:.1f}%"
               if eff else '有効投資0（PFS NULL）'), '']
    for vid, v in q['venues'].items():
        L += [f"## {v['name']}", '',
              '| R | 発走（変更） | 状態 | 版 | 取得 | 保存 | 本命 | 買い目 | 結果 |', '|---|---|---|---|---|---|---|---|---|']
        for key in sorted(k for k in races if k.startswith(vid + '_')):
            r = races[key]
            ch = f"（{r['post_initial'][11:16]}→）" if r['post_current'] != r['post_initial'] else ''
            e = r['editions'][-1] if r['editions'] else None
            link = f"[{r['race_no']}R]({key}.md)" if e else f"{r['race_no']}R"
            pj = out / f'{key}.json'
            top, bets = '', ''
            if pj.exists():
                d = json.loads(pj.read_text())
                tp = d['prediction']['ranking'][0]
                top = f"◎{tp['no']} {tp['name']}"
                bets = '<br>'.join(f"{x['k']} {x['b']}" for x in d['prediction']['tickets'][:2])
            reason = r['last_error'] or ''
            st = r.get('settlement')
            result = (f"{'-'.join(map(str, st['order'][:3]))} 払戻{st['payout']:,}円" if st else '')
            L.append(f"| {link} | {r['post_current'][11:16]}{ch} | {r['status']}{(' ' + reason) if reason else ''} | "
                     f"{e['edition'] if e else ''} | {e['source_fetched_at'][11:16] if e else ''} | {e['saved_at'][11:16] if e else ''} | "
                     f"{top} | {bets} | {result} |")
        L.append('')
    text = '\n'.join(L) + '\n'
    p = out / 'README.md'
    if not p.exists() or p.read_text() != text:
        p.write_text(text)


# ----------------------------------------------------------------------- tick
def tick(day=None, now=None, budget_seconds=480, only=None, reader=None, results=True):
    now = now or now_jst()
    day = day or now.date().isoformat()
    out = ROOT / day
    out.mkdir(parents=True, exist_ok=True)
    reader = reader or rk.Reader(ROOT / 'source_state.json')
    started = time.monotonic()
    metrics = {'tick_at': now.isoformat(), 'requests_before': getattr(getattr(reader, 'client', None), 'requests', 0)}
    cards = {}
    q = load_queue(out)
    if q and any(r.get('settlement') and 'effective_invest' not in r['settlement'] for r in q['races'].values()):
        resettle(day)  # one-time offline re-settlement of legacy (pre-revision) settlements
        q = load_queue(out)
    changed = False
    try:
        if q is None:
            q = discover(reader, day, out, cards)
            q['timings']['first_tick_at'] = now.isoformat()
            changed = True
        elif day == now.date().isoformat() and now.hour >= 6 and not q['discovered_at'].startswith(day) \
                and not q['timings'].get('rediscovered_at'):
            changed |= rediscover(reader, day, q, cards)
        if not q['races']:
            log('NO_LOCAL_MEETING', day)
            dump(out / 'queue.json', q)
            return 0
        changed |= mark_delivery(q, out)
        jobs = []
        for key, r in q['races'].items():
            if only and r['race_no'] not in only:
                continue
            mins = (datetime.fromisoformat(r['post_current']) - now).total_seconds() / 60
            have = [e['edition'] for e in r['editions']]
            if mins <= CUTOFF_MIN:
                if not r['editions'] and r['status'] != 'MISSED_DEADLINE':
                    r['status'] = 'MISSED_DEADLINE'
                    r['last_error'] = r.get('last_error') or 'NO_EDITION_BEFORE_CUTOFF'
                    log('MISSED_DEADLINE', key)
                    changed = True
                if results and r['editions'] and not r.get('settlement') and mins <= -RESULT_DELAY_MIN \
                        and r.get('result_attempts', 0) < MAX_ATTEMPTS:
                    jobs.append((3, mins, key, 'RESULT'))
                continue
            if r['status'] == 'PREDICTION_FAILURE' and r['attempts'] >= MAX_ATTEMPTS:
                if r.get('failed_code') == CODE_VERSION:
                    continue
                r['attempts'] = 0  # code changed since the failure: retry automatically
                log('RETRY_AFTER_CODE_CHANGE', key, r.get('last_error'))
            if mins <= FINAL_WINDOW_MIN and '直前版' not in have:
                jobs.append((1, mins, key, '直前版'))
            elif not have:
                jobs.append((2, mins, key, '朝版'))
        jobs.sort()
        if jobs:
            log('TICK', day, 'jobs', len(jobs), [f'{k}:{e}' for _, _, k, e in jobs[:6]])
        for _, _, key, edition in jobs:
            if time.monotonic() - started > budget_seconds:
                log('BUDGET_STOP remaining', len(jobs))
                break
            r = q['races'][key]
            try:
                if edition == 'RESULT':
                    r['result_attempts'] = r.get('result_attempts', 0) + 1
                    fp = frozen_prediction(r, out, key)
                    if fp is None:
                        r['result_attempts'] = MAX_ATTEMPTS
                        r['last_error'] = 'NO_PRECUTOFF_FROZEN_PREDICTION'
                        changed = True
                        continue
                    html = reader.result_page(r['rid'])
                    st = settle.settle(html, fp, now_jst().isoformat())
                    if st:
                        dump(out / f'{key}.result.json', st)
                        r['settlement'] = {k: st.get(k) for k in ('order', 'invest', 'refund', 'effective_invest', 'payout',
                                                                  'win_hit', 'top_in3', 'top3_capture', 'ordered_pair',
                                                                  'exact_triple', 'settled_at', 'revision', 'ticket_sha256')}
                        r['status'] = 'POSTRESULT_DIAGNOSTIC'
                        log('RESULT', key, st['order'][:3], st['payout'])
                    changed = True
                else:
                    timing = predict(reader, r, date.fromisoformat(day), edition, out, cards)
                    q['timings'].setdefault('first_prediction_at', now_jst().isoformat())
                    log('OK', key, edition, timing)
                    changed = True
            except rk.SourceStop as exc:
                r['status'] = 'SOURCE_HOLD'
                r['last_error'] = str(exc)[:160]
                log('SOURCE_STOP', key, exc)
                changed = True
                break
            except Exception as exc:
                r['attempts'] += 1
                r['failed_code'] = CODE_VERSION
                r['status'] = 'PREDICTION_FAILURE' if edition != 'RESULT' else r['status']
                r['last_error'] = f'{type(exc).__name__}:{str(exc)[:120]}'
                dump(out / f'{key}.error.json', {'race': key, 'edition': edition, 'error': r['last_error'],
                                                  'at': now_jst().isoformat(), 'trace': traceback.format_exc()[-1500:]})
                log('FAIL', key, edition, r['last_error'])
                changed = True
        if not q['timings'].get('all_first_editions_at') and all(r['editions'] or r['status'] == 'MISSED_DEADLINE'
                                                                 for r in q['races'].values()):
            q['timings']['all_first_editions_at'] = now_jst().isoformat()
            changed = True
    except rk.SourceStop as exc:
        log('SOURCE_STOP', exc)
        changed = True
    finally:
        client = getattr(reader, 'client', None)
        if client is not None and q is not None:
            q['timings']['requests'] = q['timings'].get('requests', 0) + client.requests - metrics['requests_before']
            q['timings']['wait_seconds'] = q['timings'].get('wait_seconds', 0) + getattr(client, 'wait_seconds', 0)
            metrics.update(requests=client.requests - metrics['requests_before'],
                           wait_seconds=round(getattr(client, 'wait_seconds', 0), 1))
            client.requests = 0
            client.wait_seconds = 0.0
        if changed and q is not None:
            dump(out / 'queue.json', q)
            report(q, out)
            metrics['elapsed_s'] = round(time.monotonic() - started, 1)
            with (out / 'metrics.jsonl').open('a') as fh:
                fh.write(json.dumps(metrics, ensure_ascii=False) + '\n')
        if LOG:
            with (out / 'autopilot_log.txt').open('a') as fh:
                fh.write('\n'.join(LOG) + '\n')
            LOG.clear()
    return 0


def pending_soon(day=None, minutes=12):
    """Seconds-free check used by the loop to decide whether to keep ticking."""
    now = now_jst()
    q = load_queue(ROOT / (day or now.date().isoformat()))
    if q is None:
        return True
    for r in q['races'].values():
        mins = (datetime.fromisoformat(r['post_current']) - now).total_seconds() / 60
        have = [e['edition'] for e in r['editions']]
        if mins > CUTOFF_MIN and (not have or (mins <= FINAL_WINDOW_MIN + minutes and '直前版' not in have)):
            return True
        if mins <= -RESULT_DELAY_MIN and r['editions'] and not r.get('settlement') and r.get('result_attempts', 0) < MAX_ATTEMPTS:
            return True
    return False


def resettle(day):
    """Recompute settlements from stored official order/payouts (no network)
    against the frozen pre-cutoff prediction. Writes <key>.result.json and keeps
    the previous one as <key>.result.prev.json (never silently overwritten)."""
    out = ROOT / day
    q = load_queue(out)
    n = 0
    for key, r in q['races'].items():
        rp = out / f'{key}.result.json'
        fp = frozen_prediction(r, out, key)
        if not rp.exists() or fp is None:
            continue
        old = json.loads(rp.read_text())
        res = {'order': old['order'], 'non_starters': old.get('non_starters', []),
               'did_not_finish': old.get('did_not_finish', []),
               'payouts': {k: {(tuple(sorted(int(x) for x in c.split('-'))) if k in settle.UNORDERED
                               else tuple(int(x) for x in c.split('-'))): v for c, v in d.items()}
                           for k, d in old['payouts'].items()}}
        st = settle.settle_parsed(res, json.loads(fp.read_text()), str(fp.relative_to(ROOT)), now_jst().isoformat())
        st['resettled_from'] = old.get('settled_at') or 'initial'
        if not (out / f'{key}.result.prev.json').exists():
            (out / f'{key}.result.prev.json').write_text(rp.read_text())
        dump(rp, st)
        r['settlement'] = {k: st.get(k) for k in ('order', 'invest', 'refund', 'effective_invest', 'payout', 'win_hit',
                                                  'top_in3', 'top3_capture', 'ordered_pair', 'exact_triple',
                                                  'settled_at', 'revision', 'ticket_sha256')}
        n += 1
    dump(out / 'queue.json', q)
    report(q, out)
    log('RESETTLE', day, n)
    print('RESETTLE', day, n)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date')
    ap.add_argument('--races', help='comma-separated race numbers to restrict')
    ap.add_argument('--budget', type=int, default=480)
    ap.add_argument('--pending', action='store_true', help='exit 0 if work is due within 12 min, else 1')
    ap.add_argument('--resettle', action='store_true', help='recompute settlements offline from stored results')
    a = ap.parse_args()
    if a.resettle:
        sys.exit(resettle(a.date))
    if a.pending:
        sys.exit(0 if pending_soon(a.date) else 1)
    only = {int(x) for x in a.races.split(',')} if a.races else None
    sys.exit(tick(a.date, budget_seconds=a.budget, only=only))


if __name__ == '__main__':
    main()

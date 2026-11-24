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
PAPER only: no purchase, no Formal claim. The only outbound message is the
Owner-approved pre-start comment on issue #424 (deliver()); 水分ボンバー VMI-L
is an external auxiliary at a fixed prior weight (engine.VMI_WEIGHT).
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
from runtime.local_autopilot import sbo
from runtime.local_autopilot import settle

JST = timezone(timedelta(hours=9))
ROOT = Path(os.environ.get('KM_LOCAL_AUTOPILOT_OUT') or Path(__file__).resolve().parent / 'output')
QUAD = {1: '① 絶対×妙味 → 単勝勝負', 2: '② 絶対×配当不足 → 1着固定で配当化',
        3: '③ 不安×妙味 → 複勝系（下限割れはワイド）', 4: '④ 不安×配当不足 → 軸は最小、相手・3列目で妙味'}
FINAL_WINDOW_MIN = 45
CUTOFF_MIN = 3          # Rakuten closes voting 2 min before post; we freeze 3 min before
MAX_ATTEMPTS = 3
RESULT_DELAY_MIN = 20
RESULT_MAX_ATTEMPTS = 8          # official results can lag; retries back off 15, 30, 45 ... min (11/17 OHI_11)
RESEARCH_KRS = os.environ.get('KM_LOCAL_RESEARCH_KRS', '1') == '1'  # non-production research KRS (5,000 / seed 1)
# Formal Production on the Runtime-signed Rakuten card (Owner instructions 2026-11-16).
FORMAL = os.environ.get('KM_LOCAL_FORMAL', '1') == '1'
CHECK10_MIN = 10           # T-10 final-prediction checkpoint (formal Revision 2 only on a material change)
FORMAL_MIN_LEAD_MIN = 4   # SOURCE waits out Rakuten's 60 s Crawl-delay; never start closer to cutoff
CODE_VERSION = hashlib.sha256(b''.join(
    (Path(__file__).resolve().parent / f).read_bytes() for f in ('engine.py', 'run.py', 'rakuten.py', 'settle.py', 'sbo.py'))).hexdigest()[:12]
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
def render(race, res, edition, src_at, shadow=None, revision=None, sbo_meta=None):
    """PAPER race report. Mobile-first: 印 → 買い目（買い目表記規格のツリー）→ 判断 → 詳細（折りたたみ）."""
    from runtime.local_autopilot import ticket_tree
    a = res['aki']
    L = [f"## {race['venue_name']}{race['race_no']}R {race['post_current'][11:16]}発走　{race.get('race_name', '')}",
         f"{race.get('distance') or '?'}m／{len(res['rows'])}頭／馬場 {race.get('going') or '不明'}　**{edition}**"
         f"（出馬表・オッズ取得 {src_at[11:16]}）" + (f"　改訂理由：{revision}" if revision else '')]
    if race.get('scratched'):
        L.append(f"取消・除外：{'、'.join(race['scratched'])}（予測・買い目から除外済み）")
    L += ['', '**印と役割**', '', '| 印 | 馬番 | 馬名 | 単勝 | 人気 | 勝率※ | 役割 |', '|:-:|:-:|---|--:|:-:|--:|---|']
    for x in res['order']:
        if x['mark'] or x['role'] not in ('×', ''):
            L.append(f"| {x['mark'] or ''} | {x['no']} | {x['name']} | {'' if not x['win'] else x['win']} | "
                     f"{x.get('pop', '')} | {x['p_win'] * 100:.0f}% | {x['role']} |")
    tk = [(t['k'], ticket_tree.parse(t['k'], t['b']), None) for t in res['tickets']]
    tree, total = ticket_tree.block(tk)
    L += ['', f"**買い目**（ペーパー・1点100円・実購入なし）", '', '```', tree, '```']
    ev = '–' if res['tan_ev'] is None else f"{res['tan_ev']:+.2f}"
    L += ['', '**判断**', '',
          f"- 展開 {res['pace']}／レース型 {res['race_type']}",
          f"- 本命 信頼ゲート **{res['gate']}**／{QUAD[res['quad']]}",
          f"- 荒れ具合 AKI {a['total']}（タイプ{a['type']}・{a['form']}型）：W-AKI {a['W']}・P-AKI {a['P']}・ASI {a['ASI']}・RSI {a['RSI']}",
          '', '<details><summary>指数・判定の詳細</summary>', '']
    if sbo_meta:
        L.append(f"- 外部補助指標VMI-L（水分ボンバー・F3Sへ{engine.VMI_WEIGHT:.0%}）：" + (
            f"使用 {sbo_meta['coverage']}/{sbo_meta['active']}頭（取得 {sbo_meta['fetched_at'][11:16]}）" if sbo_meta['status'] == 'USED'
            else f"未使用（{sbo_meta['status']}）→ F3Sは従来式"))
        kbm = sbo_meta.get('keibabook') or {}
        sg = kbm.get('signals') or {}
        L.append(f"- 競馬ブック（厩舎の話CCI・調教TRI・TM印TMI・RT/CPU→KBA 各{engine.KB_WEIGHT}×偏差、展開予想→EVI {engine.PACE_SHARE:.0%}）：" + (
            f"使用 {kbm['coverage']}頭［CCI {sg.get('cci', 0)}／TRI {sg.get('tri', 0)}／印 {sg.get('tm', 0)}／展開 {sg.get('pace', 0)}"
            f"／RT・CPU {max(sg.get('rt', 0), sg.get('cpu', 0))}］（取得 {str(kbm['captured_at'])[11:16]}UTC）"
            if kbm.get('status') == 'USED' else f"未使用（{kbm.get('status')}）"))
    if race.get('newcomers'):
        L.append(f"- 過去走なし（新馬等）：{race['newcomers']}頭 → 能力・展開系は UNKNOWN（中立52）で計算")
    rt = ticket_tree.roundtrip(tk)       # 川崎 v2.4 第368条：券面→ツリー→再展開の一致（検算のみ・買い目は変えない）
    L.append('- 買い目ツリー検算（券面→ツリー→再展開）：' + ('一致' if rt['ok'] else f"不一致 {rt['mismatches']}"[:300]))
    try:                                 # 地方 I2.2 Directional Exposure（検算のみ・買い目は変えない）
        from runtime.local_autopilot import exposure
        L.append(exposure.line(exposure.audit(exposure.roles_from_order(res['order']), [(k, c) for k, c, _ in tk])))
        L.append(exposure.marginal_line(exposure.marginal([(k, c) for k, c, _ in tk])))   # 大井 v2.3 第326・329条
        L.append(exposure.concentration_line(exposure.concentration([x.get('p_win') for x in res['order']])))   # KRS v1.5 第85条
    except Exception as err:             # an audit failure must never break the delivery
        L.append(f'- 役割と券面の対応：検算不可（{type(err).__name__}）')
    L += ['', '| 印 | 馬番 | 馬名 | 騎手 | 単勝 | 人気 | TPI-L | SRI-L | EVI | NCI | T3I | F3S | OPI-V | VMI | CCI | TRI | 印 | 展開 | p勝(暫定) | 役割 |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for x in res['order']:
        L.append(f"| {x['mark'] or ''} | {x['no']} | {x['name']} | {x['jockey'] or ''} | "
                 f"{'' if not x['win'] else x['win']} | {x.get('pop', '')} | {f0(x['TPIF'])} | {f0(x['SRI'])} | "
                 f"{f0(x['EVI'])} | {f0(x['NCI'])} | {f0(x['T3I'])} | {f0(x['F3S'])} | {f0(x['OPI'])} | {f0(x.get('VMI'))} | {f0(x.get('CCI'))} | {f0(x.get('TRI'))} | {f0(x.get('TMI'))} | {x.get('PACE') or ''} | "
                 f"{x['p_win'] * 100:.0f}% | {x['role']} |")
    L += ['', f"- 本命判定（§12）：WCI {res['wci']}／本命不安 {res['fuan']}（{'、'.join(res['fuan_reasons']) or 'なし'}）／逆転候補 {res['reversal']}頭"
              f"／単勝EV（暫定・未較正。資金判断に使わない）{ev}",
          f"- AKI-v2（§19）：堅決着補正 −{a['katai']}",
          '- 必須チェック：' + '／'.join(f"{k} {'YES' if v else 'NO'}" for k, v in res['checks'].items()),
          '- 券種の判断：' + '／'.join(f"{t['k']} {t['pt']}点 {t['st']}" + (f"（{t['note']}）" if t.get('note') else '') for t in res['tickets'])]
    if shadow and not shadow.get('error'):
        tc = shadow['terminal_counts']
        L += [f"- 公式29指数シャドー（FULL29_SHADOW_PAPER・消費権限なし） "
              f"{shadow['runner_count']}頭×29＝{shadow['cells']}セル：CALCULATED {tc['CALCULATED']}／RULED-NEUTRAL {tc['RULED-NEUTRAL']}"
              f"／未解決 {tc['UNRESOLVED'] + tc['RULED-HOLD'] + tc['NOT-APPLICABLE']}。F3S-L順 {'-'.join(map(str, shadow['f3s_order'][:6]))}"]
    elif shadow:
        L += [f"- 公式29指数シャドー：実行不可（{shadow['error']}）"]
    L += ['', '</details>']
    notes = sorted({f for x in res['rows'] for f in x['flags'] if 'NEUTRAL' in f})
    L += ['', f"<sub>※勝率・p勝は暫定値。未較正ペーパー。p勝はF3Sのsoftmaxと単勝人気の50:50合成（実勝率ではない）。CCI（厩舎の話）・TRI（調教）は"
              f"競馬ブック帯域が無い馬・場では中立52。複勝オッズ未取得のため複勝はワイドへルーティング。馬場：{race.get('going') or '不明'}。{' '.join(notes)}</sub>", '']
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


_SBO = []


def sbo_aux(r, runners):
    """水分ボンバー VMI-L for this race, only from a snapshot fetched before cutoff."""
    try:
        if not _SBO:
            _SBO.append(sbo.Client(ROOT / 'sbo_state.json'))
        snap = sbo.snapshot(_SBO[0], r['race_date'], r['venue_id'], r['race_no'])
        at = now_jst().isoformat()
        try:   # private cache for the formal EXT connection (raw SBO numbers never enter Git)
            from runtime.local_autopilot import ext_connect
            ext_connect.save_sbo(r['race_date'], r['venue_id'], r['race_no'], snap, at)
        except Exception:
            pass
        active = [x['horse_no'] for x in runners if x.get('status') != 'CANCELLED']
        meta = {'status': snap['status'], 'fetched_at': at, 'sha256': snap.get('sha256'), 'active': len(active),
                'coverage': 0, 'weight': engine.VMI_WEIGHT}
        if snap['status'] != 'OK':
            return None, meta
        if datetime.fromisoformat(at) >= cutoff(r):
            meta['status'] = 'FETCHED_AFTER_CUTOFF'
            return None, meta
        v = sbo.vmi(snap['table'], active)
        meta['coverage'] = sum(1 for x in v.values() if x is not None)
        meta['status'] = 'USED' if meta['coverage'] else 'NO_INDEX'
        return ({'vmi': v} if meta['coverage'] else None), meta
    except Exception as exc:  # external auxiliary must never block the prediction
        return None, {'status': 'UNAVAILABLE', 'error': f'{type(exc).__name__}:{str(exc)[:120]}',
                      'fetched_at': now_jst().isoformat(), 'sha256': None, 'coverage': 0, 'active': len(runners)}


ENGINE_KB_KEYS = {'cci', 'tri', 'tm', 'pace', 'rt', 'cpu'}


def keibabook_aux(out, r):
    """競馬ブック bands captured in the Owner's session (external/keibabook_bands.json,
    bands only). Used only when captured before this race's cutoff."""
    p = out / 'external' / 'keibabook_bands.json'
    if not p.exists():
        return None, {'status': 'NOT_CAPTURED'}
    raw = p.read_bytes()
    doc = json.loads(raw)
    meta = {'status': 'NOT_PROVIDED', 'captured_at': doc.get('captured_at'), 'sha256': hashlib.sha256(raw).hexdigest()}
    race = next((x for x in doc.get('races', []) if x.get('venue') == r['venue_name'] and x.get('race_no') == r['race_no']), None)
    if race is None:
        return None, meta
    cap = datetime.fromisoformat(doc['captured_at'].replace('Z', '+00:00'))
    if cap >= cutoff(r):
        meta['status'] = 'CAPTURED_AFTER_CUTOFF'
        return None, meta
    full = {int(k): v for k, v in race['horses'].items() if v}
    meta['evidence_only'] = full   # incl. style / course_first labels: danger-fav evidence, never the engine
    kb = {k: v for k, v in full.items() if set(v) & ENGINE_KB_KEYS}
    if not kb:
        return None, meta
    meta.update(status='USED', coverage=len(kb),
                signals={k: sum(1 for v in kb.values() if k in v) for k in ('cci', 'tri', 'tm', 'pace', 'rt', 'cpu')})
    return kb, meta


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
    ext, sbo_meta = sbo_aux(r, runners)
    kb, kb_meta = keibabook_aux(out, r)
    if kb:
        ext = dict(ext or {}, kb=kb)
    kb_evidence = kb_meta.pop('evidence_only', None)
    sbo_meta['keibabook'] = kb_meta
    res = engine.predict(race, runners, odds, today, ext)
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
        krs_input = shadow.pop('_krs_input', None)
        dump(stem.with_name(stem.name + '.shadow29.json'), shadow)
    except Exception as exc:
        shadow, krs_input = {'error': f'{type(exc).__name__}:{str(exc)[:200]}'}, None
    t3 = time.monotonic()
    md = render(race, res, edition, fetched, shadow, revision, sbo_meta)
    slim = {k: v for k, v in res.items() if k not in ('rows', 'order', 'ana')}
    slim['ranking'] = [{k: x.get(k) for k in ('mark', 'no', 'name', 'jockey', 'win', 'TPIF', 'SRI', 'EVI', 'NCI',
                                             'T3I', 'F3S', 'OPI', 'VMI', 'CCI', 'TRI', 'TMI', 'KBA', 'PACE',
                                             'p_win', 'role',
                                             # evidence only (shadow measurement: body weight / market); not consumed
                                             'frame', 'bw', 'bw_change', 'place_low', 'BWI')} for x in res['order']]
    slim['sbo'] = sbo_meta
    try:  # evidence only (危険な1番人気 + 前走内容); never consumed by ranking / tickets / KRS / capital
        from runtime.local_autopilot import danger_fav
        slim['danger_fav'] = danger_fav.flags(race, runners, kb_evidence)
        slim['prior_runs'] = {str(x['horse_no']): danger_fav.prior_record(x) for x in runners}
    except Exception as exc:
        slim['danger_fav'] = {'status': 'ERROR', 'error': f'{type(exc).__name__}:{str(exc)[:120]}'}
    slim['race_cond'] = {'distance': race.get('distance'), 'going': race.get('going'), 'surface': race.get('surface')}
    try:  # 亀谷 sire-rule matches (author claims, unvalidated on NAR): evidence only, no numeric consumer
        from runtime.local_autopilot import bloodline_kametani
        slim['kametani'] = bloodline_kametani.race_evidence(race, runners)
    except Exception as exc:
        slim['kametani'] = {'status': 'ERROR', 'error': f'{type(exc).__name__}:{str(exc)[:120]}'}
    try:  # SHADOW: 亀谷 v2 corrected reading (Drive 精読 2026-11-21); v2 / ext_model unchanged, no consumer
        from runtime.local_autopilot import kametani_v2c
        slim['kametani_v2c'] = kametani_v2c.race_evidence(race, runners)
    except Exception as exc:
        slim['kametani_v2c'] = {'status': 'ERROR', 'error': f'{type(exc).__name__}:{str(exc)[:120]}'}
    try:  # research BVI-L-R2 from our own pooled past starts (days before the race only): evidence only
        from runtime.local_autopilot import sire_stats
        slim['bvi_r2'] = sire_stats.race_evidence(race, runners, sire_stats.load(ROOT, str(r['race_date'])))
    except Exception as exc:
        slim['bvi_r2'] = {'status': 'ERROR', 'error': f'{type(exc).__name__}:{str(exc)[:120]}'}
    try:  # 南関東 class-move labels (YouTube claims, unvalidated): evidence only, no numeric consumer
        from runtime.local_autopilot import class_move
        slim['class_move'] = class_move.race_evidence(race, runners)
    except Exception as exc:
        slim['class_move'] = {'status': 'ERROR', 'error': f'{type(exc).__name__}:{str(exc)[:120]}'}
    if edition == '直前版':   # current-state evidence at the T-45 edition (evidence only, no numeric consumer)
        try:
            from runtime.local_autopilot import weather, day_trend
            slim['weather'] = weather.observe(r['venue_id'], now_jst(), Path(os.environ.get('RUNNER_TEMP') or '/tmp') / 'km_weather_cache')
            slim['day_trend'] = day_trend.build(out, r['venue_id'], now_jst())
        except Exception as exc:
            slim['weather'] = {'status': 'ERROR', 'error': f'{type(exc).__name__}:{str(exc)[:120]}'}
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
              'ticket_sha256': ticket_sha, 'prediction': slim, 'paper': True, 'calibrated': False,
              'code_version': CODE_VERSION, 'engine': 'Claude v4.3 PAPER', 'purchase_policy': 'EVERY_RACE'}
    (rev_dir / f"{rev_id}.json").write_text(json.dumps(frozen, ensure_ascii=False, indent=1, default=str) + '\n')
    (rev_dir / f"{rev_id}.md").write_text(md)
    if krs_input is not None:  # research-KRS input frozen with the revision (run later by the KRS job)
        (out / 'krs').mkdir(exist_ok=True)
        (out / 'krs' / f'{rev_id}.input.json').write_text(json.dumps(krs_input, ensure_ascii=False, sort_keys=True))
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
                          'top': res['order'][0]['no'], 'quad': res['quad'], 'aki_form': res['aki']['form'],
                          'sbo': {k: sbo_meta.get(k) for k in ('status', 'fetched_at', 'sha256', 'coverage', 'active')},
                          'keibabook': kb_meta})
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


PUBLISH_NOW_MIN = 20


def publish_now(reason):
    """Commit + push the data checkout immediately (same commands as the workflow's publish())."""
    if os.environ.get('KM_LOCAL_PUBLISH_MIDTICK', '1') == '0':
        return False
    repo = ROOT.parent
    if not (repo / '.git').exists():
        return False
    t0 = time.monotonic()

    def g(*a, timeout=60):
        return subprocess.run(['git', '-C', str(repo), *a], capture_output=True, text=True, timeout=timeout)
    try:
        g('add', '-A', 'output')
        if g('diff', '--cached', '--quiet').returncode == 0:
            return False
        g('commit', '-q', '-m', f"LOCAL autopilot {now_jst():%Y-%m-%d %H:%M} (prestart: {reason})")
        for _ in range(3):
            if g('pull', '-q', '--rebase', 'origin', 'local-autopilot-data').returncode == 0 and \
                    g('push', '-q', 'origin', 'HEAD:local-autopilot-data').returncode == 0:
                g('fetch', '-q', 'origin', '+refs/heads/local-autopilot-data:refs/remotes/origin/local-autopilot-data')
                log('PUBLISH_NOW', reason, round(time.monotonic() - t0, 1))
                return True
            time.sleep(3)
        log('PUBLISH_NOW_FAIL', reason)
    except Exception as exc:
        log('PUBLISH_NOW_FAIL', reason, f'{type(exc).__name__}:{str(exc)[:120]}')
    return False


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
            if not d or d.get('PUSH_VERIFIED'):
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
                        d['PUSH_VERIFIED'] = line.split()[1]
                        d['remote_commit_sha'] = line.split()[0]
                        d['LINK_AVAILABLE'] = REPO_URL + rel
                        changed = True
        pre = [e for e in r['editions'] if e.get('delivery', {}).get('PUSH_VERIFIED')
               and datetime.fromisoformat(e['delivery']['PUSH_VERIFIED']) < cutoff(r)]
        if pre and r['status'] in ('PREDICTION_COMPLETE', 'SOURCE_READY'):
            r['status'] = 'PRESTART_PUSH_VERIFIED'
            r['push_verified_at'] = pre[-1]['delivery']['PUSH_VERIFIED']
            changed = True
    return changed


DELIVERY_REPO = 'b03la013-max/keibametrics-runtime'
DELIVERY_FALLBACK_MIN = 10   # no 直前版 by post-10 min -> deliver the latest pre-cutoff edition


def _gh(method, path, body=None):
    import urllib.request
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    req = urllib.request.Request('https://api.github.com' + path, method=method,
                                 data=None if body is None else json.dumps(body).encode(),
                                 headers={'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json',
                                          'Content-Type': 'application/json', 'User-Agent': 'km-local-autopilot'})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def delivery_body(q, r, e, out):
    md = (out / 'rev' / f"{e['rev']}.md").read_text()
    fr = json.loads((out / 'rev' / f"{e['rev']}.json").read_text())
    rk_ = fr['prediction']['ranking']
    marks = ' '.join(f"{x['mark']}{x['no']}" for x in rk_ if x.get('mark'))
    tree = [f"W {fr['roles']['W']}", f"└ P2 {fr['roles']['P2']}", f"   └ P3 {fr['roles']['P3']}"]
    head = (f"### 🏇 {r['venue_name']}{r['race_no']}R {r['post_current'][11:16]}発走｜PAPER {e['edition']}\n"
            f"予測締切 {cutoff(r).strftime('%H:%M')}／印 {marks}\n")
    foot = (f"\n---\n<sub>Claude v4.3 PAPER（研究実装・毎レース購入方針の推薦試算）。正式Signed FINALではありません。"
            f"実購入なし。凍結 {e['frozen_at'][11:19]}／券面SHA `{e['ticket_sha256'][:12]}`／SOURCE SHA `{e['source_sha256'][:12]}`"
            f"／原本 {e['delivery'].get('LINK_AVAILABLE') or ''}</sub>")
    return head + '\n' + md + foot


def deliver(q, out, now):
    """Pre-start Owner delivery: one comment per race on the LOCAL delivery issue
    (Owner decision 2026-11-15), posted only before cutoff and only for a
    revision whose push was verified. Sent + read-back are recorded; whether the
    Owner actually saw it is not observable here (USER_REACHED UNVERIFIABLE)."""
    issue = os.environ.get('KM_LOCAL_DELIVERY_ISSUE')
    if not issue or not (os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')):
        return False
    changed = False
    for key, r in q['races'].items():
        if r.get('delivered_rev') or now >= cutoff(r) or r.get('delivery_attempts', 0) >= MAX_ATTEMPTS:
            continue
        pv = [e for e in r['editions'] if e.get('delivery', {}).get('PUSH_VERIFIED')]
        if not pv:
            continue
        e = pv[-1]
        mins = (datetime.fromisoformat(r['post_current']) - now).total_seconds() / 60
        if e['edition'] != '直前版' and mins > DELIVERY_FALLBACK_MIN:
            continue
        d = e['delivery']
        r['delivery_attempts'] = r.get('delivery_attempts', 0) + 1
        try:
            body = delivery_body(q, r, e, out)
            c = _gh('POST', f'/repos/{DELIVERY_REPO}/issues/{issue}/comments', {'body': body})
            back = _gh('GET', f"/repos/{DELIVERY_REPO}/issues/comments/{c['id']}")
            sha = hashlib.sha256(body.encode()).hexdigest()
            d.update({'USER_DELIVERY_SENT': c['created_at'], 'delivery_comment_url': c['html_url'],
                      'delivery_body_sha256': sha,
                      'DELIVERY_READBACK_VERIFIED': hashlib.sha256((back.get('body') or '').encode()).hexdigest() == sha,
                      'USER_REACHED': 'UNVERIFIABLE_GITHUB_NOTIFICATION', 'USER_ACK_VERIFIED': 'NOT_REQUIRED'})
            r['delivered_rev'] = e['rev']
            log('DELIVERED', key, e['rev'], c['html_url'])
        except Exception as exc:
            d['delivery_error'] = f'{type(exc).__name__}:{str(exc)[:120]}'
            log('DELIVERY_FAIL', key, d['delivery_error'])
        changed = True
    return changed


FORMAL_KIND = {'WIN': '単勝', 'PLACE': '複勝', 'WIDE': 'ワイド', 'QUINELLA': '馬連', 'EXACTA': '馬単',
               'TRIO': '三連複', 'TRIFECTA': '三連単'}


def auto_promotion_daily(q, out):
    from runtime.local_autopilot import auto_promote
    races = (q or {}).get('races') or {}
    if not races or not all(str(x.get('status', '')).startswith('POSTRESULT') for x in races.values()):
        return None
    st = auto_promote.load_state(ROOT)
    if (st.get('last_decision') or {}).get('day') == out.name:
        return None
    rec = auto_promote.decide(ROOT, out.name)
    rv = out / 'review'
    rv.mkdir(exist_ok=True)
    text = auto_promote.md(rec)
    try:   # reflection -> new same-budget candidates, retire the failed ones (Owner 2026-11-22 21:31)
        from runtime.local_autopilot import auto_candidates
        gen = auto_candidates.daily(ROOT, out.name, rec)
        text += auto_candidates.md(ROOT, gen)
        log('AUTO_CANDIDATES', 'new', ','.join(gen['new']) or '-', 'retired', ','.join(gen['retired']) or '-')
    except Exception as exc:
        log('AUTO_CANDIDATES_FAIL', f'{type(exc).__name__}:{str(exc)[:160]}')
    (rv / 'auto_promotion.md').write_text(text)
    log('AUTO_PROMOTION', rec['action'], rec.get('candidate'), rec.get('effective_from'))
    if rec['action'] in ('PROMOTE', 'DEMOTE'):
        issue = os.environ.get('KM_LOCAL_DELIVERY_ISSUE')
        if issue:
            _gh('POST', f'/repos/{DELIVERY_REPO}/issues/{issue}/comments', {'body': text})
    return rec


def formal_tickets_kb(tickets):
    """MEC tickets -> settle k/b lines (100-yen units; a 200-yen stake is two lines)."""
    out = []
    for t in tickets:
        k = FORMAL_KIND.get(str(t.get('bet_type')))
        sel = [str(x) for x in t.get('selection') or []]
        if not k or not sel:
            continue
        b = '→'.join(sel) if k in ('馬単', '三連単') else '-'.join(sel)
        out += [{'k': k, 'b': b}] * max(1, int(t.get('stake') or 100) // 100)
    return out


def settle_formal(r, key, out, html):
    """Formal RESULT closed loop: settle the frozen Signed-FINAL tickets against the
    official result (recommendation only, no purchase), then submit the official
    result + settlement to the Runtime /result, which re-verifies the FINAL receipt,
    runs the automatic post-result review / next-race learning state and signs a
    RESULT receipt. The receipt signature is verified here before it is recorded."""
    f = r.get('formal') or {}
    if f.get('status') != 'SIGNED_FINAL' or (r.get('formal_settlement') or {}).get('result_receipt_verified'):
        return
    r['formal_result_attempts'] = r.get('formal_result_attempts', 0) + 1
    try:
        fdir = formal_dir(out, r, key)    # latest effective revision (Revision 2 when the T-10 check re-signed)
        sm = json.loads((fdir / f'{key}.summary.json').read_text())
        fin = json.loads((fdir / f'{key}.final_receipt.json').read_text())
        fp = {'edition': 'FORMAL_SIGNED_FINAL', 'revision_id': 'FORMAL:' + f['final_receipt_sha256'][:16],
              'ticket_sha256': f['final_receipt_sha256'], 'saved_at': (sm.get('stages') or {}).get('SIGNED_FINAL'),
              'runners': [{'no': int(x)} for x in sm.get('ranking') or []],
              'prediction': {'ranking': [{'no': int(x)} for x in sm.get('ranking') or []],
                             'tickets': formal_tickets_kb(sm.get('tickets') or [])}}
        res = settle.parse_result(html)
        if res is None:
            return
        st = settle.settle_parsed(res, fp, f'formal/{key}.summary.json', now_jst().isoformat())
        st['classification'] = 'FORMAL_RECOMMENDATION_SETTLEMENT (no real purchase)'
        frozen_total = int(sm.get('total_investment') or 0)
        if st['invest'] != frozen_total:
            raise ValueError(f"SETTLEMENT_INVEST_{st['invest']}_NE_FROZEN_{frozen_total}")
        # The Runtime RESULT settles the Runtime-signed FINAL ticket set. With the R54 LOCAL ticket cap the
        # recommendation (st) is the capped subset; the signed full set is settled separately for /result.
        sf = st
        if sm.get('signed_final_tickets') is not None:
            fp_full = dict(fp, prediction=dict(fp['prediction'], tickets=formal_tickets_kb(sm['signed_final_tickets'])))
            sf = settle.settle_parsed(res, fp_full, f'formal/{key}.summary.json#signed_final', now_jst().isoformat())
            if sf['invest'] != int(sm.get('signed_final_total_investment') or 0):
                raise ValueError(f"SIGNED_SETTLEMENT_INVEST_{sf['invest']}_NE_FROZEN_{sm.get('signed_final_total_investment')}")
            st['signed_final_settlement'] = {k: sf.get(k) for k in ('invest', 'refund', 'effective_invest', 'payout', 'pfs')}
            st['local_ticket_cap_sha256'] = sm.get('local_ticket_cap_sha256')
        status = 'COMPLETE' if not sf['refund'] else 'PARTIAL'
        settlement = {'status': status, 'investment': int(sf['invest']), 'return': int(sf['payout']),
                      'winning_tickets': [h for t in sf.get('tickets') or [] for h in t.get('hits') or []]}
        if status == 'PARTIAL':
            settlement['settled_investment'] = int(sf['effective_invest'])
        from runtime.local_autopilot import formal_rakuten as fr
        base = fr._endpoint()
        hc, health = fr._call(base, '/health', None, 30)
        rc, rec = fr._call(base, '/result', {
            'family_id': 'LOCAL', 'race_id': sm['race_id'], 'final_receipt': fin,
            'official_result': {'finish_order': [int(x) for x in res['order']],
                                'non_starters': sorted(res.get('non_starters') or []),
                                'source': 'RAKUTEN_RACE_RESULT', 'result_available_at': now_jst().isoformat()},
            'settlement': settlement, 'pfs_authority': 'FORMAL_RECOMMENDATION_ONLY_NO_PURCHASE'}, 120)
        verified = (rc < 300 and isinstance(rec, dict) and (rec.get('receipt') or {}).get('status') == 'PASS'
                    and fr._verify_sig(rec, health['receipt_public_key_b64']))
        st['result_receipt_sha256'] = rec.get('receipt_sha256') if isinstance(rec, dict) else None
        st['result_receipt_verified'] = bool(verified)
        st['result_receipt_errors'] = (rec.get('receipt') or {}).get('errors') if isinstance(rec, dict) else str(rec)[:200]
        dump(fdir / f'{key}.result.json', st)
        dump(fdir / f'{key}.result_receipt.json', rec)
        art = (rec.get('artifact') or {}) if isinstance(rec, dict) else {}
        r['formal_settlement'] = {k: st.get(k) for k in ('invest', 'refund', 'effective_invest', 'payout', 'pfs',
                                                          'win_hit', 'diagnosis', 'signed_final_settlement')}
        r['formal_settlement'].update(
            result_receipt_sha256=st['result_receipt_sha256'], result_receipt_verified=st['result_receipt_verified'],
            runtime_pfs=(art.get('settlement') or {}).get('pfs'),
            # P0-1 (ChatGPT 11/24 21:52): classify the DELIVERED 60-point tickets (same object as the money);
            # the Runtime label judges the signed full MEC and is kept under its own name
            first_material_failure=_delivered_first(sm, res, st),
            first_material_failure_runtime_full_mec=(art.get('failure_localization') or {}).get('primary_failure'),
            learning_state_id=(art.get('learning_event') or {}).get('state_id'),
            learning_production_change_authorized=(art.get('learning_event') or {}).get('production_change_authorized'))
        log('FORMAL_RESULT', key, st['invest'], st['payout'], 'RESULT_RECEIPT_VERIFIED' if verified else
            f"RESULT_RECEIPT_NOT_VERIFIED:{rc}:{st['result_receipt_errors']}")
    except Exception as exc:
        log('FORMAL_RESULT_FAIL', key, f'{type(exc).__name__}:{str(exc)[:160]}')


def _delivered_first(sm, res, st):
    try:
        from runtime.local_autopilot.review import delivered_failure
        roles = {int(h): r for h, r in (sm.get('roles') or {}).items()}
        ft = [(t['bet_type'], [int(x) for x in t['selection']]) for t in sm.get('tickets') or []]
        row = dict(st, no_bet_reason='CAPITAL_POLICY_NO_BET' if sm.get('no_bet') else None)
        return delivered_failure(roles, ft, [int(x) for x in res['order']], row)
    except Exception:
        return None


CHECK10_RETRY_WAIT_S = 20


def _transient(exc):
    """Network-level failure without an HTTP status (DNS, reset, timeout). HTTP errors (403/429/5xx) are final."""
    import socket
    import urllib.error
    seen = set()
    while exc is not None and id(exc) not in seen:
        seen.add(id(exc))
        if isinstance(exc, urllib.error.HTTPError) or getattr(exc, 'status', None) or getattr(exc, 'code', None):
            return False
        if isinstance(exc, (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError)):
            return True
        if 'URLError' in str(exc) and 'HTTP' not in str(exc):
            return True
        exc = exc.__cause__ or exc.__context__
    return False


def check10(reader, r, key, out):
    """T-10 checkpoint: compare with Revision 1; on a material change re-run the existing formal pipeline
    (Revision 2 in formal/rev2/, Revision 1 kept) only if it can finish before the cutoff."""
    from runtime.local_autopilot import checkpoint10 as c10, formal_rakuten
    rec = {'started_at': now_jst().isoformat(), 'decision': None}
    r['check10'] = rec
    try:
        try:
            html = reader.card_page(r['rid'])
        except Exception as exc:
            # P0 (11/22 KOC_04, ChatGPT 18:38 review): one retry on a transient network error only (no HTTP
            # status such as 403/429 -> those are final), and only when the retry still leaves the Revision 2 budget
            if not _transient(exc) or (cutoff(r) - now_jst()).total_seconds() < c10.REV2_BUDGET_S + CHECK10_RETRY_WAIT_S + 60:
                raise
            rec['retry'] = {'first_error': f'{type(exc).__name__}:{str(exc)[:100]}', 'at': now_jst().isoformat()}
            log('CHECK10_RETRY', key, rec['retry']['first_error'])
            time.sleep(CHECK10_RETRY_WAIT_S)
            html = reader.card_page(r['rid'])
        fetched = now_jst().isoformat()
        sm1 = json.loads((out / 'formal' / f'{key}.summary.json').read_text())
        cmp = c10.compare(r, out / 'formal', key, html, fetched, [str(x) for x in sm1.get('ranking') or []])
        rec.update({k: cmp[k] for k in ('checked_at', 'material', 'reasons', 'identity', 'observed', 'role_diff',
                                         'rank_up', 'rank_down', 'rev1_source_raw_sha256', 'new_source_raw_sha256')})
        try:   # Test D: weather change is recorded, never material by itself (no approved numeric rule)
            from runtime.local_autopilot import weather
            w10 = weather.observe(r['venue_id'], now_jst(), Path(os.environ.get('RUNNER_TEMP') or '/tmp') / 'km_weather_cache')
            prev = json.loads((out / 'rev' / f"{r['editions'][-1]['rev']}.json").read_text())['prediction'].get('weather')
            cmp['weather_t10'] = w10
            cmp['weather_change_since_t45'] = weather.diff(prev, w10)
            rec['weather_change_since_t45'] = cmp['weather_change_since_t45']
        except Exception as exc:
            cmp['weather_t10'] = {'status': 'ERROR', 'error': f'{type(exc).__name__}:{str(exc)[:120]}'}
        dump(out / 'formal' / f'{key}.check10.json', cmp)
        if not cmp['material']:
            rec['decision'] = 'KEEP_REVISION_1 (再計算を要する変更なし)'
        elif (cutoff(r) - now_jst()).total_seconds() < c10.REV2_BUDGET_S:
            rec['decision'] = 'KEEP_REVISION_1 (MATERIAL_BUT_NO_TIME_BEFORE_CUTOFF)'
        else:
            sm, arts = formal_rakuten.run_formal(r, out, cutoff(r))
            d2 = out / 'formal' / 'rev2'
            d2.mkdir(parents=True, exist_ok=True)
            for name, obj in arts.items():
                dump(d2 / f'{key}.{name}.json', obj)
            sm['revision'] = 2
            sm['previous_revision_final_receipt_sha256'] = r['formal'].get('final_receipt_sha256')
            sm['revision_reasons'] = cmp['reasons']
            dump(d2 / f'{key}.summary.json', sm)
            if sm['status'] == 'SIGNED_FINAL' and sm.get('before_cutoff'):
                r['formal_r1'] = r['formal']
                r['formal'] = {k: sm.get(k) for k in ('status', 'first_failed_stage', 'error', 'race_id',
                                                       'final_receipt_sha256', 'final_verified_remote',
                                                       'final_verified_local', 'ticket_count', 'total_investment',
                                                       'no_bet', 'krs_actual_run_count', 'before_cutoff',
                                                       'elapsed_s')} | {'stages': list(sm.get('stages') or {}),
                                                                        'revision': 2}
                r['formal_effective'] = 'rev2'
                rec['decision'] = 'REVISION_2_SIGNED'
                diff = {'reasons': cmp['reasons'], 'identity': cmp['identity'], 'role_diff': cmp['role_diff'],
                        'rank_up': cmp['rank_up'], 'rank_down': cmp['rank_down'],
                        'tickets': c10.ticket_diff(sm1.get('tickets') or [], sm.get('tickets') or []),
                        'investment': [sm1.get('total_investment'), sm.get('total_investment')]}
                rec['diff'] = diff
                deliver_formal(r, key, sm, now_jst(), revision_diff=diff)
            else:
                rec['decision'] = f"KEEP_REVISION_1 (REVISION_2_{sm['status']}:{sm.get('first_failed_stage')})"
    except Exception as exc:   # SOURCE failure etc.: Revision 1 stays valid and delivered
        rec['decision'] = f'KEEP_REVISION_1 (CHECK_FAILED:{type(exc).__name__}:{str(exc)[:100]})'
    rec['finished_at'] = now_jst().isoformat()
    log('CHECK10', key, rec['decision'], rec.get('reasons'))


def formal_dir(out, r, key):
    return out / 'formal' / 'rev2' if r.get('formal_effective') == 'rev2' else out / 'formal'


def deliver_formal(r, key, sm, now, revision_diff=None):
    issue = os.environ.get('KM_LOCAL_DELIVERY_ISSUE')
    if not issue or now >= cutoff(r):
        return
    tag = '【地方版 正式 Signed FINAL 改訂 Revision 2（最新有効版）】' if revision_diff else '【地方版 正式 Signed FINAL】'
    lines = [f"### 🏇 {r['venue_name']}{r['race_no']}R {r['post_current'][11:16]}発走｜{tag.strip('【】')}",
             f"予測締切 {cutoff(r).strftime('%H:%M')}", '']
    if revision_diff:
        d = revision_diff
        idn = d['identity']
        lines += ['**10分前チェックで重要な変更を検出し再計算しました（Revision 1は保存済み・失効）**',
                  '- 変更：' + '、'.join(filter(None, [
                      f"取消/除外 {idn['active_removed']}" if idn.get('active_removed') else '',
                      f"騎手変更 {idn['jockey_changed']}" if idn.get('jockey_changed') else '',
                      f"馬場 {idn['going'][0]}→{idn['going'][1]}" if idn.get('going') else '',
                      f"発走 {idn['post'][0]}→{idn['post'][1]}" if idn.get('post') else '',
                      '役割の入れ替わり' if d.get('role_diff') else ''])),
                  f"- 上昇 {d['rank_up'] or '-'}／下降 {d['rank_down'] or '-'}",
                  '- 役割 ' + '；'.join(f"{k} +{v['in']} -{v['out']}" for k, v in d['role_diff'].items()) if d['role_diff'] else '- 役割変化なし',
                  f"- 券面 追加{d['tickets']['added_count']}・削除{d['tickets']['removed_count']}／投資 "
                  f"{d['investment'][0]:,}円→{d['investment'][1]:,}円", '']
    from runtime.local_autopilot import ticket_tree
    lines += [
              '**印** ' + ' '.join(f"{sm['marks'][x]}{x}" for x in sm['ranking'][:6]),
             '**役割** ' + '／'.join(f"{c} " + '・'.join(x for x in sm['ranking'] if c in sm['roles'][x])
                                      for c in ('W', 'P2')), '',
             f"**買い目**（推薦試算・1点100円・実購入なし）"
             + (f"　地方版上限{sm['ticket_count']}点適用（MEC全体 {sm['signed_final_ticket_count']}点）"
                if sm.get('local_ticket_cap_sha256') else ''), '']
    by = {}
    for t in sm.get('tickets') or []:
        by.setdefault(FORMAL_KIND.get(t.get('bet_type'), t.get('bet_type')), []).append(tuple(int(x) for x in t.get('selection') or []))
    odd = [t for t in sm.get('tickets') or [] if int(t.get('stake') or 100) != 100]
    pos = {int(x): i for i, x in enumerate(sm['ranking'])}           # 買い目表記規格 2.4: evaluation order
    tree, _ = ticket_tree.block([(k, sorted(v, key=lambda c: [pos.get(h, 99) for h in c]), None) for k, v in by.items()])
    lines += ['```', tree, '```']
    if odd:
        lines.append('（100円以外の点：' + '、'.join(f"{FORMAL_KIND.get(t['bet_type'], t['bet_type'])} "
                                              + '・'.join(map(str, t['selection'])) + f" {t['stake']}円" for t in odd) + '）')
    ec = sm.get('ext_connection') or {}
    if ec.get('profile'):
        st = ec.get('status') or {}
        lines += ['', '<sub>外部情報の接続：' + '／'.join([
            f"水分ボンバー {st.get('sbo_horses', 0)}頭", f"競馬ブック {st.get('kb_horses', 0)}頭",
            f"自前スピード指数 {st.get('spd_horses', 0)}頭", f"29指数の空き部品へ入力 {st.get('full29_slots', 0)}件",
            ('NAR公式＋楽天結果 ' + '〜'.join(st.get('tables_period') or []) if st.get('tables') else 'NAR表 未準備'),
            '接続前の上位3頭 ' + '・'.join((sm.get('ranking_base') or [])[:3])
            + ('（入れ替わりあり）' if ec.get('changed_top3') else '（同じ）')]) + '</sub>']
    elif ec.get('error'):
        lines += ['', f"<sub>外部情報の接続：エラーのため接続前の順位で計算（{ec['error'][:60]}）</sub>"]
    lines += ['', f"<sub>SOURCE=Runtime署名の楽天出馬表／KRS {sm['krs_actual_run_count']}回（未較正・技術Proxy）／"
                  f"Static Owner v1.1（未検証の順序規則）／FINAL Receipt `{sm['final_receipt_sha256'][:16]}`"
                  f"（署名検証 local={sm['final_verified_local']} remote={sm['final_verified_remote']}）</sub>"]
    body = '\n'.join(lines)
    try:
        c = _gh('POST', f'/repos/{DELIVERY_REPO}/issues/{issue}/comments', {'body': body})
        back = _gh('GET', f"/repos/{DELIVERY_REPO}/issues/comments/{c['id']}")
        ok = (back.get('body') or '') == body
        r['formal']['delivery'] = {'USER_DELIVERY_SENT': c['created_at'], 'url': c['html_url'],
                                   'DELIVERY_READBACK_VERIFIED': ok,
                                   'READBACK_VERIFIED': ok,   # legacy key kept
                                   'delivery_body_sha256': hashlib.sha256(body.encode()).hexdigest(),
                                   'USER_REACHED': 'UNVERIFIED (GitHub notification arrival/viewing not observable; '
                                                   'set only on the Owner\'s explicit 受信確認 for this race)',
                                   'USER_ACK_VERIFIED': False}
        log('FORMAL_DELIVERED', key, c['html_url'])
    except Exception as exc:
        log('FORMAL_DELIVERY_FAIL', key, f'{type(exc).__name__}:{str(exc)[:120]}')


def triple_step(q, out, now):
    """SPAT4 LOTO トリプル馬単 (南関東): build once inside the window before the 5-minute close of the first
    leg, deliver to the LOCAL issue, settle hit/miss after the third leg (PAPER, no purchase)."""
    from runtime.local_autopilot import triple_umatan as tu
    changed = False
    for v in tu.VENUES:
        ks = tu.legs(q, v)
        if not ks:
            continue
        t = q.setdefault('triple', {}).setdefault(v, {})
        try:
            mins = (datetime.fromisoformat(q['races'][ks[0]]['post_current']) - now).total_seconds() / 60
            if not t.get('sha256') and t.get('attempts', 0) < 3 and tu.BUILD_WINDOW_MIN[0] < mins <= tu.BUILD_WINDOW_MIN[1]:
                t['attempts'] = t.get('attempts', 0) + 1
                rec = tu.build(q, v, out, now)
                changed = True
                if rec and rec.get('status') == 'BUILT':
                    (out / 'triple').mkdir(exist_ok=True)
                    dump(out / 'triple' / f'{v}.json', rec)
                    body = tu.md(rec)
                    (out / 'triple' / f'{v}.md').write_text(body + '\n')
                    t.update(sha256=rec['sha256'], built_at=rec['built_at'], deadline=rec['deadline'],
                             legs=[x['revision'] for x in rec['legs']])
                    issue = os.environ.get('KM_LOCAL_DELIVERY_ISSUE')
                    if issue and now < datetime.fromisoformat(rec['deadline']):
                        c = _gh('POST', f'/repos/{DELIVERY_REPO}/issues/{issue}/comments', {'body': body})
                        back = _gh('GET', f"/repos/{DELIVERY_REPO}/issues/comments/{c['id']}")
                        t['delivery'] = {'USER_DELIVERY_SENT': c['created_at'], 'url': c['html_url'],
                                         'DELIVERY_READBACK_VERIFIED': (back.get('body') or '') == body,
                                         'before_deadline': datetime.fromisoformat(c['created_at'].replace('Z', '+00:00')) < datetime.fromisoformat(rec['deadline'])}
                    log('TRIPLE', v, rec['status'], rec['sha256'][:12], t.get('delivery', {}).get('url'))
                else:
                    t['last_status'] = (rec or {}).get('status')
            elif t.get('sha256') and not t.get('settlement'):
                rec = json.loads((out / 'triple' / f'{v}.json').read_text())
                st = tu.settle(rec, q)
                if st:
                    t['settlement'] = st
                    dump(out / 'triple' / f'{v}.result.json', st)
                    log('TRIPLE_RESULT', v, {k: x['hit'] for k, x in st['tiers'].items()})
                    changed = True
        except Exception as exc:
            t['error'] = f'{type(exc).__name__}:{str(exc)[:120]}'
            log('TRIPLE_FAIL', v, t['error'])
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
    reviewed = False
    metrics = {'tick_at': now.isoformat(), 'requests_before': getattr(getattr(reader, 'client', None), 'requests', 0)}
    cards = {}
    q = load_queue(out)
    if q and any(r.get('settlement') and 'effective_invest' not in r['settlement'] for r in q['races'].values()):
        resettle(day)  # one-time offline re-settlement of legacy (pre-revision) settlements
        q = load_queue(out)
    changed = False
    try:   # NAR / backfill tables for the formal EXT connection, once per race day (private cache, ~1 min)
        from runtime.local_autopilot import ext_connect
        if FORMAL and ext_connect.enabled(day):
            ext_connect.ensure(ROOT, day, refit=False)
    except Exception as exc:
        log('EXT_TABLES_FAIL', day, f'{type(exc).__name__}:{str(exc)[:160]}')
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
        changed |= deliver(q, out, now)
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
                        and r.get('result_attempts', 0) < RESULT_MAX_ATTEMPTS \
                        and now_jst().isoformat() >= (r.get('result_next_at') or ''):
                    jobs.append((3, mins, key, 'RESULT'))
                if r.get('settlement') and r.get('review_attempts', 0) < 2 and (
                        not r.get('review') or (r['review'].get('formal') is False
                                                and (r.get('formal_settlement') or {}).get('result_receipt_verified'))):
                    jobs.append((5, mins, key, 'REVIEW'))   # post-RESULT, lowest priority, local only
                if results and r.get('settlement') and (r.get('formal') or {}).get('status') == 'SIGNED_FINAL' \
                        and not (r.get('formal_settlement') or {}).get('result_receipt_verified') \
                        and r.get('formal_result_attempts', 0) < 3:
                    jobs.append((3, mins, key, 'FORMAL_RESULT'))
                continue
            if r['status'] == 'PREDICTION_FAILURE' and r['attempts'] >= MAX_ATTEMPTS:
                if r.get('failed_code') == CODE_VERSION:
                    continue
                r['attempts'] = 0  # code changed since the failure: retry automatically
                log('RETRY_AFTER_CODE_CHANGE', key, r.get('last_error'))
            if FORMAL and (r.get('formal') or {}).get('status') == 'SIGNED_FINAL' and not r.get('check10') \
                    and r.get('rid') and mins <= CHECK10_MIN and mins > CUTOFF_MIN + 1:
                jobs.append((1.2, mins, key, 'CHECK10'))   # T-10 final check (cutoff-ordered by mins)
            if mins <= FINAL_WINDOW_MIN and '直前版' not in have:
                jobs.append((1, mins, key, '直前版'))
            elif not have:
                jobs.append((2, mins, key, '朝版'))
            elif have[-1] == '直前版' and FORMAL and not r.get('formal') and r.get('formal_attempts', 0) < 2 \
                    and r.get('rid') and mins > CUTOFF_MIN + FORMAL_MIN_LEAD_MIN \
                    and __import__('runtime.local_autopilot.formal_rakuten', fromlist=['x']).runtime_v16_ready():
                jobs.append((1.5, mins, key, 'FORMAL'))
            elif have[-1] == '直前版' and RESEARCH_KRS and not (r.get('research_krs') or {}).get(r['editions'][-1]['rev']) \
                    and r.get('krs_attempts', 0) < MAX_ATTEMPTS \
                    and (out / 'krs' / f"{r['editions'][-1]['rev']}.input.json").exists():
                jobs.append((4, mins, key, 'KRS'))
        jobs.sort()
        if jobs:
            log('TICK', day, 'jobs', len(jobs), [f'{k}:{e}' for _, _, k, e in jobs[:6]])
        for _, _, key, edition in jobs:
            if time.monotonic() - started > budget_seconds:
                log('BUDGET_STOP remaining', len(jobs))
                break
            r = q['races'][key]
            try:
                if edition == 'FORMAL':
                    r['formal_attempts'] = r.get('formal_attempts', 0) + 1
                    from runtime.local_autopilot import formal_rakuten
                    sm, arts = formal_rakuten.run_formal(r, out, cutoff(r))
                    (out / 'formal').mkdir(exist_ok=True)
                    for name, obj in arts.items():
                        dump(out / 'formal' / f'{key}.{name}.json', obj)
                    dump(out / 'formal' / f'{key}.summary.json', sm)
                    if sm['status'] == 'SIGNED_FINAL' or r['formal_attempts'] >= 2:
                        r['formal'] = {k: sm.get(k) for k in ('status', 'first_failed_stage', 'error', 'race_id',
                                                               'final_receipt_sha256', 'final_verified_remote',
                                                               'final_verified_local', 'ticket_count', 'total_investment',
                                                               'no_bet', 'krs_actual_run_count', 'before_cutoff',
                                                               'elapsed_s')} | {'stages': list(sm.get('stages') or {})}
                    log('FORMAL', key, sm['status'], sm.get('first_failed_stage'), sm.get('error', '')[:120], sm['elapsed_s'])
                    if sm['status'] == 'SIGNED_FINAL':
                        deliver_formal(r, key, sm, now_jst())
                    changed = True
                    continue
                if edition == 'CHECK10':
                    check10(reader, r, key, out)
                    changed = True
                    continue
                if edition == 'KRS':
                    rev = r['editions'][-1]['rev']
                    r['krs_attempts'] = r.get('krs_attempts', 0) + 1
                    inp = json.loads((out / 'krs' / f'{rev}.input.json').read_text())
                    sm, env = __import__('runtime.local_autopilot.shadow29', fromlist=['research_krs']).research_krs(
                        inp, f"LOCAL-{r['race_date']}-{key}-{rev.split('.')[-1]}-RESEARCH")
                    sm['revision'] = rev
                    sm['ran_before_post'] = now_jst() < datetime.fromisoformat(r['post_current'])
                    dump(out / 'krs' / f'{rev}.receipt.json', {'summary': sm, 'envelope': env})
                    if 'RECEIPT_VERIFIED' in sm['stages'] or sm['http_status'] >= 400:
                        r.setdefault('research_krs', {})[rev] = {k: sm.get(k) for k in (
                            'actual_run_count', 'input_sha256', 'output_sha256', 'receipt_sha256', 'elapsed_s',
                            'http_status', 'ran_before_post')} | {'stages': list(sm['stages'])}
                    log('KRS', key, rev, sm['http_status'], sm.get('actual_run_count'), list(sm['stages'])[-1], sm['elapsed_s'])
                    changed = True
                    continue
                if edition == 'REVIEW':
                    from runtime.local_autopilot import review as rv
                    r['review_attempts'] = r.get('review_attempts', 0) + 1
                    b = rv.write_race(out, key, r)
                    if b is not None:
                        r['review'] = {'sha256': b['sha256'], 'formal': b['formal_recommendation'] is not None,
                                       'first_material_failure': b['first_material_failure'],
                                       'proposals': [x['id'] for x in b['proposals']], 'reviewed_at': now_jst().isoformat()}
                        r['review_attempts'] = 0
                        reviewed = True
                        log('REVIEW', key, b['first_material_failure'], len(b['proposals']), b['sha256'][:12])
                    changed = True
                    continue
                if edition == 'FORMAL_RESULT':
                    settle_formal(r, key, out, reader.result_page(r['rid']))
                    changed = True
                    continue
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
                                                                  'exact_triple', 'settled_at', 'revision', 'ticket_sha256',
                                                                  'diagnosis')}
                        r['status'] = 'POSTRESULT_DIAGNOSTIC'
                        log('RESULT', key, st['order'][:3], st['payout'])
                        settle_formal(r, key, out, html)
                    else:
                        r['result_next_at'] = (now_jst() + timedelta(minutes=15 * r['result_attempts'])).isoformat()
                        log('RESULT_NOT_READY', key, r['result_attempts'], r['result_next_at'][11:16])
                    changed = True
                else:
                    timing = predict(reader, r, date.fromisoformat(day), edition, out, cards)
                    q['timings'].setdefault('first_prediction_at', now_jst().isoformat())
                    log('OK', key, edition, timing)
                    changed = True
                    # P0-1 (ChatGPT 11/21 review, 佐賀3R pushed 1m13s after cutoff): a revision close to its cutoff is
                    # committed and pushed right away instead of waiting for the end of the tick.
                    if (cutoff(r) - now_jst()).total_seconds() < PUBLISH_NOW_MIN * 60:
                        publish_now(f'{key} {edition}')
            except rk.SourceStop as exc:
                r['status'] = 'SOURCE_HOLD'
                r['last_error'] = str(exc)[:160]
                log('SOURCE_STOP', key, exc)
                changed = True
                break
            except Exception as exc:
                if edition in ('KRS', 'FORMAL', 'FORMAL_RESULT', 'REVIEW'):  # research KRS / formal never affect the PAPER prediction state
                    log('KRS_FAIL', key, f'{type(exc).__name__}:{str(exc)[:160]}')
                    changed = True
                    continue
                r['attempts'] += 1
                r['failed_code'] = CODE_VERSION
                r['status'] = 'PREDICTION_FAILURE' if edition != 'RESULT' else r['status']
                r['last_error'] = f'{type(exc).__name__}:{str(exc)[:120]}'
                dump(out / f'{key}.error.json', {'race': key, 'edition': edition, 'error': r['last_error'],
                                                  'at': now_jst().isoformat(), 'trace': traceback.format_exc()[-1500:]})
                log('FAIL', key, edition, r['last_error'])
                changed = True
        changed |= triple_step(q, out, now_jst())
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
        if q is not None and FORMAL:
            try:   # Owner 2026-11-21 20:00: automatic promotion / demotion once all of the day's races are settled
                if auto_promotion_daily(q, out):   # (checks its own "all settled" and "once per day" conditions)
                    changed = True
            except Exception as e:
                log('AUTO_PROMOTION_FAIL', f'{type(e).__name__}:{str(e)[:160]}')
        if changed and q is not None:
            dump(out / 'queue.json', q)
            report(q, out)
            try:  # per-race delivery ledger (10 separated states, pre-start test, first stop); derived only
                from runtime.local_autopilot import delivery_ledger
                delivery_ledger.write(q, out, now_jst(), CUTOFF_MIN, MAX_ATTEMPTS)
            except Exception as exc:
                log('DELIVERY_LEDGER_FAIL', type(exc).__name__, str(exc)[:120])
            if reviewed:
                try:
                    from runtime.local_autopilot import review as rv
                    rv.write_daily(out, q)
                    rv.write_periods(ROOT)
                except Exception as exc:
                    log('REVIEW_SUMMARY_FAIL', type(exc).__name__, str(exc)[:120])
                try:  # evidence-only shadow measurement (allocation / payout band / NO-BET flags / market / body weight)
                    from runtime.local_autopilot import shadow_measure as smz
                    o = smz.measure(ROOT)
                    (ROOT / 'shadow_measure.json').write_text(json.dumps(o, ensure_ascii=False, indent=1) + '\n')
                    (ROOT / 'shadow_measure.md').write_text(smz.md(o))
                    smz.write_daily(ROOT, out.name)   # per-day: allocation / NO-BET / ◎ vs 1番人気 / 危険な1番人気
                    from runtime.local_autopilot import formal_eval
                    formal_eval.write_daily(out)          # per-day: KRS improved/worsened, 60-point cap effect
                    try:
                        from runtime.local_autopilot import rev_audit
                        rev_audit.write_daily(out)        # Rev2 audit + winner-outside-W diagnosis (evidence only)
                    except Exception as e:
                        log('REV_AUDIT_FAIL', f'{type(e).__name__}:{e}')
                    from runtime.local_autopilot import forward_oos
                    forward_oos.write(ROOT)               # pre-registered candidates, post-freeze races only
                    try:   # P0 index ledger + role-wise AUC of the 29 indices (evidence only)
                        from runtime.local_autopilot import index_audit
                        index_audit.write(ROOT)
                    except Exception as e:
                        log('INDEX_AUDIT_FAIL', f'{type(e).__name__}:{str(e)[:120]}')
                    from runtime.local_autopilot import aki_audit
                    aki_audit.write(ROOT)                 # AKI roughness vs outcome, formation PFS (cumulative)
                    from runtime.local_autopilot import sire_stats
                    sire_stats.write(ROOT, (date.fromisoformat(out.name) + timedelta(days=1)).isoformat())  # stats incl. today
                except Exception as exc:
                    log('SHADOW_MEASURE_FAIL', type(exc).__name__, str(exc)[:120])
            try:
                from runtime.local_autopilot import forward
                forward.write(ROOT)
            except Exception as exc:
                log('FORWARD_SUMMARY_FAIL', type(exc).__name__, str(exc)[:120])
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
    from runtime.local_autopilot import triple_umatan as tu
    for v in tu.VENUES:
        ks = tu.legs(q, v)
        if ks and not (q.get('triple') or {}).get(v, {}).get('sha256'):
            m = (datetime.fromisoformat(q['races'][ks[0]]['post_current']) - now).total_seconds() / 60
            if tu.BUILD_WINDOW_MIN[0] < m <= tu.BUILD_WINDOW_MIN[1] + minutes:
                return True
    for r in q['races'].values():
        mins = (datetime.fromisoformat(r['post_current']) - now).total_seconds() / 60
        have = [e['edition'] for e in r['editions']]
        if mins > CUTOFF_MIN and (not have or (mins <= FINAL_WINDOW_MIN + minutes and '直前版' not in have)):
            return True
        if mins <= -RESULT_DELAY_MIN and r['editions'] and not r.get('settlement') and r.get('result_attempts', 0) < RESULT_MAX_ATTEMPTS:
            return True
        if FORMAL and (r.get('formal') or {}).get('status') == 'SIGNED_FINAL' and not r.get('check10') \
                and CUTOFF_MIN + 1 < mins <= CHECK10_MIN + minutes:
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

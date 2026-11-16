"""LOCAL per-race delivery ledger (derived from queue.json every tick; no new scheduler or channel).

States are kept separate (P0-A 2.3) for the PAPER track and the formal Signed FINAL track:
  RACE_DISCOVERED -> SOURCE_READY -> PREDICTION_FROZEN -> SIGNED_FINAL_VERIFIED (formal only) -> STORED
  -> PUSH_VERIFIED -> DELIVERY_SUBMITTED -> DELIVERY_ACCEPTED (comment read back byte-identical)
  -> USER_REACHED (Owner's own confirmation only, delivery_owner_ack.json) -> OWNER_ACK_VERIFIED (NOT_REQUIRED)
A submission at or after the official post time never counts as pre-start delivery.
"""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROFILE = 'KM-LOCAL-DELIVERY-LEDGER-v1.0-20261117'
JST = timezone(timedelta(hours=9))
TERMINAL = ('POSTRESULT_DIAGNOSTIC', 'SETTLED', 'MISSED_DEADLINE', 'SOURCE_HOLD', 'PREDICTION_FAILURE', 'CANCELLED')


def _t(s):
    if not s or not isinstance(s, str) or not s[:4].isdigit():
        return None
    try:
        return datetime.fromisoformat(s.replace('Z', '+00:00')).astimezone(JST)
    except ValueError:
        return None


def _iso(t):
    return t.isoformat() if t else None


def _acks(day_dir):
    p = Path(day_dir) / 'delivery_owner_ack.json'
    if not p.exists():
        return {}
    try:
        doc = json.loads(p.read_text())
    except ValueError:
        return {}
    out = {}
    for x in doc.get('races') or []:
        out.setdefault(x.get('race'), []).append(x)
    for x in doc.get('paper_deliveries') or []:
        out.setdefault(x.get('race'), []).append(dict(x, channel='PAPER ' + (x.get('edition') or '')))
    return out


def _track(states, post, cut):
    order = list(states)
    first_missing = next((k for k in order if not states[k]['ok']), None)
    sub = states.get('DELIVERY_SUBMITTED', {}).get('at')
    return {'states': states, 'first_failed_stage': first_missing,
            'prestart_delivery': bool(sub and post and _t(sub) < post),
            'before_cutoff_delivery': bool(sub and cut and _t(sub) < cut)}


def race_entry(q, key, r, acks, now, cutoff_min, max_attempts):
    post = _t(r.get('post_current'))
    cut = post - timedelta(minutes=cutoff_min) if post else None
    eds = r.get('editions') or []
    e = eds[-1] if eds else {}
    d = e.get('delivery') or {}
    ack = [a for a in acks.get(key, []) if a.get('USER_REACHED') == 'OWNER_CONFIRMED']
    paper_ack = [a for a in ack if 'PAPER' in (a.get('channel') or '')]
    formal_ack = [a for a in ack if 'formal' in (a.get('channel') or '').lower()]
    S = lambda ok, at=None, **kw: {'ok': bool(ok), 'at': at, **kw}
    sent = d.get('USER_DELIVERY_SENT')
    paper = _track({
        'RACE_DISCOVERED': S(q.get('discovered_at'), q.get('discovered_at')),
        'SOURCE_READY': S(r.get('source_fetched_at') or e.get('source_fetched_at'),
                          r.get('source_fetched_at') or e.get('source_fetched_at')),
        'PREDICTION_FROZEN': S(e.get('frozen_at'), e.get('frozen_at'), rev=e.get('rev'), edition=e.get('edition')),
        'STORED': S(d.get('COMMITTED'), d.get('COMMITTED')),
        'PUSH_VERIFIED': S(d.get('PUSH_VERIFIED'), d.get('PUSH_VERIFIED')),
        'DELIVERY_SUBMITTED': S(_t(sent), sent if _t(sent) else None, rev=r.get('delivered_rev'),
                                url=d.get('delivery_comment_url')),
        'DELIVERY_ACCEPTED': S(d.get('DELIVERY_READBACK_VERIFIED') is True, None),
        'USER_REACHED': S(paper_ack, None, evidence='OWNER_STATEMENT' if paper_ack else
                          (d.get('USER_REACHED') or 'NO_EVIDENCE')),
    }, post, cut)
    paper['OWNER_ACK_VERIFIED'] = 'NOT_REQUIRED'
    f = r.get('formal') or {}
    fd = f.get('delivery') or {}
    formal = None
    if f:
        formal = _track({
            'SIGNED_FINAL_VERIFIED': S(f.get('status') == 'SIGNED_FINAL' and f.get('final_verified_remote'), None,
                                       status=f.get('status'), no_bet=f.get('no_bet'), error=f.get('error'),
                                       first_failed_stage=f.get('first_failed_stage')),
            'DELIVERY_SUBMITTED': S(_t(fd.get('USER_DELIVERY_SENT')), fd.get('USER_DELIVERY_SENT'), url=fd.get('url')),
            'DELIVERY_ACCEPTED': S(fd.get('READBACK_VERIFIED') is True or fd.get('DELIVERY_READBACK_VERIFIED') is True),
            'USER_REACHED': S(formal_ack, None, evidence='OWNER_STATEMENT' if formal_ack else
                              (fd.get('USER_REACHED') or 'NO_EVIDENCE')),
        }, post, cut)
        formal['OWNER_ACK_VERIFIED'] = 'NOT_REQUIRED'
    status = r.get('status')
    open_ = status not in TERMINAL and not r.get('settlement')
    # a stop is only a stop once the deadline passed or the race is terminal; before that it is WAITING
    closed = (cut is not None and now >= cut) or status in TERMINAL
    stop = paper['first_failed_stage'] if closed and paper['first_failed_stage'] not in (None, 'USER_REACHED') else None
    waiting = None if closed else paper['first_failed_stage']
    retry = {
        'reason_code': r.get('failed_code') or r.get('last_error') or (f.get('error') if f else None),
        'retry_eligible': bool(open_ and cut and now < cut and r.get('attempts', 0) < max_attempts),
        'next_retry': 'NEXT_TICK' if open_ and cut and now < cut else None,
        'remaining_deadline_min': round((cut - now).total_seconds() / 60, 1) if cut and open_ else None,
        'recovery_checkpoint': e.get('rev') or None,
    }
    return {'race': key, 'venue': r.get('venue_name'), 'race_no': r.get('race_no'), 'status': status,
            'official_post': _iso(post), 'post_changes': r.get('post_changes') or [], 'cutoff': _iso(cut),
            'paper': paper, 'formal': formal, 'first_stop': stop, 'waiting_for': waiting, 'recovery': retry,
            'delivery_attempts': r.get('delivery_attempts', 0)}


def build(q, day_dir, now=None, cutoff_min=3, max_attempts=3):
    now = now or datetime.now(JST)
    acks = _acks(day_dir)
    rows = [race_entry(q, k, r, acks, now, cutoff_min, max_attempts) for k, r in sorted(q.get('races', {}).items())]
    def cnt(track, cond):
        return sum(1 for x in rows if x[track] and cond(x[track]))
    past = [x for x in rows if x['official_post'] and _t(x['official_post']) <= now]
    summary = {
        'races_managed': len(rows),
        'paper': {'frozen': cnt('paper', lambda t: t['states']['PREDICTION_FROZEN']['ok']),
                  'push_verified': cnt('paper', lambda t: t['states']['PUSH_VERIFIED']['ok']),
                  'submitted': cnt('paper', lambda t: t['states']['DELIVERY_SUBMITTED']['ok']),
                  'submitted_prestart': cnt('paper', lambda t: t['prestart_delivery']),
                  'accepted': cnt('paper', lambda t: t['states']['DELIVERY_ACCEPTED']['ok']),
                  'user_reached_owner_confirmed': cnt('paper', lambda t: t['states']['USER_REACHED']['ok'])},
        'formal': {'attempted': sum(1 for x in rows if x['formal']),
                   'signed_final': cnt('formal', lambda t: t['states']['SIGNED_FINAL_VERIFIED']['ok']),
                   'no_bet': sum(1 for x in rows if x['formal'] and x['formal']['states']['SIGNED_FINAL_VERIFIED'].get('no_bet')),
                   'submitted_prestart': cnt('formal', lambda t: t['prestart_delivery']),
                   'accepted': cnt('formal', lambda t: t['states']['DELIVERY_ACCEPTED']['ok']),
                   'user_reached_owner_confirmed': cnt('formal', lambda t: t['states']['USER_REACHED']['ok'])},
        'posted_races': len(past),
        'posted_without_prestart_paper_delivery': [x['race'] for x in past if not x['paper']['prestart_delivery']],
        'posted_without_prestart_formal': [x['race'] for x in past if not (x['formal'] and x['formal']['prestart_delivery'])],
        'formal_stops': {x['race']: (x['formal']['states']['SIGNED_FINAL_VERIFIED'].get('first_failed_stage')
                                     or x['formal']['first_failed_stage'])
                         for x in rows if x['formal'] and not x['formal']['prestart_delivery']},
        'first_stops': {x['race']: x['first_stop'] for x in rows if x['first_stop']},
        'duplicate_attempts': [x['race'] for x in rows if x['delivery_attempts'] > 1],
    }
    return {'profile': PROFILE, 'race_date': q.get('race_date'), 'generated_at': now.isoformat(),
            'note': 'USER_REACHED counts only the Owner\'s own confirmation; GitHub post/read-back is not proof of reading.',
            'summary': summary, 'races': rows}


def md(L):
    s = L['summary']
    p, f = s['paper'], s['formal']
    out = [f"# 地方版 配送台帳 {L['race_date']}（{L['generated_at'][11:16]}時点）", '',
           f"- 管理Race {s['races_managed']}／発走済み {s['posted_races']}",
           f"- PAPER：凍結 {p['frozen']}・Push検証 {p['push_verified']}・送信 {p['submitted']}（発走前 {p['submitted_prestart']}）"
           f"・読み戻し一致 {p['accepted']}・本人確認 {p['user_reached_owner_confirmed']}",
           f"- 正式：試行 {f['attempted']}・Signed FINAL {f['signed_final']}（NO-BET {f['no_bet']}）・発走前送信 {f['submitted_prestart']}"
           f"・読み戻し一致 {f['accepted']}・本人確認 {f['user_reached_owner_confirmed']}",
           f"- 発走前PAPER配送なしで発走：{s['posted_without_prestart_paper_delivery'] or 'なし'}",
           f"- 発走前の正式配送なしで発走（未試行を含む）：{s['posted_without_prestart_formal'] or 'なし'}",
           f"- 正式の停止工程：{s['formal_stops'] or 'なし'}",
           f"- 停止工程：{s['first_stops'] or 'なし'}／配送再試行：{s['duplicate_attempts'] or 'なし'}", '',
           '| Race | 発走 | 状態 | PAPER送信 | 発走前 | 正式 | 正式送信 | 発走前 | 停止工程 |', '|---|---|---|---|---|---|---|---|---|']
    for x in L['races']:
        ps = x['paper']['states']['DELIVERY_SUBMITTED']['at']
        fo = x['formal']
        out.append(f"| {x['race']} | {(x['official_post'] or '')[11:16]} | {x['status']} | {(_iso(_t(ps)) or '-')[11:16]} | "
                   f"{'○' if x['paper']['prestart_delivery'] else '×'} | "
                   f"{(fo['states']['SIGNED_FINAL_VERIFIED'].get('status') if fo else '-')} | "
                   f"{((_iso(_t(fo['states']['DELIVERY_SUBMITTED']['at'])) or '-')[11:16]) if fo else '-'} | "
                   f"{('○' if fo['prestart_delivery'] else '×') if fo else '-'} | {x['first_stop'] or ''} |")
    out += ['', f"<sub>{L['note']}</sub>", '']
    return '\n'.join(out)


def write(q, day_dir, now=None, cutoff_min=3, max_attempts=3):
    L = build(q, day_dir, now, cutoff_min, max_attempts)
    (Path(day_dir) / 'delivery_ledger.json').write_text(json.dumps(L, ensure_ascii=False, indent=1) + '\n')
    (Path(day_dir) / 'delivery_ledger.md').write_text(md(L))
    return L

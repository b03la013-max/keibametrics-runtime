"""BAN sources: 楽天競馬 帯広 (baba 03) card/result via the LOCAL throttled client, own speed index,
NAR official ledger history (Owner-downloaded ZIP extract on the Mac), optional キンタロー/水分ボンバー/競馬ブック
feeds (files dropped by the browser-side collectors; absent -> neutral + DCR-B down)."""
import csv
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE.parent / 'local_autopilot'))
import rakuten as RK  # noqa: E402

BABA = '03'
MODEL = json.loads((HERE / 'speed_model.json').read_text())
Z2H = str.maketrans('０１２３４５６７８９ＡＢＣＯＰ', '0123456789ABCOP')


def race_class(name):
    s = RK.nfkc(name).translate(Z2H)
    m = re.search(r'(A1|A2|B1|B2|B3|B4|C1|C2|C3|OP|オープン)', s)
    return (m.group(1) if m else 'OTHER').replace('オープン', 'OP')


def speed_index(sec, load, moisture, month, cls, young):
    """Own index (NAR-fit OLS, research/banei_nar/build.py). Unknown moisture -> training mean."""
    if sec is None or load is None:
        return None
    m = MODEL['moisture_mean'] if moisture is None else moisture
    f = {'load': load, 'm': m, 'm2': m * m, 'y': 1.0 if young else 0.0, f'mon_{month}': 1.0, f'cls_{cls}': 1.0, 'c': 1.0}
    pred = sum(c * f.get(col, 0.0) for col, c in zip(MODEL['columns'], MODEL['coef']))
    return round(80 - 10 * (sec - pred) / MODEL['sd'], 2)


def _sec(t):
    m = re.fullmatch(r'(?:(\d+):)?(\d{1,2}\.\d)', t or '')
    return None if not m else int(m[1] or 0) * 60 + float(m[2])


# ------------------------------------------------------------------ 楽天 (ばんえい card template)
def day_meeting(top_html, day):
    d = day.replace('-', '')
    for rid in re.findall(r'race_card/list/RACEID/(\d{18})', top_html):
        if rid.startswith(d) and rid[8:10] == BABA:
            return rid[:16]
    return None


def parse_menu_ban(card_html, day):
    """(race_no, rid, 'HH:MM') for the whole 帯広 day. 楽天 menu links use a meeting-coded prefix
    (e.g. 2026112103041701RR); the canonical day+'03030000'+RR id serves the same card (verified 2026-11-21)."""
    i = card_html.find('<ul class="raceNumber')
    seg = card_html[i:card_html.find('</ul>', i)]
    d = day.replace('-', '')
    out = {}
    for num, hhmm in re.findall(r'<span class="num">(\d{1,2})R</span>\s*<span class="time">(\d{1,2}:\d{2})</span>', seg):
        out[int(num)] = (int(num), f'{d}{BABA}0300{int(num):04d}'[:18], hhmm)
    return sorted(out.values())


def parse_start_ban(td):
    """One past start cell (ばんえい: 200ダ, load 3 digits, time m:ss.s (margin), body 4 digits k)."""
    if 'class="place"' not in td:
        return None
    place = re.search(r'<span class="place">(.*?)</span>', td, re.S)
    body = td[td.find('</div>') + 6:]
    L = RK.lines(body)
    ft = RK.text(place[1]) if place else ''
    rid = re.search(r'race_performance/list/RACEID/(\d{18})', td)
    out = {'finish': int(ft) if ft.isdigit() else None, 'date': None, 'race_name': '', 'pop': None,
           'race_no': int(rid[1][-2:]) if rid else None, 'moisture': None,
           'jockey': None, 'load': None, 'sec': None, 'margin': None, 'body_weight': None}
    for k, ln in enumerate(L):
        m = re.fullmatch(r'(\S+)\s+(\d{2}\.\d{2}\.\d{2})', ln)
        if m and not out['date']:
            out['date'] = m[2]
            out['race_name'] = L[k + 1] if k + 1 < len(L) else ''
            continue
        m = re.search(r'200(?:ダ|ば)?\s*(\d+)人', ln)
        if m and out['pop'] is None:
            out['pop'] = int(m[1])
            continue
        m = re.fullmatch(r'[☆▲△◇★]?(\S+?)\s+(\d{3,4})', ln)
        if m and out['load'] is None and out['pop'] is not None:
            out['jockey'], out['load'] = m[1], int(m[2])
            continue
        m = re.search(r'((?:\d+:)?\d{1,2}\.\d)\s*\((-?\d+\.\d)\)', ln)
        if m:
            out['sec'], out['margin'] = _sec(m[1]), float(m[2])
            continue
        m = re.search(r'(\d{3,4})k', ln)
        if m and out['body_weight'] is None:
            out['body_weight'] = int(m[1])
    return out


def special_notes(html):
    """楽天 出馬表の特記事項 → [(馬番, 内容)]."""
    out = []
    for ul in re.findall(r"<ul class=['\"]specialNote['\"]>(.*?)</ul>", html, re.S):
        for li in re.findall(r'<li>(.*?)</li>', ul, re.S):
            t = re.sub(r'<[^>]+>', '', li).replace('&nbsp;', ' ').strip()
            m = re.match(r'(\d+)番\s*(.+)', t)
            if m:
                out.append((int(m[1]), m[2].strip()))
    return out


def result_non_starters(html):
    """楽天 成績の着差欄が「取消」「除外」の馬番（着順欄は「-」で、地方版の判定では競走中止に入ってしまう）。"""
    out = []
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.S):
        num = re.search(r'<td class="number">\s*(\d+)\s*</td>', tr)
        lead = re.search(r'<td class="lead">(.*?)</td>', tr, re.S)
        if num and lead and re.search(r'取消|除外', lead[1]):
            out.append(int(num[1]))
    return out


def parse_card_ban(html):
    i = html.find('<tbody class="raceCard">')
    body = html[i:html.find('</tbody>', i)]
    runners = []
    last = 0
    for blk in re.split(r'<tr class="box\d+(?=[ "])', body)[1:]:
        tds = re.findall(r'<t[dh][^>]*class="([^"]*)"[^>]*>(.*?)</t[dh]>', blk, re.S)
        cell, starts = {}, []
        for cls, inner in tds:
            (starts.append(inner) if cls.startswith('race') else cell.setdefault(cls.split()[0], inner))
        number = RK.text(cell.get('number'))
        nm = re.search(r'<span class="mainHorse">.*?>([^<]+)</a>', cell.get('name', ''), re.S)
        app = cell.get('name', '').split('<div class="append">')[1] if '<div class="append">' in cell.get('name', '') else ''
        rate = re.search(r'<span class="rate">(.*?)</span>', app, re.S)
        rt = RK.text(rate[1]) if rate else ''
        win = re.search(r'(\d+\.\d+)', rt)
        pop = re.search(r'(\d+)人気', rt)
        prof = RK.lines(cell.get('profile', ''))
        age = re.match(r'[牡牝セ騸]\s*(\d+)', prof[0]) if prof else None
        load = next((int(x) for x in prof if re.fullmatch(r'\d{3,4}', x)), None)
        jm = re.search(r'jockey/detail/JOCKEYID/\d+">([^<]+)</a>', cell.get('profile', ''))
        wr = [int(v) for v in re.findall(r'\d{3,4}', RK.text(cell.get('weight')))]
        wd = RK.lines(cell.get('weightDistance'))
        cur = int(wd[0]) if wd and re.fullmatch(r'\d{3,4}', wd[0]) else None
        chg = RK._int(wd[1].replace('±', '')) if len(wd) > 1 else None
        cancelled = not number.isdigit() or any(k in number + rt for k in ('取消', '除外', '中止'))
        no = int(number) if number.isdigit() else last + 1
        last = no
        runners.append({'no': no, 'name': RK.nfkc(nm[1]) if nm else RK.text(cell.get('name'))[:20],
                        'age': int(age[1]) if age else None, 'load': load,
                        'jockey': RK.nfkc(jm[1]) if jm else None,
                        'odds': float(win[1]) if win and not cancelled and float(win[1]) > 0 else None,
                        'pop': int(pop[1]) if pop else None,
                        'good_bw_range': (min(wr), max(wr)) if wr else None,
                        'body_weight': cur, 'body_delta': chg, 'scratched': cancelled,
                        'starts': [s for s in (parse_start_ban(t) for t in starts) if s]})
    # 特記事項（<ul class='specialNote'>: 「10番 騎手変更 鈴木恵介→阿部武臣」「4番 出走取消」等）を出走馬へ反映
    for no, what in special_notes(html):
        x = next((y for y in runners if y['no'] == no), None)
        if not x:
            continue
        m = re.match(r'騎手変更\s*(\S+?)→(\S+)', what)
        if m:
            x.update(jockey=m[2], jockey_changed_from=m[1])
        elif re.search(r'取消|除外', what):
            x['scratched'] = True
    # 人気 is cut off for 'hot' horses (nested <span class="hot"> ends the rate span early): rank by odds
    ranked = sorted((x['odds'], x['no']) for x in runners if x['odds'] and not x['scratched'])
    for i, (_, no) in enumerate(ranked):
        x = next(y for y in runners if y['no'] == no)
        if x['pop'] is None:
            x['pop'] = i + 1
    return runners


def moisture_from_header(html):
    m = re.search(r'(?:馬場水分|水分)[^0-9]{0,20}(\d\.\d)', RK.nfkc(re.sub(r'<[^>]+>', ' ', html[:20000])))
    return float(m[1]) if m else None


# ------------------------------------------------------------------ 水分ボンバー (SBO) 帯広 = venue code 3
SBO_CODE = 3


def parse_sbo_ban(html):
    """帯広 table.html: 馬番, 馬名, 調教師, 負担重量, 騎手, 馬体重, 近走指数(n), 馬場指数(n), 平均指数.
    Returns ({no: {'recent','track','avg','n_recent','n_track'}}, moisture %)."""
    def num(cell):
        m = re.match(r'\s*(\d+(?:\.\d+)?)\s*(?:\((\d+)\))?', cell)
        if not m:
            return None, 0
        n = int(m[2]) if m[2] is not None else 1
        return (float(m[1]) if n > 0 else None), n
    mo = re.search(r'馬場\s*[:：]\s*(\d\.\d)\s*%', RK.nfkc(re.sub(r'<[^>]+>', ' ', html)))
    t = re.search(r'<table id="table">(.*?)</table>', html, re.S)
    out = {}
    for tr in re.findall(r'<tr>(.*?)</tr>', t[1] if t else '', re.S):
        tds = [RK.nfkc(re.sub(r'<[^>]+>', ' ', td)).strip() for td in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
        if len(tds) < 9 or not tds[0].isdigit():
            continue
        rec, n1 = num(tds[6])
        trk, n2 = num(tds[7])
        avg, _ = num(tds[8])
        out[int(tds[0])] = {'recent': rec, 'track': trk, 'avg': avg, 'n_recent': n1, 'n_track': n2}
    return out, (float(mo[1]) if mo else None)


def sbo_race(client, day, race_no):
    """Fetch via the LOCAL SBO client (robots, >=10 s spacing, 30 min hold on 403/429/503).
    Raw page / SBO numbers stay out of the public repo: only SHA-256 + derived values are written."""
    import hashlib
    path = f"/{day.replace('-', '')}/{SBO_CODE}/{race_no}/table.html"
    html = client.get(path)
    table, moist = parse_sbo_ban(html)
    return {'path': path, 'sha256': hashlib.sha256(html.encode()).hexdigest(), 'table': table, 'moisture': moist}


# ------------------------------------------------------------------ 競馬ブック comments -> CCI-B band
CCI_STRONG = ('好勝負', 'チャンス', '力上位', '上位争い', '本来の姿', '一変', '巻き返し', '勝ち負け', '好調', 'デキはいい')
CCI_COND = ('展開', '障害次第', 'ひと腰なら', '流れに乗れば', '軽馬場なら', '修正でき', 'すんなり')
CCI_CAUTION = ('様子見', '追走いっぱい', '決め手欠く', '強気には', '厳しい', '手を出せない', 'どうか')


def cci_band(*texts):
    """攻略条項 4-12/4-13 + v2.3 第63条: meaning bands, never a single weak word alone."""
    t = ' '.join(x for x in texts if x)
    if not t:
        return None
    s = sum(k in t for k in CCI_STRONG)
    c = sum(k in t for k in CCI_CAUTION)
    if s >= 2 and c == 0:
        return 'VERY_STRONG'
    if s > c:
        return 'STRONG'
    if c >= 2 and s == 0:
        return 'CAUTION'
    return 'NEUTRAL'


# ------------------------------------------------------------------ NAR ledger + feeds
def nar_history(nar_dir):
    """{horse_name: [ {date, idx, moisture}, ... newest first]} from the Owner's NAR extract (optional)."""
    p = Path(nar_dir or '') / 'ban_horselist.csv'
    q = Path(nar_dir or '') / 'ban_racelist.csv'
    if not p.exists() or not q.exists():
        return {}
    races = {}
    with q.open(encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            races[(row['競走年月日'], row['レース番号'])] = row
    hist = {}
    with p.open(encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            rc = races.get((row['競走年月日'], row['レース番号']))
            if not rc:
                continue
            # 取消・除外・競走中止・競走取止めは着順もタイムも空: 0秒として指数にしない（11/21 ChatGPT反省 P0-3）
            fin_raw = (row.get('着順') or '').strip()
            if not re.sub(r'[^\d]', '', fin_raw) or not re.sub(r'[^\d1-9]', '', row.get('タイム') or ''):
                continue
            t = (row.get('タイム') or '').zfill(4)
            try:
                sec = int(t[:-3]) * 60 + int(t[-3:]) / 10
                load = int(re.sub(r'[^\d]', '', row['負担重量']))
                moist = float(rc['馬場'])
            except (ValueError, TypeError):
                continue
            d = row['競走年月日']
            idx = speed_index(sec, load, moist, int(d[4:6]), race_class(rc['レース名']),
                              '2歳' in rc['条件'] or '２歳' in rc['条件'])
            fin = re.sub(r'[^\d]', '', row.get('着順') or '')
            bwt = re.sub(r'[^\d]', '', row.get('馬体重') or '')
            hist.setdefault(row['馬名'], []).append({'date': d, 'idx': idx, 'moisture': moist,
                                                    'jockey': row.get('騎手名'), 'race_name': rc.get('レース名'),
                                                    'finish': int(fin) if fin else None,
                                                    'body_weight': int(bwt) if bwt else None})
    for v in hist.values():
        v.sort(key=lambda z: z['date'], reverse=True)
    return hist


def load_feed(feed_dir, day, kind):
    """Browser-side collector outputs: <feed_dir>/<day>/<kind>.json (kind = kintaro / sbo / keibabook)."""
    p = Path(feed_dir or '') / day / f'{kind}.json'
    return json.loads(p.read_text()) if p.exists() else {}


def parse_odds_rank(html, ordered):
    """楽天 /odds/sanrenfuku|sanrentan/ の人気順一覧（tbody.rank: 順位・組番・オッズ）→ {(a,b,c): odds}.
    三連複は昇順タプル、三連単は着順どおり。発売前（0.0・空）は除く。"""
    out = {}
    i = html.find('<tbody class="rank">')
    body = html[i:html.find('</tbody>', i)] if i >= 0 else ''
    for combo, odds in re.findall(r'<td>\s*\d+\s*</td>\s*<td>\s*([\d\-→]+)\s*</td>\s*<td[^>]*>\s*<span[^>]*>\s*([\d.,]+)\s*</span>', body):
        nums = tuple(int(x) for x in re.split(r'[-→]', combo) if x)
        try:
            o = float(odds.replace(',', ''))
        except ValueError:
            continue
        if len(nums) == 3 and o > 0:
            out[nums if ordered else tuple(sorted(nums))] = o
    return out


def official_comment_band(feed, race_no, no):
    """ばんえい十勝の公式発表（重賞の全調教師・騎手コメント）: 馬番ごとの文面を CCI-B の材料として返す。"""
    r = (feed or {}).get(str(race_no)) or {}
    v = r.get(str(no)) or {}
    return ' '.join(x for x in (v.get('trainer'), v.get('jockey')) if x) or None


def build_horses(card, moisture, race_date, hist, feeds, race_no, race_name='', skilled=None):
    """Card + history + feeds -> engine horse dicts (provenance kept by the engine)."""
    import derive
    from engine import moisture_band
    kin = (feeds.get('kintaro') or {}).get(str(race_no), {})
    sbo = (feeds.get('sbo') or {}).get(str(race_no), {})
    kb = (feeds.get('keibabook') or {}).get(str(race_no), {})
    dt = datetime.strptime(race_date, '%Y-%m-%d')
    band = moisture_band(moisture)
    out = []
    for r in card:
        nar = [z for z in hist.get(r['name'], []) if z['date'] < dt.strftime('%Y%m%d')]
        k = kin.get(str(r['no']), {})
        kbh = dict(kb.get(str(r['no']), {}))
        off = official_comment_band(feeds.get('official'), race_no, r['no'])            # 重賞の公式コメント
        kbh['cci'] = kbh.get('cci') or cci_band(kbh.get('short'), kbh.get('danwa'), kbh.get('point'),
                                                (kin.get(str(r['no'])) or {}).get('comment'), off)   # + キンタロー短評 (spec 3-2)
        kbh['official_comment'] = bool(off)
        flags = derive.horse_inputs(r, k, kbh, nar, skilled or set(), race_name, band)   # also fills start moisture
        own = []
        for s in r['starts']:
            if s.get('sec') and s.get('load') and s.get('date'):
                d = datetime.strptime('20' + s['date'], '%Y.%m.%d')
                own.append({'idx': speed_index(s['sec'], s['load'], s.get('moisture'), d.month, race_class(s['race_name']), False),
                            'moisture': s.get('moisture'), 'date': d.strftime('%Y%m%d')})
        seen = {z['date'] for z in nar}
        own = sorted(nar + [z for z in own if z['date'] not in seen], key=lambda z: z['date'], reverse=True)
        sb = (sbo.get('table') or {}).get(r['no']) or (sbo.get('table') or {}).get(str(r['no']))
        rng = r.get('good_bw_range')
        if not rng:                                # 21-4: good-run body-weight range from 1-3着 runs (NAR ledger)
            good = [z['body_weight'] for z in nar if z.get('finish') and z['finish'] <= 3 and z.get('body_weight')]
            rng = (min(good), max(good)) if good else None
        bw, bd = r.get('body_weight'), r.get('body_delta')
        out.append({**r, **flags, 'own_past': own, 'idx_sbo': sb, 'good_bw_range': rng,
                    'good_bw_src': 'CARD' if r.get('good_bw_range') else ('NAR' if rng else None),
                    'body_delta_pct': round(100 * bd / (bw - bd), 2) if bw and bd is not None and bw != bd else (0.0 if bd == 0 else None),
                    'nar_starts': len(nar),
                    'kintaro_past': k.get('past', []), 'front_ok': k.get('front_ok'),
                    'barrier_stable': k.get('barrier_stable'),
                    'cci': kbh['cci'], 'official_comment': kbh['official_comment'],
                    'moisture_known': moisture is not None,
                    'body_stable': r['body_delta'] is not None and abs(r['body_delta']) < 16})
    return out

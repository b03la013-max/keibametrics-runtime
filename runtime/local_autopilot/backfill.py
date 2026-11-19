"""Historical result backfill from the public Rakuten result pages (Owner approval 2026-11-19 01:28 JST).

Class: HISTORICAL_BACKFILL_LEARNING -- learning / backtest material only. It feeds stratum base rates
(venue x distance x going), sire statistics and pre-registration of hypotheses; it is NEVER Forward OOS
evidence and never promotes anything by itself.

Access policy is the live worker's (rakuten.Client): honest UA, robots.txt checked on every path,
Crawl-Delay 60 -> >= 61 s between ANY two requests (the same persisted source_state.json as the race-day
worker, so the two can never overlap), no retry on 403/429/503 (30 min hold), no raw HTML in Git.
It runs only inside the worker loop when no race work is due within 12 min, at night (21:30-08:30 JST).

Discovery (newest day first, back to WINDOW_START):
  day page /race_card/list/RACEID/<YYYYMMDD>0000000000 -> the venue list ids of that date;
  result page of 1R -> every RACEID of the same meeting on the page -> race numbers;
  each race: order / payouts (settle.parse_result), header (distance, going), every result row's cells.
If the first DISCOVERY_PROBE day pages yield nothing, discovery stops and the page's link patterns are
written to probe.json for inspection instead of guessing ids.
"""
import argparse
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

from runtime.local_autopilot import rakuten as rk
from runtime.local_autopilot import settle

PROFILE = 'KM-LOCAL-HISTORICAL-BACKFILL-v1.0-20261119'
CLASS = 'HISTORICAL_BACKFILL_LEARNING (not Forward OOS)'
WINDOW_START = '2026-08-01'
DISCOVERY_PROBE = 3
NIGHT = ((21, 30), (8, 30))
ROOT = Path(os.environ.get('KM_LOCAL_AUTOPILOT_OUT') or Path(__file__).resolve().parent / 'output')
RID = re.compile(r'RACEID/(\d{18})')


def is_night(now):
    hm = (now.hour, now.minute)
    return hm >= NIGHT[0] or hm < NIGHT[1]


def link_summary(html):
    ids = RID.findall(html)
    pat = Counter('DAY' if x[8:] == '0000000000' else f"{x[8:10]}:{'LIST' if x[-2:] == '00' else 'RACE'}" for x in ids)
    hrefs = Counter(re.sub(r'\d', '9', h) for h in re.findall(r'href="(/[^"#?]{3,80})', html))
    return {'raceids': len(ids), 'raceid_samples': sorted(set(ids))[:40], 'patterns': pat.most_common(20),
            'href_shapes': hrefs.most_common(40)}


def day_meetings(html, d):
    out = {}
    for x in RID.findall(html):
        if x.startswith(d) and x[8:10] in rk.VENUES and x[8:] != '0000000000':
            out[x[8:10]] = x[:16]
    return out


def parse_rows(html):
    i = html.find('<tbody class="record">')
    body = html[i:html.find('</tbody>', i)] if i >= 0 else ''
    rows = []
    for row in re.split(r'<tr class="box', body)[1:]:
        cells = {}
        hid = re.search(r'HORSEID/(\d+)', row)
        if hid:
            cells['horse_id'] = hid[1]
        for cls, val in re.findall(r'<t[dh] class="([\w ]+)"[^>]*>(.*?)</t[dh]>', row, re.S):
            k = cls.split()[0]
            cells[k if k not in cells else f'{k}_{sum(1 for c in cells if c.startswith(k))}'] = rk.text(val)
        if cells:
            rows.append(cells)
    return rows


def parse_page(html):
    h = rk.parse_header(html)
    t = rk.text(html[:200000])
    if not h.get('distance'):
        m = re.search(r'(ダ|芝)?\s*([\d,]{3,5})m', t)
        h['distance'] = int(m[2].replace(',', '')) if m else None
    if not h.get('going'):
        m = re.search(r'馬場[:：]?\s*(良|稍重|重|不良)', t) or re.search(r'(?:ダ|芝)[:：]\s*(良|稍重|重|不良)', t)
        h['going'] = m[1] if m else None
    w = re.search(r'天候[:：]?\s*(晴|曇|雨|小雨|雪|小雪)', t)
    h['weather'] = w[1] if w else None
    i = html.find('summary="コーナー通過順位"')
    seg = html[i:html.find('</table>', i)] if i >= 0 else ''
    h['corners'] = [[rk.nfkc(a), rk.nfkc(b)] for a, b in
                    re.findall(r'<th scope="row">(.*?)</th>\s*<td class="time">(.*?)</td>', seg, re.S)]
    res = settle.parse_result(html)
    if res:
        res['payouts'] = {k: {'-'.join(map(str, c)): y for c, y in v.items()} for k, v in res['payouts'].items()}
    return {'header': h, 'result': res, 'rows': parse_rows(html)}


class Backfill:
    def __init__(self, root=ROOT, reader=None, window_start=WINDOW_START, today=None):
        self.dir = Path(root) / 'backfill'
        self.dir.mkdir(parents=True, exist_ok=True)
        self.sp = self.dir / 'state.json'
        try:
            self.st = json.loads(self.sp.read_text())
        except (OSError, ValueError):
            self.st = {'profile': PROFILE, 'class': CLASS, 'days': {}, 'races': {}}
        self.st['window_start'] = window_start
        self.reader = reader or rk.Reader(Path(root) / 'source_state.json')
        self.today = today or datetime.now(rk.JST).date().isoformat()
        self.probe_dir = os.environ.get('KM_BACKFILL_PROBE_DIR')
        self.fetched = 0

    def save(self):
        self.st['updated_at'] = datetime.now(rk.JST).isoformat()
        self.sp.write_text(json.dumps(self.st, ensure_ascii=False, indent=0) + '\n')

    def _sample(self, name, html):
        if self.probe_dir:                         # local (non-Git) parser-check samples; best effort
            try:
                p = Path(self.probe_dir)
                p.mkdir(parents=True, exist_ok=True)
                if len(list(p.glob('*.html'))) < 6:
                    (p / f'{name}.html').write_text(html)
            except OSError:
                self.probe_dir = None

    def _get(self, path):
        self.fetched += 1
        try:
            return self.reader.client.get(path)
        except rk.SourceStop as e:
            if str(e).startswith('HTTP_404') or str(e).startswith('HTTP_410'):
                return None
            raise

    def next_day(self):
        d = date.fromisoformat(self.today) - timedelta(days=1)
        stop = date.fromisoformat(self.st['window_start'])
        while d >= stop:
            if d.isoformat() not in self.st['days']:
                return d.isoformat()
            d -= timedelta(days=1)
        return None

    def pending_race(self):
        for rid in sorted((r for r, v in self.st['races'].items() if v['status'] == 'PENDING'), reverse=True):
            return rid
        return None

    def discover_day(self, day):
        d = day.replace('-', '')
        html = self._get(f'/race_card/list/RACEID/{d}0000000000')
        meet = day_meetings(html or '', d)
        self._sample(f'day_{d}', html or '')
        self.st['days'][day] = {'status': 'DISCOVERED' if meet else 'NO_MEETING_LINKS', 'venues': meet}
        if not meet:
            empty = [k for k, v in self.st['days'].items() if v['status'] == 'NO_MEETING_LINKS']
            found = [k for k, v in self.st['days'].items() if v['status'] == 'DISCOVERED']
            if not found and len(empty) >= DISCOVERY_PROBE:
                self.st['discovery'] = 'FAILED_SEE_PROBE'
                (self.dir / 'probe.json').write_text(json.dumps(
                    {'day': day, 'page': f'/race_card/list/RACEID/{d}0000000000', **link_summary(html or '')},
                    ensure_ascii=False, indent=1) + '\n')
        for code, prefix in meet.items():
            self.st['races'].setdefault(prefix + '01', {'status': 'PENDING', 'day': day, 'code': code})

    def fetch_race(self, rid):
        info = self.st['races'][rid]
        html = self._get('/race_performance/list/RACEID/' + rid)
        if html is None:
            info['status'] = 'NOT_FOUND'
            return
        self._sample(f'res_{rid}', html)
        page = parse_page(html)
        prefix = rid[:16]
        for x in set(RID.findall(html)):          # the meeting's other races (1R page lists them)
            if x.startswith(prefix) and x[-2:] != '00' and x not in self.st['races']:
                self.st['races'][x] = {'status': 'PENDING', 'day': info['day'], 'code': info['code']}
        vid, vname = rk.VENUES[info['code']]
        rno = int(rid[-2:])
        rec = {'profile': PROFILE, 'class': CLASS, 'rid': rid, 'race_date': info['day'], 'venue_id': vid,
               'venue_name': vname, 'race_no': rno, 'fetched_at': datetime.now(rk.JST).isoformat(), **page}
        out = self.dir / 'results' / info['day']
        out.mkdir(parents=True, exist_ok=True)
        (out / f'{vid}_{rno:02d}.json').write_text(json.dumps(rec, ensure_ascii=False) + '\n')
        info['status'] = 'DONE' if page['result'] else 'NO_RESULT_TABLE'

    def run(self, budget):
        t0 = time.time()
        try:
            while time.time() - t0 < budget - 70:
                if self.st.get('discovery') == 'FAILED_SEE_PROBE' and not self.pending_race():
                    break
                rid = self.pending_race()
                if rid:
                    self.fetch_race(rid)
                else:
                    day = self.next_day()
                    if not day:
                        self.st['complete'] = True
                        break
                    self.discover_day(day)
                self.save()
        except rk.SourceStop as e:
            self.st['last_stop'] = str(e)
        self.save()
        try:                                       # refresh the statistical tables (learning data, evidence only)
            from runtime.local_autopilot import hist_stats
            hs = hist_stats.write(self.dir.parent)
            self.st['hist_stats'] = {'races': hs['races'], 'starts': hs['starts']} if hs else None
        except Exception as e:                     # never let the tables break the backfill
            self.st['hist_stats'] = f'FAIL:{type(e).__name__}:{e}'
        c = Counter(v['status'] for v in self.st['races'].values())
        print('BACKFILL', json.dumps({'fetched': self.fetched, 'days': len(self.st['days']), 'races': dict(c),
                                      'discovery': self.st.get('discovery'), 'stop': self.st.get('last_stop')},
                                     ensure_ascii=False))
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--budget', type=int, default=420)
    ap.add_argument('--force', action='store_true', help='ignore the night window')
    a = ap.parse_args()
    if not a.force and not is_night(datetime.now(rk.JST)):
        print('BACKFILL_SKIP_DAYTIME')
        return 0
    return Backfill().run(a.budget)


if __name__ == '__main__':
    sys.exit(main())

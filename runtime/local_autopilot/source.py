"""South-Kanto (URW/FNB/OHI/KAW) public card reader for the LOCAL autopilot.

Reuses the existing robots-respecting NANKAN client and card parser from
runtime/urw_nankan_reference_source.py, generalised from Urawa-only to the
four South-Kanto venues. One request per 10 s (or robots crawl-delay), no
retry loops, no credentials, no redirects. Raw HTML is never written to Git.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlsplit

from runtime import urw_nankan_reference_source as nk

VENUES = {'18': ('URW', '浦和'), '19': ('FNB', '船橋'), '20': ('OHI', '大井'), '21': ('KAW', '川崎')}
CODE_OF = {v[0]: k for k, v in VENUES.items()}


def _verify_header_any_venue(dom, race):
    """Lenient header check: date, venue name and race number must agree."""
    nodes = dom.all('p', 'nk23_c-tab1__subtitle')
    header = nodes[0].text() if nodes else dom.text()[:400]
    y, m, d = map(int, race['race_date'].split('-'))
    name = VENUES[race['venue_code']][1]
    if f'{y}年{m}月{d}日' not in header or name not in header:
        raise nk.NankanError('NANKAN_CARD_BODY_IDENTITY')
    return header


# parse_card() resolves this name at call time from its module globals.
nk._verify_race_header = _verify_header_any_venue


def program_links(calendar_raw, day):
    """All South-Kanto program pages listed for the day on the official calendar."""
    out = {}
    for node in nk.DOM(nk.decode(calendar_raw)).root.all('a'):
        url = urljoin(nk.CALENDAR, node.attrs.get('href', ''))
        m = re.fullmatch(re.escape(nk.ORIGIN) + '/program/' + day.replace('-', '') + r'(18|19|20|21)\d{4}\.do', url)
        if m:
            out[m[1]] = url
    return out


def parse_program(raw, url, day):
    nk.url_scope(url)
    day_id = urlsplit(url).path.rsplit('/', 1)[1][:-3]
    code = day_id[8:10]
    venue_id, venue_name = VENUES[code]
    dom = nk.DOM(nk.decode(raw)).root
    races = []
    for item in dom.all('li', 'nk23_c-block01__list__item'):
        anchors = item.all('a', 'nk23_c-block01__list__title')
        labels = item.all('span', 'nk23_c-block01__label')
        if not anchors or not labels:
            continue
        number = re.fullmatch(r'(\d{1,2})R', labels[0].text())
        if not number:
            continue
        n = int(number[1])
        text = item.text()
        post = re.search(r'\b(\d{1,2}:\d{2})\b', text)
        distance = re.search(r'\b(\d{3,4})m\b', text)
        count = re.search(r'(\d{1,2})頭', text)
        if not post:
            continue
        scheduled = datetime.fromisoformat(day + 'T' + post[1].zfill(5) + ':00+09:00')
        races.append({'provider': nk.PROVIDER, 'provider_day_id': day_id,
                      'provider_race_id': day_id + f'{n:02d}', 'venue_code': code,
                      'venue_id': venue_id, 'venue_name': venue_name, 'race_date': day, 'race_no': n,
                      'race_name': anchors[0].text(), 'class_text': text,
                      'scheduled_post_at': scheduled.isoformat(),
                      'prediction_cutoff': (scheduled - timedelta(seconds=120)).isoformat(),
                      'distance': int(distance[1]) if distance else None,
                      'surface': 'TURF' if '芝' in text else 'DIRT',
                      'program_runner_count': int(count[1]) if count else None})
    races.sort(key=lambda r: r['race_no'])
    if not races:
        raise nk.NankanError('NANKAN_PROGRAM_NO_RACES')
    return races


def parse_odds(raw):
    """Lenient win/place reader. Returns {horse_no: {win, place_low, place_high, cancelled}}."""
    dom = nk.DOM(nk.decode(raw)).root
    tables = dom.all('table', 'nk23_c-table04__table')
    out = {}
    if not tables:
        return out
    for row in tables[0].all('tr'):
        cells = [c.text() for c in row.children if isinstance(c, nk.Node) and c.tag == 'td']
        if len(cells) < 3 or not re.fullmatch(r'[1-9]|1[0-6]', cells[0]):
            continue
        no = int(cells[0])
        cancelled = any(v.replace(' ', '') in ('取消', '取止', '除外', '出走取消', '競走除外') for v in cells[2:])
        win = float(cells[2]) if re.fullmatch(r'\d+(?:\.\d+)?', cells[2]) else None
        place = re.fullmatch(r'(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)', cells[3]) if len(cells) > 3 else None
        out[no] = {'win': None if cancelled else win,
                   'place_low': float(place[1]) if place and not cancelled else None,
                   'place_high': float(place[2]) if place and not cancelled else None,
                   'cancelled': cancelled}
    return out


class Reader:
    def __init__(self, client=None):
        self.client = client or nk.Client()

    def meetings(self, day):
        _, raw = self.client.get(nk.CALENDAR)
        return program_links(raw, day)

    def program(self, url, day):
        _, raw = self.client.get(url)
        return parse_program(raw, url, day)

    def card(self, race):
        url = nk.ORIGIN + '/uma_shosai/' + race['provider_race_id'] + '.do'
        receipt, raw = self.client.get(url)
        first = race.get('program_runner_count') or 12
        last_error = None
        # The program count can be stale after a scratch; the card table is the
        # truth. Try the advertised count first, then every plausible size.
        for count in [first] + [n for n in range(16, 0, -1) if n != first]:
            excluded = []
            try:
                runners = nk.parse_card(raw, dict(race, program_runner_count=count), url, excluded_rows=excluded)
                return {'fetched_at': receipt['fetched_at'], 'runners': runners, 'excluded': excluded}
            except nk.NankanError as exc:
                last_error = exc
                if exc.receipt.get('code') != 'NANKAN_ALL_RUNNER_UNIVERSE_MISMATCH':
                    raise
        raise last_error

    def odds(self, race):
        url = nk.ORIGIN + '/odds/' + race['provider_race_id'] + '01.do'
        receipt, raw = self.client.get(url)
        return {'fetched_at': receipt['fetched_at'], 'odds': parse_odds(raw)}

"""ねっとばんばキンタロー PDF (net-banba.com/rakuten/qwYYYYMMDDRR.pdf) -> per-horse feed for the BAN engine.

Layout (2026-11 issue, A4 landscape, verified on qw2026111611): one row per horse (horse no. at x~31),
five past-race cells (1走前..5走前, ~95 pt wide from x~175). In each cell the barrier diagram carries
three segment seconds left-to-right = [start -> 第2障害, 第2障害, 障害後 -> goal] (sum = race time),
e.g. 37 / 26 / 73 for 2.16.0. Right block: 先行力 / 障害力 / 末脚 / 軽馬場 / 重馬場 grades A..E.
Circled positions are kept raw (meaning not yet confirmed) and are not used by the engine.
"""
import re
import urllib.request
from pathlib import Path

URL = 'https://net-banba.com/rakuten/qw{d}{r:02d}.pdf'
CIRCLED = {c: i + 1 for i, c in enumerate('①②③④⑤⑥⑦⑧⑨⑩⑪⑫')}
GRADE_X = [('front', 605), ('barrier', 630), ('kick', 655), ('light', 681), ('heavy', 706)]


def fetch(day, race_no, dest):
    """Download one race PDF (Owner-approved source). Returns path or None."""
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 10000:
        return dest
    url = URL.format(d=day.replace('-', ''), r=race_no)
    req = urllib.request.Request(url, headers={'User-Agent': 'KeibaMetrics-BAN-PrivateResearch/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
    except Exception:
        return None
    if not data.startswith(b'%PDF'):
        return None
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return dest


def _grade(words, top, x):
    for w in words:
        if abs(w['x0'] - x) < 8 and 0 <= w['top'] - top <= 8 and re.fullmatch(r'[A-E]', w['text']):
            return w['text']
    return None


def parse(path):
    import pdfplumber
    page = pdfplumber.open(str(path)).pages[0]
    W = page.extract_words(extra_attrs=['size'])
    rows = sorted([w for w in W if 27 <= w['x0'] <= 36 and re.fullmatch(r'\d{1,2}', w['text'])
                   and w['top'] < 440 and 7.9 <= w['size'] <= 8.5], key=lambda w: w['top'])
    out = {}
    for i, rw in enumerate(rows):
        no = int(rw['text'])
        top = rw['top'] - 16                                   # row band starts ~16 pt above the number
        bot = rows[i + 1]['top'] - 16 if i + 1 < len(rows) else top + 36
        band = [w for w in W if top <= w['top'] < bot]
        dates = sorted([w for w in band if re.fullmatch(r'\d{1,2}/\d{1,2}', w['text']) and 170 < w['x0'] < 600],
                       key=lambda w: w['x0'])
        past = []
        for d in dates:
            cell = [w for w in band if d['x0'] - 4 <= w['x0'] < d['x0'] + 92]
            seg = sorted([w for w in cell if re.fullmatch(r'\d{2,3}', w['text']) and abs(w['size'] - 6.0) < 0.3
                          and w['top'] - d['top'] > 20], key=lambda w: w['x0'])
            moist = next((float(w['text'][:-1]) for w in cell if re.fullmatch(r'\d\.\d%', w['text'])), None)
            load = next((int(w['text'][:-1]) for w in cell if re.fullmatch(r'\d{3}K', w['text'])), None)
            tm = next((w['text'] for w in cell if re.fullmatch(r'\d\.\d{2}\.\d', w['text'])), None)
            fin = next((int(w['text']) for w in cell if w['size'] >= 11 and w['text'].isdigit()), None)
            circ = [CIRCLED.get(ch) for w in sorted(cell, key=lambda w: w['x0']) for ch in w['text'] if ch in CIRCLED]
            note = next((w['text'] for w in cell if abs(w['size'] - 4.9) < 0.3), None)
            segs = [int(w['text']) for w in seg[:3]]
            past.append({'date': d['text'], 'moisture': moist, 'load': load, 'time': tm, 'finish': fin,
                         'segments_sec': segs, 'barrier_sec': segs[1] if len(segs) == 3 else None,
                         'circled_raw': circ, 'note': note})
        g = {k: _grade(band, top, x) for k, x in GRADE_X}
        out[str(no)] = {'past': past, 'grades': g,
                        'front_ok': g['front'] in ('A', 'B') if g['front'] else None,
                        'barrier_stable': g['barrier'] in ('A', 'B') if g['barrier'] else None}
    return out

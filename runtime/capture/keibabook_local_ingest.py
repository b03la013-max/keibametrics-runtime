"""Ingest one Keibabook LOCAL collection (km_local_kb_<date8>_<HHMM>.json.gz).

    python -m runtime.capture.keibabook_local_ingest FILE.json.gz --sha256 <page hash> \
        --private <keibametrics-private-evidence checkout> [--data <local-autopilot-data checkout>]

* verifies the SHA-256 the page reported for the uncompressed JSON;
* PRIVATE repo: local/<YYYY-MM-DD>/keibabook_pages_<HHMM>.json.gz (all collected pages,
  never published);
* PUBLIC data branch (optional, pre-race captures only): output/<YYYY-MM-DD>/external/
  keibabook_bands.json = bands only (no Keibabook text, times or numbers).
Prints a one-line JSON summary. Git commits are left to the caller.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import shutil
import sys
from collections import Counter
from pathlib import Path


MARK_POINTS = {'◎': 5, '○': 3, '〇': 3, '▲': 2, '△': 1, '☆': 1, '注': 1}
PACE_GROUPS = ('逃げ', '好位', '中位', '後方')


def _circled(s):
    return [ord(c) - 0x2460 + 1 for c in s if 0x2460 <= ord(c) <= 0x2473]


def _zidx(vals):
    """In-race deviation index 52 + 8 z (clamped 28-76); None when < 3 values or no spread."""
    xs = [v for v in vals.values() if v is not None]
    if len(xs) < 3:
        return {}
    mu = sum(xs) / len(xs)
    sd = (sum((x - mu) ** 2 for x in xs) / len(xs)) ** 0.5
    if sd == 0:
        return {}
    return {k: round(max(28.0, min(76.0, 52 + 8 * (v - mu) / sd)), 1) for k, v in vals.items() if v is not None}


def derive(race):
    """Derived per-horse signals from one race's collected pages (no Keibabook text):
    tm   = trackman-mark consensus index (出馬表 TM columns, ◎5 ○3 ▲2 △☆注1),
    pace = 展開予想 group (逃げ/好位/中位/後方, 出馬表 展開 table),
    rt / cpu = in-race deviation index of 能力表 RT / CPU when published."""
    out = {}
    sy = (race['pages'].get('出馬表') or {}).get('tables') or []
    main_t = next((t for t in sy if 'syutuba' in t['cls']), None)
    if main_t and main_t['rows']:
        head = main_t['rows'][0]
        try:
            a, b = head.index('My印') + 1, next(i for i, h in enumerate(head) if h.startswith('馬名'))
        except (ValueError, StopIteration):
            a = b = 0
        if b > a:
            score = {}
            for row in main_t['rows'][1:]:
                if row and row[0].isdigit():
                    score[int(row[0])] = sum(MARK_POINTS.get(c.strip()[:1], 0) for c in row[a:b])
            for no, v in _zidx(score).items():
                out.setdefault(no, {})['tm'] = v
    for t in sy:
        if t['cls'] == '' and t['rows'] and t['rows'][0] and t['rows'][0][0] in PACE_GROUPS:
            cells = [c for row in t['rows'] for c in row]
            for lab, nums in zip(cells[0::2], cells[1::2]):
                if lab in PACE_GROUPS:
                    for no in _circled(nums):
                        out.setdefault(no, {})['pace'] = lab
    no_t = next((t for t in (race['pages'].get('能力表HTML') or {}).get('tables') or []
                 if 'nouryoku' in t['cls']), None)
    if no_t:
        rt, cpu = {}, {}
        for row in no_t['rows']:
            if len(row) > 2 and row[1].isdigit():
                nums = [float(x) for x in row[2].split() if x.replace('.', '', 1).isdigit()]
                if len(nums) >= 2:
                    rt[int(row[1])], cpu[int(row[1])] = nums[0], nums[1]
        for key, vals in (('rt', rt), ('cpu', cpu)):
            for no, v in _zidx(vals).items():
                out.setdefault(no, {})[key] = v
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('--sha256', required=True)
    ap.add_argument('--private', required=True)
    ap.add_argument('--data')
    a = ap.parse_args(argv)
    src = Path(a.file)
    raw = gzip.decompress(src.read_bytes())
    sha = hashlib.sha256(raw).hexdigest()
    if sha != a.sha256:
        print(json.dumps({'error': 'SHA_MISMATCH', 'expected': a.sha256, 'got': sha}))
        return 2
    doc = json.loads(raw)
    d8 = doc['date']
    day = f'{d8[:4]}-{d8[4:6]}-{d8[6:]}'
    stamp = src.name.rsplit('_', 1)[-1].split('.')[0]
    priv = Path(a.private) / 'local' / day / f'keibabook_pages_{stamp}.json.gz'
    priv.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, priv)
    kinds = Counter(k for r in doc['races'] for k, p in r['pages'].items() if not p.get('unavailable'))
    out = {'date': day, 'races': len(doc['races']), 'pages': sum(kinds.values()), 'kinds': dict(kinds),
           'private_file': str(priv.relative_to(a.private)), 'sha256': sha}
    bands = doc.get('bands') or {}
    if a.data:
        pub = Path(a.data) / 'output' / day / 'external' / 'keibabook_bands.json'
        pub.parent.mkdir(parents=True, exist_ok=True)
        cb = {(r['venue'], r['race_no']): r['horses'] for r in bands.get('races') or []}
        races = []
        for r in doc['races']:   # bands / derived indices only, never Keibabook text or numbers
            horses = {str(no): {k: v for k, v in h.items() if k in ('cci', 'tri')}
                      for no, h in (cb.get((r['venue'], r['race_no'])) or {}).items()}
            for no, d in derive(r).items():
                horses.setdefault(str(no), {}).update(d)
            races.append({'kb_id': r['kb_id'], 'venue': r['venue'], 'race_no': r['race_no'], 'horses': horses})
        keep = {'date': d8, 'source': doc['source'], 'captured_at': doc['collected_at'],
                'rules': (bands.get('rules') or []) + ['KM-LOCAL-TM-CONSENSUS-v1', 'KM-LOCAL-PACE-GROUP-v1',
                                                        'KM-LOCAL-RT-CPU-DEV-v1'],
                'not_provided': bands.get('not_provided') or [], 'races': races}
        pub.write_text(json.dumps(keep, ensure_ascii=False))
        out['public_bands'] = str(pub.relative_to(a.data))
        out['band_races'] = len(races)
        out['signals'] = dict(Counter(k for r in races for h in r['horses'].values() for k in h))
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())

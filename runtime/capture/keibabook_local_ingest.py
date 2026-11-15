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
    bands = doc.get('bands')
    if a.data and bands and bands.get('races'):
        pub = Path(a.data) / 'output' / day / 'external' / 'keibabook_bands.json'
        pub.parent.mkdir(parents=True, exist_ok=True)
        keep = {k: bands[k] for k in ('date', 'source', 'rules', 'captured_at', 'not_provided', 'races')}
        for r in keep['races']:   # bands only
            r['horses'] = {no: {k: v for k, v in h.items() if k in ('cci', 'tri')} for no, h in r['horses'].items()}
        pub.write_text(json.dumps(keep, ensure_ascii=False))
        out['public_bands'] = str(pub.relative_to(a.data))
        out['band_races'] = len(keep['races'])
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())

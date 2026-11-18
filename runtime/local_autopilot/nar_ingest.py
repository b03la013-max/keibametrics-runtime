"""Ingest NAR official monthly race ZIPs downloaded BY THE OWNER (Owner 2026-11-19 02:02: no automated retrieval).

python -m runtime.local_autopilot.nar_ingest <out_root> <YYYYMM_..._race.zip> [...]
Extracts racelist / horselist / payback CSVs to <out_root>/hist/nar/<YYYYMM>/, records sha256 + source file name
in manifest.json, then rebuilds hist_stats.json / hist_stats.md. Class: HISTORICAL_BACKFILL_LEARNING.
"""
import hashlib
import json
import re
import sys
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from runtime.local_autopilot import hist_stats


def ingest(out_root, zips):
    out_root = Path(out_root)
    done = []
    for z in zips:
        z = Path(z)
        m = re.match(r'(\d{6})(?:\d{2})?_', z.name)
        if not m:
            raise ValueError(f'not a NAR race zip name: {z.name}')
        ym = m[1]
        dest = out_root / 'hist' / 'nar' / ym
        dest.mkdir(parents=True, exist_ok=True)
        files = {}
        with zipfile.ZipFile(z) as zf:
            for info in zf.infolist():
                base = Path(info.filename).name
                if not re.search(r'_(racelist|horselist|payback)\.csv$', base):
                    continue
                data = zf.read(info)
                (dest / base).write_bytes(data)
                files[base] = hashlib.sha256(data).hexdigest()
        if not files:
            raise ValueError(f'no race CSVs in {z.name}')
        man = {'source': 'NAR official data download (manual, by the Owner)', 'zip': z.name,
               'zip_sha256': hashlib.sha256(z.read_bytes()).hexdigest(), 'files': files,
               'ingested_at': datetime.now(timezone(timedelta(hours=9))).isoformat(), 'class': hist_stats.CLASS}
        (dest / 'manifest.json').write_text(json.dumps(man, ensure_ascii=False, indent=1) + '\n')
        done.append(ym)
    st = hist_stats.write(out_root)
    return done, st


if __name__ == '__main__':
    done, st = ingest(sys.argv[1], sys.argv[2:])
    print('NAR_INGEST', done, (st or {}).get('races'), 'races', (st or {}).get('starts'), 'starts', (st or {}).get('source'))

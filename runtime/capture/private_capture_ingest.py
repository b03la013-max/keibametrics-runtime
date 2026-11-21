"""Decode a browser-side gzip+base64 capture and store it in the PRIVATE evidence repo only.

Usage: python -m runtime.capture.private_capture_ingest <b64-file-or-json> --sha256 <hex> \
         --dest /home/claude/keibametrics-private-evidence/jra/<date>/<kind>/<HHMM>.json.gz
The b64 input may be the raw string or a tool-result JSON containing it. Verifies the SHA-256 of
the decompressed JSON before writing. Never writes to the public repository."""
import argparse, base64, gzip, hashlib, json, re, sys
from pathlib import Path

ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('--sha256', required=True)
ap.add_argument('--dest', required=True); a = ap.parse_args()
raw = Path(a.src).read_text(encoding='utf-8', errors='ignore')
m = max(re.findall(r'[A-Za-z0-9+/=]{200,}', raw), key=len)
gz = base64.b64decode(m); body = gzip.decompress(gz)
h = hashlib.sha256(body).hexdigest()
if h != a.sha256: sys.exit(f'SHA_MISMATCH {h}')
if 'keibametrics-private-evidence' not in a.dest: sys.exit('DEST_NOT_PRIVATE')
d = Path(a.dest); d.parent.mkdir(parents=True, exist_ok=True); d.write_bytes(gz)
print(json.dumps({'written': str(d), 'bytes': len(body), 'gz': len(gz), 'sha256': h}))

"""Verify every member before restoring immutable result-only observations."""
import json,hashlib,tarfile,io
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'evidence/kaw_v25_20261013'
m=json.loads((base/'official_receipts_manifest.json').read_text());raw=(base/'official_receipts.tar.gz').read_bytes()
if hashlib.sha256(raw).hexdigest()!=m['archive_sha256']:raise ValueError('ARCHIVE_DIGEST')
staged={}
with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as t:
 for x in t:
  if not x.isfile() or x.name not in m['files'] or x.name in staged or Path(x.name).name!=x.name:raise ValueError('MEMBER_SCOPE')
  b=t.extractfile(x).read()
  if hashlib.sha256(b).hexdigest()!=m['files'][x.name]:raise ValueError('MEMBER_DIGEST')
  p=base/x.name
  if p.exists() and p.read_bytes()!=b:raise ValueError('IMMUTABLE_CONFLICT')
  staged[x.name]=b
if set(staged)!=set(m['files']):raise ValueError('MEMBER_INCOMPLETE')
for n,b in staged.items():(base/n).write_bytes(b)
print(json.dumps({'status':'HASH_VERIFIED','files':len(staged),'network_calls':0}))

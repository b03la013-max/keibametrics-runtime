from pathlib import Path
import json,hashlib,base64,copy,sys,tarfile,collections,subprocess
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
root=Path.cwd(); canon=lambda v:json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
meta=json.loads((root/'evidence/jra_day_review_20261017/legacy_krs_input_hash_closure.json').read_text())
key=Ed25519PublicKey.from_public_bytes(base64.b64decode('UhjfD9zFt+e77/9JUB19R6/XFC3SG4pM5twHBqfUSzI='));rows=[]
for r in meta['rows']:
 req=json.loads((root/r['input_ref']).read_text());res=json.loads((root/r['krs_ref']).read_text());env=res['run_receipt'];rec=env['receipt']
 raw=canon(rec);key.verify(base64.b64decode(env['signature'],validate=True),raw)
 assert hashlib.sha256(raw).hexdigest()==env['receipt_sha256']
 inp=copy.deepcopy(req['krs_input_data']);inp['simulation']['run_count']=req.get('run_count',5000);inp['simulation']['master_seed']=req['seed'];inp['race']['prediction_id']=req['race_id']
 assert inp['race']['race_id']==req['race_id']==rec['race_id']
 assert hashlib.sha256(canon(inp)).hexdigest()==rec['input_sha256']
 assert hashlib.sha256(res['output_canonical_json'].encode()).hexdigest()==rec['output_sha256']
 assert canon(json.loads(res['output_canonical_json']))==canon(res['output'])
 rows.append({'race_id':r['race_id'],'signature':'PASS','input':'MATCH','output':'MATCH'})
m=json.loads((root/'evidence/jra_day_review_20261017/payload_manifest.json').read_text());bundle=root/'evidence/jra_day_review_20261017/payload.tar.gz';assert hashlib.sha256(bundle.read_bytes()).hexdigest()==m['archive_sha256']
with tarfile.open(bundle) as t:
 members=t.getmembers();expected={v['path']:v for v in m['files']};assert len(members)==len(expected)
 for member in members:
  assert member.isfile() and not member.name.startswith('/') and '..' not in Path(member.name).parts
  b=t.extractfile(member).read();assert hashlib.sha256(b).hexdigest()==expected[member.name]['sha256'];assert len(b)==expected[member.name]['size']
changed=subprocess.check_output(['git','diff','--name-only','d7ae23a','dc6333f'],text=True).splitlines()
classes=collections.defaultdict(list)
for p in changed:
 group='workflow' if p.startswith('.github/') else 'test' if p.startswith('tests/') else 'audit_script' if p.startswith('scripts/') else 'evidence' if p.startswith('evidence/') else 'learning_review' if '/learning_states/' in p else 'generated_review' if '/daily_reviews/' in p else 'status_reconciliation' if '/jra_race_day_' in p else 'runtime_code'
 classes[group].append(p)
print(json.dumps({'independent_original_receipts':len(rows),'archive_members':len(members),'archive_sha':m['archive_sha256'],'changed_files':len(changed),'class_counts':{k:len(v) for k,v in classes.items()}},indent=2))
Path('/tmp/km-independent-crypto.json').write_text(json.dumps({'receipts':rows,'archive_members':len(members),'archive_sha':m['archive_sha256'],'file_classification':classes},indent=2))

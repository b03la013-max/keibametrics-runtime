"""Read-only reuse of pinned PR262 selector; historical diagnostic only."""
import json,sys,tarfile,hashlib,importlib.util,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'runtime'))
from local_fullnumerical_production import materialize_production
b=ROOT/'evidence/kaw_v25_20261013';dep=json.loads((b/'pr262_dependency.json').read_text());a=b/'pr262_selector_snapshot.tar.gz'
if hashlib.sha256(a.read_bytes()).hexdigest()!=dep['archive_sha256']:raise ValueError('DEPENDENCY_ARCHIVE_HASH')
with tempfile.TemporaryDirectory() as temp:
 with tarfile.open(a,'r:gz') as t:
  for member in t:
   if member.name not in dep['file_hashes'] or not member.isfile():raise ValueError('DEPENDENCY_MEMBER')
   raw=t.extractfile(member).read()
   if hashlib.sha256(raw).hexdigest()!=dep['file_hashes'][member.name]:raise ValueError('DEPENDENCY_HASH')
   (Path(temp)/member.name).write_bytes(raw)
 spec=importlib.util.spec_from_file_location('pr262',Path(temp)/'local_aki_columns.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.POLICY=ROOT/'profiles/local_aki_columns_20261012_R1.json';policy=json.loads((Path(temp)/'policy.json').read_text());rows=[]
 for day in ['20261012','20261013']:
  for p in (ROOT/'runtime/executions').glob(f'KM-LOCAL-KAW-{day}-*/FORMAL/runs/*/final_receipt_envelope.json'):
   rid=json.loads(p.read_text())['receipt']['race_id'];intent=json.loads((ROOT/'runtime/formal_intents'/f'{rid}.json').read_text());source=json.loads((p.parent/'source_receipt_envelope.json').read_text())['artifact'];intent['source_snapshot_sha256']=source['source_snapshot_sha256'];q=materialize_production(source,intent,intent['required_indices']);s=m.build(q,source,policy=policy);d=m.decision(q,s)
   rows.append({'race_id':rid,'status':s['status'],'columns':s['columns'],'ticket_count':len(d['paper_tickets']),'terminal_reasons':s['terminal_reasons'],'scope':'POST_EVENT_REGRESSION / NO_NEW_FORWARD_OOS','policy_sha256':s['policy_sha256'],'source_snapshot_sha256':source['source_snapshot_sha256']})
 report={'upstream_head':dep['commit'],'upstream_file_sha256':dep['file_hashes']['local_aki_columns.py'],'rows':rows}
 (ROOT/'research/kaw_v25_20261013/pr262_comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('READ_ONLY_REPLAY',len(rows))

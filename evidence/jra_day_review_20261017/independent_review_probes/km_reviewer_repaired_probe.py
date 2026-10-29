import sys,os,tempfile,json,multiprocessing,hashlib,subprocess,time
from pathlib import Path
sys.path.insert(0,'runtime')
import jra_krs_request_checkpoint as m
from jra_krs_legacy_input_binding import check_input_binding,KRSInputBindingError,REVISION,SCHEMA
P=lambda n:{'race_id':'KM-JRA-TKY-20261018-R01','input_data':{'marker':n}}
def worker(d,n,start,q):
 start.wait()
 try:q.put(('ok',n,m.checkpoint_krs_request(P(n),d)[0].decode()))
 except Exception as e:q.put(('fail',n,type(e).__name__))
ctx=multiprocessing.get_context('fork');runs=[]
for same in (False,True):
 for i in range(12):
  d=tempfile.mkdtemp();start=ctx.Event();q=ctx.Queue();ps=[ctx.Process(target=worker,args=(d,n,start,q)) for n in ([1,1] if same else [1,2])]
  for p in ps:p.start()
  start.set();got=[q.get(timeout=10) for p in ps]
  for p in ps:p.join();assert p.exitcode==0
  oks=[v for v in got if v[0]=='ok'];assert len(oks)==(2 if same else 1)
  disk=(Path(d)/'krs_request_wire.json').read_text();assert all(v[2]==disk for v in oks)
  rec=json.loads((Path(d)/'krs_request_hashes.json').read_text());assert hashlib.sha256(disk.encode()).hexdigest()==rec['wire_sha256'];runs.append(got)
# Real abrupt process death after first atomic publication, not raised exception.
d=tempfile.mkdtemp()
code='''import os,sys
sys.path.insert(0,"runtime")
import jra_krs_request_checkpoint as m
original=m._publish
def die(path,raw):
 original(path,raw)
 if path.name=="krs_request_wire.json":os._exit(77)
m._publish=die
m.checkpoint_krs_request({"race_id":"KM-JRA-TKY-20261018-R01","input_data":{"marker":1}},sys.argv[1])
'''
p=subprocess.run([sys.executable,'-c',code,d]);assert p.returncode==77
try:m.checkpoint_krs_request(P(2),d);raise AssertionError('different payload accepted')
except m.JRAProductionKRSContractError:pass
body,rec=m.checkpoint_krs_request(P(1),d);assert json.loads(body)==P(1)
# Known declaration does not permit unsupported runtime or schema.
p={'race_id':'X','input_data':{'race':{'race_id':'X'}}};sha=hashlib.sha256(json.dumps(p['input_data'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
for rev,sch in [('UNKNOWN',SCHEMA),(REVISION,'UNKNOWN')]:
 r={'run_receipt':{'receipt':{'race_id':'X','runtime_revision':rev,'schema':sch,'input_hash_contract':'KM-KRS-INPUT-DATA-SORTED-UTF8-v1','input_sha256':sha}}}
 try:check_input_binding(p,r);raise AssertionError('unsupported accepted')
 except KRSInputBindingError:pass
print(json.dumps({'process_race_schedules':len(runs),'different_payload_race_schedules':12,'same_payload_race_schedules':12,'sigkill_style_exit_between_publications':'recovered exact payload only','unknown_runtime_schema_declared_branch':'rejected'}))
Path('/tmp/km-reviewer-repaired-probe.json').write_text(json.dumps({'schedules':runs,'abrupt_process_exit':77,'exact_recovery':True,'unknown_declared_rejected':True},indent=2))

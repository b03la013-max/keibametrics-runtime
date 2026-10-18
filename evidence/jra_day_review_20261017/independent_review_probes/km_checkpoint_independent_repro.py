import sys,tempfile,threading,json,hashlib
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,'runtime')
from jra_production_krs_contract import checkpoint_krs_request
root=Path(tempfile.mkdtemp()); barriers={n:threading.Barrier(2) for n in ('krs_request_wire.json','krs_request_hashes.json')}; counts={}; guard=threading.Lock(); orig=Path.exists
# Force real possible schedule: each writer sees each destination absent before writing.
def exists(p):
 if p.parent==root and p.name in barriers:
  key=(threading.get_ident(),p.name)
  with guard:counts[key]=counts.get(key,0)+1;c=counts[key]
  if c==2:
   barriers[p.name].wait(timeout=5)
   return False
  if c==1:return False
 return orig(p)
results=[]
def worker(i):
 try:results.append((i,checkpoint_krs_request({'race_id':'KM-JRA-TKY-20261018-R01','input_data':{'marker':i}},root)))
 except Exception as e:results.append((i,type(e).__name__,str(e)))
with patch.object(Path,'exists',exists):
 ts=[threading.Thread(target=worker,args=(i,)) for i in (1,2)]
 for t in ts:t.start()
 for t in ts:t.join()
print('both_success',len([r for r in results if len(r)==2]))
print('returned_bodies_differ',results[0][1][0]!=results[1][1][0])
print('disk_wire_sha',hashlib.sha256((root/'krs_request_wire.json').read_bytes()).hexdigest())
print('disk_record_sha',json.loads((root/'krs_request_hashes.json').read_text())['wire_sha256'])

import json,os,sys,re
sys.path.insert(0,"runtime")
from execution_gateway import load_gateway, normalize_request, execution_phase, artifact_name, derive_execution_id
req=json.load(open(os.environ["REQUEST_FILE"],encoding="utf-8"))
fam=str(req.get("family_id") or "").upper()
if fam=="LOCAL":
    gateway=load_gateway()
    normalized,ctx=normalize_request(req,gateway)
    execution_id=ctx["execution_id"]
    phase=ctx["phase"]
    art=artifact_name(execution_id,phase,gateway,"LOCAL")
else:
    execution_id=derive_execution_id(req)
    phase=execution_phase(req)
    art=re.sub(r"[^A-Za-z0-9._-]+","-",f"km-ban-execution-{execution_id}-{phase}")
with open(os.environ["GITHUB_OUTPUT"],"a",encoding="utf-8") as out:
    out.write(f"request_file={os.environ['REQUEST_FILE']}\n")
    out.write(f"execution_id={execution_id}\n")
    out.write(f"phase={phase}\n")
    out.write(f"artifact_name={art}\n")
print(json.dumps({"request_file":os.environ["REQUEST_FILE"],"execution_id":execution_id,"phase":phase,"artifact_name":art},ensure_ascii=False))

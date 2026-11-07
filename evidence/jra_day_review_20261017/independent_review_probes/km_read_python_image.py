import urllib.request,urllib.parse,json,hashlib,datetime
from pathlib import Path
base='https://registry-1.docker.io/v2/library/python/'
token=json.load(urllib.request.urlopen('https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/python:pull',timeout=15))['token']
def get(path,manifest=False):
 h={'Authorization':'Bearer '+token}
 if manifest:h['Accept']='application/vnd.oci.image.index.v1+json,application/vnd.oci.image.manifest.v1+json,application/vnd.docker.distribution.manifest.list.v2+json,application/vnd.docker.distribution.manifest.v2+json'
 with urllib.request.urlopen(urllib.request.Request(base+path,headers=h),timeout=15) as r: raw=r.read(2000000);return json.loads(raw),r.headers.get('Docker-Content-Digest'),hashlib.sha256(raw).hexdigest()
idx,digest,index_sha=get('manifests/3.13-slim',True)
assert digest == 'sha256:'+index_sha
selected=next(x for x in idx['manifests'] if x.get('platform',{}).get('os')=='linux' and x.get('platform',{}).get('architecture')=='amd64')
m,md,manifest_sha=get('manifests/'+selected['digest'],True)
assert md == selected['digest'] == 'sha256:'+manifest_sha
cfg,_,sha=get('blobs/'+m['config']['digest'])
assert m['config']['digest'] == 'sha256:'+sha
o={'observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'classification':'CURRENT PUBLIC TAG REFERENCE ONLY; NOT DEPLOYED IMAGE PROVENANCE','reference':'docker.io/library/python:3.13-slim','current_index_digest':digest,'index_digest_recomputed':'sha256:'+index_sha,'selected_reference_platform':selected['platform'],'selected_reference_digest':selected['digest'],'manifest_digest_header':md,'manifest_digest_recomputed':'sha256:'+manifest_sha,'config_digest_declared':m['config']['digest'],'config_digest_recomputed':'sha256:'+sha,'created':cfg.get('created'),'config':{k:cfg.get('config',{}).get(k) for k in ['Entrypoint','Cmd','WorkingDir']},'deployed_digest_verified':False,'layers_downloaded':0,'image_executed':False}
Path('/tmp/km-current-python-image-reference.json').write_text(json.dumps(o,indent=2)+'\n');print(json.dumps(o,indent=2))

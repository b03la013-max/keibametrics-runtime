"""Exact recovered Runtime source rehearsal, localhost only, TEST signer only.

No Railway calls, Production environment/keys, pip install, policy edits, race
FINAL, purchase or notification. Local rollback restores our own original files
and proves no provider rollback. Original launcher decoder is exercised; its
unversioned network pip step and public binding are intentionally not executed.
"""
import base64,copy,gzip,hashlib,json,os,shlex,shutil,socket,subprocess,sys,tempfile,time,urllib.request
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

APP=Path('/tmp/km-recovered-app.py');ENGINE=Path('/tmp/km-recovered-engine.py');PARAM=Path('/tmp/km-recovered-param.json');PYTHON='/tmp/km-runtime-startup-venv/bin/python';ROOT=Path('/opt/km');REPO=Path('/workspace/scratch/ab7e656e13a3/km-day-review')
EXPECTED={'app.py':'1c453a5b0e8b5e4689b4a73d18128f54c7ed0e205db5b0c58b3dd229c264a989','KRS-Engine_v1.1.0_PORTABLE.py':'9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421','parameter_map_v0.1-provisional.json':'75cc9d0e8b15de0e95bbfd76d9ed4425fa6b9076d022d1a9c6b5bc812fa3dedc'}
CANON=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
SHA=lambda b:hashlib.sha256(b).hexdigest()


def main():
    if ROOT.exists():raise RuntimeError('LOCAL_PATH_ALREADY_EXISTS_REFUSE_OVERWRITE')
    blobs={n:p.read_bytes() for n,p in zip(EXPECTED,[APP,ENGINE,PARAM])}
    for n,b in blobs.items():assert SHA(b)==EXPECTED[n],n
    key=Ed25519PrivateKey.generate();rawkey=key.private_bytes(serialization.Encoding.Raw,serialization.PrivateFormat.Raw,serialization.NoEncryption());pub=key.public_key();pub64=base64.b64encode(pub.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)).decode()
    env={'PATH':str(Path(PYTHON).parent)+os.pathsep+os.defpath,'PYTHONDONTWRITEBYTECODE':'1','PYTHONUNBUFFERED':'1','NO_PROXY':'127.0.0.1,localhost','KM_RECEIPT_PRIVATE_KEY_B64':base64.b64encode(rawkey).decode(),'KM_RECEIPT_SIGNER_KEY_ID':'KM-LOCAL-TEST-ONLY-NO-PRODUCTION','KM_ENGINE_SHA256':EXPECTED['KRS-Engine_v1.1.0_PORTABLE.py'],'KM_PARAM_SHA256':EXPECTED['parameter_map_v0.1-provisional.json'],'KM_MCPFINE_SHA256':EXPECTED['app.py'],'KM_PUBLIC_HOST':'127.0.0.1'}
    for n,prefix,count in [('app.py','KM_MCPFINE_',7),('KRS-Engine_v1.1.0_PORTABLE.py','KM_ENGINE_GZ_B64_',6)]:
        b64=base64.b64encode(gzip.compress(blobs[n],mtime=0)).decode();size=(len(b64)+count-1)//count
        for i in range(count):env[prefix+str(i)]=b64[i*size:(i+1)*size]
    env['KM_PARAM_GZ_B64']=base64.b64encode(gzip.compress(blobs['parameter_map_v0.1-provisional.json'],mtime=0)).decode()
    launcher=Path('/tmp/km-recovered-start-command.txt').read_text();outer=shlex.split(launcher);assert outer[:2]==['sh','-c'];tokens=shlex.split(outer[2]);pidx=tokens.index('python');assert tokens[pidx+1]=='-c';decoder=tokens[pidx+2]
    # No key read by decoder: inspect restricted code before execution.
    assert 'KM_RECEIPT' not in decoder and 'pip' not in decoder
    ROOT.mkdir();proc=None;logfile=None;base=None;logfd,logname=tempfile.mkstemp(prefix='km-local-runtime-log-',suffix='.txt');os.close(logfd);logpath=Path(logname);events=[]
    try:
        decoded=subprocess.run([PYTHON,'-c',decoder],env=env,capture_output=True,text=True,timeout=15,check=True)
        for n,h in EXPECTED.items():assert SHA((ROOT/n).read_bytes())==h
        events.append({'stage':'RECOVERED_EXACT_DECODER','status':'PASS','code_sha256':SHA(decoder.encode()),'stdout':decoded.stdout.strip(),'production_environment_blob_values_used':False})
        def call(path,payload=None):
            data=None if payload is None else CANON(payload);request=urllib.request.Request(base+path,data=data,headers={'Content-Type':'application/json'},method='GET' if payload is None else 'POST')
            with urllib.request.urlopen(request,timeout=200) as response:return json.load(response)
        def start(label,expected_status='READY'):
            nonlocal proc,logfile,base
            with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
            base='http://127.0.0.1:'+str(port);logfile=logpath.open('ab');proc=subprocess.Popen([PYTHON,'-m','uvicorn','app:app','--app-dir',str(ROOT),'--host','127.0.0.1','--port',str(port)],cwd=str(ROOT),env=env,stdout=logfile,stderr=subprocess.STDOUT)
            last=None
            for _ in range(200):
                if proc.poll() is not None:raise RuntimeError('LOCAL_RUNTIME_DIED:'+str(proc.returncode)+':'+logpath.read_text()[-1000:])
                try:
                    health=call('/health')
                    if health['status']==expected_status:break
                except Exception as e:last=type(e).__name__
                time.sleep(.1)
            else:raise RuntimeError('LOCAL_HEALTH_TIMEOUT:'+str(last))
            assert health['receipt_signer']['public_key_b64']==pub64
            events.append({'stage':label,'status':health['status'],'runtime_revision':health['runtime_revision'],'engine_sha256':health['engine']['sha256'],'parameter_map_sha256':health['parameter_map']['sha256'],'signer_key_id':health['receipt_signer']['key_id'],'local_process_pid':proc.pid,'listen_host':'127.0.0.1'})
            return health
        def stop():
            nonlocal proc,logfile
            if proc is not None:
                proc.terminate()
                try:proc.wait(timeout=10)
                except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
                events.append({'stage':'LOCAL_STOP','exitcode':proc.returncode});proc=None
            if logfile is not None:logfile.close();logfile=None
        ledger=json.loads((REPO/'evidence/jra_day_review_20261017/legacy_krs_input_hash_closure.json').read_text());req=json.loads((REPO/ledger['rows'][0]['input_ref']).read_text());inp=copy.deepcopy(req['krs_input_data']);rid='KM-JRA-LOCAL-STARTUP-REHEARSAL-NONPRODUCTION-20261017';inp['race']['race_id']=rid;inp['race'].pop('prediction_id',None)
        payload={'race_id':rid,'input_data':inp,'mode':'SMOKE','seed':172003,'input_class':'LOCAL-TEST-NONPRODUCTION'}
        def verify(result):
            envelope=result['run_receipt'];rec=envelope['receipt'];wire=CANON(rec);assert SHA(wire)==envelope['receipt_sha256'];pub.verify(base64.b64decode(envelope['signature'],validate=True),wire);assert envelope['signer_key_id']=='KM-LOCAL-TEST-ONLY-NO-PRODUCTION';return rec
        def smoke(label):
            result=call('/krs/execute',payload);rec=verify(result);assert rec['status']=='EXECUTED' and rec['actual_run_count']==rec['requested_run_count']==100
            normalized=copy.deepcopy(inp);normalized['race'].setdefault('prediction_id',rid);normalized.setdefault('simulation',{}).update(run_count=100,master_seed=172003);assert SHA(CANON(normalized))==rec['input_sha256'];assert SHA(result['output_canonical_json'].encode())==rec['output_sha256'];assert CANON(json.loads(result['output_canonical_json']))==CANON(result['output']);assert call('/verify',result['run_receipt'])['valid'] is True
            tamper=copy.deepcopy(result['run_receipt']);tamper['receipt']['race_id']='TAMPERED';assert call('/verify',tamper)['valid'] is False
            events.append({'stage':label,'status':'PASS','actual_run_count':rec['actual_run_count'],'input_sha256':rec['input_sha256'],'output_sha256':rec['output_sha256'],'receipt_sha256':result['run_receipt']['receipt_sha256'],'independent_ed25519':'PASS','tampered_receipt_rejected':True,'signer':'LOCAL TEST KEY ONLY'})
            return result
        start('LOCAL_COLD_START');first=smoke('LOCAL_SMOKE100_AFTER_COLD_START');stop();start('LOCAL_RESTART_SAME_TEST_KEY');assert call('/verify',first['run_receipt'])['valid'] is True;smoke('LOCAL_SMOKE100_AFTER_RESTART');stop()
        # Safe local negative control; no Production binary is changed.
        ep=ROOT/'KRS-Engine_v1.1.0_PORTABLE.py';ep.write_bytes(blobs[ep.name]+b'\n# LOCAL NEGATIVE CONTROL\n');start('LOCAL_BAD_ENGINE_HASH','DEGRADED');failed=call('/krs/execute',payload);badrec=verify(failed);assert badrec['status']=='EXECUTION-FAILED' and badrec['actual_run_count']==0;events.append({'stage':'LOCAL_BAD_ENGINE_FAIL_CLOSED','status':'PASS','actual_run_count':0});stop()
        for n,b in blobs.items():(ROOT/n).write_bytes(b)
        start('LOCAL_RESTORE_ORIGINAL_ARTIFACTS');assert call('/verify',first['run_receipt'])['valid'] is True;smoke('LOCAL_SMOKE100_AFTER_RESTORE');stop()
        versions=json.loads(subprocess.check_output([PYTHON,'-c','import json,sys,importlib.metadata as m; print(json.dumps({"python":sys.version,"dependencies":{p:m.version(p) for p in ["mcp","uvicorn","cryptography","starlette","pydantic"]}}))'],env=env,text=True))
        result={'versions':versions,'classification':'LOCAL RECOVERED-SOURCE REHEARSAL / NOT PROVIDER COLD START, RESTART, ROLLBACK OR LIVE ACCEPTANCE','source_sha256':EXPECTED,'launcher_sha256':SHA(launcher.encode()),'launcher_file_sha256':SHA(launcher.encode()),'launcher_command_sha256':SHA(launcher.strip().encode()),'launcher_sha_scope':'file bytes include newline; command hash strips surrounding whitespace','decoder':'EXACT RECOVERED; locally repackaged nonsecret original code/Engine/param','server_command':'LOCAL LOOPBACK OVERRIDE; not original public binding','dependency_install_step':'NOT RUN; exact installed dependency versions used','environment':'clean synthetic environment; TEST-only generated signer; no Production keys','public_test_key':pub64,'events':events,'real_engine_local_runs':300,'production_runtime_calls':0,'production_mutations':0,'provider_rollback':'NOT EXECUTED / NOT VERIFIED','production_cold_start_restart':'NOT EXECUTED / NOT VERIFIED','git_sha':'NOT ESTABLISHED','future_oos_credit':0,'full_prediction_final_delivery_learning_acceptance':False}
        Path('/tmp/km-independent-local-runtime-rehearsal.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    finally:
        if proc is not None:
            proc.terminate()
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
        if logfile is not None:logfile.close()
        shutil.rmtree(ROOT)
        # The local runtime logs contain only TEST-key receipts, never secret material.

if __name__=='__main__':main()

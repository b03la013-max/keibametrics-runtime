"""Byte-verified restart checkpoints, separate from immutable predictions."""
import argparse, hashlib, io, json, tarfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BASE = Path('evidence/local_aki_columns_20261012')
ARCHIVE = BASE/'forward_result_checkpoint.tar.gz'
MANIFEST = BASE/'forward_result_checkpoint_manifest.json'
NAMES = {'forward_evaluation.json','postresult_acceptance.json','replay_result_receipt.json',
         'replay_result_payload.json','replay_result_verification.json','paper_settlement.json',
         'paper_projection.json','paper_reflection.json','paper_learning.json',
         'official_result_source_receipt.json','original_official_result_receipt.json'}

def eligible(name):
    p=Path(name)
    return (not p.is_absolute() and '..' not in p.parts and
            name.startswith(str(BASE/'external')+'/KM-LOCAL-AKI-FORWARD-') and
            (p.name in NAMES or 'result_attempts' in p.parts) and p.suffix=='.json')

def pack(root=ROOT):
    root=Path(root); files={str(p.relative_to(root)):p.read_bytes()
        for p in (root/BASE/'external').glob('KM-LOCAL-AKI-FORWARD-*/*/**/*.json')
        if eligible(str(p.relative_to(root)))}
    # Fixed metadata makes unchanged checkpoints byte-identical.
    import gzip
    buffer=io.BytesIO()
    with tarfile.open(fileobj=buffer,mode='w') as archive:
        for name,raw in sorted(files.items()):
            info=tarfile.TarInfo(name);info.size=len(raw);info.mode=0o644
            archive.addfile(info,io.BytesIO(raw))
    (root/ARCHIVE).parent.mkdir(parents=True,exist_ok=True)
    (root/ARCHIVE).write_bytes(gzip.compress(buffer.getvalue(),mtime=0))
    m={'archive_sha256':hashlib.sha256((root/ARCHIVE).read_bytes()).hexdigest(),
       'files':{n:hashlib.sha256(r).hexdigest() for n,r in sorted(files.items())},
       'prediction_archive_changed':False,'additional_krs_runs':0,'purchase_authority':False}
    (root/MANIFEST).write_text(json.dumps(m,indent=2)+'\n');return {'files':len(files)}

def restore(root=ROOT):
    root=Path(root)
    if not (root/ARCHIVE).exists() and not (root/MANIFEST).exists():
        return {'status':'NO_RESULT_CHECKPOINT_YET','network_calls':0}
    m=json.loads((root/MANIFEST).read_text());raw=(root/ARCHIVE).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=m['archive_sha256']:raise ValueError('RESULT_CHECKPOINT_DIGEST_INVALID')
    staged={}
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as archive:
        for member in archive.getmembers():
            n=member.name
            if n in staged or n not in m['files'] or not eligible(n) or not member.isfile() or member.size>32*1024*1024:
                raise ValueError('RESULT_CHECKPOINT_MEMBER_INVALID')
            content=archive.extractfile(member).read()
            if hashlib.sha256(content).hexdigest()!=m['files'][n]:raise ValueError('RESULT_CHECKPOINT_FILE_DIGEST_INVALID')
            if (root/n).exists() and (root/n).read_bytes()!=content:raise ValueError('RESULT_CHECKPOINT_IMMUTABLE_CONFLICT')
            staged[n]=content
    if set(staged)!=set(m['files']):raise ValueError('RESULT_CHECKPOINT_INCOMPLETE')
    for n,content in staged.items():
        p=root/n;p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists():
            temp=p.with_suffix('.json.tmp');temp.write_bytes(content);temp.replace(p)
    return {'status':'RESULT_CHECKPOINT_HASH_VERIFIED','files':len(staged),'network_calls':0}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['pack','restore'])
    print(json.dumps(globals()[parser.parse_args().action]()))

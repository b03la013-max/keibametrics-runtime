"""Persist/restore the five signed forward cases with explicit byte hashes."""
import argparse,hashlib,json,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'evidence/local_aki_columns_20261012'
ARCHIVE=EVIDENCE/'forward_pilot_20261013_receipts.tar.gz'
MANIFEST=EVIDENCE/'forward_pilot_20261013_manifest.json'


def pack():
    pilot=json.loads((ROOT/'research/local_aki_forward_20261013/pilot_status.json').read_text())
    paths=set((ROOT/'research/local_aki_forward_20261013').rglob('*.json'));cases=[]
    paths.add(ROOT/'profiles/local_aki_prospective_evaluation_20261013_R2.json')
    for t in pilot['results']:
        if 'report_path' not in t:continue
        report=json.loads((ROOT/t['report_path']).read_text());a=report['external_acceptance'];out=ROOT/a['path']
        paths.add(ROOT/t['source_path'])
        paths.update(p for p in out.rglob('*.json') if p.name not in {'signed_source_input.json','final_payload.json'})
        cases.append({'terminal':t,'acceptance':a,'source_path':t['source_path'],'output_path':a['path'],
                      'source_input_reconstruction':'Byte copy from canonical source_path after hash verification'})
    mirrors={}
    for c in cases:
        mirror=ROOT/c['terminal']['intent_path'];mirror=mirror.parent/'source_receipt.json'
        canonical=ROOT/c['source_path']
        if mirror.read_bytes()!=canonical.read_bytes():raise ValueError('FORWARD_SOURCE_MIRROR_CONFLICT')
        mirrors[str(mirror.relative_to(ROOT))]=c['source_path'];paths.discard(mirror)
    paths={p for p in paths if not p.name.endswith('.tmp') and p.name!='result_worker_status.json'}
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    with tarfile.open(ARCHIVE,'w:gz') as archive:
        for p in sorted(paths):archive.add(p,arcname=str(p.relative_to(ROOT)),recursive=False)
    manifest={'status':'FIVE_REAL_PRESTART_FORWARD_PAPER_FINALS / RESULTS_PENDING','archive_sha256':hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
        'files':hashes,'source_mirrors':mirrors,'cases':cases,'actual_krs_run_count':100000,'source_numerical_values':1479,
        'calculated_numerical_values':1197,'ruled_neutral_values':282,'unresolved_values':0,
        'future_prediction_freeze_count':5,'unknown_future_result_evaluations':0,'purchase_authority':False,
        'unique_venues_with_real_final_including_replay':7,'all_14_venue_real_acceptance':False}
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');return manifest


def restore(destination=ROOT):
    destination=Path(destination);m=json.loads(MANIFEST.read_text())
    if hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()!=m['archive_sha256']:raise ValueError('FORWARD_ARCHIVE_DIGEST_INVALID')
    allowed=('research/local_aki_forward_20261013/','runtime/executions/KM-LOCAL-AKI-FORWARD-',
             'evidence/local_aki_columns_20261012/external/KM-LOCAL-AKI-FORWARD-',
             'profiles/local_aki_prospective_evaluation_20261013_R2.json')
    seen=set()
    with tarfile.open(ARCHIVE,'r:gz') as archive:
        for member in archive.getmembers():
            name=member.name
            if (name not in m['files'] or not member.isfile() or '..' in Path(name).parts or Path(name).is_absolute()
                or not name.startswith(allowed) or member.size>32*1024*1024):raise ValueError('FORWARD_ARCHIVE_MEMBER_INVALID')
            raw=archive.extractfile(member).read()
            if hashlib.sha256(raw).hexdigest()!=m['files'][name]:raise ValueError('FORWARD_ARCHIVE_FILE_DIGEST_INVALID')
            p=destination/name;p.parent.mkdir(parents=True,exist_ok=True)
            if p.exists():
                if p.read_bytes()!=raw:raise ValueError('FORWARD_RESTORE_IMMUTABLE_CONFLICT:'+name)
            else:
                temp=p.with_suffix('.json.tmp');temp.write_bytes(raw);temp.replace(p)
            seen.add(name)
    if seen!=set(m['files']):raise ValueError('FORWARD_ARCHIVE_INCOMPLETE')
    for mirror,canonical in m.get('source_mirrors',{}).items():
        raw=(destination/canonical).read_bytes();p=destination/mirror
        if p.exists() and p.read_bytes()!=raw:raise ValueError('FORWARD_SOURCE_MIRROR_RESTORE_CONFLICT')
        if not p.exists():p.write_bytes(raw)
    for c in m['cases']:
        p=destination/c['output_path']/'signed_source_input.json';raw=(destination/c['source_path']).read_bytes()
        if p.exists() and p.read_bytes()!=raw:raise ValueError('FORWARD_SOURCE_RESTORE_CONFLICT')
        if not p.exists():p.write_bytes(raw)
    return {'status':'HASH_VERIFIED_FORWARD_RECEIPTS_RESTORED','cases':len(m['cases']),'network_calls':0}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['pack','restore']);a=p.parse_args()
    if a.action=='pack':x=pack();print(json.dumps({'cases':len(x['cases']),'archive_bytes':ARCHIVE.stat().st_size}))
    else:print(json.dumps(restore()))

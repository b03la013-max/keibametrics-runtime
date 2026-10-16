"""Offline private-provider normalization. Never grants JRA Production authority.

Run against an explicitly supplied checkpoint ZIP. Originals remain unchanged;
only aggregate audit metadata may be committed to a public repository.
"""
import argparse
from collections import Counter
from datetime import datetime
import hashlib,json,zipfile
from pathlib import Path


def sha(data):return hashlib.sha256(data).hexdigest()


def normalize_checkpoint(path, cutoff=None):
    with zipfile.ZipFile(path) as z:
        hashes=json.loads(z.read('sha256.json'))
        for name,expected in hashes.items():
            if sha(z.read(name))!=expected:raise ValueError('PRIVATE_CHECKPOINT_HASH_MISMATCH:'+name)
        raw=z.read('results.json');rows=json.loads(raw)
        races={r['race_id']:r for r in json.loads(z.read('races.json'))}
        state=json.loads(z.read('collection_state.json'))
        observed=json.loads(z.read('observed_races.json'))
    limit=datetime.fromisoformat(cutoff.replace('Z','+00:00')) if cutoff else None
    if limit is not None and limit.tzinfo is None:raise ValueError('PIT_TIMEZONE_REQUIRED')
    normalized=[];seen={};conflicts=set();future=0
    for row in rows:
        at=datetime.fromisoformat(row['observed_at'].replace('Z','+00:00'))
        if at.tzinfo is None:raise ValueError('SOURCE_TIMEZONE_REQUIRED')
        if limit is not None and at>limit:future+=1;continue
        rid=str(row['race_id']);number=str(row['horse_number']);hid=str(row.get('horse_id') or '')
        if not hid or rid not in races:raise ValueError('PROVIDER_IDENTITY_OR_RACE_MISSING')
        key=(rid,number)
        core={k:row.get(k) for k in ('horse_id','horse_name','sire','damsire','finish','time')}
        if key in seen:
            if seen[key]!=core:conflicts.add(key)
            continue
        seen[key]=core
        item={'provider':'BLOOD_B','provider_race_id':rid,'runner_number':number,
            'horse_id':'bloodb:'+hid,'official_horse_id':None,'horse_name':row['horse_name'],
            'sire_id':None,'sire_name':row.get('sire'),'dam_id':None,'dam_name':None,
            'damsire_id':None,'damsire_name':row.get('damsire'),'birth_year':None,
            'sex':str(row.get('sex_age') or '')[:1] or None,
            'sex_age_raw':row.get('sex_age'),'sire_lineage_raw':row.get('sire_lineage'),
            'damsire_lineage_raw':row.get('damsire_lineage'),
            'source_observed_at':row['observed_at'],'source_available_at':row['observed_at'],
            'availability_basis':'OBSERVATION_UPPER_BOUND_NOT_ORIGINAL_PUBLICATION',
            'source_sha256':sha(raw),'source_row_sha256':sha(json.dumps(row,sort_keys=True,ensure_ascii=False).encode()),
            'pedigree_source':row['source_url'],'lineage_version':'BLOODB-PRIVATE-REFERENCE-v1',
            'race_date':row['race_date'],'condition_text':races[rid].get('condition_text'),
            'identity_status':'PROVIDER_ID_ONLY; OFFICIAL_CROSSWALK_AND_DAM_REQUIRED',
            'display_names_may_be_abbreviated':True,'production_authority':False,
            'scope':'PRIVATE_RESEARCH_QUARANTINE','historical_prediction_validation':False}
        normalized.append(item)
    normalized=[r for r in normalized if (r['provider_race_id'],r['runner_number']) not in conflicts]
    audit={'profile':'KM-JRA-PRIVATE-PEDIGREE-INTAKE-v1','archive_sha256':sha(Path(path).read_bytes()),
        'archive_member_hashes_verified':len(hashes),'requested_period':state['requested_period'],
        'observed_race_links':len(observed),'result_races':len({r['provider_race_id'] for r in normalized}),
        'runner_rows':len(normalized),'provider_horse_ids':len({r['horse_id'] for r in normalized}),
        'result_dates':sorted({r['race_date'] for r in normalized}),
        'runner_rows_by_year':dict(sorted(Counter(r['race_date'][:4] for r in normalized).items())),
        'sire_present':sum(bool(r['sire_name']) for r in normalized),
        'dam_present':sum(bool(r['dam_name']) for r in normalized),
        'damsire_present':sum(bool(r['damsire_name']) for r in normalized),
        'official_identity_resolved':0,'duplicate_runner_keys':len(rows)-len(seen)-future,
        'conflicting_runner_keys':len(conflicts),'excluded_after_cutoff':future,
        'prediction_cutoff':cutoff,'provider_permission_statement':state.get('permission_basis'),
        'permission_document_independently_verified':False,
        'complete_five_year_population':False,'production_rows_imported':0,
        'collection_status':state['status'],'public_raw_redistribution':False}
    return normalized,audit


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--output-directory',type=Path,required=True);p.add_argument('--prediction-cutoff');a=p.parse_args()
    rows,audit=normalize_checkpoint(a.checkpoint,a.prediction_cutoff)
    a.output_directory.mkdir(parents=True,exist_ok=True)
    (a.output_directory/'pedigree_private_normalized.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    (a.output_directory/'inventory.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:audit[k] for k in ('result_races','runner_rows','provider_horse_ids','production_rows_imported')}))

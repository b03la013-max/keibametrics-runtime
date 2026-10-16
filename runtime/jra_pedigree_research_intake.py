"""Offline private-provider normalization. Never grants JRA Production authority.

Run against an explicitly supplied checkpoint ZIP. Originals remain unchanged;
only aggregate audit metadata may be committed to a public repository.
"""
import argparse
from collections import Counter
from datetime import datetime
import hashlib,json,zipfile
from pathlib import Path
from urllib.parse import urlsplit, parse_qs


def sha(data):return hashlib.sha256(data).hexdigest()


def reconcile_checkpoint(path):
    """Reconcile retained source tables, inventory, queue and persisted rows.

    Returns aggregate metadata only; no provider rows or URLs are published.
    Does not acquire data, rewrite the checkpoint or grant source eligibility.
    """
    import sqlite3
    _, normalized = normalize_checkpoint(path)  # Verify every retained member first.
    def code(url):
        values = parse_qs(urlsplit(url).query).get('rcode', [])
        if len(values) != 1 or not values[0].isdigit():
            raise ValueError('PRIVATE_CHECKPOINT_RACE_URL_INVALID')
        return values[0]
    with zipfile.ZipFile(path) as z:
        inventory = json.loads(z.read('observed_races.json'))
        rows = json.loads(z.read('results.json'))
        races = json.loads(z.read('races.json'))
        queue = json.loads(z.read('resume_queue.json'))
        state = json.loads(z.read('collection_state.json'))
        worker = json.loads(z.read('worker_status.json'))
        pages = [json.loads(x) for x in z.read('raw_pages.jsonl').splitlines()]
        prior = [json.loads(x) for x in z.read('prior_raw_results.jsonl').splitlines()]
        db = sqlite3.connect(':memory:')
        try:
            db.deserialize(z.read('bloodb_checkpoint.sqlite'))
            sql = {'integrity':db.execute('pragma integrity_check').fetchone()[0],
                'races':db.execute('select count(*) from races').fetchone()[0],
                'rows':db.execute('select count(*) from results').fetchone()[0]}
            sql_keys = set(db.execute('select race_id,horse_number,horse_id from results'))
        finally:db.close()
    ids = {code(x['url']) for x in inventory}
    raw = {code(x['url']):x for x in prior}
    raw.update({code(x['url']):x['data'] for x in pages if x['kind']=='result'})
    parsed = {}; unparsed = 0; duplicate_rows = 0; row_conflicts = 0
    for rid,data in raw.items():
        for table in data['tables']:
            for row in table:
                if isinstance(row,dict): cells,links = row['cells'],row['links']
                else:
                    cells=[c['text'] for c in row]
                    links=[link for c in row for link in c['links']]
                horses=[x for x in links if 'hinfo?hcode=' in x['url']]
                if not horses:continue
                if len(cells)!=21:
                    unparsed+=1;continue
                hid=parse_qs(urlsplit(horses[0]['url']).query)['hcode'][0]
                key=(rid,str(cells[2]))
                value=(hid,str(cells[4]),str(cells[5]),str(cells[7]))
                if key in parsed:
                    duplicate_rows+=1;row_conflicts+=int(parsed[key]!=value)
                parsed[key]=value
    saved={(str(r['race_id']),str(r['horse_number'])):
           (str(r['horse_id']),str(r['horse_name']),str(r['sire']),str(r['damsire'])) for r in rows}
    race_ids={str(x['race_id']) for x in races}
    mismatches=sum(r['race_date']!=str(r['race_id'])[:8] or code(r['source_url'])!=str(r['race_id']) for r in rows)
    mismatches+=sum(r['race_date']!=str(r['race_id'])[:8] or code(r['source_url'])!=str(r['race_id']) for r in races)
    pending={str(x['race_id']) for x in queue['races'] if x['result_pending']}
    missing=ids-race_ids
    years=sorted({rid[:4] for rid in ids}|{rid[:4] for rid in race_ids})
    by_year={year:{'observed_links':sum(r[:4]==year for r in ids),
        'raw_result_races':sum(r[:4]==year for r in raw),
        'persisted_result_races':sum(r[:4]==year for r in race_ids),
        'runner_rows':sum(r['race_date'][:4]==year for r in rows),
        'uncollected_observed_links':sum(r[:4]==year for r in missing)} for year in years}
    sql_match=sql['integrity']=='ok' and sql['races']==len(races) and sql['rows']==len(rows) and sql_keys=={(str(r['race_id']),str(r['horse_number']),str(r['horse_id'])) for r in rows}
    report={'profile':'KM-JRA-BLOODB-CHECKPOINT-RECONCILIATION-v1',
        'archive_sha256':normalized['archive_sha256'],'archive_member_hashes_verified':normalized['archive_member_hashes_verified'],
        'requested_period':state['requested_period'],'by_year':by_year,
        'unique_observed_links':len(ids),'duplicate_inventory_links':len(inventory)-len(ids),
        'persisted_result_races':len(race_ids),'persisted_runner_rows':len(rows),
        'uncollected_observed_links':len(missing),'observed_link_capture_pct':100*len(ids&race_ids)/len(ids) if ids else None,
        'national_coverage_denominator':'UNKNOWN; OBSERVED_PROVIDER_LINKS_ONLY',
        'raw_result_races':len(raw),'raw_parsed_runner_rows':len(parsed),'unparsed_horse_rows':unparsed,
        'raw_rows_missing_from_persistence':len(set(parsed)-set(saved)),
        'persisted_rows_without_raw':len(set(saved)-set(parsed)),
        'raw_persisted_parent_or_identity_mismatches':sum(parsed[k]!=saved[k] for k in set(parsed)&set(saved)),
        'raw_duplicate_runner_rows':duplicate_rows,'raw_conflicting_runner_rows':row_conflicts,
        'date_or_race_url_join_mismatches':mismatches,'results_not_in_observed_inventory':len(race_ids-ids),
        'resume_queue_missing_result_links':len(missing-pending),'resume_queue_unexpected_pending':len(pending-missing),
        'sqlite':{**sql,'matches_json':sql_match},
        'collection_status':state['status'],'worker_phase':worker.get('phase'),
        'worker_error':worker.get('error'),
        'missing_2022_2025_cause':('NOT_COLLECTED_BEFORE_BACKGROUND_WORKER_FAILURE'
            if all(by_year.get(str(y),{}).get('raw_result_races',0)==0 for y in range(2022,2026))
            and 'exec context not found' in str(worker.get('error')) else 'REQUIRES_SEPARATE_INVESTIGATION'),
        'provider_unavailability':'NOT_ESTABLISHED','permission_denial':'NOT_ESTABLISHED',
        'recovered_result_rows':0,'production_rows_imported':0,
        'source_eligibility':'PRIVATE_RESEARCH_ONLY; OFFICIAL_CROSSWALK_AND_APPROVAL_NOT_ESTABLISHED',
        'postcapture_for_historical_prediction':True,'checkpoint_modified':False}
    return report


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

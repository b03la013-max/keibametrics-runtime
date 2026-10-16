"""Read-only reconciliation of private research exports with canonical sources.

Never copies provider rows or credentials into the repository. Counts are not a
Production admission decision; authenticated ingestion remains mandatory.
"""
import argparse,collections,csv,hashlib,io,json,zipfile
from pathlib import Path


def digest(data):return hashlib.sha256(data).hexdigest()


def inventory(root, bundle):
    with zipfile.ZipFile(bundle) as z:
        def read(name):return z.read(next(n for n in z.namelist() if n.endswith('/'+name)))
        rows=[json.loads(line) for line in read('integrated_runs.jsonl').decode().splitlines() if line.strip()]
        refs=json.loads(read('source_manifest.json'))
        audit=json.loads(read('audit.json'))
    reconciled=[]
    for ref in refs:
        path=(root/ref['path']).resolve()
        if not path.is_relative_to(root.resolve()):raise ValueError('SOURCE_PATH_OUTSIDE_REPOSITORY')
        reconciled.append({'path':ref['path'],'expected_sha256':ref['file_sha256'],
            'actual_sha256':digest(path.read_bytes()) if path.is_file() else None})
    flat=[r for r in rows if r.get('surface') in ('芝','ダ','ダート')]
    def counts(key):return dict(sorted(collections.Counter(str(r.get(key) or 'UNKNOWN') for r in flat).items()))
    source_dates=[r.get('observed_at_first') or r.get('source_observed_at') for r in rows]
    return {'bundle_sha256':digest(bundle.read_bytes()),'row_count':len(rows),'flat_rows':len(flat),
        'composite_horse_identities':len({r['horse_id'] for r in rows}),
        'identity_kind':'NAME_SIRE_DAM_COMPOSITE_NOT_OFFICIAL_ID',
        'date_min':min(r['date'] for r in rows),'date_max':max(r['date'] for r in rows),
        'flat_coverage':{k:counts(k) for k in ('year','venue','surface','distance_m','race_class','age','sex')},
        'parent_nonempty_rows':{k:sum(bool(r.get(k)) for r in flat) for k in ('sire','dam','damsire')},
        'first_observation_min':min(x for x in source_dates if x),
        'first_observation_max':max(x for x in source_dates if x),
        'primary_sources':reconciled,'primary_sources_exact_match':sum(x['expected_sha256']==x['actual_sha256'] for x in reconciled),
        'official_corpus_files':len(list((root/'runtime/pedigree_corpus').glob('*.json'))),
        'archive_reported_counts':audit,'new_production_rows_imported':0,
        'disposition':'REUSE_VERIFIED_PRIMARY_SOURCES; DO_NOT_APPEND_DUPLICATE_RESEARCH_ROWS',
        'national_coverage_denominator':'UNKNOWN','full_five_year_national_coverage':False,
        'historical_availability':'USE_OBSERVATION_TIME; DO_NOT_BACKDATE_TO_RACE_DATE',
        'production_admission':'EXISTING_SIGNATURE_OIDC_AND_PIT_GATES_REQUIRED',
        'research_utility_demonstrated':False}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=inventory(a.root,a.bundle);a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('row_count','flat_rows','composite_horse_identities','primary_sources_exact_match','official_corpus_files')}))

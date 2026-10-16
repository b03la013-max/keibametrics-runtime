"""Offline inventory of actual Phase3 captures; never admits data or infers IDs."""
from collections import Counter
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]

def read(paths, strict=True):
    profiles, runs, files = {}, {}, []
    for path in sorted(paths):
        data = json.loads(path.read_text())
        assert data['official'] is True and data['source'] == 'www.jra.go.jp'
        if strict:
            assert not data['errors'], (str(path), data['errors'])
        assert data['horse_count'] == len(data['horses'])
        files.append({'file':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                      'observed_at':data['harvested_at'], 'profiles':len(data['horses']),
                      'run_occurrences':sum(len(h['runs']) for h in data['horses']),
                      'selected_date':data['race_date'], 'errors':data['errors']})
        for horse in data['horses']:
            # A diagnostic surrogate, never an official identity or auto-join key.
            identity = tuple(horse.get(k) for k in ('horse_name','sire','dam','damsire'))
            assert all(identity), identity
            profiles[identity] = horse
            for row in horse['runs']:
                assert row['date'] <= data['harvested_at'][:10], row
                key = identity + tuple(row.get(k) for k in ('date','venue','surface','distance_m','race_name'))
                runs[key] = row
    return profiles, runs, files

def main():
    newp, newr, files = read((ROOT/'research/jra_bvi_phase3/official_recovery_20261017').glob('*.json'))
    oldp, oldr, oldfiles = read((ROOT/'research/jra_bvi_phase2/official_recovery_20261017').glob('*.json'))
    _, stored, storedfiles = read((ROOT/'runtime/pedigree_corpus').glob('*.json'), strict=False)
    combined = oldr | newr
    def coverage(rows):
        return {label:dict(sorted(Counter(str(row.get(key)) for row in rows.values()).items()))
                for label,key in [('venue','venue'),('surface','surface'),('distance_m','distance_m'),('race_name_not_normalized_class','race_name')]}
    def years(rows):
        return dict(sorted(Counter(row['date'][:4] for row in rows.values()).items()))
    report = {'identity_basis':'horse name + sire + dam + damsire / date + venue + surface + distance + race name; diagnostic surrogate only',
              'files':files, 'before_phase2_profiles':len(oldp), 'before_phase2_distinct_run_surrogates':len(oldr),
              'new_profile_surrogates':len(newp), 'new_run_occurrences':sum(f['run_occurrences'] for f in files),
              'new_distinct_run_surrogates':len(newr), 'duplicate_new_run_occurrences':sum(f['run_occurrences'] for f in files)-len(newr),
              'new_overlap_phase2_run_surrogates':len(newr.keys() & oldr.keys()),
              'stored_corpus_files_with_acquisition_errors':sum(bool(f['errors']) for f in storedfiles),
              'new_overlap_stored_corpus_run_surrogates':len(newr.keys() & stored.keys()),
              'new_run_surrogates_absent_both_previous_sets':len(newr.keys()-oldr.keys()-stored.keys()),
              'after_phase2_plus_phase3_profile_surrogates':len(oldp.keys() | newp.keys()),
              'after_phase2_plus_phase3_run_surrogates':len(combined),
              'new_years':years(newr),'combined_years':years(combined),'new_coverage':coverage(newr),
              'sire_sample_counts':{s:{'distinct_horse_surrogates':sum(h[1]==s for h in newp),'run_observations':sum(k[1]==s for k in newr)} for s in sorted({h[1] for h in newp})},
              'damsire_sample_counts':{s:{'distinct_horse_surrogates':sum(h[3]==s for h in newp),'run_observations':sum(k[3]==s for k in newr)} for s in sorted({h[3] for h in newp})},
              'jump_named_history_rows':sum('障害' in r['race_name'] for r in newr.values()),
              'discipline_caution':'Surface text may be turf for jumps. Do not use jump history as flat-race population without existing discipline eligibility rules.',
              'parent_name_coverage':{k:sum(bool(h.get(k)) for h in newp.values()) for k in ('sire','dam','damsire')},
              'official_horse_sire_damsire_race_ids_resolved':False,
              'independent_result_available_at_known':False,
              'historical_prediction_eligibility':'NOT_ESTABLISHED; observed at actual 2026 capture, no backdating',
              'production_rows_admitted':0,'production_eligibility':'PENDING_EXISTING_OIDC_INTAKE_AND_IDENTITY_RULES',
              'bloodb_before_after':{'result_races':[528,528],'result_rows':[7059,7059],'pending_links':[16812,16812],
                                     'reason':'No provider-to-official ID crosswalk; official profile samples do not close provider queue'},
              'national_five_year_race_denominator_known':False,
              'complete_result_races_recovered':0,
              'race_surrogates_in_new_history':len({tuple(r.get(k) for k in ('date','venue','surface','distance_m','race_name')) for r in newr.values()}),
              'race_surrogate_caution':'Race number/official race_id unresolved; this is not a complete race count'}
    target=ROOT/'evidence/jra_bvi_phase3_20261017/data_recovery.json'
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('files','new_coverage')},ensure_ascii=False))

if __name__=='__main__':
    main()

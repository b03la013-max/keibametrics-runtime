"""Offline actual-source pedigree/person audit; no acquisition or scoring."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(ROOT/'runtime/local_physical')]
from runtime import local_pedigree_person_evidence as audit
from runtime.local_bvi_bloodline_research import evaluate
from runtime.ohi_single_race_research import readback,private_root,write
PARSER_SHA='470e5f1c6a0fcb35363cfe59632b2c00f5d8537d9000e496b399a85c4d61223c'

def run(original_root,dataset_dir,person_envelope,pinned_parser):
    original_root=Path(original_root);dataset_dir=Path(dataset_dir);parser=Path(pinned_parser)
    if hashlib.sha256(parser.read_bytes()).hexdigest()!=PARSER_SHA:raise ValueError('PERSON_PARSER_HISTORICAL_CODE_SHA')
    spec=importlib.util.spec_from_file_location('local_person_parser_pinned',parser);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    originals=[readback(original_root/('live-r01-v1' if i==1 else f'live-r{i:02d}-v2'))[0] for i in range(1,13)]
    if any(o['race']['race_date']!='2026-10-26' or o['race']['race_no']!=i for i,o in enumerate(originals,1)):raise ValueError('PEDIGREE_PERSON_FIXED_COHORT_IDENTITY')
    as_of=min(o['source_fetched_at'] for o in originals);ep=Path(person_envelope);env=json.loads(ep.read_text())
    riders=audit.audit_signed_riders(env,audit.TRUSTED_PUBLIC_KEY_B64,as_of,mod.parse_person_profile)
    manifest=json.loads((dataset_dir/'manifest.json').read_text());raw=(dataset_dir/manifest['data_file']).read_bytes()
    reference=audit.audit_reference_dataset(manifest,raw,as_of);data=json.loads(raw)
    ae=[]
    for o in originals:
        for h in o['all_runners']:
            ae.append({'race_id':o['race']['provider_race_id'],'runner_id':h['runner_id'],
                       'existing_research':evaluate(h,o['race'],o['source_fetched_at'],(manifest,data))})
    cohort=audit.selected_history_cohort(originals);links=audit.current_rider_links(originals,riders)
    component_eligibility={
        'BVIg-L':{k:{'existing_rule_input_eligible':False,'score_consumption':False,
             'reason':'OFFICIAL_SAME_CONDITION_POPULATION_OR_COMPARISON_NOT_CONNECTED; AEI_AND_SELECTED_FIELD_HISTORY_ARE_NOT_SUBSTITUTES'}
             for k in ('sire_fit','damsire_fit','distance_sustain','distance_trait','surface_sand_fit','venue_stat','physical_style_fit')},
        'JTI-L':{k:{'independent_source_available':k in ('favorite_reliability','longshot_record'),
             'existing_rule_input_eligible':False,'score_consumption':False,
             'reason':'CAPTURED_PERSON_TOTALS_ARE_ALL_LOCAL_AND_POPULARITY_STRATA; EXISTING_RULE_IS_CURRENT_JOCKEY_ON_THIS_HORSE; NEW_TRANSFORM_AND_LICENSE_CROSSWALK_REQUIRED'}
             for k in ('venue_recent','distance_record','stable_combo','position_acquisition_skill','progression_timing_skill','favorite_reliability','longshot_record')}}
    result={'scope':'READ_ONLY_HISTORICAL_SOURCE_AUDIT_NOT_NEW_SCORING','baseline_date':'2026-10-26',
            'runners':sum(len(o['all_runners']) for o in originals),'official_person_audit':riders,
            'current_rider_links':links,'pedigree_dataset_audit':reference,
            'existing_aei_reference_matches':ae,'current_field_cohort':cohort,
            'component_eligibility':component_eligibility,
            'source_envelope_bytes_sha256':hashlib.sha256(ep.read_bytes()).hexdigest(),
            'parser_code_sha256':PARSER_SHA,'original_prediction_sha256':[o['sha256'] for o in originals],
            'implementation_sha256':{x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in
                  ('runtime/local_pedigree_person_evidence.py','scripts/local_pedigree_person_audit.py')},
            'bvi_numeric_consumption':False,'jti_numeric_consumption':False,
            'summary':{'rider_profiles':len(riders['profiles']),'current_links':dict(Counter(x['connection'] for x in links)),
                       'aei_reference_runners_with_observed_weight':sum(x['existing_research']['research_observed_weight']>0 for x in ae),
                       'cohort_records':len(cohort['records']),'cohort_groups':len(cohort['groups']),'cohort_excluded':cohort['excluded']}}
    result['sha256']=audit.sha(result);return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('original-root','dataset-dir','person-envelope','pinned-parser','output'):p.add_argument('--'+name,required=True)
    a=p.parse_args();out=private_root(a.output)
    if out.exists():raise ValueError('PERSON_AUDIT_REVISION_EXISTS')
    result=run(a.original_root,a.dataset_dir,a.person_envelope,a.pinned_parser);write(out,result)
    print(json.dumps({'sha256':result['sha256'],**result['summary']},ensure_ascii=False))
if __name__=='__main__':main()

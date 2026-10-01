"""Read-only report of current registries, frozen development and forward ledgers."""
from pathlib import Path
import json,sys,hashlib,subprocess,collections
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'runtime'))
from local_candidate_postresult import forward_status
from local_numerical_authority_gate import assess
from pfs_grand_review import build_report

def run():
    d=json.loads((ROOT/'research/utility/development_summary.json').read_text());p=json.loads((ROOT/'research/utility/program_status.json').read_text());pfs=build_report();forward=forward_status()
    # Policy/mapping/engine content equality to current main; hooks are measurement-only changes.
    main='d3093d42ca0ef9d97a62fd7789fff0022d1a098d'
    protected=[x for x in subprocess.check_output(['git','ls-files','mapping','runtime/parameter_map.json','runtime/local_physical/engine.py','runtime/mec_r3.py'],text=True).splitlines() if Path(x).is_file()]
    hashes={}
    for path in protected:
        old=subprocess.check_output(['git','show',main+':'+path]);now=Path(path).read_bytes()
        if old!=now:raise RuntimeError('PRODUCTION_POLICY_CHANGED:'+path)
        hashes[path]=hashlib.sha256(now).hexdigest()
    numeric=[r for r in d['races'] if r['status']=='DEVELOPMENT_EVALUATED']
    comparisons={key:{arm:sum(float(r[arm][key]) for r in numeric)/len(numeric) for arm in ['baseline','candidate']} for key in ['winner_rank','winner_reciprocal_rank','mean_actual_top3_rank','top3_contained_count','W_hit','P2_hit','P3_hit']}
    summary={'production_main':main,'authority':assess(),'development':comparisons,'component_classes':dict(collections.Counter(r['classification'] for r in d['component_map'])),
      'programs':p,'forward':forward,'actual_verified_races':pfs['actual_pfs']['verified_race_count'],'pfs_by_family':pfs['frozen_by_family'],'tier_pfs':pfs['tier_pfs'],
      'production_policy_hashes':hashes,'production_policy_unchanged':True,'verdict':'IMPLEMENTED / FORWARD LIFECYCLE CONNECTED IN CANDIDATE / EMPIRICAL VERDICT PENDING',
      'deployment':'PR117 unmerged; main forward execution starts only after research merge. No live activation claimed.',
      'limitations':d['limitations']+['No authentic purchase ledger supplied; real archived official result and explicit test-only purchase schema mechanically accepted; actual evidence remains zero.']}
    (ROOT/'research/utility/PHASE_B1_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'production_unchanged':True,'protected_files':len(hashes),'development_races':len(numeric),'local_forward_oos':forward['families']['LOCAL']['eligible_races'],'actual':summary['actual_verified_races']}))
if __name__=='__main__':run()

"""Run retrospective research using immutable files from an explicit data root."""
import argparse,gzip,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'research/jra_20261024_prediction'))
from replay import run
from candidates import digest

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-root',type=Path,default=ROOT);ap.add_argument('--output',type=Path,default=ROOT/'research/jra_20261024_prediction/replay.json.gz');a=ap.parse_args()
    report=run(a.data_root);a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_bytes(gzip.compress(json.dumps(report,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode(),mtime=0))
    summary={k:v for k,v in report.items() if k not in ['races','failure_matrix','all_runner_audit','frozen_input_audits','sha256']};summary['full_report_sha256']=report['sha256'];summary['runner_observations']=len(report['all_runner_audit']);summary['race_count']=len(report['races']);summary['runner_counts_by_venue']={v:sum(x['venue']==v for x in report['all_runner_audit']) for v in ['TKY','KYO','NGT']};summary['gci_context_coverage']=[{'race_id':x['race_id'],**{k:v for k,v in x['same_day_gci'].items() if k!='frozen_source_races'}} for x in report['frozen_input_audits']];summary['sha256']=digest(summary)
    a.output.with_name('summary.json').write_text(json.dumps(summary,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    a.output.with_name('failure_matrix.json').write_text(json.dumps({'classification':report['classification'],'races':report['failure_matrix']},ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'races':len(report['races']),'runners':len(report['all_runner_audit']),'arms':list(report['candidate_metrics']),'classification':report['classification'],'files':[str(a.output),str(a.output.with_name('summary.json')),str(a.output.with_name('failure_matrix.json'))]},ensure_ascii=False))

if __name__=='__main__':main()

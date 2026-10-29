"""Package large read-only audit inputs/exports; retain human-readable entrypoints."""
import gzip,hashlib,json,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
E=Path('evidence/jra_day_review_20261017');D=Path('runtime/daily_reviews/JRA-2026-10-17')

def pack():
    keep=[D/x for x in ['README.md','daily_formal_review.md','pfs_grand_review.md','improvement_backlog.md',
        'next_race_learning_oos.md','summary.json','scorecard.csv','completion.json','improvement_backlog.json',
        'forward_oos_plan.json','next_race_learning_index.json','krs_incremental_utility.json','bvi_consumption_review.json']]
    keep += [E/x for x in ['validation.json','current_authority.json','runtime_health.json','workflow_result_publisher_39014862272.json']]
    keep += [D/'supplemental_metrics.json',D/'dead_heat_review.json',E/'ci_reconciliation.json',
             E/'runtime_followup.json',E/'source_oidc/summary.json']
    keep += [D/x for x in ['remaining_evidence_closure.md','execution_assurance_closure.json',
        'delivery_learning_consumption.md','prediction_failure_matrix.json','aki_incremental_comparison.json',
        'capital_research_comparison.json','preregistered_shadow_comparison.json','venue_canon_verdict.json',
        'krs_unique_role_shadow_replay.json']]
    keep += [E/'runtime_contract_readback.json']
    keep += list(Path('runtime/learning_states/jra_day_review_20261017').glob('*.json'))
    files=[]
    for folder in [E,D,Path('runtime/pfs_grand_review')]:
        paths=(ROOT/folder).rglob('*') if folder!=Path('runtime/pfs_grand_review') else [(ROOT/folder/'JRA-2026-10-17.json')]
        for p in paths:
            if not p.is_file():continue
            rel=p.relative_to(ROOT)
            if rel in keep or p.name in ('payload.tar.gz','payload_manifest.json'):continue
            files.append(rel)
    files=sorted(set(files))
    bundle=ROOT/E/'payload.tar.gz'
    with bundle.open('wb') as output:
        with gzip.GzipFile(filename='',fileobj=output,mode='wb',mtime=0,compresslevel=9) as gz:
            with tarfile.open(fileobj=gz,mode='w') as tar:
                for rel in files:
                    info=tar.gettarinfo(str(ROOT/rel),arcname=str(rel));info.mtime=0;info.uid=info.gid=0;info.uname=info.gname=''
                    with (ROOT/rel).open('rb') as fh:tar.addfile(info,fh)
    manifest={'format':'tar.gz; relative paths; original file bytes preserved','archive_sha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),
        'files':[{'path':str(rel),'size':(ROOT/rel).stat().st_size,'sha256':hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()} for rel in files],
        'materialize':'python scripts/unpack_jra_day_review.py','readable_entrypoints':[str(x) for x in keep]}
    (ROOT/E/'payload_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    paths=keep+[E/'payload.tar.gz',E/'payload_manifest.json',Path('runtime/krs_prediction_utility.py'),
        *[Path('scripts')/x for x in ['collect_jra_day_review.py','jra_full_day_postrace_review.py','render_jra_day_review.py','pack_jra_day_review.py','unpack_jra_day_review.py',
                                   'jra_dead_heat_review.py','verify_jra_day_source_oidc.py',
                                   'jra_execution_assurance_review.py','jra_assurance_learning_update.py']],
        Path('tests/test_jra_day_review.py')]
    Path('/tmp/km-review-stage-paths.json').write_text(json.dumps([str(x) for x in paths]))
    print(json.dumps({'archive_bytes':bundle.stat().st_size,'members':len(files),'tracked_paths':len(paths)}))

if __name__=='__main__':pack()

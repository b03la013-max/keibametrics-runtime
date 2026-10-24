"""Read-only reconciliation of private research exports with canonical sources.

Never copies provider rows or credentials into the repository. Counts are not a
Production admission decision; authenticated ingestion remains mandatory.
"""
import argparse,collections,csv,hashlib,io,json,zipfile
import sys,tempfile,urllib.request,subprocess
from datetime import datetime,timezone,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(ROOT/'runtime/jra_source_runtime')]


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


def official_audit(root, *, target_date=None, prediction_date=None, plan_path=None):
    """Authenticated actual Reader/Compiler audit, not a new Producer or model."""
    from jra_pedigree_corpus import build_corpus,_verified_harvest,_verified_source,_attested,_horse_identity,_clean_runs
    from jra_bvi_consumption import build_bvi_consumption,sha
    from jra_owner_authorized_feature_rules import owner_authorized_observations,class_rank
    from jra_bvi_shadow_comparison import compare,PEDIGREE_FEATURES
    from family_authority_guard import resolve_current_authority
    root=Path(root);now=datetime.now(timezone.utc);cutoff=now.isoformat()
    day=now.astimezone(timezone(timedelta(hours=9))).date()
    prediction_date=prediction_date or day.isoformat()
    target_date=target_date or (day+timedelta(days=1)).isoformat()
    _,authority=resolve_current_authority(root)
    contracts=json.loads((root/authority['common_family_components']['family_runtime_contracts_profile']).read_text())
    contract=contracts['families']['JRA']
    # Read-only existing trust anchor; never executes a KRS or Production job.
    with urllib.request.urlopen(contract['external_endpoint'].rstrip('/')+'/health',timeout=20) as response:
        health=json.load(response)
    corpus=build_corpus(root,prediction_cutoff=cutoff,race_date=target_date)
    artifacts=[];raw_horses=[];runs={};run_conflicts=set();windows={};valid_run_observations=0
    parent_coverage=collections.Counter()
    for path in sorted((root/'runtime/pedigree_corpus').glob('*.json')):
        obj=_verified_harvest(path,not_after=now)
        if obj is None:continue
        if datetime.fromisoformat(obj['harvested_at'])>now:continue
        key=(obj.get('race_date'),obj.get('mode'),obj.get('start_race'))
        observed=obj.get('race_observations') or []
        artifact={'file':path.name,'sha256':obj['sha256'],'file_sha256':digest(path.read_bytes()),
            'date':obj['race_date'],'mode':obj['mode'],'start_race':obj.get('start_race'),
            'collection_started_at':obj.get('collection_started_at'), 'captured_at':obj['harvested_at'],
            'oidc_verified_by':cutoff,'reader_consumed':'ATTESTED_HARVEST:'+obj['sha256'] in corpus['snapshots'],
            'horses':obj['horse_count'],'prior_run_observations':sum(len(h.get('runs',[])) for h in obj['horses']),
            'profile_targets':obj['horse_token_count'],'acquisition_errors':len(obj.get('errors',[])),
            'parsed_runner_rows':sum(len(r.get('runners',[])) for r in observed),
            'profile_complete':obj['horse_count']==obj['horse_token_count'],
            'race_ids':[r['race_id'] for r in observed],
            'race_universe_missing':sum(r.get('universe_status')!='OBSERVED_OFFICIAL' for r in observed),
            'navigation_only_horses':sum(bool(h.get('official_profile_navigation_token')) for h in obj['horses']),
            'permanent_horse_ids':sum(bool(h.get('official_permanent_horse_id')) for h in obj['horses'])}
        artifacts.append(artifact)
        previous=windows.get(key)
        if previous is None or (artifact['profile_complete'],len(artifact['race_ids']))>(previous['profile_complete'],len(previous['race_ids'])):windows[key]=artifact
        for h in obj['horses']:
            parent_coverage.update(k for k in ('sire','dam','damsire') if h.get(k))
            identity=_horse_identity(h);raw_horses.append(identity)
            clean=[(run,raw.get('going') or 'UNKNOWN') for raw in h.get('runs',[]) if isinstance(raw,dict)
                   for run in _clean_runs([raw],datetime.fromisoformat(target_date).date())]
            for run,going in clean:
                valid_run_observations+=1
                rk=(identity,run['date'],run['venue'],run['surface'],run['distance_m'],run['race_name'])
                fact=(run['finish'],run['field_size'])
                if rk in runs and runs[rk]['fact']!=fact:run_conflicts.add(rk)
                value=runs.setdefault(rk,{'fact':fact,'sire':h.get('sire'),'damsire':h.get('damsire'),'going':set()})
                value['going'].add(going)
    unique_keys_before_conflicts=len(runs)
    for key in run_conflicts:runs.pop(key,None)
    raw_runs=sum(a['prior_run_observations'] for a in artifacts)
    groups={}
    for key,value in runs.items():
        identity,day,venue,surface,distance,name=key
        for parent in ('sire','damsire'):
            if not value[parent]:continue
            going=next(iter(value['going'])) if len(value['going'])==1 else 'CONFLICT_UNRESOLVED'
            group=(parent,value[parent],venue,surface,distance,class_rank(name),going)
            g=groups.setdefault(group,{'offspring':set(),'runs':0,'top3':0})
            g['offspring'].add(identity);g['runs']+=1;g['top3']+=value['fact'][0]<=3
    quality=[{'parent_type':k[0],'parent':k[1],'venue':k[2],'surface':k[3],'distance_m':k[4],
              'class_rank':k[5],'independent_composite_offspring':len(v['offspring']),
              'runs':v['runs'],'top3':v['top3'],'top3_rate':v['top3']/v['runs'],
              'uncertainty':'REPEATED_HORSE_CLUSTERS; NO_INDEPENDENT_RUN_BINOMIAL_ASSUMPTION',
              'going':k[6],'going_authority':'VERIFIED_HARVEST_FACT; QUALITY_GROUP_ONLY_NOT_NEW_BVI_INPUT',
              'model_training_eligible':False,'statistical_advantage':'INSUFFICIENT DATA'}
             for k,v in sorted(groups.items(),key=lambda item:str(item[0]))]
    mapping=json.loads((root/'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json').read_text())
    registry=json.loads((root/'mapping/jra_evidence_feature_rule_registry_v1.3_20261010.json').read_text())
    predictions=[];counts=collections.Counter();diagnostics=[];no_bet=[];no_bet_counts=collections.Counter()
    requests=sorted((root/'runtime/requests').glob(f'*{prediction_date.replace("-","")}*FORMAL.json'))
    new_files={a['file'] for a in artifacts if a['date'] in (prediction_date,target_date) and a['file']!='20261024-cards-race0-r3.json'}
    for path in requests:
        req=json.loads(path.read_text());rid=req['race_id']
        source_id=req.get('source_execution_id') or req.get('execution_id')
        sources=sorted((root/'runtime/executions'/source_id/'SOURCE').glob('runs/*/source_receipt_envelope.json')) if source_id else []
        source_path=next((p for p in sources if json.loads(p.read_text())['artifact']['source_snapshot_sha256']==req.get('source_snapshot_sha256')),None)
        if source_path is None:
            predictions.append({'race_id':rid,'status':'SOURCE_BINDING_UNRESOLVED'});continue
        if not _verified_source(source_path) or not _attested(source_path,not_after=datetime.fromisoformat(req['prediction_cutoff'])):
            predictions.append({'race_id':rid,'status':'SOURCE_ORIGINAL_CUTOFF_OIDC_UNVERIFIED'});continue
        env=json.loads(source_path.read_text());source=env['artifact']
        proof=build_bvi_consumption(req,mapping,source);counts.update(proof['counts'])
        final_path=root/'runtime/final_artifacts'/f'{rid}.json'
        final=json.loads(final_path.read_text()) if final_path.exists() else None
        final_status='NO_CANONICAL_FINAL'
        if final:
            from jra_delivery import verify_signed_final
            verify_signed_final(final,health,contract)
            if any(final.get(k)!=req.get(k) for k in ('race_id','source_snapshot_sha256','prediction_cutoff')):
                raise ValueError('AUDIT_FINAL_SOURCE_REQUEST_BINDING_MISMATCH:'+rid)
            final_status='CANONICAL_FINAL_SIGNATURE_AND_SOURCE_BINDING_VERIFIED'
        summary={'race_id':rid,'status':'SIGNED_SOURCE_BVI_NUMERICAL_REPLAY_VERIFIED',
                 'source_snapshot_sha256':req['source_snapshot_sha256'],'source_freeze_at':source['source_freeze_at'],
                 'source_path':str(source_path.relative_to(root)),'source_file_sha256':digest(source_path.read_bytes()),
                 'evidence_feature_snapshot_sha256':sha({str(r['runner_id']):r['evidence_features'] for r in req['runners']}),
                 'mapping_version':mapping['mapping_id'],'mapping_content_sha256':sha(mapping),
                 'index_provenance_hash':req.get('index_provenance_hash'),
                 'cutoff':req['prediction_cutoff'],'counts':proof['counts'],'bvi':proof['runners'],
                 'frozen_corpus_manifest':proof['pedigree_corpus_manifest'],
                 'static_proof_status':proof['static_execution_proof_status'],
                 'final_status':final_status,'downstream_artifact_hashes':proof['downstream_artifact_hashes'],
                 'signed_final_at':final['final_receipt']['receipt']['timestamp'] if final else None,
                 'ticket_count':len(final['final_ticket']['tickets']) if final else None,
                 'capital':final['capital_policy_decision']['required_capital'] if final else None,
                 'new_pilot_files_available_before_cutoff':sum(datetime.fromisoformat(a['captured_at'])<=datetime.fromisoformat(req['prediction_cutoff']) for a in artifacts if a['file'] in new_files)}
        predictions.append(summary)
    # Full20 can be valid even when the registered AKI selector correctly
    # stops before PRE_KRS. Do not drop those horses from BVI measurement or
    # mislabel a zero-exposure terminal as a Signed FINAL.
    for path in sorted((root/'runtime/jra_no_bet_terminals').glob(f'*{prediction_date.replace("-","")}*.json')):
        terminal=json.loads(path.read_text());rid=terminal['race_id']
        if rid in {r['race_id'] for r in predictions}:continue
        entry={'race_id':rid,'terminal_file_sha256':digest(path.read_bytes()),'status':'NUMERICAL_NO_BET_NOT_REPLAYED',
               'decision_reason':terminal.get('decision_reason'),'krs_executed':False,'ticket_count':0,'capital':0}
        try:
            if terminal.get('profile')!='KM-JRA-PRODUCTION-AKI-SELECTION-NO-BET-TERMINAL-v1-20261012':
                raise ValueError('NOT_FULL20_AKI_TERMINAL; SEPARATE_EVIDENCE_CLOSURE_REQUIRED')
            from jra_aki_no_bet_terminal import verify_aki_no_bet_terminal
            verification=verify_aki_no_bet_terminal(terminal,race_id=rid,require_live=True,root=root)
            cutoff_time=datetime.fromisoformat(terminal['prediction_cutoff'])
            if not _attested(path,signer='km-jra-formal-single-entry.yml',not_after=cutoff_time):
                raise ValueError('NO_BET_ORIGINAL_CUTOFF_OIDC_UNVERIFIED')
            source_dir=root/'runtime/executions'/terminal['source_execution_id']/'SOURCE'
            sp=next((p for p in source_dir.glob('runs/*/source_receipt_envelope.json')
                     if json.loads(p.read_text())['artifact']['source_snapshot_sha256']==terminal['source_snapshot_sha256']),None)
            if sp is None or not _verified_source(sp) or not _attested(sp,not_after=cutoff_time):
                raise ValueError('NO_BET_SIGNED_SOURCE_ORIGINAL_CUTOFF_UNVERIFIED')
            from copy import deepcopy
            req=deepcopy(terminal['failure_report']['prepared_numerical_request'])
            req['source_snapshot_sha256']=terminal['source_snapshot_sha256']
            source=json.loads(sp.read_text())['artifact'];proof=build_bvi_consumption(req,mapping,source)
            no_bet_counts.update(proof['counts'])
            entry.update(status='SIGNED_SOURCE_AND_OIDC_FULL20_AKI_NO_BET_BVI_REPLAY_VERIFIED',
                source_snapshot_sha256=source['source_snapshot_sha256'],cutoff=terminal['prediction_cutoff'],
                counts=proof['counts'],bvi=proof['runners'],full20_verification=verification,
                static_krs_lineage='REGISTERED_AKI_STOP; NO_KRS_OR_FINAL_CLAIM')
        except (ValueError,KeyError,RuntimeError) as exc:entry['reason']=str(exc)
        no_bet.append(entry)
    # Three real signed SOURCEs, isolated current-data vs held-out inflow; NEVER OOS.
    with tempfile.TemporaryDirectory() as temp:
        before=Path(temp);(before/'runtime/pedigree_corpus').mkdir(parents=True)
        (before/'runtime/executions').symlink_to((root/'runtime/executions').resolve(),target_is_directory=True)
        for p in (root/'runtime/pedigree_corpus').glob('*.json'):
            if p.name not in new_files:(before/'runtime/pedigree_corpus'/p.name).symlink_to(p.resolve())
        previous=build_corpus(before,prediction_cutoff=cutoff,race_date=target_date)
        for venue in ('NGT','TKY','KYO'):
            candidates=[p for p in requests if f'-{venue}-' in p.name]
            if not candidates:continue
            req=json.loads(candidates[-1].read_text());source_id=req.get('source_execution_id') or req.get('execution_id')
            sp=next((p for p in (root/'runtime/executions'/source_id/'SOURCE').glob('runs/*/source_receipt_envelope.json') if json.loads(p.read_text())['artifact']['source_snapshot_sha256']==req['source_snapshot_sha256']),None) if source_id else None
            try:
                if sp is None or not _verified_source(sp) or not _attested(sp,not_after=datetime.fromisoformat(req['prediction_cutoff'])):raise ValueError('DIAGNOSTIC_SIGNED_SOURCE_REQUIRED')
                env=json.loads(sp.read_text());src=env['artifact'];race_day=req['race_date']
                now_pool=build_corpus(root,prediction_cutoff=cutoff,race_date=race_day,exclude_race_id=req['race_id'])
                before_pool=build_corpus(before,prediction_cutoff=cutoff,race_date=race_day,exclude_race_id=req['race_id'])
                compared={}
                for name,pool in [('WITHOUT_NEW_INFLOW',before_pool),('WITH_NEW_INFLOW',now_pool)]:
                    features=owner_authorized_observations(src,registry,corpus=pool)
                    for row in features.values():
                        for key,spec in row.items():
                            if key in PEDIGREE_FEATURES:spec['observed_at']=cutoff
                    cmp=compare(req,mapping,source_sha=src['source_snapshot_sha256'],receipt_sha=env['receipt_sha256'],
                        algorithm_freeze_at=cutoff,cutoff=cutoff,enhanced_features=features,source_artifact=src,current_authority=authority,root=root)
                    compared[name]={}
                    from copy import deepcopy
                    for k,arm in cmp['arms'].items():
                        probe=deepcopy(req);probe.pop('bvi_static_consumption_proof',None)
                        probe['runners']=deepcopy(arm['numerical_runners'])
                        probe['numerical_calculated_at']=arm['numerical_calculated_at']
                        consumption=build_bvi_consumption(probe,mapping,src)
                        compared[name][k]={'bvi':{r:c['value'] for r,c in arm['bvi'].items()},
                            'bvi_counts':consumption['counts'],'postcapture_bvi_contributions':consumption['runners'],
                            'ranking':arm['owner']['static_prediction']['ranking'],'roles':arm['owner']['active_columns'],
                            'krs_input_sha256':sha(arm['krs_input'])}
                diagnostics.append({'race_id':req['race_id'],'status':'POST_CAPTURE_DIAGNOSTIC_ONLY','comparison':compared,
                    'source_snapshot_sha256':src['source_snapshot_sha256'],'original_prediction_cutoff':req['prediction_cutoff'],
                    'diagnostic_cutoff':cutoff,'runner_universe':sorted(str(r['runner_id']) for r in req['runners']),
                    'new_pool_runs':now_pool['run_count'],'old_pool_runs':before_pool['run_count'],
                    'krs_executed':False,'tickets_capital_delta':'NOT_MEASURED_WITHOUT_NEW_EXTERNAL_KRS','forward_oos_increment':0})
            except (ValueError,KeyError,RuntimeError) as exc:
                diagnostics.append({'race_id':req['race_id'],'status':'DIAGNOSTIC_BLOCKED','reason':str(exc),'forward_oos_increment':0})
    score=json.loads((root/'runtime/jra_static_owner_forward_oos/pedigree_pipeline_current.json').read_text())
    day_coverage={}
    for window in windows.values():
        if not window['race_ids']:continue
        key=window['date']+'/'+window['mode']
        d=day_coverage.setdefault(key,{'race_ids':set(),'profiles':0,'profile_targets':0,'prior_run_observations':0,'acquisition_errors':0})
        d['race_ids'].update(window['race_ids'])
        for field in ('profile_targets','prior_run_observations','acquisition_errors'):d[field]+=window[field]
        d['profiles']+=window['horses']
    for d in day_coverage.values():d['race_ids']=sorted(d['race_ids']);d['race_count']=len(d['race_ids'])
    resume={'status':'NO_SIGNED_PLAN_SUPPLIED','actual_windows_verified':0}
    if plan_path:
        plan_path=Path(plan_path)
        if not _attested(plan_path,signer='km-jra-pedigree-corpus-harvest.yml',not_after=now):
            raise ValueError('AUDIT_DAY_PLAN_OIDC_UNVERIFIED')
        from scripts.jra_weekend_bvi_intake import collect_window
        def no_reacquisition(*args,**kwargs):raise ValueError('AUDIT_OFFICIAL_REACQUISITION_FORBIDDEN')
        plan=json.loads(plan_path.read_text());resumed=[]
        for window in plan['include']:
            result=collect_window(window,root,run_id='read-only-verified-resume',collector=no_reacquisition)
            resumed.append({'race_ids':window['race_ids'],'status':result['status']})
        resume={'status':'PASS' if all(x['status']=='ALREADY_VERIFIED_COMPLETE' for x in resumed) else 'PARTIAL',
                'plan_file_sha256':digest(plan_path.read_bytes()),'actual_windows_verified':sum(x['status']=='ALREADY_VERIFIED_COMPLETE' for x in resumed),
                'target_windows':len(resumed),'target_races':sum(len(x['race_ids']) for x in resumed),
                'new_official_http_requests':0,'windows':resumed}
    return {'created_at':cutoff,'prediction_race_date':prediction_date,'target_race_date':target_date,'production_policy_change':'NONE',
        'code_git_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
        'current_authority':authority['manifest_id'],'mapping_version':mapping['mapping_id'],
        'verified_harvest_artifacts':artifacts,'verified_window_count':len(windows),'verified_windows':list(windows.values()),
        'all_race_collection_coverage':day_coverage,
        'raw_horse_observations':len(raw_horses),'unique_composite_horses':len({h for h in raw_horses if h}),
        'parent_nonempty_observations':dict(parent_coverage),'signed_plan_immutable_resume':resume,
        'raw_prior_run_observations':raw_runs,'unique_dedicated_prior_runs':len(runs),
        'valid_prior_run_observations_before_dedup':valid_run_observations,
        'invalid_or_target_future_run_observations':raw_runs-valid_run_observations,
        'duplicate_prior_observations':valid_run_observations-unique_keys_before_conflicts,
        'conflicting_prior_keys_excluded':len(run_conflicts),
        'actual_reader_corpus':{k:corpus[k] for k in ('horse_count','run_count','manifest_sha256','snapshot_count','identity_collision_count','run_conflict_count','source_signature_level')},
        'reader_corpus_without_new_inflow':{k:previous[k] for k in ('horse_count','run_count','manifest_sha256')},
        'permanent_registry_horse_ids':0,'identity_scope':'EXACT_NAME_SIRE_DAM_COMPOSITE; OBSERVED_CNAME_IS_NAVIGATION_ONLY',
        'quality_groups':quality,'quality_scope':'INDEPENDENTLY_OIDC_VERIFIED_JRA_PUBLISHED_HISTORIES; VENUE_FIELD_PRESERVED_INCLUDING_NON_JRA_PAST_RUNS',
        'production_predictions':predictions,'bvi_counts':dict(counts),'inflow_diagnostics':diagnostics,
        'numerical_no_bet_predictions':no_bet,'numerical_no_bet_bvi_counts':dict(no_bet_counts),
        'all_race_bvi_counts':dict(counts+no_bet_counts),
        'forward_oos':score,'future_production_inflow_consumption':'PENDING_OWNER_APPROVAL_AND_NEXT_SIGNED_SOURCE',
        'predictive_improvement_demonstrated':False,'source_trust_note':'Harvest OIDC independently reverified; legacy SOURCE corpus trust follows unchanged Reader authority'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path);p.add_argument('--official-audit',action='store_true');p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--target-date');p.add_argument('--prediction-date');p.add_argument('--plan',type=Path);p.add_argument('--summary-output',type=Path);a=p.parse_args()
    result=official_audit(a.root,target_date=a.target_date,prediction_date=a.prediction_date,plan_path=a.plan) if a.official_audit else inventory(a.root,a.bundle);a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    if a.summary_output:
        from jra_bvi_consumption import sha
        summary={k:v for k,v in result.items() if k not in ('quality_groups','production_predictions','inflow_diagnostics','forward_oos','numerical_no_bet_predictions')}
        summary['numerical_no_bet_predictions']=[{k:v for k,v in row.items() if k!='bvi'} for row in result['numerical_no_bet_predictions']]
        summary['production_predictions']=[{k:v for k,v in row.items() if k not in ('bvi','frozen_corpus_manifest')} for row in result['production_predictions']]
        summary['forward_oos']={k:v for k,v in result['forward_oos'].items() if k in ('status','policy_fingerprint','eligible_settled_races','required_forward_races','automatic_promotion')}
        summary['full_audit_file_sha256']=digest(a.output.read_bytes());summary['sha256']=sha(summary)
        a.summary_output.parent.mkdir(parents=True,exist_ok=True)
        if a.summary_output.exists():raise ValueError('DAILY_AUDIT_SUMMARY_IMMUTABLE')
        a.summary_output.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in (('verified_window_count','raw_horse_observations','unique_composite_horses','unique_dedicated_prior_runs','bvi_counts') if a.official_audit else ('row_count','flat_rows','composite_horse_identities','primary_sources_exact_match','official_corpus_files'))}))

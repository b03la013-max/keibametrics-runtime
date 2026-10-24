"""Read-only reconciliation of private research exports with canonical sources.

Never copies provider rows or credentials into the repository. Counts are not a
Production admission decision; authenticated ingestion remains mandatory.
"""
import argparse,collections,csv,hashlib,io,json,zipfile
import sys,tempfile,urllib.request
from datetime import datetime,timezone,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/jra_source_runtime')]


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


def official_audit(root, *, target_date='2026-10-25', prediction_date='2026-10-24'):
    """Authenticated actual Reader/Compiler audit, not a new Producer or model."""
    from jra_pedigree_corpus import build_corpus,_verified_harvest,_verified_source,_attested,_horse_identity,_clean_runs
    from jra_bvi_consumption import build_bvi_consumption,sha
    from jra_owner_authorized_feature_rules import owner_authorized_observations,class_rank
    from jra_bvi_shadow_comparison import compare,PEDIGREE_FEATURES
    from family_authority_guard import resolve_current_authority
    root=Path(root);now=datetime.now(timezone.utc);cutoff=now.isoformat()
    _,authority=resolve_current_authority(root)
    contracts=json.loads((root/authority['common_family_components']['family_runtime_contracts_profile']).read_text())
    contract=contracts['families']['JRA']
    # Read-only existing trust anchor; never executes a KRS or Production job.
    with urllib.request.urlopen(contract['external_endpoint'].rstrip('/')+'/health',timeout=20) as response:
        health=json.load(response)
    corpus=build_corpus(root,prediction_cutoff=cutoff,race_date=target_date)
    artifacts=[];raw_horses=[];runs={};run_conflicts=set();windows={};valid_run_observations=0
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
            'profile_complete':obj['horse_count']==obj['horse_token_count'],
            'race_ids':[r['race_id'] for r in observed],
            'race_universe_missing':sum(r.get('universe_status')!='OBSERVED_OFFICIAL' for r in observed),
            'navigation_only_horses':sum(bool(h.get('official_profile_navigation_token')) for h in obj['horses']),
            'permanent_horse_ids':sum(bool(h.get('official_permanent_horse_id')) for h in obj['horses'])}
        artifacts.append(artifact)
        previous=windows.get(key)
        if previous is None or (artifact['profile_complete'],len(artifact['race_ids']))>(previous['profile_complete'],len(previous['race_ids'])):windows[key]=artifact
        for h in obj['horses']:
            identity=_horse_identity(h);raw_horses.append(identity)
            for run in _clean_runs(h.get('runs',[]),datetime.fromisoformat(target_date).date()):
                valid_run_observations+=1
                rk=(identity,run['date'],run['venue'],run['surface'],run['distance_m'],run['race_name'])
                fact=(run['finish'],run['field_size'])
                if rk in runs and runs[rk]['fact']!=fact:run_conflicts.add(rk)
                runs.setdefault(rk,{'fact':fact,'sire':h.get('sire'),'damsire':h.get('damsire')})
    unique_keys_before_conflicts=len(runs)
    for key in run_conflicts:runs.pop(key,None)
    raw_runs=sum(a['prior_run_observations'] for a in artifacts)
    groups={}
    for key,value in runs.items():
        identity,day,venue,surface,distance,name=key
        for parent in ('sire','damsire'):
            if not value[parent]:continue
            group=(parent,value[parent],venue,surface,distance,class_rank(name))
            g=groups.setdefault(group,{'offspring':set(),'runs':0,'top3':0})
            g['offspring'].add(identity);g['runs']+=1;g['top3']+=value['fact'][0]<=3
    quality=[{'parent_type':k[0],'parent':k[1],'venue':k[2],'surface':k[3],'distance_m':k[4],
              'class_rank':k[5],'independent_composite_offspring':len(v['offspring']),
              'runs':v['runs'],'top3':v['top3'],'top3_rate':v['top3']/v['runs'],
              'uncertainty':'REPEATED_HORSE_CLUSTERS; NO_INDEPENDENT_RUN_BINOMIAL_ASSUMPTION',
              'going':'NOT_RETAINED_BY_EXISTING_CONSUMER; RAW_SOURCE_RESEARCH_ONLY',
              'model_training_eligible':False,'statistical_advantage':'INSUFFICIENT DATA'}
             for k,v in sorted(groups.items(),key=lambda item:str(item[0]))]
    mapping=json.loads((root/'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json').read_text())
    registry=json.loads((root/'mapping/jra_evidence_feature_rule_registry_v1.3_20261010.json').read_text())
    predictions=[];counts=collections.Counter();diagnostics=[]
    requests=sorted((root/'runtime/requests').glob(f'*{prediction_date.replace("-","")}*FORMAL.json'))
    new_files={a['file'] for a in artifacts if a['date'] in ('2026-10-24','2026-10-25') and a['file']!='20261024-cards-race0-r3.json'}
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
                 'cutoff':req['prediction_cutoff'],'counts':proof['counts'],'bvi':[{'runner_id':r['runner_id'],'value':r['bvi_value'],'class':r['consumption_class']} for r in proof['runners']],
                 'frozen_corpus_manifest':proof['pedigree_corpus_manifest'],
                 'static_proof_status':proof['static_execution_proof_status'],
                 'final_status':final_status,'downstream_artifact_hashes':proof['downstream_artifact_hashes'],
                 'signed_final_at':final['final_receipt']['receipt']['timestamp'] if final else None,
                 'ticket_count':len(final['final_ticket']['tickets']) if final else None,
                 'capital':final['capital_policy_decision']['required_capital'] if final else None,
                 'new_pilot_files_available_before_cutoff':sum(datetime.fromisoformat(a['captured_at'])<=datetime.fromisoformat(req['prediction_cutoff']) for a in artifacts if a['file'] in new_files)}
        predictions.append(summary)
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
                    compared[name]={k:{'bvi':{r:c['value'] for r,c in a['bvi'].items()},
                        'ranking':a['owner']['static_prediction']['ranking'],'roles':a['owner']['active_columns'],
                        'krs_input_sha256':sha(a['krs_input'])} for k,a in cmp['arms'].items()}
                diagnostics.append({'race_id':req['race_id'],'status':'POST_CAPTURE_DIAGNOSTIC_ONLY','comparison':compared,
                    'new_pool_runs':now_pool['run_count'],'old_pool_runs':before_pool['run_count'],
                    'krs_executed':False,'tickets_capital_delta':'NOT_MEASURED_WITHOUT_NEW_EXTERNAL_KRS','forward_oos_increment':0})
            except (ValueError,KeyError,RuntimeError) as exc:
                diagnostics.append({'race_id':req['race_id'],'status':'DIAGNOSTIC_BLOCKED','reason':str(exc),'forward_oos_increment':0})
    score=json.loads((root/'runtime/jra_static_owner_forward_oos/pedigree_pipeline_current.json').read_text())
    return {'created_at':cutoff,'target_race_date':target_date,'production_policy_change':'NONE',
        'verified_harvest_artifacts':artifacts,'verified_window_count':len(windows),'verified_windows':list(windows.values()),
        'raw_horse_observations':len(raw_horses),'unique_composite_horses':len({h for h in raw_horses if h}),
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
        'forward_oos':score,'future_production_inflow_consumption':'PENDING_OWNER_APPROVAL_AND_NEXT_SIGNED_SOURCE',
        'predictive_improvement_demonstrated':False,'source_trust_note':'Harvest OIDC independently reverified; legacy SOURCE corpus trust follows unchanged Reader authority'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path);p.add_argument('--official-audit',action='store_true');p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=official_audit(a.root) if a.official_audit else inventory(a.root,a.bundle);a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in (('verified_window_count','raw_horse_observations','unique_composite_horses','unique_dedicated_prior_runs','bvi_counts') if a.official_audit else ('row_count','flat_rows','composite_horse_identities','primary_sources_exact_match','official_corpus_files'))}))

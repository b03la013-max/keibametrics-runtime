"""Receipt-linked historical predictions; outcome never enters feature extraction."""
import argparse, collections, datetime as dt, hashlib, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[2]

def read(path):
    return json.loads(path.read_text())

def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()

def identity(rid):
    date = re.search(r'20\d{6}', rid)
    race = re.search(r'(?:^|-)R(\d{1,2})(?:-|$)', rid)
    venue = next((v for v in ['TKY','KYO','HSN','NKY','CHK','SPP','NGT','KKR','FKS','HKD',
                            'OHI','FNB','URW','SON','KAW','KOC','SAG','OBI'] if v in rid.split('-')), None)
    if not date or not race or not venue or any(x in rid.upper() for x in ['ACCEPT','TEST','SMOKE','DIAGNOSTIC']):
        return None
    return f'{venue}-{date[0]}-R{int(race[1]):02d}'

def timestamp(s):
    try:
        t = dt.datetime.fromisoformat(str(s).replace('Z','+00:00'))
        return t if t.tzinfo else None
    except ValueError:
        return None

def tickets(rows):
    out={}
    for t in rows or []:
        if t.get('bet_type') not in {'EXACTA','TRIFECTA','TRIO'}: continue
        s=tuple(int(x) for x in t['selection'])
        if t['bet_type']=='TRIO': s=tuple(sorted(s))
        if len(set(s))!=len(s): raise ValueError('duplicate horse in ticket')
        key=(t['bet_type'],s)
        if key in out: raise ValueError('duplicate canonical ticket')
        out[key]={'bet_type':key[0], 'selection':list(s), 'stake':t.get('stake',100),
                  'tier':t.get('mec_tier',t.get('tier','UNKNOWN'))}
    return list(out.values())

def build(root=ROOT):
    finals=[]; results=collections.defaultdict(list); excluded=[]
    def result(path,obj,priority):
        rid=identity(str(obj.get('race_id','')))
        if not rid: return
        rr=obj.get('official_result',obj)
        top=rr.get('top3') or rr.get('finish_order',[])[:3]
        if len(top)!=3: return
        top=[x.get('horse_no',x.get('runner_id',x.get('horse_number'))) if isinstance(x,dict) else x for x in top]
        if any(x is None for x in top): return
        payouts=rr.get('payouts') or {}
        if isinstance(payouts,list): payouts={x.get('bet_type',''):x for x in payouts}
        # A payout may be a scalar or an explicitly keyed 100-yen settlement.
        pay={}
        for k,v in payouts.items():
            if k.upper() not in {'EXACTA','TRIFECTA','TRIO'}: continue
            if isinstance(v,(float,int)): pay[k.upper()]=v
            elif isinstance(v,dict):
                amount=v.get('payout_per_100',v.get('per_100_yen',v.get('payout')))
                if amount is None and len(v)==1 and isinstance(next(iter(v.values())),(int,float)):
                    amount=next(iter(v.values()))
                if amount is not None: pay[k.upper()]=amount
        for w in obj.get('settlement',{}).get('winning_tickets',[]):
            if w.get('payout_per_100') is not None: pay.setdefault(w['bet_type'],w['payout_per_100'])
        results[rid].append({'path':str(path.relative_to(root)), 'top3':list(map(int,top)),
            'payouts':pay, 'priority':priority, 'status':rr.get('status'),
            'verified':bool(obj.get('official_result_verified')) or 'CROSSCHECKED' in str(rr.get('status',''))
                       or str(rr.get('status','')).startswith('OFFICIAL'),
            'final_ref':obj.get('frozen_prediction_ref',{}), 'settlement':obj.get('settlement',{})})
    for folder in ['runtime/results','runtime/source_candidate_results']:
        for path in sorted((root/folder).glob('*.json')): result(path,read(path),90)
    for path in sorted((root/'runtime/executions').rglob('official_result_request.json')):
        result(path,read(path),100)
    for path in sorted((root/'runtime/executions').rglob('result_summary.json')):
        o=read(path);review=o.get('automatic_post_result_review',{})
        o['top3']=review.get('official_top3',[]);o['status']='PERSISTED_SIGNED_RESULT_REVIEW'
        o['official_result_verified']=o.get('verified') is True
        o['frozen_prediction_ref']={'final_receipt_sha256':review.get('final_receipt_sha256')}
        o['payouts']={k:v['wins'][0]['payout_per_100'] for k,v in o.get('by_type',{}).items() if v.get('wins')}
        result(path,o,70)
    for path in sorted((root/'runtime/source_candidate_oos').glob('*/result_evaluation.json')):
        o=read(path); ev=o.get('result_evaluation',{}); o['top3']=ev.get('actual_top3',[])
        o['status']='RESULT_EVALUATION_WITHOUT_INDEPENDENT_OFFICIAL_FLAG';result(path,o,50)

    def final(path,obj,lane,envelope=None,pre=None):
        pre=pre or {}; env=envelope or obj.get('final_receipt',{})
        rid=str(obj.get('race_id') or pre.get('race_id') or env.get('receipt',{}).get('race_id',''))
        key=identity(rid)
        if not key: excluded.append({'path':str(path.relative_to(root)),'reason':'NON_RACE_OR_SYNTHETIC'});return
        package=obj.get('final_prediction_package',{})
        sem=obj.get('candidate_semantic_freeze',{})
        rank=package.get('ranking') or sem.get('ranking') or pre.get('ranking') or []
        roles=package.get('roles') or pre.get('roles') or {}
        if not roles and sem: roles={str(h):[c for c,k in [('W','w_active'),('P2','p2_active'),('P3','p3_active')] if str(h) in list(map(str,sem.get(k,[])))] for h in rank}
        ft=obj.get('final_ticket') or obj.get('mec',{})
        receipt=env.get('receipt',{}); freeze=receipt.get('timestamp') or obj.get('final_freeze_timestamp')
        post=obj.get('scheduled_post_at') or pre.get('scheduled_post_at')
        if not post and (path.parent/'final_before_post_verification.json').exists(): post=read(path.parent/'final_before_post_verification.json').get('scheduled_post_at')
        receipt_sha=env.get('receipt_sha256') or obj.get('final_receipt_sha256')
        verified_hint=False
        verification=path.parent/'receipt_verifications.json'
        if verification.exists(): verified_hint=read(verification).get('FINAL') is True
        if lane=='JRA_CANDIDATE': verified_hint=pre.get('candidate_final_verified') is True
        t0,t1=timestamp(freeze),timestamp(post)
        temporal=bool(t0 and t1 and t0<t1 and receipt.get('status')=='PASS' and env.get('signature'))
        reasons=[]
        if not temporal: reasons.append('MISSING_OR_NON_PRERACE_FINAL_RECEIPT_TIMING')
        if pre.get('acceptance_only') or obj.get('acceptance_only'): reasons.append('ACCEPTANCE_ONLY')
        if not rank or not roles: reasons.append('MISSING_RANKING_OR_ROLES')
        finals.append({'race_key':key,'race_id':rid,'date':key.split('-')[1],'venue':key.split('-')[0],
            'family':'JRA' if lane.startswith('JRA') else 'LOCAL','lane':lane,
            'final_path':str(path.relative_to(root)), 'final_receipt_sha256':receipt_sha,
            'receipt_artifact_sha256':receipt.get('artifact_sha256'),'source_snapshot_sha256':obj.get('source_snapshot_sha256') or pre.get('source_snapshot_sha256'),
            'receipt_verification_record_present':verified_hint, 'freeze_at':freeze,'scheduled_post_at':post,
            'temporal_eligible':temporal and not reasons,'exclusion_reasons':reasons,
            'ranking':list(map(int,rank)), 'roles':{str(h):r for h,r in roles.items()},
            'tickets':tickets(ft.get('tickets',[])), 'capital':obj.get('capital_policy_decision',obj.get('capital',{})),
            'frozen_semantics':{'pairs_count':len(obj.get('pair_dispositions',pre.get('pair_dispositions',[]))),
                                'thirds_count':len(obj.get('third_dispositions',pre.get('third_dispositions',[])))}})
    for path in sorted((root/'runtime/final_artifacts').glob('*.json')): final(path,read(path),'JRA_PRODUCTION')
    for path in sorted((root/'runtime/source_candidate_oos').glob('*/candidate_final.json')):
        prepath=path.parent/'pre_result.json';final(path,read(path),'JRA_CANDIDATE',pre=read(prepath) if prepath.exists() else {})
    for path in sorted((root/'runtime/executions').rglob('final_receipt_envelope.json')):
        env=read(path)
        if env.get('receipt',{}).get('family')!='LOCAL': continue
        final(path,env.get('artifact',{}),'LOCAL_PRODUCTION',env)
    # Prefer the outcome-bound signed revision; retain every alternate in the audit.
    grouped=collections.defaultdict(list)
    for r in finals: grouped[(r['race_key'],r['lane'])].append(r)
    rows=[]
    for (key,lane),versions in sorted(grouped.items()):
        outcomes=sorted(results.get(key,[]),key=lambda x:x['priority'],reverse=True)
        matching=[r for r in versions if any(o.get('final_ref',{}).get('final_receipt_sha256')==r['final_receipt_sha256'] for o in outcomes)]
        choice=sorted(matching or versions,key=lambda r:(r['temporal_eligible'],r['freeze_at'] or ''),reverse=True)[0]
        choice['alternate_final_paths']=[r['final_path'] for r in versions if r is not choice]
        unique={tuple(x['top3']) for x in outcomes}
        choice['outcome_conflict']=len(unique)>1
        choice['outcome']=outcomes[0] if outcomes else None
        if outcomes:
            for o in outcomes[1:]:
                if o['top3']==choice['outcome']['top3']:
                    for k,v in o['payouts'].items(): choice['outcome']['payouts'].setdefault(k,v)
        choice['result_paths']=[o['path'] for o in outcomes]
        if choice['outcome_conflict']: choice['exclusion_reasons'].append('CONFLICTING_RESULTS')
        choice['analysis_eligible']=choice['temporal_eligible'] and bool(outcomes) and not choice['outcome_conflict']
        if not outcomes: choice['exclusion_reasons'].append('RESULT_MISSING')
        rows.append(choice)
    # Numerical features are pulled only from frozen prediction/source objects.
    requests=[]
    for path in sorted((root/'runtime/requests').glob('*.json')):
        o=read(path)
        if o.get('runners') and o['runners'][0].get('canonical_components'): requests.append((path,o))
    for r in rows:
        o=read(root/r['final_path']);scores={};profile=None;feature_path=r['final_path']
        if r['lane']=='JRA_CANDIDATE':
            objective=o.get('candidate_source_objective_shadow',{})
            scores={str(h):v['all_20_diagnostic_values'] for h,v in objective.get('runners',{}).items() if v.get('all_20_diagnostic_values')}
            profile=objective.get('mapping_id')
        elif r['lane']=='JRA_PRODUCTION':
            matches=[(p,q) for p,q in requests if identity(str(q.get('race_id','')))==r['race_key'] and q.get('source_snapshot_sha256')==r['source_snapshot_sha256']]
            if matches:
                p,q=matches[0];scores={str(h['runner_id']):{k:v['value'] for k,v in h['canonical_components'].items()} for h in q['runners']}
                profile=q.get('base_index_mapping_authority',{}).get('mapping_id','JRA_PRODUCTION_FULL20')
                feature_path=str(p.relative_to(root))
        r['frozen_scores']=scores;r['numerical_profile']=profile;r['feature_path']=feature_path
    return {'schema':'KM-HISTORICAL-WIDTH-LEDGER-v1','status':'RESEARCH / NO_PRODUCTION_CHANGE',
            'rows':rows,'synthetic_exclusions':excluded,'duplicate_final_count':len(finals)-len(rows),
            'unmatched_results':sorted(set(results)-{r['race_key'] for r in rows})}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args()
    out=build();pathlib.Path(args.output).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'rows':len(out['rows']),'eligible':sum(r['analysis_eligible'] for r in out['rows']),
        'lanes':dict(collections.Counter((r['lane'],r['analysis_eligible']) for r in out['rows'])) if False else dict(collections.Counter(r['lane'] for r in out['rows'])),
        'exclusions':dict(collections.Counter(x for r in out['rows'] for x in r['exclusion_reasons'])),'unmatched_results':out['unmatched_results']},ensure_ascii=False))

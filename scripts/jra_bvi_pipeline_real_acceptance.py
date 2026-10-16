"""Actual signed SOURCE + official corpus + numerical consumer diagnostics.

Stored historical FINALs are read only. Postcapture B is never forward OOS.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, sys, os, urllib.request
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from jra_pedigree_corpus import _verified_source, _attested, build_corpus
from jra_owner_authorized_feature_rules import owner_authorized_observations
from jra_bvi_shadow_comparison import compare, execute_diagnostic_downstream
from jra_evidence_to_base_production import _weighted_index, _profile_for_runner
from jra_bvi_consumption import build_bvi_consumption
from jra_zero_touch_source_index_orchestrator import build_source_runner_stubs
from family_authority_guard import resolve_current_authority


def sha_file(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def external_call(path, payload, timeout):
    base=os.environ.get('KRS_BASE','https://quorumprobe-production.up.railway.app').rstrip('/')
    rq=urllib.request.Request(base+path,data=json.dumps(payload,ensure_ascii=False).encode(),
        headers={'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(rq,timeout=timeout) as response:
        return json.loads(response.read())


def evaluate():
    now=datetime.now(timezone.utc).isoformat()
    mapping=json.loads((ROOT/'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json').read_text())
    registry=json.loads((ROOT/'mapping/jra_evidence_feature_rule_registry_v1.3_20261010.json').read_text())
    authority_path,authority=resolve_current_authority(ROOT)
    reports=[]
    for no in ('07','12'):
        path=sorted((ROOT/'runtime/requests').glob(f'*KYO-20261011-R{no}*FORMAL.json'))[-1]
        req=json.loads(path.read_text());execution=req['source_execution_id']
        sp=next((ROOT/'runtime/executions'/execution/'SOURCE').rglob('source_receipt_envelope.json'))
        checked=_verified_source(sp)
        if checked is None: raise RuntimeError('REAL_SIGNED_SOURCE_INVALID:'+str(sp))
        env=json.loads(sp.read_text());source=env['artifact']
        if not _attested(sp,not_after=datetime.fromisoformat(req['prediction_cutoff'])):
            raise RuntimeError('REAL_SOURCE_OIDC_ORIGINAL_CUTOFF_NOT_VERIFIED')
        if req['source_snapshot_sha256']!=checked['source_snapshot_sha256']:
            raise RuntimeError('FORMAL_SOURCE_SHA_MISMATCH')
        card={str(x.get('runner_id') or x.get('horse_no')):x for x in source['jra_official_race_card_detail']['runners']}
        if set(card)!={str(x['runner_id']) for x in req['runners']}: raise RuntimeError('RUNNER_UNIVERSE_MISMATCH')
        corpus=build_corpus(ROOT,prediction_cutoff=now,race_date=req['race_date'],exclude_race_id=req['race_id'],
            required_sires={x.get('sire') for x in card.values() if x.get('sire')},
            required_damsires={x.get('damsire') for x in card.values() if x.get('damsire')})
        if not any(x.startswith('ATTESTED_HARVEST:') for x in corpus['snapshots']):
            raise RuntimeError('ACTUAL_OIDC_CORPUS_NOT_CONSUMED')
        enriched=owner_authorized_observations(source,registry,corpus=corpus)
        comparison=compare(req,mapping,source_sha=checked['source_snapshot_sha256'],receipt_sha=env['receipt_sha256'],
            algorithm_freeze_at=req['static_freeze_timestamp'],cutoff=req['prediction_cutoff'],enhanced_features=enriched,
            source_artifact=source,current_authority=authority,root=ROOT)
        a=comparison['arms']['A_CURRENT']; b=comparison['arms']['B_PEDIGREE_ENHANCED_SHADOW'];c=comparison['arms']['C_BLOODLINE_ABLATION']
        rows=[]
        for r in req['runners']:
            rid=str(r['runner_id']);base=req['index_provenance_ledger']['runners'][rid]['base_indices']['BVI']
            if abs(a['bvi'][rid]['value']-base['value'])>1e-6:raise RuntimeError('STORED_REAL_BVI_REPLAY_MISMATCH:'+rid)
            if r['name']!=card[rid]['horse_name']:raise RuntimeError('RUNNER_NAME_MISMATCH:'+rid)
            rows.append({'runner_id':rid,'name':r['name'],'sire':card[rid].get('sire'),'dam':card[rid].get('dam'),
                'damsire':card[rid].get('damsire'),'frozen_bvi':base,'postcapture_bvi':b['bvi'][rid],
                'ablation_bvi':c['bvi'][rid]})
        finalpath=ROOT/'runtime/final_artifacts'/f"{req['race_id']}.json"
        final=json.loads(finalpath.read_text());result=json.loads((ROOT/'runtime/results'/f"{req['race_id']}.json").read_text())
        top3=[str(x) for x in result['official_result']['top3']]
        execute_diagnostic_downstream(comparison,req,result['official_result'],external_call)
        for arm in comparison['arms'].values():
            owner=arm['owner'];ranking=owner['static_prediction']['ranking'];cols=owner['active_columns']
            for rank_row in arm['krs_result_utility']['rank_comparison']:
                if rank_row['static_role_hit']!=(str(rank_row['horse']) in cols[rank_row['role']]):
                    raise RuntimeError('REAL_KRS_STATIC_ROLE_LINEAGE_MISMATCH')
            arm['historical_diagnostic_metrics']={'winner_rank':ranking.index(top3[0])+1,
                'winner_discovery':top3[0] in cols['W'],'p2_capture':top3[1] in cols['P2'],'p3_capture':top3[2] in cols['P3'],
                'top3_mean_rank':sum(ranking.index(x)+1 for x in top3)/3,
                'ordered_pair_capture':any(x['head']==top3[0] and x['second']==top3[1] for x in owner['pair_dispositions']),
                'exact_semantic_capture':any((x['head'],x['second'],x['third'])==tuple(top3) for x in owner['third_dispositions'])}
        reports.append({'race_id':req['race_id'],'classification':'POST-CAPTURE DIAGNOSTIC / NOT FORWARD OOS',
            'source_path':str(sp.relative_to(ROOT)),'source_file_sha256':sha_file(sp),'source_snapshot_sha256':checked['source_snapshot_sha256'],
            'original_source_freeze_at':source['source_freeze_at'],'original_prediction_cutoff':req['prediction_cutoff'],
            'diagnostic_created_at':now,
            'diagnostic_current_authority':authority['manifest_id'],
            'diagnostic_authority_effective_at':authority['effective_at'],
            'authority_use':'CURRENT POLICY COUNTERFACTUAL ONLY; NOT HISTORICAL PRE-CUTOFF AUTHORITY',
            'mapping_id':mapping['mapping_id'],'mapping_file_sha256':sha_file(ROOT/'mapping/jra_base_index_evidence_mapping_v1.0_20260921.json'),
            'postcapture_corpus':{k:corpus.get(k) for k in ('manifest_sha256','horse_count','run_count','snapshot_count','identity_collision_count','run_conflict_count','snapshots','rejected_untrusted_inputs')},
            'bvi_consumption_ledger':build_bvi_consumption(req,mapping,source_artifact=source),
            'runners':rows,'comparison':comparison,'frozen_lineage':{'request_sha256':sha_file(path),
                'final_sha256':sha_file(finalpath),'source_binding_matches':final['source_snapshot_sha256']==checked['source_snapshot_sha256'],
                'static_prediction':final['static_prediction'],'krs_run_receipt':final['krs_run_receipt'],
                'minimum_efficient_coverage':final['minimum_efficient_coverage'],'capital_policy_decision':final['capital_policy_decision'],
                'final_ticket':final['final_ticket']},'production_rewritten':False,'forward_oos_increment':0})
    # R08 did not reach a formal FINAL. Its postcapture BVI is not closure.
    r08path=next((ROOT/'runtime/executions/KM-JRA-KYO-20261011-R08-LIVE-R1/SOURCE').rglob('source_receipt_envelope.json'))
    r08checked=_verified_source(r08path)
    if r08checked is None: raise RuntimeError('KYO_R08_SOURCE_SIGNATURE_INVALID')
    r08env=json.loads(r08path.read_text()); r08source=r08env['artifact']
    if not _attested(r08path,not_after=datetime.fromisoformat(r08source['prediction_cutoff'])):
        raise RuntimeError('KYO_R08_SOURCE_OIDC_CUTOFF_UNVERIFIED')
    r08corpus=build_corpus(ROOT,prediction_cutoff=now,race_date='2026-10-11',exclude_race_id=r08source['race_id'])
    r08features=owner_authorized_observations(r08source,registry,corpus=r08corpus)
    r08rows=[]
    for r in build_source_runner_stubs(r08source):
        try:
            cell=_weighted_index('BVI',_profile_for_runner(r),r08features.get(r['runner_id'],{}),mapping)
            r08rows.append({'runner_id':r['runner_id'],'name':r['name'],'postcapture_bvi':cell})
        except ValueError as exc:
            r08rows.append({'runner_id':r['runner_id'],'name':r['name'],'blocked':str(exc)})
    r08={'race_id':r08source['race_id'],'classification':'POST-CAPTURE DIAGNOSTIC / NOT FORWARD OOS',
        'source_snapshot_sha256':r08checked['source_snapshot_sha256'],'source_freeze_at':r08source['source_freeze_at'],
        'prediction_cutoff':r08source['prediction_cutoff'],'runners':r08rows,
        'formal_closure':'BLOCKED / HISTORICAL EVIDENCE_NO_BET; NO FROZEN FORMAL REQUEST',
        'corpus_manifest_sha256':r08corpus['manifest_sha256'],
        'corpus_horse_count':r08corpus['horse_count'],'corpus_run_count':r08corpus['run_count'],
        'corpus_snapshots':r08corpus['snapshots'],
        'corpus_run_identity_hashes':sorted({hashlib.sha256(json.dumps(
            [h['horse_name'],h['sire'],h['dam'],r['date'],r['venue'],r['surface'],r.get('distance_m'),r['race_name']],
            ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
            for h in r08corpus['horses'].values() for r in h['runs'].values()}),
        'static_krs_ticket_lineage':'NOT ESTABLISHED',
        'historical_prediction_rewritten':False}
    report={'created_at':now,'reports':reports,'kyoto_r08':r08,'gate_c':'FORWARD OOS PENDING','policy_change':'NONE'}
    from pfs_grand_review import _aggregate, _robustness
    pooled={}
    for name in reports[0]['comparison']['arms']:
        samples=[]
        for r in reports:
            settlement=r['comparison']['arms'][name]['diagnostic_virtual_settlement']
            samples.append({'race_id':r['race_id'],'date':'2026-10-11',
                'investment':settlement['investment'],'return':settlement['return'],
                'profit_loss':settlement['profit_loss'],
                'hit_but_loss':bool(settlement['return'] and settlement['profit_loss']<0)})
        pooled[name]={'aggregate':_aggregate(samples),'robustness':_robustness(samples),
            'classification':'2-RACE POSTCAPTURE VIRTUAL DIAGNOSTIC / NO FORWARD OOS / INSUFFICIENT EVIDENCE'}
    report['diagnostic_pooled_pfs']=pooled
    out=ROOT/'runtime_out/jra_bvi_pipeline_real_acceptance.json';out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('REAL_BVI_PIPELINE_ACCEPTANCE='+json.dumps({'races':[r['race_id'] for r in reports],
        'runners':sum(len(r['runners']) for r in reports),'gate_c':report['gate_c'],'output':str(out)}))
    return report

if __name__=='__main__':evaluate()

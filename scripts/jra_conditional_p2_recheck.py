"""Recheck merged311 findings; frozen research residual, no Production writes."""
import json, sys, math, hashlib, statistics
from collections import Counter, defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'runtime'), str(ROOT/'scripts'), str(ROOT/'research/jra_conditional_rank')]
from jra_prediction_quality_audit import records
from jra_probability_readiness_audit import aggregate
from probability_shadow import scores, distribution, measures, conditional_nll, instant, sha
from head_p2_shadow import fit_interaction, predict, POLICY
from jra_pedigree_corpus import _horse_identity


def corpus_inventory(directory):
    groups = defaultdict(list)
    counts = Counter()
    file_refs, parents, identities = [], defaultdict(set), set()
    for path in sorted(directory.glob('*.json')):
        obj = json.loads(path.read_text())
        counts['files'] += 1
        unsigned = {k:v for k,v in obj.items() if k != 'sha256'}
        valid = obj.get('sha256') == hashlib.sha256(json.dumps(unsigned, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        counts['content_hash_valid_files'] += valid
        counts['declared_official_files'] += obj.get('official') is True and obj.get('source') == 'www.jra.go.jp'
        file_refs.append({'path':str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else path.name,
                          'file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'declared_sha256':obj.get('sha256'),
                          'content_hash_valid':valid, 'harvested_at':obj.get('harvested_at')})
        for horse in obj.get('horses', []):
            counts['horse_observations'] += 1
            identity = _horse_identity(horse)
            counts['missing_pedigree_identity_observations'] += identity is None
            counts['missing_permanent_horse_id_observations'] += not bool(horse.get('horse_id'))
            counts['missing_sire_id_observations'] += not bool(horse.get('sire_id'))
            counts['missing_damsire_id_observations'] += not bool(horse.get('damsire_id'))
            counts['missing_raw_sha_observations'] += not bool(horse.get('raw_sha256'))
            if identity:
                identities.add(identity)
                parents[identity].add(horse.get('damsire'))
            for run in horse.get('runs', []):
                counts['run_observations'] += 1
                for field in ('race_id', 'date', 'venue', 'surface', 'distance_m', 'going', 'race_name'):
                    counts['missing_'+field+'_run_observations'] += not bool(run.get(field))
                finish, n = run.get('finish'), run.get('field_size')
                valid_label = type(finish) is int and type(n) is int and 1 <= finish <= n and n >= 2
                counts['valid_finish_labels_observations'] += valid_label
                if identity and valid_label:
                    # Audit-only surrogate grouping, never certified official race identity.
                    key = (identity, run.get('date'), run.get('venue'), run.get('race_name'), run.get('surface'), run.get('distance_m'))
                    groups[key].append((finish, n, run.get('going')))
    conflicts = sum(len(set(v)) > 1 for v in groups.values())
    counts['surrogate_unique_horse_run_groups'] = len(groups)
    counts['repeated_surrogate_observations'] = sum(len(v)-1 for v in groups.values())
    counts['conflicting_surrogate_label_or_going_groups'] = conflicts
    counts['pedigree_triple_identities'] = len(identities)
    counts['conflicting_damsire_for_triple_identities'] = sum(len(v) > 1 for v in parents.values())
    return {'counts':dict(counts), 'files':file_refs, 'hierarchical_fit':'BLOCKED',
            'official_identity_complete_verified_samples':0,
            'oidc_attestations_reverified':'NOT_PERFORMED; file hash/official flag is not attestation',
            'surrogate_dedup_scope':'name/sire/dam + date/venue/race_name/surface/distance; NOT permanent horse/race ID',
            'recovery':['Recover permanent horse/sire/damsire and official race IDs from eligible raw official sources',
                        'Resolve conflicting duplicate labels/going and preserve original observations',
                        'Verify workflow attestation/source timestamps; then build pre-cutoff horse×race rows',
                        'Count independent offspring and date/venue/surface/distance/going/class cells before partial pooling'],
            'production_admission':False, 'unaccepted_408_imported':False}


def summary(rows, field):
    return {role:aggregate([r[field][role] for r in rows]) for role in ('W','P2','P3')}


def pair_metrics(d, actual):
    pair = max(((h,s) for h in d['head_p2'] for s in d['head_p2'][h]),
               key=lambda hs:(d['marginals']['W'][hs[0]]*d['head_p2'][hs[0]][hs[1]], -int(hs[0]), -int(hs[1])))
    exact = max(d['ordered_joint'], key=lambda k:(d['ordered_joint'][k], tuple(-int(h) for h in k.split('>'))))
    return {'conditional_p2':measures(d['head_p2'][actual[0]], actual[1]),
            'pair_nll':-math.log(d['marginals']['W'][actual[0]])-math.log(d['head_p2'][actual[0]][actual[1]]),
            'exact_nll':-math.log(d['ordered_joint']['>'.join(actual)]),
            'pair_capture':list(pair)==actual[:2], 'exact_capture':exact.split('>')==actual,
            'top1_pair':list(pair),'top1_exact':exact.split('>')}


def run():
    data = records()
    base = json.loads((ROOT/'research/jra_conditional_rank/probability_candidate.json').read_text())
    train = [r for r in data if r['race_id'] in {m['race_id'] for m in base['rank_model']['training_manifest']}]
    cal = [r for r in data if r['race_id'] in {m['race_id'] for m in base['calibration_manifest']}]
    test = [r for r in data if r['day']=='20261018']
    assert (len(train),len(cal),len(test)) == (19,22,36)
    interaction = fit_interaction(train, base)
    output = ROOT/'research/jra_conditional_rank/head_p2_candidate.json'
    output.write_text(json.dumps(interaction, ensure_ascii=False, sort_keys=True, indent=2)+'\n')
    rows = []
    for cohort, subset in [('calibration',cal),('evaluation',test)]:
        for row in subset:
            sc = scores(row['runners'], base['rank_model']); actual = row['top3']
            unit = distribution(sc, dict(W=1.,P2=1.,P3=1.))
            mapped = distribution(sc, base['temperatures'])
            w_only = distribution(sc, dict(W=base['temperatures']['W'],P2=1.,P3=1.))
            rowout = {'race_id':row['race_id'], 'venue':row['venue'], 'cohort':cohort,
                      'no_bet_no_final':row['no_bet'], 'actual_top3':actual,
                      'source_sha256':row['q'].get('source_snapshot_sha256'),
                      'request_sha256':sha(row['q']),
                      'unit':{r:measures(unit['marginals'][r], actual[i]) for i,r in enumerate(('W','P2','P3'))},
                      'mapped':{r:measures(mapped['marginals'][r], actual[i]) for i,r in enumerate(('W','P2','P3'))},
                      'unit_conditional_nll':conditional_nll(sc, actual,dict(W=1.,P2=1.,P3=1.)),
                      'mapped_conditional_nll':conditional_nll(sc, actual,base['temperatures']),
                      'p2_w_temperature_only_nll':measures(w_only['marginals']['P2'],actual[1])['log_loss']}
            if cohort == 'evaluation':
                new = predict(row['runners'],base,interaction)
                rowout.update(unit_pair=pair_metrics(unit,actual),interaction_pair=pair_metrics(new,actual),
                              interaction={r:measures(new['marginals'][r],actual[i]) for i,r in enumerate(('W','P2','P3'))},
                              interaction_missing_evidence=new['missing_evidence'],
                              interaction_input_sha256=new['evidence_input_sha256'])
            rows.append(rowout)
    formal = [r for r in rows if r['cohort']=='evaluation' and not r['no_bet_no_final']]
    calibration = [r for r in rows if r['cohort']=='calibration']
    def compare_rows(rs):
        return {field:summary(rs,field) for field in ('unit','mapped')}
    comparison = {cohort:compare_rows(rs) for cohort,rs in [('calibration',calibration),('evaluation_formal',formal)]}
    context = {}
    for field in ('unit_pair','interaction_pair'):
        context[field] = {'oracle_actual_head_p2':aggregate([r[field]['conditional_p2'] for r in formal]),
                          'pair_nll':statistics.mean(r[field]['pair_nll'] for r in formal),
                          'exact_nll':statistics.mean(r[field]['exact_nll'] for r in formal),
                          'top1_pair_capture':sum(r[field]['pair_capture'] for r in formal),
                          'top1_exact_capture':sum(r[field]['exact_capture'] for r in formal), 'denominator':len(formal)}
    prior = json.loads((ROOT/'evidence/jra_p0_20261018/PREDICTIVE_STRUCTURE_AUDIT.json').read_text())
    funded = [r for r in prior['races'] if r['class']=='FUNDED_FINAL']
    risks = [r['risk_diagnostics'] for r in funded]
    plans = {}
    for day in ('2026-10-24','2026-10-25'):
        path=ROOT/'runtime/jra_race_day_plan'/(day+'.json');obj=json.loads(path.read_text())
        plans[day]={'file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'planned_target_count':len(obj['forward_oos_preregistration']['targets']),
                    'plan_modified':False,'new_candidate_registered':False}
    report = {'profile':'JRA-311-INTEGRATION-CONDITIONAL-P2-RECHECK-20261018',
              'integration':{'approved_head':'cf24befbc8ab466e30fcc73e3affa5a95697d8c4','merge_sha':'39a86b7e1fa3bc4874d78619a9194fd4c2cdf7f1',
                             'approved_and_merged_tree':'721a4cbf035d33633d160f224a89afe6cce60184','main_ci_successful_checks':5,
                             'new_followup_merge':False,'deployment_performed':False,'production_effect':'NONE'},
              'runtime_read_only_observation':{'observed_at':'2026-10-18T11:58:53.014740+00:00','health_http_status':200,'status':'READY',
                 'service':'quorumprobe','deployment_id':'7c7eeb5e-3b5b-496a-b66f-82bd71897d53','deployment_status':'SUCCESS','staged_changes':False,
                 'engine_sha256':'9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421',
                 'parameter_sha256':'75cc9d0e8b15de0e95bbfd76d9ed4425fa6b9076d022d1a9c6b5bc812fa3dedc',
                 'signer_key_id':'KM-RUNTIME-ED25519-20260917','deployment_git_sha':'UNVERIFIED','saved_command_process_binding':'UNVERIFIED',
                 'pr305_isolated_startup_rollback':'UNRESOLVED_NOT_RETRIED'},
              'base_model_sha256':base['sha256'],'interaction_model_sha256':interaction['sha256'],
              'design':'POST_RESULT_EXPLORATION_NOT_FORWARD_OOS; fixed4 interactions/L2/step/iterations; no test-driven choice',
              'calibration_comparison':comparison,
              'venue_calibration_comparison':{v:compare_rows([r for r in formal if r['venue']==v]) for v in ('TKY','KYO','NGT')},
              'root_cause_checks':{'p2_temperature_is_unit':base['temperatures']['P2']==1.,
                  'max_p2_mapped_vs_w_only_nll_difference':max(abs(r['mapped']['P2']['log_loss']-r['p2_w_temperature_only_nll']) for r in formal),
                  'w_lost_target_probability_races':sum(r['mapped']['W']['log_loss']>r['unit']['W']['log_loss'] for r in formal),
                  'conditional_vs_marginal_objective':'Temperatures selected conditional on actual earlier finishers; marginal test sums unknown heads/pairs',
                  'adoption':'REJECT_PROMOTION; keep existing uncalibrated frozen rank arm, no new calibration method'},
              'interaction':{'policy':POLICY,'coefficients':interaction['weights'],'context_metrics':context,
                             'marginal_metrics':{k:summary(formal,k) for k in ('unit','interaction')},
                             'limitations':['19 context labels/4 residual coefficients; no Niigata training',
                                            'position/pace-resilience/closing/course categories are proxies, not simulated pace or raw running style',
                                            'P3 conditional scores unchanged; marginal effects arise only through head/P2 probabilities',
                                            'No tickets, new capital, calibrated probability claim, Production connection or automatic selection']},
              'aki':{'inherited_exploratory_confusion_matrices':prior['aki_detection'],
                     'evidence_flagged_races':sum(bool(r['flags']['evidence']) for r in risks),
                     'funded_count':len(risks),'ood_test_score_range':[min(r['ood_score'] for r in risks),max(r['ood_score'] for r in risks)],
                     'verdict':'No detected arithmetic error in confusion matrix or conformal order. Evidence rule too broad/shared; race-mean OOD not error classifier; no Production gate',
                     'future_detection_validated':False},
              'bvi_corpus':corpus_inventory(ROOT/'runtime/pedigree_corpus'),
              'sampling':prior['selection_bias'],'temporal_split':prior['data_split'],
              'future':{'plans':plans,'genuine_oos_freezes':0,'verified_new_learning_next_race_consumption':0,
                        'new_candidate_runtime_connection':False,'new_arm_activation':False,
                        'existing_approved_arms_only':True,'unknown_future_accuracy':'PENDING',
                        'required':['official numbered field/cutoff','same Source/universe/cutoff','independent pre-cutoff content/code/policy persistence',
                                    'Learning effective time before target input; ON/OFF actual rank/role/ticket difference',
                                    'same-budget/point comparison and post-result settlement; no fee/purchase/notification']},
              'races':rows}
    report['code_sha256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ('scripts/jra_conditional_p2_recheck.py','research/jra_conditional_rank/head_p2_shadow.py')}
    report['sha256']=sha(report)
    (ROOT/'evidence/jra_p0_20261018/CONDITIONAL_P2_RECHECK.json').write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'context':context,'root_cause':report['root_cause_checks'],'bvi_counts':report['bvi_corpus']['counts'],'plans':plans},ensure_ascii=False))


if __name__ == '__main__':
    run()

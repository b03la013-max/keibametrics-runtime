"""Render the day audit and review-only next-race learning; no activation."""
import csv, hashlib, json, statistics, sys
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'scripts')]
from jra_full_day_postrace_review import read,write,sha,BASE,DERIVED,dt
from post_result_learning import build_learning_state

DAY='2026-10-17';OUT=ROOT/'runtime/daily_reviews'/('JRA-'+DAY)

def md_table(headers,rows):
    return '| '+' | '.join(headers)+' |\n|'+'|'.join(['---']*len(headers))+'|\n'+''.join('| '+' | '.join(str(x).replace('|','/') for x in r)+' |\n' for r in rows)

def render():
    ledger=read(OUT/'audit_ledger.json');s=ledger['summary'];rows=ledger['races'];byid={r['race_id']:r for r in rows}
    now=s['generated_at'];ex=s['execution'];pfs=s['production_frozen_recommendation'];pred=s['prediction']
    candidates=read(OUT/'alternative_lane_summary.json');cells=list(csv.DictReader((OUT/'full20_cells.csv').open()))
    ranks=read(OUT/'numerical_discrimination.json');tickets=read(OUT/'ticket_settlement.json')
    states=[];score=[]
    krsrows=[r for r in rows if r['krs']];semantic_krsrows=[r for r in krsrows if r['krs'].get('semantic_evaluation_eligible')];bviro=[r for r in rows if r['bvi']]
    bvicounts=Counter();
    for r in bviro:bvicounts.update(r['bvi'].get('counts',{}))
    bvi_inputs=Counter()
    for r in rows:bvi_inputs.update(r.get('bvi_frozen_input_inventory',{}).get('counts',{}))
    # Inspect actual frozen A/B/C diagnostics; A is a shadow comparator, not a
    # second Production execution even when it uses the current numerical rules.
    abc=[]
    for r in rows:
        path=ROOT/'runtime/jra_static_owner_forward_oos'/r['race_id']/'pre_result.json';pre=read(path,{})
        comp=pre.get('pedigree_comparison',{})
        if comp:
            arms=comp.get('arms',{})
            abc.append({'race_id':r['race_id'],'path':str(path.relative_to(ROOT)),'frozen_at':pre.get('frozen_at'),
                'pre_post':bool(pre.get('frozen_at') and dt(pre['frozen_at'])<dt(r['post'])),
                'enhanced_input_supplied':comp.get('enhanced_input_supplied'),
                'enhanced_bvi_distinct':comp.get('enhanced_bvi_distinct'),
                'enhanced_ranking_distinct':comp.get('enhanced_ranking_distinct'),
                'A_B_same_bvi':(arms.get('A_CURRENT',{}).get('bvi')==arms.get('B_PEDIGREE_ENHANCED_SHADOW',{}).get('bvi')),
                'production_effect':comp.get('production_effect'),'status':comp.get('status'),
                'predictive_improvement_demonstrated':False})
    krssummary={'eligible_races':len(krsrows),'signed_actual_runs':sum(r['krs']['execution_receipt']['actual_run_count'] for r in krsrows),
        'raw_output_hash_verified':sum(r['krs']['raw_output_sha_verified']=='PASS' for r in krsrows),
        'unique_actionable_role_rescues':sum(len(r['krs']['unique_actionable_role_rescues']) for r in krsrows),
        'false_actionable_role_proposals':sum(len(r['krs']['false_positive_actionable_role_proposals']) for r in krsrows),
        'semantic_evaluable_races':len(semantic_krsrows),'dead_heat_semantic_pending':len(krsrows)-len(semantic_krsrows),
        'role_zone_unique_rescues':sum(r['krs']['utility']['unique_rescue_role_count'] for r in semantic_krsrows),
        'role_zone_unique_harms':sum(r['krs']['utility']['unique_harm_role_count'] for r in semantic_krsrows),
        'production_unique_rescue_to_ticket':0,'production_harm':0,
        'legacy_summary_role_binding_mismatch_races':sum(r['krs']['legacy_summary_role_binding_mismatch']>0 for r in krsrows),
        'input_payload_hash_independently_matched':sum(bool(r['krs'].get('input_hash_comparison',{}).get('match')) for r in krsrows),
        'role_rescue_by_role':dict(Counter(p['proposal'] for r in krsrows for p in r['krs']['unique_actionable_role_rescues'])),
        'role_zone_comparison':'Use immutable FINAL static roles and frozen SSR-W / SSR-P2 / SSR-T3 ranks. Zone widths differ by role; not probabilities.',
        'notice':'No Shadow proposal retrospectively becomes a Production ticket. Raw engine input serialization contract not independently resolved.'}
    # Detailed scorecard retains all 36 and separate unexecuted versus unknown.
    for r in rows:
        pr=r['prediction'];st=r['settlement'] or {};aki=r['aki'] or {};kr=r['krs'] or {};nr=r['numerical'];failure=r['first_material_failure']
        score.append({'race_id':r['race_id'],'venue':r['venue'],'race_no':r['race_no'],'status':r['observed_status']['state'],
            **{k:'VERIFIED' if v else 'NOT VERIFIED' if k in ('Delivery','Learning') else 'NOT EXECUTED / NOT VERIFIED' for k,v in r['execution'].items()},
            'formal_grade':r['formal_grade'],'temporal_eligibility':r['temporal_eligibility'],
            'race_time_authority':r['authority']['race_time_manifest'],'source_git_sha':r['authority']['source_git_sha'],
            'result_top3':(' / '.join(f"finish{rank}:"+','.join(str(h['horse_no']) for h in r['official_result']['runners'] if h['finish']==rank) for rank in sorted({h['finish'] for h in r['official_result']['runners'] if h['horse_no'] in r['official_result']['top3']})) if r['official_result'].get('top3_display_order_is_not_unique') else '>'.join(map(str,r['official_result']['top3']))) if r['official_result'] else 'UNKNOWN',
            **{k:pr[k] if pr and pr[k] is not None else 'PENDING DEAD HEAT' if pr else 'NOT EXECUTED' for k in ['winner_rank','W','P2','P3','ordered_pair','ordered_exact','candidate_width']},
            **{k:aki.get('axes',{}).get(k,'NOT EXECUTED' if not aki else 'UNKNOWN') for k in ['W-AKI','P2-AKI','P3-AKI','ASI','RSI']},
            'krs_actual_runs':kr.get('execution_receipt',{}).get('actual_run_count','NOT EXECUTED'),
            'krs_actionable_unique_rescue_count':len(kr.get('unique_actionable_role_rescues',[])) if kr.get('semantic_evaluation_eligible') else 'PENDING DEAD HEAT' if kr else 'NOT EXECUTED',
            'krs_potential_role_zone_harm':kr.get('utility',{}).get('unique_harm_role_count') if kr.get('semantic_evaluation_eligible') else 'PENDING DEAD HEAT' if kr else 'NOT EXECUTED',
            'ticket_counts':json.dumps(dict(Counter(t['bet_type'] for t in st.get('tickets',[])))) if st else 'NOT EXECUTED',
            'required_capital':(r['authority'].get('capital_policy') or {}).get('required_capital','NOT EXECUTED') if isinstance(r['authority'].get('capital_policy'),dict) else 'NOT EXECUTED',
            'capital_decision':(r['authority'].get('capital_policy') or {}).get('decision','NOT EXECUTED') if isinstance(r['authority'].get('capital_policy'),dict) else 'NOT EXECUTED',
            'investment':st.get('investment','NOT EXECUTED'),'return':st.get('return','PENDING' if st else 'NOT EXECUTED'),
            'pfs':st.get('pfs','PENDING') if st and st.get('investment')!=0 else 'NOT APPLICABLE (ZERO INVESTMENT)' if st else 'NOT EXECUTED',
            'first_material_failure':failure['classification'],'dominant_pfs_loss_owner':'UNDETERMINED',
            'learning_recorded':r['verification']['learning']['recorded'],'learning_hash_verified':r['verification']['learning']['hash_verified'],
            'learning_delivered':'NOT VERIFIED','actual_purchase':'NOT VERIFIED'})
        original=read(ROOT/'runtime/learning_states'/f"{r['race_id']}.json",{})
        review={'race_id':r['race_id'],'sha256':sha(r),'failure_localization':{'first_material_failure':failure['classification']},
            'pfs_improvement':{'test_next_tracks':[],'learning_routes':['REPAIR_NOW' if failure['repair_type']=='CORRECTNESS' else 'TEST_NEXT' if pr else 'DO_NOT_CHANGE'],
                              'no_stagnation_satisfied':True,'dominant_pfs_loss_owner':{'owner':'UNDETERMINED'}}}
        state=build_learning_state(review)
        state.update({'state_id':r['race_id']+'-DAY-AUDIT-20261017-NEXT','status':'REVIEW-RECORDED / NOT ACTIVATED / NEXT-RACE-ONLY',
            'original_learning_ref':r['artifact_refs']['learning'],'original_learning_hash_verified':r['verification']['learning']['hash_verified'],
            'result_verification':{'official':bool(r['official_result']),'signed_result':r['verification']['result_receipt']['status']},
            'first_material_failure':failure,'dominant_pfs_loss_owner':r['dominant_pfs_loss_owner'],
            'numerical_discrimination_ref':'runtime/daily_reviews/JRA-2026-10-17/numerical_discrimination.json',
            'winner_p2_p3_error':{role:(not pr[role]) if pr and isinstance(pr[role],bool) else 'PENDING ADJUDICATION' if pr else 'NOT EXECUTED' for role in ['W','P2','P3']},
            'aki_error':(r['aki'] or {}).get('captures','NOT EXECUTED'),
            'krs_rescue_harm':{k:kr.get('utility',{}).get(k,'NOT EXECUTED') for k in ['rescues','unique_rescue_role_count','unique_harm_role_count']},
            'semantic_ticket_loss':r.get('semantic_conversion','NOT EXECUTED'),'capital_efficiency':{k:st.get(k,'NOT EXECUTED') for k in ['investment','return','pfs']},
            'runtime_issue':r.get('execution_failure_detail','NO OBSERVED PRE-FINAL FAILURE'),
            'correctness_repair_candidate':failure['classification'] if failure['repair_type']=='CORRECTNESS' else 'NONE',
            'predictive_hypothesis':'H-WINNER / H-P2 / H-KRS / H-CAPITAL; see forward_oos_plan.json' if pr else 'NONE',
            'learning_validity':'FAMILY-CANDIDATE','fact_validity':'RACE-LOCAL; same-day going expired before next meeting',
            'effective_time':now,'next_eligible_race':'First JRA race whose source freeze is after effective_time and whose Owner-approved lane accepts this state; earliest 2026-10-18',
            'delivery':'NOT VERIFIED','production_change_authorized':False})
        state['sha256']=sha({k:v for k,v in state.items() if k!='sha256'})
        write(ROOT/'runtime/learning_states/jra_day_review_20261017'/f"{r['race_id']}.json",state);states.append(state)
    with (OUT/'scorecard.csv').open('w',newline='') as fh:
        writer=csv.DictWriter(fh,fieldnames=list(score[0]),lineterminator='\n');writer.writeheader();writer.writerows(score)
    write(OUT/'krs_incremental_utility.json',krssummary)
    write(OUT/'bvi_consumption_review.json',{'races_with_consumption_ledger':len(bviro),'counts':dict(bvicounts),'frozen_numerical_input_counts':dict(bvi_inputs),
        'race_counts':{r['race_id']:r['bvi']['counts'] for r in bviro},
        'official_corpus_vs_admission':'Existing admitted corpus references only; research408 remains unadmitted and unused by this review.',
        'A_B_C':abc,'A_equals_B_count':sum(a['A_B_same_bvi'] for a in abc),
        'predictive_incremental_improvement':'NOT DEMONSTRATED; shadow diagnostics are not Production performance or causal effect.'})
    failures=[r for r in rows if not r['execution']['Signed_FINAL']]
    backlog=[]
    def item(priority,key,group,owner,affected,evidence,change,regression,oos,action):
        backlog.append({'priority':priority,'id':key,'route':group,'owner':owner,'affected_race_ids':affected,
            'affected_race_count':len(affected),'observed_evidence':evidence,'root_cause_or_hypothesis':change,
            'expected_benefit_hypothesis':'Prevent the observed failure or improve measured capture/capital; no guaranteed profit estimate.',
            'required_change':change,'production_policy_impact':'NONE in this review; predictive changes Shadow only',
            'regression_requirement':regression,'forward_oos_requirement':oos,'promotion_requirement':'Current Authority + Owner exact-head approval; no auto-promotion',
            'next_action':action})
    runtimefails=[r['race_id'] for r in failures if r['observed_status']['state']=='FORMAL_FAILED']
    item('P0','R-BVI-BINDING','REPAIR_NOW','Runtime',runtimefails,'Six actual Formal traceback excerpts: BVI_STATIC_PROOF_BINDING_INVALID',
        'Verify merged binding repair against immutable failed requests and future Formal path. Do not recalculate or late-final these races.',
        'Actual six requests; source/runner/owner hashes; mutation rejection; full normal pipeline','Future eligible race completion',
        'Existing fix must be checked on latest main; do not duplicate; live acceptance remains separate')
    item('P0','R-DISPATCH','REPAIR_NOW','Runtime',['KM-JRA-TKY-20261017-R05'],
        'Run38993239193: status readback imports jra_production_postresult without runtime on sys.path; persistence failed',
        'Ensure all status readback entry points resolve imports and never block independent race dispatch',
        'Same subprocess environment, status writer failure, other race continuation','Future eligible Intake/Delivery','Use existing import-path repair; verify deployment workflow SHA')
    item('P0','R-RESOLVER','REPAIR_NOW','Runtime',['KM-JRA-TKY-20261017-R08'],
        'Run39000908421 official POST reset; DISPATCHED_RUNNING residue, now terminal deadline exceeded',
        'Preserve bounded official-only retry and completion-by-path reconciliation already merged in PR303/304',
        'Reset then success, 429/503, permanent4xx, deadline, duplicate, status recovery','Next eligible race + before-post signed FINAL and Delivery',
        'Do not re-execute expired R8; live acceptance pending')
    item('P0','R-KRS-MEASUREMENT','REPAIR_NOW','Measurement',[r['race_id'] for r in krsrows if r['krs']['legacy_summary_role_binding_mismatch']],
        'Actual utility.summary.static_roles=[] disagrees with immutable FINAL. P3 evaluator used SSR-P3 while proposal selection uses SSR-T3.',
        'Bind summary to resolved frozen roles and align P3 diagnostic metric; legacy audit explicitly supplies frozen roles. Preserve signed originals.',
        'KYO11 confirmations cannot become unique rescue; distinct P3/T3; existing utility regression','Measurement correction only, no new predictive OOS claim',
        'Implemented in this PR; Owner review/merge pending')
    item('P0','P-DELIVERY','PROCESS_IMPROVEMENT','Runtime',[r['race_id'] for r in rows if r['execution']['Signed_FINAL']],
        '23 canonical publications and availability receipts; zero user receipt ACK',
        'Separate availability, notification and arrival; require real delivery evidence without silently enabling external sends',
        'Exact frozen tickets, PAPER zero, renderer failure, no duplicate sends','Future user-arrival proof','Coordinate existing open PR302; no external message sent')
    for key,group,owner,affected,mechanism in [
        ('H-WINNER','TEST_NEXT','JRA Family',[r['race_id'] for r in rows if r['prediction'] and not r['prediction']['W']], 'Winner re-audit from observed pace/position/closing; never unconditional width expansion'),
        ('H-P2','TEST_NEXT','JRA Family',[r['race_id'] for r in rows if r['prediction'] and r['prediction']['W'] and not r['prediction']['P2']], 'Independent head-local P2 and winner migration; then pair-conditioned third/order'),
        ('H-AKI','TEST_NEXT','JRA Family',[r['race_id'] for r in failures if r['first_material_failure']['classification']=='AKI PAIR INFEASIBILITY'], 'Column sharpness and distinct P2 feasibility, preserve current fail-closed'),
        ('H-KRS','TEST_NEXT','JRA Family',[r['race_id'] for r in krsrows if r['krs']['unique_actionable_role_rescues']], 'Test frozen unique proposals against Static at equal width and capital'),
        ('H-BVI','TEST_NEXT','JRA Family',[r['race_id'] for r in bviro], 'Admitted measured pedigree vs ablation; enhanced B must actually differ before utility claim'),
        ('H-CAPITAL','TEST_NEXT','Family Common',[r['race_id'] for r in rows if r['settlement'] and r['settlement'].get('investment',0)>0], 'Selective capital versus current MEC; current CORE return zero, protection contains only win; protect true-positive control'),
        ('P-RESULT','PROCESS_IMPROVEMENT','Runtime',[r['race_id'] for r in rows if r['verification']['result_receipt']['status']!='SIGNATURE_VERIFIED'], 'Persist original RESULT envelopes and learning readback; do not resign lost historical receipts')]:
        item('P1' if key in ('H-WINNER','H-P2','P-RESULT') else 'P2',key,group,owner,affected,mechanism,mechanism,
             'Frozen positive controls, same source/cutoff/universe; no candidate leakage','Pre-registered forward paired OOS; multi-day; current promotion gate','Prepare Shadow protocol; Owner authorization before runtime activation')
    item('P2','D-FREEZE','DO_NOT_CHANGE','Family Common',[],
        'Single-day correlated sample and no prospectively validated new mechanism',
        'Keep Base/Derived/BVI/AKI/KRS physics/MEC/Capital frozen; keep research408 isolated',
        'Policy files and signed artifact trees unchanged','No automatic promotion at 30 races','PROMOTION_REVIEW only after current gates and Owner review')
    write(OUT/'improvement_backlog.json',backlog)
    hypotheses=[]
    for b in backlog:
        if b['route']!='TEST_NEXT':continue
        hypotheses.append({'hypothesis_id':b['id'],'target_failure':b['root_cause_or_hypothesis'],'owner':b['owner'],
            'pre_race_evidence':'Same signed SOURCE, runner universe, official histories/pedigree/market timestamp and frozen Full20; no target result',
            'production_change':False,'comparison':'Paired same-race Current Production, Static-only, Static+KRS, Current AKI vs candidate, Current MEC vs selective Shadow; BVI A/B/C eligible only',
            'primary_metric':'Winner/P2/Exact capture at fixed candidate width' if b['id'] not in ('H-CAPITAL','H-BVI') else 'Weighted and largest-win-excluded PFS at same budget' if b['id']=='H-CAPITAL' else 'Paired winner-rank and role capture gain with distinct pre-frozen B input',
            'negative_control':'Unchanged-input arm must reproduce current frozen output; KYO11 trio positive control; B=A yields zero added-information claim',
            'false_positive_cost':'Additional false role/pair/third count, tickets and yen tracked; no silent zero cost',
            'required_capital_impact':'0 actual yen (Shadow); report hypothetical added exposure and matched-budget arm separately',
            'forward_oos_conditions':'After preregistration hash and Owner-approved activation time; same cutoff/source/universe/results; group by day and venue; no Oct17 reuse as unknown future',
            'keep_condition':'Current Authority promotion gate, paired primary improvement, robust PFS/drawdown and positive-control preservation all pass; Owner decision',
            'reject_condition':'Leakage, absent/hash-only output, post-cutoff freeze, width-only apparent gain, control harm or nonpositive prespecified paired utility',
            'numeric_thresholds':'PENDING preregistration/Owner review; not optimized on Oct17',
            'promotion':'No automatic promotion at sample count30; retain all failures and abstentions'})
    plan={'profile':'KM-FAMILY-POSTRESULT-CLOSED-LOOP-v1.0-20260921','created_at':now,'status':'PROPOSED / NOT ACTIVATED',
        'eligible_start':'After Owner-approved preregistration; earliest JRA2026-10-18, no past race reclassification',
        'hypotheses':hypotheses,'statistical_plan':'Race-level paired differences; day/meeting clusters; report samples, width, false positives, capital and uncertainty. Oct17 exploratory only.',
        'metric_manifest':['Winner Rank','W/P2/P3 Capture','Ordered Pair/Exact','same-cutoff market gain','candidate/false-positive width','KRS unique rescue/harm','semantic coverage','tickets','investment','return','PFS','Robust PFS','drawdown','hit-but-loss','NO-BET opportunity cost'],
        'promotion_gate':'Resolved Family authority JRA krs_oos_promotion_gate + common owner_pfs_promotion_gate; exact thresholds inherited and not replaced',
        'automatic_activation':False,'production_policy_change':False}
    write(OUT/'forward_oos_plan.json',plan);write(OUT/'next_race_learning_index.json',{'effective_time':now,'states':[{'race_id':x['race_id'],'sha256':x['sha256'],'path':'runtime/learning_states/jra_day_review_20261017/'+x['race_id']+'.json'} for x in states],
        'recorded':36,'signed_or_consumed_by_next_race':'NOT VERIFIED','original_learning_states_unchanged':True})
    grades={'DATA REVIEW':'COMPLETE','PREDICTION REVIEW':'PARTIAL','CAPITAL / PFS REVIEW':'COMPLETE','LEARNING REVIEW':'PARTIAL'}
    completion={'population':'COMPLETE','official_results':'COMPLETE','official_payouts':'COMPLETE','frozen_artifact_inventory':'COMPLETE',
        'missing_artifacts':'COMPLETE','full20_inventory':'COMPLETE (34 executed; 2 NOT EXECUTED)',
        'prediction_role_order_23':'COMPLETE','aki_review':'COMPLETE','krs_execution_output_and_proposals':'COMPLETE','krs_exact_input_hash_serialization':'BLOCKED',
        'bvi_consumption':'PARTIAL (ledger coverage explicit)','bvi_causal_incremental_value':'BLOCKED (no distinct eligible new prospective contrast)',
        'all_frozen_tickets_settled':'COMPLETE','bet_type_pfs':'COMPLETE','robust_pfs':'COMPLETE','hit_but_loss':'COMPLETE',
        'dominant_causal_pfs_loss_owner':'BLOCKED (no frozen controlled loss decomposition)',
        'execution_36':'COMPLETE','first_failed_stage':'PARTIAL (six actual logs and focused incidents verified; unexecuted stages explicit)',
        'delivery_rate':'COMPLETE (0 verified; absence is not proof of non-arrival)',
        'signed_result_and_learning_receipts':'PARTIAL','learning_consumption':'BLOCKED','correctness_backlog':'COMPLETE',
        'shadow_hypotheses':'COMPLETE (proposed, not activated)','venue_canon_revision':'HOLD','learning_states':'PARTIAL (recorded review revision, not delivered)',
        'runtime_deployment_git_sha':'BLOCKED','race_time_venue_canon_fingerprints':'BLOCKED'}
    write(OUT/'completion.json',{'review_grades':grades,'items':completion,'verdict':{'formal_execution':'SEVERE FAILURE','prediction':'FAILURE','capital_efficiency':'SEVERE FAILURE','learning':'MIXED'},
        'venue_canon_revision':{'TKY':'HOLD','KYO':'HOLD','NGT':'HOLD'},'reasons':'Common failures first; no multi-day frozen venue-specific OOS mechanism proven. No venue coefficient change.'})
    ptable=md_table(['指標','Production推薦','PAPER','全Signed FINAL（参考）'],[[k,
        f"{s['prediction_by_lane']['PRODUCTION'][k]['numerator']}/{s['prediction_by_lane']['PRODUCTION'][k]['denominator']}",
        f"{s['prediction_by_lane']['PAPER'][k]['numerator']}/{s['prediction_by_lane']['PAPER'][k]['denominator']}",
        f"{v['numerator']}/{v['denominator']} ({100*v['rate']:.2f}%)"] for k,v in pred.items()])
    etable=md_table(['Stage','件数 / 36'],[[k,f"{v['numerator']}/36"] for k,v in ex.items()])
    vtable=md_table(['Venue','投資','払戻','損益','PFS'],[[k,v['investment'],v['return'],v['profit_loss'],f"{v['weighted_pfs']:.2f}%"] for k,v in s['per_venue'].items()])
    btable=md_table(['券種','点数','投資','払戻','PFS'],[[k,v['ticket_count'],v['investment'],v['return'],f"{v['pfs']:.2f}%"] for k,v in s['per_bet_type'].items()])
    ftable=md_table(['分類','Race数'],s['first_material_failures'].items())
    lines=[f'# JRA {DAY} Daily Formal Review',f'監査時刻 {now}。Git snapshot `{s["git_snapshot"]}`、Status snapshot {s["status_snapshot_at"]}。対象36、公式結果36/36、払戻7券種36/36。',
        '正式FINAL23件と、未成立13件を分離。PAPER4件はFINAL23に含む。Execution障害8件、AKI Pair不成立3件、正式AKI NO-BET2件。失敗Raceへ仮想Production券面を作成していない。',
        '## 実行',etable,
        '## 予測',ptable,f'勝ち馬平均Static順位 {s["winner_mean_rank"]:.3f}。市場相対順位差 {s["market_relative_mean_winner_rank_gain"]:.3f}（正=改善。同じSigned SOURCEに保存された発走前の公式人気との比較。最終人気の診断はRace別に分離）。',
        'Winner捕捉4件はいずれも正解P2を落とし、Ordered Pair/Exactは0件。京都12Rは2着同着のためP2/P3/Order指標と着順別KRS診断はPENDING、該当分母から除外。公式複数払戻に基づく全券精算は完了。候補Role集合のTop3捕捉を着順識別成功と扱わない。京都11RはW外の勝ち馬が三連複保護券に含まれた的中であり、Winner識別成功ではない。',
        '## AKI / KRS / BVI',f'AKI Pair不成立は新潟2R・京都1R・京都3R。現行PolicyのFail-Closedを維持。過圧縮・過拡張の因果責任は比較基準なしに断定しない。KRS実行23件、計{krssummary["signed_actual_runs"]:,}回、raw output hash検証{krssummary["raw_output_hash_verified"]}/23。',
        f'KRSのUnique actionable Role Rescue {krssummary["unique_actionable_role_rescues"]}件、false-positive Role提案{krssummary["false_actionable_role_proposals"]}件。Role-zone比較Rescue {krssummary["role_zone_unique_rescues"]}、潜在Harm {krssummary["role_zone_unique_harms"]}。いずれもShadow評価。正式TicketへのRescue変換0、Productionへの削除Harm0。',
        f'旧Utility summaryのStatic Role結合不整合は{krssummary["legacy_summary_role_binding_mismatch_races"]}/23件。凍結FINALのRoleとSSR-T3を使って今回の診断を訂正し、旧署名Artifact/既存Learningは保持。Engine入力SHAの実際のシリアライズ規約は未解決で、入力hash独立一致をPASSとしない。',
        f'消費Ledger {len(bviro)}/34実行Race。MEASURED {bvicounts.get("MEASURED",0)}頭、MEASURED_PLUS_DCR {bvicounts.get("MEASURED_PLUS_DCR",0)}頭、DCR_ONLY {bvicounts.get("DCR_ONLY",0)}頭。34件の凍結数値入力での分類は {dict(bvi_inputs)}（下流消費の成立とは分離）。A/B/C凍結診断{len(abc)}件、BVIのA=B {sum(a["A_B_same_bvi"] for a in abc)}件。追加情報の改善実証なし。研究408走は隔離。',
        '既存BVI伝播LedgerではBVI scalarはTPIへ直接、SRI/F3S/T3Iへ間接に入るが、ZAI_WIN/ZAI_PLACEへの直接項はない。血統Featureが他指数へ入る共有効果と、BVI単独scalarの寄与を混同しない。A/C差は未知未来の精度改善証明ではない。',
        '## Capital / PFS',f'正式推薦の全336券を再精算。投資{pfs["investment"]:,}円、払戻{pfs["return"]:,}円、損益{pfs["profit_loss"]:,}円、加重PFS {pfs["weighted_pfs"]:.4f}%。実購入NOT VERIFIED。PAPER0円のPFS=null。',vtable,btable,
        f'払戻は京都11Rの三連複9,100円だけ。最大払戻依存100%、同Raceを投資ごと除外するとPFS0%。Top2/Top3除外も0%。最大DD {pfs["max_drawdown_yen"]:,}円、最大無払戻連続{pfs["max_zero_return_streak"]}Race（有投資Race、発走順）。Hit-but-Lossは0件。的中1件は利益6,200円。',
        'CORE投資23,400円・払戻0円。PROTECTION投資10,200円・払戻9,100円。CORE_ONLYへの事後短縮は当日の唯一の払戻を失うため、成功したSelective Capitalとは評価できない。負けRaceの点数を減らすだけではWinner Discoveryは改善しない。',
        '## Failure',ftable,
        '東京3Rを含む初期6件はSOURCE後のBVI Static proof bindingで停止。東京5RはStatus読戻しimport失敗が受付を妨げた。東京8Rは公式HTTPS resetとResolver終了のStatus未伝播。期限切れの回復FINALは作成していない。失敗Raceの機会損失は8回の正式実行機会であり、架空の投資損失へ金額化しない。',
        '## 再利用できる成功と限界',
        '34件のSigned SOURCEと全馬20指数の保存、23件の発走前Signed FINAL・同一券面公開を確認。PAPER情報Gate4件とAKI Fail-Closed5件は資金曝露を抑止した。これらは実行/安全制御の証拠であり、新しい予測法則の成功証明ではない。京都11Rの保護三連複は正のRegression Controlとして保持する。',
        '## 次Race / Canon',
        '次Raceへ渡すのは既存仕様のCorrectness課題、証拠不足、Shadow仮説と比較計画。10月17日の結果由来Learningを既に発走したRaceへ遡及適用しない。同日馬場情報は翌日の固定Featureへ持ち越さず、新たな公式SOURCEで再取得。東京・京都・新潟のCanon改定はすべてHOLD。',
        'Production Base/Derived/BVI/AKI閾値/KRS Physics/parameter_map/MEC/Capitalは維持。添付候補文書を現行本番Canonへ昇格しない。Runtime Deployment Git SHA、Race-time Venue Canonの独立Fingerprint、SOURCE OIDC bundle、購入/受領/次Race消費は未確認。',
        '## 完了判定',md_table(['段階','判定'],grades.items()),md_table(['軸','評価'],[('Formal','SEVERE FAILURE'),('Prediction','FAILURE'),('Capital','SEVERE FAILURE'),('Learning','MIXED')]),
        '全体完了とはしない。公式全件取得と精算は完成、Predictionの一部Authority/入力証明・Learningの署名依存/Deliveryは未完。詳細はcompletion.jsonとmissing_artifacts.json。']
    (OUT/'daily_formal_review.md').write_text('\n\n'.join(lines)+'\n')
    (OUT/'pfs_grand_review.md').write_text('# PFS Grand Review — JRA 2026-10-17\n\n推薦馬券の仮想精算。Actual PurchaseはNOT VERIFIED。\n\n'+vtable+'\n'+btable+'\n'+md_table(['Lane','Race数','投資','払戻','PFS'],[[k,v['race_count'],v['investment'],v['return'],f"{v['weighted_pfs']:.3f}%" if v['weighted_pfs'] is not None else 'null'] for k,v in candidates.items()])+f'\nProduction {pfs["investment"]}/{pfs["return"]}、PFS {pfs["weighted_pfs"]:.4f}%。Candidate6件・Shadow各23件は別集団、Productionや36Race母数へ足さない。Candidateの高投資券面は正式購入ではない。\n\n最大払戻除外はRaceごと投資/払戻の両方を除外。Top2以降は同払戻0のRaceを発走時刻、Race IDで固定選択する。除外対象と分子/分母はsummary.jsonに保存。\n')
    (OUT/'improvement_backlog.md').write_text('# Improvement Backlog\n\n'+md_table(['Priority','ID','Route','Owner','Race数','次Action'],[[b['priority'],b['id'],b['route'],b['owner'],b['affected_race_count'],b['next_action']] for b in backlog])+'\n詳細のEvidence/Regression/OOS/Promotion条件はimprovement_backlog.json。Production activation・Merge・通知送信は実施しない。\n')
    (OUT/'next_race_learning_oos.md').write_text('# Next-Race Learning / Forward OOS\n\n'+f'Effective time {now}。既存helperで36件のreview revisionを既存learning_states配下のday namespaceに保存。既存トップレベルLearning/署名SOURCE/FINAL/RESULTは変更していない。次Raceへの消費・署名・DeliveryはNOT VERIFIED。\n\n'+md_table(['仮説','Owner','Primary Metric','Production'],[[h['hypothesis_id'],h['owner'],h['primary_metric'],'変更なし / Shadow proposed'] for h in hypotheses])+'\n同じRace/Cutoff/Source/Runner Universe/結果集合、同予算・同点数を別比較として事前固定。各Negative Control、false-positive費用、Keep/Reject条件はforward_oos_plan.json。数値閾値の事後最適化なし、サンプル30のみで昇格なし。Owner審査前の自動実行なし。\n')
    (OUT/'README.md').write_text('# JRA 2026-10-17 全36Race監査\n\n'+md_table(['成果物','正本'],[
        ('A 全36Race Ledger','audit_ledger.json / scorecard.csv / races/*.json'),('B Daily Formal Review','daily_formal_review.md'),
        ('C PFS Grand Review','pfs_grand_review.md / runtime/pfs_grand_review/JRA-2026-10-17.json / ticket_settlement.json'),
        ('D Improvement Backlog','improvement_backlog.md / .json'),('E Next-Race Learning / OOS','next_race_learning_oos.md / forward_oos_plan.json / next_race_learning_index.json'),
        ('Full20','full20_cells.csv / numerical_discrimination.json'),('AKI / Prediction / Semantic','races/*.json'),
        ('KRS','krs_incremental_utility.json / evidence/jra_day_review_20261017/krs_checkpoints'),
        ('BVI','bvi_consumption_review.json'),('欠落 / 出典 / 完了','missing_artifacts.json / input_manifest.json / completion.json')])+
        '\n再現: `python scripts/jra_full_day_postrace_review.py --date 2026-10-17`、続いて `python scripts/render_jra_day_review.py`。収集は `scripts/collect_jra_day_review.py`（既存JRA公式専用retry client、read-only POST）。raw decoded HTML、取得時刻、POST tokenとSHA256、元Artifactパスを保持。\n\n'+
        'DATA COMPLETE / PREDICTION PARTIAL / CAPITAL COMPLETE / LEARNING PARTIAL。Analysis-only。Production数値Policy・署名済みArtifact・元Learningの書換えなし。\n\n'+
        '詳細なRace別JSON、全馬20指数CSV、公式HTML、Actions原KRS/RESULT出力は `evidence/jra_day_review_20261017/payload.tar.gz` に元bytesを保存。`payload_manifest.json` のSHA256と `python scripts/unpack_jra_day_review.py` で検証・展開する。展開後、上記2コマンドで集計を再現する。元のProduction署名ファイルは置換しない。\n')
    # Focused summaries reference the single per-race ledger, rather than
    # inventing duplicate authoritative prediction artifacts.
    for name,keys in [('prediction_utility_summary',['prediction','numerical','semantic_conversion']),('aki_performance_review',['aki','execution_failure_detail']),
                      ('mec_capital_review',['semantic_conversion','settlement','alternative_lanes']),('execution_failure_review',['execution','execution_failure_detail','workflow_results','verification'])]:
        write(OUT/(name+'.json'),{'source':'audit_ledger.json','races':[{ 'race_id':r['race_id'],**{k:r.get(k,'UNKNOWN') for k in keys}} for r in rows]})
    print(json.dumps({'grades':grades,'krs':krssummary,'bvi':dict(bvicounts),'ABC':len(abc),'AB_equal':sum(a['A_B_same_bvi'] for a in abc)},ensure_ascii=False,indent=2))

if __name__=='__main__':render()

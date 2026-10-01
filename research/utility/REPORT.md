# KeibaMetrics Family — Phase B execution report

## A. Evidence Coverage Matrix

判定対象は最新mainに保存されたSOURCE。一般的な取得可能性を実取得と混同しない。AvailabilityとAuthorityは別軸。

|Evidence|Availability|Authority / use|Binding|
|---|---|---|---|
|Official race card|AVAILABLE|PRODUCTION-AUTHORIZED|SOURCE race_card_tables|
|Runner universe|AVAILABLE|PRODUCTION-AUTHORIZED|Frozen official runner universe|
|Horse history|PARTIAL|SHADOW-ONLY|card recent starts, profile; broader history gaps retained|
|Class|PARTIAL|SHADOW-ONLY|class descriptors need contextual translation|
|Venue|AVAILABLE|PRODUCTION-AUTHORIZED|request/source|
|Distance|AVAILABLE|PRODUCTION-AUTHORIZED|request/source|
|Going|AVAILABLE|PRODUCTION-AUTHORIZED|track_condition|
|Weather|AVAILABLE|PRODUCTION-AUTHORIZED|weather|
|Body weight|PARTIAL|SHADOW-ONLY|observed current weight; not readiness proof|
|Body weight change|PARTIAL|SHADOW-ONLY|source observed change|
|Jockey|AVAILABLE|PRODUCTION-AUTHORIZED|card identity; skill mapping separate|
|Trainer|AVAILABLE|PRODUCTION-AUTHORIZED|card identity; intent unobserved|
|Official odds|PARTIAL|PRODUCTION-AUTHORIZED|odds_tables; cannot assert full exotic market snapshot|
|Same-day results|AVAILABLE|PRODUCTION-AUTHORIZED|only earlier races in frozen SOURCE|
|Same-day condition|PARTIAL|SHADOW-ONLY|condition observed; causal bias inference separate|
|Pedigree seed|PARTIAL|SHADOW-ONLY|existing auxiliary; no new numerical score|
|SBO public|PARTIAL|SHADOW-ONLY|existing auxiliary, not primary fact authority|
|Training|MISSING|SHADOW-ONLY|no verified pre-result observation|
|Trainer comments|MISSING|SHADOW-ONLY|no verified pre-result observation|
|Paddock|MISSING|SHADOW-ONLY|no verified pre-result observation|
|Layoff interval|PARTIAL|SHADOW-ONLY|derived from dated starts; full history not assumed|
|Transfer history|PARTIAL|SHADOW-ONLY|venue transition observable, transfer cause inferred|
|Corner / passing order|AVAILABLE|SHADOW-ONLY|separate official corner table now parsed; 33/33 R12 prior-race Top3|
|Pace / progression|PARTIAL|SHADOW-ONLY|corner intervals structured; lap times retained, no fitted cost|

## B. Missing / Partial Evidence Map

FNB9/30既知11レースをDevelopmentとしてのみ再計算。R1の対応canonical FORMAL保存が見つからず、12レース完備とは宣言しない。重複retryは同じLATEST runを再計上しない。結果表の馬別corner欄が空でも別表に公式隊列があった。別表を利用する修正後、R12の先行11レースTop3はcorner33/33、従来0/33。括弧内集団はrank_min/rank_maxを保持し、集団内順序を捏造しない。馬体重、休養、転入をtraining/paddockの代理観測としない。

## C. 63 Numerical Rule Closure Matrix

ProductionはNOT_READY、required63 / bound0。既存v0.1 Candidateの63規則を再利用し、新bonus・weight・thresholdなし。Candidate BOUNDはProduction READYと異なる。欠測由来52等の既存中立値の輸送を維持しながら、RULED-NEUTRALをCALCULATEDから除外。KRS研究bridgeはnumeric_transport_completeを参照し、計算済み偽装によって接続しない。以下のholdはCandidate不正入力の隔離でありLIVE停止権ではない。

|Index|Component / semantic feature|Existing numerical transform|Missing rule|Candidate calculated / neutral|
|---|---|---|---|---|
|HPI-L|recent_finish|RECENCY_WEIGHTED_NORMALIZED_FINISH|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|HPI-L|finish_margin|RECENCY_WEIGHTED_EXPONENTIAL_MARGIN|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|HPI-L|passing_position_content|RECENCY_WEIGHTED_LAST_CORNER_REACH_AND_PROGRESS|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|HPI-L|class_level|RECENCY_WEIGHTED_CLASS_ORDINAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|HPI-L|opponent_strength|RECENCY_WEIGHTED_CLASS_AND_FIELD_STRENGTH|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|HPI-L|repeatability|RECENT_PERFORMANCE_STABILITY|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|118 / 1|
|CFIg-L|same_venue|MATCHED_VENUE_PERFORMANCE_WITH_COVERAGE|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|97 / 22|
|CFIg-L|same_distance|MATCHED_DISTANCE_PERFORMANCE_WITH_COVERAGE|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|96 / 23|
|CFIg-L|similar_distance|SIMILAR_DISTANCE_PERFORMANCE_WITH_COVERAGE|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|113 / 6|
|CFIg-L|course_geometry|DIRECTION_SURFACE_GEOMETRY_MATCH_WITH_PERFORMANCE|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|117 / 2|
|CFIg-L|turn_direction|DIRECTION_MATCH_RATE_WITH_PERFORMANCE|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|117 / 2|
|CFIg-L|draw_style_fit|DRAW_BY_EARLY_POSITION_INTERACTION_OR_CANONICAL_NEUTRAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|CFIg-L|going_fit|GOING_GROUP_MATCHED_PERFORMANCE_WITH_COVERAGE|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|110 / 9|
|RFIg-L|running_style_repro|EARLY_POSITION_STYLE_STABILITY|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|118 / 1|
|RFIg-L|position_acquisition|NORMALIZED_FIRST_CALL_POSITION|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|RFIg-L|position_maintenance|EARLY_TO_LATE_POSITION_RETENTION|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|RFIg-L|third_corner_progression|EARLY_TO_THIRD_CALL_PROGRESS|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|RFIg-L|leadership_stalk_acceptance|TOP3_EARLY_OR_STALK_SUCCESS_RATE|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|79 / 40|
|RFIg-L|kickback_traffic_tolerance|NON_FRONT_RUN_PERFORMANCE_OR_CANONICAL_NEUTRAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|109 / 10|
|RFIg-L|going_adaptation|WET_DRY_MATCHED_POSITION_PERFORMANCE|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|110 / 9|
|RFIg-L|jockey_reproducibility|CURRENT_JOCKEY_RECENT_HORSE_REPRODUCIBILITY|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|82 / 37|
|BVIg-L|sire_fit|OFFICIAL_PEDIGREE_POPULATION_FIT_OR_CANONICAL_NEUTRAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|0 / 119|
|BVIg-L|damsire_fit|OFFICIAL_PEDIGREE_POPULATION_FIT_OR_CANONICAL_NEUTRAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|0 / 119|
|BVIg-L|distance_sustain|OFFICIAL_PEDIGREE_DISTANCE_SUSTAIN_OR_CANONICAL_NEUTRAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|0 / 119|
|BVIg-L|distance_trait|OFFICIAL_PEDIGREE_DISTANCE_TRAIT_OR_CANONICAL_NEUTRAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|0 / 119|
|BVIg-L|surface_sand_fit|OFFICIAL_PEDIGREE_DIRT_FIT_OR_CANONICAL_NEUTRAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|0 / 119|
|BVIg-L|venue_stat|OFFICIAL_PEDIGREE_VENUE_STAT_OR_CANONICAL_NEUTRAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|0 / 119|
|BVIg-L|physical_style_fit|PEDIGREE_PHYSICAL_STYLE_FIT_OR_CANONICAL_NEUTRAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|0 / 119|
|JTI-L|venue_recent|CURRENT_JOCKEY_ON_HORSE_VENUE_PERFORMANCE|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|65 / 54|
|JTI-L|distance_record|CURRENT_JOCKEY_ON_HORSE_DISTANCE_PERFORMANCE|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|61 / 58|
|JTI-L|stable_combo|CURRENT_JOCKEY_STABLE_COMBO_SOURCE_OR_CANONICAL_NEUTRAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|0 / 119|
|JTI-L|position_acquisition_skill|CURRENT_JOCKEY_ON_HORSE_FIRST_CALL_QUALITY|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|82 / 37|
|JTI-L|progression_timing_skill|CURRENT_JOCKEY_ON_HORSE_PROGRESS_QUALITY|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|82 / 37|
|JTI-L|favorite_reliability|CURRENT_JOCKEY_ON_HORSE_POPULAR_RUN_RELIABILITY|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|46 / 73|
|JTI-L|longshot_record|CURRENT_JOCKEY_ON_HORSE_LONGSHOT_RUN_PERFORMANCE|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|45 / 74|
|CSI-L|stable_venue_class_distance|OFFICIAL_STABLE_CONTEXT_OR_CANONICAL_NEUTRAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|0 / 119|
|CSI-L|transfer_preparation|TRANSFER_STATE_PREPARATION_OR_CANONICAL_NEUTRAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|CSI-L|layoff_preparation|LAYOFF_INTERVAL_READINESS|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|CSI-L|jockey_use_continuity|CURRENT_JOCKEY_CONTINUITY|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|CSI-L|cci_specificity|COMMENT_SPECIFICITY_OR_CANONICAL_NEUTRAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|0 / 119|
|CSI-L|tri_vertical_comparison|TRAINING_VERTICAL_COMPARISON_OR_CANONICAL_NEUTRAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|0 / 119|
|CSI-L|rotation_management|RECENT_INTERVAL_STABILITY_AND_FRESHNESS|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|118 / 1|
|BWI-L|good_weight_range|CURRENT_WEIGHT_VS_GOOD_RECENT_RANGE|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|109 / 10|
|BWI-L|weight_change_reason_rate|WEIGHT_CHANGE_CONTEXT_OR_CANONICAL_NEUTRAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|0 / 119|
|BWI-L|carried_weight|FIELD_RELATIVE_CARRIED_WEIGHT|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|BWI-L|age_growth|AGE_GROWTH_EVIDENCE_OR_CANONICAL_NEUTRAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|0 / 119|
|BWI-L|interval|DAYS_SINCE_LAST_RUN_READINESS_BAND|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|BWI-L|fatigue_rebound|INTERVAL_AND_WEIGHT_REBOUND_CONTEXT|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|BWI-L|transport_season|TRANSPORT_SEASON_SOURCE_OR_CANONICAL_NEUTRAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|0 / 119|
|BWI-L|paddock|PADDOCK_SOURCE_OR_CANONICAL_NEUTRAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|0 / 119|
|DCR|official_recent_coverage|DIRECT_EVIDENCE_COVERAGE_RATIO|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|DCR|same_venue_distance_comparability|COMPARABLE_RUN_COVERAGE_RATIO|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|DCR|training_comment_trial|COMMENT_TRAINING_SOURCE_COVERAGE_RATIO|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|DCR|bodyweight_range_coverage|BODYWEIGHT_HISTORY_COVERAGE_RATIO|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|DCR|same_day_gci_coverage|SAME_DAY_RESULT_SOURCE_COVERAGE_RATIO|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|DCR|late_odds_changes_coverage|OFFICIAL_ODDS_SOURCE_COVERAGE_RATIO|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|NCI|current_class|CURRENT_CLASS_ORDINAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|NCI|previous_class|PREVIOUS_CLASS_ORDINAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|NCI|recent_opponent_class|RECENCY_WEIGHTED_CLASS_ORDINAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|NCI|race_set_level|CURRENT_RACE_SET_CLASS_ORDINAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|NCI|class_change_pressure|CURRENT_MINUS_PREVIOUS_CLASS_PRESSURE|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|NCI|transfer_class|JRA_NAR_TRANSFER_CLASS_CONTEXT|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|119 / 0|
|NCI|class_relative_time|COMPARABLE_DISTANCE_TIME_PERCENTILE_OR_CANONICAL_NEUTRAL|CANONICAL_NEUTRAL_52_WITH_EXPLICIT_MISSINGNESS_AND_DCR_CONSEQUENCE|96 / 23|

全行共通：Input=frozen SOURCE、Output=0..100未較正ordinal、Neutral=既存規則、HOLD=nonfinite/provenance/temporal/universe不整合、Provenance=既存rule_id・SOURCE hash・component ledger。NOT-APPLICABLEは既存規則が明示した場合だけ、欠測の別名にしない。新式導入を伴う未閉鎖はProduction未閉鎖として残す。

## D. Numerical Candidate vs Baseline / calibration

同一SOURCEから既存Candidate v0.1と当該intent静的ランキングを並置。11レース・7,497 Component observations、再計算エラー0。terminal内訳はSUMMARY.json。Candidate順位変更は確認できるが、このcohortは既知・相関あり、予測改善証拠ではない。9/30の結果でfitしていない。公式settlementに結合していない項目はPENDING_VERIFIED_RESULT。

較正修正案：既存v0.1/v0.2/v0.3比較programを継続。targetはWinner rank / role discrimination、Probabilityなし。Trainingは出走前適格SOURCE＋独立確認結果、時系列でDevelopment/Validation/未来OOSを分割し同日race間をcluster。9/30はRegression/Hypothesis専用。lossはWinner/Top3順位損失、偽昇格・偽降格を併記。非負既存parameter bounds、baseline方向へのregularization、Validationでfreezeした設定のみ。URW3レースから新fitせず、同日依存・venue依存を検証。Candidateがbaselineより悪化・欠測過敏・輸送不整合ならrollback/修正、較正不能項目は削除候補。標本がない「較正完了」を捏造しない。

## E. KRS Incremental Utility Report

既存trackerはKM-JRA-KRS-OOS-PROMOTION-GATE、4/30。LOCAL4レースと呼ばない。既存pair proposals21、pair rescue race1、third proposals14、Exact rescue0。追加したRank delta / Unique Harm / false additionsが旧4件にはないため、欠測を0とせず未測定と表示。新規settlementから既存tracker/LOCAL candidate postresult evaluatorへ追加項目を保存。W/P2/P3 actual rank、Static role hit vs frozen KRS role zone hit、Unique Rescue/Harm、Pair/Exact additions、proposal widthを保存。Role→実購入の接続がない費用はNone、proposalを購入額へ捏造しない。Primary比較はStatic-only vs Static+KRS再監査、同じfreeze/原program条件。KRS回数・appearanceをProbability扱いしない。KRS pre-race proposal生成は変更なし。

## F. Existing MEC R4/R5/Common Exact status

R4=3/30、R5=3/30、Common Exact=0/30。最新ファイルから各既存evaluatorで再解決。Common ExactのCONTINUITY_ALL/KRS_TOP1/KRS_TOP3/KRS_TOP5、activation、target30、Candidate生成は不変。追加したのはfalse additions・added investment・outlier stressの集計。新trackerなし。Production MEC-R3は不変。

## G. Conversion Failure Report

保存済みPair/Third closureとMEC59券等をDevelopmentで参照。Material/Purchased Pair＋Active P3＋除外なし＋SEMANTIC_ONLYは既存Common Exactへ送る。結果後Exact追加をProductionルール化しない。Semantic coverage・購入materiality・stakeを分離。9/30検証済みsettlement未結合のため、正解Exact救済・PFSはここでは未判定。新たな馬・World・Roleを作る修正は行わない。

## H. Capital Width Candidate design / implemented harness

新サービスやtrackerを作らずresearch/utility/run_program.pyにdeterministic pre-race tier ablationを実装。PRODUCTION、CONSERVATIVE=既存CORE、BALANCED=既存CORE+PROTECTION、WIDE=既存FULL。研究3Armは同額実支出、100円minimumを先に確保し既存stake比率に整数largest remainderで配分。新券・AKI/KRS加点・結果thresholdなし。PRODUCTION実支出が研究budgetと違うとprimary公平比較不適格。券種mix差はtier policy全体の効果であり純Width因果とは呼ばない。Fixed bet-type mix感度比較を別途行う。

未来LOCAL raceだけ、final freeze＜生成＜発走、同一intent schedule・runner universe・SOURCE/FINAL hashに結合して事前生成。時刻・集合違反は研究artifact拒否、LIVE vetoなし。最初の未来30完備paired racesをpilotとし、未知OOSの十分性はeffect uncertainty・venue coverageから判断、30到達自動採用なし。Primaryはpaired net-return差、Conversion/Hit-but-loss/損失/Drawdownをguardrail、K・tier・allocationを途中変更しない。preregistrationをcommitしてから収集、欠測/締切失敗は除外せず別列。現状は実装済み・収集開始前、正式なCapital OOS activeとは称さない。

## I. Frozen / Actual / Shadow PFS separation

Frozen recommendation、explicit Actual purchase、Research candidateを別集計。Actual ledgerはpurchase_verified・ledger_complete・verification_refと各成功receipt、購入時刻、ticket/stakeを要求。failed購入は非支出、refundはproofを要求。公式結果のSETTLEDと金額を結合。Pendingは0払戻にしない。重複race ledgerは全部隔離し都合の良い一件を選ばない。Actual verified=0。Frozen成績からActual推定なし。

## J. Robust PFS / Marginal Capital Efficiency

保存済み全Frozen12件は地方9/30日次の値ではなくFamily混合集計。投資188,800円・払戻125,030円・PFS66.2235%、Median69.7967%、Hit9/12、Hit-but-loss5/12。Largest-return race除外PFS48.5726%、Top2除外39.6348%、Top3除外43.9010%、最大払戻を0化して投資維持30.4608%。Largest return share54.0030%、chronological max drawdown64,510円、losing streak3。Formal8件PFS67.3488%、比較eligible5件72.2044%。悪い成績をformal不足で消さない。Actualは0件で未算出。研究Arm同額費用とoutlier依存を併記しHeadlineだけで採用禁止。

既存tier集計へCORE→CORE+PROTECTION→FULLのadded investment/return/marginal PFS/profit deltaを追加。明示tierのない過去券は分類推定しない。欠測払戻のtierを0にしない、完備settlementのみ比較。

## K. First Material Failure distribution

SOURCEが読み取れた既知FNB11レースの最初の確認済み欠陥はProduction NUMERICAL未閉鎖=11。これは9/30の全損失原因をNUMERICALへ断定するものではない。Independent Conversion/Capital/Execution欠陥はclosure等に併記し消去しない。既存performance ledgerのfirst_failureは保持し、settled raceで未診断stageを勝手に埋めない。候補修正を一レースへ多重適用せずprimary ownerへ戻す。

## L. Unknown OOS tracker status

SUMMARY.jsonで最新値を記録。Common0、KRS4、MEC-R4/R5各3、LOCAL dual3、v0.3=0。既存target/definitionは変更なし。Syntheticや今回の11レース再計算はカウントしない。追加統計の欠測がある旧measurementは補完データなしでharm0としない。

## M. Production Freeze proof

PR116 merge後、開始時main bc7edcd7、報告確定時main d3093d42（差分はgateway canary statusのみ）へ追従。保護対象Production score registry/mapping/parameter_map/authority/Production converter/Common Exact Candidate/MEC shadow definitionsのbase hashとcandidate hashはSUMMARY.jsonで一致。Production購入Authority・固定購入Rule・数式・weightは変更なし。欠測・corner修正は既存非Production Candidate/Shadowに限定。PFS/RESULT/KRS trackerの追加はpost-result measurementのみ。

## N. Decision / next unknown race

HOLD Production Promotion。実装・修正・テストは完了、EMPIRICAL VERDICT PENDING。Final Verdict=INCONCLUSIVE。未知Prediction Accuracy/Hit/PFSが改善したとは言えない。

次の未知raceでは、(1)欠測をCALCULATEDから分けたCandidateを並走、(2)同SOURCEの別corner表を構造化、(3)KRS Rescue/Harm/順位差を新settlementで保存、(4)既存Common Exact/R4/R5を継続、(5)Capitalは結果前freezeしたArmだけ比較、(6)Actualは利用者の実購入proofがある場合だけ追加入力。LIVEをformal不足で止めない。source不足・数値不足・予測不足を点数増加で隠さない。

### Material Findings → active corrections

|Finding / impact|Root cause|Executed correction|Risk / validation|Status|
|欠測を数値計算と誤認、信頼度過大|Candidate terminal summary|RULED-NEUTRAL分離、transportとcalculated分離|数値は不変、旧artifact互換・回帰比較|IMMEDIATE-REPAIR (Candidate only)|
|同日位置情報を未利用、欠測を後方扱い|別corner表未結合・分母不適切|公式既存SOURCEの隊列・集団順位幅を構造化、観測のみ分母|括弧内順序を不確実に保持、Synthetic＋既知SOURCE回帰|IMMEDIATE-REPAIR (Shadow only)|
|KRSのrescue偏重・harm未測定|postresult field不足|existing evaluator/trackerへrank/harm/false additions追加|旧欠測は未測定、同じfreezeのpaired OOS|MEASUREMENT-REPAIR|
|Actualと推奨の混同|購入proof経路なし|同じPFS evaluatorで別Actual読込、failure/refund/pending管理|完全receiptがないActualは不明、負けを消さない|IMPLEMENTED; DATA PENDING|
|的中・coverage拡大が利益希薄化|費用の増分未可視化|既存tier marginalとCapital integer ablation実装|CORE濃縮でも外す可能性、未来同額比較|SHADOW|

### Re-run

`python research/utility/run_program.py`（read-only runtime、reportsのみ更新）。

`python -m pytest -q tests/test_phase_b_utility.py tests/test_local_fullnumerical_candidate_v01.py tests/test_pfs_grand_review.py tests/test_krs_prediction_utility.py tests/test_krs_oos_promotion_gate.py tests/test_common_exact_continuity_shadow.py tests/test_nar_auxiliary_evidence.py tests/test_local_numerical_authority_gate.py tests/test_local_production_numerical_closure.py tests/test_nar_runner_universe.py tests/test_nar_source_manifest.py`

Capital future freeze: `python research/utility/run_program.py --freeze-final FINAL.json --intent INTENT.json --budget SAME_ACTUAL_BUDGET --post OFFICIAL_ISO --output NEW_PATH.json`。過去FINALから未来OOS artifactを作ることは禁止。

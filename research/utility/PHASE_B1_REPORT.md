# Phase B.1 — Empirical Activation Report

判定：IMPLEMENTED / FORWARD LIFECYCLE CONNECTED IN CANDIDATE / EMPIRICAL VERDICT PENDING。
PR #117の研究実装を更新。Production Prediction、数値Mapping、Weight、MEC-R3、KRSの購入Authorityは変更しない。PR未merge時点ではmainでのLIVE activationを宣言しない。

## A. Candidate Rule Coverage / Missingness Map

「63 Numerical Rule Closure」を「63 Candidate Rule Coverage / Terminalization Matrix」へ訂正し、旧JSON名を置換。Productionはrequired63 / bound0、NOT_READY。CandidateのTerminalizedをCalculatedと同一視しない。

11保存Race・119Runnerの既存SOURCE診断：46 Componentに観測内容、2がNEUTRAL-DOMINANT、15が現Sourceでは全欠測。INFORMATIVEは取得内容があるという意味で、増分価値の証明ではない。`development_summary.json`は各ComponentのMissing率、分類、削除/統合候補を保存。age-growth、transport-season、stable-combo、weight-change reasonの欠測は代理変数で埋めない。

各Runner×Indexにcalculated/neutral count、missingness ratio、distinct observed source-reference dimension、fully-neutral/neutral-dominantを付記。構成項目が公開されない派生IndexのcountはNULLとし、既存missingness fractionを使う。Source参照数を独立した因果Signal数と呼ばない。Score減点・数値変更なし。

## B. Frozen Baseline vs Candidate Development Evaluation

9/30船橋の保存済み結果前CandidateとBaselineを、後続SOURCE中のOfficial Resultへ結合。10Race評価、R12はOfficial Result確認不足でHOLD。1 day/venue cluster、未知OOS=0。元Candidateのハッシュ不変を再実行時に検査。

|指標（10Race平均）|Baseline|Candidate v0.1|
|---|---:|---:|
|Winner rank|2.1|3.6|
|Winner reciprocal rank|0.7393|0.5910|
|Actual Top3 mean rank|3.0667|4.1667|
|W capture|9/10|7/10|
|P2 capture|10/10|9/10|
|P3 capture|10/10|10/10|

現Candidateに改善を認定しない。Rank/Role/false promotion/demotion、Prediction→Pair/Third/Exactの有無をRace別出力。Candidate静的ArtifactはPair/Exact policyを出していないため、その候補側比較値はN/AではなくNOT_EMITTEDと理由を明記。Neutral-heavy Indexの因果的rank displacementは識別不能とし、結果後に新Ablationを作って原因と断定しない。SOURCEを現在Compilerで再読する用途はMissingness診断だけで、Candidate順位は旧Freezeのみ使用。

## C. Authority vs Performance Failure

Authority/FormalityとPerformance First Material Failureは独立フィールド。NUMERICAL_AUTHORITY_NOT_READYによってEXACT、ROLE、CAPITAL等を消さない。既存Diagnosisがあれば採用し、secondary failureも保持。9/30Day Regressionの独立Diagnosisファイルはcheckoutで未確認のため、役割・購入の観測可能な欠落だけをラベル付きで再現し、Capital原因は捏造しない。

## D. JRA / LOCAL / BAN KRS Cohorts

既存4/30はJRA専用。JRA gateから明示LOCAL/BAN行を除外。Evaluatorは共有し、台帳のFamilyキーを分ける。既存JRAの候補定義・target30・過去測定は維持。

## E. LOCAL KRS Forward Measurement

既存LOCAL post-result evaluatorを拡張。正式FINAL後にStatic baselineとKRS utilityをFreezeし、同じrace_id / execution_idの署名検証済みRESULTからrank delta、Potential Rescue、Potential Harm/Non-confirmation、Pair/Exact proposal、false addition、proposal widthを測る。`unique_harm_role_count`は互換保存するが、実Production harm=falseを明記。

Immutable Execution Store内にpre-result Artifactを保存し、既存RESULT workflowでFamily別累積台帳へ取り込む。KRS utilityはCapital払戻欠測と独立に評価可能。既知/Mechanical/Post-startはFuture OOSへ入れない。結果Operatorが`official_result_verified=true`を明示した場合のみEligibleとし、確認がないRESULTは保存するがOOS countへ入れない。LOCAL前向き実績は現在0。

## F. Common Exact / MEC Current Status

動的に既存台帳から再計算：Common Exact0/30、MEC-R4 3/30、MEC-R5 3/30。CONTINUITY_ALL / KRS_TOP1 / TOP3 / TOP5の定義、MEC各Arm、target30を変更していない。

## G. Capital Pre-result Freeze

手動Harnessの実装を共通PFS moduleへ移し、重複実装を削除。Production FINAL署名検証後、発走前に自動呼出し。race/execution、SOURCE hash、FINAL envelope hash、runner hash、scheduled post、生成時刻、固定Protocol/definition hashes、Production tickets、budget、Arm一式を保存。

PRODUCTION、CONSERVATIVE=CORE、BALANCED=CORE+PROTECTION、WIDE=FULLを維持。最低単位・既存配分則・actual equal spendも維持。Coreなし等はShadow HOLDでProductionを停止しない。結果後再生成、異なるFreeze上書き、署名FINALとの不一致、定義Hash変更を拒否。

現在実RaceのFreeze receiptは未発生。テストreceiptを実Future evidenceへ昇格しない。`forward_protocol.json`をこのPRでcommitすることが研究開始前の定義Freeze。Rule変更時は新Window/Versionが必要。

## H. Capital Settlement / Persistence

Official RESULT後に全Armのinvestment、return、net、PFS、hit、hit-but-loss、Production差、equity incrementを保存。払戻欠測はNULL/HOLDで0にしない。Held settlementを履歴保存したうえでOfficial payout補完可能。SETTLEDはimmutable。

既存workflowがFamily別台帳と集計を永続commitする。Race A→別Python process→Race Bの累積、重複物理Race隔離、HOLDとKRS eligibilityの分離をテスト。Drawdownは時系列集計。最初の30eligibleはPilot minimumに過ぎず自動昇格しない。

## I. Actual Purchase Contract / Mechanical Test

`actual_purchase.schema.json`：race、発走予定、purchase timestamp、ticket、integer stake、success/failure、proof/reference、refundを定義。Readerは時刻・券種arity・重複purchase ID・refund<=stake・証拠・Official settlementも検査。署名RESULT経路へOptional readerを接続し、FINALから購入を生成しない。

実購入証拠は提供されていないためverified=0 / ACTUAL PFS UNKNOWN。9/22中山11Rの実在Official Result fixture（14→3馬単12,080円）と、明示test-only購入Schemaを組み合わせて受理経路をテスト。これはmechanical acceptanceであり、非架空の実購入台帳を入手したという主張ではない。真正購入fixtureとの照合は購入証拠提供後にのみ可能。

## J. Evidence Residual Gaps

既存Official Source Registryにはtraining / trainer comments / paddockを安定して取得・時刻固定する接続がない。馬体重、休養、転入は代理にしない。

Official大井にはパドック解説動画の提供実例がある（https://www.tokyocitykeiba.com/news/73701/）。存在と、現Runnerごとに再現可能なpre-result structured ingestionは異なる。現ConnectorではMISSING / NOT RELIABLY ACQUIRABLEのまま。新SourceやProduction scoreは追加しない。Source reconnaissanceは取得不能の永久証明ではない。

## K. Robust PFS by Family / Venue / Tier

`PHASE_B1_SUMMARY.json`にFamily、Venue、Formal class、Bet type、および保存済みTier economicsを出力。Headline、Top1/2/3除外、最大払戻zeroed/stakes維持、median、drawdown、losing streak、hit-but-lossを併記。

現canonical Frozen Recommendation 12RaceはJRAで、LOCAL改善証拠ではない。PFS66.2235%、最大払戻Race除外48.5726%、最大払戻を0として投資維持30.4608%、最大Drawdown64,510円。LOCAL Frozen canonical cohortは現集計0（9/30Day全体の成績を推定しない）。Tierなしの歴史RaceにTierを後付けしない。

## L. Production Freeze Proof

基準main `d3093d42ca0ef9d97a62fd7789fff0022d1a098d`。22 mapping/policy関連Tracked filesをgit content equality/hashで検査。既存87数値Golden regressionとProduction authority testsを維持。Measurement hookを追加したrunner/result/PFSファイル自体は変更しているため「全Productionファイルbyte不変」とは主張しない。変更したのは研究記録経路で、Prediction policy、数値、Production tickets、stakeを上書きしない。

## M. Current OOS Counts

|Program|現在|
|---|---:|
|JRA KRS existing|4/30|
|LOCAL KRS Phase B.1|0|
|BAN Phase B.1|0|
|Common Exact|0/30|
|MEC-R4|3/30|
|MEC-R5|3/30|
|LOCAL Numerical dual existing|3/30|
|LOCAL Numerical v0.3 existing|0/30|
|Capital Phase B.1 eligible|0|
|Verified Actual Purchase|0|

カウントは実台帳から再計算。Preregistration/測定コードを作った数はRace countではない。

## N. Promotion / Completion Verdict

Research foundation：実装・ローカル回帰70PASS。CIはPR headで別途確認。Production promotion HOLD。Candidate numerical empirical benefit NOT DEMONSTRATED。Future performance empirical verdict PENDING。

PR merge前の正確な状態は「FORWARD LIFECYCLE CONNECTED IN CANDIDATE」。mainへ研究変更がmergeされ、次の正式未知Raceが実行されて初めてoperational capture実績を確認できる。Actual purchase proof、R12Official結果、Missing Source、未出力Candidate Pair/Exactの比較は未解決として残し、PASSや0へ変換しない。

再実行：`python research/utility/run_program.py`、`python research/utility/development_evaluate.py`、`python research/utility/phase_b1_report.py`、CI内の指定pytest。結果を見てCandidateをfitする処理は含まない。

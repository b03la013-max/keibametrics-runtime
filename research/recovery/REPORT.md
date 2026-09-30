# Astra Recovery / Delta Re-Baseline — 実装報告

判定：CORRECTNESS RECOVERY CANDIDATE。FAMILY UNIFIED EXECUTION COMPLETEではない。

開始時main `cd350ad95a501ef37965b03417af63d348ab894c` を唯一の基準とし、新branch `audit/recovery-rebaseline` で作業した。PR #111はmergeせず、旧branch上の未公開変更も無条件継承していない。数値・MEC-R3・Capital・KRS・VenueのProduction方針は変更していない。

## A. Delta Re-Baseline Ledger

`DELTA_LEDGER.md` に旧主要成果を5分類した。SOURCE共通化、immutable store、corrupt FORMAL、original-intent basisはREDO。既存Freeze/Final導出/時刻調整はKEEP。過去のtest PASSはCurrent PASSとしてINVALIDATE。全Family/真の未知受入はREOPEN。

指定された `research/astra/KM-ASTRA-RECOVERY-DELTA-REBASELINE-20260930-R1.md` と同STATE JSONは開始時mainのGit treeに存在せず、API取得も404だった。欠落を隠さず、添付Recovery指示とmainの実装を根拠に進めた。旧報告は旧branchで確認済み。存在しないRecovery stateを生成して正本とはしていない。

## B. Current E2E Architecture Map

| 区間 | Current implementation / Owner | 今回 |
|---|---|---|
| Request / Authority | current_execution_gateway・family_authority_guard・現行profile参照 | current pointer維持 |
| SOURCE / runner universe / Evidence | 既存orchestrator→non_jra runner→外部SOURCE | 親に明示SOURCE phaseを吸収、取得二重実装を一つへ |
| Evidence→Prediction→Static Freeze | 既存Venue予測作業・凍結Intent、既存SOURCE binding | 判断OwnerはPrediction。未計算のランキングを生成せず、親はAWAITING_FROZEN_PREDICTIONを返す |
| Numerical / PRE_KRS / KRS | 既存runner・numerical authority・外部Engine | 変更なし。RULED-HOLDをCalculatedにしない |
| Semantic / MEC / Capital / FINAL | mainのclosure、MEC-R3、capital、署名FINAL | mainの9/30修復とShadow hookを保持 |
| FINAL→RESULT | local_result_from_signed_final | 保存IDの整数化bug、stale入力directory、別race FINALを修正。canonical要求は親から起動 |
| Settlement / Learning / Shadow tracking | 同RESULT executor→外部RESULT・fast reflection・既存tracker | 再実装せず既存処理を利用 |
| Checkpoint / Resume | execution_store＋親 | 不変保存・同一RESULT再実行防止 |

「同じ親」はLOCAL canonical経路での改善。JRA/BANをLOCALへ無条件routingする改変はしていない。全Family共通親の成立は未証明。

## C. Remaining Seam Map

| Seam | Before | After / 残存 |
|---|---|---|
| SOURCE専用とFORMAL fallbackの取得実装 | 二重 | 既存runner内の一関数 |
| SOURCEのみ開始 | 別のrunner起動に依存 | 親のSOURCE phaseを利用可能 |
| Frozen Static / Final package / Boolean | 重複入力の歴史 | mainの既存正規化を維持 |
| FINAL→RESULT | 独立entry | canonical RESULTは親へ。明示Actions artifactは互換entry維持 |
| RESULT checkpoint発行 | workflow | canonical経路は親。互換経路のみworkflow |
| SOURCE→予測判断 | 手動・外部Prediction | 残る。数値authority不足を架空の自動予測で埋めない |
| inline post_result_after_final | historical compatibility | 残存。新たな正本経路にはしない |
| JRA/BAN | 各Family executor/entry | 今回統合していない |

## D. 2026-09-30 Evidence Impact Map

| Evidence | Impact | 解釈 |
|---|---|---|
| 7件のSemantic内Exact未購入 | SUPPORT | Conversionの反復研究が必要。既存Common Shadowを保存 |
| 10R Exact的中control | CONTRADICT | 常にExact変換不能という一般化を否定 |
| 11R KRS Top1が実Exact | SUPPORT | KRS順位の再監査signalを研究する理由。Production強制昇格の証拠ではない |
| TAILが救済/損失の両方 | CONTRADICT | TAIL一律削除・既知日適合activationを否定 |
| 65,200円/35,300円/PFS54.14% | NO-IMPACT on policy authority | 添付指示で与えられた日次値。今回は全12R公式精算を独立再構築していない。署名検証とPFS実証を混同しない |
| 同一場同日7件 | CONTRADICT | 7独立OOSとして数えることを否定 |

## E. Consolidation Changes

- MERGE：SOURCE取得・検証二重blockを一つへ。
- ABSORB：既存親へSOURCE単独phaseとcanonical RESULT phaseを追加。新Service/Registry/Validatorなし。
- SIMPLIFY：canonical RESULTは既存FINALから精算。Prediction/Engineを再実行しない。
- COMPATIBILITY：明示Actions artifact参照は既存executorを維持。旧profileやVenue数値を削除しない。
- REPAIR：同一run overwrite、pointer rollback、破損checkpoint、manifest外file、RESULT run ID変換、別race FINAL、stale RESULT入力。
- REPAIR：既存Exact Shadowの本文hash検証と精算欠測の拒否。新Armなし。

## F. Actual Code Changes / Material Findings

| Finding / Root cause | Correction / implementation | Benefit / risk | Validation / 次Race |
|---|---|---|---|
| SOURCE二重Owner | 既存runner helper抽出 | driftを減らす。共有bugの影響に注意 | current mainとの24ケース差分試験、取得回数 |
| 同一run上書き | immutable保存・phase lock・原子的公開 | Frozen原本を保持。明示revisionが必要になる | overwrite再現、retry・copy中断・pointer試験 |
| 実行時post補正でretry basis不一致 | 元Intentを保存basisに指定 | 正当retryの不要再計算を防ぐ | semantic変更検出とtime補正case |
| RESULTの`123-formal`をintへ変換 | canonical IDだけ文字列維持 | 精算到達を回復、Actions numeric互換維持 | 実コードASTによる三経路試験 |
| RESULTで前raceファイル混入 | 一時入力directory再作成＋署名FINAL race照合 | Shadowの誤結合防止 | 別race guardと既存署名検証。実外部RESULT closureは未実施 |
| 独立RESULT起動と重複精算 | 親から既存executor呼出し、要求hashのimmutable retry | 既存Learningを再利用 | mock dispatch・retry・改変拒否 |
| Shadow本文を変えてSHA欄だけ維持可能 | 既存verify/settle/tracker内でhash再計算 | 結果後候補差替えを検出 | mutation拒否・正当lineage受入 |
| 欠測払戻を0円扱い | 三連単公式払戻必須、missingを未精算として検出 | 偽損失/PFSを防止。払戻欠測時は研究精算完了としない | missing payout adversarial test |

新しいPrediction仮説・EV・確率・Kelly・AKI mapping・Width ruleは実装していない。

## G. Regression / Equivalence

`run_checks.py`：current main旧2経路対新helper **24/24同等**。同一run overwriteをbeforeで再現、afterで原本保護。変更許可runtime以外のProduction policy差分なし。

`test_results.json`：68 testファイルを既存CIと同様に別process実行し全exit0（pytest 288件＋script形式15ファイル）。追加後のRESULT/SOURCE・Shadow計13件も再確認。mock/structural regressionでありlive E2E証拠ではない。

数値・Engine・parameter_map・MEC-R3・Capital・Venue・Authority profileは開始時mainと同一。Shadowの候補生成/Arm/100円単位/activation/30戦条件は同一。修正したのは不正hash・欠測精算のCorrectness挙動。

## H. External Execution Evidence

`external_verification.json` にcurrent gateway由来endpointのhealthと9/30 R12保存SOURCE/PRE_KRS/KRS/FINALのverify応答を記録する。保存済み署名の外部再検証であり新規SOURCE取得/KRS実行/FINAL生成ではない。RESULTを架空の公式払戻で生成しない。Healthおよび4種類のReceiptはHTTP200、各verifyはvalid=true / verified=true。4件の署名・receipt hash・artifact hashもローカル再計算PASS。RESULT外部実行は未実施。

## I. Shadow / OOS Preservation

既存Common Exact Continuityを作り直していない。4Arm、activation、target30、NO-AUTO-PROMOTION、production_effect NONE、Capital-width HOLDを保持。Trackerの保存済み0/30 status自体は変更しない。

新しいsettlementにshadow SHAを結合し、trackerではshadow/lineage/result本文hash、race ID、settlement-shadow一致を確認する。開始時実績0件なので既存eligible実績の移し替えなし。これは暗号署名の代わりではなく、元executorの署名検証を前提とする内部整合確認。

## J. Genuine Unknown-Future Acceptance

**NOT YET PROVABLE**。今回の開始は9/30 22:44 JST。保存済み9/30レースを未知未来へ再分類しない。現Candidate未deploy、未来レースの新SOURCE→結果前FINAL→公式RESULTをこの作業中に閉じたとは言えない。

次回は実在の未発走Raceを正当SOURCEから開始し、同一execution_idでFrozen Staticを入力、RESULT後に同じ親のRESULT phaseで閉じる。Prediction生成を省略したり、署名時刻を戻したりしない。未来開催・必要入力・公式結果の到着を待つ部分に虚偽のPASSを作らない。

## K. Architecture Reduction Report

| Measure | Before current main | After candidate |
|---|---:|---:|
| SOURCE取得実装 | 2 | 1 |
| LOCAL SOURCE/FORMAL/RESULTを扱える既存親 | FORMAL中心 | 3phase対応 |
| 新Service/Runtime/Validator/Registry | 0 | 0 |
| 新Workflow | 0 | 0 |
| 既存Workflow修正 | 0 | 2 |
| 新Prediction/資金policy | 0 | 0 |
| 手動SOURCE→Static判断 | 存在 | 存在 |
| 全Family単一親 | 未達 | 未達 |

総行数はCorrectnessと試験のため増加した。Architecture全体が小さくなった、PFSが改善したとは結論しない。

## L. Remaining Risks / Completion Boundary

1. Recovery正本文書2件の欠落。現mainと添付以外の未公開変更は確認できない。
2. SOURCE→Prediction→Staticの自動生成は未完成。既存Production numerical NOT_READYを推論で埋めない。
3. JRA/BANの完全統合は未実施。LOCALの意味を他Familyへ強制しない。
4. 真の未知Race受入と後日のRESULT closureは未達。今回の回帰PASSを代用しない。
5. Storeはプロセス中断に強くしたがfsync/全電源断recoverを保証しない。
6. Shadow trackerは内部hash整合だけでは署名authorityの独立検証にならない。既存署名済みexecutor境界を継続する。
7. Correctness fixは未公開branchの実装から選択的に再適用。Productionへのmerge/deployは行っていない。

総合：実装・current-main再基準化・回帰検証を前進させた。未知未来のPrediction/Hit/PFS改善判定は **INCONCLUSIVE**。完成条件9・10を含む未達項目があるため、FAMILY UNIFIED EXECUTION COMPLETEの宣言はしない。

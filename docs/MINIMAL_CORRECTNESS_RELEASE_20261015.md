# 最小Correctnessリリース審査（2026-10-15）

**Production未変更 / Human Review未承認 / Merge・Deploy・Activation未承認。**
本パッケージは現行mainを親に持ち、PR276・279をMergeする必要はない。
Code subject: `9d38b8cc03f185944e794d55c1afea8f864f856d`。
Base main: `464db2fd6c857c84549c4311fb8aa34629768203`。
参照元: PR276 `4e3c71fc1765027f45299cd2b406228f41d20ad8` / PR279 `2054bb18a17dd44a8f391b6225c43a2b34fa7ef2`。既存PR・Artifact・履歴は変更しない。

## 依存の解消と適用範囲

コード9・テスト7・既存Workflow3ファイル。旧PRの全取り込み、Shadow/Research/AKI券面生成、Owner Role生成の単なる関数抽出は含めない。
全197パスの採否とmain/Candidate blobは `evidence/minimal_correctness_20261015/dependency_audit.json`。
mainに同一内容があるorchestrator、返還HOLDの既存回帰、Canary修復等5パスは重複適用しない。

| 採用する変更 | 元 | 修復対象・回帰 |
|---|---|---|
| `local_race_key_intake` とrace-key Workflow | 276 | moving HEADによる要求消失、複数要求の混線。immutable before/afterから各Raceを解決し、Race別concurrency・RESULT・保存先へ分離 |
| `jra_ticket_tree_renderer` | 276 | stake混在を失わず正本券面へ戻せることを照合。LOCALも既存共通rendererを使用 |
| `local_race_key_gate` | 276+279 | job成功や保存flagをFINAL/配信成功と誤認しない。正本Gatewayでfresh verify、同一Identity、正本treeを表示。独立したDelivery署名を捏造しない |
| `local_race_entry` | 279 | SOURCE失敗/pointer欠落を原因保持HOLD、後段呼出0。FINAL存在時は既存semantic/source-bound readbackへ入り、SOURCE/Static/KRSを再生成しない |
| `local_production_static_owner` | 279 | 掲載集合とActive差分が公式PRE_CUTOFF根拠付きCANCELLED/EXCLUDED集合と完全一致するときだけ取消行を除く |
| `minimum_efficient_coverage` | 279 | Active外ranking/Role/head/Pair/Thirdを既存入口で拒否。選択則・重み・Capitalは変更しない |
| `local_physical/app_v15` | 279 | Signed SOURCEとFINALのranking/Role/券面/MEC券面を署名前に照合。既存Signer/Envelope/Trust Anchorを継承 |
| `local_result_from_signed_final` | 279 | 的中券の払戻欠落/0をCOMPLETE・戻り0円にしない。署名・送信前に停止。Shadow追加署名処理は取り込まない |
| `formal_failure_diagnostics` | 279 | 必要な正式Staticがない状態をOwner入力待ちと分類し、無許可の自動昇格を誘発しない |

返還必要・同着・未確定・Race Identity不一致・不完全な3券種払戻のHOLDは**mainに既存**。追加実装で重複させない。
Workflowから`--candidate-ticket-paper`を除外。`non_jra_formal_runner`、Shadow Owner、AKI列・研究・測定台帳・profiles/mapping/governanceに差分なし。
SOURCE受理範囲を狭めるBehavior Bは本候補に含めない。元PR279の `research/family_reliability_20261015/promotion_review/source_acceptance_narrowing_NON_PRODUCTION.patch` に非実行のまま保持する。

## 実検証

現在のmainへ新回帰を当てた30ケースは29FAIL/1PASS。修復後は関連423テスト+13 subtestがPASS（JUnitのtests=436はsubtestを含む）。`before_regression.xml` / `regression.xml` / `regression_test_list.json`参照。
浅いcheckoutで過去commitがないために失敗した履歴依存テストは、保存済みR12要求と一時Git履歴で「event SHA対moving HEAD」を再現する形へ変更した。実LIVEや実履歴の再実行とは呼ばない。
Workflow/実行コードの構文・`git diff --check`もPASS。GitHub CIは独立PRの正確なHEADで確認し、旧279の10Workflow成功を流用しない。

川崎1Rは原147ファイルSHA・4署名/artifactSHAを固定AnchorでPASS。現行Runtimeへの4件の既存Envelope再検証もHTTP200/valid=true。
348/348、保存KRS5000回、原FINAL `0f562134594438824a0f9dc322b868d0243ead1b0ae17a9715ce4e5d66f5e20e`、156点15600円を保持。オフラインのStatic/Role/Pair/Third、MEC全体SHA、Capital全体SHA、正本treeが一致した。
川崎2RはSigned SOURCE `fa082a7dfcb923b1c994d20b4eb744aa34e3a66bbb5c42ac3019a6c8dcf3a06d`、174/174、取消3/7、Active1/2/4/5/6/8でStatic→KRS入力→MEC券面をオフライン照合。外国馬混入を拒否。
R02の元`OFFICIAL_CARD_RUNNER_MISMATCH`を保持。正式KRS0、新FINAL0、外部再実行0、正式推奨PFS=null。診断用券面は正式な事前FINALではない。
原本はPR279に置いたまま、本候補には検証結果のみを追加した。`race_regression.json`参照。

## Required ChecksとHuman Reviewの具体的状態

取得時のmainは`protected=false`、branch応答のrequired contexts/checksは空、継承込みrulesetsも空。
詳細`branches/main/protection`はintegrationに管理権限がなく403。effective branch-rules endpointはConnector未対応。保護設定を変更したとは主張しない。
所有者は [Branch settings](https://github.com/b03la013-max/keibametrics-runtime/settings/branches) と [Rulesets](https://github.com/b03la013-max/keibametrics-runtime/settings/rules) で、公開API観測どおり未強制かを確認する。設定を強制する場合は管理者が実在する成功checkを選び、その**正確なcheck名/app**を指定する。同名acceptance/unit/liveがあるためWorkflow名だけで全check強制と誤認しない。
最低限の審査対象は既存Runtime Correctness / race-key acceptance / LOCAL JRA execution guarantees / Gateway Canary。PRのcheck-runsとWorkflow run URLを全件確認する。CIの歴史fixture名Liveは未知未来実証ではない。
旧276/279のreviewsは承認証拠に使わない。この独立差分と下記配置差分の**人間によるレビュー**が必要。AIはAPPROVEを提出しない。

## 現行Runtimeと最小配置

サービス `witnessstrictimage` / deployment `acf63364-0235-42ea-b68d-fbe931fcf51f`、SUCCESS・staged changesなし。
現行HealthはREADY / `f0d23766b1d2e4cefc6194458b0e9141d5479cbc`、現行Gateway Canary PASS。
現行wrapper SHA: `e54ae7ad31a1959df113568f6d1591e9753971f30fccac5325e627e07e52f12b`。
候補wrapper SHA: `ccb7af22beb13a1304715d967ceb32e48819f1b170bd1d53cd0ec87d6161974c`。
Engine `9929df99…`、parameter_map `d8c027ee…`、Signer `KM-LOCAL-RUNTIME-ED25519-20260922`、公開Anchorは不変（完全SHAはrelease_plan）。

**実際の障害はRailway startCommand内のrev固定。main Mergeだけでは古いコードを再取得する。**
さらにRuntimeのroot4モジュールはmainと異なる。main全体へのrev置換はCapital/KRS utility/MEC/Learningまで変更するため採用しない。
物理Runtimeで差し替える実行ファイルは**app_v15.pyだけ**。ClientのMEC境界修復はGitHub実行環境で効く。Runtimeの旧MEC/Capital等11モジュール、legacy app、Engine、parameter_mapを既存SHAで保全する。
準備済み `runtime_start_after_approval.txt` は旧revのbase downloadを維持し、wrapperだけCode subjectから取得する。全module/legacy/wrapper/engine/parameterのSHAを配置前にassertする。`/opt/km/rev`は修復Code subjectを表示する。shell quoting/Python AST確認済み、**起動・設定反映はしていない**。
Gatewayに必要な未適用差分は`gateway_AFTER_APPROVAL.jsonpatch`（diagnostic revision、wrapper SHA、source記述のみ）。Authority・profile・Venue・Engine・parameter・Signer・private keyの変更は不要。

## 承認後の順序とRollback

1. この独立PRのコードとCode subject、非実行配置差分をHuman Review。正確HEADの全CIと最新mainとの差分を確認。所有者のMerge承認を記録。
2. 新規Race受付を止め、進行中/締切直前のRaceがない時間帯を選ぶ。既存Signed FINAL/Checkpointは保全。承認されたPRをMergeする。
3. 別途のDeploy承認後、既存サービスのstartCommandだけを準備済み文字列に変更し、既存サービスへDeploy。リソース/課金/鍵/環境変数の値を変更しない。
4. 実Deployment ID、HealthのCode subjectと候補wrapper SHA、他の不変SHA・Anchor・Signerを検証。対応するGateway patchを所有者承認の下で適用しCanary。途中のpointer/runtime不一致中はHOLDし新Raceを実行しない。
5. 既存署名の/verify・原FINAL readback・正本treeを再確認。Candidate `/final` の異常membership拒否はローカル非署名stubで検証済み。新しいLIVE署名受入れは次工程と区別する。
6. 別途Race別/送信先承認を確認し、未知未来のSOURCE→Static→PRE_KRS→実KRS→FINAL→正本Deliveryを実証。取消なしLIVEと取消ありLIVEを分け、複数Raceは独立Deadline/worker/checkpoint/RESULT待機/競合回復を確認する。
7. 公式結果・3券種正の払戻とselection一致後にだけSigned RESULT→Settlement→Frozen Recommendation PFS→First Material Failure→Dominant PFS Loss Owner→Learning。返還必要/同着/欠測はHOLD。

Rollback: 受付HOLD→`runtime_start_rollback.txt`の旧startCommandへ戻して既存サービスをDeploy、または既知の同一snapshotへRollback→`gateway_ROLLBACK.jsonpatch`→旧Health/bundle/Anchor/既存Receipt再検証。Client修復が原因なら承認済みMergeを通常のrevert PRで戻す。**既存Artifact/OOS/失敗履歴はrevert対象にしない。** 旧取消Bugへ戻るため該当RaceはHOLD。

## 結果と残る所有者操作

2026-10-15 13:55 JSTの公式当日メニューはR01発走14:45、まだ発走前。結果ページ取得不能を0円精算にしない。専用`--resume-official-result --result-wait-seconds 0`は原SOURCE/FINALを使いWAITING_OFFICIAL_RESULT / NOT_DUE / prediction_reexecution=false。1R Closed LoopはPENDING。2Rは正式FINALなしのためSettlement/PFS/結果LearningはBLOCKED。
個別card直接取得はDNS障害、web個別cardも取得不可。全Material Changeなしの宣言はしない。
残る操作は①人間の差分レビュー、②管理者の保護設定確認/必要なら実check強制、③正確PRのMerge承認、④wrapper-only配置とGateway patchのDeploy承認。PR276/279の先行Mergeは不要。
OpenAI API要求0、新規有料リソース0、課金変更0、購入0、Production変更0。既存Railway従量費用UNKNOWN。


## 個人開発の限定承認方式への移行案（2026-10-15・未採用）

Family C1契約の独立性は実装独立性であり、第三者Human Reviewerの一律要求ではない。本資料の「人間によるレビュー」はOwner本人による実レビューと区別可能である。ただしPR280に対する従来のOwner依頼は独立Human Reviewを必須としていたため、Owner本人がGovernance追記のSHA・コードSHAを指定して限定方式を採用するまで、その条件を維持する。

採用後に限り、C0/C1証拠条件＋Owner本人の差分確認＋exact-head Merge承認を用いる。Discovery/Schedulingとwrapper Deploy、KAW限定Activationはそれぞれ明示承認対象。AI監査/CI/Owner包括方針を独立Human Reviewとは表示しない。予測Policy昇格のOOS/Human Review条件、既存数値・KRS・MEC・Capital・Signer/Anchor・Artifactを維持する。

Owner採用指示更新：2026-10-15 23:27 JSTの正式化依頼を上記Governance第9.5節へ記録した。以前の第三者レビュー探索HOLDは、Owner本人の差分・リスク確認HOLDへ移る。独立Human Reviewは未実施のままとし、Workの監査で代替しない。正本追記はPR282上で保存し、PR280の実行コードHEAD/CIを動かさない。Owner確認未成立のためMerge/Deploy/Activationは未実行。

2026-10-15 23:42 JST更新：Owner本人の差分確認・Merge承認を受領。PR280 Merge SHA552700f26a4b1b8c321a8b5b2321a1c87df41237。旧Owner確認HOLDは解消。wrapper限定Deployは単一startCommand差分をステージ後、Deployツール承認がキャンセルされ停止。Activation/新LIVEは未実行。既存f0d23766/旧Gatewayを維持し、次操作は保留1件の正規Deploy承認。

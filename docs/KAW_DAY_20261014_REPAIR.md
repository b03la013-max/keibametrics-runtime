# 川崎2026-10-14 全工程修復・受入れ報告

**CANDIDATE / NON-PRODUCTION。全体の実運用完成・未知未来性能受入れは未完了。**

## 現行正本と環境

開始main `1ccbd894e646b93fd18ff69f8f57de5e8b172667`。Family R51、LOCAL Production R3、地方Common v4.13 Rev.1、川崎v2.4-KAW、MEC-R3、Engine1.1.0、parameter0.1-provisionalを再解決。KAW v2.5/LOCAL列別AKI/Family診断/AKI vNextはPR263/262/264/265の未Merge候補。MEC-R4/R5もShadowでProduction置換なし。現在の自動Static Ownerは `KM-LOCAL-PRODUCTION-STATIC-EVIDENCE-OWNER-v1.0-20261014`、KAW pilot enabled。公式過去成績の順位則であり、29指数をProduction Predictionへ消費する権限はない。プロファイルの初期activation状態と、10R/11R/12Rの実署名成功、予測性能検証は別状態。

Railway witnessstrictimageのDeployment `acf63364-0235-42ea-b68d-fbe931fcf51f` は10/14 15:13 JST SUCCESS。Healthのengine/parameter/全bundle fingerprintは凍結Gatewayと一致。朝のtrial停止/404を現在状態へ流用しない。本作業で課金・配備・鍵・環境変数を変更していない。Base44 Console app `6aabb8079803485e24ee0259` のsandbox読み取りはPREMIUM_REQUIRED。OAuth GitHub connector未接続。独自API直結はコードを読めず未確認であり、未接続と断定しない。

## 全12RのExecution Failure Audit

受付とユーザー受取のChat実時刻はGitHub/Runtimeから復元不能。全12Rを母数に残し、UNKNOWNを成功・未依頼へ変換しない。詳細時刻・SOURCE/FINAL/RESULT参照・Cutoff・29値状態・Workflow・Learningはexecution_audit.json。

|R|保存状態|発走前FINAL|主な原因・未確認事項|
|---|---|---|---|
|1|NO_SIGNED_EXECUTION_EVIDENCE|未証明/未成立|UNKNOWN_REQUEST_OR_START; NOT_EXCLUDED_FROM_DENOMINATOR|
|2|NO_SIGNED_EXECUTION_EVIDENCE|未証明/未成立|UNKNOWN_REQUEST_OR_START; NOT_EXCLUDED_FROM_DENOMINATOR|
|3|SOURCE_ONLY|未証明/未成立|SOURCE-only execution; no frozen FORMAL checkpoint. Original chat handoff/delivery time unknown.|
|4|RESULT_SETTLED|成立|署名と精算成立。受取時刻未証明|
|5|RESULT_SETTLED|成立|署名と精算成立。受取時刻未証明|
|6|NO_SIGNED_EXECUTION_EVIDENCE|未証明/未成立|UNKNOWN; R06_CONNECTOR_REFUSAL_REPORTED_ISSUE268|
|7|SOURCE_ONLY|未証明/未成立|FORMAL entered 17:44:16 JST after release deadline17:43; SOURCE was17:41; no PRE_KRS/FINAL|
|8|SOURCE_ONLY|未証明/未成立|SOURCE-only execution; no frozen FORMAL checkpoint. Original chat handoff/delivery time unknown.|
|9|NO_SIGNED_EXECUTION_EVIDENCE|未証明/未成立|UNKNOWN_REQUEST_OR_START; NOT_EXCLUDED_FROM_DENOMINATOR|
|10|RESULT_SETTLED|成立|Git保存後scratch復元失敗（修復済み）|
|11|RESULT_SETTLED|成立|Git保存後scratch復元失敗（修復済み）|
|12|RESULT_SETTLED|成立|初回はmoving-main CheckoutでRace-Key0件。再投入でFINAL/RESULT成立|

5/12にprestart FINALとRESULT、3/12はSOURCEのみ、4/12は署名実行証拠なし。ユーザー受取のprestart証明は0/12。3R/8RはSOURCE-onlyリクエストとしてSOURCE_PASSだが全工程未完了。6RはIssue268にconnector create_fileの自動安全審査拒否が報告されており、アプリ側では解除できない。1R/2R/9Rの受付・未起動理由は不明。最初の失敗原因を全件確定したとは主張しない。

## 修復した既存経路

12R Run38549826099はPush SHA75e5debaのRace-Keyを扱うべきところ、Checkoutが後続main efa53168を取得し、そのHEADのdiffを見ていた。後続Commitは集計更新のみでRace-Key0件。旧経路FAIL→イベントbefore/after固定の新経路で1件を解決する実コミット回帰を保存。複数Race-Keyは既存intakeでmatrix化し、別Raceは独立concurrency・fail-fast false、同Raceは直列、同一Execution IDで既存Checkpointを再利用する。無効なセルもTerminal Errorとして保存し、他Raceを落とさない。

11R Run38550326785と10Rは、SOURCE/FINAL/RESULTが成立後、Git push後scratch stash復元でWorkflow failureとなった。`18b62fe1` によりすでにwarningへ修復済み。重複修復をしない。Terminal ledgerはActions exit、Signed FINAL、prestart FINAL、render、受取証拠を独立記録し、successful jobからFINALを推測しない。

Race-Key RESULT保存はOFFICIAL_RESULTの原文Snapshotを落としていたため、保存対象へ追加。4R/5R原文は既存immutableチェックポイントと照合。10R/11R/12Rは正本Runtime /source/acquireで結果後原文を新観測として取得し、/verify・raw hash・公式上位3着・払戻を照合。これらの旧Signed RESULTはfinish_orderが上位3頭のみ。新観測の全着順を旧Receiptへ追記・書換えしない。新SOURCEのSOURCE_FROZEN/formal_readyは結果後観測の状態で、発走前Prediction入力やOOSには使用しない。

縦型Treeは既存rendererを再利用。券種・馬番・順序・点数・StakeをReflattenし、混在Stakeは券面別に明示。資金判定未実施は未実施と表示する。Gate後にcanonical_tree.txtを実行台帳とActions Summaryへ出し、空表示・delivery未証明を成功へ変換しない。Base44/Chatの受取ACKは未接続で、発走前delivery完成はPENDING。

Candidate KRSの保存入力は実行前templateで、実際にはRace ID/seed/run_countを書換えていた。15実Receiptの入力をその既存演算で再構成すると全hash一致。Engine不一致ではない。今後はeffective_inputを実行直前に保存し、外部署名input hashの不一致をCandidate HOLDへ終端する。既存15件75,000実回数を検証、再実行は0。

## 4対象Rの正式PFSとFirst Failure

|R / 結果|Production 投資→払戻 / PFS|元AKI 投資→払戻 / PFS|First Material Failure|追加観測|
|---|---|---|---|---|
|4 / 4→10→1|22,900→5,130 / 22.40%|1,200→1,220 / 101.67%|CAPITAL_EFFICIENCY|Exact的中だがCapital希釈。AKI Third欠落。Trio未購入|
|5 / 1→4→10|25,600→13,910 / 54.34%|1,200→0 / 0.00%|CAPITAL_EFFICIENCY|Exact的中だがCapital希釈。AKI P2欠落。R5TOP5は134点103.81%|
|11 / 7→6→10|14,400→0 / 0.00%|1,500→0 / 0.00%|PREDICTION_ROLE_W|Static W/P2欠落。KRS Winner救済のみ。P2/Exact接続は別問題|
|12 / 3→2→13|16,800→0 / 0.00%|1,500→0 / 0.00%|PREDICTION_ROLE_W|Static/KRS共通Winner盲点。v0.3もWinnerを失う|

提供の4件RESULT Receiptは全一致。正式AuthorityはFROZEN-RECOMMENDATION、Actual Purchase UNKNOWN/PFS null。Trio購入はpurchased_trio_ticket_coverageと実TRIO券を確認し、top3_set_ticket_coverageや同じ3頭の三連単から推定しない。MEC-R3はKRSを非Capitalized Shadowにする現行権限なので、11Rの救済未購入を係数バグとして自動W追加しない。12Rは上位KRS追加では解決できない。川崎v2.4第362/365/366/371条との責務を維持。

## 数値Candidate→Ticket→Capital 比較

v0.1/v0.2/v0.3を同じ凍結SOURCEから再計算し、当時のPrediction object/hashと一致。既存OwnerのRole Graph構築を純粋関数へ抽出、Production出力を維持してCandidateへ再利用。11R/12Rの旧Ownerと新版の出力・ledgerを実入力で完全一致確認。SelectorはPR265@10589f21の同じlocal_aki_columns.py、資金ExposureはPR264の同じ測定関数を統合。別Selector/Calculatorなし。R1の既知性能FAILを解除していない。

以下は新しい結果後Conversion Replay。元の数値Role/KRS OOS台帳や元17戦を変更せず、新Ticket方式のForwardへ数えない。

|R|v0.1/v0.2 full MEC PFS|v0.1 Head-local PFS|v0.3 Head-local PFS|可変R5 v0.1 PFS|
|---|---:|---:|---:|---:|
|04|12.83%|285.00%|128.25%|27.00%|
|05|34.77%|130.31%|130.31%|38.64%|
|11|924.29%|0.00%|0.00%|1039.82%|
|12|1631.91%|0.00%|0.00%|39.80%|

全券面、Counterfactual/観測の区別、Head/Pair/Third/tier/券種Exposure、Material Pair lossとThird World、Trio/Exact独立捕捉、全資金・損益はcandidate_comparison.json.gz。広いfull MECの11R/12R大払戻は、この4失敗Fixtureで組み直したReplayであり、未知未来改善の証明ではない。圧縮は11R/12Rの正解経路を失い、v0.3が最良という結論は出ない。可変R5はAKIで選定されたRoleの最大順位境界を既存R5に渡す仮説で、結果前データだけで計算。固定TOP5を採用しない。

予算未指定はNOT_EVALUATED。2,000/5,000/10,000円は明示PAPERシナリオ。必要最小資金が超過したら既存HARD_RACE_BUDGET/NO_BETを使用し、Stake比例拡大・余剰資金の買い増しをしない。予算適合と全Semantic Material Coverageは独立保存し、AKIで削除した世界をCoverage100%と偽装しない。価格パネル欠測なのでCore-Hit Recoverability/EV/KellyはHOLD/未算出。

## 実外部受入れと次回導線

既存SOURCE/PRE_KRS/KRS/FINAL/RESULT33件をoffline署名/artifact hashと現行Runtime /verifyで照合。Candidate KRS15件も署名/effective入力hash/75,000実回数照合。新PAPER比較4件にSigned RECON FINAL+RESULT、追加zero-purchase PAPER1件にFINAL+RESULT+別Arm精算を実際に実行。失敗したstage-manifest欠落の4署名FAILも保持。new KRS0、genuine Forward0。署名/Code/source bindingはacceptance/manifest参照。Historical Replayでprestart deliveryを受入れ済みにしない。

正式Runnerの明示PAPER flagで既存数値Candidateを券面・Capitalへ接続。大きな監査世界はhashで保存し、署名パケットは券面/Stake/Policy/Source/Predictionの必要情報へ圧縮。Production FINALの後に既存Candidate KRSの実入力/実回数を確認し、発走前に別zero-purchase Shadow FINALを署名する。間に合わなければShadow HOLD。RESULT workerは署名とFINAL lineageを検証し、同じ公式結果で独立PAPER精算する。Productionの券面とShadowを混合しない。

この候補Branchをmainへ自動Mergeしないため、実運用の新経路はまだ有効化されていない。次回未知未来ではPolicy/Code/Source/Static/Ticket/Stakeを結果前にFreezeし、same-SOURCE A/B比較、失敗・期限切れを含む母数、価格/No-Bet費用、正解W/Pair/Exact削除、False Addition、PFS/DD/大払戻依存、venue/distance、latency/受取ACKを測定。初期目標30、現在0。旧Role OOSを新Ticket Armへ加算しない。

## 最終Acceptance

|判定|状態|理由|
|---|---|---|
|EXECUTION-ACCEPTANCE|VERIFIED REGRESSION / LIVE PENDING|固定イベント・複数Race・Checkpoint・既修復保存を検証。修復版の未知未来は未実行|
|EXTERNAL-RUNTIME-ACCEPTANCE|VERIFIED EXISTING RUNTIME / REPLAY PAPER|Health/bundle/署名/実APIは確認。新しい未来全工程とは別|
|PRESTART-DELIVERY-ACCEPTANCE|PENDING / BASE44 BLOCKED|受取時刻ACKなし。料金/権限を変更しない|
|NUMERICAL-CONFORMANCE|VERIFIED TRANSPORT/CALCULATION|29 Terminal値再計算。Consumption/較正/予測価値の証明ではない|
|PREDICTION-PERFORMANCE|PENDING / UNVALIDATED|11Rと12Rは別失敗。係数の結果合わせなし|
|TICKET-CONVERSION|VERIFIED REPLAY / FORWARD PENDING|実券面と署名binding。圧縮の誤削除が残る|
|CAPITAL-EFFICIENCY|PENDING|PAPER予算/No-Bet実装。持続的PFS・価格・Drawdown実証なし|
|OOS-PROMOTION-READINESS|NOT READY|new Forward0/30、Owner Gate/Human Review未完了|

残る具体的操作：Candidate PRのCorrectness差分をOwnerレビュー後に適用し、次の依頼で発走前delivery ACKまで実試験する。Base44のdirect sandboxはBuilder権限が必要、GitHub OAuth接続はOwnerの明示承認が必要。独自直結の実装を読み取れる状態にしてからConsole→GitHub/Runtime→署名→Tree→受取ACKを検証する。Issue268の自動審査拒否はプラットフォーム側の原因詳細が未提供で、Support対応が必要。予算はユーザーが明示した値だけを実運用へ結合する。

Production Suite/Authority/Engine/parameter/数値式/AKI閾値/MEC-R3/Capital政策/過去FINAL・RESULT/元OOSの変更なし。Ownerコードは出力維持の抽出のみ。買い付け・課金・配備・無断Merge/Promotionなし。全12Rの未確認原因、受取証拠、未知未来性能をPASSにしていない。

## CI integration follow-up

Initial CI detected `DEFINITION_NOT_PREREGISTERED`: the historical Forward protocol freezes the entire post-result owner file. The PAPER-only extension was moved to the existing Race-Key Shadow owner; the frozen post-result owner and old protocol hashes remain unchanged. Targeted Forward and lineage regression: 24 PASS. Latest main was incorporated without Production changes; the only concurrent main change was the JRA race-day status ledger.

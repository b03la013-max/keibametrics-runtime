# JRA Resolver P0 — 東京8R通信切断・Status整合修復

対象: KM-JRA-TKY-20261017-R08 / Run 39000908421 / Job 117303437627。
この変更はCorrectness候補。Production Merge・未来Race Activation・新しい外部Delivery・追加費用・購入の承認を含まない。

## 実障害と原因

実Runは2026-10-17 13:00:12開始、13:01:43終了FAILURE。実チェックアウトは`386b0cd4a09dffb8c448f64ea0d179dfec40384f`。
13:01:40、`resolve_and_build → resolve_day → _Client.post → _Client._open → urllib → HTTPSConnection.connect → SSL.do_handshake`でConnectionResetError(104)、URLErrorへ包装され最上位へ伝播した。
失敗要求はJRA公式`https://www.jra.go.jp/JRADB/accessD.html`への開催日選択POST。Calendarと最初のnavigation POST後、`s2 = c.post(..., tok)`で失敗した。ログは公開token値を記録していないため値を推測しない。timeoutは30秒。要求内容はnavigationの読み取りであり、投票・注文ではない。
実Tracebackは`tests/fixtures/jra_resolver_tky8_20261017_traceback.log`。切断を発生させたJRA/CDN/経路側の内部原因はログから特定できない。

既存RetryはHTTPErrorの502/503/504だけを捕捉し、Resetを内包したURLError、接続/読取Timeout、429、本文読取中の切断を捕捉しなかった。本文読取もRetryの外にあった。
WorkflowはIntent commit/Single Entry dispatch前で停止。失敗を保存するfinally経路がなく、Status側は下流`km-formal-request-runner.yml`だけを照合していた。Intentが存在しないRaceはその照合に入らず、ACK済みDispatchからDISPATCHED_RUNNINGが残存した。

## 最小修復

| 既存ファイル | 修復 |
|---|---|
| runtime/jra_source_runtime/jra_pedigree_harvest.py | 同じopener/cookie/URL/POSTを維持し、Reset・接続Timeout・本文Timeout/IncompleteRead・429/5xxを分類。恒久4xx/証明書エラー/Source違反は即停止。 |
| runtime/jra_source_runtime/jra_race_day_resolver.py | 全navigationで共有する180秒Budget、既知の公式postによる既存15分lead制約、Linux wall-clock guard、既存exact_gapsへの失敗保存。 |
| runtime/jra_source_runtime/jra_race_day_autopilot.py | IntentなしのResolver失敗表示、実Workflow outcomeによるStatus復旧、期限内の同じ失敗Runの1回限定再試行、成功Intent後に旧Resolver失敗を無効化。 |
| .github/workflows/km-jra-race-intent-resolver.yml | 同Race直列化、失敗checkpoint保存、既存generated-state publisherによるpush、push失敗時のartifact保存。 |
| .github/workflows/km-jra-autopilot-failure-recovery.yml | Resolver completionを既存day workerへ接続。Workflowが失敗記録をpushできなくても、実runを照合。 |
| .github/workflows/km-jra-single-entry-repair-regression.yml | 実ログFixtureのRegressionと既存保存・Binding試験をPR CIへ接続。 |

Retryは従来通り最大3要求。待機は3秒・6秒＋0〜0.75秒Jitter、要求の接続/ヘッダ/読取上限は従来30秒以内。1要求操作は105秒以内、Resolver全体は180秒以内。Retry-Afterは尊重するが残Budgetに収まらなければ停止する。制限を超えるsleep・再要求は行わない。
実障害はResolver step開始13:01:08から32.4秒後に失敗。従来30秒Timeoutと最大3回を維持し、その対象漏れを修復した。105秒は3×30＋3＋6＋Jitter＋politenessを覆い、180秒は3つのnavigationに共有する上限。10分Workflow timeoutを使い切らない。既存観測のDispatch→FINALは455〜782秒で、生存例だけの分布。15分leadは従来の受付条件を維持したものであり、全Raceの完走保証や新しい予測閾値ではない。

再試行するのは、詳細checkpointでretryableと判定され、実Workflowが同じrun_idでFAILURE、Intentなし、run attempt<2、既存Resolver期限内の場合だけ。先にdurable recovery claimをpublishし、曖昧なAPI応答では再送しない。publish中に期限を超えた場合も送信しない。標準Dispatch Window外のRecoveryであっても、15分leadと失敗checkpointの期限の早い方を守る。

## 時間制約を混同しない

東京8Rの公式postは13:55。標準Dispatch Windowは13:00〜13:25、既存Resolver受付最小leadは13:40、Prediction Cutoffは13:50、external dispatch deadlineは13:53、FINALは発走前である。
SOURCEのfreezeはSigned cutoff以前、Static freezeは既存Formalのtemporal ordering、External dispatchは既存deadline、FINALは既存PRE_FINAL_TEMPORAL_VERIFIEDをそれぞれ維持する。13:50をFINAL deadlineへ読み替えない。受付窓の延長・締切の後付け変更はしない。
東京8Rは既に期限超過。実ログに基づく失敗checkpointだけを既存`runtime/exact_gaps/KM-JRA-TKY-20261017-R08-LIVE-R1.json`へ追加した。execution_idは予定IDであり、Intent受付・Signed SOURCE・Full20・FINALの成立を意味しない。Runner Universe未確定のためrequired_index_countも未確定のまま。

## SOURCEと既存Fallback

PDF/JRADBの既存同一Authority fallbackは`runtime/jra_source_runtime/app.py`のRunner Universe取得が所有する。PDF優先、PDF未公開時は公式詳細card、両者が存在すればRunner集合を照合する。本修復で別サイトを導入せず、meeting keyを推測せず、PDFからResolver Identityを捏造しない。
正常取得済みnavigationは同じcall内で保持され、失敗要求だけを再実行する。Signed SOURCEの永続再利用は既存Single Entryの`materialize_phase`と署名/Binding/OIDC検証を通す。新たな無署名Source cacheは作らない。
東京4Rの実SOURCEをscratchへmaterializeし、既存Storeのhash検査とEd25519署名を確認した。Receipt SHAは`922a7baa9815b38ec7636967e35307d19a1dd1bee95525da45cbdf04d8a706a8`。保存済みcheckpointの全JSON bytesは不変。このオフライン確認を、新しいGitHub OIDC attestation検証とは表示しない。

## 障害を分離

| Race/範囲 | 分類 | 実証された停止箇所 |
|---|---|---|
| 東京8R | A/B/E/F/G | TLS Reset→Resolver Intent前停止→旧Status不整合。現在期限切れ、FINAL/Deliveryなし。 |
| 東京3R | C | SOURCE後BVI_STATIC_CONSUMPTION_BINDING。mainの既存PR298修復を再実装しない。 |
| 東京5R | B/E/F/G | Dispatch前Status readback import障害とclaim、期限切れ。既存main修復を保持。 |
| 新潟2Rほか | D | AKI_SELECTED_HEAD_WITHOUT_MATERIAL_PAIR。通信障害ではなくFail-Closedを維持。 |
| 他Venueの成功Race | 別lineage | 東京4R/新潟5R/京都5Rなどの既存Signed FINAL/Resultを変更しない。 |

他Raceの正式失敗、AKI見送り、期限切れ、Delivery未確認を通信復旧成功に置換しない。GitHub Workflow SUCCESSやcanonical availabilityを、人の受領とは扱わない。Deliveryの改善候補PR302はこの修復に混入させない。

## 10月18日全36Race

`evidence/jra_resolver_p0_20261017/tomorrow_36_protection.json`に全Raceの登録hash、R51、post、cutoff、dispatch/recovery deadline、既存公式観測hashを保存。
既存登録は36/36整合。最新の既存公式card観測は2026-10-17昼時点の36Race/450頭。今回の公式再取得はTLS Reset後Budget切れで失敗したので、最新取得成功を主張しない。新たな当日Signed SOURCEと取消/Runner Revisionの再照合は全Raceで必要。
Production BVI/AKI/KRS/MEC/Capital、Current Authority R51、KRS Engine/parameter_map、Source signer/Trust Anchorは変更0。新408走のProduction受入0。新潟2RのAKI Pair不成立は別案件で、列の補充やPolicy変更を行わない。未来Activation・当日予測・買い目発行は行っていない。

## 検証とReview

実Traceback Fixture＋HTTP Reset→正常、429/503→正常、恒久4xx停止、接続/読取Timeout、IncompleteRead、Budget直前停止、同Race二重Recovery防止、publish失敗・publish中期限切れの無送信、他Race継続、Workflow失敗後Status回復、成功Intentが旧失敗を上書きする状態遷移を試験。
実Signed SOURCEの再利用・byte不変性を検査。既存Full20/Static/AKI/KRS/FINAL/署名/Capital/Delivery/Settlement試験を回帰実行。最終の統合回帰は245件＋95 subtestsが全PASS。結果は同evidenceディレクトリの`full_regression.xml`に記録した。Resolver/保存/Bindingの選択回帰は68件PASS。YAML parse・各run stepのbash構文・Python compile・diff checkもPASS。GitHub CI結果は正確HEADのPR Checksで別途確認する。
実装者による差分の再点検は実施。独立した第三者Reviewは未実施であり、CIやAI自己点検を独立Human Reviewとは表示しない。既存Owner限定方式では、差分・リスク・RollbackをOwnerが確認し、正確HEADを承認するまでMergeしない。この依頼の第9項も同条件を要求している。

## リスクとRollback

通信回数は恒久エラーでは増えず、一時障害では最大3回/要求と同Run1回再試行の範囲で増える。JRA停止中は正しく失敗し、FINALを保証しない。Workflowイベント遅延/既存day worker queue/通信不能時はStatus反映が遅れ得る。実runの観測だけでは例外classを断定せず、詳細checkpointがないと自動Recoveryは行わない。
この変更はGitHub Actions側のResolver/Autopilot修復。RailwayのLOCALサービスはREADY、Deployment `2f7ddb5d-6ebe-4de7-b3d5-c70833fd4460`、served revision `655530735f24cce78605dd1bd34843bdb2ea253d`。再Deploy不要、再起動・設定変更なし。JRAの新しいActions実行SHAはMerge後の適格な実Runで確認する。
Rollbackは本PRの実行コード/Workflow変更をrevertする通常PR。Source/FINAL/RESULT、失敗履歴、OOS記録はrevertしない。障害中の曖昧なDispatch claimを消して再送しない。必要なら既存受付をHOLDし、署名済み成果物はread-onlyで保持する。秘密鍵・署名鍵・Runtimeを再配置しない。

## 残課題・判定

Merge SHA: PENDING_OWNER_EXACT_HEAD_APPROVAL。
独立Review: PENDING（既存Owner限定方式の適用判断とOwner確認が必要）。
Runtime deployment: 変更なし。JRA新コードの実Actions配置: Merge後確認。
Unknown-future Intent→SOURCE→Full20→Static→AKI→PRE_KRS→External KRS→MEC/Capital→Signed FINAL→発走前Delivery、結果後Settlement/Learning: PENDING。合成試験や既存別Raceの成功を本修復のLive Acceptanceへ転用しない。

最終判定: **PARTIAL / PRODUCTION_REPAIR_PENDING / LIVE_ACCEPTANCE_PENDING**。

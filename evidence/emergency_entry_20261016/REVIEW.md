# KAW正式受付障害・8レース比較監査 — 2026-10-16

**判定：5件の受付障害は未解消。成功経路と停止境界は特定したが、元の拒否応答がなくRoot Causeの確定・修復完了とは扱えない。**

main `4f24e44e0e8a6de96eb1ecfeeb2c39adcf971405`、既存Draft PR282 head `2323085066fff8563c2a46f71b2dddcc463fb809`から復元。今回の書込みはこの監査証拠だけ。過去の「安全チェックで拒否」という助手の文章を、実ツール応答や確定原因として再利用しない。

## 8レースの最初の差

時刻はJST。成功例の登録時刻はcommit timestampであり、登録APIの応答時刻ではない。失敗例の実操作・拒否時刻・HTTP・入力・Authority bindingはnull。詳細は `race_comparison.json`。

|Race|登録commit時刻／Run|Signed FINAL／Signed RESULT|確認できた最初の差|
|---|---|---|---|
|10/15 川崎6R|null／未観測|未観測／未観測|Race-Key登録物・Intent・Checkpointなし。元拒否traceなし|
|10/15 川崎7R|null／未観測|未観測／未観測|同じ観測境界。原因の同一性は未証明|
|10/15 川崎8R|18:11:46／38711152951|18:12:40／18:37:23|5項目JSONのmain pushが受理され、既存入口を完走|
|10/15 川崎9R|null／未観測|未観測／未観測|Race-Key登録物・Intent・Checkpointなし。元拒否traceなし|
|10/15 川崎10R|19:26:46／38720317619|19:27:34／19:48:10|5項目JSONのmain pushが受理され、既存入口を完走|
|10/15 川崎11R|null／未観測|未観測／未観測|Race-Key登録物・Intent・Checkpointなし。元拒否traceなし|
|10/16 川崎1R|14:23:51／38855562125|14:25:13／15:07:23|Owner継続承認後の既存push受付。Scheduler起動成功ではない|
|10/16 川崎7R|null／未観測|未観測／未観測|同じ観測境界。元拒否traceなし。日次自律承認は1Rのみ|

対象8Raceを母数に維持し、登録＋Signed FINAL成立3/8、期限後の未実行5/8と記録する。独立Delivery成功率はUNKNOWN、今回の未知未来修復試行成功率はN/A（未試行）。これらは予測精度・実購入利益の指標ではない。

mainの全同一Race revision、Race-Key JSONの内容、Intent、execution storeを照合し、Actionsは2026-10-15〜16 UTCの321件を4ページ全取得した。LOCAL Race-Key Workflowは8件すべてpush、10/16のLOCAL schedule Runは0件観測。削除されたRunや外部Runtimeストアの完全不存在は証明していない。HTTPリクエストがGitHubに一度も到達しなかったとも断定しない。

8R/10Rの登録commitはそれぞれ `3004adcd65e5961152f25048c16e06026de76ae9` / `cb8f2d39db8aca9f48e6e0e376090a3d5aca71ab`。登録に用いた元のChatGPTツール名とHTTP応答は成功例にも残っていない。GitHub actorだけからConnector操作名を推定しない。

1Rのtrigger SHAは `3a378cc7c46b660dad27d0c5d22b53d429926418`、entryログに記録された実checkout SHAは `ea0a24c56188473e4ffbcd97fe9b7cfff81fae83`。Runtime実装SHAは `655530735f24cce78605dd1bd34843bdb2ea253d`。この3値を混同しない。1Rは14:32:16〜14:33:21にチャット全ツリー提出の既存観測があるが、独立到達Receipt・user_received_atはnull。

## 受付経路 A–E

|経路|現在の事実|できること／残る制約|
|---|---|---|
|A ChatGPT Connector|`mcp__codex_apps__github_create_file`が公開されている。アプリ個別許可は現在Allow all actions|承認済みRaceの5項目JSONを既存main受付pathへ作成する操作は存在する。対象pathへの実受付成功と一般の証拠branch書込みは別。拒否後の別操作への切替はしない|
|B workflow_dispatch|GitHub Workflowの正式入力は5項目。ChatGPTには新規workflow_dispatch/repository_dispatchの専用操作が未公開|GitHub APIではActions writeが必要。公開されていない操作は権限増加だけでは追加されない。再実行ツールは新規Race登録の代替ではない|
|C push受付|`runtime/race_key_requests/*.json`のmain pushが既存正式経路。8R/10R/1Rで実行証明あり|既存実装はimmutable before/afterで入力を解決し、Current Authorityと実時刻cutoffを再検査。新たな非公式経路は不要|
|D Autonomous Dispatcher|既存local-day jobにcontents:write / actions:write、GH_TOKEN、dated approval、durable claim、最大Dispatch制約あり|チャットのdispatch操作を使わず開始する設計は存在する。10/16のschedule→dispatch実績は未証明。承認は1Rのみ、消費済み。7Rへの自動拡張不可|
|E Formal Single Entry|既存SOURCE取得→承認済Static→生成済Intent→orchestrator→署名工程。別の正式Intent push入口も存在|新規Race登録の代わりに手作りStatic/Intentを送らない。既存FINALがあれば読戻す。entry完了後にresult jobを待って配信を遅らせない|

今回実測したGETエラー原文は `HTTPError: 400: GitHub Fetch URL is not an allowed public GitHub repository or search endpoint. (Response: None)`。対象はWorkflow別runs一覧の**読取りURL**であり、Connectorの許可URL境界。対応するGitHub登録POST/PUTのHTTPではない。承認済みのrepository actions/runs GETで全ページを取得できた。過去の保護設定GETの403も登録拒否の原文ではない。

現在のChatGPT個別設定Allow all actionsは、当時の設定・OAuth Scope・個別操作審査の結果まで保証しない。接続再設定や広い管理権限の追加を根拠なく要求しない。必要なのは、失敗した操作の原traceの回収と、専用workflow_dispatchが必要な場合の接続提供側による正式な操作公開である。

GitHub公式仕様はdispatchにActions writeを要求する。2026-03-10版の例はHTTP200とRun IDを返すため、未取得の応答を204に補完しない。scheduleは遅延・dropがあり得るが、今回の未発生理由を高負荷と断定できない。

- https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event
- https://docs.github.com/en/actions/how-tos/troubleshoot-workflows

## 修復・検証

5件の拒否そのものは、元のtool name/input/error/HTTP/correlation IDが検索可能な履歴にも既存証拠にもないため再現不能。現在のコードから入力を捏造して同じ障害の再現成功としない。再現された原因がないためRuntime、Authority、Workflow、Pythonへの修正は0。既存PR149のRESULT checkpoint/AKI修復候補は別障害であり、受付制約を直したとは扱わない。

現行mainで既存Race-Key/Dispatcher/Static/Single Entry/RESULT recoveryを含むRegression **199 PASS**。既存PR149のCI3件は成功を読戻し（Run38847107934/954/985）、今回の新修復CIやLIVE受付成功として数えない。追加CI起動は0。

成功3例は現行Gatewayの公開鍵に対しEd25519、Receipt SHA、Artifact SHA、Race Identity、engine/parameter SHAを再検証。SOURCE/PRE_KRS/KRS/FINAL/RESULTの15署名、9Checkpoint内282ファイルのhash一致、発走前FINAL、RESULTの原FINAL・券面結合を確認した。8R180点/18,000円、10R144点/14,400円、1R156点/15,600円の保存内容は変更していない。実購入PFSはUNKNOWN。

2026-10-16 18:17:53 JSTの既存Runtime `/health` はHTTP200、Gateway assessment PASS、R51、bundle `c6508062d02389fc32900a473a2eee83566a0f1132712033002dd79697d5d25a`。新規予測送信は0。Merge/Deploy/Activation/Policy/29指数/KRS/MEC/Capital/既存Receipt/OOS変更、馬券購入、追加OpenAI有料要求、新規サービス、課金設定変更はいずれも0。Railway Soft5USD/Hard10USDは変更せず、今回の実増分費はUNKNOWN。

## 通常の一言で受け取るための既存契約

「川崎○Rのケイバメトリクス調査願います」は正式予測依頼のまま維持する。まず該当ExecutionのCanonical Checkpoint/FINALを探し、既に署名FINALがあれば原本・Race Identity・freeze・最新公式変更を検証して全ツリーをチャット提出する。result jobの完了を配信条件にしない。

承認済み未来Raceを既存Autonomous Dispatcherが事前受付・実行し、チャットはこの読戻しを行う責務分担なら、毎RaceのGitHub画面操作を必要としない。ただし現時点のdated approvalは10/16 KAW1Rのみで、任意Raceを自動受付できる状態ではない。未登録・未承認・接続拒否を新経路で埋めない。

次の独立Owner承認対象は `next_acceptance_gate.json` に具体化した。新しい公式Race Identity、Active、当時のCurrent Authority、新planSHA、Cutoff、対象1Raceのdated approval、既存schedule/Activationの個別承認が未成立なのでPENDING。古いRaceの承認・planSHA・cutoff・activationは流用しない。

完成判定は、承認された未知未来1Raceで実受付原応答とRunを取得し、SOURCE→29指数→Static→KRS→MEC→Capital→Signed FINALをcutoff前に実証し、正確な全ツリーを発走前にチャット配信、提出SHA/時刻と独立到達確認を区別し、同じFINALに公式RESULT/Settlement/Learningが閉じること。自律運用の完成を主張する場合はschedule開始→dispatch受理も実測で必要。過去3成功例や199テストで代替しない。

## 未回収の原trace

接続提供側／当該チャットの実行ログで必要なのは5件それぞれの操作名、非秘密入力、実行時刻、chat/run correlation ID、拒否原文と拒否主体、GitHubに到達したならHTTP status/request IDである。失敗の報告時刻は `race_comparison.json` に別項目で保持した。このtraceがない現在は「同じRoot Cause」「接続安全制御が確定原因」「根本修復完了」のいずれも主張しない。これは未完了箇所の明示であり、別Transportへの迂回承認ではない。

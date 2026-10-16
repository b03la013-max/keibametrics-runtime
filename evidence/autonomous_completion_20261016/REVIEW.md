# KeibaMetrics P0 自律受付・Delivery 最終監査

対象: b03la013-max/keibametrics-runtime / Draft PR #282。2026-10-16 JST。

**今回の到達点は、既存Dispatcherへの修復実装・回帰・CI・証拠保存です。Production採用と未知未来の連続成功は未達です。** Main、Runtime、Activation、既存10/16承認、cronを変更していません。旧Raceを新LIVEとして再実行していません。

## 最新Productionと変更の単位

- 最新main: `02cd804b2e1e1fbc829f1a5a49e0ce7884b88698`。開始時とコードCI完了後に再取得し一致。
- 受領時PR282: `60cc7bff06ae7daade7550a600484ac46d4eb78b`、Draft、未Merge。既存4実行ファイルの修復・206回帰・4CIの証拠は `../family_p0_20261016/` に保持。今回も同じ回帰経路を使用。
- PR280/284はMerge済み。Dispatcher、単一入口、厳格なGit永続化を再利用。
- Current Authority: `KM-FAMILY-CURRENT-AUTHORITY-20261012-R51`。LOCAL common v4.13 Rev.1、KRS v1.7 Rev.1。旧添付仕様の版を現在のAuthorityへ逆適用しない。
- KAW Production Static Ownerの対象VenueはKAWのみ。prediction/numerical/KRS/ticket/capitalへの新しい数値消費は許可していない。
- Railway `witnessstrictimage`: Deployment `2f7ddb5d-6ebe-4de7-b3d5-c70833fd4460`、ONLINE 1/1。Health HTTP200、Gateway assessment PASS。
- Runtime revision `655530735f24cce78605dd1bd34843bdb2ea253d`、bundle `c6508062d02389fc32900a473a2eee83566a0f1132712033002dd79697d5d25a`。Engine 1.1.0、parameter 0.1-provisional、Signer `KM-LOCAL-RUNTIME-ED25519-20260922`が期待値と一致。

| レビュー単位 | Commit | 内容・分類 |
|---|---|---|
| 1 | `633c0175ac69edecbea447f989488907cda90128` | 既存failure diagnosticsとその既存テスト。Runner/署名/Authority不一致を自動Retry案内からHOLDへ。非予測Correctness |
| 2 | `5a15f18dd06792609ad9e4465534d1d61b1f6f0f` | 既存Dispatcher/Intake、既存2Workflow、既存2テスト。承認対象事前登録・限定worker・dated plan push起動。運用変更として別承認が必要 |
| 3 | `9a98ac7be5f82246a01e3a5fd3fc0745251ca4f4` | 既存Discoveryの公式GETだけ最大3回Retry、原エラー保存。Dispatcher/既存テスト/Workflow除外パス |

最新コードHEADは単位3。8変更パスを上の3単位へ分離。単位2/3は前単位に依存するため、無検証の部分cherry-pickを勧めない。PR全体には以前からの監査資料・Governance候補がある。今回のコード差分を「PR全体4ファイル」とは表示しない。

## 実装した経路

公式Discoveryは `DISCOVERY_ONLY_NOT_REGISTERED_NOT_SIGNED_SOURCE` として固定する。Venue/date/race/post/cutoff/Authority/実行ID/公式snapshot/計画SHAを既存day planに保存し、登録済みとは扱わない。

新しい事前登録は `preregister_authorized_races=true` と本人の `preregistration_approval_ref` がある場合だけ有効。承認済み対象集合をstateへ固定し、既存の五項目Race-Keyと正規化済みSOURCE要求Intentをまとめて永続化する。未知のActive Runnerを確定表示しない。`runtime/formal_intents/` の凍結Static入り正式Intentは従来どおりSigned SOURCE後に生成する。受付Intentと凍結正式Intentの成功率を分ける。

登録済みKeyは、自分の計画SHA・Authority・fields hash・Intent hash・原Keyが一致した場合だけ、そのRaceの開始窓で既存workflow_dispatchへ送る。他経路のKey、他revision、改変、不整合は上書きせずHOLD。Claimを永続化してから送信し、曖昧応答後の再送はしない。RESULT待機は既存の別jobへ残す。

同じlocal-day jobを、承認済みのdated plan/approvalのmain pushでも起動可能にした。新Dispatcher・新Workflow・迂回APIは追加していない。GitHubのGITHUB_TOKENによる保存pushは再帰起動しない。実行はmain・Activation・dated approval・Plan SHA・Current Authority・KAW Owner・費用・Dispatch上限の全guardを通す。

継続workerは既定0秒。`worker_seconds` と `worker_duration_approval_ref` の明示承認がある場合だけ最大21,000秒、60秒間隔で独立したRace窓を確認する。承認変更・計画変更・Authority変更で停止する。初期10/16 Phase Bの設定値は変えていない。次回開催の起動時刻/lease/複数の起動機会は、実公式時刻と本人承認が揃ってから設定する。今回、次回cronを勝手に追加していない。

## 障害・復旧の境界

| 障害 | 今回の扱い |
|---|---|
| 公式Discovery GETのDNS/一時HTTP | 最大3回。URL、時刻、attempt、原エラー、応答snapshotを保存。署名生成POSTには適用しない |
| Runtime healthの一時通信 | 既存transport retryと最大3回preflight。送信前のみ |
| Signer/fingerprint/Authority/Runner/Receipt不一致 | HOLD。無条件Retryの案内を停止 |
| Git競合 | 既存persistを再利用。Race-local署名記録の競合は自動解消しない。失敗証拠はWorkflow artifactにも残す |
| 登録後・送信前Worker停止 | 保存済み所有KeyとIntentを再照合して開始窓で再開。模擬再起動で重複送信0を確認 |
| Claim後の停止/曖昧送信 | ActionsとCheckpointを照合。盲目的再送0。自動で全障害から復帰できるとは宣言しない |
| Signed SOURCE後の停止 | 前回修復のSOURCE/凍結Intentの段階保存を維持。承認された既存Checkpoint Resumeが可能。自動再Dispatchはしない |
| 遅延・Cutoff逸脱 | 新規開始を停止、第一停止工程と時刻を保存。既存ClaimでFINALがなければ期限切れterminal |

既存回帰は226 PASS。変更前は、事前登録欠落3件と不適切なRetry案内1件を再現。別途、Discovery DNS単発障害による停止を再現し修復。これは元のChatGPT拒否の再現ではない。最新コードHEADのCIは6/6 PASS。LOCAL/JRA互換性、Formal Single Entry、Gateway Canaryも含む。保護対象のprofiles、Signed Artifact、OOS、数値式、KRS、MEC、Capitalに今回の差分はない。

## 実Raceの事実

| 2026-10-16 KAW | GitHub登録/Intent/SOURCE | FINAL | RESULT/Settlement/Learning | Delivery |
|---|---|---|---|---|
| 1R | 既存push受付・署名chainあり | 14:25:13 JST | RESULT 15:07:23 JST、記録あり | Canonical表示記録あり。独立したユーザー到達Receiptは未確認 |
| 7R | mainにKey/Intent/Checkpointなし | なし | なし | なし |
| 10R | mainにKey/Intent/Checkpointなし | なし | なし | なし |
| 11R | mainにKey/Intent/Checkpointなし | なし | なし | なし |

7R/10R/11Rはユーザー報告として「Race-Key登録拒否」を保存。原ツール名・入力・エラー原文・GitHub HTTP・第一停止時刻を取得できていないため、拒否主体と元Root CauseはUNKNOWN。GitHubに何も届かなかったことをHTTP拒否の証明にしない。

1Rは14:22台の既存Race-Key pushから実行された。18:28台の遅延scheduleは読み戻しであり、14:00 Scheduler成功ではない。全12Race Discoveryと、承認R1だけ/最大1Dispatchは別の事実。7R等を自律実行で補完する送信承認は存在しなかった。10/15の成功8R/10Rも既存署名・券面・結果処理を保存し、失敗6R/7R/9R/11Rと合わせた10Race比較を別JSONへ永続保存した。

## DeliveryとConnector

このWork環境にはGit DataのDraft編集操作があるが、新規workflow_dispatch専用操作は公開されていない。標準ChatGPT GitHub appは公式説明でread-only。過去の拒否主体を現在の公開操作一覧から逆算しない。API操作未公開をPython/GitHub権限不具合として修復しない。

既存Canonical ArtifactとJob Summaryは、鮮度・署名検証を通過した原本から全点・Stake・総額・FINAL SHA・成立時刻・内容hashを保存/表示できる。通常の「川崎○Rのケイバメトリクス調査願います」は、登録済みRaceの状態確認→署名FINAL読み戻しとして維持する。未登録の場合は明確な未受付状態を返し、新登録を成功したことにしない。

GitHub ActionsのWeb/Email通知は選択可能だが、通常はWorkflow完了時通知。このWorkflowにはRESULT待機jobもあるため、発走前通知の保証には使えない。設定対象ユーザーの受信設定と実到達は未確認。既存コード内にSlack/Discord/Telegram等の通知先実装・設定は見つからない。新しい外部宛先へは送信していない。

ChatGPTへのSigned FINAL即時Pushは、この接続で確認できた機能ではない。既存の毎時監査タスクも発走前配送保証ではない。現在使える閲覧経路はCanonical Artifact/Job Summaryとチャット読み戻し。通知を希望する場合の候補はGitHub WebまたはEmailだが、単独ではDの到達SLAを満たさない。GitHub保存、通知送信、ユーザー到達を別々に測定する。

参照: [OpenAI GitHub接続](https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt)、[Actions通知条件](https://docs.github.com/en/actions/concepts/workflows-and-actions/notifications-for-workflow-runs)、[Web/Email設定](https://docs.github.com/en/subscriptions-and-notifications/how-tos/managing-github-actions-notifications)、[GITHUB_TOKEN再帰抑止](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)。

## 次の未知未来と完成判定

次回公式KAWは11/9〜11/13。[公式告知](https://www.kawasaki-keiba.jp/info/news/detail.html?did=3432)。この環境の11/9 DiscoveryはDNSで停止。GitHub CIからの同日公式取得は `OFFICIAL_ALL_RACES_NOT_PROVEN`。開催日だけを公式Race Identity/時刻/Runner付きPlan SHAへ代用しない。

`future_acceptance.json` に固定分母・10指標・段階拡大・停止条件を保存。実公式計画とOwner承認が未成立なので、対象集合確定・実行・成功率はPENDING。初回はPhase Bの1Race、次にPhase Cの少数Raceを提案するが、未承認Race番号を有効profileへ書いていない。

| 成果 | 判定 |
|---|---|
| A チャット新規登録から独立 | 実装・CI PASS、Production採用PENDING |
| B 承認済み全対象の事前登録 | オフラインPASS、未来公式計画・Owner承認待ちBLOCKED |
| C 発走前正式予測完走 | 既存1R実績を保持、新構成の未知未来PENDING |
| D 発走前買い目確認/到達 | 原本閲覧経路あり、実時刻付き到達実証PENDING |
| E RESULT/Settlement/PFS/Learning | 既存3成功対照の記録あり、未来継続実証PENDING |
| F 一時障害からの回復 | 限定再試行/再開/安全停止の回帰PASS、実環境回復PENDING |
| G 同じ障害の再発なし | 未知未来の固定集合で未実証PENDING |

## Owner確認・Rollback・費用

既存Governance第9節の限定Owner方式を使用する。AI監査/CIをOwner本人確認・独立Human Reviewとして記録しない。本人が正確なHEAD・上記差分・停止条件・Rollbackを確認した記録がないためMerge HOLD。今回指令も未承認Merge/Deploy/Activationを禁止している。事前登録/継続worker/起動時刻/費用はCorrectnessの包括承認へ混ぜず、dated operational approvalとして分ける。

Rollbackは、承認された運用で新しいdated approval/Activationを停止→新規Claimを止める→既存Claim/Receiptを照合→今回の実行コードを以前のreview済み版へ戻す順。署名FINAL、RESULT、凍結Intent、Race-local台帳を削除・上書きしない。主にActions clientの修復であり、稼働Runtimeの保護bundleファイル変更はない。今回Railway再Deployは要求しない。

追加OpenAI有料API要求0、新規有料サービス0、購入0、Production送信/Activation/Deploy/Merge0。既存Railway Soft $5/Hard $10への変更0。現在の実効上限・課金増分を返すBilling操作は公開されていないため、実費増分はUNKNOWN。CI実行が無料だったとは推定しない。新workerの稼働時間は費用承認が必要で、金額上限をDispatch回数で代替しない。

必要な外部操作は、(1)対象HEADのOwner本人確認と明示Merge承認、(2)公式Race情報取得後の対象集合・Plan SHA・時刻・lease・費用・Activation承認、(3)通知を使う場合の本人の通知先選択と実到達確認。過去拒否の断定には原ツールログが必要だが、その欠測を理由に未承認経路を試さない。

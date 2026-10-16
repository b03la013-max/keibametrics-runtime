# ChatGPT正式予測受付障害：実行境界監査と既存手順の修正

2026-10-16。基準main `4f24e44e0e8a6de96eb1ecfeeb2c39adcf971405`。対象は10/15川崎6・7・8・9・10・11R、10/16川崎1・7R。判定は **構造的な受付制約を確認／既存チャット手順の誤りを修正候補化／未知未来LIVE受入れは未完了**。

## 確定したこと

通常ChatGPTのGitHub連携とCodex/Work側の書込能力には区別が必要である。OpenAI公式説明は通常ChatGPT連携を読取用とし、編集・pushはCodexを案内している。本WorkセッションのGitHubツール89件には`create_file`、`create_tree`、`create_commit`、`update_ref`があるが、専用の新規`workflow_dispatch`操作はない。過去の失敗チャットのツール一覧は取得できていないため、そこで何が公開されていたかを本Workの一覧から逆算しない。

さらに現行LOCAL自律Dispatcherの承認は **10/16川崎1Rだけ、最大1Dispatch**。cronは14:00/14:05/14:10 JSTのみ。7Rの自律受付は承認されておらず、発走前時刻のオフライン再現で`NOT_AUTHORIZED_FOR_THIS_PHASE`となる。これはGuardの正常な動作であり、権限を広げずに「自律で7Rも開始できる」とは言えない。

**個々の失敗5件の拒否主体・原ツール入力・原HTTP応答は未回収。** 過去Assistantの「安全チェック」という説明は原応答ではない。5件すべて同じ拒否原因、GitHubの権限不足、Runtimeエラー、又はホストの安全拒否と断定する証拠はない。この未確定部分を上の構造的問題の証明で埋めていない。

## 8レース比較

| Race | GitHub登録／Workflow | 正式Artifact | 最初に確認できた境界 |
|---|---|---|---|
| 10/15 6R | 登録物・該当runなし | Intent、Checkpoint、FINALなし | canonical GitHub登録以前。原拒否欠測 |
| 10/15 7R | 登録物・該当runなし | 同上 | 同上 |
| 10/15 8R | 5項目JSONのmain push、run 38711152951 | FINAL 18:12:40、RESULT 18:37:23 JST | mainへの登録成立後、既存入口が完走 |
| 10/15 9R | 登録物・該当runなし | Intent、Checkpoint、FINALなし | canonical GitHub登録以前。原拒否欠測 |
| 10/15 10R | 5項目JSONのmain push、run 38720317619 | FINAL 19:27:34、RESULT 19:48:10 JST | mainへの登録成立後、既存入口が完走 |
| 10/15 11R | 登録物・該当runなし | Intent、Checkpoint、FINALなし | canonical GitHub登録以前。原拒否欠測 |
| 10/16 1R | claim後の既存push入口による1回回復、run 38855562125 | FINAL 14:25:13、RESULT 15:07:23 JST | WorkのGit Data書込から実行成立。schedule成功ではない |
| 10/16 7R | 登録物・該当runなし | Intent、Checkpoint、FINALなし | canonical GitHub登録以前。加えて自律承認対象外 |

10/15のActions全269件を3ページ、10/16の全52件を取得した観測時点の比較。失敗5件の該当実行は見つからない。10/16の他の成功runはR02とR06で、R07と混同しない。外部Runtimeの未公開ストア全件列挙はしておらず、存在しないことの証明範囲はmainと取得済みActions履歴である。

成功8R/10Rの登録commitはそれぞれ`3004adcd65e5961152f25048c16e06026de76ae9`、`cb8f2d39db8aca9f48e6e0e376090a3d5aca71ab`。GitHub actorは`b03la013-max`。使われた元チャットの書込ツール名・そのHTTP応答は回収できていない。commitとpush runは確認できるが、これを通常ChatGPT連携の書込成功証明にはしない。

原停止時刻も欠測ならnullで保持する。過去Assistantの報告時刻とGitHub監査の観測時刻は別欄にする。10/16 7Rの17:58 Cutoffは既存公式計画から確認できるが、失敗操作の原payloadがその値だったかは未証明。現在の新規受付は`SOURCE_CUTOFF_EXPIRED`で停止し、過去FINALは作らない。

## A〜Eの経路監査

| 経路 | 実際の入口・必要条件 | 観測結果 |
|---|---|---|
| A: 通常ChatGPT Connector | そのチャットに公開された書込操作が必要 | 公式仕様は読取。元5件の公開操作一覧は欠測。本Workの書込能力と区別 |
| B: workflow_dispatch | 既存workflow、main、5項目、Actions write、対象承認・期限 | GitHub機能は存在。既存Dispatcherは`gh workflow run`を使用。本Workに専用dispatchツールなし |
| C: push受付 | 認可済みContents writeでmainの`runtime/race_key_requests/*.json`を保存 | 8R/10R/1Rで実証。元の拒否を迂回する代替手段として使用しない |
| D: Autonomous Dispatcher | Activation＋日付/計画SHA/対象Race/費用/上限の承認、schedule、Actions write | 実装あり。現行承認R01だけ。10/16のLOCAL schedule runは観測されず、1Rは回復実行 |
| E: Formal Single Entry | 既存の凍結済みFormal Intentから既存orchestratorへ | 新規Race発見やConnectorへの操作公開は担当しない。Staticをチャットで捏造して渡さない |

Dispatcherは`GITHUB_TOKEN`によるclaim保存後、明示的な`workflow_dispatch`を行う。GitHubは通常の`GITHUB_TOKEN` pushによる再帰起動を抑止する一方、dispatchを例外としている。この既存設計を二重Dispatchや新しいDispatcherへ置き換えていない。

## 実際のConnector応答と権限

現セッションの`get_app_permissions(GitHub)`は、アプリ固有設定 **Allow all actions**、全体既定 **Allow low-risk actions**を返した。変更していない。この設定はGitHub AppのOAuth/Actions write権限証明でも、通常チャットへの新規操作追加でもない。

読み取り診断`github_fetch`に既存workflow詳細URLを渡した実応答は次のとおり。

```
error_code: INVALID_ARGUMENT
HTTPError: 400: GitHub Fetch URL is not an allowed public GitHub repository or search endpoint. (Response: None)
```

これはConnectorのURL受付制限。新規Race登録のHTTP拒否ではなく、GitHubサーバーからの403/404とも分類しない。`github_fetch`はGET専用であり、URLを変えてPOST dispatchを行えるわけではない。未公開操作をPythonやBrowserで迂回する試行はしていない。

必要なのは、通常チャットからの直接登録を求める場合の「認可された書込／dispatch操作の製品側公開」、又は既存Dispatcherへの対象Raceの事前承認である。GitHub repository選択・管理者承認、Contents write／Actions write、ホスト側承認を別々に扱う。すでにAllow allの設定をさらに緩める修正は存在せず、秘密トークンをチャットへ貼らせる運用にも変更しない。

## 最小修正と検証

既存`docs/KM-VENUE-CHAT-FORMAL-SETUP-20261011-R11.md`の0.5節は全場向けの記載なのに、読み先をJRAの`runtime/final_artifacts/`へ固定していた。実際のLOCAL成功3例はそのJRAパスに存在せず、LOCALの`FORMAL/LATEST.json`に存在することを再現した。

この既存文書だけを修正し、Family別正本、LOCALのmanifest/署名/時刻照合、既存`terminal_state`によるCanonical読み戻しを明記した。JRAの15分前受付条件とAKI/Full20/DCR規則をLOCALへ誤適用しないよう範囲も明示した。新規登録と既存FINAL読み戻し、通常ChatGPTとWork、自律承認と単なる計画の存在を分離した。ユーザーの「ケイバメトリクス調査願います」は変更していない。

これは**読み戻し手順の誤りの修正候補**であり、原登録拒否の原因を再現した修正ではない。既存のPython、Workflow、Runtime、Authorityに、この5件を説明する不具合は再現できなかったため変更していない。コード変更で製品側の非公開操作を追加したとは主張しない。

- 既存7モジュールのRegression: **165 PASS**。最初の4件の失敗は疎なcheckoutに含めなかった3つの既存fixtureのFileNotFoundErrorで、同じHEADのfixtureを復元して再実行した。実装・テスト変更なし。
- 既存CI **38826746181 SUCCESS**を再利用。CI HEAD `5fa4ad0667c0705b756752397079c87eacdfb984`と今回mainのDispatcher/Intake/Entry/Gate/Orchestrator/Workflowは全6ファイルのGit blob SHAが一致。今回新規CI runの成功とは表現しない。
- 8R/10R/1RのSOURCE/FORMAL/OFFICIAL_RESULT/RESULT全manifest・ファイルhashを既存`resolve_phase`で検証。
- 3例のFINAL/RESULT計6Receiptは既存Runtimeの`/verify`で各HTTP200、valid/verified=true。
- 券面のround-tripは180点／144点／156点。既存精算関数とSigned RESULTの金額が一致。新規署名、券面変更、精算履歴変更なし。
- Runtimeの現行Gateway照合PASS。Engine、parameter、Signer、Current Authorityを変更していない。

## 最終7問への回答

1. **8R/10Rと6R/7R/9R/11Rの差は何か。** 成功2例は5項目がmainに登録されてpushイベントが発生し、正式処理が動いた。失敗4例はこの境界に到達した証拠がない。拒否主体まで同じと断定する原応答はない。
2. **10/16 7Rは同じRoot Causeか。** 同じ「canonical登録前で止まった」症状。個々の拒否原因の同一性は未証明。自律R01限定承認のため7Rが補完されないことは確定。
3. **ChatGPTからの正式な新規登録操作はあるか。** 本Workには正式なGitHubファイル/Git Data書込操作があり、既存push受付に接続できる。通常ChatGPTの読取連携に同じ能力は保証されず、本Workにも専用新規dispatchツールはない。
4. **Dispatcherだけで開始できるか。** 実装上は可能。ただし対象承認と起動が前提。現状は1R限定・実schedule成功未実証で、7R以降を自律で開始できる状態ではない。
5. **通常依頼文を変えず運用できるか。** 承認済みDispatcherが事前実行し、チャットがCanonical FINALを読む分担なら可能。現在すべてのRaceで成立しているという意味ではない。
6. **どこに修復が必要か。** 製品側の操作公開、既存Dispatcherの対象/時刻の承認・運用、既存チャット手順。Runtime・予測式・KRS・MEC・Capital・Authorityの改変では解消しない。今回の差分は手順1ファイルのみ。
7. **完成条件は何か。** 事前に対象を承認した未知未来Raceで、既存scheduleからclaim→1回dispatch→Signed SOURCE→29指数の計算/中立内訳→Static→PRE_KRS/KRS→MEC/Capital→期限前Signed FINAL→原本Deliveryを実証する。その後RESULT/Settlement/PFS/Learningまで閉じる。受付前の操作/承認/HTTP応答とcommit/runを同時保存し、受領確認と表示だけの自己観測を分離する。

## 未完了・承認境界

既存R01承認・計画SHA・最大1Dispatchを維持する指令のため、同日の7R以降への拡張は行っていない。新規未知未来Raceを承認済みと見なせる記録はない。対象Race/日、既存Runtime費用範囲、最大Dispatch数、起動時間を指定した一度のOwner承認で既存Dispatcherを使う方針とし、毎RaceのGitHub手動操作は完成条件に含めない。

5件の原ツール応答・呼出し有無・適用されたホスト承認理由の回収は、元セッション側の実行ログに依存する。本監査でそのログを取得できるインターフェースは確認できなかった。既存記録の欠測を埋める偽ログや架空のHTTPコードは作らない。

今回の修正・証拠は既存Draft PR #282へ保存する。同PRへ先に追加された監査commit `c17282755a30d9e5bd03c3c4785d55be2a5132bb`の記録を保持し、`evidence/emergency_entry_20261016/local_readback/`に今回の追加検証を保存する。先行監査の199 PASSと本検証の165 PASSは別実行であり合算しない。新規PR、Merge、Deploy、Activation変更、対象拡張、追加OpenAI有料API、新規有料サービス、馬券購入は行わない。Railway Soft $5 / Hard $10は変更しない。未知未来Raceの新しいLIVE完了は未実証のため、**受付障害の完全解消とは判定しない**。

## 一次資料

- OpenAI公式: https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt
- GitHub dispatch APIとActions write: https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event
- GitHubのGITHUB_TOKENによる起動規則: https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow
- GitHub scheduleの遅延・dropの可能性: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule （一般仕様であり、今回の1R未起動の原因がdropだったという証明ではない）

詳細台帳: `race_incidents.json`、`connector_boundary_addendum.json`、`offline_boundary_reproduction.json`、`guidance_path_reproduction.json`、`canonical_preservation.json`、`ci_reuse.json`、`existing_regression_complete.xml`。全Actions履歴は先行監査の`../github_observations.json`にも保存済み。

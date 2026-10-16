# Family P0 統合・本番適用レビュー（2026-10-16）

状態：Correctness統合・検証済み / Draft / Production未変更 / 未知未来LIVE未実証。
対象Repository：b03la013-max/keibametrics-runtime。既存PR #282を使用し、新しいPR・Dispatcher・Validator・Workflowは追加しない。
コードHEAD：`029a627d784fee90b645d324728ef47b70b02d8b`。検証tree：`9e17f10ff7ca70b4faca876d5b69fec6a4def33a`。
基準main：`7997b4b860f76e4719a9d5bd65aa442f3bdf9afc`。

## A. 全12Raceと第一停止工程

公式Discoveryは12Race。Canonicalの正式成立は5/12。残り7Raceの「最初に証明できない工程」はRace-Key Registrationであり、原障害の発生場所が判明したという意味ではない。GitHub外のRuntimeストアを完全列挙したとの主張はしない。

| Race | Canonical正式経路 | 第一停止／重大失敗 | 推奨額→払戻 | 推奨PFS |
|---|---|---|---:|---:|
| 1R | SOURCE～FINAL～RESULT完了 | CAPITAL_EFFICIENCY | 15,600→15,030 | 96.35% |
| 2R | 同上 | NONE（馬番tie-breakの成功は識別精度の証明ではない） | 7,500→35,610 | 474.80% |
| 3R | Key以降未観測 | RACE_KEY_REGISTRATION未証明／原原因UNKNOWN | N/A | N/A |
| 4R | 同上 | 同上 | N/A | N/A |
| 5R | 同上 | 同上 | N/A | N/A |
| 6R | SOURCE～FINAL～RESULT完了 | PREDICTION_ROLE_P2 | 15,600→0 | 0% |
| 7R | 登録拒否報告、Key以降未観測 | 原応答欠測／拒否主体UNKNOWN | N/A | N/A |
| 8R | Key以降未観測 | RACE_KEY_REGISTRATION未証明／原原因UNKNOWN | N/A | N/A |
| 9R | SOURCE～FINAL～RESULT完了 | PREDICTION_ROLE_W | 13,200→0 | 0% |
| 10R | 登録拒否報告、Key以降未観測 | 原応答欠測／拒否主体UNKNOWN | N/A | N/A |
| 11R | 同上 | 同上 | N/A | N/A |
| 12R | SOURCE～FINAL～RESULT完了 | PREDICTION_ROLE_W | 14,400→0 | 0% |

7Raceそれぞれの原エラー、原時刻、実行主体、Run ID、失敗Artifact、失敗SHAはnull/UNKNOWN。観測対象main SHAと実際の失敗SHAを混同しない。SOURCE/Numerical/Static/PRE_KRS/KRS/MEC/Capital/FINAL/Deliveryへ架空の失敗を割り当てない。個別記録は `evidence/p0_final_integration_20261016/race_stage_audit.json`。

## B. PR統合と依存

| PR | 最新調査結果 | 今回の扱い |
|---|---|---|
| #280・#284 | mainへMerge済み | 再実装・再Deployしない |
| #282 | 最新mainをDraftへ統合。GitHub mergeable=true | P0及び最小精算Correctnessの統合先 |
| #285@2f7fa25a | mergeable=true。#282と重複するのはPFS helper 2ファイル | 当該修復だけ#282へ再利用。予測・資金候補と監査は#285へ保持 |
| #149@57a0b4d2 | mergeable=true | 4ファイルの修復を#282へ再利用。merge-treeが#282と同treeになり、追加実装不要 |
| #124@77b1d803 | 現在mainに対しmergeable=false/dirty | C2の資格・shared-store・Human Review等は別案件。今回へ混入させない |
| #262@773790a3・#263@3107a9ff | 現在mainに対しmergeable=false/dirty | AKI及びKAW研究の独立候補として保持 |
| #264@d3adf346・#265@77f849f7 | mergeable=true | 共通有限値helper以外のBehavior変更は今回の本番差分に取り込まない |

パス単位の重複は `pr_overlap.json`。git merge-treeで#282＋#285は競合0だったが、その統合treeは採用していない。Merge可能性と性能・権限の承認を区別する。#282採用後は#149の修復と#285の有限値修復を再度cherry-pickする必要はない。元PR・履歴は削除しない。

## C. Correctnessの範囲と検証

既存#282のRace別Checkpoint破損隔離、SOURCE/Intent早期保存、期限状態記録、外部再検証済みFINALだけのSummary表示、承認対象事前登録、限定worker、公式GET限定Retryを保持。
#285/#265の既存helperを再利用し、NaN/Infinity/booleanを有効なPFS・昇格証拠にしない。
#149の既存RESULT jobを修正し、OFFICIAL_RESULTだけ保存済みの中断でも厳格な既存publisherで永続化する。派生OOS保存はRESULT存在時だけに限定。精算投資額・払戻は有限・非負のJSON numberを要求し、文字列・booleanを拒否する。
欠損払戻は既存Official parserのHOLDを維持し、0払戻で埋めない。古いツリーや過去の検証booleanだけでFINALを正当化しない。元のConnector拒否がこれらのBugで発生したとは説明しない。

ローカル関連回帰284 PASS。未展開のcanonical fixtureを原mainから展開した後の結果。初回fixture欠測ログを保存し、skipや判定緩和なし。
コードHEADのGitHub CI 8/8 SUCCESS：38910202471、38910202198、38910202774、38910202275、38910202687、38910202284、38910202299、38910202669。Ingress CIは243 PASS。
既存5戦の25署名・artifact digestを現在のRuntime公開鍵に固定して再検証。RESULTのFINAL参照、精算、Reflection、Learningの金額・参照も一致。
main対比の既存Signed Artifact、Intent、Race-Key、OOS JSON、数値・Runtime bundle・Owner profile差分は0。コードtreeを一致させて外部CIへ送った。証拠追加で実行Codeを変更しない。

## D. Production適用・Owner判断

Production Merge/Deploy/Activationは0。レビュー一覧にexact-HEAD承認はなく、今回指令も「正式承認と実行権限が成立した変更のみ」と指定しているためHOLD。
限定Owner方式の本人確認をAIの監査やCI成功で代用しない。#282に以前から含まれるGovernance第9節の提案は自身の明示採用条件を持ち、保存や本統合だけでは有効化しない。独立Human ReviewはNOT_PERFORMED。
今回追加した精算Correctnessと、#282の事前登録・起動契機・worker稼働時間は別レビュー単位。後者の運用承認は日付・対象・計画SHA・時刻・lease・費用・最大回数を固定する。予測Policy・Capital変更の承認には流用しない。
主にGitHub Actions clientの変更であり、今回の差分にRailway Runtime再Deployは必要ない。

## E. Runtime・Scheduler・処理時間

公開health再取得：2026-10-16T13:38:19Z（22:38:19 JST）、Gateway assessment PASS、READY。
revision `655530735f24cce78605dd1bd34843bdb2ea253d`、bundle `c6508062d02389fc32900a473a2eee83566a0f1132712033002dd79697d5d25a`。Signer、Engine、parameter、全期待capabilityと一致。
Railway一覧は取得できたが、既存projectの環境状態・service configはviewer権限不足で拒否。最後の既知Deployment `2f7ddb5d-6ebe-4de7-b3d5-c70833fd4460` を現在のplatform稼働証明へ流用しない。現在Deployment/pending changes/BillingはUNKNOWN。

cronは14:00/14:05/14:10 JST。確認できたlocal-day Run38880716990は18:28:40 JST生成、同時刻開始。どの予約に対応したかはUNKNOWNなので遅延範囲4:18:40～4:28:40とする。三つの予約を三つの実行成功にしない。これは既存1Rの読み戻しであり、1Rの発走前FINALは別push Run38855562125による。

| Race | entry開始→FINAL署名 | Signed SOURCE→FINAL | Cutoffまでの残秒 |
|---|---:|---:|---:|
| 1R | 47.75秒 | 18.35秒 | 1,966.25秒 |
| 2R | 42.85秒 | 11.03秒 | 824.15秒 |
| 6R | 57.79秒 | 20.60秒 | 378.21秒 |
| 9R | 48.46秒 | 18.30秒 | 1,429.54秒 |
| 12R | 55.02秒 | 19.25秒 | 435.98秒 |

5例の計測はSOURCE取得全体、受付前queue、障害Retryを含む最悪時間保証ではない。Cutoff・既存minimum remainingを緩和せず、事前pushで同じ限定workerを起動する運用を使用する。無承認cron追加・常駐延長はしない。

## F. 全Race事前登録

実装・回帰は完了、Production採用・未来対象承認・複数Race実環境受入れは未完了。
dated approvalが指定するRace全件について、同一plan SHAに結合したKey・正規化SOURCE受付Intent・Authority・post/cutoff・Execution IDを永続化する。Signed SOURCE後のStatic入りFrozen Formal Intentと区別。Active Runnerはfresh SOURCEまで未確定。
同じdriverが各Raceの独立実行窓で既存Single Entryへ渡す。claimをGit保存してから送信、曖昧応答は再送しない。RESULT待ちで後続受付を止めない。署名/Authority/Runner不一致はFAIL-CLOSED。再開は既存Checkpointの検証を通す。
現在保存されている日付別承認は10/16 KAW R1・最大1Dispatch。全12Discoveryを全12送信承認に変えない。GitHub Activation変数の現在値を公開ツールで直接再確認できておらず、過去のschedule実行で代用しない。

## G. 発走前FINALとDelivery

発走前FINALは既存pushによる5例を保持。1R FINAL 14:25:13、RESULT 15:07:23 JST。
Canonical FINALを読み戻し、署名・全券面・縦型ツリー・点数・Stake・総額・成立時刻・内容hashを5戦分再現保存した。今回生成したツリーは結果後の監査表示であり、発走前配信実績ではない。
既存Summary・Canonical Artifact・mainのdelivery treeを正本閲覧経路として使用する。GitHub保存成功、通知送信、ユーザー受領を分離。通知設定・送信・ユーザー到達の実証はなく、Delivery VERIFIEDは0件、5戦の到達状態はUNKNOWN。
現在公開されたツールにはChatGPTへのSigned FINAL即時Push操作を確認できない。GitHub Web/Emailは既存の選択肢だが、本人の通知設定を未確認、RESULT待機を含むWorkflow完了通知は発走前保証にできない。新しい宛先・有料配信先は作成・送信しない。利用する宛先と、同一FINAL SHAに結合する発走前受領方法をOwnerが選ぶ必要がある。

## H. Closed Loop

Signed5戦のOfficial RESULT・Settlement・PFS・Reflection・Learningを再照合。66,300→50,640、損益−15,660、PFS76.380090%。元精算・署名は変更していない。
未成立7戦は正式推奨PFS=N/A。Actual Purchase PFSは全戦UNKNOWN。失敗Raceは実行成功率の分母から除外しない。指定4戦の58,800→15,030は25.561224%であり、5戦集計や12戦日次PFSと混同しない。

## I. 予測・Capital研究

1R Exact的中とCapital損失、6R P2欠落、9R W/P2欠落、12R W方向づけ失敗のFixtureを#285で維持。KRS併用R3のPFS17.10%とR1/R2の旧性能棄却を保持。Forwardへ復活・昇格させない。
Original AKI、#262 Reference、#265 R1/R2、MEC-R5、Capitalは別系列の凍結Evidence・券面・Stake・分母で比較する。#285の研究を#282へ混ぜず、Historical Replayと真正Forwardを分離。未知未来30戦以上・3日以上、収益性・DD・等予算/点数・Human Review等の既存Gateは変更しない。

## J. 次期LIVE受入れ

次回候補開催は11/9～13。今回のGitHub CIでも11/9 Discoveryは `OFFICIAL_ALL_RACES_NOT_PROVEN`。公式Race集合、post/cutoff、plan SHA、Owner対象承認は未成立。存在しない時刻・Runner・対象番号を推測でActivationへ書かない。
公式計画公開後、少数の明示承認Raceを固定し、全対象の事前登録率、SOURCE、Static/KRS、Cutoff前FINAL、保存/通知/受領、RESULT/Settlement/Learning、重複Dispatch、不正署名、期限違反、復旧を測定する。初回合格後に同一開催の複数Raceへ別承認で拡張。
成功率は固定対象全件を分母とする。重複Dispatch、不正署名受理、Cutoff後の新FINALは0。失敗・未受付・NO-BET・未受領を削除しない。単一成功を全Race保証へ拡大しない。

## K. 残る外部操作とRollback

1. Ownerが最終HEADの実差分・証拠・リスクを確認し、既存方式の条件を満たした採用／Merge承認を記録する。AIは承認欄を書かない。
2. 公式計画公開後、対象集合・plan SHA・post/cutoff・起動機会・worker lease・費用・最大回数・Activationを承認。旧10/16承認を流用しない。
3. 本人が通知先／閲覧経路と発走前の同一FINAL受領証跡を選択・確認する。未確認の宛先へ送らない。
4. Railway環境・pending changes・Billingの完全な再確認には、既存projectを読める接続権限の復旧が必要。公開health PASSとは別条件。

Rollback：未採用中はDraftを採用しない。採用後はOwnerの正規操作でdated approval/Activationを停止し新規claimを止め、既存claim/Receiptを照合してからレビュー済みコードだけをrevert。署名Artifact、Original FINAL、RESULT、Intent、OOSと監査証拠を削除・上書きしない。Runtime bundle不変につき本修復用のRailway再Deploy／Rollbackは不要。

追加OpenAI有料API要求0、新規有料サービス0、馬券購入0、Railway上限変更0（既存Soft $5/Hard $10維持）。Actions実行費とRailway課金増分はBilling未取得でUNKNOWN。上限や無料を推定しない。

完成判定：Correctness統合VERIFIED。Production適用BLOCKED_OWNER_REVIEW。未来対象集合BLOCKED_OFFICIAL_PLAN。発走前Delivery、複数Race継続成功、実環境復旧、長期PFS改善はPENDING。全Race保証の完成を宣言しない。

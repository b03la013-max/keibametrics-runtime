# JRA P0 実復旧・引継ぎ

2026-10-17 昼JST。これは実行証拠の更新であり、未来の全Race成功、予測改善、実購入を宣言しない。

## 別々の根本原因と修復

- 東京3R等：Full20/Static後、PRE_KRS前のBVI Static bindingで`BVI_STATIC_PROOF_BINDING_INVALID`、Exit1。Static freeze後にSOURCE追跡用3注記を追加したことによる偽hash不一致。PR298（main `4a83eb956cca6903448cf14f5ade2fbb994b2c60`）は予測意味hashから当該注記だけを分離し、注記とSOURCE/checkpointの厳密な照合は維持した。Formal最初の失敗保存とWorkflow結果によるStatus整合も修復。
- 東京5R等：直接起動したAutopilotがStatusの配信Receipt読込で兄弟runtimeをimportできず、`ModuleNotFoundError: jra_production_postresult`、Exit1。Dispatch APIより前に停止した。Scheduler非起動やAPI拒否ではない。PR299（HEAD `2daf8b30220b61555de3eced426ed3ec9f1ddceb`、main merge `bfcecabab87fe0fa8da0f2e1fa9672987bb56847`）で起動path、Race別ImportError隔離、確定no-sendだけの既存窓内Retry、古いclaimより実Intentを優先する表示を修復。
- PR299の実行コード変更は`runtime/jra_source_runtime/jra_race_day_autopilot.py`だけ。テスト変更は`tests/test_jra_race_day_autopilot.py`、`tests/test_jra_p0_20261018.py`。保護8ファイルhash不変。PR CI4/4・main CI4/4成功、継続性回帰41件成功。
- C1条件は既存第4節のOwning Family acceptance、実装独立性又は第二Family互換性、negative testsを確認。PR280限定のOwner例外方式を一般化しない。独立Human Reviewを実施したとは表示しない。現行の実装修復・審査・authorized merge指令内のJRA-only Correctnessであり、Policy/Activation承認を増やさない。

## 期限内の実救済

| Race | Formal Run | Full20 | KRS | FINAL署名JST | 正式券面 |
|---|---:|---:|---:|---|---|
| 新潟6R | 38998354986 | 300/300 | 5,000 | 12:21:56 | 4点・400円 |
| 京都6R | 38998370228 | 320/320 | 5,000 | 12:22:14 | PAPER・0点0円 |
| 東京6R | 38998381910 | 360/360 | 5,000 | 12:22:36 | 30点・3,000円 |
| 新潟7R | 38998782039 | 300/300 | 5,000 | 12:28:48 | 6点・600円 |
| 京都7R | 38998786014 | 200/200 | 5,000 | 12:28:48 | 6点・600円 |

上記5件はPRE_KRS/KRS/FINAL Ed25519署名、署名payload、Canonical券面、GitHub availability receiptを独立照合し、署名はCutoff前、公開は発走前。券面は改変していない。東京7Rは既存窓開始12:30後、重複なしを確認しIntent `2fdf1c5766d50d30d168a8837367c8a464fce27e`で開始。進行結果は最新証拠で別判定する。

東京5RはResolver最小lead15分による12:10受付期限を超え、Cutoff12:20・発走12:25も経過。元claimを保持し、`85efccd827514fa480d2a01087d934d935138014`でMISSED_WINDOW/再試行不可へ整合。期限切れ東京3R、新潟3/4R、新潟1R、東京1R、京都2Rを事前予測として再実行していない。

## DeliveryとClosed Loop

GitHub Canonical公開と人の到達は別。正式券面の公開確認済みでも、`user_received_at=null`、実購入UNVERIFIEDを保持。ChatGPTの自動即時Pushや人の既読は未証明。既存チャットへ正本リンクを提示したことを人の受領ACKに置き換えない。

東京4Rは既存Formal RESULT Run38997652821でRESULT_E2E_PASS。原FINAL `6d58951e6e2b6d76aacb5fd5816c56df99052c52b210706798497db49cc37a22`、署名RESULT receipt `d9602d09f6839abbc0571fbcae0d9a6ced0cd9984bdbcfbe17ec9bf5e7a8ae2d`、Reflection `c7b1b84337ed89c1d4db64e0602a72a71d6ed09a119962a166e5d8144cc380bc`、Learning `f4586da0ab49a72217614eb25598d772bd94a3a2e187af5845100a8e273aba07`が結合。PAPER0円、PFS=null。LearningはPREQUENTIAL-NEXT-RACE-ONLY、Policy自動変更なし。古い京都10/12R12は既存Post-Result経路の再試行もSOURCE_DNS_RESOLUTION_FAILED、Exit2。RESULT欠測をPFS0にしない。

## 10月18日36Race

公式番号付き36/36・450頭、登録hash、発走、Cutoff、Dispatch Windowを再照合。個別一覧は`race_readiness_36.json`。未来当日Intent、Signed SOURCE、Numerical、Static、AKI、PRE_KRS、KRS、MEC、Capital、FINAL、Delivery、RESULT、Settlement、Learningの実成功はそれぞれ0/36（未実行）。事前登録36/36と混同しない。WAITING36、READY0、最初の未成立工程は当日Intent/Dispatch Receipt。LIVE ACCEPTANCE PENDING。

AKI W8/4・P2=8の実例は10/17新潟2R。Head8は8→8を購入できず、4→8の有効PROTECT PairがあってもHead8の欠落を解消しない。P2 ALTERNATIVE3や肯定証拠不足4をBASEへ勝手に追加しない。正当なPolicy不成立としてFail-Closedを維持し他Raceを継続。

## 残存条件

- 修復後の新しい既存Autopilot WorkerでStatus更新と自律受付を実測。旧Pythonがmain pullだけでhot reloadされるとは扱わない。
- Railway既存KRS/CalculatorはOnline、Engine/parameter_map/署名鍵は契約一致。Docker部署metadataにapp Git SHAがなくmainとの完全配置一致は未証明。保存startCommandの不整合を理由に再起動・redeployしない。
- 人の発走前Delivery受領確認は未証明。未来36Raceの完走は未実行。
- 新408走は研究隔離、現行OOS0/30は旧7件と分離。追加費用、有料API、購入、新通知先、再署名、Policy昇格なし。

総合はP0-RECOVERY-PARTIAL。既知Correctnessの修復と実Race完走を、未来全36Raceの成功や予測改善へ拡大解釈しない。

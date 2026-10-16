# 中央版の実行保証を地方版へ導入する独立PR

2026-10-12 16:45 JST調査。基点mainは `cde95da4705ff8a647f758d74f241e5f7cdd0656`。初回取得 `dd93a866cc8c4d2e2cfacc469156b19feb7281bb` からの差分は当日autopilot状態2ファイルのみで、最新mainへrebase済み。本書・実装はCandidate PRであり、Productionへの採用・購入権限・予測性能の昇格を宣言しない。

## 正本とVenue

発効済みCurrent Authorityは [R51](../profiles/KM_FAMILY_CURRENT_AUTHORITY_20261012_R51.json)。地方はProduction Suite R3、Common Canon v4.13 Rev.1、Suite Manifest R16、Numerical Mapping v1.0／Registry v1.1、29指数63規則、MEC-R3、Engine v1.1.0を維持。CALCULATEDと許可されたRULED_NEUTRALは区別する。数値閉鎖と未知未来の予測性能、下流利用権限は別であり、R16の新規Prediction/KRS/Ticket/Capital consumption許可はfalseのまま。

Current [Routing R38](../profiles/venue_chat_routes_20261008_R38.json) のLOCAL 14場を照合した：OHI/KAW/FNB/URW/SON/HIM/NGY/KSM/KNZ/KCH/SAG/MOR/MIZ/MON。FNBは明示的なv2.1 Canon override。他13場はこのRoutingに個別Canon版の明示がないため、未確認の版を推定しない。全14場の設定行をaudit.jsonに保存。新コードは競走のAdmission/時間/保存を担当し、Venue評価規則を変更しない。大井v2.4 PR #137と旧R42系PR #136はopen・未マージで、採用しない。

R16内の`family_current_authority`文字列はR50だが、Family Guardは発効時刻でR51を動的解決する。旧snapshot文字列やJRAの継承status文言を実行完了証拠としない。設定類215ファイルのSHA-256を保存し、このPRで変更ゼロを確認した。

## 10月12日の実障害と先行修正

- [PR #254](https://github.com/b03la013-max/keibametrics-runtime/pull/254)：六時間常駐Workerの終了、予備Worker待機、京都11R起動窓の欠落、dispatch state/statusのrebase競合を修復。短時間Worker交代、Race単位の失敗局所化、確認済みdispatchのunion、表示再生成。
- [PR #255](https://github.com/b03la013-max/keibametrics-runtime/pull/255)：Numerical READYと外部FINAL待機をBLOCKEDと誤表示しない。実際の6競走の選定停止を回帰対象に追加。
- [PR #242](https://github.com/b03la013-max/keibametrics-runtime/pull/242)、[#249](https://github.com/b03la013-max/keibametrics-runtime/pull/249)、[#250](https://github.com/b03la013-max/keibametrics-runtime/pull/250)：受け渡された馬からAKIを再計算し、選定停止の適格NO_BET証明とcutoff境界を修正。JRA規則を地方へ移す権限はない。
- [PR #251](https://github.com/b03la013-max/keibametrics-runtime/pull/251)、[#252](https://github.com/b03la013-max/keibametrics-runtime/pull/252)：新馬PAPER full replayとMEC必須配線。[失敗Run 38207950295](https://github.com/b03la013-max/keibametrics-runtime/actions/runs/38207950295)のログ末尾は`TICKETS_EMPTY`。Replayの成功を事前FINALに読み替えない。
- [Run 38216955252](https://github.com/b03la013-max/keibametrics-runtime/actions/runs/38216955252)：RESULT_E2E_PASS、署名・精算SETTLED後、共有`family_prediction_utility/current.json`、`krs_oos_status.json`、`mec_r4_oos_status.json`のrebase競合で失敗。署名拒否・精算不成立とは別の保存障害である。
- [京都12R Run 38215742882](https://github.com/b03la013-max/keibametrics-runtime/actions/runs/38215742882)：既存GitHub記録に全320指数・実KRS5000・34必須工程・事前署名FINAL成功。今回地方の実レースで再現したという意味ではない。

## 移植区分と実装

| 対象 | 判定・地方側の処理 |
|---|---|
| Race Intent | 全push範囲から全Intentを列挙。従来の「ちょうど1件」制約を除去。IDとpath、Family、重複を検証。既存Static入力と権限検証は維持。 |
| scheduling／実行継続 | LOCAL Single Entryを競走別matrix、最大4並列、fail-fast=false、Execution IDごとのconcurrencyへ変更。事前処理30分上限。RESULT待機は別matrix jobへ分け、事前枠を占有しない。別Raceの失敗が成功RaceのRESULTを阻止しない。 |
| pre-start | SOURCE新規取得はcutoffとrelease deadlineの早い方まで。署名SOURCE再利用後のFORMALはrelease deadlineまで。timezone、cutoff<post、deadline<post、正の有限bufferを検証。境界時刻は停止。Replayのmodeを自動変更しない。 |
| Signed SOURCE | 地方で実装済みのcheckpoint hash、receipt/snapshot binding、受信側`/source/verify`、Race/Universe照合を維持。JRA OIDC/PDF形式を流用しない。 |
| full numerical closure | 地方の29指数63規則・完全性・未計算/HOLD拒否を回帰確認。JRA Full20やDCRを地方の計算規則に混入しない。 |
| receipt integrity | 既存SOURCE/PRE_KRS/KRS/FINAL/RESULT検証を維持。保存時、署名/競走別記録/未知pathの競合はFAIL CLOSED。force pushなし。 |
| receipt後の保存 | per-race checkpointを保持し、既知7集計viewだけをmerged race recordsから再生成してpush。scratchを退避・復元し、失敗時もcommit/stashを保全。初回forward acceptanceは個別execution artifactに残し、共有race-specific summaryをこの経路では競合更新しない。 |
| failure localization | SOURCE後の期限切れをFORMALへ正しく帰属。欠けた構造化エラーの工程・code・classを補う。PASSへ変更しない。 |
| Cache | 同一push内で同Venueの各Raceが保存keyを衝突させないようExecution IDを追加。 |

変更ファイル：`runtime/local_prestart_gate.py`、`runtime/formal_execution_orchestrator.py`、`runtime/non_jra_formal_runner.py`、`tools/local_intent_matrix.py`、`tools/persist_local_checkpoints.py`、LOCAL Single Entry Workflow、専用Acceptance Workflow、回帰テスト。

JRA固有のPDF出走表、jockey/person/pedigree収集形式、Full20/DCR第3条、AKI v2.1の列選定・NO_BET規則、新馬R51 PAPER、Static Owner、BVIモデル/血統proxyは移植しない。LOCAL側のBVI研究PR #253は既にmainの研究機能として存在するが、数値や予測利用権限を追加しない。PR #124はDraft・未マージ、調査時head `1033c818bf2451ccb9496ae017c7aea0c35ad13e`。実API成功やProduction Owner移行を新たに宣言しない。

## 検証と実証範囲

[evidence](../evidence/local_jra_execution_guarantees_20261012/audit.json)に正本、Venue行、関連PR、hash、log参照を保存。

- LOCAL関連121テストPASS：時間境界、発走後deadline拒否、無timezone拒否、12競走batch、旧Execution ID、実Git bare remoteのrebase競合と両Race保持、署名相当の競合HOLD、scratch復元、実tracker view再計算、既存SOURCE/FORMAL checkpoint、29指数、authority firewall、NAR Universe、OOS隔離。
- 中央側既存18テストPASS：全日dispatch、Worker交代、dispatch失敗局所化、実state競合、当日の6選定停止回帰。合計139件は機械的検証であり未知未来の予測実績ではない。
- ローカルPython 3.14。GitHub専用Acceptanceは3.13で同じ121件を実行しlog artifactを保存する。変更Workflowのmatrix/RESULT分離は構成テスト済み。mainでの実レース運用は未実施。
- 2026-10-12 16:45 JSTの実LOCAL `/health` GETとGateway assessmentはPASS。profile、署名鍵ID、Engine/parameter map、bundle fingerprintを現行正本と一致確認。これは現行外部Runtimeの互換性証明であり、このPRの採用、SOURCE数値閉鎖、KRS/FINAL/RESULT実競走完了の証明ではない。
- Production正本、係数、予測モデル、MEC/Capital policy、正式予測、既存署名成果物、OOS cohortは変更しない。同期されたproject `sources/`も変更しない。

## 残課題と採用条件

1. 独立PRをレビューし、採用後に適格な未来LOCAL Raceで事前SOURCE→既存Static→29指数→外部KRS→FINAL→公式RESULTの証跡を確認する。現時点でmainへは未導入。
2. LOCALの全日開催表自動発見・Static自律生成は今回追加しない。地方Production Ownerが未完成のため、JRA autopilotをそのまま有効化して既存Static入力を捏造できない。新batchは既に作成されたLOCAL Intentの受付と継続を保証する。
3. RESULT jobは同じbatchの事前job終了後に開始し、最大4並列で待機。大量batchの結果処理遅延は残るが、事前実行枠は解放される。GitHubの全体同時実行上限を超える保証ではない。
4. 既存の独立LOCAL RESULT/legacy workflowやJRA RESULT Runner自体はこのPRで置換しない。そこで発生した共有集計競合の再試験・統一は別対象。本修正は新LOCAL Single Entryの両保存箇所に配線したもの。未知またはimmutable conflictを自動採用しない。
5. Venue別Canon版がRoutingに明示されない13場、R16 snapshotのR50表記、旧JRA status文言は監査上の残差。今回の実行保証移植を根拠に正本を書き換えない。
6. Prediction Utility、較正、PFS改善、実購入Capitalの有効性は未証明。Candidate/Shadow昇格を行わない。Rollbackはこの独立PRを撤回、採用済みなら実行保証変更だけをrevertし、署名成果物と正本を保持する。

# Family Unified Execution Recasting — 実装・検証報告

状態：CORRECTNESS CONSOLIDATION CANDIDATE。Production未変更、昇格不可。Family全体の再鋳造完了ではない。

対象指示：添付「Unified Execution System Recasting / Behavior-Preserving Consolidation Directive」。Repository基準は `af4e9677e5f0a8b23ce429947a0e8e767fbee742`。このRepositoryは依頼文中の過去Production記述より更新されており、実際のCurrent AuthorityはR35、LOCAL Gateway v1.4。旧バージョンへ戻す操作はしていない。

## A. 現行 E2E Map

| 処理 | 実装上のOwner | 今回の確認 |
|---|---|---|
| Venue Intent / Authority | formal_intents、family_authority_guard、current_execution_gateway | WorkflowとCurrent pointerを読んだ |
| SOURCE→FORMALの親 | formal_execution_orchestrator | LOCALのみ。全Family単一入口ではない |
| 公式SOURCE・Runner Universe | non_jra_formal_runner → 外部 /source/manifest/local、/source/acquire、/source/verify | 二重取得実装を既存Runner内へ集約 |
| Evidence / Numerical | local_evidence_*、race_day_fast_path、numerical authority gate | 数値規則・mappingを変更していない |
| Frozen Static | Intent入力、source basis binding | 現状、親は既にFreezeされたStaticを要求する。SOURCEからStaticを生成する完全自動親ではない |
| PRE_KRS / KRS | 同Runner→現行Railway Runtime | Engine 1.1.0、parameter_map照合PASS |
| Semantic / MEC / Capital / FINAL | 同Runner、minimum_efficient_coverage、capital_policy、外部FINAL署名 | コード・policy保存 |
| Durable resume | execution_store、親orchestrator | 同一run上書きと破損FORMAL再実行を修正 |
| RESULT / Settlement / Learning | Runner RESULT分岐、local_result_from_signed_final、post_result_learning | SOURCE→FORMAL親とは別の起動経路。今回は統合未実施 |

モジュール分割は維持する。JRA/BANへLOCALの処理を無条件適用しない。全Familyの単一親化には各Familyの意味保存を別途実証する必要がある。

## B. First Failure Owner

外部Actions run **36588067035** は SOURCE段階の `SOURCE_ACQUISITION_NOT_FROZEN` で失敗した。発走予定08:18 UTCに対し15:09 UTCに新規取得しており、ログの取得データは `POST_CUTOFF / POST_START / oos_eligible=false`。これは再取得をPre-raceへ偽装する理由にならない。最新失敗をPrediction、Venue、KRSの精度欠陥とは判定しない。

直前のrun **36587350052** は既存SOURCEを利用した再実行で成功したが、FINAL署名時刻は15:04 UTC。結果前SOURCEがあることとFINALが発走前完成したことは別である。未知レース受入・OOSへ昇格しない。

## C. 重複・欠陥と具体的修正

| Finding / 原因 | Correction実装 | 検証 / 副作用 |
|---|---|---|
| SOURCE専用分岐と直接FORMAL分岐が同じ取得・検証を別実装 | `acquire_verified_source`を既存Runner内に抽出し両方から呼ぶ | 24ケースで旧2経路と取得引数・保存出力・失敗コードが一致。共有バグの影響範囲は広がるため両入口を試験 |
| `persist_phase`が同じrun IDへcopy2上書き | 同一bytes・同一revisionのretryは保存済みmanifestを維持、相違は拒否 | 旧版上書きを再現。修正版で原本保持。意図的再計算には別run IDが必要 |
| ファイル途中保存・pointer更新の非原子的処理 | 同一filesystemの一時directory→rename、pointerはreplace、phase単位lock | copy中断でも旧pointer保持。電源断耐性を保証するfsyncまでは実装していない |
| 壊れたFORMALがSOURCE成功時に再実行へ流れる | resume_planの最初でCORRUPT FORMALを分類して原本復旧へ | SOURCEがCOMPLETE/MISSING/CORRUPTの全ケースで再計算なし |
| resolve時のcross-execution path・不正manifest | Store内でidentity/path/hash/形式を確認 | cross-execution pointer、切断JSONを拒否。署名検証の代用品ではない |
| materializeがmanifest外のファイルもコピー | manifestに束縛されたファイルだけを復元 | 追加されたstale_predictionをコピーしない |

全て既存CoreのCorrectness修正であり、新Prediction仮説、加点、券選択規則ではない。次の未知Raceで見るのはSOURCE→FINAL到達、二重取得回数、checkpoint retry時の不変性、deadline前完成である。予測精度/PFS向上はまだ証明していない。

## D. 統合Architecture

採用した最小変更は「既存親orchestrator＋既存Runner内の共通SOURCE処理＋既存Store」。新Runtime、Adapter、Validator、Receipt、Authority profileは追加していない。

残す境界は Authority / SOURCE / Frozen Prediction / PRE_KRS+KRS / MEC+Capital+FINAL / RESULT。これは新しい6サービスの提案ではなく、現行コード内の責務区分である。成功した途中checkpointは再利用し、後続失敗を全段再実行の理由にしない。

## E. Disposition Ledger

`component_inventory.json` に追跡対象Python runtime/services・Workflow **251件**と参照元候補を収録（Workflow160件）。字句参照探索であり動的到達性の完全証明ではない。参照0件を削除証拠にはしていない。

| 対象 | 裁定 | 実施 |
|---|---|---|
| 親orchestrator | KEEP / REPAIR | 破損FORMAL再実行を修正 |
| Runner二重SOURCEブロック | MERGE / ABSORB | 2実装→1実装 |
| execution_store | KEEP / REPAIR | 不変保存・原子的公開・復元対象限定 |
| Static Freeze boolean / final package | COMPAT | 今回以前の正規化修正が既に存在。自分の成果として数えない |
| legacy二段Workflow・履歴profile | COMPAT | 参照・再現用途が残るため削除していない |
| Engine / mapping / MEC / Capital / Venue | KEEP | 無変更 |
| 新Runtime・追加Guard | DELETE候補 | 作成しない |
| JRA/BANの入口・RESULT親統合 | KEEP / 統合未実施 | 意味保存なしに削除しない |

## F. 修正コード

- `runtime/non_jra_formal_runner.py`
- `runtime/formal_execution_orchestrator.py`
- `runtime/execution_store.py`
- 既存テスト2ファイル更新、SOURCE集約の回帰テスト1ファイル追加。

`python research/recasting/run_checks.py` は旧版比較、上書き反例、変更禁止領域確認、保存済みReceiptのローカル署名確認を再実行する。Network acquisition / KRS新実行 / 実購入は行わない。

## G. Regression

関連 **66 tests PASS**。RepositoryのテストはFamilyごとにprocessを分離し、66ファイルすべて終了code0（pytest **276 tests** とscript形式 **15ファイル**）。詳細は `test_results.json`。

最初の全件単一process試験はJRA/LOCALの同名module import衝突、および未導入dependencyで失敗した。既存CIと同様にprocessを分離し、必要dependencyを導入して再確認した。これを単一process全件PASSと表現しない。

既知A/B/Cは既存orchestrator testsで検証済み。Dは外部失敗ログと既存Temporal/OOS試験で確認。新規修正では異常run上書き、old-run pointer rollback、途中copy失敗、path混入、破損FORMAL、manifest外ファイルの復元を試験した。

## H. External Evidence

現行Railway `/health` read-only取得でprofile、Engine、parameter_map、bundle照合PASS（`runtime_health.json`）。配置変更・秘密鍵・環境変数変更なし。

保存済みSOURCE/PRE_KRS/KRS/FINALの**4つの異なるReceipt（5ファイル）**について、取得済みHealth公開鍵でEd25519署名、receipt SHA256、artifact SHA256を全てローカル検証。公開鍵は現行endpointのHealth由来で、独立した第三者trust anchorを新設したわけではない。

外部 `/source/verify`・`/verify` POSTは当初自動承認審査に拒否されたが、9/30のユーザー明示承認後に実行した。4種類の異なるReceipt（5ファイル）すべてHTTP 200 / valid=true。SOURCEはsignature_valid・artifact_validもtrue。その他のartifact hashはローカル照合済み。結果は `external_verification.json`。

## I. Behavior Equivalence

SOURCE旧2経路×入力3形態×正常/取得失敗/署名失敗/readiness失敗＝**24/24一致**。mock differentialでありネットワークE2E同等性ではない。

数値、Engine物理、parameter_map、MEC、Capital、Venue、既存署名コードの変更は0。Receiptは再署名すれば時刻等が変わるのでbyte equalityの対象にしない。今回は保存済み署名原本を変更せず検証した。

変更された挙動は欠陥入力での `EXPECTED CORRECTNESS FIX`。Family全体のNumerical→Ticket→Settlement全値比較を完了したとは言えない。

## J. Reduction KPI

| 指標 | Before | After |
|---|---:|---:|
| SOURCE取得＋検証の実装箇所 | 2 | 1 |
| LOCAL single-entry親Owner | 1 | 1 |
| 新規Runtime / Adapter / Validator / Receipt schema | 0 | 0 |
| 新規Authority設定・新規数値parameter | 0 | 0 |
| Workflow定義（全体inventory） | 160 | 160 |
| Duplicate freeze/final carrierの正規化Owner | 1 | 1 |
| 手動Static handoff | 存在 | 存在 |
| 全Family単一親 | 未達 | 未達 |

Guard/Gate/active hotfixの厳密な実稼働総数、Race実行に必要な独立設定数は動的経路の完全調査が未了。架空の削減数を示さない。Storeの修正でコード量は増えており、Family全面削減に成功したとの評価はしない。

## K. Genuine Pre-race Acceptance

**NOT RUN / 未完**。検証に用いた9/29 R6は発走済み。未来日付を書いたsynthetic caseや履歴replayを代用しない。次の実在レースで、同一cutoff・正当SOURCE→Prediction Freeze→PRE_KRS→KRS→MEC→Canonical→署名FINALがdeadline前に閉じた証拠が必要。

Candidate未deploy、Production未promotion。次のRaceへ既に改善が反映されたとは報告しない。

## L. Remaining Risks / 完了境界

1. 親はFrozen Static入力を要求し、SOURCEからStatic生成までは所有しない。新SOURCEを取得した後に過去Staticを黙って再束縛する問題は、意味保存の確認なしに解消できない。既存Static freeze/source時刻検査を維持。
2. SOURCE時刻の再同期は既存実装。追加修正で、保存するFORMAL semantic basisを元の正規化Intentから作成し、実行時の時刻補正やdefault付与によるretry誤判定を除去した。元Intent＋署名SOURCEを束縛し、順位変更を検出する回帰試験PASS。deadline通過後の新規実行を許可する変更ではない。
3. immutable FORMAL再利用はStore hash/basis一致で返る。毎回の独立署名再検証を保証する改修は今回未実施。既存署名検証を弱めていないが、改ざんStore対策の完全性を主張しない。
4. 原子的rename/replaceはローカルfilesystemの可視性対策。process強制終了がrun公開後・pointer公開前に起きた場合のorphan復旧、複数GitHub runner間のbranch競合は追加の実運用試験対象。
5. 数値Authority未閉鎖を実行統合で「計算済み」にしない。現在profileに記載されたrequired score rules未束縛は別問題であり、今回数値式を捏造しない。
6. Prediction utility、PFS、未知OOSの改善は未測定。今回の成果は実装重複と確認可能な保存・再開欠陥の修正に限定。

**判定：限定されたCorrectness Consolidationは実装・回帰確認済み。Family Unified Execution完成、LIVE受入、Production昇格は未達。**

## 提出状態（9/30追加）

ユーザー明示承認後、GitHub接続を用いて `audit/execution-recasting` branchへ修正コード・検証資料を公開し、Draft PR #111を作成した。URL: https://github.com/b03la013-max/keibametrics-runtime/pull/111 。外部署名検証も上記の通りPASS。merge・deploy・Production昇格は未実施。Family全体統合と実レースの発走前受入は引き続き未完。

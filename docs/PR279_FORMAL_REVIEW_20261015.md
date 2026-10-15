# PR #279 正式受入れのためのHuman Review資料

判定：CODE CANDIDATE / OFFLINE REGRESSION VERIFIED / PRODUCTION NOT APPLIED / FORWARD LIVE PENDING。
対象：KAW取消・除外のSource→Static→KRS→Semantic→Ticketの同一性。Owner新設、数値式・予測Weight・Engine/parameter・MEC-R3選択則・AKI・Capital Policy・Venue Canon・Current Authorityの変更は含まない。

## 正本と権限

最新取得main：0c98b731bf8a7e4448e2c7b1b208fbb710768a59。Family Authority R51、LOCAL R3、KAW v2.4-KAW。KAW OwnerはKAW限定の明示承認済み・性能未検証Owner。R01実行main f3048ace、R02実行main b07ec98ca。PR279親 a29a8260 / baseは未マージDraft PR276@4e3c71fc。PR257は既存統合済み。C2は今回の実行条件ではない。
現行Runtimeの読み取り専用Health：200 READY、物理revision f0d23766。Health成功はCandidateコードのRuntime受入れを意味しない。キー・秘密鍵を取得/生成/回転していない。

## A/B Root Causeと修復

R02 2026-10-15、Listed8、公式取消3/7、Active6(1,2,4,5,6,8)。Signed SOURCE12:33:50.654116 JST、174/174指数終端(152計算、22規程Neutral)。旧Ownerは公式カードに残る取消行8頭とActive6頭の完全一致を要求し、OFFICIAL_CARD_RUNNER_MISMATCH。Source自体・数値6頭は正しく、Owner未承認やC2/API障害ではない。Static、PRE_KRS、KRS、FINAL、Deliveryは未成立。これを失敗履歴として保持し成功へ改変しない。

修復は既存箇所のみ：
1. local_production_static_owner：a29修復を継承。parsedとListedが一致し、除外差分がSigned SOURCEの明示CANCELLED/EXCLUDEDと一致する場合だけActive行を使う。今回さらに取消根拠のevidence_sourcesが公式・PRE_CUTOFFの保存SOURCEへ結び付くことを要求。根拠欠落・非公式根拠・不明除去はHOLD。
2. nar_runner_universe.enrich_source_artifact：オッズ表への単なる名前欠落だけでINACTIVEとした場合、既存SOURCE例外境界でHOLD。Listed/状態台帳/取得原文は残す。旧source_policyは公式betting universeをActive判定へ利用するため、この追加Fail-Closedは旧版より受理範囲を狭めるCandidate変更としてHuman Review対象。Productionのポリシーや署名済み過去SOURCEを無断変更していない。
3. minimum_efficient_coverage._active_roles：既存Role/Pair/Third入口で、実際のrequest.runners外の順位・Role・purchased_heads・Pair・Third参照を拒否。既存SOURCE→request一致検査を前提に、取消馬を買い目へ流さない。削除や勝手な代替馬追加はせずHOLD。MEC配分、券種選択、金額計算・Capital Policyは不変。

## C Stage別Universe

| Stage | 正本/適用集合 | 実証範囲 |
|---|---|---|
| 公式カード原文・Signed SOURCE | Listed、Active、取消状態と根拠、全履歴を保持 | R02掲載8/取消2/Active6の原署名・SHA維持 |
| Numerical | Signed Active | R02 6×29=174、未解決0 |
| Static順位・W/P2/P3・Pair/Third | Activeのみ | Candidate保存SOURCE再生で6頭、取消3/7なし |
| PRE_KRS/KRS Input | Active、番号・馬名ともSOURCEと完全一致 | 既存validate_krs_horsesで6頭PASS、取消3追加はHOLD |
| 外部KRS応答 | Input SHAと既存Receiptへ結合 | R01実応答保存済み。R02修復版の新外部実行は未実施 |
| Semantic/MEC/Ticket/Capital | Active参照のみ | Candidateローカル純関数再生PASS、外部参照を停止 |
| Signed FINAL/Delivery | 同一SOURCE/Static/KRS由来の正本 | R01原本PASS。R02 BLOCKED |

R02のオフライン診断で作成されるMEC/Ticket情報は無署名・非配信・非Production。正式推奨、事前券面、Forward OOSへ計上しない。

## D Temporal

R02取消根拠の公式カード/オッズ取得は12:33:46.088736 / 46.095554 JST。Source Freeze12:33:46.703678、署名12:33:50.654116より前。取消公表の正確な時刻は取得物に掲載されずUNKNOWN。
新オフライン再生時計はSigned SOURCE時刻+1秒。過去のsource-freeze+1秒という診断時計の記録はそのまま履歴として保全し、実行時刻と誤認しない。
Static後のMaterial Changeは旧Sourceへのbindingを維持できずHOLD。既存Revision/Reforecast契約で別Revisionを作るまで旧FINALを現行と提示しない。既存FINALは上書きしない。発走後の新FORMAL Staticは拒否。保存済みデータのReplayは明示的オフライン、外部要求・新署名・新Freeze・OOS加算なし。
Material Observerの実際の近接運用・配信停止/再配信は未受入れ。今回の最新公式モバイル再取得はツール404/取得不可となったため、最新状態一致を新たに断言していない。既存Bounded Taskの13:40/14:40確認と結果後継続はPENDING。

## E R01 Positive Control

147原ファイルのSHA照合済み。SOURCE/PRE_KRS/KRS/FINAL4署名とartifact hashを固定Trust Anchorで再照合。元Signed FINAL receiptSHA 0f562134594438824a0f9dc322b868d0243ead1b0ae17a9715ce4e5d66f5e20e不変。
元Source・元Static Freeze時計・保存済み実KRS Utilityを用いた再生：順位/marks/Role/Pair/Third完全一致、MEC全体(SHA含む)完全一致、156券・各100円・15600円、Capital判断(SHA含む)完全一致、正本Ticket Tree完全一致。元Artifactを再保存していない。これは元成功の非回帰証拠で新Forward成功ではない。
チャット発走前提示は保存済み。独立署名Delivery Receipt、プラットフォーム既読証明、信頼できる厳密表示時刻は未成立。

## F Regression

関連141PASS、JUnit保存。初回の4失敗は疎チェックアウトで既存Fixtureを未復元だったため、既存ファイル復元後に全件実行。実装修正でテストを回避していない。
追加ガード前の同じ対象テストでは8FAIL/24PASS：公式根拠欠落2件、オッズ欠落推測1件、Active外参照5件。修正後にこれらは既存HOLD境界で停止。a29の取消整合は以前の1FAIL/13PASS→14PASSを引き継ぐ。
指定14ケースは research/family_reliability_20261015/runner_universe_review/regression_case_map.json にProof名とオフライン/LIVEの区別を保存。
SOURCE失敗/Checkpoint欠落、安定Execution ID、相違時Resume拒否、Worker/一時Git競合の回復・Immutable競合HOLD、Race別並列・RESULT待機分離、FINAL再生成禁止、未知払戻HOLDも既存回帰を実施。

## G PR279累積修復の受入れ表

| 修復 | 修正前 | 修正後/互換性 | 外部受入れ/残存 |
|---|---|---|---|
| SOURCE停止・Checkpoint | BLOCKEDや欠落pointerから後段へ進みTypeError/古いSOURCE利用 | 原因を保持しSOURCEでHOLD、3既存ケースで後段呼出0 | Candidate。通常Source/Owner実行R01成功は旧Production経路 |
| FINAL Read-back | 保存FINALがあってもSource/Static再実行へ入る | 正本検証後読戻し、再実行0、変更basisはHOLD | 保存R11/R12既存受入れ証拠継承。新Production配置なし |
| Canonical Tree Delivery | FINAL成立とチャット配信を混同 | Renderer round-trip、券種/点数/stake一致 | R01チャットリンク提示あり、署名Delivery Receiptなし |
| Deadline/Resume/Worker | 締切超過/競合/RESULT待ちによる阻害 | 既存Guard・race-local store・分離Workflowで検証 | 多Race外部全日LIVEは未成立 |
| 欠落払戻 | 的中払戻欠落/0をCOMPLETE戻り0へ誤精算 | 署名送信前RESULT_WINNING_PAYOUT_NOT_READY | Candidate。公式RESULT自動取得経路は既存3券種完全取得必須 |
| 取消整合 | 掲載8≠Active6でStatic停止 | 公式取消差分だけ除外、根拠・下流境界を検証 | 修復版外部KRS/FINALは未成立 |

## Human Reviewで判断する事項

- PR276依存とPR279累積Correctness差分を確認。PRのbaseへのclean状態をmain統合済みと混同しない。
- KAWの既存Owner権限内のCorrectness修復であり、予測政策/実証成熟度を昇格しない。
- SOURCEのより厳しい曖昧欠落HOLDを明示審査。Active公式情報不整合を無理に補完しない。
- Runtime側nar_runner_universe変更はSource bundle SHAが変わる。現行R51/Gatewayのfingerprintとの整合を、別途承認されたリリース手順でレビューする。今回Authority/Gateway pointerを書き換えず、Deployしない。
- Client側Owner/MEC境界、依存PR、Runtime側SOURCE修復を実行経路へ反映する承認が必要。CIだけで配置済みとは扱わない。
- 承認後、Cutoff前の正規Race、正本Runtime、指定データの送信承認、最新取消/時刻/馬体重/Runner再確認、同一basisでCheckpoint再開。新Material情報なら旧SOURCE/FINALを書換えず契約上のRevisionへ進む。R02の過去失敗は残す。
- 複数未知未来のSOURCE→Signed FINAL→発走前Deliveryと結果後Closed Loopを取得するまでは本番信頼性完成・全Family成功を宣言しない。

## H/I/J 現在の終端状態

新LIVE：BLOCKED。R02送信承認は既存Runtime/対象データへ成立しているが、修復のProduction適用は未承認。別Raceへの承認拡張なし。
R01：元Signed FINAL保持、14:45発走前なのでOfficial RESULT/Settlement/PFS/First Material Failure/Dominant Loss Owner/LearningはPENDING。
R02：正式FINALなし。結果取得後は失敗/Integrity回帰用資料のみ、正式推奨PFS0%を作らない。Actual Purchase PFS UNKNOWN、正式結果Learning/SettlementはBLOCKED。
OpenAI要求0、課金変更0、新規有料リソース0、馬券購入0、Production merge/deploy/activation0。既存Runtimeの限界従量費用はUNKNOWN。
本資料の提出はHuman Review完了や承認ではない。CODE CANDIDATE、CI、外部Runtime配置、LIVE、署名Delivery、結果閉ループを独立して判定する。

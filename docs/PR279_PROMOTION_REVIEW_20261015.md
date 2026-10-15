# PR279 Production昇格審査 — 2026-10-15

**REVIEW PENDING / NOT MERGE-READY / NOT DEPLOY-READY**。本資料の完成はHuman Review承認ではない。
旧PR279_FORMAL_REVIEW_20261015.mdの詳細Root Cause/時刻/署名/14ケース対応表を継承し、本資料のA/B分類と配置判定を優先する。

## 正本・全変更監査

監査元24af04cf20a89f6903970c9c1f733ffa3e3f10d5、base4e3c71fc1765027f45299cd2b406228f41d20ad8（未マージDraft PR276）。103変更ファイルのパス・blob・分類はresearch/family_reliability_20261015/promotion_review/full_change_inventory.json。文書・Evidence/ZIP・テスト・実行コード・運用Snapshotを区別した。
最新main取得f711e999（完全SHAはinventory）。24af対mainのmerge-tree成功、tree408df8c40b450d62f50ebe7baaed309afcde9abf。PR baseへのmergeable=trueはmain統合済みを意味しない。
R51 / LOCAL Suite KM-LOCAL-RENDERED-INTEGRITY-20260827-R3 / KAWv2.4。現行Common v4.13 Rev.1・KRSv1.7 Rev.1はR51を優先し添付旧版へ戻さない。既存KAW-only Authorized-Unvalidated Ownerの性能を昇格しない。
実LOCAL /health200 READY、物理revision f0d23766b1d2e4cefc6194458b0e9141d5479cbc、現行appSHA e54ae7ad31a1959df113568f6d1591e9753971f30fccac5325e627e07e52f12b。Candidateは未配置。

## Correctness / Behavior分離

A昇格審査対象：SOURCE停止/Checkpoint、Immutable FINAL読戻し/検証/正本ツリー、Deadline/Identity/Worker分離、払戻欠損/返還未対応HOLD、公式明示取消のOwner整合、Active外Role/Pair/Third/MEC/FINAL拒否。
正しい取消処理による旧不具合からの出力差はCorrectnessとして扱う。正常R01のStatic/Role/Pair/Third、MEC全体SHA、Capital全体SHA、券面は一致。数値式・予測Weight・Physics・Engine/parameter・MEC選択則・AKI・Capital Policy・Venue Canonを変更していない。profiles/mapping/governanceに本PR差分なし。

**Bを分離**：オッズ表名前欠落によるINACTIVEをSOURCEで一律HOLDする5行は、現行DECLARED_RACE_CARD_PLUS_ACTIVE_OFFICIAL_BETTING_UNIVERSE契約の受理範囲を狭める。実行モジュールから除去し、対応テストを現行契約へ復元。コードと専用テストの差分を `source_acceptance_narrowing_NON_PRODUCTION.patch` へ保存。独立Candidate・非実行・自動適用なし。旧24afのBテスト成功を現行Aの成功と混同しない。KAW Ownerは取消根拠不明のINACTIVEを勝手に除去せずHOLDするためR02明示取消の修復は維持。

tools/local_kaw_day_audit.pyは保存ID/別台帳集計で、失敗/研究/aliasを保持し未知未来へ換算しない。Canary Workflowは既存R51表示訂正とPASS確認でAuthority変更なし。pedigree_backfill_cursor/canary_statusは過去運用SnapshotでリリースAuthorityではなく、最新mainの運用状態を巻き戻す対象ではない。過去署名Artifact/OOSは削除しない。

## 修復別監査

| 箇所 | 障害・原因 | 修正/検証 | 残存 |
|---|---|---|---|
| local_race_entry SOURCE | BLOCKED/欠落pointerでも後段へ進みTypeError/旧SOURCE利用 | 原因保持HOLD、3失敗再現→後段呼出0 | Production未配置 |
| entry/orchestrator | FINAL存在時SOURCE/Static再実行 | 正本manifest/semantic/source basis照合、相違HOLD | 中間IntentのAUTO再開は不一致の場合あり。RESULT専用経路使用 |
| local_race_key_gate | 保存flagだけを署名証拠と混同/ツリー未表示 | 既存Gatewayで新鮮なverify、Identity、同rendererの券面/stake | 独立署名Delivery Receipt未成立 |
| Deadline/Worker/Store | 遅延・RESULT待機・Git競合・Race混線 | 既存guard/安定ID/checkpoint/並列/一時競合復旧、immutable競合HOLD | 外部複数Race全日LIVE未達 |
| local_result_from_signed_final | 的中払戻欠損/0をCOMPLETE return0 | 欠落/別券種/0は署名前HOLD、正の正当払戻は不変 | 自動公式取得は既存3券種完全性必須 |
| orchestrator RESULT | 取消行省略により返還曝露を損失扱い | 凍結対象馬取消/除外/番号不明はREFUND_REQUIRED | 返還計算を追加せずHOLD、deadheatもHOLD |
| static_owner | R02掲載8対Active6で停止 | Listed一致・差分が公式PRE_CUTOFF根拠付き取消集合と一致した場合だけ6頭 | 不明除去HOLD |
| minimum_efficient_coverage | Active外Role/heads/Pair/Third | 既存入口でHOLD、正常MEC/Capital全体SHA一致 | 既存Source/request一致前提 |
| app_v15.final | Signed ActiveとFINAL参照不一致 | 署名検証後/Signer前に422、正常R01payload未変更 | 非署名stubテストは外部署名受入れではない |

## R02・R01・Temporal

R02：Signed SOURCE12:33:50.654116JST、receiptfa082a7dfcb923b1c994d20b4eb744aa34e3a66bbb5c42ac3019a6c8dcf3a06d。Listed8、公式取消3/7、Active1,2,4,5,6,8、Numerical174/174。取消を含むcard/odds観測12:33:46.088736/095554、SOURCE Freeze12:33:46.703678前。正確な公式取消公表時刻UNKNOWN。
元LIVEのSTATIC/OFFICIAL_CARD_RUNNER_MISMATCHを保持、Static Freezeなし/KRS0/FINALなし/Deliveryなし。修復再生は保存SOURCE・署名後+1秒の診断時計で6頭一致、KRS入力/semantic/MEC/Ticket/Capital確認。外部KRS、新署名、未来OOSへ算入しない。
Static後Material Changeはbinding不一致HOLD、旧FINAL不変。添付KAW第228条のSTALE→SUPERSEDED→新prediction_id/Reforecastに従う。発走後FORMAL再生成禁止。真の近接Revision運用はPENDING。

R01：147原ファイルSHA、4署名/artifactSHA、Numerical348/348、Static11:42:35、実KRS5000、FINAL11:43:30JST、receipt0f562134594438824a0f9dc322b868d0243ead1b0ae17a9715ce4e5d66f5e20eを保持。156点/15600円推奨と正本ツリー一致、元予測再生成なし。チャット発走前提示観測済み、独立署名Delivery/既読/厳密表示時刻なし。
72 checkpoint/intentファイルを衝突0で復元。既存 `--resume-official-result --result-wait-seconds 0` は元SOURCE/FINALを読み13:29JSTにWAITING_OFFICIAL_RESULT / OFFICIAL_RESULT_NOT_DUE / prediction_reexecution=false。発走14:45前なのでRESULT/Settlement/PFS/First Material Failure/Dominant PFS Loss Owner/LearningはPENDING。公式払戻不足はHOLD。Actual Purchase PFS UNKNOWN。R02の正式推奨PFSnullを0%で代用しない。既存Bounded Taskで両Raceを独立継続する。

## Merge/Deploy審査とRollback

| Gate | 実結果 |
|---|---|
| PR | Draft、24af mergeable=true、PR276依存未解決 |
| CI | 24af check-runs12件successを再取得。前回10Workflow集計とは別単位。分離後HEADはPR本文で別報告 |
| 必須check指定 | main/protection読取401。設定未確認、実check成功と混同しない |
| Human Review | reviews一覧0件、未承認 |
| Runtime互換 | app_v15新SHA ccb7af22beb13a1304715d967ceb32e48819f1b170bd1d53cd0ec87d6161974c。現行Gateway/R51 fingerprintとは異なりリリース整合審査必要 |
| Source module | B分離後d2ab387d6ce20bff26b86e3be341fda0777b984a1ff664dc688ee0fde523b7cb、現行一致 |
| Receipt | 既存anchor/keyid/Envelope schema/署名は不変。新handlerの正式外部署名未受入れ |
| Merge/Deploy承認 | 本依頼は承認ではない。未実施 |

**NOT MERGE-READY / NOT DEPLOY-READY**。PR276依存、必須check指定、Human Review、Runtime release fingerprint整合、明示承認が未完。
承認対象の確定順序：A差分/B除外/依存PRのHuman Review→所有者による必須checks確認→正確commitとwrapper/bundle/Gateway整合差分の審査→明示Merge/Deploy承認→既存サービスへリリース→実Deployment SHA/Health/Canary/旧Receipt/署名前拒否の確認。今回Authority/Gateway pointerは変更しない。Clientだけ適用し下流未配置を完成としない。
Rollback基準は旧既知revision f0d23766と旧bundle・公開Trust Anchor。承認済み既存リリース手順だけで戻し、新SOURCE/FINAL/RESULT/失敗台帳は削除しない。旧取消Bugへ戻るため該当RaceはHOLD維持。指紋不一致・署名不正・404/503は受付HOLD、鍵やAuthorityを自動変更しない。

## 適用後LIVE・複数Race

Race別送信承認・正本Runtime・費用条件を確認し、個別post/cutoff・取消/除外/騎手/斤量/馬場/馬体重・Runner Universeを再取得。KAW Ownerの他Venue転用禁止。旧R02失敗は保持、締切超過後に事前FINALを作らない。
1RaceでSOURCE→Static→PRE_KRS→実KRS→MEC/Ticket/Capital→Signed FINAL→外部Verify→正本Deliveryを行い、全SHA/署名/実時刻/run数/Deploymentを記録。取消がなければ通常LIVEのみ成功、取消LIVEはPENDING。
続いて同日複数Raceの独立deadline/worker/checkpoint、RESULT待ち中の後続dispatch、Git競合復旧、重複dispatch/FINAL再生成0、配信retryを検証。全失敗/HOLD/締切超過、第一停止工程、復旧時間を母集団へ残す。
結果後公式RESULT/払戻完全性→署名→Settlement/PFS/Learningまで独立完了。Replay/CI/単一成功を全日/他Family成功としない。

## 成果物A–J

A全差分監査COMPLETED、B分離COMPLETED、CR02回帰VERIFIED(offline)、DR01保全VERIFIED、EClosed Loop PENDING、FMerge BLOCKED、GDeploy BLOCKED、HLIVE計画COMPLETED/実証PENDING、I複数Race条件COMPLETED/実証PENDING、JCIは正確HEAD/runをPR本文に記載。
追加OpenAI要求0、課金変更/新規有料リソース/秘密送信/馬券購入/Production変更0。既存Railway従量費用UNKNOWN。C2/API/Owner性能昇格は本審査対象外。

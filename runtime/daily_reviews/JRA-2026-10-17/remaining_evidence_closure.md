# PR #305 Remaining Evidence Closure / 実行保証

継承HEAD: `470bb61b9beb2e397079e2925d2ceb9905d0c9fb`。最新main: `d7ae23a07f7e872957085ef2bf72cf794a0c316f`。R51は実行時に再解決。JRA Static Ownerは `OWNER_AUTHORIZED_UNVALIDATED`、登録時Forward OOS=0、Market優位未証明という実際の承認条件を維持する。

| 対象 | 確認 / 修復 | 未完了 |
|---|---|---|
| SOURCE OIDC | 34/34件が独立Sigstore/OIDC検証PASS。東京11RはAPI制限解除後に原Bundle回復 | なし |
| KRS Output | 原23件がReceiptのcanonical SHAと一致。実行時にcanonical SHA / 構造化Outputの結合を強制する修復を追加 | Owner承認Mergeと次の未知Raceでの受入 |
| KRS Input | 正確に送信するUTF-8 JSON bytesとそのSHAを送信前に保存するcheckpointを追加。既知の宣言済み入力hash契約は内容照合、未知契約は拒否 | 追加照合で23/23原Receiptがrace.prediction_id補完後のsorted UTF-8 SHAと一致し、署名も23/23検証。別sidecarの内容結合を実装。Owner Mergeと次未知Raceの受入は未完了 |
| Runtime | health READY、Engine / parameter_mapは既存契約と一致。Railway image-based Deployment ID確認 | App Git SHA / 実コードfingerprintはUNVERIFIED。CIやEngine hashで代替しない |
| 署名原本 | SOURCE34、PRE_KRS/KRS/FINAL23、RESULT原Envelope19を検証。RESULT workflowの原本always-uploadとoptional診断前保存は既にmainに存在 | 東京4R・京都5R・新潟5Rの古いRESULT原本3件はGitHubと可視Base44 Logから未回復。再生成・再署名しない。京都12Rの同着manual hold維持 |
| Delivery | 発走前Signed FINAL23、Canonical可用性23。元の公開時刻を再timestampしない | ユーザー受領ACK0確認。観測経路にChatGPT自動Push実装なし。経路承認なしに外部送信しない |
| Learning | 22件既存保存、36件のunsigned review revision。明示的な投資0がUNKNOWNになるfallbackを修復 | 次Race消費0確認。新Shadow Intakeは準備済み、Production数値への適用なし |

修正コード: `runtime/jra_production_krs_contract.py`、`.github/workflows/km-formal-request-runner.yml`、`runtime/race_day_fast_reflection.py`。未知未来準備: `runtime/jra_learning_intake.py`、`runtime/jra_role_rescue_shadow.py`。予測係数、AKI v2.1、KRS Physics、MEC-R3、Capital Policy、署名済み原本は変更しない。Rollbackはこのコード/Workflow差分をrevertし、凍結予測・公式結果・証拠は保持する。

既存Commonの9つの事前登録定義hashは不変。JRA専用計測補正を既存Common cohortへ遡及混合しない。独立ReviewとOwnerの対象HEAD承認は未取得。Merge/Deployment/Activationなし。修復の実行時有効性とLive Acceptanceは次の適格未知RaceまでPENDING。

## 全36Raceの失敗分類

`prediction_failure_matrix.json` はFormal未成立13件も含む全36件。Execution Failureを不的中に加算しない。First Material FailureとDominant PFS Loss Ownerを分離し、因果的な損失配賦はUNDETERMINEDを維持する。Production19件のW捕捉3/19、P2 10/18、P3 12/18、Pair/Exact0/18。京都12Rの非一意順序は元母数へ混入しない。

AKI比較は `aki_incremental_comparison.json`。同一Source・同一指数・同一順位を確認できたFrozen Candidate Owner比較は20件。役割捕捉の消失3件・追加6件を観測したが、Candidate raw owner hashはProduction Proofと一致しないためProduction AKI不具合・因果効果と断定しない。新潟2R等のPair不成立は正式Fail-Closedを維持し、Shadowでも無断のP2追加やPair生成を行わない。

KRS23実行/115,000runの既存比較は `krs_incremental_utility.json`。過去候補を作り直さず、既存Static支持をUnique Rescueにしない。新しいone-per-column案は `krs_unique_role_shadow_replay.json` と固定コードに保存した研究Replayで、Production追加券0・追加資金0。Forward OOSには0件算入。

BVIは既存 `bvi_consumption_review.json` を継承。入力454頭に実測433・実測+DCR8・DCR-only13。下流Ledger28Race376頭は実測359・混合6・DCR-only11で、6件のBinding失敗を下流消費に数えない。ABC30件はA=B。血統408走の隔離維持、増分精度/PFSは未実証。

## 資金比較

正式推薦PFSの母集団は19件の正投資FINAL（336券）、PAPER FINAL4件は投資0、FINALなし13件は仮想投資を作らない。実購入PFSはNOT VERIFIED。唯一の払戻は京都11RのPROTECTION TRIO9,100円であり、Winner/Pair/Exactを捕捉した成功とは読み替えない。

| 研究Replay arm | 投資 | 払戻 | PFS |
|---|---:|---:|---:|
| A_CURRENT_PRODUCTION | 33600 | 9100 | 27.0833% |
| B_SELECTIVE_CORE_ONLY | 23400 | 0 | 0.0000% |
| C_AKI_TRIGGER_SELECTIVE | 23400 | 0 | 0.0000% |
| D_STATIC_TOP3_BOX | 11400 | 2110 | 18.5088% |
| E_SOURCE_MARKET_TOP3_BOX | 11400 | 10690 | 93.7719% |

Aは過去の正式推薦再精算。B-Eは研究Replayで、ACTUAL/Productionの別成績へ昇格しない。D/Eのみ6点×100円で同予算・同点数。A/B/Cは資金差があるためPFSだけで同予算優位を主張しない。B/Cは京都11Rの既存保護的中を失うため、Production昇格候補としてREJECTし、研究の負の対照に限る。Winnerを発見できなかったRaceはCapital削減で予測改善したことにならない。

Aの最大払戻依存100%、最大払戻Race除外PFS0%、Top3払戻Race除外PFS0%、最大drawdown24,500円、zero-return連続14Race、hit-but-loss0。CORE/PROTECTIONとVenue/券種別は元の `pfs_grand_review.md` / `supplemental_metrics.json`。因果的な『Capitalで失った円額』は凍結対照なしに断定しない。

## 次Race / Venue

`preregistered_shadow_comparison.json` に候補別ID、コードSHA、アルゴリズム、比較条件、Primary/Secondary Metric、負の対照、False-positive Cost、資金影響0円、60 distinct Race・3開催日・2Venueの設計Pilot、Stop/Reject、Owner Promotion Authorityを固定した。これはpower計算ではなく、30/60到達で自動昇格しない。署名・同一時点・同一Source/Runner Universeを要求し、過去10月17日を未知未来OOSへ数えない。稼働ActivationはOwner審査待ち。

東京・京都・新潟はHOLD。東京/京都添付条項はCandidateでありProduction正本へ置換しない。新潟のrace-time Venue fingerprintは未回復。Pace/Position/Corner/Closing等の事前Mechanismは複数日Frozen OOSとPositive Controlを要し、Common問題をVenue係数へ転写しない。

## 成果物の対応

1. Remaining Evidence Closure: 本書 + `execution_assurance_closure.json`
2. KRS Hash / Runtime / Receipt: 本書 + `evidence/jra_day_review_20261017/runtime_contract_readback.json`
3. Delivery / Learning: `delivery_learning_consumption.md` + closure JSONの全36行
4. 全36Race Failure Matrix: `prediction_failure_matrix.json`
5. AKI/KRS/BVI: `aki_incremental_comparison.json`、既存KRS/BVI Review、`krs_unique_role_shadow_replay.json`
6. Capital/Robust PFS: `capital_research_comparison.json` + 既存Grand Review
7. Venue: `venue_canon_verdict.json`
8. Correctness: 既存 `improvement_backlog.json` / .md を更新
9. 事前登録: `preregistered_shadow_comparison.json`（hash固定、NOT ACTIVATED）
10. Next-Race Learning: 既存day namespaceの36件review revisionと `next_race_learning_index.json`

判定: CORRECTNESS PARTIAL / PREDICTION REVIEW PARTIAL / CAPITAL REVIEW COMPLETE / LEARNING CLOSED LOOP PARTIAL / LIVE ACCEPTANCE PENDING。

追加の原本回復調査: KeibaMetrics ConsoleのExecutionReceipt / ExecutionRun / ExecutionArtifact / LedgerIndexを当該3Raceで読み取り照会し、可視レコード0件。KRS京都11Rのpayload Logも可視0件。これは認証ユーザーの可視範囲であり、全システム上の不存在を断定しない。RuntimeConfigのJRA2経路は既存契約と一致。Builder・Sandbox・署名・データ変更は行っていない。詳細 `evidence/jra_day_review_20261017/receipt_recovery.json`。


## Runtime起動証拠の追加照合

RailwayのDeployment `7c7eeb5e-3b5b-496a-b66f-82bd71897d53` の2026-10-14 06:16:02Z起動ログから、`KM_RUNTIME_BLOB_SHA` の第1値 `1c453a5b0e8b5e4689b4a73d18128f54c7ed0e205db5b0c58b3dd229c264a989` を取得した。後続2値は既存Engine / parameter_map SHAと一致する。ただしログ生成元の実装を取得できず、第1値のhash対象範囲・現行稼働プロセス全コード・Git commitとの結合はUNVERIFIED。現行追跡ファイル14,570件とローカル履歴の候補blob16件に一致なし。この探索範囲を全履歴の不存在と解釈しない。

保存済みstartCommandは診断出力後`SystemExit(9)`となる一方、当該Deploymentの起動ログはuvicornの起動とhealth 200を示す。これは以前のP0証拠にも存在するconfig/deployment差異であり、今回の操作で発生したものではない。`get_service_config`でも同じ保存設定・stagedなしを確認した。設定変更は次回Deploymentで反映され得るため、稼働中のREADYだけで次回配置の安全性を判断しない。再起動・再配置・変数変更は実施していない。

OAuth経路の環境変数は値非公開。コードblobを取得できず、legacy Input SHAの対象範囲の確定にも到達していない。署名Receiptのhashを一致する値へ置き換える処理は行わない。送信bytesの不変checkpointと宣言済み契約の厳密照合は将来の追跡を改善する修復であり、過去23件のInput SHA検証完了とは扱わない。原ログ・設定・照合範囲は `evidence/jra_day_review_20261017/runtime_boot_readback.json` に保存した。

コードHEAD `58ec50282964eb438f56315e8464dd24dae32764` の9件のCIは全SUCCESSを再確認。GitHubのPR Review一覧は0件。追加差分は上記証拠・説明のみで、Productionコード・凍結済みShadow定義・署名原本・数値Policyは変更しない。Owner承認・Independent Review・配置元と起動設定の結合・未知未来Live Acceptanceは未完了。


## 追加解決：legacy Input SHA

後続調査で、Runtime v1.3.1の既存23原Receiptすべてが、input_data.race.prediction_idをouter race_idで補完したsorted/compact UTF-8 JSONのSHAと一致した。23原ReceiptのEd25519署名とreceipt SHAも独立検証PASS。これは既存入力内容の結合を回復した証拠であり、過去のexact HTTP wire bytesの回収やApp Git SHA確認ではない。

`runtime/jra_krs_legacy_input_binding.py` とFormal Runnerへ別の入力結合gateを追加。既存Shadowが固定するcontractコード・14定義・登録SHAは変更しない。未知Runtime/schema、identity競合、内容不一致はFail-Closed。原Receiptを変更せず、送信前identityチェックと送信後normalized SHA照合、独立/verifyを組み合わせる。外部20,000回CIにも同じgateを接続し、synthetic fixtureの内外Race IDを一致させた。詳細 `evidence/jra_day_review_20261017/legacy_krs_input_hash_closure.json`。上記のlegacy未解決という記述は、この後続証拠により解消されたが、Runtime Git照合・Delivery・Learning閉路は未解決のまま。

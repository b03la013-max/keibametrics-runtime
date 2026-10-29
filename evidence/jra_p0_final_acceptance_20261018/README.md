# JRA 2026-10-18 P0最終受入記録

観測時刻：2026-10-17T01:11:36.538424+00:00。対象は登録済み36レース。PR #295・#296のMergeを再確認した。

**総合判定：BLOCKED／最終受入未成立。** 各レースの現在状態はWAITING 36件、READY 0件、実行済みの当日障害BLOCKED 0件。公式馬番付き集合は36/36件・450頭を観測。全36件で登録頭数とも一致。実配置アプリケーションのGit SHA照合と、10月18日実SOURCE以降の受入は未成立。WAITINGは将来の正常完走保証ではない。

確認したmain SHA：`1700c71a305dcb1e1dc69572c26a5fab0116842b`。PR #296から23Commitは10月17日の実行データのみで、Productionコード・Authority・Mappingおよび10月18日Artifactに変更なし。

## 実入力によるAKI判定

10月17日新潟2Rの実Production SOURCEとIntentを、R51の承認済みAKI実装で読み取り専用再実行した。240/240指数成立後、`AKI_SELECTED_HEAD_WITHOUT_MATERIAL_PAIR`を再現。元のProduction Runは38985972079、headは`a4a2b9cd85b196c2a1bd9581c964103ac0f77dd2`。SOURCEのEd25519・snapshot bindingはローカル再検証済み。OIDCは保存済みPASSの参照であり今回の独立再認証ではない。

| 列・条件 | 実際の選定 |
|---|---|
| W・REVIEW（ASI=40） | 8、4 |
| P2・BASE（P2-AKI=0、RSI=0） | 8 |
| P3・BASE | 8、4、3 |

8番を1着にすると2着候補が同じ8番しかなく、8→8は正しく除外される。P2 anchorの4番は肯定支持群が1件で規定の2件未満。3番は支持群2件だがgap=0.847890925のALTERNATIVEで、P2 BASEでは不採用。8→3のcompatible証拠は存在し、欠落・誤結合ではない。この実入力では登録規則間の組合せ不成立と判定した。3番の追加、8番の削除、閾値変更は予測Policy変更に当たるため実施せず、Fail-Closedを維持する。

過去の実正式入力2件（京都2026-10-11 7R／12R）は同じ登録AKIで通過し、全W候補に異なる馬のmaterial pairがあった。これらは保存後のローカル検証であり、新規Production実行・未知未来OOSではない。10月18日のAKI通過率は未検証。

## 配置・Authorityの証拠範囲

- R51とAKI・BVI Mapping・Static・KRS bridge・MEC・Capitalの保護対象8ファイルのSHA-256が前受入時と一致。AKI実行時のAuthority／Registry／Compiler fingerprint照合も実入力で通過。
- 実SOURCEの署名内16モジュールSHAがmainコードと一致。元Production Runから継承mainまでの変更では当該計算コードに変更なし。GitHub Actions側の数値・Static・AKI・MEC・Capitalと、Railway外部KRSを区別する。
- 実HealthのKRS engineとparameter_mapはR51参照契約の期待SHAと一致。公開署名鍵も既存検証値と一致。parameter_mapはPROVISIONAL_UNCALIBRATED。
- 保存済み正式2レースのPRE_KRS／KRS／FINAL計6ReceiptのEd25519署名とReceipt hashを現在の既存公開鍵で再検証した。KRSの実5000回ReceiptのEngine／parameter SHAも現Healthと一致。これは過去実行の証拠であり、当日実行の代用ではない。

- RailwayのKRS配置IDは`7c7eeb5e-3b5b-496a-b66f-82bd71897d53`、Calculatorは`c05f3e85-18ae-4147-821e-97f224c2258c`。双方SUCCESS／live／stagedなし。ただしイメージ配置にGit commit SHAがなく、Health revisionからもアプリGit SHAは証明不能。配置IDをGit SHAの代用にしない。再配置・再起動は未実施。
- Calculatorの保存起動設定はmainからコード取得、KRSの保存起動設定と稼働Healthには再起動時の再現性懸念がある。現在の稼働が正常でも、保存設定から安全に同じサービスを再現できるとは未確認。設定を変更していない。

## 36レース別判定

時刻はJST。全行の正式実行可能性は「条件付き・未証明」。公式番号観測は署名済み当日SOURCEではなく、取消・変更を含む当日の再取得が必要。日付前に実行済みと扱わない。

| Race Identity | 発走 | Cutoff | 観測馬番数 | 状態 | 最初の未成立工程 |
|---|---:|---:|---:|---|---|
| KM-JRA-NGT-20261018-R01 | 09:40 | 09:35 | 13 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-TKY-20261018-R01 | 09:45 | 09:40 | 12 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-KYO-20261018-R01 | 09:55 | 09:50 | 13 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-NGT-20261018-R02 | 10:05 | 10:00 | 15 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-TKY-20261018-R02 | 10:15 | 10:10 | 10 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-KYO-20261018-R02 | 10:25 | 10:20 | 7 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-NGT-20261018-R03 | 10:35 | 10:30 | 13 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-TKY-20261018-R03 | 10:45 | 10:40 | 12 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-KYO-20261018-R03 | 10:55 | 10:50 | 12 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-NGT-20261018-R04 | 11:05 | 11:00 | 15 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-TKY-20261018-R04 | 11:15 | 11:10 | 16 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-KYO-20261018-R04 | 11:25 | 11:20 | 15 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-NGT-20261018-R05 | 11:55 | 11:50 | 15 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-TKY-20261018-R05 | 12:05 | 12:00 | 8 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-KYO-20261018-R05 | 12:15 | 12:10 | 5 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-NGT-20261018-R06 | 12:25 | 12:20 | 15 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-TKY-20261018-R06 | 12:35 | 12:30 | 8 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-KYO-20261018-R06 | 12:45 | 12:40 | 18 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-NGT-20261018-R07 | 12:55 | 12:50 | 18 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-TKY-20261018-R07 | 13:05 | 13:00 | 12 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-KYO-20261018-R07 | 13:15 | 13:10 | 9 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-NGT-20261018-R08 | 13:25 | 13:20 | 15 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-TKY-20261018-R08 | 13:35 | 13:30 | 16 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-KYO-20261018-R08 | 13:45 | 13:40 | 12 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-NGT-20261018-R09 | 14:00 | 13:55 | 14 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-TKY-20261018-R09 | 14:10 | 14:05 | 9 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-KYO-20261018-R09 | 14:20 | 14:15 | 8 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-NGT-20261018-R10 | 14:35 | 14:30 | 18 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-TKY-20261018-R10 | 14:45 | 14:40 | 9 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-KYO-20261018-R10 | 14:55 | 14:50 | 10 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-NGT-20261018-R11 | 15:10 | 15:05 | 10 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-TKY-20261018-R11 | 15:20 | 15:15 | 13 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-KYO-20261018-R11 | 15:40 | 15:35 | 17 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-NGT-20261018-R12 | 16:00 | 15:55 | 10 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-TKY-20261018-R12 | 16:10 | 16:05 | 16 | WAITING | 当日Intent／Dispatch Receipt |
| KM-JRA-KYO-20261018-R12 | 16:30 | 16:25 | 12 | WAITING | 当日Intent／Dispatch Receipt |

## 既存運用への引継ぎ

既存の事前受付36件、Dispatcher、Single Entry、Checkpoint、署名Receipt、PR #296のProduction優先Shadow制御を継承した。現時点では新規起動・新規実行経路・外部KRS呼び出し・新規通知・購入を行っていない。新規408走は研究専用のまま、Productionへの受入0件。追加費用とProduction Policy変更0件。

事前登録36件と当日正式Intent／Dispatch Receiptの成立は別。10月18日の正式Intentはまだ0件で、全Raceの実起動Windowは未到来。番号付き集合が成立したRaceの最初の未成立工程は当日Intent／Dispatch Receiptで、その次のデータ依存が当日Signed SOURCEである。

当日の順序は、既存当日Intent／Dispatch Receipt→正式SOURCE→Full20→Static／AKI→PRE_KRS→外部KRS→MEC／Capital→Signed FINAL→既存Delivery。研究A/B/Cは正式処理の余裕がある場合だけ既存Shadow経路を使用し、間に合わなければ延期する。予測不成立に候補の水増しは行わない。署名済みSOURCE／FINAL／RESULTを書き換えない。

10月18日の正式受付・SOURCE・Numerical・Static・KRS・FINAL・Deliveryの実行成功数はまだ0。RESULT・Settlement・Learningは未到来。BVI実測寄与頭数、当日DCR処理数、当日A/B/C凍結数、当日Forward OOS適格数は未実行でありPASSを付けない。旧27頭・旧OOS成績を当日に流用しない。

公式PDFは新潟の既存URLを1回確認したがHTTP403で取得できず、アクセス拒否を迂回・連続再試行していない。番号付き集合の受入根拠は公式HTML出馬表である。初回未確認記録と公開後の再取得記録を別々に保持した。

## 再現証拠

- `race_acceptance_36.json`：全Race、時刻、hash、馬番付き出走集合、最初の未成立工程。
- `official_cards_observed.json`：公式ページの観測URL・日時・decoded HTML hash（元HTTP bytes hashではない）。
- `aki_real_input_replay.json`／`aki_role_feature_diagnostics.json`：実入力の停止再現と各列の採否理由。
- `aki_actual_controls.json`：過去実入力2件の正常通過。
- `deployment_alignment.json`／`source_runtime_hash_comparison.json`／`runtime_health.json`／`health_contract_comparison.json`／`protected_component_hashes.json`：配置証拠と限界。

実行コードに変更を加えていないため、新たなSynthetic Test件数を成果としない。実データの署名・hash再検証、元入力不変検証、承認コードでの停止再現／正常対照を受入根拠とした。CI結果はRuntime受入の代用にしない。

# JRA 2026-10-17 Daily Formal Review

監査時刻 2026-10-17T08:19:29.361663+00:00。Git snapshot `70e4f366ed3610c6fec452a8c9ff6f6eac705fb8`、Status snapshot 2026-10-17T17:14:25.793642+09:00。対象36、公式結果36/36、払戻7券種36/36。

正式FINAL23件と、未成立13件を分離。PAPER4件はFINAL23に含む。Execution障害8件、AKI Pair不成立3件、正式AKI NO-BET2件。失敗Raceへ仮想Production券面を作成していない。

## 実行

| Stage | 件数 / 36 |
|---|---|
| AKI | 25/36 |
| Capital | 23/36 |
| Delivery | 0/36 |
| Full20 | 34/36 |
| Intent | 34/36 |
| KRS | 23/36 |
| Learning | 22/36 |
| MEC | 23/36 |
| PRE_KRS | 23/36 |
| Published_before_post | 23/36 |
| SOURCE | 34/36 |
| Settlement | 22/36 |
| Signed_FINAL | 23/36 |
| Signed_FINAL_before_post | 23/36 |
| Signed_SOURCE | 34/36 |
| Static | 29/36 |


## 予測

| 指標 | Production推薦 | PAPER | 全Signed FINAL（参考） |
|---|---|---|---|
| P2 | 10/18 | 1/4 | 11/22 (50.00%) |
| P3 | 12/18 | 1/4 | 13/22 (59.09%) |
| W | 3/19 | 1/4 | 4/23 (17.39%) |
| ordered_exact | 0/18 | 0/4 | 0/22 (0.00%) |
| ordered_pair | 0/18 | 0/4 | 0/22 (0.00%) |
| top3_set_in_role_union | 6/19 | 1/4 | 7/23 (30.43%) |
| top3_set_in_static_top3 | 1/19 | 0/4 | 1/23 (4.35%) |


勝ち馬平均Static順位 6.000。市場相対順位差 -1.043（正=改善。同じSigned SOURCEに保存された発走前の公式人気との比較。最終人気の診断はRace別に分離）。

Winner捕捉4件はいずれも正解P2を落とし、Ordered Pair/Exactは0件。京都12Rは2着同着のためP2/P3/Order指標と着順別KRS診断はPENDING、該当分母から除外。公式複数払戻に基づく全券精算は完了。候補Role集合のTop3捕捉を着順識別成功と扱わない。京都11RはW外の勝ち馬が三連複保護券に含まれた的中であり、Winner識別成功ではない。

## AKI / KRS / BVI

AKI Pair不成立は新潟2R・京都1R・京都3R。現行PolicyのFail-Closedを維持。過圧縮・過拡張の因果責任は比較基準なしに断定しない。KRS実行23件、計115,000回、raw output hash検証23/23。

KRSのUnique actionable Role Rescue 6件、false-positive Role提案59件。Role-zone比較Rescue 18、潜在Harm 0。いずれもShadow評価。正式TicketへのRescue変換0、Productionへの削除Harm0。

旧Utility summaryのStatic Role結合不整合は23/23件。凍結FINALのRoleとSSR-T3を使って今回の診断を訂正し、旧署名Artifact/既存Learningは保持。Engine入力SHAの実際のシリアライズ規約は未解決で、入力hash独立一致をPASSとしない。

消費Ledger 28/34実行Race。MEASURED 359頭、MEASURED_PLUS_DCR 6頭、DCR_ONLY 11頭。34件の凍結数値入力での分類は {'MEASURED': 433, 'MEASURED_PLUS_DCR': 8, 'DCR_ONLY': 13}（下流消費の成立とは分離）。A/B/C凍結診断30件、BVIのA=B 30件。追加情報の改善実証なし。研究408走は隔離。

既存BVI伝播LedgerではBVI scalarはTPIへ直接、SRI/F3S/T3Iへ間接に入るが、ZAI_WIN/ZAI_PLACEへの直接項はない。血統Featureが他指数へ入る共有効果と、BVI単独scalarの寄与を混同しない。A/C差は未知未来の精度改善証明ではない。

## Capital / PFS

正式推薦の全336券を再精算。投資33,600円、払戻9,100円、損益-24,500円、加重PFS 27.0833%。実購入NOT VERIFIED。PAPER0円のPFS=null。

| Venue | 投資 | 払戻 | 損益 | PFS |
|---|---|---|---|---|
| KYO | 7500 | 9100 | 1600 | 121.33% |
| NGT | 14500 | 0 | -14500 | 0.00% |
| TKY | 11600 | 0 | -11600 | 0.00% |


| 券種 | 点数 | 投資 | 払戻 | PFS |
|---|---|---|---|---|
| EXACTA | 89 | 8900 | 0 | 0.00% |
| TRIFECTA | 175 | 17500 | 0 | 0.00% |
| TRIO | 72 | 7200 | 9100 | 126.39% |


払戻は京都11Rの三連複9,100円だけ。最大払戻依存100%、同Raceを投資ごと除外するとPFS0%。Top2/Top3除外も0%。最大DD 24,500円、最大無払戻連続14Race（有投資Race、発走順）。Hit-but-Lossは0件。的中1件は利益6,200円。

CORE投資23,400円・払戻0円。PROTECTION投資10,200円・払戻9,100円。CORE_ONLYへの事後短縮は当日の唯一の払戻を失うため、成功したSelective Capitalとは評価できない。負けRaceの点数を減らすだけではWinner Discoveryは改善しない。

## Failure

| 分類 | Race数 |
|---|---|
| AKI PAIR INFEASIBILITY | 3 |
| EXECUTION / RECEIPT FAILURE | 6 |
| NO MATERIAL FAILURE | 2 |
| P2 DISCOVERY FAILURE | 4 |
| RACE INTENT / DISPATCH FAILURE | 1 |
| SOURCE / RESOLVER FAILURE | 1 |
| WINNER DISCOVERY FAILURE | 19 |


東京3Rを含む初期6件はSOURCE後のBVI Static proof bindingで停止。東京5RはStatus読戻しimport失敗が受付を妨げた。東京8Rは公式HTTPS resetとResolver終了のStatus未伝播。期限切れの回復FINALは作成していない。失敗Raceの機会損失は8回の正式実行機会であり、架空の投資損失へ金額化しない。

## 再利用できる成功と限界

34件のSigned SOURCEと全馬20指数の保存、23件の発走前Signed FINAL・同一券面公開を確認。PAPER情報Gate4件とAKI Fail-Closed5件は資金曝露を抑止した。これらは実行/安全制御の証拠であり、新しい予測法則の成功証明ではない。京都11Rの保護三連複は正のRegression Controlとして保持する。

## 次Race / Canon

次Raceへ渡すのは既存仕様のCorrectness課題、証拠不足、Shadow仮説と比較計画。10月17日の結果由来Learningを既に発走したRaceへ遡及適用しない。同日馬場情報は翌日の固定Featureへ持ち越さず、新たな公式SOURCEで再取得。東京・京都・新潟のCanon改定はすべてHOLD。

Production Base/Derived/BVI/AKI閾値/KRS Physics/parameter_map/MEC/Capitalは維持。添付候補文書を現行本番Canonへ昇格しない。Runtime Deployment Git SHA、Race-time Venue Canonの独立Fingerprint、SOURCE OIDC bundle、購入/受領/次Race消費は未確認。

## 完了判定

| 段階 | 判定 |
|---|---|
| DATA REVIEW | COMPLETE |
| PREDICTION REVIEW | PARTIAL |
| CAPITAL / PFS REVIEW | COMPLETE |
| LEARNING REVIEW | PARTIAL |


| 軸 | 評価 |
|---|---|
| Formal | SEVERE FAILURE |
| Prediction | FAILURE |
| Capital | SEVERE FAILURE |
| Learning | MIXED |


全体完了とはしない。公式全件取得と精算は完成、Predictionの一部Authority/入力証明・Learningの署名依存/Deliveryは未完。詳細はcompletion.jsonとmissing_artifacts.json。

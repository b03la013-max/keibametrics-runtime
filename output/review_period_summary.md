# 地方版 週次 2026-W47（自動・推薦試算・実購入なし）

- 反省済みRace 237／PAPER PFS 60.2%／正式推薦 PFS 94.8%
- 第一失敗：{'NONE': 34, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 54, 'PREDICTION_ROLE_W': 75, 'PREDICTION_ROLE_P2': 37, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 36 | 56.2 | 36.0 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 5, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 7, 'EXACT_ORIENTATION': 1} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 22 | 63.0 | 36.9 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 6, 'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 6, 'NONE': 2} |
| SON | 36 | 23.6 | 56.9 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 237 | 33.8% | 69.2% | 33.8% | 16.5% | 13.9% | 11.0% | 23.6% | 1.56 |
| 正式推薦 | 199 | 33.2% | 62.3% | 62.3% | 71.9% | 100.0% | 62.3% | 30.2% | 1.4 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中35.7%（無作為9.7%、差+26.0）／P2 平均1.0頭 的中17.1%（無作為9.7%、差+7.4）／P3 平均1.0頭 的中14.0%（無作為9.7%、差+4.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中67.2%（無作為28.9%、差+38.3）／P2 平均6.0頭 的中71.3%（無作為57.9%、差+13.5）／P3 平均10.67頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.63/40（選択性補正込み）・能力順位 14.04/20（57R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.01/40（選択性補正込み）・能力順位 13.74/20（50R平均）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 99 | 473,930 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 67 | 250,260 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 46 | 234,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 237 | 932,560 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 4 | 22,410 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 週次 2026-W48（自動・推薦試算・実購入なし）

- 反省済みRace 125／PAPER PFS 56.5%／正式推薦 PFS 39.8%
- 第一失敗：{'PREDICTION_ROLE_P2': 22, 'CAPITAL_EFFICIENCY': 45, 'PREDICTION_ROLE_W': 49, 'NONE': 9}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 13 | 22.5 | 76.6 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 5, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 26 | 30.5 | 32.7 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'NONE': 3, 'PREDICTION_ROLE_P2': 5} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 21 | 99.9 | 50.4 | {'PREDICTION_ROLE_W': 11, 'NONE': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 7} |
| URW | 30 | 77.8 | 34.0 | {'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_W': 11, 'NONE': 2, 'PREDICTION_ROLE_P2': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 125 | 30.4% | 64.8% | 30.4% | 10.4% | 11.2% | 5.6% | 23.2% | 1.48 |
| 正式推薦 | 125 | 30.4% | 60.8% | 60.8% | 73.6% | 100.0% | 60.8% | 41.6% | 1.47 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中30.4%（無作為9.4%、差+21.0）／P2 平均1.0頭 的中10.4%（無作為9.4%、差+1.0）／P3 平均1.0頭 的中11.2%（無作為9.4%、差+1.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.8%（無作為28.3%、差+32.5）／P2 平均6.0頭 的中73.6%（無作為56.6%、差+17.0）／P3 平均10.83頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.87/40（選択性補正込み）・能力順位 13.72/20（125R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.99/40（選択性補正込み）・能力順位 13.32/20（125R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 6,000円（6.1%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）31R・着順まで的中 1R／的中 43R のうち的中赤字 21R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 53.9%（同じ125Rの実績 56.5%）／券種別 EXACTA 46点 PFS 5.9%／TRIFECTA 80点 PFS 7.4%／TRIO 643点 PFS 54.1%／WIDE 214点 PFS 93.7%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 61R PFS 51.1% 的中赤字 10/20／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 56R PFS 55.9% 的中赤字 11/20／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 123R：実績 53.7% − ミラー 43.6% = Δ 10.1pt（95%区間 -14.0〜36.7、最高1R除き 4.7pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 286,900円（38.3%）／保護層の資金比率 0.0（125R）／組だけ的中（三連単は外れ）38R・着順まで的中 19R／的中 67R のうち的中赤字 56R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 49.2%（同じ125Rの実績 39.8%）／券種別 EXACTA 1875点 PFS 47.2%／TRIFECTA 3125点 PFS 22.5%／TRIO 2500点 PFS 55.9%／荒れ度（発走前・1番人気オッズ）MID 61R PFS 45.0% 的中赤字 22/28／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 56R PFS 37.2% 的中赤字 30/35／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 123R：実績 40.1% − ミラー 73.0% = Δ -32.9pt（95%区間 -65.0〜-1.1、最高1R除き -39.7pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、20R×3券種）：購入 7／予算で削除 0／予想で除外 17／未生成・券種なし 36／役割馬の行き先 {'PURCHASED': 60}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、20R×3券種）：購入 25／予算で削除 9／予想で除外 16／未生成・券種なし 10／役割馬の行き先 {'PURCHASED': 147, 'BUDGET_COMPRESSED': 74}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 9R／W外 11R、2着が P2 役割 0R）：STATIC 0/9（平均4.33位）／STYLE_COND 1/9（平均4.11位） 救済1・喪失0／MARKET_COND 0/8（平均4.25位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 15R／W外 5R、2着が P2 役割 12R）：STATIC 12/15（平均3.73位）／STYLE_COND 12/15（平均3.53位） 救済0・喪失0／MARKET_COND 12/14（平均3.07位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 56 | 204,080 | RECURRING |
| P1:ROLE_W_MISS | P1 | 49 | 259,380 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 22 | 132,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 125 | 552,080 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 362／PAPER PFS 58.9%／正式推薦 PFS 74.0%
- 第一失敗：{'NONE': 43, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 99, 'PREDICTION_ROLE_W': 124, 'PREDICTION_ROLE_P2': 59, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 37 | 75.6 | 60.5 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 26 | 30.5 | 32.7 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'NONE': 3, 'PREDICTION_ROLE_P2': 5} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 57 | 52.8 | 54.5 | {'PREDICTION_ROLE_W': 27, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_P2': 8, 'NONE': 5} |
| URW | 30 | 77.8 | 34.0 | {'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_W': 11, 'NONE': 2, 'PREDICTION_ROLE_P2': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 362 | 32.6% | 67.7% | 32.6% | 14.4% | 13.0% | 9.1% | 23.5% | 1.53 |
| 正式推薦 | 324 | 32.1% | 61.7% | 61.7% | 72.5% | 100.0% | 61.7% | 34.6% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.1%（無作為9.6%、差+23.5）／P2 平均1.0頭 的中13.8%（無作為9.6%、差+4.2）／P3 平均1.0頭 的中12.6%（無作為9.6%、差+3.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中64.0%（無作為28.6%、差+35.4）／P2 平均6.0頭 的中72.5%（無作為57.2%、差+15.2）／P3 平均10.75頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.42/40（選択性補正込み）・能力順位 13.82/20（182R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.28/40（選択性補正込み）・能力順位 13.44/20（175R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 6,000円（6.1%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）31R・着順まで的中 1R／的中 43R のうち的中赤字 21R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 53.9%（同じ125Rの実績 56.5%）／券種別 EXACTA 46点 PFS 5.9%／TRIFECTA 80点 PFS 7.4%／TRIO 643点 PFS 54.1%／WIDE 214点 PFS 93.7%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 61R PFS 51.1% 的中赤字 10/20／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 56R PFS 55.9% 的中赤字 11/20／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 123R：実績 53.7% − ミラー 43.6% = Δ 10.1pt（95%区間 -14.0〜36.7、最高1R除き 4.7pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 286,900円（38.3%）／保護層の資金比率 0.0（125R）／組だけ的中（三連単は外れ）38R・着順まで的中 19R／的中 67R のうち的中赤字 56R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 49.2%（同じ125Rの実績 39.8%）／券種別 EXACTA 1875点 PFS 47.2%／TRIFECTA 3125点 PFS 22.5%／TRIO 2500点 PFS 55.9%／荒れ度（発走前・1番人気オッズ）MID 61R PFS 45.0% 的中赤字 22/28／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 56R PFS 37.2% 的中赤字 30/35／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 123R：実績 40.1% − ミラー 73.0% = Δ -32.9pt（95%区間 -65.0〜-1.1、最高1R除き -39.7pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、20R×3券種）：購入 7／予算で削除 0／予想で除外 17／未生成・券種なし 36／役割馬の行き先 {'PURCHASED': 60}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、20R×3券種）：購入 25／予算で削除 9／予想で除外 16／未生成・券種なし 10／役割馬の行き先 {'PURCHASED': 147, 'BUDGET_COMPRESSED': 74}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 9R／W外 11R、2着が P2 役割 0R）：STATIC 0/9（平均4.33位）／STYLE_COND 1/9（平均4.11位） 救済1・喪失0／MARKET_COND 0/8（平均4.25位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 15R／W外 5R、2着が P2 役割 12R）：STATIC 12/15（平均3.73位）／STYLE_COND 12/15（平均3.53位） 救済0・喪失0／MARKET_COND 12/14（平均3.07位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 148 | 733,310 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 123 | 454,340 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 68 | 366,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 362 | 1,484,640 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

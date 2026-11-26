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

- 反省済みRace 127／PAPER PFS 60.7%／正式推薦 PFS 39.6%
- 第一失敗：{'PREDICTION_ROLE_P2': 22, 'CAPITAL_EFFICIENCY': 45, 'PREDICTION_ROLE_W': 51, 'NONE': 9}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 13 | 22.5 | 76.6 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 5, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 26 | 30.5 | 32.7 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'NONE': 3, 'PREDICTION_ROLE_P2': 5} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 22 | 112.3 | 50.5 | {'PREDICTION_ROLE_W': 12, 'NONE': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 7} |
| URW | 31 | 82.5 | 32.9 | {'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_W': 12, 'NONE': 2, 'PREDICTION_ROLE_P2': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 127 | 29.9% | 63.8% | 29.9% | 11.8% | 11.0% | 5.5% | 24.4% | 1.49 |
| 正式推薦 | 127 | 29.9% | 59.8% | 59.8% | 74.0% | 100.0% | 59.8% | 41.7% | 1.48 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中29.9%（無作為9.4%、差+20.5）／P2 平均1.0頭 的中11.8%（無作為9.4%、差+2.4）／P3 平均1.0頭 的中11.0%（無作為9.4%、差+1.6）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中59.8%（無作為28.3%、差+31.5）／P2 平均6.0頭 的中74.0%（無作為56.6%、差+17.4）／P3 平均10.83頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.92/40（選択性補正込み）・能力順位 13.75/20（127R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.91/40（選択性補正込み）・能力順位 13.32/20（127R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 6,000円（5.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）33R・着順まで的中 1R／的中 45R のうち的中赤字 21R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 53.4%（同じ127Rの実績 60.7%）／券種別 EXACTA 46点 PFS 5.9%／TRIFECTA 80点 PFS 7.4%／TRIO 657点 PFS 59.9%／WIDE 218点 PFS 94.9%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 63R PFS 60.2% 的中赤字 10/22／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 56R PFS 55.9% 的中赤字 11/20／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 125R：実績 58.0% − ミラー 42.8% = Δ 15.2pt（95%区間 -8.8〜43.4、最高1R除き 9.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 291,700円（38.3%）／保護層の資金比率 0.0（127R）／組だけ的中（三連単は外れ）39R・着順まで的中 19R／的中 68R のうち的中赤字 57R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 49.3%（同じ127Rの実績 39.6%）／券種別 EXACTA 1905点 PFS 46.5%／TRIFECTA 3175点 PFS 22.1%／TRIO 2540点 PFS 56.2%／荒れ度（発走前・1番人気オッズ）MID 63R PFS 44.4% 的中赤字 23/29／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 56R PFS 37.2% 的中赤字 30/35／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 125R：実績 39.9% − ミラー 72.5% = Δ -32.6pt（95%区間 -65.5〜-0.6、最高1R除き -39.3pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、22R×3券種）：購入 9／予算で削除 0／予想で除外 17／未生成・券種なし 40／役割馬の行き先 {'PURCHASED': 66}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、22R×3券種）：購入 26／予算で削除 9／予想で除外 20／未生成・券種なし 11／役割馬の行き先 {'PURCHASED': 161, 'BUDGET_COMPRESSED': 81}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 9R／W外 13R、2着が P2 役割 0R）：STATIC 0/9（平均4.33位）／STYLE_COND 1/9（平均4.11位） 救済1・喪失0／MARKET_COND 0/8（平均4.25位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 15R／W外 7R、2着が P2 役割 12R）：STATIC 12/15（平均3.73位）／STYLE_COND 12/15（平均3.53位） 救済0・喪失0／MARKET_COND 12/14（平均3.07位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 57 | 206,940 | RECURRING |
| P1:ROLE_W_MISS | P1 | 51 | 268,240 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 22 | 132,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 127 | 560,940 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 364／PAPER PFS 60.4%／正式推薦 PFS 73.7%
- 第一失敗：{'NONE': 43, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 99, 'PREDICTION_ROLE_W': 126, 'PREDICTION_ROLE_P2': 59, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 37 | 75.6 | 60.5 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 26 | 30.5 | 32.7 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'NONE': 3, 'PREDICTION_ROLE_P2': 5} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 58 | 58.5 | 54.4 | {'PREDICTION_ROLE_W': 28, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_P2': 8, 'NONE': 5} |
| URW | 31 | 82.5 | 32.9 | {'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_W': 12, 'NONE': 2, 'PREDICTION_ROLE_P2': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 364 | 32.4% | 67.3% | 32.4% | 14.8% | 12.9% | 9.1% | 23.9% | 1.54 |
| 正式推薦 | 326 | 31.9% | 61.3% | 61.3% | 72.7% | 100.0% | 61.3% | 34.7% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.8%（無作為9.6%、差+23.2）／P2 平均1.0頭 的中14.5%（無作為9.6%、差+4.9）／P3 平均1.0頭 的中12.5%（無作為9.6%、差+2.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.5%（無作為28.6%、差+34.8）／P2 平均6.0頭 的中72.7%（無作為57.2%、差+15.5）／P3 平均10.75頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.45/40（選択性補正込み）・能力順位 13.84/20（184R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.22/40（選択性補正込み）・能力順位 13.44/20（177R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 6,000円（5.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）33R・着順まで的中 1R／的中 45R のうち的中赤字 21R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 53.4%（同じ127Rの実績 60.7%）／券種別 EXACTA 46点 PFS 5.9%／TRIFECTA 80点 PFS 7.4%／TRIO 657点 PFS 59.9%／WIDE 218点 PFS 94.9%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 63R PFS 60.2% 的中赤字 10/22／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 56R PFS 55.9% 的中赤字 11/20／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 125R：実績 58.0% − ミラー 42.8% = Δ 15.2pt（95%区間 -8.8〜43.4、最高1R除き 9.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 291,700円（38.3%）／保護層の資金比率 0.0（127R）／組だけ的中（三連単は外れ）39R・着順まで的中 19R／的中 68R のうち的中赤字 57R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 49.3%（同じ127Rの実績 39.6%）／券種別 EXACTA 1905点 PFS 46.5%／TRIFECTA 3175点 PFS 22.1%／TRIO 2540点 PFS 56.2%／荒れ度（発走前・1番人気オッズ）MID 63R PFS 44.4% 的中赤字 23/29／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 56R PFS 37.2% 的中赤字 30/35／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 125R：実績 39.9% − ミラー 72.5% = Δ -32.6pt（95%区間 -65.5〜-0.6、最高1R除き -39.3pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、22R×3券種）：購入 9／予算で削除 0／予想で除外 17／未生成・券種なし 40／役割馬の行き先 {'PURCHASED': 66}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、22R×3券種）：購入 26／予算で削除 9／予想で除外 20／未生成・券種なし 11／役割馬の行き先 {'PURCHASED': 161, 'BUDGET_COMPRESSED': 81}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 9R／W外 13R、2着が P2 役割 0R）：STATIC 0/9（平均4.33位）／STYLE_COND 1/9（平均4.11位） 救済1・喪失0／MARKET_COND 0/8（平均4.25位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 15R／W外 7R、2着が P2 役割 12R）：STATIC 12/15（平均3.73位）／STYLE_COND 12/15（平均3.53位） 救済0・喪失0／MARKET_COND 12/14（平均3.07位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 150 | 742,170 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 124 | 457,200 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 68 | 366,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 364 | 1,493,500 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

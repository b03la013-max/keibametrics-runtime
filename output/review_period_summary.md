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

- 反省済みRace 147／PAPER PFS 68.0%／正式推薦 PFS 40.8%
- 第一失敗：{'PREDICTION_ROLE_P2': 25, 'CAPITAL_EFFICIENCY': 55, 'PREDICTION_ROLE_W': 56, 'NONE': 11}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 19 | 61.6 | 65.8 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 11, 'PREDICTION_ROLE_W': 5, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 33 | 71.6 | 44.9 | {'PREDICTION_ROLE_W': 12, 'CAPITAL_EFFICIENCY': 10, 'NONE': 5, 'PREDICTION_ROLE_P2': 6} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 24 | 105.1 | 47.9 | {'PREDICTION_ROLE_W': 14, 'NONE': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 7} |
| URW | 36 | 68.6 | 29.8 | {'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_W': 14, 'NONE': 2, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 147 | 30.6% | 64.6% | 30.6% | 11.6% | 11.6% | 7.5% | 25.2% | 1.51 |
| 正式推薦 | 147 | 29.9% | 61.9% | 61.9% | 74.1% | 100.0% | 61.9% | 44.2% | 1.48 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中30.6%（無作為9.4%、差+21.2）／P2 平均1.0頭 的中11.6%（無作為9.4%、差+2.1）／P3 平均1.0頭 的中11.6%（無作為9.4%、差+2.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中61.9%（無作為28.3%、差+33.6）／P2 平均6.0頭 的中74.1%（無作為56.6%、差+17.6）／P3 平均10.85頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.14/40（選択性補正込み）・能力順位 13.85/20（147R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.16/40（選択性補正込み）・能力順位 13.39/20（147R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 7,800円（6.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）38R・着順まで的中 2R／的中 55R のうち的中赤字 26R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 54.5%（同じ147Rの実績 68.0%）／券種別 EXACTA 57点 PFS 20.5%／TRIFECTA 104点 PFS 15.4%／TRIO 757点 PFS 65.0%／WIDE 250点 PFS 110.5%／WIN 9点 PFS 56.7%／荒れ度（発走前・1番人気オッズ）MID 76R PFS 76.6% 的中赤字 12/28／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 63R PFS 55.5% 的中赤字 14/24／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 145R：実績 65.9% − ミラー 43.8% = Δ 22.1pt（95%区間 -3.1〜52.3、最高1R除き 15.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 337,700円（38.3%）／保護層の資金比率 0.0（147R）／組だけ的中（三連単は外れ）45R・着順まで的中 25R／的中 82R のうち的中赤字 69R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 51.2%（同じ147Rの実績 40.8%）／券種別 EXACTA 2205点 PFS 49.5%／TRIFECTA 3675点 PFS 22.7%／TRIO 2940点 PFS 57.0%／荒れ度（発走前・1番人気オッズ）MID 76R PFS 48.9% 的中赤字 33/41／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 63R PFS 33.9% 的中赤字 32/37／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 145R：実績 41.1% − ミラー 69.3% = Δ -28.2pt（95%区間 -56.8〜-1.8、最高1R除き -33.9pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、42R×3券種）：購入 17／予算で削除 0／予想で除外 36／未生成・券種なし 73／役割馬の行き先 {'PURCHASED': 126}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、42R×3券種）：購入 55／予算で削除 16／予想で除外 36／未生成・券種なし 19／役割馬の行き先 {'PURCHASED': 308, 'BUDGET_COMPRESSED': 154}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 16R／W外 26R、2着が P2 役割 2R）：STATIC 2/16（平均4.0位）／STYLE_COND 4/16（平均3.75位） 救済2・喪失0／MARKET_COND 4/15（平均3.07位） 救済3・喪失1
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 30R／W外 12R、2着が P2 役割 24R）：STATIC 25/30（平均3.83位）／STYLE_COND 25/30（平均3.67位） 救済0・喪失0／MARKET_COND 27/29（平均2.83位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 69 | 244,760 | RECURRING |
| P1:ROLE_W_MISS | P1 | 56 | 294,370 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 25 | 150,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 147 | 634,760 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 384／PAPER PFS 63.2%／正式推薦 PFS 72.3%
- 第一失敗：{'NONE': 45, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 109, 'PREDICTION_ROLE_W': 131, 'PREDICTION_ROLE_P2': 62, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 43 | 85.2 | 57.1 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 16, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 33 | 71.6 | 44.9 | {'PREDICTION_ROLE_W': 12, 'CAPITAL_EFFICIENCY': 10, 'NONE': 5, 'PREDICTION_ROLE_P2': 6} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 60 | 57.0 | 53.3 | {'PREDICTION_ROLE_W': 30, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_P2': 8, 'NONE': 5} |
| URW | 36 | 68.6 | 29.8 | {'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_W': 14, 'NONE': 2, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 384 | 32.6% | 67.4% | 32.6% | 14.6% | 13.0% | 9.6% | 24.2% | 1.54 |
| 正式推薦 | 346 | 31.8% | 62.1% | 62.1% | 72.8% | 100.0% | 62.1% | 36.1% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.0%（無作為9.6%、差+23.4）／P2 平均1.0頭 的中14.1%（無作為9.6%、差+4.6）／P3 平均1.0頭 的中12.7%（無作為9.6%、差+3.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中64.3%（無作為28.6%、差+35.7）／P2 平均6.0頭 的中72.9%（無作為57.2%、差+15.7）／P3 平均10.77頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.55/40（選択性補正込み）・能力順位 13.9/20（204R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.37/40（選択性補正込み）・能力順位 13.48/20（197R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 7,800円（6.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）38R・着順まで的中 2R／的中 55R のうち的中赤字 26R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 54.5%（同じ147Rの実績 68.0%）／券種別 EXACTA 57点 PFS 20.5%／TRIFECTA 104点 PFS 15.4%／TRIO 757点 PFS 65.0%／WIDE 250点 PFS 110.5%／WIN 9点 PFS 56.7%／荒れ度（発走前・1番人気オッズ）MID 76R PFS 76.6% 的中赤字 12/28／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 63R PFS 55.5% 的中赤字 14/24／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 145R：実績 65.9% − ミラー 43.8% = Δ 22.1pt（95%区間 -3.1〜52.3、最高1R除き 15.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 337,700円（38.3%）／保護層の資金比率 0.0（147R）／組だけ的中（三連単は外れ）45R・着順まで的中 25R／的中 82R のうち的中赤字 69R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 51.2%（同じ147Rの実績 40.8%）／券種別 EXACTA 2205点 PFS 49.5%／TRIFECTA 3675点 PFS 22.7%／TRIO 2940点 PFS 57.0%／荒れ度（発走前・1番人気オッズ）MID 76R PFS 48.9% 的中赤字 33/41／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 63R PFS 33.9% 的中赤字 32/37／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 145R：実績 41.1% − ミラー 69.3% = Δ -28.2pt（95%区間 -56.8〜-1.8、最高1R除き -33.9pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、42R×3券種）：購入 17／予算で削除 0／予想で除外 36／未生成・券種なし 73／役割馬の行き先 {'PURCHASED': 126}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、42R×3券種）：購入 55／予算で削除 16／予想で除外 36／未生成・券種なし 19／役割馬の行き先 {'PURCHASED': 308, 'BUDGET_COMPRESSED': 154}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 16R／W外 26R、2着が P2 役割 2R）：STATIC 2/16（平均4.0位）／STYLE_COND 4/16（平均3.75位） 救済2・喪失0／MARKET_COND 4/15（平均3.07位） 救済3・喪失1
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 30R／W外 12R、2着が P2 役割 24R）：STATIC 25/30（平均3.83位）／STYLE_COND 25/30（平均3.67位） 救済0・喪失0／MARKET_COND 27/29（平均2.83位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 155 | 768,300 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 136 | 495,020 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 71 | 384,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 384 | 1,567,320 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

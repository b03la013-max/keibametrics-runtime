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

- 反省済みRace 133／PAPER PFS 65.7%／正式推薦 PFS 41.3%
- 第一失敗：{'PREDICTION_ROLE_P2': 24, 'CAPITAL_EFFICIENCY': 46, 'PREDICTION_ROLE_W': 52, 'NONE': 11}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 14 | 25.7 | 75.1 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 5, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 28 | 68.8 | 44.9 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'NONE': 5, 'PREDICTION_ROLE_P2': 5} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 23 | 108.6 | 48.3 | {'PREDICTION_ROLE_W': 13, 'NONE': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 7} |
| URW | 33 | 74.1 | 30.9 | {'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_W': 12, 'NONE': 2, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 133 | 30.1% | 65.4% | 30.1% | 11.3% | 10.5% | 6.8% | 24.8% | 1.5 |
| 正式推薦 | 133 | 30.1% | 60.9% | 60.9% | 72.9% | 100.0% | 60.9% | 42.1% | 1.47 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中30.1%（無作為9.4%、差+20.7）／P2 平均1.0頭 的中11.3%（無作為9.4%、差+1.9）／P3 平均1.0頭 的中10.5%（無作為9.4%、差+1.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.9%（無作為28.2%、差+32.7）／P2 平均6.0頭 的中72.9%（無作為56.4%、差+16.5）／P3 平均10.86頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.88/40（選択性補正込み）・能力順位 13.82/20（133R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.01/40（選択性補正込み）・能力順位 13.34/20（133R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 7,200円（6.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）35R・着順まで的中 1R／的中 48R のうち的中赤字 23R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 51.8%（同じ133Rの実績 65.7%）／券種別 EXACTA 52点 PFS 13.8%／TRIFECTA 96点 PFS 6.1%／TRIO 687点 PFS 68.6%／WIDE 226点 PFS 95.0%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 66R PFS 75.0% 的中赤字 11/24／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 59R PFS 52.4% 的中赤字 12/21／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 131R：実績 63.3% − ミラー 44.7% = Δ 18.6pt（95%区間 -9.4〜49.0、最高1R除き 11.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 305,500円（38.3%）／保護層の資金比率 0.0（133R）／組だけ的中（三連単は外れ）41R・着順まで的中 20R／的中 71R のうち的中赤字 58R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 47.8%（同じ133Rの実績 41.3%）／券種別 EXACTA 1995点 PFS 48.8%／TRIFECTA 3325点 PFS 21.7%／TRIO 2660点 PFS 60.0%／荒れ度（発走前・1番人気オッズ）MID 66R PFS 49.4% 的中赤字 24/32／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 59R PFS 35.3% 的中赤字 30/35／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 131R：実績 41.6% − ミラー 71.3% = Δ -29.7pt（95%区間 -60.8〜0.3、最高1R除き -36.1pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、28R×3券種）：購入 12／予算で削除 0／予想で除外 24／未生成・券種なし 48／役割馬の行き先 {'PURCHASED': 84}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、28R×3券種）：購入 33／予算で削除 12／予想で除外 26／未生成・券種なし 13／役割馬の行き先 {'PURCHASED': 205, 'BUDGET_COMPRESSED': 107}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 11R／W外 17R、2着が P2 役割 0R）：STATIC 0/11（平均4.36位）／STYLE_COND 2/11（平均4.09位） 救済2・喪失0／MARKET_COND 2/10（平均3.6位） 救済2・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 20R／W外 8R、2着が P2 役割 15R）：STATIC 15/20（平均4.05位）／STYLE_COND 15/20（平均3.8位） 救済0・喪失0／MARKET_COND 17/19（平均2.95位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 58 | 209,610 | RECURRING |
| P1:ROLE_W_MISS | P1 | 52 | 274,240 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 24 | 144,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 133 | 581,610 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 370／PAPER PFS 62.2%／正式推薦 PFS 73.8%
- 第一失敗：{'NONE': 45, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 100, 'PREDICTION_ROLE_W': 127, 'PREDICTION_ROLE_P2': 61, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 38 | 75.5 | 60.3 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 11, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 28 | 68.8 | 44.9 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'NONE': 5, 'PREDICTION_ROLE_P2': 5} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 59 | 57.7 | 53.5 | {'PREDICTION_ROLE_W': 29, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_P2': 8, 'NONE': 5} |
| URW | 33 | 74.1 | 30.9 | {'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_W': 12, 'NONE': 2, 'PREDICTION_ROLE_P2': 6} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 370 | 32.4% | 67.8% | 32.4% | 14.6% | 12.7% | 9.5% | 24.1% | 1.54 |
| 正式推薦 | 332 | 31.9% | 61.7% | 61.7% | 72.3% | 100.0% | 61.7% | 34.9% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.8%（無作為9.5%、差+23.3）／P2 平均1.0頭 的中14.1%（無作為9.5%、差+4.6）／P3 平均1.0頭 的中12.2%（無作為9.5%、差+2.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.9%（無作為28.6%、差+35.4）／P2 平均6.0頭 的中72.2%（無作為57.1%、差+15.0）／P3 平均10.77頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.41/40（選択性補正込み）・能力順位 13.89/20（190R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.28/40（選択性補正込み）・能力順位 13.45/20（183R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 7,200円（6.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）35R・着順まで的中 1R／的中 48R のうち的中赤字 23R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 51.8%（同じ133Rの実績 65.7%）／券種別 EXACTA 52点 PFS 13.8%／TRIFECTA 96点 PFS 6.1%／TRIO 687点 PFS 68.6%／WIDE 226点 PFS 95.0%／WIN 8点 PFS 43.8%／荒れ度（発走前・1番人気オッズ）MID 66R PFS 75.0% 的中赤字 11/24／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 59R PFS 52.4% 的中赤字 12/21／UNKNOWN 2R PFS 175.7% 的中赤字 0/1／市場ミラーとの差 131R：実績 63.3% − ミラー 44.7% = Δ 18.6pt（95%区間 -9.4〜49.0、最高1R除き 11.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 305,500円（38.3%）／保護層の資金比率 0.0（133R）／組だけ的中（三連単は外れ）41R・着順まで的中 20R／的中 71R のうち的中赤字 58R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 47.8%（同じ133Rの実績 41.3%）／券種別 EXACTA 1995点 PFS 48.8%／TRIFECTA 3325点 PFS 21.7%／TRIO 2660点 PFS 60.0%／荒れ度（発走前・1番人気オッズ）MID 66R PFS 49.4% 的中赤字 24/32／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 59R PFS 35.3% 的中赤字 30/35／UNKNOWN 2R PFS 19.8% 的中赤字 2/2／市場ミラーとの差 131R：実績 41.6% − ミラー 71.3% = Δ -29.7pt（95%区間 -60.8〜0.3、最高1R除き -36.1pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、28R×3券種）：購入 12／予算で削除 0／予想で除外 24／未生成・券種なし 48／役割馬の行き先 {'PURCHASED': 84}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、28R×3券種）：購入 33／予算で削除 12／予想で除外 26／未生成・券種なし 13／役割馬の行き先 {'PURCHASED': 205, 'BUDGET_COMPRESSED': 107}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 11R／W外 17R、2着が P2 役割 0R）：STATIC 0/11（平均4.36位）／STYLE_COND 2/11（平均4.09位） 救済2・喪失0／MARKET_COND 2/10（平均3.6位） 救済2・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 20R／W外 8R、2着が P2 役割 15R）：STATIC 15/20（平均4.05位）／STYLE_COND 15/20（平均3.8位） 救済0・喪失0／MARKET_COND 17/19（平均2.95位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 151 | 748,170 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 125 | 459,870 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 70 | 378,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 370 | 1,514,170 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

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

- 反省済みRace 52／PAPER PFS 48.8%／正式推薦 PFS 38.6%
- 第一失敗：{'PREDICTION_ROLE_P2': 13, 'CAPITAL_EFFICIENCY': 18, 'PREDICTION_ROLE_W': 18, 'NONE': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 20 | 49.9 | 22.0 | {'PREDICTION_ROLE_W': 6, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 7, 'NONE': 1} |
| NGY | 3 | 85.2 | 7.2 | {'PREDICTION_ROLE_W': 3} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| URW | 8 | 109.8 | 52.5 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'NONE': 1, 'PREDICTION_ROLE_P2': 2} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 52 | 34.6% | 69.2% | 34.6% | 9.6% | 11.5% | 5.8% | 25.0% | 1.5 |
| 正式推薦 | 52 | 36.5% | 65.4% | 65.4% | 73.1% | 100.0% | 65.4% | 44.2% | 1.56 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中34.6%（無作為10.2%、差+24.4）／P2 平均1.0頭 的中9.6%（無作為10.2%、差-0.6）／P3 平均1.0頭 的中11.5%（無作為10.2%、差+1.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中65.4%（無作為30.6%、差+34.8）／P2 平均6.0頭 的中73.1%（無作為61.1%、差+11.9）／P3 平均10.04頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.46/40（選択性補正込み）・能力順位 13.81/20（52R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.74/40（選択性補正込み）・能力順位 13.25/20（52R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（5.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）14R・着順まで的中 0R／的中 17R のうち的中赤字 8R／損益分岐の倍率 平均 7.8倍／同じ点数を無作為に選んだ場合の期待PFS 42.8%（同じ52Rの実績 48.8%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 266点 PFS 52.9%／WIDE 92点 PFS 63.7%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 22R PFS 53.5% 的中赤字 4/8／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 27R PFS 38.9% 的中赤字 4/7／市場ミラーとの差 52R：実績 48.8% − ミラー 50.6% = Δ -1.8pt（95%区間 -41.0〜41.8、最高1R除き -13.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 118,000円（37.8%）／保護層の資金比率 0.0（52R）／組だけ的中（三連単は外れ）18R・着順まで的中 8R／的中 26R のうち的中赤字 22R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 36.6%（同じ52Rの実績 38.6%）／券種別 EXACTA 780点 PFS 41.4%／TRIFECTA 1300点 PFS 13.2%／TRIO 1040点 PFS 68.1%／荒れ度（発走前・1番人気オッズ）MID 22R PFS 60.1% 的中赤字 9/11／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 27R PFS 24.3% 的中赤字 12/14／市場ミラーとの差 52R：実績 38.6% − ミラー 98.7% = Δ -60.2pt（95%区間 -125.8〜-0.8、最高1R除き -77.0pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 22 | 84,790 | RECURRING |
| P1:ROLE_W_MISS | P1 | 18 | 97,990 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 13 | 78,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 52 | 240,790 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 289／PAPER PFS 58.2%／正式推薦 PFS 83.4%
- 第一失敗：{'NONE': 37, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 72, 'PREDICTION_ROLE_W': 93, 'PREDICTION_ROLE_P2': 50, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 34 | 79.4 | 66.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 56 | 54.0 | 29.7 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 6, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_W': 11, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 3 | 85.2 | 7.2 | {'PREDICTION_ROLE_W': 3} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 36 | 23.6 | 56.9 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 4} |
| URW | 8 | 109.8 | 52.5 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'NONE': 1, 'PREDICTION_ROLE_P2': 2} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 289 | 33.9% | 69.2% | 33.9% | 15.2% | 13.5% | 10.0% | 23.9% | 1.55 |
| 正式推薦 | 251 | 33.9% | 62.9% | 62.9% | 72.1% | 100.0% | 62.9% | 33.1% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中35.4%（無作為9.8%、差+25.5）／P2 平均1.0頭 的中14.9%（無作為9.8%、差+5.1）／P3 平均1.0頭 的中13.3%（無作為9.8%、差+3.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.7%（無作為29.4%、差+37.2）／P2 平均6.0頭 的中71.8%（無作為58.8%、差+13.0）／P3 平均10.48頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.07/40（選択性補正込み）・能力順位 13.93/20（109R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.37/40（選択性補正込み）・能力順位 13.49/20（102R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（5.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）14R・着順まで的中 0R／的中 17R のうち的中赤字 8R／損益分岐の倍率 平均 7.8倍／同じ点数を無作為に選んだ場合の期待PFS 42.8%（同じ52Rの実績 48.8%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 266点 PFS 52.9%／WIDE 92点 PFS 63.7%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 22R PFS 53.5% 的中赤字 4/8／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 27R PFS 38.9% 的中赤字 4/7／市場ミラーとの差 52R：実績 48.8% − ミラー 50.6% = Δ -1.8pt（95%区間 -41.0〜41.8、最高1R除き -13.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 118,000円（37.8%）／保護層の資金比率 0.0（52R）／組だけ的中（三連単は外れ）18R・着順まで的中 8R／的中 26R のうち的中赤字 22R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 36.6%（同じ52Rの実績 38.6%）／券種別 EXACTA 780点 PFS 41.4%／TRIFECTA 1300点 PFS 13.2%／TRIO 1040点 PFS 68.1%／荒れ度（発走前・1番人気オッズ）MID 22R PFS 60.1% 的中赤字 9/11／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 27R PFS 24.3% 的中赤字 12/14／市場ミラーとの差 52R：実績 38.6% − ミラー 98.7% = Δ -60.2pt（95%区間 -125.8〜-0.8、最高1R除き -77.0pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 117 | 571,920 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 89 | 335,050 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 59 | 312,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 289 | 1,173,350 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

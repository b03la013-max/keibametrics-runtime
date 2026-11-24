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

- 反省済みRace 68／PAPER PFS 47.7%／正式推薦 PFS 46.7%
- 第一失敗：{'PREDICTION_ROLE_P2': 15, 'CAPITAL_EFFICIENCY': 21, 'PREDICTION_ROLE_W': 25, 'NONE': 7}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 11 | 30.0 | 46.3 | {'PREDICTION_ROLE_W': 6, 'CAPITAL_EFFICIENCY': 2, 'NONE': 2, 'PREDICTION_ROLE_P2': 1} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| URW | 12 | 116.2 | 56.3 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 68 | 33.8% | 67.6% | 33.8% | 8.8% | 10.3% | 7.4% | 23.5% | 1.49 |
| 正式推薦 | 68 | 36.8% | 63.2% | 63.2% | 73.5% | 100.0% | 63.2% | 44.1% | 1.54 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.8%（無作為9.8%、差+24.0）／P2 平均1.0頭 的中8.8%（無作為9.8%、差-1.0）／P3 平均1.0頭 的中10.3%（無作為9.8%、差+0.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.2%（無作為29.5%、差+33.7）／P2 平均6.0頭 的中73.5%（無作為59.1%、差+14.5）／P3 平均10.4頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.06/40（選択性補正込み）・能力順位 13.86/20（68R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.89/40（選択性補正込み）・能力順位 13.44/20（68R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 3,000円（5.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）16R・着順まで的中 1R／的中 22R のうち的中赤字 11R／損益分岐の倍率 平均 7.8倍／同じ点数を無作為に選んだ場合の期待PFS 38.4%（同じ68Rの実績 47.7%）／券種別 EXACTA 21点 PFS 12.9%／TRIFECTA 40点 PFS 14.8%／TRIO 348点 PFS 48.6%／WIDE 120点 PFS 61.5%／WIN 3点 PFS 63.3%／荒れ度（発走前・1番人気オッズ）MID 32R PFS 55.7% 的中赤字 6/12／OPEN 4R PFS 82.5% 的中赤字 0/2／SOLID 32R PFS 36.6% 的中赤字 5/8／市場ミラーとの差 68R：実績 47.7% − ミラー 44.5% = Δ 3.1pt（95%区間 -29.4〜34.9、最高1R除き -6.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 154,600円（37.9%）／保護層の資金比率 0.0（68R）／組だけ的中（三連単は外れ）22R・着順まで的中 12R／的中 35R のうち的中赤字 27R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 34.8%（同じ68Rの実績 46.7%）／券種別 EXACTA 1020点 PFS 52.5%／TRIFECTA 1700点 PFS 29.9%／TRIO 1360点 PFS 63.4%／荒れ度（発走前・1番人気オッズ）MID 32R PFS 67.0% 的中赤字 11/16／OPEN 4R PFS 27.3% 的中赤字 2/2／SOLID 32R PFS 28.9% 的中赤字 14/17／市場ミラーとの差 68R：実績 46.7% − ミラー 98.8% = Δ -52.1pt（95%区間 -107.5〜-0.4、最高1R除き -64.7pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 27 | 102,630 | RECURRING |
| P1:ROLE_W_MISS | P1 | 25 | 132,520 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 15 | 90,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 68 | 300,630 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 305／PAPER PFS 57.4%／正式推薦 PFS 82.8%
- 第一失敗：{'NONE': 41, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 75, 'PREDICTION_ROLE_W': 100, 'PREDICTION_ROLE_P2': 52, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 34 | 79.4 | 66.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 11 | 30.0 | 46.3 | {'PREDICTION_ROLE_W': 6, 'CAPITAL_EFFICIENCY': 2, 'NONE': 2, 'PREDICTION_ROLE_P2': 1} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 36 | 23.6 | 56.9 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 4} |
| URW | 12 | 116.2 | 56.3 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 305 | 33.8% | 68.9% | 33.8% | 14.8% | 13.1% | 10.2% | 23.6% | 1.54 |
| 正式推薦 | 267 | 34.1% | 62.5% | 62.5% | 72.3% | 100.0% | 62.5% | 33.7% | 1.44 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中35.0%（無作為9.7%、差+25.3）／P2 平均1.0頭 的中14.2%（無作為9.7%、差+4.5）／P3 平均1.0頭 的中12.7%（無作為9.7%、差+2.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中65.8%（無作為29.1%、差+36.6）／P2 平均6.0頭 的中72.1%（無作為58.3%、差+13.8）／P3 平均10.57頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.78/40（選択性補正込み）・能力順位 13.94/20（125R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.37/40（選択性補正込み）・能力順位 13.56/20（118R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 3,000円（5.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）16R・着順まで的中 1R／的中 22R のうち的中赤字 11R／損益分岐の倍率 平均 7.8倍／同じ点数を無作為に選んだ場合の期待PFS 38.4%（同じ68Rの実績 47.7%）／券種別 EXACTA 21点 PFS 12.9%／TRIFECTA 40点 PFS 14.8%／TRIO 348点 PFS 48.6%／WIDE 120点 PFS 61.5%／WIN 3点 PFS 63.3%／荒れ度（発走前・1番人気オッズ）MID 32R PFS 55.7% 的中赤字 6/12／OPEN 4R PFS 82.5% 的中赤字 0/2／SOLID 32R PFS 36.6% 的中赤字 5/8／市場ミラーとの差 68R：実績 47.7% − ミラー 44.5% = Δ 3.1pt（95%区間 -29.4〜34.9、最高1R除き -6.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 154,600円（37.9%）／保護層の資金比率 0.0（68R）／組だけ的中（三連単は外れ）22R・着順まで的中 12R／的中 35R のうち的中赤字 27R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 34.8%（同じ68Rの実績 46.7%）／券種別 EXACTA 1020点 PFS 52.5%／TRIFECTA 1700点 PFS 29.9%／TRIO 1360点 PFS 63.4%／荒れ度（発走前・1番人気オッズ）MID 32R PFS 67.0% 的中赤字 11/16／OPEN 4R PFS 27.3% 的中赤字 2/2／SOLID 32R PFS 28.9% 的中赤字 14/17／市場ミラーとの差 68R：実績 46.7% − ミラー 98.8% = Δ -52.1pt（95%区間 -107.5〜-0.4、最高1R除き -64.7pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 124 | 606,450 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 94 | 352,890 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 61 | 324,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 305 | 1,233,190 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

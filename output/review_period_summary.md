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

- 反省済みRace 94／PAPER PFS 52.7%／正式推薦 PFS 45.0%
- 第一失敗：{'PREDICTION_ROLE_P2': 16, 'CAPITAL_EFFICIENCY': 31, 'PREDICTION_ROLE_W': 39, 'NONE': 8}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 16 | 41.2 | 45.7 | {'PREDICTION_ROLE_W': 7, 'CAPITAL_EFFICIENCY': 6, 'NONE': 2, 'PREDICTION_ROLE_P2': 1} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 12 | 63.2 | 60.5 | {'PREDICTION_ROLE_W': 9, 'NONE': 1, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 1} |
| URW | 21 | 94.7 | 37.1 | {'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 94 | 27.7% | 64.9% | 27.7% | 12.8% | 9.6% | 7.4% | 23.4% | 1.47 |
| 正式推薦 | 94 | 30.9% | 58.5% | 58.5% | 76.6% | 100.0% | 58.5% | 43.6% | 1.45 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中27.7%（無作為9.6%、差+18.1）／P2 平均1.0頭 的中12.8%（無作為9.6%、差+3.2）／P3 平均1.0頭 的中9.6%（無作為9.6%、差-0.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中58.5%（無作為28.8%、差+29.7）／P2 平均6.0頭 的中76.6%（無作為57.6%、差+19.0）／P3 平均10.66頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.48/40（選択性補正込み）・能力順位 13.64/20（94R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.74/40（選択性補正込み）・能力順位 13.24/20（94R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 5,400円（7.1%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）23R・着順まで的中 1R／的中 32R のうち的中赤字 16R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 60.3%（同じ94Rの実績 52.7%）／券種別 EXACTA 37点 PFS 7.3%／TRIFECTA 72点 PFS 8.2%／TRIO 484点 PFS 53.4%／WIDE 160点 PFS 80.6%／WIN 5点 PFS 70.0%／荒れ度（発走前・1番人気オッズ）MID 47R PFS 61.6% 的中赤字 8/17／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 40R PFS 45.5% 的中赤字 8/13／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 93R：実績 53.9% − ミラー 43.5% = Δ 10.4pt（95%区間 -17.0〜38.7、最高1R除き 3.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 214,900円（38.1%）／保護層の資金比率 0.0（94R）／組だけ的中（三連単は外れ）31R・着順まで的中 14R／的中 52R のうち的中赤字 42R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 57.7%（同じ94Rの実績 45.0%）／券種別 EXACTA 1410点 PFS 53.0%／TRIFECTA 2350点 PFS 23.5%／TRIO 1880点 PFS 65.9%／荒れ度（発走前・1番人気オッズ）MID 47R PFS 55.7% 的中赤字 19/25／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 40R PFS 37.0% 的中赤字 20/24／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 93R：実績 45.2% − ミラー 83.4% = Δ -38.2pt（95%区間 -80.9〜2.3、最高1R除き -47.3pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 42 | 158,410 | RECURRING |
| P1:ROLE_W_MISS | P1 | 39 | 199,380 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 16 | 96,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 94 | 410,410 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 331／PAPER PFS 58.1%／正式推薦 PFS 79.2%
- 第一失敗：{'NONE': 42, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 85, 'PREDICTION_ROLE_W': 114, 'PREDICTION_ROLE_P2': 53, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 34 | 79.4 | 66.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 16 | 41.2 | 45.7 | {'PREDICTION_ROLE_W': 7, 'CAPITAL_EFFICIENCY': 6, 'NONE': 2, 'PREDICTION_ROLE_P2': 1} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 48 | 34.8 | 57.8 | {'PREDICTION_ROLE_W': 25, 'CAPITAL_EFFICIENCY': 11, 'PREDICTION_ROLE_P2': 7, 'NONE': 5} |
| URW | 21 | 94.7 | 37.1 | {'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 331 | 32.0% | 68.0% | 32.0% | 15.4% | 12.7% | 10.0% | 23.6% | 1.53 |
| 正式推薦 | 293 | 32.4% | 61.1% | 61.1% | 73.4% | 100.0% | 61.1% | 34.5% | 1.42 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.3%（無作為9.7%、差+22.6）／P2 平均1.0頭 的中15.2%（無作為9.7%、差+5.6）／P3 平均1.0頭 的中12.1%（無作為9.7%、差+2.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.4%（無作為28.9%、差+34.6）／P2 平均6.0頭 的中73.6%（無作為57.7%、差+15.9）／P3 平均10.67頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.29/40（選択性補正込み）・能力順位 13.79/20（151R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.18/40（選択性補正込み）・能力順位 13.41/20（144R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 5,400円（7.1%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）23R・着順まで的中 1R／的中 32R のうち的中赤字 16R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 60.3%（同じ94Rの実績 52.7%）／券種別 EXACTA 37点 PFS 7.3%／TRIFECTA 72点 PFS 8.2%／TRIO 484点 PFS 53.4%／WIDE 160点 PFS 80.6%／WIN 5点 PFS 70.0%／荒れ度（発走前・1番人気オッズ）MID 47R PFS 61.6% 的中赤字 8/17／OPEN 6R PFS 57.4% 的中赤字 0/2／SOLID 40R PFS 45.5% 的中赤字 8/13／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 93R：実績 53.9% − ミラー 43.5% = Δ 10.4pt（95%区間 -17.0〜38.7、最高1R除き 3.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 214,900円（38.1%）／保護層の資金比率 0.0（94R）／組だけ的中（三連単は外れ）31R・着順まで的中 14R／的中 52R のうち的中赤字 42R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 57.7%（同じ94Rの実績 45.0%）／券種別 EXACTA 1410点 PFS 53.0%／TRIFECTA 2350点 PFS 23.5%／TRIO 1880点 PFS 65.9%／荒れ度（発走前・1番人気オッズ）MID 47R PFS 55.7% 的中赤字 19/25／OPEN 6R PFS 18.2% 的中赤字 2/2／SOLID 40R PFS 37.0% 的中赤字 20/24／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 93R：実績 45.2% − ミラー 83.4% = Δ -38.2pt（95%区間 -80.9〜2.3、最高1R除き -47.3pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 138 | 673,310 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 109 | 408,670 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 62 | 330,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 331 | 1,342,970 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

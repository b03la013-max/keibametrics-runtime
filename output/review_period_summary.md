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

- 反省済みRace 15／PAPER PFS 53.6%／正式推薦 PFS 12.9%
- 第一失敗：{'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 6}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 5 | 37.3 | 4.5 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1, 'PREDICTION_ROLE_W': 2} |
| MIZ | 8 | 80.7 | 12.2 | {'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 2} |
| SAG | 2 | 0.0 | 36.3 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 15 | 40.0% | 66.7% | 40.0% | 6.7% | 20.0% | 6.7% | 26.7% | 1.47 |
| 正式推薦 | 15 | 40.0% | 60.0% | 60.0% | 60.0% | 100.0% | 60.0% | 26.7% | 1.4 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中40.0%（無作為10.4%、差+29.6）／P2 平均1.0頭 的中6.7%（無作為10.4%、差-3.7）／P3 平均1.0頭 的中20.0%（無作為10.4%、差+9.6）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.0%（無作為31.2%、差+28.8）／P2 平均6.0頭 的中60.0%（無作為62.4%、差-2.4）／P3 平均9.73頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.2/40（選択性補正込み）・能力順位 13.48/20（15R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.09/40（選択性補正込み）・能力順位 12.78/20（15R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（5.2%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）4R・着順まで的中 0R／的中 6R のうち的中赤字 2R／損益分岐の倍率 平均 7.7倍／同じ点数を無作為に選んだ場合の期待PFS 52.3%（同じ15Rの実績 53.6%）／券種別 EXACTA 5点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 75点 PFS 40.0%／WIDE 26点 PFS 121.5%／WIN 1点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 4R PFS 83.2% 的中赤字 1/2／OPEN 1R PFS 128.6% 的中赤字 0/1／SOLID 10R PFS 36.6% 的中赤字 1/3／市場ミラーとの差 15R：実績 53.6% − ミラー 79.0% = Δ -25.4pt（95%区間 -110.5〜50.0、最高1R除き -46.7pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 34,200円（38.0%）／保護層の資金比率 0.0（15R）／組だけ的中（三連単は外れ）4R・着順まで的中 3R／的中 4R のうち的中赤字 4R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 47.4%（同じ15Rの実績 12.9%）／券種別 EXACTA 225点 PFS 8.6%／TRIFECTA 375点 PFS 16.5%／TRIO 300点 PFS 11.5%／荒れ度（発走前・1番人気オッズ）MID 4R PFS 31.6% 的中赤字 2/2／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 10R PFS 6.7% 的中赤字 2/2／市場ミラーとの差 15R：実績 12.9% − ミラー 127.2% = Δ -114.3pt（95%区間 -268.8〜-16.8、最高1R除き -125.6pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 6 | 36,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 4 | 12,410 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 15 | 78,410 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 252／PAPER PFS 59.8%／正式推薦 PFS 89.2%
- 第一失敗：{'NONE': 34, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 58, 'PREDICTION_ROLE_W': 81, 'PREDICTION_ROLE_P2': 42, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 29 | 91.8 | 33.0 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 6, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 44 | 60.1 | 30.1 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 5, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 10, 'EXACT_ORIENTATION': 1} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 24 | 58.0 | 36.8 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 6, 'PREDICTION_ROLE_W': 6, 'CAPITAL_EFFICIENCY': 7, 'NONE': 2} |
| SON | 36 | 23.6 | 56.9 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 252 | 34.1% | 69.0% | 34.1% | 15.9% | 14.3% | 10.7% | 23.8% | 1.56 |
| 正式推薦 | 214 | 33.6% | 62.1% | 62.1% | 71.0% | 100.0% | 62.1% | 29.9% | 1.4 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中36.1%（無作為9.8%、差+26.3）／P2 平均1.0頭 的中16.0%（無作為9.8%、差+6.2）／P3 平均1.0頭 的中14.6%（無作為9.8%、差+4.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.4%（無作為29.2%、差+37.2）／P2 平均6.0頭 的中70.1%（無作為58.4%、差+11.7）／P3 平均10.57頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.54/40（選択性補正込み）・能力順位 13.92/20（72R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.34/40（選択性補正込み）・能力順位 13.52/20（65R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（5.2%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）4R・着順まで的中 0R／的中 6R のうち的中赤字 2R／損益分岐の倍率 平均 7.7倍／同じ点数を無作為に選んだ場合の期待PFS 52.3%（同じ15Rの実績 53.6%）／券種別 EXACTA 5点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 75点 PFS 40.0%／WIDE 26点 PFS 121.5%／WIN 1点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 4R PFS 83.2% 的中赤字 1/2／OPEN 1R PFS 128.6% 的中赤字 0/1／SOLID 10R PFS 36.6% 的中赤字 1/3／市場ミラーとの差 15R：実績 53.6% − ミラー 79.0% = Δ -25.4pt（95%区間 -110.5〜50.0、最高1R除き -46.7pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 34,200円（38.0%）／保護層の資金比率 0.0（15R）／組だけ的中（三連単は外れ）4R・着順まで的中 3R／的中 4R のうち的中赤字 4R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 47.4%（同じ15Rの実績 12.9%）／券種別 EXACTA 225点 PFS 8.6%／TRIFECTA 375点 PFS 16.5%／TRIO 300点 PFS 11.5%／荒れ度（発走前・1番人気オッズ）MID 4R PFS 31.6% 的中赤字 2/2／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 10R PFS 6.7% 的中赤字 2/2／市場ミラーとの差 15R：実績 12.9% − ミラー 127.2% = Δ -114.3pt（95%区間 -268.8〜-16.8、最高1R除き -125.6pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 105 | 509,930 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 71 | 262,670 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 51 | 264,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 252 | 1,010,970 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 4 | 22,410 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

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

- 反省済みRace 26／PAPER PFS 38.4%／正式推薦 PFS 11.7%
- 第一失敗：{'PREDICTION_ROLE_P2': 8, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 11}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 8 | 24.5 | 9.6 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 4} |
| MIZ | 12 | 69.0 | 11.2 | {'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 3} |
| SAG | 6 | 0.0 | 15.3 | {'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_P2': 2} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 26 | 34.6% | 65.4% | 34.6% | 7.7% | 19.2% | 11.5% | 23.1% | 1.42 |
| 正式推薦 | 26 | 34.6% | 57.7% | 57.7% | 65.4% | 100.0% | 57.7% | 34.6% | 1.46 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中34.6%（無作為10.5%、差+24.1）／P2 平均1.0頭 的中7.7%（無作為10.5%、差-2.8）／P3 平均1.0頭 的中19.2%（無作為10.5%、差+8.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中57.7%（無作為31.4%、差+26.2）／P2 平均6.0頭 的中65.4%（無作為62.9%、差+2.5）／P3 平均9.69頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.73/40（選択性補正込み）・能力順位 13.19/20（26R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.23/40（選択性補正込み）・能力順位 12.78/20（26R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,800円（8.4%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 8R のうち的中赤字 3R／損益分岐の倍率 平均 8.3倍／同じ点数を無作為に選んだ場合の期待PFS 48.6%（同じ26Rの実績 38.4%）／券種別 EXACTA 13点 PFS 0.0%／TRIFECTA 24点 PFS 0.0%／TRIO 134点 PFS 35.4%／WIDE 42点 PFS 83.6%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 39.5% 的中赤字 1/2／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 15R PFS 24.7% 的中赤字 2/4／市場ミラーとの差 26R：実績 38.4% − ミラー 75.4% = Δ -37.0pt（95%区間 -91.3〜15.5、最高1R除き -48.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 59,500円（38.1%）／保護層の資金比率 0.0（26R）／組だけ的中（三連単は外れ）9R・着順まで的中 3R／的中 10R のうち的中赤字 10R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 44.6%（同じ26Rの実績 11.7%）／券種別 EXACTA 390点 PFS 9.5%／TRIFECTA 650点 PFS 9.5%／TRIO 520点 PFS 16.0%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 17.8% 的中赤字 3/3／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 15R PFS 9.1% 的中赤字 6/6／市場ミラーとの差 26R：実績 11.7% − ミラー 92.2% = Δ -80.5pt（95%区間 -171.2〜-20.5、最高1R除き -85.5pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 11 | 63,280 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 10 | 41,760 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 8 | 48,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 26 | 137,760 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 263／PAPER PFS 58.0%／正式推薦 PFS 85.4%
- 第一失敗：{'NONE': 34, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 61, 'PREDICTION_ROLE_W': 86, 'PREDICTION_ROLE_P2': 45, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 32 | 83.7 | 30.9 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 48 | 59.4 | 27.8 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 5, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_W': 10, 'PREDICTION_ROLE_P2': 11, 'EXACT_ORIENTATION': 1} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 28 | 48.4 | 31.7 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 7, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| SON | 36 | 23.6 | 56.9 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 263 | 33.8% | 68.8% | 33.8% | 15.6% | 14.4% | 11.0% | 23.6% | 1.55 |
| 正式推薦 | 225 | 33.3% | 61.8% | 61.8% | 71.1% | 100.0% | 61.8% | 30.7% | 1.41 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中35.5%（無作為9.8%、差+25.7）／P2 平均1.0頭 的中15.5%（無作為9.8%、差+5.7）／P3 平均1.0頭 的中14.8%（無作為9.8%、差+5.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中65.5%（無作為29.4%、差+36.2）／P2 平均6.0頭 的中70.3%（無作為58.7%、差+11.5）／P3 平均10.5頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.35/40（選択性補正込み）・能力順位 13.77/20（83R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.06/40（選択性補正込み）・能力順位 13.41/20（76R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,800円（8.4%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 8R のうち的中赤字 3R／損益分岐の倍率 平均 8.3倍／同じ点数を無作為に選んだ場合の期待PFS 48.6%（同じ26Rの実績 38.4%）／券種別 EXACTA 13点 PFS 0.0%／TRIFECTA 24点 PFS 0.0%／TRIO 134点 PFS 35.4%／WIDE 42点 PFS 83.6%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 39.5% 的中赤字 1/2／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 15R PFS 24.7% 的中赤字 2/4／市場ミラーとの差 26R：実績 38.4% − ミラー 75.4% = Δ -37.0pt（95%区間 -91.3〜15.5、最高1R除き -48.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 59,500円（38.1%）／保護層の資金比率 0.0（26R）／組だけ的中（三連単は外れ）9R・着順まで的中 3R／的中 10R のうち的中赤字 10R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 44.6%（同じ26Rの実績 11.7%）／券種別 EXACTA 390点 PFS 9.5%／TRIFECTA 650点 PFS 9.5%／TRIO 520点 PFS 16.0%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 17.8% 的中赤字 3/3／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 15R PFS 9.1% 的中赤字 6/6／市場ミラーとの差 26R：実績 11.7% − ミラー 92.2% = Δ -80.5pt（95%区間 -171.2〜-20.5、最高1R除き -85.5pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 110 | 537,210 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 77 | 292,020 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 54 | 282,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 263 | 1,070,320 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 4 | 22,410 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

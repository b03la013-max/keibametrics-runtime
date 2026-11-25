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

- 反省済みRace 84／PAPER PFS 44.3%／正式推薦 PFS 46.6%
- 第一失敗：{'PREDICTION_ROLE_P2': 16, 'CAPITAL_EFFICIENCY': 28, 'PREDICTION_ROLE_W': 32, 'NONE': 8}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 24 | 46.2 | 36.3 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2} |
| NGY | 13 | 44.5 | 45.8 | {'PREDICTION_ROLE_W': 6, 'CAPITAL_EFFICIENCY': 4, 'NONE': 2, 'PREDICTION_ROLE_P2': 1} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |
| SON | 8 | 26.4 | 67.8 | {'PREDICTION_ROLE_W': 6, 'NONE': 1, 'PREDICTION_ROLE_P2': 1} |
| URW | 18 | 82.9 | 43.3 | {'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 5, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 84 | 31.0% | 67.9% | 31.0% | 14.3% | 8.3% | 8.3% | 22.6% | 1.5 |
| 正式推薦 | 84 | 34.5% | 61.9% | 61.9% | 77.4% | 100.0% | 61.9% | 42.9% | 1.51 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中31.0%（無作為9.7%、差+21.2）／P2 平均1.0頭 的中14.3%（無作為9.7%、差+4.5）／P3 平均1.0頭 的中8.3%（無作為9.7%、差-1.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中61.9%（無作為29.2%、差+32.7）／P2 平均6.0頭 的中77.4%（無作為58.4%、差+19.0）／P3 平均10.51頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.96/40（選択性補正込み）・能力順位 13.79/20（84R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.99/40（選択性補正込み）・能力順位 13.36/20（84R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 5,400円（7.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）20R・着順まで的中 1R／的中 28R のうち的中赤字 15R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 50.4%（同じ84Rの実績 44.3%）／券種別 EXACTA 35点 PFS 7.7%／TRIFECTA 72点 PFS 8.2%／TRIO 430点 PFS 47.9%／WIDE 142点 PFS 59.7%／WIN 4点 PFS 87.5%／荒れ度（発走前・1番人気オッズ）MID 41R PFS 49.7% 的中赤字 8/15／OPEN 4R PFS 82.5% 的中赤字 0/2／SOLID 38R PFS 37.9% 的中赤字 7/11／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 83R：実績 45.4% − ミラー 44.1% = Δ 1.2pt（95%区間 -24.4〜30.1、最高1R除き -6.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 191,400円（38.0%）／保護層の資金比率 0.0（84R）／組だけ的中（三連単は外れ）28R・着順まで的中 12R／的中 47R のうち的中赤字 38R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 46.1%（同じ84Rの実績 46.6%）／券種別 EXACTA 1260点 PFS 55.9%／TRIFECTA 2100点 PFS 24.2%／TRIO 1680点 PFS 67.5%／荒れ度（発走前・1番人気オッズ）MID 41R PFS 58.4% 的中赤字 17/22／OPEN 4R PFS 27.3% 的中赤字 2/2／SOLID 38R PFS 36.4% 的中赤字 18/22／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 83R：実績 46.8% − ミラー 90.2% = Δ -43.4pt（95%区間 -90.1〜1.9、最高1R除き -53.6pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 38 | 147,070 | RECURRING |
| P1:ROLE_W_MISS | P1 | 32 | 164,430 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 16 | 96,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 84 | 369,070 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 321／PAPER PFS 56.0%／正式推薦 PFS 80.8%
- 第一失敗：{'NONE': 42, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 82, 'PREDICTION_ROLE_W': 107, 'PREDICTION_ROLE_P2': 53, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 34 | 79.4 | 66.2 | {'NONE': 5, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1} |
| KOC | 23 | 60.4 | 32.5 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 60 | 52.1 | 36.2 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 7, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 15, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 13, 'EXACT_ORIENTATION': 1} |
| NGY | 13 | 44.5 | 45.8 | {'PREDICTION_ROLE_W': 6, 'CAPITAL_EFFICIENCY': 4, 'NONE': 2, 'PREDICTION_ROLE_P2': 1} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 33 | 50.0 | 29.3 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 9, 'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 11, 'NONE': 2} |
| SON | 44 | 24.3 | 58.9 | {'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 7, 'NONE': 5} |
| URW | 18 | 82.9 | 43.3 | {'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 5, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 321 | 33.0% | 68.8% | 33.0% | 15.9% | 12.5% | 10.3% | 23.4% | 1.55 |
| 正式推薦 | 283 | 33.6% | 62.2% | 62.2% | 73.5% | 100.0% | 62.2% | 33.9% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.8%（無作為9.7%、差+24.1）／P2 平均1.0頭 的中16.0%（無作為9.7%、差+6.3）／P3 平均1.0頭 的中11.7%（無作為9.7%、差+2.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中65.0%（無作為29.0%、差+36.0）／P2 平均6.0頭 的中73.8%（無作為58.1%、差+15.7）／P3 平均10.61頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.64/40（選択性補正込み）・能力順位 13.89/20（141R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.37/40（選択性補正込み）・能力順位 13.5/20（134R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 5,400円（7.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）20R・着順まで的中 1R／的中 28R のうち的中赤字 15R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 50.4%（同じ84Rの実績 44.3%）／券種別 EXACTA 35点 PFS 7.7%／TRIFECTA 72点 PFS 8.2%／TRIO 430点 PFS 47.9%／WIDE 142点 PFS 59.7%／WIN 4点 PFS 87.5%／荒れ度（発走前・1番人気オッズ）MID 41R PFS 49.7% 的中赤字 8/15／OPEN 4R PFS 82.5% 的中赤字 0/2／SOLID 38R PFS 37.9% 的中赤字 7/11／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 83R：実績 45.4% − ミラー 44.1% = Δ 1.2pt（95%区間 -24.4〜30.1、最高1R除き -6.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 191,400円（38.0%）／保護層の資金比率 0.0（84R）／組だけ的中（三連単は外れ）28R・着順まで的中 12R／的中 47R のうち的中赤字 38R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 46.1%（同じ84Rの実績 46.6%）／券種別 EXACTA 1260点 PFS 55.9%／TRIFECTA 2100点 PFS 24.2%／TRIO 1680点 PFS 67.5%／荒れ度（発走前・1番人気オッズ）MID 41R PFS 58.4% 的中赤字 17/22／OPEN 4R PFS 27.3% 的中赤字 2/2／SOLID 38R PFS 36.4% 的中赤字 18/22／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 83R：実績 46.8% − ミラー 90.2% = Δ -43.4pt（95%区間 -90.1〜1.9、最高1R除き -53.6pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 131 | 638,360 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 105 | 397,330 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 62 | 330,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 321 | 1,301,630 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 6 | 26,550 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

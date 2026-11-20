# 地方版 週次 2026-W47（自動・推薦試算・実購入なし）

- 反省済みRace 165／PAPER PFS 59.8%／正式推薦 PFS 120.6%
- 第一失敗：{'NONE': 23, 'WINNER_DISCOVERED_LOW': 5, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 9, 'CAPITAL_EFFICIENCY': 35, 'PREDICTION_ROLE_W': 55, 'PREDICTION_ROLE_P2': 22, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KSM | 34 | 52.6 | 334.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 7, 'NONE': 7} |
| MIZ | 24 | 34.4 | 21.9 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 1, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 50 | 81.4 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 7, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 7, 'PREDICTION_ROLE_W': 18, 'CAPITAL_EFFICIENCY': 9, 'EXACT_ORIENTATION': 2} |
| SON | 33 | 25.3 | 62.0 | {'PREDICTION_ROLE_W': 13, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 165 | 35.2% | 67.9% | 35.2% | 15.8% | 12.7% | 12.7% | 25.5% | 1.55 |
| 正式推薦 | 134 | 34.3% | 59.0% | 59.0% | 72.4% | 100.0% | 59.0% | 26.9% | 1.34 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中42.1%（無作為9.9%、差+32.2）／P2 平均1.0頭 的中15.8%（無作為9.9%、差+5.9）／P3 平均1.0頭 的中10.5%（無作為9.9%、差+0.6）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中64.9%（無作為29.7%、差+35.2）／P2 平均6.0頭 的中71.9%（無作為59.5%、差+12.5）／P3 平均10.42頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 4 | 3,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 72 | 350,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 44 | 167,090 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 31 | 144,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 165 | 647,690 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 4 | 22,410 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 165／PAPER PFS 59.8%／正式推薦 PFS 120.6%
- 第一失敗：{'NONE': 23, 'WINNER_DISCOVERED_LOW': 5, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 9, 'CAPITAL_EFFICIENCY': 35, 'PREDICTION_ROLE_W': 55, 'PREDICTION_ROLE_P2': 22, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KSM | 34 | 52.6 | 334.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 7, 'NONE': 7} |
| MIZ | 24 | 34.4 | 21.9 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 1, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 50 | 81.4 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 7, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 7, 'PREDICTION_ROLE_W': 18, 'CAPITAL_EFFICIENCY': 9, 'EXACT_ORIENTATION': 2} |
| SON | 33 | 25.3 | 62.0 | {'PREDICTION_ROLE_W': 13, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 165 | 35.2% | 67.9% | 35.2% | 15.8% | 12.7% | 12.7% | 25.5% | 1.55 |
| 正式推薦 | 134 | 34.3% | 59.0% | 59.0% | 72.4% | 100.0% | 59.0% | 26.9% | 1.34 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中42.1%（無作為9.9%、差+32.2）／P2 平均1.0頭 的中15.8%（無作為9.9%、差+5.9）／P3 平均1.0頭 的中10.5%（無作為9.9%、差+0.6）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中64.9%（無作為29.7%、差+35.2）／P2 平均6.0頭 的中71.9%（無作為59.5%、差+12.5）／P3 平均10.42頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 4 | 3,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 72 | 350,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 44 | 167,090 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 31 | 144,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 165 | 647,690 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 4 | 22,410 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

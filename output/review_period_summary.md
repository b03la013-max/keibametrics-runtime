# 地方版 週次 2026-W47（自動・推薦試算・実購入なし）

- 反省済みRace 141／PAPER PFS 59.7%／正式推薦 PFS 131.2%
- 第一失敗：{'NONE': 18, 'WINNER_DISCOVERED_LOW': 5, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 9, 'CAPITAL_EFFICIENCY': 28, 'PREDICTION_ROLE_W': 46, 'PREDICTION_ROLE_P2': 19, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KSM | 24 | 32.4 | 460.2 | {'PREDICTION_ROLE_W': 10, 'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 3, 'NONE': 6} |
| MIZ | 24 | 34.4 | 21.9 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 1, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 45 | 88.0 | 49.0 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 6, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 5, 'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 9, 'EXACT_ORIENTATION': 2} |
| SON | 24 | 18.8 | 53.4 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_P2': 5, 'NONE': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 141 | 32.6% | 67.4% | 32.6% | 15.6% | 11.3% | 11.3% | 24.8% | 1.56 |
| 正式推薦 | 110 | 32.7% | 58.2% | 58.2% | 71.8% | 100.0% | 58.2% | 25.5% | 1.35 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中36.4%（無作為9.4%、差+27.0）／P2 平均1.0頭 的中15.2%（無作為9.4%、差+5.8）／P3 平均1.0頭 的中3.0%（無作為9.4%、差-6.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.7%（無作為28.2%、差+38.5）／P2 平均6.0頭 的中69.7%（無作為56.3%、差+13.4）／P3 平均10.91頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 4 | 3,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 63 | 296,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 37 | 137,250 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 28 | 126,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 141 | 545,850 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 141／PAPER PFS 59.7%／正式推薦 PFS 131.2%
- 第一失敗：{'NONE': 18, 'WINNER_DISCOVERED_LOW': 5, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 9, 'CAPITAL_EFFICIENCY': 28, 'PREDICTION_ROLE_W': 46, 'PREDICTION_ROLE_P2': 19, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KSM | 24 | 32.4 | 460.2 | {'PREDICTION_ROLE_W': 10, 'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 3, 'NONE': 6} |
| MIZ | 24 | 34.4 | 21.9 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 1, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 45 | 88.0 | 49.0 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 6, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 5, 'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 9, 'EXACT_ORIENTATION': 2} |
| SON | 24 | 18.8 | 53.4 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_P2': 5, 'NONE': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 141 | 32.6% | 67.4% | 32.6% | 15.6% | 11.3% | 11.3% | 24.8% | 1.56 |
| 正式推薦 | 110 | 32.7% | 58.2% | 58.2% | 71.8% | 100.0% | 58.2% | 25.5% | 1.35 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中36.4%（無作為9.4%、差+27.0）／P2 平均1.0頭 的中15.2%（無作為9.4%、差+5.8）／P3 平均1.0頭 的中3.0%（無作為9.4%、差-6.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.7%（無作為28.2%、差+38.5）／P2 平均6.0頭 的中69.7%（無作為56.3%、差+13.4）／P3 平均10.91頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 4 | 3,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 63 | 296,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 37 | 137,250 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 28 | 126,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 141 | 545,850 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

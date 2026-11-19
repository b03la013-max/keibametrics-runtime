# 地方版 週次 2026-W47（自動・推薦試算・実購入なし）

- 反省済みRace 138／PAPER PFS 59.6%／正式推薦 PFS 133.9%
- 第一失敗：{'NONE': 18, 'WINNER_DISCOVERED_LOW': 5, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 9, 'CAPITAL_EFFICIENCY': 27, 'PREDICTION_ROLE_W': 45, 'PREDICTION_ROLE_P2': 18, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KSM | 24 | 32.4 | 460.2 | {'PREDICTION_ROLE_W': 10, 'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 3, 'NONE': 6} |
| MIZ | 24 | 34.4 | 21.9 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 1, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 42 | 89.7 | 50.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 6, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 4, 'PREDICTION_ROLE_W': 15, 'CAPITAL_EFFICIENCY': 8, 'EXACT_ORIENTATION': 2} |
| SON | 24 | 18.8 | 53.4 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_P2': 5, 'NONE': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 138 | 32.6% | 67.4% | 32.6% | 15.9% | 11.6% | 11.6% | 24.6% | 1.56 |
| 正式推薦 | 107 | 32.7% | 57.9% | 57.9% | 72.0% | 100.0% | 57.9% | 25.2% | 1.35 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中36.7%（無作為9.6%、差+27.1）／P2 平均1.0頭 的中16.7%（無作為9.6%、差+7.1）／P3 平均1.0頭 的中3.3%（無作為9.6%、差-6.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.7%（無作為28.8%、差+37.9）／P2 平均6.0頭 的中70.0%（無作為57.5%、差+12.5）／P3 平均10.63頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 4 | 3,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 62 | 290,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 36 | 136,540 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 27 | 120,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 138 | 533,140 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 138／PAPER PFS 59.6%／正式推薦 PFS 133.9%
- 第一失敗：{'NONE': 18, 'WINNER_DISCOVERED_LOW': 5, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 9, 'CAPITAL_EFFICIENCY': 27, 'PREDICTION_ROLE_W': 45, 'PREDICTION_ROLE_P2': 18, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KSM | 24 | 32.4 | 460.2 | {'PREDICTION_ROLE_W': 10, 'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 3, 'NONE': 6} |
| MIZ | 24 | 34.4 | 21.9 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 1, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 42 | 89.7 | 50.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 6, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 4, 'PREDICTION_ROLE_W': 15, 'CAPITAL_EFFICIENCY': 8, 'EXACT_ORIENTATION': 2} |
| SON | 24 | 18.8 | 53.4 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_P2': 5, 'NONE': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 138 | 32.6% | 67.4% | 32.6% | 15.9% | 11.6% | 11.6% | 24.6% | 1.56 |
| 正式推薦 | 107 | 32.7% | 57.9% | 57.9% | 72.0% | 100.0% | 57.9% | 25.2% | 1.35 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中36.7%（無作為9.6%、差+27.1）／P2 平均1.0頭 的中16.7%（無作為9.6%、差+7.1）／P3 平均1.0頭 的中3.3%（無作為9.6%、差-6.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.7%（無作為28.8%、差+37.9）／P2 平均6.0頭 的中70.0%（無作為57.5%、差+12.5）／P3 平均10.63頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 4 | 3,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 62 | 290,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 36 | 136,540 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 27 | 120,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 138 | 533,140 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

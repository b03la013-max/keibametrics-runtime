# 地方版 週次 2026-W47（自動・推薦試算・実購入なし）

- 反省済みRace 128／PAPER PFS 62.7%／正式推薦 PFS 140.0%
- 第一失敗：{'NONE': 16, 'WINNER_DISCOVERED_LOW': 5, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 9, 'CAPITAL_EFFICIENCY': 24, 'PREDICTION_ROLE_W': 41, 'PREDICTION_ROLE_P2': 17, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KSM | 21 | 36.8 | 504.0 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 3, 'NONE': 5} |
| MIZ | 24 | 34.4 | 21.9 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 1, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 38 | 97.4 | 50.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 5, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 4, 'PREDICTION_ROLE_W': 14, 'CAPITAL_EFFICIENCY': 6, 'EXACT_ORIENTATION': 2} |
| SON | 21 | 17.3 | 59.1 | {'PREDICTION_ROLE_W': 10, 'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_P2': 4, 'NONE': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 128 | 31.2% | 66.4% | 31.2% | 15.6% | 11.7% | 10.9% | 25.0% | 1.54 |
| 正式推薦 | 97 | 33.0% | 57.7% | 57.7% | 71.1% | 100.0% | 57.7% | 25.8% | 1.3 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中30.0%（無作為9.8%、差+20.2）／P2 平均1.0頭 的中15.0%（無作為9.8%、差+5.2）／P3 平均1.0頭 的中0.0%（無作為9.8%、差-9.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中70.0%（無作為29.5%、差+40.5）／P2 平均6.0頭 的中65.0%（無作為59.0%、差+6.0）／P3 平均10.35頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 4 | 3,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 58 | 266,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 33 | 125,810 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 26 | 114,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 128 | 492,410 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 128／PAPER PFS 62.7%／正式推薦 PFS 140.0%
- 第一失敗：{'NONE': 16, 'WINNER_DISCOVERED_LOW': 5, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 9, 'CAPITAL_EFFICIENCY': 24, 'PREDICTION_ROLE_W': 41, 'PREDICTION_ROLE_P2': 17, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KSM | 21 | 36.8 | 504.0 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 3, 'NONE': 5} |
| MIZ | 24 | 34.4 | 21.9 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 1, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 38 | 97.4 | 50.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 5, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 4, 'PREDICTION_ROLE_W': 14, 'CAPITAL_EFFICIENCY': 6, 'EXACT_ORIENTATION': 2} |
| SON | 21 | 17.3 | 59.1 | {'PREDICTION_ROLE_W': 10, 'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_P2': 4, 'NONE': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 128 | 31.2% | 66.4% | 31.2% | 15.6% | 11.7% | 10.9% | 25.0% | 1.54 |
| 正式推薦 | 97 | 33.0% | 57.7% | 57.7% | 71.1% | 100.0% | 57.7% | 25.8% | 1.3 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中30.0%（無作為9.8%、差+20.2）／P2 平均1.0頭 的中15.0%（無作為9.8%、差+5.2）／P3 平均1.0頭 的中0.0%（無作為9.8%、差-9.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中70.0%（無作為29.5%、差+40.5）／P2 平均6.0頭 的中65.0%（無作為59.0%、差+6.0）／P3 平均10.35頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 4 | 3,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 58 | 266,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 33 | 125,810 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 26 | 114,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 128 | 492,410 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

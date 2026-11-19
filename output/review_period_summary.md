# 地方版 週次 2026-W47（自動・推薦試算・実購入なし）

- 反省済みRace 123／PAPER PFS 61.3%／正式推薦 PFS 145.0%
- 第一失敗：{'NONE': 16, 'WINNER_DISCOVERED_LOW': 5, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 9, 'CAPITAL_EFFICIENCY': 20, 'PREDICTION_ROLE_W': 40, 'PREDICTION_ROLE_P2': 17, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KSM | 20 | 36.7 | 528.6 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 2, 'NONE': 5} |
| MIZ | 24 | 34.4 | 21.9 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 1, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 36 | 91.9 | 50.1 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 5, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 4, 'PREDICTION_ROLE_W': 14, 'CAPITAL_EFFICIENCY': 4, 'EXACT_ORIENTATION': 2} |
| SON | 19 | 16.2 | 60.6 | {'PREDICTION_ROLE_W': 9, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 4, 'NONE': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 123 | 30.9% | 65.9% | 30.9% | 15.4% | 12.2% | 9.8% | 24.4% | 1.53 |
| 正式推薦 | 92 | 32.6% | 56.5% | 56.5% | 69.6% | 100.0% | 56.5% | 22.8% | 1.25 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中26.7%（無作為9.8%、差+16.9）／P2 平均1.0頭 的中13.3%（無作為9.8%、差+3.5）／P3 平均1.0頭 的中0.0%（無作為9.8%、差-9.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.7%（無作為29.4%、差+37.3）／P2 平均6.0頭 的中53.3%（無作為58.8%、差-5.4）／P3 平均10.33頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 4 | 3,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 57 | 260,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 29 | 114,430 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 26 | 114,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 123 | 475,030 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 123／PAPER PFS 61.3%／正式推薦 PFS 145.0%
- 第一失敗：{'NONE': 16, 'WINNER_DISCOVERED_LOW': 5, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 9, 'CAPITAL_EFFICIENCY': 20, 'PREDICTION_ROLE_W': 40, 'PREDICTION_ROLE_P2': 17, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KSM | 20 | 36.7 | 528.6 | {'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 2, 'NONE': 5} |
| MIZ | 24 | 34.4 | 21.9 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 1, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 36 | 91.9 | 50.1 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 5, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 4, 'PREDICTION_ROLE_W': 14, 'CAPITAL_EFFICIENCY': 4, 'EXACT_ORIENTATION': 2} |
| SON | 19 | 16.2 | 60.6 | {'PREDICTION_ROLE_W': 9, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 4, 'NONE': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 123 | 30.9% | 65.9% | 30.9% | 15.4% | 12.2% | 9.8% | 24.4% | 1.53 |
| 正式推薦 | 92 | 32.6% | 56.5% | 56.5% | 69.6% | 100.0% | 56.5% | 22.8% | 1.25 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中26.7%（無作為9.8%、差+16.9）／P2 平均1.0頭 的中13.3%（無作為9.8%、差+3.5）／P3 平均1.0頭 的中0.0%（無作為9.8%、差-9.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.7%（無作為29.4%、差+37.3）／P2 平均6.0頭 的中53.3%（無作為58.8%、差-5.4）／P3 平均10.33頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 4 | 3,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 57 | 260,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 29 | 114,430 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 26 | 114,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 123 | 475,030 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

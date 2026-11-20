# 地方版 週次 2026-W47（自動・推薦試算・実購入なし）

- 反省済みRace 155／PAPER PFS 61.9%／正式推薦 PFS 120.1%
- 第一失敗：{'NONE': 19, 'WINNER_DISCOVERED_LOW': 5, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 9, 'CAPITAL_EFFICIENCY': 34, 'PREDICTION_ROLE_W': 51, 'PREDICTION_ROLE_P2': 21, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KSM | 30 | 54.5 | 378.5 | {'PREDICTION_ROLE_W': 12, 'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 6, 'NONE': 7} |
| MIZ | 24 | 34.4 | 21.9 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 1, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 48 | 84.3 | 45.9 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 6, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 6, 'PREDICTION_ROLE_W': 18, 'CAPITAL_EFFICIENCY': 9, 'EXACT_ORIENTATION': 2} |
| SON | 29 | 25.8 | 46.8 | {'PREDICTION_ROLE_W': 12, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 155 | 34.8% | 67.7% | 34.8% | 15.5% | 12.3% | 12.9% | 26.5% | 1.56 |
| 正式推薦 | 124 | 33.9% | 58.9% | 58.9% | 72.6% | 100.0% | 58.9% | 25.8% | 1.35 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中42.6%（無作為9.9%、差+32.7）／P2 平均1.0頭 的中14.9%（無作為9.9%、差+5.0）／P3 平均1.0頭 的中8.5%（無作為9.9%、差-1.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.0%（無作為29.6%、差+36.4）／P2 平均6.0頭 的中72.3%（無作為59.1%、差+13.2）／P3 平均10.49頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 4 | 3,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 68 | 326,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 43 | 162,340 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 30 | 138,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 155 | 612,940 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 4 | 22,410 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 155／PAPER PFS 61.9%／正式推薦 PFS 120.1%
- 第一失敗：{'NONE': 19, 'WINNER_DISCOVERED_LOW': 5, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 9, 'CAPITAL_EFFICIENCY': 34, 'PREDICTION_ROLE_W': 51, 'PREDICTION_ROLE_P2': 21, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KSM | 30 | 54.5 | 378.5 | {'PREDICTION_ROLE_W': 12, 'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 6, 'NONE': 7} |
| MIZ | 24 | 34.4 | 21.9 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 1, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 48 | 84.3 | 45.9 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 6, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 6, 'PREDICTION_ROLE_W': 18, 'CAPITAL_EFFICIENCY': 9, 'EXACT_ORIENTATION': 2} |
| SON | 29 | 25.8 | 46.8 | {'PREDICTION_ROLE_W': 12, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 155 | 34.8% | 67.7% | 34.8% | 15.5% | 12.3% | 12.9% | 26.5% | 1.56 |
| 正式推薦 | 124 | 33.9% | 58.9% | 58.9% | 72.6% | 100.0% | 58.9% | 25.8% | 1.35 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中42.6%（無作為9.9%、差+32.7）／P2 平均1.0頭 的中14.9%（無作為9.9%、差+5.0）／P3 平均1.0頭 的中8.5%（無作為9.9%、差-1.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.0%（無作為29.6%、差+36.4）／P2 平均6.0頭 的中72.3%（無作為59.1%、差+13.2）／P3 平均10.49頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 4 | 3,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 68 | 326,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 43 | 162,340 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 30 | 138,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 155 | 612,940 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 4 | 22,410 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

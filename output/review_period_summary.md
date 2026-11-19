# 地方版 週次 2026-W47（自動・推薦試算・実購入なし）

- 反省済みRace 139／PAPER PFS 60.6%／正式推薦 PFS 133.5%
- 第一失敗：{'NONE': 18, 'WINNER_DISCOVERED_LOW': 5, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 9, 'CAPITAL_EFFICIENCY': 28, 'PREDICTION_ROLE_W': 45, 'PREDICTION_ROLE_P2': 18, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KSM | 24 | 32.4 | 460.2 | {'PREDICTION_ROLE_W': 10, 'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 3, 'NONE': 6} |
| MIZ | 24 | 34.4 | 21.9 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 1, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 43 | 92.4 | 51.3 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 6, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 4, 'PREDICTION_ROLE_W': 15, 'CAPITAL_EFFICIENCY': 9, 'EXACT_ORIENTATION': 2} |
| SON | 24 | 18.8 | 53.4 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_P2': 5, 'NONE': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 139 | 33.1% | 67.6% | 33.1% | 15.8% | 11.5% | 11.5% | 25.2% | 1.56 |
| 正式推薦 | 108 | 32.4% | 58.3% | 58.3% | 72.2% | 100.0% | 58.3% | 25.9% | 1.35 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中38.7%（無作為9.6%、差+29.2）／P2 平均1.0頭 的中16.1%（無作為9.6%、差+6.6）／P3 平均1.0頭 的中3.2%（無作為9.6%、差-6.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中67.7%（無作為28.7%、差+39.1）／P2 平均6.0頭 的中71.0%（無作為57.3%、差+13.7）／P3 平均10.68頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 4 | 3,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 62 | 290,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 37 | 137,250 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 27 | 120,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 139 | 533,850 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 139／PAPER PFS 60.6%／正式推薦 PFS 133.5%
- 第一失敗：{'NONE': 18, 'WINNER_DISCOVERED_LOW': 5, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 9, 'CAPITAL_EFFICIENCY': 28, 'PREDICTION_ROLE_W': 45, 'PREDICTION_ROLE_P2': 18, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KSM | 24 | 32.4 | 460.2 | {'PREDICTION_ROLE_W': 10, 'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 3, 'NONE': 6} |
| MIZ | 24 | 34.4 | 21.9 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 1, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 43 | 92.4 | 51.3 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 6, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 4, 'PREDICTION_ROLE_W': 15, 'CAPITAL_EFFICIENCY': 9, 'EXACT_ORIENTATION': 2} |
| SON | 24 | 18.8 | 53.4 | {'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_P2': 5, 'NONE': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 139 | 33.1% | 67.6% | 33.1% | 15.8% | 11.5% | 11.5% | 25.2% | 1.56 |
| 正式推薦 | 108 | 32.4% | 58.3% | 58.3% | 72.2% | 100.0% | 58.3% | 25.9% | 1.35 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中38.7%（無作為9.6%、差+29.2）／P2 平均1.0頭 的中16.1%（無作為9.6%、差+6.6）／P3 平均1.0頭 的中3.2%（無作為9.6%、差-6.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中67.7%（無作為28.7%、差+39.1）／P2 平均6.0頭 的中71.0%（無作為57.3%、差+13.7）／P3 平均10.68頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 4 | 3,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 62 | 290,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 37 | 137,250 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 27 | 120,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 139 | 533,850 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

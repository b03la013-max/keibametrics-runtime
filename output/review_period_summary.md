# 地方版 週次 2026-W47（自動・推薦試算・実購入なし）

- 反省済みRace 57／PAPER PFS 92.4%／正式推薦 PFS 49.6%
- 第一失敗：{'NONE': 7, 'WINNER_DISCOVERED_LOW': 5, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 9, 'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_W': 10, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 18 | 95.1 | 20.4 | {'NONE': 3, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1, 'EXACT_ORIENTATION': 1} |
| MIZ | 22 | 37.9 | 25.0 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 1, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2} |
| OHI | 17 | 166.1 | 77.6 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 3, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 2} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 57 | 38.6% | 71.9% | 38.6% | 19.3% | 21.1% | 12.3% | 31.6% | 1.7 |
| 正式推薦 | 26 | 38.5% | 61.5% | 61.5% | 73.1% | 100.0% | 61.5% | 34.6% | 1.35 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 4 | 3,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 27 | 80,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 15 | 60,530 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 13 | 36,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 57 | 163,130 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 57／PAPER PFS 92.4%／正式推薦 PFS 49.6%
- 第一失敗：{'NONE': 7, 'WINNER_DISCOVERED_LOW': 5, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 9, 'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_W': 10, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 18 | 95.1 | 20.4 | {'NONE': 3, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1, 'EXACT_ORIENTATION': 1} |
| MIZ | 22 | 37.9 | 25.0 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 1, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2} |
| OHI | 17 | 166.1 | 77.6 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 3, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 2} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 57 | 38.6% | 71.9% | 38.6% | 19.3% | 21.1% | 12.3% | 31.6% | 1.7 |
| 正式推薦 | 26 | 38.5% | 61.5% | 61.5% | 73.1% | 100.0% | 61.5% | 34.6% | 1.35 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 4 | 3,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 27 | 80,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 15 | 60,530 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 13 | 36,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 57 | 163,130 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

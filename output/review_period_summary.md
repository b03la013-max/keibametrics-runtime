# 地方版 週次 2026-W47（自動・推薦試算・実購入なし）

- 反省済みRace 77／PAPER PFS 86.3%／正式推薦 PFS 41.7%
- 第一失敗：{'NONE': 9, 'WINNER_DISCOVERED_LOW': 5, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 9, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 21, 'PREDICTION_ROLE_P2': 6, 'EXACT_ORIENTATION': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KSM | 3 | 160.7 | 0.0 | {'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1} |
| MIZ | 24 | 34.4 | 21.9 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 1, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 24 | 117.6 | 59.6 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 4, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 9, 'CAPITAL_EFFICIENCY': 2, 'EXACT_ORIENTATION': 1} |
| SON | 2 | 7.9 | 2.0 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 77 | 28.6% | 68.8% | 28.6% | 16.9% | 18.2% | 9.1% | 29.9% | 1.64 |
| 正式推薦 | 46 | 30.4% | 54.3% | 54.3% | 71.7% | 100.0% | 54.3% | 23.9% | 1.26 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 4 | 3,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 38 | 146,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 20 | 78,400 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 15 | 48,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 77 | 259,000 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 77／PAPER PFS 86.3%／正式推薦 PFS 41.7%
- 第一失敗：{'NONE': 9, 'WINNER_DISCOVERED_LOW': 5, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 9, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 21, 'PREDICTION_ROLE_P2': 6, 'EXACT_ORIENTATION': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KSM | 3 | 160.7 | 0.0 | {'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1} |
| MIZ | 24 | 34.4 | 21.9 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 1, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 24 | 117.6 | 59.6 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 4, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 9, 'CAPITAL_EFFICIENCY': 2, 'EXACT_ORIENTATION': 1} |
| SON | 2 | 7.9 | 2.0 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 77 | 28.6% | 68.8% | 28.6% | 16.9% | 18.2% | 9.1% | 29.9% | 1.64 |
| 正式推薦 | 46 | 30.4% | 54.3% | 54.3% | 71.7% | 100.0% | 54.3% | 23.9% | 1.26 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 4 | 3,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 38 | 146,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 20 | 78,400 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 15 | 48,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 77 | 259,000 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

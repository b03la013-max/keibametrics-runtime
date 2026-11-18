# 地方版 週次 2026-W47（自動・推薦試算・実購入なし）

- 反省済みRace 82／PAPER PFS 81.6%／正式推薦 PFS 38.0%
- 第一失敗：{'NONE': 9, 'WINNER_DISCOVERED_LOW': 5, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 9, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 24, 'PREDICTION_ROLE_P2': 8, 'EXACT_ORIENTATION': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KSM | 5 | 109.5 | 0.0 | {'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 2} |
| MIZ | 24 | 34.4 | 21.9 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 1, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 24 | 117.6 | 59.6 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 4, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 9, 'CAPITAL_EFFICIENCY': 2, 'EXACT_ORIENTATION': 1} |
| SON | 5 | 3.1 | 0.8 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 1, 'PREDICTION_ROLE_P2': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 82 | 28.0% | 68.3% | 28.0% | 15.9% | 17.1% | 8.5% | 28.0% | 1.62 |
| 正式推薦 | 51 | 29.4% | 52.9% | 52.9% | 68.6% | 100.0% | 52.9% | 21.6% | 1.22 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 4 | 3,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 41 | 164,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 20 | 78,400 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 17 | 60,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 82 | 289,000 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 82／PAPER PFS 81.6%／正式推薦 PFS 38.0%
- 第一失敗：{'NONE': 9, 'WINNER_DISCOVERED_LOW': 5, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 9, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_W': 24, 'PREDICTION_ROLE_P2': 8, 'EXACT_ORIENTATION': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KSM | 5 | 109.5 | 0.0 | {'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 2} |
| MIZ | 24 | 34.4 | 21.9 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 1, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 24 | 117.6 | 59.6 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 4, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 9, 'CAPITAL_EFFICIENCY': 2, 'EXACT_ORIENTATION': 1} |
| SON | 5 | 3.1 | 0.8 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 1, 'PREDICTION_ROLE_P2': 1} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 82 | 28.0% | 68.3% | 28.0% | 15.9% | 17.1% | 8.5% | 28.0% | 1.62 |
| 正式推薦 | 51 | 29.4% | 52.9% | 52.9% | 68.6% | 100.0% | 52.9% | 21.6% | 1.22 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 4 | 3,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 41 | 164,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 20 | 78,400 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 17 | 60,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 82 | 289,000 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

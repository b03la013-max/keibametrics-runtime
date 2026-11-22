# 地方版 週次 2026-W47（自動・推薦試算・実購入なし）

- 反省済みRace 228／PAPER PFS 58.7%／正式推薦 PFS 98.4%
- 第一失敗：{'NONE': 34, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 51, 'PREDICTION_ROLE_W': 73, 'PREDICTION_ROLE_P2': 33, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KOC | 18 | 30.5 | 38.8 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 1, 'NONE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 6} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 36 | 56.2 | 36.0 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 5, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 7, 'EXACT_ORIENTATION': 1} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 18 | 71.6 | 42.8 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 3, 'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 5, 'NONE': 2} |
| SON | 36 | 23.6 | 56.9 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 228 | 33.8% | 68.4% | 33.8% | 17.1% | 14.0% | 11.4% | 23.7% | 1.55 |
| 正式推薦 | 190 | 33.7% | 61.6% | 61.6% | 72.6% | 100.0% | 61.6% | 29.5% | 1.41 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中35.8%（無作為9.7%、差+26.2）／P2 平均1.0頭 的中18.3%（無作為9.7%、差+8.7）／P3 平均1.0頭 的中14.2%（無作為9.7%、差+4.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.4%（無作為28.8%、差+37.5）／P2 平均6.0頭 的中72.6%（無作為57.7%、差+14.9）／P3 平均10.69頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.52/40（選択性補正込み）・能力順位 14.03/20（48R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.19/40（選択性補正込み）・能力順位 13.94/20（41R平均）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 97 | 462,730 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 63 | 234,200 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 42 | 210,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 228 | 886,500 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 4 | 22,410 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 月次 2026-11（自動・推薦試算・実購入なし）

- 反省済みRace 228／PAPER PFS 58.7%／正式推薦 PFS 98.4%
- 第一失敗：{'NONE': 34, 'WINNER_DISCOVERED_LOW': 9, 'THIRD_MISS': 3, 'P2_MISS': 6, 'WINNER_NOT_DISCOVERED': 3, 'W_WIDTH_OR_ROLE': 12, 'CAPITAL_EFFICIENCY': 51, 'PREDICTION_ROLE_W': 73, 'PREDICTION_ROLE_P2': 33, 'EXACT_ORIENTATION': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 24 | 104.2 | 44.2 | {'NONE': 4, 'WINNER_DISCOVERED_LOW': 2, 'THIRD_MISS': 1, 'P2_MISS': 2, 'WINNER_NOT_DISCOVERED': 1, 'W_WIDTH_OR_ROLE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| KOC | 18 | 30.5 | 38.8 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 1, 'NONE': 2, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 6} |
| KSM | 36 | 50.0 | 317.6 | {'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 7} |
| MIZ | 36 | 56.2 | 36.0 | {'P2_MISS': 3, 'WINNER_DISCOVERED_LOW': 1, 'W_WIDTH_OR_ROLE': 5, 'NONE': 5, 'THIRD_MISS': 1, 'WINNER_NOT_DISCOVERED': 1, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 7, 'EXACT_ORIENTATION': 1} |
| OHI | 60 | 73.8 | 55.4 | {'THIRD_MISS': 1, 'WINNER_DISCOVERED_LOW': 2, 'NONE': 10, 'W_WIDTH_OR_ROLE': 2, 'WINNER_NOT_DISCOVERED': 1, 'P2_MISS': 1, 'PREDICTION_ROLE_P2': 8, 'PREDICTION_ROLE_W': 22, 'CAPITAL_EFFICIENCY': 11, 'EXACT_ORIENTATION': 2} |
| SAG | 18 | 71.6 | 42.8 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 3, 'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 5, 'NONE': 2} |
| SON | 36 | 23.6 | 56.9 | {'PREDICTION_ROLE_W': 16, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 6, 'NONE': 4} |

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 228 | 33.8% | 68.4% | 33.8% | 17.1% | 14.0% | 11.4% | 23.7% | 1.55 |
| 正式推薦 | 190 | 33.7% | 61.6% | 61.6% | 72.6% | 100.0% | 61.6% | 29.5% | 1.41 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中35.8%（無作為9.7%、差+26.2）／P2 平均1.0頭 的中18.3%（無作為9.7%、差+8.7）／P3 平均1.0頭 的中14.2%（無作為9.7%、差+4.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.4%（無作為28.8%、差+37.5）／P2 平均6.0頭 的中72.6%（無作為57.7%、差+14.9）／P3 平均10.69頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.52/40（選択性補正込み）・能力順位 14.03/20（48R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.19/40（選択性補正込み）・能力順位 13.94/20（41R平均）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 5 | 3,540 | RECURRING |
| P0:KRS_UTILITY_NOT_AVAILABLE | P0 | 4 | 35,780 | RECURRING |
| P1:ROLE_W_MISS | P1 | 97 | 462,730 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 63 | 234,200 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 42 | 210,660 | RECURRING |
| P1:ROLE_P3_MISS | P1 | 3 | 880 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 228 | 886,500 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 4 | 22,410 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

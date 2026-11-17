# 地方版 2026-11-17 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 28／PAPER PFS 32.3%／正式推薦 PFS 43.9%
- 第一失敗：{'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 14, 'PREDICTION_ROLE_P2': 3, 'EXACT_ORIENTATION': 3, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 8 | 86.5 | 15.8 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 1, 'EXACT_ORIENTATION': 1} |
| MIZ | 12 | 4.6 | 21.9 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 8 | 14.1 | 105.1 | {'NONE': 1, 'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 1, 'EXACT_ORIENTATION': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 31／正式試行 31・発走前送信 31／本人確認 0
2. 計算完走：Full29 31／Signed FINAL 31／KRS5000 31／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 32.3%／正式推薦 43.9%／実購入なし
5. Learning：RESULT署名検証 28／学習状態保存 28／前Raceの学習状態を結合した正式Race 31（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '27/30R', 'C2-DANGER-FAV-RANK-A': '19/30R', 'C3-FAV-AS-W-WHEN-DIVERGED': '18/30R', 'C4-LOCAL-CAP-60': '27/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 28 | 21.4% | 67.9% | 21.4% | 10.7% | 10.7% | 10.7% | 17.9% | 1.54 |
| 正式推薦 | 28 | 35.7% | 50.0% | 50.0% | 71.4% | 100.0% | 50.0% | 17.9% | 1.21 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 14 | 84,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 9 | 37,600 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 28 | 139,600 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

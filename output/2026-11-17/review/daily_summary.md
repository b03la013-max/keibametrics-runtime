# 地方版 2026-11-17 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 24／PAPER PFS 31.6%／正式推薦 PFS 49.8%
- 第一失敗：{'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 11, 'PREDICTION_ROLE_P2': 3, 'EXACT_ORIENTATION': 2, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 7 | 78.8 | 18.0 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 1, 'EXACT_ORIENTATION': 1} |
| MIZ | 11 | 5.1 | 23.9 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 6 | 18.8 | 134.4 | {'NONE': 1, 'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 28／正式試行 28・発走前送信 28／本人確認 0
2. 計算完走：Full29 28／Signed FINAL 28／KRS5000 28／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 31.6%／正式推薦 49.8%／実購入なし
5. Learning：RESULT署名検証 24／学習状態保存 24／前Raceの学習状態を結合した正式Race 28（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '23/30R', 'C2-DANGER-FAV-RANK-A': '16/30R', 'C3-FAV-AS-W-WHEN-DIVERGED': '14/30R', 'C4-LOCAL-CAP-60': '23/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 24 | 25.0% | 70.8% | 25.0% | 12.5% | 8.3% | 12.5% | 16.7% | 1.62 |
| 正式推薦 | 24 | 37.5% | 54.2% | 54.2% | 75.0% | 100.0% | 54.2% | 20.8% | 1.29 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 11 | 66,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 8 | 33,700 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 24 | 117,700 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

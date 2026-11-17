# 地方版 2026-11-17 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 20／PAPER PFS 29.0%／正式推薦 PFS 58.7%
- 第一失敗：{'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 3, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 5 | 73.2 | 23.6 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1} |
| MIZ | 10 | 5.6 | 25.0 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2} |
| OHI | 5 | 22.6 | 161.2 | {'NONE': 1, 'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 25／正式試行 25・発走前送信 25／本人確認 0
2. 計算完走：Full29 25／Signed FINAL 25／KRS5000 25／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 29.0%／正式推薦 58.7%／実購入なし
5. Learning：RESULT署名検証 20／学習状態保存 20／前Raceの学習状態を結合した正式Race 25（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '19/30R', 'C2-DANGER-FAV-RANK-A': '15/30R', 'C3-FAV-AS-W-WHEN-DIVERGED': '12/30R', 'C4-LOCAL-CAP-60': '19/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 20 | 30.0% | 65.0% | 30.0% | 15.0% | 10.0% | 15.0% | 15.0% | 1.55 |
| 正式推薦 | 20 | 35.0% | 55.0% | 55.0% | 70.0% | 100.0% | 55.0% | 25.0% | 1.25 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 9 | 54,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 6 | 22,950 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 20 | 94,950 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-17 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 15／PAPER PFS 18.2%／正式推薦 PFS 75.3%
- 第一失敗：{'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 7, 'PREDICTION_ROLE_P2': 1, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 4 | 47.0 | 29.5 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 2} |
| MIZ | 8 | 1.7 | 31.2 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 1} |
| OHI | 3 | 27.1 | 254.1 | {'NONE': 1, 'PREDICTION_ROLE_W': 2} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 20／正式試行 20・発走前送信 20／本人確認 0
2. 計算完走：Full29 20／Signed FINAL 20／KRS5000 20／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 18.2%／正式推薦 75.3%／実購入なし
5. Learning：RESULT署名検証 15／学習状態保存 15／前Raceの学習状態を結合した正式Race 20（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '14/30R', 'C2-DANGER-FAV-RANK-A': '11/30R', 'C3-FAV-AS-W-WHEN-DIVERGED': '8/30R', 'C4-LOCAL-CAP-60': '14/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 15 | 33.3% | 66.7% | 33.3% | 20.0% | 13.3% | 13.3% | 13.3% | 1.53 |
| 正式推薦 | 15 | 40.0% | 53.3% | 53.3% | 80.0% | 100.0% | 53.3% | 33.3% | 1.27 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 7 | 42,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 5 | 19,590 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 15 | 67,590 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

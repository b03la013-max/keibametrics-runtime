# 地方版 2026-11-17 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 16／PAPER PFS 17.3%／正式推薦 PFS 70.6%
- 第一失敗：{'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 1, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 4 | 47.0 | 29.5 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 2} |
| MIZ | 8 | 1.7 | 31.2 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 1} |
| OHI | 4 | 20.4 | 190.5 | {'NONE': 1, 'PREDICTION_ROLE_W': 3} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 22／正式試行 22・発走前送信 22／本人確認 0
2. 計算完走：Full29 22／Signed FINAL 22／KRS5000 22／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 17.3%／正式推薦 70.6%／実購入なし
5. Learning：RESULT署名検証 16／学習状態保存 16／前Raceの学習状態を結合した正式Race 22（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '15/30R', 'C2-DANGER-FAV-RANK-A': '12/30R', 'C3-FAV-AS-W-WHEN-DIVERGED': '9/30R', 'C4-LOCAL-CAP-60': '15/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 16 | 31.2% | 62.5% | 31.2% | 18.8% | 12.5% | 12.5% | 12.5% | 1.5 |
| 正式推薦 | 16 | 37.5% | 50.0% | 50.0% | 75.0% | 100.0% | 50.0% | 31.2% | 1.25 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 8 | 48,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 5 | 19,590 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 16 | 73,590 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

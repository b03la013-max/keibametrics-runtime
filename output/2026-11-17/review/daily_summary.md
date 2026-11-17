# 地方版 2026-11-17 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 17／PAPER PFS 16.5%／正式推薦 PFS 66.5%
- 第一失敗：{'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 2, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 4 | 47.0 | 29.5 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 2} |
| MIZ | 9 | 1.6 | 27.8 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 2} |
| OHI | 4 | 20.4 | 190.5 | {'NONE': 1, 'PREDICTION_ROLE_W': 3} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 22／正式試行 22・発走前送信 22／本人確認 0
2. 計算完走：Full29 22／Signed FINAL 22／KRS5000 22／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 16.5%／正式推薦 66.5%／実購入なし
5. Learning：RESULT署名検証 17／学習状態保存 17／前Raceの学習状態を結合した正式Race 22（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '16/30R', 'C2-DANGER-FAV-RANK-A': '12/30R', 'C3-FAV-AS-W-WHEN-DIVERGED': '10/30R', 'C4-LOCAL-CAP-60': '16/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 17 | 29.4% | 58.8% | 29.4% | 17.6% | 11.8% | 11.8% | 11.8% | 1.47 |
| 正式推薦 | 17 | 35.3% | 52.9% | 52.9% | 70.6% | 100.0% | 52.9% | 29.4% | 1.29 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 8 | 48,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 5 | 19,590 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 17 | 79,590 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

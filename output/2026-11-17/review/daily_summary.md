# 地方版 2026-11-17 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 21／PAPER PFS 27.9%／正式推薦 PFS 56.3%
- 第一失敗：{'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 3, 'EXACT_ORIENTATION': 1, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 6 | 64.7 | 21.0 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1, 'EXACT_ORIENTATION': 1} |
| MIZ | 10 | 5.6 | 25.0 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2} |
| OHI | 5 | 22.6 | 161.2 | {'NONE': 1, 'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 26／正式試行 26・発走前送信 26／本人確認 0
2. 計算完走：Full29 26／Signed FINAL 26／KRS5000 26／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 27.9%／正式推薦 56.3%／実購入なし
5. Learning：RESULT署名検証 21／学習状態保存 21／前Raceの学習状態を結合した正式Race 26（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '20/30R', 'C2-DANGER-FAV-RANK-A': '16/30R', 'C3-FAV-AS-W-WHEN-DIVERGED': '12/30R', 'C4-LOCAL-CAP-60': '20/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 21 | 28.6% | 66.7% | 28.6% | 14.3% | 9.5% | 14.3% | 14.3% | 1.57 |
| 正式推薦 | 21 | 38.1% | 57.1% | 57.1% | 71.4% | 100.0% | 57.1% | 23.8% | 1.29 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 9 | 54,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 7 | 28,470 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 21 | 100,470 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

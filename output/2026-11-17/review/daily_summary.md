# 地方版 2026-11-17 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 35／PAPER PFS 38.2%／正式推薦 PFS 50.1%
- 第一失敗：{'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_W': 16, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 3, 'NONE': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 12 | 94.4 | 46.0 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1, 'NONE': 1} |
| MIZ | 12 | 4.6 | 21.9 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 11 | 10.0 | 85.3 | {'NONE': 2, 'PREDICTION_ROLE_W': 7, 'CAPITAL_EFFICIENCY': 1, 'EXACT_ORIENTATION': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 36／正式試行 36・発走前送信 36／本人確認 0
2. 計算完走：Full29 36／Signed FINAL 36／KRS5000 36／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 38.2%／正式推薦 50.1%／実購入なし
5. Learning：RESULT署名検証 35／学習状態保存 35／前Raceの学習状態を結合した正式Race 36（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '21/30R', 'C3-FAV-AS-W-WHEN-DIVERGED': '20/30R', 'C4-LOCAL-CAP-60': '30R到達'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 35 | 17.1% | 65.7% | 17.1% | 11.4% | 11.4% | 8.6% | 20.0% | 1.57 |
| 正式推薦 | 35 | 31.4% | 54.3% | 54.3% | 71.4% | 100.0% | 54.3% | 20.0% | 1.26 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 16 | 96,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 11 | 40,580 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 4 | 24,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 35 | 160,580 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-17 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 33／PAPER PFS 31.7%／正式推薦 PFS 45.7%
- 第一失敗：{'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 16, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 3, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 11 | 76.5 | 36.8 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1, 'NONE': 1} |
| MIZ | 12 | 4.6 | 21.9 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 10 | 11.3 | 84.1 | {'NONE': 1, 'PREDICTION_ROLE_W': 7, 'CAPITAL_EFFICIENCY': 1, 'EXACT_ORIENTATION': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 36／正式試行 36・発走前送信 36／本人確認 0
2. 計算完走：Full29 36／Signed FINAL 36／KRS5000 36／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 31.7%／正式推薦 45.7%／実購入なし
5. Learning：RESULT署名検証 33／学習状態保存 33／前Raceの学習状態を結合した正式Race 36（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '20/30R', 'C3-FAV-AS-W-WHEN-DIVERGED': '20/30R', 'C4-LOCAL-CAP-60': '30R到達'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 33 | 18.2% | 66.7% | 18.2% | 12.1% | 12.1% | 9.1% | 18.2% | 1.61 |
| 正式推薦 | 33 | 33.3% | 51.5% | 51.5% | 69.7% | 100.0% | 51.5% | 18.2% | 1.24 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 16 | 96,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 10 | 40,420 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 4 | 24,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 33 | 160,420 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

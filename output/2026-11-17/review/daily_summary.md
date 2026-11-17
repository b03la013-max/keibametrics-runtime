# 地方版 2026-11-17 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 27／PAPER PFS 33.3%／正式推薦 PFS 45.5%
- 第一失敗：{'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 3, 'EXACT_ORIENTATION': 3, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 8 | 86.5 | 15.8 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 1, 'EXACT_ORIENTATION': 1} |
| MIZ | 12 | 4.6 | 21.9 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 7 | 16.1 | 120.2 | {'NONE': 1, 'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 1, 'EXACT_ORIENTATION': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 30／正式試行 30・発走前送信 30／本人確認 0
2. 計算完走：Full29 30／Signed FINAL 30／KRS5000 30／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 33.3%／正式推薦 45.5%／実購入なし
5. Learning：RESULT署名検証 27／学習状態保存 27／前Raceの学習状態を結合した正式Race 30（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '26/30R', 'C2-DANGER-FAV-RANK-A': '18/30R', 'C3-FAV-AS-W-WHEN-DIVERGED': '17/30R', 'C4-LOCAL-CAP-60': '26/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 27 | 22.2% | 70.4% | 22.2% | 11.1% | 11.1% | 11.1% | 18.5% | 1.59 |
| 正式推薦 | 27 | 37.0% | 51.9% | 51.9% | 74.1% | 100.0% | 51.9% | 18.5% | 1.26 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 13 | 78,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 9 | 37,600 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 27 | 133,600 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

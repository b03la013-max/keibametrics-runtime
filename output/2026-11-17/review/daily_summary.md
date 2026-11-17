# 地方版 2026-11-17 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 29／PAPER PFS 35.6%／正式推薦 PFS 42.4%
- 第一失敗：{'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 14, 'PREDICTION_ROLE_P2': 4, 'EXACT_ORIENTATION': 3, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 9 | 91.6 | 14.0 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| MIZ | 12 | 4.6 | 21.9 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'EXACT_ORIENTATION': 1} |
| OHI | 8 | 14.1 | 105.1 | {'NONE': 1, 'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 1, 'EXACT_ORIENTATION': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 32／正式試行 32・発走前送信 32／本人確認 0
2. 計算完走：Full29 32／Signed FINAL 32／KRS5000 32／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 35.6%／正式推薦 42.4%／実購入なし
5. Learning：RESULT署名検証 29／学習状態保存 29／前Raceの学習状態を結合した正式Race 32（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '28/30R', 'C2-DANGER-FAV-RANK-A': '19/30R', 'C3-FAV-AS-W-WHEN-DIVERGED': '19/30R', 'C4-LOCAL-CAP-60': '28/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 29 | 20.7% | 69.0% | 20.7% | 10.3% | 10.3% | 10.3% | 20.7% | 1.59 |
| 正式推薦 | 29 | 37.9% | 51.7% | 51.7% | 69.0% | 100.0% | 51.7% | 17.2% | 1.24 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 14 | 84,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 9 | 37,600 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 4 | 24,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 29 | 145,600 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

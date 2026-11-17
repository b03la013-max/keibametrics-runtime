# 地方版 2026-11-17 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 6／PAPER PFS 7.6%／正式推薦 PFS 16.5%
- 第一失敗：{'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 1 | 48.6 | 43.3 | {'CAPITAL_EFFICIENCY': 1} |
| MIZ | 5 | 2.4 | 11.1 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 11／正式試行 11・発走前送信 11／本人確認 0
2. 計算完走：Full29 11／Signed FINAL 11／KRS5000 11／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 7.6%／正式推薦 16.5%／実購入なし
5. Learning：RESULT署名検証 6／学習状態保存 6／前Raceの学習状態を結合した正式Race 11（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '5/30R', 'C2-DANGER-FAV-RANK-A': '5/30R', 'C3-FAV-AS-W-WHEN-DIVERGED': '2/30R', 'C4-LOCAL-CAP-60': '5/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 6 | 50.0% | 100.0% | 50.0% | 33.3% | 16.7% | 16.7% | 16.7% | 1.83 |
| 正式推薦 | 6 | 66.7% | 66.7% | 66.7% | 100.0% | 100.0% | 66.7% | 33.3% | 1.33 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 4 | 18,070 | RECURRING |
| P1:ROLE_W_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 6 | 30,070 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

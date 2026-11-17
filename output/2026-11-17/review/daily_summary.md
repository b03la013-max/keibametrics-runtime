# 地方版 2026-11-17 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 3／PAPER PFS 4.1%／正式推薦 PFS 14.1%
- 第一失敗：{'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 3 | 4.1 | 14.1 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 4／正式試行 4・発走前送信 4／本人確認 0
2. 計算完走：Full29 4／Signed FINAL 4／KRS5000 4／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 4.1%／正式推薦 14.1%／実購入なし
5. Learning：RESULT署名検証 3／学習状態保存 3／前Raceの学習状態を結合した正式Race 4（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 3 | 33.3% | 100.0% | 33.3% | 33.3% | 0.0% | 0.0% | 0.0% | 1.67 |
| 正式推薦 | 3 | 66.7% | 66.7% | 66.7% | 100.0% | 100.0% | 66.7% | 33.3% | 1.67 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 2 | 9,460 | SINGLE_OR_FEW (過大評価しない) |
| P1:ROLE_W_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 3 | 15,460 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-17 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 7／PAPER PFS 13.0%／正式推薦 PFS 123.0%
- 第一失敗：{'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 2, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 1 | 48.6 | 43.3 | {'CAPITAL_EFFICIENCY': 1} |
| MIZ | 5 | 2.4 | 11.1 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2} |
| OHI | 1 | 61.4 | 762.2 | {'NONE': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 13／正式試行 13・発走前送信 13／本人確認 0
2. 計算完走：Full29 13／Signed FINAL 13／KRS5000 13／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 13.0%／正式推薦 123.0%／実購入なし
5. Learning：RESULT署名検証 7／学習状態保存 7／前Raceの学習状態を結合した正式Race 13（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '6/30R', 'C2-DANGER-FAV-RANK-A': '6/30R', 'C3-FAV-AS-W-WHEN-DIVERGED': '3/30R', 'C4-LOCAL-CAP-60': '6/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 7 | 57.1% | 100.0% | 57.1% | 42.9% | 14.3% | 14.3% | 14.3% | 1.86 |
| 正式推薦 | 7 | 71.4% | 71.4% | 71.4% | 100.0% | 100.0% | 71.4% | 42.9% | 1.43 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 4 | 18,070 | RECURRING |
| P1:ROLE_W_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 7 | 30,070 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

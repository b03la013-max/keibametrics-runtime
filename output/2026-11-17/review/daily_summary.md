# 地方版 2026-11-17 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 10／PAPER PFS 9.1%／正式推薦 PFS 105.5%
- 第一失敗：{'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 2 | 14.8 | 21.7 | {'CAPITAL_EFFICIENCY': 1, 'PREDICTION_ROLE_W': 1} |
| MIZ | 6 | 2.1 | 41.6 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 2} |
| OHI | 2 | 30.7 | 381.1 | {'NONE': 1, 'PREDICTION_ROLE_W': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 16／正式試行 16・発走前送信 16／本人確認 0
2. 計算完走：Full29 16／Signed FINAL 16／KRS5000 16／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 9.1%／正式推薦 105.5%／実購入なし
5. Learning：RESULT署名検証 10／学習状態保存 10／前Raceの学習状態を結合した正式Race 16（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '9/30R', 'C2-DANGER-FAV-RANK-A': '8/30R', 'C3-FAV-AS-W-WHEN-DIVERGED': '4/30R', 'C4-LOCAL-CAP-60': '9/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 10 | 50.0% | 90.0% | 50.0% | 30.0% | 10.0% | 20.0% | 10.0% | 1.6 |
| 正式推薦 | 10 | 60.0% | 60.0% | 60.0% | 90.0% | 100.0% | 60.0% | 40.0% | 1.3 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 4 | 24,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 4 | 18,070 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 10 | 42,070 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

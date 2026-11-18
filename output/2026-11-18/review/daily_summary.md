# 地方版 2026-11-18 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 19／PAPER PFS 37.3%／正式推薦 PFS 57.1%
- 第一失敗：{'PREDICTION_ROLE_W': 11, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 4, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 9 | 66.9 | 4.7 | {'PREDICTION_ROLE_W': 6, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1} |
| OHI | 1 | 67.1 | 0.0 | {'PREDICTION_ROLE_W': 1} |
| SON | 9 | 5.7 | 115.9 | {'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_P2': 1, 'NONE': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 24／正式試行 24・発走前送信 24／本人確認 0
2. 計算完走：Full29 24／Signed FINAL 24／KRS5000 24／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 37.3%／正式推薦 57.1%／実購入なし
5. Learning：RESULT署名検証 19／学習状態保存 19／前Raceの学習状態を結合した正式Race 24（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '30R到達', 'C5-SMALL-POINTS': '18/30R', 'C6-CHECK10-REVISION': '9/30R', 'C7-KAMETANI-BUY-MATCH': '21/30R', 'C8-ODDS-GAP-FAVORITE': '16/30R', 'C9-BENTER-COMBINATION': '15/30R', 'C10-HARVILLE-DISCOUNT': '15/30R', 'C11-FIXED-2-4-8-VS-AKI-FORM': '18/30R', 'C12-AKI-VS-MARKET-ROUGHNESS': '18/30R', 'C13-FORMAL-MIX-P2BOX20': '2/30R', 'C14-FORMAL-P2BOX20-ONLY': '2/30R', 'C15-FORMAL-MIX-WAXIS-TRIO': '2/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 19 | 10.5% | 47.4% | 10.5% | 21.1% | 5.3% | 0.0% | 15.8% | 1.37 |
| 正式推薦 | 19 | 21.1% | 42.1% | 42.1% | 68.4% | 100.0% | 42.1% | 15.8% | 1.16 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 11 | 66,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 4 | 16,170 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 19 | 100,170 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

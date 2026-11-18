# 地方版 2026-11-18 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 24／PAPER PFS 31.1%／正式推薦 PFS 50.9%
- 第一失敗：{'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 6, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 11 | 56.0 | 8.5 | {'PREDICTION_ROLE_W': 6, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2, 'NONE': 1} |
| OHI | 3 | 29.1 | 28.4 | {'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 1} |
| SON | 10 | 5.2 | 104.3 | {'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_P2': 1, 'NONE': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 29／正式試行 29・発走前送信 29／本人確認 0
2. 計算完走：Full29 29／Signed FINAL 29／KRS5000 29／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 31.1%／正式推薦 50.9%／実購入なし
5. Learning：RESULT署名検証 24／学習状態保存 24／前Raceの学習状態を結合した正式Race 29（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '30R到達', 'C5-SMALL-POINTS': '23/30R', 'C6-CHECK10-REVISION': '13/30R', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '21/30R', 'C9-BENTER-COMBINATION': '20/30R', 'C10-HARVILLE-DISCOUNT': '20/30R', 'C11-FIXED-2-4-8-VS-AKI-FORM': '23/30R', 'C12-AKI-VS-MARKET-ROUGHNESS': '23/30R', 'C13-FORMAL-MIX-P2BOX20': '3/30R', 'C14-FORMAL-P2BOX20-ONLY': '3/30R', 'C15-FORMAL-MIX-WAXIS-TRIO': '3/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 24 | 20.8% | 54.2% | 20.8% | 20.8% | 4.2% | 0.0% | 12.5% | 1.38 |
| 正式推薦 | 24 | 29.2% | 45.8% | 45.8% | 75.0% | 100.0% | 45.8% | 16.7% | 1.21 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 13 | 78,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 7 | 25,960 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 24 | 121,960 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

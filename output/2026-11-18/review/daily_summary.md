# 地方版 2026-11-18 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 21／PAPER PFS 35.4%／正式推薦 PFS 57.3%
- 第一失敗：{'PREDICTION_ROLE_W': 11, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 5, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 10 | 61.0 | 7.6 | {'PREDICTION_ROLE_W': 6, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1, 'NONE': 1} |
| OHI | 2 | 47.9 | 42.6 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 1} |
| SON | 9 | 5.7 | 115.9 | {'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_P2': 1, 'NONE': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 27／正式試行 27・発走前送信 27／本人確認 0
2. 計算完走：Full29 27／Signed FINAL 27／KRS5000 27／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 35.4%／正式推薦 57.3%／実購入なし
5. Learning：RESULT署名検証 21／学習状態保存 21／前Raceの学習状態を結合した正式Race 27（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '30R到達', 'C5-SMALL-POINTS': '20/30R', 'C6-CHECK10-REVISION': '11/30R', 'C7-KAMETANI-BUY-MATCH': '26/30R', 'C8-ODDS-GAP-FAVORITE': '18/30R', 'C9-BENTER-COMBINATION': '17/30R', 'C10-HARVILLE-DISCOUNT': '17/30R', 'C11-FIXED-2-4-8-VS-AKI-FORM': '20/30R', 'C12-AKI-VS-MARKET-ROUGHNESS': '20/30R', 'C13-FORMAL-MIX-P2BOX20': '2/30R', 'C14-FORMAL-P2BOX20-ONLY': '2/30R', 'C15-FORMAL-MIX-WAXIS-TRIO': '2/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 21 | 19.0% | 52.4% | 19.0% | 23.8% | 4.8% | 0.0% | 14.3% | 1.38 |
| 正式推薦 | 21 | 28.6% | 47.6% | 47.6% | 71.4% | 100.0% | 47.6% | 19.0% | 1.24 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 11 | 66,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 6 | 21,050 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 21 | 105,050 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

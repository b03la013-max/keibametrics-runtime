# 地方版 2026-11-18 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 18／PAPER PFS 39.7%／正式推薦 PFS 7.2%
- 第一失敗：{'PREDICTION_ROLE_W': 11, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 9 | 66.9 | 4.7 | {'PREDICTION_ROLE_W': 6, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1} |
| OHI | 1 | 67.1 | 0.0 | {'PREDICTION_ROLE_W': 1} |
| SON | 8 | 6.5 | 11.0 | {'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_P2': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 23／正式試行 23・発走前送信 23／本人確認 0
2. 計算完走：Full29 23／Signed FINAL 23／KRS5000 23／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 39.7%／正式推薦 7.2%／実購入なし
5. Learning：RESULT署名検証 18／学習状態保存 18／前Raceの学習状態を結合した正式Race 23（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '30R到達', 'C5-SMALL-POINTS': '17/30R', 'C6-CHECK10-REVISION': '9/30R', 'C7-KAMETANI-BUY-MATCH': '20/30R', 'C8-ODDS-GAP-FAVORITE': '15/30R', 'C9-BENTER-COMBINATION': '14/30R', 'C10-HARVILLE-DISCOUNT': '14/30R', 'C11-FIXED-2-4-8-VS-AKI-FORM': '17/30R', 'C12-AKI-VS-MARKET-ROUGHNESS': '17/30R', 'C13-FORMAL-MIX-P2BOX20': '1/30R', 'C14-FORMAL-P2BOX20-ONLY': '1/30R', 'C15-FORMAL-MIX-WAXIS-TRIO': '1/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 18 | 11.1% | 50.0% | 11.1% | 22.2% | 5.6% | 0.0% | 16.7% | 1.39 |
| 正式推薦 | 18 | 16.7% | 38.9% | 38.9% | 66.7% | 100.0% | 38.9% | 11.1% | 1.06 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 11 | 66,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 4 | 16,170 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 18 | 100,170 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-18 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 13／PAPER PFS 49.3%／正式推薦 PFS 0.3%
- 第一失敗：{'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 7 | 83.1 | 0.0 | {'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2} |
| SON | 6 | 2.6 | 0.7 | {'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 1, 'PREDICTION_ROLE_P2': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 18／正式試行 18・発走前送信 18／本人確認 0
2. 計算完走：Full29 18／Signed FINAL 18／KRS5000 18／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 49.3%／正式推薦 0.3%／実購入なし
5. Learning：RESULT署名検証 13／学習状態保存 13／前Raceの学習状態を結合した正式Race 18（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '29/30R', 'C3-FAV-AS-W-WHEN-DIVERGED': '28/30R', 'C4-LOCAL-CAP-60': '30R到達', 'C5-SMALL-POINTS': '12/30R', 'C6-CHECK10-REVISION': '7/30R', 'C7-KAMETANI-BUY-MATCH': '13/30R', 'C8-ODDS-GAP-FAVORITE': '10/30R', 'C9-BENTER-COMBINATION': '9/30R', 'C10-HARVILLE-DISCOUNT': '9/30R', 'C11-FIXED-2-4-8-VS-AKI-FORM': '12/30R', 'C12-AKI-VS-MARKET-ROUGHNESS': '12/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 13 | 7.7% | 53.8% | 7.7% | 7.7% | 0.0% | 0.0% | 7.7% | 1.23 |
| 正式推薦 | 13 | 15.4% | 30.8% | 30.8% | 53.8% | 100.0% | 30.8% | 0.0% | 0.85 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 9 | 54,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 1 | 5,760 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 13 | 77,760 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

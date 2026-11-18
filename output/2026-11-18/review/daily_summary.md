# 地方版 2026-11-18 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 14／PAPER PFS 46.1%／正式推薦 PFS 3.4%
- 第一失敗：{'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 7 | 83.1 | 0.0 | {'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2} |
| SON | 7 | 2.2 | 6.7 | {'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_P2': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 19／正式試行 19・発走前送信 19／本人確認 0
2. 計算完走：Full29 19／Signed FINAL 19／KRS5000 19／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 46.1%／正式推薦 3.4%／実購入なし
5. Learning：RESULT署名検証 14／学習状態保存 14／前Raceの学習状態を結合した正式Race 19（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '28/30R', 'C4-LOCAL-CAP-60': '30R到達', 'C5-SMALL-POINTS': '13/30R', 'C6-CHECK10-REVISION': '8/30R', 'C7-KAMETANI-BUY-MATCH': '15/30R', 'C8-ODDS-GAP-FAVORITE': '11/30R', 'C9-BENTER-COMBINATION': '10/30R', 'C10-HARVILLE-DISCOUNT': '10/30R', 'C11-FIXED-2-4-8-VS-AKI-FORM': '13/30R', 'C12-AKI-VS-MARKET-ROUGHNESS': '13/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 14 | 7.1% | 50.0% | 7.1% | 14.3% | 0.0% | 0.0% | 7.1% | 1.21 |
| 正式推薦 | 14 | 14.3% | 35.7% | 35.7% | 57.1% | 100.0% | 35.7% | 7.1% | 0.93 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 9 | 54,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 2 | 9,170 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 14 | 81,170 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

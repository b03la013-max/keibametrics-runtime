# 地方版 2026-11-18 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 11／PAPER PFS 57.3%／正式推薦 PFS 0.4%
- 第一失敗：{'PREDICTION_ROLE_W': 7, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 6 | 94.5 | 0.0 | {'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2} |
| SON | 5 | 3.1 | 0.8 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 1, 'PREDICTION_ROLE_P2': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 15／正式試行 15・発走前送信 15／本人確認 0
2. 計算完走：Full29 15／Signed FINAL 15／KRS5000 15／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 57.3%／正式推薦 0.4%／実購入なし
5. Learning：RESULT署名検証 11／学習状態保存 11／前Raceの学習状態を結合した正式Race 15（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '28/30R', 'C3-FAV-AS-W-WHEN-DIVERGED': '27/30R', 'C4-LOCAL-CAP-60': '30R到達', 'C5-SMALL-POINTS': '10/30R', 'C6-CHECK10-REVISION': '5/30R', 'C7-KAMETANI-BUY-MATCH': '11/30R', 'C8-ODDS-GAP-FAVORITE': '8/30R', 'C9-BENTER-COMBINATION': '7/30R', 'C10-HARVILLE-DISCOUNT': '7/30R', 'C11-FIXED-2-4-8-VS-AKI-FORM': '10/30R', 'C12-AKI-VS-MARKET-ROUGHNESS': '10/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 11 | 9.1% | 54.5% | 9.1% | 9.1% | 0.0% | 0.0% | 9.1% | 1.27 |
| 正式推薦 | 11 | 18.2% | 36.4% | 36.4% | 54.5% | 100.0% | 36.4% | 0.0% | 0.91 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 7 | 42,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 1 | 5,760 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 11 | 65,760 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

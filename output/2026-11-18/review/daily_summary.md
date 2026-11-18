# 地方版 2026-11-18 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 16／PAPER PFS 40.3%／正式推薦 PFS 8.2%
- 第一失敗：{'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 8 | 74.2 | 5.3 | {'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1} |
| SON | 8 | 6.5 | 11.0 | {'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_P2': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 21／正式試行 21・発走前送信 21／本人確認 0
2. 計算完走：Full29 21／Signed FINAL 21／KRS5000 21／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 40.3%／正式推薦 8.2%／実購入なし
5. Learning：RESULT署名検証 16／学習状態保存 16／前Raceの学習状態を結合した正式Race 21（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '29/30R', 'C4-LOCAL-CAP-60': '30R到達', 'C5-SMALL-POINTS': '15/30R', 'C6-CHECK10-REVISION': '8/30R', 'C7-KAMETANI-BUY-MATCH': '18/30R', 'C8-ODDS-GAP-FAVORITE': '13/30R', 'C9-BENTER-COMBINATION': '12/30R', 'C10-HARVILLE-DISCOUNT': '12/30R', 'C11-FIXED-2-4-8-VS-AKI-FORM': '15/30R', 'C12-AKI-VS-MARKET-ROUGHNESS': '15/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 16 | 12.5% | 56.2% | 12.5% | 18.8% | 0.0% | 0.0% | 12.5% | 1.38 |
| 正式推薦 | 16 | 18.8% | 43.8% | 43.8% | 62.5% | 100.0% | 43.8% | 12.5% | 1.0 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 9 | 54,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 4 | 16,170 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 16 | 88,170 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

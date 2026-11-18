# 地方版 2026-11-18 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 34／PAPER PFS 33.2%／正式推薦 PFS 39.9%
- 第一失敗：{'PREDICTION_ROLE_W': 17, 'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 8, 'NONE': 2, 'EXACT_ORIENTATION': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 12 | 51.8 | 7.8 | {'PREDICTION_ROLE_W': 7, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2, 'NONE': 1} |
| OHI | 10 | 27.5 | 11.6 | {'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 2, 'EXACT_ORIENTATION': 1, 'PREDICTION_ROLE_P2': 2} |
| SON | 12 | 21.1 | 95.5 | {'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_P2': 2, 'NONE': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 35／正式試行 35・発走前送信 35／本人確認 0
2. 計算完走：Full29 35／Signed FINAL 35／KRS5000 35／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 33.2%／正式推薦 39.9%／実購入なし
5. Learning：RESULT署名検証 34／学習状態保存 34／前Raceの学習状態を結合した正式Race 35（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '30R到達', 'C5-SMALL-POINTS': '30R到達', 'C6-CHECK10-REVISION': '18/30R', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '30R到達', 'C9-BENTER-COMBINATION': '30R到達', 'C10-HARVILLE-DISCOUNT': '30R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '30R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '8/30R', 'C14-FORMAL-P2BOX20-ONLY': '8/30R', 'C15-FORMAL-MIX-WAXIS-TRIO': '8/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 34 | 29.4% | 64.7% | 29.4% | 14.7% | 2.9% | 5.9% | 14.7% | 1.38 |
| 正式推薦 | 34 | 29.4% | 50.0% | 50.0% | 73.5% | 100.0% | 50.0% | 14.7% | 1.21 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 17 | 102,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 9 | 36,110 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 6 | 36,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 34 | 174,110 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

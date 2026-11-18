# 地方版 2026-11-18 日次総括（自動・推薦試算・実購入なし）

- 反省済みRace 36／PAPER PFS 38.2%／正式推薦 PFS 45.1%
- 第一失敗：{'PREDICTION_ROLE_W': 17, 'PREDICTION_ROLE_P2': 7, 'CAPITAL_EFFICIENCY': 8, 'NONE': 3, 'EXACT_ORIENTATION': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 12 | 51.8 | 7.8 | {'PREDICTION_ROLE_W': 7, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2, 'NONE': 1} |
| OHI | 12 | 43.7 | 32.0 | {'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 2, 'EXACT_ORIENTATION': 1, 'PREDICTION_ROLE_P2': 3, 'NONE': 1} |
| SON | 12 | 21.1 | 95.5 | {'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_P2': 2, 'NONE': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 36／正式試行 36・発走前送信 36／本人確認 0
2. 計算完走：Full29 36／Signed FINAL 36／KRS5000 36／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 38.2%／正式推薦 45.1%／実購入なし
5. Learning：RESULT署名検証 36／学習状態保存 36／前Raceの学習状態を結合した正式Race 36（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '30R到達', 'C5-SMALL-POINTS': '30R到達', 'C6-CHECK10-REVISION': '19/30R', 'C7-KAMETANI-BUY-MATCH': '0/30R', 'C8-ODDS-GAP-FAVORITE': '30R到達', 'C9-BENTER-COMBINATION': '30R到達', 'C10-HARVILLE-DISCOUNT': '30R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '30R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '9/30R', 'C14-FORMAL-P2BOX20-ONLY': '9/30R', 'C15-FORMAL-MIX-WAXIS-TRIO': '9/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 36 | 33.3% | 66.7% | 33.3% | 13.9% | 2.8% | 5.6% | 16.7% | 1.39 |
| 正式推薦 | 36 | 33.3% | 52.8% | 52.8% | 72.2% | 100.0% | 52.8% | 16.7% | 1.22 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 17 | 102,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 9 | 36,110 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 7 | 42,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 36 | 180,110 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

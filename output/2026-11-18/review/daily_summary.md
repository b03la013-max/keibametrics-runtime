# 地方版 2026-11-18 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 28／PAPER PFS 33.8%／正式推薦 PFS 47.8%
- 第一失敗：{'PREDICTION_ROLE_W': 14, 'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 7, 'NONE': 2, 'EXACT_ORIENTATION': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 12 | 51.8 | 7.8 | {'PREDICTION_ROLE_W': 7, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2, 'NONE': 1} |
| OHI | 4 | 22.3 | 24.4 | {'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 1, 'EXACT_ORIENTATION': 1} |
| SON | 12 | 21.1 | 95.5 | {'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_P2': 2, 'NONE': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 30／正式試行 30・発走前送信 30／本人確認 0
2. 計算完走：Full29 30／Signed FINAL 30／KRS5000 30／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 33.8%／正式推薦 47.8%／実購入なし
5. Learning：RESULT署名検証 28／学習状態保存 28／前Raceの学習状態を結合した正式Race 30（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '30R到達', 'C5-SMALL-POINTS': '27/30R', 'C6-CHECK10-REVISION': '15/30R', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '25/30R', 'C9-BENTER-COMBINATION': '24/30R', 'C10-HARVILLE-DISCOUNT': '24/30R', 'C11-FIXED-2-4-8-VS-AKI-FORM': '27/30R', 'C12-AKI-VS-MARKET-ROUGHNESS': '27/30R', 'C13-FORMAL-MIX-P2BOX20': '5/30R', 'C14-FORMAL-P2BOX20-ONLY': '5/30R', 'C15-FORMAL-MIX-WAXIS-TRIO': '5/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 28 | 25.0% | 57.1% | 25.0% | 17.9% | 3.6% | 3.6% | 14.3% | 1.36 |
| 正式推薦 | 28 | 32.1% | 50.0% | 50.0% | 75.0% | 100.0% | 50.0% | 17.9% | 1.21 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 14 | 84,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 8 | 31,220 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 4 | 24,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 28 | 139,220 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

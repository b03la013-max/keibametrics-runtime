# 地方版 2026-11-18 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 27／PAPER PFS 36.4%／正式推薦 PFS 49.5%
- 第一失敗：{'PREDICTION_ROLE_W': 14, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 7, 'NONE': 2, 'EXACT_ORIENTATION': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 12 | 51.8 | 7.8 | {'PREDICTION_ROLE_W': 7, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2, 'NONE': 1} |
| OHI | 4 | 22.3 | 24.4 | {'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 1, 'EXACT_ORIENTATION': 1} |
| SON | 11 | 24.9 | 104.2 | {'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_P2': 1, 'NONE': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 30／正式試行 30・発走前送信 30／本人確認 0
2. 計算完走：Full29 30／Signed FINAL 30／KRS5000 30／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 36.4%／正式推薦 49.5%／実購入なし
5. Learning：RESULT署名検証 27／学習状態保存 27／前Raceの学習状態を結合した正式Race 30（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '30R到達', 'C5-SMALL-POINTS': '26/30R', 'C6-CHECK10-REVISION': '15/30R', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '24/30R', 'C9-BENTER-COMBINATION': '23/30R', 'C10-HARVILLE-DISCOUNT': '23/30R', 'C11-FIXED-2-4-8-VS-AKI-FORM': '26/30R', 'C12-AKI-VS-MARKET-ROUGHNESS': '26/30R', 'C13-FORMAL-MIX-P2BOX20': '4/30R', 'C14-FORMAL-P2BOX20-ONLY': '4/30R', 'C15-FORMAL-MIX-WAXIS-TRIO': '4/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 27 | 22.2% | 55.6% | 22.2% | 18.5% | 3.7% | 0.0% | 14.8% | 1.37 |
| 正式推薦 | 27 | 33.3% | 48.1% | 48.1% | 77.8% | 100.0% | 48.1% | 18.5% | 1.22 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 14 | 84,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 8 | 31,220 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 27 | 133,220 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

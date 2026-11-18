# 地方版 2026-11-18 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 26／PAPER PFS 37.6%／正式推薦 PFS 51.4%
- 第一失敗：{'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 7, 'NONE': 2, 'EXACT_ORIENTATION': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 11 | 56.0 | 8.5 | {'PREDICTION_ROLE_W': 6, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2, 'NONE': 1} |
| OHI | 4 | 22.3 | 24.4 | {'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 1, 'EXACT_ORIENTATION': 1} |
| SON | 11 | 24.9 | 104.2 | {'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_P2': 1, 'NONE': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 30／正式試行 30・発走前送信 30／本人確認 0
2. 計算完走：Full29 30／Signed FINAL 30／KRS5000 30／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 37.6%／正式推薦 51.4%／実購入なし
5. Learning：RESULT署名検証 26／学習状態保存 26／前Raceの学習状態を結合した正式Race 30（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '30R到達', 'C5-SMALL-POINTS': '25/30R', 'C6-CHECK10-REVISION': '14/30R', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '23/30R', 'C9-BENTER-COMBINATION': '22/30R', 'C10-HARVILLE-DISCOUNT': '22/30R', 'C11-FIXED-2-4-8-VS-AKI-FORM': '25/30R', 'C12-AKI-VS-MARKET-ROUGHNESS': '25/30R', 'C13-FORMAL-MIX-P2BOX20': '4/30R', 'C14-FORMAL-P2BOX20-ONLY': '4/30R', 'C15-FORMAL-MIX-WAXIS-TRIO': '4/30R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 26 | 23.1% | 57.7% | 23.1% | 19.2% | 3.8% | 0.0% | 15.4% | 1.38 |
| 正式推薦 | 26 | 34.6% | 50.0% | 50.0% | 76.9% | 100.0% | 50.0% | 19.2% | 1.23 |

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 13 | 78,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 8 | 31,220 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 26 | 127,220 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

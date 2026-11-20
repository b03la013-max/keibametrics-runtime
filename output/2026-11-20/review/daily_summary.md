# 地方版 2026-11-20 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 20／PAPER PFS 66.8%／正式推薦 PFS 82.7%
- 第一失敗：{'CAPITAL_EFFICIENCY': 7, 'NONE': 5, 'PREDICTION_ROLE_W': 6, 'PREDICTION_ROLE_P2': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 9 | 109.0 | 36.8 | {'CAPITAL_EFFICIENCY': 4, 'NONE': 1, 'PREDICTION_ROLE_W': 4} |
| OHI | 2 | 0.0 | 278.3 | {'PREDICTION_ROLE_P2': 1, 'NONE': 1} |
| SON | 9 | 41.5 | 85.1 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 2, 'NONE': 3} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 26／正式試行 26・発走前送信 26／本人確認 0
2. 計算完走：Full29 26／Signed FINAL 26／KRS5000 26／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 66.8%／正式推薦 82.7%／実購入なし
5. Learning：RESULT署名検証 20／学習状態保存 20／前Raceの学習状態を結合した正式Race 26（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '30R到達', 'C6-CHECK10-REVISION': '30R到達', 'C7-KAMETANI-BUY-MATCH': '17/30R', 'C8-ODDS-GAP-FAVORITE': '30R到達', 'C9-BENTER-COMBINATION': '30R到達', 'C10-HARVILLE-DISCOUNT': '30R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '30R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '30R到達', 'C14-FORMAL-P2BOX20-ONLY': '30R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '30R到達', 'C22-KEEP-MEC-TRIO20': '19/30R', 'C23-THIRD3-BY-PAIR': '19/30R', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '19/30R', 'C16-W-INDEX-CONSENSUS': '30R到達', 'C17-P2-ZAI-PLACE': '30R到達', 'C18-W-PLUS-FAVORITE': '30R到達', 'C19-W-PLUS-TOP2-POP': '30R到達', 'C20-P2-PLUS-TOP3-POP': '30R到達', 'C21-BVI-L-R2-TERTILE': '60/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 20 | 50.0% | 70.0% | 50.0% | 20.0% | 25.0% | 20.0% | 30.0% | 1.55 |
| 正式推薦 | 20 | 45.0% | 70.0% | 70.0% | 80.0% | 100.0% | 70.0% | 40.0% | 1.4 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中50.0%（無作為10.9%、差+39.1）／P2 平均1.0頭 的中20.0%（無作為10.9%、差+9.1）／P3 平均1.0頭 的中25.0%（無作為10.9%、差+14.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中70.0%（無作為32.6%、差+37.4）／P2 平均6.0頭 的中80.0%（無作為65.2%、差+14.8）／P3 平均9.55頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 7 | 29,840 | RECURRING |
| P1:ROLE_W_MISS | P1 | 6 | 36,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 20 | 77,840 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 10,410 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

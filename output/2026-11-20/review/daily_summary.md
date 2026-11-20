# 地方版 2026-11-20 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 21／PAPER PFS 64.6%／正式推薦 PFS 78.7%
- 第一失敗：{'CAPITAL_EFFICIENCY': 7, 'NONE': 5, 'PREDICTION_ROLE_W': 7, 'PREDICTION_ROLE_P2': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 10 | 100.0 | 33.1 | {'CAPITAL_EFFICIENCY': 4, 'NONE': 1, 'PREDICTION_ROLE_W': 5} |
| OHI | 2 | 0.0 | 278.3 | {'PREDICTION_ROLE_P2': 1, 'NONE': 1} |
| SON | 9 | 41.5 | 85.1 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 2, 'NONE': 3} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 27／正式試行 27・発走前送信 27／本人確認 0
2. 計算完走：Full29 27／Signed FINAL 27／KRS5000 27／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 64.6%／正式推薦 78.7%／実購入なし
5. Learning：RESULT署名検証 21／学習状態保存 21／前Raceの学習状態を結合した正式Race 27（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '30R到達', 'C6-CHECK10-REVISION': '30R到達', 'C7-KAMETANI-BUY-MATCH': '18/30R', 'C8-ODDS-GAP-FAVORITE': '30R到達', 'C9-BENTER-COMBINATION': '30R到達', 'C10-HARVILLE-DISCOUNT': '30R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '30R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '30R到達', 'C14-FORMAL-P2BOX20-ONLY': '30R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '30R到達', 'C22-KEEP-MEC-TRIO20': '20/30R', 'C23-THIRD3-BY-PAIR': '20/30R', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '20/30R', 'C16-W-INDEX-CONSENSUS': '30R到達', 'C17-P2-ZAI-PLACE': '30R到達', 'C18-W-PLUS-FAVORITE': '30R到達', 'C19-W-PLUS-TOP2-POP': '30R到達', 'C20-P2-PLUS-TOP3-POP': '30R到達', 'C21-BVI-L-R2-TERTILE': '60/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 21 | 52.4% | 71.4% | 52.4% | 19.0% | 23.8% | 23.8% | 28.6% | 1.52 |
| 正式推薦 | 21 | 42.9% | 66.7% | 66.7% | 81.0% | 100.0% | 66.7% | 38.1% | 1.38 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中52.4%（無作為10.8%、差+41.6）／P2 平均1.0頭 的中19.0%（無作為10.8%、差+8.2）／P3 平均1.0頭 的中23.8%（無作為10.8%、差+13.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.7%（無作為32.5%、差+34.2）／P2 平均6.0頭 的中81.0%（無作為64.9%、差+16.0）／P3 平均9.57頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 7 | 42,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 7 | 29,840 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 21 | 83,840 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 10,410 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

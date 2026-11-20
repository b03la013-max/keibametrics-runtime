# 地方版 2026-11-20 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 30／PAPER PFS 49.7%／正式推薦 PFS 61.6%
- 第一失敗：{'CAPITAL_EFFICIENCY': 9, 'NONE': 6, 'PREDICTION_ROLE_W': 12, 'PREDICTION_ROLE_P2': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 12 | 85.3 | 32.4 | {'CAPITAL_EFFICIENCY': 5, 'NONE': 1, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 1} |
| OHI | 6 | 17.5 | 115.8 | {'PREDICTION_ROLE_P2': 1, 'NONE': 2, 'CAPITAL_EFFICIENCY': 1, 'PREDICTION_ROLE_W': 2} |
| SON | 12 | 33.3 | 63.8 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 5, 'NONE': 3} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 31／正式試行 31・発走前送信 31／本人確認 0
2. 計算完走：Full29 31／Signed FINAL 31／KRS5000 31／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 49.7%／正式推薦 61.6%／実購入なし
5. Learning：RESULT署名検証 30／学習状態保存 30／前Raceの学習状態を結合した正式Race 31（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '30R到達', 'C7-KAMETANI-BUY-MATCH': '22/30R', 'C8-ODDS-GAP-FAVORITE': '30R到達', 'C9-BENTER-COMBINATION': '30R到達', 'C10-HARVILLE-DISCOUNT': '30R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '30R到達', 'C14-FORMAL-P2BOX20-ONLY': '30R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '30R到達', 'C22-KEEP-MEC-TRIO20': '29/30R', 'C23-THIRD3-BY-PAIR': '29/30R', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '29/30R', 'C16-W-INDEX-CONSENSUS': '30R到達', 'C17-P2-ZAI-PLACE': '30R到達', 'C18-W-PLUS-FAVORITE': '30R到達', 'C19-W-PLUS-TOP2-POP': '30R到達', 'C20-P2-PLUS-TOP3-POP': '30R到達', 'C21-BVI-L-R2-TERTILE': '60/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 30 | 46.7% | 73.3% | 46.7% | 23.3% | 16.7% | 20.0% | 23.3% | 1.53 |
| 正式推薦 | 30 | 36.7% | 60.0% | 60.0% | 83.3% | 100.0% | 60.0% | 33.3% | 1.37 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中46.7%（無作為10.3%、差+36.4）／P2 平均1.0頭 的中23.3%（無作為10.3%、差+13.0）／P3 平均1.0頭 的中16.7%（無作為10.3%、差+6.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.0%（無作為30.9%、差+29.1）／P2 平均6.0頭 的中83.3%（無作為61.8%、差+21.5）／P3 平均10.1頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 12 | 72,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 9 | 36,590 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 30 | 126,590 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 10,410 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

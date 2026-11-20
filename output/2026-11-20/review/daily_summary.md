# 地方版 2026-11-20 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 15／PAPER PFS 82.2%／正式推薦 PFS 61.0%
- 第一失敗：{'CAPITAL_EFFICIENCY': 7, 'NONE': 3, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 8 | 120.6 | 41.4 | {'CAPITAL_EFFICIENCY': 4, 'NONE': 1, 'PREDICTION_ROLE_W': 3} |
| SON | 7 | 45.5 | 83.5 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 1, 'NONE': 2} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 20／正式試行 20・発走前送信 20／本人確認 0
2. 計算完走：Full29 20／Signed FINAL 20／KRS5000 20／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 82.2%／正式推薦 61.0%／実購入なし
5. Learning：RESULT署名検証 15／学習状態保存 15／前Raceの学習状態を結合した正式Race 20（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '30R到達', 'C6-CHECK10-REVISION': '30R到達', 'C7-KAMETANI-BUY-MATCH': '16/30R', 'C8-ODDS-GAP-FAVORITE': '30R到達', 'C9-BENTER-COMBINATION': '30R到達', 'C10-HARVILLE-DISCOUNT': '30R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '30R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '30R到達', 'C14-FORMAL-P2BOX20-ONLY': '30R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '30R到達', 'C22-KEEP-MEC-TRIO20': '14/30R', 'C23-THIRD3-BY-PAIR': '14/30R', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '14/30R', 'C16-W-INDEX-CONSENSUS': '30R到達', 'C17-P2-ZAI-PLACE': '30R到達', 'C18-W-PLUS-FAVORITE': '30R到達', 'C19-W-PLUS-TOP2-POP': '30R到達', 'C20-P2-PLUS-TOP3-POP': '30R到達', 'C21-BVI-L-R2-TERTILE': '60/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 15 | 53.3% | 66.7% | 53.3% | 20.0% | 26.7% | 26.7% | 40.0% | 1.67 |
| 正式推薦 | 15 | 46.7% | 73.3% | 73.3% | 93.3% | 100.0% | 73.3% | 40.0% | 1.53 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中53.3%（無作為11.1%、差+42.2）／P2 平均1.0頭 的中20.0%（無作為11.1%、差+8.9）／P3 平均1.0頭 的中26.7%（無作為11.1%、差+15.6）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中73.3%（無作為33.3%、差+40.1）／P2 平均6.0頭 的中93.3%（無作為66.5%、差+26.8）／P3 平均9.4頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 7 | 29,840 | RECURRING |
| P1:ROLE_W_MISS | P1 | 4 | 24,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 15 | 59,840 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 10,410 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-20 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 18／PAPER PFS 73.7%／正式推薦 PFS 60.9%
- 第一失敗：{'CAPITAL_EFFICIENCY': 7, 'NONE': 4, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 9 | 109.0 | 36.8 | {'CAPITAL_EFFICIENCY': 4, 'NONE': 1, 'PREDICTION_ROLE_W': 4} |
| OHI | 1 | 0.0 | 0.0 | {'PREDICTION_ROLE_P2': 1} |
| SON | 8 | 46.4 | 95.7 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 1, 'NONE': 3} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 23／正式試行 23・発走前送信 23／本人確認 0
2. 計算完走：Full29 23／Signed FINAL 23／KRS5000 23／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 73.7%／正式推薦 60.9%／実購入なし
5. Learning：RESULT署名検証 18／学習状態保存 18／前Raceの学習状態を結合した正式Race 23（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '30R到達', 'C6-CHECK10-REVISION': '30R到達', 'C7-KAMETANI-BUY-MATCH': '17/30R', 'C8-ODDS-GAP-FAVORITE': '30R到達', 'C9-BENTER-COMBINATION': '30R到達', 'C10-HARVILLE-DISCOUNT': '30R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '30R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '30R到達', 'C14-FORMAL-P2BOX20-ONLY': '30R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '30R到達', 'C22-KEEP-MEC-TRIO20': '17/30R', 'C23-THIRD3-BY-PAIR': '17/30R', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '17/30R', 'C16-W-INDEX-CONSENSUS': '30R到達', 'C17-P2-ZAI-PLACE': '30R到達', 'C18-W-PLUS-FAVORITE': '30R到達', 'C19-W-PLUS-TOP2-POP': '30R到達', 'C20-P2-PLUS-TOP3-POP': '30R到達', 'C21-BVI-L-R2-TERTILE': '60/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 18 | 50.0% | 72.2% | 50.0% | 16.7% | 27.8% | 22.2% | 33.3% | 1.61 |
| 正式推薦 | 18 | 44.4% | 72.2% | 72.2% | 83.3% | 100.0% | 72.2% | 38.9% | 1.44 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中50.0%（無作為11.1%、差+38.9）／P2 平均1.0頭 的中16.7%（無作為11.1%、差+5.6）／P3 平均1.0頭 的中27.8%（無作為11.1%、差+16.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中72.2%（無作為33.2%、差+39.0）／P2 平均6.0頭 的中83.3%（無作為66.4%、差+17.0）／P3 平均9.39頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 7 | 29,840 | RECURRING |
| P1:ROLE_W_MISS | P1 | 5 | 30,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 18 | 71,840 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 10,410 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

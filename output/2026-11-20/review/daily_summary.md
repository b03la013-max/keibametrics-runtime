# 地方版 2026-11-20 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 28／PAPER PFS 52.6%／正式推薦 PFS 66.0%
- 第一失敗：{'CAPITAL_EFFICIENCY': 9, 'NONE': 6, 'PREDICTION_ROLE_W': 10, 'PREDICTION_ROLE_P2': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 12 | 85.3 | 32.4 | {'CAPITAL_EFFICIENCY': 5, 'NONE': 1, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 1} |
| OHI | 4 | 24.1 | 173.7 | {'PREDICTION_ROLE_P2': 1, 'NONE': 2, 'CAPITAL_EFFICIENCY': 1} |
| SON | 12 | 33.3 | 63.8 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 5, 'NONE': 3} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 30／正式試行 30・発走前送信 30／本人確認 0
2. 計算完走：Full29 30／Signed FINAL 30／KRS5000 30／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 52.6%／正式推薦 66.0%／実購入なし
5. Learning：RESULT署名検証 28／学習状態保存 28／前Raceの学習状態を結合した正式Race 30（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '30R到達', 'C6-CHECK10-REVISION': '30R到達', 'C7-KAMETANI-BUY-MATCH': '22/30R', 'C8-ODDS-GAP-FAVORITE': '30R到達', 'C9-BENTER-COMBINATION': '30R到達', 'C10-HARVILLE-DISCOUNT': '30R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '30R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '30R到達', 'C14-FORMAL-P2BOX20-ONLY': '30R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '30R到達', 'C22-KEEP-MEC-TRIO20': '27/30R', 'C23-THIRD3-BY-PAIR': '27/30R', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '27/30R', 'C16-W-INDEX-CONSENSUS': '30R到達', 'C17-P2-ZAI-PLACE': '30R到達', 'C18-W-PLUS-FAVORITE': '30R到達', 'C19-W-PLUS-TOP2-POP': '30R到達', 'C20-P2-PLUS-TOP3-POP': '30R到達', 'C21-BVI-L-R2-TERTILE': '60/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 28 | 50.0% | 71.4% | 50.0% | 21.4% | 17.9% | 21.4% | 25.0% | 1.5 |
| 正式推薦 | 28 | 39.3% | 64.3% | 64.3% | 82.1% | 100.0% | 64.3% | 35.7% | 1.39 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中50.0%（無作為10.5%、差+39.5）／P2 平均1.0頭 的中21.4%（無作為10.5%、差+10.9）／P3 平均1.0頭 的中17.9%（無作為10.5%、差+7.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中64.3%（無作為31.6%、差+32.7）／P2 平均6.0頭 的中82.1%（無作為63.2%、差+18.9）／P3 平均9.82頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 10 | 60,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 9 | 36,590 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 28 | 114,590 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 10,410 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

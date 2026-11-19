# 地方版 2026-11-19 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 18／PAPER PFS 13.0%／正式推薦 PFS 586.4%
- 第一失敗：{'PREDICTION_ROLE_P2': 5, 'NONE': 4, 'PREDICTION_ROLE_W': 6, 'CAPITAL_EFFICIENCY': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 9 | 18.0 | 1165.5 | {'PREDICTION_ROLE_P2': 3, 'NONE': 4, 'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 1} |
| OHI | 1 | 0.0 | 59.7 | {'CAPITAL_EFFICIENCY': 1} |
| SON | 8 | 9.3 | 0.7 | {'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 23／正式試行 23・発走前送信 23／本人確認 0
2. 計算完走：Full29 23／Signed FINAL 23／KRS5000 23／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 13.0%／正式推薦 586.4%／実購入なし
5. Learning：RESULT署名検証 18／学習状態保存 18／前Raceの学習状態を結合した正式Race 23（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '30R到達', 'C5-SMALL-POINTS': '30R到達', 'C6-CHECK10-REVISION': '30R到達', 'C7-KAMETANI-BUY-MATCH': '0/30R', 'C8-ODDS-GAP-FAVORITE': '30R到達', 'C9-BENTER-COMBINATION': '30R到達', 'C10-HARVILLE-DISCOUNT': '30R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '30R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '16/30R', 'C14-FORMAL-P2BOX20-ONLY': '16/30R', 'C15-FORMAL-MIX-WAXIS-TRIO': '16/30R', 'C16-W-INDEX-CONSENSUS': '17/30R', 'C17-P2-ZAI-PLACE': '17/30R', 'C18-W-PLUS-FAVORITE': '17/30R', 'C19-W-PLUS-TOP2-POP': '17/30R', 'C20-P2-PLUS-TOP3-POP': '17/30R', 'C21-BVI-L-R2-TERTILE': '31/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 18 | 22.2% | 50.0% | 22.2% | 16.7% | 0.0% | 16.7% | 16.7% | 1.33 |
| 正式推薦 | 18 | 33.3% | 66.7% | 66.7% | 61.1% | 100.0% | 66.7% | 33.3% | 1.33 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中22.2%（無作為9.8%、差+12.4）／P2 平均1.0頭 的中16.7%（無作為9.8%、差+6.8）／P3 平均1.0頭 的中0.0%（無作為9.8%、差-9.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.7%（無作為29.5%、差+37.1）／P2 平均6.0頭 的中61.1%（無作為59.0%、差+2.1）／P3 平均10.33頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 6 | 36,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 3 | 13,460 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 18 | 79,460 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

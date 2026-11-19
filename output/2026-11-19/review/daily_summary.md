# 地方版 2026-11-19 日次総括（自動・推薦試算・実購入なし）

- 反省済みRace 36／PAPER PFS 33.0%／正式推薦 PFS 319.1%
- 第一失敗：{'PREDICTION_ROLE_P2': 8, 'NONE': 6, 'PREDICTION_ROLE_W': 13, 'CAPITAL_EFFICIENCY': 9}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 12 | 13.7 | 912.6 | {'PREDICTION_ROLE_P2': 3, 'NONE': 5, 'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 1} |
| OHI | 12 | 65.9 | 33.6 | {'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'NONE': 1, 'PREDICTION_ROLE_P2': 2} |
| SON | 12 | 16.7 | 11.2 | {'PREDICTION_ROLE_W': 6, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 3} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 36／正式試行 36・発走前送信 36／本人確認 0
2. 計算完走：Full29 36／Signed FINAL 36／KRS5000 36／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 33.0%／正式推薦 319.1%／実購入なし
5. Learning：RESULT署名検証 36／学習状態保存 36／前Raceの学習状態を結合した正式Race 36（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '30R到達', 'C6-CHECK10-REVISION': '30R到達', 'C7-KAMETANI-BUY-MATCH': '11/30R', 'C8-ODDS-GAP-FAVORITE': '30R到達', 'C9-BENTER-COMBINATION': '30R到達', 'C10-HARVILLE-DISCOUNT': '30R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '30R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '24/30R', 'C14-FORMAL-P2BOX20-ONLY': '24/30R', 'C15-FORMAL-MIX-WAXIS-TRIO': '24/30R', 'C16-W-INDEX-CONSENSUS': '30R到達', 'C17-P2-ZAI-PLACE': '30R到達', 'C18-W-PLUS-FAVORITE': '30R到達', 'C19-W-PLUS-TOP2-POP': '30R到達', 'C20-P2-PLUS-TOP3-POP': '30R到達', 'C21-BVI-L-R2-TERTILE': '31/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 36 | 36.1% | 63.9% | 36.1% | 13.9% | 2.8% | 19.4% | 22.2% | 1.5 |
| 正式推薦 | 36 | 33.3% | 63.9% | 63.9% | 66.7% | 100.0% | 63.9% | 30.6% | 1.5 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中36.1%（無作為9.4%、差+26.7）／P2 平均1.0頭 的中13.9%（無作為9.4%、差+4.5）／P3 平均1.0頭 的中2.8%（無作為9.4%、差-6.6）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.9%（無作為28.1%、差+35.8）／P2 平均6.0頭 的中66.7%（無作為56.3%、差+10.4）／P3 平均10.92頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 13 | 78,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 9 | 28,500 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 8 | 48,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 36 | 154,500 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

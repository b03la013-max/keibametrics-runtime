# 地方版 2026-11-19 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 29／PAPER PFS 30.6%／正式推薦 PFS 392.8%
- 第一失敗：{'PREDICTION_ROLE_P2': 6, 'NONE': 6, 'PREDICTION_ROLE_W': 10, 'CAPITAL_EFFICIENCY': 7}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 12 | 13.7 | 912.6 | {'PREDICTION_ROLE_P2': 3, 'NONE': 5, 'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 1} |
| OHI | 5 | 96.2 | 61.2 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 1, 'NONE': 1} |
| SON | 12 | 16.7 | 11.2 | {'PREDICTION_ROLE_W': 6, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 3} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 31／正式試行 31・発走前送信 31／本人確認 0
2. 計算完走：Full29 31／Signed FINAL 31／KRS5000 31／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 30.6%／正式推薦 392.8%／実購入なし
5. Learning：RESULT署名検証 29／学習状態保存 29／前Raceの学習状態を結合した正式Race 31（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '30R到達', 'C6-CHECK10-REVISION': '30R到達', 'C7-KAMETANI-BUY-MATCH': '0/30R', 'C8-ODDS-GAP-FAVORITE': '30R到達', 'C9-BENTER-COMBINATION': '30R到達', 'C10-HARVILLE-DISCOUNT': '30R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '30R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '21/30R', 'C14-FORMAL-P2BOX20-ONLY': '21/30R', 'C15-FORMAL-MIX-WAXIS-TRIO': '21/30R', 'C16-W-INDEX-CONSENSUS': '28/30R', 'C17-P2-ZAI-PLACE': '28/30R', 'C18-W-PLUS-FAVORITE': '28/30R', 'C19-W-PLUS-TOP2-POP': '28/30R', 'C20-P2-PLUS-TOP3-POP': '28/30R', 'C21-BVI-L-R2-TERTILE': '31/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 29 | 34.5% | 62.1% | 34.5% | 17.2% | 3.4% | 20.7% | 20.7% | 1.52 |
| 正式推薦 | 29 | 31.0% | 65.5% | 65.5% | 69.0% | 100.0% | 65.5% | 34.5% | 1.55 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中34.5%（無作為9.7%、差+24.8）／P2 平均1.0頭 的中17.2%（無作為9.7%、差+7.6）／P3 平均1.0頭 的中3.4%（無作為9.7%、差-6.2）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中65.5%（無作為29.0%、差+36.5）／P2 平均6.0頭 的中69.0%（無作為58.1%、差+10.9）／P3 平均10.52頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 10 | 60,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 7 | 22,310 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 6 | 36,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 29 | 118,310 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

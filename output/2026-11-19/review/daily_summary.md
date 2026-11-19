# 地方版 2026-11-19 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 15／PAPER PFS 12.0%／正式推薦 PFS 698.9%
- 第一失敗：{'PREDICTION_ROLE_P2': 5, 'NONE': 4, 'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 8 | 15.7 | 1309.9 | {'PREDICTION_ROLE_P2': 3, 'NONE': 4, 'PREDICTION_ROLE_W': 1} |
| SON | 7 | 8.0 | 0.8 | {'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 21／正式試行 21・発走前送信 21／本人確認 0
2. 計算完走：Full29 21／Signed FINAL 21／KRS5000 21／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 12.0%／正式推薦 698.9%／実購入なし
5. Learning：RESULT署名検証 15／学習状態保存 15／前Raceの学習状態を結合した正式Race 21（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '30R到達', 'C5-SMALL-POINTS': '30R到達', 'C6-CHECK10-REVISION': '30R到達', 'C7-KAMETANI-BUY-MATCH': '0/30R', 'C8-ODDS-GAP-FAVORITE': '30R到達', 'C9-BENTER-COMBINATION': '30R到達', 'C10-HARVILLE-DISCOUNT': '30R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '30R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '13/30R', 'C14-FORMAL-P2BOX20-ONLY': '13/30R', 'C15-FORMAL-MIX-WAXIS-TRIO': '13/30R', 'C16-W-INDEX-CONSENSUS': '14/30R', 'C17-P2-ZAI-PLACE': '14/30R', 'C18-W-PLUS-FAVORITE': '14/30R', 'C19-W-PLUS-TOP2-POP': '14/30R', 'C20-P2-PLUS-TOP3-POP': '14/30R', 'C21-BVI-L-R2-TERTILE': '31/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 15 | 26.7% | 46.7% | 26.7% | 13.3% | 0.0% | 20.0% | 13.3% | 1.27 |
| 正式推薦 | 15 | 33.3% | 66.7% | 66.7% | 53.3% | 100.0% | 66.7% | 26.7% | 1.2 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中26.7%（無作為9.8%、差+16.9）／P2 平均1.0頭 的中13.3%（無作為9.8%、差+3.5）／P3 平均1.0頭 的中0.0%（無作為9.8%、差-9.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.7%（無作為29.4%、差+37.3）／P2 平均6.0頭 的中53.3%（無作為58.8%、差-5.4）／P3 平均10.33頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 5 | 30,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 1 | 5,680 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 15 | 65,680 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-19 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 16／PAPER PFS 12.4%／正式推薦 PFS 655.3%
- 第一失敗：{'PREDICTION_ROLE_P2': 5, 'NONE': 4, 'PREDICTION_ROLE_W': 6, 'CAPITAL_EFFICIENCY': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 8 | 15.7 | 1309.9 | {'PREDICTION_ROLE_P2': 3, 'NONE': 4, 'PREDICTION_ROLE_W': 1} |
| SON | 8 | 9.3 | 0.7 | {'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 21／正式試行 21・発走前送信 21／本人確認 0
2. 計算完走：Full29 21／Signed FINAL 21／KRS5000 21／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 12.4%／正式推薦 655.3%／実購入なし
5. Learning：RESULT署名検証 16／学習状態保存 16／前Raceの学習状態を結合した正式Race 21（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '30R到達', 'C5-SMALL-POINTS': '30R到達', 'C6-CHECK10-REVISION': '30R到達', 'C7-KAMETANI-BUY-MATCH': '0/30R', 'C8-ODDS-GAP-FAVORITE': '30R到達', 'C9-BENTER-COMBINATION': '30R到達', 'C10-HARVILLE-DISCOUNT': '30R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '30R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '14/30R', 'C14-FORMAL-P2BOX20-ONLY': '14/30R', 'C15-FORMAL-MIX-WAXIS-TRIO': '14/30R', 'C16-W-INDEX-CONSENSUS': '15/30R', 'C17-P2-ZAI-PLACE': '15/30R', 'C18-W-PLUS-FAVORITE': '15/30R', 'C19-W-PLUS-TOP2-POP': '15/30R', 'C20-P2-PLUS-TOP3-POP': '15/30R', 'C21-BVI-L-R2-TERTILE': '31/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 16 | 25.0% | 50.0% | 25.0% | 12.5% | 0.0% | 18.8% | 12.5% | 1.31 |
| 正式推薦 | 16 | 31.2% | 62.5% | 62.5% | 56.2% | 100.0% | 62.5% | 25.0% | 1.25 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中25.0%（無作為10.0%、差+15.0）／P2 平均1.0頭 的中12.5%（無作為10.0%、差+2.5）／P3 平均1.0頭 的中0.0%（無作為10.0%、差-10.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中62.5%（無作為29.9%、差+32.6）／P2 平均6.0頭 的中56.2%（無作為59.8%、差-3.5）／P3 平均10.19頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 6 | 36,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 1 | 5,680 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 16 | 71,680 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

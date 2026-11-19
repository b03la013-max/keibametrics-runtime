# 地方版 2026-11-19 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 22／PAPER PFS 34.3%／正式推薦 PFS 507.1%
- 第一失敗：{'PREDICTION_ROLE_P2': 5, 'NONE': 5, 'PREDICTION_ROLE_W': 7, 'CAPITAL_EFFICIENCY': 5}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 10 | 16.4 | 1095.1 | {'PREDICTION_ROLE_P2': 3, 'NONE': 5, 'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 1} |
| OHI | 2 | 158.4 | 55.3 | {'CAPITAL_EFFICIENCY': 2} |
| SON | 10 | 16.0 | 9.4 | {'PREDICTION_ROLE_W': 6, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 27／正式試行 27・発走前送信 27／本人確認 0
2. 計算完走：Full29 27／Signed FINAL 27／KRS5000 27／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 34.3%／正式推薦 507.1%／実購入なし
5. Learning：RESULT署名検証 22／学習状態保存 22／前Raceの学習状態を結合した正式Race 27（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '30R到達', 'C5-SMALL-POINTS': '30R到達', 'C6-CHECK10-REVISION': '30R到達', 'C7-KAMETANI-BUY-MATCH': '0/30R', 'C8-ODDS-GAP-FAVORITE': '30R到達', 'C9-BENTER-COMBINATION': '30R到達', 'C10-HARVILLE-DISCOUNT': '30R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '30R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '19/30R', 'C14-FORMAL-P2BOX20-ONLY': '19/30R', 'C15-FORMAL-MIX-WAXIS-TRIO': '19/30R', 'C16-W-INDEX-CONSENSUS': '21/30R', 'C17-P2-ZAI-PLACE': '21/30R', 'C18-W-PLUS-FAVORITE': '21/30R', 'C19-W-PLUS-TOP2-POP': '21/30R', 'C20-P2-PLUS-TOP3-POP': '21/30R', 'C21-BVI-L-R2-TERTILE': '31/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 22 | 31.8% | 54.5% | 31.8% | 22.7% | 4.5% | 22.7% | 22.7% | 1.45 |
| 正式推薦 | 22 | 31.8% | 68.2% | 68.2% | 68.2% | 100.0% | 68.2% | 40.9% | 1.55 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中31.8%（無作為9.9%、差+21.9）／P2 平均1.0頭 的中22.7%（無作為9.9%、差+12.8）／P3 平均1.0頭 的中4.5%（無作為9.9%、差-5.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中68.2%（無作為29.8%、差+38.3）／P2 平均6.0頭 的中68.2%（無作為59.7%、差+8.5）／P3 平均10.23頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 7 | 42,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 5 | 17,060 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 22 | 89,060 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

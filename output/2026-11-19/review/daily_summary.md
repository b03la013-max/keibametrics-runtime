# 地方版 2026-11-19 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 21／PAPER PFS 33.4%／正式推薦 PFS 531.3%
- 第一失敗：{'PREDICTION_ROLE_P2': 5, 'NONE': 5, 'PREDICTION_ROLE_W': 6, 'CAPITAL_EFFICIENCY': 5}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 10 | 16.4 | 1095.1 | {'PREDICTION_ROLE_P2': 3, 'NONE': 5, 'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 1} |
| OHI | 2 | 158.4 | 55.3 | {'CAPITAL_EFFICIENCY': 2} |
| SON | 9 | 12.6 | 10.5 | {'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 26／正式試行 26・発走前送信 26／本人確認 0
2. 計算完走：Full29 26／Signed FINAL 26／KRS5000 26／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 33.4%／正式推薦 531.3%／実購入なし
5. Learning：RESULT署名検証 21／学習状態保存 21／前Raceの学習状態を結合した正式Race 26（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '30R到達', 'C5-SMALL-POINTS': '30R到達', 'C6-CHECK10-REVISION': '30R到達', 'C7-KAMETANI-BUY-MATCH': '0/30R', 'C8-ODDS-GAP-FAVORITE': '30R到達', 'C9-BENTER-COMBINATION': '30R到達', 'C10-HARVILLE-DISCOUNT': '30R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '30R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '18/30R', 'C14-FORMAL-P2BOX20-ONLY': '18/30R', 'C15-FORMAL-MIX-WAXIS-TRIO': '18/30R', 'C16-W-INDEX-CONSENSUS': '20/30R', 'C17-P2-ZAI-PLACE': '20/30R', 'C18-W-PLUS-FAVORITE': '20/30R', 'C19-W-PLUS-TOP2-POP': '20/30R', 'C20-P2-PLUS-TOP3-POP': '20/30R', 'C21-BVI-L-R2-TERTILE': '31/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 21 | 28.6% | 52.4% | 28.6% | 19.0% | 0.0% | 23.8% | 19.0% | 1.38 |
| 正式推薦 | 21 | 33.3% | 71.4% | 71.4% | 66.7% | 100.0% | 71.4% | 42.9% | 1.52 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中28.6%（無作為9.9%、差+18.7）／P2 平均1.0頭 的中19.0%（無作為9.9%、差+9.2）／P3 平均1.0頭 的中0.0%（無作為9.9%、差-9.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中71.4%（無作為29.7%、差+41.8）／P2 平均6.0頭 的中66.7%（無作為59.3%、差+7.3）／P3 平均10.29頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 6 | 36,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 5 | 17,060 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 21 | 83,060 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

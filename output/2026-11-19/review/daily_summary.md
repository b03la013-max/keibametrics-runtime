# 地方版 2026-11-19 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 14／PAPER PFS 12.9%／正式推薦 PFS 748.9%
- 第一失敗：{'PREDICTION_ROLE_P2': 5, 'NONE': 4, 'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 7 | 18.1 | 1497.0 | {'PREDICTION_ROLE_P2': 3, 'NONE': 4} |
| SON | 7 | 8.0 | 0.8 | {'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 19／正式試行 19・発走前送信 19／本人確認 0
2. 計算完走：Full29 19／Signed FINAL 19／KRS5000 19／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 12.9%／正式推薦 748.9%／実購入なし
5. Learning：RESULT署名検証 14／学習状態保存 14／前Raceの学習状態を結合した正式Race 19（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '30R到達', 'C5-SMALL-POINTS': '30R到達', 'C6-CHECK10-REVISION': '29/30R', 'C7-KAMETANI-BUY-MATCH': '0/30R', 'C8-ODDS-GAP-FAVORITE': '30R到達', 'C9-BENTER-COMBINATION': '30R到達', 'C10-HARVILLE-DISCOUNT': '30R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '30R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '13/30R', 'C14-FORMAL-P2BOX20-ONLY': '13/30R', 'C15-FORMAL-MIX-WAXIS-TRIO': '13/30R', 'C16-W-INDEX-CONSENSUS': '13/30R', 'C17-P2-ZAI-PLACE': '13/30R', 'C18-W-PLUS-FAVORITE': '13/30R', 'C19-W-PLUS-TOP2-POP': '13/30R', 'C20-P2-PLUS-TOP3-POP': '13/30R', 'C21-BVI-L-R2-TERTILE': '31/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 14 | 28.6% | 50.0% | 28.6% | 14.3% | 0.0% | 21.4% | 14.3% | 1.29 |
| 正式推薦 | 14 | 35.7% | 71.4% | 71.4% | 50.0% | 100.0% | 71.4% | 28.6% | 1.21 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中28.6%（無作為9.9%、差+18.7）／P2 平均1.0頭 的中14.3%（無作為9.9%、差+4.4）／P3 平均1.0頭 的中0.0%（無作為9.9%、差-9.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中71.4%（無作為29.7%、差+41.7）／P2 平均6.0頭 的中50.0%（無作為59.4%、差-9.4）／P3 平均10.21頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 4 | 24,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 1 | 5,680 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 14 | 59,680 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-22 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 12／PAPER PFS 117.2%／正式推薦 PFS 60.5%
- 第一失敗：{'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_P2': 3, 'NONE': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KOC | 2 | 111.2 | 46.6 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 1} |
| MIZ | 8 | 136.2 | 57.3 | {'PREDICTION_ROLE_P2': 3, 'NONE': 3, 'CAPITAL_EFFICIENCY': 2} |
| SAG | 2 | 40.0 | 87.2 | {'PREDICTION_ROLE_W': 1, 'NONE': 1} |

## 日次自律監査

1. 配送：管理 34R／PAPER発走前送信 17／正式試行 17・発走前送信 17／本人確認 0
2. 計算完走：Full29 17／Signed FINAL 17／KRS5000 17／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 117.2%／正式推薦 60.5%／実購入なし
5. Learning：RESULT署名検証 12／学習状態保存 12／前Raceの学習状態を結合した正式Race 17（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '30R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '11/30R', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '30R到達', 'C23-THIRD3-BY-PAIR': '30R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '30R到達', 'C16-W-INDEX-CONSENSUS': '30R到達', 'C17-P2-ZAI-PLACE': '30R到達', 'C18-W-PLUS-FAVORITE': '30R到達', 'C19-W-PLUS-TOP2-POP': '30R到達', 'C20-P2-PLUS-TOP3-POP': '30R到達', 'C21-BVI-L-R2-TERTILE': '139/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 12 | 41.7% | 66.7% | 41.7% | 25.0% | 25.0% | 16.7% | 41.7% | 1.67 |
| 正式推薦 | 12 | 33.3% | 83.3% | 83.3% | 66.7% | 100.0% | 83.3% | 66.7% | 1.75 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中41.7%（無作為9.8%、差+31.9）／P2 平均1.0頭 的中25.0%（無作為9.8%、差+15.2）／P3 平均1.0頭 的中25.0%（無作為9.8%、差+15.2）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中83.3%（無作為29.3%、差+54.0）／P2 平均6.0頭 的中66.7%（無作為58.7%、差+8.0）／P3 平均10.33頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.83/40（選択性補正込み）・能力順位 14.57/20（12R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 17.47/40（選択性補正込み）・能力順位 14.77/20（12R平均）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 4 | 12,330 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 2 | 11,400 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 12 | 36,330 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

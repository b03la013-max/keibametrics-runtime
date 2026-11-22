# 地方版 2026-11-22 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 29／PAPER PFS 101.6%／正式推薦 PFS 52.5%
- 第一失敗：{'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 8, 'NONE': 6}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KOC | 8 | 94.0 | 36.6 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_P2': 1} |
| MIZ | 12 | 100.6 | 50.2 | {'PREDICTION_ROLE_P2': 5, 'NONE': 4, 'CAPITAL_EFFICIENCY': 3} |
| SAG | 9 | 109.8 | 69.8 | {'PREDICTION_ROLE_W': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_P2': 2} |

## 日次自律監査

1. 配送：管理 34R／PAPER発走前送信 33／正式試行 33・発走前送信 33／本人確認 0
2. 計算完走：Full29 33／Signed FINAL 33／KRS5000 33／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 101.6%／正式推薦 52.5%／実購入なし
5. Learning：RESULT署名検証 29／学習状態保存 29／前Raceの学習状態を結合した正式Race 33（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '30R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '28/30R', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '30R到達', 'C23-THIRD3-BY-PAIR': '30R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '30R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '139/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 29 | 34.5% | 69.0% | 34.5% | 17.2% | 24.1% | 10.3% | 27.6% | 1.66 |
| 正式推薦 | 29 | 37.9% | 82.8% | 82.8% | 69.0% | 100.0% | 82.8% | 48.3% | 1.66 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中34.5%（無作為9.6%、差+24.9）／P2 平均1.0頭 的中17.2%（無作為9.6%、差+7.7）／P3 平均1.0頭 的中24.1%（無作為9.6%、差+14.6）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中82.8%（無作為28.7%、差+54.0）／P2 平均6.0頭 的中69.0%（無作為57.4%、差+11.5）／P3 平均10.62頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.76/40（選択性補正込み）・能力順位 14.12/20（29R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 17.15/40（選択性補正込み）・能力順位 14.33/20（29R平均）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 11 | 34,720 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 8 | 48,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 5 | 29,400 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 29 | 106,720 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

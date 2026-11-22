# 地方版 2026-11-22 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 25／PAPER PFS 96.0%／正式推薦 PFS 57.1%
- 第一失敗：{'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_P2': 6, 'NONE': 6}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KOC | 6 | 47.0 | 42.7 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 3} |
| MIZ | 12 | 100.6 | 50.2 | {'PREDICTION_ROLE_P2': 5, 'NONE': 4, 'CAPITAL_EFFICIENCY': 3} |
| SAG | 7 | 130.2 | 81.5 | {'PREDICTION_ROLE_W': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_P2': 1} |

## 日次自律監査

1. 配送：管理 34R／PAPER発走前送信 29／正式試行 29・発走前送信 29／本人確認 0
2. 計算完走：Full29 29／Signed FINAL 29／KRS5000 29／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 96.0%／正式推薦 57.1%／実購入なし
5. Learning：RESULT署名検証 25／学習状態保存 25／前Raceの学習状態を結合した正式Race 29（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '30R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '24/30R', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '30R到達', 'C23-THIRD3-BY-PAIR': '30R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '30R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '139/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 25 | 28.0% | 64.0% | 28.0% | 20.0% | 24.0% | 12.0% | 24.0% | 1.56 |
| 正式推薦 | 25 | 36.0% | 80.0% | 80.0% | 72.0% | 100.0% | 80.0% | 48.0% | 1.68 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中28.0%（無作為9.6%、差+18.4）／P2 平均1.0頭 的中20.0%（無作為9.6%、差+10.4）／P3 平均1.0頭 的中24.0%（無作為9.6%、差+14.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中80.0%（無作為28.9%、差+51.1）／P2 平均6.0頭 的中72.0%（無作為57.8%、差+14.2）／P3 平均10.56頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.72/40（選択性補正込み）・能力順位 13.9/20（25R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.97/40（選択性補正込み）・能力順位 14.32/20（25R平均）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 9 | 28,390 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 6 | 36,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 5 | 29,400 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 25 | 88,390 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

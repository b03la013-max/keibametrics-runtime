# 地方版 2026-11-22 日次総括（自動・推薦試算・実購入なし）

- 反省済みRace 34／PAPER PFS 98.0%／正式推薦 PFS 45.9%
- 第一失敗：{'PREDICTION_ROLE_W': 7, 'CAPITAL_EFFICIENCY': 11, 'PREDICTION_ROLE_P2': 10, 'NONE': 6}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KOC | 11 | 102.7 | 30.0 | {'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 1} |
| MIZ | 12 | 100.6 | 50.2 | {'PREDICTION_ROLE_P2': 5, 'NONE': 4, 'CAPITAL_EFFICIENCY': 3} |
| SAG | 11 | 90.1 | 57.1 | {'PREDICTION_ROLE_W': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_P2': 4} |

## 日次自律監査

1. 配送：管理 34R／PAPER発走前送信 34／正式試行 34・発走前送信 34／本人確認 0
2. 計算完走：Full29 34／Signed FINAL 34／KRS5000 34／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 98.0%／正式推薦 45.9%／実購入なし
5. Learning：RESULT署名検証 34／学習状態保存 34／前Raceの学習状態を結合した正式Race 34（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '30R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '30R到達', 'C23-THIRD3-BY-PAIR': '30R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '30R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '139/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 34 | 29.4% | 70.6% | 29.4% | 14.7% | 20.6% | 8.8% | 23.5% | 1.65 |
| 正式推薦 | 34 | 32.4% | 79.4% | 79.4% | 67.6% | 100.0% | 79.4% | 47.1% | 1.59 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中29.4%（無作為9.7%、差+19.7）／P2 平均1.0頭 的中14.7%（無作為9.7%、差+5.0）／P3 平均1.0頭 的中20.6%（無作為9.7%、差+10.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中79.4%（無作為29.2%、差+50.2）／P2 平均6.0頭 的中67.6%（無作為58.4%、差+9.3）／P3 平均10.53頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.85/40（選択性補正込み）・能力順位 13.94/20（34R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.5/40（選択性補正込み）・能力順位 13.92/20（34R平均）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 13 | 44,450 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 10 | 60,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 7 | 40,600 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 34 | 134,450 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

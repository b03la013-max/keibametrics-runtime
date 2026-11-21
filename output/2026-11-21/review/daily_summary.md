# 地方版 2026-11-21 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 18／PAPER PFS 20.8%／正式推薦 PFS 29.4%
- 第一失敗：{'WINNER_DISCOVERED_LOW': 4, 'W_WIDTH_OR_ROLE': 3, 'PREDICTION_ROLE_P2': 3, 'NONE': 2, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KOC | 9 | 30.0 | 57.4 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 1, 'NONE': 2, 'CAPITAL_EFFICIENCY': 2} |
| SAG | 9 | 13.5 | 6.1 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 2, 'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 2} |

## 日次自律監査

1. 配送：管理 23R／PAPER発走前送信 16／正式試行 16・発走前送信 15／本人確認 0
2. 計算完走：Full29 15／Signed FINAL 15／KRS5000 15／NO-BET 0／HOLD {'SOURCE_FREEZE': 1}
3. 精度：下表
4. PFS：PAPER 20.8%／正式推薦 29.4%／実購入なし
5. Learning：RESULT署名検証 11／学習状態保存 11／前Raceの学習状態を結合した正式Race 15（Production変更なし）
6. 障害・改善：停止 {'KOC_01': 'DELIVERY_SUBMITTED', 'KOC_02': 'DELIVERY_SUBMITTED', 'KOC_03': 'DELIVERY_SUBMITTED', 'SAG_01': 'DELIVERY_SUBMITTED', 'SAG_02': 'DELIVERY_SUBMITTED', 'SAG_03': 'DELIVERY_SUBMITTED'}／正式停止 {'KOC_04': 'SOURCE_FREEZE'}／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '30R到達', 'C7-KAMETANI-BUY-MATCH': '28/30R', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '17/30R', 'C26-EXT-CONNECTION': '0/30R', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '30R到達', 'C23-THIRD3-BY-PAIR': '30R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '30R到達', 'C16-W-INDEX-CONSENSUS': '30R到達', 'C17-P2-ZAI-PLACE': '30R到達', 'C18-W-PLUS-FAVORITE': '30R到達', 'C19-W-PLUS-TOP2-POP': '30R到達', 'C20-P2-PLUS-TOP3-POP': '30R到達', 'C21-BVI-L-R2-TERTILE': '122/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 18 | 33.3% | 72.2% | 33.3% | 22.2% | 27.8% | 5.6% | 22.2% | 1.78 |
| 正式推薦 | 11 | 45.5% | 81.8% | 81.8% | 72.7% | 100.0% | 81.8% | 36.4% | 1.82 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.3%（無作為9.9%、差+23.4）／P2 平均1.0頭 的中22.2%（無作為9.9%、差+12.3）／P3 平均1.0頭 的中27.8%（無作為9.9%、差+17.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中81.8%（無作為28.6%、差+53.2）／P2 平均6.0頭 的中72.7%（無作為57.2%、差+15.5）／P3 平均10.55頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.61/40（選択性補正込み）・能力順位 14.88/20（18R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 17.28/40（選択性補正込み）・能力順位 14.65/20（11R平均）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 1 | 540 | SINGLE_OR_FEW (過大評価しない) |
| P1:ROLE_W_MISS | P1 | 9 | 16,830 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 6 | 22,330 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 18 | 56,030 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

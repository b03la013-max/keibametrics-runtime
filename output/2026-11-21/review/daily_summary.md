# 地方版 2026-11-21 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 10／PAPER PFS 12.5%／正式推薦 PFS 0.0%
- 第一失敗：{'WINNER_DISCOVERED_LOW': 4, 'W_WIDTH_OR_ROLE': 3, 'PREDICTION_ROLE_P2': 2, 'PREDICTION_ROLE_W': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KOC | 5 | 28.3 | 0.0 | {'WINNER_DISCOVERED_LOW': 3, 'W_WIDTH_OR_ROLE': 1, 'PREDICTION_ROLE_P2': 1} |
| SAG | 5 | 2.1 | 0.0 | {'W_WIDTH_OR_ROLE': 2, 'WINNER_DISCOVERED_LOW': 1, 'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 1} |

## 日次自律監査

1. 配送：管理 23R／PAPER発走前送信 8／正式試行 8・発走前送信 7／本人確認 0
2. 計算完走：Full29 7／Signed FINAL 7／KRS5000 7／NO-BET 0／HOLD {'SOURCE_FREEZE': 1}
3. 精度：下表
4. PFS：PAPER 12.5%／正式推薦 0.0%／実購入なし
5. Learning：RESULT署名検証 3／学習状態保存 3／前Raceの学習状態を結合した正式Race 7（Production変更なし）
6. 障害・改善：停止 {'KOC_01': 'DELIVERY_SUBMITTED', 'KOC_02': 'DELIVERY_SUBMITTED', 'KOC_03': 'DELIVERY_SUBMITTED', 'SAG_01': 'DELIVERY_SUBMITTED', 'SAG_02': 'DELIVERY_SUBMITTED', 'SAG_03': 'DELIVERY_SUBMITTED'}／正式停止 {'KOC_04': 'SOURCE_FREEZE'}／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '30R到達', 'C7-KAMETANI-BUY-MATCH': '27/30R', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '9/30R', 'C26-EXT-CONNECTION': '0/30R', 'C13-FORMAL-MIX-P2BOX20': '30R到達', 'C14-FORMAL-P2BOX20-ONLY': '30R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '30R到達', 'C22-KEEP-MEC-TRIO20': '30R到達', 'C23-THIRD3-BY-PAIR': '30R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '30R到達', 'C16-W-INDEX-CONSENSUS': '30R到達', 'C17-P2-ZAI-PLACE': '30R到達', 'C18-W-PLUS-FAVORITE': '30R到達', 'C19-W-PLUS-TOP2-POP': '30R到達', 'C20-P2-PLUS-TOP3-POP': '30R到達', 'C21-BVI-L-R2-TERTILE': '122/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 10 | 20.0% | 60.0% | 20.0% | 10.0% | 20.0% | 10.0% | 10.0% | 1.6 |
| 正式推薦 | 3 | 33.3% | 66.7% | 66.7% | 33.3% | 100.0% | 66.7% | 0.0% | 1.0 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中20.0%（無作為10.1%、差+9.9）／P2 平均1.0頭 的中10.0%（無作為10.1%、差-0.1）／P3 平均1.0頭 的中20.0%（無作為10.1%、差+9.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.7%（無作為27.4%、差+39.2）／P2 平均6.0頭 的中33.3%（無作為54.8%、差-21.5）／P3 平均11.0頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.2/40（選択性補正込み）・能力順位 14.09/20（10R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.9/40（選択性補正込み）・能力順位 12.3/20（3R平均）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P0:FORMAL_HOLD:SOURCE_FREEZE | P0 | 1 | 540 | SINGLE_OR_FEW (過大評価しない) |
| P1:ROLE_W_MISS | P1 | 8 | 10,830 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P1:HIT_BUT_LOSS | P1 | 2 | 1,130 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 10 | 22,830 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

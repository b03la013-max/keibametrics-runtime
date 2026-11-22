# 地方版 2026-11-22 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 7／PAPER PFS 125.3%／正式推薦 PFS 36.3%
- 第一失敗：{'PREDICTION_ROLE_P2': 3, 'NONE': 1, 'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 6 | 133.1 | 40.6 | {'PREDICTION_ROLE_P2': 3, 'NONE': 1, 'CAPITAL_EFFICIENCY': 2} |
| SAG | 1 | 75.0 | 10.0 | {'PREDICTION_ROLE_W': 1} |

## 日次自律監査

1. 配送：管理 34R／PAPER発走前送信 12／正式試行 12・発走前送信 12／本人確認 0
2. 計算完走：Full29 12／Signed FINAL 12／KRS5000 12／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 125.3%／正式推薦 36.3%／実購入なし
5. Learning：RESULT署名検証 7／学習状態保存 7／前Raceの学習状態を結合した正式Race 12（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '30R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '29/30R', 'C26-EXT-CONNECTION': '6/30R', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '30R到達', 'C23-THIRD3-BY-PAIR': '30R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '30R到達', 'C16-W-INDEX-CONSENSUS': '30R到達', 'C17-P2-ZAI-PLACE': '30R到達', 'C18-W-PLUS-FAVORITE': '30R到達', 'C19-W-PLUS-TOP2-POP': '30R到達', 'C20-P2-PLUS-TOP3-POP': '30R到達', 'C21-BVI-L-R2-TERTILE': '139/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 7 | 57.1% | 71.4% | 57.1% | 28.6% | 28.6% | 28.6% | 42.9% | 1.86 |
| 正式推薦 | 7 | 42.9% | 85.7% | 85.7% | 57.1% | 100.0% | 85.7% | 57.1% | 1.86 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中57.1%（無作為10.0%、差+47.1）／P2 平均1.0頭 的中28.6%（無作為10.0%、差+18.6）／P3 平均1.0頭 的中28.6%（無作為10.0%、差+18.6）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中85.7%（無作為30.0%、差+55.7）／P2 平均6.0頭 的中57.1%（無作為60.0%、差-2.8）／P3 平均10.14頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 19.14/40（選択性補正込み）・能力順位 14.85/20（7R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.55/40（選択性補正込み）・能力順位 14.62/20（7R平均）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 3 | 11,920 | RECURRING |
| P1:ROLE_W_MISS | P1 | 1 | 5,400 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 7 | 29,920 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

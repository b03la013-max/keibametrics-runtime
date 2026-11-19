# 地方版 2026-11-19 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 4／PAPER PFS 0.0%／正式推薦 PFS 0.0%
- 第一失敗：{'PREDICTION_ROLE_P2': 2, 'PREDICTION_ROLE_W': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 2 | 0.0 | 0.0 | {'PREDICTION_ROLE_P2': 2} |
| SON | 2 | 0.0 | 0.0 | {'PREDICTION_ROLE_W': 2} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 8／正式試行 8・発走前送信 8／本人確認 0
2. 計算完走：Full29 8／Signed FINAL 8／KRS5000 8／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 0.0%／正式推薦 0.0%／実購入なし
5. Learning：RESULT署名検証 4／学習状態保存 4／前Raceの学習状態を結合した正式Race 8（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '30R到達', 'C5-SMALL-POINTS': '30R到達', 'C6-CHECK10-REVISION': '22/30R', 'C7-KAMETANI-BUY-MATCH': '0/30R', 'C8-ODDS-GAP-FAVORITE': '30R到達', 'C9-BENTER-COMBINATION': '30R到達', 'C10-HARVILLE-DISCOUNT': '30R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '30R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '10/30R', 'C14-FORMAL-P2BOX20-ONLY': '10/30R', 'C15-FORMAL-MIX-WAXIS-TRIO': '10/30R', 'C16-W-INDEX-CONSENSUS': '3/30R', 'C17-P2-ZAI-PLACE': '3/30R', 'C18-W-PLUS-FAVORITE': '3/30R', 'C19-W-PLUS-TOP2-POP': '3/30R', 'C20-P2-PLUS-TOP3-POP': '3/30R', 'C21-BVI-L-R2-TERTILE': '23/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 4 | 25.0% | 50.0% | 25.0% | 50.0% | 0.0% | 0.0% | 0.0% | 1.25 |
| 正式推薦 | 4 | 25.0% | 50.0% | 50.0% | 25.0% | 100.0% | 50.0% | 0.0% | 1.0 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中25.0%（無作為9.6%、差+15.4）／P2 平均1.0頭 的中50.0%（無作為9.6%、差+40.4）／P3 平均1.0頭 的中0.0%（無作為9.6%、差-9.6）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中50.0%（無作為28.7%、差+21.3）／P2 平均6.0頭 的中25.0%（無作為57.5%、差-32.5）／P3 平均10.5頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P1:ROLE_W_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 4 | 24,000 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

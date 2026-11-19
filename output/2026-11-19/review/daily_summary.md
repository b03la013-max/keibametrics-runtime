# 地方版 2026-11-19 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 10／PAPER PFS 3.8%／正式推薦 PFS 999.6%
- 第一失敗：{'PREDICTION_ROLE_P2': 4, 'NONE': 2, 'PREDICTION_ROLE_W': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KSM | 5 | 0.0 | 1999.2 | {'PREDICTION_ROLE_P2': 3, 'NONE': 2} |
| SON | 5 | 7.5 | 0.0 | {'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 14／正式試行 14・発走前送信 14／本人確認 0
2. 計算完走：Full29 14／Signed FINAL 14／KRS5000 14／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 3.8%／正式推薦 999.6%／実購入なし
5. Learning：RESULT署名検証 10／学習状態保存 10／前Raceの学習状態を結合した正式Race 14（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '30R到達', 'C2-DANGER-FAV-RANK-A': '30R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '30R到達', 'C4-LOCAL-CAP-60': '30R到達', 'C5-SMALL-POINTS': '30R到達', 'C6-CHECK10-REVISION': '27/30R', 'C7-KAMETANI-BUY-MATCH': '0/30R', 'C8-ODDS-GAP-FAVORITE': '30R到達', 'C9-BENTER-COMBINATION': '30R到達', 'C10-HARVILLE-DISCOUNT': '30R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '30R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '11/30R', 'C14-FORMAL-P2BOX20-ONLY': '11/30R', 'C15-FORMAL-MIX-WAXIS-TRIO': '11/30R', 'C16-W-INDEX-CONSENSUS': '9/30R', 'C17-P2-ZAI-PLACE': '9/30R', 'C18-W-PLUS-FAVORITE': '9/30R', 'C19-W-PLUS-TOP2-POP': '9/30R', 'C20-P2-PLUS-TOP3-POP': '9/30R', 'C21-BVI-L-R2-TERTILE': '31/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 10 | 30.0% | 50.0% | 30.0% | 20.0% | 0.0% | 20.0% | 10.0% | 1.1 |
| 正式推薦 | 10 | 30.0% | 60.0% | 60.0% | 40.0% | 100.0% | 60.0% | 20.0% | 1.0 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中30.0%（無作為10.0%、差+20.0）／P2 平均1.0頭 的中20.0%（無作為10.0%、差+10.0）／P3 平均1.0頭 的中0.0%（無作為10.0%、差-10.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.0%（無作為30.1%、差+29.9）／P2 平均6.0頭 的中40.0%（無作為60.2%、差-20.2）／P3 平均10.1頭 的中100.0%（無作為100.0%、差+0.0）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | 4 | 24,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 4 | 24,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 10 | 48,000 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

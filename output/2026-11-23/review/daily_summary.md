# 地方版 2026-11-23 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 25／PAPER PFS 39.7%／正式推薦 PFS 12.2%
- 第一失敗：{'PREDICTION_ROLE_P2': 7, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 11}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 8 | 24.5 | 9.6 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 4} |
| MIZ | 12 | 69.0 | 11.2 | {'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 3} |
| SAG | 5 | 0.0 | 18.4 | {'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_P2': 1} |

## 日次自律監査

1. 配送：管理 33R／PAPER発走前送信 29／正式試行 29・発走前送信 29／本人確認 0
2. 計算完走：Full29 29／Signed FINAL 29／KRS5000 29／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 39.7%／正式推薦 12.2%／実購入なし
5. Learning：RESULT署名検証 25／学習状態保存 25／前Raceの学習状態を結合した正式Race 29（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '165/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 25 | 36.0% | 68.0% | 36.0% | 8.0% | 20.0% | 12.0% | 24.0% | 1.48 |
| 正式推薦 | 25 | 36.0% | 56.0% | 56.0% | 68.0% | 100.0% | 56.0% | 36.0% | 1.44 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中36.0%（無作為10.4%、差+25.6）／P2 平均1.0頭 的中8.0%（無作為10.4%、差-2.4）／P3 平均1.0頭 的中20.0%（無作為10.4%、差+9.6）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中56.0%（無作為31.2%、差+24.8）／P2 平均6.0頭 的中68.0%（無作為62.4%、差+5.6）／P3 平均9.76頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.28/40（選択性補正込み）・能力順位 13.45/20（25R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.21/40（選択性補正込み）・能力順位 12.86/20（25R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,800円（8.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 8R のうち的中赤字 3R／損益分岐の倍率 平均 8.3倍／同じ点数を無作為に選んだ場合の期待PFS 49.5%（同じ25Rの実績 39.7%）／券種別 EXACTA 13点 PFS 0.0%／TRIFECTA 24点 PFS 0.0%／TRIO 129点 PFS 36.8%／WIDE 40点 PFS 87.8%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 7R PFS 44.8% 的中赤字 1/2／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 15R PFS 24.7% 的中赤字 2/4／市場ミラーとの差 25R：実績 39.7% − ミラー 71.9% = Δ -32.2pt（95%区間 -85.7〜19.9、最高1R除き -43.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 57,100円（38.1%）／保護層の資金比率 0.0（25R）／組だけ的中（三連単は外れ）9R・着順まで的中 3R／的中 10R のうち的中赤字 10R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 45.6%（同じ25Rの実績 12.2%）／券種別 EXACTA 375点 PFS 9.9%／TRIFECTA 625点 PFS 9.9%／TRIO 500点 PFS 16.7%／荒れ度（発走前・1番人気オッズ）MID 7R PFS 20.4% 的中赤字 3/3／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 15R PFS 9.1% 的中赤字 6/6／市場ミラーとの差 25R：実績 12.2% − ミラー 90.8% = Δ -78.6pt（95%区間 -175.3〜-17.0、最高1R除き -83.8pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 11 | 63,280 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 10 | 41,760 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 7 | 42,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 25 | 131,760 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

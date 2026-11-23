# 地方版 2026-11-23 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 24／PAPER PFS 43.0%／正式推薦 PFS 12.3%
- 第一失敗：{'PREDICTION_ROLE_P2': 7, 'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 11}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 8 | 24.5 | 9.6 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 4} |
| MIZ | 11 | 82.8 | 11.6 | {'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 2} |
| SAG | 5 | 0.0 | 18.4 | {'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_P2': 1} |

## 日次自律監査

1. 配送：管理 33R／PAPER発走前送信 28／正式試行 28・発走前送信 28／本人確認 0
2. 計算完走：Full29 28／Signed FINAL 28／KRS5000 28／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 43.0%／正式推薦 12.3%／実購入なし
5. Learning：RESULT署名検証 24／学習状態保存 24／前Raceの学習状態を結合した正式Race 28（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '165/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 24 | 33.3% | 66.7% | 33.3% | 8.3% | 20.8% | 8.3% | 25.0% | 1.5 |
| 正式推薦 | 24 | 37.5% | 54.2% | 54.2% | 66.7% | 100.0% | 54.2% | 33.3% | 1.42 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.3%（無作為10.4%、差+22.9）／P2 平均1.0頭 的中8.3%（無作為10.4%、差-2.1）／P3 平均1.0頭 的中20.8%（無作為10.4%、差+10.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中54.2%（無作為31.3%、差+22.9）／P2 平均6.0頭 的中66.7%（無作為62.5%、差+4.2）／P3 平均9.75頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.21/40（選択性補正込み）・能力順位 13.41/20（24R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.89/40（選択性補正込み）・能力順位 12.79/20（24R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,200円（6.2%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 8R のうち的中赤字 3R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 53.5%（同じ24Rの実績 43.0%）／券種別 EXACTA 10点 PFS 0.0%／TRIFECTA 16点 PFS 0.0%／TRIO 124点 PFS 38.3%／WIDE 40点 PFS 87.8%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 7R PFS 44.8% 的中赤字 1/2／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 14R PFS 28.1% 的中赤字 2/4／市場ミラーとの差 24R：実績 43.0% − ミラー 72.9% = Δ -29.8pt（95%区間 -93.1〜25.5、最高1R除き -42.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 54,800円（38.1%）／保護層の資金比率 0.0（24R）／組だけ的中（三連単は外れ）8R・着順まで的中 3R／的中 9R のうち的中赤字 9R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 47.5%（同じ24Rの実績 12.3%）／券種別 EXACTA 360点 PFS 9.8%／TRIFECTA 600点 PFS 10.3%／TRIO 480点 PFS 16.8%／荒れ度（発走前・1番人気オッズ）MID 7R PFS 20.4% 的中赤字 3/3／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 14R PFS 9.2% 的中赤字 5/5／市場ミラーとの差 24R：実績 12.3% − ミラー 93.9% = Δ -81.6pt（95%区間 -186.6〜-16.4、最高1R除き -87.0pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 11 | 63,280 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 9 | 36,230 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 7 | 42,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 24 | 126,230 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

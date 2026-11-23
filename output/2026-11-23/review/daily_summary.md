# 地方版 2026-11-23 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 19／PAPER PFS 53.4%／正式推薦 PFS 11.5%
- 第一失敗：{'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 9}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 6 | 30.9 | 3.8 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1, 'PREDICTION_ROLE_W': 3} |
| MIZ | 10 | 85.8 | 12.3 | {'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 2} |
| SAG | 3 | 0.0 | 24.2 | {'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 33R／PAPER発走前送信 24／正式試行 24・発走前送信 24／本人確認 0
2. 計算完走：Full29 24／Signed FINAL 24／KRS5000 24／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 53.4%／正式推薦 11.5%／実購入なし
5. Learning：RESULT署名検証 19／学習状態保存 19／前Raceの学習状態を結合した正式Race 24（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '165/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 19 | 31.6% | 63.2% | 31.6% | 5.3% | 21.1% | 5.3% | 26.3% | 1.42 |
| 正式推薦 | 19 | 31.6% | 52.6% | 52.6% | 63.2% | 100.0% | 52.6% | 26.3% | 1.42 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中31.6%（無作為10.4%、差+21.2）／P2 平均1.0頭 的中5.3%（無作為10.4%、差-5.1）／P3 平均1.0頭 的中21.1%（無作為10.4%、差+10.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中52.6%（無作為31.2%、差+21.5）／P2 平均6.0頭 的中63.2%（無作為62.3%、差+0.8）／P3 平均9.74頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.26/40（選択性補正込み）・能力順位 13.09/20（19R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.48/40（選択性補正込み）・能力順位 12.4/20（19R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（4.1%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）5R・着順まで的中 0R／的中 7R のうち的中赤字 2R／損益分岐の倍率 平均 7.8倍／同じ点数を無作為に選んだ場合の期待PFS 59.5%（同じ19Rの実績 53.4%）／券種別 EXACTA 7点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 99点 PFS 45.6%／WIDE 32点 PFS 105.9%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 51.8% 的中赤字 1/2／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 10R PFS 36.6% 的中赤字 1/3／市場ミラーとの差 19R：実績 53.4% − ミラー 66.0% = Δ -12.6pt（95%区間 -88.8〜51.7、最高1R除き -28.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 43,400円（38.1%）／保護層の資金比率 0.0（19R）／組だけ的中（三連単は外れ）5R・着順まで的中 3R／的中 5R のうち的中赤字 5R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 54.4%（同じ19Rの実績 11.5%）／券種別 EXACTA 285点 PFS 6.8%／TRIFECTA 475点 PFS 13.1%／TRIO 380点 PFS 13.1%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 21.1% 的中赤字 2/2／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 10R PFS 6.7% 的中赤字 2/2／市場ミラーとの差 19R：実績 11.5% − ミラー 104.8% = Δ -93.3pt（95%区間 -218.4〜-12.9、最高1R除き -100.9pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 9 | 52,490 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 6 | 36,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 5 | 16,900 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 19 | 100,900 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-23 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 11／PAPER PFS 61.2%／正式推薦 PFS 11.0%
- 第一失敗：{'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 4 | 44.3 | 5.6 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1, 'PREDICTION_ROLE_W': 1} |
| MIZ | 7 | 73.9 | 14.0 | {'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 2} |

## 日次自律監査

1. 配送：管理 33R／PAPER発走前送信 15／正式試行 15・発走前送信 15／本人確認 0
2. 計算完走：Full29 15／Signed FINAL 15／KRS5000 15／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 61.2%／正式推薦 11.0%／実購入なし
5. Learning：RESULT署名検証 11／学習状態保存 11／前Raceの学習状態を結合した正式Race 15（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '30R到達', 'C23-THIRD3-BY-PAIR': '30R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '30R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '165/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 11 | 54.5% | 81.8% | 54.5% | 9.1% | 18.2% | 9.1% | 27.3% | 1.45 |
| 正式推薦 | 11 | 54.5% | 72.7% | 72.7% | 45.5% | 100.0% | 72.7% | 27.3% | 1.36 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中54.5%（無作為10.5%、差+44.1）／P2 平均1.0頭 的中9.1%（無作為10.5%、差-1.4）／P3 平均1.0頭 的中18.2%（無作為10.5%、差+7.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中72.7%（無作為31.4%、差+41.3）／P2 平均6.0頭 的中45.5%（無作為62.9%、差-17.4）／P3 平均9.64頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.91/40（選択性補正込み）・能力順位 13.87/20（11R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.62/40（選択性補正込み）・能力順位 12.72/20（11R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（7.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）3R・着順まで的中 0R／的中 5R のうち的中赤字 2R／損益分岐の倍率 平均 7.8倍／同じ点数を無作為に選んだ場合の期待PFS 37.7%（同じ11Rの実績 61.2%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 55点 PFS 42.4%／WIDE 20点 PFS 146.5%／荒れ度（発走前・1番人気オッズ）MID 3R PFS 111.0% 的中赤字 1/2／SOLID 8R PFS 45.1% 的中赤字 1/3／市場ミラーとの差 11R：実績 61.2% − ミラー 95.6% = Δ -34.4pt（95%区間 -156.2〜70.4、最高1R除き -64.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 25,100円（38.0%）／保護層の資金比率 0.0（11R）／組だけ的中（三連単は外れ）3R・着順まで的中 2R／的中 3R のうち的中赤字 3R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 29.0%（同じ11Rの実績 11.0%）／券種別 EXACTA 165点 PFS 7.9%／TRIFECTA 275点 PFS 12.9%／TRIO 220点 PFS 10.8%／荒れ度（発走前・1番人気オッズ）MID 3R PFS 17.9% 的中赤字 1/1／SOLID 8R PFS 8.4% 的中赤字 2/2／市場ミラーとの差 11R：実績 11.0% − ミラー 155.2% = Δ -144.2pt（95%区間 -349.6〜-10.1、最高1R除き -158.7pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 3 | 18,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 3 | 10,770 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 11 | 58,770 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

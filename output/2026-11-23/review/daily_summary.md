# 地方版 2026-11-23 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 15／PAPER PFS 53.6%／正式推薦 PFS 12.9%
- 第一失敗：{'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 6}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 5 | 37.3 | 4.5 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1, 'PREDICTION_ROLE_W': 2} |
| MIZ | 8 | 80.7 | 12.2 | {'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 2} |
| SAG | 2 | 0.0 | 36.3 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 33R／PAPER発走前送信 21／正式試行 21・発走前送信 21／本人確認 0
2. 計算完走：Full29 21／Signed FINAL 21／KRS5000 21／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 53.6%／正式推薦 12.9%／実購入なし
5. Learning：RESULT署名検証 15／学習状態保存 15／前Raceの学習状態を結合した正式Race 21（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '165/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 15 | 40.0% | 66.7% | 40.0% | 6.7% | 20.0% | 6.7% | 26.7% | 1.47 |
| 正式推薦 | 15 | 40.0% | 60.0% | 60.0% | 60.0% | 100.0% | 60.0% | 26.7% | 1.4 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中40.0%（無作為10.4%、差+29.6）／P2 平均1.0頭 的中6.7%（無作為10.4%、差-3.7）／P3 平均1.0頭 的中20.0%（無作為10.4%、差+9.6）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.0%（無作為31.2%、差+28.8）／P2 平均6.0頭 的中60.0%（無作為62.4%、差-2.4）／P3 平均9.73頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.2/40（選択性補正込み）・能力順位 13.48/20（15R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.09/40（選択性補正込み）・能力順位 12.78/20（15R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（5.2%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）4R・着順まで的中 0R／的中 6R のうち的中赤字 2R／損益分岐の倍率 平均 7.7倍／同じ点数を無作為に選んだ場合の期待PFS 52.3%（同じ15Rの実績 53.6%）／券種別 EXACTA 5点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 75点 PFS 40.0%／WIDE 26点 PFS 121.5%／WIN 1点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 4R PFS 83.2% 的中赤字 1/2／OPEN 1R PFS 128.6% 的中赤字 0/1／SOLID 10R PFS 36.6% 的中赤字 1/3／市場ミラーとの差 15R：実績 53.6% − ミラー 79.0% = Δ -25.4pt（95%区間 -110.5〜50.0、最高1R除き -46.7pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 34,200円（38.0%）／保護層の資金比率 0.0（15R）／組だけ的中（三連単は外れ）4R・着順まで的中 3R／的中 4R のうち的中赤字 4R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 47.4%（同じ15Rの実績 12.9%）／券種別 EXACTA 225点 PFS 8.6%／TRIFECTA 375点 PFS 16.5%／TRIO 300点 PFS 11.5%／荒れ度（発走前・1番人気オッズ）MID 4R PFS 31.6% 的中赤字 2/2／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 10R PFS 6.7% 的中赤字 2/2／市場ミラーとの差 15R：実績 12.9% − ミラー 127.2% = Δ -114.3pt（95%区間 -268.8〜-16.8、最高1R除き -125.6pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 6 | 36,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 4 | 12,410 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 15 | 78,410 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

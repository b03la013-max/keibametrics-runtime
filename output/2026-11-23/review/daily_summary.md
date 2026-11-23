# 地方版 2026-11-23 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 22／PAPER PFS 48.9%／正式推薦 PFS 12.7%
- 第一失敗：{'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 10}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 7 | 27.3 | 8.7 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 3} |
| MIZ | 11 | 82.8 | 11.6 | {'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 2} |
| SAG | 4 | 0.0 | 23.0 | {'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 2} |

## 日次自律監査

1. 配送：管理 33R／PAPER発走前送信 27／正式試行 27・発走前送信 27／本人確認 0
2. 計算完走：Full29 27／Signed FINAL 27／KRS5000 27／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 48.9%／正式推薦 12.7%／実購入なし
5. Learning：RESULT署名検証 22／学習状態保存 22／前Raceの学習状態を結合した正式Race 27（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '165/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 22 | 31.8% | 68.2% | 31.8% | 4.5% | 22.7% | 4.5% | 27.3% | 1.5 |
| 正式推薦 | 22 | 36.4% | 54.5% | 54.5% | 68.2% | 100.0% | 54.5% | 31.8% | 1.45 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中31.8%（無作為10.5%、差+21.3）／P2 平均1.0頭 的中4.5%（無作為10.5%、差-6.0）／P3 平均1.0頭 的中22.7%（無作為10.5%、差+12.2）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中54.5%（無作為31.6%、差+22.9）／P2 平均6.0頭 的中68.2%（無作為63.2%、差+5.0）／P3 平均9.64頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.91/40（選択性補正込み）・能力順位 13.39/20（22R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.78/40（選択性補正込み）・能力順位 12.7/20（22R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（3.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 8R のうち的中赤字 3R／損益分岐の倍率 平均 7.7倍／同じ点数を無作為に選んだ場合の期待PFS 55.1%（同じ22Rの実績 48.9%）／券種別 EXACTA 7点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 114点 PFS 41.7%／WIDE 38点 PFS 92.4%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 51.8% 的中赤字 1/2／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 13R PFS 32.6% 的中赤字 2/4／市場ミラーとの差 22R：実績 48.9% − ミラー 75.5% = Δ -26.6pt（95%区間 -96.5〜37.2、最高1R除き -40.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 50,100円（38.0%）／保護層の資金比率 0.0（22R）／組だけ的中（三連単は外れ）7R・着順まで的中 3R／的中 8R のうち的中赤字 8R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 48.7%（同じ22Rの実績 12.7%）／券種別 EXACTA 330点 PFS 10.6%／TRIFECTA 550点 PFS 11.3%／TRIO 440点 PFS 16.1%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 21.1% 的中赤字 2/2／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 13R PFS 9.9% 的中赤字 5/5／市場ミラーとの差 22R：実績 12.7% − ミラー 100.8% = Δ -88.0pt（95%区間 -198.3〜-17.5、最高1R除き -94.3pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 10 | 58,250 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 8 | 31,200 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 6 | 36,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 22 | 115,200 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

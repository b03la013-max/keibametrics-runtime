# 地方版 2026-11-23 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 27／PAPER PFS 37.2%／正式推薦 PFS 13.9%
- 第一失敗：{'PREDICTION_ROLE_P2': 8, 'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 11}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 9 | 22.2 | 16.4 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4} |
| MIZ | 12 | 69.0 | 11.2 | {'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 3} |
| SAG | 6 | 0.0 | 15.3 | {'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_P2': 2} |

## 日次自律監査

1. 配送：管理 33R／PAPER発走前送信 30／正式試行 30・発走前送信 30／本人確認 0
2. 計算完走：Full29 30／Signed FINAL 30／KRS5000 30／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 37.2%／正式推薦 13.9%／実購入なし
5. Learning：RESULT署名検証 27／学習状態保存 27／前Raceの学習状態を結合した正式Race 30（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '165/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 27 | 37.0% | 66.7% | 37.0% | 7.4% | 18.5% | 11.1% | 22.2% | 1.44 |
| 正式推薦 | 27 | 37.0% | 59.3% | 59.3% | 66.7% | 100.0% | 59.3% | 37.0% | 1.48 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中37.0%（無作為10.5%、差+26.6）／P2 平均1.0頭 的中7.4%（無作為10.5%、差-3.1）／P3 平均1.0頭 的中18.5%（無作為10.5%、差+8.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中59.3%（無作為31.4%、差+27.9）／P2 平均6.0頭 的中66.7%（無作為62.8%、差+3.9）／P3 平均9.7頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.0/40（選択性補正込み）・能力順位 13.31/20（27R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.51/40（選択性補正込み）・能力順位 12.92/20（27R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,800円（8.1%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 8R のうち的中赤字 3R／損益分岐の倍率 平均 8.2倍／同じ点数を無作為に選んだ場合の期待PFS 47.2%（同じ27Rの実績 37.2%）／券種別 EXACTA 13点 PFS 0.0%／TRIFECTA 24点 PFS 0.0%／TRIO 139点 PFS 34.2%／WIDE 44点 PFS 79.8%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 39.5% 的中赤字 1/2／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 16R PFS 23.5% 的中赤字 2/4／市場ミラーとの差 27R：実績 37.2% − ミラー 75.5% = Δ -38.3pt（95%区間 -92.2〜12.9、最高1R除き -49.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 61,700円（38.1%）／保護層の資金比率 0.0（27R）／組だけ的中（三連単は外れ）9R・着順まで的中 4R／的中 11R のうち的中赤字 11R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 43.2%（同じ27Rの実績 13.9%）／券種別 EXACTA 405点 PFS 11.8%／TRIFECTA 675点 PFS 13.2%／TRIO 540点 PFS 16.2%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 17.8% 的中赤字 3/3／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 16R PFS 12.9% 的中赤字 7/7／市場ミラーとの差 27R：実績 13.9% − ミラー 89.7% = Δ -75.9pt（95%区間 -167.6〜-17.5、最高1R除き -80.5pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 11 | 63,280 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 11 | 43,560 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 8 | 48,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 27 | 139,560 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-23 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 14／PAPER PFS 57.0%／正式推薦 PFS 8.6%
- 第一失敗：{'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 6}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 5 | 37.3 | 4.5 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1, 'PREDICTION_ROLE_W': 2} |
| MIZ | 8 | 80.7 | 12.2 | {'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 2} |
| SAG | 1 | 0.0 | 0.0 | {'PREDICTION_ROLE_W': 1} |

## 日次自律監査

1. 配送：管理 33R／PAPER発走前送信 19／正式試行 19・発走前送信 19／本人確認 0
2. 計算完走：Full29 19／Signed FINAL 19／KRS5000 19／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 57.0%／正式推薦 8.6%／実購入なし
5. Learning：RESULT署名検証 14／学習状態保存 14／前Raceの学習状態を結合した正式Race 19（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '30R到達', 'C23-THIRD3-BY-PAIR': '30R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '30R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '165/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 14 | 42.9% | 64.3% | 42.9% | 7.1% | 21.4% | 7.1% | 28.6% | 1.5 |
| 正式推薦 | 14 | 42.9% | 57.1% | 57.1% | 57.1% | 100.0% | 57.1% | 21.4% | 1.36 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中42.9%（無作為10.4%、差+32.4）／P2 平均1.0頭 的中7.1%（無作為10.4%、差-3.3）／P3 平均1.0頭 的中21.4%（無作為10.4%、差+11.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中57.1%（無作為31.3%、差+25.8）／P2 平均6.0頭 的中57.1%（無作為62.6%、差-5.5）／P3 平均9.71頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.0/40（選択性補正込み）・能力順位 13.46/20（14R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.54/40（選択性補正込み）・能力順位 12.53/20（14R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（5.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）4R・着順まで的中 0R／的中 6R のうち的中赤字 2R／損益分岐の倍率 平均 7.7倍／同じ点数を無作為に選んだ場合の期待PFS 54.8%（同じ14Rの実績 57.0%）／券種別 EXACTA 5点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 70点 PFS 42.9%／WIDE 24点 PFS 131.7%／WIN 1点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 3R PFS 111.0% 的中赤字 1/2／OPEN 1R PFS 128.6% 的中赤字 0/1／SOLID 10R PFS 36.6% 的中赤字 1/3／市場ミラーとの差 14R：実績 57.0% − ミラー 84.1% = Δ -27.0pt（95%区間 -119.6〜53.3、最高1R除き -49.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 31,900円（38.0%）／保護層の資金比率 0.0（14R）／組だけ的中（三連単は外れ）4R・着順まで的中 2R／的中 3R のうち的中赤字 3R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 50.3%（同じ14Rの実績 8.6%）／券種別 EXACTA 210点 PFS 6.2%／TRIFECTA 350点 PFS 10.1%／TRIO 280点 PFS 8.5%／荒れ度（発走前・1番人気オッズ）MID 3R PFS 17.9% 的中赤字 1/1／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 10R PFS 6.7% 的中赤字 2/2／市場ミラーとの差 14R：実績 8.6% − ミラー 134.2% = Δ -125.6pt（95%区間 -290.5〜-20.6、最高1R除き -135.3pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 6 | 36,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 3 | 10,770 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 14 | 76,770 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

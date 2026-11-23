# 地方版 2026-11-23 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 18／PAPER PFS 44.3%／正式推薦 PFS 10.7%
- 第一失敗：{'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 8}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 6 | 30.9 | 3.8 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1, 'PREDICTION_ROLE_W': 3} |
| MIZ | 9 | 70.6 | 10.9 | {'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 2} |
| SAG | 3 | 0.0 | 24.2 | {'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 33R／PAPER発走前送信 24／正式試行 24・発走前送信 24／本人確認 0
2. 計算完走：Full29 24／Signed FINAL 24／KRS5000 24／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 44.3%／正式推薦 10.7%／実購入なし
5. Learning：RESULT署名検証 18／学習状態保存 18／前Raceの学習状態を結合した正式Race 24（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '165/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 18 | 33.3% | 61.1% | 33.3% | 5.6% | 22.2% | 5.6% | 22.2% | 1.39 |
| 正式推薦 | 18 | 33.3% | 55.6% | 55.6% | 61.1% | 100.0% | 55.6% | 22.2% | 1.39 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.3%（無作為10.4%、差+22.9）／P2 平均1.0頭 的中5.6%（無作為10.4%、差-4.9）／P3 平均1.0頭 的中22.2%（無作為10.4%、差+11.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中55.6%（無作為31.2%、差+24.3）／P2 平均6.0頭 的中61.1%（無作為62.5%、差-1.4）／P3 平均9.72頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.22/40（選択性補正込み）・能力順位 12.92/20（18R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.5/40（選択性補正込み）・能力順位 12.23/20（18R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（4.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）4R・着順まで的中 0R／的中 6R のうち的中赤字 2R／損益分岐の倍率 平均 7.7倍／同じ点数を無作為に選んだ場合の期待PFS 62.3%（同じ18Rの実績 44.3%）／券種別 EXACTA 7点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 92点 PFS 32.6%／WIDE 30点 PFS 105.3%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 51.8% 的中赤字 1/2／OPEN 2R PFS 64.3% 的中赤字 0/1／SOLID 10R PFS 36.6% 的中赤字 1/3／市場ミラーとの差 18R：実績 44.3% − ミラー 70.3% = Δ -26.0pt（95%区間 -103.5〜37.2、最高1R除き -43.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 41,200円（38.1%）／保護層の資金比率 0.0（18R）／組だけ的中（三連単は外れ）4R・着順まで的中 3R／的中 4R のうち的中赤字 4R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 56.7%（同じ18Rの実績 10.7%）／券種別 EXACTA 270点 PFS 7.1%／TRIFECTA 450点 PFS 13.8%／TRIO 360点 PFS 9.6%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 21.1% 的中赤字 2/2／OPEN 2R PFS 0.0% 的中赤字 0/0／SOLID 10R PFS 6.7% 的中赤字 2/2／市場ミラーとの差 18R：実績 10.7% − ミラー 109.2% = Δ -98.5pt（95%区間 -232.8〜-13.4、最高1R除き -106.9pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 8 | 48,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 6 | 36,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 4 | 12,410 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 18 | 96,410 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

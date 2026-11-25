# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 19／PAPER PFS 42.6%／正式推薦 PFS 37.2%
- 第一失敗：{'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 11, 'NONE': 1, 'PREDICTION_ROLE_P2': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 2 | 36.4 | 29.7 | {'CAPITAL_EFFICIENCY': 1, 'PREDICTION_ROLE_W': 1} |
| SON | 10 | 22.8 | 54.2 | {'PREDICTION_ROLE_W': 8, 'NONE': 1, 'PREDICTION_ROLE_P2': 1} |
| URW | 7 | 87.6 | 14.9 | {'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 2} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 24／正式試行 24・発走前送信 24／本人確認 0
2. 計算完走：Full29 24／Signed FINAL 24／KRS5000 24／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 42.6%／正式推薦 37.2%／実購入なし
5. Learning：RESULT署名検証 19／学習状態保存 19／前Raceの学習状態を結合した正式Race 24（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 19 | 15.8% | 57.9% | 15.8% | 26.3% | 5.3% | 10.5% | 15.8% | 1.37 |
| 正式推薦 | 19 | 21.1% | 42.1% | 42.1% | 89.5% | 100.0% | 42.1% | 36.8% | 1.16 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中15.8%（無作為9.1%、差+6.7）／P2 平均1.0頭 的中26.3%（無作為9.1%、差+17.2）／P3 平均1.0頭 的中5.3%（無作為9.1%、差-3.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中42.1%（無作為27.4%、差+14.7）／P2 平均6.0頭 的中89.5%（無作為54.8%、差+34.6）／P3 平均11.16頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.21/40（選択性補正込み）・能力順位 12.97/20（19R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.85/40（選択性補正込み）・能力順位 12.37/20（19R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（13.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）4R・着順まで的中 0R／的中 6R のうち的中赤字 4R／損益分岐の倍率 平均 9.1倍／同じ点数を無作為に選んだ場合の期待PFS 92.2%（同じ19Rの実績 42.6%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 97点 PFS 61.2%／WIDE 26点 PFS 48.8%／WIN 2点 PFS 80.0%／荒れ度（発走前・1番人気オッズ）MID 11R PFS 53.1% 的中赤字 2/3／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 6R PFS 43.3% 的中赤字 2/3／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 18R：実績 46.9% − ミラー 36.5% = Δ 10.4pt（95%区間 -33.0〜70.0、最高1R除き -13.8pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 43,700円（38.3%）／保護層の資金比率 0.0（19R）／組だけ的中（三連単は外れ）7R・着順まで的中 0R／的中 12R のうち的中赤字 11R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 91.7%（同じ19Rの実績 37.2%）／券種別 EXACTA 285点 PFS 49.9%／TRIFECTA 475点 PFS 0.0%／TRIO 380点 PFS 74.1%／荒れ度（発走前・1番人気オッズ）MID 11R PFS 20.1% 的中赤字 6/6／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 6R PFS 76.4% 的中赤字 4/5／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 18R：実績 37.8% − ミラー 40.7% = Δ -3.0pt（95%区間 -53.9〜54.1、最高1R除き -25.1pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 11 | 54,860 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 11 | 46,080 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 19 | 88,080 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

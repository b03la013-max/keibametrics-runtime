# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 11／PAPER PFS 129.8%／正式推薦 PFS 22.7%
- 第一失敗：{'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| SON | 7 | 181.6 | 31.0 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1} |
| URW | 4 | 29.7 | 8.0 | {'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 2} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 17／正式試行 17・発走前送信 17／本人確認 0
2. 計算完走：Full29 17／Signed FINAL 17／KRS5000 17／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 129.8%／正式推薦 22.7%／実購入なし
5. Learning：RESULT署名検証 11／学習状態保存 11／前Raceの学習状態を結合した正式Race 17（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 11 | 54.5% | 90.9% | 54.5% | 0.0% | 18.2% | 0.0% | 27.3% | 1.64 |
| 正式推薦 | 11 | 36.4% | 72.7% | 72.7% | 63.6% | 100.0% | 72.7% | 36.4% | 1.36 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中54.5%（無作為8.8%、差+45.8）／P2 平均1.0頭 的中0.0%（無作為8.8%、差-8.8）／P3 平均1.0頭 的中18.2%（無作為8.8%、差+9.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中72.7%（無作為26.4%、差+46.4）／P2 平均6.0頭 的中63.6%（無作為52.7%、差+10.9）／P3 平均11.45頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.64/40（選択性補正込み）・能力順位 14.55/20（11R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.6/40（選択性補正込み）・能力順位 13.56/20（11R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（6.8%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）4R・着順まで的中 0R／的中 4R のうち的中赤字 0R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 50.3%（同じ11Rの実績 129.8%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 57点 PFS 112.1%／WIDE 20点 PFS 251.5%／荒れ度（発走前・1番人気オッズ）MID 7R PFS 23.3% 的中赤字 0/1／SOLID 3R PFS 206.3% 的中赤字 0/2／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 10R：実績 91.1% − ミラー 13.5% = Δ 77.7pt（95%区間 0.0〜234.6、最高1R除き 13.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 25,700円（38.9%）／保護層の資金比率 0.0（11R）／組だけ的中（三連単は外れ）3R・着順まで的中 1R／的中 6R のうち的中赤字 6R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 37.5%（同じ11Rの実績 22.7%）／券種別 EXACTA 165点 PFS 27.2%／TRIFECTA 275点 PFS 13.7%／TRIO 220点 PFS 30.5%／荒れ度（発走前・1番人気オッズ）MID 7R PFS 5.1% 的中赤字 2/2／SOLID 3R PFS 66.7% 的中赤字 3/3／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 10R：実績 23.6% − ミラー 26.6% = Δ -3.0pt（95%区間 -26.1〜21.0、最高1R除き -12.0pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、11R×3券種）：購入 3／予算で削除 0／予想で除外 10／未生成・券種なし 20／役割馬の行き先 {'PURCHASED': 33}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、11R×3券種）：購入 11／予算で削除 6／予想で除外 10／未生成・券種なし 6／役割馬の行き先 {'PURCHASED': 80, 'BUDGET_COMPRESSED': 46}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 6R／W外 5R、2着が P2 役割 0R）：STATIC 0/6（平均5.17位）／STYLE_COND 1/6（平均4.67位） 救済1・喪失0／MARKET_COND 0/5（平均4.4位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 8R／W外 3R、2着が P2 役割 6R）：STATIC 6/8（平均4.12位）／STYLE_COND 6/8（平均3.75位） 救済0・喪失0／MARKET_COND 6/7（平均2.86位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 6 | 21,040 | RECURRING |
| P1:ROLE_W_MISS | P1 | 3 | 18,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 11 | 51,040 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

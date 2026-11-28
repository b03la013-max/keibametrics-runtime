# 地方版 2026-11-28 日次総括（自動・推薦試算・実購入なし）

- 反省済みRace 24／PAPER PFS 26.1%／正式推薦 PFS 149.7%
- 第一失敗：{'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 3, 'NONE': 5, 'PREDICTION_ROLE_W': 10}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KOC | 12 | 21.0 | 280.0 | {'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 1, 'NONE': 4, 'PREDICTION_ROLE_W': 3} |
| SAG | 12 | 31.2 | 19.5 | {'PREDICTION_ROLE_W': 7, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2, 'NONE': 1} |

## 日次自律監査

1. 配送：管理 24R／PAPER発走前送信 24／正式試行 24・発走前送信 24／本人確認 0
2. 計算完走：Full29 24／Signed FINAL 24／KRS5000 24／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 26.1%／正式推薦 149.7%／実購入なし
5. Learning：RESULT署名検証 24／学習状態保存 24／前Raceの学習状態を結合した正式Race 24（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '100R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '300R到達', 'C17-P2-ZAI-PLACE': '300R到達', 'C18-W-PLUS-FAVORITE': '300R到達', 'C19-W-PLUS-TOP2-POP': '300R到達', 'C20-P2-PLUS-TOP3-POP': '300R到達', 'C21-BVI-L-R2-TERTILE': '300R到達'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 24 | 37.5% | 66.7% | 37.5% | 0.0% | 20.8% | 8.3% | 16.7% | 1.54 |
| 正式推薦 | 24 | 37.5% | 58.3% | 58.3% | 70.8% | 100.0% | 87.5% | 29.2% | 1.46 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中37.5%（無作為9.8%、差+27.7）／P2 平均1.0頭 的中0.0%（無作為9.8%、差-9.8）／P3 平均1.0頭 的中20.8%（無作為9.8%、差+11.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中58.3%（無作為29.5%、差+28.9）／P2 平均6.0頭 的中70.8%（無作為58.9%、差+11.9）／P3 平均10.42頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.21/40（選択性補正込み）・能力順位 13.68/20（24R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.75/40（選択性補正込み）・能力順位 13.78/20（24R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,200円（6.2%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）4R・着順まで的中 0R／的中 7R のうち的中赤字 5R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 38.3%（同じ24Rの実績 26.1%）／券種別 EXACTA 12点 PFS 109.2%／TRIFECTA 16点 PFS 0.0%／TRIO 126点 PFS 22.8%／WIDE 38点 PFS 23.9%／WIN 3点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 9R PFS 22.8% 的中赤字 1/2／OPEN 2R PFS 77.5% 的中赤字 0/1／SOLID 13R PFS 20.7% 的中赤字 4/4／市場ミラーとの差 24R：実績 26.1% − ミラー 67.4% = Δ -41.3pt（95%区間 -97.7〜9.5、最高1R除き -52.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（24R）／組だけ的中（三連単は外れ）7R・着順まで的中 7R／的中 12R のうち的中赤字 7R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 32.8%（同じ24Rの実績 149.7%）／券種別 EXACTA 429点 PFS 63.1%／TRIFECTA 1011点 PFS 186.4%／荒れ度（発走前・1番人気オッズ）MID 9R PFS 139.0% 的中赤字 1/4／OPEN 2R PFS 102.8% 的中赤字 0/1／SOLID 13R PFS 164.4% 的中赤字 6/7／市場ミラーとの差 24R：実績 149.7% − ミラー 63.7% = Δ 86.0pt（95%区間 -54.0〜285.6、最高1R除き 3.2pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、24R×3券種）：購入 5／予算で削除 0／予想で除外 26／未生成・券種なし 41／役割馬の行き先 {'PURCHASED': 72}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、24R×3券種）：購入 18／予算で削除 6／予想で除外 27／未生成・券種なし 21／役割馬の行き先 {'PURCHASED': 180, 'BUDGET_COMPRESSED': 70}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 9R／W外 15R、2着が P2 役割 0R）：STATIC 0/9（平均3.89位）／STYLE_COND 1/9（平均3.89位） 救済1・喪失0／MARKET_COND 1/9（平均3.44位） 救済1・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 14R／W外 10R、2着が P2 役割 8R）：STATIC 10/14（平均4.86位）／STYLE_COND 10/14（平均4.93位） 救済0・喪失0／MARKET_COND 13/14（平均3.36位） 救済4・喪失1

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 10 | 54,450 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 7 | 32,600 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 6 | 36,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 24 | 104,600 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

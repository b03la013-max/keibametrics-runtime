# 地方版 2026-11-28 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 22／PAPER PFS 28.4%／正式推薦 PFS 162.9%
- 第一失敗：{'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 3, 'NONE': 5, 'PREDICTION_ROLE_W': 9}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KOC | 11 | 23.1 | 305.4 | {'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 1, 'NONE': 4, 'PREDICTION_ROLE_W': 3} |
| SAG | 11 | 33.7 | 20.4 | {'PREDICTION_ROLE_W': 6, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2, 'NONE': 1} |

## 日次自律監査

1. 配送：管理 24R／PAPER発走前送信 24／正式試行 24・発走前送信 24／本人確認 0
2. 計算完走：Full29 24／Signed FINAL 24／KRS5000 24／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 28.4%／正式推薦 162.9%／実購入なし
5. Learning：RESULT署名検証 22／学習状態保存 22／前Raceの学習状態を結合した正式Race 24（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '100R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '300R到達', 'C17-P2-ZAI-PLACE': '300R到達', 'C18-W-PLUS-FAVORITE': '300R到達', 'C19-W-PLUS-TOP2-POP': '300R到達', 'C20-P2-PLUS-TOP3-POP': '300R到達', 'C21-BVI-L-R2-TERTILE': '300R到達'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 22 | 40.9% | 72.7% | 40.9% | 0.0% | 22.7% | 9.1% | 18.2% | 1.68 |
| 正式推薦 | 22 | 40.9% | 59.1% | 59.1% | 72.7% | 100.0% | 86.4% | 31.8% | 1.5 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中40.9%（無作為10.0%、差+30.9）／P2 平均1.0頭 的中0.0%（無作為10.0%、差-10.0）／P3 平均1.0頭 的中22.7%（無作為10.0%、差+12.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中59.1%（無作為29.9%、差+29.1）／P2 平均6.0頭 的中72.7%（無作為59.9%、差+12.8）／P3 平均10.23頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.41/40（選択性補正込み）・能力順位 14.24/20（22R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.99/40（選択性補正込み）・能力順位 14.09/20（22R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,200円（6.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）4R・着順まで的中 0R／的中 7R のうち的中赤字 5R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 34.1%（同じ22Rの実績 28.4%）／券種別 EXACTA 12点 PFS 109.2%／TRIFECTA 16点 PFS 0.0%／TRIO 114点 PFS 25.2%／WIDE 34点 PFS 26.8%／WIN 3点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 25.4% 的中赤字 1/2／OPEN 1R PFS 177.1% 的中赤字 0/1／SOLID 13R PFS 20.7% 的中赤字 4/4／市場ミラーとの差 22R：実績 28.4% − ミラー 60.2% = Δ -31.8pt（95%区間 -90.7〜18.0、最高1R除き -42.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（22R）／組だけ的中（三連単は外れ）6R・着順まで的中 7R／的中 11R のうち的中赤字 6R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 32.2%（同じ22Rの実績 162.9%）／券種別 EXACTA 393点 PFS 67.5%／TRIFECTA 927点 PFS 203.3%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 155.2% 的中赤字 0/3／OPEN 1R PFS 205.5% 的中赤字 0/1／SOLID 13R PFS 164.4% 的中赤字 6/7／市場ミラーとの差 22R：実績 162.9% − ミラー 66.6% = Δ 96.3pt（95%区間 -56.5〜313.3、最高1R除き 6.1pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、22R×3券種）：購入 5／予算で削除 0／予想で除外 24／未生成・券種なし 37／役割馬の行き先 {'PURCHASED': 66}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、22R×3券種）：購入 17／予算で削除 5／予想で除外 24／未生成・券種なし 20／役割馬の行き先 {'PURCHASED': 165, 'BUDGET_COMPRESSED': 60}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 9R／W外 13R、2着が P2 役割 0R）：STATIC 0/9（平均3.89位）／STYLE_COND 1/9（平均3.89位） 救済1・喪失0／MARKET_COND 1/9（平均3.44位） 救済1・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 13R／W外 9R、2着が P2 役割 8R）：STATIC 10/13（平均4.46位）／STYLE_COND 10/13（平均4.54位） 救済0・喪失0／MARKET_COND 12/13（平均3.38位） 救済3・喪失1

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 9 | 49,010 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 6 | 27,160 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 22 | 93,160 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

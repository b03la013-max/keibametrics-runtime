# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 21／PAPER PFS 106.5%／正式推薦 PFS 28.9%
- 第一失敗：{'PREDICTION_ROLE_W': 6, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_P2': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 3 | 30.4 | 17.4 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 2} |
| NGY | 2 | 40.0 | 0.0 | {'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 1} |
| SON | 9 | 163.8 | 37.0 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1} |
| URW | 7 | 80.2 | 31.7 | {'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 4} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 28／正式試行 28・発走前送信 28／本人確認 0
2. 計算完走：Full29 28／Signed FINAL 28／KRS5000 28／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 106.5%／正式推薦 28.9%／実購入なし
5. Learning：RESULT署名検証 21／学習状態保存 21／前Raceの学習状態を結合した正式Race 28（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 21 | 42.9% | 71.4% | 42.9% | 9.5% | 23.8% | 0.0% | 38.1% | 1.62 |
| 正式推薦 | 21 | 33.3% | 71.4% | 71.4% | 76.2% | 100.0% | 71.4% | 42.9% | 1.57 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中42.9%（無作為9.1%、差+33.7）／P2 平均1.0頭 的中9.5%（無作為9.1%、差+0.4）／P3 平均1.0頭 的中23.8%（無作為9.1%、差+14.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中71.4%（無作為27.4%、差+44.0）／P2 平均6.0頭 的中76.2%（無作為54.8%、差+21.4）／P3 平均11.1頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.1/40（選択性補正込み）・能力順位 14.55/20（21R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.75/40（選択性補正込み）・能力順位 14.1/20（21R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（3.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）9R・着順まで的中 0R／的中 10R のうち的中赤字 3R／損益分岐の倍率 平均 7.8倍／同じ点数を無作為に選んだ場合の期待PFS 37.1%（同じ21Rの実績 106.5%）／券種別 EXACTA 7点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 111点 PFS 93.3%／WIDE 36点 PFS 197.2%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 10R PFS 39.1% 的中赤字 0/2／SOLID 10R PFS 129.0% 的中赤字 3/7／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 20R：実績 85.5% − ミラー 33.5% = Δ 52.0pt（95%区間 -6.5〜140.2、最高1R除き 19.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 48,900円（38.8%）／保護層の資金比率 0.0（21R）／組だけ的中（三連単は外れ）5R・着順まで的中 4R／的中 12R のうち的中赤字 12R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 26.4%（同じ21Rの実績 28.9%）／券種別 EXACTA 315点 PFS 32.6%／TRIFECTA 525点 PFS 21.5%／TRIO 420点 PFS 35.4%／荒れ度（発走前・1番人気オッズ）MID 10R PFS 12.7% 的中赤字 3/3／SOLID 10R PFS 46.7% 的中赤字 8/8／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 20R：実績 29.7% − ミラー 34.0% = Δ -4.3pt（95%区間 -23.4〜15.8、最高1R除き -9.1pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、21R×3券種）：購入 8／予算で削除 0／予想で除外 17／未生成・券種なし 38／役割馬の行き先 {'PURCHASED': 63}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、21R×3券種）：購入 25／予算で削除 9／予想で除外 18／未生成・券種なし 11／役割馬の行き先 {'PURCHASED': 154, 'BUDGET_COMPRESSED': 79}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 9R／W外 12R、2着が P2 役割 0R）：STATIC 0/9（平均4.33位）／STYLE_COND 1/9（平均4.11位） 救済1・喪失0／MARKET_COND 0/8（平均4.25位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 15R／W外 6R、2着が P2 役割 12R）：STATIC 12/15（平均3.73位）／STYLE_COND 12/15（平均3.53位） 救済0・喪失0／MARKET_COND 12/14（平均3.07位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 12 | 35,580 | RECURRING |
| P1:ROLE_W_MISS | P1 | 6 | 36,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 21 | 89,580 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

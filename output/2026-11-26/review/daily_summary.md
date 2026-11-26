# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 34／PAPER PFS 115.2%／正式推薦 PFS 40.1%
- 第一失敗：{'PREDICTION_ROLE_W': 10, 'CAPITAL_EFFICIENCY': 16, 'PREDICTION_ROLE_P2': 6, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 6 | 38.4 | 31.9 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 5} |
| NGY | 6 | 235.7 | 83.6 | {'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 1} |
| SON | 12 | 160.3 | 35.4 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 1} |
| URW | 10 | 51.7 | 24.7 | {'PREDICTION_ROLE_P2': 3, 'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 4} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 40／正式試行 40・発走前送信 40／本人確認 0
2. 計算完走：Full29 40／Signed FINAL 40／KRS5000 40／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 115.2%／正式推薦 40.1%／実購入なし
5. Learning：RESULT署名検証 34／学習状態保存 34／前Raceの学習状態を結合した正式Race 40（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 34 | 32.4% | 70.6% | 32.4% | 8.8% | 20.6% | 5.9% | 38.2% | 1.68 |
| 正式推薦 | 34 | 32.4% | 70.6% | 70.6% | 73.5% | 100.0% | 70.6% | 52.9% | 1.59 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.4%（無作為9.2%、差+23.2）／P2 平均1.0頭 的中8.8%（無作為9.2%、差-0.4）／P3 平均1.0頭 的中20.6%（無作為9.2%、差+11.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中70.6%（無作為27.6%、差+43.0）／P2 平均6.0頭 的中73.5%（無作為55.2%、差+18.3）／P3 平均11.06頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.79/40（選択性補正込み）・能力順位 14.69/20（34R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.68/40（選択性補正込み）・能力順位 14.24/20（34R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,800円（6.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）14R・着順まで的中 0R／的中 16R のうち的中赤字 6R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 32.5%（同じ34Rの実績 115.2%）／券種別 EXACTA 13点 PFS 34.6%／TRIFECTA 24点 PFS 0.0%／TRIO 178点 PFS 127.4%／WIDE 58点 PFS 147.4%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 19R PFS 115.3% 的中赤字 1/6／SOLID 14R PFS 89.6% 的中赤字 5/9／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 33R：実績 103.1% − ミラー 37.2% = Δ 65.9pt（95%区間 -3.6〜155.8、最高1R除き 36.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 78,500円（38.5%）／保護層の資金比率 0.0（34R）／組だけ的中（三連単は外れ）11R・着順まで的中 7R／的中 21R のうち的中赤字 19R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 25.0%（同じ34Rの実績 40.1%）／券種別 EXACTA 510点 PFS 42.7%／TRIFECTA 850点 PFS 23.5%／TRIO 680点 PFS 59.0%／荒れ度（発走前・1番人気オッズ）MID 19R PFS 45.3% 的中赤字 9/11／SOLID 14R PFS 35.1% 的中赤字 9/9／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 33R：実績 40.9% − ミラー 43.2% = Δ -2.2pt（95%区間 -21.6〜18.0、最高1R除き -5.5pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、34R×3券種）：購入 14／予算で削除 0／予想で除外 28／未生成・券種なし 60／役割馬の行き先 {'PURCHASED': 102}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、34R×3券種）：購入 42／予算で削除 13／予想で除外 32／未生成・券種なし 15／役割馬の行き先 {'PURCHASED': 251, 'BUDGET_COMPRESSED': 125}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 11R／W外 23R、2着が P2 役割 0R）：STATIC 0/11（平均4.36位）／STYLE_COND 2/11（平均4.09位） 救済2・喪失0／MARKET_COND 2/10（平均3.6位） 救済2・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 24R／W外 10R、2着が P2 役割 18R）：STATIC 19/24（平均3.92位）／STYLE_COND 19/24（平均3.79位） 救済0・喪失0／MARKET_COND 21/23（平均3.04位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 19 | 56,540 | RECURRING |
| P1:ROLE_W_MISS | P1 | 10 | 52,990 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 6 | 36,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 34 | 134,540 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

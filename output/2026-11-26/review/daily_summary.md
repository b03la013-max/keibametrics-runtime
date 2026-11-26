# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 42／PAPER PFS 116.5%／正式推薦 PFS 38.9%
- 第一失敗：{'PREDICTION_ROLE_W': 12, 'CAPITAL_EFFICIENCY': 22, 'PREDICTION_ROLE_P2': 6, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 9 | 106.9 | 34.0 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 8} |
| NGY | 9 | 183.3 | 70.1 | {'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 3} |
| SON | 12 | 160.3 | 35.4 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 1} |
| URW | 12 | 45.0 | 22.9 | {'PREDICTION_ROLE_P2': 3, 'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 5} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 45／正式試行 45・発走前送信 45／本人確認 0
2. 計算完走：Full29 45／Signed FINAL 45／KRS5000 45／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 116.5%／正式推薦 38.9%／実購入なし
5. Learning：RESULT署名検証 42／学習状態保存 42／前Raceの学習状態を結合した正式Race 45（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 42 | 38.1% | 69.0% | 38.1% | 11.9% | 19.0% | 9.5% | 35.7% | 1.64 |
| 正式推薦 | 42 | 31.0% | 71.4% | 71.4% | 76.2% | 100.0% | 71.4% | 52.4% | 1.52 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中38.1%（無作為9.3%、差+28.8）／P2 平均1.0頭 的中11.9%（無作為9.3%、差+2.6）／P3 平均1.0頭 的中19.0%（無作為9.3%、差+9.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中71.4%（無作為27.9%、差+43.5）／P2 平均6.0頭 的中76.2%（無作為55.8%、差+20.4）／P3 平均11.0頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.33/40（選択性補正込み）・能力順位 14.54/20（42R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.58/40（選択性補正込み）・能力順位 13.97/20（42R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（7.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）15R・着順まで的中 1R／的中 21R のうち的中赤字 8R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 49.0%（同じ42Rの実績 116.5%）／券種別 EXACTA 18点 PFS 50.0%／TRIFECTA 32点 PFS 31.6%／TRIO 218点 PFS 107.0%／WIDE 70点 PFS 204.7%／WIN 3点 PFS 53.3%／荒れ度（発走前・1番人気オッズ）MID 24R PFS 119.7% 的中赤字 2/9／SOLID 17R PFS 92.4% 的中赤字 6/11／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 41R：実績 106.9% − ミラー 40.8% = Δ 66.0pt（95%区間 3.7〜147.2、最高1R除き 42.8pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 97,300円（38.6%）／保護層の資金比率 0.0（42R）／組だけ的中（三連単は外れ）12R・着順まで的中 10R／的中 27R のうち的中赤字 25R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 45.9%（同じ42Rの実績 38.9%）／券種別 EXACTA 630点 PFS 49.1%／TRIFECTA 1050点 PFS 23.4%／TRIO 840点 PFS 50.8%／荒れ度（発走前・1番人気オッズ）MID 24R PFS 45.9% 的中赤字 14/16／SOLID 17R PFS 30.6% 的中赤字 10/10／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 41R：実績 39.6% − ミラー 42.2% = Δ -2.6pt（95%区間 -18.1〜13.2、最高1R除き -5.2pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、42R×3券種）：購入 17／予算で削除 0／予想で除外 36／未生成・券種なし 73／役割馬の行き先 {'PURCHASED': 126}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、42R×3券種）：購入 55／予算で削除 16／予想で除外 36／未生成・券種なし 19／役割馬の行き先 {'PURCHASED': 308, 'BUDGET_COMPRESSED': 154}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 16R／W外 26R、2着が P2 役割 2R）：STATIC 2/16（平均4.0位）／STYLE_COND 4/16（平均3.75位） 救済2・喪失0／MARKET_COND 4/15（平均3.07位） 救済3・喪失1
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 30R／W外 12R、2着が P2 役割 24R）：STATIC 25/30（平均3.83位）／STYLE_COND 25/30（平均3.67位） 救済0・喪失0／MARKET_COND 27/29（平均2.83位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 25 | 76,260 | RECURRING |
| P1:ROLE_W_MISS | P1 | 12 | 64,990 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 6 | 36,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 42 | 166,260 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

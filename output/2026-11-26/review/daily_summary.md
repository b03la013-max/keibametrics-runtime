# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 33／PAPER PFS 118.2%／正式推薦 PFS 41.3%
- 第一失敗：{'PREDICTION_ROLE_W': 10, 'CAPITAL_EFFICIENCY': 16, 'PREDICTION_ROLE_P2': 5, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 6 | 38.4 | 31.9 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 5} |
| NGY | 5 | 282.9 | 100.3 | {'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 1, 'NONE': 2, 'CAPITAL_EFFICIENCY': 1} |
| SON | 12 | 160.3 | 35.4 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 1} |
| URW | 10 | 51.7 | 24.7 | {'PREDICTION_ROLE_P2': 3, 'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 4} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 38／正式試行 38・発走前送信 38／本人確認 0
2. 計算完走：Full29 38／Signed FINAL 38／KRS5000 38／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 118.2%／正式推薦 41.3%／実購入なし
5. Learning：RESULT署名検証 33／学習状態保存 33／前Raceの学習状態を結合した正式Race 38（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 33 | 33.3% | 72.7% | 33.3% | 9.1% | 21.2% | 6.1% | 39.4% | 1.7 |
| 正式推薦 | 33 | 33.3% | 69.7% | 69.7% | 75.8% | 100.0% | 69.7% | 54.5% | 1.61 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.3%（無作為9.2%、差+24.1）／P2 平均1.0頭 的中9.1%（無作為9.2%、差-0.1）／P3 平均1.0頭 的中21.2%（無作為9.2%、差+12.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中69.7%（無作為27.7%、差+42.0）／P2 平均6.0頭 的中75.8%（無作為55.3%、差+20.4）／P3 平均11.03頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.09/40（選択性補正込み）・能力順位 14.81/20（33R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.69/40（選択性補正込み）・能力順位 14.27/20（33R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,800円（6.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）14R・着順まで的中 0R／的中 16R のうち的中赤字 6R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 31.7%（同じ33Rの実績 118.2%）／券種別 EXACTA 13点 PFS 34.6%／TRIFECTA 24点 PFS 0.0%／TRIO 173点 PFS 131.1%／WIDE 56点 PFS 152.7%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 18R PFS 121.3% 的中赤字 1/6／SOLID 14R PFS 89.6% 的中赤字 5/9／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 32R：実績 105.9% − ミラー 38.2% = Δ 67.7pt（95%区間 -6.1〜160.9、最高1R除き 37.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 76,200円（38.5%）／保護層の資金比率 0.0（33R）／組だけ的中（三連単は外れ）11R・着順まで的中 7R／的中 21R のうち的中赤字 19R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 24.6%（同じ33Rの実績 41.3%）／券種別 EXACTA 495点 PFS 44.0%／TRIFECTA 825点 PFS 24.2%／TRIO 660点 PFS 60.8%／荒れ度（発走前・1番人気オッズ）MID 18R PFS 47.8% 的中赤字 9/11／SOLID 14R PFS 35.1% 的中赤字 9/9／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 32R：実績 42.2% − ミラー 44.5% = Δ -2.3pt（95%区間 -21.7〜19.2、最高1R除き -5.7pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、33R×3券種）：購入 14／予算で削除 0／予想で除外 27／未生成・券種なし 58／役割馬の行き先 {'PURCHASED': 99}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、33R×3券種）：購入 42／予算で削除 13／予想で除外 30／未生成・券種なし 14／役割馬の行き先 {'PURCHASED': 243, 'BUDGET_COMPRESSED': 121}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 11R／W外 22R、2着が P2 役割 0R）：STATIC 0/11（平均4.36位）／STYLE_COND 2/11（平均4.09位） 救済2・喪失0／MARKET_COND 2/10（平均3.6位） 救済2・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 23R／W外 10R、2着が P2 役割 18R）：STATIC 18/23（平均3.83位）／STYLE_COND 18/23（平均3.7位） 救済0・喪失0／MARKET_COND 20/22（平均2.91位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 19 | 56,540 | RECURRING |
| P1:ROLE_W_MISS | P1 | 10 | 52,990 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 33 | 128,540 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 45／PAPER PFS 109.8%／正式推薦 PFS 41.2%
- 第一失敗：{'PREDICTION_ROLE_W': 13, 'CAPITAL_EFFICIENCY': 23, 'PREDICTION_ROLE_P2': 6, 'NONE': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 97.7 | 35.4 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 9} |
| NGY | 11 | 150.4 | 72.6 | {'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 2, 'NONE': 3, 'CAPITAL_EFFICIENCY': 3} |
| SON | 12 | 160.3 | 35.4 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 1} |
| URW | 12 | 45.0 | 22.9 | {'PREDICTION_ROLE_P2': 3, 'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 5} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 48／正式試行 48・発走前送信 48／本人確認 0
2. 計算完走：Full29 48／Signed FINAL 48／KRS5000 48／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 109.8%／正式推薦 41.2%／実購入なし
5. Learning：RESULT署名検証 46／学習状態保存 46／前Raceの学習状態を結合した正式Race 48（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 45 | 35.6% | 66.7% | 35.6% | 13.3% | 20.0% | 8.9% | 33.3% | 1.62 |
| 正式推薦 | 45 | 31.1% | 71.1% | 71.1% | 77.8% | 100.0% | 71.1% | 53.3% | 1.53 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中35.6%（無作為9.3%、差+26.2）／P2 平均1.0頭 的中13.3%（無作為9.3%、差+4.0）／P3 平均1.0頭 的中20.0%（無作為9.3%、差+10.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中71.1%（無作為27.9%、差+43.2）／P2 平均6.0頭 的中77.8%（無作為55.9%、差+21.9）／P3 平均10.98頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.13/40（選択性補正込み）・能力順位 14.44/20（45R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.62/40（選択性補正込み）・能力順位 14.02/20（45R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（6.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）15R・着順まで的中 1R／的中 21R のうち的中赤字 8R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 47.5%（同じ45Rの実績 109.8%）／券種別 EXACTA 18点 PFS 50.0%／TRIFECTA 32点 PFS 31.6%／TRIO 233点 PFS 100.1%／WIDE 76点 PFS 188.6%／WIN 3点 PFS 53.3%／荒れ度（発走前・1番人気オッズ）MID 26R PFS 110.9% 的中赤字 2/9／SOLID 18R PFS 88.5% 的中赤字 6/11／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 44R：実績 100.5% − ミラー 44.2% = Δ 56.4pt（95%区間 -4.2〜129.1、最高1R除き 34.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 104,100円（38.6%）／保護層の資金比率 0.0（45R）／組だけ的中（三連単は外れ）13R・着順まで的中 11R／的中 29R のうち的中赤字 26R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 43.9%（同じ45Rの実績 41.2%）／券種別 EXACTA 675点 PFS 51.1%／TRIFECTA 1125点 PFS 27.4%／TRIO 900点 PFS 50.9%／荒れ度（発走前・1番人気オッズ）MID 26R PFS 44.2% 的中赤字 15/17／SOLID 18R PFS 38.3% 的中赤字 10/11／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 44R：実績 41.8% − ミラー 56.5% = Δ -14.7pt（95%区間 -48.6〜12.5、最高1R除き -17.4pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、45R×3券種）：購入 17／予算で削除 0／予想で除外 39／未生成・券種なし 79／役割馬の行き先 {'PURCHASED': 135}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、45R×3券種）：購入 60／予算で削除 17／予想で除外 38／未生成・券種なし 20／役割馬の行き先 {'PURCHASED': 330, 'BUDGET_COMPRESSED': 164}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 16R／W外 29R、2着が P2 役割 2R）：STATIC 2/16（平均4.0位）／STYLE_COND 4/16（平均3.75位） 救済2・喪失0／MARKET_COND 4/15（平均3.07位） 救済3・喪失1
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 32R／W外 13R、2着が P2 役割 26R）：STATIC 27/32（平均3.91位）／STYLE_COND 27/32（平均3.78位） 救済0・喪失0／MARKET_COND 29/31（平均2.9位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 26 | 79,390 | RECURRING |
| P1:ROLE_W_MISS | P1 | 13 | 70,990 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 6 | 36,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 45 | 175,390 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

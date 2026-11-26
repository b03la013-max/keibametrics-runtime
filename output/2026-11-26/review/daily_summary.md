# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 24／PAPER PFS 114.5%／正式推薦 PFS 37.3%
- 第一失敗：{'PREDICTION_ROLE_W': 7, 'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_P2': 3, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 4 | 40.3 | 27.0 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 3} |
| NGY | 3 | 26.7 | 59.8 | {'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 1, 'NONE': 1} |
| SON | 10 | 188.0 | 38.5 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 1} |
| URW | 7 | 80.2 | 31.7 | {'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 4} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 31／正式試行 31・発走前送信 31／本人確認 0
2. 計算完走：Full29 31／Signed FINAL 31／KRS5000 31／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 114.5%／正式推薦 37.3%／実購入なし
5. Learning：RESULT署名検証 24／学習状態保存 24／前Raceの学習状態を結合した正式Race 31（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 24 | 37.5% | 70.8% | 37.5% | 12.5% | 20.8% | 0.0% | 41.7% | 1.67 |
| 正式推薦 | 24 | 29.2% | 70.8% | 70.8% | 79.2% | 100.0% | 70.8% | 50.0% | 1.62 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中37.5%（無作為9.3%、差+28.2）／P2 平均1.0頭 的中12.5%（無作為9.3%、差+3.2）／P3 平均1.0頭 的中20.8%（無作為9.3%、差+11.6）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中70.8%（無作為27.8%、差+43.0）／P2 平均6.0頭 的中79.2%（無作為55.6%、差+23.6）／P3 平均10.96頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.5/40（選択性補正込み）・能力順位 14.64/20（24R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.85/40（選択性補正込み）・能力順位 14.2/20（24R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（3.2%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）11R・着順まで的中 0R／的中 12R のうち的中赤字 4R／損益分岐の倍率 平均 7.8倍／同じ点数を無作為に選んだ場合の期待PFS 36.9%（同じ24Rの実績 114.5%）／券種別 EXACTA 7点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 128点 PFS 108.1%／WIDE 42点 PFS 180.2%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 13R PFS 69.9% 的中赤字 1/4／SOLID 10R PFS 129.0% 的中赤字 3/7／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 23R：実績 96.5% − ミラー 32.1% = Δ 64.4pt（95%区間 1.7〜148.0、最高1R除き 36.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 56,000円（38.9%）／保護層の資金比率 0.0（24R）／組だけ的中（三連単は外れ）7R・着順まで的中 5R／的中 15R のうち的中赤字 14R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 28.5%（同じ24Rの実績 37.3%）／券種別 EXACTA 360点 PFS 35.8%／TRIFECTA 600点 PFS 22.2%／TRIO 480点 PFS 57.1%／荒れ度（発走前・1番人気オッズ）MID 13R PFS 31.9% 的中赤字 5/6／SOLID 10R PFS 46.7% 的中赤字 8/8／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 23R：実績 38.3% − ミラー 35.4% = Δ 2.9pt（95%区間 -17.3〜25.9、最高1R除き -3.9pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、24R×3券種）：購入 10／予算で削除 0／予想で除外 18／未生成・券種なし 44／役割馬の行き先 {'PURCHASED': 72}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、24R×3券種）：購入 31／予算で削除 10／予想で除外 20／未生成・券種なし 11／役割馬の行き先 {'PURCHASED': 175, 'BUDGET_COMPRESSED': 88}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 9R／W外 15R、2着が P2 役割 0R）：STATIC 0/9（平均4.33位）／STYLE_COND 1/9（平均4.11位） 救済1・喪失0／MARKET_COND 0/8（平均4.25位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 17R／W外 7R、2着が P2 役割 14R）：STATIC 14/17（平均3.71位）／STYLE_COND 14/17（平均3.47位） 救済0・喪失0／MARKET_COND 14/16（平均3.06位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 14 | 41,110 | RECURRING |
| P1:ROLE_W_MISS | P1 | 7 | 38,860 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 24 | 95,110 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

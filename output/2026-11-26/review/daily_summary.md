# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 25／PAPER PFS 107.7%／正式推薦 PFS 35.8%
- 第一失敗：{'PREDICTION_ROLE_W': 7, 'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_P2': 4, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 4 | 40.3 | 27.0 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 3} |
| NGY | 3 | 26.7 | 59.8 | {'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 1, 'NONE': 1} |
| SON | 10 | 188.0 | 38.5 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 1} |
| URW | 8 | 68.5 | 27.7 | {'PREDICTION_ROLE_P2': 2, 'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 4} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 32／正式試行 32・発走前送信 32／本人確認 0
2. 計算完走：Full29 32／Signed FINAL 32／KRS5000 32／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 107.7%／正式推薦 35.8%／実購入なし
5. Learning：RESULT署名検証 25／学習状態保存 25／前Raceの学習状態を結合した正式Race 32（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 25 | 40.0% | 72.0% | 40.0% | 12.0% | 20.0% | 4.0% | 40.0% | 1.68 |
| 正式推薦 | 25 | 32.0% | 72.0% | 72.0% | 76.0% | 100.0% | 72.0% | 48.0% | 1.6 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中40.0%（無作為9.3%、差+30.7）／P2 平均1.0頭 的中12.0%（無作為9.3%、差+2.7）／P3 平均1.0頭 的中20.0%（無作為9.3%、差+10.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中72.0%（無作為27.8%、差+44.2）／P2 平均6.0頭 的中76.0%（無作為55.5%、差+20.5）／P3 平均10.96頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.72/40（選択性補正込み）・能力順位 14.65/20（25R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.81/40（選択性補正込み）・能力順位 14.16/20（25R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,200円（5.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）11R・着順まで的中 0R／的中 13R のうち的中赤字 5R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 34.4%（同じ25Rの実績 107.7%）／券種別 EXACTA 10点 PFS 45.0%／TRIFECTA 16点 PFS 0.0%／TRIO 133点 PFS 104.1%／WIDE 42点 PFS 180.2%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 13R PFS 69.9% 的中赤字 1/4／SOLID 11R PFS 112.4% 的中赤字 4/8／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 24R：実績 90.9% − ミラー 48.8% = Δ 42.1pt（95%区間 -28.4〜128.4、最高1R除き 15.7pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 58,300円（38.9%）／保護層の資金比率 0.0（25R）／組だけ的中（三連単は外れ）7R・着順まで的中 5R／的中 15R のうち的中赤字 14R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 27.5%（同じ25Rの実績 35.8%）／券種別 EXACTA 375点 PFS 34.4%／TRIFECTA 625点 PFS 21.3%／TRIO 500点 PFS 54.8%／荒れ度（発走前・1番人気オッズ）MID 13R PFS 31.9% 的中赤字 5/6／SOLID 11R PFS 42.4% 的中赤字 8/8／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 24R：実績 36.7% − ミラー 36.6% = Δ 0.1pt（95%区間 -19.7〜22.2、最高1R除き -6.5pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、25R×3券種）：購入 11／予算で削除 0／予想で除外 20／未生成・券種なし 44／役割馬の行き先 {'PURCHASED': 75}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、25R×3券種）：購入 31／予算で削除 10／予想で除外 22／未生成・券種なし 12／役割馬の行き先 {'PURCHASED': 182, 'BUDGET_COMPRESSED': 92}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 10R／W外 15R、2着が P2 役割 0R）：STATIC 0/10（平均4.1位）／STYLE_COND 2/10（平均3.8位） 救済2・喪失0／MARKET_COND 1/9（平均3.89位） 救済1・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 18R／W外 7R、2着が P2 役割 14R）：STATIC 14/18（平均3.89位）／STYLE_COND 14/18（平均3.67位） 救済0・喪失0／MARKET_COND 15/17（平均2.94位） 救済2・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 14 | 41,110 | RECURRING |
| P1:ROLE_W_MISS | P1 | 7 | 38,860 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 4 | 24,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 25 | 101,110 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

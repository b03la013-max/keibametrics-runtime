# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 19／PAPER PFS 102.5%／正式推薦 PFS 31.0%
- 第一失敗：{'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 11, 'PREDICTION_ROLE_P2': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 2 | 11.9 | 17.0 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 1} |
| NGY | 2 | 40.0 | 0.0 | {'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 1} |
| SON | 9 | 163.8 | 37.0 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1} |
| URW | 6 | 57.2 | 37.0 | {'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 4} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 26／正式試行 26・発走前送信 26／本人確認 0
2. 計算完走：Full29 26／Signed FINAL 26／KRS5000 26／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 102.5%／正式推薦 31.0%／実購入なし
5. Learning：RESULT署名検証 19／学習状態保存 19／前Raceの学習状態を結合した正式Race 26（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 19 | 42.1% | 73.7% | 42.1% | 5.3% | 21.1% | 0.0% | 31.6% | 1.58 |
| 正式推薦 | 19 | 31.6% | 73.7% | 73.7% | 73.7% | 100.0% | 73.7% | 42.1% | 1.53 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中42.1%（無作為9.1%、差+33.0）／P2 平均1.0頭 的中5.3%（無作為9.1%、差-3.8）／P3 平均1.0頭 的中21.1%（無作為9.1%、差+12.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中73.7%（無作為27.2%、差+46.5）／P2 平均6.0頭 的中73.7%（無作為54.4%、差+19.3）／P3 平均11.16頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.53/40（選択性補正込み）・能力順位 14.32/20（19R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.96/40（選択性補正込み）・能力順位 14.09/20（19R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（4.1%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）7R・着順まで的中 0R／的中 8R のうち的中赤字 2R／損益分岐の倍率 平均 7.8倍／同じ点数を無作為に選んだ場合の期待PFS 40.0%（同じ19Rの実績 102.5%）／券種別 EXACTA 7点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 99点 PFS 84.8%／WIDE 32点 PFS 211.6%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 9R PFS 17.8% 的中赤字 0/1／SOLID 9R PFS 134.3% 的中赤字 2/6／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 18R：実績 78.9% − ミラー 32.1% = Δ 46.9pt（95%区間 -15.2〜137.9、最高1R除き 9.8pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 44,300円（38.9%）／保護層の資金比率 0.0（19R）／組だけ的中（三連単は外れ）4R・着順まで的中 4R／的中 11R のうち的中赤字 11R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 28.4%（同じ19Rの実績 31.0%）／券種別 EXACTA 285点 PFS 33.9%／TRIFECTA 475点 PFS 23.8%／TRIO 380点 PFS 37.7%／荒れ度（発走前・1番人気オッズ）MID 9R PFS 14.1% 的中赤字 3/3／SOLID 9R PFS 49.8% 的中赤字 7/7／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 18R：実績 32.0% − ミラー 33.9% = Δ -2.0pt（95%区間 -23.6〜20.2、最高1R除き -7.2pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、19R×3券種）：購入 6／予算で削除 0／予想で除外 17／未生成・券種なし 34／役割馬の行き先 {'PURCHASED': 57}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、19R×3券種）：購入 23／予算で削除 8／予想で除外 16／未生成・券種なし 10／役割馬の行き先 {'PURCHASED': 139, 'BUDGET_COMPRESSED': 73}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 8R／W外 11R、2着が P2 役割 0R）：STATIC 0/8（平均4.5位）／STYLE_COND 1/8（平均4.25位） 救済1・喪失0／MARKET_COND 0/7（平均4.14位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 14R／W外 5R、2着が P2 役割 11R）：STATIC 11/14（平均3.71位）／STYLE_COND 11/14（平均3.57位） 救済0・喪失0／MARKET_COND 11/13（平均2.92位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 11 | 30,680 | RECURRING |
| P1:ROLE_W_MISS | P1 | 5 | 30,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 19 | 78,680 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

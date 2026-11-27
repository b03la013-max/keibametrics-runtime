# 地方版 2026-11-27 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 24／PAPER PFS 54.5%／正式推薦 PFS 50.1%
- 第一失敗：{'PREDICTION_ROLE_W': 10, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 10, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 4 | 8.2 | 90.5 | {'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 1} |
| SON | 11 | 90.5 | 19.2 | {'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 1} |
| URW | 9 | 31.0 | 69.9 | {'PREDICTION_ROLE_W': 5, 'NONE': 2, 'CAPITAL_EFFICIENCY': 2} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 28／正式試行 28・発走前送信 28／本人確認 0
2. 計算完走：Full29 28／Signed FINAL 28／KRS5000 28／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 54.5%／正式推薦 50.1%／実購入なし
5. Learning：RESULT署名検証 24／学習状態保存 24／前Raceの学習状態を結合した正式Race 28（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '295/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 24 | 41.7% | 66.7% | 41.7% | 29.2% | 20.8% | 0.0% | 29.2% | 1.71 |
| 正式推薦 | 24 | 41.7% | 58.3% | 58.3% | 91.7% | 100.0% | 83.3% | 37.5% | 1.58 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中41.7%（無作為9.3%、差+32.4）／P2 平均1.0頭 的中29.2%（無作為9.3%、差+19.9）／P3 平均1.0頭 的中20.8%（無作為9.3%、差+11.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中58.3%（無作為27.9%、差+30.5）／P2 平均6.0頭 的中91.7%（無作為55.7%、差+36.0）／P3 平均11.0頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.88/40（選択性補正込み）・能力順位 15.0/20（24R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.82/40（選択性補正込み）・能力順位 14.85/20（24R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）7R・着順まで的中 0R／的中 10R のうち的中赤字 6R／損益分岐の倍率 平均 7.0倍／同じ点数を無作為に選んだ場合の期待PFS 43.8%（同じ24Rの実績 54.5%）／券種別 TRIO 120点 PFS 43.8%／WIDE 48点 PFS 81.0%／荒れ度（発走前・1番人気オッズ）MID 14R PFS 75.8% 的中赤字 1/5／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 8R PFS 21.1% 的中赤字 4/4／UNKNOWN 1R PFS 77.1% 的中赤字 1/1／市場ミラーとの差 23R：実績 53.5% − ミラー 36.8% = Δ 16.7pt（95%区間 -31.4〜69.1、最高1R除き -1.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（24R）／組だけ的中（三連単は外れ）6R・着順まで的中 9R／的中 15R のうち的中赤字 12R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 28.0%（同じ24Rの実績 50.1%）／券種別 EXACTA 423点 PFS 49.2%／TRIFECTA 1017点 PFS 50.5%／荒れ度（発走前・1番人気オッズ）MID 14R PFS 57.3% 的中赤字 8/10／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 8R PFS 46.8% 的中赤字 3/4／UNKNOWN 1R PFS 25.5% 的中赤字 1/1／市場ミラーとの差 23R：実績 51.2% − ミラー 34.5% = Δ 16.7pt（95%区間 -23.2〜65.0、最高1R除き 0.3pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、24R×3券種）：購入 7／予算で削除 0／予想で除外 17／未生成・券種なし 48／役割馬の行き先 {'PURCHASED': 72}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、24R×3券種）：購入 23／予算で削除 5／予想で除外 20／未生成・券種なし 24／役割馬の行き先 {'BUDGET_COMPRESSED': 80, 'PURCHASED': 184}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 10R／W外 14R、2着が P2 役割 4R）：STATIC 4/10（平均2.1位）／STYLE_COND 5/10（平均2.0位） 救済1・喪失0／MARKET_COND 2/9（平均2.44位） 救済1・喪失2
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 14R／W外 10R、2着が P2 役割 12R）：STATIC 12/14（平均3.14位）／STYLE_COND 12/14（平均3.0位） 救済0・喪失0／MARKET_COND 13/13（平均2.69位） 救済2・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 12 | 49,250 | RECURRING |
| P1:ROLE_W_MISS | P1 | 10 | 49,500 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 24 | 103,250 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

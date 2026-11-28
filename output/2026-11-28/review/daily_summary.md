# 地方版 2026-11-28 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 5／PAPER PFS 15.6%／正式推薦 PFS 8.8%
- 第一失敗：{'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 1, 'PREDICTION_ROLE_W': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KOC | 2 | 40.0 | 15.2 | {'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 1} |
| SAG | 3 | 0.0 | 4.6 | {'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 2} |

## 日次自律監査

1. 配送：管理 24R／PAPER発走前送信 9／正式試行 9・発走前送信 9／本人確認 0
2. 計算完走：Full29 9／Signed FINAL 9／KRS5000 9／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 15.6%／正式推薦 8.8%／実購入なし
5. Learning：RESULT署名検証 5／学習状態保存 5／前Raceの学習状態を結合した正式Race 9（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '100R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '300R到達', 'C17-P2-ZAI-PLACE': '300R到達', 'C18-W-PLUS-FAVORITE': '300R到達', 'C19-W-PLUS-TOP2-POP': '300R到達', 'C20-P2-PLUS-TOP3-POP': '300R到達', 'C21-BVI-L-R2-TERTILE': '300R到達'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 5 | 60.0% | 80.0% | 60.0% | 0.0% | 40.0% | 0.0% | 20.0% | 1.8 |
| 正式推薦 | 5 | 60.0% | 80.0% | 80.0% | 40.0% | 100.0% | 100.0% | 20.0% | 2.0 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中60.0%（無作為9.9%、差+50.1）／P2 平均1.0頭 的中0.0%（無作為9.9%、差-9.9）／P3 平均1.0頭 的中40.0%（無作為9.9%、差+30.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中80.0%（無作為29.6%、差+50.4）／P2 平均6.0頭 的中40.0%（無作為59.2%、差-19.2）／P3 平均10.2頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 19.2/40（選択性補正込み）・能力順位 15.07/20（5R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.11/40（選択性補正込み）・能力順位 14.11/20（5R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）1R・着順まで的中 0R／的中 2R のうち的中赤字 2R／損益分岐の倍率 平均 7.2倍／同じ点数を無作為に選んだ場合の期待PFS 15.8%（同じ5Rの実績 15.6%）／券種別 EXACTA 2点 PFS 0.0%／TRIO 25点 PFS 10.8%／WIDE 8点 PFS 36.2%／WIN 1点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）SOLID 5R PFS 15.6% 的中赤字 2/2／市場ミラーとの差 5R：実績 15.6% − ミラー 123.1% = Δ -107.5pt（95%区間 -266.7〜12.9、最高1R除き -148.6pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（5R）／組だけ的中（三連単は外れ）1R・着順まで的中 1R／的中 2R のうち的中赤字 2R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 10.1%（同じ5Rの実績 8.8%）／券種別 EXACTA 87点 PFS 22.6%／TRIFECTA 213点 PFS 3.2%／荒れ度（発走前・1番人気オッズ）SOLID 5R PFS 8.8% 的中赤字 2/2／市場ミラーとの差 5R：実績 8.8% − ミラー 65.7% = Δ -56.8pt（95%区間 -140.9〜6.8、最高1R除き -78.7pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、5R×3券種）：購入 1／予算で削除 0／予想で除外 5／未生成・券種なし 9／役割馬の行き先 {'PURCHASED': 15}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、5R×3券種）：購入 3／予算で削除 2／予想で除外 6／未生成・券種なし 4／役割馬の行き先 {'PURCHASED': 38, 'BUDGET_COMPRESSED': 13}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 3R／W外 2R、2着が P2 役割 0R）：STATIC 0/3（平均5.67位）／STYLE_COND 0/3（平均6.0位） 救済0・喪失0／MARKET_COND 0/3（平均3.0位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 4R／W外 1R、2着が P2 役割 1R）：STATIC 2/4（平均5.75位）／STYLE_COND 2/4（平均6.0位） 救済0・喪失0／MARKET_COND 4/4（平均3.25位） 救済2・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 2 | 9,350 | SINGLE_OR_FEW (過大評価しない) |
| P1:ROLE_W_MISS | P1 | 1 | 5,180 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 5 | 27,350 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

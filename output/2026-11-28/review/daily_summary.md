# 地方版 2026-11-28 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 9／PAPER PFS 31.1%／正式推薦 PFS 56.2%
- 第一失敗：{'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 3, 'NONE': 1, 'PREDICTION_ROLE_W': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KOC | 4 | 19.3 | 114.7 | {'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 1, 'NONE': 1, 'PREDICTION_ROLE_W': 1} |
| SAG | 5 | 38.7 | 9.5 | {'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2} |

## 日次自律監査

1. 配送：管理 24R／PAPER発走前送信 13／正式試行 13・発走前送信 13／本人確認 0
2. 計算完走：Full29 13／Signed FINAL 13／KRS5000 13／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 31.1%／正式推薦 56.2%／実購入なし
5. Learning：RESULT署名検証 9／学習状態保存 9／前Raceの学習状態を結合した正式Race 13（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '100R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '300R到達', 'C17-P2-ZAI-PLACE': '300R到達', 'C18-W-PLUS-FAVORITE': '300R到達', 'C19-W-PLUS-TOP2-POP': '300R到達', 'C20-P2-PLUS-TOP3-POP': '300R到達', 'C21-BVI-L-R2-TERTILE': '300R到達'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 9 | 44.4% | 88.9% | 44.4% | 0.0% | 33.3% | 11.1% | 22.2% | 1.89 |
| 正式推薦 | 9 | 55.6% | 77.8% | 77.8% | 66.7% | 100.0% | 88.9% | 22.2% | 1.78 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中44.4%（無作為10.6%、差+33.9）／P2 平均1.0頭 的中0.0%（無作為10.6%、差-10.6）／P3 平均1.0頭 的中33.3%（無作為10.6%、差+22.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中77.8%（無作為31.7%、差+46.1）／P2 平均6.0頭 的中66.7%（無作為63.4%、差+3.2）／P3 平均9.67頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.78/40（選択性補正込み）・能力順位 14.76/20（9R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.57/40（選択性補正込み）・能力順位 14.42/20（9R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（8.1%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）2R・着順まで的中 0R／的中 4R のうち的中赤字 4R／損益分岐の倍率 平均 8.2倍／同じ点数を無作為に選んだ場合の期待PFS 22.1%（同じ9Rの実績 31.1%）／券種別 EXACTA 7点 PFS 187.1%／TRIFECTA 8点 PFS 0.0%／TRIO 45点 PFS 12.0%／WIDE 12点 PFS 37.5%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 2R PFS 0.0% 的中赤字 0/0／SOLID 7R PFS 39.0% 的中赤字 4/4／市場ミラーとの差 9R：実績 31.1% − ミラー 71.1% = Δ -40.0pt（95%区間 -156.6〜33.2、最高1R除き -73.6pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（9R）／組だけ的中（三連単は外れ）3R・着順まで的中 2R／的中 5R のうち的中赤字 4R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 13.9%（同じ9Rの実績 56.2%）／券種別 EXACTA 156点 PFS 41.0%／TRIFECTA 384点 PFS 62.4%／荒れ度（発走前・1番人気オッズ）MID 2R PFS 214.1% 的中赤字 0/1／SOLID 7R PFS 11.1% 的中赤字 4/4／市場ミラーとの差 9R：実績 56.2% − ミラー 54.4% = Δ 1.8pt（95%区間 -85.2〜118.4、最高1R除き -46.5pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、9R×3券種）：購入 3／予算で削除 0／予想で除外 10／未生成・券種なし 14／役割馬の行き先 {'PURCHASED': 27}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、9R×3券種）：購入 7／予算で削除 4／予想で除外 8／未生成・券種なし 8／役割馬の行き先 {'PURCHASED': 67, 'BUDGET_COMPRESSED': 20}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 4R／W外 5R、2着が P2 役割 0R）：STATIC 0/4（平均4.75位）／STYLE_COND 0/4（平均5.25位） 救済0・喪失0／MARKET_COND 0/4（平均4.0位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 7R／W外 2R、2着が P2 役割 4R）：STATIC 5/7（平均4.57位）／STYLE_COND 5/7（平均4.71位） 救済0・喪失0／MARKET_COND 6/7（平均3.14位） 救済2・喪失1

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 4 | 19,330 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 2 | 11,180 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 9 | 43,330 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-27 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 34／PAPER PFS 56.2%／正式推薦 PFS 40.6%
- 第一失敗：{'PREDICTION_ROLE_W': 14, 'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 13, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 10 | 9.6 | 53.9 | {'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 4} |
| SON | 12 | 96.7 | 17.6 | {'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 1} |
| URW | 12 | 56.2 | 52.4 | {'PREDICTION_ROLE_W': 6, 'NONE': 2, 'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_P2': 2} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 35／正式試行 35・発走前送信 35／本人確認 0
2. 計算完走：Full29 35／Signed FINAL 35／KRS5000 35／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 56.2%／正式推薦 40.6%／実購入なし
5. Learning：RESULT署名検証 34／学習状態保存 34／前Raceの学習状態を結合した正式Race 35（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '300R到達', 'C17-P2-ZAI-PLACE': '300R到達', 'C18-W-PLUS-FAVORITE': '300R到達', 'C19-W-PLUS-TOP2-POP': '300R到達', 'C20-P2-PLUS-TOP3-POP': '300R到達', 'C21-BVI-L-R2-TERTILE': '295/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 34 | 38.2% | 67.6% | 38.2% | 23.5% | 20.6% | 0.0% | 26.5% | 1.68 |
| 正式推薦 | 34 | 38.2% | 58.8% | 58.8% | 82.4% | 100.0% | 79.4% | 32.4% | 1.56 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中38.2%（無作為9.0%、差+29.3）／P2 平均1.0頭 的中23.5%（無作為9.0%、差+14.6）／P3 平均1.0頭 的中20.6%（無作為9.0%、差+11.6）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中58.8%（無作為26.9%、差+31.9）／P2 平均6.0頭 的中82.4%（無作為53.8%、差+28.5）／P3 平均11.35頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.68/40（選択性補正込み）・能力順位 14.96/20（34R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.62/40（選択性補正込み）・能力順位 14.73/20（34R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）9R・着順まで的中 0R／的中 14R のうち的中赤字 7R／損益分岐の倍率 平均 7.2倍／同じ点数を無作為に選んだ場合の期待PFS 46.8%（同じ34Rの実績 56.2%）／券種別 EXACTA 2点 PFS 0.0%／TRIO 176点 PFS 37.2%／WIDE 66点 PFS 109.5%／WIN 1点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 20R PFS 79.3% 的中赤字 1/8／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 12R PFS 19.4% 的中赤字 5/5／UNKNOWN 1R PFS 77.1% 的中赤字 1/1／市場ミラーとの差 33R：実績 55.6% − ミラー 83.7% = Δ -28.1pt（95%区間 -106.4〜41.9、最高1R除き -41.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（34R）／組だけ的中（三連単は外れ）8R・着順まで的中 11R／的中 19R のうち的中赤字 16R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 40.6%（同じ34Rの実績 40.6%）／券種別 EXACTA 594点 PFS 43.2%／TRIFECTA 1446点 PFS 39.5%／荒れ度（発走前・1番人気オッズ）MID 20R PFS 45.9% 的中赤字 10/12／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 12R PFS 36.4% 的中赤字 5/6／UNKNOWN 1R PFS 25.5% 的中赤字 1/1／市場ミラーとの差 33R：実績 41.0% − ミラー 38.1% = Δ 2.9pt（95%区間 -28.3〜40.6、最高1R除き -8.8pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、34R×3券種）：購入 9／予算で削除 0／予想で除外 26／未生成・券種なし 67／役割馬の行き先 {'PURCHASED': 102}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、34R×3券種）：購入 29／予算で削除 9／予想で除外 32／未生成・券種なし 32／役割馬の行き先 {'BUDGET_COMPRESSED': 126, 'PURCHASED': 260}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 13R／W外 21R、2着が P2 役割 4R）：STATIC 4/13（平均2.77位）／STYLE_COND 5/13（平均2.62位） 救済1・喪失0／MARKET_COND 3/12（平均2.58位） 救済2・喪失2
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 20R／W外 14R、2着が P2 役割 15R）：STATIC 15/20（平均3.9位）／STYLE_COND 16/20（平均3.75位） 救済1・喪失0／MARKET_COND 18/19（平均2.79位） 救済4・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 16 | 62,610 | RECURRING |
| P1:ROLE_W_MISS | P1 | 14 | 70,830 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 34 | 152,610 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

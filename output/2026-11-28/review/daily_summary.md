# 地方版 2026-11-28 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 15／PAPER PFS 32.5%／正式推薦 PFS 99.1%
- 第一失敗：{'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 3, 'NONE': 3, 'PREDICTION_ROLE_W': 5}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KOC | 7 | 41.2 | 195.7 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1, 'NONE': 3, 'PREDICTION_ROLE_W': 1} |
| SAG | 8 | 26.0 | 14.6 | {'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2} |

## 日次自律監査

1. 配送：管理 24R／PAPER発走前送信 19／正式試行 19・発走前送信 19／本人確認 0
2. 計算完走：Full29 19／Signed FINAL 19／KRS5000 19／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 32.5%／正式推薦 99.1%／実購入なし
5. Learning：RESULT署名検証 15／学習状態保存 15／前Raceの学習状態を結合した正式Race 19（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '100R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '300R到達', 'C17-P2-ZAI-PLACE': '300R到達', 'C18-W-PLUS-FAVORITE': '300R到達', 'C19-W-PLUS-TOP2-POP': '300R到達', 'C20-P2-PLUS-TOP3-POP': '300R到達', 'C21-BVI-L-R2-TERTILE': '300R到達'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 15 | 40.0% | 80.0% | 40.0% | 0.0% | 26.7% | 6.7% | 20.0% | 1.87 |
| 正式推薦 | 15 | 40.0% | 66.7% | 66.7% | 73.3% | 100.0% | 86.7% | 33.3% | 1.73 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中40.0%（無作為10.4%、差+29.6）／P2 平均1.0頭 的中0.0%（無作為10.4%、差-10.4）／P3 平均1.0頭 的中26.7%（無作為10.4%、差+16.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.7%（無作為31.1%、差+35.6）／P2 平均6.0頭 的中73.3%（無作為62.2%、差+11.1）／P3 平均9.8頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.73/40（選択性補正込み）・能力順位 14.68/20（15R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.32/40（選択性補正込み）・能力順位 14.53/20（15R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（5.1%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）3R・着順まで的中 0R／的中 6R のうち的中赤字 5R／損益分岐の倍率 平均 7.8倍／同じ点数を無作為に選んだ場合の期待PFS 34.0%（同じ15Rの実績 32.5%）／券種別 EXACTA 9点 PFS 145.6%／TRIFECTA 8点 PFS 0.0%／TRIO 75点 PFS 21.1%／WIDE 22点 PFS 41.4%／WIN 3点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 4R PFS 9.0% 的中赤字 1/1／OPEN 1R PFS 177.1% 的中赤字 0/1／SOLID 10R PFS 28.4% 的中赤字 4/4／市場ミラーとの差 15R：実績 32.5% − ミラー 57.9% = Δ -25.5pt（95%区間 -96.5〜34.1、最高1R除き -42.5pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（15R）／組だけ的中（三連単は外れ）5R・着順まで的中 5R／的中 9R のうち的中赤字 6R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 33.4%（同じ15Rの実績 99.1%）／券種別 EXACTA 261点 PFS 74.2%／TRIFECTA 639点 PFS 109.3%／荒れ度（発走前・1番人気オッズ）MID 4R PFS 283.5% 的中赤字 0/2／OPEN 1R PFS 205.5% 的中赤字 0/1／SOLID 10R PFS 14.7% 的中赤字 6/6／市場ミラーとの差 15R：実績 99.1% − ミラー 47.1% = Δ 52.0pt（95%区間 -34.1〜151.7、最高1R除き 16.9pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、15R×3券種）：購入 4／予算で削除 0／予想で除外 16／未生成・券種なし 25／役割馬の行き先 {'PURCHASED': 45}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、15R×3券種）：購入 13／予算で削除 4／予想で除外 14／未生成・券種なし 14／役割馬の行き先 {'PURCHASED': 111, 'BUDGET_COMPRESSED': 36}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 6R／W外 9R、2着が P2 役割 0R）：STATIC 0/6（平均4.5位）／STYLE_COND 0/6（平均4.67位） 救済0・喪失0／MARKET_COND 1/6（平均3.17位） 救済1・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 10R／W外 5R、2着が P2 役割 6R）：STATIC 8/10（平均4.4位）／STYLE_COND 8/10（平均4.5位） 救済0・喪失0／MARKET_COND 9/10（平均3.2位） 救済2・喪失1

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 6 | 27,160 | RECURRING |
| P1:ROLE_W_MISS | P1 | 5 | 25,010 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 4 | 24,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 15 | 63,160 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

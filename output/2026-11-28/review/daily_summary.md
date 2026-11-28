# 地方版 2026-11-28 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 17／PAPER PFS 26.8%／正式推薦 PFS 87.5%
- 第一失敗：{'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 3, 'NONE': 3, 'PREDICTION_ROLE_W': 6}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KOC | 8 | 31.2 | 171.2 | {'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 1, 'NONE': 3, 'PREDICTION_ROLE_W': 1} |
| SAG | 9 | 22.9 | 13.0 | {'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2} |

## 日次自律監査

1. 配送：管理 24R／PAPER発走前送信 21／正式試行 21・発走前送信 21／本人確認 0
2. 計算完走：Full29 21／Signed FINAL 21／KRS5000 21／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 26.8%／正式推薦 87.5%／実購入なし
5. Learning：RESULT署名検証 17／学習状態保存 17／前Raceの学習状態を結合した正式Race 21（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '100R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '300R到達', 'C17-P2-ZAI-PLACE': '300R到達', 'C18-W-PLUS-FAVORITE': '300R到達', 'C19-W-PLUS-TOP2-POP': '300R到達', 'C20-P2-PLUS-TOP3-POP': '300R到達', 'C21-BVI-L-R2-TERTILE': '300R到達'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 17 | 41.2% | 76.5% | 41.2% | 0.0% | 23.5% | 11.8% | 17.6% | 1.71 |
| 正式推薦 | 17 | 41.2% | 64.7% | 64.7% | 64.7% | 100.0% | 88.2% | 29.4% | 1.59 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中41.2%（無作為10.2%、差+31.0）／P2 平均1.0頭 的中0.0%（無作為10.2%、差-10.2）／P3 平均1.0頭 的中23.5%（無作為10.2%、差+13.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中64.7%（無作為30.7%、差+34.0）／P2 平均6.0頭 的中64.7%（無作為61.3%、差+3.4）／P3 平均9.94頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.82/40（選択性補正込み）・能力順位 14.3/20（17R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.86/40（選択性補正込み）・能力順位 14.02/20（17R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,200円（8.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）3R・着順まで的中 0R／的中 6R のうち的中赤字 5R／損益分岐の倍率 平均 8.4倍／同じ点数を無作為に選んだ場合の期待PFS 35.1%（同じ17Rの実績 26.8%）／券種別 EXACTA 12点 PFS 109.2%／TRIFECTA 16点 PFS 0.0%／TRIO 87点 PFS 18.2%／WIDE 24点 PFS 37.9%／WIN 3点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 5R PFS 6.8% 的中赤字 1/1／OPEN 1R PFS 177.1% 的中赤字 0/1／SOLID 11R PFS 23.7% 的中赤字 4/4／市場ミラーとの差 17R：実績 26.8% − ミラー 47.7% = Δ -21.0pt（95%区間 -80.8〜25.9、最高1R除き -34.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（17R）／組だけ的中（三連単は外れ）5R・着順まで的中 5R／的中 9R のうち的中赤字 6R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 32.5%（同じ17Rの実績 87.5%）／券種別 EXACTA 297点 PFS 65.2%／TRIFECTA 723点 PFS 96.6%／荒れ度（発走前・1番人気オッズ）MID 5R PFS 226.8% 的中赤字 0/2／OPEN 1R PFS 205.5% 的中赤字 0/1／SOLID 11R PFS 13.4% 的中赤字 6/6／市場ミラーとの差 17R：実績 87.5% − ミラー 46.7% = Δ 40.8pt（95%区間 -36.3〜133.2、最高1R除き 9.4pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、17R×3券種）：購入 4／予算で削除 0／予想で除外 20／未生成・券種なし 27／役割馬の行き先 {'PURCHASED': 51}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、17R×3券種）：購入 13／予算で削除 5／予想で除外 18／未生成・券種なし 15／役割馬の行き先 {'PURCHASED': 127, 'BUDGET_COMPRESSED': 42}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 7R／W外 10R、2着が P2 役割 0R）：STATIC 0/7（平均4.43位）／STYLE_COND 0/7（平均4.57位） 救済0・喪失0／MARKET_COND 1/7（平均3.29位） 救済1・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 11R／W外 6R、2着が P2 役割 6R）：STATIC 8/11（平均4.91位）／STYLE_COND 8/11（平均5.0位） 救済0・喪失0／MARKET_COND 10/11（平均3.27位） 救済3・喪失1

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 6 | 31,010 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 6 | 27,160 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 17 | 75,160 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

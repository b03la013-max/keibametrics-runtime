# 地方版 2026-11-28 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 18／PAPER PFS 25.5%／正式推薦 PFS 82.6%
- 第一失敗：{'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 3, 'NONE': 3, 'PREDICTION_ROLE_W': 7}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KOC | 9 | 28.2 | 152.2 | {'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 1, 'NONE': 3, 'PREDICTION_ROLE_W': 2} |
| SAG | 9 | 22.9 | 13.0 | {'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2} |

## 日次自律監査

1. 配送：管理 24R／PAPER発走前送信 22／正式試行 22・発走前送信 22／本人確認 0
2. 計算完走：Full29 22／Signed FINAL 22／KRS5000 22／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 25.5%／正式推薦 82.6%／実購入なし
5. Learning：RESULT署名検証 18／学習状態保存 18／前Raceの学習状態を結合した正式Race 22（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '100R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '300R到達', 'C17-P2-ZAI-PLACE': '300R到達', 'C18-W-PLUS-FAVORITE': '300R到達', 'C19-W-PLUS-TOP2-POP': '300R到達', 'C20-P2-PLUS-TOP3-POP': '300R到達', 'C21-BVI-L-R2-TERTILE': '300R到達'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 18 | 38.9% | 72.2% | 38.9% | 0.0% | 27.8% | 11.1% | 16.7% | 1.72 |
| 正式推薦 | 18 | 38.9% | 61.1% | 61.1% | 66.7% | 100.0% | 83.3% | 27.8% | 1.61 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中38.9%（無作為10.1%、差+28.8）／P2 平均1.0頭 的中0.0%（無作為10.1%、差-10.1）／P3 平均1.0頭 的中27.8%（無作為10.1%、差+17.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中61.1%（無作為30.3%、差+30.8）／P2 平均6.0頭 的中66.7%（無作為60.7%、差+6.0）／P3 平均10.06頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.94/40（選択性補正込み）・能力順位 14.34/20（18R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.85/40（選択性補正込み）・能力順位 14.19/20（18R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,200円（8.1%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）3R・着順まで的中 0R／的中 6R のうち的中赤字 5R／損益分岐の倍率 平均 8.3倍／同じ点数を無作為に選んだ場合の期待PFS 34.3%（同じ18Rの実績 25.5%）／券種別 EXACTA 12点 PFS 109.2%／TRIFECTA 16点 PFS 0.0%／TRIO 92点 PFS 17.2%／WIDE 26点 PFS 35.0%／WIN 3点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 5.8% 的中赤字 1/1／OPEN 1R PFS 177.1% 的中赤字 0/1／SOLID 11R PFS 23.7% 的中赤字 4/4／市場ミラーとの差 18R：実績 25.5% − ミラー 45.5% = Δ -20.0pt（95%区間 -79.3〜25.7、最高1R除き -32.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（18R）／組だけ的中（三連単は外れ）6R・着順まで的中 5R／的中 9R のうち的中赤字 6R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 32.0%（同じ18Rの実績 82.6%）／券種別 EXACTA 315点 PFS 61.5%／TRIFECTA 765点 PFS 91.3%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 189.0% 的中赤字 0/2／OPEN 1R PFS 205.5% 的中赤字 0/1／SOLID 11R PFS 13.4% 的中赤字 6/6／市場ミラーとの差 18R：実績 82.6% − ミラー 71.2% = Δ 11.4pt（95%区間 -80.6〜117.8、最高1R除き -19.9pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、18R×3券種）：購入 4／予算で削除 0／予想で除外 21／未生成・券種なし 29／役割馬の行き先 {'PURCHASED': 54}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、18R×3券種）：購入 13／予算で削除 5／予想で除外 20／未生成・券種なし 16／役割馬の行き先 {'PURCHASED': 134, 'BUDGET_COMPRESSED': 47}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 7R／W外 11R、2着が P2 役割 0R）：STATIC 0/7（平均4.43位）／STYLE_COND 0/7（平均4.57位） 救済0・喪失0／MARKET_COND 1/7（平均3.29位） 救済1・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 11R／W外 7R、2着が P2 役割 6R）：STATIC 8/11（平均4.91位）／STYLE_COND 8/11（平均5.0位） 救済0・喪失0／MARKET_COND 10/11（平均3.27位） 救済3・喪失1

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 7 | 37,010 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 6 | 27,160 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 18 | 81,160 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

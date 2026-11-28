# 地方版 2026-11-28 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 20／PAPER PFS 23.3%／正式推薦 PFS 173.8%
- 第一失敗：{'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 3, 'NONE': 4, 'PREDICTION_ROLE_W': 8}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KOC | 10 | 25.8 | 335.9 | {'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 1, 'NONE': 4, 'PREDICTION_ROLE_W': 2} |
| SAG | 10 | 21.0 | 11.7 | {'PREDICTION_ROLE_W': 6, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2} |

## 日次自律監査

1. 配送：管理 24R／PAPER発走前送信 24／正式試行 24・発走前送信 24／本人確認 0
2. 計算完走：Full29 24／Signed FINAL 24／KRS5000 24／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 23.3%／正式推薦 173.8%／実購入なし
5. Learning：RESULT署名検証 20／学習状態保存 20／前Raceの学習状態を結合した正式Race 24（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '100R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '300R到達', 'C17-P2-ZAI-PLACE': '300R到達', 'C18-W-PLUS-FAVORITE': '300R到達', 'C19-W-PLUS-TOP2-POP': '300R到達', 'C20-P2-PLUS-TOP3-POP': '300R到達', 'C21-BVI-L-R2-TERTILE': '300R到達'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 20 | 40.0% | 70.0% | 40.0% | 0.0% | 25.0% | 10.0% | 15.0% | 1.65 |
| 正式推薦 | 20 | 40.0% | 60.0% | 60.0% | 70.0% | 100.0% | 85.0% | 30.0% | 1.55 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中40.0%（無作為9.9%、差+30.1）／P2 平均1.0頭 的中0.0%（無作為9.9%、差-9.9）／P3 平均1.0頭 的中25.0%（無作為9.9%、差+15.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.0%（無作為29.8%、差+30.2）／P2 平均6.0頭 的中70.0%（無作為59.6%、差+10.4）／P3 平均10.25頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.5/40（選択性補正込み）・能力順位 14.07/20（20R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.06/40（選択性補正込み）・能力順位 14.15/20（20R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,200円（7.4%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）3R・着順まで的中 0R／的中 6R のうち的中赤字 5R／損益分岐の倍率 平均 8.2倍／同じ点数を無作為に選んだ場合の期待PFS 35.5%（同じ20Rの実績 23.3%）／券種別 EXACTA 12点 PFS 109.2%／TRIFECTA 16点 PFS 0.0%／TRIO 102点 PFS 15.5%／WIDE 30点 PFS 30.3%／WIN 3点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 5.8% 的中赤字 1/1／OPEN 1R PFS 177.1% 的中赤字 0/1／SOLID 13R PFS 20.7% 的中赤字 4/4／市場ミラーとの差 20R：実績 23.3% − ミラー 48.4% = Δ -25.1pt（95%区間 -79.5〜19.8、最高1R除き -36.7pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（20R）／組だけ的中（三連単は外れ）6R・着順まで的中 6R／的中 10R のうち的中赤字 6R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 33.7%（同じ20Rの実績 173.8%）／券種別 EXACTA 357点 PFS 71.2%／TRIFECTA 843点 PFS 217.3%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 189.0% 的中赤字 0/2／OPEN 1R PFS 205.5% 的中赤字 0/1／SOLID 13R PFS 164.4% 的中赤字 6/7／市場ミラーとの差 20R：実績 173.8% − ミラー 64.5% = Δ 109.3pt（95%区間 -58.6〜352.1、最高1R除き 10.3pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、20R×3券種）：購入 4／予算で削除 0／予想で除外 23／未生成・券種なし 33／役割馬の行き先 {'PURCHASED': 60}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、20R×3券種）：購入 15／予算で削除 5／予想で除外 22／未生成・券種なし 18／役割馬の行き先 {'PURCHASED': 151, 'BUDGET_COMPRESSED': 54}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 8R／W外 12R、2着が P2 役割 0R）：STATIC 0/8（平均4.12位）／STYLE_COND 1/8（平均4.12位） 救済1・喪失0／MARKET_COND 1/8（平均3.25位） 救済1・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 12R／W外 8R、2着が P2 役割 7R）：STATIC 9/12（平均4.58位）／STYLE_COND 9/12（平均4.67位） 救済0・喪失0／MARKET_COND 11/12（平均3.25位） 救済3・喪失1

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 8 | 43,010 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 6 | 27,160 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 20 | 87,160 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

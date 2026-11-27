# 地方版 2026-11-27 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 19／PAPER PFS 58.0%／正式推薦 PFS 48.6%
- 第一失敗：{'PREDICTION_ROLE_W': 10, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_P2': 1, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 2 | 0.0 | 150.0 | {'PREDICTION_ROLE_W': 2} |
| SON | 10 | 99.6 | 16.0 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 1} |
| URW | 7 | 15.3 | 66.1 | {'PREDICTION_ROLE_W': 5, 'NONE': 1, 'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 24／正式試行 24・発走前送信 24／本人確認 0
2. 計算完走：Full29 24／Signed FINAL 24／KRS5000 24／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 58.0%／正式推薦 48.6%／実購入なし
5. Learning：RESULT署名検証 19／学習状態保存 19／前Raceの学習状態を結合した正式Race 24（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '295/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 19 | 31.6% | 57.9% | 31.6% | 31.6% | 21.1% | 0.0% | 31.6% | 1.63 |
| 正式推薦 | 19 | 31.6% | 47.4% | 47.4% | 94.7% | 100.0% | 78.9% | 31.6% | 1.47 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中31.6%（無作為9.5%、差+22.0）／P2 平均1.0頭 的中31.6%（無作為9.5%、差+22.0）／P3 平均1.0頭 的中21.1%（無作為9.5%、差+11.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中47.4%（無作為28.6%、差+18.8）／P2 平均6.0頭 的中94.7%（無作為57.2%、差+37.5）／P3 平均10.74頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.42/40（選択性補正込み）・能力順位 14.49/20（19R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.62/40（選択性補正込み）・能力順位 14.38/20（19R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 7R のうち的中赤字 4R／損益分岐の倍率 平均 7.0倍／同じ点数を無作為に選んだ場合の期待PFS 51.9%（同じ19Rの実績 58.0%）／券種別 TRIO 95点 PFS 42.7%／WIDE 38点 PFS 96.3%／荒れ度（発走前・1番人気オッズ）MID 11R PFS 80.9% 的中赤字 1/4／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 6R PFS 22.6% 的中赤字 2/2／UNKNOWN 1R PFS 77.1% 的中赤字 1/1／市場ミラーとの差 18R：実績 57.0% − ミラー 39.0% = Δ 17.9pt（95%区間 -39.7〜83.9、最高1R除き -5.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（19R）／組だけ的中（三連単は外れ）6R・着順まで的中 6R／的中 11R のうち的中赤字 9R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 34.0%（同じ19Rの実績 48.6%）／券種別 EXACTA 342点 PFS 48.3%／TRIFECTA 798点 PFS 48.7%／荒れ度（発走前・1番人気オッズ）MID 11R PFS 53.2% 的中赤字 6/7／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 6R PFS 52.1% 的中赤字 2/3／UNKNOWN 1R PFS 25.5% 的中赤字 1/1／市場ミラーとの差 18R：実績 49.9% − ミラー 35.8% = Δ 14.1pt（95%区間 -33.4〜74.5、最高1R除き -7.3pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、19R×3券種）：購入 6／予算で削除 0／予想で除外 13／未生成・券種なし 38／役割馬の行き先 {'PURCHASED': 57}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、19R×3券種）：購入 16／予算で削除 4／予想で除外 18／未生成・券種なし 19／役割馬の行き先 {'BUDGET_COMPRESSED': 61, 'PURCHASED': 143}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 6R／W外 13R、2着が P2 役割 3R）：STATIC 3/6（平均1.5位）／STYLE_COND 4/6（平均1.5位） 救済1・喪失0／MARKET_COND 2/5（平均2.0位） 救済1・喪失1
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 9R／W外 10R、2着が P2 役割 8R）：STATIC 8/9（平均3.0位）／STYLE_COND 8/9（平均2.89位） 救済0・喪失0／MARKET_COND 8/8（平均2.25位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 10 | 49,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 9 | 39,330 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 19 | 87,330 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

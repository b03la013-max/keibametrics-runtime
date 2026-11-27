# 地方版 2026-11-27 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 18／PAPER PFS 38.4%／正式推薦 PFS 51.3%
- 第一失敗：{'PREDICTION_ROLE_W': 9, 'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_P2': 1, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 2 | 0.0 | 150.0 | {'PREDICTION_ROLE_W': 2} |
| SON | 9 | 64.9 | 17.8 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1} |
| URW | 7 | 15.3 | 66.1 | {'PREDICTION_ROLE_W': 5, 'NONE': 1, 'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 23／正式試行 23・発走前送信 23／本人確認 0
2. 計算完走：Full29 23／Signed FINAL 23／KRS5000 23／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 38.4%／正式推薦 51.3%／実購入なし
5. Learning：RESULT署名検証 18／学習状態保存 18／前Raceの学習状態を結合した正式Race 23（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '295/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 18 | 33.3% | 61.1% | 33.3% | 33.3% | 22.2% | 0.0% | 33.3% | 1.67 |
| 正式推薦 | 18 | 33.3% | 50.0% | 50.0% | 94.4% | 100.0% | 83.3% | 33.3% | 1.5 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.3%（無作為9.6%、差+23.8）／P2 平均1.0頭 的中33.3%（無作為9.6%、差+23.8）／P3 平均1.0頭 的中22.2%（無作為9.6%、差+12.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中50.0%（無作為28.7%、差+21.3）／P2 平均6.0頭 的中94.4%（無作為57.4%、差+37.1）／P3 平均10.72頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.94/40（選択性補正込み）・能力順位 14.7/20（18R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.9/40（選択性補正込み）・能力順位 14.55/20（18R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 6R のうち的中赤字 4R／損益分岐の倍率 平均 7.0倍／同じ点数を無作為に選んだ場合の期待PFS 44.2%（同じ18Rの実績 38.4%）／券種別 TRIO 90点 PFS 45.1%／WIDE 36点 PFS 21.7%／荒れ度（発走前・1番人気オッズ）MID 10R PFS 47.9% 的中赤字 1/3／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 6R PFS 22.6% 的中赤字 2/2／UNKNOWN 1R PFS 77.1% 的中赤字 1/1／市場ミラーとの差 17R：実績 36.1% − ミラー 41.3% = Δ -5.2pt（95%区間 -50.1〜45.0、最高1R除き -24.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（18R）／組だけ的中（三連単は外れ）6R・着順まで的中 6R／的中 11R のうち的中赤字 9R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 30.1%（同じ18Rの実績 51.3%）／券種別 EXACTA 324点 PFS 51.0%／TRIFECTA 756点 PFS 51.4%／荒れ度（発走前・1番人気オッズ）MID 10R PFS 58.5% 的中赤字 6/7／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 6R PFS 52.1% 的中赤字 2/3／UNKNOWN 1R PFS 25.5% 的中赤字 1/1／市場ミラーとの差 17R：実績 52.8% − ミラー 33.9% = Δ 18.9pt（95%区間 -29.7〜84.9、最高1R除き -3.5pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、18R×3券種）：購入 6／予算で削除 0／予想で除外 12／未生成・券種なし 36／役割馬の行き先 {'PURCHASED': 54}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、18R×3券種）：購入 16／予算で削除 4／予想で除外 16／未生成・券種なし 18／役割馬の行き先 {'BUDGET_COMPRESSED': 57, 'PURCHASED': 136}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 6R／W外 12R、2着が P2 役割 3R）：STATIC 3/6（平均1.5位）／STYLE_COND 4/6（平均1.5位） 救済1・喪失0／MARKET_COND 2/5（平均2.0位） 救済1・喪失1
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 9R／W外 9R、2着が P2 役割 8R）：STATIC 8/9（平均3.0位）／STYLE_COND 8/9（平均2.89位） 救済0・喪失0／MARKET_COND 8/8（平均2.25位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 9 | 43,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 9 | 39,330 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 18 | 81,330 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

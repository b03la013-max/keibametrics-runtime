# 地方版 2026-11-27 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 21／PAPER PFS 61.4%／正式推薦 PFS 50.8%
- 第一失敗：{'PREDICTION_ROLE_W': 10, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 7, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 3 | 5.2 | 100.0 | {'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1} |
| SON | 10 | 99.6 | 16.0 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 1} |
| URW | 8 | 34.8 | 75.9 | {'PREDICTION_ROLE_W': 5, 'NONE': 2, 'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 26／正式試行 26・発走前送信 26／本人確認 0
2. 計算完走：Full29 26／Signed FINAL 26／KRS5000 26／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 61.4%／正式推薦 50.8%／実購入なし
5. Learning：RESULT署名検証 21／学習状態保存 21／前Raceの学習状態を結合した正式Race 26（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '295/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 21 | 38.1% | 61.9% | 38.1% | 28.6% | 19.0% | 0.0% | 33.3% | 1.67 |
| 正式推薦 | 21 | 38.1% | 52.4% | 52.4% | 90.5% | 100.0% | 81.0% | 33.3% | 1.57 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中38.1%（無作為9.4%、差+28.7）／P2 平均1.0頭 的中28.6%（無作為9.4%、差+19.1）／P3 平均1.0頭 的中19.0%（無作為9.4%、差+9.6）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中52.4%（無作為28.3%、差+24.1）／P2 平均6.0頭 的中90.5%（無作為56.5%、差+33.9）／P3 平均10.86頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.0/40（選択性補正込み）・能力順位 14.75/20（21R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.02/40（選択性補正込み）・能力順位 14.62/20（21R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）7R・着順まで的中 0R／的中 9R のうち的中赤字 5R／損益分岐の倍率 平均 7.0倍／同じ点数を無作為に選んだ場合の期待PFS 47.6%（同じ21Rの実績 61.4%）／券種別 TRIO 105点 PFS 50.1%／WIDE 42点 PFS 89.8%／荒れ度（発走前・1番人気オッズ）MID 12R PFS 88.5% 的中赤字 1/5／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 7R PFS 21.6% 的中赤字 3/3／UNKNOWN 1R PFS 77.1% 的中赤字 1/1／市場ミラーとの差 20R：実績 60.6% − ミラー 38.6% = Δ 22.0pt（95%区間 -32.6〜84.3、最高1R除き 1.5pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（21R）／組だけ的中（三連単は外れ）6R・着順まで的中 7R／的中 12R のうち的中赤字 9R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 31.2%（同じ21Rの実績 50.8%）／券種別 EXACTA 375点 PFS 48.7%／TRIFECTA 885点 PFS 51.8%／荒れ度（発走前・1番人気オッズ）MID 12R PFS 60.8% 的中赤字 6/8／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 7R PFS 44.6% 的中赤字 2/3／UNKNOWN 1R PFS 25.5% 的中赤字 1/1／市場ミラーとの差 20R：実績 52.1% − ミラー 35.8% = Δ 16.3pt（95%区間 -28.4〜70.2、最高1R除き -2.8pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、21R×3券種）：購入 7／予算で削除 0／予想で除外 14／未生成・券種なし 42／役割馬の行き先 {'PURCHASED': 63}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、21R×3券種）：購入 18／予算で削除 4／予想で除外 20／未生成・券種なし 21／役割馬の行き先 {'BUDGET_COMPRESSED': 68, 'PURCHASED': 160}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 8R／W外 13R、2着が P2 役割 3R）：STATIC 3/8（平均2.0位）／STYLE_COND 4/8（平均2.0位） 救済1・喪失0／MARKET_COND 2/7（平均2.57位） 救済1・喪失1
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 11R／W外 10R、2着が P2 役割 9R）：STATIC 9/11（平均3.27位）／STYLE_COND 9/11（平均3.09位） 救済0・喪失0／MARKET_COND 10/10（平均2.6位） 救済2・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 10 | 49,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 9 | 39,330 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 21 | 93,330 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

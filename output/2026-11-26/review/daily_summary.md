# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 7／PAPER PFS 214.9%／正式推薦 PFS 19.0%
- 第一失敗：{'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| SON | 5 | 300.9 | 26.6 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 1} |
| URW | 2 | 0.0 | 0.0 | {'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 1} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 11／正式試行 11・発走前送信 11／本人確認 0
2. 計算完走：Full29 11／Signed FINAL 11／KRS5000 11／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 214.9%／正式推薦 19.0%／実購入なし
5. Learning：RESULT署名検証 7／学習状態保存 7／前Raceの学習状態を結合した正式Race 11（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 7 | 71.4% | 100.0% | 71.4% | 0.0% | 14.3% | 0.0% | 28.6% | 1.71 |
| 正式推薦 | 7 | 28.6% | 71.4% | 71.4% | 57.1% | 100.0% | 71.4% | 28.6% | 1.14 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中71.4%（無作為8.8%、差+62.6）／P2 平均1.0頭 的中0.0%（無作為8.8%、差-8.8）／P3 平均1.0頭 的中14.3%（無作為8.8%、差+5.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中71.4%（無作為26.5%、差+45.0）／P2 平均6.0頭 的中57.1%（無作為53.0%、差+4.2）／P3 平均11.43頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 18.29/40（選択性補正込み）・能力順位 15.22/20（7R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.24/40（選択性補正込み）・能力順位 13.43/20（7R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）2R・着順まで的中 0R／的中 3R のうち的中赤字 0R／損益分岐の倍率 平均 7.0倍／同じ点数を無作為に選んだ場合の期待PFS 70.7%（同じ7Rの実績 214.9%）／券種別 TRIO 35点 PFS 160.9%／WIDE 14点 PFS 350.0%／荒れ度（発走前・1番人気オッズ）MID 5R PFS 34.0% 的中赤字 0/1／SOLID 1R PFS 757.1% 的中赤字 0/1／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 6R：実績 154.5% − ミラー 4.8% = Δ 149.8pt（95%区間 0.0〜402.1、最高1R除き 28.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 16,500円（39.3%）／保護層の資金比率 0.0（7R）／組だけ的中（三連単は外れ）2R・着順まで的中 0R／的中 3R のうち的中赤字 3R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 32.4%（同じ7Rの実績 19.0%）／券種別 EXACTA 105点 PFS 22.5%／TRIFECTA 175点 PFS 0.0%／TRIO 140点 PFS 40.2%／荒れ度（発走前・1番人気オッズ）MID 5R PFS 4.8% 的中赤字 1/1／SOLID 1R PFS 95.7% 的中赤字 1/1／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 6R：実績 20.0% − ミラー 25.0% = Δ -5.1pt（95%区間 -39.9〜34.4、最高1R除き -21.5pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、7R×3券種）：購入 2／予算で削除 0／予想で除外 5／未生成・券種なし 14／役割馬の行き先 {'PURCHASED': 21}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、7R×3券種）：購入 5／予算で削除 4／予想で除外 8／未生成・券種なし 4／役割馬の行き先 {'PURCHASED': 50, 'BUDGET_COMPRESSED': 30}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 5R／W外 2R、2着が P2 役割 0R）：STATIC 0/5（平均4.6位）／STYLE_COND 1/5（平均4.2位） 救済1・喪失0／MARKET_COND 0/4（平均5.0位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 5R／W外 2R、2着が P2 役割 3R）：STATIC 3/5（平均5.4位）／STYLE_COND 3/5（平均5.0位） 救済0・喪失0／MARKET_COND 3/4（平均4.0位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 3 | 10,010 | RECURRING |
| P1:ROLE_W_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 7 | 34,010 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

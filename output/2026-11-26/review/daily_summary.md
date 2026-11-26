# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 5／PAPER PFS 300.9%／正式推薦 PFS 26.6%
- 第一失敗：{'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| SON | 4 | 376.1 | 33.3 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 1} |
| URW | 1 | 0.0 | 0.0 | {'PREDICTION_ROLE_P2': 1} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 9／正式試行 9・発走前送信 9／本人確認 0
2. 計算完走：Full29 9／Signed FINAL 9／KRS5000 9／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 300.9%／正式推薦 26.6%／実購入なし
5. Learning：RESULT署名検証 5／学習状態保存 5／前Raceの学習状態を結合した正式Race 9（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 5 | 80.0% | 100.0% | 80.0% | 0.0% | 20.0% | 0.0% | 40.0% | 1.6 |
| 正式推薦 | 5 | 40.0% | 80.0% | 80.0% | 60.0% | 100.0% | 80.0% | 40.0% | 1.4 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中80.0%（無作為9.2%、差+70.8）／P2 平均1.0頭 的中0.0%（無作為9.2%、差-9.2）／P3 平均1.0頭 的中20.0%（無作為9.2%、差+10.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中80.0%（無作為27.5%、差+52.5）／P2 平均6.0頭 的中60.0%（無作為54.9%、差+5.1）／P3 平均11.0頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 18.8/40（選択性補正込み）・能力順位 15.07/20（5R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 17.02/40（選択性補正込み）・能力順位 13.97/20（5R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）2R・着順まで的中 0R／的中 3R のうち的中赤字 0R／損益分岐の倍率 平均 7.0倍／同じ点数を無作為に選んだ場合の期待PFS 72.1%（同じ5Rの実績 300.9%）／券種別 TRIO 25点 PFS 225.2%／WIDE 10点 PFS 490.0%／荒れ度（発走前・1番人気オッズ）MID 3R PFS 56.7% 的中赤字 0/1／SOLID 1R PFS 757.1% 的中赤字 0/1／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 4R：実績 231.8% − ミラー 7.1% = Δ 224.6pt（95%区間 0.0〜567.9、最高1R除き 47.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 12,000円（40.0%）／保護層の資金比率 0.0（5R）／組だけ的中（三連単は外れ）2R・着順まで的中 0R／的中 3R のうち的中赤字 3R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 26.1%（同じ5Rの実績 26.6%）／券種別 EXACTA 75点 PFS 31.5%／TRIFECTA 125点 PFS 0.0%／TRIO 100点 PFS 56.3%／荒れ度（発走前・1番人気オッズ）MID 3R PFS 8.1% 的中赤字 1/1／SOLID 1R PFS 95.7% 的中赤字 1/1／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 4R：実績 30.0% − ミラー 19.7% = Δ 10.2pt（95%区間 -27.5〜55.3、最高1R除き -12.1pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、5R×3券種）：購入 2／予算で削除 0／予想で除外 3／未生成・券種なし 10／役割馬の行き先 {'PURCHASED': 15}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、5R×3券種）：購入 5／予算で削除 4／予想で除外 4／未生成・券種なし 2／役割馬の行き先 {'PURCHASED': 35, 'BUDGET_COMPRESSED': 20}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 4R／W外 1R、2着が P2 役割 0R）：STATIC 0/4（平均5.25位）／STYLE_COND 0/4（平均5.0位） 救済0・喪失0／MARKET_COND 0/3（平均4.33位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 4R／W外 1R、2着が P2 役割 3R）：STATIC 3/4（平均4.75位）／STYLE_COND 3/4（平均4.5位） 救済0・喪失0／MARKET_COND 3/3（平均3.0位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 3 | 10,010 | RECURRING |
| P1:ROLE_W_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P1:ROLE_P2_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 5 | 22,010 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

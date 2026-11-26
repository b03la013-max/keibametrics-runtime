# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 9／PAPER PFS 158.6%／正式推薦 PFS 26.4%
- 第一失敗：{'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| SON | 6 | 206.5 | 36.2 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 1} |
| URW | 3 | 42.4 | 6.8 | {'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 13／正式試行 13・発走前送信 13／本人確認 0
2. 計算完走：Full29 13／Signed FINAL 13／KRS5000 13／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 158.6%／正式推薦 26.4%／実購入なし
5. Learning：RESULT署名検証 9／学習状態保存 9／前Raceの学習状態を結合した正式Race 13（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 9 | 55.6% | 100.0% | 55.6% | 0.0% | 22.2% | 0.0% | 33.3% | 1.89 |
| 正式推薦 | 9 | 33.3% | 77.8% | 77.8% | 66.7% | 100.0% | 77.8% | 44.4% | 1.56 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中55.6%（無作為8.8%、差+46.8）／P2 平均1.0頭 的中0.0%（無作為8.8%、差-8.8）／P3 平均1.0頭 的中22.2%（無作為8.8%、差+13.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中77.8%（無作為26.4%、差+51.4）／P2 平均6.0頭 的中66.7%（無作為52.8%、差+13.9）／P3 平均11.44頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 18.56/40（選択性補正込み）・能力順位 15.78/20（9R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 17.72/40（選択性補正込み）・能力順位 14.49/20（9R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（8.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）4R・着順まで的中 0R／的中 4R のうち的中赤字 0R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 49.7%（同じ9Rの実績 158.6%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 45点 PFS 142.0%／WIDE 16点 PFS 314.4%／荒れ度（発走前・1番人気オッズ）MID 5R PFS 34.0% 的中赤字 0/1／SOLID 3R PFS 206.3% 的中赤字 0/2／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 8R：実績 113.5% − ミラー 16.8% = Δ 96.8pt（95%区間 0.0〜301.6、最高1R除き 17.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 20,900円（38.7%）／保護層の資金比率 0.0（9R）／組だけ的中（三連単は外れ）3R・着順まで的中 1R／的中 5R のうち的中赤字 5R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 26.0%（同じ9Rの実績 26.4%）／券種別 EXACTA 135点 PFS 28.0%／TRIFECTA 225点 PFS 16.7%／TRIO 180点 PFS 37.3%／荒れ度（発走前・1番人気オッズ）MID 5R PFS 4.8% 的中赤字 1/1／SOLID 3R PFS 66.7% 的中赤字 3/3／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 8R：実績 28.0% − ミラー 31.8% = Δ -3.8pt（95%区間 -29.7〜25.8、最高1R除き -15.4pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、9R×3券種）：購入 3／予算で削除 0／予想で除外 8／未生成・券種なし 16／役割馬の行き先 {'PURCHASED': 27}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、9R×3券種）：購入 10／予算で削除 5／予想で除外 8／未生成・券種なし 4／役割馬の行き先 {'PURCHASED': 66, 'BUDGET_COMPRESSED': 37}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 5R／W外 4R、2着が P2 役割 0R）：STATIC 0/5（平均4.6位）／STYLE_COND 1/5（平均4.2位） 救済1・喪失0／MARKET_COND 0/4（平均5.0位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 7R／W外 2R、2着が P2 役割 5R）：STATIC 5/7（平均4.29位）／STYLE_COND 5/7（平均3.86位） 救済0・喪失0／MARKET_COND 5/6（平均3.0位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 5 | 15,750 | RECURRING |
| P1:ROLE_W_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 9 | 39,750 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

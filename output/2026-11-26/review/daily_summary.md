# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 22／PAPER PFS 120.8%／正式推薦 PFS 30.0%
- 第一失敗：{'PREDICTION_ROLE_W': 7, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_P2': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 3 | 30.4 | 17.4 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 2} |
| NGY | 2 | 40.0 | 0.0 | {'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 1} |
| SON | 10 | 188.0 | 38.5 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 1} |
| URW | 7 | 80.2 | 31.7 | {'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 4} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 30／正式試行 30・発走前送信 30／本人確認 0
2. 計算完走：Full29 30／Signed FINAL 30／KRS5000 30／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 120.8%／正式推薦 30.0%／実購入なし
5. Learning：RESULT署名検証 22／学習状態保存 22／前Raceの学習状態を結合した正式Race 30（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 22 | 40.9% | 68.2% | 40.9% | 13.6% | 22.7% | 0.0% | 40.9% | 1.64 |
| 正式推薦 | 22 | 31.8% | 68.2% | 68.2% | 77.3% | 100.0% | 68.2% | 45.5% | 1.59 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中40.9%（無作為9.2%、差+31.7）／P2 平均1.0頭 的中13.6%（無作為9.2%、差+4.4）／P3 平均1.0頭 的中22.7%（無作為9.2%、差+13.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中68.2%（無作為27.7%、差+40.5）／P2 平均6.0頭 的中77.3%（無作為55.3%、差+21.9）／P3 平均11.0頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.09/40（選択性補正込み）・能力順位 14.56/20（22R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.44/40（選択性補正込み）・能力順位 14.09/20（22R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（3.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）10R・着順まで的中 0R／的中 11R のうち的中赤字 3R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 37.5%（同じ22Rの実績 120.8%）／券種別 EXACTA 7点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 118点 PFS 114.4%／WIDE 38点 PFS 194.7%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 11R PFS 75.4% 的中赤字 0/3／SOLID 10R PFS 129.0% 的中赤字 3/7／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 21R：実績 101.6% − ミラー 31.7% = Δ 69.9pt（95%区間 3.6〜154.9、最高1R除き 39.6pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 51,300円（38.9%）／保護層の資金比率 0.0（22R）／組だけ的中（三連単は外れ）6R・着順まで的中 4R／的中 13R のうち的中赤字 13R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 29.8%（同じ22Rの実績 30.0%）／券種別 EXACTA 330点 PFS 31.1%／TRIFECTA 550点 PFS 20.6%／TRIO 440点 PFS 40.9%／荒れ度（発走前・1番人気オッズ）MID 11R PFS 16.3% 的中赤字 4/4／SOLID 10R PFS 46.7% 的中赤字 8/8／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 21R：実績 30.8% − ミラー 34.8% = Δ -4.1pt（95%区間 -22.7〜15.3、最高1R除き -8.6pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、22R×3券種）：購入 9／予算で削除 0／予想で除外 17／未生成・券種なし 40／役割馬の行き先 {'PURCHASED': 66}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、22R×3券種）：購入 26／予算で削除 9／予想で除外 20／未生成・券種なし 11／役割馬の行き先 {'PURCHASED': 161, 'BUDGET_COMPRESSED': 81}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 9R／W外 13R、2着が P2 役割 0R）：STATIC 0/9（平均4.33位）／STYLE_COND 1/9（平均4.11位） 救済1・喪失0／MARKET_COND 0/8（平均4.25位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 15R／W外 7R、2着が P2 役割 12R）：STATIC 12/15（平均3.73位）／STYLE_COND 12/15（平均3.53位） 救済0・喪失0／MARKET_COND 12/14（平均3.07位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 13 | 38,440 | RECURRING |
| P1:ROLE_W_MISS | P1 | 7 | 38,860 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 22 | 92,440 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

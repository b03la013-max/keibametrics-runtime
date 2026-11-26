# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 23／PAPER PFS 116.1%／正式推薦 PFS 36.5%
- 第一失敗：{'PREDICTION_ROLE_W': 7, 'CAPITAL_EFFICIENCY': 12, 'PREDICTION_ROLE_P2': 3, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 3 | 30.4 | 17.4 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 2} |
| NGY | 3 | 26.7 | 59.8 | {'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 1, 'NONE': 1} |
| SON | 10 | 188.0 | 38.5 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 1} |
| URW | 7 | 80.2 | 31.7 | {'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 4} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 30／正式試行 30・発走前送信 30／本人確認 0
2. 計算完走：Full29 30／Signed FINAL 30／KRS5000 30／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 116.1%／正式推薦 36.5%／実購入なし
5. Learning：RESULT署名検証 23／学習状態保存 23／前Raceの学習状態を結合した正式Race 30（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 23 | 39.1% | 69.6% | 39.1% | 13.0% | 21.7% | 0.0% | 39.1% | 1.61 |
| 正式推薦 | 23 | 30.4% | 69.6% | 69.6% | 78.3% | 100.0% | 69.6% | 47.8% | 1.61 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中39.1%（無作為9.2%、差+29.9）／P2 平均1.0頭 的中13.0%（無作為9.2%、差+3.9）／P3 平均1.0頭 的中21.7%（無作為9.2%、差+12.6）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中69.6%（無作為27.5%、差+42.0）／P2 平均6.0頭 的中78.3%（無作為55.1%、差+23.2）／P3 平均11.04頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.52/40（選択性補正込み）・能力順位 14.54/20（23R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.75/40（選択性補正込み）・能力順位 14.16/20（23R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（3.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）10R・着順まで的中 0R／的中 11R のうち的中赤字 3R／損益分岐の倍率 平均 7.8倍／同じ点数を無作為に選んだ場合の期待PFS 38.1%（同じ23Rの実績 116.1%）／券種別 EXACTA 7点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 123点 PFS 109.8%／WIDE 40点 PFS 185.0%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 12R PFS 69.7% 的中赤字 0/3／SOLID 10R PFS 129.0% 的中赤字 3/7／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 22R：実績 97.5% − ミラー 30.4% = Δ 67.1pt（95%区間 1.3〜152.7、最高1R除き 38.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 53,600円（38.8%）／保護層の資金比率 0.0（23R）／組だけ的中（三連単は外れ）7R・着順まで的中 4R／的中 14R のうち的中赤字 13R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 29.4%（同じ23Rの実績 36.5%）／券種別 EXACTA 345点 PFS 34.6%／TRIFECTA 575点 PFS 19.7%／TRIO 460点 PFS 58.9%／荒れ度（発走前・1番人気オッズ）MID 12R PFS 29.9% 的中赤字 4/5／SOLID 10R PFS 46.7% 的中赤字 8/8／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 22R：実績 37.5% − ミラー 34.5% = Δ 3.0pt（95%区間 -18.9〜26.2、最高1R除き -4.1pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、23R×3券種）：購入 9／予算で削除 0／予想で除外 18／未生成・券種なし 42／役割馬の行き先 {'PURCHASED': 69}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、23R×3券種）：購入 28／予算で削除 10／予想で除外 20／未生成・券種なし 11／役割馬の行き先 {'PURCHASED': 168, 'BUDGET_COMPRESSED': 86}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 9R／W外 14R、2着が P2 役割 0R）：STATIC 0/9（平均4.33位）／STYLE_COND 1/9（平均4.11位） 救済1・喪失0／MARKET_COND 0/8（平均4.25位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 16R／W外 7R、2着が P2 役割 13R）：STATIC 13/16（平均3.62位）／STYLE_COND 13/16（平均3.44位） 救済0・喪失0／MARKET_COND 13/15（平均3.13位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 13 | 38,440 | RECURRING |
| P1:ROLE_W_MISS | P1 | 7 | 38,860 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 23 | 92,440 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

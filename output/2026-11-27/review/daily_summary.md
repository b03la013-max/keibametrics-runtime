# 地方版 2026-11-27 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 35／PAPER PFS 56.1%／正式推薦 PFS 40.4%
- 第一失敗：{'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 5, 'CAPITAL_EFFICIENCY': 13, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 11 | 13.4 | 52.1 | {'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 4} |
| SON | 12 | 96.7 | 17.6 | {'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 1} |
| URW | 12 | 56.2 | 52.4 | {'PREDICTION_ROLE_W': 6, 'NONE': 2, 'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_P2': 2} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 36／正式試行 36・発走前送信 36／本人確認 0
2. 計算完走：Full29 36／Signed FINAL 36／KRS5000 36／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 56.1%／正式推薦 40.4%／実購入なし
5. Learning：RESULT署名検証 35／学習状態保存 35／前Raceの学習状態を結合した正式Race 36（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '300R到達', 'C17-P2-ZAI-PLACE': '300R到達', 'C18-W-PLUS-FAVORITE': '300R到達', 'C19-W-PLUS-TOP2-POP': '300R到達', 'C20-P2-PLUS-TOP3-POP': '300R到達', 'C21-BVI-L-R2-TERTILE': '295/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 35 | 37.1% | 68.6% | 37.1% | 22.9% | 20.0% | 0.0% | 25.7% | 1.69 |
| 正式推薦 | 35 | 37.1% | 57.1% | 57.1% | 82.9% | 100.0% | 80.0% | 31.4% | 1.54 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中37.1%（無作為9.0%、差+28.2）／P2 平均1.0頭 的中22.9%（無作為9.0%、差+13.9）／P3 平均1.0頭 的中20.0%（無作為9.0%、差+11.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中57.1%（無作為26.9%、差+30.3）／P2 平均6.0頭 的中82.9%（無作為53.7%、差+29.1）／P3 平均11.37頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.63/40（選択性補正込み）・能力順位 14.95/20（35R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.34/40（選択性補正込み）・能力順位 14.56/20（35R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）9R・着順まで的中 0R／的中 15R のうち的中赤字 8R／損益分岐の倍率 平均 7.2倍／同じ点数を無作為に選んだ場合の期待PFS 46.0%（同じ35Rの実績 56.1%）／券種別 EXACTA 2点 PFS 0.0%／TRIO 181点 PFS 36.1%／WIDE 68点 PFS 111.8%／WIN 1点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 20R PFS 79.3% 的中赤字 1/8／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 13R PFS 22.0% 的中赤字 6/6／UNKNOWN 1R PFS 77.1% 的中赤字 1/1／市場ミラーとの差 34R：実績 55.5% − ミラー 82.8% = Δ -27.3pt（95%区間 -110.0〜34.6、最高1R除き -40.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（35R）／組だけ的中（三連単は外れ）8R・着順まで的中 11R／的中 20R のうち的中赤字 17R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 39.7%（同じ35Rの実績 40.4%）／券種別 EXACTA 612点 PFS 45.2%／TRIFECTA 1488点 PFS 38.4%／荒れ度（発走前・1番人気オッズ）MID 20R PFS 45.9% 的中赤字 10/12／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 13R PFS 36.2% 的中赤字 6/7／UNKNOWN 1R PFS 25.5% 的中赤字 1/1／市場ミラーとの差 34R：実績 40.8% − ミラー 42.7% = Δ -1.8pt（95%区間 -32.1〜33.6、最高1R除き -13.4pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、35R×3券種）：購入 9／予算で削除 0／予想で除外 27／未生成・券種なし 69／役割馬の行き先 {'PURCHASED': 105}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、35R×3券種）：購入 30／予算で削除 9／予想で除外 33／未生成・券種なし 33／役割馬の行き先 {'BUDGET_COMPRESSED': 129, 'PURCHASED': 269}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 13R／W外 22R、2着が P2 役割 4R）：STATIC 4/13（平均2.77位）／STYLE_COND 5/13（平均2.62位） 救済1・喪失0／MARKET_COND 3/12（平均2.58位） 救済2・喪失2
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 20R／W外 15R、2着が P2 役割 15R）：STATIC 15/20（平均3.9位）／STYLE_COND 16/20（平均3.75位） 救済1・喪失0／MARKET_COND 18/19（平均2.79位） 救済4・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 17 | 66,600 | RECURRING |
| P1:ROLE_W_MISS | P1 | 15 | 74,820 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 35 | 156,600 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

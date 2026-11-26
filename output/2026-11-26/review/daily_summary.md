# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 30／PAPER PFS 121.1%／正式推薦 PFS 40.7%
- 第一失敗：{'PREDICTION_ROLE_W': 9, 'CAPITAL_EFFICIENCY': 14, 'PREDICTION_ROLE_P2': 5, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 5 | 32.7 | 33.5 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 4} |
| NGY | 4 | 307.5 | 101.7 | {'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 1, 'NONE': 2} |
| SON | 12 | 160.3 | 35.4 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 1} |
| URW | 9 | 55.9 | 24.6 | {'PREDICTION_ROLE_P2': 3, 'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 4} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 36／正式試行 36・発走前送信 36／本人確認 0
2. 計算完走：Full29 36／Signed FINAL 36／KRS5000 36／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 121.1%／正式推薦 40.7%／実購入なし
5. Learning：RESULT署名検証 30／学習状態保存 30／前Raceの学習状態を結合した正式Race 36（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 30 | 36.7% | 73.3% | 36.7% | 10.0% | 16.7% | 6.7% | 36.7% | 1.63 |
| 正式推薦 | 30 | 33.3% | 70.0% | 70.0% | 73.3% | 100.0% | 70.0% | 50.0% | 1.57 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中36.7%（無作為9.3%、差+27.4）／P2 平均1.0頭 的中10.0%（無作為9.3%、差+0.7）／P3 平均1.0頭 的中16.7%（無作為9.3%、差+7.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中70.0%（無作為27.8%、差+42.2）／P2 平均6.0頭 的中73.3%（無作為55.5%、差+17.8）／P3 平均11.0頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.73/40（選択性補正込み）・能力順位 14.62/20（30R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.39/40（選択性補正込み）・能力順位 14.03/20（30R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,800円（7.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）12R・着順まで的中 0R／的中 14R のうち的中赤字 5R／損益分岐の倍率 平均 8.2倍／同じ点数を無作為に選んだ場合の期待PFS 33.7%（同じ30Rの実績 121.1%）／券種別 EXACTA 13点 PFS 34.6%／TRIFECTA 24点 PFS 0.0%／TRIO 158点 PFS 134.7%／WIDE 50点 PFS 163.4%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 16R PFS 124.8% 的中赤字 1/5／SOLID 13R PFS 90.8% 的中赤字 4/8／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 29R：実績 107.8% − ミラー 41.0% = Δ 66.8pt（95%区間 -11.1〜176.1、最高1R除き 34.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 69,300円（38.5%）／保護層の資金比率 0.0（30R）／組だけ的中（三連単は外れ）9R・着順まで的中 6R／的中 18R のうち的中赤字 16R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 26.4%（同じ30Rの実績 40.7%）／券種別 EXACTA 450点 PFS 43.6%／TRIFECTA 750点 PFS 21.9%／TRIO 600点 PFS 62.0%／荒れ度（発走前・1番人気オッズ）MID 16R PFS 46.3% 的中赤字 7/9／SOLID 13R PFS 35.9% 的中赤字 8/8／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 29R：実績 41.6% − ミラー 44.3% = Δ -2.7pt（95%区間 -23.6〜21.1、最高1R除き -6.5pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、30R×3券種）：購入 12／予算で削除 0／予想で除外 26／未生成・券種なし 52／役割馬の行き先 {'PURCHASED': 90}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、30R×3券種）：購入 36／予算で削除 12／予想で除外 28／未生成・券種なし 14／役割馬の行き先 {'PURCHASED': 221, 'BUDGET_COMPRESSED': 109}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 11R／W外 19R、2着が P2 役割 0R）：STATIC 0/11（平均4.36位）／STYLE_COND 2/11（平均4.09位） 救済2・喪失0／MARKET_COND 2/10（平均3.6位） 救済2・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 21R／W外 9R、2着が P2 役割 16R）：STATIC 16/21（平均3.9位）／STYLE_COND 16/21（平均3.71位） 救済0・喪失0／MARKET_COND 18/20（平均2.9位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 16 | 47,190 | RECURRING |
| P1:ROLE_W_MISS | P1 | 9 | 48,510 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 30 | 119,190 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 16／PAPER PFS 95.8%／正式推薦 PFS 25.7%
- 第一失敗：{'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_P2': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 2 | 11.9 | 17.0 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 1} |
| NGY | 1 | 80.0 | 0.0 | {'PREDICTION_ROLE_W': 1} |
| SON | 8 | 162.0 | 31.8 | {'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1} |
| URW | 5 | 22.8 | 24.6 | {'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 3} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 23／正式試行 23・発走前送信 23／本人確認 0
2. 計算完走：Full29 23／Signed FINAL 23／KRS5000 23／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 95.8%／正式推薦 25.7%／実購入なし
5. Learning：RESULT署名検証 16／学習状態保存 16／前Raceの学習状態を結合した正式Race 23（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 16 | 37.5% | 75.0% | 37.5% | 6.2% | 25.0% | 0.0% | 31.2% | 1.69 |
| 正式推薦 | 16 | 31.2% | 68.8% | 68.8% | 75.0% | 100.0% | 68.8% | 37.5% | 1.5 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中37.5%（無作為9.1%、差+28.4）／P2 平均1.0頭 的中6.2%（無作為9.1%、差-2.8）／P3 平均1.0頭 的中25.0%（無作為9.1%、差+15.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中68.8%（無作為27.2%、差+41.6）／P2 平均6.0頭 的中75.0%（無作為54.3%、差+20.7）／P3 平均11.19頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.12/40（選択性補正込み）・能力順位 14.61/20（16R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.41/40（選択性補正込み）・能力順位 13.9/20（16R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（4.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 6R のうち的中赤字 2R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 40.2%（同じ16Rの実績 95.8%）／券種別 EXACTA 7点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 84点 PFS 85.0%／WIDE 26点 PFS 193.5%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 19.8% 的中赤字 0/1／SOLID 7R PFS 115.7% 的中赤字 2/4／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 15R：実績 67.8% − ミラー 27.2% = Δ 40.6pt（95%区間 -23.7〜151.8、最高1R除き -3.8pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 37,300円（38.9%）／保護層の資金比率 0.0（16R）／組だけ的中（三連単は外れ）3R・着順まで的中 3R／的中 9R のうち的中赤字 9R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 29.6%（同じ16Rの実績 25.7%）／券種別 EXACTA 240点 PFS 34.7%／TRIFECTA 400点 PFS 21.2%／TRIO 320点 PFS 24.6%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 15.9% 的中赤字 3/3／SOLID 7R PFS 38.8% 的中赤字 5/5／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 15R：実績 26.6% − ミラー 34.7% = Δ -8.1pt（95%区間 -30.7〜14.6、最高1R除き -14.2pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、16R×3券種）：購入 5／予算で削除 0／予想で除外 15／未生成・券種なし 28／役割馬の行き先 {'PURCHASED': 48}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、16R×3券種）：購入 18／予算で削除 7／予想で除外 14／未生成・券種なし 9／役割馬の行き先 {'PURCHASED': 117, 'BUDGET_COMPRESSED': 62}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 6R／W外 10R、2着が P2 役割 0R）：STATIC 0/6（平均5.17位）／STYLE_COND 1/6（平均4.67位） 救済1・喪失0／MARKET_COND 0/5（平均4.4位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 11R／W外 5R、2着が P2 役割 9R）：STATIC 9/11（平均3.73位）／STYLE_COND 9/11（平均3.36位） 救済0・喪失0／MARKET_COND 9/10（平均2.4位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 9 | 29,300 | RECURRING |
| P1:ROLE_W_MISS | P1 | 5 | 30,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 16 | 71,300 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

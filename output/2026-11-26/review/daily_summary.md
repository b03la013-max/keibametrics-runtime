# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 32／PAPER PFS 121.4%／正式推薦 PFS 41.8%
- 第一失敗：{'PREDICTION_ROLE_W': 9, 'CAPITAL_EFFICIENCY': 16, 'PREDICTION_ROLE_P2': 5, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 6 | 38.4 | 31.9 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 5} |
| NGY | 5 | 282.9 | 100.3 | {'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 1, 'NONE': 2, 'CAPITAL_EFFICIENCY': 1} |
| SON | 12 | 160.3 | 35.4 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 1} |
| URW | 9 | 55.9 | 24.6 | {'PREDICTION_ROLE_P2': 3, 'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 4} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 37／正式試行 37・発走前送信 37／本人確認 0
2. 計算完走：Full29 37／Signed FINAL 37／KRS5000 37／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 121.4%／正式推薦 41.8%／実購入なし
5. Learning：RESULT署名検証 32／学習状態保存 32／前Raceの学習状態を結合した正式Race 37（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 32 | 34.4% | 75.0% | 34.4% | 9.4% | 21.9% | 6.2% | 40.6% | 1.72 |
| 正式推薦 | 32 | 34.4% | 71.9% | 71.9% | 75.0% | 100.0% | 71.9% | 53.1% | 1.59 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中34.4%（無作為9.3%、差+25.1）／P2 平均1.0頭 的中9.4%（無作為9.3%、差+0.1）／P3 平均1.0頭 的中21.9%（無作為9.3%、差+12.6）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中71.9%（無作為27.8%、差+44.1）／P2 平均6.0頭 的中75.0%（無作為55.5%、差+19.5）／P3 平均11.0頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.38/40（選択性補正込み）・能力順位 14.84/20（32R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.75/40（選択性補正込み）・能力順位 14.19/20（32R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,800円（6.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）14R・着順まで的中 0R／的中 16R のうち的中赤字 6R／損益分岐の倍率 平均 8.2倍／同じ点数を無作為に選んだ場合の期待PFS 32.3%（同じ32Rの実績 121.4%）／券種別 EXACTA 13点 PFS 34.6%／TRIFECTA 24点 PFS 0.0%／TRIO 168点 PFS 135.0%／WIDE 54点 PFS 158.3%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 17R PFS 128.0% 的中赤字 1/6／SOLID 14R PFS 89.6% 的中赤字 5/9／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 31R：実績 108.8% − ミラー 39.3% = Δ 69.6pt（95%区間 -6.1〜167.2、最高1R除き 38.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 73,900円（38.5%）／保護層の資金比率 0.0（32R）／組だけ的中（三連単は外れ）10R・着順まで的中 7R／的中 20R のうち的中赤字 18R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 25.1%（同じ32Rの実績 41.8%）／券種別 EXACTA 480点 PFS 45.4%／TRIFECTA 800点 PFS 25.0%／TRIO 640点 PFS 60.3%／荒れ度（発走前・1番人気オッズ）MID 17R PFS 49.1% 的中赤字 8/10／SOLID 14R PFS 35.1% 的中赤字 9/9／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 31R：実績 42.8% − ミラー 45.1% = Δ -2.4pt（95%区間 -22.1〜18.0、最高1R除き -5.9pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、32R×3券種）：購入 14／予算で削除 0／予想で除外 26／未生成・券種なし 56／役割馬の行き先 {'PURCHASED': 96}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、32R×3券種）：購入 41／予算で削除 13／予想で除外 28／未生成・券種なし 14／役割馬の行き先 {'PURCHASED': 236, 'BUDGET_COMPRESSED': 116}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 11R／W外 21R、2着が P2 役割 0R）：STATIC 0/11（平均4.36位）／STYLE_COND 2/11（平均4.09位） 救済2・喪失0／MARKET_COND 2/10（平均3.6位） 救済2・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 23R／W外 9R、2着が P2 役割 18R）：STATIC 18/23（平均3.83位）／STYLE_COND 18/23（平均3.7位） 救済0・喪失0／MARKET_COND 20/22（平均2.91位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 18 | 52,060 | RECURRING |
| P1:ROLE_W_MISS | P1 | 9 | 48,510 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 32 | 124,060 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

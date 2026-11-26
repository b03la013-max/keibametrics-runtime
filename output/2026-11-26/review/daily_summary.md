# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 35／PAPER PFS 115.2%／正式推薦 PFS 40.1%
- 第一失敗：{'PREDICTION_ROLE_W': 10, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_P2': 6, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 7 | 49.2 | 32.9 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 6} |
| NGY | 6 | 235.7 | 83.6 | {'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 1} |
| SON | 12 | 160.3 | 35.4 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 1} |
| URW | 10 | 51.7 | 24.7 | {'PREDICTION_ROLE_P2': 3, 'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 4} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 40／正式試行 40・発走前送信 40／本人確認 0
2. 計算完走：Full29 40／Signed FINAL 40／KRS5000 40／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 115.2%／正式推薦 40.1%／実購入なし
5. Learning：RESULT署名検証 35／学習状態保存 35／前Raceの学習状態を結合した正式Race 40（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 35 | 34.3% | 71.4% | 34.3% | 11.4% | 22.9% | 5.7% | 40.0% | 1.71 |
| 正式推薦 | 35 | 31.4% | 71.4% | 71.4% | 74.3% | 100.0% | 71.4% | 54.3% | 1.6 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中34.3%（無作為9.3%、差+25.0）／P2 平均1.0頭 的中11.4%（無作為9.3%、差+2.2）／P3 平均1.0頭 的中22.9%（無作為9.3%、差+13.6）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中71.4%（無作為27.8%、差+43.7）／P2 平均6.0頭 的中74.3%（無作為55.5%、差+18.8）／P3 平均11.0頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.51/40（選択性補正込み）・能力順位 14.79/20（35R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.75/40（選択性補正込み）・能力順位 14.27/20（35R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,800円（6.4%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）15R・着順まで的中 0R／的中 17R のうち的中赤字 6R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 32.0%（同じ35Rの実績 115.2%）／券種別 EXACTA 13点 PFS 34.6%／TRIFECTA 24点 PFS 0.0%／TRIO 183点 PFS 127.5%／WIDE 60点 PFS 145.3%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 20R PFS 115.4% 的中赤字 1/7／SOLID 14R PFS 89.6% 的中赤字 5/9／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 34R：実績 103.5% − ミラー 36.9% = Δ 66.6pt（95%区間 -2.3〜156.4、最高1R除き 38.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 80,900円（38.5%）／保護層の資金比率 0.0（35R）／組だけ的中（三連単は外れ）11R・着順まで的中 8R／的中 22R のうち的中赤字 20R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 24.4%（同じ35Rの実績 40.1%）／券種別 EXACTA 525点 PFS 42.2%／TRIFECTA 875点 PFS 24.3%／TRIO 700点 PFS 58.3%／荒れ度（発走前・1番人気オッズ）MID 20R PFS 45.0% 的中赤字 10/12／SOLID 14R PFS 35.1% 的中赤字 9/9／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 34R：実績 40.9% − ミラー 43.0% = Δ -2.2pt（95%区間 -20.8〜17.0、最高1R除き -5.4pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、35R×3券種）：購入 15／予算で削除 0／予想で除外 28／未生成・券種なし 62／役割馬の行き先 {'PURCHASED': 105}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、35R×3券種）：購入 45／予算で削除 13／予想で除外 32／未生成・券種なし 15／役割馬の行き先 {'PURCHASED': 258, 'BUDGET_COMPRESSED': 127}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 12R／W外 23R、2着が P2 役割 1R）：STATIC 1/12（平均4.08位）／STYLE_COND 3/12（平均3.83位） 救済2・喪失0／MARKET_COND 3/11（平均3.36位） 救済2・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 25R／W外 10R、2着が P2 役割 19R）：STATIC 20/25（平均3.84位）／STYLE_COND 20/25（平均3.68位） 救済0・喪失0／MARKET_COND 22/24（平均2.96位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 20 | 60,210 | RECURRING |
| P1:ROLE_W_MISS | P1 | 10 | 52,990 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 6 | 36,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 35 | 138,210 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

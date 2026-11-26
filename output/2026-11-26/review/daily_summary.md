# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 28／PAPER PFS 128.4%／正式推薦 PFS 40.1%
- 第一失敗：{'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_P2': 5, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 4 | 40.3 | 27.0 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 3} |
| NGY | 4 | 307.5 | 101.7 | {'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 1, 'NONE': 2} |
| SON | 11 | 173.1 | 35.0 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 1} |
| URW | 9 | 55.9 | 24.6 | {'PREDICTION_ROLE_P2': 3, 'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 4} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 35／正式試行 35・発走前送信 35／本人確認 0
2. 計算完走：Full29 35／Signed FINAL 35／KRS5000 35／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 128.4%／正式推薦 40.1%／実購入なし
5. Learning：RESULT署名検証 28／学習状態保存 28／前Raceの学習状態を結合した正式Race 35（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 28 | 39.3% | 75.0% | 39.3% | 10.7% | 17.9% | 7.1% | 39.3% | 1.64 |
| 正式推薦 | 28 | 32.1% | 71.4% | 71.4% | 71.4% | 100.0% | 71.4% | 46.4% | 1.54 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中39.3%（無作為9.1%、差+30.2）／P2 平均1.0頭 的中10.7%（無作為9.1%、差+1.6）／P3 平均1.0頭 的中17.9%（無作為9.1%、差+8.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中71.4%（無作為27.3%、差+44.1）／P2 平均6.0頭 的中71.4%（無作為54.7%、差+16.7）／P3 平均11.14頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.21/40（選択性補正込み）・能力順位 14.73/20（28R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.57/40（選択性補正込み）・能力順位 14.03/20（28R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,800円（7.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）12R・着順まで的中 0R／的中 14R のうち的中赤字 5R／損益分岐の倍率 平均 8.3倍／同じ点数を無作為に選んだ場合の期待PFS 33.9%（同じ28Rの実績 128.4%）／券種別 EXACTA 13点 PFS 34.6%／TRIFECTA 24点 PFS 0.0%／TRIO 148点 PFS 143.9%／WIDE 46点 PFS 177.6%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 14R PFS 141.2% 的中赤字 1/5／SOLID 13R PFS 90.8% 的中赤字 4/8／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 27R：実績 114.5% − ミラー 43.5% = Δ 71.0pt（95%区間 -8.8〜184.1、最高1R除き 36.5pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 65,100円（38.8%）／保護層の資金比率 0.0（28R）／組だけ的中（三連単は外れ）8R・着順まで的中 5R／的中 16R のうち的中赤字 14R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 27.1%（同じ28Rの実績 40.1%）／券種別 EXACTA 420点 PFS 45.5%／TRIFECTA 700点 PFS 19.1%／TRIO 560点 PFS 62.3%／荒れ度（発走前・1番人気オッズ）MID 14R PFS 45.8% 的中赤字 5/7／SOLID 13R PFS 35.9% 的中赤字 8/8／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 27R：実績 41.0% − ミラー 37.7% = Δ 3.3pt（95%区間 -15.9〜24.5、最高1R除き -0.5pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、28R×3券種）：購入 12／予算で削除 0／予想で除外 24／未生成・券種なし 48／役割馬の行き先 {'PURCHASED': 84}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、28R×3券種）：購入 33／予算で削除 12／予想で除外 26／未生成・券種なし 13／役割馬の行き先 {'PURCHASED': 205, 'BUDGET_COMPRESSED': 107}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 11R／W外 17R、2着が P2 役割 0R）：STATIC 0/11（平均4.36位）／STYLE_COND 2/11（平均4.09位） 救済2・喪失0／MARKET_COND 2/10（平均3.6位） 救済2・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 20R／W外 8R、2着が P2 役割 15R）：STATIC 15/20（平均4.05位）／STYLE_COND 15/20（平均3.8位） 救済0・喪失0／MARKET_COND 17/19（平均2.95位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 14 | 41,110 | RECURRING |
| P1:ROLE_W_MISS | P1 | 8 | 44,860 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 28 | 113,110 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

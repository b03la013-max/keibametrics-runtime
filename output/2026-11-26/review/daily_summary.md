# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 17／PAPER PFS 103.8%／正式推薦 PFS 30.0%
- 第一失敗：{'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_P2': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 2 | 11.9 | 17.0 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 1} |
| NGY | 1 | 80.0 | 0.0 | {'PREDICTION_ROLE_W': 1} |
| SON | 8 | 162.0 | 31.8 | {'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1} |
| URW | 6 | 57.2 | 37.0 | {'PREDICTION_ROLE_P2': 1, 'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 4} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 24／正式試行 24・発走前送信 24／本人確認 0
2. 計算完走：Full29 24／Signed FINAL 24／KRS5000 24／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 103.8%／正式推薦 30.0%／実購入なし
5. Learning：RESULT署名検証 17／学習状態保存 17／前Raceの学習状態を結合した正式Race 24（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 17 | 41.2% | 76.5% | 41.2% | 5.9% | 23.5% | 0.0% | 29.4% | 1.65 |
| 正式推薦 | 17 | 29.4% | 70.6% | 70.6% | 76.5% | 100.0% | 70.6% | 41.2% | 1.47 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中41.2%（無作為9.1%、差+32.1）／P2 平均1.0頭 的中5.9%（無作為9.1%、差-3.2）／P3 平均1.0頭 的中23.5%（無作為9.1%、差+14.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中70.6%（無作為27.3%、差+43.3）／P2 平均6.0頭 的中76.5%（無作為54.7%、差+21.8）／P3 平均11.12頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.12/40（選択性補正込み）・能力順位 14.58/20（17R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.68/40（選択性補正込み）・能力順位 13.86/20（17R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（4.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 7R のうち的中赤字 2R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 41.4%（同じ17Rの実績 103.8%）／券種別 EXACTA 7点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 89点 PFS 80.2%／WIDE 28点 PFS 241.8%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 19.8% 的中赤字 0/1／SOLID 8R PFS 129.6% 的中赤字 2/5／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 16R：実績 77.7% − ミラー 25.7% = Δ 52.0pt（95%区間 -14.2〜154.1、最高1R除き 10.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 39,600円（38.8%）／保護層の資金比率 0.0（17R）／組だけ的中（三連単は外れ）4R・着順まで的中 3R／的中 10R のうち的中赤字 10R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 29.2%（同じ17Rの実績 30.0%）／券種別 EXACTA 255点 PFS 35.5%／TRIFECTA 425点 PFS 20.0%／TRIO 340点 PFS 38.5%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 15.9% 的中赤字 3/3／SOLID 8R PFS 46.2% 的中赤字 6/6／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 16R：実績 31.1% − ミラー 33.3% = Δ -2.2pt（95%区間 -26.6〜22.1、最高1R除き -8.1pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、17R×3券種）：購入 5／予算で削除 0／予想で除外 16／未生成・券種なし 30／役割馬の行き先 {'PURCHASED': 51}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、17R×3券種）：購入 20／予算で削除 8／予想で除外 14／未生成・券種なし 9／役割馬の行き先 {'PURCHASED': 124, 'BUDGET_COMPRESSED': 65}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 7R／W外 10R、2着が P2 役割 0R）：STATIC 0/7（平均4.86位）／STYLE_COND 1/7（平均4.57位） 救済1・喪失0／MARKET_COND 0/6（平均4.5位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 12R／W外 5R、2着が P2 役割 10R）：STATIC 10/12（平均3.67位）／STYLE_COND 10/12（平均3.42位） 救済0・喪失0／MARKET_COND 10/11（平均2.64位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 10 | 29,380 | RECURRING |
| P1:ROLE_W_MISS | P1 | 5 | 30,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 17 | 71,380 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

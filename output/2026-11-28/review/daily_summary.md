# 地方版 2026-11-28 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 14／PAPER PFS 34.9%／正式推薦 PFS 105.7%
- 第一失敗：{'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 3, 'NONE': 3, 'PREDICTION_ROLE_W': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KOC | 7 | 41.2 | 195.7 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1, 'NONE': 3, 'PREDICTION_ROLE_W': 1} |
| SAG | 7 | 29.5 | 15.7 | {'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2} |

## 日次自律監査

1. 配送：管理 24R／PAPER発走前送信 18／正式試行 18・発走前送信 18／本人確認 0
2. 計算完走：Full29 18／Signed FINAL 18／KRS5000 18／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 34.9%／正式推薦 105.7%／実購入なし
5. Learning：RESULT署名検証 14／学習状態保存 14／前Raceの学習状態を結合した正式Race 18（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '100R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '300R到達', 'C17-P2-ZAI-PLACE': '300R到達', 'C18-W-PLUS-FAVORITE': '300R到達', 'C19-W-PLUS-TOP2-POP': '300R到達', 'C20-P2-PLUS-TOP3-POP': '300R到達', 'C21-BVI-L-R2-TERTILE': '300R到達'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 14 | 42.9% | 85.7% | 42.9% | 0.0% | 28.6% | 7.1% | 21.4% | 1.93 |
| 正式推薦 | 14 | 42.9% | 71.4% | 71.4% | 71.4% | 100.0% | 85.7% | 35.7% | 1.79 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中42.9%（無作為10.5%、差+32.4）／P2 平均1.0頭 的中0.0%（無作為10.5%、差-10.5）／P3 平均1.0頭 的中28.6%（無作為10.5%、差+18.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中71.4%（無作為31.4%、差+40.0）／P2 平均6.0頭 的中71.4%（無作為62.8%、差+8.7）／P3 平均9.71頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.43/40（選択性補正込み）・能力順位 14.73/20（14R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.45/40（選択性補正込み）・能力順位 14.57/20（14R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（5.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）3R・着順まで的中 0R／的中 6R のうち的中赤字 5R／損益分岐の倍率 平均 7.8倍／同じ点数を無作為に選んだ場合の期待PFS 36.1%（同じ14Rの実績 34.9%）／券種別 EXACTA 7点 PFS 187.1%／TRIFECTA 8点 PFS 0.0%／TRIO 70点 PFS 22.6%／WIDE 22点 PFS 41.4%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 4R PFS 9.0% 的中赤字 1/1／OPEN 1R PFS 177.1% 的中赤字 0/1／SOLID 9R PFS 31.5% 的中赤字 4/4／市場ミラーとの差 14R：実績 34.9% − ミラー 52.8% = Δ -17.9pt（95%区間 -96.1〜38.0、最高1R除き -35.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（14R）／組だけ的中（三連単は外れ）4R・着順まで的中 5R／的中 8R のうち的中赤字 5R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 35.6%（同じ14Rの実績 105.7%）／券種別 EXACTA 243点 PFS 78.0%／TRIFECTA 597点 PFS 117.0%／荒れ度（発走前・1番人気オッズ）MID 4R PFS 283.5% 的中赤字 0/2／OPEN 1R PFS 205.5% 的中赤字 0/1／SOLID 9R PFS 15.6% 的中赤字 5/5／市場ミラーとの差 14R：実績 105.7% − ミラー 48.4% = Δ 57.3pt（95%区間 -32.1〜159.5、最高1R除き 20.0pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、14R×3券種）：購入 4／予算で削除 0／予想で除外 14／未生成・券種なし 24／役割馬の行き先 {'PURCHASED': 42}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、14R×3券種）：購入 12／予算で削除 4／予想で除外 13／未生成・券種なし 13／役割馬の行き先 {'PURCHASED': 104, 'BUDGET_COMPRESSED': 32}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 6R／W外 8R、2着が P2 役割 0R）：STATIC 0/6（平均4.5位）／STYLE_COND 0/6（平均4.67位） 救済0・喪失0／MARKET_COND 1/6（平均3.17位） 救済1・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 10R／W外 4R、2着が P2 役割 6R）：STATIC 8/10（平均4.4位）／STYLE_COND 8/10（平均4.5位） 救済0・喪失0／MARKET_COND 9/10（平均3.2位） 救済2・喪失1

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 5 | 21,580 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 4 | 24,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 4 | 19,430 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 14 | 57,580 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

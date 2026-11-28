# 地方版 2026-11-28 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 12／PAPER PFS 26.9%／正式推薦 PFS 106.2%
- 第一失敗：{'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 3, 'NONE': 2, 'PREDICTION_ROLE_W': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KOC | 6 | 19.1 | 194.1 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1, 'NONE': 2, 'PREDICTION_ROLE_W': 1} |
| SAG | 6 | 33.5 | 18.3 | {'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2} |

## 日次自律監査

1. 配送：管理 24R／PAPER発走前送信 16／正式試行 16・発走前送信 16／本人確認 0
2. 計算完走：Full29 16／Signed FINAL 16／KRS5000 16／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 26.9%／正式推薦 106.2%／実購入なし
5. Learning：RESULT署名検証 12／学習状態保存 12／前Raceの学習状態を結合した正式Race 16（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '100R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '300R到達', 'C17-P2-ZAI-PLACE': '300R到達', 'C18-W-PLUS-FAVORITE': '300R到達', 'C19-W-PLUS-TOP2-POP': '300R到達', 'C20-P2-PLUS-TOP3-POP': '300R到達', 'C21-BVI-L-R2-TERTILE': '300R到達'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 12 | 50.0% | 91.7% | 50.0% | 0.0% | 33.3% | 8.3% | 16.7% | 1.92 |
| 正式推薦 | 12 | 50.0% | 75.0% | 75.0% | 66.7% | 100.0% | 91.7% | 33.3% | 1.75 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中50.0%（無作為10.4%、差+39.6）／P2 平均1.0頭 的中0.0%（無作為10.4%、差-10.4）／P3 平均1.0頭 的中33.3%（無作為10.4%、差+22.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中75.0%（無作為31.3%、差+43.7）／P2 平均6.0頭 的中66.7%（無作為62.7%、差+4.0）／P3 平均9.75頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 17.5/40（選択性補正込み）・能力順位 14.83/20（12R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.65/40（選択性補正込み）・能力順位 14.53/20（12R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（6.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）2R・着順まで的中 0R／的中 5R のうち的中赤字 5R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 23.4%（同じ12Rの実績 26.9%）／券種別 EXACTA 7点 PFS 187.1%／TRIFECTA 8点 PFS 0.0%／TRIO 60点 PFS 9.0%／WIDE 18点 PFS 39.4%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 3R PFS 11.8% 的中赤字 1/1／SOLID 9R PFS 31.5% 的中赤字 4/4／市場ミラーとの差 12R：実績 26.9% − ミラー 60.5% = Δ -33.6pt（95%区間 -120.6〜25.2、最高1R除き -57.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（12R）／組だけ的中（三連単は外れ）4R・着順まで的中 4R／的中 7R のうち的中赤字 5R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 18.0%（同じ12Rの実績 106.2%）／券種別 EXACTA 210点 PFS 76.9%／TRIFECTA 510点 PFS 118.3%／荒れ度（発走前・1番人気オッズ）MID 3R PFS 378.0% 的中赤字 0/2／SOLID 9R PFS 15.6% 的中赤字 5/5／市場ミラーとの差 12R：実績 106.2% − ミラー 56.4% = Δ 49.8pt（95%区間 -51.1〜167.4、最高1R除き 4.9pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、12R×3券種）：購入 3／予算で削除 0／予想で除外 13／未生成・券種なし 20／役割馬の行き先 {'PURCHASED': 36}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、12R×3券種）：購入 10／予算で削除 4／予想で除外 11／未生成・券種なし 11／役割馬の行き先 {'PURCHASED': 90, 'BUDGET_COMPRESSED': 27}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 6R／W外 6R、2着が P2 役割 0R）：STATIC 0/6（平均4.5位）／STYLE_COND 0/6（平均4.67位） 救済0・喪失0／MARKET_COND 1/6（平均3.17位） 救済1・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 9R／W外 3R、2着が P2 役割 5R）：STATIC 7/9（平均4.78位）／STYLE_COND 7/9（平均4.89位） 救済0・喪失0／MARKET_COND 8/9（平均3.11位） 救済2・喪失1

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 5 | 21,580 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 4 | 24,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 3 | 13,430 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 12 | 51,580 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

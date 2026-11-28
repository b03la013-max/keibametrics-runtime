# 地方版 2026-11-28 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 10／PAPER PFS 28.4%／正式推薦 PFS 50.6%
- 第一失敗：{'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 3, 'NONE': 1, 'PREDICTION_ROLE_W': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KOC | 5 | 15.6 | 91.7 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1, 'NONE': 1, 'PREDICTION_ROLE_W': 1} |
| SAG | 5 | 38.7 | 9.5 | {'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2} |

## 日次自律監査

1. 配送：管理 24R／PAPER発走前送信 14／正式試行 14・発走前送信 14／本人確認 0
2. 計算完走：Full29 14／Signed FINAL 14／KRS5000 14／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 28.4%／正式推薦 50.6%／実購入なし
5. Learning：RESULT署名検証 10／学習状態保存 10／前Raceの学習状態を結合した正式Race 14（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '100R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '300R到達', 'C17-P2-ZAI-PLACE': '300R到達', 'C18-W-PLUS-FAVORITE': '300R到達', 'C19-W-PLUS-TOP2-POP': '300R到達', 'C20-P2-PLUS-TOP3-POP': '300R到達', 'C21-BVI-L-R2-TERTILE': '300R到達'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 10 | 50.0% | 90.0% | 50.0% | 0.0% | 40.0% | 10.0% | 20.0% | 1.9 |
| 正式推薦 | 10 | 60.0% | 80.0% | 80.0% | 60.0% | 100.0% | 90.0% | 20.0% | 1.8 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中50.0%（無作為10.5%、差+39.5）／P2 平均1.0頭 的中0.0%（無作為10.5%、差-10.5）／P3 平均1.0頭 的中40.0%（無作為10.5%、差+29.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中80.0%（無作為31.6%、差+48.4）／P2 平均6.0頭 的中60.0%（無作為63.1%、差-3.1）／P3 平均9.7頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 17.8/40（選択性補正込み）・能力順位 14.77/20（10R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.52/40（選択性補正込み）・能力順位 14.52/20（10R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（7.4%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）2R・着順まで的中 0R／的中 4R のうち的中赤字 4R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 20.7%（同じ10Rの実績 28.4%）／券種別 EXACTA 7点 PFS 187.1%／TRIFECTA 8点 PFS 0.0%／TRIO 50点 PFS 10.8%／WIDE 14点 PFS 32.1%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 2R PFS 0.0% 的中赤字 0/0／SOLID 8R PFS 34.8% 的中赤字 4/4／市場ミラーとの差 10R：実績 28.4% − ミラー 71.0% = Δ -42.6pt（95%区間 -142.5〜25.3、最高1R除き -73.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（10R）／組だけ的中（三連単は外れ）4R・着順まで的中 2R／的中 5R のうち的中赤字 4R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 12.6%（同じ10Rの実績 50.6%）／券種別 EXACTA 174点 PFS 36.8%／TRIFECTA 426点 PFS 56.2%／荒れ度（発走前・1番人気オッズ）MID 2R PFS 214.1% 的中赤字 0/1／SOLID 8R PFS 9.7% 的中赤字 4/4／市場ミラーとの差 10R：実績 50.6% − ミラー 50.7% = Δ -0.1pt（95%区間 -79.0〜104.4、最高1R除き -43.2pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、10R×3券種）：購入 3／予算で削除 0／予想で除外 11／未生成・券種なし 16／役割馬の行き先 {'PURCHASED': 30}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、10R×3券種）：購入 7／予算で削除 4／予想で除外 10／未生成・券種なし 9／役割馬の行き先 {'PURCHASED': 74, 'BUDGET_COMPRESSED': 23}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 5R／W外 5R、2着が P2 役割 0R）：STATIC 0/5（平均5.0位）／STYLE_COND 0/5（平均5.2位） 救済0・喪失0／MARKET_COND 1/5（平均3.4位） 救済1・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 8R／W外 2R、2着が P2 役割 4R）：STATIC 6/8（平均4.75位）／STYLE_COND 6/8（平均4.75位） 救済0・喪失0／MARKET_COND 7/8（平均2.88位） 救済2・喪失1

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | 4 | 24,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 4 | 19,330 | RECURRING |
| P1:ROLE_W_MISS | P1 | 2 | 11,180 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 10 | 49,330 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

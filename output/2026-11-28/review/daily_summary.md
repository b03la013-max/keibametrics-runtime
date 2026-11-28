# 地方版 2026-11-28 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 8／PAPER PFS 27.9%／正式推薦 PFS 61.8%
- 第一失敗：{'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 2, 'NONE': 1, 'PREDICTION_ROLE_W': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KOC | 4 | 19.3 | 114.7 | {'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 1, 'NONE': 1, 'PREDICTION_ROLE_W': 1} |
| SAG | 4 | 34.5 | 8.9 | {'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 24R／PAPER発走前送信 11／正式試行 11・発走前送信 11／本人確認 0
2. 計算完走：Full29 11／Signed FINAL 11／KRS5000 11／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 27.9%／正式推薦 61.8%／実購入なし
5. Learning：RESULT署名検証 8／学習状態保存 8／前Raceの学習状態を結合した正式Race 11（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '100R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '300R到達', 'C17-P2-ZAI-PLACE': '300R到達', 'C18-W-PLUS-FAVORITE': '300R到達', 'C19-W-PLUS-TOP2-POP': '300R到達', 'C20-P2-PLUS-TOP3-POP': '300R到達', 'C21-BVI-L-R2-TERTILE': '300R到達'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 8 | 50.0% | 87.5% | 50.0% | 0.0% | 25.0% | 12.5% | 12.5% | 1.75 |
| 正式推薦 | 8 | 62.5% | 75.0% | 75.0% | 62.5% | 100.0% | 87.5% | 25.0% | 1.75 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中50.0%（無作為10.1%、差+39.9）／P2 平均1.0頭 的中0.0%（無作為10.1%、差-10.1）／P3 平均1.0頭 的中25.0%（無作為10.1%、差+14.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中75.0%（無作為30.3%、差+44.7）／P2 平均6.0頭 的中62.5%（無作為60.7%、差+1.8）／P3 平均10.0頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.75/40（選択性補正込み）・能力順位 14.5/20（8R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.56/40（選択性補正込み）・能力順位 14.4/20（8R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（9.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）1R・着順まで的中 0R／的中 3R のうち的中赤字 3R／損益分岐の倍率 平均 8.4倍／同じ点数を無作為に選んだ場合の期待PFS 23.1%（同じ8Rの実績 27.9%）／券種別 EXACTA 7点 PFS 187.1%／TRIFECTA 8点 PFS 0.0%／TRIO 40点 PFS 6.8%／WIDE 10点 PFS 29.0%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 2R PFS 0.0% 的中赤字 0/0／SOLID 6R PFS 36.0% 的中赤字 3/3／市場ミラーとの差 8R：実績 27.9% − ミラー 72.2% = Δ -44.3pt（95%区間 -170.5〜37.2、最高1R除き -83.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（8R）／組だけ的中（三連単は外れ）2R・着順まで的中 2R／的中 4R のうち的中赤字 3R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 14.3%（同じ8Rの実績 61.8%）／券種別 EXACTA 138点 PFS 41.2%／TRIFECTA 342点 PFS 70.1%／荒れ度（発走前・1番人気オッズ）MID 2R PFS 214.1% 的中赤字 0/1／SOLID 6R PFS 11.0% 的中赤字 3/3／市場ミラーとの差 8R：実績 61.8% − ミラー 56.2% = Δ 5.5pt（95%区間 -91.0〜136.6、最高1R除き -49.1pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、8R×3券種）：購入 2／予算で削除 0／予想で除外 10／未生成・券種なし 12／役割馬の行き先 {'PURCHASED': 24}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、8R×3券種）：購入 6／予算で削除 3／予想で除外 8／未生成・券種なし 7／役割馬の行き先 {'PURCHASED': 60, 'BUDGET_COMPRESSED': 20}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 4R／W外 4R、2着が P2 役割 0R）：STATIC 0/4（平均4.75位）／STYLE_COND 0/4（平均5.25位） 救済0・喪失0／MARKET_COND 0/4（平均4.0位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 6R／W外 2R、2着が P2 役割 3R）：STATIC 4/6（平均5.17位）／STYLE_COND 4/6（平均5.33位） 救済0・喪失0／MARKET_COND 5/6（平均3.5位） 救済2・喪失1

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 3 | 14,040 | RECURRING |
| P1:ROLE_W_MISS | P1 | 2 | 11,180 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 8 | 38,040 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

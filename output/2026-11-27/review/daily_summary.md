# 地方版 2026-11-27 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 9／PAPER PFS 31.4%／正式推薦 PFS 17.8%
- 第一失敗：{'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 5}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| SON | 6 | 47.1 | 21.8 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 2} |
| URW | 3 | 0.0 | 9.9 | {'PREDICTION_ROLE_W': 3} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 12／正式試行 12・発走前送信 12／本人確認 0
2. 計算完走：Full29 12／Signed FINAL 12／KRS5000 12／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 31.4%／正式推薦 17.8%／実購入なし
5. Learning：RESULT署名検証 9／学習状態保存 9／前Raceの学習状態を結合した正式Race 12（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '295/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 9 | 33.3% | 55.6% | 33.3% | 44.4% | 44.4% | 0.0% | 44.4% | 1.78 |
| 正式推薦 | 9 | 33.3% | 44.4% | 44.4% | 100.0% | 100.0% | 88.9% | 33.3% | 1.44 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.3%（無作為9.6%、差+23.7）／P2 平均1.0頭 的中44.4%（無作為9.6%、差+34.8）／P3 平均1.0頭 的中44.4%（無作為9.6%、差+34.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中44.4%（無作為28.9%、差+15.6）／P2 平均6.0頭 的中100.0%（無作為57.7%、差+42.3）／P3 平均10.56頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 19.22/40（選択性補正込み）・能力順位 15.13/20（9R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.25/40（選択性補正込み）・能力順位 14.9/20（9R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）4R・着順まで的中 0R／的中 4R のうち的中赤字 4R／損益分岐の倍率 平均 7.0倍／同じ点数を無作為に選んだ場合の期待PFS 65.4%（同じ9Rの実績 31.4%）／券種別 TRIO 45点 PFS 35.6%／WIDE 18点 PFS 21.1%／荒れ度（発走前・1番人気オッズ）MID 4R PFS 17.5% 的中赤字 1/1／SOLID 4R PFS 33.9% 的中赤字 2/2／UNKNOWN 1R PFS 77.1% 的中赤字 1/1／市場ミラーとの差 8R：実績 25.7% − ミラー 32.9% = Δ -7.1pt（95%区間 -33.2〜19.3、最高1R除き -8.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（9R）／組だけ的中（三連単は外れ）3R・着順まで的中 3R／的中 6R のうち的中赤字 6R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 41.0%（同じ9Rの実績 17.8%）／券種別 EXACTA 159点 PFS 29.6%／TRIFECTA 381点 PFS 12.9%／荒れ度（発走前・1番人気オッズ）MID 4R PFS 30.6% 的中赤字 3/3／SOLID 4R PFS 3.1% 的中赤字 2/2／UNKNOWN 1R PFS 25.5% 的中赤字 1/1／市場ミラーとの差 8R：実績 16.8% − ミラー 27.1% = Δ -10.2pt（95%区間 -29.6〜4.9、最高1R除き -11.7pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、9R×3券種）：購入 4／予算で削除 0／予想で除外 5／未生成・券種なし 18／役割馬の行き先 {'PURCHASED': 27}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、9R×3券種）：購入 8／予算で削除 2／予想で除外 8／未生成・券種なし 9／役割馬の行き先 {'PURCHASED': 68, 'BUDGET_COMPRESSED': 27}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 3R／W外 6R、2着が P2 役割 2R）：STATIC 2/3（平均1.33位）／STYLE_COND 2/3（平均1.33位） 救済0・喪失0／MARKET_COND 1/2（平均2.5位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 4R／W外 5R、2着が P2 役割 4R）：STATIC 4/4（平均2.0位）／STYLE_COND 4/4（平均2.0位） 救済0・喪失0／MARKET_COND 3/3（平均2.0位） 救済0・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 6 | 26,390 | RECURRING |
| P1:ROLE_W_MISS | P1 | 5 | 25,500 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 9 | 44,390 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-27 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 12／PAPER PFS 23.6%／正式推薦 PFS 15.0%
- 第一失敗：{'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 7}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| SON | 7 | 40.4 | 21.5 | {'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 2} |
| URW | 5 | 0.0 | 5.9 | {'PREDICTION_ROLE_W': 5} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 18／正式試行 18・発走前送信 18／本人確認 0
2. 計算完走：Full29 18／Signed FINAL 18／KRS5000 18／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 23.6%／正式推薦 15.0%／実購入なし
5. Learning：RESULT署名検証 12／学習状態保存 12／前Raceの学習状態を結合した正式Race 18（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '295/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 12 | 25.0% | 50.0% | 25.0% | 41.7% | 33.3% | 0.0% | 33.3% | 1.58 |
| 正式推薦 | 12 | 33.3% | 41.7% | 41.7% | 100.0% | 100.0% | 75.0% | 25.0% | 1.5 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中25.0%（無作為9.5%、差+15.5）／P2 平均1.0頭 的中41.7%（無作為9.5%、差+32.2）／P3 平均1.0頭 的中33.3%（無作為9.5%、差+23.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中41.7%（無作為28.4%、差+13.2）／P2 平均6.0頭 的中100.0%（無作為56.9%、差+43.1）／P3 平均10.75頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.25/40（選択性補正込み）・能力順位 14.33/20（12R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.68/40（選択性補正込み）・能力順位 14.8/20（12R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）4R・着順まで的中 0R／的中 4R のうち的中赤字 4R／損益分岐の倍率 平均 7.0倍／同じ点数を無作為に選んだ場合の期待PFS 56.2%（同じ12Rの実績 23.6%）／券種別 TRIO 60点 PFS 26.7%／WIDE 24点 PFS 15.8%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 11.7% 的中赤字 1/1／SOLID 5R PFS 27.1% 的中赤字 2/2／UNKNOWN 1R PFS 77.1% 的中赤字 1/1／市場ミラーとの差 11R：実績 18.7% − ミラー 23.9% = Δ -5.2pt（95%区間 -25.3〜14.0、最高1R除き -5.7pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（12R）／組だけ的中（三連単は外れ）5R・着順まで的中 3R／的中 7R のうち的中赤字 7R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 36.4%（同じ12Rの実績 15.0%）／券種別 EXACTA 207点 PFS 28.6%／TRIFECTA 513点 PFS 9.6%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 23.8% 的中赤字 4/4／SOLID 5R PFS 2.5% 的中赤字 2/2／UNKNOWN 1R PFS 25.5% 的中赤字 1/1／市場ミラーとの差 11R：実績 14.1% − ミラー 38.3% = Δ -24.3pt（95%区間 -61.5〜0.9、最高1R除き -26.7pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、12R×3券種）：購入 4／予算で削除 0／予想で除外 8／未生成・券種なし 24／役割馬の行き先 {'PURCHASED': 36}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、12R×3券種）：購入 9／予算で削除 3／予想で除外 12／未生成・券種なし 12／役割馬の行き先 {'PURCHASED': 89, 'BUDGET_COMPRESSED': 40}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 3R／W外 9R、2着が P2 役割 2R）：STATIC 2/3（平均1.33位）／STYLE_COND 2/3（平均1.33位） 救済0・喪失0／MARKET_COND 1/2（平均2.5位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 5R／W外 7R、2着が P2 役割 5R）：STATIC 5/5（平均2.0位）／STYLE_COND 5/5（平均1.8位） 救済0・喪失0／MARKET_COND 4/4（平均2.0位） 救済0・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 7 | 37,500 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 7 | 31,180 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 12 | 61,180 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

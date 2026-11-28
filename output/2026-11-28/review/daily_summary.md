# 地方版 2026-11-28 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 3／PAPER PFS 5.5%／正式推薦 PFS 4.6%
- 第一失敗：{'PREDICTION_ROLE_P2': 2, 'PREDICTION_ROLE_W': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KOC | 1 | 17.1 | 0.0 | {'PREDICTION_ROLE_P2': 1} |
| SAG | 2 | 0.0 | 6.8 | {'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 1} |

## 日次自律監査

1. 配送：管理 24R／PAPER発走前送信 6／正式試行 6・発走前送信 6／本人確認 0
2. 計算完走：Full29 6／Signed FINAL 6／KRS5000 6／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 5.5%／正式推薦 4.6%／実購入なし
5. Learning：RESULT署名検証 3／学習状態保存 3／前Raceの学習状態を結合した正式Race 6（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '100R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '300R到達', 'C17-P2-ZAI-PLACE': '300R到達', 'C18-W-PLUS-FAVORITE': '300R到達', 'C19-W-PLUS-TOP2-POP': '300R到達', 'C20-P2-PLUS-TOP3-POP': '300R到達', 'C21-BVI-L-R2-TERTILE': '300R到達'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 3 | 66.7% | 66.7% | 66.7% | 0.0% | 33.3% | 0.0% | 0.0% | 1.67 |
| 正式推薦 | 3 | 33.3% | 66.7% | 66.7% | 33.3% | 100.0% | 100.0% | 33.3% | 2.0 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中66.7%（無作為10.1%、差+56.6）／P2 平均1.0頭 的中0.0%（無作為10.1%、差-10.1）／P3 平均1.0頭 的中33.3%（無作為10.1%、差+23.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.7%（無作為30.2%、差+36.5）／P2 平均6.0頭 的中33.3%（無作為60.4%、差-27.1）／P3 平均10.0頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 18.33/40（選択性補正込み）・能力順位 14.01/20（3R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.95/40（選択性補正込み）・能力順位 13.46/20（3R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）0R・着順まで的中 0R／的中 1R のうち的中赤字 1R／損益分岐の倍率 平均 7.3倍／同じ点数を無作為に選んだ場合の期待PFS 18.1%（同じ3Rの実績 5.5%）／券種別 EXACTA 2点 PFS 0.0%／TRIO 15点 PFS 0.0%／WIDE 4点 PFS 30.0%／WIN 1点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）SOLID 3R PFS 5.5% 的中赤字 1/1／市場ミラーとの差 3R：実績 5.5% − ミラー 201.4% = Δ -195.9pt（95%区間 -440.0〜-61.4、最高1R除き -258.7pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（3R）／組だけ的中（三連単は外れ）0R・着順まで的中 1R／的中 1R のうち的中赤字 1R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 10.0%（同じ3Rの実績 4.6%）／券種別 EXACTA 48点 PFS 2.9%／TRIFECTA 132点 PFS 5.2%／荒れ度（発走前・1番人気オッズ）SOLID 3R PFS 4.6% 的中赤字 1/1／市場ミラーとの差 3R：実績 4.6% − ミラー 100.4% = Δ -95.8pt（95%区間 -223.8〜0.0、最高1R除き -143.8pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、3R×3券種）：購入 0／予算で削除 0／予想で除外 4／未生成・券種なし 5／役割馬の行き先 {'PURCHASED': 9}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、3R×3券種）：購入 2／予算で削除 0／予想で除外 4／未生成・券種なし 3／役割馬の行き先 {'PURCHASED': 24, 'BUDGET_COMPRESSED': 6}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 2R／W外 1R、2着が P2 役割 0R）：STATIC 0/2（平均6.0位）／STYLE_COND 0/2（平均6.5位） 救済0・喪失0／MARKET_COND 0/2（平均3.0位） 救済0・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 2R／W外 1R、2着が P2 役割 0R）：STATIC 1/2（平均6.5位）／STYLE_COND 1/2（平均7.0位） 救済0・喪失0／MARKET_COND 2/2（平均3.0位） 救済1・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P1:ROLE_W_MISS | P1 | 1 | 5,180 | SINGLE_OR_FEW (過大評価しない) |
| P1:HIT_BUT_LOSS | P1 | 1 | 5,180 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 3 | 17,180 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

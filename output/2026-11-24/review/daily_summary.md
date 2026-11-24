# 地方版 2026-11-24 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 21／PAPER PFS 59.9%／正式推薦 PFS 41.5%
- 第一失敗：{'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 9 | 19.7 | 38.4 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 2, 'NONE': 1} |
| NGY | 4 | 59.7 | 26.4 | {'PREDICTION_ROLE_W': 4} |
| URW | 8 | 109.8 | 52.5 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'NONE': 1, 'PREDICTION_ROLE_P2': 2} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 26／正式試行 26・発走前送信 26／本人確認 0
2. 計算完走：Full29 26／Signed FINAL 26／KRS5000 26／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 59.9%／正式推薦 41.5%／実購入なし
5. Learning：RESULT署名検証 21／学習状態保存 21／前Raceの学習状態を結合した正式Race 26（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '211/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 21 | 28.6% | 66.7% | 28.6% | 0.0% | 9.5% | 0.0% | 23.8% | 1.48 |
| 正式推薦 | 21 | 38.1% | 61.9% | 61.9% | 81.0% | 100.0% | 61.9% | 52.4% | 1.48 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中28.6%（無作為10.0%、差+18.6）／P2 平均1.0頭 的中0.0%（無作為10.0%、差-10.0）／P3 平均1.0頭 的中9.5%（無作為10.0%、差-0.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中61.9%（無作為30.0%、差+31.9）／P2 平均6.0頭 的中81.0%（無作為60.1%、差+20.9）／P3 平均10.29頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.81/40（選択性補正込み）・能力順位 13.86/20（21R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.08/40（選択性補正込み）・能力順位 13.19/20（21R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（3.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 7R のうち的中赤字 4R／損益分岐の倍率 平均 7.6倍／同じ点数を無作為に選んだ場合の期待PFS 35.8%（同じ21Rの実績 59.9%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 109点 PFS 70.1%／WIDE 40点 PFS 48.5%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 70.3% 的中赤字 2/4／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 12R PFS 59.1% 的中赤字 2/3／市場ミラーとの差 21R：実績 59.9% − ミラー 15.3% = Δ 44.6pt（95%区間 -7.2〜122.8、最高1R除き 15.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 47,500円（37.7%）／保護層の資金比率 0.0（21R）／組だけ的中（三連単は外れ）8R・着順まで的中 3R／的中 13R のうち的中赤字 10R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 36.3%（同じ21Rの実績 41.5%）／券種別 EXACTA 315点 PFS 59.9%／TRIFECTA 525点 PFS 13.5%／TRIO 420点 PFS 62.7%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 37.0% 的中赤字 3/4／OPEN 1R PFS 84.2% 的中赤字 1/1／SOLID 12R PFS 40.9% 的中赤字 6/8／市場ミラーとの差 21R：実績 41.5% − ミラー 152.6% = Δ -111.1pt（95%区間 -226.7〜-17.1、最高1R除き -100.8pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 10 | 33,010 | RECURRING |
| P1:ROLE_W_MISS | P1 | 8 | 33,240 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 4 | 24,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 21 | 81,010 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

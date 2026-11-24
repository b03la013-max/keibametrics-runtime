# 地方版 2026-11-24 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 23／PAPER PFS 68.9%／正式推薦 PFS 50.3%
- 第一失敗：{'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'NONE': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 9 | 19.7 | 38.4 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 2, 'NONE': 1} |
| NGY | 5 | 48.4 | 27.0 | {'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 1} |
| URW | 9 | 134.9 | 75.1 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'NONE': 2, 'PREDICTION_ROLE_P2': 2} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 28／正式試行 28・発走前送信 28／本人確認 0
2. 計算完走：Full29 28／Signed FINAL 28／KRS5000 28／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 68.9%／正式推薦 50.3%／実購入なし
5. Learning：RESULT署名検証 23／学習状態保存 23／前Raceの学習状態を結合した正式Race 28（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '211/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 23 | 30.4% | 69.6% | 30.4% | 0.0% | 8.7% | 0.0% | 26.1% | 1.48 |
| 正式推薦 | 23 | 39.1% | 65.2% | 65.2% | 82.6% | 100.0% | 65.2% | 52.2% | 1.48 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中30.4%（無作為10.0%、差+20.5）／P2 平均1.0頭 的中0.0%（無作為10.0%、差-10.0）／P3 平均1.0頭 的中8.7%（無作為10.0%、差-1.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中65.2%（無作為29.9%、差+35.3）／P2 平均6.0頭 的中82.6%（無作為59.8%、差+22.8）／P3 平均10.3頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.96/40（選択性補正込み）・能力順位 13.99/20（23R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.53/40（選択性補正込み）・能力順位 13.4/20（23R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（3.4%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）7R・着順まで的中 0R／的中 8R のうち的中赤字 4R／損益分岐の倍率 平均 7.6倍／同じ点数を無作為に選んだ場合の期待PFS 34.3%（同じ23Rの実績 68.9%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 119点 PFS 82.7%／WIDE 44点 PFS 48.6%／荒れ度（発走前・1番人気オッズ）MID 10R PFS 90.0% 的中赤字 2/5／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 12R PFS 59.1% 的中赤字 2/3／市場ミラーとの差 23R：実績 68.9% − ミラー 15.9% = Δ 52.9pt（95%区間 -1.0〜122.4、最高1R除き 26.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 52,200円（37.8%）／保護層の資金比率 0.0（23R）／組だけ的中（三連単は外れ）8R・着順まで的中 4R／的中 15R のうち的中赤字 11R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 34.3%（同じ23Rの実績 50.3%）／券種別 EXACTA 345点 PFS 66.3%／TRIFECTA 575点 PFS 31.2%／TRIO 460点 PFS 62.0%／荒れ度（発走前・1番人気オッズ）MID 10R PFS 58.1% 的中赤字 4/6／OPEN 1R PFS 84.2% 的中赤字 1/1／SOLID 12R PFS 40.9% 的中赤字 6/8／市場ミラーとの差 23R：実績 50.3% − ミラー 141.6% = Δ -91.3pt（95%区間 -198.5〜3.1、最高1R除き -107.1pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 11 | 37,260 | RECURRING |
| P1:ROLE_W_MISS | P1 | 8 | 33,240 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 4 | 24,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 23 | 85,260 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-24 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 15／PAPER PFS 53.4%／正式推薦 PFS 45.1%
- 第一失敗：{'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 7 | 0.0 | 36.6 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 1} |
| NGY | 2 | 0.0 | 0.0 | {'PREDICTION_ROLE_W': 2} |
| URW | 6 | 145.0 | 70.0 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'NONE': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 20／正式試行 20・発走前送信 20／本人確認 0
2. 計算完走：Full29 20／Signed FINAL 20／KRS5000 20／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 53.4%／正式推薦 45.1%／実購入なし
5. Learning：RESULT署名検証 15／学習状態保存 15／前Raceの学習状態を結合した正式Race 20（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '211/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 15 | 40.0% | 73.3% | 40.0% | 0.0% | 6.7% | 0.0% | 20.0% | 1.4 |
| 正式推薦 | 15 | 33.3% | 66.7% | 66.7% | 86.7% | 100.0% | 66.7% | 46.7% | 1.47 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中40.0%（無作為10.5%、差+29.5）／P2 平均1.0頭 的中0.0%（無作為10.5%、差-10.5）／P3 平均1.0頭 的中6.7%（無作為10.5%、差-3.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.7%（無作為31.4%、差+35.3）／P2 平均6.0頭 的中86.7%（無作為62.8%、差+23.9）／P3 平均9.87頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.27/40（選択性補正込み）・能力順位 13.59/20（15R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.78/40（選択性補正込み）・能力順位 12.47/20（15R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（5.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）4R・着順まで的中 0R／的中 4R のうち的中赤字 3R／損益分岐の倍率 平均 7.6倍／同じ点数を無作為に選んだ場合の期待PFS 43.0%（同じ15Rの実績 53.4%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 75点 PFS 69.6%／WIDE 28点 PFS 31.1%／荒れ度（発走前・1番人気オッズ）MID 4R PFS 21.1% 的中赤字 1/1／SOLID 11R PFS 64.0% 的中赤字 2/3／市場ミラーとの差 15R：実績 53.4% − ミラー 19.6% = Δ 33.9pt（95%区間 -19.8〜134.0、最高1R除き -9.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 33,600円（37.3%）／保護層の資金比率 0.0（15R）／組だけ的中（三連単は外れ）4R・着順まで的中 3R／的中 9R のうち的中赤字 6R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 35.6%（同じ15Rの実績 45.1%）／券種別 EXACTA 225点 PFS 75.8%／TRIFECTA 375点 PFS 18.9%／TRIO 300点 PFS 54.8%／荒れ度（発走前・1番人気オッズ）MID 4R PFS 56.4% 的中赤字 1/2／SOLID 11R PFS 41.0% 的中赤字 5/7／市場ミラーとの差 15R：実績 45.1% − ミラー 145.1% = Δ -100.0pt（95%区間 -235.3〜5.5、最高1R除き -84.5pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 6 | 20,720 | RECURRING |
| P1:ROLE_W_MISS | P1 | 5 | 24,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 15 | 56,720 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

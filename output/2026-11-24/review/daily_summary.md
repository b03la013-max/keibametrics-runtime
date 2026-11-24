# 地方版 2026-11-24 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 7／PAPER PFS 11.4%／正式推薦 PFS 13.5%
- 第一失敗：{'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 4 | 0.0 | 12.0 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 1} |
| URW | 3 | 31.4 | 15.6 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 11／正式試行 11・発走前送信 11／本人確認 0
2. 計算完走：Full29 11／Signed FINAL 11／KRS5000 11／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 11.4%／正式推薦 13.5%／実購入なし
5. Learning：RESULT署名検証 7／学習状態保存 7／前Raceの学習状態を結合した正式Race 11（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '211/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 7 | 42.9% | 85.7% | 42.9% | 0.0% | 0.0% | 0.0% | 14.3% | 1.57 |
| 正式推薦 | 7 | 42.9% | 71.4% | 71.4% | 85.7% | 100.0% | 71.4% | 28.6% | 1.57 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中42.9%（無作為10.7%、差+32.2）／P2 平均1.0頭 的中0.0%（無作為10.7%、差-10.7）／P3 平均1.0頭 的中0.0%（無作為10.7%、差-10.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中71.4%（無作為32.1%、差+39.3）／P2 平均6.0頭 的中85.7%（無作為64.2%、差+21.5）／P3 平均9.43頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.14/40（選択性補正込み）・能力順位 14.49/20（7R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.02/40（選択性補正込み）・能力順位 12.85/20（7R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（10.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）2R・着順まで的中 0R／的中 2R のうち的中赤字 2R／損益分岐の倍率 平均 8.3倍／同じ点数を無作為に選んだ場合の期待PFS 23.8%（同じ7Rの実績 11.4%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 35点 PFS 10.0%／WIDE 12点 PFS 25.8%／荒れ度（発走前・1番人気オッズ）SOLID 7R PFS 11.4% 的中赤字 2/2／市場ミラーとの差 7R：実績 11.4% − ミラー 26.9% = Δ -15.5pt（95%区間 -31.6〜-4.1、最高1R除き -17.6pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 15,800円（37.6%）／保護層の資金比率 0.0（7R）／組だけ的中（三連単は外れ）1R・着順まで的中 1R／的中 4R のうち的中赤字 4R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 22.2%（同じ7Rの実績 13.5%）／券種別 EXACTA 105点 PFS 35.4%／TRIFECTA 175点 PFS 7.1%／TRIO 140点 PFS 5.0%／荒れ度（発走前・1番人気オッズ）SOLID 7R PFS 13.5% 的中赤字 4/4／市場ミラーとの差 7R：実績 13.5% − ミラー 40.3% = Δ -26.8pt（95%区間 -50.0〜-5.3、最高1R除き -31.2pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 4 | 18,330 | RECURRING |
| P1:ROLE_W_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P1:ROLE_P2_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 7 | 36,330 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 1 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

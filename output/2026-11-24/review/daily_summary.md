# 地方版 2026-11-24 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 19／PAPER PFS 66.5%／正式推薦 PFS 39.3%
- 第一失敗：{'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 6, 'PREDICTION_ROLE_P2': 4, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 8 | 21.8 | 38.2 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 1} |
| NGY | 3 | 85.2 | 7.2 | {'PREDICTION_ROLE_W': 3} |
| URW | 8 | 109.8 | 52.5 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'NONE': 1, 'PREDICTION_ROLE_P2': 2} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 24／正式試行 24・発走前送信 24／本人確認 0
2. 計算完走：Full29 24／Signed FINAL 24／KRS5000 24／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 66.5%／正式推薦 39.3%／実購入なし
5. Learning：RESULT署名検証 19／学習状態保存 19／前Raceの学習状態を結合した正式Race 24（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '211/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 19 | 31.6% | 68.4% | 31.6% | 0.0% | 5.3% | 0.0% | 26.3% | 1.47 |
| 正式推薦 | 19 | 42.1% | 68.4% | 68.4% | 78.9% | 100.0% | 68.4% | 47.4% | 1.53 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中31.6%（無作為10.1%、差+21.5）／P2 平均1.0頭 的中0.0%（無作為10.1%、差-10.1）／P3 平均1.0頭 的中5.3%（無作為10.1%、差-4.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中68.4%（無作為30.3%、差+38.1）／P2 平均6.0頭 的中78.9%（無作為60.6%、差+18.3）／P3 平均10.21頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.89/40（選択性補正込み）・能力順位 13.91/20（19R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.26/40（選択性補正込み）・能力順位 13.15/20（19R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（4.2%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 7R のうち的中赤字 4R／損益分岐の倍率 平均 7.6倍／同じ点数を無作為に選んだ場合の期待PFS 36.5%（同じ19Rの実績 66.5%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 97点 PFS 78.8%／WIDE 36点 PFS 53.9%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 70.3% 的中赤字 2/4／SOLID 11R PFS 64.0% 的中赤字 2/3／市場ミラーとの差 19R：実績 66.5% − ミラー 15.5% = Δ 51.0pt（95%区間 -5.7〜129.2、最高1R除き 18.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 43,000円（37.7%）／保護層の資金比率 0.0（19R）／組だけ的中（三連単は外れ）6R・着順まで的中 3R／的中 11R のうち的中赤字 8R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 29.8%（同じ19Rの実績 39.3%）／券種別 EXACTA 285点 PFS 66.2%／TRIFECTA 475点 PFS 14.9%／TRIO 380点 PFS 49.7%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 37.0% 的中赤字 3/4／SOLID 11R PFS 41.0% 的中赤字 5/7／市場ミラーとの差 19R：実績 39.3% − ミラー 129.2% = Δ -89.9pt（95%区間 -196.4〜-4.7、最高1R除き -77.2pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 8 | 28,480 | RECURRING |
| P1:ROLE_W_MISS | P1 | 6 | 28,710 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 4 | 24,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 19 | 76,480 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

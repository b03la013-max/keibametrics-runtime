# 地方版 2026-11-24 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 8／PAPER PFS 84.6%／正式推薦 PFS 29.9%
- 第一失敗：{'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 4 | 0.0 | 12.0 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 1} |
| URW | 4 | 196.4 | 47.8 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 1, 'NONE': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 13／正式試行 13・発走前送信 13／本人確認 0
2. 計算完走：Full29 13／Signed FINAL 13／KRS5000 13／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 84.6%／正式推薦 29.9%／実購入なし
5. Learning：RESULT署名検証 8／学習状態保存 8／前Raceの学習状態を結合した正式Race 13（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '211/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 8 | 50.0% | 87.5% | 50.0% | 0.0% | 12.5% | 0.0% | 25.0% | 1.62 |
| 正式推薦 | 8 | 37.5% | 75.0% | 75.0% | 87.5% | 100.0% | 75.0% | 37.5% | 1.5 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中50.0%（無作為11.4%、差+38.6）／P2 平均1.0頭 的中0.0%（無作為11.4%、差-11.4）／P3 平均1.0頭 的中12.5%（無作為11.4%、差+1.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中75.0%（無作為34.3%、差+40.7）／P2 平均6.0頭 的中87.5%（無作為68.7%、差+18.8）／P3 平均9.0頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.88/40（選択性補正込み）・能力順位 14.18/20（8R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.34/40（選択性補正込み）・能力順位 12.35/20（8R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（9.2%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）3R・着順まで的中 0R／的中 3R のうち的中赤字 2R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 42.2%（同じ8Rの実績 84.6%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 40点 PFS 119.2%／WIDE 14点 PFS 52.1%／荒れ度（発走前・1番人気オッズ）SOLID 8R PFS 84.6% 的中赤字 2/3／市場ミラーとの差 8R：実績 84.6% − ミラー 24.0% = Δ 60.6pt（95%区間 -27.7〜248.6、最高1R除き -15.5pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 18,300円（38.1%）／保護層の資金比率 0.0（8R）／組だけ的中（三連単は外れ）2R・着順まで的中 1R／的中 5R のうち的中赤字 4R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 41.3%（同じ8Rの実績 29.9%）／券種別 EXACTA 120点 PFS 66.3%／TRIFECTA 200点 PFS 6.2%／TRIO 160点 PFS 32.0%／荒れ度（発走前・1番人気オッズ）SOLID 8R PFS 29.9% 的中赤字 4/5／市場ミラーとの差 8R：実績 29.9% − ミラー 92.9% = Δ -63.0pt（95%区間 -140.2〜-10.6、最高1R除き -26.8pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 4 | 18,330 | RECURRING |
| P1:ROLE_W_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P1:ROLE_P2_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 8 | 36,330 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

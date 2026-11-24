# 地方版 2026-11-24 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 3／PAPER PFS 8.6%／正式推薦 PFS 9.6%
- 第一失敗：{'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 2 | 0.0 | 6.5 | {'CAPITAL_EFFICIENCY': 1, 'PREDICTION_ROLE_W': 1} |
| URW | 1 | 25.7 | 15.7 | {'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 7／正式試行 7・発走前送信 7／本人確認 0
2. 計算完走：Full29 7／Signed FINAL 7／KRS5000 7／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 8.6%／正式推薦 9.6%／実購入なし
5. Learning：RESULT署名検証 3／学習状態保存 3／前Raceの学習状態を結合した正式Race 7（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '183/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 3 | 66.7% | 100.0% | 66.7% | 0.0% | 0.0% | 0.0% | 0.0% | 1.33 |
| 正式推薦 | 3 | 33.3% | 66.7% | 66.7% | 100.0% | 100.0% | 66.7% | 33.3% | 1.67 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中66.7%（無作為10.7%、差+55.9）／P2 平均1.0頭 的中0.0%（無作為10.7%、差-10.7）／P3 平均1.0頭 的中0.0%（無作為10.7%、差-10.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.7%（無作為32.2%、差+34.4）／P2 平均6.0頭 的中100.0%（無作為64.4%、差+35.6）／P3 平均9.33頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.33/40（選択性補正込み）・能力順位 13.78/20（3R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.11/40（選択性補正込み）・能力順位 12.9/20（3R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）0R・着順まで的中 0R／的中 1R のうち的中赤字 1R／損益分岐の倍率 平均 7.0倍／同じ点数を無作為に選んだ場合の期待PFS 37.7%（同じ3Rの実績 8.6%）／券種別 TRIO 15点 PFS 0.0%／WIDE 6点 PFS 30.0%／荒れ度（発走前・1番人気オッズ）SOLID 3R PFS 8.6% 的中赤字 1/1／市場ミラーとの差 3R：実績 8.6% − ミラー 30.0% = Δ -21.4pt（95%区間 -64.3〜0.0、最高1R除き 0.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 6,800円（37.8%）／保護層の資金比率 0.0（3R）／組だけ的中（三連単は外れ）1R・着順まで的中 0R／的中 2R のうち的中赤字 2R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 33.2%（同じ3Rの実績 9.6%）／券種別 EXACTA 45点 PFS 28.2%／TRIFECTA 75点 PFS 0.0%／TRIO 60点 PFS 7.5%／荒れ度（発走前・1番人気オッズ）SOLID 3R PFS 9.6% 的中赤字 2/2／市場ミラーとの差 3R：実績 9.6% − ミラー 39.5% = Δ -29.9pt（95%区間 -68.7〜0.0、最高1R除き -34.3pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 2 | 10,280 | SINGLE_OR_FEW (過大評価しない) |
| P1:ROLE_W_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 3 | 16,280 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

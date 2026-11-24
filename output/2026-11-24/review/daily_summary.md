# 地方版 2026-11-24 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 12／PAPER PFS 59.1%／正式推薦 PFS 37.6%
- 第一失敗：{'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 6 | 0.0 | 19.9 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 2} |
| NGY | 1 | 0.0 | 0.0 | {'PREDICTION_ROLE_W': 1} |
| URW | 5 | 157.1 | 66.3 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 2, 'NONE': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 17／正式試行 17・発走前送信 17／本人確認 0
2. 計算完走：Full29 17／Signed FINAL 17／KRS5000 17／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 59.1%／正式推薦 37.6%／実購入なし
5. Learning：RESULT署名検証 12／学習状態保存 12／前Raceの学習状態を結合した正式Race 17（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '211/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 12 | 50.0% | 83.3% | 50.0% | 0.0% | 8.3% | 0.0% | 16.7% | 1.42 |
| 正式推薦 | 12 | 33.3% | 66.7% | 66.7% | 83.3% | 100.0% | 66.7% | 41.7% | 1.42 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中50.0%（無作為10.8%、差+39.2）／P2 平均1.0頭 的中0.0%（無作為10.8%、差-10.8）／P3 平均1.0頭 的中8.3%（無作為10.8%、差-2.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.7%（無作為32.4%、差+34.2）／P2 平均6.0頭 的中83.3%（無作為64.9%、差+18.4）／P3 平均9.5頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.5/40（選択性補正込み）・能力順位 13.76/20（12R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.25/40（選択性補正込み）・能力順位 12.33/20（12R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（6.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）3R・着順まで的中 0R／的中 3R のうち的中赤字 2R／損益分岐の倍率 平均 7.8倍／同じ点数を無作為に選んだ場合の期待PFS 47.2%（同じ12Rの実績 59.1%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 60点 PFS 79.5%／WIDE 22点 PFS 33.2%／荒れ度（発走前・1番人気オッズ）MID 1R PFS 0.0% 的中赤字 0/0／SOLID 11R PFS 64.0% 的中赤字 2/3／市場ミラーとの差 12R：実績 59.1% − ミラー 16.8% = Δ 42.4pt（95%区間 -18.5〜167.5、最高1R除き -10.5pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 27,100円（37.6%）／保護層の資金比率 0.0（12R）／組だけ的中（三連単は外れ）3R・着順まで的中 2R／的中 7R のうち的中赤字 5R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 38.3%（同じ12Rの実績 37.6%）／券種別 EXACTA 180点 PFS 49.5%／TRIFECTA 300点 PFS 13.3%／TRIO 240点 PFS 59.0%／荒れ度（発走前・1番人気オッズ）MID 1R PFS 0.0% 的中赤字 0/0／SOLID 11R PFS 41.0% 的中赤字 5/7／市場ミラーとの差 12R：実績 37.6% − ミラー 121.2% = Δ -83.6pt（95%区間 -212.7〜6.5、最高1R除き -62.4pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 5 | 20,040 | RECURRING |
| P1:ROLE_W_MISS | P1 | 4 | 18,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 12 | 50,040 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-23 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 6／PAPER PFS 66.5%／正式推薦 PFS 11.1%
- 第一失敗：{'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 2 | 55.2 | 11.2 | {'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 1} |
| MIZ | 4 | 75.7 | 11.1 | {'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 33R／PAPER発走前送信 9／正式試行 9・発走前送信 9／本人確認 0
2. 計算完走：Full29 9／Signed FINAL 9／KRS5000 9／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 66.5%／正式推薦 11.1%／実購入なし
5. Learning：RESULT署名検証 6／学習状態保存 6／前Raceの学習状態を結合した正式Race 9（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '30R到達', 'C23-THIRD3-BY-PAIR': '30R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '30R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '165/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 6 | 66.7% | 100.0% | 66.7% | 16.7% | 16.7% | 16.7% | 16.7% | 1.33 |
| 正式推薦 | 6 | 50.0% | 83.3% | 83.3% | 50.0% | 100.0% | 83.3% | 33.3% | 1.17 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中66.7%（無作為10.6%、差+56.1）／P2 平均1.0頭 的中16.7%（無作為10.6%、差+6.1）／P3 平均1.0頭 的中16.7%（無作為10.6%、差+6.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中83.3%（無作為31.7%、差+51.7）／P2 平均6.0頭 的中50.0%（無作為63.3%、差-13.3）／P3 平均9.5頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 17.33/40（選択性補正込み）・能力順位 14.14/20（6R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.74/40（選択性補正込み）・能力順位 12.3/20（6R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（11.8%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）1R・着順まで的中 0R／的中 2R のうち的中赤字 0R／損益分岐の倍率 平均 8.5倍／同じ点数を無作為に選んだ場合の期待PFS 50.1%（同じ6Rの実績 66.5%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 30点 PFS 38.0%／WIDE 10点 PFS 225.0%／荒れ度（発走前・1番人気オッズ）MID 1R PFS 302.9% 的中赤字 0/1／SOLID 5R PFS 28.9% 的中赤字 0/1／市場ミラーとの差 6R：実績 66.5% − ミラー 120.8% = Δ -54.3pt（95%区間 -251.9〜128.1、最高1R除き -111.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 13,800円（38.3%）／保護層の資金比率 0.0（6R）／組だけ的中（三連単は外れ）1R・着順まで的中 1R／的中 2R のうち的中赤字 2R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 37.0%（同じ6Rの実績 11.1%）／券種別 EXACTA 90点 PFS 5.0%／TRIFECTA 150点 PFS 10.6%／TRIO 120点 PFS 16.4%／荒れ度（発走前・1番人気オッズ）MID 1R PFS 0.0% 的中赤字 0/0／SOLID 5R PFS 13.4% 的中赤字 2/2／市場ミラーとの差 6R：実績 11.1% − ミラー 73.8% = Δ -62.7pt（95%区間 -152.7〜8.5、最高1R除き -83.3pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 2 | 7,990 | SINGLE_OR_FEW (過大評価しない) |
| P1:ROLE_W_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 6 | 31,990 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

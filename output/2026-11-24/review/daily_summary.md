# 地方版 2026-11-24 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 11／PAPER PFS 64.0%／正式推薦 PFS 34.5%
- 第一失敗：{'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 5 | 0.0 | 9.6 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 2} |
| NGY | 1 | 0.0 | 0.0 | {'PREDICTION_ROLE_W': 1} |
| URW | 5 | 157.1 | 66.3 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 2, 'NONE': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 17／正式試行 17・発走前送信 17／本人確認 0
2. 計算完走：Full29 17／Signed FINAL 17／KRS5000 17／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 64.0%／正式推薦 34.5%／実購入なし
5. Learning：RESULT署名検証 12／学習状態保存 12／前Raceの学習状態を結合した正式Race 17（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '211/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 11 | 45.5% | 81.8% | 45.5% | 0.0% | 9.1% | 0.0% | 18.2% | 1.45 |
| 正式推薦 | 11 | 27.3% | 63.6% | 63.6% | 81.8% | 100.0% | 63.6% | 36.4% | 1.36 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中45.5%（無作為10.9%、差+34.6）／P2 平均1.0頭 的中0.0%（無作為10.9%、差-10.9）／P3 平均1.0頭 的中9.1%（無作為10.9%、差-1.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.6%（無作為32.7%、差+31.0）／P2 平均6.0頭 的中81.8%（無作為65.3%、差+16.5）／P3 平均9.45頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.27/40（選択性補正込み）・能力順位 13.7/20（11R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.65/40（選択性補正込み）・能力順位 11.98/20（11R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（7.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）3R・着順まで的中 0R／的中 3R のうち的中赤字 2R／損益分岐の倍率 平均 7.8倍／同じ点数を無作為に選んだ場合の期待PFS 50.3%（同じ11Rの実績 64.0%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 55点 PFS 86.7%／WIDE 20点 PFS 36.5%／荒れ度（発走前・1番人気オッズ）MID 1R PFS 0.0% 的中赤字 0/0／SOLID 10R PFS 69.6% 的中赤字 2/3／市場ミラーとの差 11R：実績 64.0% − ミラー 18.1% = Δ 45.8pt（95%区間 -20.1〜176.9、最高1R除き -11.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 24,900円（37.7%）／保護層の資金比率 0.0（11R）／組だけ的中（三連単は外れ）3R・着順まで的中 1R／的中 6R のうち的中赤字 4R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 41.2%（同じ11Rの実績 34.5%）／券種別 EXACTA 165点 PFS 48.2%／TRIFECTA 275点 PFS 4.5%／TRIO 220点 PFS 61.6%／荒れ度（発走前・1番人気オッズ）MID 1R PFS 0.0% 的中赤字 0/0／SOLID 10R PFS 37.9% 的中赤字 4/6／市場ミラーとの差 11R：実績 34.5% − ミラー 131.3% = Δ -96.8pt（95%区間 -230.1〜2.7、最高1R除き -74.8pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 4 | 18,330 | RECURRING |
| P1:ROLE_W_MISS | P1 | 4 | 18,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 11 | 48,330 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

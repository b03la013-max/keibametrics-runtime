# 地方版 2026-11-24 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 30／PAPER PFS 57.0%／正式推薦 PFS 58.5%
- 第一失敗：{'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_W': 11, 'PREDICTION_ROLE_P2': 5, 'NONE': 5}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 12 | 24.7 | 61.3 | {'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 2, 'NONE': 2} |
| NGY | 7 | 35.1 | 49.0 | {'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 1, 'NONE': 1} |
| URW | 11 | 112.0 | 61.4 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 3, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 33／正式試行 33・発走前送信 33／本人確認 0
2. 計算完走：Full29 33／Signed FINAL 33／KRS5000 33／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 57.0%／正式推薦 58.5%／実購入なし
5. Learning：RESULT署名検証 30／学習状態保存 30／前Raceの学習状態を結合した正式Race 33（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '211/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 30 | 33.3% | 70.0% | 33.3% | 0.0% | 6.7% | 6.7% | 23.3% | 1.47 |
| 正式推薦 | 30 | 43.3% | 63.3% | 63.3% | 76.7% | 100.0% | 63.3% | 46.7% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.3%（無作為9.6%、差+23.7）／P2 平均1.0頭 的中0.0%（無作為9.6%、差-9.6）／P3 平均1.0頭 的中6.7%（無作為9.6%、差-3.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.3%（無作為28.9%、差+34.4）／P2 平均6.0頭 的中76.7%（無作為57.8%、差+18.9）／P3 平均10.67頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.07/40（選択性補正込み）・能力順位 13.95/20（30R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.2/40（選択性補正込み）・能力順位 13.43/20（30R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,200円（5.2%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）7R・着順まで的中 1R／的中 10R のうち的中赤字 6R／損益分岐の倍率 平均 7.8倍／同じ点数を無作為に選んだ場合の期待PFS 32.0%（同じ30Rの実績 57.0%）／券種別 EXACTA 8点 PFS 33.8%／TRIFECTA 16点 PFS 36.9%／TRIO 154点 PFS 65.5%／WIDE 54点 PFS 39.6%／WIN 1点 PFS 190.0%／荒れ度（発走前・1番人気オッズ）MID 15R PFS 61.8% 的中赤字 3/6／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 14R PFS 56.9% 的中赤字 3/4／市場ミラーとの差 30R：実績 57.0% − ミラー 17.3% = Δ 39.7pt（95%区間 -2.6〜92.8、最高1R除き 19.5pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 68,200円（37.9%）／保護層の資金比率 0.0（30R）／組だけ的中（三連単は外れ）8R・着順まで的中 6R／的中 18R のうち的中赤字 12R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 31.7%（同じ30Rの実績 58.5%）／券種別 EXACTA 450点 PFS 84.7%／TRIFECTA 750点 PFS 46.6%／TRIO 600点 PFS 53.6%／荒れ度（発走前・1番人気オッズ）MID 15R PFS 63.5% 的中赤字 4/7／OPEN 1R PFS 84.2% 的中赤字 1/1／SOLID 14R PFS 51.3% 的中赤字 7/10／市場ミラーとの差 30R：実績 58.5% − ミラー 126.9% = Δ -68.4pt（95%区間 -157.6〜14.8、最高1R除き -82.2pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 12 | 42,160 | RECURRING |
| P1:ROLE_W_MISS | P1 | 11 | 51,240 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 30 | 114,160 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

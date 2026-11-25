# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 25／PAPER PFS 61.0%／正式推薦 PFS 40.3%
- 第一失敗：{'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_W': 14, 'NONE': 1, 'PREDICTION_ROLE_P2': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 4 | 38.2 | 44.5 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 1} |
| SON | 12 | 63.2 | 60.5 | {'PREDICTION_ROLE_W': 9, 'NONE': 1, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 1} |
| URW | 9 | 66.4 | 11.6 | {'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 29／正式試行 29・発走前送信 29／本人確認 0
2. 計算完走：Full29 29／Signed FINAL 29／KRS5000 29／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 61.0%／正式推薦 40.3%／実購入なし
5. Learning：RESULT署名検証 25／学習状態保存 25／前Raceの学習状態を結合した正式Race 29（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 25 | 12.0% | 56.0% | 12.0% | 20.0% | 8.0% | 8.0% | 20.0% | 1.36 |
| 正式推薦 | 25 | 16.0% | 44.0% | 44.0% | 84.0% | 100.0% | 44.0% | 44.0% | 1.16 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中12.0%（無作為9.0%、差+3.0）／P2 平均1.0頭 的中20.0%（無作為9.0%、差+11.0）／P3 平均1.0頭 的中8.0%（無作為9.0%、差-1.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中44.0%（無作為27.0%、差+17.0）／P2 平均6.0頭 的中84.0%（無作為54.0%、差+30.0）／P3 平均11.32頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 10.64/40（選択性補正込み）・能力順位 12.87/20（25R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.1/40（選択性補正込み）・能力順位 12.6/20（25R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（11.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 9R のうち的中赤字 5R／損益分岐の倍率 平均 8.8倍／同じ点数を無作為に選んだ場合の期待PFS 115.0%（同じ25Rの実績 61.0%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 131点 PFS 60.5%／WIDE 38点 PFS 138.4%／WIN 2点 PFS 80.0%／荒れ度（発走前・1番人気オッズ）MID 14R PFS 66.2% 的中赤字 2/4／OPEN 2R PFS 0.0% 的中赤字 0/0／SOLID 8R PFS 77.3% 的中赤字 3/5／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 24R：実績 65.8% − ミラー 35.5% = Δ 30.3pt（95%区間 -20.3〜86.4、最高1R除き 12.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 57,900円（38.6%）／保護層の資金比率 0.0（25R）／組だけ的中（三連単は外れ）9R・着順まで的中 2R／的中 16R のうち的中赤字 14R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 121.7%（同じ25Rの実績 40.3%）／券種別 EXACTA 375点 PFS 49.2%／TRIFECTA 625点 PFS 7.0%／TRIO 500点 PFS 75.3%／荒れ度（発走前・1番人気オッズ）MID 14R PFS 30.5% 的中赤字 7/8／OPEN 2R PFS 0.0% 的中赤字 0/0／SOLID 8R PFS 69.3% 的中赤字 6/7／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 24R：実績 40.9% − ミラー 34.6% = Δ 6.3pt（95%区間 -35.4〜52.4、最高1R除き -9.7pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 14 | 66,860 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 14 | 52,470 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 25 | 106,470 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

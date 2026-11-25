# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 31／PAPER PFS 52.6%／正式推薦 PFS 33.1%
- 第一失敗：{'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_W': 17, 'PREDICTION_ROLE_P2': 3, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 7 | 29.8 | 25.4 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 2} |
| SON | 12 | 63.2 | 60.5 | {'PREDICTION_ROLE_W': 9, 'NONE': 1, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 1} |
| URW | 12 | 50.3 | 10.2 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 6} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 33／正式試行 33・発走前送信 33／本人確認 0
2. 計算完走：Full29 33／Signed FINAL 33／KRS5000 33／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 52.6%／正式推薦 33.1%／実購入なし
5. Learning：RESULT署名検証 31／学習状態保存 31／前Raceの学習状態を結合した正式Race 33（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 31 | 19.4% | 58.1% | 19.4% | 16.1% | 6.5% | 6.5% | 16.1% | 1.39 |
| 正式推薦 | 31 | 16.1% | 45.2% | 45.2% | 74.2% | 100.0% | 45.2% | 35.5% | 1.23 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中19.4%（無作為8.9%、差+10.4）／P2 平均1.0頭 的中16.1%（無作為8.9%、差+7.2）／P3 平均1.0頭 的中6.5%（無作為8.9%、差-2.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中45.2%（無作為26.8%、差+18.4）／P2 平均6.0頭 的中74.2%（無作為53.5%、差+20.7）／P3 平均11.42頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.32/40（選択性補正込み）・能力順位 12.95/20（31R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.62/40（選択性補正込み）・能力順位 12.5/20（31R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（9.2%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 11R のうち的中赤字 7R／損益分岐の倍率 平均 8.4倍／同じ点数を無作為に選んだ場合の期待PFS 98.9%（同じ31Rの実績 52.6%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 161点 PFS 49.3%／WIDE 50点 PFS 113.0%／WIN 2点 PFS 80.0%／荒れ度（発走前・1番人気オッズ）MID 17R PFS 58.8% 的中赤字 4/6／OPEN 2R PFS 0.0% 的中赤字 0/0／SOLID 11R PFS 60.4% 的中赤字 3/5／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 30R：実績 56.1% − ミラー 39.5% = Δ 16.6pt（95%区間 -24.8〜70.0、最高1R除き 1.5pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 71,700円（38.5%）／保護層の資金比率 0.0（31R）／組だけ的中（三連単は外れ）10R・着順まで的中 2R／的中 17R のうち的中赤字 15R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 99.9%（同じ31Rの実績 33.1%）／券種別 EXACTA 465点 PFS 42.0%／TRIFECTA 775点 PFS 5.7%／TRIO 620点 PFS 60.7%／荒れ度（発走前・1番人気オッズ）MID 17R PFS 25.1% 的中赤字 7/8／OPEN 2R PFS 0.0% 的中赤字 0/0／SOLID 11R PFS 52.0% 的中赤字 7/8／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 30R：実績 33.3% − ミラー 35.3% = Δ -2.0pt（95%区間 -36.9〜35.2、最高1R除き -15.0pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 17 | 84,860 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 15 | 57,400 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 31 | 141,400 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

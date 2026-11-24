# 地方版 2026-11-24 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 26／PAPER PFS 64.7%／正式推薦 PFS 45.2%
- 第一失敗：{'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_W': 9, 'PREDICTION_ROLE_P2': 5, 'NONE': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 10 | 28.6 | 36.4 | {'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 2, 'NONE': 1} |
| NGY | 6 | 40.7 | 22.5 | {'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 1} |
| URW | 10 | 122.7 | 67.5 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 31／正式試行 31・発走前送信 31／本人確認 0
2. 計算完走：Full29 31／Signed FINAL 31／KRS5000 31／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 64.7%／正式推薦 45.2%／実購入なし
5. Learning：RESULT署名検証 26／学習状態保存 26／前Raceの学習状態を結合した正式Race 31（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '211/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 26 | 34.6% | 73.1% | 34.6% | 0.0% | 7.7% | 7.7% | 26.9% | 1.54 |
| 正式推薦 | 26 | 42.3% | 65.4% | 65.4% | 76.9% | 100.0% | 65.4% | 50.0% | 1.46 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中34.6%（無作為9.8%、差+24.8）／P2 平均1.0頭 的中0.0%（無作為9.8%、差-9.8）／P3 平均1.0頭 的中7.7%（無作為9.8%、差-2.2）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中65.4%（無作為29.5%、差+35.8）／P2 平均6.0頭 的中76.9%（無作為59.1%、差+17.8）／P3 平均10.42頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.58/40（選択性補正込み）・能力順位 14.14/20（26R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.3/40（選択性補正込み）・能力順位 13.38/20（26R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,200円（5.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）7R・着順まで的中 1R／的中 10R のうち的中赤字 6R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 33.0%（同じ26Rの実績 64.7%）／券種別 EXACTA 8点 PFS 33.8%／TRIFECTA 16点 PFS 36.9%／TRIO 134点 PFS 75.2%／WIDE 46点 PFS 46.5%／WIN 1点 PFS 190.0%／荒れ度（発走前・1番人気オッズ）MID 12R PFS 76.7% 的中赤字 3/6／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 13R PFS 60.6% 的中赤字 3/4／市場ミラーとの差 26R：実績 64.7% − ミラー 14.4% = Δ 50.3pt（95%区間 5.7〜111.9、最高1R除き 27.6pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 58,900円（37.8%）／保護層の資金比率 0.0（26R）／組だけ的中（三連単は外れ）8R・着順まで的中 5R／的中 16R のうち的中赤字 12R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 32.7%（同じ26Rの実績 45.2%）／券種別 EXACTA 390点 PFS 59.4%／TRIFECTA 650点 PFS 28.5%／TRIO 520点 PFS 55.3%／荒れ度（発走前・1番人気オッズ）MID 12R PFS 48.4% 的中赤字 4/6／OPEN 1R PFS 84.2% 的中赤字 1/1／SOLID 13R PFS 39.2% 的中赤字 7/9／市場ミラーとの差 26R：実績 45.2% − ミラー 126.4% = Δ -81.3pt（95%区間 -180.1〜1.4、最高1R除き -94.7pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 12 | 42,160 | RECURRING |
| P1:ROLE_W_MISS | P1 | 9 | 39,240 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 26 | 102,160 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

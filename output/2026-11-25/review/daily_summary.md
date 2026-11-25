# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 20／PAPER PFS 44.1%／正式推薦 PFS 36.4%
- 第一失敗：{'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 11, 'NONE': 1, 'PREDICTION_ROLE_P2': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 3 | 51.0 | 26.7 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 1} |
| SON | 10 | 22.8 | 54.2 | {'PREDICTION_ROLE_W': 8, 'NONE': 1, 'PREDICTION_ROLE_P2': 1} |
| URW | 7 | 87.6 | 14.9 | {'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 2} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 25／正式試行 25・発走前送信 25／本人確認 0
2. 計算完走：Full29 25／Signed FINAL 25／KRS5000 25／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 44.1%／正式推薦 36.4%／実購入なし
5. Learning：RESULT署名検証 20／学習状態保存 20／前Raceの学習状態を結合した正式Race 25（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 20 | 15.0% | 60.0% | 15.0% | 25.0% | 10.0% | 10.0% | 20.0% | 1.45 |
| 正式推薦 | 20 | 20.0% | 45.0% | 45.0% | 90.0% | 100.0% | 45.0% | 40.0% | 1.2 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中15.0%（無作為9.1%、差+5.9）／P2 平均1.0頭 的中25.0%（無作為9.1%、差+15.9）／P3 平均1.0頭 的中10.0%（無作為9.1%、差+0.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中45.0%（無作為27.3%、差+17.7）／P2 平均6.0頭 的中90.0%（無作為54.6%、差+35.4）／P3 平均11.2頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.9/40（選択性補正込み）・能力順位 13.23/20（20R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.33/40（選択性補正込み）・能力順位 12.65/20（20R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（13.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）5R・着順まで的中 0R／的中 7R のうち的中赤字 5R／損益分岐の倍率 平均 9.0倍／同じ点数を無作為に選んだ場合の期待PFS 88.8%（同じ20Rの実績 44.1%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 102点 PFS 62.5%／WIDE 28点 PFS 49.6%／WIN 2点 PFS 80.0%／荒れ度（発走前・1番人気オッズ）MID 11R PFS 53.1% 的中赤字 2/3／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 7R PFS 47.1% 的中赤字 3/4／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 19R：実績 48.4% − ミラー 36.6% = Δ 11.7pt（95%区間 -30.1〜69.2、最高1R除き -11.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 46,100円（38.4%）／保護層の資金比率 0.0（20R）／組だけ的中（三連単は外れ）7R・着順まで的中 1R／的中 13R のうち的中赤字 12R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 87.1%（同じ20Rの実績 36.4%）／券種別 EXACTA 300点 PFS 48.0%／TRIFECTA 500点 PFS 1.2%／TRIO 400点 PFS 71.5%／荒れ度（発走前・1番人気オッズ）MID 11R PFS 20.1% 的中赤字 6/6／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 7R PFS 68.5% 的中赤字 5/6／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 19R：実績 36.9% − ミラー 38.6% = Δ -1.7pt（95%区間 -53.4〜56.2、最高1R除き -22.6pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 12 | 50,840 | RECURRING |
| P1:ROLE_W_MISS | P1 | 11 | 54,860 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 20 | 92,840 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

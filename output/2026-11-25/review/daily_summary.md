# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 17／PAPER PFS 23.0%／正式推薦 PFS 41.5%
- 第一失敗：{'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 9, 'NONE': 1, 'PREDICTION_ROLE_P2': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 2 | 36.4 | 29.7 | {'CAPITAL_EFFICIENCY': 1, 'PREDICTION_ROLE_W': 1} |
| SON | 9 | 24.3 | 60.3 | {'PREDICTION_ROLE_W': 7, 'NONE': 1, 'PREDICTION_ROLE_P2': 1} |
| URW | 6 | 15.6 | 17.4 | {'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 22／正式試行 22・発走前送信 22／本人確認 0
2. 計算完走：Full29 22／Signed FINAL 22／KRS5000 22／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 23.0%／正式推薦 41.5%／実購入なし
5. Learning：RESULT署名検証 17／学習状態保存 17／前Raceの学習状態を結合した正式Race 22（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 17 | 17.6% | 58.8% | 17.6% | 29.4% | 5.9% | 11.8% | 11.8% | 1.41 |
| 正式推薦 | 17 | 23.5% | 47.1% | 47.1% | 94.1% | 100.0% | 47.1% | 41.2% | 1.24 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中17.6%（無作為9.2%、差+8.4）／P2 平均1.0頭 的中29.4%（無作為9.2%、差+20.2）／P3 平均1.0頭 的中5.9%（無作為9.2%、差-3.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中47.1%（無作為27.7%、差+19.4）／P2 平均6.0頭 的中94.1%（無作為55.4%、差+38.7）／P3 平均11.06頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.71/40（選択性補正込み）・能力順位 13.09/20（17R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.8/40（選択性補正込み）・能力順位 12.69/20（17R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（15.1%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）3R・着順まで的中 0R／的中 5R のうち的中赤字 4R／損益分岐の倍率 平均 9.4倍／同じ点数を無作為に選んだ場合の期待PFS 89.1%（同じ17Rの実績 23.0%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 87点 PFS 30.6%／WIDE 22点 PFS 38.2%／WIN 2点 PFS 80.0%／荒れ度（発走前・1番人気オッズ）MID 10R PFS 12.4% 的中赤字 2/2／SOLID 6R PFS 43.3% 的中赤字 2/3／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 16R：実績 25.6% − ミラー 40.1% = Δ -14.5pt（95%区間 -43.5〜7.0、最高1R除き -16.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 39,100円（38.3%）／保護層の資金比率 0.0（17R）／組だけ的中（三連単は外れ）7R・着順まで的中 0R／的中 12R のうち的中赤字 11R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 89.2%（同じ17Rの実績 41.5%）／券種別 EXACTA 255点 PFS 55.8%／TRIFECTA 425点 PFS 0.0%／TRIO 340点 PFS 82.8%／荒れ度（発走前・1番人気オッズ）MID 10R PFS 22.1% 的中赤字 6/6／SOLID 6R PFS 76.4% 的中赤字 4/5／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 16R：実績 42.5% − ミラー 45.8% = Δ -3.3pt（95%区間 -62.0〜62.8、最高1R除き -28.5pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 11 | 46,080 | RECURRING |
| P1:ROLE_W_MISS | P1 | 9 | 42,860 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 17 | 76,080 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

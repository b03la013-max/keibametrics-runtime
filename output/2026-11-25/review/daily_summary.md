# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 35／PAPER PFS 47.4%／正式推薦 PFS 32.7%
- 第一失敗：{'CAPITAL_EFFICIENCY': 11, 'PREDICTION_ROLE_W': 18, 'PREDICTION_ROLE_P2': 4, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 11 | 18.7 | 27.0 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 3, 'NONE': 1} |
| SON | 12 | 63.2 | 60.5 | {'PREDICTION_ROLE_W': 9, 'NONE': 1, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 1} |
| URW | 12 | 50.3 | 10.2 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 6} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 36／正式試行 36・発走前送信 36／本人確認 0
2. 計算完走：Full29 36／Signed FINAL 36／KRS5000 36／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 47.4%／正式推薦 32.7%／実購入なし
5. Learning：RESULT署名検証 35／学習状態保存 35／前Raceの学習状態を結合した正式Race 36（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 35 | 17.1% | 54.3% | 17.1% | 14.3% | 5.7% | 5.7% | 14.3% | 1.37 |
| 正式推薦 | 35 | 17.1% | 48.6% | 48.6% | 71.4% | 100.0% | 48.6% | 37.1% | 1.29 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中17.1%（無作為8.9%、差+8.3）／P2 平均1.0頭 的中14.3%（無作為8.9%、差+5.4）／P3 平均1.0頭 的中5.7%（無作為8.9%、差-3.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中48.6%（無作為26.6%、差+22.0）／P2 平均6.0頭 的中71.4%（無作為53.1%、差+18.3）／P3 平均11.49頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 10.77/40（選択性補正込み）・能力順位 12.9/20（35R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.96/40（選択性補正込み）・能力順位 12.61/20（35R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（8.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 11R のうち的中赤字 7R／損益分岐の倍率 平均 8.3倍／同じ点数を無作為に選んだ場合の期待PFS 92.8%（同じ35Rの実績 47.4%）／券種別 EXACTA 18点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 181点 PFS 43.8%／WIDE 56点 PFS 100.9%／WIN 3点 PFS 53.3%／荒れ度（発走前・1番人気オッズ）MID 18R PFS 55.5% 的中赤字 4/6／OPEN 2R PFS 0.0% 的中赤字 0/0／SOLID 14R PFS 49.6% 的中赤字 3/5／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 34R：実績 50.1% − ミラー 38.7% = Δ 11.5pt（95%区間 -27.3〜57.5、最高1R除き -2.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 81,000円（38.6%）／保護層の資金比率 0.0（35R）／組だけ的中（三連単は外れ）11R・着順まで的中 3R／的中 19R のうち的中赤字 16R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 91.9%（同じ35Rの実績 32.7%）／券種別 EXACTA 525点 PFS 41.9%／TRIFECTA 875点 PFS 9.3%／TRIO 700点 PFS 55.1%／荒れ度（発走前・1番人気オッズ）MID 18R PFS 23.8% 的中赤字 7/8／OPEN 2R PFS 0.0% 的中赤字 0/0／SOLID 14R PFS 49.3% 的中赤字 8/10／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 34R：実績 32.9% − ミラー 36.0% = Δ -3.1pt（95%区間 -33.6〜30.8、最高1R除き -14.5pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 18 | 90,860 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 16 | 62,560 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 4 | 24,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 35 | 158,560 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

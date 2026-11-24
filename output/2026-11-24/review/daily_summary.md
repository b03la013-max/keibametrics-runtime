# 地方版 2026-11-24 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 35／PAPER PFS 56.0%／正式推薦 PFS 54.9%
- 第一失敗：{'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 6, 'NONE': 6}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 12 | 24.7 | 61.3 | {'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 2, 'NONE': 2} |
| NGY | 11 | 30.0 | 46.3 | {'PREDICTION_ROLE_W': 6, 'CAPITAL_EFFICIENCY': 2, 'NONE': 2, 'PREDICTION_ROLE_P2': 1} |
| URW | 12 | 116.2 | 56.3 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 36／正式試行 36・発走前送信 36／本人確認 0
2. 計算完走：Full29 36／Signed FINAL 36／KRS5000 36／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 56.0%／正式推薦 54.9%／実購入なし
5. Learning：RESULT署名検証 35／学習状態保存 35／前Raceの学習状態を結合した正式Race 36（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '211/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 35 | 31.4% | 65.7% | 31.4% | 2.9% | 5.7% | 5.7% | 22.9% | 1.46 |
| 正式推薦 | 35 | 40.0% | 62.9% | 62.9% | 77.1% | 100.0% | 62.9% | 45.7% | 1.51 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中31.4%（無作為9.5%、差+22.0）／P2 平均1.0頭 的中2.9%（無作為9.5%、差-6.6）／P3 平均1.0頭 的中5.7%（無作為9.5%、差-3.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中62.9%（無作為28.4%、差+34.5）／P2 平均6.0頭 的中77.1%（無作為56.8%、差+20.3）／P3 平均10.83頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.83/40（選択性補正込み）・能力順位 13.97/20（35R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.32/40（選択性補正込み）・能力順位 13.55/20（35R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,200円（4.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）8R・着順まで的中 1R／的中 12R のうち的中赤字 7R／損益分岐の倍率 平均 7.7倍／同じ点数を無作為に選んだ場合の期待PFS 30.6%（同じ35Rの実績 56.0%）／券種別 EXACTA 8点 PFS 33.8%／TRIFECTA 16点 PFS 36.9%／TRIO 179点 PFS 58.6%／WIDE 64点 PFS 54.1%／WIN 1点 PFS 190.0%／荒れ度（発走前・1番人気オッズ）MID 18R PFS 65.1% 的中赤字 4/8／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 16R PFS 50.8% 的中赤字 3/4／市場ミラーとの差 35R：実績 56.0% − ミラー 19.6% = Δ 36.3pt（95%区間 -2.6〜88.4、最高1R除き 18.8pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 79,600円（37.9%）／保護層の資金比率 0.0（35R）／組だけ的中（三連単は外れ）10R・着順まで的中 7R／的中 20R のうち的中赤字 13R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 29.5%（同じ35Rの実績 54.9%）／券種別 EXACTA 525点 PFS 76.4%／TRIFECTA 875点 PFS 46.6%／TRIO 700点 PFS 49.0%／荒れ度（発走前・1番人気オッズ）MID 18R PFS 62.1% 的中赤字 5/9／OPEN 1R PFS 84.2% 的中赤字 1/1／SOLID 16R PFS 44.9% 的中赤字 7/10／市場ミラーとの差 35R：実績 54.9% − ミラー 115.4% = Δ -60.5pt（95%区間 -138.5〜6.5、最高1R除き -72.0pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 13 | 63,240 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 13 | 46,320 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 6 | 36,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 35 | 136,320 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

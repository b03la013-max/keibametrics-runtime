# 地方版 2026-11-24 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 31／PAPER PFS 60.1%／正式推薦 PFS 56.6%
- 第一失敗：{'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_W': 12, 'PREDICTION_ROLE_P2': 5, 'NONE': 5}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 12 | 24.7 | 61.3 | {'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 2, 'NONE': 2} |
| NGY | 7 | 35.1 | 49.0 | {'PREDICTION_ROLE_W': 5, 'CAPITAL_EFFICIENCY': 1, 'NONE': 1} |
| URW | 12 | 116.2 | 56.3 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 33／正式試行 33・発走前送信 33／本人確認 0
2. 計算完走：Full29 33／Signed FINAL 33／KRS5000 33／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 60.1%／正式推薦 56.6%／実購入なし
5. Learning：RESULT署名検証 31／学習状態保存 31／前Raceの学習状態を結合した正式Race 33（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '211/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 31 | 32.3% | 67.7% | 32.3% | 0.0% | 6.5% | 6.5% | 22.6% | 1.45 |
| 正式推薦 | 31 | 41.9% | 61.3% | 61.3% | 77.4% | 100.0% | 61.3% | 45.2% | 1.45 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.3%（無作為9.6%、差+22.7）／P2 平均1.0頭 的中0.0%（無作為9.6%、差-9.6）／P3 平均1.0頭 的中6.5%（無作為9.6%、差-3.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中61.3%（無作為28.8%、差+32.5）／P2 平均6.0頭 的中77.4%（無作為57.5%、差+19.9）／P3 平均10.71頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.87/40（選択性補正込み）・能力順位 13.88/20（31R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.04/40（選択性補正込み）・能力順位 13.43/20（31R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,200円（5.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）7R・着順まで的中 1R／的中 11R のうち的中赤字 6R／損益分岐の倍率 平均 7.7倍／同じ点数を無作為に選んだ場合の期待PFS 32.2%（同じ31Rの実績 60.1%）／券種別 EXACTA 8点 PFS 33.8%／TRIFECTA 16点 PFS 36.9%／TRIO 159点 PFS 63.4%／WIDE 56点 PFS 58.8%／WIN 1点 PFS 190.0%／荒れ度（発走前・1番人気オッズ）MID 16R PFS 68.0% 的中赤字 3/7／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 14R PFS 56.9% 的中赤字 3/4／市場ミラーとの差 31R：実績 60.1% − ミラー 18.6% = Δ 41.5pt（95%区間 0.8〜94.7、最高1R除き 21.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 70,400円（37.8%）／保護層の資金比率 0.0（31R）／組だけ的中（三連単は外れ）8R・着順まで的中 6R／的中 18R のうち的中赤字 12R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 32.1%（同じ31Rの実績 56.6%）／券種別 EXACTA 465点 PFS 81.9%／TRIFECTA 775点 PFS 45.1%／TRIO 620点 PFS 51.9%／荒れ度（発走前・1番人気オッズ）MID 16R PFS 59.5% 的中赤字 4/7／OPEN 1R PFS 84.2% 的中赤字 1/1／SOLID 14R PFS 51.3% 的中赤字 7/10／市場ミラーとの差 31R：実績 56.6% − ミラー 122.8% = Δ -66.2pt（95%区間 -157.6〜12.3、最高1R除き -79.4pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 12 | 57,240 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 12 | 42,160 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 31 | 120,160 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

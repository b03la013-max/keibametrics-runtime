# 地方版 2026-11-24 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 22／PAPER PFS 71.7%／正式推薦 PFS 51.2%
- 第一失敗：{'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 8, 'PREDICTION_ROLE_P2': 4, 'NONE': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 9 | 19.7 | 38.4 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 2, 'NONE': 1} |
| NGY | 4 | 59.7 | 26.4 | {'PREDICTION_ROLE_W': 4} |
| URW | 9 | 134.9 | 75.1 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'NONE': 2, 'PREDICTION_ROLE_P2': 2} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 27／正式試行 27・発走前送信 27／本人確認 0
2. 計算完走：Full29 27／Signed FINAL 27／KRS5000 27／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 71.7%／正式推薦 51.2%／実購入なし
5. Learning：RESULT署名検証 22／学習状態保存 22／前Raceの学習状態を結合した正式Race 27（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '211/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 22 | 27.3% | 68.2% | 27.3% | 0.0% | 9.1% | 0.0% | 27.3% | 1.5 |
| 正式推薦 | 22 | 36.4% | 63.6% | 63.6% | 81.8% | 100.0% | 63.6% | 54.5% | 1.5 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中27.3%（無作為10.0%、差+17.3）／P2 平均1.0頭 的中0.0%（無作為10.0%、差-10.0）／P3 平均1.0頭 的中9.1%（無作為10.0%、差-0.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.6%（無作為29.9%、差+33.7）／P2 平均6.0頭 的中81.8%（無作為59.8%、差+22.0）／P3 平均10.32頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.77/40（選択性補正込み）・能力順位 13.99/20（22R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.41/40（選択性補正込み）・能力順位 13.34/20（22R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（3.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）7R・着順まで的中 0R／的中 8R のうち的中赤字 4R／損益分岐の倍率 平均 7.6倍／同じ点数を無作為に選んだ場合の期待PFS 35.1%（同じ22Rの実績 71.7%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 114点 PFS 86.3%／WIDE 42点 PFS 51.0%／荒れ度（発走前・1番人気オッズ）MID 9R PFS 99.7% 的中赤字 2/5／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 12R PFS 59.1% 的中赤字 2/3／市場ミラーとの差 22R：実績 71.7% − ミラー 14.7% = Δ 57.1pt（95%区間 1.8〜133.6、最高1R除き 29.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 49,800円（37.7%）／保護層の資金比率 0.0（22R）／組だけ的中（三連単は外れ）8R・着順まで的中 4R／的中 14R のうち的中赤字 10R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 35.3%（同じ22Rの実績 51.2%）／券種別 EXACTA 330点 PFS 64.0%／TRIFECTA 550点 PFS 32.6%／TRIO 440点 PFS 64.9%／荒れ度（発走前・1番人気オッズ）MID 9R PFS 61.3% 的中赤字 3/5／OPEN 1R PFS 84.2% 的中赤字 1/1／SOLID 12R PFS 40.9% 的中赤字 6/8／市場ミラーとの差 22R：実績 51.2% − ミラー 145.7% = Δ -94.5pt（95%区間 -206.1〜-1.3、最高1R除き -111.1pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 10 | 33,010 | RECURRING |
| P1:ROLE_W_MISS | P1 | 8 | 33,240 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 4 | 24,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 22 | 81,010 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

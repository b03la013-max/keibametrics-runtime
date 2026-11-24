# 地方版 2026-11-24 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 33／PAPER PFS 59.1%／正式推薦 PFS 54.1%
- 第一失敗：{'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 5, 'NONE': 5}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 12 | 24.7 | 61.3 | {'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 2, 'NONE': 2} |
| NGY | 9 | 36.5 | 41.5 | {'PREDICTION_ROLE_W': 6, 'CAPITAL_EFFICIENCY': 2, 'NONE': 1} |
| URW | 12 | 116.2 | 56.3 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 34／正式試行 34・発走前送信 34／本人確認 0
2. 計算完走：Full29 34／Signed FINAL 34／KRS5000 34／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 59.1%／正式推薦 54.1%／実購入なし
5. Learning：RESULT署名検証 33／学習状態保存 33／前Raceの学習状態を結合した正式Race 34（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '211/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 33 | 30.3% | 63.6% | 30.3% | 3.0% | 6.1% | 6.1% | 24.2% | 1.45 |
| 正式推薦 | 33 | 39.4% | 60.6% | 60.6% | 78.8% | 100.0% | 60.6% | 45.5% | 1.48 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中30.3%（無作為9.5%、差+20.8）／P2 平均1.0頭 的中3.0%（無作為9.5%、差-6.5）／P3 平均1.0頭 的中6.1%（無作為9.5%、差-3.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.6%（無作為28.5%、差+32.1）／P2 平均6.0頭 的中78.8%（無作為57.1%、差+21.7）／P3 平均10.79頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.82/40（選択性補正込み）・能力順位 13.98/20（33R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.06/40（選択性補正込み）・能力順位 13.39/20（33R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,200円（4.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）8R・着順まで的中 1R／的中 12R のうち的中赤字 7R／損益分岐の倍率 平均 7.7倍／同じ点数を無作為に選んだ場合の期待PFS 30.8%（同じ33Rの実績 59.1%）／券種別 EXACTA 8点 PFS 33.8%／TRIFECTA 16点 PFS 36.9%／TRIO 169点 PFS 62.1%／WIDE 60点 PFS 57.7%／WIN 1点 PFS 190.0%／荒れ度（発走前・1番人気オッズ）MID 17R PFS 68.9% 的中赤字 4/8／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 15R PFS 53.7% 的中赤字 3/4／市場ミラーとの差 33R：実績 59.1% − ミラー 19.9% = Δ 39.1pt（95%区間 -0.9〜91.4、最高1R除き 20.6pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 74,800円（37.8%）／保護層の資金比率 0.0（33R）／組だけ的中（三連単は外れ）9R・着順まで的中 6R／的中 19R のうち的中赤字 13R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 30.5%（同じ33Rの実績 54.1%）／券種別 EXACTA 495点 PFS 79.9%／TRIFECTA 825点 PFS 42.4%／TRIO 660点 PFS 49.4%／荒れ度（発走前・1番人気オッズ）MID 17R PFS 57.8% 的中赤字 5/8／OPEN 1R PFS 84.2% 的中赤字 1/1／SOLID 15R PFS 47.9% 的中赤字 7/10／市場ミラーとの差 33R：実績 54.1% − ミラー 118.5% = Δ -64.4pt（95%区間 -145.1〜6.5、最高1R除き -76.7pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 13 | 63,240 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 13 | 46,320 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 5 | 30,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 33 | 130,320 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 22／PAPER PFS 53.7%／正式推薦 PFS 36.4%
- 第一失敗：{'CAPITAL_EFFICIENCY': 8, 'PREDICTION_ROLE_W': 12, 'NONE': 1, 'PREDICTION_ROLE_P2': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 3 | 51.0 | 26.7 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 1} |
| SON | 11 | 43.8 | 56.1 | {'PREDICTION_ROLE_W': 8, 'NONE': 1, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 1} |
| URW | 8 | 74.2 | 13.1 | {'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 3} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 27／正式試行 27・発走前送信 27／本人確認 0
2. 計算完走：Full29 27／Signed FINAL 27／KRS5000 27／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 53.7%／正式推薦 36.4%／実購入なし
5. Learning：RESULT署名検証 22／学習状態保存 22／前Raceの学習状態を結合した正式Race 27（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 22 | 13.6% | 59.1% | 13.6% | 22.7% | 9.1% | 9.1% | 22.7% | 1.45 |
| 正式推薦 | 22 | 18.2% | 45.5% | 45.5% | 86.4% | 100.0% | 45.5% | 40.9% | 1.18 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中13.6%（無作為9.1%、差+4.6）／P2 平均1.0頭 的中22.7%（無作為9.1%、差+13.7）／P3 平均1.0頭 的中9.1%（無作為9.1%、差+0.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中45.5%（無作為27.2%、差+18.3）／P2 平均6.0頭 的中86.4%（無作為54.3%、差+32.1）／P3 平均11.27頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.59/40（選択性補正込み）・能力順位 13.12/20（22R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.14/40（選択性補正込み）・能力順位 12.63/20（22R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（12.2%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 8R のうち的中赤字 5R／損益分岐の倍率 平均 8.9倍／同じ点数を無作為に選んだ場合の期待PFS 87.0%（同じ22Rの実績 53.7%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 114点 PFS 69.6%／WIDE 32点 PFS 76.2%／WIN 2点 PFS 80.0%／荒れ度（発走前・1番人気オッズ）MID 12R PFS 48.3% 的中赤字 2/3／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 8R PFS 77.3% 的中赤字 3/5／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 21R：実績 58.5% − ミラー 33.4% = Δ 25.1pt（95%区間 -20.9〜84.0、最高1R除き 4.7pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 50,700円（38.4%）／保護層の資金比率 0.0（22R）／組だけ的中（三連単は外れ）8R・着順まで的中 1R／的中 14R のうち的中赤字 13R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 87.5%（同じ22Rの実績 36.4%）／券種別 EXACTA 330点 PFS 52.6%／TRIFECTA 550点 PFS 1.1%／TRIO 440点 PFS 68.5%／荒れ度（発走前・1番人気オッズ）MID 12R PFS 18.4% 的中赤字 6/6／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 8R PFS 69.3% 的中赤字 6/7／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 21R：実績 36.9% − ミラー 34.9% = Δ 2.0pt（95%区間 -43.5〜54.3、最高1R除き -16.6pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 13 | 52,350 | RECURRING |
| P1:ROLE_W_MISS | P1 | 12 | 60,860 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 22 | 100,350 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

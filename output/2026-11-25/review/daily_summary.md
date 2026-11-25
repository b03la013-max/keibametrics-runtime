# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 23／PAPER PFS 51.9%／正式推薦 PFS 39.1%
- 第一失敗：{'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_W': 12, 'NONE': 1, 'PREDICTION_ROLE_P2': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 4 | 38.2 | 44.5 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 1} |
| SON | 11 | 43.8 | 56.1 | {'PREDICTION_ROLE_W': 8, 'NONE': 1, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 1} |
| URW | 8 | 74.2 | 13.1 | {'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 3} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 28／正式試行 28・発走前送信 28／本人確認 0
2. 計算完走：Full29 28／Signed FINAL 28／KRS5000 28／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 51.9%／正式推薦 39.1%／実購入なし
5. Learning：RESULT署名検証 23／学習状態保存 23／前Raceの学習状態を結合した正式Race 28（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 23 | 13.0% | 60.9% | 13.0% | 21.7% | 8.7% | 8.7% | 21.7% | 1.43 |
| 正式推薦 | 23 | 17.4% | 47.8% | 47.8% | 87.0% | 100.0% | 47.8% | 43.5% | 1.22 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中13.0%（無作為9.1%、差+4.0）／P2 平均1.0頭 的中21.7%（無作為9.1%、差+12.7）／P3 平均1.0頭 的中8.7%（無作為9.1%、差-0.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中47.8%（無作為27.2%、差+20.7）／P2 平均6.0頭 的中87.0%（無作為54.3%、差+32.6）／P3 平均11.26頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.43/40（選択性補正込み）・能力順位 13.17/20（23R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.5/40（選択性補正込み）・能力順位 12.8/20（23R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（11.8%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 8R のうち的中赤字 5R／損益分岐の倍率 平均 8.8倍／同じ点数を無作為に選んだ場合の期待PFS 84.3%（同じ23Rの実績 51.9%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 119点 PFS 66.6%／WIDE 34点 PFS 71.8%／WIN 2点 PFS 80.0%／荒れ度（発走前・1番人気オッズ）MID 13R PFS 45.0% 的中赤字 2/3／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 8R PFS 77.3% 的中赤字 3/5／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 22R：実績 56.3% − ミラー 38.5% = Δ 17.8pt（95%区間 -30.6〜76.5、最高1R除き -2.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 53,100円（38.5%）／保護層の資金比率 0.0（23R）／組だけ的中（三連単は外れ）8R・着順まで的中 2R／的中 15R のうち的中赤字 14R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 83.9%（同じ23Rの実績 39.1%）／券種別 EXACTA 345点 PFS 53.4%／TRIFECTA 575点 PFS 7.7%／TRIO 460点 PFS 67.7%／荒れ度（発走前・1番人気オッズ）MID 13R PFS 24.6% 的中赤字 7/7／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 8R PFS 69.3% 的中赤字 6/7／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 22R：実績 39.7% − ミラー 37.8% = Δ 1.9pt（95%区間 -43.7〜51.6、最高1R除き -15.8pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 14 | 52,470 | RECURRING |
| P1:ROLE_W_MISS | P1 | 12 | 60,860 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 23 | 100,470 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

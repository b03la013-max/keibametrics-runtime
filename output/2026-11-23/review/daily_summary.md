# 地方版 2026-11-23 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 7／PAPER PFS 58.4%／正式推薦 PFS 9.5%
- 第一失敗：{'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 2 | 55.2 | 11.2 | {'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 1} |
| MIZ | 5 | 60.6 | 8.9 | {'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 33R／PAPER発走前送信 10／正式試行 10・発走前送信 10／本人確認 0
2. 計算完走：Full29 10／Signed FINAL 10／KRS5000 10／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 58.4%／正式推薦 9.5%／実購入なし
5. Learning：RESULT署名検証 7／学習状態保存 7／前Raceの学習状態を結合した正式Race 10（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '30R到達', 'C23-THIRD3-BY-PAIR': '30R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '30R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '165/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 7 | 57.1% | 85.7% | 57.1% | 14.3% | 14.3% | 14.3% | 14.3% | 1.43 |
| 正式推薦 | 7 | 42.9% | 71.4% | 71.4% | 42.9% | 100.0% | 71.4% | 28.6% | 1.14 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中57.1%（無作為10.5%、差+46.7）／P2 平均1.0頭 的中14.3%（無作為10.5%、差+3.8）／P3 平均1.0頭 的中14.3%（無作為10.5%、差+3.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中71.4%（無作為31.4%、差+40.0）／P2 平均6.0頭 的中42.9%（無作為62.9%、差-20.0）／P3 平均9.57頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.43/40（選択性補正込み）・能力順位 13.57/20（7R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.02/40（選択性補正込み）・能力順位 11.52/20（7R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（10.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）1R・着順まで的中 0R／的中 2R のうち的中赤字 0R／損益分岐の倍率 平均 8.3倍／同じ点数を無作為に選んだ場合の期待PFS 51.3%（同じ7Rの実績 58.4%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 35点 PFS 32.6%／WIDE 12点 PFS 187.5%／荒れ度（発走前・1番人気オッズ）MID 1R PFS 302.9% 的中赤字 0/1／SOLID 6R PFS 24.9% 的中赤字 0/1／市場ミラーとの差 7R：実績 58.4% − ミラー 106.2% = Δ -47.8pt（95%区間 -237.8〜106.1、最高1R除き -95.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 16,200円（38.6%）／保護層の資金比率 0.0（7R）／組だけ的中（三連単は外れ）1R・着順まで的中 1R／的中 2R のうち的中赤字 2R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 41.9%（同じ7Rの実績 9.5%）／券種別 EXACTA 105点 PFS 4.3%／TRIFECTA 175点 PFS 9.1%／TRIO 140点 PFS 14.1%／荒れ度（発走前・1番人気オッズ）MID 1R PFS 0.0% 的中赤字 0/0／SOLID 6R PFS 11.1% 的中赤字 2/2／市場ミラーとの差 7R：実績 9.5% − ミラー 224.3% = Δ -214.7pt（95%区間 -526.3〜-6.1、最高1R除き -257.2pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P1:HIT_BUT_LOSS | P1 | 2 | 7,990 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 7 | 37,990 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

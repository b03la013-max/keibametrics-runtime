# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 18／PAPER PFS 44.4%／正式推薦 PFS 39.2%
- 第一失敗：{'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 10, 'NONE': 1, 'PREDICTION_ROLE_P2': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 2 | 36.4 | 29.7 | {'CAPITAL_EFFICIENCY': 1, 'PREDICTION_ROLE_W': 1} |
| SON | 9 | 24.3 | 60.3 | {'PREDICTION_ROLE_W': 7, 'NONE': 1, 'PREDICTION_ROLE_P2': 1} |
| URW | 7 | 87.6 | 14.9 | {'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 2} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 23／正式試行 23・発走前送信 23／本人確認 0
2. 計算完走：Full29 23／Signed FINAL 23／KRS5000 23／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 44.4%／正式推薦 39.2%／実購入なし
5. Learning：RESULT署名検証 18／学習状態保存 18／前Raceの学習状態を結合した正式Race 23（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 18 | 16.7% | 61.1% | 16.7% | 27.8% | 5.6% | 11.1% | 16.7% | 1.44 |
| 正式推薦 | 18 | 22.2% | 44.4% | 44.4% | 94.4% | 100.0% | 44.4% | 38.9% | 1.22 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中16.7%（無作為9.2%、差+7.5）／P2 平均1.0頭 的中27.8%（無作為9.2%、差+18.6）／P3 平均1.0頭 的中5.6%（無作為9.2%、差-3.6）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中44.4%（無作為27.6%、差+16.9）／P2 平均6.0頭 的中94.4%（無作為55.1%、差+39.3）／P3 平均11.11頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.83/40（選択性補正込み）・能力順位 13.33/20（18R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.62/40（選択性補正込み）・能力順位 12.75/20（18R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（14.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）4R・着順まで的中 0R／的中 6R のうち的中赤字 4R／損益分岐の倍率 平均 9.2倍／同じ点数を無作為に選んだ場合の期待PFS 86.3%（同じ18Rの実績 44.4%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 92点 PFS 64.6%／WIDE 24点 PFS 52.9%／WIN 2点 PFS 80.0%／荒れ度（発走前・1番人気オッズ）MID 11R PFS 53.1% 的中赤字 2/3／SOLID 6R PFS 43.3% 的中赤字 2/3／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 17R：実績 49.1% − ミラー 38.2% = Δ 10.9pt（95%区間 -33.4〜75.9、最高1R除き -14.5pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 41,400円（38.3%）／保護層の資金比率 0.0（18R）／組だけ的中（三連単は外れ）7R・着順まで的中 0R／的中 12R のうち的中赤字 11R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 85.2%（同じ18Rの実績 39.2%）／券種別 EXACTA 270点 PFS 52.7%／TRIFECTA 450点 PFS 0.0%／TRIO 360点 PFS 78.2%／荒れ度（発走前・1番人気オッズ）MID 11R PFS 20.1% 的中赤字 6/6／SOLID 6R PFS 76.4% 的中赤字 4/5／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 17R：実績 40.0% − ミラー 43.1% = Δ -3.1pt（95%区間 -58.7〜55.3、最高1R除き -26.7pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 11 | 46,080 | RECURRING |
| P1:ROLE_W_MISS | P1 | 10 | 48,860 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 18 | 82,080 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

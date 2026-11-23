# 地方版 2026-11-23 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 29／PAPER PFS 35.0%／正式推薦 PFS 41.5%
- 第一失敗：{'PREDICTION_ROLE_P2': 8, 'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_W': 11, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 12 | 69.0 | 11.2 | {'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 3} |
| SAG | 7 | 0.0 | 17.8 | {'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_P2': 2} |

## 日次自律監査

1. 配送：管理 33R／PAPER発走前送信 31／正式試行 31・発走前送信 31／本人確認 0
2. 計算完走：Full29 31／Signed FINAL 31／KRS5000 31／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 35.0%／正式推薦 41.5%／実購入なし
5. Learning：RESULT署名検証 29／学習状態保存 29／前Raceの学習状態を結合した正式Race 31（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '165/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 29 | 34.5% | 65.5% | 34.5% | 6.9% | 17.2% | 10.3% | 20.7% | 1.45 |
| 正式推薦 | 29 | 34.5% | 62.1% | 62.1% | 69.0% | 100.0% | 62.1% | 41.4% | 1.52 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中34.5%（無作為10.4%、差+24.1）／P2 平均1.0頭 的中6.9%（無作為10.4%、差-3.5）／P3 平均1.0頭 的中17.2%（無作為10.4%、差+6.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中62.1%（無作為31.1%、差+30.9）／P2 平均6.0頭 的中69.0%（無作為62.3%、差+6.7）／P3 平均9.79頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.59/40（選択性補正込み）・能力順位 13.47/20（29R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.11/40（選択性補正込み）・能力順位 13.14/20（29R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,800円（7.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 8R のうち的中赤字 3R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 49.9%（同じ29Rの実績 35.0%）／券種別 EXACTA 13点 PFS 0.0%／TRIFECTA 24点 PFS 0.0%／TRIO 149点 PFS 31.9%／WIDE 48点 PFS 73.1%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 10R PFS 31.9% 的中赤字 1/2／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 16R PFS 23.5% 的中赤字 2/4／市場ミラーとの差 29R：実績 35.0% − ミラー 72.5% = Δ -37.5pt（95%区間 -88.1〜9.5、最高1R除き -47.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 66,200円（38.0%）／保護層の資金比率 0.0（29R）／組だけ的中（三連単は外れ）10R・着順まで的中 5R／的中 13R のうち的中赤字 12R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 44.8%（同じ29Rの実績 41.5%）／券種別 EXACTA 435点 PFS 27.3%／TRIFECTA 725点 PFS 13.9%／TRIO 580点 PFS 86.6%／荒れ度（発走前・1番人気オッズ）MID 10R PFS 97.2% 的中赤字 4/5／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 16R PFS 12.9% 的中赤字 7/7／市場ミラーとの差 29R：実績 41.5% − ミラー 84.7% = Δ -43.2pt（95%区間 -143.1〜47.4、最高1R除き -73.2pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 12 | 47,580 | RECURRING |
| P1:ROLE_W_MISS | P1 | 11 | 63,280 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 8 | 48,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 29 | 143,580 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

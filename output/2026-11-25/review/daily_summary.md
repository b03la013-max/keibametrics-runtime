# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 29／PAPER PFS 54.8%／正式推薦 PFS 35.4%
- 第一失敗：{'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_W': 16, 'PREDICTION_ROLE_P2': 2, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 6 | 30.0 | 29.7 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1} |
| SON | 12 | 63.2 | 60.5 | {'PREDICTION_ROLE_W': 9, 'NONE': 1, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 1} |
| URW | 11 | 54.8 | 11.1 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 5} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 32／正式試行 32・発走前送信 32／本人確認 0
2. 計算完走：Full29 32／Signed FINAL 32／KRS5000 32／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 54.8%／正式推薦 35.4%／実購入なし
5. Learning：RESULT署名検証 29／学習状態保存 29／前Raceの学習状態を結合した正式Race 32（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 29 | 17.2% | 58.6% | 17.2% | 17.2% | 6.9% | 6.9% | 17.2% | 1.38 |
| 正式推薦 | 29 | 13.8% | 44.8% | 44.8% | 79.3% | 100.0% | 44.8% | 37.9% | 1.21 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中17.2%（無作為9.0%、差+8.2）／P2 平均1.0頭 的中17.2%（無作為9.0%、差+8.2）／P3 平均1.0頭 的中6.9%（無作為9.0%、差-2.1）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中44.8%（無作為27.0%、差+17.8）／P2 平均6.0頭 的中79.3%（無作為54.0%、差+25.3）／P3 平均11.31頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.14/40（選択性補正込み）・能力順位 12.83/20（29R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.7/40（選択性補正込み）・能力順位 12.36/20（29R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（9.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 10R のうち的中赤字 6R／損益分岐の倍率 平均 8.5倍／同じ点数を無作為に選んだ場合の期待PFS 103.8%（同じ29Rの実績 54.8%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 151点 PFS 52.5%／WIDE 46点 PFS 118.5%／WIN 2点 PFS 80.0%／荒れ度（発走前・1番人気オッズ）MID 16R PFS 60.5% 的中赤字 3/5／OPEN 2R PFS 0.0% 的中赤字 0/0／SOLID 10R PFS 65.2% 的中赤字 3/5／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 28R：実績 58.6% − ミラー 39.0% = Δ 19.6pt（95%区間 -27.6〜73.0、最高1R除き 3.7pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 67,000円（38.5%）／保護層の資金比率 0.0（29R）／組だけ的中（三連単は外れ）10R・着順まで的中 2R／的中 17R のうち的中赤字 15R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 106.0%（同じ29Rの実績 35.4%）／券種別 EXACTA 435点 PFS 44.9%／TRIFECTA 725点 PFS 6.1%／TRIO 580点 PFS 64.9%／荒れ度（発走前・1番人気オッズ）MID 16R PFS 26.7% 的中赤字 7/8／OPEN 2R PFS 0.0% 的中赤字 0/0／SOLID 10R PFS 57.2% 的中赤字 7/8／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 28R：実績 35.7% − ミラー 35.6% = Δ 0.1pt（95%区間 -36.3〜40.1、最高1R除き -13.7pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 16 | 78,860 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 15 | 57,400 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 29 | 129,400 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-23 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 32／PAPER PFS 40.3%／正式推薦 PFS 39.3%
- 第一失敗：{'PREDICTION_ROLE_P2': 8, 'CAPITAL_EFFICIENCY': 11, 'PREDICTION_ROLE_W': 12, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 12 | 69.0 | 11.2 | {'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 3} |
| SAG | 10 | 26.1 | 17.9 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 2} |

## 日次自律監査

1. 配送：管理 33R／PAPER発走前送信 33／正式試行 33・発走前送信 33／本人確認 0
2. 計算完走：Full29 33／Signed FINAL 33／KRS5000 33／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 40.3%／正式推薦 39.3%／実購入なし
5. Learning：RESULT署名検証 32／学習状態保存 32／前Raceの学習状態を結合した正式Race 33（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '165/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 32 | 34.4% | 68.8% | 34.4% | 15.6% | 15.6% | 9.4% | 25.0% | 1.53 |
| 正式推薦 | 32 | 31.2% | 62.5% | 62.5% | 71.9% | 100.0% | 62.5% | 43.8% | 1.59 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中34.4%（無作為10.3%、差+24.0）／P2 平均1.0頭 的中15.6%（無作為10.3%、差+5.3）／P3 平均1.0頭 的中15.6%（無作為10.3%、差+5.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中62.5%（無作為31.0%、差+31.5）／P2 平均6.0頭 的中71.9%（無作為62.0%、差+9.8）／P3 平均9.81頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.31/40（選択性補正込み）・能力順位 13.76/20（32R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.35/40（選択性補正込み）・能力順位 13.26/20（32R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,800円（7.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）8R・着順まで的中 0R／的中 10R のうち的中赤字 4R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 46.8%（同じ32Rの実績 40.3%）／券種別 EXACTA 13点 PFS 0.0%／TRIFECTA 24点 PFS 0.0%／TRIO 164点 PFS 39.2%／WIDE 54点 PFS 72.6%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 13R PFS 47.0% 的中赤字 2/4／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 16R PFS 23.5% 的中赤字 2/4／市場ミラーとの差 32R：実績 40.3% − ミラー 71.7% = Δ -31.4pt（95%区間 -78.9〜13.9、最高1R除き -40.8pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 72,900円（38.0%）／保護層の資金比率 0.0（32R）／組だけ的中（三連単は外れ）12R・着順まで的中 5R／的中 15R のうち的中赤字 14R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 41.1%（同じ32Rの実績 39.3%）／券種別 EXACTA 480点 PFS 28.0%／TRIFECTA 800点 PFS 12.6%／TRIO 640点 PFS 81.1%／荒れ度（発走前・1番人気オッズ）MID 13R PFS 78.9% 的中赤字 6/7／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 16R PFS 12.9% 的中赤字 7/7／市場ミラーとの差 32R：実績 39.3% − ミラー 81.7% = Δ -42.4pt（95%区間 -136.1〜38.6、最高1R除き -69.5pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 14 | 56,310 | RECURRING |
| P1:ROLE_W_MISS | P1 | 12 | 69,280 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 8 | 48,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 32 | 158,310 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

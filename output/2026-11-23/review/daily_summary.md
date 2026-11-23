# 地方版 2026-11-23 日次総括（自動・推薦試算・実購入なし）

- 反省済みRace 33／PAPER PFS 39.2%／正式推薦 PFS 38.1%
- 第一失敗：{'PREDICTION_ROLE_P2': 9, 'CAPITAL_EFFICIENCY': 11, 'PREDICTION_ROLE_W': 12, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 10 | 20.2 | 94.3 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| MIZ | 12 | 69.0 | 11.2 | {'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 3} |
| SAG | 11 | 24.0 | 16.3 | {'PREDICTION_ROLE_W': 3, 'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_P2': 3} |

## 日次自律監査

1. 配送：管理 33R／PAPER発走前送信 33／正式試行 33・発走前送信 33／本人確認 0
2. 計算完走：Full29 33／Signed FINAL 33／KRS5000 33／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 39.2%／正式推薦 38.1%／実購入なし
5. Learning：RESULT署名検証 33／学習状態保存 33／前Raceの学習状態を結合した正式Race 33（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '165/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 33 | 36.4% | 69.7% | 36.4% | 15.2% | 15.2% | 9.1% | 24.2% | 1.52 |
| 正式推薦 | 33 | 33.3% | 63.6% | 63.6% | 69.7% | 100.0% | 63.6% | 42.4% | 1.58 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中36.4%（無作為10.2%、差+26.1）／P2 平均1.0頭 的中15.2%（無作為10.2%、差+4.9）／P3 平均1.0頭 的中15.2%（無作為10.2%、差+4.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.6%（無作為30.7%、差+32.9）／P2 平均6.0頭 的中69.7%（無作為61.5%、差+8.2）／P3 平均9.94頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.36/40（選択性補正込み）・能力順位 13.75/20（33R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.44/40（選択性補正込み）・能力順位 13.31/20（33R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,800円（6.8%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）8R・着順まで的中 0R／的中 10R のうち的中赤字 4R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 46.3%（同じ33Rの実績 39.2%）／券種別 EXACTA 13点 PFS 0.0%／TRIFECTA 24点 PFS 0.0%／TRIO 169点 PFS 38.0%／WIDE 56点 PFS 70.0%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 14R PFS 43.8% 的中赤字 2/4／OPEN 3R PFS 114.8% 的中赤字 0/2／SOLID 16R PFS 23.5% 的中赤字 2/4／市場ミラーとの差 33R：実績 39.2% − ミラー 69.8% = Δ -30.6pt（95%区間 -77.4〜14.8、最高1R除き -39.7pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 75,000円（37.9%）／保護層の資金比率 0.0（33R）／組だけ的中（三連単は外れ）12R・着順まで的中 5R／的中 15R のうち的中赤字 14R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 40.5%（同じ33Rの実績 38.1%）／券種別 EXACTA 495点 PFS 27.2%／TRIFECTA 825点 PFS 12.2%／TRIO 660点 PFS 78.7%／荒れ度（発走前・1番人気オッズ）MID 14R PFS 73.3% 的中赤字 6/7／OPEN 3R PFS 8.4% 的中赤字 1/1／SOLID 16R PFS 12.9% 的中赤字 7/7／市場ミラーとの差 33R：実績 38.1% − ミラー 81.2% = Δ -43.1pt（95%区間 -137.0〜36.1、最高1R除き -69.3pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 14 | 56,310 | RECURRING |
| P1:ROLE_W_MISS | P1 | 12 | 69,280 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 9 | 54,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 33 | 164,310 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

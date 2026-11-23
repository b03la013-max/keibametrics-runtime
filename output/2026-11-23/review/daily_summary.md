# 地方版 2026-11-23 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 16／PAPER PFS 50.1%／正式推薦 PFS 12.1%
- 第一失敗：{'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 6}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 5 | 37.3 | 4.5 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1, 'PREDICTION_ROLE_W': 2} |
| MIZ | 9 | 70.6 | 10.9 | {'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 2} |
| SAG | 2 | 0.0 | 36.3 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 33R／PAPER発走前送信 21／正式試行 21・発走前送信 21／本人確認 0
2. 計算完走：Full29 21／Signed FINAL 21／KRS5000 21／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 50.1%／正式推薦 12.1%／実購入なし
5. Learning：RESULT署名検証 16／学習状態保存 16／前Raceの学習状態を結合した正式Race 21（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '165/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 16 | 37.5% | 68.8% | 37.5% | 6.2% | 18.8% | 6.2% | 25.0% | 1.44 |
| 正式推薦 | 16 | 37.5% | 62.5% | 62.5% | 56.2% | 100.0% | 62.5% | 25.0% | 1.38 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中37.5%（無作為10.5%、差+27.0）／P2 平均1.0頭 的中6.2%（無作為10.5%、差-4.2）／P3 平均1.0頭 的中18.8%（無作為10.5%、差+8.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中62.5%（無作為31.4%、差+31.1）／P2 平均6.0頭 的中56.2%（無作為62.7%、差-6.5）／P3 平均9.69頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.81/40（選択性補正込み）・能力順位 13.32/20（16R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.17/40（選択性補正込み）・能力順位 12.64/20（16R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（4.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）4R・着順まで的中 0R／的中 6R のうち的中赤字 2R／損益分岐の倍率 平均 7.7倍／同じ点数を無作為に選んだ場合の期待PFS 56.0%（同じ16Rの実績 50.1%）／券種別 EXACTA 7点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 80点 PFS 37.5%／WIDE 26点 PFS 121.5%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 5R PFS 64.7% 的中赤字 1/2／OPEN 1R PFS 128.6% 的中赤字 0/1／SOLID 10R PFS 36.6% 的中赤字 1/3／市場ミラーとの差 16R：実績 50.1% − ミラー 73.8% = Δ -23.7pt（95%区間 -111.5〜47.8、最高1R除き -43.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 36,400円（37.9%）／保護層の資金比率 0.0（16R）／組だけ的中（三連単は外れ）4R・着順まで的中 3R／的中 4R のうち的中赤字 4R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 51.7%（同じ16Rの実績 12.1%）／券種別 EXACTA 240点 PFS 8.0%／TRIFECTA 400点 PFS 15.5%／TRIO 320点 PFS 10.8%／荒れ度（発走前・1番人気オッズ）MID 5R PFS 25.3% 的中赤字 2/2／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 10R PFS 6.7% 的中赤字 2/2／市場ミラーとの差 16R：実績 12.1% − ミラー 119.2% = Δ -107.2pt（95%区間 -263.8〜-14.0、最高1R除き -117.3pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | 6 | 36,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 6 | 36,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 4 | 12,410 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 16 | 84,410 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

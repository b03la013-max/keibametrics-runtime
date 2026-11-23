# 地方版 2026-11-23 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 10／PAPER PFS 50.3%／正式推薦 PFS 12.1%
- 第一失敗：{'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 4 | 44.3 | 5.6 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1, 'PREDICTION_ROLE_W': 1} |
| MIZ | 6 | 55.5 | 16.3 | {'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2} |

## 日次自律監査

1. 配送：管理 33R／PAPER発走前送信 15／正式試行 15・発走前送信 15／本人確認 0
2. 計算完走：Full29 15／Signed FINAL 15／KRS5000 15／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 50.3%／正式推薦 12.1%／実購入なし
5. Learning：RESULT署名検証 10／学習状態保存 10／前Raceの学習状態を結合した正式Race 15（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '30R到達', 'C23-THIRD3-BY-PAIR': '30R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '30R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '165/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 10 | 50.0% | 80.0% | 50.0% | 10.0% | 10.0% | 10.0% | 20.0% | 1.4 |
| 正式推薦 | 10 | 50.0% | 70.0% | 70.0% | 50.0% | 100.0% | 70.0% | 30.0% | 1.3 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中50.0%（無作為10.7%、差+39.3）／P2 平均1.0頭 的中10.0%（無作為10.7%、差-0.7）／P3 平均1.0頭 的中10.0%（無作為10.7%、差-0.7）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中70.0%（無作為32.1%、差+37.9）／P2 平均6.0頭 的中50.0%（無作為64.2%、差-14.2）／P3 平均9.4頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.8/40（選択性補正込み）・能力順位 13.68/20（10R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.35/40（選択性補正込み）・能力順位 12.36/20（10R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（7.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）2R・着順まで的中 0R／的中 4R のうち的中赤字 2R／損益分岐の倍率 平均 7.9倍／同じ点数を無作為に選んだ場合の期待PFS 40.3%（同じ10Rの実績 50.3%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 50点 PFS 26.8%／WIDE 18点 PFS 146.1%／荒れ度（発走前・1番人気オッズ）MID 3R PFS 111.0% 的中赤字 1/2／SOLID 7R PFS 28.3% 的中赤字 1/2／市場ミラーとの差 10R：実績 50.3% − ミラー 84.7% = Δ -34.4pt（95%区間 -156.6〜76.6、最高1R除き -67.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 22,900円（38.2%）／保護層の資金比率 0.0（10R）／組だけ的中（三連単は外れ）2R・着順まで的中 2R／的中 3R のうち的中赤字 3R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 31.5%（同じ10Rの実績 12.1%）／券種別 EXACTA 150点 PFS 8.7%／TRIFECTA 250点 PFS 14.2%／TRIO 200点 PFS 11.9%／荒れ度（発走前・1番人気オッズ）MID 3R PFS 17.9% 的中赤字 1/1／SOLID 7R PFS 9.5% 的中赤字 2/2／市場ミラーとの差 10R：実績 12.1% − ミラー 170.7% = Δ -158.7pt（95%区間 -387.7〜-12.6、最高1R除き -176.3pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | 4 | 24,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 3 | 18,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 3 | 10,770 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 10 | 52,770 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

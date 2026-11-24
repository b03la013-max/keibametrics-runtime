# 地方版 2026-11-24 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 20／PAPER PFS 62.6%／正式推薦 PFS 41.6%
- 第一失敗：{'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 7, 'PREDICTION_ROLE_P2': 4, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 8 | 21.8 | 38.2 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 1} |
| NGY | 4 | 59.7 | 26.4 | {'PREDICTION_ROLE_W': 4} |
| URW | 8 | 109.8 | 52.5 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'NONE': 1, 'PREDICTION_ROLE_P2': 2} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 25／正式試行 25・発走前送信 25／本人確認 0
2. 計算完走：Full29 25／Signed FINAL 25／KRS5000 25／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 62.6%／正式推薦 41.6%／実購入なし
5. Learning：RESULT署名検証 20／学習状態保存 20／前Raceの学習状態を結合した正式Race 25（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '211/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 20 | 30.0% | 70.0% | 30.0% | 0.0% | 10.0% | 0.0% | 25.0% | 1.5 |
| 正式推薦 | 20 | 40.0% | 65.0% | 65.0% | 80.0% | 100.0% | 65.0% | 50.0% | 1.5 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中30.0%（無作為10.0%、差+20.0）／P2 平均1.0頭 的中0.0%（無作為10.0%、差-10.0）／P3 平均1.0頭 的中10.0%（無作為10.0%、差-0.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中65.0%（無作為30.0%、差+35.0）／P2 平均6.0頭 的中80.0%（無作為60.1%、差+19.9）／P3 平均10.3頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.25/40（選択性補正込み）・能力順位 13.94/20（20R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.24/40（選択性補正込み）・能力順位 13.22/20（20R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（3.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 7R のうち的中赤字 4R／損益分岐の倍率 平均 7.7倍／同じ点数を無作為に選んだ場合の期待PFS 36.0%（同じ20Rの実績 62.6%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 104点 PFS 73.5%／WIDE 38点 PFS 51.1%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 70.3% 的中赤字 2/4／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 11R PFS 64.0% 的中赤字 2/3／市場ミラーとの差 20R：実績 62.6% − ミラー 14.6% = Δ 48.0pt（95%区間 -4.3〜124.4、最高1R除き 17.2pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 45,100円（37.6%）／保護層の資金比率 0.0（20R）／組だけ的中（三連単は外れ）7R・着順まで的中 3R／的中 12R のうち的中赤字 9R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 30.1%（同じ20Rの実績 41.6%）／券種別 EXACTA 300点 PFS 62.9%／TRIFECTA 500点 PFS 14.2%／TRIO 400点 PFS 59.8%／荒れ度（発走前・1番人気オッズ）MID 8R PFS 37.0% 的中赤字 3/4／OPEN 1R PFS 84.2% 的中赤字 1/1／SOLID 11R PFS 41.0% 的中赤字 5/7／市場ミラーとの差 20R：実績 41.6% − ミラー 122.7% = Δ -81.2pt（95%区間 -183.0〜3.5、最高1R除き -68.7pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 9 | 29,430 | RECURRING |
| P1:ROLE_W_MISS | P1 | 7 | 29,660 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 4 | 24,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 20 | 77,430 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

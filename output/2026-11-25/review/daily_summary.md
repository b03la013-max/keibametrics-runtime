# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 10／PAPER PFS 7.1%／正式推薦 PFS 60.4%
- 第一失敗：{'PREDICTION_ROLE_W': 5, 'NONE': 1, 'CAPITAL_EFFICIENCY': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| SON | 6 | 2.7 | 84.1 | {'PREDICTION_ROLE_W': 5, 'NONE': 1} |
| URW | 4 | 18.2 | 25.0 | {'CAPITAL_EFFICIENCY': 4} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 15／正式試行 15・発走前送信 15／本人確認 0
2. 計算完走：Full29 15／Signed FINAL 15／KRS5000 15／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 7.1%／正式推薦 60.4%／実購入なし
5. Learning：RESULT署名検証 10／学習状態保存 10／前Raceの学習状態を結合した正式Race 15（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 10 | 0.0% | 70.0% | 0.0% | 40.0% | 0.0% | 0.0% | 10.0% | 1.6 |
| 正式推薦 | 10 | 20.0% | 50.0% | 50.0% | 100.0% | 100.0% | 50.0% | 50.0% | 1.5 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中0.0%（無作為9.2%、差-9.2）／P2 平均1.0頭 的中40.0%（無作為9.2%、差+30.8）／P3 平均1.0頭 的中0.0%（無作為9.2%、差-9.2）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中50.0%（無作為27.5%、差+22.5）／P2 平均6.0頭 的中100.0%（無作為55.0%、差+45.0）／P3 平均11.0頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 10.9/40（選択性補正込み）・能力順位 13.65/20（10R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.8/40（選択性補正込み）・能力順位 13.29/20（10R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,800円（18.2%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）2R・着順まで的中 0R／的中 2R のうち的中赤字 2R／損益分岐の倍率 平均 9.9倍／同じ点数を無作為に選んだ場合の期待PFS 111.3%（同じ10Rの実績 7.1%）／券種別 EXACTA 9点 PFS 0.0%／TRIFECTA 24点 PFS 0.0%／TRIO 52点 PFS 7.1%／WIDE 14点 PFS 23.6%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 9.6% 的中赤字 1/1／SOLID 3R PFS 6.3% 的中赤字 1/1／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 9R：実績 8.4% − ミラー 18.0% = Δ -9.5pt（95%区間 -37.2〜13.4、最高1R除き -17.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 22,800円（38.0%）／保護層の資金比率 0.0（10R）／組だけ的中（三連単は外れ）5R・着順まで的中 0R／的中 8R のうち的中赤字 7R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 124.8%（同じ10Rの実績 60.4%）／券種別 EXACTA 150点 PFS 76.3%／TRIFECTA 250点 PFS 0.0%／TRIO 200点 PFS 124.0%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 27.0% 的中赤字 4/4／SOLID 3R PFS 138.7% 的中赤字 2/3／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 9R：実績 64.2% − ミラー 11.3% = Δ 52.9pt（95%区間 -1.5〜137.7、最高1R除き 12.8pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 7 | 28,200 | RECURRING |
| P1:ROLE_W_MISS | P1 | 5 | 22,200 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 10 | 40,200 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

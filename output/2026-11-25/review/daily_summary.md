# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 9／PAPER PFS 7.6%／正式推薦 PFS 66.2%
- 第一失敗：{'PREDICTION_ROLE_W': 5, 'NONE': 1, 'CAPITAL_EFFICIENCY': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| SON | 6 | 2.7 | 84.1 | {'PREDICTION_ROLE_W': 5, 'NONE': 1} |
| URW | 3 | 24.3 | 30.4 | {'CAPITAL_EFFICIENCY': 3} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 12／正式試行 12・発走前送信 12／本人確認 0
2. 計算完走：Full29 12／Signed FINAL 12／KRS5000 12／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 7.6%／正式推薦 66.2%／実購入なし
5. Learning：RESULT署名検証 9／学習状態保存 9／前Raceの学習状態を結合した正式Race 12（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 9 | 0.0% | 66.7% | 0.0% | 33.3% | 0.0% | 0.0% | 11.1% | 1.56 |
| 正式推薦 | 9 | 22.2% | 44.4% | 44.4% | 100.0% | 100.0% | 44.4% | 55.6% | 1.44 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中0.0%（無作為9.3%、差-9.3）／P2 平均1.0頭 的中33.3%（無作為9.3%、差+24.1）／P3 平均1.0頭 的中0.0%（無作為9.3%、差-9.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中44.4%（無作為27.8%、差+16.7）／P2 平均6.0頭 的中100.0%（無作為55.6%、差+44.4）／P3 平均10.89頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 10.33/40（選択性補正込み）・能力順位 13.44/20（9R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.31/40（選択性補正込み）・能力順位 13.24/20（9R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,800円（19.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）2R・着順まで的中 0R／的中 2R のうち的中赤字 2R／損益分岐の倍率 平均 10.2倍／同じ点数を無作為に選んだ場合の期待PFS 119.4%（同じ9Rの実績 7.6%）／券種別 EXACTA 9点 PFS 0.0%／TRIFECTA 24点 PFS 0.0%／TRIO 47点 PFS 7.9%／WIDE 12点 PFS 27.5%／荒れ度（発走前・1番人気オッズ）MID 5R PFS 11.1% 的中赤字 1/1／SOLID 3R PFS 6.3% 的中赤字 1/1／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 8R：実績 9.2% − ミラー 9.7% = Δ -0.5pt（95%区間 -22.3〜19.6、最高1R除き -8.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 20,600円（38.1%）／保護層の資金比率 0.0（9R）／組だけ的中（三連単は外れ）5R・着順まで的中 0R／的中 7R のうち的中赤字 6R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 138.5%（同じ9Rの実績 66.2%）／券種別 EXACTA 135点 PFS 80.9%／TRIFECTA 225点 PFS 0.0%／TRIO 180点 PFS 137.8%／荒れ度（発走前・1番人気オッズ）MID 5R PFS 30.6% 的中赤字 3/3／SOLID 3R PFS 138.7% 的中赤字 2/3／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 8R：実績 71.1% − ミラー 7.1% = Δ 64.1pt（95%区間 7.3〜159.4、最高1R除き 19.7pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 6 | 22,730 | RECURRING |
| P1:ROLE_W_MISS | P1 | 5 | 22,200 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 9 | 34,730 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

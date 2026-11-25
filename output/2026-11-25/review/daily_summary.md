# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 11／PAPER PFS 26.0%／正式推薦 PFS 58.4%
- 第一失敗：{'PREDICTION_ROLE_W': 6, 'NONE': 1, 'CAPITAL_EFFICIENCY': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| SON | 7 | 28.5 | 77.5 | {'PREDICTION_ROLE_W': 6, 'NONE': 1} |
| URW | 4 | 18.2 | 25.0 | {'CAPITAL_EFFICIENCY': 4} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 16／正式試行 16・発走前送信 16／本人確認 0
2. 計算完走：Full29 16／Signed FINAL 16／KRS5000 16／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 26.0%／正式推薦 58.4%／実購入なし
5. Learning：RESULT署名検証 11／学習状態保存 11／前Raceの学習状態を結合した正式Race 16（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 11 | 9.1% | 72.7% | 9.1% | 36.4% | 0.0% | 9.1% | 18.2% | 1.64 |
| 正式推薦 | 11 | 18.2% | 45.5% | 45.5% | 100.0% | 100.0% | 45.5% | 54.5% | 1.45 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中9.1%（無作為9.6%、差-0.5）／P2 平均1.0頭 的中36.4%（無作為9.6%、差+26.7）／P3 平均1.0頭 的中0.0%（無作為9.6%、差-9.6）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中45.5%（無作為28.9%、差+16.6）／P2 平均6.0頭 的中100.0%（無作為57.8%、差+42.2）／P3 平均10.64頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.91/40（選択性補正込み）・能力順位 13.69/20（11R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.86/40（選択性補正込み）・能力順位 13.03/20（11R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（20.9%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）3R・着順まで的中 0R／的中 3R のうち的中赤字 2R／損益分岐の倍率 平均 10.5倍／同じ点数を無作為に選んだ場合の期待PFS 104.2%（同じ11Rの実績 26.0%）／券種別 EXACTA 12点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 57点 PFS 46.7%／WIDE 14点 PFS 23.6%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 9.6% 的中赤字 1/1／SOLID 4R PFS 53.9% 的中赤字 1/2／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 10R：実績 30.2% − ミラー 38.2% = Δ -8.0pt（95%区間 -32.1〜11.1、最高1R除き -9.5pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 25,200円（38.2%）／保護層の資金比率 0.0（11R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 9R のうち的中赤字 8R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 119.2%（同じ11Rの実績 58.4%）／券種別 EXACTA 165点 PFS 69.4%／TRIFECTA 275点 PFS 0.0%／TRIO 220点 PFS 123.2%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 27.0% 的中赤字 4/4／SOLID 4R PFS 113.5% 的中赤字 3/4／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 10R：実績 61.6% − ミラー 36.1% = Δ 25.5pt（95%区間 -52.7〜122.2、最高1R除き -13.3pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 8 | 31,910 | RECURRING |
| P1:ROLE_W_MISS | P1 | 6 | 25,910 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 11 | 43,910 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 16／PAPER PFS 24.1%／正式推薦 PFS 43.1%
- 第一失敗：{'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 8, 'NONE': 1, 'PREDICTION_ROLE_P2': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 1 | 72.9 | 41.8 | {'CAPITAL_EFFICIENCY': 1} |
| SON | 9 | 24.3 | 60.3 | {'PREDICTION_ROLE_W': 7, 'NONE': 1, 'PREDICTION_ROLE_P2': 1} |
| URW | 6 | 15.6 | 17.4 | {'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 21／正式試行 21・発走前送信 21／本人確認 0
2. 計算完走：Full29 21／Signed FINAL 21／KRS5000 21／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 24.1%／正式推薦 43.1%／実購入なし
5. Learning：RESULT署名検証 16／学習状態保存 16／前Raceの学習状態を結合した正式Race 21（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 16 | 18.8% | 62.5% | 18.8% | 31.2% | 6.2% | 12.5% | 12.5% | 1.44 |
| 正式推薦 | 16 | 25.0% | 50.0% | 50.0% | 93.8% | 100.0% | 50.0% | 37.5% | 1.25 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中18.8%（無作為9.3%、差+9.5）／P2 平均1.0頭 的中31.2%（無作為9.3%、差+22.0）／P3 平均1.0頭 的中6.2%（無作為9.3%、差-3.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中50.0%（無作為27.9%、差+22.1）／P2 平均6.0頭 的中93.8%（無作為55.7%、差+38.0）／P3 平均11.0頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.06/40（選択性補正込み）・能力順位 13.13/20（16R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.81/40（選択性補正込み）・能力順位 12.6/20（16R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（15.8%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）3R・着順まで的中 0R／的中 5R のうち的中赤字 4R／損益分岐の倍率 平均 9.5倍／同じ点数を無作為に選んだ場合の期待PFS 92.9%（同じ16Rの実績 24.1%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 82点 PFS 32.4%／WIDE 20点 PFS 42.0%／WIN 2点 PFS 80.0%／荒れ度（発走前・1番人気オッズ）MID 9R PFS 13.6% 的中赤字 2/2／SOLID 6R PFS 43.3% 的中赤字 2/3／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 15R：実績 26.9% − ミラー 32.1% = Δ -5.2pt（95%区間 -24.4〜12.6、最高1R除き -5.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 36,700円（38.2%）／保護層の資金比率 0.0（16R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 11R のうち的中赤字 10R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 94.3%（同じ16Rの実績 43.1%）／券種別 EXACTA 240点 PFS 59.3%／TRIFECTA 400点 PFS 0.0%／TRIO 320点 PFS 84.7%／荒れ度（発走前・1番人気オッズ）MID 9R PFS 22.6% 的中赤字 5/5／SOLID 6R PFS 76.4% 的中赤字 4/5／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 15R：実績 44.2% − ミラー 37.0% = Δ 7.2pt（95%区間 -51.3〜79.2、最高1R除き -19.0pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 10 | 41,130 | RECURRING |
| P1:ROLE_W_MISS | P1 | 8 | 37,910 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 16 | 71,130 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

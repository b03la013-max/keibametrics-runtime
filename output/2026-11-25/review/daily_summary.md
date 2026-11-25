# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 28／PAPER PFS 56.4%／正式推薦 PFS 36.6%
- 第一失敗：{'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_W': 15, 'PREDICTION_ROLE_P2': 2, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 6 | 30.0 | 29.7 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1} |
| SON | 12 | 63.2 | 60.5 | {'PREDICTION_ROLE_W': 9, 'NONE': 1, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 1} |
| URW | 10 | 60.0 | 12.2 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 4} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 32／正式試行 32・発走前送信 32／本人確認 0
2. 計算完走：Full29 32／Signed FINAL 32／KRS5000 32／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 56.4%／正式推薦 36.6%／実購入なし
5. Learning：RESULT署名検証 28／学習状態保存 28／前Raceの学習状態を結合した正式Race 32（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 28 | 17.9% | 57.1% | 17.9% | 17.9% | 7.1% | 7.1% | 17.9% | 1.39 |
| 正式推薦 | 28 | 14.3% | 46.4% | 46.4% | 78.6% | 100.0% | 46.4% | 39.3% | 1.21 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中17.9%（無作為8.9%、差+8.9）／P2 平均1.0頭 的中17.9%（無作為8.9%、差+8.9）／P3 平均1.0頭 的中7.1%（無作為8.9%、差-1.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中46.4%（無作為26.8%、差+19.7）／P2 平均6.0頭 的中78.6%（無作為53.5%、差+25.0）／P3 平均11.39頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.25/40（選択性補正込み）・能力順位 12.85/20（28R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.01/40（選択性補正込み）・能力順位 12.55/20（28R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（10.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 10R のうち的中赤字 6R／損益分岐の倍率 平均 8.6倍／同じ点数を無作為に選んだ場合の期待PFS 106.4%（同じ28Rの実績 56.4%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 146点 PFS 54.3%／WIDE 44点 PFS 123.9%／WIN 2点 PFS 80.0%／荒れ度（発走前・1番人気オッズ）MID 15R PFS 64.0% 的中赤字 3/5／OPEN 2R PFS 0.0% 的中赤字 0/0／SOLID 10R PFS 65.2% 的中赤字 3/5／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 27R：実績 60.4% − ミラー 36.1% = Δ 24.4pt（95%区間 -22.7〜82.0、最高1R除き 8.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 64,600円（38.5%）／保護層の資金比率 0.0（28R）／組だけ的中（三連単は外れ）10R・着順まで的中 2R／的中 17R のうち的中赤字 15R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 109.5%（同じ28Rの実績 36.6%）／券種別 EXACTA 420点 PFS 46.5%／TRIFECTA 700点 PFS 6.3%／TRIO 560点 PFS 67.2%／荒れ度（発走前・1番人気オッズ）MID 15R PFS 28.5% 的中赤字 7/8／OPEN 2R PFS 0.0% 的中赤字 0/0／SOLID 10R PFS 57.2% 的中赤字 7/8／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 27R：実績 37.0% − ミラー 33.7% = Δ 3.3pt（95%区間 -33.1〜42.4、最高1R除き -11.0pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 15 | 72,860 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 15 | 57,400 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 28 | 123,400 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

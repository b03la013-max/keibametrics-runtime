# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 27／PAPER PFS 58.1%／正式推薦 PFS 38.0%
- 第一失敗：{'CAPITAL_EFFICIENCY': 10, 'PREDICTION_ROLE_W': 14, 'PREDICTION_ROLE_P2': 2, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 5 | 36.0 | 35.6 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 1} |
| SON | 12 | 63.2 | 60.5 | {'PREDICTION_ROLE_W': 9, 'NONE': 1, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 1} |
| URW | 10 | 60.0 | 12.2 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 4} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 30／正式試行 30・発走前送信 30／本人確認 0
2. 計算完走：Full29 30／Signed FINAL 30／KRS5000 30／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 58.1%／正式推薦 38.0%／実購入なし
5. Learning：RESULT署名検証 27／学習状態保存 27／前Raceの学習状態を結合した正式Race 30（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 27 | 18.5% | 59.3% | 18.5% | 18.5% | 7.4% | 7.4% | 18.5% | 1.41 |
| 正式推薦 | 27 | 14.8% | 48.1% | 48.1% | 81.5% | 100.0% | 48.1% | 40.7% | 1.22 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中18.5%（無作為8.9%、差+9.6）／P2 平均1.0頭 的中18.5%（無作為8.9%、差+9.6）／P3 平均1.0頭 的中7.4%（無作為8.9%、差-1.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中48.1%（無作為26.8%、差+21.3）／P2 平均6.0頭 的中81.5%（無作為53.7%、差+27.8）／P3 平均11.37頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.44/40（選択性補正込み）・能力順位 13.03/20（27R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.41/40（選択性補正込み）・能力順位 12.8/20（27R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（10.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 10R のうち的中赤字 6R／損益分岐の倍率 平均 8.6倍／同じ点数を無作為に選んだ場合の期待PFS 108.9%（同じ27Rの実績 58.1%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 141点 PFS 56.2%／WIDE 42点 PFS 129.8%／WIN 2点 PFS 80.0%／荒れ度（発走前・1番人気オッズ）MID 15R PFS 64.0% 的中赤字 3/5／OPEN 2R PFS 0.0% 的中赤字 0/0／SOLID 9R PFS 70.7% 的中赤字 3/5／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 26R：実績 62.4% − ミラー 37.2% = Δ 25.2pt（95%区間 -21.2〜84.7、最高1R除き 8.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 62,400円（38.5%）／保護層の資金比率 0.0（27R）／組だけ的中（三連単は外れ）10R・着順まで的中 2R／的中 17R のうち的中赤字 15R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 113.1%（同じ27Rの実績 38.0%）／券種別 EXACTA 405点 PFS 48.2%／TRIFECTA 675点 PFS 6.5%／TRIO 540点 PFS 69.7%／荒れ度（発走前・1番人気オッズ）MID 15R PFS 28.5% 的中赤字 7/8／OPEN 2R PFS 0.0% 的中赤字 0/0／SOLID 9R PFS 63.6% 的中赤字 7/8／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 26R：実績 38.4% − ミラー 35.0% = Δ 3.4pt（95%区間 -33.9〜45.1、最高1R除き -11.4pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 15 | 57,400 | RECURRING |
| P1:ROLE_W_MISS | P1 | 14 | 66,860 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 27 | 117,400 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

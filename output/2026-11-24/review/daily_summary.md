# 地方版 2026-11-24 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 13／PAPER PFS 60.9%／正式推薦 PFS 41.5%
- 第一失敗：{'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 2, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 6 | 0.0 | 19.9 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 2} |
| NGY | 1 | 0.0 | 0.0 | {'PREDICTION_ROLE_W': 1} |
| URW | 6 | 145.0 | 70.0 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'NONE': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 18／正式試行 18・発走前送信 18／本人確認 0
2. 計算完走：Full29 18／Signed FINAL 18／KRS5000 18／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 60.9%／正式推薦 41.5%／実購入なし
5. Learning：RESULT署名検証 13／学習状態保存 13／前Raceの学習状態を結合した正式Race 18（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '211/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 13 | 46.2% | 84.6% | 46.2% | 0.0% | 7.7% | 0.0% | 23.1% | 1.46 |
| 正式推薦 | 13 | 38.5% | 69.2% | 69.2% | 84.6% | 100.0% | 69.2% | 46.2% | 1.46 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中46.2%（無作為10.6%、差+35.6）／P2 平均1.0頭 的中0.0%（無作為10.6%、差-10.6）／P3 平均1.0頭 的中7.7%（無作為10.6%、差-2.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中69.2%（無作為31.7%、差+37.5）／P2 平均6.0頭 的中84.6%（無作為63.4%、差+21.2）／P3 平均9.77頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.31/40（選択性補正込み）・能力順位 14.07/20（13R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.04/40（選択性補正込み）・能力順位 12.74/20（13R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（6.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）4R・着順まで的中 0R／的中 4R のうち的中赤字 3R／損益分岐の倍率 平均 7.7倍／同じ点数を無作為に選んだ場合の期待PFS 44.1%（同じ13Rの実績 60.9%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 65点 PFS 80.3%／WIDE 24点 PFS 36.2%／荒れ度（発走前・1番人気オッズ）MID 2R PFS 42.1% 的中赤字 1/1／SOLID 11R PFS 64.0% 的中赤字 2/3／市場ミラーとの差 13R：実績 60.9% − ミラー 17.0% = Δ 43.9pt（95%区間 -14.7〜162.3、最高1R除き -4.8pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 29,300円（37.6%）／保護層の資金比率 0.0（13R）／組だけ的中（三連単は外れ）3R・着順まで的中 3R／的中 8R のうち的中赤字 6R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 35.6%（同じ13Rの実績 41.5%）／券種別 EXACTA 195点 PFS 54.8%／TRIFECTA 325点 PFS 21.8%／TRIO 260点 PFS 56.2%／荒れ度（発走前・1番人気オッズ）MID 2R PFS 44.3% 的中赤字 1/1／SOLID 11R PFS 41.0% 的中赤字 5/7／市場ミラーとの差 13R：実績 41.5% − ミラー 114.7% = Δ -73.2pt（95%区間 -192.3〜11.5、最高1R除き -52.9pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 6 | 20,720 | RECURRING |
| P1:ROLE_W_MISS | P1 | 4 | 18,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 13 | 50,720 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-24 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 14／PAPER PFS 56.9%／正式推薦 PFS 38.5%
- 第一失敗：{'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 2, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 6 | 0.0 | 19.9 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 2} |
| NGY | 2 | 0.0 | 0.0 | {'PREDICTION_ROLE_W': 2} |
| URW | 6 | 145.0 | 70.0 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 2, 'NONE': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 19／正式試行 19・発走前送信 19／本人確認 0
2. 計算完走：Full29 19／Signed FINAL 19／KRS5000 19／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 56.9%／正式推薦 38.5%／実購入なし
5. Learning：RESULT署名検証 14／学習状態保存 14／前Raceの学習状態を結合した正式Race 19（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '211/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 14 | 42.9% | 78.6% | 42.9% | 0.0% | 7.1% | 0.0% | 21.4% | 1.36 |
| 正式推薦 | 14 | 35.7% | 64.3% | 64.3% | 85.7% | 100.0% | 64.3% | 42.9% | 1.43 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中42.9%（無作為10.4%、差+32.4）／P2 平均1.0頭 的中0.0%（無作為10.4%、差-10.4）／P3 平均1.0頭 的中7.1%（無作為10.4%、差-3.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中64.3%（無作為31.2%、差+33.0）／P2 平均6.0頭 的中85.7%（無作為62.5%、差+23.2）／P3 平均9.93頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.36/40（選択性補正込み）・能力順位 13.69/20（14R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.47/40（選択性補正込み）・能力順位 12.32/20（14R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（5.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）4R・着順まで的中 0R／的中 4R のうち的中赤字 3R／損益分岐の倍率 平均 7.6倍／同じ点数を無作為に選んだ場合の期待PFS 43.9%（同じ14Rの実績 56.9%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 70点 PFS 74.6%／WIDE 26点 PFS 33.5%／荒れ度（発走前・1番人気オッズ）MID 3R PFS 28.1% 的中赤字 1/1／SOLID 11R PFS 64.0% 的中赤字 2/3／市場ミラーとの差 14R：実績 56.9% − ミラー 15.9% = Δ 41.0pt（95%区間 -13.8〜143.6、最高1R除き -4.5pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 31,400円（37.4%）／保護層の資金比率 0.0（14R）／組だけ的中（三連単は外れ）3R・着順まで的中 3R／的中 8R のうち的中赤字 6R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 35.0%（同じ14Rの実績 38.5%）／券種別 EXACTA 210点 PFS 50.9%／TRIFECTA 350点 PFS 20.2%／TRIO 280点 PFS 52.1%／荒れ度（発走前・1番人気オッズ）MID 3R PFS 29.6% 的中赤字 1/1／SOLID 11R PFS 41.0% 的中赤字 5/7／市場ミラーとの差 14R：実績 38.5% − ミラー 153.3% = Δ -114.7pt（95%区間 -245.2〜-1.4、最高1R除き -99.2pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 6 | 20,720 | RECURRING |
| P1:ROLE_W_MISS | P1 | 5 | 24,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 14 | 56,720 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-24 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 9／PAPER PFS 76.4%／正式推薦 PFS 26.5%
- 第一失敗：{'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 2, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 5 | 0.0 | 9.6 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 2} |
| URW | 4 | 196.4 | 47.8 | {'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_W': 1, 'NONE': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 14／正式試行 14・発走前送信 14／本人確認 0
2. 計算完走：Full29 14／Signed FINAL 14／KRS5000 14／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 76.4%／正式推薦 26.5%／実購入なし
5. Learning：RESULT署名検証 9／学習状態保存 9／前Raceの学習状態を結合した正式Race 14（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '211/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 9 | 55.6% | 88.9% | 55.6% | 0.0% | 11.1% | 0.0% | 22.2% | 1.56 |
| 正式推薦 | 9 | 33.3% | 77.8% | 77.8% | 77.8% | 100.0% | 77.8% | 33.3% | 1.44 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中55.6%（無作為11.3%、差+44.3）／P2 平均1.0頭 的中0.0%（無作為11.3%、差-11.3）／P3 平均1.0頭 的中11.1%（無作為11.3%、差-0.2）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中77.8%（無作為33.9%、差+43.9）／P2 平均6.0頭 的中77.8%（無作為67.7%、差+10.1）／P3 平均9.11頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.0/40（選択性補正込み）・能力順位 13.89/20（9R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.13/40（選択性補正込み）・能力順位 12.01/20（9R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（8.3%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）3R・着順まで的中 0R／的中 3R のうち的中赤字 2R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 52.2%（同じ9Rの実績 76.4%）／券種別 EXACTA 3点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 45点 PFS 106.0%／WIDE 16点 PFS 45.6%／荒れ度（発走前・1番人気オッズ）SOLID 9R PFS 76.4% 的中赤字 2/3／市場ミラーとの差 9R：実績 76.4% − ミラー 21.7% = Δ 54.7pt（95%区間 -23.0〜223.3、最高1R除き -13.8pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 20,700円（38.3%）／保護層の資金比率 0.0（9R）／組だけ的中（三連単は外れ）2R・着順まで的中 1R／的中 5R のうち的中赤字 4R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 42.7%（同じ9Rの実績 26.5%）／券種別 EXACTA 135点 PFS 59.0%／TRIFECTA 225点 PFS 5.6%／TRIO 180点 PFS 28.4%／荒れ度（発走前・1番人気オッズ）SOLID 9R PFS 26.5% 的中赤字 4/5／市場ミラーとの差 9R：実績 26.5% − ミラー 154.0% = Δ -127.4pt（95%区間 -292.1〜-19.4、最高1R除き -103.8pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 4 | 18,330 | RECURRING |
| P1:ROLE_W_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 9 | 42,330 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

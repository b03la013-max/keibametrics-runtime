# 地方版 2026-11-24 日次総括（自動・推薦試算・実購入なし）

- 反省済みRace 36／PAPER PFS 59.1%／正式推薦 PFS 54.6%
- 第一失敗：{'CAPITAL_EFFICIENCY': 11, 'PREDICTION_ROLE_W': 13, 'PREDICTION_ROLE_P2': 6, 'NONE': 6}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 12 | 24.7 | 61.3 | {'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 2, 'NONE': 2} |
| NGY | 12 | 42.2 | 46.2 | {'PREDICTION_ROLE_W': 6, 'CAPITAL_EFFICIENCY': 3, 'NONE': 2, 'PREDICTION_ROLE_P2': 1} |
| URW | 12 | 116.2 | 56.3 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 4, 'NONE': 2, 'PREDICTION_ROLE_P2': 3} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 36／正式試行 36・発走前送信 36／本人確認 0
2. 計算完走：Full29 36／Signed FINAL 36／KRS5000 36／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 59.1%／正式推薦 54.6%／実購入なし
5. Learning：RESULT署名検証 36／学習状態保存 36／前Raceの学習状態を結合した正式Race 36（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '211/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 36 | 30.6% | 66.7% | 30.6% | 5.6% | 5.6% | 5.6% | 25.0% | 1.5 |
| 正式推薦 | 36 | 38.9% | 63.9% | 63.9% | 77.8% | 100.0% | 63.9% | 44.4% | 1.53 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中30.6%（無作為9.4%、差+21.1）／P2 平均1.0頭 的中5.6%（無作為9.4%、差-3.9）／P3 平均1.0頭 的中5.6%（無作為9.4%、差-3.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中63.9%（無作為28.3%、差+35.6）／P2 平均6.0頭 的中77.8%（無作為56.6%、差+21.2）／P3 平均10.86頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.03/40（選択性補正込み）・能力順位 14.08/20（36R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.45/40（選択性補正込み）・能力順位 13.6/20（36R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,200円（4.4%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）9R・着順まで的中 1R／的中 13R のうち的中赤字 7R／損益分岐の倍率 平均 7.6倍／同じ点数を無作為に選んだ場合の期待PFS 30.1%（同じ36Rの実績 59.1%）／券種別 EXACTA 8点 PFS 33.8%／TRIFECTA 16点 PFS 36.9%／TRIO 184点 PFS 62.4%／WIDE 66点 PFS 56.4%／WIN 1点 PFS 190.0%／荒れ度（発走前・1番人気オッズ）MID 19R PFS 71.0% 的中赤字 4/9／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 16R PFS 50.8% 的中赤字 3/4／市場ミラーとの差 36R：実績 59.1% − ミラー 24.1% = Δ 35.0pt（95%区間 -2.2〜81.6、最高1R除き 17.8pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 82,000円（38.0%）／保護層の資金比率 0.0（36R）／組だけ的中（三連単は外れ）10R・着順まで的中 7R／的中 21R のうち的中赤字 14R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 28.9%（同じ36Rの実績 54.6%）／券種別 EXACTA 540点 PFS 79.3%／TRIFECTA 900点 PFS 45.3%／TRIO 720点 PFS 47.7%／荒れ度（発走前・1番人気オッズ）MID 19R PFS 61.2% 的中赤字 6/10／OPEN 1R PFS 84.2% 的中赤字 1/1／SOLID 16R PFS 44.9% 的中赤字 7/10／市場ミラーとの差 36R：実績 54.6% − ミラー 118.0% = Δ -63.5pt（95%区間 -142.4〜1.5、最高1R除き -74.7pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 14 | 49,630 | RECURRING |
| P1:ROLE_W_MISS | P1 | 13 | 63,240 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 6 | 36,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 36 | 139,630 | RECURRING |
| P2:INDEX_OBSERVATION_COVERAGE | P2 | 2 | 4,140 | SINGLE_OR_FEW (過大評価しない) |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

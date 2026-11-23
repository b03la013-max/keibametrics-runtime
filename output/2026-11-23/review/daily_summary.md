# 地方版 2026-11-23 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 3／PAPER PFS 101.0%／正式推薦 PFS 0.0%
- 第一失敗：{'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| MIZ | 3 | 101.0 | 0.0 | {'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 2} |

## 日次自律監査

1. 配送：管理 33R／PAPER発走前送信 5／正式試行 5・発走前送信 5／本人確認 0
2. 計算完走：Full29 5／Signed FINAL 5／KRS5000 5／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 101.0%／正式推薦 0.0%／実購入なし
5. Learning：RESULT署名検証 3／学習状態保存 3／前Raceの学習状態を結合した正式Race 5（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '30R到達', 'C23-THIRD3-BY-PAIR': '30R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '30R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '157/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 3 | 33.3% | 100.0% | 33.3% | 0.0% | 0.0% | 0.0% | 0.0% | 1.0 |
| 正式推薦 | 3 | 66.7% | 66.7% | 66.7% | 33.3% | 100.0% | 66.7% | 0.0% | 0.67 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.3%（無作為10.4%、差+23.0）／P2 平均1.0頭 的中0.0%（無作為10.4%、差-10.4）／P3 平均1.0頭 的中0.0%（無作為10.4%、差-10.4）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中66.7%（無作為31.1%、差+35.6）／P2 平均6.0頭 的中33.3%（無作為62.2%、差-28.9）／P3 平均9.67頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 10.67/40（選択性補正込み）・能力順位 12.27/20（3R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.15/40（選択性補正込み）・能力順位 10.6/20（3R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）0R・着順まで的中 0R／的中 1R のうち的中赤字 0R／損益分岐の倍率 平均 7.0倍／同じ点数を無作為に選んだ場合の期待PFS 92.8%（同じ3Rの実績 101.0%）／券種別 TRIO 15点 PFS 0.0%／WIDE 6点 PFS 353.3%／荒れ度（発走前・1番人気オッズ）MID 1R PFS 302.9% 的中赤字 0/1／SOLID 2R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 3R：実績 101.0% − ミラー 247.6% = Δ -146.7pt（95%区間 -554.3〜302.9、最高1R除き -371.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 6,800円（37.8%）／保護層の資金比率 0.0（3R）／組だけ的中（三連単は外れ）0R・着順まで的中 0R／的中 0R のうち的中赤字 0R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 62.0%（同じ3Rの実績 0.0%）／券種別 EXACTA 45点 PFS 0.0%／TRIFECTA 75点 PFS 0.0%／TRIO 60点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 1R PFS 0.0% 的中赤字 0/0／SOLID 2R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 3R：実績 0.0% − ミラー 140.5% = Δ -140.5pt（95%区間 -275.8〜-53.8、最高1R除き -183.8pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P1:ROLE_W_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 3 | 18,000 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

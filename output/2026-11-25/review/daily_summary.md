# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 7／PAPER PFS 9.0%／正式推薦 PFS 80.6%
- 第一失敗：{'PREDICTION_ROLE_W': 4, 'NONE': 1, 'CAPITAL_EFFICIENCY': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| SON | 5 | 3.0 | 100.9 | {'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| URW | 2 | 36.4 | 30.1 | {'CAPITAL_EFFICIENCY': 2} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 10／正式試行 10・発走前送信 10／本人確認 0
2. 計算完走：Full29 10／Signed FINAL 10／KRS5000 10／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 9.0%／正式推薦 80.6%／実購入なし
5. Learning：RESULT署名検証 7／学習状態保存 7／前Raceの学習状態を結合した正式Race 10（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 7 | 0.0% | 71.4% | 0.0% | 28.6% | 0.0% | 0.0% | 14.3% | 1.57 |
| 正式推薦 | 7 | 14.3% | 42.9% | 42.9% | 100.0% | 100.0% | 42.9% | 71.4% | 1.57 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中0.0%（無作為9.3%、差-9.3）／P2 平均1.0頭 的中28.6%（無作為9.3%、差+19.3）／P3 平均1.0頭 的中0.0%（無作為9.3%、差-9.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中42.9%（無作為27.9%、差+15.0）／P2 平均6.0頭 的中100.0%（無作為55.7%、差+44.3）／P3 平均10.86頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 10.29/40（選択性補正込み）・能力順位 14.28/20（7R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.98/40（選択性補正込み）・能力順位 13.97/20（7R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,800円（23.1%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）2R・着順まで的中 0R／的中 2R のうち的中赤字 2R／損益分岐の倍率 平均 11.1倍／同じ点数を無作為に選んだ場合の期待PFS 71.8%（同じ7Rの実績 9.0%）／券種別 EXACTA 9点 PFS 0.0%／TRIFECTA 24点 PFS 0.0%／TRIO 37点 PFS 10.0%／WIDE 8点 PFS 41.2%／荒れ度（発走前・1番人気オッズ）MID 3R PFS 15.9% 的中赤字 1/1／SOLID 3R PFS 6.3% 的中赤字 1/1／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 6R：実績 11.3% − ミラー 11.9% = Δ -0.6pt（95%区間 -27.5〜25.5、最高1R除き -10.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 15,900円（37.9%）／保護層の資金比率 0.0（7R）／組だけ的中（三連単は外れ）5R・着順まで的中 0R／的中 6R のうち的中赤字 5R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 51.0%（同じ7Rの実績 80.6%）／券種別 EXACTA 105点 PFS 86.3%／TRIFECTA 175点 PFS 0.0%／TRIO 140点 PFS 177.2%／荒れ度（発走前・1番人気オッズ）MID 3R PFS 40.7% 的中赤字 2/2／SOLID 3R PFS 138.7% 的中赤字 2/3／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 6R：実績 89.7% − ミラー 9.4% = Δ 80.2pt（95%区間 4.0〜201.1、最高1R除き 21.4pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 5 | 18,590 | RECURRING |
| P1:ROLE_W_MISS | P1 | 4 | 16,200 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 7 | 24,590 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

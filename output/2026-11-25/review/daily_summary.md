# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 6／PAPER PFS 2.7%／正式推薦 PFS 88.9%
- 第一失敗：{'PREDICTION_ROLE_W': 4, 'NONE': 1, 'CAPITAL_EFFICIENCY': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| SON | 5 | 3.0 | 100.9 | {'PREDICTION_ROLE_W': 4, 'NONE': 1} |
| URW | 1 | 0.0 | 29.3 | {'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 10／正式試行 10・発走前送信 10／本人確認 0
2. 計算完走：Full29 10／Signed FINAL 10／KRS5000 10／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 2.7%／正式推薦 88.9%／実購入なし
5. Learning：RESULT署名検証 6／学習状態保存 6／前Raceの学習状態を結合した正式Race 10（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 6 | 0.0% | 66.7% | 0.0% | 16.7% | 0.0% | 0.0% | 0.0% | 1.33 |
| 正式推薦 | 6 | 16.7% | 33.3% | 33.3% | 100.0% | 100.0% | 33.3% | 66.7% | 1.33 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中0.0%（無作為9.2%、差-9.2）／P2 平均1.0頭 的中16.7%（無作為9.2%、差+7.5）／P3 平均1.0頭 的中0.0%（無作為9.2%、差-9.2）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中33.3%（無作為27.5%、差+5.8）／P2 平均6.0頭 的中100.0%（無作為55.0%、差+45.0）／P3 平均11.0頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 8.83/40（選択性補正込み）・能力順位 13.78/20（6R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.16/40（選択性補正込み）・能力順位 13.39/20（6R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,800円（25.4%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）1R・着順まで的中 0R／的中 1R のうち的中赤字 1R／損益分岐の倍率 平均 11.8倍／同じ点数を無作為に選んだ場合の期待PFS 78.2%（同じ6Rの実績 2.7%）／券種別 EXACTA 9点 PFS 0.0%／TRIFECTA 24点 PFS 0.0%／TRIO 32点 PFS 0.0%／WIDE 6点 PFS 31.7%／荒れ度（発走前・1番人気オッズ）MID 2R PFS 0.0% 的中赤字 0/0／SOLID 3R PFS 6.3% 的中赤字 1/1／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 5R：実績 3.5% − ミラー 13.5% = Δ -10.0pt（95%区間 -37.5〜0.0、最高1R除き 0.0pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 13,600円（37.8%）／保護層の資金比率 0.0（6R）／組だけ的中（三連単は外れ）4R・着順まで的中 0R／的中 5R のうち的中赤字 4R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 57.9%（同じ6Rの実績 88.9%）／券種別 EXACTA 90点 PFS 84.2%／TRIFECTA 150点 PFS 0.0%／TRIO 120点 PFS 203.7%／荒れ度（発走前・1番人気オッズ）MID 2R PFS 45.7% 的中赤字 1/1／SOLID 3R PFS 138.7% 的中赤字 2/3／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 5R：実績 101.5% − ミラー 10.1% = Δ 91.4pt（95%区間 -0.1〜235.2、最高1R除き 20.6pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 4 | 16,200 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 4 | 14,440 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 6 | 20,440 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

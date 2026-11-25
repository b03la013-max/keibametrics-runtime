# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 13／PAPER PFS 23.2%／正式推薦 PFS 49.4%
- 第一失敗：{'PREDICTION_ROLE_W': 7, 'NONE': 1, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 4}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| SON | 8 | 26.4 | 67.8 | {'PREDICTION_ROLE_W': 6, 'NONE': 1, 'PREDICTION_ROLE_P2': 1} |
| URW | 5 | 14.6 | 20.0 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 19／正式試行 19・発走前送信 19／本人確認 0
2. 計算完走：Full29 19／Signed FINAL 19／KRS5000 19／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 23.2%／正式推薦 49.4%／実購入なし
5. Learning：RESULT署名検証 13／学習状態保存 13／前Raceの学習状態を結合した正式Race 19（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 13 | 7.7% | 61.5% | 7.7% | 30.8% | 0.0% | 7.7% | 15.4% | 1.46 |
| 正式推薦 | 13 | 15.4% | 46.2% | 46.2% | 92.3% | 100.0% | 46.2% | 46.2% | 1.38 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中7.7%（無作為9.5%、差-1.8）／P2 平均1.0頭 的中30.8%（無作為9.5%、差+21.3）／P3 平均1.0頭 的中0.0%（無作為9.5%、差-9.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中46.2%（無作為28.5%、差+17.6）／P2 平均6.0頭 的中92.3%（無作為57.1%、差+35.2）／P3 平均10.77頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 10.54/40（選択性補正込み）・能力順位 12.78/20（13R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.32/40（選択性補正込み）・能力順位 12.62/20（13R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（18.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）3R・着順まで的中 0R／的中 3R のうち的中赤字 2R／損益分岐の倍率 平均 9.9倍／同じ点数を無作為に選んだ場合の期待PFS 101.5%（同じ13Rの実績 23.2%）／券種別 EXACTA 12点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 67点 PFS 39.7%／WIDE 18点 PFS 18.3%／荒れ度（発走前・1番人気オッズ）MID 7R PFS 8.5% 的中赤字 1/1／SOLID 5R PFS 46.8% 的中赤字 1/2／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 12R：実績 26.5% − ミラー 34.9% = Δ -8.4pt（95%区間 -30.5〜8.4、最高1R除き -9.8pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 29,600円（37.9%）／保護層の資金比率 0.0（13R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 9R のうち的中赤字 8R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 109.4%（同じ13Rの実績 49.4%）／券種別 EXACTA 195点 PFS 58.7%／TRIFECTA 325点 PFS 0.0%／TRIO 260点 PFS 104.2%／荒れ度（発走前・1番人気オッズ）MID 7R PFS 23.1% 的中赤字 4/4／SOLID 5R PFS 90.8% 的中赤字 3/4／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 12R：実績 51.3% − ミラー 45.8% = Δ 5.5pt（95%区間 -64.1〜89.0、最高1R除き -28.0pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 8 | 31,910 | RECURRING |
| P1:ROLE_W_MISS | P1 | 7 | 31,910 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 1 | 6,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 13 | 55,910 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

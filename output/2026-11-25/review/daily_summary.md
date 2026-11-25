# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 26／PAPER PFS 59.9%／正式推薦 PFS 38.8%
- 第一失敗：{'CAPITAL_EFFICIENCY': 9, 'PREDICTION_ROLE_W': 14, 'PREDICTION_ROLE_P2': 2, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 5 | 36.0 | 35.6 | {'CAPITAL_EFFICIENCY': 3, 'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 1} |
| SON | 12 | 63.2 | 60.5 | {'PREDICTION_ROLE_W': 9, 'NONE': 1, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 1} |
| URW | 9 | 66.4 | 11.6 | {'CAPITAL_EFFICIENCY': 5, 'PREDICTION_ROLE_W': 4} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 30／正式試行 30・発走前送信 30／本人確認 0
2. 計算完走：Full29 30／Signed FINAL 30／KRS5000 30／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 59.9%／正式推薦 38.8%／実購入なし
5. Learning：RESULT署名検証 26／学習状態保存 26／前Raceの学習状態を結合した正式Race 30（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 26 | 15.4% | 57.7% | 15.4% | 19.2% | 7.7% | 7.7% | 19.2% | 1.38 |
| 正式推薦 | 26 | 15.4% | 46.2% | 46.2% | 80.8% | 100.0% | 46.2% | 42.3% | 1.19 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中15.4%（無作為9.0%、差+6.4）／P2 平均1.0頭 的中19.2%（無作為9.0%、差+10.3）／P3 平均1.0頭 的中7.7%（無作為9.0%、差-1.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中46.2%（無作為26.9%、差+19.2）／P2 平均6.0頭 的中80.8%（無作為53.8%、差+27.0）／P3 平均11.35頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.08/40（選択性補正込み）・能力順位 12.96/20（26R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.19/40（選択性補正込み）・能力順位 12.71/20（26R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（10.6%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 10R のうち的中赤字 6R／損益分岐の倍率 平均 8.7倍／同じ点数を無作為に選んだ場合の期待PFS 111.7%（同じ26Rの実績 59.9%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 136点 PFS 58.3%／WIDE 40点 PFS 136.2%／WIN 2点 PFS 80.0%／荒れ度（発走前・1番人気オッズ）MID 15R PFS 64.0% 的中赤字 3/5／OPEN 2R PFS 0.0% 的中赤字 0/0／SOLID 8R PFS 77.3% 的中赤字 3/5／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 25R：実績 64.5% − ミラー 38.5% = Δ 26.0pt（95%区間 -21.4〜83.1、最高1R除き 8.6pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 60,200円（38.6%）／保護層の資金比率 0.0（26R）／組だけ的中（三連単は外れ）10R・着順まで的中 2R／的中 16R のうち的中赤字 14R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 117.1%（同じ26Rの実績 38.8%）／券種別 EXACTA 390点 PFS 47.3%／TRIFECTA 650点 PFS 6.8%／TRIO 520点 PFS 72.4%／荒れ度（発走前・1番人気オッズ）MID 15R PFS 28.5% 的中赤字 7/8／OPEN 2R PFS 0.0% 的中赤字 0/0／SOLID 8R PFS 69.3% 的中赤字 6/7／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 25R：実績 39.3% − ミラー 33.6% = Δ 5.6pt（95%区間 -32.7〜51.2、最高1R除き -9.7pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 14 | 66,860 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 14 | 52,470 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 2 | 12,000 | SINGLE_OR_FEW (過大評価しない) |
| P2:CALIBRATION_BACKLOG | P2 | 26 | 112,470 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

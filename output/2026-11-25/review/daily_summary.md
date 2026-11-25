# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 34／PAPER PFS 48.7%／正式推薦 PFS 33.7%
- 第一失敗：{'CAPITAL_EFFICIENCY': 11, 'PREDICTION_ROLE_W': 18, 'PREDICTION_ROLE_P2': 3, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 10 | 20.9 | 29.6 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 2, 'NONE': 1} |
| SON | 12 | 63.2 | 60.5 | {'PREDICTION_ROLE_W': 9, 'NONE': 1, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 1} |
| URW | 12 | 50.3 | 10.2 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 6} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 36／正式試行 36・発走前送信 36／本人確認 0
2. 計算完走：Full29 36／Signed FINAL 36／KRS5000 36／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 48.7%／正式推薦 33.7%／実購入なし
5. Learning：RESULT署名検証 34／学習状態保存 34／前Raceの学習状態を結合した正式Race 36（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 34 | 17.6% | 52.9% | 17.6% | 14.7% | 5.9% | 5.9% | 14.7% | 1.38 |
| 正式推薦 | 34 | 17.6% | 47.1% | 47.1% | 73.5% | 100.0% | 47.1% | 38.2% | 1.29 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中17.6%（無作為8.9%、差+8.8）／P2 平均1.0頭 的中14.7%（無作為8.9%、差+5.8）／P3 平均1.0頭 的中5.9%（無作為8.9%、差-3.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中47.1%（無作為26.6%、差+20.5）／P2 平均6.0頭 的中73.5%（無作為53.2%、差+20.3）／P3 平均11.47頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.0/40（選択性補正込み）・能力順位 12.98/20（34R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 13.89/40（選択性補正込み）・能力順位 12.62/20（34R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（8.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 11R のうち的中赤字 7R／損益分岐の倍率 平均 8.3倍／同じ点数を無作為に選んだ場合の期待PFS 92.3%（同じ34Rの実績 48.7%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 176点 PFS 45.1%／WIDE 56点 PFS 100.9%／WIN 2点 PFS 80.0%／荒れ度（発走前・1番人気オッズ）MID 17R PFS 58.8% 的中赤字 4/6／OPEN 2R PFS 0.0% 的中赤字 0/0／SOLID 14R PFS 49.6% 的中赤字 3/5／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 33R：実績 51.7% − ミラー 39.1% = Δ 12.6pt（95%区間 -27.6〜63.2、最高1R除き -1.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 78,800円（38.6%）／保護層の資金比率 0.0（34R）／組だけ的中（三連単は外れ）11R・着順まで的中 3R／的中 19R のうち的中赤字 16R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 91.7%（同じ34Rの実績 33.7%）／券種別 EXACTA 510点 PFS 43.1%／TRIFECTA 850点 PFS 9.5%／TRIO 680点 PFS 56.7%／荒れ度（発走前・1番人気オッズ）MID 17R PFS 25.1% 的中赤字 7/8／OPEN 2R PFS 0.0% 的中赤字 0/0／SOLID 14R PFS 49.3% 的中赤字 8/10／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 33R：実績 33.9% − ミラー 37.0% = Δ -3.2pt（95%区間 -32.8〜31.2、最高1R除き -15.0pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 18 | 90,860 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 16 | 62,560 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 34 | 152,560 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

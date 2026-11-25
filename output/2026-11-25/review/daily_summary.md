# 地方版 2026-11-25 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 33／PAPER PFS 50.0%／正式推薦 PFS 34.7%
- 第一失敗：{'CAPITAL_EFFICIENCY': 11, 'PREDICTION_ROLE_W': 17, 'PREDICTION_ROLE_P2': 3, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 9 | 23.2 | 32.9 | {'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 2, 'NONE': 1} |
| SON | 12 | 63.2 | 60.5 | {'PREDICTION_ROLE_W': 9, 'NONE': 1, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 1} |
| URW | 12 | 50.3 | 10.2 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 6} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 34／正式試行 34・発走前送信 34／本人確認 0
2. 計算完走：Full29 34／Signed FINAL 34／KRS5000 34／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 50.0%／正式推薦 34.7%／実購入なし
5. Learning：RESULT署名検証 33／学習状態保存 33／前Raceの学習状態を結合した正式Race 34（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '236/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 33 | 18.2% | 54.5% | 18.2% | 15.2% | 6.1% | 6.1% | 15.2% | 1.36 |
| 正式推薦 | 33 | 18.2% | 48.5% | 48.5% | 75.8% | 100.0% | 48.5% | 39.4% | 1.3 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中18.2%（無作為8.9%、差+9.3）／P2 平均1.0頭 的中15.2%（無作為8.9%、差+6.3）／P3 平均1.0頭 的中6.1%（無作為8.9%、差-2.8）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中48.5%（無作為26.6%、差+21.8）／P2 平均6.0頭 的中75.8%（無作為53.3%、差+22.5）／P3 平均11.45頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 11.0/40（選択性補正込み）・能力順位 13.01/20（33R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.21/40（選択性補正込み）・能力順位 12.82/20（33R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 2,400円（8.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）6R・着順まで的中 0R／的中 11R のうち的中赤字 7R／損益分岐の倍率 平均 8.3倍／同じ点数を無作為に選んだ場合の期待PFS 94.1%（同じ33Rの実績 50.0%）／券種別 EXACTA 16点 PFS 0.0%／TRIFECTA 32点 PFS 0.0%／TRIO 171点 PFS 46.4%／WIDE 54点 PFS 104.6%／WIN 2点 PFS 80.0%／荒れ度（発走前・1番人気オッズ）MID 17R PFS 58.8% 的中赤字 4/6／OPEN 2R PFS 0.0% 的中赤字 0/0／SOLID 13R PFS 52.7% 的中赤字 3/5／UNKNOWN 1R PFS 0.0% 的中赤字 0/0／市場ミラーとの差 32R：実績 53.1% − ミラー 40.1% = Δ 12.9pt（95%区間 -28.5〜58.8、最高1R除き -1.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 76,400円（38.6%）／保護層の資金比率 0.0（33R）／組だけ的中（三連単は外れ）11R・着順まで的中 3R／的中 19R のうち的中赤字 16R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 94.1%（同じ33Rの実績 34.7%）／券種別 EXACTA 495点 PFS 44.4%／TRIFECTA 825点 PFS 9.8%／TRIO 660点 PFS 58.4%／荒れ度（発走前・1番人気オッズ）MID 17R PFS 25.1% 的中赤字 7/8／OPEN 2R PFS 0.0% 的中赤字 0/0／SOLID 13R PFS 53.1% 的中赤字 8/10／UNKNOWN 1R PFS 26.3% 的中赤字 1/1／市場ミラーとの差 32R：実績 34.9% − ミラー 36.8% = Δ -1.9pt（95%区間 -32.9〜32.1、最高1R除き -14.0pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 17 | 84,860 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 16 | 62,560 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 33 | 146,560 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

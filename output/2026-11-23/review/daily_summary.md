# 地方版 2026-11-23 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 17／PAPER PFS 46.7%／正式推薦 PFS 11.4%
- 第一失敗：{'PREDICTION_ROLE_P2': 6, 'CAPITAL_EFFICIENCY': 4, 'PREDICTION_ROLE_W': 7}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 6 | 30.9 | 3.8 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1, 'PREDICTION_ROLE_W': 3} |
| MIZ | 9 | 70.6 | 10.9 | {'PREDICTION_ROLE_W': 3, 'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 2} |
| SAG | 2 | 0.0 | 36.3 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 1} |

## 日次自律監査

1. 配送：管理 33R／PAPER発走前送信 23／正式試行 23・発走前送信 23／本人確認 0
2. 計算完走：Full29 23／Signed FINAL 23／KRS5000 23／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 46.7%／正式推薦 11.4%／実購入なし
5. Learning：RESULT署名検証 17／学習状態保存 17／前Raceの学習状態を結合した正式Race 23（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '100R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '100R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '30R到達', 'C26-EXT-CONNECTION': '30R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '165/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 17 | 35.3% | 64.7% | 35.3% | 5.9% | 23.5% | 5.9% | 23.5% | 1.47 |
| 正式推薦 | 17 | 35.3% | 58.8% | 58.8% | 58.8% | 100.0% | 58.8% | 23.5% | 1.41 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中35.3%（無作為10.4%、差+24.9）／P2 平均1.0頭 的中5.9%（無作為10.4%、差-4.5）／P3 平均1.0頭 的中23.5%（無作為10.4%、差+13.2）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中58.8%（無作為31.1%、差+27.7）／P2 平均6.0頭 的中58.8%（無作為62.2%、差-3.4）／P3 平均9.76頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 14.0/40（選択性補正込み）・能力順位 13.39/20（17R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 12.95/40（選択性補正込み）・能力順位 12.56/20（17R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（4.5%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）4R・着順まで的中 0R／的中 6R のうち的中赤字 2R／損益分岐の倍率 平均 7.8倍／同じ点数を無作為に選んだ場合の期待PFS 52.6%（同じ17Rの実績 46.7%）／券種別 EXACTA 7点 PFS 0.0%／TRIFECTA 8点 PFS 0.0%／TRIO 87点 PFS 34.5%／WIDE 28点 PFS 112.9%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 51.8% 的中赤字 1/2／OPEN 1R PFS 128.6% 的中赤字 0/1／SOLID 10R PFS 36.6% 的中赤字 1/3／市場ミラーとの差 17R：実績 46.7% − ミラー 74.0% = Δ -27.3pt（95%区間 -108.2〜38.5、最高1R除き -45.8pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 38,800円（38.0%）／保護層の資金比率 0.0（17R）／組だけ的中（三連単は外れ）4R・着順まで的中 3R／的中 4R のうち的中赤字 4R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 48.8%（同じ17Rの実績 11.4%）／券種別 EXACTA 255点 PFS 7.6%／TRIFECTA 425点 PFS 14.6%／TRIO 340点 PFS 10.2%／荒れ度（発走前・1番人気オッズ）MID 6R PFS 21.1% 的中赤字 2/2／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 10R PFS 6.7% 的中赤字 2/2／市場ミラーとの差 17R：実績 11.4% − ミラー 115.6% = Δ -104.3pt（95%区間 -246.6〜-15.8、最高1R除き -113.6pt）

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:ROLE_W_MISS | P1 | 7 | 42,000 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 6 | 36,000 | RECURRING |
| P1:HIT_BUT_LOSS | P1 | 4 | 12,410 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 17 | 90,410 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 26／PAPER PFS 104.1%／正式推薦 PFS 34.4%
- 第一失敗：{'PREDICTION_ROLE_W': 8, 'CAPITAL_EFFICIENCY': 13, 'PREDICTION_ROLE_P2': 4, 'NONE': 1}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 4 | 40.3 | 27.0 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 3} |
| NGY | 3 | 26.7 | 59.8 | {'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 1, 'NONE': 1} |
| SON | 11 | 173.1 | 35.0 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 1} |
| URW | 8 | 68.5 | 27.7 | {'PREDICTION_ROLE_P2': 2, 'PREDICTION_ROLE_W': 2, 'CAPITAL_EFFICIENCY': 4} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 33／正式試行 33・発走前送信 33／本人確認 0
2. 計算完走：Full29 33／Signed FINAL 33／KRS5000 33／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 104.1%／正式推薦 34.4%／実購入なし
5. Learning：RESULT署名検証 26／学習状態保存 26／前Raceの学習状態を結合した正式Race 33（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '100R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '100R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 26 | 38.5% | 73.1% | 38.5% | 11.5% | 19.2% | 3.8% | 38.5% | 1.65 |
| 正式推薦 | 26 | 30.8% | 69.2% | 69.2% | 73.1% | 100.0% | 69.2% | 46.2% | 1.54 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中38.5%（無作為9.2%、差+29.2）／P2 平均1.0頭 的中11.5%（無作為9.2%、差+2.3）／P3 平均1.0頭 的中19.2%（無作為9.2%、差+10.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中69.2%（無作為27.7%、差+41.6）／P2 平均6.0頭 的中73.1%（無作為55.3%、差+17.8）／P3 平均11.0頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.23/40（選択性補正込み）・能力順位 14.59/20（26R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.29/40（選択性補正込み）・能力順位 13.92/20（26R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,200円（5.7%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）11R・着順まで的中 0R／的中 13R のうち的中赤字 5R／損益分岐の倍率 平均 8.1倍／同じ点数を無作為に選んだ場合の期待PFS 36.4%（同じ26Rの実績 104.1%）／券種別 EXACTA 10点 PFS 45.0%／TRIFECTA 16点 PFS 0.0%／TRIO 138点 PFS 100.3%／WIDE 44点 PFS 172.0%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 13R PFS 69.9% 的中赤字 1/4／SOLID 12R PFS 104.8% 的中赤字 4/8／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 25R：実績 87.8% − ミラー 47.1% = Δ 40.7pt（95%区間 -27.9〜124.5、最高1R除き 15.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 60,500円（38.8%）／保護層の資金比率 0.0（26R）／組だけ的中（三連単は外れ）7R・着順まで的中 5R／的中 15R のうち的中赤字 14R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 27.7%（同じ26Rの実績 34.4%）／券種別 EXACTA 390点 PFS 33.1%／TRIFECTA 650点 PFS 20.5%／TRIO 520点 PFS 52.7%／荒れ度（発走前・1番人気オッズ）MID 13R PFS 31.9% 的中赤字 5/6／SOLID 12R PFS 38.9% 的中赤字 8/8／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 25R：実績 35.2% − ミラー 35.6% = Δ -0.3pt（95%区間 -19.5〜20.1、最高1R除き -6.7pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、26R×3券種）：購入 11／予算で削除 0／予想で除外 21／未生成・券種なし 46／役割馬の行き先 {'PURCHASED': 78}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、26R×3券種）：購入 31／予算で削除 10／予想で除外 24／未生成・券種なし 13／役割馬の行き先 {'PURCHASED': 190, 'BUDGET_COMPRESSED': 96}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 10R／W外 16R、2着が P2 役割 0R）：STATIC 0/10（平均4.1位）／STYLE_COND 2/10（平均3.8位） 救済2・喪失0／MARKET_COND 1/9（平均3.89位） 救済1・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 18R／W外 8R、2着が P2 役割 14R）：STATIC 14/18（平均3.89位）／STYLE_COND 14/18（平均3.67位） 救済0・喪失0／MARKET_COND 15/17（平均2.94位） 救済2・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 14 | 41,110 | RECURRING |
| P1:ROLE_W_MISS | P1 | 8 | 44,860 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 4 | 24,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 26 | 107,110 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

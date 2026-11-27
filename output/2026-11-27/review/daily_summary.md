# 地方版 2026-11-27 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 30／PAPER PFS 62.7%／正式推薦 PFS 44.5%
- 第一失敗：{'PREDICTION_ROLE_W': 12, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 13, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 7 | 4.7 | 70.7 | {'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 4} |
| SON | 12 | 96.7 | 17.6 | {'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 1} |
| URW | 11 | 62.7 | 57.2 | {'PREDICTION_ROLE_W': 6, 'NONE': 2, 'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_P2': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 33／正式試行 33・発走前送信 33／本人確認 0
2. 計算完走：Full29 33／Signed FINAL 33／KRS5000 33／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 62.7%／正式推薦 44.5%／実購入なし
5. Learning：RESULT署名検証 30／学習状態保存 30／前Raceの学習状態を結合した正式Race 33（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '300R到達', 'C17-P2-ZAI-PLACE': '300R到達', 'C18-W-PLUS-FAVORITE': '300R到達', 'C19-W-PLUS-TOP2-POP': '300R到達', 'C20-P2-PLUS-TOP3-POP': '300R到達', 'C21-BVI-L-R2-TERTILE': '295/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 30 | 43.3% | 66.7% | 43.3% | 23.3% | 23.3% | 0.0% | 26.7% | 1.7 |
| 正式推薦 | 30 | 40.0% | 60.0% | 60.0% | 86.7% | 100.0% | 80.0% | 33.3% | 1.53 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中43.3%（無作為9.1%、差+34.3）／P2 平均1.0頭 的中23.3%（無作為9.1%、差+14.3）／P3 平均1.0頭 的中23.3%（無作為9.1%、差+14.3）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.0%（無作為27.2%、差+32.8）／P2 平均6.0頭 的中86.7%（無作為54.3%、差+32.3）／P3 平均11.27頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.67/40（選択性補正込み）・能力順位 14.97/20（30R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.9/40（選択性補正込み）・能力順位 14.85/20（30R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）8R・着順まで的中 0R／的中 13R のうち的中赤字 6R／損益分岐の倍率 平均 7.1倍／同じ点数を無作為に選んだ場合の期待PFS 41.7%（同じ30Rの実績 62.7%）／券種別 TRIO 152点 PFS 40.9%／WIDE 60点 PFS 118.2%／荒れ度（発走前・1番人気オッズ）MID 18R PFS 90.5% 的中赤字 1/8／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 10R PFS 16.9% 的中赤字 4/4／UNKNOWN 1R PFS 77.1% 的中赤字 1/1／市場ミラーとの差 29R：実績 62.2% − ミラー 56.3% = Δ 6.0pt（95%区間 -45.4〜57.9、最高1R除き -8.4pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（30R）／組だけ的中（三連単は外れ）7R・着順まで的中 10R／的中 18R のうち的中赤字 15R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 27.4%（同じ30Rの実績 44.5%）／券種別 EXACTA 528点 PFS 47.2%／TRIFECTA 1272点 PFS 43.4%／荒れ度（発走前・1番人気オッズ）MID 18R PFS 48.5% 的中赤字 9/11／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 10R PFS 43.7% 的中赤字 5/6／UNKNOWN 1R PFS 25.5% 的中赤字 1/1／市場ミラーとの差 29R：実績 45.2% − ミラー 41.7% = Δ 3.5pt（95%区間 -31.2〜43.8、最高1R除き -9.9pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、30R×3券種）：購入 8／予算で削除 0／予想で除外 22／未生成・券種なし 60／役割馬の行き先 {'PURCHASED': 90}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、30R×3券種）：購入 27／予算で削除 7／予想で除外 26／未生成・券種なし 30／役割馬の行き先 {'BUDGET_COMPRESSED': 110, 'PURCHASED': 228}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 13R／W外 17R、2着が P2 役割 4R）：STATIC 4/13（平均2.77位）／STYLE_COND 5/13（平均2.62位） 救済1・喪失0／MARKET_COND 3/12（平均2.58位） 救済2・喪失2
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 18R／W外 12R、2着が P2 役割 15R）：STATIC 15/18（平均3.11位）／STYLE_COND 16/18（平均2.94位） 救済1・喪失0／MARKET_COND 17/17（平均2.65位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 15 | 59,280 | RECURRING |
| P1:ROLE_W_MISS | P1 | 12 | 61,500 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 30 | 131,280 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

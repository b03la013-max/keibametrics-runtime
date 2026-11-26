# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 37／PAPER PFS 115.4%／正式推薦 PFS 37.9%
- 第一失敗：{'PREDICTION_ROLE_W': 12, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_P2': 6, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 7 | 49.2 | 32.9 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 6} |
| NGY | 7 | 236.1 | 71.6 | {'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 1} |
| SON | 12 | 160.3 | 35.4 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 1} |
| URW | 11 | 48.1 | 22.5 | {'PREDICTION_ROLE_P2': 3, 'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 4} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 42／正式試行 42・発走前送信 42／本人確認 0
2. 計算完走：Full29 42／Signed FINAL 42／KRS5000 42／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 115.4%／正式推薦 37.9%／実購入なし
5. Learning：RESULT署名検証 37／学習状態保存 37／前Raceの学習状態を結合した正式Race 42（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 37 | 32.4% | 67.6% | 32.4% | 10.8% | 21.6% | 5.4% | 37.8% | 1.68 |
| 正式推薦 | 37 | 29.7% | 67.6% | 67.6% | 73.0% | 100.0% | 67.6% | 51.4% | 1.51 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中32.4%（無作為9.2%、差+23.3）／P2 平均1.0頭 的中10.8%（無作為9.2%、差+1.6）／P3 平均1.0頭 的中21.6%（無作為9.2%、差+12.5）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中67.6%（無作為27.5%、差+40.1）／P2 平均6.0頭 的中73.0%（無作為55.0%、差+18.0）／P3 平均11.11頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.0/40（選択性補正込み）・能力順位 14.52/20（37R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.17/40（選択性補正込み）・能力順位 13.95/20（37R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,800円（6.1%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）15R・着順まで的中 0R／的中 18R のうち的中赤字 6R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 41.8%（同じ37Rの実績 115.4%）／券種別 EXACTA 13点 PFS 34.6%／TRIFECTA 24点 PFS 0.0%／TRIO 193点 PFS 120.9%／WIDE 64点 PFS 162.3%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 20R PFS 115.4% 的中赤字 1/7／SOLID 16R PFS 92.6% 的中赤字 5/10／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 36R：実績 104.3% − ミラー 35.1% = Δ 69.2pt（95%区間 1.2〜155.2、最高1R除き 42.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 85,600円（38.6%）／保護層の資金比率 0.0（37R）／組だけ的中（三連単は外れ）11R・着順まで的中 8R／的中 22R のうち的中赤字 20R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 41.8%（同じ37Rの実績 37.9%）／券種別 EXACTA 555点 PFS 39.9%／TRIFECTA 925点 PFS 23.0%／TRIO 740点 PFS 55.1%／荒れ度（発走前・1番人気オッズ）MID 20R PFS 45.0% 的中赤字 10/12／SOLID 16R PFS 30.7% 的中赤字 9/9／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 36R：実績 38.6% − ミラー 40.6% = Δ -2.0pt（95%区間 -19.6〜15.5、最高1R除き -5.0pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、37R×3券種）：購入 15／予算で削除 0／予想で除外 30／未生成・券種なし 66／役割馬の行き先 {'PURCHASED': 111}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、37R×3券種）：購入 45／予算で削除 13／予想で除外 36／未生成・券種なし 17／役割馬の行き先 {'PURCHASED': 272, 'BUDGET_COMPRESSED': 139}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 12R／W外 25R、2着が P2 役割 1R）：STATIC 1/12（平均4.08位）／STYLE_COND 3/12（平均3.83位） 救済2・喪失0／MARKET_COND 3/11（平均3.36位） 救済2・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 25R／W外 12R、2着が P2 役割 19R）：STATIC 20/25（平均3.84位）／STYLE_COND 20/25（平均3.68位） 救済0・喪失0／MARKET_COND 22/24（平均2.96位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 20 | 60,210 | RECURRING |
| P1:ROLE_W_MISS | P1 | 12 | 64,990 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 6 | 36,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 37 | 150,210 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

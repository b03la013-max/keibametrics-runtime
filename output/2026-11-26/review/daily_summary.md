# 地方版 2026-11-26 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 36／PAPER PFS 112.5%／正式推薦 PFS 39.0%
- 第一失敗：{'PREDICTION_ROLE_W': 11, 'CAPITAL_EFFICIENCY': 17, 'PREDICTION_ROLE_P2': 6, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KNZ | 7 | 49.2 | 32.9 | {'PREDICTION_ROLE_W': 1, 'CAPITAL_EFFICIENCY': 6} |
| NGY | 6 | 235.7 | 83.6 | {'PREDICTION_ROLE_W': 1, 'PREDICTION_ROLE_P2': 2, 'NONE': 2, 'CAPITAL_EFFICIENCY': 1} |
| SON | 12 | 160.3 | 35.4 | {'CAPITAL_EFFICIENCY': 6, 'PREDICTION_ROLE_W': 5, 'PREDICTION_ROLE_P2': 1} |
| URW | 11 | 48.1 | 22.5 | {'PREDICTION_ROLE_P2': 3, 'PREDICTION_ROLE_W': 4, 'CAPITAL_EFFICIENCY': 4} |

## 日次自律監査

1. 配送：管理 48R／PAPER発走前送信 41／正式試行 41・発走前送信 41／本人確認 0
2. 計算完走：Full29 41／Signed FINAL 41／KRS5000 41／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 112.5%／正式推薦 39.0%／実購入なし
5. Learning：RESULT署名検証 36／学習状態保存 36／前Raceの学習状態を結合した正式Race 41（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '100R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '100R到達', 'C9-BENTER-COMBINATION': '100R到達', 'C10-HARVILLE-DISCOUNT': '100R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '100R到達', 'C14-FORMAL-P2BOX20-ONLY': '100R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '100R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '100R到達', 'C17-P2-ZAI-PLACE': '100R到達', 'C18-W-PLUS-FAVORITE': '100R到達', 'C19-W-PLUS-TOP2-POP': '100R到達', 'C20-P2-PLUS-TOP3-POP': '100R到達', 'C21-BVI-L-R2-TERTILE': '266/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 36 | 33.3% | 69.4% | 33.3% | 11.1% | 22.2% | 5.6% | 38.9% | 1.67 |
| 正式推薦 | 36 | 30.6% | 69.4% | 69.4% | 72.2% | 100.0% | 69.4% | 52.8% | 1.56 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中33.3%（無作為9.2%、差+24.1）／P2 平均1.0頭 的中11.1%（無作為9.2%、差+1.9）／P3 平均1.0頭 的中22.2%（無作為9.2%、差+13.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中69.4%（無作為27.6%、差+41.9）／P2 平均6.0頭 的中72.2%（無作為55.2%、差+17.1）／P3 平均11.08頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.08/40（選択性補正込み）・能力順位 14.58/20（36R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 16.42/40（選択性補正込み）・能力順位 14.12/20（36R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 1,800円（6.2%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）15R・着順まで的中 0R／的中 17R のうち的中赤字 6R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 37.2%（同じ36Rの実績 112.5%）／券種別 EXACTA 13点 PFS 34.6%／TRIFECTA 24点 PFS 0.0%／TRIO 188点 PFS 124.1%／WIDE 62点 PFS 140.6%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 20R PFS 115.4% 的中赤字 1/7／SOLID 15R PFS 84.9% 的中赤字 5/9／UNKNOWN 1R PFS 577.1% 的中赤字 0/1／市場ミラーとの差 35R：実績 100.9% − ミラー 36.0% = Δ 65.0pt（95%区間 -4.9〜155.8、最高1R除き 37.3pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 83,300円（38.6%）／保護層の資金比率 0.0（36R）／組だけ的中（三連単は外れ）11R・着順まで的中 8R／的中 22R のうち的中赤字 20R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 29.7%（同じ36Rの実績 39.0%）／券種別 EXACTA 540点 PFS 41.1%／TRIFECTA 900点 PFS 23.6%／TRIO 720点 PFS 56.6%／荒れ度（発走前・1番人気オッズ）MID 20R PFS 45.0% 的中赤字 10/12／SOLID 15R PFS 32.7% 的中赤字 9/9／UNKNOWN 1R PFS 13.3% 的中赤字 1/1／市場ミラーとの差 35R：実績 39.7% − ミラー 41.8% = Δ -2.1pt（95%区間 -19.9〜15.8、最高1R除き -5.2pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、36R×3券種）：購入 15／予算で削除 0／予想で除外 29／未生成・券種なし 64／役割馬の行き先 {'PURCHASED': 108}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、36R×3券種）：購入 45／予算で削除 13／予想で除外 34／未生成・券種なし 16／役割馬の行き先 {'PURCHASED': 265, 'BUDGET_COMPRESSED': 134}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 12R／W外 24R、2着が P2 役割 1R）：STATIC 1/12（平均4.08位）／STYLE_COND 3/12（平均3.83位） 救済2・喪失0／MARKET_COND 3/11（平均3.36位） 救済2・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 25R／W外 11R、2着が P2 役割 19R）：STATIC 20/25（平均3.84位）／STYLE_COND 20/25（平均3.68位） 救済0・喪失0／MARKET_COND 22/24（平均2.96位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 20 | 60,210 | RECURRING |
| P1:ROLE_W_MISS | P1 | 11 | 58,990 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 6 | 36,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 36 | 144,210 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

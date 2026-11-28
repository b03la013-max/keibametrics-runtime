# 地方版 2026-11-28 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 11／PAPER PFS 26.1%／正式推薦 PFS 51.7%
- 第一失敗：{'PREDICTION_ROLE_P2': 4, 'CAPITAL_EFFICIENCY': 3, 'NONE': 1, 'PREDICTION_ROLE_W': 3}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| KOC | 5 | 15.6 | 91.7 | {'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 1, 'NONE': 1, 'PREDICTION_ROLE_W': 1} |
| SAG | 6 | 33.5 | 18.3 | {'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 2, 'CAPITAL_EFFICIENCY': 2} |

## 日次自律監査

1. 配送：管理 24R／PAPER発走前送信 15／正式試行 15・発走前送信 15／本人確認 0
2. 計算完走：Full29 15／Signed FINAL 15／KRS5000 15／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 26.1%／正式推薦 51.7%／実購入なし
5. Learning：RESULT署名検証 11／学習状態保存 11／前Raceの学習状態を結合した正式Race 15（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '100R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '300R到達', 'C17-P2-ZAI-PLACE': '300R到達', 'C18-W-PLUS-FAVORITE': '300R到達', 'C19-W-PLUS-TOP2-POP': '300R到達', 'C20-P2-PLUS-TOP3-POP': '300R到達', 'C21-BVI-L-R2-TERTILE': '300R到達'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 11 | 54.5% | 90.9% | 54.5% | 0.0% | 36.4% | 9.1% | 18.2% | 1.91 |
| 正式推薦 | 11 | 54.5% | 72.7% | 72.7% | 63.6% | 100.0% | 90.9% | 27.3% | 1.73 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中54.5%（無作為10.4%、差+44.2）／P2 平均1.0頭 的中0.0%（無作為10.4%、差-10.4）／P3 平均1.0頭 的中36.4%（無作為10.4%、差+26.0）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中72.7%（無作為31.2%、差+41.6）／P2 平均6.0頭 的中63.6%（無作為62.3%、差+1.3）／P3 平均9.82頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 18.09/40（選択性補正込み）・能力順位 14.87/20（11R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 15.34/40（選択性補正込み）・能力順位 14.48/20（11R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 600円（6.8%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）2R・着順まで的中 0R／的中 4R のうち的中赤字 4R／損益分岐の倍率 平均 8.0倍／同じ点数を無作為に選んだ場合の期待PFS 20.7%（同じ11Rの実績 26.1%）／券種別 EXACTA 7点 PFS 187.1%／TRIFECTA 8点 PFS 0.0%／TRIO 55点 PFS 9.8%／WIDE 16点 PFS 28.1%／WIN 2点 PFS 0.0%／荒れ度（発走前・1番人気オッズ）MID 2R PFS 0.0% 的中赤字 0/0／SOLID 9R PFS 31.5% 的中赤字 4/4／市場ミラーとの差 11R：実績 26.1% − ミラー 65.3% = Δ -39.2pt（95%区間 -134.6〜22.7、最高1R除き -66.1pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（11R）／組だけ的中（三連単は外れ）4R・着順まで的中 3R／的中 6R のうち的中赤字 5R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 11.8%（同じ11Rの実績 51.7%）／券種別 EXACTA 192点 PFS 33.3%／TRIFECTA 468点 PFS 59.2%／荒れ度（発走前・1番人気オッズ）MID 2R PFS 214.1% 的中赤字 0/1／SOLID 9R PFS 15.6% 的中赤字 5/5／市場ミラーとの差 11R：実績 51.7% − ミラー 46.8% = Δ 4.9pt（95%区間 -68.6〜93.6、最高1R除き -33.4pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、11R×3券種）：購入 3／予算で削除 0／予想で除外 12／未生成・券種なし 18／役割馬の行き先 {'PURCHASED': 33}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、11R×3券種）：購入 8／予算で削除 4／予想で除外 11／未生成・券種なし 10／役割馬の行き先 {'PURCHASED': 81, 'BUDGET_COMPRESSED': 27}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 6R／W外 5R、2着が P2 役割 0R）：STATIC 0/6（平均4.5位）／STYLE_COND 0/6（平均4.67位） 救済0・喪失0／MARKET_COND 1/6（平均3.17位） 救済1・喪失0
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 8R／W外 3R、2着が P2 役割 4R）：STATIC 6/8（平均4.75位）／STYLE_COND 6/8（平均4.75位） 救済0・喪失0／MARKET_COND 7/8（平均2.88位） 救済2・喪失1

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 5 | 21,580 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 4 | 24,000 | RECURRING |
| P1:ROLE_W_MISS | P1 | 3 | 13,430 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 11 | 51,580 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

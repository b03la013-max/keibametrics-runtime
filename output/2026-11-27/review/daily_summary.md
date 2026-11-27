# 地方版 2026-11-27 日次総括（途中）（自動・推薦試算・実購入なし）

- 反省済みRace 28／PAPER PFS 62.7%／正式推薦 PFS 46.6%
- 第一失敗：{'PREDICTION_ROLE_W': 11, 'PREDICTION_ROLE_P2': 3, 'CAPITAL_EFFICIENCY': 12, 'NONE': 2}

| 場 | Race | PAPER PFS | 正式 PFS | 第一失敗 |
|---|---|---|---|---|
| NGY | 6 | 5.5 | 77.4 | {'PREDICTION_ROLE_W': 2, 'PREDICTION_ROLE_P2': 1, 'CAPITAL_EFFICIENCY': 3} |
| SON | 12 | 96.7 | 17.6 | {'CAPITAL_EFFICIENCY': 7, 'PREDICTION_ROLE_W': 4, 'PREDICTION_ROLE_P2': 1} |
| URW | 10 | 56.4 | 62.9 | {'PREDICTION_ROLE_W': 5, 'NONE': 2, 'CAPITAL_EFFICIENCY': 2, 'PREDICTION_ROLE_P2': 1} |

## 日次自律監査

1. 配送：管理 36R／PAPER発走前送信 32／正式試行 32・発走前送信 32／本人確認 0
2. 計算完走：Full29 32／Signed FINAL 32／KRS5000 32／NO-BET 0／HOLD なし
3. 精度：下表
4. PFS：PAPER 62.7%／正式推薦 46.6%／実購入なし
5. Learning：RESULT署名検証 28／学習状態保存 28／前Raceの学習状態を結合した正式Race 32（Production変更なし）
6. 障害・改善：停止 なし／正式停止 なし／OOS進捗 {'C1-FAV-AXIS-TRIO': '300R到達', 'C2-DANGER-FAV-RANK-A': '100R到達', 'C3-FAV-AS-W-WHEN-DIVERGED': '100R到達', 'C4-LOCAL-CAP-60': '300R到達', 'C5-SMALL-POINTS': '300R到達', 'C6-CHECK10-REVISION': '100R到達', 'C7-KAMETANI-BUY-MATCH': '30R到達', 'C8-ODDS-GAP-FAVORITE': '300R到達', 'C9-BENTER-COMBINATION': '300R到達', 'C10-HARVILLE-DISCOUNT': '300R到達', 'C11-FIXED-2-4-8-VS-AKI-FORM': '300R到達', 'C12-AKI-VS-MARKET-ROUGHNESS': '300R到達', 'C25-AKI-FORM-SAME-POINTS': '100R到達', 'C26-EXT-CONNECTION': '100R到達', 'C13-FORMAL-MIX-P2BOX20': '300R到達', 'C14-FORMAL-P2BOX20-ONLY': '300R到達', 'C15-FORMAL-MIX-WAXIS-TRIO': '300R到達', 'C22-KEEP-MEC-TRIO20': '100R到達', 'C23-THIRD3-BY-PAIR': '100R到達', 'C24-W-PLUS-TOP2POP-SAME-BUDGET': '100R到達', 'C16-W-INDEX-CONSENSUS': '300R到達', 'C17-P2-ZAI-PLACE': '300R到達', 'C18-W-PLUS-FAVORITE': '300R到達', 'C19-W-PLUS-TOP2-POP': '300R到達', 'C20-P2-PLUS-TOP3-POP': '300R到達', 'C21-BVI-L-R2-TERTILE': '295/300R'}

## 精度（回収とは別に測定）

| 系統 | Race | ◎1着率 | 1着が事前3位以内 | W的中 | P2的中 | P3的中 | 1着が買い目頭 | 3連複組合せ含有 | 平均Top3捕捉 |
|---|---|---|---|---|---|---|---|---|---|
| PAPER | 28 | 42.9% | 67.9% | 42.9% | 25.0% | 25.0% | 0.0% | 28.6% | 1.75 |
| 正式推薦 | 28 | 39.3% | 60.7% | 60.7% | 89.3% | 100.0% | 82.1% | 35.7% | 1.57 |
- PAPER 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均1.0頭 的中42.9%（無作為9.1%、差+33.7）／P2 平均1.0頭 的中25.0%（無作為9.1%、差+15.9）／P3 平均1.0頭 的中25.0%（無作為9.1%、差+15.9）
- 正式推薦 役割の頭数と的中（無作為＝頭数÷出走頭数）：W 平均3.0頭 的中60.7%（無作為27.4%、差+33.3）／P2 平均6.0頭 的中89.3%（無作為54.9%、差+34.4）／P3 平均11.14頭 的中100.0%（無作為100.0%、差+0.0）
- PAPER KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 17.18/40（選択性補正込み）・能力順位 15.12/20（28R平均）
- 正式推薦 KMS v1.2 第9・10条の式（参考値、KMX・PFSとは別）：役割捕捉 17.08/40（選択性補正込み）・能力順位 14.9/20（28R平均）
- PAPER 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 None（0R）／組だけ的中（三連単は外れ）8R・着順まで的中 0R／的中 12R のうち的中赤字 6R／損益分岐の倍率 平均 7.1倍／同じ点数を無作為に選んだ場合の期待PFS 39.5%（同じ28Rの実績 62.7%）／券種別 TRIO 142点 PFS 43.7%／WIDE 56点 PFS 110.7%／荒れ度（発走前・1番人気オッズ）MID 17R PFS 88.3% 的中赤字 1/7／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 9R PFS 18.7% 的中赤字 4/4／UNKNOWN 1R PFS 77.1% 的中赤字 1/1／市場ミラーとの差 27R：実績 62.1% − ミラー 60.4% = Δ 1.7pt（95%区間 -52.5〜54.1、最高1R除き -13.9pt）
- 正式推薦 回収の頑健性（B2・証拠のみ、券面は変えない）：券種をまたぐ同じ組への追加投資 0円（0.0%）／保護層の資金比率 0.0（28R）／組だけ的中（三連単は外れ）7R・着順まで的中 10R／的中 17R のうち的中赤字 14R／損益分岐の倍率 平均 60.0倍／同じ点数を無作為に選んだ場合の期待PFS 26.4%（同じ28Rの実績 46.6%）／券種別 EXACTA 495点 PFS 46.7%／TRIFECTA 1185点 PFS 46.6%／荒れ度（発走前・1番人気オッズ）MID 17R PFS 51.4% 的中赤字 9/11／OPEN 1R PFS 0.0% 的中赤字 0/0／SOLID 9R PFS 45.2% 的中赤字 4/5／UNKNOWN 1R PFS 25.5% 的中赤字 1/1／市場ミラーとの差 27R：実績 47.4% − ミラー 43.7% = Δ 3.7pt（95%区間 -34.0〜46.1、最高1R除き -10.7pt）
- PAPER 実着順の組の行き先（B1・証拠のみ、28R×3券種）：購入 8／予算で削除 0／予想で除外 20／未生成・券種なし 56／役割馬の行き先 {'PURCHASED': 84}
- 正式推薦 実着順の組の行き先（B1・証拠のみ、28R×3券種）：購入 26／予算で削除 6／予想で除外 24／未生成・券種なし 28／役割馬の行き先 {'BUDGET_COMPRESSED': 99, 'PURCHASED': 213}
- PAPER 頭別P2（B3 n92・影の計測、勝ち馬W内 12R／W外 16R、2着が P2 役割 4R）：STATIC 4/12（平均2.67位）／STYLE_COND 5/12（平均2.5位） 救済1・喪失0／MARKET_COND 3/11（平均2.36位） 救済2・喪失2
- 正式推薦 頭別P2（B3 n92・影の計測、勝ち馬W内 17R／W外 11R、2着が P2 役割 14R）：STATIC 14/17（平均3.12位）／STYLE_COND 15/17（平均2.94位） 救済1・喪失0／MARKET_COND 16/16（平均2.5位） 救済3・喪失0

## 改善優先順位（P0→P1→P2、件数・影響額順）

| ID | 区分 | 件数 | 影響額(円) | 証拠の強さ |
|---|---|---|---|---|
| P1:HIT_BUT_LOSS | P1 | 14 | 55,100 | RECURRING |
| P1:ROLE_W_MISS | P1 | 11 | 55,500 | RECURRING |
| P1:ROLE_P2_MISS | P1 | 3 | 18,000 | RECURRING |
| P2:CALIBRATION_BACKLOG | P2 | 28 | 121,100 | RECURRING |

<sub>PROPOSED_ONLY (adoption requires genuine forward OOS + Owner review; no automatic Production change)</sub>

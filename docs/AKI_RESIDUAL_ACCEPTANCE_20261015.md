# LOCAL AKI残存課題・受入れ判定 — 2026-10-15

**Correctness repair VERIFIED / Selection performance REJECTED / NON-PRODUCTION / NO-AUTO-PROMOTION**

## A — 現行完成度

開始時mainは `f0d012f5423528cb1d208cddddb71b743b6db51a`。Family R51、LOCAL `KM-LOCAL-RENDERED-INTEGRITY-20260827-R3`、Production MEC-R3、Engine1.1.0、parameter0.1-provisional。PR262/263/264/265はDraft・未Merge、264→263及び265→264の依存を維持。PR276のRace-Key/配送/結果保存修復も未Merge。本報告は旧09:06の404を現在状態へ流用しない。

最新mainの元AKI台帳は**19戦・4開催日**、20,200→11,920円、PFS59.01%、損益−8,280円。Production同19戦409,500→212,350円、51.86%。10/14の4R・5Rが増分。10R・11R・12RはSigned RESULTが存在するが、OFFICIAL_RESULT checkpointが保存されず、現行TrackerはWAITING_OFFICIAL_RESULTでHOLD。欠測を解除して22戦と称さない。保存方針修復は既存PR276へ置き、重複実装しない。

今回の比較標本は**元17戦固定**。全SOURCE/PRE_KRS/KRS/FINAL/RESULT85件を公開Ed25519 anchorでoffline検証し、現行Runtime `/verify`でも85件valid。公式SOURCE原文736個のhashを照合。元KRS実回数85,000を再照合しただけで新規実行へ加算しない。SOURCEから29指数を独立再計算してSelectorを再実行。元17戦のReceipt、Ticket、OOS台帳、R1/R2過去レポートを変更しない。Actual Purchase PFSはnull。

## B — 列別の残存失敗とOwner

`research/aki_residual_20261015/residual_audit.json.gz` は17戦×4方式の完全比較。結果前情報、結果後Top3/非的中券、Counterfactual資金比較を区別する。Prediction Universe、W選択、Head-local Pair、Pair-conditioned Third、Exact orientation、券面捕捉を独立保存する。購入券面によるWinner CaptureとW列Captureも同一視しない。

|川崎10/13|Original AKI|PR262 Reference|PR265 R1|PR265 R2|
|---|---|---|---|---|
|1R 6→1→2|W選択喪失、Trio払戻あり|6→1が元SEMANTIC_ONLY|W選択喪失|W回復、Pairは非Materialのまま|
|3R 5→3→2|正解HeadのP2削除|P2削除、Trio払戻あり|P2削除|P2削除|
|6R 1→7→4|6点600→2,300円|W1は保持、P2=7削除|W1喪失|W1回復、P2=7削除、9点900→0|
|7R 1→2→11|8点800→3,520円|条件付きThirdをPROTECTへ変更しExact方向喪失|W1喪失|Exact回復、33点3,300→3,520円|
|9R 7→2→3|W7保持、P2=2削除|W7削除|W7削除|W7削除|
|10R 1→3→2|P2=3は元Universeにない|同じ上流欠落|同じ上流欠落|同じ上流欠落|
|12R 10→8→12|W10保持、P2=8削除|Exact orientation喪失|44点4,400→20,970円|同じ44点、12R依存は残る|

R1はW Roleへ入場制限した後のscore spanをgap単位へ用い、R2はWだけobserved active fieldのspanへ戻す。式/係数を変えなくても選択幅を変えるため、これは性能変更として隔離する。6R Head1のP2=7はgap19.71117 > limit9.35955で除外。9R Winner7はgap13.17204 > R2 limit10.41666。予算ではなくscore-gap判断が支配的。

R1/R2は上流RoleとPair/ThirdのPURCHASE/PROTECTを保存する。PR262 Referenceは独立Numerical PAPERモデルであり、元Static Role外の選択もある。Referenceの高PFSを、そのままProduction Universe内選択品質の証明へ転用しない。旧ReferenceがPROTECT関係を生成することと、元PURCHASE方向を保持するR1のCorrectnessは別比較。PROTECTを全Exactへ昇格させない。

10R UNKNOWNのRole欠落はPrediction Ownerへ返す。Stage/Path理由、Static、KRS独立支持、失われるThird Worldは測定へ保存するが、既存gap計算はこれらの独立機構を直接比較していない。未知条件のUNKNOWNを自動的な強弱又は買い義務へ変換しない。

## C/D — Correctnessと性能変更の分離・修復

再利用：SOURCE identity、全29指数Provenance、欠測を支持としない入場条件、凍結Role Universe、Head別P2/Pair別P3、元Exact/Set保護の意味、結果前Freeze、整数Stake、署名lineage、Checkpoint及び独立精算。数値式/閾値変更なし。

棄却：R1/R2の現行Selection Policy。R2は元成功6Rを回復せず、7Rを8→33点へ増やし、PFS/DDも劣化。新しい幅/係数/指数/Selectorは作らない。両modeをFORWARD_PAPERへ指定すると、既存Selectorが `PERFORMANCE_REJECTED_ARM_FORWARD_FORBIDDEN` で停止する。Historical Replayは引き続き再現できる。旧prospective planのR2という改訂名と、HEAD_LOCAL_VNEXT_R2というSelection Policyは別物。

確認されたCorrectness修復は次の3点。

1. SelectionがNO_BETなのにReference経路がPAPER券面を返す不整合を修復。Semantic MECは保持し、券面出力だけ0件へ終端。
2. 明示HARD_RACE_BUDGETのinsufficient_action=NO_BETが、研究情報GateのPAPERで上書きされる不整合を修復。既存Capital Policy本体は変更せず、LOCAL PAPER接続で登録済み非投資判断を守る。insufficient_action=PAPERは非投資の診断券面として残し、購入権限は常にfalse。
3. 旧分析toolがselection hash作成後にremoved_capitalを同じ選択オブジェクトへ書き込む混同を修復。今後のCapital測定はdeepcopyしたpost_result_capital_pair_lossesへ分離。旧レポートの派生値混入は履歴として保持し、事後書換えしない。

修正前4 FAILを保存（予算ケースは同一実凍結入力、ASI failureはfault injection、Forward禁止はmode guardの試験）。修正後、元Reference/R1/R2全17戦の実選択・券面が不変であることと、選択hashの自己整合、Budget NO_BET、PAPER非投資、棄却方式Forward拒否を検証。NO_BET改善を予測性能改善又はPFS100%と称さない。

## E — 17戦比較・性能受入れ

|Arm|投資|払戻|PFS|全損|Ticket W/Pair/Exact捕捉|最大DD|最多払戻比率|
|---|---:|---:|---:|---:|---|---:|---:|
|Production|361,000|193,310|53.55%|2|16/14/11|172,860|27.31%|
|Original AKI|17,800|10,700|60.11%|11|10/5/4|9,200|32.90%|
|PR262 Reference Replay|85,800|98,260|114.52%|6|13/8/0|33,360|39.81%|
|PR265 R1 Replay|68,700|65,100|94.76%|12|10/5/3|37,710|56.59%|
|PR265 R2 Replay|89,800|69,550|77.45%|10|13/6/4|48,960|52.97%|
|R1 Capital-only Replay|361,000|229,940|63.70%|12|10/5/3|209,770|34.99%|
|R2 Capital-only Replay|361,000|242,360|67.14%|10|13/6/4|197,350|33.20%|

R1→R2は+211点/+21,100円、払戻+4,450円。結果後観測の非的中券は677→885本。非的中券を全て「発走前に誤りと分かるFalse Addition」と断定しない。OHI7戦及びVenue/距離別、上位3払戻除外、負け連続、Hit-but-Lossを完全保存。Referenceも最大払戻除外PFS91.12%、上位3除外30.14%で、持続的利益を証明していない。

選択仮説の5条件への回答：削除したMaterialを事前情報から合理的に区別できることは未実証。Stage/Pathで説明可能な例はあるが採否を判別する比較Evidenceが不足。W幅拡大の追加券・資金負担は上記の通りで正当化できない。価格/較正がないため期待価値による説明も不可。単日結果への過適合を避け、**新Selection Candidateは0件**とする。元AKIを比較対象として維持する。

## F — Capital PAPER、合法matched比較、NO-BET

既存PR264測定を再利用し、Head/Pair/Exact Third/Core/Protection/その他tier/券種Exposure、失われるWorld、追加投資を保存。Productionの100円均等配分は不変。未分類tierやTailをPeripheralへ勝手に読み替えない。Core Densityだけで経済的合理性を断定しない。券種オッズの結果前panelがないためCore-Hit Recoverability/EV/KellyはHOLD。

既存matched comparatorの固定namespaceを再利用した整数100円Counterfactual。結果を使わないhash順で同点数subsetを作るが、これは合理的Selector又は結果前OOSの証明ではない。単純な比例倍率ではない。

|比較|同一投資/Arm|Production|Original AKI|Reference|R1|R2|
|---|---:|---:|---:|---:|---:|---:|
|Full coverage同予算|364,300|53.32%|38.88%|124.75%|72.41%|65.15%|
|同予算・同点数subset|15,700|0.00%|68.15%|32.29%|16.18%|22.10%|

上表は独立Replay対照で、元17戦成績を上書きしない。全券面・Stake・Drawdownも保存。0/2,000/5,000/10,000円の204明示PAPERシナリオでは101ケースがNO_BET。ユーザー資金上限ではない。Semanticを予算で削らず、成立しなければ非投資とする。回避Stake/失われた払戻の結果後機会費用を保存するが、最適な見送り規則が証明されたとはしない。

## G — 外部Runtime受入れ

Railway project `kmjrawitnessv061` / service `witnessstrictimage`、Deployment `acf63364-0235-42ea-b68d-fbe931fcf51f` SUCCESS、staged changesなし。復旧は所有者による10/14 15:13 JSTの既存配備であり、本作業の課金/plan/鍵設定/Deployではない。正本Endpointは `https://witnessstrictimage-production.up.railway.app`。

health/Canary PASS、全bundle fingerprint `2141fd66d2417c6488ac10349dca55820f45e7354d43e33f8fa4317969d3fa2e`、Engine SHA `9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421`、parameter SHA `d8c027ee5bcc8fd3d2c248e8059b341776be38910e833d7589f09ab817c161f5`、公開Trust Anchor/Signerは一致。署名秘密鍵は取得・回転しない。旧OCI image digestや依存package byteまで同一と証明したわけではない。

今回の修復コードによる実API受入れ：凍結SOURCE再利用→live verify→新PRE_KRS→実KRS20,000回→FINAL→RESULT→別PAPER精算/Reflection/Learning。Execution `LOCAL-AKI-REPLAY-0d5f6b8b0ea97c90`、FINAL `4c73d163df308d910f0e71e57458282161fda72ac20283c740e73b3e45182ca1`、RESULT `2bdb56351e6827786e91c7e958c3e757c8cca7a99cd5498ca45589f252a5faa4`。初回diagnostic署名も保存し、最終試験は同一KRS input/Receiptを再利用。新実回数合計20,000であり40,000と重複計上しない。

100円は明示的な障害再現PAPERシナリオ。棄却R1の選択は不変、Capital NO_BET、Canonical/PAPER券0、投資0、払戻0、PFS null。未来発走前の予測ではなくPOST_EVENT_REPLAY。新Forward0。raw Receipt archive/manifest、入力hash・実回数・署名往復・失敗前後・Current Runtimeログはevidence参照。

## H/I/J — Forward状態・PR・残存条件

新Selection Armの事前登録は**REJECTED / 0件**。性能基準を満たす候補がないため無理に登録しない。旧17戦/最新元AKI19戦/PR262旧pilot/今回のReplay/新コードForwardを混合しない。実行CorrectnessがPASSでも、予測・Capital性能受入れやProduction昇格は別。

PR265を最小差分で更新し、Draft維持。旧265レポートの404は当時の事実として保持し、最新判定は本報告を優先。関連24テストファイル233件PASS、修正前後ログを保存。PR276を参照・依存関係とし、同じWorkflow修復を本PRへコピーしない。CI結果はPR本文に実Run参照で記録する。

Promotion残存条件：事前Evidenceで独立選択仮説成立→同一SOURCEのProduction/Original AKI/候補→Code/Policy/Static/Ticket/Stakeの結果前Freeze→発走前Signed FINAL及びユーザーDelivery→公式RESULT/Settlement→真正Forward最低30戦・3開催日→絶対PFS100%以上、Production相対比較、Drawdown、同予算/同点数、Coverage/HBL/集中/最大払戻除外条件→Human Review。30戦だけで自動昇格しない。

|成果物|判定|
|---|---|
|A 完成度判定|COMPLETED / 正式実用化はPENDING|
|B 列別残存失敗|VERIFIED HISTORICAL / 予測増分価値PENDING|
|C R2 CorrectnessとPolicy分離|COMPLETED / R2 Policy REJECTED|
|D 最小修復・不採用理由|VERIFIED / 新Selection Candidateなし|
|E 17戦比較|VERIFIED HISTORICAL / 新Forwardではない|
|F Capital PAPER|VERIFIED CONFORMANCE / 経済性PENDING、価格BLOCKED|
|G Runtime|VERIFIED LIVE REPLAY / 未知未来全日実行PENDING|
|H 新Forward事前登録|REJECTED / 0、新実績0|
|I PR/CI|Draft更新、終端CI結果はPR参照|
|J Production昇格|PENDING / Owner承認なし|

Production Authority、数値、Engine、parameter、MEC-R3、Capital本体、元17戦OOS・Signed FINAL/RESULT・旧Forward登録の変更なし。購入、課金、配備、無断Merge/Activation/Promotionなし。価格不足、3件公式Checkpoint欠落、配送ACK、真正未来性能を未達のまま明示する。

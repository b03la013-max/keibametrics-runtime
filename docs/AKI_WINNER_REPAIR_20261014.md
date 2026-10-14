# AKI Winner修復・候補再選別 — 2026-10-14

**CANDIDATE / NON-PRODUCTION / PERFORMANCE-ACCEPTANCE-FAILED / EXTERNAL-RUNTIME-BLOCKED**

## A — Runtime: BLOCKED; source reconstruction VERIFIED

最新main `951d3da7ad619e160d3b0ab836b35aef563e2301`。参考mainとの差分はJRA当日statusのみ。Family R51、LOCAL R3、MEC-R3、29指数63規則、Capital、Engine、parameter、元17戦台帳は維持。PR262/263/264/265はDraft/unmerged。265のbase264→263と262継承を維持。

Railway `keibametrics-runtime`はservices/deploymentsとも0。ただし正本Gatewayは別project `kmjrawitnessv061` の `witnessstrictimage` を指す。旧Deployment f02bb3d4-d700-43c8-b181-f9649cf8e276は2026-10-14 03:05:32 JSTにREMOVED。APIのcanRedeployフラグはBuild復元成功の証明ではない。今回の09:06 JST /healthと/verifyは404 Application not found。前回のtrial expired拒否を保持し、今回は課金・plan・配備・変数変更を一切実施していない。

凍結Git f0d23766から9/9 wrapper/sourceモジュールとparameter SHAを再構成・照合できた。Engine SHA 9929df…とparameter d8c027…、公開Trust Anchorは保存されている。Engine本体bytes、image digest、凍結依存、Signer秘密鍵の復元は未実証。python:3.13-slimというmutable tagだけで旧Build同一性を主張しない。秘密鍵は取得・公開・回転していない。現行SOURCE/FINAL署名往復、CanaryはBLOCKED。保存済み署名のoffline verifyをlive受入れと混同しない。

## B — Code-level Root Cause: VERIFIED

`runtime/local_aki_columns.py:build()` のRole admission (lines105–111) → span (138–146) が原因。R1は元W Roleへ制限した値のmax−minを、FIELD-relative gap式の正規化単位に使う。選べる馬の集合を限定するとgapの許容幅まで縮み、同じleader/riskでもWinnerを落とす。R2は観測済み全active fieldのspanを再利用し、選択可能集合は元W Roleへ限定したまま。式・指数・risk・閾値・上流Static/KRS・P2/P3式は変えない。

|Race / Winner|gap|R1 span / limit|R2 field span / limit|R1→R2 W|残る失敗|
|---|---:|---:|---:|---|---|
|1R / 6|14.639651|14.639651 / 8.322863|38.257977 / 21.750240|['2', '3'] → ['2', '3', '1', '7', '6']|6→1は元SEMANTIC_ONLY; 購入強制なし|
|6R / 1|6.078468|18.032349 / 5.122571|26.444141 / 7.512165|['2'] → ['2', '1']|Head1のP2=7 score-gap除外; Exact未回復|
|7R / 1|4.319182|10.189876 / 3.542371|36.429761 / 12.664310|['9', '2'] → ['9', '2', '1', '11']|Exact回復するが8→33点、資金増|
|9R / 7|13.172038|13.172038 / 3.544954|38.705333 / 10.416659|['3'] → ['3', '1']|gap13.17 > limit10.42; ReferenceでもW非選択|

**前回報告の訂正**：PR262 Referenceは6R・7RのWinner1をW列に保持していた。6RはP2=7、7RはExact orientationで正解券を失う。PR265 R1で発生したW喪失と別工程。9RはReferenceもZAI-WIN gapでWinner7を落とす。4件ともStatic W UniverseにはWinnerが存在するため、Universe欠落・物理Engine係数の問題とは断定しない。

6R Head1 P2pool leader4のlimit9.35955に対し7のgap19.71117。予算ではなく条件付きscore-gap除外。9Rは既存W順位/幅政策の反例。結果からriskを広げたりCORE全件購入へ変更しない。

## C/D/E — Minimal repair and historical comparison: VERIFIED / candidate REJECTED

R2 opt-inを同一Selectorへ追加。別Selector/Calculator/Workflowなし。PR262 default・R1の17戦selection hash/ticketは回帰で維持。既存Regression toolへmode/output引数を追加し、旧保存先への新Arm書込みは拒否。旧report、Signed FINAL/RESULT、旧Forward plan、17戦OOSは不変。既存settlement、Exposure診断、WIDE整数配分、robustnessを再利用。

|Arm|投資|払戻|PFS|全損|購入Winner/Pair/Exact|最大DD|最多払戻比率|
|---|---:|---:|---:|---:|---|---:|---:|
|Production|361,000|193,310|53.55%|2|16/14/11|172,860|27.31%|
|Original AKI|17,800|10,700|60.11%|11|10/5/4|9,200|32.90%|
|PR262 Replay|85,800|98,260|114.52%|6|13/8/0|33,360|39.81%|
|PR265 R1 Replay|68,700|65,100|94.76%|12|10/5/3|37,710|56.59%|
|PR265 D Replay|361,000|229,940|63.70%|12|10/5/3|209,770|34.99%|
|R2 Selection Replay|89,800|69,550|77.45%|10|13/6/4|48,960|52.97%|
|R2 Capital-only Replay|361,000|242,360|67.14%|10|13/6/4|197,350|33.20%|

購入captureと列captureは別。全17RのW pool/score/axis/leader/risk/span/limit、条件付きP2/P3、追加/削除券、False Addition（非的中券）、Head/Pair/Third/tier/券種Exposureはcomparison.json.gz/full_report.json.gzに保存。OHI成功・失敗を全件含め、Venue/距離別集計も保存。

R1→R2は+211点/+21,100円、払戻+4,450円。経済的改善はない。R6はB6点600→2300に対しR2 9点900→0。R7はB8点800→3520に対しR2 33点3300→3520。R9は0維持。R12は44点4400→20970でR1と同じ。12Rだけの成功を一般化しない。等予算は既存WIDEによる整数100円Stake-onlyの結果後ablation。等点数比較は合法な結果前matched policy未登録のためPENDING。単純比例拡大はしていない。全17Rは投資あり、No-Bet counterfactualは未定義。市場price欠測なのでEV/Kelly・経済的最適性は主張しない。

## F — External receipts / test / CI

新修復Codeの外部Receipt0、新KRS0。旧PR265の停止前実行LOCAL-AKI-REPLAY-f613ba0c2da58926 / input4f2f15eb… / FINAL03f4b1df… / RESULT844affa… / KRS20,000を履歴として保持。旧署名・artifact/input/lineageは既存offline回帰で検証する。新R2の外部実証ではない。ローカル回帰226 PASS。CIの実結果はevidenceのverification/CI記録を参照。Canaryの404失敗は許容判定へ変更しない。

## G — Forward eligibility: REJECTED; genuine future PENDING

新Arm事前登録0・Forward実績0。R2はR6成功経路未維持、R7余分資金、R9喪失、17戦PFS/DD悪化のため次期Forwardへ採用しない。旧R1 planを書換えない。元AKI比較対象は維持。旧17戦を新Armへ移さない。

残存P2/W判断を結果前Evidenceで支持する仮説が成立してから、独立Policy/Code/同SOURCE/Static/Input/Stakeの結果前Freezeを行う。Runtime復旧後health/verify/Canaryと真正な署名往復を先に受入れ、A/B/C同SOURCEで発走前FINAL→RESULT→settlementを要求。Winner/Pair/Exact loss、False Addition、equal-budget/ticket、No-Bet費用、PFS/DD/大払戻依存を測定。現行Owner Gateの真正Forward30戦以上・複数条件・絶対収益性・相対比較・Human Reviewを満たしても自動Promotionなし。今回のReplayは未知未来成功標本ではない。

## H — PR: Draft / Production frozen

PR265を更新し、262/263/264依存を維持。ProductionのMerge/Activation/購入/課金なし。未完了は外部復旧、残存選択品質、市場価格、合法matched比較、真正Forward。Correctness修復を性能改善と偽装せず、この候補を棄却した比較結果を提出する。

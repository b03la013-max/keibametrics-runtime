# LOCAL AKI：22戦診断・公式価格接続・残存受入れ（2026-10-15）

結論：市場接続と測定はCandidateとして実装・実行済み。新Selection Candidateは0、真正Forwardも0。R1/R2はREJECTEDを維持する。Production完成・絶対収益性・昇格を主張しない。

## A — VERIFIED：正本と22戦の失敗構造

開始時main `7033f510964f671ee0f311dbea90d7387b8cc8ca`。Family R51、LOCAL Production R3、MEC-R3、川崎v2.4、29指数/63規則のPrediction Consumption境界は維持。PR262/263/264/265/276はDraft/未マージ。PR276の修復がmainまたはProductionへ反映済みとは扱わない。

RuntimeはDeployment `acf63364-0235-42ea-b68d-fbe931fcf51f` SUCCESS、Git `f0d23766b1d2e4cefc6194458b0e9141d5479cbc`。mainとは異なるが、現行Gatewayが指定する凍結Runtimeと一致し、bundle fingerprintも一致する。Engine1.1.0、parameter0.1-provisional、Signer/Trust Anchorを変更していない。OCI全イメージの再現同一性を証明したものではない。

22戦はPR276で回復した旧方式コホート。元17戦に10/14の5戦を追加した歴史比較で、新CandidateのForwardではない。R10/R11/R12のOFFICIAL_RESULTは後日の公式再照合であり、当時の原文checkpointを捏造したものではない。全22件、整合エラー0、Actual Purchase PFSはnull。

| Arm | 投資円 | 払戻円 | PFS | 購入Winner/Pair/Exact | 全損 | 最大DD円 |
|---|---:|---:|---:|---|---:|---:|
| Production凍結推薦 |456,300|274,490|60.16%|18/16/13|4|197,150|
| Original AKI凍結Shadow |24,700|11,920|48.26%|12/6/4|15|12,780|
| PR262 Reference Replay |115,800|128,460|110.93%|16/10/0|8|39,750|
| PR265 R1 Replay / REJECTED |80,300|70,230|87.46%|12/6/4|16|37,710|
| PR265 R2 Replay / REJECTED |110,100|74,680|67.83%|15/7/5|14|48,960|

上流Role捕捉はW18/22、P2 19/22、P3 22/22。Originalの列選択は12/12/15、Head-local Pair6/22、Pair-conditioned Third4/22。第一失敗は上流W欠落4、AKI W選択喪失6、上流P2欠落1、Head-local P2喪失5、Third喪失2、正解Exact保持4。

Productionは的中18戦中15戦で的中赤字。Originalは7的中/15全損、最大払戻依存29.53%。Referenceは最大払戻除外で94.14%、Exact購入捕捉0。R1/R2の最大払戻依存52.46%/49.33%。Referenceの集計黒字だけをForwardへの採用根拠にしない。Referenceは未較正数値から独自Role候補を選ぶため、凍結Static Role内に限定するR1/R2とはadmissionが異なる。監査には上流Role外の選択IDも保存し、単純な幅変更の因果比較とはしない。

全Race・Venue/距離/Class別、Core/Protection/Peripheral・Head/Pair/Third/券種Exposure、非的中追加券の実現数、First Failure/Dominant Loss Ownerは `research/aki_market_20261015/comparison22` に保存。非的中券は事前に無価値と証明された券ではない。False Exclusionは上流Worldの有無と購入への各段階で区別する。

## B — CANDIDATE / 部分VERIFIED：Market Evidence接続

新Selectorを作らず、既存 `local_race_key_shadow_owner.py` に次を追加した。

- `market_source_manifest`：既存NAR manifestと汎用 `/source/acquire` を再利用し、馬単/三連複/三連単の公式ページを明示opt-inで取得。凍結physical Runtime/Manifest/HTTPSガードは変更しない。
- `bind_market_evidence`：署名検証済みSOURCE、Receipt/Artifact/原文/Snapshot hash、日付・場・R、URL/HTML header、Runner Universeを照合。Fetched時刻は取得開始なので、SOURCE Freezeを保守的な利用可能時刻とする。価格とSelection/Ticket hash、結果前Freezeを結合する。
- 未発売、取得失敗、欠測、更新時刻不明、更新遅延、締切後、最終オッズを区別。Win価格から組合せ価格を推定しない。全券の実価格と時点が揃わなければMarket-Payout SufficiencyはUNKNOWN。
- 価格変化は署名検証済みの前観測、厳密な取得順序、同Race/Universeを要求。単なる観測差であり安定性・較正確率とはしない。
- `compile_candidate_portfolio` / compact署名用出力へ接続。既存Runnerの明示 `candidate_market_source_receipt` は外部Verify後に保存し、Candidateだけへ渡す。未検証・不一致はCandidate HOLD。Productionの券面・資金判断は変えない。

**実外部取得**：2026-10-15朝、川崎1R（公式発走14:45）は単複が未発売。3つの組合せページはHTTP302でhttpの単複ページへ転送し、正本SOURCEは `SOURCE_HTTPS_REQUIRED` で拒否した。実レスポンスとエラーを保存し、HTTPS拒否を緩和しない。市場が開く前の観測であり、Prediction/FINAL/Forwardを開始したものではない。12:00は明示的な観測用Cutoffで、正式Prediction Cutoffを制定したものではない。

**Historical transport実証**：10/14川崎4R公式ページを正本Runtimeが署名取得。EXACTA132、TRIO220、TRIFECTA1,254の正の実価格を抽出。零表示は有効価格にしない。4→10=12.2、1-4-10=10.6、4→10→1=39.1はいずれも最終オッズで、発走前評価に使えない。例示した3券は結果を知った診断対象で、事前選択の実績ではない。全てusable=false/UNKNOWN。parser fixtureの原文hashは、このSigned SOURCEの原文と一致する。

実SOURCE参照：

- 本日未発売：`886203534764ee9d9168f3107c63698069a19c189bc14f90ec1cff29fc2eee9b`
- 過去価格：`c0901e65f42059f5d9101d9b99776a8c9ef491e98e87466224c3f61793965225`

## C — PENDING / R1,R2 REJECTED：Selection Evidence Sufficiency

Originalは既存 `aki_adaptive_purchase_shadow.build` のRole順位slice→Head別P2/Pair別Third→券種優先・予算選択でWorldを落とす。既に列別幅はあるが、Role順位の切断ではMaterial Pair固有のStage/Path支持を比較していない。

PR262 Referenceは `local_aki_columns.build` の観測score/risk/gap選択と、生成Pair/ThirdをPROTECTへ置く経路があり、元PURCHASE Exactが購入へ継承されない。R1/R2は既存Materiality伝播を再利用するが、gap除外と上流Role欠落が残る。R2のW正規化修復は一部Wを回復しても、川崎6RのP2を回復しない。

10/13の成功・失敗を反映した新しい重み/閾値を制定しない。必要なのは、失われたMaterial Worldと追加しても当たらないWorldを結果前に識別する独立Evidence、正式な券種別価格、較正または合法的な経済評価、追加Capitalの説明である。現状では不足するため、新Selection/Capital方式を登録しない。Prediction Universe外のW/P2欠落はPrediction Ownerへ返す。

## D — VERIFIED：Capital / NO-BET Correctness

Selection、Allocation、Abstentionを分離。PR265@77f849f7の修復をそのまま使用し、Selectorは変更していない。新価格bindingは選択hashを変えず、結果後Capital測定を選択objectへ書き戻さない。

22×3方式×4明示PAPER予算=264シナリオ、うち132がterminal NO_BETで空券面/投資0。予算は0/2,000/5,000/10,000円の研究シナリオでユーザー資金ではない。Capitalの `no_bet:true` はPAPERでも実購入禁止を表す場合があるため、PAPERの券面抑制はterminal `decision=NO_BET` と区別する。

Core-Hit Recoverabilityは事前券種別価格不足でHOLD。既存100円単位整数比較を再利用した同予算・同点数controlsは、結果に依存しないhash順位による反実仮想であり、合理的最適配分や実績の創作ではない。EV/Kelly、資金上限の仮定、一律黒字保証なし。

## E — VERIFIED：Historical / Replay比較の不変性

元17戦のProduction361,000→193,310、Original17,800→10,700、Reference85,800→98,260、R1 68,700→65,100、R2 89,800→69,550は不変。22戦研究出力を別ディレクトリへ保存し、元OOS/FINAL/RESULT/旧研究値を上書きしない。

PR262→PR263（Venue）→PR264（共通測定）→PR265（Selector研究/Correctness）を継承。PR276（実行修復）を今回の提出先とし、同じSelectorを別PRへ二重実装しない。既存Regression tool/整数matched helper/元R1固定レポート/Trust Anchor attestationを、同一パス・固定Git blobで再利用する。

## F — VERIFIED（限定範囲）：External Acceptance

Health/Gateway Canary PASS、凍結Engine/parameter/bundle/Trust Anchor一致。旧22戦SOURCE/PRE_KRS/KRS/FINAL/RESULT計110署名をoffline+現在の外部 `/verify` で再検証、全PASS。今回の検証で新KRSは0。今回の新外部実行は上記市場SOURCE取得・署名Verifyであり、新Selection CandidateのFULL pipeline・発走前Signed FINAL・利用者配信の実証ではない。

## G — PENDING：Forward OOS

新Selection Policyなし、新Candidate登録0、新Forward0/30。結果を知った22戦を未知標本へ移さない。準備profileはFORWARD-NOT-ADMITTEDを維持。

次へ進むには、まず開いた市場で正式SOURCE/Staticと同一Race/Universeの時点付き券種価格を取得し、独立したSelection仮説を成立させる。その後Policy/Code/Input/World/Ticket/Stake/NO-BET/市場Bindingを事前Freezeし、同一SOURCEのProduction/Original/新Candidateを並列比較する。失敗Raceを母数から除かない。R43継承Gateの真正Forward30戦以上・3開催日以上、絶対収益性、Production比較、Drawdown非悪化、同予算/同点数、NO-BET機会費用、Human Reviewが未達。

## H — COMPLETED / CI別記：GitHubと回帰

PR276をDraftのまま更新。既存Workflowに今回のmarket回帰を追加し、新Workflowは作らない。実HTML・実凍結入力・Marketなしの旧挙動・NO-BET・hash純粋性・締切拒否を検証。詳細結果は `evidence/aki_market_20261015/regression.txt` とGitHub CIへ保存する。Git履歴や隣接PRの固定fixtureは実SHAで復元してから試験し、欠落による失敗をPASSとして扱わない。

再現：

```bash
python tools/aki_vnext_regression_20261014.py --candidate-mode HEAD_LOCAL_VNEXT_R2 --residual-audit --cohort22 --out research/aki_market_20261015/reproduction22 --verify-external
python tools/local_kaw_candidate_comparison.py --market-probe evidence/aki_market_20261015/request.json --market-out evidence/aki_market_20261015/new-observation
```

後者は価格観測のみ。日付/時刻/Universeは次回の正式SOURCEと照合したrequestへ更新し、過去requestの時刻を流用しない。既存probeのSOURCE/terminalは不変で、安全な再開は署名を再検証して同一保存SOURCEを読む。

## I — PENDING：Promotion Readiness

**NOT READY**。価格取得後の選択識別品質、経済合理性、真正Forward母数、外部発走前FINAL、利用者の発走前受領、持続PFSとHuman Reviewが未達。Production main/数値係数/Engine/parameter/MEC-R3/Capital Policy/Venue Canon/元OOSは変更なし。購入、Merge、Deployment、課金、鍵変更、自動Promotionなし。

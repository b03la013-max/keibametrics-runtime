# ケイバメトリクス各場別チャット 正式セットアップ R12

Revision: 2026-10-12 R12。R11の後継運用文書。対象競馬場を指定して使用する。GitHub `b03la013-max/keibametrics-runtime` の実装と署名成果物を正本とする。本書は独立した数値・購入・昇格権限を持たない。

## 1. 目的と完了条件

正式調査依頼を、適格なSOURCE・全馬Full20・Static・AKI・PRE_KRS・外部KRS・MEC・Capital・署名FINALまで実行する。結果判明後は公式結果・精算・振り返り・Learningへ接続する。表示を簡潔にしても計算、検証、保存工程を省略しない。

Workflow成功、指数完成、KRS実行、署名FINAL、予測性能、実購入、実回収率は別々に確認する。未知未来の精度と投資成績が最終目的であり、監査項目や文書の量を成果としない。

## 2. 起動と正本解決

「対象場・対象Rのケイバメトリクス調査」「正式予測」「完全フル規格」は正式実行依頼とする。開催日、発走時刻、公式出走馬Universe、コース条件、締切を解決する。発走後の依頼はPOST-START-REPLAYまたは結果調査へ分離する。未来の期限・締切規則は現行Contractを読む。

最初にmain SHA、発効済みCURRENT-AUTHORITY、対象Family/Venue Canon、Runtime/Signer/Receipt Contractを読む。2026-10-12の改修時点はR51。R50の正式AKI mapping・列選定を継承し、R51は全馬NEWCOMERのPAPER実行のみ追加する。LOCAL/BANの設定は継承先を確認し、JRA数値を流用しない。Snapshotを永久の現行値として扱わない。

対象Raceの状況、既存FINAL/NO_BET、実行中Runを確認する。適合する実行があれば再利用する。新規実行は既存正式Single Entryから一度起動する。依頼だけで実行済みと表示しない。

## 3. 長時間処理をチャットから切り離す

開始後、Race ID・execution_id・Run URL・現在工程を先に表示する。数値計算、署名検証、KRS、成果物保存は外部Runtimeが継続する。チャットの継続を計算成立の条件にしない。

待機中はRun/Jobの小さいmetadataで現在工程・失敗工程・更新時刻を確認する。進捗CLIは `python runtime/jra_pipeline_progress.py --run-id <ID>`。API各呼出しは15秒上限。利用可能なGitHubコネクタでも同じ情報を読む。大量のSOURCE、指数全件、全券面、ログ全文を繰り返し会話へ展開しない。長い一回の待機を避け、作業中は60秒以内に必要な状況を伝える。

切断後はexecution_id/RunからSOURCE・Request・Receipt・Checkpointを読む。Authority・入力hash・Race・時点・Contractが一致するときだけ再利用する。失敗時はFirst Failed Stage、Exact Gap、Owner、再実行可否を示す。同じ不適格入力の無意味な再実行はしない。失敗や署名不一致をPASSに置換しない。

血統Corpusは関連資料すべてを署名検証する。独立したharvest検証は最大4並列、統合順は固定。byte hash・署名Workflow別のキャッシュを使う。未来資料・未検証資料は採用しない。並列数を実測速度の倍率と読み替えない。

## 4. SOURCE・Universe・Full20

JRA公式SOURCE、Receipt、Ed25519/OIDC検証、Freeze時刻、Checkpoint bindingを確認する。Official Runner Universeを一頭も黙って省略しない。芝/ダート、距離、内外、馬場、天候、取消等を正本へ束縛する。

各馬13基礎＋7派生の20指数、Provenance、Evidence Ledgerを完成させる。公式に不存在の情報は承認済み第3条DCRで情報不足を保持して計算する。チャット独自の50点補完、合成証拠、未計算セルのCALCULATED化は禁止。中立50を能力肯定と扱わない。

血統の数値完成、個馬BVI寄与、SOURCE→Corpus→Feature→Static→券面Lineage、未知未来増分は別に確認する。更新後Corpusを過去のOOSへ混入しない。

## 5. Static・正式AKI・列選定

Owner Authorization、Policy/Runtime fingerprint、Activation、Static Freezeを確認する。許可と未知未来の性能実証を分ける。Trackerの現状は毎回正本を読む。

R50の正本は `profiles/jra_aki_v21_components_20261011_v1.json`、`profiles/jra_aki_v21_columns_20261011_v1.json`、`runtime/jra_aki_v21.py`、`runtime/jra_aki_v21_features.py`。W-AKI・P2-AKI・P3-AKI・軸飛びリスク/ASI・RSI・外部変動・堅決着補正は登録mappingで算出する。列は肯定証拠、列別gap、軸リスク等の登録規則で可変にする。R11の「AKI区分→固定1-2-5等」の記述は現行正式規則として使用しない。AKIから予算や点数を直接逆算せず、正式列とPair/ThirdからMECが券面を生成する。

全馬Base13がNEWCOMERの場合だけR51 dispatcherが専用規則を適用する。正本は `profiles/jra_newcomer_aki_paper_20261012_v1.json`、`runtime/jra_aki_dispatch.py` とOwner record。CFI/BVIは同じ血統経路として一度数え、公式人物統計または実測馬体の別観測経路を必要とする。中立・出典なしは観測に数えない。列幅は既存BASEと軸リスク連動REVIEWで算出する。既走馬のR50規則・AKI軸・指数数式は変えない。

新馬規則はOWNER_AUTHORIZED_UNVALIDATED / PAPERのみ。比較用Roleを購入肯定証拠へ読み替えない。無理な頭数補充なし。各列の採否理由と実計算を保存する。空列・一頭軸禁止等の残る適格な不成立は診断し、承認済みNO_BET terminal条件を満たす場合だけ署名見送りにする。NO_BETをKRS/FINAL完走へ読み替えない。

## 6. PRE_KRS・外部KRS

Current Authority、Race/Deadline、Signed SOURCE、Checkpoint、Universe、Full20/Provenance、Static Freeze、AKI/列、Head-local P2、Pair-conditioned Third、実測外部入力、Engine/parameter map、Signerを確認する。PRE_KRSでは署名入力から列を独立再計算し、hashと一致させる。

外部KRSはContractの正式Engine、実run_count、Receiptを検証する。標準5,000回を実行したことを回数の実記録で確認する。仮想回数、Candidate KRSをProductionの証拠にしない。Second Opinion/Shadowの提案を無断昇格しない。有意な追加提案がなくても実行記録を保存する。

## 7. MEC・Ticket・Capital・FINAL

Semantic Universe、Head/P2/Pair-conditioned ThirdとSemantic Originを保ち、正式MECで冗長重複を処理する。券種ごとの順序・順不同正規化、重複除去、点数、100円単位等の正式stakeを機械照合する。予算を使い切るため候補を追加しない。

BET/LIMITED/PAPER/NO_BETを正本で判定する。新馬R51はPAPERで購入権限なし。参考券面・参考額と実投資0円を区別する。資金不足を理由に予測の意味を消さない。推奨と実購入は別台帳。

PRE_KRS・KRS・MEC・Capital・FINAL各Receiptの署名、Race/Source/index/time bindingを確認する。発走前の適格FINALだけを正式事前FINALとする。POST-START-REPLAY/acceptance_onlyは `runtime/acceptance_artifacts` へ保存し、過去の事前FINALを作成・上書きしない。再実行の性能を未知未来OOSへ加算しない。

## 8. 結果・Learning

正式事前FINAL→公式結果→署名Result Evidence→精算→W/P2/P3/Order評価→KRS増分→Semantic/Ticket変換→Capital/PFS→First Material Failure→損失Owner→Fast Reflection→Learning n+1を保存する。各実Artifactの成立を確認する。PAPER・Replayの結果評価は実投資成績やProduction Forward OOSと別にする。

実購入証拠なしのActual PFSは未検証。単一結果から係数、KRS物理、MEC、Capitalを自動変更しない。Promotionは独立Forward OOSと正式判断を要する。

## 9. 表示

実行中：Race/実行ID、現在工程、数値計算数、Runリンク、次の確認対象を簡潔に表示する。

完了：正式順位、AKI各軸、W/P2/P3、券種別点数、参考額/Capital、実KRS回数、署名正本リンク、時点区分を表示する。全計算・Lineageは正本に保存してリンクする。状況一覧はindexであり、個別の署名FINAL/NO_BET/Acceptanceを最終照合する。

停止：First Failed Stage、具体的な理由、未成立工程、保存済みCheckpoint、修復/再開可否を示す。Candidate順位を正式買い目へ変換しない。UNVALIDATEDを隠さず、未較正確率・EV、実購入・性能改善を捏造しない。

本改定の実装・検証詳細は `docs/JRA_SMOOTH_EXECUTION_20261012.md`、GitHub PR #251を参照する。全工程の成立は対象Raceの実Artifactで判断する。

2026-10-12起動継続追補（PR #254）：全日常駐を最大30分のWorker交代へ変更し、17:30まで明示的に次Workerを起動する。予備cronも短時間方式。確認済みdispatchと結果handoffのstateは競合時にunion、表示indexは再生成する。起動失敗はRace単位で再試行し、他Raceを止めない。署名不足や証拠不足を成功表示へ置換しない。修復後の京都12Rは全320指数・KRS5,000回・34必須工程PASS、16:06:27 JSTに事前署名FINAL成立（Run 38215742882）。

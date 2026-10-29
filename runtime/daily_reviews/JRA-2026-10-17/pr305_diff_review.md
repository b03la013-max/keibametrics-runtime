# PR #305 差分Review・導入準備・Winner Discovery

Review対象はmain `d7ae23a07f7e872957085ef2bf72cf794a0c316f`、PR HEAD `7d3887df7f0a7133fa3d4c06fa5b22a15f27f44f` と本Reviewで加えた修復。`58ec502` は修復コードのコミット、`7d3887d` はその後に起動証拠・説明3ファイルだけを追加したコミットであり、異なるProductionコードを示していない。Review後の最終HEADとCIはPR本文に記録する。

本Reviewは既存テストの成否から独立して呼出順序・検証対象・保存経路・hash契約・時点・比較母数を読み直した差分Reviewである。同じ実装担当Assistantによる点検であり、第三者による独立著者ReviewやOwner承認とは区別する。取得時GitHubの提出済みReviewは0件。自己承認は作成しない。

## 差分Reviewの指摘と修復

| ID | 重要度 | 確認した問題 | 対応 / 状態 |
|---|---|---|---|
| R305-01 | P1 | KRS応答がcontract / signature検証後に保存されるため、不正応答や検証失敗時に本文を失う | 同じ既存ファイルへの保存を検証前へ移動。保存は実行認可としない。hash不一致・verify=false・HTTP503は停止を維持し、既存always-upload経路へ証拠を残す |
| R305-02 | P2 | 固定Shadow登録のAuthority定義キー1件に元checkoutの絶対パスがあり、他checkoutでそのまま参照できない | 登録・定義・SHAを変更せず、新しい読み取り専用Verifierで記録済みprefixのみを移送先へ対応付ける。全14定義と候補fingerprintを検証。隔離checkoutでもPASS、改変コードは拒否 |
| R305-03 | P0残存 | legacy Input SHAのhash対象範囲を現稼働Receiptから特定できない | 未解決。送信wire hash、input_data canonical hash、Receipt内hashを同義に扱わない。過去Receiptを再署名しない |
| R305-04 | P0残存 | Railway保存startCommandは診断後終了、配置済み起動ログはuvicorn。Git commit結合なし | 設定・Deploymentを再取得して差異を確認。実配置snapshotの起動コマンドとsource bytesを取得するまで再配置禁止。既存稼働サービスは変更しない |
| R305-05 | P0残存 | 公開可用性とユーザー受領、Learning保存とPrediction消費は異なる | ACK・次Input bindingがなく未実証。新通知経路やProduction数値への自動適用を追加しない |

ローカル検証は60 tests /25 subtests PASS。新しい4ケースはWorkflow内の実KRSブロックを抽出して、実京都11R応答のhash改変、署名検証拒否、HTTP503、正常応答を注入する。異常時に成功stageへ進まず観測応答が残り、正常時は既存stageに到達する。別の隔離checkoutで固定登録を検証し、定義改変時は拒否した。YAMLとWorkflow内PythonのcompileもPASS。

Production数式、AKI規則、KRS Physics、MEC、Capital、Current Authority、署名済みSOURCE / FINAL / RESULT / Requestの既存ファイルには差分なし。今回のRuntime側コード変更はWorkflowの保存順序のみ。Shadow R1本文・14定義bytes・元のLearning Stateを保持する。詳細は `evidence/jra_day_review_20261017/pr305_review_validation.json`。

## Runtime / hash契約

Railwayの現Deploymentは `7c7eeb5e-3b5b-496a-b66f-82bd71897d53`、snapshot IDは `1db3ca05-b62e-4038-8106-80c3c561e761`、status SUCCESS。metadataはimage `python:3.13-slim`でcommitHashなし。実配置Git SHAはUNVERIFIED。起動ログmarkerの第1SHA `1c453a5b0e8b5e4689b4a73d18128f54c7ed0e205db5b0c58b3dd229c264a989` は回収済みだが、hash対象の実装とGit対応を未取得。Engine/parameter SHA一致でApp SHAを代替しない。

保存設定は現在も診断後`SystemExit(9)`、staged=null。OAuthは変数値を非公開とするため、環境変数コードblobの原本を取得できない。現行14,570追跡ファイルと可用ローカル履歴候補16blobにmarker一致なし。全リモート履歴・他保存先の不存在を意味しない。稼働中の起動snapshotを確認できない状態で、診断コマンドを実行するための再Deployや推測した起動コマンドへの変更を行わない。

KRS Outputは元23件で、`output_canonical_json`のUTF-8 SHAと署名Receiptの`output_sha256`、構造化Outputの内容一致を確認。独立`/verify`は引き続き必須。Inputは、送信前に保存するexact compact UTF-8 bytesのSHAと、sorted input_data SHAを別保存する。明示された既知契約のみ内容を照合し、未知の宣言契約は拒否。宣言のない現legacy ReceiptはUNVERIFIED_LEGACY_HASH_SCOPEであり、Input真正性の照合完了と主張しない。未知契約を推測して過去hashを置換する修復は行っていない。

## Winner Discovery 16件

`winner_discovery_16_review.json` / `.md` は正投資19Race中のW候補外16件を全件収録。20指数320セルのValue、同値順位区間、Rule、出典フィールド、計算Component、選定Headとの差分、血統消費、展開Evidence、AKI原Registry、KRS原提案を追跡した。既存数式による値差の分解であり、凍結値を再採点・置換していない。

同一SOURCE・全馬凍結Full20からAKI Compilerを診断再実行し、元Receipt全体が16/16一致。勝馬はOTHER14件、ALTERNATIVE2件。全16件がBASE gap外、14件はREVIEW gap外、3件はsupport group不足、1件はrole quality floor未達（重複あり）。ALTERNATIVEの東京10R・京都12RもW trigger BASEのため不選定。これは規則どおりの除外を観測したもので、正当な規則の変更や実装バグの断定を認める証拠ではない。

Evidence不足、Numerical Discrimination、Static順位、AKI除外、KRS未活用、Venue Mechanismを各Raceで分けた。Evidenceの存在だけで十分性は証明できず、指数順位の低さだけで数式の因果欠陥とも断定しない。全16勝馬に測定血統Componentがあり、15件はMEASURED、1件はMEASURED_PLUS_DCR。新潟8R勝馬は血統距離の観測だけが残り、BVI coverage=0.24で既存DCR減衰が適用されている。全指数では6勝馬・10セルに情報不足フラグがあり、計算済みとEvidence十分を混同しない。欠測BVIだけで16件すべてを説明する根拠はない。BVI scalarの直接ZAI_WIN係数は0で、共有血統Featureが他のBaseへ寄与する経路と区別する。Venueは3場ともHOLD。

Winnerだけは京都12Rでも一意なので、本診断では同Raceの事前KRS W提案を評価する。16件中5件に未採用のactionable W提案が存在し、固定one-per-column候補が選ぶ勝馬は3件。従来のKRS Order適格母数が京都12Rを除外した集計は変更しない。原FINAL / Receiptと正式RESULTの同着保留も維持する。

## 同一19Raceの5 Lane観測比較

| Lane | W捕捉 /19 | W候補枠合計 | W不正解枠合計 | Ticket / PFS |
|---|---:|---:|---:|---|
| Frozen Static roles | 3 | 36 | 33 | 独立したStatic-only FINAL券面なし |
| Static + 全KRS actionable提案の観測union | 8 | 59 | 51 | 新しい事後診断のみ。Pair/Third/Ticketへ変換しない |
| Production AKI | 3 | 36 | 33 | 正式推薦336券、33,600円→9,100円、PFS27.0833% |
| 既存one-per-column Role Rescue | 6 | 48 | 42 | Role-only。必要券面・資金・PFSはNOT DEFINED |
| 同SOURCE市場Top3 BOX役割集合 | 10 | 57 | 47 | 既存研究Replay114券、11,400円→10,690円、PFS93.7719%。Production昇格不可 |

幅の増加を予測改善実証と扱わない。Staticの凍結rolesは既に正式AKI後であり、Production AKIと同じbaseline。独立したpre-AKI Production ablationを後から作らない。KRS全提案unionは今回新設した事後の観測比較で、Forward用未登録・未Activation。未知未来へ利用するには別Candidateとして事前登録とOwner審査が必要。既存one-per-column定義と登録SHAは不変。全95行の同SOURCE・Cutoff・W/P2/P3・幅・Orderの評価可否と、計算可能な2 LaneのRobust PFSは `five_lane_role_observation_review.json`。Role追加から推測Ticketを作りPFSを算出しない。京都12RのP2/P3/Orderは正式同着保留を尊重する。

CORE限定案、AKI Trigger Selective案、市場BOXをProductionへ導入しない。Winnerを発見できないRaceの点数削減はPrediction改善ではない。

## Delivery / Learning

正式観測経路はGitHub Canonical・Actions step summaryと可用性readback。SOURCE34、FINAL23、発走前可用性23、確認済み受領ACK0。`runtime/jra_delivery.py`はnotification_sent_at / user_received_atをnull、user_delivery_verifiedをfalseとして保存する。観測対象JRA経路にChatGPT自動Pushや受領ACK処理はない。PR #302は未Mergeで、完成回答の永続化・readbackを改善するが、自動Pushの実証ではない。承認済み送信先・通知adapterが確認できないため、実証のための新規外部送信は行わない。

Learning記録22、次Prediction実消費0確認。元34Requestと現Formal Runnerに消費bindingが確認できず、記録だけをclosed loopとしない。署名RESULTが次同Venue cutoffを越えた7件、cutoff前9件だが消費未確認、残り20件UNKNOWNという既存分類を維持。Shadow Intakeは準備済みだが、accepted contextに数値適用権限はなくProductionへ接続しない。

## Merge / Rollback / 次未知Race

Merge ReadinessはBLOCKED。最新HEADへのOwner承認・第三者の独立著者Reviewは未取得。CI全PASSもこれらの代替にならない。Runtime Deployment source / startCommand / Git SHA照合、実Delivery、Learning閉路も未成立。

Workflow変更のRollbackは検証前へ移動した応答保存ブロックを以前の位置へ戻すコードrevert。過去署名・証拠は削除しない。ただし証拠喪失が復活するため回避策として先にrevertしない。PR全体のRollbackはruntime contract / runner / zero保持のコード差分をOwner手順でrevertし、監査資料は保持する。RuntimeのRollbackコマンドは未検証。未取得の正常起動設定を推測し、現Deploymentを再起動する計画を安全なRollbackとして提示しない。

10月18日計画は3Venue×12Raceを登録済みだが、登録は実行完了を意味しない。次の適格未知Raceは、最新公式post/cutoff、Authority、Scope、SOURCE、Runner Universeを当日に再確認して選ぶ。今回の作業はDispatch・Shadow Activationを追加しない。

Live Acceptanceは(1)承認対象HEADとWorkflow SHA、(2)正式Intent一回受付、(3)公式Resolve、(4)OIDC/Signed SOURCE、(5)Full20、Static、AKI、(6)署名PRE_KRSとKRS原応答・exact wire checkpoint・hash検証、(7)PRE_KRS→MEC/Capital→Signed FINALが期限内、(8)承認済み経路の送信/公開/受領を別記録、(9)公式RESULT/Settlement、(10)許可されたLearningを次RaceのSOURCE freezeより前に固定し、そのdigestを次Prediction Inputと結合、の実証を要求する。いずれか未確認なら部分結果とし、単なるWorkflow SUCCESSでPASSにしない。期限切れRaceの再FINALは禁止。必要な導入承認と通知/学習経路がそろうまでLive AcceptanceはPENDING。

判定: CORRECTNESS PARTIAL / WINNER DISCOVERY TRACE COMPLETE（改善効用は未実証）/ SHADOW READINESS PARTIAL・NOT ACTIVATED / DELIVERY・LEARNING CLOSED LOOP PARTIAL / LIVE ACCEPTANCE PENDING。


## 後続Correctness解決：legacy hashの補完規則

追加調査で、23件すべてのInput SHAが`input_data.race.prediction_id = outer race_id`補完後のsorted/compact UTF-8 JSONと完全一致。23件の原Ed25519署名・Receipt SHAも検証した。R305-03は歴史的入力内容の照合について解決。exact wireは過去に未保存のため別扱いとする。Runtime原コード・Git SHAは依然未回復であり、R305-04を解決したとは主張しない。

既存の固定contractファイルを改変せず、別sidecarをFormal Runnerへ接続した。未知Runtime/schema・別Race・conflicting prediction_id・内容改変は拒否し、署名verifyは別途必須。元リクエストを変更しない。新しい入力結合JSONも既存のalways-upload対象へ保存する。既存の外部20,000回CIのfixtureでは、外側だけをacceptance用Race IDに変え内側をselftestのままにしていたため、fixtureのidentityを一致させ、実API経路でも新gateを試験する。Productionの入力や予測値は書き換えない。

既存Shadow登録本文と14定義SHAは不変。新gateはCorrectness検証であり、Shadow列選定・数値Policy変更ではない。Owner承認・第三者Review・MergeとLive Acceptanceは引き続き必要。

後続入力結合の検証を含め、ローカル70 tests /25 subtests PASS。原23署名入力の照合、内容改変・未知版・別Race拒否、Workflowでの入力不一致停止と証拠保存、canonical field-order不変を確認した。


## Final independent closure (2026-10-17)

A distinct technical reviewer audited the107 actual PR paths and562 archived evidence members at dc6333f, then independently reproduced and re-reviewed two repairs. Original23 cryptographic Input/Output bindings PASS. CHECKPOINT_TOCTOU is resolved by the durable caller wrapper, leaving frozen serializer bytes unchanged. DECLARED_SCHEMA_BYPASS is resolved by revision/schema checks before both branches. New helper/tests are covered by PR and main-push CI paths. Local exact utility CI command:78 tests /25 subtests PASS;24 independent process schedules plus abrupt process death recovery PASS.

Reports: independent_review.md (initial findings; OPEN states are historical), independent_repair_review.md (superseding closure), evidence/independent_review.json and independent_repair_review.json. Independent agent review is not GitHub human/Owner approval. Original probe scripts are preserved under evidence/jra_day_review_20261017/independent_review_probes.

The109 two-dot comparison contains two main-only live state files absent from the actual107-path PR diff. Independent three-way merge preserved their latest main blobs; no state rollback repair was made. New files add to107 and will be listed in final commit inventory. Production numerical policies, signed originals and14 preregistered definition fingerprints are unchanged.

Remaining readiness,23 Delivery evidence records,36 existing Learning timing records, Rollback constraints and19-stage unknown-future acceptance checklist are consolidated in execution_assurance_closure.json#/final_independent_closure. Railway diagnosis/build/boot/health and static launcher analysis are in runtime_startup_provenance.json. Saved command unconditionally exits9; current uvicorn readiness does not prove next startup. App Git SHA/image digest/PID1 source linkage remain UNVERIFIED. **NOT MERGE-READY.**

Delivery receive ACK0 verified; next Prediction Learning consumption0 verified. No new notification, Production binding, Merge, Deploy or Activation was performed. Frozen recommendation19 positive FINALs33,600yen→9,100yen remains distinct from actual purchase and from36-race execution coverage.

Required13 outputs are consolidated, not duplicated: independent reports/full diff inventory; original23 KRS verification; Railway/startup provenance evidence; Delivery/Learning rows; exact repair diff and CI; Rollback, Merge Readiness, Live Acceptance and blocker ledger in the same closure object.


## Railway startup follow-up: seven causes checked (2026-10-17 20:24–20:26 JST)

Runtime source and Production configuration changes:0. Merge/Deploy/Restart/Activation:0. Current HEAD at readback5383c5cf56e919b997afac3ff62a78338950d4cb, main d7ae23a07f7e872957085ef2bf72cf794a0c316f, CI9/9 success, draft/open,117paths. Independent technical review of those source bytes remains valid; no GitHub human/Owner approval.

Fresh get_service_config + describe_service agree on saved diagnostic command, source python:3.13-slim, restartPolicy NEVER, staged=null, active7c7eeb5e. Inventory contains only production environment; existing jra-validation-sandbox and km-jra-validation-oneshot are Bun proxy/request services, not recovered exact KRS runtime replicas or permission to redeploy. list_variables is explicitly valuesRedacted=true:122names,0values. No Railway CLI/auth/container runtime on local host. No secret values were obtained or used.

Read50deployment records. Previous35de5393 has a successful historical healthcheck, but no recovered code/config/signature compatibility; canRollback=true is only a platform action flag. A failed Sept17deployment also exposes canRollback=true, so flags cannot certify a safe target. Diagnosis queries for removed35de5393 and failedf7637487 repeat the current saved command; this does not prove the historical commands, mutation time or actor. Active boot log remains uvicornPID1 + app-blob1c453a5b... /engine/parameter marker; exact argv/module/source hash scope unknown.

Clean local reproduction of exact saved command SHA7e0a88dae4037bb1b8c9bbcde56d8116ac5fbfe493690bdf0a6ba753e84f0778: no blob=>9, valid synthetic blobs=>9, malformed base64=>1. A distinct reviewer reran all3. Host Python3.12.14, not a deployed Python3.13 container. No Production blob, keys, calls, signing or listener used. This proves a local failure mode, not current deployed PID1 or next Railway restart. Reproduce using the preserved script in evidence/independent_review_probes/km_saved_startup_repro.py and a temporary JSON string copied from runtime_startup_provenance.json#/context/startCommand. Script refuses any other command SHA.

Inspected current public docker.io/library/python:3.13-slim manifest/config only, no layers pulled or executed. Reference index70729b46..., selected linux/amd64 image8fb4cfa1..., configce3ff952... recomputed exactly; Entrypoint=null,Cmd=[python3]. These identify the current public reference, NOT the deployed image or its platform. Never promote this reference digest to active deployment evidence. Read-only fetch probe preserved beside local reproduction.

All7hypotheses and exact evidence/limits are recorded in runtime_startup_provenance.json#/startup_followup. Residual diagnostic command is observed; its causal history, correct deployed launcher, immutable deployed digest/GitSHA and restart/rollback safety remain UNKNOWN/UNVERIFIED. No speculative startCommand patch was staged: removing SystemExit(9) alone would still not launch a server, and inventing uvicorn app:app would lack source authority.

Official Railway references: https://docs.railway.com/deployments/start-command (explicit start command overrides image ENTRYPOINT); https://docs.railway.com/config-as-code (deployment details displays settings the deployment went out with). These are general platform semantics, not actual snapshot proof.

Next required evidence: provider-supported read-only deployment details/export for active snapshot1db3ca05..., actualPID1argv, immutableimageDigest/platform, sourcebundle/hashscope/buildmanifest and rollback target snapshot. Do not export private signing keys. Available connector read tools omit these fields; browser fallback has not been used without approval. Once recovered, reproduce the exact launcher in an existing approved isolated environment/local equivalent, then Health/KRS hashes/Receipt/version/engine/parameters/stop-start/rollback/signature checks. Until then **NOT MERGE-READY**, no Deploy/Restart/rollback authorization sought.

Delivery remains23available/0verifiedsend/0ACK; Learning22stored/0verifiedintake/inputbinding/consumption. These do not become complete through Railway availability. No notification adapter/destination or new Production learning policy was connected.


## Startup最終追加照合：snapshot / 実プロセス回収（2026-10-17）

上記の「App原本・起動command・hash対象UNKNOWN」は後続証拠で更新した。最新mainは `98b6be3261b72acf460a07da7d981ae83f871151`（旧d7ae23a以降は日次state/statusのみ）。親HEAD `dc86a93f877bda4ece521e8bec768b0080b8a349` のCI9/9 SUCCESS。Mergeは未実施。

**Root Causeは保存サービス設定と配置snapshotの世代差、および管理APIの参照scope差である。** Deployment Detailsの配置7c7eeb5e… / snapshot1db3ca05…は108変数・healthcheck300秒・コードblob復元/SHA検証→pip→exec uvicorn。現在サービスは122変数・30秒・診断後SystemExit(9)。異なる配置のMCP diagnosisも現行サービスcommandを返しており、実配置commandの代替にはならなかった。誰がいつ診断設定へ変更したか、過去設定継承・provider反映漏れはUNKNOWNを維持する。

読み取り専用Consoleで同じDeployment/instanceのPID1（python /usr/local/bin/uvicorn app:app --app-dir /opt/km …8080）を確認した。Appの実ファイルSHAは `1c453a5b0e8b5e4689b4a73d18128f54c7ed0e205db5b0c58b3dd229c264a989`。回収したsnapshot App bytes・実ファイル・起動ログ第1blobが一致し、hash対象はdecoded App bytesと確定した。Engine `9929df99…`、parameter `75cc9d0e…` も実ファイルと回収原本が一致する。Git SHAはUNVERIFIED、Imageはpython:3.13-slim / UI sha:70729 prefixのみでfull actual digestはUNVERIFIED。現在の公開registry digestを実配置証明へ読み替えない。

正しい配置時startCommand全文と未適用修復候補は `evidence/jra_day_review_20261017/startup_owner_configuration_candidate.json`。実配置は7App/6Engine/1parameter gzip blobを復元し3 SHAを確認後、uvicornをexecする。候補はこの処理を保ち、実配置と同じ28依存版を固定しpip retry2/timeout15秒、healthcheck300秒へ戻す。候補command SHA `610839e28c178df8b0527d3a5850fe67b597f94bf5ef757823df9fb3ec326fec`。Owner未承認につきService設定・環境・Signer・Deploymentへ未適用。現行service blob値は独立decode未確認であり、適用前の3 SHA preflightが必要。ネットワーク/package可用性も別条件である。

独立した技術Reviewerが原Appの正規化処理をASTから抽出し、23原ReceiptのInput SHAを23/23再現。元23件の署名・Output検証は前節のPASSを維持し、再署名しない。実装担当と別のReviewerでありGitHub human承認ではない。

回収したApp/Engine/parameter原本、Python3.13.16、実配置と一致する依存版で**隔離試験PASS**：Cold Start READY→実Engine SMOKE100→同一TEST鍵でStop/Restart・旧Receipt検証→SMOKE100→Engine改変でDEGRADED/actual_run_count0→原本復元READY→SMOKE100。合計300run、Input/Output canonical SHA・Ed25519・改ざん拒否すべてPASS。元launcherのdecode処理を実行した。元の未固定pip installと公開bind、Railway provider操作は実行せず、ローカルPythonのcompiler/buildも本番と異なる。候補28pinのdry-runは変更不要。これは未知未来OOS・本番Restart・provider Rollback・Live Acceptanceではない。

回収原本は `independent_review_probes/recovered_runtime_reference/` にbyte不変で保存した監査referenceで、Productionへの接続なし。再現probe `independent_review_probes/km_recovered_runtime_rehearsal.py` は冒頭のscratch入力を使う実行時snapshotである。再現時は上記3原本を `/tmp/km-recovered-{app.py,engine.py,param.json}` へcopyし、candidateのrecovered commandを末尾newline付き `/tmp/km-recovered-start-command.txt` に保存する。同じPython/depsを `/tmp/km-runtime-startup-venv` に用意し、probe内REPOをcheckoutへ合わせる。LOCAL `/opt/km` が存在すれば上書きを拒否する。元の入力fixtureは既存archiveを展開した正本を参照し、新しいLOCAL identity・TEST鍵を使用する。Production鍵を持ち込まない。

**判定：NOT MERGE-READY。** 現在のサービスcommandは依然として診断用で、次回Deployment安全性は未成立。Ownerが設定候補を承認し、現行blob整合・隔離したprovider起動・rollback先snapshotを検証するまで格上げしない。稼働中配置7c7eeb5e…を将来候補導入のrollback基準として保全する。前配置35de5393…のREMOVED/canRollbackだけでは安全なrollback先としない。

DeliveryはSigned FINAL/公開可用性23・ACK0確認。Learning保存22・次Prediction消費0確認を維持する。新通知先・Production Learning接続なし。原RESULT3件回復待ち、京都12R同着manual holdも維持する。Production数式、AKI、KRS Physics、MEC、Capital、Venue Canon、Shadow14定義/fingerprint、署名原本は不変更。残存provider試験/設定適用、exact HEAD Merge、必要Deploy/Activationは個別Owner承認事項である。

最終追加差分10ファイルの独立技術Review PASS。全PR124path台帳の自己参照以外123 SHA一致、Shadow14定義不変、原23Receipt/562archive member再検証PASS。新しい空の隔離環境へ候補と同じpip flagsで28依存版を導入し、全29版（pip含む）・pip check・原App importもPASS。最終Railway readbackでも配置7c7eeb5e…/snapshot1db3ca05…/SUCCESSは不変、現行commandはSystemExit9・30秒・stagedなし。Owner未承認の適用は行わず、NOT MERGE-READYを維持する。

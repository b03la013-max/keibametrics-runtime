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

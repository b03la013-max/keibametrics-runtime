# Prospective Shadow cohort connection — prepared, inactive

既存の `dayplan.forward_oos_preregistration` を実際のcheckpoint、Shadow、provider witness、結果、cohort別trackerへ接続するShadow限定のCorrectness修復。正式SOURCE、Full20、FINAL、券面、日程、Autopilot、数値Policy、Modelを変更しない。新しいWorkflow・Dispatcher・Registryは追加しない。

## 固定した範囲

- 新cohort案は `JRA-CONDITIONAL-RANK-20261025-R2`。元のR1 model、Role sidecar、equal-exposure portfolioのIDとModel SHAを維持する。新しいモデルを学習していない。
- 候補は既存の単純除外主要候補と凍結済みR1 ConditionalRank/equal-exposureを継承する。条件付きP2は `HOLD_NOT_INCLUDED`。10/24結果や660比較を見て選んだ新best arm、#332の追加研究候補を新cohortへ昇格・混入しない。
- 適格性の対象は `CONDITIONAL_RANK_EQUAL_EXPOSURE_ONLY`。Role/Learning各armはこの登録により適格化しない。State本文のSOURCE前存在証明、Learning数値実消費、Production昇格は別判定。
- 各cohortの最低60Race・3日・2Venue、条件付きP2のHOLD、自動昇格禁止を維持。cohort間で分母を合算しない。
- 同じcohort IDを異なるCode/Model/Policyで再利用しても合算しない。proof・結果・trackerに安定したpin fingerprintを結び付け、同IDに異なるbundleがあればtrackerは `COHORT_PIN_CONFLICT`・strict計上0とする。登録日・対象Race追加だけの差はpin fingerprintを変えない。
- Production数値Learning実消費は0。既存24Target・139bindings・10Stateの保存実績と、結果後ON/OFF再現で券面が変わった23Targetを区別する。139bindings中130は既存provider存在証明、9は既存summary commitmentであり、9件をState本文のSOURCE前存在証明へ拡大しない。追加522券・52,200円は仮想追加露出であり、同予算改善の証明ではない。

## 既存経路への接続

`jra_shadow_checkpoint.pack` が既存dayplanの登録本文と独立保存receiptポインタを取り込み、retryはその原本を再利用する。実際のShadowは新 `oos_candidate_id` と元のmodel/sidecar/portfolio ID、登録SHA、Prediction Input SHAを保持する。結果保存とtrackerはprovider証明、登録SHA、cohort ID、scopeを照合する。

Formal RequestのproducerはSOURCE Freeze後に開始できるため、producerの開始日時を事前登録時刻の代わりに使わない。既存 `km-jra-learning-binding-audit.yml` の `jra-learning-mechanical-<run_id>` artifactへ登録dayplan、Sidecar/Rank/Checkpoint code、Model、既存Owner承認のprovider読取snapshotを追加保存する。検証ではGitHub providerのrun/attempt、artifact ID・SHA・server作成/更新時刻と独立ZIP内容を確認し、登録本文と実行Code/Model/Policyの一致を要求する。

独立registration artifactの更新時刻は原SOURCE Freezeより前であることを要求する。producerのrunがSOURCE後でも先行する正規CI証拠があれば受理し、その証拠がなければOOS不適格とする。git author/committer日時は代用しない。

## 登録用の具体物と未実行の境界

`prospective_registration_request.json` は既存dayplanに渡すレビュー用fragment。`active=false`、Owner参照・registered_at・独立receiptは未設定。ライブplanへ書き込んでおらず、正式登録成功数・新Freeze数・新真正OOS数はいずれも0。

1. 最終統合treeでSidecar/Rank/Checkpoint/Model/PolicyのSHAを再照合する。#331の既存write_status抽出を含む実bytesが基準。コードが変われば本fragmentのCode SHAも再固定する。
2. 最新HEADと変更範囲のOwner承認、および既存Authority上の将来登録操作の許可が成立してから、正規経路で将来cohort本文を有効化する。登録には `status=OWNER_APPROVED_PREREGISTRATION`、実Owner参照、実登録時刻が必要。今回の実装完了をMerge・Deploy・有効化の承認と扱わない。
3. 既存CIがその正確な登録本文とcode/modelを独立保存し、SOURCE前に完了したことを確認する。新Workflowを作らない。CI不成立や期限超過の場合はShadow資格だけを止める。
4. 登録本文のSHAを変えず、別field `forward_oos_preregistration_witness={run_id,run_attempt,artifact_id}` へ成立済みprovider receiptを指定する。初回保存時に未知のartifact IDを本文へ入れる循環を避けるため、ポインタは登録本文から分離している。
5. 既存Autopilotの通常窓で実行された新Raceのcheckpoint、実output、provider archive、結果を確認して初めて計上する。発走後Replay、旧10/24原本、inactive登録、Owner参照なし、独立保存なしには新しいOOS creditを与えない。

Owner参照の文字列や自己申告のverifiedフラグを承認と扱わない。固定repoの実Owner `b03la013-max` が既存PRに出した明示的なcomment/reviewをGitHub読取APIで取得し、承認HEADのCode/Model、cohort ID、Policy、対象Raceを含むscope SHAと照合する。Owner自身のPRではself-reviewできないためcommentも対象。pending/dismissed/reject、削除・取得不能、非Owner、対象不一致、後日編集、登録後の承認ではstrict0。保存済みprovider snapshotと現行内容の一致も要求するので、reviewのsubmitted_atだけを本文時刻の証拠に使わない。

受理する明示的承認本文はJSON（任意のjson code fence可）で、`decision=APPROVE_PROSPECTIVE_SHADOW_PREREGISTRATION`、`candidate_id`、`scope_sha256`、`approved_head_sha`を含む。scope SHAはCode/Model/Policy/元ID/Authority/対象Race/input scope等の正確な内容から計算する。APIによる承認証拠の収集は読取のみであり、commentを投稿しない。`archive_and_pins_verified` と `owner_approval_verified` を分け、両方が成立した場合だけ登録資格を認める。暗号学的な人間の署名とは主張しない。

原Race Intake登録writerは不変計画の別経路であり、異なる既存計画を上書きするために使用しない。

## 原本保全と回帰証拠

`legacy_compatibility_regression.json` は既存GitHub provider ZIP33件を新readerでオフライン検証し、保存証明33/33、旧結果13件の原本byte再利用13/13、derived真正OOS0を確認したもの。旧13件が記録したeligibleという履歴は書き換えず、trackerで `legacy_recorded_eligible_races=13` とstrict0を区別する。

`preregistration_cause_and_contract.json` は修復前mainの原因調査原本。fd0cb…から4eb5…への差分はPR318のattempt別artifact名とprovider元attempt読取に限定され、Model/Rank数値は同じだった。修復前の「metadata未接続」という観測は、今回の修復後の稼働成功を意味しない。

この変更はlocal試験まで。remote/main書込、Merge、Deploy/Restart、Workflow dispatch、外部通知・POST、実馬券購入、旧plan・旧Freeze・旧結果の書換を行っていない。

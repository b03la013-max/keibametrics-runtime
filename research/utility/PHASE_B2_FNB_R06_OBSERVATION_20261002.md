# Phase B.2 船橋6R 凍結Artifact観測・RESULT精算 A–O

判定: **Production RESULT / Frozen Recommendation settlement COMPLETE。Phase B.2 初回完全受入 HOLD。**
`LIVE FORWARD MEASUREMENT OPERATIONAL`とは判定しない。R6の発走前captureに失敗し、固定Capital四Arm・LOCAL KRS計測を含むPersistent Forward Measurementが閉じていない。結果後に欠落Artifactを再生成していない。

## A — Race / Execution
2026-10-01 船橋6R、17:05 JST。race_id `KM-LOCAL-FNB-20261001-R06-LIVE-R1`。execution_id `LOCAL-KM-LOCAL-FNB-20261001-R06-LIVE-R1-EXEC`。12頭、真正LOCAL FORMAL-PRE-RACE。R7/R8/R12をこの対象へ置換しない。

## B — Freeze Authority
研究開始基準は2026-10-01 11:15:47 JST確認のcommit `76897d48ec6d0910ebd5b91bba69a149343f65b0`全tree。tree `d1afeaba33b5a893025e5591cc2849a4ec02f58c`。
PHASE-B2-FORWARD-v1のdefinition_sha256 9/9が基準commitのbyte内容と一致。最新mainは運用Artifactの読取りと既存RESULT workflow起動に用いた。研究定義を最新mainへ置換していない。Code/Rule/Weight/Arm変更、Candidate fitting、Prediction/Candidate/KRS/Capital再生成なし。

## C — Signed Official SOURCE / Universe
SOURCE時刻2026-10-01 16:35:27.672501 JST。
receipt SHA256 `49bc85b90e13af9e94f8b47318e4eccde3ce5499f80412a6a79632c6009c9de7`。
snapshot SHA256 `2adfe2abd41899138ffa385dff3ebee45a872379fd1f5f4a83c751535d4b9436`。
全Runner Universe: 1 ゴームズ、2 マイリトルロマンス、3 シンキングファーザ、4 フェアリオンアイス、5 プレシャストップ、6 セイダンシング、7 ゲットジェロウス、8 レイワエポック、9 ダンガリー、10 ウインコンパス、11 マサノプレジオーソ、12 ソウ。
発走前SOURCE/FINAL immutable storeを既存workflowが解決・検証した。

## D — Evidence / Numerical Authority
Production Numerical Authority **NOT_READY**。63 component rulesがunbound。Formality PASSと数値Authority充足を混同しない。
training/trainer comment/paddock等の取得不能EvidenceはUNKNOWN。代理Scoreを新規作成していない。既存凍結計算のneutral/default値は実測Evidenceとみなさない。
Candidate各runnerのcomponent coverage/missingnessは発走前Artifactを保持（付録参照）。因果的欠落影響は未識別。

## E — Signed FINAL / Lineage
FINAL freeze: 2026-10-01 16:37:46.988350 JST。
receipt SHA256 `1410322b506e050ad0249a63f2f81be039d27aac914d9eca216726922fc92399`。
artifact SHA256 `88c58a0d846ee59449cab10715e3f02098a3b0518be2c1de0b505a568c11524f`。
ticket SHA256 `12f2fc799fb13bbe584a57758e0d5d8d33407a9cbfaa61a2ade13d10c7adf719`。
Production KRS receipt SHA256 `e26085e258fb19d9ff8b94a28b6cd0b70b8a94680ec807f9859106e1a2517a7b`。
59 tickets、推奨投資5,900円。Signed RESULT frozen_refsは同一FINAL receipt・freeze timestamp・ticketへbinding。全file hashesとstore timestampは末尾manifest付録。

## F — Production Static / Candidate v0.1
Production順位: 9,5,1,4,3,6,11,8,7,10,2,12。
Candidate v0.1順位: 9,5,6,1,3,8,11,7,10,4,2,12。

| 指標 | Production | Candidate v0.1 | Candidate差分 |
|---|---:|---:|---:|
| 実勝馬3の順位 | 5 | 5 | 0 |
| 実2着8の順位 | 8 | 6 | 2位改善 |
| 実3着9の順位 | 1 | 1 | 0 |
| 実Top3平均順位 | 4.6667 | 4.0000 | 0.6667改善 |
| W role捕捉 | false | true | +1 |
| P2 role捕捉 | false | true | +1 |
| P3 role捕捉 | true | true | 0 |
| 予測順位Top3と実Top3の重なり | 1/3 | 1/3 | 0 |

Winner role捕捉は「勝馬が順位1位」と同義ではない。Candidate ticket activationは未実装なのでCandidate PFSはUNKNOWN。v0.2/v0.3が既存workflowで評価されても本凍結比較のCandidateへ採用しない。

## G — Production KRS / LOCAL Measurement
Production KRSは発走前20,000 runs。Signed RESULT review: UNIQUE-RESCUE、P2_ROLE_RESCUE、P3_ROLE_CONFIRMED。Winner / ordered pair / ordered exactは非支持。
Candidate v0.1 KRSは発走前5,000 runs。評価: ordered pair Potential Rescue、P2/P3確認、Winner non-confirmation、exact非支持。Potential Harm role count 1、false pair additions 22、false exact additions 33、proposal width56。Production deletion/harm=false。実際の追加ticket/capitalは未materializeなのでUNKNOWN。Role proposalから金銭効果を推測しない。
Phase B.2専用LOCAL KRS persistent measurementはcapture欠落で未成立。KRS occurrenceはProbabilityではない。

## H — Common Exact 固定四Arm
以下は各追加Armだけの精算。既存署名FINAL binding valid / OOS eligible=true。R6 exact 3→8→9はcandidate setにない。

| Arm | 投資円 | 払戻円 | 損益円 | PFS % |
|---|---:|---:|---:|---:|
| CONTINUITY_ALL | 9400 | 0 | -9400 | 0.0000 |
| KRS_TOP1 | 0 | 0 | 0 | UNKNOWN |
| KRS_TOP3 | 100 | 0 | -100 | 0.0000 |
| KRS_TOP5 | 100 | 0 | -100 | 0.0000 |

Production+Arm PFS: CONTINUITY_ALL 60.9150%、KRS_TOP1 157.9661%、KRS_TOP3/TOP5 155.3333%。全Arm rescue_hit=false。Coverage追加はこの一戦では払戻増なし・追加損失。settlement SHA256 `ab8ce8c8d085468fb2c7f641c53a31a806bd9a9957501c2499eada9f6c0d200e`。

## I — MEC R3 / R4 / R5
MEC R3 Productionは59tickets・5,900円・9,320円。Top3 set covered、ordered pair/exact not covered。
MEC R4:
| Arm | 投資円 | 払戻円 | 損益円 | PFS % |
|---|---:|---:|---:|---:|
| CORE_ONLY | 800 | 0 | -800 | 0.0000 |
| CORE_PROTECTION | 2100 | 0 | -2100 | 0.0000 |
| CPSS_ALL | 2200 | 0 | -2200 | 0.0000 |
| CPSS_TOP3 | 2200 | 0 | -2200 | 0.0000 |
| CPSS_TOP4 | 2200 | 0 | -2200 | 0.0000 |
| CPSS_TOP5 | 2200 | 0 | -2200 | 0.0000 |
| CPSS_TOP6 | 2200 | 0 | -2200 | 0.0000 |
| CPSS_TOP7 | 2200 | 0 | -2200 | 0.0000 |
| CPSS_TOP8 | 2200 | 0 | -2200 | 0.0000 |

MEC R5:
| Arm | 投資円 | 払戻円 | 損益円 | PFS % |
|---|---:|---:|---:|---:|
| SET_ONLY | 4100 | 9320 | 5220 | 227.3171 |
| SET_PAIR | 5500 | 9320 | 3820 | 169.4545 |
| SET_PAIR_EXACT_TOP3 | 6100 | 9320 | 3220 | 152.7869 |
| SET_PAIR_EXACT_TOP4 | 7900 | 9320 | 1420 | 117.9747 |
| SET_PAIR_EXACT_TOP5 | 9400 | 9320 | -80 | 99.1489 |
| SET_PAIR_EXACT_TOP6 | 11100 | 9320 | -1780 | 83.9640 |
| SET_PAIR_EXACT_TOP7 | 12500 | 9320 | -3180 | 74.5600 |
| SET_PAIR_EXACT_TOP8 | 13900 | 9320 | -4580 | 67.0504 |

R4 settlement SHA256 `6aa23a50b0da3584b757b48ca218bb836a0c2bf986b35f6961006fd2a16ea624`。R5 settlement SHA256 `d9a2396ba4949c13977aec17e81efb4de19e2bf8ce588b202358a357a28085ee`。
同じ的中でも資金増加により利益が減り、R5 TOP5以降は損失。この観測を改善証明・Arm選択へ使わない。

## J — Capital 固定四Arm / Equal Spend
Production Frozen Recommendationは精算済み。他のCONSERVATIVE/BALANCED/WIDEとequalspend比較は**UNKNOWN / PRE-RESULT CAPTURE MISSING**。
欠落を結果後の再allocationやCapital再生成で補完しない。MEC各ArmはCapital四Arm/equalspendの代替ではない。

## K — Official RESULT Authority
[NAR公式結果](https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/RaceMarkTable?k_babaCode=19&k_raceDate=2026%2F10%2F01&k_raceNo=6)を独立確認。実Top3: 3 シンキングファーザ → 8 レイワエポック → 9 ダンガリー。
100円払戻: 馬単19,510円、三連複9,320円、三連単78,400円。
実観測時刻/result_available_at: 2026-10-02 00:18:13.632 JST（元の公式公開時刻はUNKNOWN、後から推定しない）。
取得HTML SHA256 `a22c59ebe34796ff4c9c1574bdd462c09b8df90a41a591b00c4abf1c0d0a39cd`。
Signed RESULT時刻2026-10-02 00:19:44.286635 JST、verified=true。
receipt SHA256 `4dbd5bd36870f0ded806445d826f40248126dd1c8c675ecb1a7d684895124a93`。
artifact SHA256 `8504c91cc1ecd192ef99357e246edfc0c8978d2c510e9afa91ff26bb612b5751`。
同一race/execution・Frozen FINAL binding確認済み。研究定義への遡及変更なし。

## L — Frozen Recommendation PFS / Actual PFS
投資5,900円、払戻9,320円、損益+3,420円、PFS **157.966102%**。三連複3-8-9の100円ticket的中。精算completeness100%。
馬単: 1,400→0円、三連単: 400→0円、三連複: 4,100→9,320円。
Actual PFS **UNKNOWN / NO VERIFIED PURCHASE**、購入証拠records=[]。推奨精算を実購入成績として表示しない。

## M — 二軸Failure / Correctness
Authority/Formality Axis: formal grade PASS、Signed SOURCE/FINAL/RESULT lineage検証PASS、Numerical Authority NOT_READY、Phase B.2 capture SHADOW_CAPTURE_FAILED。Capital/LOCAL measurement未成立。
Performance Axis: first material failure **PREDICTION_ROLE_W**。P2捕捉欠落、ordered pair/exact coverage欠落。三連複的中・正の純益と同時に保持。
既存correctness failure `NameError:name 'acceptance_only' is not defined`を記録。自動patchなし、Production停止なし。

## N — Count増分 / Exclusions
このR6実行による既存tracker差分（実行直前commit df622283664ebba8595c3bd8b078ab38c7d4cc83から比較）:
Common Exact LOCAL 3→4 (+1)、MEC R4 LOCAL 6→7 (+1)、MEC R5 LOCAL 6→7 (+1)、Candidate dual旧tracker 6→7 (+1)。
Phase B.2 R6 eligible/KRS/Capital増分 **0**。他raceの既存LOCAL3件をR6の受入へ転用しない。JRA KRS **4/30、増分0**。Known/Synthetic/RECON/post-startはFuture OOSへ算入しない。
capture failureは既存denominator ledgerに保持済み。本報告でledgerを書換えない。

## O — Capture / Settlement Failures / Acceptance
発走前capture failureは既存FORMAL failure Artifactに残る。RESULT R1 run36883188420はrequestの必須result_available_at欠落で失敗。観測した時刻をR2入力に追加し、予測/code変更なしで再実行。
[RESULT R2 run36883355362](https://github.com/b03la013-max/keibametrics-runtime/actions/runs/36883355362) SUCCESS。Production settlement / Signed RESULT / immutable store /既存tracker persistence成功。
R6 RESULTにはlocal_forward_measurement_settlement.json / local_initial_forward_acceptance.jsonがなく、runtime/local_candidate_forward_measurementsにR6もない。したがってPre-result Freeze→Signed FINAL→Official RESULT→Settlementまでは成立、**Persistent Forward Measurementが未完了**。完全受入HOLD。
初回一戦から改修・昇格なし。自動実購入なし。観測タスクの完了停止条件を満たしていない。Pipeline Acceptanceが成立してもPrediction/KRS/MEC/Capital/PFS改善の証明にはならない。

## 付録 — 凍結定義hash
- runtime/local_fullnumerical_candidate.py: `f4c83023fd8e331c690dc0d9f0a49d36095dfbc9003418e1a8374a59fc26471e`
- runtime/krs_prediction_utility.py: `5a6324282bc6f8d356ae696b585a3128015bf61482c7a8b94599ab9ae97468fc`
- runtime/pfs_grand_review.py: `6ef5d2e42d6c98c902e45a4739d15d9902ffb2703e513fa8b8b28570bbd8f49c`
- runtime/local_candidate_postresult.py: `79d00ffad987266bfb8be11c153295296869415f609d8f62a5aa6d8167529c64`
- runtime/common_exact_continuity_shadow.py: `862d56c66a07cb7d8a937fe481ea4f1c2736b001f22ea321c4d35e1ef219dfbf`
- runtime/mec_r4_shadow.py: `e51e195c3fa062bf428e63416e9759f7e9fde1815fe9f4c5f87ac7cd1ae753d5`
- mapping/local_full_numerical_mapping_v0.1_candidate_20260923.json: `837d6395a2d99829c04e087f6572997e2343e0943d00865db3db6d3464d8a73e`
- mapping/local_evidence_feature_rule_registry_v0.1_candidate_20260923.json: `b7740e4eb1d8e009eb872743e3f24a007e877727def72be8ee31c0931f9e5693`
- runtime/local_mec_r5_shadow.py: `4b2643b93f2eed687526dc4bb55d4f2f4e223b303c800aae3c27235f5ba9c23d`

## 付録 — Runner Missingness (発走前値)
| Runner | Missing components | Real component coverage |
|---|---:|---:|
| 1 | 21 | 0.666667 |
| 2 | 27 | 0.571429 |
| 3 | 25 | 0.603175 |
| 4 | 16 | 0.746032 |
| 5 | 16 | 0.746032 |
| 6 | 17 | 0.730159 |
| 7 | 17 | 0.730159 |
| 8 | 16 | 0.746032 |
| 9 | 17 | 0.730159 |
| 10 | 17 | 0.730159 |
| 11 | 15 | 0.761905 |
| 12 | 18 | 0.714286 |
全欠落component名とindex saturationは[発走前Candidate summary](https://github.com/b03la013-max/keibametrics-runtime/blob/main/runtime/executions/LOCAL-KM-LOCAL-FNB-20261001-R06-LIVE-R1-EXEC/FORMAL/runs/36831374594-formal/candidate_numerical_shadow_summary.json)に固定保存。

## 付録 — Immutable manifests (全file SHA256)
[FORMAL manifest](https://github.com/b03la013-max/keibametrics-runtime/blob/main/runtime/executions/LOCAL-KM-LOCAL-FNB-20261001-R06-LIVE-R1-EXEC/FORMAL/runs/36831374594-formal/manifest.json)、[RESULT manifest](https://github.com/b03la013-max/keibametrics-runtime/blob/main/runtime/executions/LOCAL-KM-LOCAL-FNB-20261001-R06-LIVE-R1-EXEC/RESULT/runs/36883355362-result/manifest.json)。
以下は既存store manifestのbyte-content hash。receipt/artifact内部hashとは対象が異なる。

### FORMAL

stored_at=2026-10-01T07:38:11.198273+00:00; manifest_sha256=`6626a5fef0d707292a203bd57ef3198f605b659f56f478adc8d3ac1c41dcf78d`; github_sha=`958af0d871d8e4725c2dd03e9f42bef7f6e81334`

| File | Bytes | SHA256 |
|---|---:|---|
| candidate_krs_dual_shadow_summary.json | 1215 | `c1711d6f36cd3a64bcd32ffc25714c81941dac629537eb38a685764bafbf4ae2` |
| candidate_krs_input_preresult.json | 17633 | `a68de350fcdfc8a46d60979de790824c3574db83b9a7f310ed3fcc0671627abb` |
| candidate_krs_input_preresult_v02.json | 17794 | `1f5428647ca0b348f3f251416c50d223c71fea41e9c9ce1725b90244c5b88ebd` |
| candidate_krs_input_preresult_v03.json | 17661 | `c941c391f2968014f7057f9e4b9d214542696c11db0633ddec440d68833bfd80` |
| candidate_krs_receipt_envelope.json | 76143 | `3e99fac11f61c2901ad3261491cbff08afee5b9e10746f7b165cbfc247f576f5` |
| candidate_krs_shadow_summary.json | 556 | `eeb5d4e692fe40c7917a27a56c1b2711a00f25238d90dbf70664fd95529f7057` |
| candidate_krs_triple_shadow_summary.json | 1779 | `d687727899d9c70e0e8507b059f2b79d8fd7e6e9f660ecf72c672e5e0c9914ad` |
| candidate_krs_v01_receipt_envelope.json | 76143 | `3e99fac11f61c2901ad3261491cbff08afee5b9e10746f7b165cbfc247f576f5` |
| candidate_krs_v02_receipt_envelope.json | 76440 | `2ac370f781fbccb1727d3b438672191270b40282edea8a955a28bd1f8c39fd08` |
| candidate_krs_v02_shadow_summary.json | 556 | `0a4d3b606f930c6648bc373b25f3d86739ef57c801e2aaf9c93c94076d2f50b4` |
| candidate_krs_v03_receipt_envelope.json | 76507 | `77dff1749e43cf3cab64e1f45416755626f5f22bad8115b4662d0a936a9f5481` |
| candidate_krs_v03_shadow_summary.json | 556 | `2dec48a38432225fd08d6fe23fc3750bdf53e1a0d02226b85834459a1bf70d19` |
| candidate_numerical_dual_shadow_summary.json | 272517 | `0b1bfc24f0d1a83647e6259703c05bc08ade996e2e36b9f95b7b3c08fe3fceee` |
| candidate_numerical_shadow_summary.json | 134256 | `3d98b44f8845ab278fd224617b15765b1023ff0f71a97deb22c3d417c3d68674` |
| candidate_numerical_v03_shadow_summary.json | 22853 | `2247c6c0699eaf101e961f87edf91f7735e5ef12df43fe515882bfe099b5fca3` |
| capital_decision.json | 631 | `e9ac28b49b4bb1fcbd59a307ae06714b2301b0280f8a3ba3fa5f23970247491a` |
| common_exact_continuity_shadow_binding_attestation.json | 535 | `96e299a52ad8085f2bfa8d56b1844337fdcaf5ade284ca4f804e157992a3b516` |
| common_exact_continuity_shadow_pre_result.json | 28964 | `deeec5a2d40c381999a00ed9457811342d40ce1e2c7b4d57c77fbcf59744020b` |
| deadline_preflight.json | 176 | `dd8b7690740e4e2fb4b0792f932261cb1b000d577d5e8ca3fbf8aa18ced94514` |
| evidence_acquisition_ledger.json | 674 | `52cbc50caf64c482d66f566952179eb98f310fe8cb1bb2de55b1b7b5daed4add` |
| execution_context.json | 631 | `b3147e5e00e5014e85787a168ea25b88c20da57f997741d0d44e53aa39863cea` |
| final_receipt_envelope.json | 166145 | `1fa43cdd67a2ea1320ac5faaf6f12ebf84f8093530e1b075d4cfae39bfe3007d` |
| formal_checkpoint_basis.json | 2067 | `d40b2846cbc2f21bde37af69cfd7e1d0f6e2c5f405ed12948d9ed48be390fe31` |
| krs_prediction_utility.json | 36967 | `9079860d49b9fc2e13fb03822c2f90088eb59c7d86af927300e91cfd66f2ffb2` |
| krs_receipt_envelope.json | 79396 | `a31887e501c0382795a5336c936a0de030d42471ee65ad1ebfcb50d8862a3ba9` |
| local_forward_measurement_failure.json | 227 | `b7dc1f85c5bee1e829c06c144651f151a4ab5fad13147defe5e0d8d612c7b31d` |
| local_mec_r5_shadow_binding_attestation.json | 592 | `f7bc0167489e81b798b9f67bca089d47e95dc3139e703ce1206f45cd2de8ded1` |
| local_mec_r5_shadow_pre_result.json | 67816 | `1a3babeecfca855ae470d2b2aea7bef528caad1c6015921557667acad9ece934` |
| mec_plan.json | 40690 | `04863f4a6e67c7eb57268442b77da7f4cc7487937c9f8f68420be0612f8bff89` |
| mec_r4_shadow_basis.json | 177499 | `11583122235d8820917c60c02942983a354847045fa274c4bb4fa1559eeecc71` |
| mec_r4_shadow_binding_attestation.json | 735 | `09f15c7ef0691d91ee78d5baf164ecb57091b4a161c0724f4038bf9b28f0b810` |
| mec_r4_shadow_pre_result.json | 20586 | `daa43ce0c042e30f11068839757ca4a62adf82dd962511dc6d14d9c7d8a77c17` |
| mec_verification.json | 224 | `0222177952c7fdde1e947d87276595e9de436d1f9e1962e76eed48e31ed59902` |
| numerical_authority_preflight.json | 2596 | `d76cdd4fcc99397471afe3f58540d82957ea7d2776017fe2aa4f2be7ff6123c0` |
| numerical_materialization_summary.json | 2959 | `c38654408a7f174bb9aa8e585ca9e2a99ec1ce15b142812f32c61f8df677e9e0` |
| official_current_state_preflight.json | 242 | `5ad6c40dfe1558e35b0cba980543e970435d4bf56ed8f9620b6e537bf5aa071a` |
| pre_krs_receipt_envelope.json | 2380 | `f10f2cf89a220a672003d4a18bbcb8f53543c813830243614dd6d3c2a2c69962` |
| race_day_fast_path_release_report.json | 12314 | `52eacda598b60780c55b36f5b4456803e7512e23a926a516e289ca22c80bb7b4` |
| race_identity_preflight.json | 154 | `9c95aaeb32d1ac026c9a89b0813691b5338e68b490d64e9aae88a14cf18d2d8e` |
| role_pair_third_closure.json | 21893 | `165da691691a933e1370ebbdb7886c2250ab74808fe7fbe6edb3ddbeba8e75e8` |
| runner_universe_diagnostic.json | 8137 | `0d6c57304e66112afad36548e096abeeaaad756676db9baf8214c31be8728e78` |
| runtime_preflight.json | 3699 | `46654c71de43abed174363e865493a5b7cdaab771dc193d7ba476dedc16038bd` |
| source_artifact_resolution.json | 206 | `25ba7ee3dc0be691db62a8035c63d4bd16a04b77bfc2553fc4aec3601c1ce3e2` |
| source_derived_krs_technical_proxy.json | 283877 | `02ca5bc305a7927989315d9ffc70d61f7e7ea8216284e14003357a33ce24dba6` |
| source_receipt_envelope.json | 954902 | `8501a346b165f2b088f81013faef49eb3c12cbc7b5856da310177c049b901265` |
| source_verification.json | 225 | `d55c4617e66b9e9dd720f922bd70db17d3ad12341f87252e1a421c055991155e` |
| static_source_basis_binding.json | 323 | `1f5a9b0ba434947c93e90a4182f748f8a81f20b55a7b0ae66f4f748b5665c464` |

### RESULT

stored_at=2026-10-01T15:19:44.605371+00:00; manifest_sha256=`dc9467d796e7b2329e52826e62ff07e979797dc45a3a2843f64c53c1046ced02`; github_sha=`df622283664ebba8595c3bd8b078ab38c7d4cc83`

| File | Bytes | SHA256 |
|---|---:|---|
| actual_purchase_pfs.json | 100 | `598d27f75fd04a29bf2d03e903d14b90c12f45774e3b5db783d48988dc25e686` |
| artifact_resolution.json | 400 | `2d3fa230d7b56844bf28e1fc655444f31ed4e675aa7a991efa85221030a984c1` |
| candidate_dual_oos_measurement.json | 2470 | `2f2ea52b70d0ccdff900e167866d880cc0d679f06ded3de556e09c1854f6f622` |
| candidate_dual_oos_status.json | 1312 | `c393aa16c72159956c11cdd4cf0891e9cd945003b02cc0fb1d317a17a3170bbf` |
| candidate_dual_shadow_postresult.json | 7605 | `426bb6c366abe765fad6128b7b27d79fa916edfab08b3ac3aff13a5b924774df` |
| candidate_v03_oos_measurement.json | 4024 | `e46c368cb33e3ffd78ec02119e5846899cdbc3067883e59d82f672cd1faa42a0` |
| candidate_v03_oos_status.json | 1139 | `ede1d512b21cd4557c76a3548439e265767f710a44d88d7272647f2dbc677900` |
| candidate_v03_shadow_postresult.json | 4393 | `ccb0b9ddca3d6d4586f6e5ee83b2b8bf5750046618624b57388e31b7181150f3` |
| candidate_v03_signed_final_binding.json | 1212 | `46d71ad9c0f76d5cb32043b8e50e93a5f9205b50c922a80d9cd5ffb338a154ce` |
| common_exact_continuity_oos_status.json | 10815 | `14977555d5d501f1caf79800fd592b0ac8a3130e999ca73f8df7aa418d5502d2` |
| common_exact_continuity_shadow_binding.json | 535 | `96e299a52ad8085f2bfa8d56b1844337fdcaf5ade284ca4f804e157992a3b516` |
| common_exact_continuity_shadow_settlement.json | 1703 | `b8026b2f7c9ab7181d1547e00380d11965c3efb85b49f7af9d8f0e030f11870a` |
| local_mec_r5_oos_status.json | 15489 | `bf5c3495006533e88313e2bc85aa2d8d467ad487acf45d024752c67c0758c61d` |
| local_mec_r5_shadow_binding.json | 592 | `f7bc0167489e81b798b9f67bca089d47e95dc3139e703ce1206f45cd2de8ded1` |
| local_mec_r5_shadow_settlement.json | 4737 | `a332ba7dca95481354c87f5cf291bf1e10a3d9b5cfe1a14ce210b5008d75d994` |
| mec_r4_oos_status.json | 54489 | `fd6cc9c683b6d906e23d7c3681a82b93a4eb728b24adaba2524dc56c89d3587e` |
| mec_r4_shadow_binding.json | 735 | `09f15c7ef0691d91ee78d5baf164ecb57091b4a161c0724f4038bf9b28f0b810` |
| mec_r4_shadow_settlement.json | 5076 | `173c135177aa465bd59999c3ac3aa219586c92f5696d627cc233cb078f5b9564` |
| race_day_fast_reflection.json | 1203 | `86e38140222dbc3ef366a14a6c210ef03733616019aaf8d7624f25a530c58f59` |
| result_checkpoint_basis.json | 90 | `17168371084295cf5d1d9c62a81e44e0aafc2504bb59f4ce12c67e8251bce65a` |
| result_receipt_envelope.json | 6568 | `abf9bb86f6dd83a74b8736aee2abdb7068f7be200290e4ca74ba36cfce72992d` |
| result_summary.json | 97662 | `9e504f34c237b4f3cb655eda110b3871faf990114233431ab9b68b0af728b664` |

# Phase B.2 Empirical Launch — implementation and launch gate

## Current main / PR rebaseline

2026-10-01開始時main：d3093d42ca0ef9d97a62fd7789fff0022d1a098d。PR117 head b33d359、main比ahead2 / behind0、conflictなし。mainが進んでいないためrebase不要。前回基準のAuthorityを再計算してNOT_READY(required63 / Production bound0)を確認。ProductionとCandidate Coverageを混同しない。

## Research foundation merge basis

Mergeの理由は測定correctnessと前向き収集の接続。Prediction/PFS改善ではない。Production mapping、KRS物理、MEC-R3、Capital policy、Venue Canonは不変更。Candidate v0.1のCompiler/MappingもB.1から不変更。既存Arm/target30は維持。Shadow failureはProductionを止めない。

変更は既存post-result owner、同一ledger/RESULT workflowの測定・権限検証・受入報告。新Model、新MEC、新Service、新KRS trackerは作成しない。

## Result authority

OOSにはoperator verified=true、nonempty official_result_verification_ref、同一race/execution、既存/verifyで検証されたSigned RESULT、PASS RESULT phase、Receipt/Artifact SHA整合、署名Artifactと同じ結果/払戻を要求。flagだけでは不可。研究SettlementへReceipt SHA、Artifact SHA、検証参照を固定。

不足はHOLD_RESULT_AUTHORITY。機械的払戻診断は保存するがKRS/Capital countへ算入しない。Production RESULT/Settlementは継続。Common Exact/MECの未来LOCAL行にも同じAuthorityを適用し、過去の既存cohortは変更しない。

## Frozen Candidate falsification

既知Developmentの劣化を保持：Winner rank 2.1→3.6、W capture9/10→7/10。1日/1場、10結合Race、1結果未確認HOLD。fitなし。

今後の凍結ArtifactからWinner rank/RR、Actual Top3 mean rank、Role capture、false W promotion/demotion、Index missingness、Candidate KRS入力参照を記録する。中立Componentの因果的寄与は事前Ablationなしに断定しない。結果後にweight0へして同じwindowを再採点しない。

Preregistered decisions：PROMOTE / CONTINUE / HOLD / REVISE / REJECT / SIMPLIFY。
Futility：複数日かつ複数会場、各day/venue clusterでWinnerとTop3順位差が悪化、Role capture増分非正、Race方向の悪化が改善を上回り、観測missingness層に方向逆転なしなら早期REJECT/SIMPLIFYレビュー。標本数30だけで継続を強制せず、1Raceだけで棄却しない。これは記述的レビュー条件で統計的証明ではない。欠測/context不足はHOLD。Production promotionもCandidate削除も自動実施しない。

15全欠測/2中立優勢Componentは凍結missingnessで監視。Removalは次Versionのみ。training/comments/paddockはUNKNOWN、代理Scoreなし。

## Initial genuine future acceptance — A–O

初回真正RaceのA–Oは既存RESULT executionのlocal_initial_forward_acceptance.jsonへ自動出力する。

|Item|内容|現状態|
|---|---|---|
|A|Race / execution identity|真正Future capture待ち|
|B|事前Freeze timestamps|同上|
|C|SOURCE/FINAL hashes|Signed immutable実行待ち|
|D|Frozen baseline|同上|
|E|Frozen Candidate v0.1 / outcome comparison|同上|
|F|Production KRS delta/rescue/non-confirmation|同上|
|G|Common Exact固定4Arm|0/30、定義維持|
|H|MEC-R4/R5|各3/30、定義維持|
|I|Capital固定4Arm/equal-spend|Forward eligible0|
|J|Official result authority|署名RESULT＋検証参照待ち|
|K|各Settlement|真正Result待ち|
|L|PFS/Arm/Robustness|Future economics未観測|
|M|Authority / Performance二軸|実装済み、Future評価待ち|
|N|Count変化|eligibleのみ増分、JRA4/30維持|
|O|capture/settlement failures|消去せず記録、欠測を0にしない|

SOURCE、FINAL、Candidate、KRS、Common Exact、MEC-R4/R5の結果前inventory hashを保存。Capital含む前後PASSが揃わず、既存Shadow settlementも欠落/未完了ならLIVE_FORWARD_MEASUREMENT_OPERATIONALを出さない。単なる合成Testや過去RaceをInitial Liveへ昇格しない。

既存candidate KRSはFINAL後にpre-post実行するため、そのdownstream経路は既存凍結Candidate KRS/RESULT Artifactを参照。実Ticketへ信号がmaterializeされていなければadded capital/countはUNKNOWN/NOT MATERIALIZED。候補から購入を推定しない。

## Validation / launch status

ローカル回帰79PASS（B.1 retained + authority/futility regression）。CIは新PR headで確認する。Production protected content22ファイルのmain一致とNumeric goldenを維持。Result race/digest/verification/ref/execution欠落はShadow HOLDとなり、Production不変をテスト。

コード接続と実Race closureは別。現LOCAL KRS/Capital Forward0、Actual verified0。No genuine future race has yet closed both phases. Phase B.2 empirical completion is PENDING。実購入は証拠がなければUNKNOWN。

PRが測定基盤としてmergeされた後、次のeligible LOCAL FORMALを監視し、前後のReceiptとpersistent countsを確認する。未来を待つ部分は自動追跡へ引き継ぐ。Prediction/KRS/MEC/Capital/PFS改善は宣言しない。

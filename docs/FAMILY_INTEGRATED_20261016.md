# Family 統合監査・実装レビュー（2026年10月16日）

Draft / NON-PRODUCTION。既存PR #285を使用し、新PR・Dispatcher・Workflowは増設しない。P0受付修復はPR #282、AKI原Selectorと既存Correctness修復はPR #265から再利用した。main/Runtime/Activation/予測Owner/29指数式/KRS/MEC-R3/Capital規則/Original FINAL/OOSを変更していない。

## 実行と金額

最新main `fa8daf81fbac6ad4e183b042ff6af3fd7d93603f`。profiles全件の現行候補を再解決した結果、現在もFamily R51・KAW v2.4・LOCAL Production Suite R3。KAW OwnerはKAWのみ有効で数値のPrediction/KRS消費は無効。RailwayはDeployment `2f7ddb5d-6ebe-4de7-b3d5-c70833fd4460`、Online 1/1、失敗・保留差分なし。

| R | Canonical正式実行 | FINAL JST | RESULT JST | 推奨額→精算払戻 | 第一重大失敗 | Dominant PFS Loss Owner |
|---|---|---|---|---|---|---|
| 1 | SOURCE→Static→KRS→FINAL→RESULT完了 | 14:25:13 | 15:07:23 | 15,600→15,030 | CAPITAL_EFFICIENCY | CAPITAL |
| 2 | 同上 | 15:14:15 | 15:36:54 | 7,500→35,610 | NONE | NONE_REALIZED_PFS_POSITIVE |
| 3 | Canonical Key/FINAL未観測 | — | — | N/A | RACE_KEY_REGISTRATION、原因UNKNOWN | UNKNOWN |
| 4 | 同上 | — | — | N/A | 同上 | UNKNOWN |
| 5 | 同上 | — | — | N/A | 同上 | UNKNOWN |
| 6 | SOURCE→Static→KRS→FINAL→RESULT完了 | 17:21:41 | 17:38:10 | 15,600→0 | PREDICTION_ROLE_P2 | PREDICTION_ROLE |
| 7 | 登録拒否報告、Canonical未観測 | — | — | N/A | 原ツール応答欠測、拒否主体UNKNOWN | UNKNOWN |
| 8 | Canonical Key/FINAL未観測 | — | — | N/A | RACE_KEY_REGISTRATION、原因UNKNOWN | UNKNOWN |
| 9 | SOURCE→Static→KRS→FINAL→RESULT完了 | 18:39:10 | 19:13:43 | 13,200→0 | PREDICTION_ROLE_W | PREDICTION_ROLE |
| 10 | 登録拒否報告、Canonical未観測 | — | — | N/A | 原ツール応答欠測、拒否主体UNKNOWN | UNKNOWN |
| 11 | 同上 | — | — | N/A | 同上 | UNKNOWN |
| 12 | SOURCE→Static→KRS→FINAL→RESULT完了 | 20:40:44 | 20:57:18 | 14,400→0 | PREDICTION_ROLE_W | PREDICTION_ROLE |

時刻の小数秒・ハッシュ・実行IDは `research/kaw_v26_20261016/integrated_summary.json` が正本。Runtime外部ストアの全件列挙機能は未確認のため「世界中にArtifactがない」とは断定しない。上表はGitHub Canonicalでの正式成立判定。

指定4戦は **58,800→15,030、PFS25.561224%、損益−43,770**。依頼文の28.73%は計算不一致。Signed 5戦は **66,300→50,640、PFS76.380090%、損益−15,660**。未成立7戦を0円の負け券へ変換せず、全12戦の実行分母へ残す。実購入はUNKNOWN。

全12戦に対するKey/Intent/SOURCE/Static/KRS/FINAL/RESULT閉ループは5/12。Discovery 12/12と送信承認を分離する。自律承認はR1・最大1Dispatchだけであり、5戦とも観測された成立は既存push経路。Schedulerの全Race成功とは数えない。保存済み5戦のユーザー到達Receiptはすべて未確認で、保存成功・通知送信・ユーザー到達は別計測。

## 原因と反証

- R1の8→5→6は実際の馬単・三連単に存在するが三連複5-6-8は非購入。156点により的中後も−570円。Head/Pair/Exact/Tierごとの額と密度を保存した。事前の券種別価格panelが未確認なのでCore-Hit RecoverabilityはPRICE_HOLD。結果払戻から事前の最適削除券を作っていない。
- R6の2着1はP3のみ、12→1はSEMANTIC_ONLY。KRSは当該Pairを290/5000回・出現順位4位で示したがProductionへ昇格する権限はない。第一喪失はP2形成で、MECが正しいPairを削ったという説明ではない。
- R9の5はStatic9位、P3のみ。KRSはWinnerを救済したが、実2着7のP2/Pairを救済できなかった。W救済とExact変換の成功を混同しない。異距離/別場実績は不明・低評価の意味を分離して候補監査した。
- R12の10はStatic4位・P2/P3のみ。KRSはWinnerを救済せず、3・11のW追加が偽陽性だった。5→10→8が存在しても10→5→8や三連複5-8-10の購入証明にはならない。
- R2は全頭実走比較なしの馬番タイブレーク。払戻が大きくても能力識別の実証ではない。全5戦でP3が全頭付与されており、P3捕捉5/5に選別力を見いださない。

第一重大失敗とは別に、Dominant PFS Loss Ownerは既存の保守的分類器を再利用。明示的なLayer損失反実仮想がないものはFIRST_FAILURE_FALLBACKと信頼度を保存し、厳密な因果寄与額とは称さない。

## 実装・比較

Correctness：PR #265の既存修復を再利用し、非有限値/booleanをPromotion/PFSの有効証拠にしない。mainではpfs=Infinityが「PFS正」と分類され、Trueが1.0へ変換されることを再現した。これは原Connector拒否の原因ではない。

測定：既存 `family_conversion_diagnostics` にopt-in資金露出・接続・事前価格の検証を再利用/拡張。事前価格は同Race・出所・Cutoff前・有限値を必須とし、欠測時はHOLD。既定の診断出力・選択・MECは維持。

Candidate：PR #265の同一 `local_aki_columns` に、観測済み異条件好走と位置情報を要するRole世界、及びKRSを条件付きで併用するablationを追加。全馬W化やSSRからの勝率化はしない。既存Role/Pair/Thirdを保持し、実Code SHA・Policy SHA・SOURCE・選択・全Stakeを凍結する。今回の凍結時刻は結果後であり、すべてHistorical Replay。

| Policy | 5戦投資 | 払戻 | PFS | 判定 |
|---|---:|---:|---:|---|
| Production / ＋KRS診断 | 66,300 | 50,640 | 76.38% | 元券面不変 |
| Original AKI | 6,900 | 8,690 | 125.94% | 同5戦の保存済みShadow。汎化証明ではない |
| PR262 Reference | 7,700 | 12,430 | 161.43% | 同一EvidenceのReplay、未昇格 |
| PR265 R1 | 4,000 | 15,030 | 375.75% | 旧17戦の性能棄却を維持。新5戦だけで復活しない |
| PR265 R2 | 5,900 | 15,030 | 254.75% | 同上 |
| Role Diversity R3 | 130,200 | 15,030 | 11.54% | 増額・性能悪化、Forward拒否 |
| Role Diversity＋KRS R3 | 109,500 | 18,720 | 17.10% | 6R Exactを救済しても赤字・過大資本、Forward拒否 |
| 有限10,000円・全MEC維持 | 0 | 0 | N/A | 5戦NO-BET。損失回避と機会費用を保存 |

同一SOURCEで全Policy、全点・各Stake、追加/削除、Core/Protection負担、KRS W/P2/Pair Rescue、偽追加、false deletion=0、Exact、PFS差、DD、Equal-Budget/Equal-Ticketを保存。Matched比較は既存の結果非依存ハッシュ順・整数100円配分を再利用し、原券面を置換しない。NO-BETも分母へ残す。旧17戦/現行19戦OOSを変更・再分類していない。

5戦51頭×29指数＝1,479値をSigned SOURCEから独立再計算。CALCULATED1,260、RULED-NEUTRAL219、未解決0。各指数/各馬の値・Rule ID・Evidence refs・欠測率を保存。計算完了とStatic/KRSでの消費は別であり、数値の未承認接続は行っていない。5戦だけから指数の因果的な増分識別価値は確定しない。

## 次の受入れと停止点

1. P0はPR #282のexact HEADをOwnerがレビュー・承認して採用する。今回の差分はClient側でありRuntime再Deployを必要とする変更ではない。未知未来の公式Plan SHA・固定Race集合・Cutoff・Dispatch機会・lease・費用・Activation承認が揃うまでHOLD。
2. 次回KAW 11/9〜13の開催日からRace番号/時刻/Runner/送信承認を推測しない。公式計画と日付別承認を再取得し、初回少数Race→同一開催複数Raceへ拡大する。
3. 全対象を固定分母にDiscovery/Key/受付Intent/凍結Intent/SOURCE/Static/KRS/FINAL/Cutoff/正本保存/通知/受領/RESULT/Settlement/Learningを測定する。重複Dispatch・不正署名受理・期限後FINALは0。未受付・第一停止工程・原エラー・時刻を残す。
4. 予測比較は同じFrozen SOURCEのProductionと既存の未昇格Policyを分離。R1/R2/R3の棄却済みPolicyを新Forwardへ登録しない。新しい性能合格Policyがまだないため、現時点の第一停止工程は `CANDIDATE_SELECTION_PERFORMANCE_REJECTED`。単にラベルを変えて次の30戦へ流さない。
5. 新PolicyはCode/Policy/入力/選択/Stakeを結果前に独立固定し、真正未来30戦以上・3日以上・収益性・DD・等予算/点数・最大勝ち除外・現行Owner Gate・Human Reviewを通す。合格しても自動昇格しない。
6. 配送は内容hashと同じFINAL SHAに結合した発走前受領時刻が必要。GitHub保存や通常Workflow完了通知で代用しない。新しい外部宛先は追加していない。

追加OpenAI有料API0、購入0、新規有料Service0、Railway上限変更0。実課金増分はBilling未取得でUNKNOWN。公式結果の追加照合は既存CIからGETだけを行い、署名/Runtime呼出し/発走後FINALを一切発生させない。

Rollback：Draftを採用しない。採用が別途承認された後も、このopt-in候補と測定差分のみをレビュー済みrevertで戻し、Original FINAL/Receipt/Intent/OOS/新しい監査証拠は削除しない。Future Activationは既存のOwner承認手順で停止し、曖昧なClaimは照合前に再送しない。

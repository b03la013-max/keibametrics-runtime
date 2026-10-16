# 川崎1R LIVE完了・PR #149採用判定

2026年10月16日 15:14 JSTまでに実物照合済み。対象: `KM-LOCAL-KAW-20261016-R01-LIVE-R1`。この記録はAIによる技術監査であり、独立Human ReviewやOwner本人確認を代行しない。

## 川崎1Rの実績

**発走前Signed FINALと本チャットへのCanonical原本提示を完了。発走後のSigned RESULT、Settlement、PFS、Learningまで完了。**

[実行38855562125](https://github.com/b03la013-max/keibametrics-runtime/actions/runs/38855562125) は15:07:40 JST時点でSUCCESS。既存Race-Key入口を一度使用した回復実行であり、Scheduler自律起動の成功とは分類しない。14:00/14:05/14:10のLOCAL起動は14:19〜14:22の確認で見つからず、原因は未確定。Activation・cron・計画SHA・最大1Dispatchは変更していない。

| 段階 | 実績（JST） |
|---|---|
| 回復入口 | 14:22:19に既存Dispatcher検査を通してclaimを保存。14:23:54に既存push入口が1回起動 |
| Signed SOURCE | 14:24:55、公式出馬表取得済み、12頭、署名再検証PASS |
| 29指数・Static | 12頭×29=348終端。308 CALCULATED / 40 RULED-NEUTRAL / 未解決0。Staticは既存のSOURCE依存規則で凍結 |
| PRE_KRS / KRS | 14:24:57 / 14:25:13、各Receipt再検証PASS |
| MEC / Capital | coverage 1.0、156点・各100円、推奨必要額15,600円。資金上限判定なし、実購入なし |
| Signed FINAL | **14:25:13.751332**、15:00発走・14:58締切より前。必須33段階完了 |
| チャット提示 | 14:28に原本ファイル、14:32〜14:33:21にCanonical全文を提示 |
| 公式RESULT | NAR原文を15:07:22.750523に取得。着順8→5→6と払戻を原文から再解析して一致 |
| Signed RESULT | **15:07:23.440255**、同じFINAL参照、15:14の外部署名再検証HTTP200・valid/verified=true |
| Settlement / PFS / Learning | RESULT側必須7段階完了。既存精算関数で再計算一致。Learningは次走向け記録のみ、Production変更なし |

Deliveryの証拠は本チャットへの原本提示とその自己観測記録。独立した受信Receiptやユーザー受領確認はないため、`user_received_at` と独立Delivery Receiptは未確認のまま。Workflow gateの未確認値を成功に書き換えていない。

Canonicalテキストは3,378 bytes、SHA-256 `df395b6cd9db71d5a4cc08bac76c1e850eee48614207c985efccf57f89e14e07`。初回ファイルの余分な末尾空行を除去し、全文提示前に原本とバイト一致させた。買い目・金額は変更していない。

14:42の公式出馬表再読取りはこの監査環境のDNS解決失敗で未成立。14:24取得後の無変更を発走前に再証明したとは扱わない。発走後の公式結果取得はGitHub実行環境で成功し、保存原文とSHAを検証した。

## 推奨買い目の精算（購入実績ではない）

| 券種 | 点数 | 推奨額 | 払戻相当 | 差額 |
|---|---:|---:|---:|---:|
| 馬単 | 15 | 1,500円 | 1,110円 | −390円 |
| 三連複 | 36 | 3,600円 | 0円 | −3,600円 |
| 三連単 | 105 | 10,500円 | 13,920円 | +3,420円 |
| 合計 | 156 | **15,600円** | **15,030円** | **−570円** |

PFS **96.346154%**、精算率100%。馬単8→5、三連単8→5→6が対象。公式三連複5–6–8の100円払戻は3,280円だが、凍結済み推奨にはその組合せがないため推奨三連複の精算は0円。欠損払戻を0円に置き換えていない。

既存Learningの主な失敗分類は `CAPITAL_EFFICIENCY`（的中しても全体は損失）。`PREQUENTIAL-NEXT-RACE-ONLY`で記録され、Prediction/KRS/MEC/Capitalや数値重みの自動変更はない。実購入PFSは `UNKNOWN / NO VERIFIED PURCHASE`。監査による馬券購入は0件。

## 署名と永続化

- Signed FINAL Receipt: `58cb29919a8612edd3b0ebf5e5446d5400e924dd078ae739a92554dd7a097eb0`
- Signed RESULT Receipt: `ee4e80a41d3bdfd6871c796596e797d4ecad4baf7f1ea3445ee3f5c0791623dc`
- RESULT artifact: `cb7820680ca6302c64ef68ed763691c83af3ef0597cd28250fc0d559decefe59`
- NAR公式原文: `375c3209367011238c258ad9b963617934487fd48fc4984e20694a89320ca5ef`
- RESULT Actions ZIP: `8ea8c86218d7bc1c2e7e1f49791ccafc0422b30c29ea9ce2825b2ac31eedbe11`、Artifact ID 12029065211。ダウンロード後digest一致。
- SOURCE / FORMAL / OFFICIAL_RESULT / RESULTの全manifestと各ファイルhashを、既存`resolve_phase`で検証。保持済みFINALを再実行・再署名していない。
- RESULTジョブにはscratch restore warningがあるが、signed recordsは既にpush済み。mainからのmanifest全体読戻し成功で永続化を確認。
- 回復リクエストのmain commit: `3a378cc7c46b660dad27d0c5d22b53d429926418`。実行確認後のstate追記: `77b242f4b68802ef292e663228d6fecefa814933`。既存OOSの派生ビュー更新は既存RESULT処理によるもので、この監査で履歴を書き換えていない。

RESULT観測のstate追記commit: `3507dc1f0885c0164eb225d9fe3a1577d1c74945`。既存`checkpoint_status`でSOURCE/FORMAL/RESULT参照を更新し、実行状態をcompleted/successへ反映。独立受領未確認の値と承認範囲は維持。

## PR #149の採用判定

**技術監査は条件付きPASS、MergeはHOLD。** HEAD `57a0b4d21323a3c0b9015d6b575f228555a8f40d`、Draft/open、unmerged、GitHubレビュー0件を再確認。既存CI 3/3 SUCCESS、既存回帰100件PASS。NaN/Infinity/bool/文字列等24拒否プローブと正常値5組、正当な0円精算を既存Verifierで確認。今回の実物Signed RESULTも同じPRの既存Verifierを通過した。

変更4ファイルはworkflowの未確定OFFICIAL_RESULT保存条件、既存AKI精算照合の型・有限値検査、対応する2テストファイルのみ。Dispatcher/SOURCE/Static/KRS/FINAL経路の実装変更なし。新しいValidatorなし。

正常な払戻・0円の受理を確認。ただし従来からの返還・同着の一部は `SPECIAL_OFFICIAL_OUTCOME_NEEDS_SETTLEMENT_SUPPORT`、凍結対象の取消は `OFFICIAL_RESULT_REFUND_REQUIRED` でHOLD。正常数値としての同額返還ペア受理を、返還全経路の対応完了とは解釈しない。

main `a03e2676039188f855dad6986847d162e75c6d00`とのmerge-treeは競合0、tree `c9b247013abbec309f414d9b5599d02b2c679b4d`。これはMerge実行ではない。

Owner本人確認の対象は[既存の4ファイル差分・精算停止条件・Rollback記録](pr149_owner_review_1344JST.md)に限定する。署名・公式権威・同一FINAL・金額整合性が欠ける場合は停止。Rollbackは4ファイルの限定revertで、取得済みCheckpoint、Signed FINAL/RESULT/Receipt、OOS履歴は保持する。

ユーザー指令Cの「本人確認が未成立ならMergeをHOLD」に従う。作業継続指示を、差分を本人が確認済みという事実や独立Human Reviewに置き換えない。Owner限定承認方式のため、この指定HEAD・停止条件・RollbackについてOwner本人の確認記録が成立するまでは採用しない。

## 費用・権限の結果

OpenAI追加有料API要求0件、馬券購入0件。Railway Soft $5 / Hard $10を維持。新Architecture、追加サービス、Merge、Deploy、新Activation、Engine/parameter/Current Authority/Prediction/KRS/MEC/Capital設定変更なし。既存Activationは維持した。運用回復で追加したのは既存承認範囲のR1 claim・リクエスト・実行状態と監査記録。

15:16 JSTの最終スキャンでは別途R02のrun `38859938474`（commit `9ae4f528c64402d91ceb916691591ae3e39a54b2`）も存在した。差分はR02専用リクエスト、ジョブもR02であり、今回のR01の重複起動ではない。この監査はR02を開始・変更していない。R01の結果はその別実行と混同しない。

主目的の発走前FINALとCanonical提示、発走後の結果処理は完了。残る未成立項目はSchedulerによる自律起動の実証、独立Delivery受領確認、PR #149のOwner本人確認。

# 川崎8R SOURCE-first 入口修復 — 2026-10-12

対象: `KM-LOCAL-KAW-20261012-R08-LIVE-R1`、18:30 JST発走。

## 実証した結果

外部LOCAL RuntimeでSOURCEを取得・署名検証。凍結時刻は18:21:06.217214 JST、署名時刻18:21:10.657202 JST。公式出走馬12頭。Receipt SHAは`0c3cd98133511663a7d4cb18ca124fd7727fd7af40a4351cc23ad68e7071bd63`。

現行63ルール・29指数の診断計算は348/348項目を数値終端化。CALCULATED=306、RULED_NEUTRAL=42、未解決=0、strict_full_numerical_ready=true。42項目を計算済みとは呼ばない。既存full_numerical_calculationフラグはfalseを保持し、strict closureとは区別する。予測/KRS/Ticket/Capitalへの数値利用承認は全てfalseのまま。

承認済みStatic Freezeがなく、停止理由は`PRODUCTION_STATIC_OWNER_REQUIRED`。KRS、MEC、Capital、Signed FINALを実行済みとは報告しない。既存C2 OwnerはDraft PR #124・受入未完了で、`tools/LOCAL_FORMAL_RESTART.md`にはAPI課金停止記録がある。今回、Ownerを自作・昇格しない。発走後の正式事前予測再構成は禁止。

## 修正内容

1. `runtime.local_race_entry`はレース指定の明示SOURCE-first入口。現在AuthorityとFamilyを確認し、既存の検証済みSOURCEを直接参照、未取得なら発走前期限を確認して外部取得する。入力Intent・全指数の診断・停止理由を保存する。承認済みFrozen Staticを明示した場合のみ従来Formal入口へ接続する。従来のFULL入口でStaticを要求する規約は維持する。
2. orchestrator指定出力先を`KM_RUNTIME_OUT`でSOURCE/FORMAL/RESULT subprocessまで伝播。従来は指定先が空でもSOURCEチェックポイントを保存してPASSになり得た。
3. SOURCE保存前と再開時に、Receipt存在、SOURCE_FROZEN、LOCAL・race_id一致、検証成功、formal_readyを必須確認。空チェックポイントでPASSを返さない。
4. 独立dispatch workflowはread-only権限でSOURCE-first実行と証跡保存。既存Production suite・係数・モデル・Authority・Venue設定・購入方針を変更しない。HOLDを成功終了にしない。自動昇格・自動購入・mainへの実行記録自動pushはない。

## 検証・保存

LOCAL関連189 tests PASS（実際のGit競合テストを含む）。SOURCE-first入口を川崎8Rの実SOURCEで実行し、SOURCE_PASS→数値診断→Static Owner HOLDまで確認。新しい出力先配線はsubprocess環境と保存対象を検証する回帰テストで確認。修正後の新規外部SOURCE取得、KRS/MEC/FINALの実証とは区別する。

`evidence/kaw_r08_entry_repair_20261012/closure_summary.json`に件数と元JSON SHA-256を記録。SOURCE全体と全指数のJSONはgzipで原文保存し、展開後SHAを照合可能。署名済みSOURCEそのものは変更しない。

ローカルcanonical execution storeの初回不完全runを保持し、実際の署名済みSOURCE/検証結果を含む別runを18:26:57 JSTに追記してlatestを更新した。過去runの書換えはない。GitHubには圧縮原文と要約を証跡として保存し、canonical storeへ配備済みとは報告しない。

実行例（リポジトリroot、現行依存導入済み）:

```sh
python -m runtime.local_race_entry --request race-request.json --output entry-out --run-id source-first-unique
```

最低限、LOCAL family、venue_id/race_date/race_no、タイムゾーン付きscheduled_post_at/prediction_cutoff、現行current_authority_manifestを指定する。execution_id/race_idを指定する場合は一致必須。workflow dispatchのrequest_jsonにも同じJSONを渡せる。SOURCEは正式FINALではないため、Static Owner HOLDをNO_BETとして精算・学習しない。

## 完全解消の未達条件

正式FINALまでの完全解消には、現行Authorityで受入済みのStatic Ownerが発走前にFrozen Staticを供給する必要がある。入口修正をProductionへ反映するには独立PRの受入・配備も必要。川崎8Rの期限は経過しており、その正式事前FINALは今から作れない。次の対象レースで上記Owner条件を満たしたうえで、署名付きSOURCE→Static→KRS→MEC/Capital→FINALを通し実証する必要がある。

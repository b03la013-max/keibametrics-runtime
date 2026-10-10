# 京都５ Formal pipeline repair — 2026-10-10

## 到達状態

既存Single Entryの停止判定・証拠保存・完了判定を修復。買い目付きProduction Signed FINALの成立は未完了。
調査開始時main: `d5d0c05d3d5ab7e2b6227b86dd0dbaed3f684a6d`（PR189）。Current Authority: `KM-FAMILY-CURRENT-AUTHORITY-20261008-R44`。京都攻略はv1.0-KYO-CANDIDATE、Production昇格なし。

## 京都10Rと実ログ

調査したmainの `runtime/jra_formal_intents/`, `runtime/requests/`, `runtime/executions/`, `runtime/exact_gaps/` には2026-10-10京都10Rの該当記録がない。参照会話の「京都10R調査」はRuntime起動証拠を示していない。外部全体に記録が存在しないとは断定しない。したがって京都10R自身の実ログから計算失敗を断定しない。

実際の停止は京都8R run [38024041474](https://github.com/b03la013-max/keibametrics-runtime/actions/runs/38024041474) / job 114130967768のGitHubログを再取得して確認。Signed SOURCE待機後、2026-10-10 13:27:25 JSTに`JRA_PRODUCTION_STATIC_OWNER_NOT_AUTHORIZED`を先頭に出し、同じ例外に`PRODUCTION_FEATURE_INDEX_CLOSURE`を付加している。Formal submit/waitはskip。`continue-on-error`のstep conclusion successを計算成功として扱えない。
東京11R run [38025311364](https://github.com/b03la013-max/keibametrics-runtime/actions/runs/38025311364)もオンラインjob情報を再確認。NO-BET生成とOIDC attestationは成功、正式Submit/Waitはskip。既存PR186のNO-BET正常終了改善を再実装していない。

## 修復した不具合

1. Auto handoffのFull20検査をStatic承認検査の前に移動。数値不足が最初の停止原因になり、Staticの独立阻害点も準備レポートに保存される。
2. Static readinessの固定falseを、現行Authorityの既存activation gateと実行可能Static診断で判定する。権限は一切付与しない。準備完了を外部全工程完了とは表示しない。
3. CLIがhandoffの正確な失敗理由を保存してレポートSHAを再計算する。Evidence NO-BET対象は実際のBase不足に限定し、Static-only、hash不正、時点不正をそのNO-BETに変換しない。
4. 全20が揃ってStaticで停止しても、NO-BETファイルの不存在を理由にExact Gap保存が停止しない。Candidate投入は既存cutoff guardを継続使用する。
5. Formal run IDだけで`FORMAL_COMPLETE`にならない。canonical runnerが署名検証後のsummaryをartifact化し、Single Entryは成功runから取得してrace/source、全20、KRS実数、Receipt検証、全mandatory stage、非Replay・非acceptanceを照合する。これは外部Runnerの検証結果の内容照合で、ローカル関数による独立署名検証と偽称しない。
6. 回帰CIはread-onlyで実SOURCEを歴史的再計算。既存外部KRS SIM-HIGH mechanical acceptanceもhandoff変更時に起動するよう接続。

## 実SOURCE再計算

5件を現行コードで再計算。durable manifest/file hashとenvelope内公開鍵でのEd25519を検査。OIDC signerの独立検証はこのローカル再計算では行っていない。

| SOURCE | Base計算 / 停止 | 全20計算 / 必要 | 最初の具体原因 |
|---|---:|---:|---|
| 京都8R | 6 / 72 | 0 / 120 | LOW_CAREER HPI 0.34 < 0.38 |
| 京都9R | 1 / 207 | 0 / 320 | ESTABLISHED HPI 0.29 < 0.42 |
| 東京3R | 16 / 192 | 0 / 320 | LOW_CAREER HPI 0.16 < 0.38 |
| 東京5R | 36 / 120 | 0 / 240 | NEWCOMER SSI 0 < 0.34 |
| 東京11R | 11 / 132 | 0 / 220 | LOW_CAREER HPI 0.16 < 0.38 |

全件で独立したStatic activation不足も確認。元SOURCEを改変せず、再計算を事前予測・OOSとして登録しない。各馬×指数の不足Feature・重み・証拠Ownerは再現スクリプトが出力する詳細JSONにある。

## 検証

対象10テストファイル: **52 passed, 70 subtests passed**（Python 3.14一時環境）。数値不足と権限不足の順序、Candidate数値拒否、Static改ざん、source hash、freeze/cutoff、KRS 20000→5000拒否、Replay/acceptance拒否、NO-BETとFINALの分離を含む。
変更4workflowのYAML、shell、埋め込みPythonの構文検査成功。全リポジトリsuiteの成功は主張しない。

再現:

```sh
python scripts/audit_jra_formal_repair.py --output runtime_out/repair_audit
python -m pytest -q tests/test_jra_production_auto_handoff.py tests/test_jra_single_entry_outcome.py tests/test_jra_single_entry_exact_gap.py tests/test_jra_static_owner_executable.py tests/test_jra_production_no_bet_terminal.py tests/test_jra_production_no_bet_real_source.py tests/test_jra_candidate_dispatch_guard.py tests/test_jra_execution_maturity_bridge.py tests/test_jra_production_krs_contract.py tests/test_jra_official_fact_evaluator_production.py
```

## 残ブロッカー

- SOURCEは取得済みでも、既存Production mappingの必要Evidence coverageを満たせない。既存閾値・重みを下げたり、未観測Featureを数値で埋めたりしていない。全20を成立させる実在Evidence取得と登録ruleに適合するEvaluator閉鎖が必要。
- R44に新Static Ownerの独立Production activationがない。必要なPolicy別forward OOS・市場比較・独立reviewの実体がない状態で承認を捏造できない。既存Candidateの件数を新Ownerへ流用しない。
- 添付『貼り付けたテキスト（1）.txt』の2026-10-10 R9原文はローカル資料と参照チャットの取得結果にない。取得できた運用概要・現行Authority・ユーザーの明示制約で作業し、原文との完全準拠は未確認。
- 本修復で新規の実レースProduction PRE_KRS/FINALは発行していない。締切後の京都10Rに事前FINALは作らない。外部mechanical acceptanceが通っても、未知Raceの発走前正式完走とは別。

正式完了には「実SOURCE Full20 closure」および「正当なStatic権限」を満たした次の発走前Raceで、canonical経路のKRS/MEC/Ticket/Capital/Signed FINALを実証する必要がある。

## PR外部検証の実施結果

[PR190](https://github.com/b03la013-max/keibametrics-runtime/pull/190)の実装commit `2aa7a470ea836d6be79761f8b7a1e53b0d97607e` で6workflow成功を確認。

- [専用回帰CI 38028621226](https://github.com/b03la013-max/keibametrics-runtime/actions/runs/38028621226): Python 3.13でも52件・70 subtests成功、実SOURCE5件の歴史的再計算成功。
- [外部KRS 38028621166](https://github.com/b03la013-max/keibametrics-runtime/actions/runs/38028621166): SIM-HIGH requested=20000 / actual=20000、外部`/verify`成功。Receipt SHA `7dfe15f2516db9e5b75638d419c00fb4456b3524c2a3e03b2fbf264908721b7b`。入力は合成mechanical acceptanceで、Production/OOS/購入権限なし、FINAL未発行。
- Production Source-only Real Evidence Closure、JRA LOCAL Maturity Import、Family R31 Scope Ownership、LOCAL Runtime Correctness Regressionも成功。これらのCI成功を実RaceのProduction全工程完了として扱わない。

実装commitのGit treeはローカルcommit `308b5072a900b8a2afe2d41a1034d1f6cbb6d0b9` と同一 (`5b65a4750c8a36559eb8f2d51f3db97ade10b21a`)。Git送信の認証が利用できなかったため、接続済みGitHub API経由で同一treeを提出した。main未反映、draft PRとして保存。

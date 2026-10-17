# JRA 10月18日36Race・昼時点の再確認とAutopilot実障害修復

2026年10月17日12時台JSTの実取得。公式HTMLで新潟・東京・京都36Race／450頭を再確認し、登録hash、Race ID、発走、Cutoff、Dispatch Windowを照合。発走時刻変更0件。新潟6Rは初回RUNNERS_EMPTY、1回の通常公式再取得で15頭を確認し、両観測を保持した。当日Signed SOURCEではない。各Raceの最初の未成立工程は当日Intent／Dispatch Receipt、状態WAITING36、READY0。未来の実行成功は計上しない。

## 独立した実障害

東京3RのBVI_STATIC_PROOF_BINDING_INVALIDはPR298で修復済み。今回判明した東京5R等の受付障害は別原因。Autopilotをruntime/jra_source_runtimeから直接起動すると、配信Receiptを読むrace_statusが兄弟runtime内のjra_production_postresultをimportできない。Run38993239193／38995356610の実ログでModuleNotFoundError、Exit1を確認。Status生成がDispatch APIより前に失敗し、11:30:38の東京5R claimが未ACKのまま残った。WAITING表示は古いIndexであり根本原因ではない。

既存Autopilotのimport pathを直接起動時に解決。Race別Status隔離にImportErrorを含め、API未呼出しが確定したCLAIM_PUBLISH_FAILED_NO_SENDだけ既存窓内の再試行を認める。応答不明claimの自動再送はしない。既存Dispatch Window、Resolver最小lead15分、Prediction Cutoff、予測Policyは変更しない。

東京5Rは12:25発走、Resolver受付期限12:10、Cutoff12:20。今回指令到着時点で既存Resolver期限超過のため新規事前実行を行わない。新潟6R／京都6R／東京6Rは公式Resolverで再取得し、重複Intentがないことを確認して既存Formal Intent push入口で救済した。新Workflow／Webhook／入口を追加していない。各最終成果は実Runで別途判定する。

## 実Runtimeと血統証拠

Railwayはkmjrawitnessv061 Project内の既存KRS／Calculator双方Online、既存Deployment SUCCESS、stagedなし。mainと配置アプリGit SHAの完全一致はimage deployment metadataにcommitHashがないため未証明。再配置・再起動なし。HealthのEngine／parameter_map／署名鍵を既存JRA契約と照合。

東京4R、新潟5R、京都5Rの実Canonical FINALでimmutable hash、PRE_KRS／KRS／FINALのEd25519署名と券面bindingを独立検証。各KRS5000回、Capital PAPER、0点0円。41頭中39頭MEASURED、2頭DCR_ONLY。全当日Runner分母のCoverageとは区別する。過去京都10/12R12のFINALも署名確認したが、既存Post-Result経路の取得はSOURCE_DNS_RESOLUTION_FAILEDで停止、RESULTを生成・推測せずPFS欠測を保持した。

現行血統A/B/C Forward OOSは0/30、旧系列7件と混ぜない。新408走のProduction受入0、係数・Mapping・AKI・KRS・MEC・Capital変更0、購入0。GitHub availabilityと人の受領確認は別。自動ChatGPT即時Push・人の既読は未証明。

## 36Race別準備

時刻JST。すべて条件付き・LIVE ACCEPTANCE PENDING。

| Race | 発走 | Cutoff | 頭数 | 状態 |
|---|---:|---:|---:|---|
| KM-JRA-NGT-20261018-R01 | 09:40 | 09:35 | 13 | WAITING |
| KM-JRA-TKY-20261018-R01 | 09:45 | 09:40 | 12 | WAITING |
| KM-JRA-KYO-20261018-R01 | 09:55 | 09:50 | 13 | WAITING |
| KM-JRA-NGT-20261018-R02 | 10:05 | 10:00 | 15 | WAITING |
| KM-JRA-TKY-20261018-R02 | 10:15 | 10:10 | 10 | WAITING |
| KM-JRA-KYO-20261018-R02 | 10:25 | 10:20 | 7 | WAITING |
| KM-JRA-NGT-20261018-R03 | 10:35 | 10:30 | 13 | WAITING |
| KM-JRA-TKY-20261018-R03 | 10:45 | 10:40 | 12 | WAITING |
| KM-JRA-KYO-20261018-R03 | 10:55 | 10:50 | 12 | WAITING |
| KM-JRA-NGT-20261018-R04 | 11:05 | 11:00 | 15 | WAITING |
| KM-JRA-TKY-20261018-R04 | 11:15 | 11:10 | 16 | WAITING |
| KM-JRA-KYO-20261018-R04 | 11:25 | 11:20 | 15 | WAITING |
| KM-JRA-NGT-20261018-R05 | 11:55 | 11:50 | 15 | WAITING |
| KM-JRA-TKY-20261018-R05 | 12:05 | 12:00 | 8 | WAITING |
| KM-JRA-KYO-20261018-R05 | 12:15 | 12:10 | 5 | WAITING |
| KM-JRA-NGT-20261018-R06 | 12:25 | 12:20 | 15 | WAITING |
| KM-JRA-TKY-20261018-R06 | 12:35 | 12:30 | 8 | WAITING |
| KM-JRA-KYO-20261018-R06 | 12:45 | 12:40 | 18 | WAITING |
| KM-JRA-NGT-20261018-R07 | 12:55 | 12:50 | 18 | WAITING |
| KM-JRA-TKY-20261018-R07 | 13:05 | 13:00 | 12 | WAITING |
| KM-JRA-KYO-20261018-R07 | 13:15 | 13:10 | 9 | WAITING |
| KM-JRA-NGT-20261018-R08 | 13:25 | 13:20 | 15 | WAITING |
| KM-JRA-TKY-20261018-R08 | 13:35 | 13:30 | 16 | WAITING |
| KM-JRA-KYO-20261018-R08 | 13:45 | 13:40 | 12 | WAITING |
| KM-JRA-NGT-20261018-R09 | 14:00 | 13:55 | 14 | WAITING |
| KM-JRA-TKY-20261018-R09 | 14:10 | 14:05 | 9 | WAITING |
| KM-JRA-KYO-20261018-R09 | 14:20 | 14:15 | 8 | WAITING |
| KM-JRA-NGT-20261018-R10 | 14:35 | 14:30 | 18 | WAITING |
| KM-JRA-TKY-20261018-R10 | 14:45 | 14:40 | 9 | WAITING |
| KM-JRA-KYO-20261018-R10 | 14:55 | 14:50 | 10 | WAITING |
| KM-JRA-NGT-20261018-R11 | 15:10 | 15:05 | 10 | WAITING |
| KM-JRA-TKY-20261018-R11 | 15:20 | 15:15 | 13 | WAITING |
| KM-JRA-KYO-20261018-R11 | 15:40 | 15:35 | 17 | WAITING |
| KM-JRA-NGT-20261018-R12 | 16:00 | 15:55 | 10 | WAITING |
| KM-JRA-TKY-20261018-R12 | 16:10 | 16:05 | 16 | WAITING |
| KM-JRA-KYO-20261018-R12 | 16:30 | 16:25 | 12 | WAITING |

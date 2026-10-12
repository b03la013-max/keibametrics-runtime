# JRA AKI positive-evidence failure routing repair

京都5R（2026-10-12）のSigned SOURCEからProduction Full20は180/180まで閉じたが、全9頭のRFI・PRIは第3条DCRの50、TPIは49.748–55.617、F3Sは54.126–60.432。列の裏付けは3指数中2以上65が必要であり、W/P2/P3全列が空となった。指数の計算完成は肯定証拠の成立を意味しない。

本来の選定停止に加え、ClassifierがAKIを扱わず、例外後も`FIRST=None / FORMAL_PRE_KRS_HANDOFF`を保存していた。既存NO_BETはFull20欠落またはStatic権限欠落しか受け付けず、Workflowは検証可能なTerminalを作れず失敗した。

修正は承認済みSelectorのエラーを再現したうえで、`PRODUCTION_AKI_COLUMN_SELECTION`を保存し、二種類の肯定証拠停止（空列／禁止された単頭）のみ独立したAKI NO_BETへ送る。Runtime/Registry fingerprint、SOURCE・Full20・Authority bindingを検査し、馬別列別の主指数、裏付け指数、gap、除外理由を保持する。Registry不正、SOURCE不正、未承認、その他内部エラーはNO_BETへ偽装せずFail Closedを維持する。

見送りTerminalは全20指数をCALCULATEDのまま保存する。投資0、券面なし、PRE_KRS/KRS未実行、Signed FINALなし。独立GitHub OIDC Attestationと内容再計算検証を行い、当日索引では`AKI_NO_BET`とFull20欠落による`EVIDENCE_NO_BET`を区別する。結果後は既存NO_BET Learningへ接続し、PFSを定義しない。

R50、AKI Runtime/Compiler、閾値、mapping、KRS Physics、MEC、Capitalは変更しない。候補を強制追加せず、CandidateをProductionへ昇格しない。

京都5RのRecovery Workflowは原Signed SOURCEのEd25519/OIDCを検証し、承認済みProduction数値を再計算する。新しい決定の作成時刻がCutoffを超えれば`HISTORICAL_DIAGNOSTIC`とし、事前FINALやLIVE OOSへ遡及しない。原Exact Gapや旧署名Artifactは書き換えない。

検証：新規12テストで空列・単頭禁止・不正proof/source/ledger/authority・成功例のNO_BET化拒否・非ゼロ投資・時点違反・実京都5R SOURCE再現・未知内部エラー・ゼロ投資の結果後Learningを確認。関連するAKI、Handoff、Classifier、NO_BET、Learning、Autopilot、Maturity Bridgeの回帰テストも実行する。未知未来の予測性能を実証する変更ではない。

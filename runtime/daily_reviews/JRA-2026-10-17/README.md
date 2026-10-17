# JRA 2026-10-17 全36Race監査

| 成果物 | 正本 |
|---|---|
| A 全36Race Ledger | audit_ledger.json / scorecard.csv / races/*.json |
| B Daily Formal Review | daily_formal_review.md |
| C PFS Grand Review | pfs_grand_review.md / runtime/pfs_grand_review/JRA-2026-10-17.json / ticket_settlement.json |
| D Improvement Backlog | improvement_backlog.md / .json |
| E Next-Race Learning / OOS | next_race_learning_oos.md / forward_oos_plan.json / next_race_learning_index.json |
| Full20 | full20_cells.csv / numerical_discrimination.json |
| AKI / Prediction / Semantic | races/*.json |
| KRS | krs_incremental_utility.json / evidence/jra_day_review_20261017/krs_checkpoints |
| BVI | bvi_consumption_review.json |
| 欠落 / 出典 / 完了 | missing_artifacts.json / input_manifest.json / completion.json |

再現: `python scripts/jra_full_day_postrace_review.py --date 2026-10-17`、続いて `python scripts/render_jra_day_review.py`。収集は `scripts/collect_jra_day_review.py`（既存JRA公式専用retry client、read-only POST）。raw decoded HTML、取得時刻、POST tokenとSHA256、元Artifactパスを保持。

DATA COMPLETE / PREDICTION PARTIAL / CAPITAL COMPLETE / LEARNING PARTIAL。Analysis-only。Production数値Policy・署名済みArtifact・元Learningの書換えなし。

詳細なRace別JSON、全馬20指数CSV、公式HTML、Actions原KRS/RESULT出力は `evidence/jra_day_review_20261017/payload.tar.gz` に元bytesを保存。`payload_manifest.json` のSHA256と `python scripts/unpack_jra_day_review.py` で検証・展開する。展開後、上記2コマンドで集計を再現する。元のProduction署名ファイルは置換しない。

券種別Candidate/Paper-reference/各MEC Shadow、勝ち馬20指数順位、Head別資金集中、Lane別KRS救済は `supplemental_metrics.json`。再現コマンド `python scripts/jra_day_review_supplement.py`。

KRS補正はJRA診断専用 `runtime/jra_krs_utility_measurement.py` を監査から明示使用する。事前登録がhash固定するCommon `krs_prediction_utility.py` とforward_protocolは元bytesを維持する。Production呼出への接続と補正後OOS cohortはOwner承認・事前登録待ちで、今回自動Activationしない。

追加検証：SOURCE OIDCを公式GitHub CLIで独立照合し、34件中34件がPASS。Repository、SOURCE Workflow、source SHA、main ref、GitHub-hosted Runnerを制約し、証明対象SOURCE bytesのSHA256も照合した。東京11Rも公開API取得制限解除後に原Bundle取得・独立検証が通過した。34/34件PASSであり、原本欠落・署名不成立ではなかった。BundleとVerifier JSONは監査payloadに保存、一覧は `evidence/jra_day_review_20261017/source_oidc/summary.json`。`python scripts/verify_jra_day_source_oidc.py --gh /path/to/gh` で既存Bundleを再利用して再検証できる。Predicate内のRun IDはWorkflowが記載した主張として扱い、証明書のWorkflow/Source identityと区別する。

京都12Rの追加感度分析は `dead_heat_review.json`（再現: `python scripts/jra_dead_heat_review.py`）。公式払戻対象の5→7→10と5→10→7を別々に評価。両順序ともW=False、P2/P3=True、Ordered Pair/Exact=False、推薦券面払戻0円。KRSの役割救済は各順序1件だが、異なる役割への割当を合算しない。元のP2/P3/Order評価母数と正式RESULT同着保留は維持。Productionへの変更・追加署名・Receipt再生成はない。

追加実行保証Review: [remaining_evidence_closure.md](remaining_evidence_closure.md)。KRS Output結合・送信bytes checkpoint・投資0保持の最小Correctness修復、Learning時刻検証、全36Failure Matrix、固定Shadow比較を保存。Merge/Activation・次Race消費は未確認。

追加差分Reviewと本番導入条件: [pr305_diff_review.md](pr305_diff_review.md)。勝ち馬16件・320セルの追跡: [winner_discovery_16_review.md](winner_discovery_16_review.md) / JSON。五Laneの同一Race観測比較は `five_lane_role_observation_review.json`。既存Shadow登録bytesと定義SHAは不変。

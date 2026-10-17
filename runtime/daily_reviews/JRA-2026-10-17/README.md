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

# Phase 0.7 確定単勝オッズ — 公開用数値メタデータ

Owner記録: `OWNER-APPROVAL-20261103-1211-PHASE07`。
対象はPhase 0の固定178R（2026-10-11〜2026-11-01）。追加期間・自動取得・本番接続は含まない。

## 取得・保存

2026-11-01の18Rパイロットを全件受入した後、残160Rを取得し、全178Rを再検証した。
robots・利用条件の直接確認2件を含め211リクエスト。開始間隔の最小値6.115116834640503秒。
HTTP失敗0、最終HOLD0。取得開始から最終応答まで2243.249秒（修復による停止時間を含む）。
実ページに観測した完全なリンクを使用し、cnameやchecksumを生成していない。

このRepositoryはpublicである。各JSONは `JRA_CLOSING_ODDS_PUBLIC_METADATA_V1` で、
解析値、URL、実取得時刻、Raw/parsed/元capture/公開recordのSHAだけを保持する。
HTML原文・raw_html_base64は含まない。本文を省いた公開recordを完全captureと偽って検証しない。
`source_capture_file_sha256` は私有Artifact内の元JSONのSHAであり、公開JSON自体のSHAではない。
`source_capture_sha256` は元captureの内部payload digest、`public_record_sha256` は公開recordのdigestである。

Rawと完全capture、失敗時の原票、全リクエスト記録は本人専用の非公開Artifactに保管した。
Artifact名: `KeibaMetrics_Phase07_private_closing_178R_20261103.zip`。
SHA256: `3348002659d95a8b9784f71bc91e098f3cc1ae732fe4a14378638896c43b1b46`。
公開RepositoryのActions Artifactは非公開Storeとして扱わず、今回の手動取得workflowも実行していない。

## 適格性と原本の保持

明示的な最終オッズ表示、Race日付・場・番号、全Active馬の価格と集合を検証した。
旧RESULTに取消欄がなく、元モデルには残っていた次の3頭は、公式最終表の取消表示から
両比較系列で同じように除外し、市場確率・ZAIのレース内標準化を再計算した。

- `KM-JRA-KYO-20261018-R09`：7番。
- `KM-JRA-NGT-20261018-R05`：3番。
- `KM-JRA-KYO-20261024-R07`：7番。

`KM-JRA-NGT-20261024-R04` の取消4番は元モデルから既に除かれており、非数値の証拠として保持した。
取消・除外は着順不在や欠番から推測しない。未知のActive馬・着順との矛盾・説明不能の欠番は拒否する。
今回の比較は178R・2,346頭、時系列前後半89R/89R。元Phase 0は178R・2,349頭であり、
そのsummary・Frozen FINAL・RESULT・SOURCEは変更していない。元入力544ファイルのSHA一致を確認した。
最終オッズ画面には独立した人気列がなく、人気順位は未保存。価格から人気を推測していない。
取得時刻は2026-11-03で、過去の市場締切時刻を意味しない。記録は未署名の研究用Evidenceである。

## 結果とコード

入力main: `f14df65507867833f54ab989126ac6114d50dec1`。
実原票対応の研究Reader: PR #366、`8006ccc1bf51343335de6761756b42b4141caaf1`（Draft・別審査）。
ProductionのSOURCE / autopilot / delivery / postresult / Policy / 重み / 買い目に変更はない。

今回の比較結果:
`runtime/reports/benter_second_stage/2026-11-03-closing-r2/closing_comparison.json`。
13指数・オッズ変化:
`runtime/reports/benter_second_stage/2026-11-03-closing-r2-indices/`。
既存asofを上書きせず、新しいr2ディレクトリに保存した。
同フォルダのsummary.json・summary.md・ledger.csvはPhase 0互換の旧主系列出力であり、
今回の同一Active集合による比較はclosing_comparisonを参照する。
Claude試算との既知の差は、開催日境界での分割と、平均中心化のみという方法の差による。

再現には本人の私有ArtifactとReader #366が必要。公開JSONだけからRaw検証を省略して数値を生成しない。
Artifactを展開し、依存numpy=2.3.5、scipy=1.17.0の環境で、別の新規入力viewと新しい出力先を作る。

```bash
python /private-artifact/prepare_analysis_view.py --repo /repo --artifact /private-artifact --view /new-private-analysis-view
PYTHONPATH=/private-artifact/offline_guard OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python /repo/runtime/analysis/benter_second_stage.py --series closing --from 2026-10-11 --to 2026-11-01 --asof 2026-11-03 --root /new-private-analysis-view --out /new-output-closing
PYTHONPATH=/private-artifact/offline_guard OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python /private-artifact/measure_closing_indices.py /new-output-indices --repo /repo --root /new-private-analysis-view
```

500Rの判定手順はPR #365で取得前に固定済み。
`docs/BENTER_500R_PREREGISTRATION.md` を参照し、今回178Rの観測から判定基準・重みを変更しない。

# Workブラウザ取得と既存JRA BVI算定の接続

2026-10-10。実会員ページの観測から、`allsel → racesel?rdate=… → main.php?rcode=…`、競馬場別テーブル、`td`と2段ヘッダー（血統タイプW/P/S/T）、25列の出馬表を確認した。従来のMac収集器の発見・解析処理をこの構造に対応させた。テストは合成データだけを使用し、有料馬別データをGitHubへ保存しない。

Workの取得済みJSONをオフラインで処理できる。

```sh
python scripts/jra_bloodb_browser_bvi.py \
  --snapshot /PRIVATE/bvi-bloodb-20261011.json \
  --output /PRIVATE/bvi-audit/report.json
```

出力親ディレクトリは0700、ファイルは0600で保存する。stdoutは件数のみ。既存ファイルを上書きしない。認証情報やCookieは入力しない。このコマンドは外部サイトを取得しない。

接続の条件：同日・同場・同Rの署名SOURCEが一意に存在し、署名・本文ハッシュ・SOURCE文脈・全馬名／馬番・時点が照合できること。Blood-B取得時刻はSOURCE凍結以降、予測締切未満。署名済みSOURCEがなければ各馬BVIをnullとし、`MATCHING_SIGNED_JRA_SOURCE_MISSING`を記録する。0点・50点・独自血統評価による穴埋めは行わない。

算定は既存`compile_source_to_features`からJRA公式実測特徴だけを生成し、`evaluate_partial_production_base_indices`を使用する。`JRA-EVIDENCE-TO-BASE-MAPPING-v1.0-PRODUCTION-20260921`のカテゴリー点、profile別BVI重み、coverage閾値は変更しない。算式は既存のΣ（カテゴリー点×取得済み特徴重み）÷Σ取得済み特徴重み。閾値未達はBLOCKED。

Blood-Bの表示名、小系統、独自評価は私的sidecarへ保持し、JRA署名SOURCE、血統コーパス、Production Featureを変更しない。省略種牡馬名の推測展開はしない。

このレポートは計算診断でありProduction署名・Full20・Static成立の受領証ではない。独立SOURCE OIDC照合結果は別に報告し、BVI権限・Static権限・OOS加算を与えない。実会員閲覧できたことだけでBVI公式数値が成立するわけではない。

2026-10-11東京・京都の取得済みスナップショットに対する実検証：24レース344頭を解析。チェックアウトしたmain `fbb82654a8c77a8afb7b3e50a189d9af1cd13fd6`には対象24レースの署名SOURCEがなく、公式BVI値344件は未算定。取得内容は本リポジトリへ転送していない。

残る実行条件：対象レースの正式Race Intentとcanonical SOURCE取得・独立証人検証、SOURCE凍結後のBlood-B再取得、JRA血統母集団の必要標本、Production Full20閉包。必要条件未成立をソフトウェアのテスト成功と混同しない。既存Mac自動取得に関する提供元利用許諾の確認フローは維持する。

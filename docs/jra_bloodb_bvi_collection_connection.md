# 収集プログラムと既存公式BVI算式の接続

Candidate。Production算式・重み・Current Authorityの変更はない。

`jra_bloodb_signed_source_queue_sync.py` が生成する新しい署名SOURCEキューには
`calculate_bvi_diagnostic=true` を設定する。Mac会員収集器の `run_one` は取得成功後、
保存HTMLのSHA256を確認し、全馬・競馬場・日付・R・SOURCE凍結時刻・予測締切を
照合して既存 `compile_source_to_features` と
`evaluate_partial_production_base_indices` を呼び出す。
結果は私的収集ディレクトリの `bvi_diagnostic.json` へ保存する。
数値や会員本文はstdoutやGitHubへ出さない。

札幌・函館・福島・新潟・東京・中山・中京・京都・阪神・小倉に対応する。
Blood-B表示評価を公式特徴量に流し込まず、公式JRA SOURCE由来の特徴量だけを使用する。
SOURCE欠落・時点不一致・全馬不一致・取得形式不適合ではBVIをnullとし理由を残す。
収集の成功とBVI算定成立を区別し、BVI側がBLOCKEDでも取得済み原表を保持する。

Workブラウザーの収集JSONLをオフラインで接続する例：

```sh
python scripts/jra_bloodb_browser_bvi.py \
  --collection-jsonl /PRIVATE/raw_pages.jsonl \
  --output /PRIVATE/bvi_report.json
```

`kind=main` だけを取り込み、結果ページ・競走後の馬履歴は予測入力にしない。
同じURL・同じ原表の再取得は最初の観測時刻を保持する。原表が変化した複数捕捉は
勝手に選択せずBLOCKEDとする。署名SOURCEが複数候補の場合も自動選択せず、必要なら
`--source-index /PRIVATE/source_index.json` で実レースコード→署名SOURCEパスを指定する。
指定しても署名・レース・時点・全馬の検証を省略しない。

2026-10-11の実データ検証：保存済み14レース204頭のmain原表を解析し、
該当する署名SOURCE欠落を204頭すべてnullで報告した。数値成立の実績ではない。
合成テストでは既存カテゴリー点82/74と既存重み0.30/0.24による
加重平均の一致、全10場SOURCE選択、HTML改ざん拒否を検証する。

`bvi_authority=false` と `static_prediction_authority=false` を維持する。
公式算式の診断実行は、独立OIDC検証・Canonical SOURCE・Full20閉包・正式Freeze成立を
代替しない。過去レースの研究成績から正式予測や未知未来OOS実績を作らない。

# LOCAL AKI result-worker restart verification

2026-10-13 09:00 JST前の確認。最新main 0a477399b185d26b6aa20d44229455424f2d2848は日次JRA状態とpedigree cursorのみ変更。LOCAL Current Authority R51と数値利用境界に変更なし。

結果保存用archiveが次回Worker開始時に復元されない欠落を修正した。予測archive復元後、結果checkpointのarchive hash・全ファイルhash・許可パス・重複・既存immutable conflictを検査し、全検査通過後に復元する。初回未作成は正常。固定tar metadataとgzip mtime=0で、同じ証拠の再保存はbyte-identical。Prediction/SOURCE/PRE_KRS/KRS/FINALはcheckpoint対象外。

保存済みforward_evaluationを読む場合もRESULT Ed25519署名、artifact/receipt digest、race、FINAL/SOURCE/plan binding、保存精算との一致を再検査する。結果workerは新規KRS・実購入・本番昇格を行わない。

回帰170件成功。追加検証はfresh directory復元・二度目復元・byte-identical pack・既存ファイル競合・破損archive・未作成checkpoint・署名不正cached RESULT。結果そのものはまだ未公表で、実RESULT checkpointの外部証明は未成立。今日のMON/MOR/KAW/KNZ/NGY各1Rは凍結5件、すべて未発走WAITING、未知未来結果評価0件。12時JST開始の毎時結果処理予約は有効、確認時点実行履歴なし。

場別予測較正、未知未来での比較・性能検証、本番利用審査は引き続き未完了。全14場の技術接続成功はこの性能検証の代替ではない。

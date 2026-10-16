# 通常依頼の正式読み戻し手順

対象の発話は従来どおり「川崎○Rのケイバメトリクス調査願います」。この手順は新規Dispatch権限を与えない。

1. 指定日（省略時はAsia/Tokyoの当日）・Venue・Raceを公式Race Identityへ照合する。曖昧な日付を任意の過去成功Raceへ置換しない。
2. 最新main、Current Authority、KAW Owner、dated approval、固定公式day plan、day stateを読む。Discovery、Key登録、受付Intent、凍結Static入りFormal Intentを別々に表示する。
3. 既存のexecution_store/Canonical Artifactを当該実行IDで読む。SOURCE/FORMAL/RESULTのLATESTとmanifest整合を既存resolverで確認する。
4. FINALが存在する場合は既存Gateway verifier/terminal_stateとcanonical rendererで検証する。自己申告した公開鍵、保存済みのtrueだけ、別RaceのFINALを代用しない。検証操作が使えなければ署名検証未実施として保留する。
5. 検証済みFINALからCanonical買い目を原文のまま表示する。全点数・各Stake・総額・FINAL receipt SHA・artifact SHA・成立時刻を添える。新しい買い目を補完せず、発走後なら過去確定原本であると明示する。
6. 未成立の場合は登録状態、最初の未成立工程、期限、保存済みの原エラー、再開可否を回答する。未登録を成功に書き換えず、チャットから未公開Dispatchや未承認main書込みを試さない。
7. GitHub公開時刻・チャット表示時刻・通知provider応答・ユーザー到達確認を分けて記録する。到達の確認には同じFINAL SHA/内容hashと受領時刻が必要。ユーザーの既読を推定しない。

毎Raceの手動GitHub登録は主経路にしない。承認対象の登録/実行は既存Autonomous Dispatcher、チャットは状態照会/正本の読み戻しを担当する。次回日程/対象/公式計画が未承認なら、自律運転開始済みとは表示しない。

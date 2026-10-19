# 浦和の凍結済み参考予想

正式予測ではありません。各日の `index.json` と各Raceの
`RNN/manifest.json`・`RNN/readback.txt` を同一Raceとして読み戻します。
全馬、根拠、UNKNOWN、参考上位、展開、出典、凍結時刻、最終結論を含みます。

| 開催日 | 保存済みRace | 評価対象頭数 | 現在の公式再取得 |
| --- | ---: | ---: | --- |
| [2026-10-20](2026-10-20/index.json) | 12 | 131 | 未成立 |
| [2026-10-21](2026-10-21/index.json) | 12 | 139 | 未成立 |

本文は10月19日に生成した元の凍結表示とbyte一致します。公開時刻は
新しい予想生成時刻ではありません。取消・馬体重・オッズ等の当日更新を
確認したものとして扱わず、旧Snapshotへ結果後情報を混ぜません。

公開readerの検証範囲は
`PUBLISHED_PRESENTATION_ONLY_SOURCE_RAW_NOT_REVERIFIED` です。
本文SHA、Race Identity、全馬の名前と根拠、時刻、結論を照合します。
SOURCEの生HTML原本はこの公開配布物に含めず、readerは生SOURCEや
正式署名を再検証したとは主張しません。単独の実行モデルSHAは元原本に
存在せずUNKNOWNです。方式Component SHAとは区別します。

通常入口は `python -m runtime.local_race_entry --query
'2026年10月20日浦和7Rのケイバメトリクス調査願います'
--output /tmp/urw-readback --run-id readback --display` です。
検証済みSigned FINAL、現行正式Gate、保存済みREFERENCEの順序を保ちます。
公開表示物が壊れていれば新規生成で埋めずHOLDします。

このコード変更は通常ChatGPTへActionを自動インストールしません。
Venueチャットは、利用可能な正規Connectorで同一Raceのmanifestと本文を
実際に取得して回答する必要があります。CLI成功、保存成功、本文照合成功は、
ChatGPT画面表示・再読込保持・ユーザー受領の証拠とは分離します。

新規の無人SOURCE取得は `DATA_SOURCE_POLICY` が第一停止です。
2026-10-19のNAR robots確認では一般UAにTodayRaceInfoをDisallowしています。
許可された公式Feedまたは提供者の明示的許諾が確認されるまで、禁止対象の
カード・オッズGETを実行しません。保存済み本文の読戻しは継続できます。

URW Ownerの品質不合格、KAW限定Owner Scope、下流4Consumerの未認可、
日付別正式ActivationのGateは維持しています。REFERENCEをSigned SOURCE、
KRS、MEC、Capital、Signed FINAL、正式買い目、推奨PFSへ昇格しません。
現在の新規Formal実行、実購入、外部通知、恒常自律稼働は未実証です。

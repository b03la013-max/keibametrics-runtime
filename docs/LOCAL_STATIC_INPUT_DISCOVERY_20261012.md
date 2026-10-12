# LOCAL既存Static入力の自動探索 — 2026-10-12

利用者へ内部ファイルの保存先を尋ねる前に、実行入口が自らexact raceのcanonical Intentを探索する。新しいPrediction Ownerや係数を作る変更ではない。

## 調査で確認した現行経路

LOCALは、チャットで生成・凍結したStaticをFull Formal Intentとして外部Runtimeへ渡す既存経路を持つ。例: `runtime/formal_intents/KM-LOCAL-OHI-20261009-R04-LIVE-R2.json`。Staticには`CHAT-OWNED / RESULT-BLIND / R44-NUMERICAL-NO-PREDICTION-CONSUMPTION`が記録されている。対応する保存済みPRE_KRS、KRS、FINALを外部`/verify`で再検証しvalid/verified=trueを確認した。KRS実回数は5000。

これは過去の既存経路の実証であり、川崎8RのKRS/FINALや新モデルの性能を実証したものではない。C2 PR #124の未受入・API課金停止記録は、LOCALのこの既存Frozen入力経路の必須依存ではない。C2を必須条件のように利用者に提示してしまった説明を訂正する。

## 実装修正

- レース指定（LOCAL venue/date/race_no/post/cutoff）だけから安定execution_id/race_idを作成し、現行Authorityを解決して保存する。
- 明示Static、または`runtime/formal_intents/<execution_id>.json`の同一レースStaticを解決する。検索インデックスのヒット有無を不存在の根拠にしない。
- Family、Race ID、Venue/date/no、cutoff/post、全馬の重複なしranking、宣言済みSigned SOURCE参照を照合する。他レースのStaticや時間の異なる入力を借用しない。
- 見つからなければ、既存チャット所有入力に渡す`static_owner_input.json`を保存する。真正なSOURCE参照・全馬Universe・凍結Evidenceを含み、C2が必須ではないこと、数値の予測利用が未承認であることを明示する。新しいRankingは生成しない。
- 発走前期限を過ぎた場合は生成許可false、DEADLINE_HOLDとする。HOLDをNO_BETやSigned FINAL成功に変換しない。

## 一回の正式依頼を処理する担当側の手順

ユーザーにStatic/OwnerのGitHub保存先を調べさせない。担当側が、Current Authority・Venue Canon・公式Race Identity・post/cutoffを解決し、SOURCE-first入口を実行する。既存同一レースIntent/FINALがあれば真正なArtifactを読み戻す。Staticがなければ、発走前の真正な未知未来に限り、従来のチャット所有経路としてSOURCE凍結Evidenceと現行Canonを用いたStatic/roles/Pair/Thirdを担当側で作成し、完全Intentを凍結・保存して既存Formal入口へ接続する。

新モデル・新係数・新しい自律Ownerの採用とは区別する。未承認の29指数の予測/KRS/Ticket/Capital利用やJRA固有Static Ownerへの置換はしない。期限を過ぎたレースでは当時の未実行を保持し、後から正式事前Static/FINALを作らない。

## 川崎8Rの確定状態

18:21にSigned SOURCE取得・検証済み。12頭×29指数=348項目、計算306・規約中立42・未解決0。同一raceのFormal Intent/Staticはcanonical pathに存在しない。修正済み入口からIDやAuthorityの手入力なしでSOURCEを再取得せず読み戻し、全指数診断・Owner入力packetまで生成できた。最終停止は`DEADLINE_HOLD:FORMAL_INCOMPLETE`、最初の未成立工程はStatic Freeze。

正式FINALは未成立。C2を導入すればこの過去レースの正式事前予測を復元できる、という結論にはしない。

## 証跡

`evidence/local_static_input_discovery_20261012/` に既存チャット所有経路の署名再検証、実際のcanonical Static検索、川崎8RのID省略入口実行とOwner入力要約、201回帰testsのログを保存。Source/Production suite/Authority/Venue/係数/モデル/Capitalポリシーを変更しない。

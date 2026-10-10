# Blood-B 血統データ・Mac会員ブラウザ取得（2026-10-10）

**Status: PRE-INTEGRATION / PRIVATE DIAGNOSTIC / LIVE SUBSCRIBER HTML NOT VALIDATED / NO PRODUCTION BVI AUTHORITY**

対象：<https://www.blood-b.com/allsel>（ブラッドバイアス血統馬券プロジェクト）。未ログインでアクセスすると `/wp/login/` に移動することを公開Webで確認した。DataBuyer IDとパスワードは契約者本人が本人のMacの画面でのみ入力する。

同サイトの公開説明には「血統情報・人気ランク・相対指数・血統評価・血統タイプ・ローテ評価」「コース別ブラッドバイアス」がある。ただし、**亀谷独自の血統評価はJRA公式の実測産駒成績ではない**。公式BVI母集団は既存の `jra_pedigree_corpus.py` に残し、BloodBは別系統の補助説明変数・診断比較として取り込む。未観測数値を生成したり閾値を下げたりしない。

## 利用許諾・データ境界

有料会員であるだけでは、自動取得、大量保存、GitHub転載、モデル学習または第三者への再提供の許可が確認できたわけではない。**この目的と範囲についてblood-b.com提供者の許可を取得した場合にのみ、本収集器の `--provider-permission-confirmed` を指定して使う。** 利用規約が禁止している場合は起動しない。CAPTCHA、MFA、決済画面、パスワード入力の自動化、アクセス制限回避、会員アカウントのクラウド移転は行わない。問い合わせ先は同サイト公開の `support@blood-b.com`。商用・再配布用途は別途権利確認が必要。

## 1. Macの準備・本人ログイン

```sh
git clone https://github.com/b03la013-max/keibametrics-runtime.git
cd keibametrics-runtime
python3 -m venv .venv
source .venv/bin/activate
python -m pip install playwright beautifulsoup4
python -m playwright install chromium
python runtime/jra_bloodb_mac_collector.py login
```

専用Chromiumが開く。ご自身でDataBuyer認証し、 `/allsel` の会員内容が閲覧できることを確認してEnter。専用の認証プロファイルは `~/.keibametrics/browser_bloodb` に格納（mode 0700）。ChromeやSafariの既存プロファイルに直接接続したりCookieをGitHubへアップロードしない。

## 2. 会員ページのHTML構造確認（許可取得後）

```sh
python runtime/jra_bloodb_mac_collector.py inspect \
  --race-url https://www.blood-b.com/allsel \
  --provider-permission-confirmed
```

`inspect` は表の行数と見出し名だけを端末へ出力し、馬別の有料データ本文は出力しない。**公開ページでは実際の会員HTMLのテーブル構造を検証できていない**ため、ここでの結果によって実サイトのセレクタの修正が必要な場合がある。勝手にログイン画面を抽出成功と判定しない。

公開の出馬表レースリンクには例として `https://www.blood-b.com/main.php?rcode=2026080901010601` という形式がある。実際の会員ページから取得した**正しいレースリンクのみ**指定する。レースIDを作り出したり他レースへ流用しない。

## 3. 限定されたレースだけ保存する（許可取得後）

まずJRAの**正式署名済みSOURCE**を検証し、出走馬一覧をMacの私的領域へエクスポートする。例の `official_runners_path` は外部で署名検証済み・馬番／馬名の照合済みである必要がある。**JSONを書いたというだけでは署名されたことにならない**。

```json
{
  "race_id": "KM-JRA-KYO-20261011-R01",
  "race_date": "2026-10-11",
  "prediction_cutoff": "2026-10-11T09:15:00+09:00",
  "bloodb_race_url": "https://www.blood-b.com/main.php?rcode=ACTUAL_RACE_LINK",
  "official_runners_path": "/Users/YOU/.keibametrics/kyo_r01_official_runners.json"
}
```

URLの `ACTUAL_RACE_LINK` は**実際の16〜20桁程度の数字**へ置き換えること。上記は例示であって実在レースに対応するURLだと主張していない。

```sh
python runtime/jra_bloodb_mac_collector.py capture \
  --spec ~/.keibametrics/bloodb_race.json \
  --provider-permission-confirmed
```

取得成功時だけ `~/.keibametrics/private_bloodb/<race_id>/` にDOM HTML、SHA-256、独立出走馬照合済みの診断JSONを原子的に保存。出走馬を1頭でも照合できなければ、認証画面へ飛ばされたら、締切後なら、同一馬が重複すれば失敗として記録し、Production指数へは送らない。

## 完成していない重要事項

- 既存会員アカウントでの**本物の取得成功**は未確認。CIは実サイト会員情報に一切触れない模擬HTML試験だけ。
- `/allsel` は会員メニュー／集約表示の可能性がある。レース単位の正しいリンク発見と、公式レース識別子への対応づけを実観測して実装する必要がある。
- 実際の有料表がHTMLの `table/th/td` でない場合は、現行の保守的パーサでは **FAIL CLOSED**。取得できたふりをしない。DOM見出し確認後にパーサを更新する。
- 診断ラベルとJRA産駒コーパスは別ソースであり、BloodBの独自評価がBVI公式数値へ自動変換されることはない。数値的利用は情報源契約・時点証明・モデル係数の独立検証が揃ってから。
- Macの電源・起動・ログイン更新は本人管理。現在は**明示したURLのみ**のローカル収集で、全レース自動巡回・launchd統合はまだ存在しない。

## 証拠の意味

`raw_sha256` は**保存したブラウザHTMLバイト列**の完全性のみを示す。提供元が電子署名したとの意味ではない。正式JRA SOURCEのEd25519/OIDCとは別のtrust domain。スクレイピング自体はBVIの欠落する実走サンプルの捏造やStatic認可を解決しない。

## 4. Mac自動レース発見・5分間隔の会員データ収集

これまでの単一レース収集に加え、認証済み /allsel に**実際に掲載されたレースリンクのみ**を抽出し、日付・レース番号・開催場を照合する queue ワーカーを実装した。rcodeを生成・推測しない。複数開催場で同じレース番号がある場合、開催場のラベルが明瞭でなければ停止する。これは模擬HTMLのテストであり、実会員ページのDOMやライセンス条件を確認した証明ではない。

契約者のMacに ~/.keibametrics/bloodb_queue.json を置き、正式JRA SOURCEから導いたレース情報を配列で登録する。例:

~~~json
[
  {
    "race_id": "KM-JRA-KYO-20261011-R09",
    "race_date": "2026-10-11",
    "race_no": 9,
    "venue": "京都",
    "prediction_cutoff": "2026-10-11T14:00:00+09:00",
    "signed_source_envelope_path": "/Users/YOU/.keibametrics/jra_signed_source_envelope.json"
  }
]
~~~

上記日付・締切は動作説明用で、実レースの証明ではない。signed_source_envelope_path は署名済みJRA SOURCEと一致する必要がある。埋込Ed25519の検証だけでは第三者OIDCを証明せず、SOURCEの外部証跡は別ゲートで確認する。代替として official_runners_path が使えるが、これは非署名Diagnostic照合情報と明示される。

提供元からの自動利用許可を確認した場合のみ、次の順で本人のMac上で実行する。

~~~sh
python runtime/jra_bloodb_mac_collector.py login
python runtime/jra_bloodb_mac_automation.py discover --queue ~/.keibametrics/bloodb_queue.json --provider-permission-confirmed
python runtime/jra_bloodb_mac_automation.py queue --queue ~/.keibametrics/bloodb_queue.json --provider-permission-confirmed
python runtime/jra_bloodb_mac_automation.py install-launchd --queue ~/.keibametrics/bloodb_queue.json --provider-permission-confirmed
~~~

macOS launchd により約5分間隔で実行。締切まで65分以内の対象だけ取り込む。Macがスリープ中・オフライン・認証失効・契約範囲外の場合は成功とみなさない。保存は ~/.keibametrics/private_bloodb/<race_id>/ だけで、ログイン情報・生HTML・有料評価をGitHubやCIへアップロードしない。止めるには launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/jp.keibametrics.bloodb-collector.plist を実行する。

現時点の未完了条件: 実会員HTMLのセレクタ実測、ローカルGitHub SOURCE同期の実運用検証、血統評価の実指数化・較正、Production Full20/Staticの認可。キュー取込は独自Blood-BラベルをDiagnosticで保持し、JRA実績ベースの血統コーパス・正式Predictionと混合しない。実会員取得と本番接続をテスト済みと主張しない。

## 5. JRA正式SOURCE → Blood-Bキューを自動生成する実装（2026-10-10）

旧方式の手動JSONキュー作成は必須ではなくなった。MacにGitHubリポジトリの最新runtime/executions（各正式レースのSOURCE受領証）とruntime/jra_formal_intentsがある場合、scripts/jra_bloodb_signed_source_queue_sync.pyが未来36時間のFORMAL-PRE-RACEから有効なものだけを選び、同じexecution_idのEd25519署名SOURCEを検証してキューへ登録する。欠測SOURCEのレースは明示してスキップ。Blood-Bの有料会員ページへはアクセスしない。

~~~sh
git pull --ff-only
source .venv/bin/activate
python -m pip install cryptography beautifulsoup4 playwright
python scripts/jra_bloodb_signed_source_queue_sync.py --dry-run
python scripts/jra_bloodb_signed_source_queue_sync.py
~~~

キューの初期実行・CIとも、SOURCEの外部GitHub OIDC証人をローカルで再照合する工程ではない。SOURCE受領証自体のEd25519署名とSOURCE本文ハッシュ、race_date、venue_id、race_no、正式cutoff、署名時刻を再検証する。SOURCEに対応する正式Race Intentのないレースは採用せず、期限超過分を未来レースへ付け替えない。JRA正式Productionへの接続は既存の独立OIDCゲートによる別の権限確認が必要。

前節で設定したlaunchdは、登録済みリポジトリのスナップショットを対象に5分間隔でこのキュー同期を実行してから（許可済みであれば）Blood-Bの会員情報を3レース以内で取得する。**自動git pull・JRA全レースの自動起動を無条件に行う仕組みではない。** GitHubのmainを最新にし、発走前の正式SOURCE受領証がMacに存在することが必要。

実会員ページ確認は、提供元が当該自動利用を許可していることを確認後、`python runtime/jra_bloodb_mac_collector.py login` で本人ログインしたうえで、`python runtime/jra_bloodb_mac_collector.py inspect --provider-permission-confirmed` を実行する。表見出し・行数だけが出力され、馬別有料情報・ID・パスワード・認証Cookieは出さない。取得失敗、会員DOM非対応、利用許諾未確認を理由に不正なProduction BVI・OOS・Finalへ自動昇格させない。

## 6. 次工程：Mac実会員1レースのローカル受入（2026-10-10）

新規の `runtime/jra_bloodb_mac_acceptance.py` は、PR #205で正式SOURCEから生成したキューの**指定1レース**を対象に、「実会員ブラウザ取得→HTML/SHA再照合→全馬の馬名・馬番照合→SOURCEハッシュ照合→締切前取得の判定」をMac内だけで行う。CIは模擬HTMLとテスト用Ed25519 SOURCEを使い、**実会員サイト取得済みとは主張しない**。

手順：Macの最新mainを取り込み、本人のログインセッション・提供元の自動利用許諾があることを確認する。受入コマンド実行にはSOURCEをMacに同期しておく必要がある。

~~~sh
git pull --ff-only
source .venv/bin/activate
python -m pip install -q beautifulsoup4 cryptography playwright
python -m playwright install chromium

# 利用規約・許諾未確認でも可能。SOURCE署名と今後36時間の対象確認のみ。
python scripts/jra_bloodb_signed_source_queue_sync.py --dry-run
python scripts/jra_bloodb_signed_source_queue_sync.py

# 以下のinspect/liveは提供元がこの目的の自動アクセス・保存を許可した場合だけ実行
python runtime/jra_bloodb_mac_collector.py login
python runtime/jra_bloodb_mac_collector.py inspect --provider-permission-confirmed

# 対象の正式race_idはdry-run/queueから実在値を指定。下記は書式例。
python runtime/jra_bloodb_mac_acceptance.py live \
  --race-id KM-JRA-KYO-20261011-R09 \
  --provider-permission-confirmed

# ブラウザ接続なし。締切後でもローカル保存物の完全性を再検査可能
python runtime/jra_bloodb_mac_acceptance.py status \
  --race-id KM-JRA-KYO-20261011-R09
~~~

`live` が出す結果は `LOCAL_CAPTURE_ARTIFACT_INTEGRITY_VERIFIED` であり、次の内容を**公開せず**ローカルに検査する。

- 元SOURCEのEd25519受領証とSOURCE本文、対象競馬場・レース日・レース番号・締切を再検証
- 対象SOURCEをMacで検証した時点のJRA全馬集合と血統診断保存馬の完全一致（馬名と馬番、重複ゼロ）
- 保存済み有料HTMLのSHA-256とsummary・bindingの一致
- SOURCE凍結より前にBlood-Bを取得したような時刻矛盾、締切後取得、別レース混入を拒否
- 生HTML、有料馬別評価、Cookie、ID・パスワードは端末出力、GitHub、CIへ転送しない
- Local Captured Dataは正式SOURCEと同一trust domainではない。提供元電子署名も第三者OIDC検証も本コマンドでは成立しない

`status` はブラウザ・Blood-Bサーバーへアクセスしない。事前に`live`または既存workerで取得した `~/.keibametrics/private_bloodb/<race_id>/` がなければ失敗する。 `live` も締切後、権限不明、ログイン切れ、レースリンク曖昧、表解析不可ならFAIL CLOSEDする。

**未了の必須実証：** 会員契約者のMacで許可済みの実ページに対して `inspect` と `live` を実行し、当該レースの表ヘッダーと全馬照合を確認すること。現在はこの実会員Acceptance未実施。実ページのDOMが既存パーサと異なる場合は、端末に有料本文を出さずヘッダー・行数等のみでセレクタ修正を行う。許諾の有無をフラグが技術的に証明するわけではない。

**Production境界：** `LOCAL_CAPTURE_ARTIFACT_INTEGRITY_VERIFIED` はあくまでMac上のData Integrity結果。JRA公式血統BVIを置換しない。Unknown OOS加算、買い目、KRS、STATIC、FINALに影響させない。次の昇格は提供元の利用許諾確認とJRA独立OIDCゲート、時系列純度、正確な実HTML解析の実証、血統信号の未知未来OOSの順序を守る。

## 7. 次工程：Mac実会員DOMのプライバシー保持Probe（2026-10-10）

PR #206の`live`受入試験は厳格に失敗する設計であるため、実サイトのHTMLが未確認の段階では、失敗原因を実会員情報やスクリーンショットを転送せず調べる必要がある。今回 `runtime/jra_bloodb_mac_probe.py` を追加した。

**提供元から会員ページの当該自動閲覧・構造検査について許可を得ている場合のみ**、Macの専用プロファイルで本人ログインした後、次を実行する。事前にPR #205のSigned SOURCE Queueが生成されている必要がある。

~~~sh
git pull --ff-only
source .venv/bin/activate
python scripts/jra_bloodb_signed_source_queue_sync.py --dry-run
python scripts/jra_bloodb_signed_source_queue_sync.py

# 本人ログイン（未実施なら）
python runtime/jra_bloodb_mac_collector.py login

# 実際のキュー内の未来Race IDを指定する。下記は形式例であり、
# 有効なSOURCE・会員ページを有することを示すものではない。
python runtime/jra_bloodb_mac_probe.py \
  --race-id KM-JRA-KYO-20261011-R09 \
  --provider-permission-confirmed
~~~

Probeは署名付きJRA SOURCE、日付・場・レース番号・全馬集合・発走前cutoffを再確認し、会員`/allsel`から**実際に表示されているリンク**のみを探索する。レースの数字を生成・推測しない。

出力は、index/detailそれぞれのテーブル数、行数、`th/td`件数、列見出し（最大数・長さ制限、馬名を含む見出しはREDACT）、`div/span/iframe/script`等の構造件数、実際のレース候補数、全馬照合の**件数**、失敗理由だけ。**HTML本文、有料の馬別値、馬名一覧、認証Cookie、パスワード、会員ID、具体的な会員レースURLは出力・永続保存しない。** 出力された構造情報は人がレビューできるが、その構造が有料サービスのライセンス条件上共有可能かは別途確認する。

成功時の`LOCAL_MEMBER_DOM_SCHEMA_COMPATIBLE`は**画面構造と既存パーサが1レース全馬分で一致すること**のみを意味する。会員情報の収集・永続化はしない。正式なローカル収集受入は前節の`jra_bloodb_mac_acceptance.py live`で別途行う。

- `BLOODB_RACE_LINK_MISSING_OR_AMBIGUOUS`：会員indexから場・日・Rが一意に見つからない。見える表・ドロップダウン・script/iframe構成を確認し、実サイト固有の発見方法を修正する
- `BLOODB_RUNNER_COVERAGE_UNVERIFIED`：表形式・馬名列・全馬が現行パーサの前提と合わない。構造診断だけで原因を分類する
- `BLOODB_LOGIN_REQUIRED`、`...REDIRECT`：本人認証・画面遷移・権利条件を確認する。認証バイパスしない
- `BLOODB_PROBE_PREDICTION_CUTOFF_EXPIRED`：締切後には発走前Probe成功を主張しない
- `BLOCKED`：実会員HTMLや許可未確認の段階では本番成功ではない

CIは署名付きJRA SOURCEテストフィクスチャと合成HTMLでProbe出力・全馬一致・動的div非対応・リンク不在・ログイン失効・レース取り違え・cutoffを確認する。実会員DOMが実証済みという意味ではない。Probeは`production_authority=false`、`bvi_authority=false`、`oos_increment=0`固定で、BVI/Static/KRS/FINALへ干渉しない。

**次の実証は、提供元が許諾した範囲で契約者のMacからProbeを1レース実行し、出力された構造診断だけでparser対応を判断すること。** 現時点でこの実行は未実施。

## 8. Mac Last-Mile Readiness（2026-10-10）

macOSの端末で本人のプライバシーを保護しながら「実運用の残り障害」を確認するコマンドを追加した。GitHub CIがPASSしたからといって有料会員画面を実際に読めたと誤判定することを防ぐ。

~~~sh
cd ~/keibametrics-runtime
git pull --ff-only
source .venv/bin/activate
python scripts/jra_bloodb_mac_readiness.py
~~~

JSON出力はMac環境、必要パッケージ、専用ブラウザのフォルダ存在、署名SOURCE関連キューの状態（将来レース件数のみ）、launchdファイルの有無を示す。これは**オフライン検査**であり、プロファイルが存在することと「実際にBlood-Bへログインできている」ことは同義ではない。また許諾や実会員DOMの適合を技術的に証明するコマンドではない。

### 残りの現実世界の受入条件

1. サイト運営者からこの自動閲覧・ローカル保存用途の許可があること（契約の有料会員であることだけでは証明不能）
2. Macで本人がDataBuyer IDへログインしていること。パスワードや認証CookieはChatGPT、GitHubに渡さない
3. Macに未来レースの正式JRA SOURCE受領証とRace Intentが同期されていること。SOURCEそのものがなければ私的Blood-Bキューは作られない
4. 許可を得た範囲で `jra_bloodb_mac_probe.py` を対象1レースで実行し、実際の見出しと全馬一致を確認すること
5. `jra_bloodb_mac_acceptance.py live` で取得とハッシュ照合に成功すること。その後もProduction BVIと混ぜずDiagnosticで保持すること

「readinessに未完了がある状態」「実会員HTMLを取得できていない状態」では**会員サイト自動取得の完成を認定しない**。コンポーネントのCIテストだけは既に通過しており、実運用の最後の一段がどこかを数値的に表示するためのチェックである。現時点でMacの実機操作はChatGPTから実行されていない。

## 9. Mac最終受入：オペレーター1コマンド統合（PR #213後続）

PR #213のオフライン診断に加えて、既存の正式SOURCE署名検証、キュー同期、
将来レース選択、会員DOM Probe、取得、全馬・SHA・時点・出典の再照合を
一つのローカル実行へ接続した。これは**Mac内の有料データ診断取得**であり、
モデルのProduction昇格やJRA独立OIDC attestationは一切発行しない。

まずMacでコードを更新し、認証済みプロファイルを準備する。利用条件は本書冒頭と同じ。
自動閲覧・保存への提供元許諾が確認できている場合に限り、次を実行する。

~~~sh
cd ~/keibametrics-runtime
git pull --ff-only
source .venv/bin/activate
python scripts/jra_bloodb_mac_final_acceptance.py offline
python scripts/jra_bloodb_mac_final_acceptance.py live --provider-permission-confirmed
~~~

`offline` はサイトへ接続せず、未来レースの公式署名SOURCE候補を確認する。
`live` は同期済みの有効SOURCEをもつ未来のレースから締切65分以内で最も早い1件を
自動選択する。既存の`--race-id KM-JRA-KYO-YYYYMMDD-RNN`で正確な1レースも指定可能。
認証済みMacブラウザと提供元許可が必須で、ID/Cookie/生HTML・有料馬別値は
GitHubやChatGPTへ出さない。会員DOMの構造照合失敗・ログイン失効・出走馬不一致
・締切切れ・SOURCE署名不整合は`BLOCKED`で終了する。

正常終了時の`MAC_LOCAL_BLOODB_ACCEPTANCE_VERIFIED`は
「指定レースの会員表示をローカル取得し、保存物をSOURCEと照合できた」という意味に限定する。
無権限での自動実行・事後時点書換え・正式BVI/Static/KRS/FINALへの自動流入を許可しない。
会員許諾・本人ログイン・実DOM確認はMac側でのみ成立する受入要件のままである。

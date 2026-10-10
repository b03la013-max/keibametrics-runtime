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

現時点の未完了条件: 実会員HTMLのセレクタ実測、全レースからの自動キュー生成、血統評価の実指数化・較正、Production Full20/Staticの認可。キュー取込は独自Blood-BラベルをDiagnosticで保持し、JRA実績ベースの血統コーパス・正式Predictionと混合しない。実会員取得と本番接続をテスト済みと主張しない。

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

# Phase 0.6 確定オッズ系列（CODEのみ、外部取得未実行）

本番SOURCE・autopilot・delivery・postresultには接続しない。Ownerの個別承認、現行robots.txt・利用条件の確認後にだけ、独立した手動Workflowを使用する。本PRの作成・CI成功は取得実行の承認ではない。今回、WorkflowもJRAへのHTTP取得も実行していない。

## リポジトリ内で確認できたこと

`runtime/jra_source_runtime/jra_same_day_results.py:parse_result_detail` は成績を解析するが、全頭の単勝価格を出力しない。`tests/test_jra_same_day_results.py` の保存fixtureには着順・馬番・通過順等があり、全頭の価格列はない。既存のRESULT JSONは公式成績URLとRaw SHAを持つ一方、Raw HTMLと全頭確定オッズを残していない。人気順位・勝ち馬の単勝払戻から他馬の価格は復元できない。

従って「現在の成績ページに全頭確定オッズがある」とは、この保存資料だけでは断定できない。実ページの現在の表構造はOwner承認後の取得で確認する。合成fixtureの成功を実JRAページの受入成功と呼ばない。

保存済みの `runtime/diagnostics/NKY-20260927-payout-links.json` と `NKY-20260927-postrace-review-probe.json` に、成績ページから公式の確定オッズへ進むRace固有のリンクがある。取得先は **https://www.jra.go.jp/JRADB/accessO.html**。POSTの`cname`はその都度公式ページに実在する値を使う。保存例（中山2026/9/27 3R）は `pw151ouS306202604090320260927Z/15`。汎用メニュー`pw15oli00/6D`と区別し、末尾チェック値やRaceトークンを推測・合成しない。

## Readerと保存形式

`runtime/analysis/closing_odds_reader.py`は純粋なHTML Reader。開催日・場・Race番号の一意なヘッダー、見出し／caption／titleでの明示的な最終／確定オッズ又は成績表示、単勝価格列、全Active集合を照合する。Navigationやリンク先ラベルの「最終オッズ」「レース結果」は確定性の根拠にしない。人気だけの表、払戻表、出馬表の時点価格を確定オッズへ格上げしない。未知の表構造、複数候補、全頭価格不足はHOLDする。

同着馬は両方Activeとして残す。取消・除外は正式RESULTと照合して取り除き、中止・失格は出走した馬として残す。全角数字をNFKC正規化する。`---`はActive価格として拒否する。`999.9`は表示上限として保存し、元の正確な超過価格を推定しない。人気が公表表から取得できなければNULLを保持し、同額価格の並びから順位を推測しない。

保存先は`runtime/closing_odds/<race_id>.json`。署名や正式SOURCEは作らない。

| 項目 | 内容 |
|---|---|
| schema / classification | JRA_CLOSING_ODDS_RESEARCH_V1 / OFFLINE_RESEARCH_ONLY_UNSIGNED |
| race_id / captured_at / url | 対象ID、応答取得後の実UTC時刻、公式URL |
| request_cname | 実ページで観測したPOSTトークン。認証情報を含めない |
| raw_html_base64 / raw_sha256 | 正確なHTMLバイト列とSHA256 |
| content_type / encoding | 明示的な文字コード。置換文字による救済はしない |
| parsed / parsed_sha256 | 全頭価格・人気・取消除外の解析結果とSHA256 |
| capture_sha256 | hash欄以外のcanonical JSON全体のSHA256 |

同一Filesystem内のtemporary fileをfsyncし、hard linkで新規公開する。既存ファイルがあれば競合時も上書きしない。再読込み時はRaw SHA、解析結果SHA、全体SHAに加え、Rawの再解析とRace／Active集合を再照合する。通常のGit commitやWorkflow concurrencyをExactly Once送信保証と呼ばない。本機能はメール送信を行わない。

## 手動Workflowの安全策

`.github/workflows/km-jra-closing-odds-manual.yml` は`workflow_dispatch`のみ、既定はローカル計画表示。schedule・push・PR起動なし、`contents: read`、checkout認証永続化なし。Owner承認記録とrobots／規約レビューの入力が全てある場合だけ`--execute`を渡す。これらは操作者の申告であり、Owner署名の暗号検証やGitHubの保護Environmentによる承認を実装したものではない。

取得時はrobots.txtをまず取得し、各URLのcan_fetch、crawl-delay、request-rateを適用する。最低5秒を**各HTTP要求**の間に空ける。robots取得失敗、禁止、未知の文字コード、リダイレクト、非200応答は停止。許可先はHTTPSの`www.jra.go.jp`の限定パスのみ。Cookieは匿名セッションのRAMだけに保持し、認証情報を使わず、ログ・Artifactへ出さない。取得上限は既定300要求、最大500、タイムアウト120分。Day単位のNavigationは再利用し、正常な他Raceの処理は継続する。

失敗した最終応答Rawは`runtime/closing_odds_rejected/<実行時刻>/`へ別保存する。これは適格価格ではない。部分失敗はexit 1とし、SUCCESSに隠さない。既存captureは再取得せず、独立分析で検証する。成功・失敗の研究JSONは30日Artifactに保存し、mainやブランチへの自動書込みはしない。永続保存する場合はArtifactを確認し、元パスへ復元する個別の作業が必要となる。

実行前にOwnerが確認する事項：対象期間・最大要求数、JRA利用条件／robotsへの適合、研究Rawの保存・再配布範囲、GitHub Actions利用枠内の費用。新規有料Providerは使わない。robotsの許可だけで著作物の再配布許諾が得られたとは判断しない。

## オフライン更新コマンド（例示のみ、今回は実行しない）

Phase 0と修正版0.5は、diagnosticsの1コマンドで同じ新規asofへ出る。11/7〜11/8の結果保存後の例：

```bash
python runtime/analysis/benter_index_diagnostics.py --from 2026-10-11 --to 2026-11-08 --asof 2026-11-09 --out runtime/reports/benter_second_stage/2026-11-09-phase06
```

Owner承認後に取得・保存された確定オッズを比較する場合のみ、別の新規出力先で追加実行する。HTTPは行わない。

```bash
python runtime/analysis/benter_second_stage.py --series closing --from 2026-10-11 --to 2026-11-08 --asof 2026-11-09 --out runtime/reports/benter_second_stage/2026-11-09-closing
```

`--series closing`でも主系列summary.json／ledger.csvは変更せず、比較は`closing_comparison.json`・`.md`・`ledger_closing.csv`へ追加する。価格がない現状は0R。比較時のM ρ²・Δρ²・95%区間・シャッフル95%点は、両系列で全く同じRace集合・時系列分割を使う。過去の市場締切時刻は未観測であり、後日取得のcaptured_atを締切時刻へ遡及しない。

旧Phase 0計算器は`_benter_second_stage_legacy.py`へ**バイトを変えず**移し、既存公開APIと既定CLIはそれへ委譲する。calculator SHAは元の`d1e24264…`を保つ。追加モジュールのSHAは比較JSONに別記する。同じ環境・入力・seedで既定出力と旧計算器出力がバイト一致することをテストする。過去の別CPUホストとのビット同一性を意味しない。

累積200Rを超えた更新では、Δρ²の95%区間下限が0を超えるか、開催日WF累積が同じ方向か、市場βが不自然に縮んでいないかを合わせて確認する。確定系列が揃った場合は同一集合で観測時点の感度も比較する。178Rの点推定だけで指数の順位や重み採用を判断せず、500Rで同じ事前仕様を再検証する。自動スケジュール化は別承認とし、このWorkflowには加えない。

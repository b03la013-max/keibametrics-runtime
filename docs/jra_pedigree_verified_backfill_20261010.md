# JRA血統コーパス実収集・時点証明・BVI閉鎖 運用記録（2026-10-10）

## 目的と範囲

血統名だけで指数を埋めるのではなく、JRA公式の競走馬ページから父・母・母父・過去走実績を収集し、種牡馬や母父の**時点別産駒母集団**を作る。2026-10-10に確認したProduction Base13は京都9Rで199/208計算セルだが、Full20完全成立はゼロ。**それ以前の予測結果を後から書き換えない**。

## 作成・実装

- `runtime/jra_source_runtime/jra_pedigree_harvest.py`：公式サイト限定・robots許容・逐次低負荷取得・外部リダイレクト拒否・HTML親族セルの実態に合わせた解析。HTTP 502/503/504のみ限定再試行。403/429では回避せず中止。最大3レース単位で逐次取得・取得失敗を明示。父/母のない馬に値を捏造しない。
- `runtime/jra_pedigree_corpus.py`：旧実装の任意の `official:true` を拒否。JRA旧SOURCEはEd25519/ハッシュ/レースIDを再検証。旧SOURCEのOIDCは原取得時の上流ワークフロー検証に依存し、コーパス読込時の全件独立再検証はしていない（必要ならsource_attestation_verifierを渡してfail-closed検査できる）。ハーベストも実際にGitHub Actionsの承認済み収集ワークフローが署名したファイルだけを採用。予測締切後のハーベストや予測対象レースは除外。
- 同名馬の誤結合防止：名前＋父＋母のトリプルをsha256に変換して同定。産駒数と過去走数は別々に数える。矛盾する同一条件・同日過去走は後勝ち上書きせず除去する。サンプル不足は元の規則通り不足のまま。
- `runtime/jra_source_to_evidence_features.py`：対象レースの父・母父に関連する母集団だけを読み込む。検証失敗数を検証レポートに記録。
- `.github/workflows/km-jra-pedigree-verified-backfill.yml`：過去日付を3レースずつ取得、実測の一致と内容ハッシュを検査、GitHub OIDCで出力ファイルを署名し、同じ署名を再検証してからコミットする。前回の最後の位置を `runtime/pedigree_backfill_cursor.json` で記録。火・木・土に稼働予定。GitHub Actions runnerが実際に動作しネット接続があることが前提。競馬番組がない日、503継続、サンプル欠落、署名失敗は**完了したことにせず停止**。
- `.github/workflows/km-jra-pedigree-corpus-harvest.yml`：現行の開催日向けも少数バッチ・署名付与へ変更。
- `tests/test_jra_owner_authorized_rules.py`など：真正なEd25519テスト署名、改ざん拒否、未来観測拒否、同名馬衝突、実ページ解析、レース窓と中断・再開を検証。

## 外部検証の区別

低負荷の実サイトSmokeは **GitHub Actions 38040909151 PASS**。2026-10-04のJRA公式競走馬情報で、実際に3頭・過去走7件の取得を確認。以前の失敗は多重巡回による503と親族マークアップの解析不備。これは取得機能の実証であって全国コーパスの完成、Production Full20、未知未来での的中や回収率改善の証明ではない。

**重要な時間の境界:** 2026-10-10以降に採集した2024年の過去走データは、2026-10-10以降に行う新しいレースの評価資料になりうるが、2026-10-04の「事前予測OOS」の証拠に使ってはいけない。履歴診断の比較ではバックフィルを物理的に除外した旧SOURCE条件を保持する。

GitHub Actionsの署名の正しさはGitHub OIDC/Sigstoreを信用するが、JRA自身の公開鍵でJRAが個々の血統ページへ署名していると主張しない。ホスト制限・入力HTMLパーサ・取得時刻・SHA256・生成ワークフロー署名という異なる証拠を区別する。

## 残存条件

1. バックフィルが歴史的データを実際に取得・保存すること。**コードが存在することは収集完了ではない**。
2. 同じ出走馬の父・母父について必要な産駒数が集まり、既存BVI規則の最小観測件数を満たすこと。
3. 新馬のPRI/CSI/GCI/RFI、馬体重未発表、調教・コメント等の、BVI以外の指数不足を解消すること。
4. Current Authority R44の独立Static Ownerは未承認。今の補完作業でProduction昇格は行わず、実競走で適格なOOS検証を経ること。
5. 公開リポジトリへの大規模な実績データ蓄積について、利用者がJRAサイトの利用条件・転用範囲を確認し、必要なら私的なリポジトリ／保管先に切り替えること。生HTMLは保存せず構造化された事実・参照SHAを保持。

## 手動で対象日を指定

GitHub Actionsの `JRA Official Pedigree Backfill (Verified)` を `workflow_dispatch` で起動し、`date`に過去の日付、`start_race`に0,3,6,...を指定できる。手動の探索実行は定期カーソルを勝手に進めない。Macローカルなら同じ収集器で `python runtime/jra_source_runtime/jra_pedigree_harvest.py --date YYYY-MM-DD --mode results --start-race 0 --max-races 3 --delay 1.3 --out-dir PRIVATE` を実行できるが、そのままではGitHub OIDC署名済みとは見なされずProduction BVIへ自動混入しない。

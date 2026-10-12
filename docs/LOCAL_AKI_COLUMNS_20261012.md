# LOCAL AKI列選定 — 実装・検証報告（2026-10-12）

**判定：実装候補・Replay検証済み／外部実行未成立／Production昇格不可。**

これは完成したProduction機構の報告ではない。新規の実KRS、署名FINAL、未知未来OOS、全14場の実証は未成立。実購入権限は常にfalse。

## 正本の解決

着手main：`d00238d6b6e9281672a7f0ef2e2363b7899b0331`。FamilyはR51、LOCAL共通v4.13 Rev.1、情報源v1.10、Suite R16、29指数・63構成規則、KRS v1.7 Rev.1／Engine1.1.0／未較正parameter_map、MEC R3、現行Capitalを解決した。添付v4.12 Rev.3等は継承元であり、現行正本を巻き戻さない。

R51 LOCALの`numerical_consumption_boundary`はPrediction／KRS／Ticket／Capitalすべてfalse。数値式のProduction成立と下流予測の昇格を区別する。BANは独立Familyで、本機構は拒否する。PR #257はMERGEDであり、複数Intent、短い事前Jobと独立RESULT Job、Receiptを上書きしないGit競合処理を継承する。

## 中央版との対応

指定されたJRA4モジュール・2registryを確認した。

| 移植する手法 | LOCALでの実装 |
|---|---|
| SOURCE・Universe・全指数の依存関係 | 29指数の正式materializerを使用。SOURCEと出走馬集合を照合 |
| W／P2／P3を別々に選定 | ZAI-WIN／ZAI-PLACE／T3I-L。中央の指数名・Full20を流用しない |
| MAIN／追加候補を別記録 | 観測適格な最高役割得点群をMAIN、連続したAKI連動得点差内を追加候補 |
| 軸リスク・列ズレを独立評価 | Wはmax(W-AKI,100-ASI)、P2/P3はmax(列AKI,RSI)。相関したリスクを加算しない |
| 再計算・MEC・署名束縛 | PRE_KRS前と券面後にSOURCEから29指数を再materialize。候補選定と候補MECのhashをFINAL traceへ結ぶ |
| 未観測情報と権限の保持 | missing=trueは肯定根拠に数えない。数値中立を能力・購入信頼度として扱わない。PAPER限定 |

JRAの係数、normalized gap閾値、dispersion floor、支持得点閾値、固定頭数、NEWCOMER政策、外部変動帯は移植していない。中央版の署名済み正式実行結果との全件照合は未完了。

## Mappingと列選定

`profiles/local_aki_columns_20261012_R1.json`が新規候補規則、`research/local_aki_columns_20261012/mapping_resolution.json`が既存数値正本との対応表。W/P2/P3-AKI、ASI、RSIの既存数値式を再利用し、確率・EVとして扱わない。ASIの単独軸禁止域は地方継承元第39条から確認した。

既存29指数mappingに独立した外部変動値・堅決着補正値の実装がないため、両者をゼロで補完せず未定義の数値として記録する。完全な総合AKI値を捏造しない。この2項目の正式数値mappingは残条件である。

各列の候補は予算を使わず、観測適格な役割得点の最高値・最低値から得点幅を作り、`最高値−候補値 ≤ 得点幅×列リスク÷100`を追加候補条件にする。単独Wが成立した場合は、その馬をP2/P3アンカー候補から構造的に除外し、P2も単独ならその2着馬をP3から除外する。順位による無根拠補充ではなく、残った観測適格な役割得点の最高値を用いる。堅い構造を2点で完走する回帰を追加した。これは新しい未較正の研究仮説であり、公式な予測確率ではない。能力拮抗の得点幅と100−DCRによる情報不確実性を別表示する。

PERFORMANCE／CONDITION_FIT／POSITIONのうち2群以上に実観測があり、該当役割の指数がCALCULATEDの場合だけ入場する。これらの群は同じ馬柱を共有し得るので、統計的独立性の証明とは扱わない。全馬追加、順位による無根拠補充、点数上限による削除はない。同得点・実観測の全馬が適格になる場合はParityとして明示する。

Head-local Pairは、異なるHeadと2着馬に観測位置情報がある関係だけを候補PROTECTとする。Thirdは、そのPairの下で別馬の進出・位置維持の観測を接続する。これは条件付きの研究上の保護関係であり、具体的な展開適合や順序の正しさを実証したものではない。順序の購入確信を作らず、MEC R3の全体P3 tail保持を維持する。現候補はEXACTA／TRIOを生成し、TRIFECTAを積極的に発行する新しい根拠規則は未実装。

広い意味的集合はそのままMECへ渡し、最後に既存Capitalで判定する。常にPAPERで、必要な根拠列が空、軸不安なのに支持ある第2Headがない、Headに支持Pairがない場合はNO_BET。NO_BET候補にも診断券面は保存するが、購入券面は空。

## 過去記録と欠落

GitHubの全LOCAL Intent・Family RequestとFORMAL保存工程を走査した。114実行ID、79保存FORMAL attempt、同一競走の別IDを束ねると93個の識別済み競走（検証用IDを含む）、識別不能ID1個。再計算PAPER60／HOLD19／入力・保存記録不足35。欠落はSOURCE以外にもStatic23、Provenance23、RESULT／Settlement／Learning35を記録した。HOLDの16件は29指数指定なし、2件は発走後SOURCE、1件は発走時刻なし。

SOURCE原文のArtifact hash、Receipt hash、Ed25519署名をローカルで検証した。旧実行が成功かどうかによって抽出していない。`corpus_audit.json.gz`には失敗・候補不足・各列・券種点数・資金・結果・精算・欠落・旧Learning参照を保持した。各項目の数は重複可能な欠落件数であり、全件署名FINAL完走数ではない。

関連保管資料は2395項目を12ページで所在確認した。Rev15運用正本、浦和2026-09-23 R4 Freeze、地方回帰fixture、大井2026-09-14 Day Registry、川崎2026-09-10 Aggregate等を本文確認した。浦和R4は43点の推奨を持つが、外部署名SOURCE/PRE_KRS/KRS/FINALが取得されていない旨を記録しており、正式実行として補完していない。保管された過去全ファイルの本文・全馬指数・結果連結は未完了。所在確認件数を実証レース数に加算していない。

## 比較結果

同一競走を重複除去し、両方式を精算できた39レース（船橋・大井・川崎）。すべて結果が既知のReplayであり、新候補の未知未来OOSは0。

| 指標 | 新候補PAPER | 既存凍結推奨 |
|---|---:|---:|
| 参考点数合計 | 2743 | 9396 |
| 参考投資 | 274,300円 | 939,600円 |
| 参考払戻 | 123,290円 | 436,440円 |
| 参考PFS | 44.95% | 46.45% |
| 何らか的中 | 20/39 | 35/39 |
| 的中しながら赤字 | 15/39 | 30/39 |
| 最長赤字連続 | 14 | 19 |

新候補のW捕捉26/39、P2捕捉25/39、P3捕捉31/39。必要な候補を落とした例があり、性能改善を宣言しない。投資額・点数が異なるため、損失金額の縮小だけで優位としない。場別・頭数別・クラス別・距離別、時系列分割、最大払戻感度、損失・Drawdownは`comparison.json`。同予算・同点数は解析上の線形正規化までであり、整数100円券面を再選定する公平比較は未完了。時系列を分けても事前に既知だった結果はOOSにならない。

点数は2〜341点。例：船橋2026-09-29 R6は31点、2026-10-02 R4は183点、川崎2026-10-12 R11は10点。後者はW=[2,4,1]／P2=[2,4,1]／P3=[1,4,3]で、結果[2,5,6]のP2/P3を逃した。既存136点は1,900円の払戻／13,600円の投資で的中赤字だった。点数が変わる実装と、点数が適切である実証は分ける。

## 接続・外部実行の現状

`runtime/non_jra_formal_runner.py`に、PRE_KRS前の候補選定、SOURCEからの再計算、MEC後の候補MEC／Capital／再計算、FINAL transport traceへのhash束縛を接続した。現行Production Static／KRS入力／Ticketは置換しない。これはブランチ実装であり、mainへの反映・正式運用起動は未実施。

`tools/local_aki_external_acceptance.py`は実際の川崎11R Signed SOURCEを使い、既存LOCALの `/verify`→`/pre-krs`→`/krs/execute`（SIM-HIGH20,000）→`/final`→`/verify`へ送る具体的なReplay/PAPER試験。候補全指数と券面を保存し、入力hash、署名Artifact hash、Signed FINAL round-tripを照合する。実購入は送らず、実FINALの購入券は空。既存Production Receiptは上書きしない。内容hash別の保存先で再開する。

外部試験は自動承認審査が「SOURCE由来情報を当該Railway宛先へ送る承認未確認」と拒否した。宛先がR51とGatewayに一致し、実Healthが凍結配備束と一致し、公開鍵が既存Signed SOURCEの鍵と一致することを別のread-only検査で確認したが、再審査でも送信は拒否された。`destination_verification.json`に確認結果を保存。外部実行ID・新実KRS回数・新署名FINALは**なし／0／未成立**。実行コードの記載は実行証明ではない。

## CIで見つかった既存回帰の修正

PR CIの2系列は、旧大井10月9日7戦のテストが全台帳を走査し、川崎2戦の追加で9戦になったため失敗した。テストをその7戦の実署名済み保存先へ限定し、期待精算・署名束縛・OOS不変の検査は維持した。新規AKI列CIは成功。追加で既存実行保証の201 testsとAKI/MEC/Capitalの27 testsがローカルでPASS（重複を含む別suite件数）。

## 回帰と残条件

137 tests PASS（新規18＋関連119）。小頭数3・6、多頭数12・18、Parity、堅い得点構造と高リスク幅、軸不安、情報不足、欠測、取消Universe、重複、非有限値、SOURCE不一致、予算分離、SOURCEからの独立再計算、既存Worker／Git競合の回帰を含む。

残条件：外部送信の明示承認→既存正式入口で候補Signed SOURCE→KRS→MEC→Capital→FINAL→RESULT／Settlement／Reflection／Learningの通し実証、外部変動・堅決着補正mapping、実証されたPair/Third順序規則、39戦以外の欠落解消、公平券面比較、全14場の適用・場別検証、登録済み未来計画の継続実測。30戦到達は審査の開始条件にすぎず自動昇格しない。

**現時点で「全地方競馬場で実装完成」「正式FINAL成立」「予測改善実証済み」とは報告しない。**

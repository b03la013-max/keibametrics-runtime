# 川崎11R — AKI外部実検証（2026-10-12）

**判定：川崎11Rの実SOURCEによる外部Replay/PAPERはRESULT・Reflection・Learningまで成立。全地方版完成・Production昇格・未知未来OOSの実証ではない。**

2026-10-12のユーザー承認後、R51／現行Gatewayに登録されたRailway Runtimeへ実SOURCEを送信した。外部PRE_KRS、実KRS20,000回、既存MEC R3、Capital PAPER、Signed FINAL、既存の署名済み公式結果を用いたSigned RESULTを検証した。Ed25519署名、Receipt hash、Artifact hash、Race ID、KRS入力hash、FINAL→RESULTの凍結参照を独立照合した。

| 項目 | 保存成果物で確認した値 |
|---|---|
| 対象 | KM-LOCAL-KAW-20261012-R11-LIVE-R1 |
| SOURCE | 発走前に凍結済みの既存9頭SOURCE。取得し直して事前予測と偽装していない |
| 全必要指数 | 9頭×29指数＝261。CALCULATED232／RULED-NEUTRAL29／未解決0 |
| 実行ID | LOCAL-AKI-REPLAY-39f06c07ee208cf9 |
| 実KRS回数 | 20,000回。FINAL表示構造改修時は同一入力hash・署名検証済みKRSを再利用。40,000回と二重計上しない |
| 候補列 | W＝2,4,1／P2＝2,4,1／P3＝1,4,3 |
| MEC | 馬単6点＋三連複4点＝10点 |
| Capital | PAPER。候補数を資金に合わせて削らない |
| 購入券面 | 0件。実購入なし |
| 公式結果 | 2→5→6。既存Signed RESULTの公式情報を検証して再利用 |
| PAPER精算 | 参考投資1,000円／払戻0円／参考PFS0% |
| 購入側精算 | 投資0円／払戻0円／PFS未定義。実購入実績として集計しない |
| Reflection | 最初のPAPER失敗＝PREDICTION_ROLE_P2 |
| Learning | 署名FINAL／公式結果／PAPER精算に接続。Production変更false |
| 未知未来OOS | 0。全て結果既知のReplay |

## Receipt識別子

FINAL：`474e06e674a0e2cbe5a703c63b5565b80a479260ead33d012ab39b4d58e51f98`

RESULT：`ddbe9b0e313c0aff62db10a6683114e2284f5e08b00c7e892302a21a7ea506da`

AKI選定：`d5d21719bae10808d24c04ac9f95fe1f19008dee33e63c1240b097874062bd5d`

元の外部検証ID `LOCAL-AKI-REPLAY-f47929a904d363cc` のFINALも保持した。そこでは列がnested AKI情報にだけあり、標準Reflectionがrolesを読めない問題を確認した。予測規則・列・券面は変更せず、signed FPPのranking/rolesへの明示投影を追加した別IDで修正を検証した。既存FINALを上書きしていない。

## 署名FINALに保存されたPAPER買い目ツリー

以下はPAPER候補。実購入券面ではない。全点を1点100円で試算する。

- 馬単：6点／参考600円
  - 1着：1
    - 2着：2・4
  - 1着：2
    - 2着：1・4
  - 1着：4
    - 2着：1・2
- 三連複：4点／参考400円
  - 組合せ
    - 1－2－3
    - 1－2－4
    - 1－3－4
    - 2－3－4
- 三連単：0点

計10点／参考1,000円。公式2着5と3着6は候補に入っておらず、不的中。外部実行成功を予測成功と同一視しない。

## 保存・再検証

`evidence/local_aki_columns_20261012/external_acceptance_manifest.json` に全成果物のhash・系譜・承認範囲を記録した。`kaw_r11_external_receipts.tar.gz` に実Receipt、全29指数の全馬配列、選定、MEC、Capital、再計算、PAPER精算・Reflection・Learningを収録。SOURCEは既存canonical repository Receiptを参照し、重複SOURCE、そこから再構築可能な送信payload、同一の旧版数値配列は重複保管しない。元コピーのhashはmanifestに保持する。

`tests/test_local_aki_external_receipts.py` はこの実成果物を読み、外部通信なしで署名・系譜・KRS入力・roles・PAPER境界・精算・失敗位置を再検証する。合成Receiptを実証の代わりにしていない。

## まだ成立していない範囲

大井の6頭2点・14頭341点の外部検証は、自動承認審査が今回の承認を川崎11Rに限定し、別レースSOURCE送信として拒否した。Receiptは存在せず、船橋を含め他場を外部実行済みと報告しない。2〜341点の可変性は前回のローカルReplay検証の範囲にとどまる。

外部変動／堅決着補正の正式数値mapping、実証された順序規則、全14場の実SOURCE外部検証、未知未来OOS、同予算・同点数の実行可能な比較、既存正式Single Entryから候補を起動する本番接続は残る。今回のhelperは既存外部エンドポイントの受入検証であり、既存正式Single Entryで全地方版を完走した証明ではない。

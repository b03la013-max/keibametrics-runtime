# 京都2026-10-25の運用・監査修復

## 実装したP0

- SOURCEの子Workflowが原本保存前に失敗しても、同じRace/Execution/Requestへ結び日次StatusをSOURCE_FAILEDへ進める。新しい試行・正式FINAL・AKI NO_BET・正式準備済みRequestを古い失敗で上書きしない。Cutoffを超えたものは遅延FINAL生成対象にせず、PFSはnull。
- SOURCE完了イベントから既存AutopilotのStatus照合を起動する。SOURCEの自動rerun、別入口、手動Dispatchは追加しない。
- FINALの資金監査を、PRE_KRSの券面なしConformanceと区別する。実際に凍結する券面から、券種・1着・Ordered Pairの投資、集中度を集計し、署名前に実投資総額と一致させる。
- 実際のSOURCE取得・Static計算・FINAL・Cutoff・発走時刻を並べる。legacy `static_freeze_timestamp` がCutoff境界を意味する場合に、その意味を明記する。独立保存証拠やOOS資格を与えない。
- 新規SOURCEの凍結前に、既に取得した2回目の公式出馬表を同一Race・Active馬の同一性・原本SHA・Cutoffへ束縛する。最新馬場をSource→FeatureとKRSの共通Contextへ接続し、2原本を保持する。旧署名SOURCEは明示的な新取得用Bindingを持たない限り従来のContextを保持する。取得数・KRS回数は増やさない。新しい実装HashをReceiptとPolicy fingerprintへ含め、別コード/PolicyのOOSを混合しない。
- Current Authorityのコード・Registry・SOURCE Hashを照合した上で、全馬全RoleのRule ID、期待カテゴリ、実測カテゴリ、根拠、未充足要件を保存する。新馬PAPER専用の既存Policyも再現し、基準・候補・券面を変更しない。
- 新規Reviewは`DECISION_AWARE_V2`で作る。PAPERの正式0点を券面変換失敗とせず、予測Roleの失敗は残す。MECの必須Semantic Unitでない三連単未捕捉を残余診断に分ける。既存Review/Learningは既存Workflowのreadbackによりそのまま保持する。従来APIの既定もLEGACYとして、過去の再現Hashを維持する。

## 実原本による検収

`offline_audit.json`は京都4R〜12Rの9件・117頭・351 Roleセルを再現した事後監査。SOURCE/FINAL/RESULTの生SHAを記録し、変更していないことを再確認した。実券面の総投資は8,100円。9件とも実時計の順序は整合する。これは発走前の独立保存再証明ではない。

京都11Rは保存SOURCE内の2原本で稍重→良が確認でき、従来Contextは稍重を返した。新取得用Bindingを用いる純粋な事後診断では良を返し、他8件の馬場は変わらない。新SOURCE・予測・署名は生成していない。

京都5RはPAPERで予測Role成功、京都7Rは三連複保護で利益、京都8Rは正解三連単捕捉。これらを失敗として一括変更しない。京都4R・6R・9R〜12RはW Role形成の失敗を残す。

```bash
PYTHONPATH=runtime:runtime/jra_source_runtime python scripts/audit_kyoto_20261025_correctness.py --output /tmp/kyoto-correctness.json
```

取消番号修復は既存PR #337で扱う。原SOURCE Run40149439237 / Artifact12581592816を実取得し、ZIP SHA `f77dd21d83c9e6b98eaea6bb1d274018d53e08517abfa0bff8d38bffb80b357c`、136,226バイトの原CP932詳細のSHA `c896c6468a98a490307755982f29bb0c04e41f34dc3edfd222df40823fa71a1e`を検証。登録9頭・取消5番1頭・出走8頭となった。今回のコード変更へ同じParser修正を重複して入れない。

## P1/P2と残る受入

既存PR #332へ京都全9 FINALを同予算・券種構成で比較する診断を追加する。8方式はいずれも当日のProductionを下回り、新規的中救済0。予測係数・BVI重み・KRS権限の変更根拠にはしない。正例7R・8Rを分母から落とさない。

未知未来OOSは、この事後診断と別工程である。固定ENV 5e7f…の30 Raceと、PR332の別モデルの既存60 Race・3日・2場条件を混ぜない。既存の前向き登録はinactive、Owner承認と独立した発走前保存がないものは登録・昇格しない。ENVの5束縛コード・モデル・既存のProduction優先ゲートを変更しない。

馬場変更後の正式再予測には、旧FINALを保持した新SOURCE/Static/KRS/FINALの版管理が必要である。本修復はそこを既存のRace ID上書きで代用しない。現行の不変FINALストアに対する改版権限・改版契約が未定のため、この受入は未完了。User Deliveryも受領証拠のないものを成功扱いにしない。

今回のPRは実装修復の候補であり、mainへのMerge・Deploy・署名発行・過去結果の再登録を行ったという記録ではない。
